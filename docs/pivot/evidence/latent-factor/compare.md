# The latent funding-stress factor (#543)

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| latent_factor | 11 / 5.46 fail | fail | 11 / 6.15 fail | 0 / 0.78 fail |
| latent_factor_resid | 11 / 5.46 fail | fail | 11 / 6.15 fail | 0 / 0.78 fail |
| latent_factor_logit | 11 / 4.65 fail | fail | 11 / 6.23 fail | 1 / 1.89 fail |
| risk_gbm+latent_factor | 12 / 3.50 fail | fail | 12 / 4.88 fail | 2 / 0.44 fail |
| risk_gbm+latent_factor_resid | 12 / 3.50 fail | fail | 12 / 4.85 fail | 2 / 0.44 fail |
| risk_gbm+latent_factor_logit | 12 / 2.54 fail | fail | 12 / 4.42 fail | 2 / 2.11 fail |
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
| latent_factor | 14 / 3.38 fail | fail | 14 / 3.84 fail | 1 / 3.33 fail |
| latent_factor_resid | 14 / 3.34 fail | fail | 14 / 3.84 fail | 1 / 3.33 fail |
| latent_factor_logit | 12 / 3.37 fail | fail | 12 / 4.12 fail | 1 / 2.89 fail |
| risk_gbm+latent_factor | 13 / 3.09 fail | fail | 13 / 3.87 fail | 2 / 2.83 fail |
| risk_gbm+latent_factor_resid | 13 / 3.09 fail | fail | 13 / 3.87 fail | 2 / 2.83 fail |
| risk_gbm+latent_factor_logit | 15 / 2.15 fail | fail | 15 / 3.41 fail | 4 / 1.69 fail |
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
| latent_factor | 12 / 4.01 fail | fail | 12 / 4.39 fail | 0 / 0.78 fail |
| latent_factor_resid | 12 / 4.01 fail | fail | 12 / 4.39 fail | 0 / 0.78 fail |
| latent_factor_logit | 11 / 3.35 fail | fail | 11 / 4.45 fail | 1 / 1.47 fail |
| risk_gbm+latent_factor | 13 / 3.37 fail | fail | 13 / 4.13 fail | 2 / 1.00 fail |
| risk_gbm+latent_factor_resid | 13 / 3.37 fail | fail | 13 / 4.13 fail | 2 / 1.00 fail |
| risk_gbm+latent_factor_logit | 15 / 2.98 fail | fail | 15 / 4.25 fail | 4 / 2.42 fail |
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

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor | 11 of 26 | 0.423 [0.250, 0.609] | 0.269 | 5.46 | 0.0 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor_logit | 11 of 26 | 0.423 [0.242, 0.606] | 0.269 | 4.65 | 0.5 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| latent_factor_resid | 11 of 26 | 0.423 [0.238, 0.600] | 0.269 | 5.46 | 0.0 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 | 1.2 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+latent_factor | 12 of 26 | 0.462 [0.278, 0.667] | 0.231 | 3.50 | 0.2 / 0.0 | 1 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+latent_factor_logit | 12 of 26 | 0.462 [0.269, 0.654] | 0.231 | 2.54 | 0.2 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+latent_factor_resid | 12 of 26 | 0.462 [0.273, 0.667] | 0.231 | 3.50 | 0.2 / 0.0 | 1 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 1.85 | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 1.77 | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.192 | 1.88 | 0.7 / 0.0 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| latent_factor | 0.00 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.06 (17) | 0.03 (101) | 0.11 (9) | 0.00 (13) |
| latent_factor_logit | 0.00 (102) | 0.00 (4) | – | 0.00 (5) | 0.00 (29) | 0.00 (17) | 0.00 (101) | 0.00 (9) | 0.00 (13) |
| latent_factor_resid | 0.00 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.06 (17) | 0.03 (101) | 0.11 (9) | 0.00 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+latent_factor | 0.39 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.32 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+latent_factor_logit | 0.39 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.59 (17) | 0.33 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+latent_factor_resid | 0.39 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.32 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| latent_factor | +0.0242 [-0.0170, +0.0667] | -0.0906 [-0.1007, -0.0801] | -0.0189 [-0.0244, -0.0138] | -0.0076 [-0.0097, -0.0049] | +0.0245 [-0.0043, +0.0610] | -0.0007 [-0.0221, +0.0235] | -0.0178 [-0.0293, -0.0057] | +0.0693 [-0.0111, +0.1547] | +0.0331 [+0.0133, +0.0572] |
| latent_factor_logit | +0.0275 [-0.0032, +0.0629] | +0.0292 [+0.0141, +0.0413] | +0.0136 [+0.0119, +0.0155] | +0.0017 [-0.0029, +0.0052] | +0.0258 [-0.0030, +0.0636] | +0.0256 [+0.0008, +0.0535] | +0.0153 [+0.0079, +0.0245] | +0.0903 [-0.0026, +0.1922] | +0.0390 [+0.0073, +0.0712] |
| latent_factor_resid | +0.0252 [-0.0160, +0.0713] | -0.0909 [-0.1007, -0.0804] | -0.0193 [-0.0252, -0.0143] | -0.0080 [-0.0101, -0.0052] | +0.0243 [-0.0054, +0.0650] | -0.0003 [-0.0231, +0.0248] | -0.0180 [-0.0296, -0.0051] | +0.0712 [-0.0058, +0.1510] | +0.0335 [+0.0112, +0.0590] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+latent_factor | +0.0442 [-0.0026, +0.0927] | -0.0634 [-0.0769, -0.0495] | -0.0123 [-0.0172, -0.0080] | -0.0057 [-0.0091, -0.0023] | +0.0274 [-0.0038, +0.0636] | +0.0573 [+0.0303, +0.0849] | -0.0134 [-0.0259, +0.0001] | +0.1155 [+0.0352, +0.1937] | +0.0686 [+0.0400, +0.0954] |
| risk_gbm+latent_factor_logit | +0.0589 [+0.0223, +0.0985] | +0.0275 [+0.0122, +0.0413] | +0.0136 [+0.0119, +0.0155] | +0.0034 [-0.0006, +0.0064] | +0.0268 [+0.0002, +0.0595] | +0.0613 [+0.0359, +0.0893] | +0.0173 [+0.0089, +0.0266] | +0.1155 [+0.0285, +0.1939] | +0.0686 [+0.0429, +0.0951] |
| risk_gbm+latent_factor_resid | +0.0445 [-0.0010, +0.0921] | -0.0636 [-0.0776, -0.0496] | -0.0126 [-0.0173, -0.0084] | -0.0060 [-0.0094, -0.0024] | +0.0271 [-0.0057, +0.0674] | +0.0572 [+0.0297, +0.0859] | -0.0136 [-0.0253, -0.0010] | +0.1155 [+0.0353, +0.1963] | +0.0686 [+0.0405, +0.0934] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.358 | 6.69 | 2.9 / 4.7 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.380 | 7.04 | 1.2 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor | 14 of 26 | 0.538 [0.357, 0.727] | 0.395 | 6.96 | 0.2 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor_logit | 12 of 26 | 0.462 [0.267, 0.654] | 0.404 | 6.85 | 0.7 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| latent_factor_resid | 14 of 26 | 0.538 [0.346, 0.720] | 0.388 | 6.85 | 0.2 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.231 | 4.08 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.154 | 1.38 | 1.5 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+latent_factor | 13 of 26 | 0.500 [0.305, 0.704] | 0.283 | 5.92 | 0.7 / 0.0 | 1 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+latent_factor_logit | 15 of 26 | 0.577 [0.393, 0.762] | 0.269 | 5.04 | 0.7 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+latent_factor_resid | 13 of 26 | 0.500 [0.304, 0.704] | 0.283 | 5.92 | 0.7 / 0.0 | 1 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.192 | 2.42 | 3.2 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.192 | 2.31 | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.192 | 2.31 | 1.0 / 0.7 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| latent_factor | 0.84 (102) | 0.50 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.71 (101) | 0.44 (9) | 0.62 (13) |
| latent_factor_logit | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.66 (29) | 0.71 (17) | 0.74 (101) | 0.44 (9) | 0.46 (13) |
| latent_factor_resid | 0.83 (102) | 0.50 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.70 (101) | 0.44 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+latent_factor | 0.63 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.54 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+latent_factor_logit | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.65 (17) | 0.54 (101) | 0.67 (9) | 0.38 (13) |
| risk_gbm+latent_factor_resid | 0.63 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.54 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| latent_factor | +0.0242 [-0.0170, +0.0667] | -0.0906 [-0.1007, -0.0801] | -0.0189 [-0.0244, -0.0138] | -0.0076 [-0.0097, -0.0049] | +0.0245 [-0.0043, +0.0610] | -0.0007 [-0.0221, +0.0235] | -0.0178 [-0.0293, -0.0057] | +0.0693 [-0.0111, +0.1547] | +0.0331 [+0.0133, +0.0572] |
| latent_factor_logit | +0.0275 [-0.0032, +0.0629] | +0.0292 [+0.0141, +0.0413] | +0.0136 [+0.0119, +0.0155] | +0.0017 [-0.0029, +0.0052] | +0.0258 [-0.0030, +0.0636] | +0.0256 [+0.0008, +0.0535] | +0.0153 [+0.0079, +0.0245] | +0.0903 [-0.0026, +0.1922] | +0.0390 [+0.0073, +0.0712] |
| latent_factor_resid | +0.0252 [-0.0160, +0.0713] | -0.0909 [-0.1007, -0.0804] | -0.0193 [-0.0252, -0.0143] | -0.0080 [-0.0101, -0.0052] | +0.0243 [-0.0054, +0.0650] | -0.0003 [-0.0231, +0.0248] | -0.0180 [-0.0296, -0.0051] | +0.0712 [-0.0058, +0.1510] | +0.0335 [+0.0112, +0.0590] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+latent_factor | +0.0442 [-0.0026, +0.0927] | -0.0634 [-0.0769, -0.0495] | -0.0123 [-0.0172, -0.0080] | -0.0057 [-0.0091, -0.0023] | +0.0274 [-0.0038, +0.0636] | +0.0573 [+0.0303, +0.0849] | -0.0134 [-0.0259, +0.0001] | +0.1155 [+0.0352, +0.1937] | +0.0686 [+0.0400, +0.0954] |
| risk_gbm+latent_factor_logit | +0.0589 [+0.0223, +0.0985] | +0.0275 [+0.0122, +0.0413] | +0.0136 [+0.0119, +0.0155] | +0.0034 [-0.0006, +0.0064] | +0.0268 [+0.0002, +0.0595] | +0.0613 [+0.0359, +0.0893] | +0.0173 [+0.0089, +0.0266] | +0.1155 [+0.0285, +0.1939] | +0.0686 [+0.0429, +0.0951] |
| risk_gbm+latent_factor_resid | +0.0445 [-0.0010, +0.0921] | -0.0636 [-0.0776, -0.0496] | -0.0126 [-0.0173, -0.0084] | -0.0060 [-0.0094, -0.0024] | +0.0271 [-0.0057, +0.0674] | +0.0572 [+0.0297, +0.0859] | -0.0136 [-0.0253, -0.0010] | +0.1155 [+0.0353, +0.1963] | +0.0686 [+0.0405, +0.0934] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|
| latent_factor | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| latent_factor_resid | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| latent_factor_logit | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm+latent_factor | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+latent_factor_resid | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+latent_factor_logit | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 3 of 5 |
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
| latent_factor | 0.0840 / 0.3319 | 0.1019 / 0.3838 | 0.1091 / 0.4017 | 0.1129 / 0.4014 | 0.1145 / 0.4033 |
| latent_factor_resid | 0.0841 / 0.3290 | 0.1020 / 0.3824 | 0.1092 / 0.4007 | 0.1130 / 0.4002 | 0.1146 / 0.4020 |
| latent_factor_logit | 0.0529 / 0.1937 | 0.0590 / 0.2142 | 0.0617 / 0.2276 | 0.0647 / 0.2385 | 0.0626 / 0.2265 |
| risk_gbm+latent_factor | 0.0731 / 0.2952 | 0.0972 / 0.3680 | 0.1010 / 0.3746 | 0.1041 / 0.3750 | 0.1081 / 0.3879 |
| risk_gbm+latent_factor_resid | 0.0733 / 0.2953 | 0.0974 / 0.3674 | 0.1012 / 0.3744 | 0.1043 / 0.3745 | 0.1083 / 0.3873 |
| risk_gbm+latent_factor_logit | 0.0465 / 0.1829 | 0.0596 / 0.2182 | 0.0593 / 0.2211 | 0.0613 / 0.2301 | 0.0623 / 0.2309 |
| risk_gbm | 0.0577 / 0.6598 | 0.0687 / 0.8020 | 0.0667 / 0.7889 | 0.0668 / 0.7921 | 0.0696 / 0.8044 |
| risk_gbm_base | 0.0592 / 0.6599 | 0.0691 / 0.8045 | 0.0677 / 0.7914 | 0.0668 / 0.7890 | 0.0696 / 0.8085 |
| risk_logistic | 0.0606 / 0.6775 | 0.0676 / 0.8012 | 0.0689 / 0.8060 | 0.0688 / 0.8073 | 0.0690 / 0.8166 |
| risk_logistic_base | 0.0596 / 0.6638 | 0.0672 / 0.7968 | 0.0689 / 0.7996 | 0.0689 / 0.8122 | 0.0687 / 0.8139 |
| risk_quantile_skewt_base | 0.0630 / 0.7127 | 0.0687 / 0.8316 | 0.0670 / 0.7958 | 0.0669 / 0.8027 | 0.0670 / 0.7932 |
| ngboost_laplace | 0.0462 / 0.1682 | 0.0568 / 0.2092 | 0.0595 / 0.2245 | 0.0615 / 0.2523 | 0.0637 / 0.2666 |
| calendar_climatology | 0.0714 / 0.2963 | 0.0711 / 0.2954 | 0.0707 / 0.2943 | 0.0708 / 0.2952 | 0.0709 / 0.2958 |
| persistence_logistic | 0.0563 / 0.2014 | 0.0611 / 0.2184 | 0.0644 / 0.2424 | 0.0624 / 0.2254 | 0.0634 / 0.2394 |

## latent_factor: onsets only this row warns

latent_factor warns 14 of 26 onsets; at least one of the five passers warns 16. 4 are warned by latent_factor and by none of the five passers:

* 2019-05-28 (flagged at h = 1, 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)
* 2020-03-12 (flagged at h = 1)

Warned by a passer and not by latent_factor: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### latent_factor: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 8 | 0 of 1873 | 1871 |
| 2 | 90 | 0 | 0 | 7 | 10 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 6 | 11 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 6 | 11 | 0 of 1869 | 1869 |

## latent_factor_resid: onsets only this row warns

latent_factor_resid warns 14 of 26 onsets; at least one of the five passers warns 16. 4 are warned by latent_factor_resid and by none of the five passers:

* 2019-05-28 (flagged at h = 1, 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)
* 2020-03-12 (flagged at h = 1)

Warned by a passer and not by latent_factor_resid: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### latent_factor_resid: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 8 | 0 of 1873 | 1871 |
| 2 | 90 | 0 | 0 | 7 | 10 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 6 | 10 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 6 | 11 | 0 of 1869 | 1869 |

## latent_factor_logit: onsets only this row warns

latent_factor_logit warns 12 of 26 onsets; at least one of the five passers warns 16. 4 are warned by latent_factor_logit and by none of the five passers:

* 2019-05-28 (flagged at h = 1, 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)
* 2020-03-12 (flagged at h = 5)

Warned by a passer and not by latent_factor_logit: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### latent_factor_logit: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 4 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 9 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 9 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 11 | 0 of 1869 | 1869 |

## risk_gbm+latent_factor: onsets only this row warns

risk_gbm+latent_factor warns 13 of 26 onsets; at least one of the five passers warns 16. 3 are warned by risk_gbm+latent_factor and by none of the five passers:

* 2019-05-28 (flagged at h = 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by risk_gbm+latent_factor: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+latent_factor: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 2 | 0 of 1873 | 1848 |
| 2 | 90 | 0 | 0 | 7 | 8 | 0 of 1872 | 1830 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1822 |
| 4 | 90 | 1 | 0 | 7 | 7 | 0 of 1870 | 1824 |
| 5 | 89 | 0 | 0 | 7 | 8 | 0 of 1869 | 1829 |

## risk_gbm+latent_factor_resid: onsets only this row warns

risk_gbm+latent_factor_resid warns 13 of 26 onsets; at least one of the five passers warns 16. 3 are warned by risk_gbm+latent_factor_resid and by none of the five passers:

* 2019-05-28 (flagged at h = 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by risk_gbm+latent_factor_resid: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+latent_factor_resid: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 2 | 0 of 1873 | 1848 |
| 2 | 90 | 0 | 0 | 7 | 8 | 0 of 1872 | 1830 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1822 |
| 4 | 90 | 1 | 0 | 7 | 7 | 0 of 1870 | 1824 |
| 5 | 89 | 0 | 0 | 7 | 8 | 0 of 1869 | 1829 |

## risk_gbm+latent_factor_logit: onsets only this row warns

risk_gbm+latent_factor_logit warns 15 of 26 onsets; at least one of the five passers warns 16. 4 are warned by risk_gbm+latent_factor_logit and by none of the five passers:

* 2019-05-28 (flagged at h = 2, 3, 5)
* 2019-06-25 (flagged at h = 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)
* 2020-03-12 (flagged at h = 5)

Warned by a passer and not by risk_gbm+latent_factor_logit: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-10-15

### risk_gbm+latent_factor_logit: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 7 | 0 | 0 of 1873 | 1850 |
| 2 | 90 | 0 | 0 | 7 | 7 | 0 of 1872 | 1830 |
| 3 | 90 | 0 | 0 | 7 | 8 | 0 of 1871 | 1822 |
| 4 | 90 | 1 | 0 | 7 | 6 | 0 of 1870 | 1824 |
| 5 | 89 | 0 | 0 | 7 | 7 | 0 of 1869 | 1829 |

## latent_factor against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.026 [-0.040, -0.012] |
| 2 | -0.033 [-0.049, -0.015] |
| 3 | -0.042 [-0.057, -0.025] |
| 4 | -0.046 [-0.061, -0.029] |
| 5 | -0.045 [-0.060, -0.028] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.023 [-0.028, 0.079] | 0.051 [-0.001, 0.109] | 0.049 [0.002, 0.098] |
| 2020 | 251 | -0.130 [-0.139, -0.120] | -0.158 [-0.172, -0.139] | -0.161 [-0.175, -0.142] |
| 2021-23 | 748 | -0.033 [-0.039, -0.026] | -0.071 [-0.080, -0.062] | -0.079 [-0.088, -0.070] |
| 2024 | 250 | -0.011 [-0.014, -0.008] | -0.025 [-0.029, -0.020] | -0.025 [-0.032, -0.017] |
| 2025-26 | 249 | 0.009 [-0.019, 0.044] | 0.001 [-0.022, 0.028] | 0.014 [-0.013, 0.046] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.055 [-0.075, -0.035] | -0.056 [-0.071, -0.039] | -0.049 [-0.065, -0.030] |
| ordinary | 1603 | -0.023 [-0.038, -0.006] | -0.040 [-0.057, -0.021] | -0.045 [-0.062, -0.026] |
| quarter_end | 31 | -0.046 [-0.108, 0.012] | -0.050 [-0.095, -0.003] | -0.050 [-0.102, 0.001] |
| tax_date | 89 | -0.036 [-0.069, 0.001] | -0.056 [-0.084, -0.028] | -0.036 [-0.072, 0.006] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.020 [-0.023, -0.016] | -0.048 [-0.054, -0.041] | -0.054 [-0.060, -0.047] |
| 1 | 324 | -0.099 [-0.113, -0.082] | -0.130 [-0.145, -0.110] | -0.134 [-0.149, -0.113] |
| 2 | 41 | 0.082 [–] | 0.089 [–] | 0.096 [–] |
| 3 | 473 | -0.000 [-0.045, 0.048] | 0.018 [-0.029, 0.069] | 0.023 [-0.023, 0.071] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.154, 0.222] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.353] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [0.000, 0.533] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.095 [-0.125, 0.304] |

## latent_factor against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.038 [-0.048, -0.029] |
| 2 | -0.045 [-0.056, -0.034] |
| 3 | -0.050 [-0.062, -0.037] |
| 4 | -0.051 [-0.064, -0.038] |
| 5 | -0.051 [-0.063, -0.037] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.030 [-0.059, -0.001] | 0.013 [-0.020, 0.052] | 0.024 [-0.009, 0.063] |
| 2020 | 251 | -0.124 [-0.133, -0.112] | -0.159 [-0.170, -0.146] | -0.160 [-0.169, -0.147] |
| 2021-23 | 748 | -0.033 [-0.040, -0.026] | -0.070 [-0.080, -0.062] | -0.079 [-0.088, -0.070] |
| 2024 | 250 | -0.012 [-0.014, -0.009] | -0.025 [-0.029, -0.020] | -0.025 [-0.032, -0.017] |
| 2025-26 | 249 | -0.004 [-0.026, 0.022] | 0.005 [-0.018, 0.033] | 0.005 [-0.019, 0.035] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.049 [-0.064, -0.034] | -0.040 [-0.059, -0.019] | -0.044 [-0.063, -0.023] |
| ordinary | 1603 | -0.036 [-0.047, -0.027] | -0.051 [-0.063, -0.038] | -0.052 [-0.065, -0.038] |
| quarter_end | 31 | -0.062 [-0.099, -0.025] | -0.059 [-0.091, -0.025] | -0.076 [-0.110, -0.042] |
| tax_date | 89 | -0.034 [-0.058, -0.011] | -0.041 [-0.065, -0.013] | -0.037 [-0.064, -0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.020 [-0.024, -0.017] | -0.048 [-0.054, -0.042] | -0.053 [-0.061, -0.047] |
| 1 | 324 | -0.098 [-0.110, -0.084] | -0.130 [-0.146, -0.110] | -0.133 [-0.149, -0.114] |
| 2 | 41 | 0.034 [–] | 0.076 [-0.066, 0.161] | 0.082 [–] |
| 3 | 473 | -0.041 [-0.067, -0.015] | -0.008 [-0.041, 0.028] | 0.001 [-0.032, 0.035] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.308, 0.069] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.308, 0.273] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | 0.000 [-0.188, 0.167] |

## latent_factor against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.013 [-0.023, -0.000] |
| 2 | -0.031 [-0.041, -0.020] |
| 3 | -0.038 [-0.049, -0.027] |
| 4 | -0.042 [-0.053, -0.032] |
| 5 | -0.044 [-0.054, -0.033] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.024 [-0.016, 0.070] | 0.015 [-0.022, 0.052] | 0.012 [-0.020, 0.044] |
| 2020 | 251 | -0.091 [-0.100, -0.081] | -0.121 [-0.130, -0.110] | -0.124 [-0.134, -0.113] |
| 2021-23 | 748 | -0.019 [-0.024, -0.014] | -0.057 [-0.064, -0.049] | -0.065 [-0.073, -0.057] |
| 2024 | 250 | -0.008 [-0.010, -0.005] | -0.021 [-0.024, -0.018] | -0.024 [-0.027, -0.020] |
| 2025-26 | 249 | 0.025 [-0.005, 0.063] | 0.003 [-0.014, 0.026] | -0.001 [-0.017, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.023, 0.023] | -0.029 [-0.042, -0.014] | -0.035 [-0.048, -0.021] |
| ordinary | 1603 | -0.018 [-0.029, -0.005] | -0.042 [-0.054, -0.030] | -0.047 [-0.059, -0.036] |
| quarter_end | 31 | 0.069 [-0.010, 0.153] | 0.029 [-0.051, 0.113] | 0.013 [-0.074, 0.097] |
| tax_date | 89 | 0.033 [0.013, 0.058] | -0.003 [-0.009, 0.003] | -0.010 [-0.017, -0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.011 [-0.013, -0.009] | -0.039 [-0.044, -0.034] | -0.045 [-0.050, -0.039] |
| 1 | 324 | -0.069 [-0.080, -0.058] | -0.101 [-0.112, -0.087] | -0.106 [-0.118, -0.091] |
| 2 | 41 | 0.075 [–] | 0.058 [–] | 0.055 [-0.026, 0.099] |
| 3 | 473 | 0.015 [-0.019, 0.055] | -0.003 [-0.035, 0.030] | -0.007 [-0.037, 0.022] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [0.000, 0.174] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [0.000, 0.353] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.095 [0.000, 0.211] |

## latent_factor against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.028 [-0.037, -0.018] |
| 2 | -0.041 [-0.051, -0.030] |
| 3 | -0.045 [-0.055, -0.035] |
| 4 | -0.051 [-0.062, -0.039] |
| 5 | -0.051 [-0.062, -0.040] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.007 [-0.021, 0.038] | 0.015 [-0.012, 0.045] | 0.014 [-0.014, 0.044] |
| 2020 | 251 | -0.114 [-0.124, -0.102] | -0.133 [-0.140, -0.122] | -0.142 [-0.151, -0.130] |
| 2021-23 | 748 | -0.032 [-0.039, -0.026] | -0.066 [-0.075, -0.059] | -0.076 [-0.085, -0.068] |
| 2024 | 250 | -0.007 [-0.013, -0.000] | -0.022 [-0.027, -0.015] | -0.024 [-0.030, -0.016] |
| 2025-26 | 249 | -0.001 [-0.008, 0.008] | -0.004 [-0.015, 0.011] | -0.008 [-0.019, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.022 [-0.036, -0.007] | -0.038 [-0.053, -0.023] | -0.044 [-0.059, -0.028] |
| ordinary | 1603 | -0.030 [-0.040, -0.021] | -0.047 [-0.057, -0.037] | -0.053 [-0.064, -0.042] |
| quarter_end | 31 | 0.009 [-0.024, 0.042] | -0.006 [-0.042, 0.031] | -0.012 [-0.049, 0.028] |
| tax_date | 89 | -0.002 [-0.028, 0.027] | -0.031 [-0.055, -0.004] | -0.036 [-0.062, -0.008] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.019 [-0.023, -0.015] | -0.045 [-0.051, -0.039] | -0.052 [-0.059, -0.045] |
| 1 | 324 | -0.090 [-0.102, -0.076] | -0.111 [-0.124, -0.096] | -0.120 [-0.133, -0.101] |
| 2 | 41 | -0.015 [–] | 0.012 [–] | -0.021 [–] |
| 3 | 473 | -0.005 [-0.032, 0.022] | -0.003 [-0.032, 0.026] | -0.005 [-0.034, 0.026] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [0.000, 0.188] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.273] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.083 [0.000, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.095 [0.000, 0.231] |

## latent_factor_resid against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.026 [-0.040, -0.011] |
| 2 | -0.033 [-0.049, -0.016] |
| 3 | -0.043 [-0.058, -0.025] |
| 4 | -0.046 [-0.062, -0.030] |
| 5 | -0.045 [-0.060, -0.028] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.024 [-0.028, 0.080] | 0.052 [0.004, 0.106] | 0.050 [0.001, 0.100] |
| 2020 | 251 | -0.131 [-0.139, -0.120] | -0.158 [-0.172, -0.140] | -0.161 [-0.175, -0.140] |
| 2021-23 | 748 | -0.033 [-0.040, -0.027] | -0.071 [-0.080, -0.062] | -0.079 [-0.088, -0.070] |
| 2024 | 250 | -0.012 [-0.015, -0.008] | -0.026 [-0.030, -0.020] | -0.026 [-0.032, -0.017] |
| 2025-26 | 249 | 0.009 [-0.018, 0.044] | 0.001 [-0.023, 0.030] | 0.013 [-0.014, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.055 [-0.074, -0.035] | -0.056 [-0.071, -0.039] | -0.048 [-0.066, -0.030] |
| ordinary | 1603 | -0.023 [-0.038, -0.005] | -0.040 [-0.057, -0.021] | -0.045 [-0.062, -0.027] |
| quarter_end | 31 | -0.044 [-0.100, 0.013] | -0.049 [-0.094, 0.001] | -0.049 [-0.101, 0.004] |
| tax_date | 89 | -0.035 [-0.068, 0.003] | -0.056 [-0.083, -0.026] | -0.036 [-0.072, 0.008] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.020 [-0.023, -0.017] | -0.048 [-0.055, -0.042] | -0.054 [-0.061, -0.047] |
| 1 | 324 | -0.099 [-0.113, -0.082] | -0.130 [-0.146, -0.110] | -0.134 [-0.150, -0.114] |
| 2 | 41 | 0.084 [-0.124, 0.221] | 0.090 [–] | 0.097 [-0.023, 0.158] |
| 3 | 473 | 0.000 [-0.044, 0.051] | 0.019 [-0.027, 0.070] | 0.024 [-0.021, 0.069] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.158, 0.222] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.357] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [-0.077, 0.545] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.095 [-0.125, 0.300] |

## latent_factor_resid against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.038 [-0.047, -0.028] |
| 2 | -0.045 [-0.057, -0.034] |
| 3 | -0.050 [-0.062, -0.036] |
| 4 | -0.052 [-0.064, -0.038] |
| 5 | -0.051 [-0.064, -0.038] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.029 [-0.058, -0.001] | 0.014 [-0.018, 0.051] | 0.025 [-0.009, 0.065] |
| 2020 | 251 | -0.124 [-0.133, -0.113] | -0.159 [-0.170, -0.146] | -0.160 [-0.170, -0.147] |
| 2021-23 | 748 | -0.033 [-0.040, -0.027] | -0.071 [-0.080, -0.062] | -0.079 [-0.088, -0.071] |
| 2024 | 250 | -0.012 [-0.015, -0.009] | -0.026 [-0.029, -0.020] | -0.026 [-0.032, -0.017] |
| 2025-26 | 249 | -0.004 [-0.026, 0.023] | 0.005 [-0.018, 0.035] | 0.005 [-0.019, 0.034] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.048 [-0.063, -0.033] | -0.040 [-0.059, -0.019] | -0.044 [-0.063, -0.023] |
| ordinary | 1603 | -0.037 [-0.046, -0.027] | -0.051 [-0.063, -0.038] | -0.052 [-0.066, -0.039] |
| quarter_end | 31 | -0.060 [-0.102, -0.022] | -0.058 [-0.089, -0.023] | -0.075 [-0.107, -0.039] |
| tax_date | 89 | -0.033 [-0.056, -0.009] | -0.041 [-0.066, -0.014] | -0.037 [-0.064, -0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.021 [-0.024, -0.018] | -0.048 [-0.055, -0.042] | -0.054 [-0.061, -0.047] |
| 1 | 324 | -0.098 [-0.109, -0.084] | -0.131 [-0.146, -0.110] | -0.134 [-0.149, -0.114] |
| 2 | 41 | 0.035 [–] | 0.077 [–] | 0.083 [–] |
| 3 | 473 | -0.040 [-0.065, -0.015] | -0.008 [-0.040, 0.028] | 0.001 [-0.032, 0.039] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.316, 0.071] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.182] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.300, 0.286] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | 0.000 [-0.182, 0.172] |

## latent_factor_resid against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.013 [-0.024, -0.001] |
| 2 | -0.031 [-0.042, -0.020] |
| 3 | -0.039 [-0.049, -0.028] |
| 4 | -0.042 [-0.052, -0.032] |
| 5 | -0.044 [-0.054, -0.034] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.025 [-0.014, 0.072] | 0.016 [-0.021, 0.050] | 0.012 [-0.019, 0.046] |
| 2020 | 251 | -0.091 [-0.100, -0.081] | -0.121 [-0.131, -0.110] | -0.124 [-0.135, -0.113] |
| 2021-23 | 748 | -0.019 [-0.025, -0.014] | -0.057 [-0.065, -0.050] | -0.065 [-0.073, -0.058] |
| 2024 | 250 | -0.008 [-0.010, -0.005] | -0.022 [-0.024, -0.019] | -0.024 [-0.027, -0.021] |
| 2025-26 | 249 | 0.024 [-0.005, 0.062] | 0.003 [-0.015, 0.025] | -0.001 [-0.017, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.022, 0.025] | -0.028 [-0.042, -0.014] | -0.035 [-0.048, -0.022] |
| ordinary | 1603 | -0.018 [-0.030, -0.006] | -0.043 [-0.054, -0.031] | -0.048 [-0.059, -0.036] |
| quarter_end | 31 | 0.071 [-0.008, 0.151] | 0.030 [-0.054, 0.114] | 0.014 [-0.071, 0.100] |
| tax_date | 89 | 0.034 [0.013, 0.058] | -0.003 [-0.009, 0.004] | -0.010 [-0.017, -0.002] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.011 [-0.014, -0.009] | -0.039 [-0.044, -0.034] | -0.045 [-0.051, -0.040] |
| 1 | 324 | -0.070 [-0.080, -0.058] | -0.101 [-0.113, -0.086] | -0.106 [-0.118, -0.091] |
| 2 | 41 | 0.076 [–] | 0.059 [-0.038, 0.125] | 0.056 [-0.028, 0.099] |
| 3 | 473 | 0.016 [-0.018, 0.054] | -0.002 [-0.034, 0.031] | -0.006 [-0.037, 0.025] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [0.000, 0.174] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [0.000, 0.364] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.095 [0.000, 0.211] |

## latent_factor_resid against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.028 [-0.037, -0.018] |
| 2 | -0.041 [-0.052, -0.030] |
| 3 | -0.045 [-0.056, -0.034] |
| 4 | -0.051 [-0.061, -0.039] |
| 5 | -0.051 [-0.063, -0.040] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.008 [-0.021, 0.040] | 0.016 [-0.013, 0.047] | 0.015 [-0.014, 0.043] |
| 2020 | 251 | -0.114 [-0.124, -0.102] | -0.133 [-0.140, -0.122] | -0.142 [-0.151, -0.130] |
| 2021-23 | 748 | -0.032 [-0.039, -0.027] | -0.067 [-0.075, -0.059] | -0.077 [-0.085, -0.069] |
| 2024 | 250 | -0.008 [-0.013, -0.001] | -0.022 [-0.027, -0.016] | -0.024 [-0.031, -0.016] |
| 2025-26 | 249 | -0.001 [-0.009, 0.008] | -0.004 [-0.015, 0.010] | -0.009 [-0.020, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.036, -0.005] | -0.038 [-0.053, -0.022] | -0.044 [-0.060, -0.028] |
| ordinary | 1603 | -0.030 [-0.039, -0.021] | -0.047 [-0.058, -0.037] | -0.054 [-0.064, -0.043] |
| quarter_end | 31 | 0.011 [-0.024, 0.049] | -0.005 [-0.041, 0.032] | -0.011 [-0.051, 0.031] |
| tax_date | 89 | -0.002 [-0.028, 0.028] | -0.030 [-0.054, -0.003] | -0.036 [-0.061, -0.008] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.019 [-0.023, -0.016] | -0.046 [-0.052, -0.040] | -0.052 [-0.059, -0.046] |
| 1 | 324 | -0.090 [-0.102, -0.076] | -0.111 [-0.123, -0.095] | -0.120 [-0.133, -0.101] |
| 2 | 41 | -0.014 [–] | 0.013 [-0.050, 0.050] | -0.020 [-0.083, 0.016] |
| 3 | 473 | -0.005 [-0.031, 0.024] | -0.003 [-0.032, 0.029] | -0.004 [-0.033, 0.024] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [0.000, 0.185] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.273] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.083 [0.000, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.095 [0.000, 0.231] |

## latent_factor_logit against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.005, 0.015] |
| 2 | 0.010 [0.001, 0.019] |
| 3 | 0.005 [-0.003, 0.014] |
| 4 | 0.002 [-0.005, 0.010] |
| 5 | 0.007 [0.000, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.026 [-0.016, 0.072] | 0.040 [0.009, 0.075] | 0.038 [0.011, 0.071] |
| 2020 | 251 | -0.010 [-0.023, -0.002] | -0.018 [-0.025, -0.012] | -0.018 [-0.026, -0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.002 [-0.002, -0.001] | -0.002 [-0.003, -0.002] |
| 2024 | 250 | -0.002 [-0.006, 0.000] | -0.003 [-0.007, -0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | 0.010 [-0.017, 0.044] | 0.003 [-0.023, 0.033] | 0.021 [-0.001, 0.049] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.029 [-0.056, -0.003] | -0.013 [-0.031, 0.002] | -0.004 [-0.017, 0.011] |
| ordinary | 1603 | 0.010 [-0.000, 0.023] | 0.009 [-0.000, 0.020] | 0.009 [0.001, 0.019] |
| quarter_end | 31 | -0.025 [-0.098, 0.040] | -0.037 [-0.096, 0.020] | -0.036 [-0.094, 0.020] |
| tax_date | 89 | -0.030 [-0.072, 0.013] | -0.022 [-0.057, 0.008] | 0.002 [-0.040, 0.043] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.001 [-0.003, -0.000] | -0.001 [-0.002, -0.001] |
| 1 | 324 | -0.005 [-0.007, -0.003] | -0.012 [-0.015, -0.010] | -0.014 [-0.017, -0.011] |
| 2 | 41 | 0.084 [–] | 0.089 [–] | 0.113 [–] |
| 3 | 473 | 0.015 [-0.019, 0.053] | 0.023 [-0.004, 0.054] | 0.031 [0.008, 0.057] |

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
| 1 | -0.007 [-0.012, -0.002] |
| 2 | -0.002 [-0.007, 0.003] |
| 3 | -0.002 [-0.008, 0.004] |
| 4 | -0.003 [-0.009, 0.002] |
| 5 | 0.001 [-0.005, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.027 [-0.045, -0.009] | 0.002 [-0.020, 0.025] | 0.014 [-0.012, 0.041] |
| 2020 | 251 | -0.004 [-0.014, 0.004] | -0.019 [-0.024, -0.015] | -0.017 [-0.022, -0.013] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.002 [-0.002, -0.001] | -0.002 [-0.003, -0.002] |
| 2024 | 250 | -0.002 [-0.007, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.003 [-0.028, 0.025] | 0.007 [-0.013, 0.033] | 0.013 [-0.007, 0.039] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.022 [-0.045, -0.000] | 0.002 [-0.011, 0.018] | 0.001 [-0.010, 0.014] |
| ordinary | 1603 | -0.003 [-0.008, 0.002] | -0.002 [-0.007, 0.005] | 0.002 [-0.004, 0.010] |
| quarter_end | 31 | -0.041 [-0.095, 0.010] | -0.047 [-0.088, -0.013] | -0.062 [-0.109, -0.022] |
| tax_date | 89 | -0.028 [-0.060, -0.001] | -0.008 [-0.024, 0.006] | 0.001 [-0.015, 0.018] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.002, -0.001] |
| 1 | 324 | -0.004 [-0.010, 0.000] | -0.013 [-0.016, -0.010] | -0.013 [-0.016, -0.010] |
| 2 | 41 | 0.035 [–] | 0.076 [–] | 0.099 [-0.013, 0.181] |
| 3 | 473 | -0.025 [-0.041, -0.010] | -0.003 [-0.021, 0.015] | 0.008 [-0.013, 0.031] |

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
| 1 | 0.019 [0.011, 0.027] |
| 2 | 0.012 [0.007, 0.017] |
| 3 | 0.009 [0.004, 0.013] |
| 4 | 0.006 [0.003, 0.010] |
| 5 | 0.008 [0.004, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.028 [-0.004, 0.062] | 0.004 [-0.014, 0.020] | 0.001 [-0.012, 0.014] |
| 2020 | 251 | 0.029 [0.014, 0.042] | 0.019 [0.011, 0.028] | 0.018 [0.011, 0.025] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.012 [0.011, 0.014] | 0.012 [0.010, 0.013] |
| 2024 | 250 | 0.002 [-0.003, 0.005] | 0.001 [-0.003, 0.004] | 0.001 [-0.004, 0.004] |
| 2025-26 | 249 | 0.026 [-0.003, 0.060] | 0.005 [-0.013, 0.026] | 0.007 [-0.008, 0.025] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.026 [0.002, 0.052] | 0.014 [0.005, 0.025] | 0.010 [0.003, 0.017] |
| ordinary | 1603 | 0.015 [0.008, 0.024] | 0.007 [0.002, 0.011] | 0.007 [0.003, 0.010] |
| quarter_end | 31 | 0.090 [-0.010, 0.193] | 0.041 [-0.067, 0.150] | 0.027 [-0.087, 0.138] |
| tax_date | 89 | 0.039 [0.007, 0.071] | 0.031 [0.008, 0.052] | 0.028 [0.005, 0.050] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.008 [0.006, 0.010] | 0.008 [0.006, 0.009] |
| 1 | 324 | 0.025 [0.016, 0.032] | 0.016 [0.011, 0.022] | 0.014 [0.009, 0.018] |
| 2 | 41 | 0.076 [–] | 0.058 [–] | 0.072 [-0.003, 0.134] |
| 3 | 473 | 0.030 [0.005, 0.059] | 0.002 [-0.013, 0.016] | 0.001 [-0.011, 0.012] |

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
| 1 | 0.003 [0.000, 0.007] |
| 2 | 0.002 [0.000, 0.004] |
| 3 | 0.003 [0.001, 0.004] |
| 4 | -0.002 [-0.004, -0.000] |
| 5 | 0.001 [-0.000, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.011 [-0.004, 0.028] | 0.004 [-0.002, 0.009] | 0.004 [-0.002, 0.009] |
| 2020 | 251 | 0.006 [0.000, 0.010] | 0.007 [0.001, 0.011] | 0.000 [-0.001, 0.001] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.002 [0.002, 0.003] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.002 [0.000, 0.005] | 0.001 [0.001, 0.002] | 0.001 [-0.000, 0.003] |
| 2025-26 | 249 | 0.000 [-0.005, 0.006] | -0.001 [-0.007, 0.005] | -0.001 [-0.003, 0.001] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.004 [-0.004, 0.013] | 0.004 [0.002, 0.007] | 0.001 [-0.001, 0.003] |
| ordinary | 1603 | 0.003 [-0.000, 0.006] | 0.002 [0.001, 0.004] | 0.001 [-0.001, 0.002] |
| quarter_end | 31 | 0.030 [0.007, 0.055] | 0.007 [0.003, 0.011] | 0.002 [-0.000, 0.005] |
| tax_date | 89 | 0.003 [-0.011, 0.019] | 0.003 [0.001, 0.006] | 0.002 [-0.000, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] | 0.000 [-0.000, 0.001] |
| 1 | 324 | 0.004 [0.001, 0.006] | 0.007 [0.005, 0.008] | 0.000 [-0.000, 0.001] |
| 2 | 41 | -0.014 [-0.076, 0.021] | 0.012 [–] | -0.004 [-0.013, 0.007] |
| 3 | 473 | 0.010 [-0.001, 0.024] | 0.002 [-0.004, 0.007] | 0.003 [-0.002, 0.007] |

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
| 1 | -0.015 [-0.029, -0.002] |
| 2 | -0.029 [-0.043, -0.012] |
| 3 | -0.034 [-0.049, -0.020] |
| 4 | -0.037 [-0.052, -0.022] |
| 5 | -0.039 [-0.052, -0.023] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.043 [-0.011, 0.099] | 0.051 [-0.001, 0.106] | 0.049 [0.000, 0.103] |
| 2020 | 251 | -0.103 [-0.114, -0.092] | -0.134 [-0.150, -0.115] | -0.137 [-0.153, -0.117] |
| 2021-23 | 748 | -0.026 [-0.032, -0.021] | -0.061 [-0.069, -0.053] | -0.068 [-0.077, -0.060] |
| 2024 | 250 | -0.009 [-0.011, -0.007] | -0.021 [-0.025, -0.016] | -0.023 [-0.027, -0.016] |
| 2025-26 | 249 | 0.012 [-0.011, 0.041] | 0.005 [-0.016, 0.031] | 0.003 [-0.017, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.006, 0.014] | -0.008 [-0.016, 0.001] | -0.010 [-0.018, -0.000] |
| ordinary | 1603 | -0.018 [-0.033, -0.002] | -0.039 [-0.056, -0.022] | -0.044 [-0.060, -0.026] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.016 [-0.019, -0.014] | -0.041 [-0.047, -0.036] | -0.046 [-0.052, -0.040] |
| 1 | 324 | -0.077 [-0.089, -0.065] | -0.112 [-0.125, -0.094] | -0.116 [-0.130, -0.099] |
| 2 | 41 | 0.058 [–] | 0.071 [–] | 0.075 [–] |
| 3 | 473 | 0.022 [-0.022, 0.069] | 0.025 [-0.021, 0.074] | 0.022 [-0.021, 0.069] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.172, 0.176] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.188, 0.312] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.111, 0.462] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.048 [-0.150, 0.250] |

## risk_gbm+latent_factor against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.027 [-0.035, -0.018] |
| 2 | -0.040 [-0.050, -0.030] |
| 3 | -0.041 [-0.053, -0.029] |
| 4 | -0.043 [-0.054, -0.030] |
| 5 | -0.044 [-0.057, -0.032] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.010 [-0.039, 0.024] | 0.013 [-0.022, 0.051] | 0.024 [-0.013, 0.062] |
| 2020 | 251 | -0.096 [-0.108, -0.084] | -0.135 [-0.148, -0.121] | -0.136 [-0.148, -0.123] |
| 2021-23 | 748 | -0.026 [-0.032, -0.021] | -0.061 [-0.069, -0.053] | -0.068 [-0.076, -0.059] |
| 2024 | 250 | -0.010 [-0.011, -0.008] | -0.021 [-0.026, -0.014] | -0.023 [-0.028, -0.016] |
| 2025-26 | 249 | -0.001 [-0.021, 0.021] | 0.009 [-0.016, 0.039] | -0.006 [-0.026, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.003, 0.022] | 0.008 [-0.011, 0.030] | -0.005 [-0.017, 0.010] |
| ordinary | 1603 | -0.032 [-0.041, -0.022] | -0.050 [-0.062, -0.037] | -0.051 [-0.064, -0.038] |
| quarter_end | 31 | -0.015 [-0.062, 0.027] | -0.010 [-0.074, 0.050] | -0.026 [-0.083, 0.026] |
| tax_date | 89 | 0.002 [-0.031, 0.031] | 0.015 [-0.009, 0.043] | -0.001 [-0.045, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.017 [-0.020, -0.014] | -0.041 [-0.047, -0.036] | -0.046 [-0.052, -0.040] |
| 1 | 324 | -0.076 [-0.086, -0.065] | -0.112 [-0.125, -0.095] | -0.116 [-0.130, -0.098] |
| 2 | 41 | 0.010 [–] | 0.057 [–] | 0.061 [–] |
| 3 | 473 | -0.018 [-0.043, 0.012] | -0.002 [-0.035, 0.034] | -0.001 [-0.038, 0.035] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.323, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.238, 0.125] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.160] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.100] |

## risk_gbm+latent_factor against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.012, 0.011] |
| 2 | -0.026 [-0.037, -0.015] |
| 3 | -0.030 [-0.041, -0.019] |
| 4 | -0.033 [-0.043, -0.023] |
| 5 | -0.037 [-0.047, -0.027] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.044 [-0.001, 0.092] | 0.014 [-0.020, 0.053] | 0.012 [-0.023, 0.044] |
| 2020 | 251 | -0.063 [-0.077, -0.049] | -0.097 [-0.111, -0.082] | -0.101 [-0.114, -0.086] |
| 2021-23 | 748 | -0.012 [-0.017, -0.008] | -0.047 [-0.055, -0.040] | -0.054 [-0.061, -0.047] |
| 2024 | 250 | -0.006 [-0.009, -0.002] | -0.017 [-0.021, -0.011] | -0.021 [-0.024, -0.018] |
| 2025-26 | 249 | 0.027 [-0.004, 0.066] | 0.007 [-0.014, 0.032] | -0.011 [-0.026, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.057 [0.032, 0.085] | 0.019 [0.005, 0.035] | 0.004 [-0.004, 0.013] |
| ordinary | 1603 | -0.013 [-0.025, -0.000] | -0.042 [-0.053, -0.029] | -0.046 [-0.058, -0.035] |
| quarter_end | 31 | 0.116 [0.037, 0.195] | 0.078 [-0.010, 0.168] | 0.063 [-0.020, 0.151] |
| tax_date | 89 | 0.069 [0.043, 0.095] | 0.053 [0.026, 0.080] | 0.026 [-0.014, 0.060] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.007 [-0.010, -0.005] | -0.032 [-0.037, -0.028] | -0.037 [-0.042, -0.032] |
| 1 | 324 | -0.048 [-0.057, -0.037] | -0.083 [-0.094, -0.070] | -0.089 [-0.100, -0.075] |
| 2 | 41 | 0.051 [–] | 0.039 [–] | 0.034 [–] |
| 3 | 473 | 0.038 [-0.001, 0.078] | 0.003 [-0.029, 0.039] | -0.009 [-0.040, 0.021] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.120, 0.207] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.259, 0.118] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.154, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.150, 0.259] |

## risk_gbm+latent_factor against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.017 [-0.026, -0.007] |
| 2 | -0.036 [-0.046, -0.026] |
| 3 | -0.037 [-0.046, -0.026] |
| 4 | -0.042 [-0.052, -0.031] |
| 5 | -0.045 [-0.055, -0.034] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.027 [-0.007, 0.066] | 0.014 [-0.017, 0.047] | 0.014 [-0.016, 0.046] |
| 2020 | 251 | -0.087 [-0.098, -0.073] | -0.108 [-0.119, -0.097] | -0.119 [-0.130, -0.106] |
| 2021-23 | 748 | -0.025 [-0.031, -0.020] | -0.057 [-0.064, -0.050] | -0.066 [-0.074, -0.058] |
| 2024 | 250 | -0.005 [-0.010, 0.000] | -0.017 [-0.023, -0.009] | -0.021 [-0.026, -0.015] |
| 2025-26 | 249 | 0.002 [-0.013, 0.020] | 0.001 [-0.017, 0.023] | -0.019 [-0.031, -0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.036 [0.012, 0.061] | 0.010 [-0.007, 0.027] | -0.005 [-0.018, 0.009] |
| ordinary | 1603 | -0.026 [-0.035, -0.017] | -0.046 [-0.056, -0.035] | -0.052 [-0.063, -0.042] |
| quarter_end | 31 | 0.055 [-0.018, 0.130] | 0.044 [-0.012, 0.101] | 0.038 [-0.018, 0.095] |
| tax_date | 89 | 0.033 [-0.001, 0.069] | 0.026 [-0.006, 0.062] | 0.000 [-0.045, 0.044] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.015 [-0.019, -0.013] | -0.038 [-0.044, -0.033] | -0.044 [-0.050, -0.038] |
| 1 | 324 | -0.068 [-0.078, -0.057] | -0.093 [-0.103, -0.079] | -0.102 [-0.114, -0.087] |
| 2 | 41 | -0.039 [–] | -0.007 [–] | -0.042 [-0.096, 0.004] |
| 3 | 473 | 0.018 [-0.014, 0.051] | 0.003 [-0.027, 0.033] | -0.006 [-0.036, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.077, 0.174] on 26 onsets.

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
| ordinary | 12 | 0.000 [-0.182, 0.215] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.091, 0.214] |

## risk_gbm+latent_factor_resid against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.016 [-0.029, -0.001] |
| 2 | -0.029 [-0.043, -0.013] |
| 3 | -0.035 [-0.049, -0.018] |
| 4 | -0.037 [-0.052, -0.022] |
| 5 | -0.039 [-0.053, -0.022] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.043 [-0.010, 0.098] | 0.051 [-0.002, 0.107] | 0.049 [0.000, 0.102] |
| 2020 | 251 | -0.103 [-0.114, -0.092] | -0.134 [-0.150, -0.114] | -0.137 [-0.154, -0.119] |
| 2021-23 | 748 | -0.026 [-0.032, -0.021] | -0.061 [-0.070, -0.053] | -0.068 [-0.077, -0.060] |
| 2024 | 250 | -0.010 [-0.011, -0.008] | -0.021 [-0.026, -0.016] | -0.023 [-0.028, -0.017] |
| 2025-26 | 249 | 0.012 [-0.011, 0.040] | 0.005 [-0.016, 0.033] | 0.003 [-0.017, 0.029] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.006, 0.015] | -0.008 [-0.016, 0.001] | -0.009 [-0.018, 0.000] |
| ordinary | 1603 | -0.018 [-0.033, -0.002] | -0.040 [-0.056, -0.020] | -0.044 [-0.060, -0.025] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.016 [-0.019, -0.014] | -0.042 [-0.047, -0.036] | -0.046 [-0.052, -0.041] |
| 1 | 324 | -0.078 [-0.088, -0.065] | -0.112 [-0.126, -0.094] | -0.116 [-0.131, -0.098] |
| 2 | 41 | 0.059 [–] | 0.071 [–] | 0.076 [-0.022, 0.128] |
| 3 | 473 | 0.023 [-0.022, 0.070] | 0.025 [-0.023, 0.076] | 0.022 [-0.021, 0.069] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.167, 0.174] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.176, 0.300] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.111, 0.455] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.048 [-0.143, 0.250] |

## risk_gbm+latent_factor_resid against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.027 [-0.036, -0.018] |
| 2 | -0.041 [-0.051, -0.030] |
| 3 | -0.042 [-0.053, -0.029] |
| 4 | -0.043 [-0.054, -0.030] |
| 5 | -0.045 [-0.057, -0.032] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.010 [-0.038, 0.022] | 0.013 [-0.021, 0.050] | 0.025 [-0.011, 0.065] |
| 2020 | 251 | -0.097 [-0.109, -0.084] | -0.135 [-0.148, -0.122] | -0.136 [-0.148, -0.123] |
| 2021-23 | 748 | -0.026 [-0.032, -0.021] | -0.061 [-0.069, -0.053] | -0.068 [-0.077, -0.060] |
| 2024 | 250 | -0.010 [-0.012, -0.008] | -0.021 [-0.026, -0.014] | -0.023 [-0.028, -0.016] |
| 2025-26 | 249 | -0.002 [-0.021, 0.021] | 0.009 [-0.017, 0.040] | -0.006 [-0.027, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.004, 0.021] | 0.008 [-0.010, 0.027] | -0.005 [-0.017, 0.009] |
| ordinary | 1603 | -0.032 [-0.041, -0.023] | -0.050 [-0.062, -0.037] | -0.051 [-0.064, -0.038] |
| quarter_end | 31 | -0.015 [-0.063, 0.026] | -0.010 [-0.071, 0.048] | -0.026 [-0.084, 0.026] |
| tax_date | 89 | 0.002 [-0.030, 0.030] | 0.015 [-0.009, 0.042] | -0.001 [-0.041, 0.038] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.017 [-0.020, -0.015] | -0.042 [-0.047, -0.036] | -0.046 [-0.052, -0.040] |
| 1 | 324 | -0.077 [-0.086, -0.065] | -0.112 [-0.126, -0.095] | -0.116 [-0.130, -0.100] |
| 2 | 41 | 0.011 [-0.121, 0.108] | 0.058 [-0.069, 0.137] | 0.062 [-0.049, 0.124] |
| 3 | 473 | -0.018 [-0.044, 0.010] | -0.001 [-0.035, 0.034] | -0.001 [-0.036, 0.036] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.333, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.125] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [–] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.095] |

## risk_gbm+latent_factor_resid against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.013, 0.011] |
| 2 | -0.026 [-0.036, -0.016] |
| 3 | -0.030 [-0.041, -0.020] |
| 4 | -0.033 [-0.043, -0.023] |
| 5 | -0.037 [-0.047, -0.027] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.044 [0.000, 0.095] | 0.015 [-0.022, 0.052] | 0.012 [-0.021, 0.046] |
| 2020 | 251 | -0.064 [-0.077, -0.049] | -0.097 [-0.111, -0.082] | -0.101 [-0.114, -0.087] |
| 2021-23 | 748 | -0.013 [-0.017, -0.008] | -0.047 [-0.055, -0.040] | -0.054 [-0.062, -0.047] |
| 2024 | 250 | -0.006 [-0.009, -0.003] | -0.018 [-0.022, -0.012] | -0.022 [-0.025, -0.018] |
| 2025-26 | 249 | 0.027 [-0.004, 0.067] | 0.007 [-0.014, 0.030] | -0.011 [-0.027, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.057 [0.031, 0.085] | 0.019 [0.005, 0.035] | 0.004 [-0.005, 0.013] |
| ordinary | 1603 | -0.014 [-0.026, -0.000] | -0.042 [-0.053, -0.029] | -0.047 [-0.058, -0.035] |
| quarter_end | 31 | 0.116 [0.035, 0.202] | 0.078 [-0.008, 0.166] | 0.063 [-0.028, 0.153] |
| tax_date | 89 | 0.069 [0.043, 0.096] | 0.053 [0.025, 0.080] | 0.026 [-0.015, 0.061] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.008 [-0.010, -0.006] | -0.032 [-0.037, -0.028] | -0.037 [-0.042, -0.033] |
| 1 | 324 | -0.048 [-0.058, -0.037] | -0.083 [-0.094, -0.070] | -0.089 [-0.101, -0.075] |
| 2 | 41 | 0.052 [–] | 0.040 [–] | 0.035 [–] |
| 3 | 473 | 0.038 [-0.003, 0.081] | 0.004 [-0.031, 0.036] | -0.008 [-0.039, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.120, 0.207] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.118] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.154, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.147, 0.250] |

## risk_gbm+latent_factor_resid against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.017 [-0.026, -0.007] |
| 2 | -0.036 [-0.046, -0.026] |
| 3 | -0.037 [-0.047, -0.027] |
| 4 | -0.042 [-0.052, -0.032] |
| 5 | -0.045 [-0.055, -0.035] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.028 [-0.006, 0.064] | 0.015 [-0.015, 0.046] | 0.014 [-0.017, 0.045] |
| 2020 | 251 | -0.087 [-0.099, -0.074] | -0.109 [-0.118, -0.097] | -0.119 [-0.129, -0.106] |
| 2021-23 | 748 | -0.026 [-0.031, -0.021] | -0.057 [-0.065, -0.050] | -0.066 [-0.074, -0.058] |
| 2024 | 250 | -0.006 [-0.011, -0.000] | -0.018 [-0.023, -0.009] | -0.021 [-0.026, -0.015] |
| 2025-26 | 249 | 0.001 [-0.014, 0.019] | 0.000 [-0.018, 0.023] | -0.019 [-0.032, -0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.036 [0.012, 0.061] | 0.010 [-0.006, 0.028] | -0.005 [-0.019, 0.009] |
| ordinary | 1603 | -0.026 [-0.035, -0.017] | -0.046 [-0.056, -0.036] | -0.053 [-0.064, -0.042] |
| quarter_end | 31 | 0.055 [-0.019, 0.129] | 0.044 [-0.014, 0.102] | 0.038 [-0.019, 0.096] |
| tax_date | 89 | 0.033 [-0.001, 0.070] | 0.026 [-0.006, 0.061] | 0.000 [-0.044, 0.046] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.016 [-0.019, -0.013] | -0.039 [-0.044, -0.033] | -0.045 [-0.051, -0.039] |
| 1 | 324 | -0.069 [-0.078, -0.058] | -0.093 [-0.104, -0.080] | -0.102 [-0.114, -0.088] |
| 2 | 41 | -0.038 [-0.125, 0.013] | -0.006 [-0.054, 0.038] | -0.041 [–] |
| 3 | 473 | 0.018 [-0.013, 0.049] | 0.004 [-0.027, 0.035] | -0.006 [-0.037, 0.024] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.074, 0.167] on 26 onsets.

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
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.091, 0.200] |

## risk_gbm+latent_factor_logit against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.002, 0.022] |
| 2 | 0.009 [0.001, 0.019] |
| 3 | 0.007 [-0.000, 0.016] |
| 4 | 0.006 [-0.002, 0.013] |
| 5 | 0.007 [0.000, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.057 [0.015, 0.106] | 0.047 [0.014, 0.082] | 0.046 [0.016, 0.079] |
| 2020 | 251 | -0.012 [-0.024, -0.004] | -0.017 [-0.023, -0.011] | -0.018 [-0.025, -0.010] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.002 [-0.002, -0.001] | -0.002 [-0.003, -0.001] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.011 [-0.005, 0.034] | 0.007 [-0.009, 0.028] | 0.011 [-0.006, 0.031] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.007 [-0.000, 0.017] | 0.002 [-0.001, 0.007] | 0.002 [-0.002, 0.007] |
| ordinary | 1603 | 0.012 [0.002, 0.025] | 0.008 [-0.000, 0.018] | 0.008 [0.000, 0.017] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, -0.000] | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] |
| 1 | 324 | -0.003 [-0.005, -0.002] | -0.012 [-0.014, -0.009] | -0.013 [-0.015, -0.010] |
| 2 | 41 | 0.049 [–] | 0.060 [–] | 0.083 [–] |
| 3 | 473 | 0.043 [0.007, 0.084] | 0.035 [0.007, 0.064] | 0.034 [0.009, 0.062] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.094, 0.243] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.188, 0.300] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.250 [-0.067, 0.533] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.095 [-0.118, 0.300] |

## risk_gbm+latent_factor_logit against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.005, 0.005] |
| 2 | -0.003 [-0.007, 0.002] |
| 3 | 0.000 [-0.005, 0.006] |
| 4 | 0.000 [-0.005, 0.006] |
| 5 | 0.001 [-0.005, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.005 [-0.016, 0.026] | 0.009 [-0.014, 0.036] | 0.022 [-0.005, 0.052] |
| 2020 | 251 | -0.005 [-0.016, 0.002] | -0.018 [-0.024, -0.014] | -0.017 [-0.022, -0.013] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.001 [-0.002, -0.001] | -0.002 [-0.003, -0.001] |
| 2024 | 250 | -0.001 [-0.001, -0.000] | -0.001 [-0.004, 0.003] | -0.000 [-0.002, 0.001] |
| 2025-26 | 249 | -0.002 [-0.017, 0.016] | 0.011 [-0.008, 0.033] | 0.002 [-0.020, 0.026] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.013 [0.002, 0.025] | 0.018 [0.000, 0.037] | 0.007 [-0.006, 0.021] |
| ordinary | 1603 | -0.001 [-0.006, 0.003] | -0.002 [-0.007, 0.003] | 0.002 [-0.004, 0.009] |
| quarter_end | 31 | -0.015 [-0.063, 0.027] | -0.010 [-0.070, 0.051] | -0.026 [-0.083, 0.027] |
| tax_date | 89 | 0.002 [-0.032, 0.030] | 0.015 [-0.010, 0.042] | -0.001 [-0.044, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] |
| 1 | 324 | -0.002 [-0.007, 0.001] | -0.012 [-0.015, -0.009] | -0.013 [-0.015, -0.010] |
| 2 | 41 | 0.001 [–] | 0.047 [–] | 0.069 [–] |
| 3 | 473 | 0.003 [-0.014, 0.021] | 0.008 [-0.011, 0.030] | 0.011 [-0.012, 0.037] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.240, 0.087] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.125] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.286, 0.273] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.000 [-0.167, 0.172] |

## risk_gbm+latent_factor_logit against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.025 [0.017, 0.035] |
| 2 | 0.011 [0.006, 0.017] |
| 3 | 0.011 [0.007, 0.016] |
| 4 | 0.010 [0.006, 0.013] |
| 5 | 0.009 [0.004, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.059 [0.023, 0.099] | 0.011 [-0.007, 0.028] | 0.009 [-0.004, 0.023] |
| 2020 | 251 | 0.027 [0.012, 0.041] | 0.020 [0.011, 0.030] | 0.018 [0.011, 0.026] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.012 [0.011, 0.014] | 0.012 [0.010, 0.013] |
| 2024 | 250 | 0.003 [-0.001, 0.007] | 0.003 [-0.000, 0.006] | 0.001 [-0.003, 0.004] |
| 2025-26 | 249 | 0.027 [-0.000, 0.056] | 0.009 [-0.007, 0.027] | -0.003 [-0.023, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.061 [0.035, 0.089] | 0.029 [0.017, 0.044] | 0.015 [0.008, 0.023] |
| ordinary | 1603 | 0.017 [0.009, 0.027] | 0.006 [0.002, 0.010] | 0.006 [0.003, 0.009] |
| quarter_end | 31 | 0.116 [0.031, 0.194] | 0.078 [-0.012, 0.170] | 0.063 [-0.028, 0.151] |
| tax_date | 89 | 0.069 [0.042, 0.096] | 0.053 [0.025, 0.082] | 0.026 [-0.018, 0.060] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.010] | 0.008 [0.006, 0.010] | 0.008 [0.006, 0.009] |
| 1 | 324 | 0.026 [0.019, 0.033] | 0.017 [0.011, 0.023] | 0.015 [0.009, 0.019] |
| 2 | 41 | 0.042 [–] | 0.029 [–] | 0.042 [–] |
| 3 | 473 | 0.058 [0.029, 0.092] | 0.013 [-0.002, 0.028] | 0.004 [-0.010, 0.017] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.056, 0.292] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.111] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.091, 0.444] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | 0.095 [-0.105, 0.316] |

## risk_gbm+latent_factor_logit against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [0.004, 0.017] |
| 2 | 0.001 [-0.002, 0.005] |
| 3 | 0.005 [0.002, 0.008] |
| 4 | 0.001 [-0.002, 0.004] |
| 5 | 0.001 [-0.002, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.042 [0.018, 0.070] | 0.011 [-0.000, 0.022] | 0.012 [0.000, 0.024] |
| 2020 | 251 | 0.004 [-0.003, 0.009] | 0.009 [0.003, 0.013] | 0.001 [-0.002, 0.003] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.003 [0.002, 0.003] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.004 [0.000, 0.008] | 0.003 [0.001, 0.007] | 0.001 [-0.000, 0.003] |
| 2025-26 | 249 | 0.001 [-0.012, 0.017] | 0.002 [-0.009, 0.017] | -0.011 [-0.023, -0.001] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.040 [0.017, 0.066] | 0.020 [0.005, 0.035] | 0.006 [-0.008, 0.019] |
| ordinary | 1603 | 0.005 [0.000, 0.010] | 0.002 [0.000, 0.004] | 0.000 [-0.001, 0.001] |
| quarter_end | 31 | 0.055 [-0.014, 0.129] | 0.044 [-0.015, 0.103] | 0.038 [-0.015, 0.096] |
| tax_date | 89 | 0.033 [-0.002, 0.070] | 0.026 [-0.006, 0.061] | 0.000 [-0.044, 0.045] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.001, 0.002] | 0.002 [0.000, 0.003] | 0.000 [0.000, 0.001] |
| 1 | 324 | 0.006 [0.003, 0.007] | 0.007 [0.005, 0.009] | 0.001 [-0.000, 0.002] |
| 2 | 41 | -0.048 [–] | -0.017 [–] | -0.034 [–] |
| 3 | 473 | 0.038 [0.017, 0.062] | 0.013 [0.003, 0.023] | 0.006 [-0.005, 0.017] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [0.000, 0.250] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [0.000, 0.231] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | 0.095 [0.000, 0.250] |

