Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41 | 15 of 26 | 0.577 [0.417, 0.741] | 0.192 | 2.35 | 1.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb | 16 of 26 | 0.615 [0.440, 0.786] | 0.192 | 2.35 | 1.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.115 | 1.35 | 0.5 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.25 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb | 0.34 (102) | 0.50 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+every_day+gate+settle+h41+iorb | +0.0442 [+0.0158, +0.0733] | +0.0350 [+0.0212, +0.0466] | +0.0136 [+0.0119, +0.0155] | -0.0058 [-0.0174, +0.0034] | +0.0264 [+0.0024, +0.0563] | +0.0595 [+0.0347, +0.0862] | +0.0136 [+0.0073, +0.0208] | +0.1247 [+0.0432, +0.2095] | +0.0689 [+0.0395, +0.0976] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
