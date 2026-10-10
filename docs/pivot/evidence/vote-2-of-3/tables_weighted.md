Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.358 | 6.69 | 2.9 / 4.7 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.319 | 6.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.231 | 4.08 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.380 | 7.04 | 1.2 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 0.269 | 4.81 | 0.2 / 0.0 | 4 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| vote_2_of_3 | 15 of 26 | 0.577 [0.389, 0.750] | 0.235 | 4.27 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers yes / no / yes) | fail (no / no / yes) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| hierarchical_logistic | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.55 (29) | 0.71 (17) | 0.64 (101) | 0.56 (9) | 0.69 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| two_part_gbm | 0.53 (102) | 0.25 (4) | – | 0.00 (5) | 0.45 (29) | 0.59 (17) | 0.47 (101) | 0.44 (9) | 0.54 (13) |
| vote_2_of_3 | 0.60 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.65 (17) | 0.50 (101) | 0.56 (9) | 0.54 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| two_part_gbm | +0.0459 [+0.0147, +0.0821] | +0.0338 [+0.0187, +0.0466] | +0.0138 [+0.0121, +0.0157] | +0.0016 [-0.0029, +0.0052] | +0.0185 [-0.0013, +0.0446] | +0.0499 [+0.0247, +0.0784] | +0.0149 [+0.0077, +0.0231] | +0.1213 [+0.0296, +0.2096] | +0.0672 [+0.0447, +0.0923] |
| vote_2_of_3 | +0.0016 [-0.0503, +0.0495] | +0.0279 [+0.0113, +0.0416] | +0.0138 [+0.0121, +0.0157] | +0.0030 [-0.0003, +0.0058] | +0.0350 [+0.0091, +0.0687] | +0.0377 [+0.0081, +0.0694] | +0.0079 [-0.0034, +0.0187] | +0.1190 [+0.0381, +0.2042] | +0.0601 [+0.0254, +0.0915] |
