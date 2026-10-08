Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| onset_gbm_class_weight+recalibrated | 8 of 26 | 0.308 [0.143, 0.482] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| onset_gbm_class_weight_funding+recalibrated | 8 of 26 | 0.308 [0.143, 0.500] | 0.231 | 3.38 | 0.2 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| onset_gbm_focal+recalibrated | 10 of 26 | 0.385 [0.208, 0.565] | 0.231 | 2.85 | 0.2 / 0.3 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| onset_logistic+recalibrated | 11 of 26 | 0.423 [0.250, 0.586] | 0.231 | 3.54 | 0.2 / 0.3 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic_class_weight+recalibrated | 6 of 26 | 0.231 [0.091, 0.381] | 0.115 | 0.81 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| onset_logistic_class_weight_funding+recalibrated | 5 of 26 | 0.192 [0.062, 0.333] | 0.115 | 0.77 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| onset_gbm_class_weight+recalibrated | 0.46 (102) | 0.00 (4) | – | 0.00 (5) | 0.00 (29) | 0.41 (17) | 0.34 (101) | 0.11 (9) | 0.38 (13) |
| onset_gbm_class_weight_funding+recalibrated | 0.46 (102) | 0.00 (4) | – | 0.00 (5) | 0.00 (29) | 0.41 (17) | 0.34 (101) | 0.11 (9) | 0.38 (13) |
| onset_gbm_focal+recalibrated | 0.31 (102) | 0.00 (4) | – | 0.00 (5) | 0.00 (29) | 0.41 (17) | 0.20 (101) | 0.00 (9) | 0.38 (13) |
| onset_logistic+recalibrated | 0.52 (102) | 0.00 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.36 (101) | 0.67 (9) | 0.46 (13) |
| onset_logistic_class_weight+recalibrated | 0.08 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.18 (17) | 0.05 (101) | 0.33 (9) | 0.15 (13) |
| onset_logistic_class_weight_funding+recalibrated | 0.08 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.24 (17) | 0.06 (101) | 0.22 (9) | 0.08 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| published_v1 | 0.51 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.47 (101) | 0.33 (9) | 0.38 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| onset_gbm_class_weight+recalibrated | -0.0106 [-0.0256, +0.0041] | +0.0026 [-0.0048, +0.0097] | +0.0078 [+0.0066, +0.0090] | +0.0012 [-0.0020, +0.0037] | -0.0052 [-0.0112, -0.0006] | +0.0091 [-0.0017, +0.0196] | -0.0017 [-0.0045, +0.0007] | +0.0060 [-0.1023, +0.1222] | +0.0297 [+0.0063, +0.0508] |
| onset_gbm_class_weight_funding+recalibrated | -0.0106 [-0.0248, +0.0034] | +0.0026 [-0.0049, +0.0099] | +0.0078 [+0.0066, +0.0090] | +0.0011 [-0.0022, +0.0037] | -0.0047 [-0.0111, +0.0001] | +0.0090 [-0.0010, +0.0214] | -0.0015 [-0.0043, +0.0009] | +0.0012 [-0.1133, +0.1156] | +0.0294 [+0.0061, +0.0502] |
| onset_gbm_focal+recalibrated | -0.0000 [-0.0109, +0.0112] | +0.0009 [-0.0076, +0.0091] | +0.0081 [+0.0068, +0.0094] | +0.0010 [-0.0020, +0.0035] | -0.0011 [-0.0046, +0.0023] | +0.0141 [+0.0049, +0.0244] | +0.0001 [-0.0021, +0.0022] | +0.0303 [-0.0714, +0.1348] | +0.0340 [+0.0098, +0.0543] |
| onset_logistic+recalibrated | +0.0046 [-0.0073, +0.0158] | +0.0189 [+0.0073, +0.0292] | +0.0100 [+0.0085, +0.0116] | +0.0041 [+0.0015, +0.0066] | +0.0087 [+0.0018, +0.0174] | +0.0242 [+0.0110, +0.0400] | +0.0048 [+0.0019, +0.0077] | +0.0670 [+0.0163, +0.1153] | +0.0413 [+0.0262, +0.0582] |
| onset_logistic_class_weight+recalibrated | -0.0222 [-0.0825, +0.0282] | +0.0194 [+0.0074, +0.0300] | +0.0116 [+0.0100, +0.0134] | +0.0051 [+0.0027, +0.0080] | +0.0162 [-0.0038, +0.0409] | +0.0251 [+0.0073, +0.0457] | -0.0007 [-0.0143, +0.0102] | +0.0954 [+0.0558, +0.1377] | +0.0562 [+0.0270, +0.0916] |
| onset_logistic_class_weight_funding+recalibrated | -0.0222 [-0.0818, +0.0297] | +0.0202 [+0.0080, +0.0316] | +0.0128 [+0.0112, +0.0145] | +0.0051 [+0.0022, +0.0083] | +0.0182 [-0.0047, +0.0468] | +0.0310 [+0.0103, +0.0558] | -0.0002 [-0.0147, +0.0108] | +0.0936 [+0.0541, +0.1289] | +0.0560 [+0.0283, +0.0916] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| published_v1 | +0.0460 [+0.0127, +0.0833] | +0.0328 [+0.0266, +0.0391] | +0.0127 [+0.0111, +0.0144] | +0.0010 [-0.0043, +0.0050] | +0.0229 [-0.0053, +0.0574] | +0.0421 [+0.0202, +0.0713] | +0.0169 [+0.0088, +0.0259] | +0.0922 [+0.0137, +0.1746] | +0.0534 [+0.0285, +0.0795] |
