Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 2.46 | 0.0 / 0.0 | 4 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| vote_2_of_3 | 15 of 26 | 0.577 [0.389, 0.750] | 0.192 | 2.19 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| two_part_gbm | 0.25 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.47 (17) | 0.16 (101) | 0.44 (9) | 0.38 (13) |
| vote_2_of_3 | 0.53 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| two_part_gbm | +0.0459 [+0.0147, +0.0821] | +0.0338 [+0.0187, +0.0466] | +0.0138 [+0.0121, +0.0157] | +0.0016 [-0.0029, +0.0052] | +0.0185 [-0.0013, +0.0446] | +0.0499 [+0.0247, +0.0784] | +0.0149 [+0.0077, +0.0231] | +0.1213 [+0.0296, +0.2096] | +0.0672 [+0.0447, +0.0923] |
| vote_2_of_3 | +0.0469 [+0.0144, +0.0822] | +0.0394 [+0.0313, +0.0473] | +0.0138 [+0.0121, +0.0157] | +0.0030 [-0.0003, +0.0058] | +0.0284 [+0.0085, +0.0543] | +0.0414 [+0.0177, +0.0674] | +0.0179 [+0.0108, +0.0260] | +0.1477 [+0.0662, +0.2336] | +0.0701 [+0.0475, +0.0942] |
