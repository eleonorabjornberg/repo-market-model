Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_fed_repo | 14 of 26 | 0.538 [0.368, 0.711] | 0.231 | 3.73 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic_srf | 15 of 26 | 0.577 [0.389, 0.741] | 0.231 | 3.81 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic_fed_repo | 0.60 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.48 (101) | 0.56 (9) | 0.62 (13) |
| hierarchical_logistic_srf | 0.53 (102) | 0.00 (4) | – | 0.00 (5) | 0.41 (29) | 0.59 (17) | 0.43 (101) | 0.56 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| published_v1 | 0.51 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.47 (101) | 0.33 (9) | 0.38 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| hierarchical_logistic_fed_repo | +0.0190 [-0.0015, +0.0425] | +0.0186 [+0.0094, +0.0270] | +0.0130 [+0.0114, +0.0146] | +0.0015 [-0.0032, +0.0052] | +0.0322 [+0.0077, +0.0625] | +0.0332 [+0.0139, +0.0543] | +0.0108 [+0.0057, +0.0168] | +0.0896 [+0.0290, +0.1456] | +0.0545 [+0.0341, +0.0760] |
| hierarchical_logistic_srf | +0.0212 [+0.0016, +0.0433] | +0.0180 [+0.0084, +0.0260] | +0.0131 [+0.0114, +0.0148] | +0.0015 [-0.0030, +0.0052] | +0.0366 [+0.0081, +0.0709] | +0.0356 [+0.0132, +0.0600] | +0.0116 [+0.0059, +0.0178] | +0.0952 [+0.0340, +0.1534] | +0.0534 [+0.0312, +0.0756] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| published_v1 | +0.0460 [+0.0127, +0.0833] | +0.0328 [+0.0266, +0.0391] | +0.0127 [+0.0111, +0.0144] | +0.0010 [-0.0043, +0.0050] | +0.0229 [-0.0053, +0.0574] | +0.0421 [+0.0202, +0.0713] | +0.0169 [+0.0088, +0.0259] | +0.0922 [+0.0137, +0.1746] | +0.0534 [+0.0285, +0.0795] |
