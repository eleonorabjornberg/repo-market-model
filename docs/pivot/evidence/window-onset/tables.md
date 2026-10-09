Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| window_onset_gbm+recalibrated | 10 of 26 | 0.385 [0.214, 0.567] | 0.192 | 2.42 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| window_onset_hierarchical_logistic+recalibrated | 10 of 26 | 0.385 [0.222, 0.559] | 0.258 | 4.46 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| published_v1 | 0.51 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.47 (101) | 0.33 (9) | 0.38 (13) |
| window_onset_gbm+recalibrated | 0.14 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.35 (17) | 0.08 (101) | 0.00 (9) | 0.08 (13) |
| window_onset_hierarchical_logistic+recalibrated | 0.54 (102) | 0.00 (4) | – | 0.00 (5) | 0.24 (29) | 0.76 (17) | 0.42 (101) | 0.33 (9) | 0.31 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| published_v1 | +0.0460 [+0.0127, +0.0833] | +0.0328 [+0.0266, +0.0391] | +0.0127 [+0.0111, +0.0144] | +0.0010 [-0.0043, +0.0050] | +0.0229 [-0.0053, +0.0574] | +0.0421 [+0.0202, +0.0713] | +0.0169 [+0.0088, +0.0259] | +0.0922 [+0.0137, +0.1746] | +0.0534 [+0.0285, +0.0795] |
| window_onset_gbm+recalibrated | -0.0556 [-0.1009, -0.0109] | -0.0970 [-0.1486, -0.0532] | +0.0071 [+0.0059, +0.0085] | +0.0011 [-0.0034, +0.0044] | +0.0130 [-0.0067, +0.0379] | +0.0015 [-0.0214, +0.0264] | -0.0268 [-0.0414, -0.0135] | +0.0473 [-0.0445, +0.1372] | +0.0555 [+0.0250, +0.0975] |
| window_onset_hierarchical_logistic+recalibrated | -0.0386 [-0.0820, -0.0006] | -0.1095 [-0.1679, -0.0550] | +0.0116 [+0.0101, +0.0132] | +0.0023 [-0.0013, +0.0051] | +0.0344 [-0.0038, +0.0824] | +0.0136 [-0.0190, +0.0512] | -0.0189 [-0.0350, -0.0046] | +0.0519 [-0.0215, +0.1225] | +0.0282 [+0.0077, +0.0475] |
