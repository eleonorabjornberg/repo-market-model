Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_net | 14 of 26 | 0.538 [0.360, 0.722] | 0.231 | 3.38 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic+recalibrated | 11 of 26 | 0.423 [0.250, 0.586] | 0.231 | 3.54 | 0.2 / 0.3 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic_net+recalibrated | 11 of 26 | 0.423 [0.250, 0.591] | 0.231 | 2.81 | 0.2 / 0.7 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic_net | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.76 (17) | 0.58 (101) | 0.56 (9) | 0.69 (13) |
| onset_logistic+recalibrated | 0.52 (102) | 0.00 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.36 (101) | 0.67 (9) | 0.46 (13) |
| onset_logistic_net+recalibrated | 0.51 (102) | 0.00 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.34 (101) | 0.67 (9) | 0.54 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| hierarchical_logistic_net | +0.0250 [+0.0039, +0.0472] | +0.0150 [+0.0019, +0.0268] | +0.0135 [+0.0118, +0.0154] | +0.0015 [-0.0029, +0.0053] | +0.0365 [+0.0080, +0.0740] | +0.0425 [+0.0218, +0.0667] | +0.0118 [+0.0059, +0.0180] | +0.1078 [+0.0596, +0.1528] | +0.0463 [+0.0247, +0.0688] |
| onset_logistic+recalibrated | +0.0046 [-0.0073, +0.0158] | +0.0189 [+0.0073, +0.0292] | +0.0100 [+0.0085, +0.0116] | +0.0041 [+0.0015, +0.0066] | +0.0087 [+0.0018, +0.0174] | +0.0242 [+0.0110, +0.0400] | +0.0048 [+0.0019, +0.0077] | +0.0670 [+0.0163, +0.1153] | +0.0413 [+0.0262, +0.0582] |
| onset_logistic_net+recalibrated | +0.0042 [-0.0072, +0.0156] | +0.0107 [-0.0056, +0.0255] | +0.0100 [+0.0085, +0.0117] | +0.0036 [+0.0009, +0.0057] | +0.0085 [+0.0024, +0.0160] | +0.0245 [+0.0110, +0.0390] | +0.0035 [+0.0003, +0.0065] | +0.0575 [+0.0055, +0.1067] | +0.0425 [+0.0278, +0.0578] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
