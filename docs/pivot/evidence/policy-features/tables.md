Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic+recalibrated | 11 of 26 | 0.423 [0.250, 0.586] | 0.231 | 3.54 | 0.2 / 0.3 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic_policy+recalibrated | 15 of 26 | 0.577 [0.406, 0.742] | 0.231 | 3.23 | 0.5 / 1.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| rare_gbm_balanced_bootstrap+recalibrated | 7 of 26 | 0.269 [0.105, 0.438] | 0.115 | 1.19 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 6 of 26 | 0.231 [0.087, 0.375] | 0.154 | 1.65 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| onset_logistic+recalibrated | 0.52 (102) | 0.00 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.36 (101) | 0.67 (9) | 0.46 (13) |
| onset_logistic_policy+recalibrated | 0.48 (102) | 0.75 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.39 (101) | 0.56 (9) | 0.54 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| rare_gbm_balanced_bootstrap+recalibrated | 0.22 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.24 (17) | 0.16 (101) | 0.33 (9) | 0.08 (13) |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 0.14 (102) | 0.00 (4) | – | 0.00 (5) | 0.14 (29) | 0.29 (17) | 0.10 (101) | 0.22 (9) | 0.08 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| onset_logistic+recalibrated | +0.0046 [-0.0073, +0.0158] | +0.0189 [+0.0073, +0.0292] | +0.0100 [+0.0085, +0.0116] | +0.0041 [+0.0015, +0.0066] | +0.0087 [+0.0018, +0.0174] | +0.0242 [+0.0110, +0.0400] | +0.0048 [+0.0019, +0.0077] | +0.0670 [+0.0163, +0.1153] | +0.0413 [+0.0262, +0.0582] |
| onset_logistic_policy+recalibrated | +0.0145 [+0.0049, +0.0246] | +0.0280 [+0.0186, +0.0371] | +0.0100 [+0.0080, +0.0120] | +0.0046 [+0.0013, +0.0083] | +0.0214 [+0.0059, +0.0411] | +0.0343 [+0.0174, +0.0539] | +0.0093 [+0.0066, +0.0123] | +0.0695 [+0.0099, +0.1262] | +0.0475 [+0.0329, +0.0648] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| rare_gbm_balanced_bootstrap+recalibrated | -0.0221 [-0.0739, +0.0258] | +0.0314 [+0.0235, +0.0393] | +0.0136 [+0.0120, +0.0155] | +0.0018 [-0.0023, +0.0051] | +0.0255 [+0.0079, +0.0479] | +0.0380 [+0.0172, +0.0604] | +0.0016 [-0.0109, +0.0124] | +0.1263 [+0.0343, +0.2181] | +0.0503 [+0.0322, +0.0691] |
| rare_gbm_balanced_bootstrap_policy+recalibrated | -0.0304 [-0.0795, +0.0140] | +0.0307 [+0.0221, +0.0382] | +0.0136 [+0.0119, +0.0154] | +0.0039 [+0.0002, +0.0071] | +0.0274 [+0.0042, +0.0555] | +0.0349 [+0.0153, +0.0576] | +0.0016 [-0.0112, +0.0127] | +0.1161 [+0.0356, +0.1923] | +0.0320 [+0.0099, +0.0524] |
