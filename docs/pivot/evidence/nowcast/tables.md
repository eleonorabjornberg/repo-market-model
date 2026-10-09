Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1_nowcast | 4 of 26 | 0.154 [0.031, 0.294] | 0.192 | 2.38 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1_nowcast_substituted | 6 of 26 | 0.231 [0.086, 0.389] | 0.231 | 2.96 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| published_v1 | 0.51 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.47 (101) | 0.33 (9) | 0.38 (13) |
| published_v1_nowcast | 0.43 (102) | 0.00 (4) | – | 0.00 (5) | 0.38 (29) | 0.53 (17) | 0.42 (101) | 0.22 (9) | 0.15 (13) |
| published_v1_nowcast_substituted | 0.50 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.18 (17) | 0.44 (101) | 0.22 (9) | 0.31 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| published_v1 | +0.0460 [+0.0127, +0.0833] | +0.0328 [+0.0266, +0.0391] | +0.0127 [+0.0111, +0.0144] | +0.0010 [-0.0043, +0.0050] | +0.0229 [-0.0053, +0.0574] | +0.0421 [+0.0202, +0.0713] | +0.0169 [+0.0088, +0.0259] | +0.0922 [+0.0137, +0.1746] | +0.0534 [+0.0285, +0.0795] |
| published_v1_nowcast | +0.0449 [+0.0115, +0.0809] | +0.0317 [+0.0251, +0.0383] | +0.0126 [+0.0111, +0.0145] | +0.0012 [-0.0038, +0.0048] | +0.0275 [-0.0029, +0.0657] | +0.0443 [+0.0212, +0.0739] | +0.0170 [+0.0090, +0.0262] | +0.0895 [+0.0062, +0.1759] | +0.0522 [+0.0268, +0.0783] |
| published_v1_nowcast_substituted | +0.0405 [+0.0087, +0.0763] | +0.0126 [+0.0021, +0.0215] | +0.0130 [+0.0114, +0.0149] | +0.0019 [-0.0020, +0.0051] | +0.0165 [-0.0015, +0.0386] | +0.0260 [+0.0107, +0.0430] | +0.0139 [+0.0062, +0.0230] | +0.0698 [-0.0168, +0.1592] | +0.0485 [+0.0284, +0.0722] |
