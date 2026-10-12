Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.7 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb | 19 of 26 | 0.731 [0.560, 0.889] | 0.382 | 7.08 flat / 3.46 weighted (tier 1 on the weighted count) | 3.4 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | 18 of 26 | 0.692 [0.518, 0.852] | 0.349 | 6.54 flat / 3.23 weighted (tier 1 on the weighted count) | 1.2 / 0.3 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | 18 of 26 | 0.692 [0.519, 0.857] | 0.299 | 6.31 flat / 2.88 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 1b. Tier 1 at each lead alone, inside and outside the early years, and the recall with equal weight per regime: reported for every model, not part of the pass rule.

calendar_climatology:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.667] | 6.692 [4.583, 10.002] | 3.750 [2.485, 5.938] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.538 [3.440, 8.668] | 3.173 [1.975, 5.211] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.577 [3.464, 8.734] | 3.212 [1.990, 5.282] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.615 [3.500, 8.739] | 3.250 [2.012, 5.360] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.654 [3.516, 8.811] | 3.288 [2.033, 5.400] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.765 [5.086, 12.286] | 3.324 [2.034, 5.576] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 5.111 (no interval) | 5.000 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

persistence_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.233, 0.609] | 7.038 [4.823, 10.000] | 3.250 [2.032, 4.952] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.444] | 4.769 [2.961, 7.201] | 2.067 [1.193, 3.329] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.206, 0.567] | 5.923 [3.750, 8.714] | 2.683 [1.527, 4.207] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.136, 0.500] | 5.385 [3.275, 8.160] | 2.375 [1.310, 3.931] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.481] | 4.538 [2.761, 7.000] | 1.856 [1.083, 2.962] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.880] | 8.471 [5.500, 13.182] | 3.706 [2.208, 6.083] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 8.444 (no interval) | 4.806 (no interval) |

Recall with equal weight per regime: 0.287 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 0/5).

risk_gbm+every_day+gate+settle+h41+iorb:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.367, 0.704] | 3.654 [2.621, 5.105] | 1.625 [1.121, 2.425] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.652] | 3.308 [2.171, 4.786] | 1.404 [0.946, 2.063] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 3.462 [2.216, 5.159] | 1.452 [0.942, 2.219] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.265, 0.667] | 3.462 [2.216, 5.111] | 1.500 [1.000, 2.234] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.762] | 3.500 [2.219, 5.200] | 1.644 [1.087, 2.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.967] | 5.412 [3.360, 8.309] | 2.015 [1.250, 3.143] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 10.222 (no interval) | 6.194 (no interval) |

Recall with equal weight per regime: 0.641 (2018-19 13/17, 2020 2/2, 2024 0/2, 2025-26 4/5).

risk_gbm+every_day+gate+settle+h41+iorb+state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.632] | 3.423 [2.087, 5.389] | 1.385 [0.766, 2.366] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.346 [2.805, 6.545] | 2.317 [1.419, 3.708] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.846 [2.451, 5.895] | 1.913 [1.181, 3.050] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.658] | 3.962 [2.520, 5.957] | 2.019 [1.243, 3.250] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.350, 0.727] | 3.577 [2.240, 5.500] | 1.942 [1.184, 3.119] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 0.952] | 6.471 [3.998, 10.376] | 2.662 [1.544, 4.600] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.222, 0.833] | 6.667 [3.667, 14.752] | 4.306 [2.229, 10.335] |

Recall with equal weight per regime: 0.591 (2018-19 13/17, 2020 2/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.294, 0.640] | 3.385 [1.999, 5.334] | 1.346 [0.700, 2.326] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.290, 0.650] | 3.769 [2.333, 5.857] | 1.865 [1.068, 3.126] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 3.538 [2.195, 5.476] | 1.606 [0.967, 2.565] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.885 [2.517, 5.810] | 1.788 [1.135, 2.773] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.350, 0.727] | 3.577 [2.241, 5.444] | 1.702 [1.046, 2.650] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.471 [3.958, 10.215] | 2.662 [1.528, 4.517] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.249, 0.833] | 6.000 [3.461, 11.750] | 3.278 [1.722, 6.813] |

Recall with equal weight per regime: 0.591 (2018-19 13/17, 2020 2/2, 2024 0/2, 2025-26 3/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb | 0.59 (102) | 0.50 (4) | – | 0.00 (5) | 0.69 (29) | 0.82 (17) | 0.54 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | 0.63 (102) | 0.50 (4) | – | 0.00 (5) | 0.48 (29) | 0.88 (17) | 0.52 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | 0.63 (102) | 0.50 (4) | – | 0.00 (5) | 0.59 (29) | 0.88 (17) | 0.55 (101) | 0.44 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| risk_gbm+every_day+gate+settle+h41+iorb | +0.0442 [+0.0158, +0.0733] | +0.0350 [+0.0212, +0.0466] | +0.0136 [+0.0118, +0.0154] | -0.0056 [-0.0171, +0.0035] | +0.0258 [+0.0024, +0.0550] | +0.0579 [+0.0339, +0.0839] | +0.0135 [+0.0073, +0.0208] | +0.1309 [+0.0525, +0.2116] | +0.0683 [+0.0375, +0.0976] |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | +0.0492 [+0.0274, +0.0744] | +0.0193 [+0.0134, +0.0252] | +0.0052 [+0.0027, +0.0078] | -0.0049 [-0.0113, -0.0002] | +0.0370 [+0.0086, +0.0692] | +0.0419 [+0.0175, +0.0678] | +0.0125 [+0.0064, +0.0193] | +0.1142 [+0.0468, +0.1840] | +0.0598 [+0.0413, +0.0804] |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | +0.0492 [+0.0262, +0.0722] | +0.0307 [+0.0219, +0.0392] | +0.0134 [+0.0118, +0.0151] | +0.0010 [-0.0042, +0.0053] | +0.0385 [+0.0104, +0.0740] | +0.0537 [+0.0293, +0.0833] | +0.0175 [+0.0116, +0.0237] | +0.1178 [+0.0430, +0.1967] | +0.0701 [+0.0493, +0.0906] |
