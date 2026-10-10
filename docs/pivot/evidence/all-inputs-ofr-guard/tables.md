Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| all_inputs_gbm+recalibrated | 16 of 26 | 0.615 [0.423, 0.806] | 0.231 | 3.54 | 0.2 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| all_inputs_logistic+recalibrated | 13 of 26 | 0.500 [0.333, 0.682] | 0.231 | 3.54 | 0.5 / 0.0 | 1 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 | 1.2 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| all_inputs_gbm+recalibrated | 0.57 (102) | 0.50 (4) | – | 0.00 (5) | 0.14 (29) | 0.53 (17) | 0.45 (101) | 0.33 (9) | 0.54 (13) |
| all_inputs_logistic+recalibrated | 0.56 (102) | 0.25 (4) | – | 0.00 (5) | 0.10 (29) | 0.53 (17) | 0.41 (101) | 0.56 (9) | 0.46 (13) |
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| all_inputs_gbm+recalibrated | +0.0017 [-0.0115, +0.0147] | -0.0001 [-0.0095, +0.0101] | +0.0095 [+0.0081, +0.0110] | +0.0019 [-0.0022, +0.0049] | +0.0133 [+0.0010, +0.0287] | +0.0248 [+0.0101, +0.0410] | +0.0010 [-0.0020, +0.0040] | +0.0656 [-0.0057, +0.1476] | +0.0464 [+0.0210, +0.0704] |
| all_inputs_logistic+recalibrated | +0.0072 [-0.0046, +0.0188] | -0.0098 [-0.0196, -0.0002] | +0.0058 [+0.0045, +0.0071] | +0.0030 [+0.0011, +0.0046] | +0.0089 [+0.0034, +0.0156] | +0.0127 [-0.0026, +0.0285] | +0.0016 [-0.0010, +0.0041] | +0.0204 [-0.0355, +0.0694] | +0.0272 [+0.0073, +0.0441] |
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
