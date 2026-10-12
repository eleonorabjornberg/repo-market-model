Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted (tier 1 on the flat count) | 2.4 / 4.4 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb | 16 of 26 | 0.615 [0.440, 0.786] | 0.250 | 4.38 flat / 2.07 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | 14 of 26 | 0.538 [0.364, 0.720] | 0.231 | 3.38 flat / 1.50 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | 14 of 26 | 0.538 [0.360, 0.714] | 0.231 | 3.54 flat / 1.54 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 1b. Tier 1 at each lead alone, inside and outside the early years, and the recall with equal weight per regime: reported for every model, not part of the pass rule.

calendar_climatology:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.536] | 4.846 [3.129, 7.438] | 2.798 [1.804, 4.484] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 4.885 [3.069, 7.601] | 2.712 [1.716, 4.351] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 4.923 [3.100, 7.667] | 2.731 [1.728, 4.392] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 4.962 [3.115, 7.709] | 2.750 [1.743, 4.441] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.000 [3.125, 7.751] | 2.769 [1.750, 4.472] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.846] | 6.235 [3.684, 10.417] | 2.618 [1.433, 4.614] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 3.778 (no interval) | 3.667 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

persistence_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.038, 0.300] | 2.769 [1.708, 4.218] | 0.875 [0.522, 1.347] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.077, 0.400] | 3.423 [2.087, 5.167] | 1.173 [0.742, 1.750] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.080, 0.393] | 2.808 [1.524, 4.517] | 1.115 [0.576, 1.855] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 3.154 [1.848, 5.000] | 1.173 [0.676, 1.888] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.061, 0.345] | 2.808 [1.467, 4.684] | 1.125 [0.558, 1.921] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.188, 0.667] | 6.176 [3.625, 10.183] | 2.441 [1.336, 4.208] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 4.889 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.103 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_gbm+every_day+gate+settle+h41+iorb:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.677] | 0.808 [0.440, 1.280] | 0.337 [0.173, 0.548] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.216, 0.565] | 1.731 [1.048, 2.650] | 0.692 [0.422, 1.088] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 1.769 [1.087, 2.760] | 0.788 [0.467, 1.279] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 1.577 [0.944, 2.423] | 0.654 [0.391, 1.044] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.346 [1.458, 3.643] | 1.135 [0.724, 1.765] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.428, 0.867] | 3.647 [2.125, 5.938] | 1.441 [0.833, 2.400] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.778 (no interval) | 3.250 (no interval) |

Recall with equal weight per regime: 0.562 (2018-19 11/17, 2020 2/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+gate+settle+h41+iorb+state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.179, 0.519] | 0.538 [0.238, 0.938] | 0.269 [0.125, 0.479] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 1.577 [0.823, 2.684] | 0.615 [0.321, 1.050] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 1.615 [0.912, 2.640] | 0.702 [0.386, 1.190] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.563] | 1.462 [0.821, 2.389] | 0.615 [0.350, 1.025] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 1.769 [0.970, 2.905] | 0.769 [0.431, 1.250] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.875] | 3.706 [2.157, 6.200] | 1.515 [0.852, 2.635] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 2.778 [1.133, 6.800] | 1.472 [0.591, 3.689] |

Recall with equal weight per regime: 0.387 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 0.577 [0.273, 0.958] | 0.250 [0.112, 0.438] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.567] | 1.462 [0.773, 2.417] | 0.587 [0.310, 1.000] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.567] | 2.000 [1.147, 3.218] | 0.817 [0.483, 1.333] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.567] | 1.769 [1.000, 2.842] | 0.712 [0.421, 1.146] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 2.077 [1.136, 3.375] | 0.856 [0.484, 1.369] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.875] | 3.706 [2.074, 6.143] | 1.515 [0.842, 2.539] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.222 [1.363, 7.202] | 1.583 [0.679, 3.643] |

Recall with equal weight per regime: 0.387 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb | 0.34 (102) | 0.50 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | 0.24 (102) | 0.50 (4) | – | 0.00 (5) | 0.21 (29) | 0.35 (17) | 0.18 (101) | 0.44 (9) | 0.31 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | 0.24 (102) | 0.50 (4) | – | 0.00 (5) | 0.31 (29) | 0.41 (17) | 0.20 (101) | 0.44 (9) | 0.31 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| risk_gbm+every_day+gate+settle+h41+iorb | +0.0442 [+0.0158, +0.0733] | +0.0350 [+0.0212, +0.0466] | +0.0136 [+0.0118, +0.0154] | -0.0056 [-0.0171, +0.0035] | +0.0258 [+0.0024, +0.0550] | +0.0579 [+0.0339, +0.0839] | +0.0135 [+0.0073, +0.0208] | +0.1309 [+0.0525, +0.2116] | +0.0683 [+0.0375, +0.0976] |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | +0.0492 [+0.0274, +0.0744] | +0.0193 [+0.0134, +0.0252] | +0.0052 [+0.0027, +0.0078] | -0.0049 [-0.0113, -0.0002] | +0.0370 [+0.0086, +0.0692] | +0.0419 [+0.0175, +0.0678] | +0.0125 [+0.0064, +0.0193] | +0.1142 [+0.0468, +0.1840] | +0.0598 [+0.0413, +0.0804] |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | +0.0492 [+0.0262, +0.0722] | +0.0307 [+0.0219, +0.0392] | +0.0134 [+0.0118, +0.0151] | +0.0010 [-0.0042, +0.0053] | +0.0385 [+0.0104, +0.0740] | +0.0537 [+0.0293, +0.0833] | +0.0175 [+0.0116, +0.0237] | +0.1178 [+0.0430, +0.1967] | +0.0701 [+0.0493, +0.0906] |
