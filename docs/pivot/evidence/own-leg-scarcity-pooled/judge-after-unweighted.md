# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `d0d268dc1c82…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

## calendar_climatology (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.212, 0.576] | 0.269 | 5.00 flat / 2.77 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

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

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.286 (105 of 1873 days never flag) | 198 | 0.514 | 0.364 | 0.0714 | +0.0000 [+0.0000, +0.0000] | -0.0151 [-0.0211, -0.0097] | 0.586 | 0.442 | no |
| 2 | 0.286 (147 of 1872 days never flag) | 196 | 0.496 | 0.352 | 0.0711 | +0.0000 [+0.0000, +0.0000] | -0.0100 [-0.0146, -0.0054] | 0.586 | 0.423 | no |
| 3 | 0.286 (147 of 1871 days never flag) | 196 | 0.493 | 0.347 | 0.0707 | +0.0000 [+0.0000, +0.0000] | -0.0063 [-0.0098, -0.0028] | 0.585 | 0.419 | no |
| 4 | 0.286 (147 of 1870 days never flag) | 196 | 0.486 | 0.342 | 0.0708 | +0.0000 [+0.0000, +0.0000] | -0.0085 [-0.0120, -0.0048] | 0.580 | 0.411 | no |
| 5 | 0.286 (147 of 1869 days never flag) | 196 | 0.478 | 0.337 | 0.0709 | +0.0000 [+0.0000, +0.0000] | -0.0075 [-0.0114, -0.0036] | 0.578 | 0.403 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.512 (climatology 0.512, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1757, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0470 [-0.1017, +0.0117]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.436 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0645 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0913 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1596 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1021 | 0.2439 | 0.0000 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.426 | 0.1369 | 0.2615 | +0.0000 [+0.0000, +0.0000] |
| day_type | month_end | 150 | 17 | 0.529 | 0.375 | 0.1364 | 0.1133 | +0.0000 [+0.0000, +0.0000] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.398 | 0.1006 | 0.0630 | +0.0000 [+0.0000, +0.0000] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.250 | 0.4089 | 0.2903 | +0.0000 [+0.0000, +0.0000] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.267 | 0.2274 | 0.1461 | +0.0000 [+0.0000, +0.0000] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.4822 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2213 | 0.2213 |

## persistence_logistic (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 7 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.107, 0.448] | 0.269 | 4.62 flat / 1.86 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

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

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.285 (210 of 1873 days never flag) | 133 | 0.436 | 0.459 | 0.0563 | +0.0151 [+0.0094, +0.0214] | +0.0000 [+0.0000, +0.0000] | 0.876 | 0.394 | no |
| 2 | 0.258 (147 of 1872 days never flag) | 170 | 0.583 | 0.476 | 0.0611 | +0.0100 [+0.0056, +0.0146] | +0.0000 [+0.0000, +0.0000] | 0.817 | 0.531 | no |
| 3 | 0.255 (189 of 1871 days never flag) | 120 | 0.341 | 0.392 | 0.0644 | +0.0063 [+0.0030, +0.0098] | +0.0000 [+0.0000, +0.0000] | 0.765 | 0.298 | no |
| 4 | 0.251 (232 of 1870 days never flag) | 141 | 0.428 | 0.418 | 0.0624 | +0.0085 [+0.0047, +0.0121] | +0.0000 [+0.0000, +0.0000] | 0.788 | 0.380 | no |
| 5 | 0.323 (315 of 1869 days never flag) | 127 | 0.391 | 0.425 | 0.0634 | +0.0075 [+0.0036, +0.0114] | +0.0000 [+0.0000, +0.0000] | 0.772 | 0.349 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.506 (climatology 0.512, difference -0.0059 [-0.0893, +0.0823]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0510, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.451 | 0.455 | 0.1679 | 0.2720 | +0.0168 [-0.0027, +0.0376] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.0978 | 0.1165 | +0.0256 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0240 | 0.0048 | +0.0080 [+0.0058, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0873 | 0.0000 | +0.0224 [+0.0166, +0.0283] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1445 | 0.2439 | 0.0333 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.464 | 0.472 | 0.1830 | 0.2615 | +0.0241 [+0.0043, +0.0450] |
| day_type | month_end | 150 | 17 | 0.412 | 0.583 | 0.0778 | 0.1133 | +0.0212 [+0.0029, +0.0434] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.432 | 0.0774 | 0.0630 | +0.0125 [+0.0072, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.0845 | 0.2903 | +0.0604 [-0.0440, +0.1631] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.429 | 0.0819 | 0.1461 | +0.0355 [+0.0130, +0.0568] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1364 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3171 | 0.2213 |

## ngboost_laplace (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.250 | 4.38 flat / 1.84 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.174, 0.536] | 0.231 | 3.42 flat / 1.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 1.692 [0.886, 2.895] | 0.538 [0.279, 0.923] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.235] | 1.731 [0.863, 2.833] | 0.731 [0.304, 1.325] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.030, 0.226] | 1.423 [0.611, 2.579] | 0.481 [0.219, 0.860] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.091, 0.381] | 2.538 [1.384, 4.048] | 1.029 [0.524, 1.750] |
| lead 5 alone (fail) | 26 | 2 | 0.077 [0.000, 0.167] | 1.577 [0.571, 2.923] | 0.692 [0.213, 1.357] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.875] | 6.529 [4.217, 10.143] | 2.721 [1.604, 4.534] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 0.333 (no interval) | 0.167 (no interval) |

Recall with equal weight per regime: 0.362 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.438 (147 of 1873 days never flag) | 112 | 0.486 | 0.607 | 0.0462 | +0.0252 [+0.0186, +0.0323] | +0.0101 [+0.0050, +0.0152] | 0.928 | 0.460 | no |
| 2 | 0.526 (168 of 1872 days never flag) | 63 | 0.129 | 0.286 | 0.0568 | +0.0143 [+0.0086, +0.0201] | +0.0043 [-0.0009, +0.0092] | 0.899 | 0.104 | no |
| 3 | 0.531 (147 of 1871 days never flag) | 59 | 0.159 | 0.373 | 0.0595 | +0.0112 [+0.0046, +0.0169] | +0.0049 [-0.0008, +0.0100] | 0.892 | 0.138 | no |
| 4 | 0.54 (147 of 1870 days never flag) | 102 | 0.261 | 0.353 | 0.0615 | +0.0093 [+0.0028, +0.0154] | +0.0008 [-0.0050, +0.0062] | 0.873 | 0.223 | no |
| 5 | 0.627 (147 of 1869 days never flag) | 59 | 0.130 | 0.305 | 0.0637 | +0.0072 [-0.0004, +0.0140] | -0.0003 [-0.0076, +0.0060] | 0.862 | 0.107 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.603 (climatology 0.512, difference +0.0911 [-0.0509, +0.1787]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0303, +0.0551], realised minus predicted +0.0654 [+0.0350, +0.0998]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.577 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0503 | 0.0159 | +0.0329 [+0.0235, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.909 | 0.0443 | 0.1165 | +0.0287 [+0.0113, +0.0503] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0096 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0260 | 0.0000 | +0.0283 [+0.0221, +0.0343] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 1.000 | 0.0561 | 0.2439 | +0.0463 [+0.0179, +0.0828] |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.596 | 0.2024 | 0.2615 | +0.0552 [+0.0317, +0.0794] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.0819 | 0.1133 | +0.0481 [+0.0291, +0.0671] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.554 | 0.0518 | 0.0630 | +0.0187 [+0.0123, +0.0262] |
| day_type | quarter_end | 31 | 9 | 0.667 | 1.000 | 0.1699 | 0.2903 | +0.1308 [+0.0495, +0.2125] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.750 | 0.0904 | 0.1461 | +0.0670 [+0.0493, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## risk_gbm (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.667] | 0.192 | 2.00 flat / 1.37 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.115 | 1.31 flat / 0.84 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.310, 0.667] | 1.346 [0.889, 2.000] | 0.760 [0.480, 1.216] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.455] | 1.077 [0.618, 1.778] | 0.606 [0.282, 1.136] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.038 [0.606, 1.714] | 0.587 [0.282, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 0.885 [0.519, 1.450] | 0.462 [0.226, 0.875] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.038 [0.611, 1.690] | 0.567 [0.273, 1.068] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.800] | 1.353 [0.800, 2.250] | 0.618 [0.321, 1.167] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.222 [1.625, 7.333] | 2.778 [1.286, 6.750] |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 77 | 0.300 | 0.545 | 0.0575 | +0.0139 [+0.0085, +0.0196] | -0.0012 [-0.0094, +0.0065] | 0.643 | 0.280 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 54 | 0.187 | 0.481 | 0.0686 | +0.0025 [-0.0039, +0.0081] | -0.0075 [-0.0160, -0.0005] | 0.578 | 0.171 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0665 | +0.0042 [-0.0024, +0.0101] | -0.0021 [-0.0100, +0.0048] | 0.580 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 46 | 0.167 | 0.500 | 0.0669 | +0.0039 [-0.0029, +0.0099] | -0.0045 [-0.0124, +0.0024] | 0.579 | 0.153 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 48 | 0.152 | 0.438 | 0.0697 | +0.0012 [-0.0054, +0.0074] | -0.0063 [-0.0137, +0.0006] | 0.577 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.523 (climatology 0.512, difference +0.0110 [-0.1321, +0.1313]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1044, ΔBrier vs climatology +0.0250 [+0.0161, +0.0339], realised minus predicted +0.0931 [+0.0564, +0.1322]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0959 | 0.2720 | +0.0016 [-0.0200, +0.0242] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0148 | 0.0159 | +0.0396 [+0.0307, +0.0483] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0028 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0390 | 0.1165 | +0.0173 [-0.0006, +0.0406] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0021 | 0.0048 | +0.0090 [+0.0071, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0021 | 0.0000 | +0.0317 [+0.0250, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0240 | 0.2439 | -0.0030 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.0979 | 0.2615 | +0.0145 [-0.0059, +0.0355] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0987 | 0.1133 | +0.0545 [+0.0304, +0.0791] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0435, +0.2143] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0950] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2003 | 0.2213 |

## risk_gbm+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.760] | 0.274 | 5.85 flat / 2.63 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.262 | 4.54 flat / 1.87 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 1.423 [0.812, 2.278] | 0.606 [0.315, 1.070] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.962 [1.815, 4.467] | 1.163 [0.726, 1.786] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 2.808 [1.515, 4.530] | 1.154 [0.570, 1.975] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.308 [1.419, 3.501] | 0.808 [0.500, 1.239] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.538 [1.444, 4.000] | 0.952 [0.552, 1.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.833, 9.910] | 2.632 [1.517, 4.469] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 5.111 [3.000, 10.008] | 2.639 [1.519, 5.438] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 102 | 0.464 | 0.637 | 0.0476 | +0.0238 [+0.0166, +0.0321] | +0.0087 [+0.0039, +0.0140] | 0.897 | 0.443 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 139 | 0.446 | 0.446 | 0.0601 | +0.0110 [+0.0065, +0.0153] | +0.0010 [-0.0020, +0.0040] | 0.845 | 0.402 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 132 | 0.428 | 0.447 | 0.0603 | +0.0103 [+0.0066, +0.0145] | +0.0040 [+0.0011, +0.0073] | 0.814 | 0.385 | no |
| 4 | 0.335 (147 of 1870 days never flag) | 118 | 0.420 | 0.492 | 0.0595 | +0.0114 [+0.0070, +0.0160] | +0.0029 [+0.0003, +0.0058] | 0.820 | 0.386 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 117 | 0.370 | 0.436 | 0.0630 | +0.0079 [+0.0035, +0.0123] | +0.0004 [-0.0027, +0.0032] | 0.789 | 0.331 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0116 [-0.1004, +0.1004]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0841, ΔBrier vs climatology +0.0454 [+0.0318, +0.0607], realised minus predicted +0.0117 [-0.0184, +0.0444]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2373 | 0.2720 | +0.0573 [+0.0304, +0.0862] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1174 | 0.0159 | +0.0233 [+0.0097, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0192 | 0.0000 | +0.0131 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0328 | 0.0200 | +0.0006 [-0.0060, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.1153 | 0.1165 | +0.0293 [+0.0021, +0.0606] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0236 | 0.0048 | +0.0074 [+0.0049, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0654 | 0.0000 | +0.0253 [+0.0194, +0.0316] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1446 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.650 | 0.2483 | 0.2615 | +0.0573 [+0.0324, +0.0837] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1080 | 0.1133 | +0.0597 [+0.0358, +0.0874] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.592 | 0.0861 | 0.0630 | +0.0160 [+0.0093, +0.0240] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0510, +0.2060] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0421, +0.0961] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3382 | 0.2213 |

## risk_gbm+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.778] | 0.269 | 5.65 flat / 2.56 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.545] | 0.254 | 4.46 flat / 1.93 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.285, 0.643] | 0.923 [0.545, 1.500] | 0.394 [0.221, 0.667] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.538 [1.600, 3.790] | 1.000 [0.614, 1.566] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.458] | 2.962 [1.815, 4.474] | 1.135 [0.712, 1.700] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.409] | 2.154 [1.304, 3.348] | 0.798 [0.491, 1.250] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.423 [1.478, 3.778] | 1.029 [0.620, 1.652] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 5.000 [3.000, 7.924] | 1.882 [1.118, 3.096] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 6.889 (no interval) | 3.833 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 70 | 0.329 | 0.657 | 0.0494 | +0.0220 [+0.0148, +0.0296] | +0.0069 [+0.0018, +0.0121] | 0.805 | 0.315 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 120 | 0.388 | 0.450 | 0.0623 | +0.0087 [+0.0037, +0.0134] | -0.0013 [-0.0053, +0.0024] | 0.750 | 0.350 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 134 | 0.413 | 0.425 | 0.0604 | +0.0103 [+0.0051, +0.0149] | +0.0040 [-0.0006, +0.0079] | 0.747 | 0.369 | no |
| 4 | 0.258 (147 of 1870 days never flag) | 109 | 0.384 | 0.486 | 0.0603 | +0.0105 [+0.0055, +0.0154] | +0.0020 [-0.0015, +0.0056] | 0.759 | 0.352 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 111 | 0.348 | 0.432 | 0.0637 | +0.0072 [+0.0017, +0.0125] | -0.0003 [-0.0043, +0.0037] | 0.742 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.530 (climatology 0.512, difference +0.0178 [-0.1007, +0.1301]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0860, ΔBrier vs climatology +0.0435 [+0.0306, +0.0581], realised minus predicted +0.0619 [+0.0330, +0.0947]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.1676 | 0.2720 | +0.0417 [+0.0143, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0224 | 0.0159 | +0.0323 [+0.0157, +0.0454] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0152 | 0.0200 | +0.0007 [-0.0068, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0902 | 0.1165 | +0.0284 [+0.0031, +0.0604] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0098 | 0.0048 | +0.0076 [+0.0052, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0033 | 0.0000 | +0.0316 [+0.0249, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1135 | 0.2439 | 0.0371 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.676 | 0.1718 | 0.2615 | +0.0457 [+0.0214, +0.0719] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1025 | 0.1133 | +0.0602 [+0.0346, +0.0877] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.578 | 0.0419 | 0.0630 | +0.0138 [+0.0076, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0438, +0.2071] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0418, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3822 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.417, 0.741] | 0.246 | 4.35 flat / 2.03 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.231 | 3.46 flat / 1.63 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 0.769 [0.400, 1.261] | 0.298 [0.149, 0.511] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.231, 0.562] | 1.731 [1.069, 2.696] | 0.692 [0.429, 1.087] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.216, 0.571] | 1.769 [1.105, 2.720] | 0.788 [0.476, 1.263] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.216, 0.571] | 1.577 [0.935, 2.440] | 0.654 [0.393, 1.036] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.645] | 2.346 [1.450, 3.667] | 1.135 [0.713, 1.750] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.437, 0.875] | 3.647 [2.111, 6.083] | 1.441 [0.839, 2.423] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.166, 0.714] | 5.667 [3.363, 11.405] | 3.139 [1.812, 6.679] |

Recall with equal weight per regime: 0.437 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 64 | 0.314 | 0.688 | 0.0499 | +0.0215 [+0.0142, +0.0286] | +0.0064 [+0.0011, +0.0117] | 0.804 | 0.303 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 100 | 0.396 | 0.550 | 0.0543 | +0.0168 [+0.0118, +0.0223] | +0.0068 [+0.0021, +0.0119] | 0.801 | 0.370 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 94 | 0.348 | 0.511 | 0.0563 | +0.0144 [+0.0089, +0.0198] | +0.0081 [+0.0032, +0.0130] | 0.778 | 0.321 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 94 | 0.384 | 0.564 | 0.0530 | +0.0178 [+0.0124, +0.0232] | +0.0094 [+0.0051, +0.0141] | 0.808 | 0.360 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 123 | 0.449 | 0.504 | 0.0542 | +0.0168 [+0.0113, +0.0224] | +0.0092 [+0.0048, +0.0141] | 0.804 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.704 (climatology 0.512, difference +0.1918 [+0.0419, +0.3200]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0719, ΔBrier vs climatology +0.0576 [+0.0400, +0.0768], realised minus predicted +0.0312 [+0.0067, +0.0565]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.694 | 0.1692 | 0.2720 | +0.0420 [+0.0131, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0243 | 0.0159 | +0.0310 [+0.0152, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0135 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0131 | 0.0200 | -0.0013 [-0.0085, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0898 | 0.1165 | +0.0279 [+0.0027, +0.0580] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0091 | 0.0048 | +0.0074 [+0.0047, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0030 | 0.0000 | +0.0316 [+0.0251, +0.0386] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1374 | 0.2439 | 0.0348 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.352 | 0.698 | 0.1724 | 0.2615 | +0.0445 [+0.0181, +0.0702] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.0999 | 0.1133 | +0.0579 [+0.0340, +0.0836] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0425 | 0.0630 | +0.0134 [+0.0067, +0.0199] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0507, +0.2140] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0392, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3821 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41+iorb (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.440, 0.786] | 0.250 | 4.38 flat / 2.07 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.652] | 0.231 | 3.46 flat / 1.63 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

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

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 67 | 0.329 | 0.687 | 0.0498 | +0.0216 [+0.0144, +0.0296] | +0.0065 [+0.0012, +0.0125] | 0.804 | 0.316 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 100 | 0.396 | 0.550 | 0.0543 | +0.0168 [+0.0118, +0.0222] | +0.0068 [+0.0020, +0.0122] | 0.801 | 0.370 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 94 | 0.348 | 0.511 | 0.0563 | +0.0144 [+0.0090, +0.0199] | +0.0081 [+0.0035, +0.0129] | 0.778 | 0.321 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 94 | 0.384 | 0.564 | 0.0530 | +0.0178 [+0.0124, +0.0234] | +0.0094 [+0.0050, +0.0142] | 0.808 | 0.360 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 123 | 0.449 | 0.504 | 0.0542 | +0.0168 [+0.0115, +0.0223] | +0.0092 [+0.0047, +0.0136] | 0.804 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.704 (climatology 0.512, difference +0.1918 [+0.0357, +0.3321]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0711, ΔBrier vs climatology +0.0584 [+0.0404, +0.0773], realised minus predicted +0.0293 [+0.0056, +0.0553]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.343 | 0.700 | 0.1724 | 0.2720 | +0.0442 [+0.0158, +0.0733] |
| regime | 2020 | 251 | 4 | 0.500 | 0.500 | 0.0282 | 0.0159 | +0.0350 [+0.0212, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0181 | 0.0200 | -0.0056 [-0.0171, +0.0035] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0895 | 0.1165 | +0.0258 [+0.0024, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0098 | 0.0048 | +0.0064 [+0.0029, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0027 | 0.0000 | +0.0316 [+0.0246, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1425 | 0.2439 | 0.0321 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.708 | 0.1772 | 0.2615 | +0.0474 [+0.0224, +0.0736] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.0999 | 0.1133 | +0.0579 [+0.0339, +0.0839] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.600 | 0.0445 | 0.0630 | +0.0135 [+0.0073, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0525, +0.2116] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0375, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3803 | 0.2213 |

## risk_gbm+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.406, 0.750] | 0.269 | 5.50 flat / 2.46 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.226, 0.565] | 0.235 | 4.27 flat / 1.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 1.308 [0.741, 2.167] | 0.558 [0.310, 0.938] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.769 [1.749, 4.185] | 1.096 [0.687, 1.700] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.962 [1.741, 4.697] | 1.231 [0.676, 2.058] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.469] | 2.385 [1.316, 3.929] | 0.846 [0.463, 1.391] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 2.154 [1.316, 3.333] | 0.865 [0.518, 1.381] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.353 [3.950, 10.000] | 2.588 [1.526, 4.313] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.889 (no interval) | 2.222 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 84 | 0.357 | 0.595 | 0.0481 | +0.0233 [+0.0166, +0.0308] | +0.0082 [+0.0034, +0.0134] | 0.888 | 0.338 | yes |
| 2 | 0.257 (147 of 1872 days never flag) | 133 | 0.439 | 0.459 | 0.0593 | +0.0118 [+0.0082, +0.0152] | +0.0018 [-0.0015, +0.0051] | 0.831 | 0.397 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 135 | 0.420 | 0.430 | 0.0590 | +0.0117 [+0.0083, +0.0156] | +0.0054 [+0.0016, +0.0093] | 0.803 | 0.376 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 117 | 0.399 | 0.470 | 0.0581 | +0.0127 [+0.0092, +0.0162] | +0.0043 [+0.0016, +0.0072] | 0.809 | 0.363 | no |
| 5 | 0.258 (147 of 1869 days never flag) | 107 | 0.370 | 0.477 | 0.0613 | +0.0096 [+0.0060, +0.0132] | +0.0021 [-0.0009, +0.0050] | 0.780 | 0.337 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0122 [-0.1051, +0.1055]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0310, +0.0576], realised minus predicted +0.0219 [-0.0100, +0.0582]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.576 | 0.2177 | 0.2720 | +0.0498 [+0.0240, +0.0771] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.1033 | 0.0159 | +0.0291 [+0.0201, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0240 | 0.0200 | +0.0027 [-0.0017, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0986 | 0.1165 | +0.0283 [+0.0050, +0.0582] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0184 | 0.0048 | +0.0084 [+0.0065, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0557 | 0.0000 | +0.0265 [+0.0204, +0.0326] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1148 | 0.2439 | 0.0329 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.602 | 0.2277 | 0.2615 | +0.0528 [+0.0291, +0.0779] |
| day_type | month_end | 150 | 17 | 0.706 | 0.706 | 0.1066 | 0.1133 | +0.0588 [+0.0341, +0.0842] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.500 | 0.0741 | 0.0630 | +0.0154 [+0.0094, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0488, +0.2053] |
| day_type | tax_date | 89 | 13 | 0.538 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0420, +0.0959] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.4541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2486 | 0.2213 |

## risk_gbm+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.433, 0.792] | 0.269 | 5.62 flat / 2.50 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.600] | 0.242 | 4.35 flat / 1.74 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.647] | 1.385 [0.793, 2.263] | 0.596 [0.312, 1.077] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.923 [1.850, 4.400] | 1.144 [0.708, 1.750] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.923 [1.636, 4.700] | 1.183 [0.603, 2.037] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 2.231 [1.361, 3.529] | 0.769 [0.469, 1.230] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.423 [1.387, 4.000] | 0.856 [0.484, 1.425] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.846, 9.834] | 2.632 [1.490, 4.475] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 2.250 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 101 | 0.464 | 0.644 | 0.0467 | +0.0247 [+0.0175, +0.0325] | +0.0096 [+0.0047, +0.0148] | 0.913 | 0.444 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 140 | 0.460 | 0.457 | 0.0591 | +0.0119 [+0.0074, +0.0163] | +0.0019 [-0.0012, +0.0048] | 0.877 | 0.417 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 137 | 0.442 | 0.445 | 0.0584 | +0.0123 [+0.0086, +0.0161] | +0.0059 [+0.0030, +0.0089] | 0.865 | 0.398 | no |
| 4 | 0.335 (147 of 1870 days never flag) | 117 | 0.428 | 0.504 | 0.0580 | +0.0128 [+0.0089, +0.0172] | +0.0044 [+0.0020, +0.0072] | 0.865 | 0.394 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 114 | 0.370 | 0.447 | 0.0619 | +0.0090 [+0.0046, +0.0133] | +0.0015 [-0.0015, +0.0046] | 0.849 | 0.333 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0116 [-0.1013, +0.1034]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0328, +0.0605], realised minus predicted +0.0387 [+0.0087, +0.0716]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2373 | 0.2720 | +0.0573 [+0.0292, +0.0859] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1171 | 0.0159 | +0.0233 [+0.0105, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0047 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0037 [-0.0003, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0987 | 0.1165 | +0.0318 [+0.0046, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0021 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0654 | 0.0000 | +0.0253 [+0.0194, +0.0314] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1446 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.650 | 0.2483 | 0.2615 | +0.0573 [+0.0318, +0.0820] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1060 | 0.1133 | +0.0598 [+0.0356, +0.0871] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.600 | 0.0723 | 0.0630 | +0.0170 [+0.0102, +0.0242] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0472, +0.2084] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0413, +0.0938] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3382 | 0.2213 |

## risk_gbm+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.324, 0.682] | 0.231 | 3.04 flat / 1.55 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.423] | 0.192 | 1.88 flat / 0.96 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 1.231 [0.731, 2.000] | 0.510 [0.300, 0.853] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.457] | 1.308 [0.824, 2.000] | 0.596 [0.310, 1.030] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.077 [0.667, 1.667] | 0.462 [0.250, 0.779] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.000 [0.615, 1.550] | 0.375 [0.210, 0.625] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.379] | 1.231 [0.774, 1.913] | 0.625 [0.352, 1.060] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.812] | 2.412 [1.500, 4.077] | 0.971 [0.579, 1.688] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 2.639 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 88 | 0.400 | 0.636 | 0.0481 | +0.0233 [+0.0177, +0.0293] | +0.0082 [+0.0032, +0.0134] | 0.905 | 0.382 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 66 | 0.230 | 0.485 | 0.0603 | +0.0107 [+0.0075, +0.0139] | +0.0007 [-0.0031, +0.0044] | 0.852 | 0.211 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 56 | 0.203 | 0.500 | 0.0595 | +0.0111 [+0.0077, +0.0150] | +0.0048 [+0.0008, +0.0089] | 0.820 | 0.187 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 54 | 0.203 | 0.519 | 0.0593 | +0.0115 [+0.0079, +0.0153] | +0.0031 [-0.0004, +0.0065] | 0.832 | 0.188 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 56 | 0.174 | 0.429 | 0.0624 | +0.0085 [+0.0048, +0.0120] | +0.0010 [-0.0030, +0.0045] | 0.796 | 0.155 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.518 (climatology 0.512, difference +0.0053 [-0.1142, +0.1111]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0297, +0.0515], realised minus predicted +0.0535 [+0.0202, +0.0884]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.608 | 0.1666 | 0.2720 | +0.0429 [+0.0257, +0.0603] |
| regime | 2020 | 251 | 4 | 0.250 | 1.000 | 0.0661 | 0.0159 | +0.0366 [+0.0281, +0.0449] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0099 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0178 | 0.0200 | +0.0030 [-0.0012, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0771 | 0.1165 | +0.0299 [+0.0055, +0.0612] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0128 | 0.0048 | +0.0086 [+0.0066, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0337 | 0.0000 | +0.0301 [+0.0237, +0.0363] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0843 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.448 | 0.644 | 0.1731 | 0.2615 | +0.0505 [+0.0329, +0.0687] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1034 | 0.1133 | +0.0575 [+0.0328, +0.0848] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.600 | 0.0494 | 0.0630 | +0.0156 [+0.0111, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0496, +0.2077] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.875 | 0.0961 | 0.1461 | +0.0685 [+0.0414, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.4080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2173 | 0.2213 |

## risk_gbm+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.783] | 0.231 | 4.08 flat / 1.66 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.618] | 0.231 | 3.23 flat / 1.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.696] | 1.538 [0.738, 2.706] | 0.712 [0.331, 1.288] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.393] | 2.615 [1.391, 4.300] | 0.904 [0.476, 1.519] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.538] | 2.500 [1.292, 4.214] | 0.856 [0.439, 1.438] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.478] | 1.962 [0.869, 3.500] | 0.625 [0.256, 1.145] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.444] | 2.192 [1.077, 3.769] | 0.779 [0.380, 1.357] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 5.353 [3.217, 8.500] | 2.059 [1.197, 3.375] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 0.917 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 87 | 0.336 | 0.540 | 0.0604 | +0.0110 [+0.0011, +0.0208] | -0.0041 [-0.0123, +0.0042] | 0.873 | 0.313 | no |
| 2 | 0.605 (147 of 1872 days never flag) | 125 | 0.410 | 0.456 | 0.0716 | -0.0005 [-0.0089, +0.0076] | -0.0105 [-0.0182, -0.0033] | 0.816 | 0.371 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 122 | 0.413 | 0.467 | 0.0723 | -0.0017 [-0.0111, +0.0062] | -0.0080 [-0.0169, -0.0004] | 0.798 | 0.376 | yes |
| 4 | 0.655 (147 of 1870 days never flag) | 104 | 0.384 | 0.510 | 0.0703 | +0.0005 [-0.0068, +0.0069] | -0.0079 [-0.0145, -0.0022] | 0.814 | 0.355 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 106 | 0.355 | 0.462 | 0.0729 | -0.0019 [-0.0084, +0.0038] | -0.0095 [-0.0154, -0.0042] | 0.775 | 0.322 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.480 (climatology 0.512, difference -0.0322 [-0.1362, +0.0556]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0227, +0.0506], realised minus predicted +0.0060 [-0.0286, +0.0431]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.507 | 0.3118 | 0.2720 | +0.0131 [-0.0304, +0.0570] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0240, +0.0127] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0688 | 0.1165 | +0.0286 [+0.0036, +0.0581] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0084 | 0.0048 | +0.0080 [+0.0061, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1098 | 0.0000 | +0.0120 [+0.0062, +0.0178] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1009 | 0.2439 | 0.0281 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.376 | 0.547 | 0.3114 | 0.2615 | +0.0154 [-0.0232, +0.0525] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1094 | 0.1133 | +0.0570 [+0.0317, +0.0837] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1025 | 0.0630 | +0.0012 [-0.0092, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0503, +0.2063] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0947] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.778] | 0.231 | 3.85 flat / 1.45 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.567] | 0.231 | 3.12 flat / 1.06 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.688] | 1.462 [0.700, 2.579] | 0.635 [0.275, 1.156] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 2.192 [1.097, 3.709] | 0.702 [0.324, 1.214] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 2.538 [1.300, 4.311] | 0.837 [0.417, 1.432] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 2.000 [0.914, 3.654] | 0.635 [0.271, 1.191] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.000 [0.968, 3.565] | 0.673 [0.320, 1.198] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 5.235 [3.130, 8.571] | 1.971 [1.125, 3.342] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.222 [0.400, 2.714] | 0.472 [0.125, 1.143] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 84 | 0.329 | 0.548 | 0.0609 | +0.0105 [+0.0004, +0.0200] | -0.0046 [-0.0129, +0.0032] | 0.870 | 0.307 | no |
| 2 | 0.668 (147 of 1872 days never flag) | 109 | 0.374 | 0.477 | 0.0718 | -0.0007 [-0.0093, +0.0071] | -0.0107 [-0.0191, -0.0034] | 0.814 | 0.341 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 123 | 0.413 | 0.463 | 0.0723 | -0.0016 [-0.0115, +0.0067] | -0.0079 [-0.0174, -0.0001] | 0.801 | 0.375 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 106 | 0.391 | 0.509 | 0.0704 | +0.0004 [-0.0070, +0.0074] | -0.0081 [-0.0149, -0.0018] | 0.818 | 0.361 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 101 | 0.355 | 0.485 | 0.0727 | -0.0017 [-0.0081, +0.0042] | -0.0093 [-0.0155, -0.0038] | 0.779 | 0.325 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.504 (climatology 0.512, difference -0.0078 [-0.1152, +0.0856]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0913, ΔBrier vs climatology +0.0381 [+0.0238, +0.0540], realised minus predicted +0.0028 [-0.0323, +0.0386]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.514 | 0.3133 | 0.2720 | +0.0133 [-0.0301, +0.0543] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1939 | 0.0159 | -0.0054 [-0.0268, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0119 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0050 | 0.0200 | +0.0005 [-0.0055, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0684 | 0.1165 | +0.0281 [+0.0054, +0.0560] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0077 [+0.0056, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1096 | 0.0000 | +0.0121 [+0.0066, +0.0181] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1248 | 0.2439 | 0.0259 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.548 | 0.3121 | 0.2615 | +0.0142 [-0.0235, +0.0495] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1068 | 0.1133 | +0.0547 [+0.0325, +0.0782] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1031 | 0.0630 | +0.0008 [-0.0095, +0.0108] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0470, +0.2071] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.714] | 0.231 | 3.04 flat / 1.35 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.615] | 0.192 | 2.38 flat / 0.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 1.538 [0.733, 2.630] | 0.712 [0.333, 1.224] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 1.962 [0.928, 3.459] | 0.779 [0.400, 1.320] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 2.038 [1.018, 3.458] | 0.798 [0.409, 1.323] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.517] | 1.846 [0.857, 3.222] | 0.692 [0.328, 1.183] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.000 [0.978, 3.421] | 0.798 [0.416, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 3.824 [2.035, 6.727] | 1.559 [0.812, 2.751] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.556 [0.600, 3.400] | 0.944 [0.300, 2.425] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 87 | 0.336 | 0.540 | 0.0604 | +0.0110 [+0.0017, +0.0209] | -0.0041 [-0.0122, +0.0039] | 0.873 | 0.313 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 111 | 0.432 | 0.541 | 0.0649 | +0.0062 [-0.0032, +0.0150] | -0.0038 [-0.0127, +0.0044] | 0.839 | 0.402 | no |
| 3 | 0.615 (147 of 1871 days never flag) | 108 | 0.399 | 0.509 | 0.0687 | +0.0020 [-0.0082, +0.0112] | -0.0043 [-0.0139, +0.0044] | 0.827 | 0.368 | no |
| 4 | 0.754 (147 of 1870 days never flag) | 99 | 0.370 | 0.515 | 0.0650 | +0.0059 [-0.0015, +0.0131] | -0.0026 [-0.0097, +0.0041] | 0.843 | 0.342 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 112 | 0.435 | 0.536 | 0.0652 | +0.0057 [-0.0010, +0.0121] | -0.0018 [-0.0081, +0.0043] | 0.828 | 0.405 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0145, +0.2668]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0818, ΔBrier vs climatology +0.0477 [+0.0295, +0.0684], realised minus predicted -0.0171 [-0.0463, +0.0160]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.507 | 0.3118 | 0.2720 | +0.0131 [-0.0284, +0.0549] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0226, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0688 | 0.1165 | +0.0286 [+0.0048, +0.0604] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0084 | 0.0048 | +0.0080 [+0.0060, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1098 | 0.0000 | +0.0120 [+0.0065, +0.0174] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1009 | 0.2439 | 0.0281 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.376 | 0.547 | 0.3114 | 0.2615 | +0.0154 [-0.0210, +0.0532] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1094 | 0.1133 | +0.0570 [+0.0330, +0.0845] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1025 | 0.0630 | +0.0012 [-0.0087, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0471, +0.2088] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0416, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.719] | 0.231 | 3.23 flat / 1.40 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.192 | 2.42 flat / 1.00 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.696] | 1.462 [0.686, 2.586] | 0.635 [0.279, 1.172] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.154 [1.052, 3.800] | 0.827 [0.430, 1.413] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 2.115 [1.031, 3.728] | 0.827 [0.427, 1.427] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.219, 0.571] | 1.962 [0.952, 3.389] | 0.779 [0.387, 1.359] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 1.885 [0.850, 3.357] | 0.769 [0.375, 1.336] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 4.059 [2.312, 7.000] | 1.618 [0.920, 2.896] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.667 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 84 | 0.329 | 0.548 | 0.0609 | +0.0105 [+0.0011, +0.0201] | -0.0046 [-0.0128, +0.0035] | 0.870 | 0.307 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 116 | 0.432 | 0.517 | 0.0652 | +0.0059 [-0.0035, +0.0144] | -0.0041 [-0.0129, +0.0041] | 0.838 | 0.399 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 112 | 0.413 | 0.509 | 0.0688 | +0.0018 [-0.0087, +0.0106] | -0.0045 [-0.0145, +0.0041] | 0.823 | 0.381 | no |
| 4 | 0.641 (147 of 1870 days never flag) | 106 | 0.399 | 0.519 | 0.0643 | +0.0066 [-0.0014, +0.0139] | -0.0019 [-0.0096, +0.0054] | 0.844 | 0.369 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 109 | 0.435 | 0.550 | 0.0647 | +0.0062 [-0.0005, +0.0128] | -0.0013 [-0.0080, +0.0051] | 0.827 | 0.406 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1893 [+0.0390, +0.3183]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0475 [+0.0293, +0.0674], realised minus predicted -0.0179 [-0.0488, +0.0162]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.514 | 0.3133 | 0.2720 | +0.0133 [-0.0292, +0.0558] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1939 | 0.0159 | -0.0054 [-0.0262, +0.0109] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0119 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0050 | 0.0200 | +0.0005 [-0.0050, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0684 | 0.1165 | +0.0281 [+0.0049, +0.0583] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0077 [+0.0056, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1096 | 0.0000 | +0.0121 [+0.0063, +0.0176] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1248 | 0.2439 | 0.0259 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.548 | 0.3121 | 0.2615 | +0.0142 [-0.0216, +0.0515] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1068 | 0.1133 | +0.0547 [+0.0307, +0.0797] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1031 | 0.0630 | +0.0008 [-0.0095, +0.0112] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0496, +0.2096] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0979] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_gbm+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.760] | 0.269 | 5.23 flat / 2.36 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.235 | 4.27 flat / 1.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.640] | 1.500 [0.875, 2.438] | 0.663 [0.361, 1.167] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.038 [1.743, 4.810] | 1.125 [0.638, 1.817] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.206, 0.567] | 2.577 [1.308, 4.400] | 0.894 [0.460, 1.523] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 2.385 [1.208, 4.116] | 0.856 [0.442, 1.466] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.476] | 3.077 [1.564, 5.125] | 1.327 [0.613, 2.329] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.412 [3.867, 10.501] | 2.735 [1.517, 4.786] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 1.639 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 93 | 0.386 | 0.581 | 0.0559 | +0.0155 [+0.0082, +0.0238] | +0.0005 [-0.0059, +0.0070] | 0.849 | 0.363 | yes |
| 2 | 0.489 (147 of 1872 days never flag) | 133 | 0.388 | 0.406 | 0.0697 | +0.0013 [-0.0044, +0.0070] | -0.0087 [-0.0144, -0.0031] | 0.775 | 0.343 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 126 | 0.428 | 0.468 | 0.0697 | +0.0010 [-0.0038, +0.0057] | -0.0053 [-0.0103, -0.0005] | 0.728 | 0.389 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 119 | 0.413 | 0.479 | 0.0692 | +0.0016 [-0.0031, +0.0061] | -0.0069 [-0.0115, -0.0025] | 0.752 | 0.377 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 131 | 0.370 | 0.389 | 0.0729 | -0.0020 [-0.0072, +0.0029] | -0.0095 [-0.0151, -0.0043] | 0.717 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.479 (climatology 0.512, difference -0.0329 [-0.1329, +0.0587]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0962, ΔBrier vs climatology +0.0333 [+0.0203, +0.0469], realised minus predicted -0.0114 [-0.0467, +0.0268]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.566 | 0.2828 | 0.2720 | +0.0391 [+0.0075, +0.0714] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0137, +0.0099] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0086, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0022, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0675 | 0.1165 | +0.0265 [+0.0030, +0.0554] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0218 | 0.0048 | +0.0076 [+0.0058, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1294 | 0.0000 | +0.0062 [+0.0011, +0.0119] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0781 | 0.2439 | 0.0070 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.432 | 0.587 | 0.2860 | 0.2615 | +0.0397 [+0.0114, +0.0682] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1101 | 0.1133 | +0.0563 [+0.0319, +0.0831] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.507 | 0.1068 | 0.0630 | +0.0066 [-0.0009, +0.0146] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0462, +0.2080] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0402, +0.0966] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2839 | 0.2213 |

## risk_gbm+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.424, 0.794] | 0.269 | 5.27 flat / 2.34 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 4.23 flat / 1.74 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.686] | 1.538 [0.958, 2.474] | 0.673 [0.386, 1.144] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.481] | 3.077 [1.811, 4.801] | 1.135 [0.650, 1.792] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 2.538 [1.294, 4.223] | 0.856 [0.420, 1.422] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.519] | 2.423 [1.267, 4.100] | 0.827 [0.429, 1.406] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.519] | 3.115 [1.666, 5.242] | 1.375 [0.675, 2.445] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.412 [4.000, 10.200] | 2.735 [1.573, 4.657] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 1.583 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 94 | 0.386 | 0.574 | 0.0564 | +0.0150 [+0.0075, +0.0232] | -0.0000 [-0.0057, +0.0060] | 0.842 | 0.363 | yes |
| 2 | 0.489 (147 of 1872 days never flag) | 139 | 0.424 | 0.424 | 0.0699 | +0.0012 [-0.0047, +0.0065] | -0.0088 [-0.0146, -0.0033] | 0.768 | 0.378 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 123 | 0.413 | 0.463 | 0.0696 | +0.0011 [-0.0040, +0.0060] | -0.0052 [-0.0103, -0.0004] | 0.732 | 0.375 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 121 | 0.420 | 0.479 | 0.0694 | +0.0014 [-0.0034, +0.0066] | -0.0070 [-0.0115, -0.0024] | 0.760 | 0.384 | yes |
| 5 | 0.491 (147 of 1869 days never flag) | 133 | 0.377 | 0.391 | 0.0727 | -0.0018 [-0.0071, +0.0032] | -0.0093 [-0.0150, -0.0038] | 0.719 | 0.330 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.500 (climatology 0.512, difference -0.0122 [-0.1225, +0.0832]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0944, ΔBrier vs climatology +0.0351 [+0.0216, +0.0503], realised minus predicted -0.0146 [-0.0480, +0.0223]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.573 | 0.2844 | 0.2720 | +0.0393 [+0.0063, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2020 | 0.0159 | -0.0034 [-0.0161, +0.0083] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0363 | 0.0000 | +0.0103 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0095 | 0.0200 | +0.0005 [-0.0052, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0671 | 0.1165 | +0.0259 [+0.0045, +0.0515] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0211 | 0.0048 | +0.0073 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1291 | 0.0000 | +0.0063 [+0.0010, +0.0120] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1019 | 0.2439 | 0.0047 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.424 | 0.582 | 0.2866 | 0.2615 | +0.0385 [+0.0083, +0.0682] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1076 | 0.1133 | +0.0540 [+0.0316, +0.0791] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.500 | 0.1074 | 0.0630 | +0.0062 [-0.0014, +0.0143] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0518, +0.2102] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0379, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.363, 0.719] | 0.231 | 4.15 flat / 1.97 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.606] | 0.231 | 3.42 flat / 1.57 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.650] | 1.500 [0.875, 2.476] | 0.663 [0.353, 1.163] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.923 [0.900, 3.500] | 0.760 [0.383, 1.319] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.206, 0.571] | 1.692 [0.842, 3.000] | 0.731 [0.390, 1.250] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.231 [1.231, 3.773] | 0.933 [0.534, 1.538] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.808 [1.429, 4.900] | 1.269 [0.589, 2.330] |
| inside 2018-2019 | 17 | 11 | 0.647 (no interval) | 5.000 (no interval) | 2.279 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 1.389 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 93 | 0.386 | 0.581 | 0.0559 | +0.0155 [+0.0082, +0.0237] | +0.0005 [-0.0056, +0.0068] | 0.849 | 0.363 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 106 | 0.403 | 0.528 | 0.0622 | +0.0088 [+0.0023, +0.0156] | -0.0012 [-0.0077, +0.0056] | 0.805 | 0.374 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 90 | 0.333 | 0.511 | 0.0655 | +0.0052 [-0.0004, +0.0112] | -0.0011 [-0.0068, +0.0049] | 0.773 | 0.308 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 112 | 0.391 | 0.482 | 0.0636 | +0.0073 [+0.0014, +0.0130] | -0.0012 [-0.0070, +0.0047] | 0.794 | 0.358 | yes |
| 5 | 0.698 (147 of 1869 days never flag) | 133 | 0.435 | 0.451 | 0.0649 | +0.0060 [+0.0000, +0.0119] | -0.0015 [-0.0079, +0.0049] | 0.783 | 0.393 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0192, +0.2720]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0837, ΔBrier vs climatology +0.0458 [+0.0278, +0.0657], realised minus predicted -0.0358 [-0.0675, -0.0024]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.566 | 0.2828 | 0.2720 | +0.0391 [+0.0085, +0.0728] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0133, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0087, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0025, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0675 | 0.1165 | +0.0265 [+0.0041, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0218 | 0.0048 | +0.0076 [+0.0057, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1294 | 0.0000 | +0.0062 [+0.0009, +0.0119] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0781 | 0.2439 | 0.0070 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.432 | 0.587 | 0.2860 | 0.2615 | +0.0397 [+0.0117, +0.0686] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1101 | 0.1133 | +0.0563 [+0.0325, +0.0810] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.507 | 0.1068 | 0.0630 | +0.0066 [-0.0006, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0469, +0.2050] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0412, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2839 | 0.2213 |

## risk_gbm+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.351, 0.722] | 0.238 | 4.27 flat / 2.03 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.619] | 0.231 | 3.46 flat / 1.57 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.676] | 1.538 [0.919, 2.500] | 0.673 [0.366, 1.171] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 2.154 [1.094, 3.778] | 0.837 [0.462, 1.424] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 1.962 [1.000, 3.375] | 0.827 [0.452, 1.397] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.038 [1.129, 3.444] | 0.846 [0.466, 1.423] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.692 [1.367, 4.728] | 1.240 [0.565, 2.296] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.875] | 5.176 [2.920, 9.000] | 2.324 [1.183, 4.364] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 1.472 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 94 | 0.386 | 0.574 | 0.0564 | +0.0150 [+0.0080, +0.0231] | -0.0000 [-0.0060, +0.0060] | 0.842 | 0.363 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 112 | 0.403 | 0.500 | 0.0626 | +0.0085 [+0.0022, +0.0151] | -0.0015 [-0.0081, +0.0052] | 0.805 | 0.371 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 103 | 0.377 | 0.505 | 0.0656 | +0.0050 [-0.0009, +0.0111] | -0.0013 [-0.0073, +0.0050] | 0.769 | 0.347 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 108 | 0.399 | 0.509 | 0.0629 | +0.0080 [+0.0021, +0.0145] | -0.0005 [-0.0065, +0.0060] | 0.794 | 0.368 | yes |
| 5 | 0.723 (147 of 1869 days never flag) | 129 | 0.428 | 0.457 | 0.0644 | +0.0065 [+0.0004, +0.0125] | -0.0010 [-0.0074, +0.0054] | 0.779 | 0.387 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1893 [+0.0398, +0.3290]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0839, ΔBrier vs climatology +0.0456 [+0.0277, +0.0660], realised minus predicted -0.0365 [-0.0667, -0.0047]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.573 | 0.2844 | 0.2720 | +0.0393 [+0.0072, +0.0745] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2020 | 0.0159 | -0.0034 [-0.0161, +0.0077] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0363 | 0.0000 | +0.0103 [+0.0086, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0095 | 0.0200 | +0.0005 [-0.0054, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0671 | 0.1165 | +0.0259 [+0.0048, +0.0531] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0211 | 0.0048 | +0.0073 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1291 | 0.0000 | +0.0063 [+0.0009, +0.0118] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1019 | 0.2439 | 0.0047 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.424 | 0.582 | 0.2866 | 0.2615 | +0.0385 [+0.0114, +0.0677] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1076 | 0.1133 | +0.0540 [+0.0323, +0.0775] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.500 | 0.1074 | 0.0630 | +0.0062 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0513, +0.2113] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0972] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.308, 0.704] | 0.231 | 3.92 flat / 1.77 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 3.04 flat / 1.04 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.655] | 2.269 [1.130, 3.870] | 1.183 [0.550, 2.137] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.447] | 2.654 [1.414, 4.401] | 0.913 [0.469, 1.523] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.535] | 2.462 [1.192, 4.191] | 0.827 [0.400, 1.417] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 2.308 [1.095, 3.957] | 0.779 [0.369, 1.346] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.447] | 2.269 [1.091, 3.900] | 0.769 [0.367, 1.320] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.882] | 5.353 [2.952, 9.078] | 2.353 [1.211, 4.250] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 1.222 [0.500, 2.857] | 0.667 [0.229, 1.701] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 120 | 0.436 | 0.508 | 0.0560 | +0.0154 [+0.0061, +0.0247] | +0.0003 [-0.0079, +0.0078] | 0.919 | 0.402 | yes |
| 2 | 0.605 (147 of 1872 days never flag) | 129 | 0.432 | 0.465 | 0.0663 | +0.0047 [-0.0044, +0.0130] | -0.0053 [-0.0139, +0.0020] | 0.880 | 0.392 | yes |
| 3 | 0.621 (147 of 1871 days never flag) | 126 | 0.449 | 0.492 | 0.0659 | +0.0048 [-0.0055, +0.0137] | -0.0015 [-0.0115, +0.0072] | 0.892 | 0.412 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 119 | 0.428 | 0.496 | 0.0656 | +0.0052 [-0.0021, +0.0113] | -0.0033 [-0.0099, +0.0027] | 0.847 | 0.393 | no |
| 5 | 0.667 (147 of 1869 days never flag) | 115 | 0.406 | 0.487 | 0.0728 | -0.0019 [-0.0108, +0.0062] | -0.0094 [-0.0182, -0.0017] | 0.817 | 0.372 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.491 (climatology 0.512, difference -0.0213 [-0.1189, +0.0586]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0877, ΔBrier vs climatology +0.0417 [+0.0281, +0.0571], realised minus predicted +0.0232 [-0.0094, +0.0588]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.481 | 0.3126 | 0.2720 | +0.0169 [-0.0246, +0.0564] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0837 | 0.0159 | +0.0174 [-0.0067, +0.0366] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0006 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0000, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0778 | 0.1165 | +0.0277 [+0.0050, +0.0578] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0030 | 0.0048 | +0.0090 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0031 | 0.0000 | +0.0317 [+0.0253, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0494 | 0.2439 | 0.0189 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.513 | 0.3198 | 0.2615 | +0.0183 [-0.0178, +0.0529] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1059 | 0.1133 | +0.0577 [+0.0326, +0.0840] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.441 | 0.0796 | 0.0630 | +0.0063 [-0.0035, +0.0156] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0490, +0.2079] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.692] | 0.231 | 3.85 flat / 1.61 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.562] | 0.231 | 3.15 flat / 1.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.654] | 1.962 [0.933, 3.333] | 0.904 [0.413, 1.625] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.115, 0.435] | 2.346 [1.237, 3.867] | 0.827 [0.417, 1.388] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.147, 0.481] | 2.308 [1.048, 3.900] | 0.731 [0.310, 1.263] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 2.346 [1.132, 4.000] | 0.788 [0.385, 1.352] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.192 [1.077, 3.769] | 0.750 [0.361, 1.300] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 5.176 [2.950, 8.701] | 2.088 [1.169, 3.700] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.333 (no interval) | 0.694 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0569 | +0.0145 [+0.0051, +0.0240] | -0.0006 [-0.0089, +0.0072] | 0.917 | 0.399 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 117 | 0.403 | 0.479 | 0.0667 | +0.0044 [-0.0045, +0.0123] | -0.0057 [-0.0144, +0.0019] | 0.877 | 0.368 | no |
| 3 | 0.618 (147 of 1871 days never flag) | 119 | 0.428 | 0.496 | 0.0658 | +0.0049 [-0.0053, +0.0135] | -0.0014 [-0.0115, +0.0068] | 0.896 | 0.393 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 121 | 0.435 | 0.496 | 0.0631 | +0.0078 [+0.0010, +0.0140] | -0.0007 [-0.0068, +0.0048] | 0.884 | 0.400 | no |
| 5 | 0.591 (147 of 1869 days never flag) | 108 | 0.370 | 0.472 | 0.0669 | +0.0040 [-0.0019, +0.0095] | -0.0035 [-0.0096, +0.0020] | 0.819 | 0.337 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.499 (climatology 0.512, difference -0.0135 [-0.1307, +0.0836]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0861, ΔBrier vs climatology +0.0434 [+0.0291, +0.0589], realised minus predicted +0.0215 [-0.0098, +0.0565]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.515 | 0.3148 | 0.2720 | +0.0153 [-0.0252, +0.0560] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0864 | 0.0159 | +0.0156 [-0.0099, +0.0360] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0007 | 0.0000 | +0.0137 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0014 | 0.0200 | +0.0016 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0775 | 0.1165 | +0.0273 [+0.0067, +0.0557] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0087 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0028 | 0.0000 | +0.0317 [+0.0247, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0732 | 0.2439 | 0.0166 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.541 | 0.3213 | 0.2615 | +0.0156 [-0.0205, +0.0507] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1035 | 0.1133 | +0.0558 [+0.0329, +0.0823] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.466 | 0.0805 | 0.0630 | +0.0054 [-0.0048, +0.0149] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0542, +0.2064] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0383, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.696] | 0.231 | 3.46 flat / 1.68 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.263, 0.667] | 0.231 | 2.65 flat / 1.02 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 2.269 [1.125, 3.929] | 1.183 [0.519, 2.261] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.258, 0.609] | 1.885 [0.861, 3.500] | 0.750 [0.370, 1.333] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 2.269 [1.125, 3.895] | 0.885 [0.458, 1.489] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 2.000 [0.933, 3.667] | 0.731 [0.350, 1.313] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.625] | 1.692 [0.750, 3.131] | 0.683 [0.328, 1.212] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 4.588 [2.428, 8.101] | 2.176 [1.073, 4.096] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.750 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 120 | 0.436 | 0.508 | 0.0560 | +0.0154 [+0.0059, +0.0245] | +0.0003 [-0.0079, +0.0078] | 0.919 | 0.402 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 111 | 0.446 | 0.559 | 0.0603 | +0.0108 [+0.0015, +0.0189] | +0.0008 [-0.0086, +0.0089] | 0.892 | 0.418 | yes |
| 3 | 0.731 (147 of 1871 days never flag) | 117 | 0.420 | 0.496 | 0.0631 | +0.0076 [-0.0034, +0.0166] | +0.0013 [-0.0096, +0.0102] | 0.899 | 0.386 | no |
| 4 | 0.754 (147 of 1870 days never flag) | 108 | 0.406 | 0.519 | 0.0609 | +0.0099 [+0.0027, +0.0165] | +0.0014 [-0.0054, +0.0082] | 0.868 | 0.376 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 97 | 0.384 | 0.546 | 0.0658 | +0.0052 [-0.0041, +0.0131] | -0.0024 [-0.0106, +0.0053] | 0.856 | 0.359 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0210, +0.2697]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0768, ΔBrier vs climatology +0.0527 [+0.0344, +0.0728], realised minus predicted +0.0019 [-0.0281, +0.0322]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.481 | 0.3126 | 0.2720 | +0.0169 [-0.0237, +0.0566] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0837 | 0.0159 | +0.0174 [-0.0071, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0003, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0778 | 0.1165 | +0.0277 [+0.0047, +0.0555] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0030 | 0.0048 | +0.0090 [+0.0072, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0031 | 0.0000 | +0.0317 [+0.0252, +0.0385] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0494 | 0.2439 | 0.0189 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.513 | 0.3198 | 0.2615 | +0.0183 [-0.0183, +0.0531] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1059 | 0.1133 | +0.0577 [+0.0329, +0.0831] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.441 | 0.0796 | 0.0630 | +0.0063 [-0.0039, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0483, +0.2074] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0427, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.682] | 0.231 | 3.46 flat / 1.57 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.192 | 2.42 flat / 0.97 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 1.962 [0.914, 3.400] | 0.904 [0.392, 1.643] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 1.885 [0.889, 3.231] | 0.779 [0.390, 1.300] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.038 [0.963, 3.600] | 0.798 [0.407, 1.352] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.962 [1.000, 3.371] | 0.769 [0.409, 1.310] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.962 [0.921, 3.464] | 0.788 [0.395, 1.371] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.842] | 4.588 [2.571, 7.889] | 1.971 [1.091, 3.500] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0569 | +0.0145 [+0.0051, +0.0242] | -0.0006 [-0.0089, +0.0074] | 0.917 | 0.399 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 104 | 0.396 | 0.529 | 0.0608 | +0.0103 [+0.0013, +0.0185] | +0.0003 [-0.0086, +0.0084] | 0.893 | 0.367 | yes |
| 3 | 0.599 (147 of 1871 days never flag) | 111 | 0.420 | 0.523 | 0.0634 | +0.0073 [-0.0035, +0.0171] | +0.0010 [-0.0095, +0.0107] | 0.898 | 0.390 | no |
| 4 | 0.641 (147 of 1870 days never flag) | 109 | 0.420 | 0.532 | 0.0577 | +0.0131 [+0.0060, +0.0197] | +0.0047 [-0.0026, +0.0112] | 0.895 | 0.391 | yes |
| 5 | 0.723 (147 of 1869 days never flag) | 111 | 0.435 | 0.541 | 0.0595 | +0.0114 [+0.0053, +0.0182] | +0.0039 [-0.0025, +0.0106] | 0.856 | 0.405 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1899 [+0.0427, +0.3224]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0774, ΔBrier vs climatology +0.0521 [+0.0340, +0.0716], realised minus predicted +0.0022 [-0.0268, +0.0317]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.515 | 0.3148 | 0.2720 | +0.0153 [-0.0263, +0.0564] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0864 | 0.0159 | +0.0156 [-0.0107, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0007 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0014 | 0.0200 | +0.0016 [-0.0033, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0775 | 0.1165 | +0.0273 [+0.0054, +0.0563] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0028 | 0.0000 | +0.0317 [+0.0248, +0.0383] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0732 | 0.2439 | 0.0166 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.541 | 0.3213 | 0.2615 | +0.0156 [-0.0213, +0.0519] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1035 | 0.1133 | +0.0558 [+0.0323, +0.0818] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.466 | 0.0805 | 0.0630 | +0.0054 [-0.0047, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0543, +0.2097] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0390, +0.0977] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.696] | 0.269 | 4.73 flat / 2.33 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 3.88 flat / 1.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 3.385 [1.808, 5.684] | 1.760 [0.850, 3.125] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.151, 0.471] | 3.077 [1.714, 5.044] | 1.337 [0.681, 2.324] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 3.692 [2.037, 6.106] | 1.500 [0.750, 2.625] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.423 [1.216, 4.051] | 0.837 [0.420, 1.410] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.529] | 3.115 [1.625, 5.278] | 1.308 [0.607, 2.371] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 6.588 [3.952, 11.118] | 3.118 [1.666, 5.918] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.833 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 156 | 0.486 | 0.436 | 0.0496 | +0.0218 [+0.0143, +0.0297] | +0.0067 [+0.0010, +0.0127] | 0.903 | 0.435 | yes |
| 2 | 0.605 (147 of 1872 days never flag) | 135 | 0.396 | 0.407 | 0.0613 | +0.0097 [+0.0041, +0.0154] | -0.0003 [-0.0056, +0.0045] | 0.854 | 0.350 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 169 | 0.529 | 0.432 | 0.0599 | +0.0108 [+0.0060, +0.0154] | +0.0045 [-0.0001, +0.0091] | 0.856 | 0.474 | no |
| 4 | 0.48 (147 of 1870 days never flag) | 124 | 0.442 | 0.492 | 0.0618 | +0.0091 [+0.0045, +0.0135] | +0.0006 [-0.0038, +0.0048] | 0.829 | 0.406 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 140 | 0.428 | 0.421 | 0.0692 | +0.0017 [-0.0037, +0.0067] | -0.0058 [-0.0117, -0.0003] | 0.782 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.492 (climatology 0.512, difference -0.0197 [-0.1117, +0.0624]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0898, ΔBrier vs climatology +0.0397 [+0.0271, +0.0539], realised minus predicted +0.0212 [-0.0113, +0.0580]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.410 | 0.2736 | 0.2720 | +0.0457 [+0.0147, +0.0775] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1223 | 0.0159 | +0.0209 [+0.0043, +0.0353] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0079 | 0.0000 | +0.0134 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0039 | 0.0200 | +0.0037 [-0.0000, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0755 | 0.1165 | +0.0300 [+0.0055, +0.0612] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0051 | 0.0048 | +0.0090 [+0.0072, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0504 | 0.0000 | +0.0282 [+0.0218, +0.0345] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0778 | 0.2439 | 0.0175 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.544 | 0.439 | 0.2818 | 0.2615 | +0.0459 [+0.0179, +0.0739] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1072 | 0.1133 | +0.0584 [+0.0347, +0.0842] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.375 | 0.0795 | 0.0630 | +0.0137 [+0.0063, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0485, +0.2109] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0409, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2722 | 0.2213 |

## risk_gbm+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.700] | 0.262 | 4.50 flat / 2.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.88 flat / 1.59 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.077 [1.625, 5.042] | 1.481 [0.698, 2.542] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.148, 0.500] | 3.000 [1.639, 4.842] | 1.288 [0.630, 2.227] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.500 [1.833, 5.632] | 1.365 [0.643, 2.341] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 2.462 [1.217, 4.094] | 0.827 [0.401, 1.389] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.188, 0.522] | 2.923 [1.500, 4.815] | 1.269 [0.580, 2.250] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 6.294 [3.643, 10.455] | 2.824 [1.525, 4.947] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.667 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 147 | 0.479 | 0.456 | 0.0504 | +0.0210 [+0.0137, +0.0295] | +0.0059 [-0.0001, +0.0122] | 0.897 | 0.432 | yes |
| 2 | 0.452 (147 of 1872 days never flag) | 132 | 0.388 | 0.409 | 0.0617 | +0.0094 [+0.0036, +0.0151] | -0.0006 [-0.0063, +0.0046] | 0.849 | 0.343 | no |
| 3 | 0.726 (147 of 1871 days never flag) | 163 | 0.522 | 0.442 | 0.0600 | +0.0107 [+0.0055, +0.0155] | +0.0044 [-0.0003, +0.0092] | 0.857 | 0.469 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 126 | 0.449 | 0.492 | 0.0604 | +0.0105 [+0.0055, +0.0150] | +0.0020 [-0.0024, +0.0062] | 0.845 | 0.412 | yes |
| 5 | 0.489 (147 of 1869 days never flag) | 129 | 0.384 | 0.411 | 0.0670 | +0.0039 [-0.0012, +0.0088] | -0.0036 [-0.0091, +0.0019] | 0.792 | 0.340 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.512, difference -0.0147 [-0.1229, +0.0768]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0872, ΔBrier vs climatology +0.0423 [+0.0285, +0.0569], realised minus predicted +0.0221 [-0.0105, +0.0568]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.431 | 0.2769 | 0.2720 | +0.0447 [+0.0131, +0.0776] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1254 | 0.0159 | +0.0193 [+0.0030, +0.0347] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0081 | 0.0000 | +0.0134 [+0.0117, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0018 | 0.0200 | +0.0016 [-0.0030, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0296 [+0.0063, +0.0590] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0044 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0518 | 0.0000 | +0.0280 [+0.0216, +0.0343] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0976 | 0.2439 | 0.0158 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.456 | 0.2836 | 0.2615 | +0.0437 [+0.0161, +0.0738] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1047 | 0.1133 | +0.0561 [+0.0322, +0.0814] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.390 | 0.0807 | 0.0630 | +0.0130 [+0.0058, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0526, +0.2114] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0373, +0.0988] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2718 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.312, 0.690] | 0.235 | 4.23 flat / 2.21 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.654] | 0.231 | 3.42 flat / 1.55 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.385 [1.833, 5.633] | 1.760 [0.865, 3.147] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.609] | 1.500 [0.656, 2.800] | 0.615 [0.295, 1.096] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.077 [1.081, 3.542] | 0.856 [0.474, 1.406] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.619] | 2.538 [1.292, 4.421] | 1.183 [0.527, 2.185] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.619] | 2.769 [1.423, 4.800] | 1.260 [0.587, 2.298] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.833] | 5.706 [3.143, 9.572] | 2.882 [1.512, 5.366] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 0.944 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 156 | 0.486 | 0.436 | 0.0496 | +0.0218 [+0.0140, +0.0297] | +0.0067 [+0.0009, +0.0126] | 0.903 | 0.435 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 95 | 0.403 | 0.589 | 0.0545 | +0.0165 [+0.0098, +0.0230] | +0.0065 [+0.0001, +0.0130] | 0.871 | 0.380 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 108 | 0.391 | 0.500 | 0.0566 | +0.0141 [+0.0082, +0.0203] | +0.0078 [+0.0020, +0.0139] | 0.871 | 0.360 | yes |
| 4 | 0.468 (147 of 1870 days never flag) | 120 | 0.391 | 0.450 | 0.0567 | +0.0141 [+0.0086, +0.0196] | +0.0056 [-0.0001, +0.0112] | 0.851 | 0.353 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 132 | 0.435 | 0.455 | 0.0618 | +0.0092 [+0.0032, +0.0154] | +0.0016 [-0.0048, +0.0078] | 0.829 | 0.393 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0178, +0.2693]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0776, ΔBrier vs climatology +0.0519 [+0.0344, +0.0709], realised minus predicted -0.0023 [-0.0330, +0.0273]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.410 | 0.2736 | 0.2720 | +0.0457 [+0.0136, +0.0778] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1223 | 0.0159 | +0.0209 [+0.0043, +0.0354] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0079 | 0.0000 | +0.0134 [+0.0118, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0039 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0755 | 0.1165 | +0.0300 [+0.0052, +0.0623] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0051 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0504 | 0.0000 | +0.0282 [+0.0220, +0.0345] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0778 | 0.2439 | 0.0175 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.544 | 0.439 | 0.2818 | 0.2615 | +0.0459 [+0.0173, +0.0746] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1072 | 0.1133 | +0.0584 [+0.0337, +0.0833] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.375 | 0.0795 | 0.0630 | +0.0137 [+0.0064, +0.0215] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0491, +0.2110] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0424, +0.0948] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2722 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.314, 0.692] | 0.231 | 4.00 flat / 1.95 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.611] | 0.231 | 3.04 flat / 1.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.077 [1.606, 5.143] | 1.481 [0.702, 2.600] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.000 [0.900, 3.467] | 0.798 [0.400, 1.352] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.212, 0.571] | 2.615 [1.208, 4.565] | 1.202 [0.533, 2.220] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 1.885 [0.925, 3.269] | 0.750 [0.375, 1.294] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 2.654 [1.235, 4.646] | 1.231 [0.550, 2.250] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 5.647 [3.091, 9.546] | 2.647 [1.367, 4.751] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 0.889 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 147 | 0.479 | 0.456 | 0.0504 | +0.0210 [+0.0132, +0.0291] | +0.0059 [+0.0001, +0.0120] | 0.897 | 0.432 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 112 | 0.432 | 0.536 | 0.0550 | +0.0161 [+0.0094, +0.0227] | +0.0061 [-0.0005, +0.0123] | 0.871 | 0.402 | yes |
| 3 | 0.599 (147 of 1871 days never flag) | 125 | 0.413 | 0.456 | 0.0569 | +0.0138 [+0.0077, +0.0201] | +0.0075 [+0.0016, +0.0135] | 0.866 | 0.374 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 108 | 0.428 | 0.546 | 0.0546 | +0.0163 [+0.0100, +0.0226] | +0.0078 [+0.0015, +0.0143] | 0.863 | 0.399 | yes |
| 5 | 0.723 (147 of 1869 days never flag) | 128 | 0.428 | 0.461 | 0.0594 | +0.0116 [+0.0054, +0.0178] | +0.0040 [-0.0024, +0.0106] | 0.832 | 0.388 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1899 [+0.0366, +0.3187]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0771, ΔBrier vs climatology +0.0524 [+0.0346, +0.0715], realised minus predicted +0.0003 [-0.0289, +0.0299]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.431 | 0.2769 | 0.2720 | +0.0447 [+0.0133, +0.0778] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1254 | 0.0159 | +0.0193 [+0.0024, +0.0338] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0081 | 0.0000 | +0.0134 [+0.0117, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0018 | 0.0200 | +0.0016 [-0.0031, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0296 [+0.0065, +0.0605] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0044 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0518 | 0.0000 | +0.0280 [+0.0218, +0.0342] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0976 | 0.2439 | 0.0158 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.456 | 0.2836 | 0.2615 | +0.0437 [+0.0145, +0.0740] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1047 | 0.1133 | +0.0561 [+0.0309, +0.0812] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.390 | 0.0807 | 0.0630 | +0.0130 [+0.0055, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0542, +0.2103] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0380, +0.0994] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2718 | 0.2213 |

## risk_gbm+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.192 | 2.04 flat / 1.33 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.568] | 0.154 | 1.62 flat / 1.04 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.346 [0.900, 2.000] | 0.740 [0.457, 1.190] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.594, 1.516] | 0.548 [0.302, 0.926] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.115 [0.679, 1.750] | 0.663 [0.345, 1.161] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.038 [0.606, 1.650] | 0.567 [0.288, 0.980] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.038 [0.621, 1.667] | 0.712 [0.371, 1.250] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 76 | 0.293 | 0.539 | 0.0580 | +0.0134 [+0.0080, +0.0191] | -0.0017 [-0.0097, +0.0061] | 0.642 | 0.273 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0591 | +0.0119 [+0.0070, +0.0168] | +0.0019 [-0.0050, +0.0085] | 0.639 | 0.259 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 65 | 0.261 | 0.554 | 0.0605 | +0.0102 [+0.0048, +0.0154] | +0.0039 [-0.0027, +0.0099] | 0.636 | 0.244 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 64 | 0.268 | 0.578 | 0.0587 | +0.0121 [+0.0071, +0.0170] | +0.0037 [-0.0025, +0.0096] | 0.633 | 0.253 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 62 | 0.254 | 0.565 | 0.0596 | +0.0114 [+0.0065, +0.0160] | +0.0038 [-0.0022, +0.0095] | 0.632 | 0.238 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1902 [+0.0363, +0.3262]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0855, ΔBrier vs climatology +0.0439 [+0.0317, +0.0572], realised minus predicted +0.0590 [+0.0302, +0.0902]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0211, +0.0239] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0167 | 0.0159 | +0.0382 [+0.0294, +0.0470] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0007 | 0.0000 | +0.0137 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0007 | 0.0200 | +0.0016 [-0.0030, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0386 | 0.1165 | +0.0168 [+0.0005, +0.0385] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0014 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0018 | 0.0000 | +0.0317 [+0.0251, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0479 | 0.2439 | -0.0053 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.588 | 0.0985 | 0.2615 | +0.0133 [-0.0073, +0.0339] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0961 | 0.1133 | +0.0522 [+0.0290, +0.0759] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.500 | 0.0133 | 0.0630 | +0.0045 [-0.0005, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2099 | 0.2903 | +0.1309 [+0.0527, +0.2129] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.0988 | 0.1461 | +0.0683 [+0.0393, +0.0972] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2001 | 0.2213 |

## risk_gbm_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.158, 0.460] | 0.115 | 1.35 flat / 0.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 1.462 [0.962, 2.222] | 0.933 [0.532, 1.563] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 0.962 [0.542, 1.524] | 0.490 [0.212, 0.917] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.269 [0.760, 2.042] | 0.798 [0.391, 1.445] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.077 [0.630, 1.684] | 0.606 [0.276, 1.107] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.222 [1.500, 7.400] | 2.861 [1.222, 7.000] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 80 | 0.300 | 0.525 | 0.0586 | +0.0129 [+0.0079, +0.0176] | -0.0022 [-0.0100, +0.0046] | 0.643 | 0.278 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 49 | 0.173 | 0.490 | 0.0686 | +0.0024 [-0.0042, +0.0085] | -0.0076 [-0.0164, +0.0001] | 0.578 | 0.158 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 57 | 0.174 | 0.421 | 0.0674 | +0.0033 [-0.0034, +0.0093] | -0.0030 [-0.0113, +0.0038] | 0.580 | 0.155 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 57 | 0.203 | 0.491 | 0.0660 | +0.0048 [-0.0017, +0.0111] | -0.0036 [-0.0111, +0.0031] | 0.580 | 0.186 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 49 | 0.152 | 0.429 | 0.0696 | +0.0013 [-0.0055, +0.0071] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.136 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.539 (climatology 0.512, difference +0.0266 [-0.1146, +0.1515]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1041, ΔBrier vs climatology +0.0253 [+0.0163, +0.0348], realised minus predicted +0.0899 [+0.0555, +0.1265]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0972 | 0.2720 | -0.0015 [-0.0206, +0.0159] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0237 | 0.0159 | +0.0335 [+0.0228, +0.0443] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [+0.0001, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0377 | 0.1165 | +0.0199 [+0.0032, +0.0405] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0058 | 0.0000 | +0.0309 [+0.0245, +0.0370] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0203 | 0.2439 | 0.0057 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.1021 | 0.2615 | +0.0089 [-0.0095, +0.0255] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.1003 | 0.1133 | +0.0379 [+0.0140, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0129 | 0.0630 | +0.0054 [+0.0003, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1126 [+0.0332, +0.1946] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1168 | 0.1461 | +0.0706 [+0.0489, +0.0946] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2084 | 0.2213 |

## risk_gbm_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.824] | 0.284 | 6.04 flat / 2.73 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.619] | 0.265 | 4.58 flat / 1.99 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.300, 0.636] | 2.846 [1.853, 4.264] | 1.144 [0.695, 1.818] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 2.923 [1.806, 4.462] | 1.154 [0.707, 1.792] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 2.885 [1.636, 4.643] | 1.231 [0.636, 2.087] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 2.000 [1.151, 3.222] | 0.663 [0.385, 1.065] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.387] | 2.654 [1.538, 4.304] | 1.038 [0.600, 1.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.118 [3.749, 9.819] | 2.574 [1.428, 4.340] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 5.889 (no interval) | 3.028 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 155 | 0.579 | 0.523 | 0.0486 | +0.0228 [+0.0155, +0.0309] | +0.0077 [+0.0030, +0.0129] | 0.899 | 0.536 | yes |
| 2 | 0.315 (147 of 1872 days never flag) | 137 | 0.439 | 0.445 | 0.0601 | +0.0110 [+0.0069, +0.0151] | +0.0010 [-0.0021, +0.0039] | 0.836 | 0.395 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 134 | 0.428 | 0.440 | 0.0613 | +0.0094 [+0.0056, +0.0132] | +0.0031 [+0.0001, +0.0061] | 0.812 | 0.384 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 110 | 0.420 | 0.527 | 0.0585 | +0.0123 [+0.0074, +0.0173] | +0.0038 [+0.0007, +0.0072] | 0.838 | 0.390 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 119 | 0.362 | 0.420 | 0.0630 | +0.0080 [+0.0035, +0.0120] | +0.0004 [-0.0026, +0.0034] | 0.782 | 0.322 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.534 (climatology 0.512, difference +0.0222 [-0.1006, +0.1277]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0448 [+0.0306, +0.0605], realised minus predicted +0.0098 [-0.0214, +0.0442]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0542 [+0.0257, +0.0845] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1263 | 0.0159 | +0.0173 [+0.0016, +0.0307] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0321 | 0.0200 | +0.0008 [-0.0060, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.1139 | 0.1165 | +0.0318 [+0.0048, +0.0663] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0225 | 0.0048 | +0.0080 [+0.0057, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0691 | 0.0000 | +0.0246 [+0.0189, +0.0302] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1409 | 0.2439 | 0.0481 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.632 | 0.534 | 0.2526 | 0.2615 | +0.0517 [+0.0258, +0.0791] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1097 | 0.1133 | +0.0430 [+0.0192, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.479 | 0.0863 | 0.0630 | +0.0165 [+0.0094, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0371, +0.1936] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0951] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.269 | 5.73 flat / 2.55 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.556] | 0.246 | 4.38 flat / 1.89 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.588] | 2.423 [1.600, 3.652] | 0.904 [0.570, 1.408] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.615 [1.633, 3.950] | 1.029 [0.631, 1.563] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.885 [1.739, 4.500] | 1.115 [0.686, 1.750] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 2.231 [1.375, 3.455] | 0.865 [0.543, 1.370] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.121, 0.435] | 2.346 [1.400, 3.696] | 0.990 [0.591, 1.583] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 5.000 [3.056, 8.167] | 1.882 [1.125, 3.200] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.111 (no interval) | 3.806 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 134 | 0.507 | 0.530 | 0.0505 | +0.0209 [+0.0140, +0.0279] | +0.0058 [+0.0012, +0.0105] | 0.805 | 0.471 | no |
| 2 | 0.315 (147 of 1872 days never flag) | 122 | 0.388 | 0.443 | 0.0623 | +0.0087 [+0.0040, +0.0133] | -0.0013 [-0.0054, +0.0025] | 0.749 | 0.349 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 130 | 0.399 | 0.423 | 0.0613 | +0.0094 [+0.0044, +0.0142] | +0.0030 [-0.0014, +0.0070] | 0.746 | 0.355 | no |
| 4 | 0.265 (147 of 1870 days never flag) | 116 | 0.420 | 0.500 | 0.0594 | +0.0114 [+0.0060, +0.0167] | +0.0030 [-0.0008, +0.0067] | 0.763 | 0.387 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 107 | 0.333 | 0.430 | 0.0636 | +0.0073 [+0.0021, +0.0121] | -0.0002 [-0.0043, +0.0036] | 0.740 | 0.298 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.544 (climatology 0.512, difference +0.0322 [-0.0976, +0.1388]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0429 [+0.0300, +0.0571], realised minus predicted +0.0588 [+0.0304, +0.0903]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.559 | 0.1689 | 0.2720 | +0.0386 [+0.0127, +0.0658] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0313 | 0.0159 | +0.0263 [+0.0081, +0.0404] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0145 | 0.0200 | +0.0009 [-0.0065, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.0889 | 0.1165 | +0.0310 [+0.0055, +0.0607] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0086 | 0.0048 | +0.0082 [+0.0059, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0070 | 0.0000 | +0.0308 [+0.0244, +0.0366] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1098 | 0.2439 | 0.0458 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.543 | 0.1761 | 0.2615 | +0.0401 [+0.0146, +0.0649] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1041 | 0.1133 | +0.0436 [+0.0174, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.479 | 0.0421 | 0.0630 | +0.0143 [+0.0078, +0.0210] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0341, +0.1908] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0952] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3903 | 0.2213 |

## risk_gbm_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.800] | 0.269 | 5.73 flat / 2.59 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.600] | 0.250 | 4.42 flat / 1.98 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.680] | 2.462 [1.538, 3.824] | 1.019 [0.629, 1.588] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.462] | 2.808 [1.775, 4.300] | 1.106 [0.685, 1.750] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 2.885 [1.667, 4.696] | 1.240 [0.666, 2.145] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.500 [1.390, 4.087] | 0.933 [0.500, 1.525] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.385 [1.517, 3.692] | 1.048 [0.635, 1.671] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 6.471 [4.000, 10.309] | 2.632 [1.538, 4.438] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.333 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 135 | 0.507 | 0.526 | 0.0487 | +0.0227 [+0.0162, +0.0302] | +0.0076 [+0.0030, +0.0127] | 0.893 | 0.470 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 134 | 0.439 | 0.455 | 0.0594 | +0.0116 [+0.0085, +0.0151] | +0.0016 [-0.0017, +0.0051] | 0.820 | 0.397 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 131 | 0.406 | 0.427 | 0.0598 | +0.0109 [+0.0075, +0.0145] | +0.0045 [+0.0011, +0.0085] | 0.802 | 0.363 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 126 | 0.442 | 0.484 | 0.0567 | +0.0141 [+0.0099, +0.0183] | +0.0056 [+0.0026, +0.0089] | 0.835 | 0.405 | no |
| 5 | 0.265 (147 of 1869 days never flag) | 113 | 0.370 | 0.451 | 0.0613 | +0.0096 [+0.0062, +0.0130] | +0.0021 [-0.0010, +0.0050] | 0.772 | 0.334 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.535 (climatology 0.512, difference +0.0228 [-0.0941, +0.1215]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0857, ΔBrier vs climatology +0.0437 [+0.0300, +0.0589], realised minus predicted +0.0197 [-0.0113, +0.0551]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.523 | 0.2205 | 0.2720 | +0.0484 [+0.0229, +0.0773] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1138 | 0.0159 | +0.0229 [+0.0100, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0155 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0227 | 0.0200 | +0.0029 [-0.0014, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.667 | 0.0976 | 0.1165 | +0.0320 [+0.0078, +0.0614] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0170 | 0.0048 | +0.0090 [+0.0071, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0607 | 0.0000 | +0.0257 [+0.0200, +0.0314] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1137 | 0.2439 | 0.0482 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.523 | 0.2331 | 0.2615 | +0.0486 [+0.0250, +0.0746] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1082 | 0.1133 | +0.0422 [+0.0179, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.474 | 0.0748 | 0.0630 | +0.0165 [+0.0103, +0.0237] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0372, +0.1918] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1168 | 0.1461 | +0.0706 [+0.0489, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0837 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2566 | 0.2213 |

## risk_gbm_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.833] | 0.269 | 5.73 flat / 2.57 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.242 | 4.35 flat / 1.85 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.636] | 2.769 [1.793, 4.143] | 1.125 [0.700, 1.786] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.962 [1.862, 4.445] | 1.163 [0.741, 1.794] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.520] | 3.000 [1.750, 4.778] | 1.260 [0.690, 2.103] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.923 [1.051, 3.154] | 0.625 [0.343, 1.019] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.538 [1.417, 4.087] | 0.942 [0.524, 1.518] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.118 [3.818, 9.909] | 2.574 [1.515, 4.344] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.750] | 5.000 [2.997, 9.500] | 2.556 [1.438, 5.375] |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 153 | 0.579 | 0.529 | 0.0478 | +0.0237 [+0.0164, +0.0313] | +0.0086 [+0.0041, +0.0137] | 0.914 | 0.537 | yes |
| 2 | 0.315 (147 of 1872 days never flag) | 139 | 0.446 | 0.446 | 0.0592 | +0.0119 [+0.0075, +0.0160] | +0.0019 [-0.0012, +0.0049] | 0.875 | 0.402 | yes |
| 3 | 0.458 (147 of 1871 days never flag) | 138 | 0.435 | 0.435 | 0.0594 | +0.0113 [+0.0077, +0.0153] | +0.0050 [+0.0020, +0.0081] | 0.862 | 0.390 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 110 | 0.435 | 0.545 | 0.0571 | +0.0138 [+0.0093, +0.0187] | +0.0053 [+0.0024, +0.0087] | 0.874 | 0.406 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 116 | 0.362 | 0.431 | 0.0618 | +0.0091 [+0.0049, +0.0132] | +0.0016 [-0.0015, +0.0046] | 0.846 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.534 (climatology 0.512, difference +0.0222 [-0.0983, +0.1196]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0831, ΔBrier vs climatology +0.0463 [+0.0324, +0.0618], realised minus predicted +0.0369 [+0.0061, +0.0695]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0542 [+0.0277, +0.0836] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1260 | 0.0159 | +0.0173 [+0.0018, +0.0320] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0043 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0022 | 0.0200 | +0.0038 [-0.0002, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0974 | 0.1165 | +0.0343 [+0.0077, +0.0644] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0009 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0691 | 0.0000 | +0.0246 [+0.0191, +0.0303] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1409 | 0.2439 | 0.0481 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.632 | 0.534 | 0.2526 | 0.2615 | +0.0517 [+0.0265, +0.0789] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1076 | 0.1133 | +0.0431 [+0.0173, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.487 | 0.0725 | 0.0630 | +0.0175 [+0.0106, +0.0249] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0335, +0.1904] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0931] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.718] | 0.231 | 3.62 flat / 1.81 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.462] | 0.192 | 2.00 flat / 1.08 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 2.346 [1.655, 3.500] | 0.971 [0.651, 1.513] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 1.269 [0.815, 1.957] | 0.558 [0.300, 0.957] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.000 [0.581, 1.619] | 0.442 [0.214, 0.816] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.115 [0.682, 1.727] | 0.462 [0.250, 0.786] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.423 [0.912, 2.263] | 0.769 [0.430, 1.307] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.812] | 2.706 [1.636, 4.556] | 1.044 [0.604, 1.808] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.751] | 5.333 [3.222, 10.750] | 3.250 [1.795, 7.125] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 128 | 0.479 | 0.523 | 0.0492 | +0.0222 [+0.0169, +0.0277] | +0.0071 [+0.0023, +0.0116] | 0.908 | 0.443 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 65 | 0.230 | 0.492 | 0.0603 | +0.0107 [+0.0074, +0.0138] | +0.0007 [-0.0037, +0.0045] | 0.845 | 0.211 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 52 | 0.188 | 0.500 | 0.0605 | +0.0102 [+0.0067, +0.0135] | +0.0039 [-0.0003, +0.0077] | 0.824 | 0.173 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 62 | 0.239 | 0.532 | 0.0584 | +0.0125 [+0.0085, +0.0165] | +0.0040 [+0.0001, +0.0077] | 0.841 | 0.222 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 62 | 0.181 | 0.403 | 0.0624 | +0.0085 [+0.0051, +0.0118] | +0.0010 [-0.0028, +0.0044] | 0.791 | 0.160 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.526 (climatology 0.512, difference +0.0141 [-0.1025, +0.1244]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0897, ΔBrier vs climatology +0.0398 [+0.0288, +0.0513], realised minus predicted +0.0507 [+0.0176, +0.0856]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.576 | 0.1679 | 0.2720 | +0.0397 [+0.0236, +0.0565] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0750 | 0.0159 | +0.0305 [+0.0195, +0.0408] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0032 [-0.0013, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.0758 | 0.1165 | +0.0324 [+0.0085, +0.0609] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0117 | 0.0048 | +0.0092 [+0.0073, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0375 | 0.0000 | +0.0293 [+0.0233, +0.0352] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0806 | 0.2439 | 0.0353 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.551 | 0.1774 | 0.2615 | +0.0449 [+0.0275, +0.0625] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1050 | 0.1133 | +0.0408 [+0.0165, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.494 | 0.0496 | 0.0630 | +0.0161 [+0.0117, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2030 | 0.2903 | +0.1126 [+0.0374, +0.1919] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2254 | 0.2213 |

## risk_gbm_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.767] | 0.231 | 3.96 flat / 1.61 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.567] | 0.231 | 3.15 flat / 1.13 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 2.423 [1.333, 3.965] | 1.000 [0.558, 1.681] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.192 [1.087, 3.724] | 0.788 [0.389, 1.344] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.481] | 2.538 [1.273, 4.209] | 0.894 [0.461, 1.478] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.769 [0.744, 3.154] | 0.548 [0.212, 1.010] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 2.038 [0.950, 3.538] | 0.712 [0.327, 1.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.955] | 5.176 [3.059, 8.429] | 1.971 [1.150, 3.316] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.667 [0.692, 3.857] | 0.917 [0.318, 2.333] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (105 of 1873 days never flag) | 135 | 0.514 | 0.533 | 0.0615 | +0.0099 [+0.0001, +0.0193] | -0.0051 [-0.0140, +0.0029] | 0.874 | 0.478 | no |
| 2 | 0.603 (147 of 1872 days never flag) | 109 | 0.374 | 0.477 | 0.0716 | -0.0006 [-0.0096, +0.0072] | -0.0106 [-0.0192, -0.0031] | 0.817 | 0.341 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 121 | 0.399 | 0.455 | 0.0733 | -0.0026 [-0.0115, +0.0051] | -0.0089 [-0.0175, -0.0013] | 0.796 | 0.360 | no |
| 4 | 0.643 (147 of 1870 days never flag) | 96 | 0.362 | 0.521 | 0.0694 | +0.0015 [-0.0058, +0.0085] | -0.0070 [-0.0137, -0.0006] | 0.823 | 0.336 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 102 | 0.355 | 0.480 | 0.0728 | -0.0019 [-0.0084, +0.0035] | -0.0094 [-0.0158, -0.0040] | 0.770 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.501 (climatology 0.512, difference -0.0110 [-0.1232, +0.0940]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0224, +0.0512], realised minus predicted +0.0046 [-0.0308, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.3131 | 0.2720 | +0.0099 [-0.0341, +0.0495] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2009 | 0.0159 | -0.0101 [-0.0343, +0.0089] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0027 [-0.0027, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0674 | 0.1165 | +0.0312 [+0.0072, +0.0606] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0072 | 0.0048 | +0.0086 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1136 | 0.0000 | +0.0113 [+0.0058, +0.0169] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0972 | 0.2439 | 0.0369 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.533 | 0.3157 | 0.2615 | +0.0098 [-0.0291, +0.0446] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1110 | 0.1133 | +0.0404 [+0.0156, +0.0675] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.490 | 0.1027 | 0.0630 | +0.0017 [-0.0087, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0339, +0.1905] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0923] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2962 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.368, 0.778] | 0.231 | 3.96 flat / 1.58 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.182, 0.517] | 0.231 | 3.15 flat / 1.13 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.647] | 3.077 [1.742, 4.862] | 1.183 [0.674, 1.889] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.379] | 2.269 [1.148, 3.728] | 0.808 [0.402, 1.357] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.111, 0.448] | 2.462 [1.185, 4.139] | 0.817 [0.383, 1.398] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.378] | 1.846 [0.842, 3.218] | 0.625 [0.284, 1.119] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.154 [1.062, 3.694] | 0.769 [0.378, 1.327] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.958] | 5.176 [3.083, 8.385] | 1.971 [1.148, 3.306] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.667 [0.750, 3.625] | 0.833 [0.333, 1.959] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 161 | 0.579 | 0.503 | 0.0617 | +0.0097 [-0.0002, +0.0192] | -0.0054 [-0.0137, +0.0022] | 0.874 | 0.532 | no |
| 2 | 0.607 (147 of 1872 days never flag) | 110 | 0.367 | 0.464 | 0.0721 | -0.0011 [-0.0095, +0.0068] | -0.0111 [-0.0191, -0.0036] | 0.814 | 0.333 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 118 | 0.391 | 0.458 | 0.0728 | -0.0021 [-0.0122, +0.0057] | -0.0084 [-0.0180, -0.0009] | 0.797 | 0.354 | no |
| 4 | 0.588 (147 of 1870 days never flag) | 99 | 0.370 | 0.515 | 0.0705 | +0.0003 [-0.0075, +0.0073] | -0.0082 [-0.0152, -0.0014] | 0.819 | 0.342 | yes |
| 5 | 0.575 (147 of 1869 days never flag) | 105 | 0.355 | 0.467 | 0.0729 | -0.0020 [-0.0083, +0.0037] | -0.0095 [-0.0156, -0.0038] | 0.771 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.512, difference -0.0138 [-0.1284, +0.0885]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0918, ΔBrier vs climatology +0.0377 [+0.0232, +0.0544], realised minus predicted +0.0039 [-0.0299, +0.0400]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.487 | 0.3159 | 0.2720 | +0.0093 [-0.0342, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1988 | 0.0159 | -0.0092 [-0.0323, +0.0093] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0045 | 0.0200 | -0.0001 [-0.0066, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0654 | 0.1165 | +0.0318 [+0.0097, +0.0597] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0080 [+0.0058, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1120 | 0.0000 | +0.0117 [+0.0061, +0.0177] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1019 | 0.2439 | 0.0494 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.648 | 0.503 | 0.3169 | 0.2615 | +0.0086 [-0.0288, +0.0447] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1089 | 0.1133 | +0.0435 [+0.0219, +0.0664] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.450 | 0.1032 | 0.0630 | +0.0011 [-0.0098, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0365, +0.1928] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0943] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.308, 0.682] | 0.231 | 3.62 flat / 1.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.619] | 0.231 | 2.58 flat / 1.05 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.200, 0.556] | 2.423 [1.314, 4.000] | 1.000 [0.547, 1.656] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 1.731 [0.833, 3.059] | 0.692 [0.352, 1.182] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 2.115 [1.000, 3.750] | 0.856 [0.444, 1.475] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 2.077 [0.960, 3.750] | 0.837 [0.419, 1.463] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 1.962 [1.036, 3.333] | 0.798 [0.435, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 4.529 [2.562, 7.644] | 1.824 [1.042, 3.146] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.889 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (105 of 1873 days never flag) | 135 | 0.514 | 0.533 | 0.0615 | +0.0099 [+0.0001, +0.0193] | -0.0051 [-0.0137, +0.0026] | 0.874 | 0.478 | no |
| 2 | 0.599 (147 of 1872 days never flag) | 104 | 0.424 | 0.567 | 0.0650 | +0.0060 [-0.0035, +0.0153] | -0.0040 [-0.0134, +0.0044] | 0.846 | 0.398 | no |
| 3 | 0.593 (147 of 1871 days never flag) | 115 | 0.435 | 0.522 | 0.0673 | +0.0034 [-0.0061, +0.0122] | -0.0029 [-0.0123, +0.0059] | 0.830 | 0.403 | yes |
| 4 | 0.765 (147 of 1870 days never flag) | 115 | 0.442 | 0.530 | 0.0650 | +0.0059 [-0.0023, +0.0133] | -0.0026 [-0.0109, +0.0049] | 0.843 | 0.411 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 104 | 0.384 | 0.510 | 0.0665 | +0.0044 [-0.0025, +0.0109] | -0.0031 [-0.0102, +0.0032] | 0.819 | 0.355 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1658 [+0.0518, +0.2840]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0450 [+0.0244, +0.0673], realised minus predicted -0.0207 [-0.0524, +0.0120]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.3131 | 0.2720 | +0.0099 [-0.0329, +0.0526] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2009 | 0.0159 | -0.0101 [-0.0344, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0027 [-0.0021, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0674 | 0.1165 | +0.0312 [+0.0066, +0.0611] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0072 | 0.0048 | +0.0086 [+0.0068, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1136 | 0.0000 | +0.0113 [+0.0059, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0972 | 0.2439 | 0.0369 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.533 | 0.3157 | 0.2615 | +0.0098 [-0.0290, +0.0465] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1110 | 0.1133 | +0.0404 [+0.0156, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.490 | 0.1027 | 0.0630 | +0.0017 [-0.0088, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0359, +0.1919] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0945] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2962 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.345, 0.727] | 0.231 | 3.73 flat / 1.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.231, 0.611] | 0.192 | 2.35 flat / 0.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.640] | 3.077 [1.724, 5.000] | 1.183 [0.667, 1.920] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.269 [1.153, 4.000] | 0.837 [0.437, 1.438] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.538 [0.667, 2.840] | 0.606 [0.286, 1.088] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.885 [0.896, 3.318] | 0.769 [0.392, 1.326] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.115 [1.000, 3.775] | 0.808 [0.413, 1.389] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.882 [2.850, 8.314] | 1.926 [1.104, 3.312] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.556 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 161 | 0.579 | 0.503 | 0.0617 | +0.0097 [-0.0000, +0.0195] | -0.0054 [-0.0136, +0.0025] | 0.874 | 0.532 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 119 | 0.432 | 0.504 | 0.0658 | +0.0053 [-0.0035, +0.0138] | -0.0047 [-0.0135, +0.0034] | 0.839 | 0.398 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 92 | 0.377 | 0.565 | 0.0669 | +0.0038 [-0.0052, +0.0127] | -0.0025 [-0.0116, +0.0060] | 0.825 | 0.354 | no |
| 4 | 0.713 (147 of 1870 days never flag) | 107 | 0.420 | 0.542 | 0.0649 | +0.0060 [-0.0025, +0.0146] | -0.0025 [-0.0106, +0.0061] | 0.845 | 0.392 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 116 | 0.442 | 0.526 | 0.0662 | +0.0047 [-0.0020, +0.0114] | -0.0028 [-0.0094, +0.0041] | 0.821 | 0.410 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.718 (climatology 0.512, difference +0.2062 [+0.0614, +0.3424]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0831, ΔBrier vs climatology +0.0464 [+0.0271, +0.0663], realised minus predicted -0.0194 [-0.0506, +0.0131]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.487 | 0.3159 | 0.2720 | +0.0093 [-0.0343, +0.0511] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1988 | 0.0159 | -0.0092 [-0.0313, +0.0102] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0105, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0045 | 0.0200 | -0.0001 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0654 | 0.1165 | +0.0318 [+0.0096, +0.0601] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0080 [+0.0058, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1120 | 0.0000 | +0.0117 [+0.0058, +0.0179] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1019 | 0.2439 | 0.0494 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.648 | 0.503 | 0.3169 | 0.2615 | +0.0086 [-0.0288, +0.0458] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1089 | 0.1133 | +0.0435 [+0.0210, +0.0666] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.450 | 0.1032 | 0.0630 | +0.0011 [-0.0096, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0325, +0.1916] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.800] | 0.269 | 5.12 flat / 2.28 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.231 | 4.23 flat / 1.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.731 [1.667, 4.182] | 1.106 [0.670, 1.776] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.615 [1.454, 4.059] | 0.981 [0.539, 1.529] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.538 [1.272, 4.227] | 0.913 [0.472, 1.517] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.471] | 2.385 [1.241, 4.050] | 0.817 [0.414, 1.375] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 3.038 [1.520, 5.159] | 1.308 [0.609, 2.380] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 6.412 [3.900, 10.211] | 2.735 [1.571, 4.728] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.417 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 151 | 0.571 | 0.530 | 0.0569 | +0.0145 [+0.0069, +0.0226] | -0.0006 [-0.0069, +0.0054] | 0.852 | 0.530 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 117 | 0.353 | 0.419 | 0.0698 | +0.0013 [-0.0041, +0.0065] | -0.0087 [-0.0146, -0.0032] | 0.773 | 0.313 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 122 | 0.406 | 0.459 | 0.0706 | +0.0000 [-0.0047, +0.0044] | -0.0063 [-0.0112, -0.0017] | 0.726 | 0.368 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 118 | 0.406 | 0.475 | 0.0683 | +0.0025 [-0.0028, +0.0075] | -0.0059 [-0.0110, -0.0011] | 0.768 | 0.370 | yes |
| 5 | 0.498 (147 of 1869 days never flag) | 130 | 0.370 | 0.392 | 0.0728 | -0.0019 [-0.0073, +0.0032] | -0.0094 [-0.0153, -0.0038] | 0.709 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.512, difference -0.0153 [-0.1294, +0.0940]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0960, ΔBrier vs climatology +0.0335 [+0.0199, +0.0483], realised minus predicted -0.0133 [-0.0493, +0.0253]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.519 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0687] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2090 | 0.0159 | -0.0081 [-0.0241, +0.0060] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0027 [-0.0030, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0662 | 0.1165 | +0.0290 [+0.0078, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0206 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1332 | 0.0000 | +0.0055 [+0.0001, +0.0108] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0744 | 0.2439 | 0.0157 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.530 | 0.2903 | 0.2615 | +0.0341 [+0.0043, +0.0649] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1118 | 0.1133 | +0.0396 [+0.0167, +0.0640] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.491 | 0.1070 | 0.0630 | +0.0071 [-0.0005, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0356, +0.1888] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1168 | 0.1461 | +0.0706 [+0.0484, +0.0944] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2920 | 0.2213 |

## risk_gbm_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.774] | 0.269 | 5.08 flat / 2.19 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.618] | 0.231 | 4.15 flat / 1.70 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.696] | 3.423 [2.111, 5.333] | 1.337 [0.800, 2.135] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.385] | 2.577 [1.412, 4.209] | 0.971 [0.518, 1.602] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.172, 0.529] | 2.500 [1.241, 4.261] | 0.817 [0.389, 1.430] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 2.308 [1.143, 4.000] | 0.769 [0.367, 1.353] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.115 [1.580, 5.282] | 1.356 [0.632, 2.517] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.412 [3.818, 10.637] | 2.735 [1.509, 4.902] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 2.556 [1.300, 5.337] | 1.167 [0.577, 2.583] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 173 | 0.600 | 0.486 | 0.0572 | +0.0142 [+0.0066, +0.0228] | -0.0009 [-0.0066, +0.0054] | 0.850 | 0.549 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 115 | 0.345 | 0.417 | 0.0703 | +0.0008 [-0.0050, +0.0063] | -0.0092 [-0.0151, -0.0033] | 0.770 | 0.307 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 122 | 0.413 | 0.467 | 0.0701 | +0.0006 [-0.0040, +0.0050] | -0.0058 [-0.0108, -0.0009] | 0.728 | 0.376 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 116 | 0.406 | 0.483 | 0.0695 | +0.0013 [-0.0038, +0.0063] | -0.0071 [-0.0122, -0.0021] | 0.762 | 0.371 | yes |
| 5 | 0.498 (147 of 1869 days never flag) | 133 | 0.377 | 0.391 | 0.0729 | -0.0020 [-0.0078, +0.0030] | -0.0095 [-0.0155, -0.0039] | 0.709 | 0.330 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.495 (climatology 0.512, difference -0.0169 [-0.1304, +0.0848]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0345 [+0.0206, +0.0496], realised minus predicted -0.0138 [-0.0497, +0.0250]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.481 | 0.2869 | 0.2720 | +0.0353 [+0.0025, +0.0716] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2069 | 0.0159 | -0.0072 [-0.0222, +0.0072] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0090 | 0.0200 | -0.0000 [-0.0064, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0642 | 0.1165 | +0.0297 [+0.0090, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0200 | 0.0048 | +0.0076 [+0.0055, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1316 | 0.0000 | +0.0059 [+0.0008, +0.0116] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0790 | 0.2439 | 0.0282 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.486 | 0.2915 | 0.2615 | +0.0329 [+0.0033, +0.0651] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1096 | 0.1133 | +0.0427 [+0.0224, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.441 | 0.1075 | 0.0630 | +0.0065 [-0.0011, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0307, +0.1935] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0966] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2851 | 0.2213 |

## risk_gbm_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.680] | 0.262 | 4.50 flat / 2.01 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 3.35 flat / 1.49 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.594] | 2.731 [1.680, 4.308] | 1.106 [0.655, 1.792] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.192 [1.125, 3.810] | 0.856 [0.463, 1.431] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 1.962 [0.957, 3.423] | 0.798 [0.409, 1.364] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.115 [1.087, 3.652] | 0.894 [0.484, 1.522] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.769 [1.406, 4.750] | 1.269 [0.581, 2.316] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.706 [3.400, 9.445] | 2.544 [1.438, 4.470] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.222 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 151 | 0.571 | 0.530 | 0.0569 | +0.0145 [+0.0068, +0.0228] | -0.0006 [-0.0065, +0.0058] | 0.852 | 0.530 | yes |
| 2 | 0.599 (147 of 1872 days never flag) | 117 | 0.432 | 0.513 | 0.0624 | +0.0087 [+0.0018, +0.0158] | -0.0013 [-0.0085, +0.0056] | 0.815 | 0.399 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 112 | 0.442 | 0.545 | 0.0641 | +0.0066 [+0.0004, +0.0131] | +0.0003 [-0.0061, +0.0067] | 0.774 | 0.413 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 112 | 0.413 | 0.509 | 0.0636 | +0.0073 [+0.0010, +0.0133] | -0.0012 [-0.0076, +0.0051] | 0.795 | 0.381 | yes |
| 5 | 0.655 (147 of 1869 days never flag) | 129 | 0.413 | 0.442 | 0.0662 | +0.0047 [-0.0018, +0.0110] | -0.0029 [-0.0094, +0.0040] | 0.772 | 0.371 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1665 [+0.0511, +0.2853]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0860, ΔBrier vs climatology +0.0435 [+0.0244, +0.0650], realised minus predicted -0.0400 [-0.0718, -0.0060]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.519 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0706] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2090 | 0.0159 | -0.0081 [-0.0243, +0.0055] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0027 [-0.0022, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0662 | 0.1165 | +0.0290 [+0.0070, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0206 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1332 | 0.0000 | +0.0055 [+0.0003, +0.0109] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0744 | 0.2439 | 0.0157 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.530 | 0.2903 | 0.2615 | +0.0341 [+0.0033, +0.0648] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1118 | 0.1133 | +0.0396 [+0.0164, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.491 | 0.1070 | 0.0630 | +0.0071 [-0.0006, +0.0155] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0339, +0.1887] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1168 | 0.1461 | +0.0706 [+0.0478, +0.0937] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2920 | 0.2213 |

## risk_gbm_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.727] | 0.269 | 4.81 flat / 2.16 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.233, 0.616] | 0.231 | 3.38 flat / 1.56 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.680] | 3.423 [2.080, 5.302] | 1.337 [0.796, 2.119] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 2.000 [1.094, 3.375] | 0.760 [0.432, 1.260] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.692 [0.823, 3.035] | 0.673 [0.340, 1.202] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.962 [1.000, 3.400] | 0.827 [0.453, 1.398] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 3.115 [1.700, 5.269] | 1.423 [0.737, 2.488] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 6.000 [3.625, 9.779] | 2.632 [1.500, 4.625] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.556 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 173 | 0.600 | 0.486 | 0.0572 | +0.0142 [+0.0067, +0.0222] | -0.0009 [-0.0067, +0.0050] | 0.850 | 0.549 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 104 | 0.374 | 0.500 | 0.0631 | +0.0079 [+0.0013, +0.0143] | -0.0021 [-0.0088, +0.0044] | 0.805 | 0.344 | yes |
| 3 | 0.466 (147 of 1871 days never flag) | 98 | 0.391 | 0.551 | 0.0637 | +0.0070 [+0.0011, +0.0134] | +0.0007 [-0.0054, +0.0074] | 0.768 | 0.366 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 106 | 0.399 | 0.519 | 0.0635 | +0.0074 [+0.0008, +0.0140] | -0.0011 [-0.0079, +0.0061] | 0.798 | 0.369 | yes |
| 5 | 0.528 (147 of 1869 days never flag) | 142 | 0.442 | 0.430 | 0.0659 | +0.0050 [-0.0014, +0.0111] | -0.0025 [-0.0093, +0.0042] | 0.773 | 0.395 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.512, difference +0.2074 [+0.0600, +0.3396]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0268, +0.0642], realised minus predicted -0.0386 [-0.0698, -0.0044]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.481 | 0.2869 | 0.2720 | +0.0353 [+0.0035, +0.0676] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2069 | 0.0159 | -0.0072 [-0.0222, +0.0062] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0090 | 0.0200 | -0.0000 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0642 | 0.1165 | +0.0297 [+0.0093, +0.0557] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0200 | 0.0048 | +0.0076 [+0.0056, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1316 | 0.0000 | +0.0059 [+0.0008, +0.0116] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0790 | 0.2439 | 0.0282 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.486 | 0.2915 | 0.2615 | +0.0329 [+0.0040, +0.0629] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1096 | 0.1133 | +0.0427 [+0.0207, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.441 | 0.1075 | 0.0630 | +0.0065 [-0.0010, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0329, +0.1885] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0481, +0.0952] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2851 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.235, 0.625] | 0.231 | 3.77 flat / 1.70 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.485] | 0.231 | 2.69 flat / 0.94 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.172, 0.542] | 3.077 [1.667, 5.168] | 1.423 [0.716, 2.580] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 2.231 [1.111, 3.826] | 0.798 [0.380, 1.364] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.105, 0.444] | 2.500 [1.207, 4.250] | 0.865 [0.412, 1.481] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.115, 0.441] | 2.000 [0.947, 3.522] | 0.663 [0.302, 1.161] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 1.846 [0.810, 3.286] | 0.625 [0.274, 1.125] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.278, 0.778] | 5.118 [2.840, 8.820] | 2.250 [1.178, 4.234] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 1.222 [0.462, 2.864] | 0.667 [0.187, 1.834] |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (126 of 1873 days never flag) | 155 | 0.536 | 0.484 | 0.0571 | +0.0143 [+0.0046, +0.0237] | -0.0008 [-0.0089, +0.0068] | 0.920 | 0.490 | yes |
| 2 | 0.603 (147 of 1872 days never flag) | 114 | 0.403 | 0.491 | 0.0664 | +0.0047 [-0.0048, +0.0124] | -0.0053 [-0.0141, +0.0022] | 0.879 | 0.369 | no |
| 3 | 0.621 (147 of 1871 days never flag) | 124 | 0.428 | 0.476 | 0.0668 | +0.0039 [-0.0060, +0.0125] | -0.0024 [-0.0117, +0.0057] | 0.891 | 0.390 | no |
| 4 | 0.643 (147 of 1870 days never flag) | 102 | 0.362 | 0.490 | 0.0647 | +0.0061 [-0.0011, +0.0126] | -0.0023 [-0.0090, +0.0037] | 0.855 | 0.332 | no |
| 5 | 0.683 (147 of 1869 days never flag) | 96 | 0.348 | 0.500 | 0.0727 | -0.0018 [-0.0108, +0.0060] | -0.0093 [-0.0181, -0.0018] | 0.814 | 0.320 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.513 (climatology 0.512, difference +0.0013 [-0.0974, +0.1058]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0873, ΔBrier vs climatology +0.0422 [+0.0274, +0.0587], realised minus predicted +0.0217 [-0.0109, +0.0567]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.465 | 0.3139 | 0.2720 | +0.0138 [-0.0278, +0.0533] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0927 | 0.0159 | +0.0113 [-0.0168, +0.0345] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0038 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0764 | 0.1165 | +0.0302 [+0.0088, +0.0588] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0018 | 0.0048 | +0.0095 [+0.0080, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0069 | 0.0000 | +0.0309 [+0.0243, +0.0373] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0457 | 0.2439 | 0.0276 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.484 | 0.3240 | 0.2615 | +0.0127 [-0.0242, +0.0488] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1075 | 0.1133 | +0.0411 [+0.0185, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.435 | 0.0799 | 0.0630 | +0.0068 [-0.0033, +0.0166] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0383, +0.1920] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0481, +0.0937] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2894 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.300, 0.700] | 0.231 | 3.85 flat / 1.61 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.565] | 0.231 | 3.27 flat / 1.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.210, 0.571] | 2.923 [1.538, 4.945] | 1.212 [0.629, 2.092] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.118, 0.438] | 2.077 [1.000, 3.619] | 0.760 [0.364, 1.334] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.111, 0.455] | 2.423 [1.200, 4.209] | 0.788 [0.368, 1.400] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 2.308 [1.142, 4.000] | 0.760 [0.366, 1.318] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.467] | 2.269 [1.154, 3.950] | 0.827 [0.422, 1.432] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 5.235 [3.000, 9.000] | 2.147 [1.163, 3.851] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.222 [0.500, 2.750] | 0.583 [0.200, 1.466] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 154 | 0.557 | 0.506 | 0.0578 | +0.0136 [+0.0042, +0.0233] | -0.0014 [-0.0095, +0.0063] | 0.920 | 0.513 | yes |
| 2 | 0.607 (147 of 1872 days never flag) | 102 | 0.345 | 0.471 | 0.0671 | +0.0040 [-0.0050, +0.0118] | -0.0060 [-0.0147, +0.0016] | 0.878 | 0.314 | no |
| 3 | 0.618 (147 of 1871 days never flag) | 122 | 0.428 | 0.484 | 0.0663 | +0.0044 [-0.0059, +0.0132] | -0.0019 [-0.0117, +0.0065] | 0.893 | 0.391 | no |
| 4 | 0.588 (147 of 1870 days never flag) | 120 | 0.435 | 0.500 | 0.0632 | +0.0076 [+0.0007, +0.0138] | -0.0008 [-0.0074, +0.0055] | 0.883 | 0.400 | yes |
| 5 | 0.575 (147 of 1869 days never flag) | 110 | 0.370 | 0.464 | 0.0672 | +0.0037 [-0.0026, +0.0097] | -0.0038 [-0.0098, +0.0020] | 0.814 | 0.335 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.492 (climatology 0.512, difference -0.0200 [-0.1284, +0.0824]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0430 [+0.0288, +0.0593], realised minus predicted +0.0225 [-0.0099, +0.0558]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.490 | 0.3174 | 0.2720 | +0.0113 [-0.0310, +0.0525] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0912 | 0.0159 | +0.0118 [-0.0144, +0.0351] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0011 [-0.0041, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0311 [+0.0100, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0313 [+0.0247, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0503 | 0.2439 | 0.0401 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.506 | 0.3262 | 0.2615 | +0.0100 [-0.0267, +0.0460] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1056 | 0.1133 | +0.0446 [+0.0230, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.452 | 0.0806 | 0.0630 | +0.0056 [-0.0046, +0.0156] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0331, +0.1941] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0477, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2827 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.273, 0.655] | 0.231 | 3.88 flat / 1.80 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.231 | 2.50 flat / 1.00 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.526] | 3.077 [1.667, 5.040] | 1.423 [0.724, 2.538] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 2.538 [1.286, 4.177] | 0.990 [0.538, 1.587] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.038 [0.950, 3.556] | 0.827 [0.424, 1.392] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.115 [1.043, 3.643] | 0.837 [0.446, 1.393] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.077 [1.045, 3.500] | 0.817 [0.425, 1.350] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 5.059 [2.736, 8.900] | 2.309 [1.188, 4.319] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 0.833 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (126 of 1873 days never flag) | 155 | 0.536 | 0.484 | 0.0571 | +0.0143 [+0.0049, +0.0236] | -0.0008 [-0.0089, +0.0074] | 0.920 | 0.490 | yes |
| 2 | 0.599 (147 of 1872 days never flag) | 136 | 0.504 | 0.515 | 0.0605 | +0.0106 [+0.0011, +0.0196] | +0.0006 [-0.0085, +0.0089] | 0.897 | 0.466 | yes |
| 3 | 0.593 (147 of 1871 days never flag) | 114 | 0.442 | 0.535 | 0.0617 | +0.0090 [-0.0014, +0.0185] | +0.0027 [-0.0074, +0.0121] | 0.902 | 0.411 | no |
| 4 | 0.765 (147 of 1870 days never flag) | 115 | 0.435 | 0.522 | 0.0609 | +0.0099 [+0.0024, +0.0175] | +0.0014 [-0.0063, +0.0088] | 0.868 | 0.403 | no |
| 5 | 0.69 (147 of 1869 days never flag) | 112 | 0.420 | 0.518 | 0.0671 | +0.0038 [-0.0055, +0.0123] | -0.0037 [-0.0128, +0.0044] | 0.849 | 0.389 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1658 [+0.0511, +0.2833]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0798, ΔBrier vs climatology +0.0497 [+0.0304, +0.0710], realised minus predicted -0.0023 [-0.0328, +0.0309]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.465 | 0.3139 | 0.2720 | +0.0138 [-0.0264, +0.0547] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0927 | 0.0159 | +0.0113 [-0.0177, +0.0349] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0158] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0038 [+0.0000, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0764 | 0.1165 | +0.0302 [+0.0089, +0.0569] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0018 | 0.0048 | +0.0095 [+0.0078, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0069 | 0.0000 | +0.0309 [+0.0245, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0457 | 0.2439 | 0.0276 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.484 | 0.3240 | 0.2615 | +0.0127 [-0.0222, +0.0491] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1075 | 0.1133 | +0.0411 [+0.0176, +0.0659] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.435 | 0.0799 | 0.0630 | +0.0068 [-0.0030, +0.0163] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0335, +0.1895] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0493, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2894 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.667] | 0.231 | 3.77 flat / 1.72 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.636] | 0.231 | 2.58 flat / 1.12 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 2.923 [1.518, 4.783] | 1.212 [0.600, 2.011] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 2.692 [1.417, 4.421] | 1.000 [0.538, 1.619] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.462 [0.606, 2.700] | 0.577 [0.258, 1.021] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.731 [0.828, 3.002] | 0.750 [0.385, 1.287] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 2.385 [1.237, 4.050] | 1.010 [0.545, 1.695] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.846] | 4.882 [2.714, 8.364] | 2.118 [1.158, 3.635] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 1.667 [0.764, 3.500] | 0.972 [0.406, 2.250] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 154 | 0.557 | 0.506 | 0.0578 | +0.0136 [+0.0042, +0.0229] | -0.0014 [-0.0098, +0.0062] | 0.920 | 0.513 | yes |
| 2 | 0.578 (147 of 1872 days never flag) | 136 | 0.475 | 0.485 | 0.0613 | +0.0097 [+0.0007, +0.0186] | -0.0003 [-0.0089, +0.0081] | 0.893 | 0.434 | yes |
| 3 | 0.652 (147 of 1871 days never flag) | 91 | 0.384 | 0.582 | 0.0614 | +0.0093 [-0.0014, +0.0186] | +0.0030 [-0.0074, +0.0120] | 0.900 | 0.362 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 98 | 0.384 | 0.541 | 0.0583 | +0.0125 [+0.0049, +0.0201] | +0.0041 [-0.0035, +0.0116] | 0.895 | 0.358 | yes |
| 5 | 0.528 (147 of 1869 days never flag) | 123 | 0.442 | 0.496 | 0.0610 | +0.0099 [+0.0031, +0.0164] | +0.0024 [-0.0044, +0.0091] | 0.852 | 0.406 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.718 (climatology 0.512, difference +0.2062 [+0.0596, +0.3414]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0786, ΔBrier vs climatology +0.0508 [+0.0319, +0.0721], realised minus predicted -0.0001 [-0.0311, +0.0312]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.490 | 0.3174 | 0.2720 | +0.0113 [-0.0297, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0912 | 0.0159 | +0.0118 [-0.0167, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0011 [-0.0043, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0311 [+0.0103, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0313 [+0.0246, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0503 | 0.2439 | 0.0401 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.506 | 0.3262 | 0.2615 | +0.0100 [-0.0269, +0.0462] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1056 | 0.1133 | +0.0446 [+0.0225, +0.0699] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.452 | 0.0806 | 0.0630 | +0.0056 [-0.0047, +0.0155] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0355, +0.1932] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0488, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2827 | 0.2213 |

## risk_gbm_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.333, 0.731] | 0.269 | 4.73 flat / 2.33 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.96 flat / 1.65 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.200, 0.588] | 3.308 [1.867, 5.400] | 1.519 [0.806, 2.703] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.423] | 2.885 [1.500, 4.773] | 1.250 [0.583, 2.207] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 3.769 [2.087, 6.044] | 1.577 [0.817, 2.673] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 2.500 [1.261, 4.268] | 0.856 [0.425, 1.457] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 3.115 [1.600, 5.087] | 1.308 [0.605, 2.315] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 6.588 [3.762, 10.889] | 3.118 [1.618, 5.625] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 1.222 [0.500, 3.000] | 0.833 [0.250, 2.334] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (126 of 1873 days never flag) | 164 | 0.557 | 0.476 | 0.0507 | +0.0207 [+0.0130, +0.0294] | +0.0056 [-0.0003, +0.0117] | 0.905 | 0.508 | yes |
| 2 | 0.603 (147 of 1872 days never flag) | 130 | 0.396 | 0.423 | 0.0614 | +0.0097 [+0.0043, +0.0152] | -0.0003 [-0.0057, +0.0047] | 0.852 | 0.352 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 169 | 0.514 | 0.420 | 0.0608 | +0.0099 [+0.0055, +0.0145] | +0.0035 [-0.0007, +0.0078] | 0.857 | 0.458 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 125 | 0.435 | 0.480 | 0.0608 | +0.0100 [+0.0048, +0.0151] | +0.0015 [-0.0034, +0.0064] | 0.839 | 0.397 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 140 | 0.428 | 0.421 | 0.0692 | +0.0018 [-0.0037, +0.0070] | -0.0058 [-0.0118, -0.0000] | 0.777 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.508 (climatology 0.512, difference -0.0047 [-0.1012, +0.0944]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0260, +0.0553], realised minus predicted +0.0193 [-0.0152, +0.0546]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.459 | 0.2748 | 0.2720 | +0.0425 [+0.0112, +0.0777] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1312 | 0.0159 | +0.0148 [-0.0056, +0.0328] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0038 [+0.0003, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0741 | 0.1165 | +0.0325 [+0.0094, +0.0629] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0039 | 0.0048 | +0.0095 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0541 | 0.0000 | +0.0275 [+0.0216, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0740 | 0.2439 | 0.0262 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.472 | 0.2861 | 0.2615 | +0.0402 [+0.0106, +0.0725] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1088 | 0.1133 | +0.0418 [+0.0186, +0.0685] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.422 | 0.0797 | 0.0630 | +0.0142 [+0.0067, +0.0227] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0390, +0.1911] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0478, +0.0949] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2803 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.286, 0.714] | 0.250 | 4.38 flat / 1.97 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.621] | 0.231 | 3.88 flat / 1.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.192, 0.571] | 3.231 [1.788, 5.222] | 1.356 [0.739, 2.289] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 2.923 [1.457, 4.862] | 1.260 [0.565, 2.250] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.167, 0.528] | 3.538 [1.846, 5.751] | 1.404 [0.648, 2.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 2.462 [1.194, 4.158] | 0.827 [0.395, 1.414] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 2.538 [1.233, 4.324] | 0.990 [0.454, 1.733] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.895] | 6.294 [3.600, 10.692] | 2.824 [1.472, 5.072] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 0.778 [0.250, 1.625] | 0.361 [0.100, 0.875] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 162 | 0.557 | 0.481 | 0.0512 | +0.0202 [+0.0127, +0.0282] | +0.0051 [-0.0008, +0.0110] | 0.904 | 0.509 | yes |
| 2 | 0.607 (147 of 1872 days never flag) | 128 | 0.374 | 0.406 | 0.0620 | +0.0090 [+0.0034, +0.0147] | -0.0010 [-0.0067, +0.0043] | 0.850 | 0.330 | no |
| 3 | 0.534 (147 of 1871 days never flag) | 161 | 0.500 | 0.429 | 0.0605 | +0.0102 [+0.0054, +0.0150] | +0.0038 [-0.0009, +0.0083] | 0.855 | 0.447 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 125 | 0.442 | 0.488 | 0.0605 | +0.0103 [+0.0054, +0.0151] | +0.0019 [-0.0032, +0.0068] | 0.845 | 0.405 | yes |
| 5 | 0.489 (147 of 1869 days never flag) | 119 | 0.384 | 0.445 | 0.0672 | +0.0037 [-0.0011, +0.0090] | -0.0038 [-0.0091, +0.0017] | 0.784 | 0.346 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.491 (climatology 0.512, difference -0.0213 [-0.1310, +0.0810]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0876, ΔBrier vs climatology +0.0419 [+0.0284, +0.0573], realised minus predicted +0.0228 [-0.0103, +0.0591]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.467 | 0.2794 | 0.2720 | +0.0407 [+0.0093, +0.0725] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1302 | 0.0159 | +0.0155 [-0.0048, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0013 | 0.0200 | +0.0011 [-0.0042, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0716 | 0.1165 | +0.0333 [+0.0106, +0.0610] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0034 | 0.0048 | +0.0089 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0542 | 0.0000 | +0.0276 [+0.0213, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0747 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.481 | 0.2885 | 0.2615 | +0.0382 [+0.0100, +0.0682] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1068 | 0.1133 | +0.0449 [+0.0232, +0.0695] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.427 | 0.0808 | 0.0630 | +0.0132 [+0.0059, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0320, +0.1895] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1136 | 0.1461 | +0.0711 [+0.0481, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2732 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.275, 0.667] | 0.258 | 4.46 flat / 2.22 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.235, 0.607] | 0.231 | 3.15 flat / 1.45 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.577] | 3.308 [1.903, 5.412] | 1.519 [0.806, 2.657] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 3.000 [1.559, 5.000] | 1.356 [0.656, 2.375] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.615 [1.333, 4.435] | 1.240 [0.620, 2.182] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.077 [1.000, 3.637] | 0.865 [0.452, 1.474] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.731 [1.371, 4.600] | 1.260 [0.583, 2.283] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.346, 0.834] | 6.176 [3.524, 10.584] | 3.000 [1.565, 5.584] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.750 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (126 of 1873 days never flag) | 164 | 0.557 | 0.476 | 0.0507 | +0.0207 [+0.0129, +0.0295] | +0.0056 [-0.0004, +0.0116] | 0.905 | 0.508 | yes |
| 2 | 0.599 (147 of 1872 days never flag) | 148 | 0.504 | 0.473 | 0.0547 | +0.0164 [+0.0092, +0.0237] | +0.0064 [-0.0006, +0.0133] | 0.877 | 0.459 | yes |
| 3 | 0.428 (147 of 1871 days never flag) | 131 | 0.457 | 0.481 | 0.0551 | +0.0155 [+0.0093, +0.0220] | +0.0092 [+0.0030, +0.0157] | 0.872 | 0.417 | yes |
| 4 | 0.522 (147 of 1870 days never flag) | 111 | 0.413 | 0.514 | 0.0567 | +0.0141 [+0.0080, +0.0206] | +0.0056 [-0.0009, +0.0126] | 0.848 | 0.382 | no |
| 5 | 0.655 (147 of 1869 days never flag) | 125 | 0.391 | 0.432 | 0.0631 | +0.0078 [+0.0012, +0.0140] | +0.0003 [-0.0065, +0.0070] | 0.821 | 0.350 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1665 [+0.0547, +0.2791]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0798, ΔBrier vs climatology +0.0496 [+0.0303, +0.0699], realised minus predicted -0.0067 [-0.0377, +0.0258]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.459 | 0.2748 | 0.2720 | +0.0425 [+0.0109, +0.0762] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1312 | 0.0159 | +0.0148 [-0.0050, +0.0317] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0038 [+0.0001, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0741 | 0.1165 | +0.0325 [+0.0098, +0.0625] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0039 | 0.0048 | +0.0095 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0541 | 0.0000 | +0.0275 [+0.0215, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0740 | 0.2439 | 0.0262 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.472 | 0.2861 | 0.2615 | +0.0402 [+0.0102, +0.0720] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1088 | 0.1133 | +0.0418 [+0.0172, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.422 | 0.0797 | 0.0630 | +0.0142 [+0.0068, +0.0228] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0328, +0.1876] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0931] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2803 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.278, 0.667] | 0.231 | 3.77 flat / 1.74 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.192 | 2.46 flat / 1.04 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.208, 0.576] | 3.231 [1.826, 5.131] | 1.356 [0.717, 2.233] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 2.269 [1.176, 3.688] | 0.865 [0.467, 1.398] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 1.808 [0.827, 3.200] | 0.702 [0.344, 1.229] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 1.962 [0.963, 3.455] | 0.817 [0.423, 1.391] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 2.269 [1.172, 3.923] | 0.933 [0.490, 1.586] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.833] | 5.118 [2.905, 8.617] | 2.265 [1.226, 3.924] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.222 [0.500, 2.667] | 0.750 [0.288, 1.875] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 162 | 0.557 | 0.481 | 0.0512 | +0.0202 [+0.0125, +0.0280] | +0.0051 [-0.0009, +0.0109] | 0.904 | 0.509 | yes |
| 2 | 0.526 (147 of 1872 days never flag) | 120 | 0.439 | 0.508 | 0.0556 | +0.0155 [+0.0089, +0.0228] | +0.0055 [-0.0008, +0.0123] | 0.871 | 0.405 | yes |
| 3 | 0.652 (147 of 1871 days never flag) | 106 | 0.428 | 0.557 | 0.0549 | +0.0158 [+0.0100, +0.0219] | +0.0095 [+0.0038, +0.0153] | 0.867 | 0.400 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 110 | 0.428 | 0.536 | 0.0551 | +0.0157 [+0.0095, +0.0225] | +0.0072 [+0.0007, +0.0142] | 0.863 | 0.398 | yes |
| 5 | 0.528 (147 of 1869 days never flag) | 120 | 0.442 | 0.508 | 0.0608 | +0.0101 [+0.0037, +0.0166] | +0.0026 [-0.0041, +0.0092] | 0.826 | 0.408 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.512, difference +0.2074 [+0.0613, +0.3406]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0781, ΔBrier vs climatology +0.0514 [+0.0325, +0.0715], realised minus predicted -0.0023 [-0.0322, +0.0283]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.467 | 0.2794 | 0.2720 | +0.0407 [+0.0091, +0.0712] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1302 | 0.0159 | +0.0155 [-0.0040, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0013 | 0.0200 | +0.0011 [-0.0050, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0716 | 0.1165 | +0.0333 [+0.0108, +0.0615] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0034 | 0.0048 | +0.0089 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0542 | 0.0000 | +0.0276 [+0.0213, +0.0337] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0747 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.481 | 0.2885 | 0.2615 | +0.0382 [+0.0087, +0.0667] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1068 | 0.1133 | +0.0449 [+0.0227, +0.0693] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.427 | 0.0808 | 0.0630 | +0.0132 [+0.0058, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0286, +0.1963] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1136 | 0.1461 | +0.0711 [+0.0478, +0.0962] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2732 | 0.2213 |

## risk_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.769] | 0.192 | 2.31 flat / 1.63 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.65 flat / 1.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.357, 0.727] | 1.654 [1.105, 2.550] | 1.029 [0.617, 1.728] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 0.962 [0.520, 1.637] | 0.548 [0.225, 1.060] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.154 [0.667, 1.895] | 0.712 [0.339, 1.296] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.538 [0.943, 2.481] | 1.077 [0.566, 1.904] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.385 [0.833, 2.238] | 0.894 [0.450, 1.594] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 3.889 (no interval) | 3.389 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0864 (105 of 1873 days never flag) | 88 | 0.321 | 0.511 | 0.0600 | +0.0114 [+0.0062, +0.0165] | -0.0037 [-0.0121, +0.0040] | 0.642 | 0.297 | no |
| 2 | 0.318 (147 of 1872 days never flag) | 53 | 0.201 | 0.528 | 0.0678 | +0.0032 [-0.0033, +0.0091] | -0.0068 [-0.0148, +0.0004] | 0.579 | 0.187 | no |
| 3 | 0.118 (147 of 1871 days never flag) | 58 | 0.203 | 0.483 | 0.0687 | +0.0019 [-0.0054, +0.0087] | -0.0044 [-0.0133, +0.0033] | 0.578 | 0.186 | no |
| 4 | 0.107 (147 of 1870 days never flag) | 66 | 0.188 | 0.394 | 0.0689 | +0.0019 [-0.0049, +0.0081] | -0.0065 [-0.0151, +0.0011] | 0.578 | 0.165 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 58 | 0.159 | 0.379 | 0.0693 | +0.0016 [-0.0056, +0.0080] | -0.0059 [-0.0144, +0.0015] | 0.577 | 0.139 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.588 (climatology 0.512, difference +0.0754 [-0.0491, +0.1806]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1079, ΔBrier vs climatology +0.0216 [+0.0098, +0.0329], realised minus predicted +0.0742 [+0.0405, +0.1110]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.564 | 0.1071 | 0.2720 | -0.0038 [-0.0245, +0.0163] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0283 | 0.0159 | +0.0266 [+0.0104, +0.0402] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0048 | 0.0200 | +0.0049 [+0.0006, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.706 | 0.0382 | 0.1165 | +0.0183 [+0.0033, +0.0374] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0025 | 0.0048 | +0.0094 [+0.0077, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0041 | 0.0000 | +0.0308 [+0.0245, +0.0367] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.0741 | 0.2439 | -0.0329 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.553 | 0.1072 | 0.2615 | +0.0069 [-0.0120, +0.0248] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1048 | 0.1133 | +0.0284 [+0.0008, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.515 | 0.0125 | 0.0630 | +0.0043 [-0.0009, +0.0090] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3499 | 0.2903 | +0.1030 [+0.0321, +0.1692] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1308 | 0.1461 | +0.0798 [+0.0478, +0.1161] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2023 | 0.2213 |

## risk_logistic+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.259, 0.600] | 0.265 | 4.54 flat / 2.10 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.517] | 0.231 | 3.38 flat / 1.46 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.419] | 2.154 [1.280, 3.353] | 0.923 [0.523, 1.464] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.500 [0.896, 2.375] | 0.654 [0.359, 1.125] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.192 [0.704, 1.938] | 0.577 [0.293, 1.062] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.269 [0.731, 2.067] | 0.587 [0.295, 1.073] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.731 [1.629, 4.274] | 1.135 [0.661, 1.826] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.312, 0.750] | 3.824 [2.125, 6.333] | 1.368 [0.750, 2.250] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.889 (no interval) | 3.472 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 127 | 0.507 | 0.559 | 0.0501 | +0.0213 [+0.0138, +0.0290] | +0.0062 [+0.0006, +0.0117] | 0.879 | 0.475 | yes |
| 2 | 0.473 (147 of 1872 days never flag) | 77 | 0.273 | 0.494 | 0.0593 | +0.0118 [+0.0060, +0.0178] | +0.0018 [-0.0029, +0.0064] | 0.841 | 0.251 | yes |
| 3 | 0.382 (147 of 1871 days never flag) | 66 | 0.254 | 0.530 | 0.0626 | +0.0080 [+0.0014, +0.0146] | +0.0017 [-0.0046, +0.0076] | 0.812 | 0.236 | yes |
| 4 | 0.498 (147 of 1870 days never flag) | 67 | 0.246 | 0.507 | 0.0614 | +0.0094 [+0.0033, +0.0152] | +0.0009 [-0.0048, +0.0065] | 0.820 | 0.227 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 133 | 0.449 | 0.466 | 0.0627 | +0.0083 [+0.0031, +0.0136] | +0.0007 [-0.0039, +0.0051] | 0.797 | 0.408 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.621 (climatology 0.512, difference +0.1086 [+0.0223, +0.1877]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0406 [+0.0244, +0.0581], realised minus predicted -0.0058 [-0.0354, +0.0263]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.630 | 0.2485 | 0.2720 | +0.0519 [+0.0244, +0.0802] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1310 | 0.0159 | +0.0103 [-0.0136, +0.0275] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0188 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0349 | 0.0200 | +0.0019 [-0.0051, +0.0080] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.500 | 0.1145 | 0.1165 | +0.0303 [+0.0036, +0.0614] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0241 | 0.0048 | +0.0078 [+0.0056, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0674 | 0.0000 | +0.0244 [+0.0187, +0.0299] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1946 | 0.2439 | 0.0094 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.595 | 0.2576 | 0.2615 | +0.0497 [+0.0238, +0.0757] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1142 | 0.1133 | +0.0335 [+0.0050, +0.0634] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.534 | 0.0859 | 0.0630 | +0.0153 [+0.0084, +0.0225] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0288, +0.1764] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0482, +0.1158] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3403 | 0.2213 |

## risk_logistic+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.720] | 0.269 | 5.12 flat / 2.35 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.219, 0.548] | 0.231 | 3.73 flat / 1.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 2.231 [1.448, 3.263] | 1.038 [0.652, 1.609] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.385] | 1.462 [0.844, 2.305] | 0.635 [0.348, 1.073] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 1.615 [0.898, 2.652] | 0.702 [0.375, 1.216] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.231 [0.684, 2.000] | 0.577 [0.284, 1.038] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.478] | 3.038 [1.792, 4.750] | 1.250 [0.740, 1.983] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.481, 0.920] | 4.765 [2.849, 7.502] | 1.765 [1.062, 2.834] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.778 (no interval) | 3.444 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (105 of 1873 days never flag) | 120 | 0.443 | 0.517 | 0.0519 | +0.0195 [+0.0127, +0.0271] | +0.0044 [-0.0011, +0.0101] | 0.802 | 0.409 | no |
| 2 | 0.473 (147 of 1872 days never flag) | 75 | 0.266 | 0.493 | 0.0615 | +0.0095 [+0.0036, +0.0156] | -0.0005 [-0.0054, +0.0045] | 0.752 | 0.244 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 83 | 0.297 | 0.494 | 0.0627 | +0.0080 [+0.0011, +0.0146] | +0.0017 [-0.0047, +0.0079] | 0.746 | 0.273 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 66 | 0.246 | 0.515 | 0.0623 | +0.0085 [+0.0028, +0.0143] | +0.0001 [-0.0054, +0.0056] | 0.758 | 0.228 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 142 | 0.457 | 0.444 | 0.0633 | +0.0076 [+0.0020, +0.0131] | +0.0001 [-0.0049, +0.0048] | 0.743 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0979 [-0.0161, +0.1873]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0913, ΔBrier vs climatology +0.0382 [+0.0211, +0.0539], realised minus predicted +0.0444 [+0.0151, +0.0726]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.570 | 0.1788 | 0.2720 | +0.0363 [+0.0110, +0.0633] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0359 | 0.0159 | +0.0193 [-0.0051, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0173 | 0.0200 | +0.0020 [-0.0056, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.500 | 0.0894 | 0.1165 | +0.0294 [+0.0050, +0.0613] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0102 | 0.0048 | +0.0081 [+0.0057, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0053 | 0.0000 | +0.0307 [+0.0244, +0.0370] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1636 | 0.2439 | 0.0072 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.550 | 0.1811 | 0.2615 | +0.0381 [+0.0154, +0.0633] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1087 | 0.1133 | +0.0340 [+0.0044, +0.0651] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.474 | 0.0417 | 0.0630 | +0.0131 [+0.0069, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0283, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0501, +0.1180] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3843 | 0.2213 |

## risk_logistic+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.708] | 0.269 | 4.77 flat / 2.02 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 3.23 flat / 1.22 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.038 [1.241, 3.095] | 0.913 [0.568, 1.440] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.133, 0.409] | 1.808 [1.125, 2.864] | 0.760 [0.420, 1.320] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.094, 0.375] | 1.269 [0.643, 2.222] | 0.577 [0.260, 1.080] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.364] | 1.769 [0.895, 3.105] | 0.740 [0.347, 1.354] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.080, 0.313] | 2.000 [1.161, 3.214] | 0.750 [0.400, 1.292] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.917] | 5.294 [3.333, 8.385] | 1.765 [1.107, 2.789] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 3.778 [1.941, 8.337] | 2.500 [1.192, 6.051] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (126 of 1873 days never flag) | 116 | 0.450 | 0.543 | 0.0502 | +0.0212 [+0.0143, +0.0282] | +0.0062 [+0.0011, +0.0115] | 0.876 | 0.419 | yes |
| 2 | 0.318 (147 of 1872 days never flag) | 94 | 0.338 | 0.500 | 0.0583 | +0.0128 [+0.0078, +0.0180] | +0.0028 [-0.0021, +0.0078] | 0.830 | 0.311 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 72 | 0.283 | 0.542 | 0.0611 | +0.0096 [+0.0028, +0.0157] | +0.0032 [-0.0034, +0.0097] | 0.805 | 0.264 | yes |
| 4 | 0.498 (147 of 1870 days never flag) | 85 | 0.283 | 0.459 | 0.0602 | +0.0106 [+0.0058, +0.0156] | +0.0021 [-0.0031, +0.0077] | 0.812 | 0.256 | no |
| 5 | 0.388 (147 of 1869 days never flag) | 111 | 0.428 | 0.532 | 0.0610 | +0.0100 [+0.0053, +0.0142] | +0.0024 [-0.0023, +0.0069] | 0.792 | 0.397 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1023 [+0.0175, +0.1786]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0899, ΔBrier vs climatology +0.0395 [+0.0240, +0.0564], realised minus predicted +0.0037 [-0.0282, +0.0364]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.575 | 0.2314 | 0.2720 | +0.0463 [+0.0212, +0.0731] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1169 | 0.0159 | +0.0160 [-0.0038, +0.0306] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0133 [+0.0115, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0263 | 0.0200 | +0.0041 [-0.0004, +0.0087] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.579 | 0.0994 | 0.1165 | +0.0299 [+0.0064, +0.0589] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0192 | 0.0048 | +0.0088 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0583 | 0.0000 | +0.0256 [+0.0200, +0.0310] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1671 | 0.2439 | 0.0068 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.565 | 0.2389 | 0.2615 | +0.0467 [+0.0235, +0.0698] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1128 | 0.1133 | +0.0326 [+0.0030, +0.0610] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.507 | 0.0748 | 0.0630 | +0.0153 [+0.0092, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0303, +0.1713] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0477, +0.1164] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2506 | 0.2213 |

## risk_logistic+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.259, 0.600] | 0.231 | 4.19 flat / 1.89 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.515] | 0.231 | 3.04 flat / 1.27 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 2.077 [1.250, 3.261] | 0.904 [0.530, 1.455] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.577 [0.920, 2.522] | 0.663 [0.363, 1.147] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.077 [0.625, 1.750] | 0.529 [0.250, 0.982] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.316] | 1.154 [0.619, 1.913] | 0.538 [0.258, 0.987] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.128, 0.429] | 2.615 [1.500, 4.200] | 1.038 [0.586, 1.681] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.300, 0.786] | 3.824 [2.125, 6.502] | 1.368 [0.731, 2.341] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.889 (no interval) | 2.889 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 125 | 0.507 | 0.568 | 0.0492 | +0.0222 [+0.0147, +0.0304] | +0.0071 [+0.0017, +0.0130] | 0.907 | 0.476 | yes |
| 2 | 0.473 (147 of 1872 days never flag) | 83 | 0.302 | 0.506 | 0.0584 | +0.0127 [+0.0069, +0.0183] | +0.0027 [-0.0018, +0.0076] | 0.882 | 0.278 | yes |
| 3 | 0.382 (147 of 1871 days never flag) | 63 | 0.254 | 0.556 | 0.0607 | +0.0100 [+0.0036, +0.0165] | +0.0036 [-0.0028, +0.0098] | 0.866 | 0.237 | yes |
| 4 | 0.498 (147 of 1870 days never flag) | 64 | 0.246 | 0.531 | 0.0600 | +0.0109 [+0.0051, +0.0166] | +0.0024 [-0.0033, +0.0078] | 0.863 | 0.229 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 130 | 0.449 | 0.477 | 0.0615 | +0.0094 [+0.0043, +0.0144] | +0.0019 [-0.0028, +0.0063] | 0.851 | 0.410 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.621 (climatology 0.512, difference +0.1086 [+0.0217, +0.1862]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0872, ΔBrier vs climatology +0.0423 [+0.0261, +0.0597], realised minus predicted +0.0203 [-0.0110, +0.0514]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.630 | 0.2485 | 0.2720 | +0.0519 [+0.0251, +0.0810] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1307 | 0.0159 | +0.0103 [-0.0121, +0.0280] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0049 | 0.0200 | +0.0049 [+0.0006, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0979 | 0.1165 | +0.0327 [+0.0063, +0.0644] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0025 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0674 | 0.0000 | +0.0244 [+0.0188, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1946 | 0.2439 | 0.0094 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.595 | 0.2576 | 0.2615 | +0.0497 [+0.0238, +0.0758] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1121 | 0.1133 | +0.0336 [+0.0051, +0.0659] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.547 | 0.0721 | 0.0630 | +0.0164 [+0.0097, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0305, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0490, +0.1171] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3403 | 0.2213 |

## risk_logistic+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.708] | 0.231 | 4.08 flat / 1.94 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.195, 0.500] | 0.192 | 2.42 flat / 1.09 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.294, 0.640] | 2.538 [1.666, 3.740] | 1.115 [0.717, 1.730] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.381] | 1.038 [0.581, 1.737] | 0.510 [0.227, 0.978] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.808 [0.429, 1.364] | 0.442 [0.184, 0.875] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 0.577 [0.250, 1.046] | 0.346 [0.108, 0.740] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.379] | 2.231 [1.258, 3.650] | 0.942 [0.510, 1.583] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 4.059 [2.440, 6.571] | 1.485 [0.898, 2.426] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.111 [2.076, 9.168] | 2.806 [1.317, 6.752] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (126 of 1873 days never flag) | 131 | 0.464 | 0.496 | 0.0506 | +0.0208 [+0.0154, +0.0264] | +0.0057 [+0.0003, +0.0110] | 0.887 | 0.426 | no |
| 2 | 0.318 (147 of 1872 days never flag) | 53 | 0.187 | 0.491 | 0.0595 | +0.0115 [+0.0070, +0.0161] | +0.0015 [-0.0033, +0.0064] | 0.843 | 0.171 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 48 | 0.196 | 0.562 | 0.0618 | +0.0088 [+0.0032, +0.0145] | +0.0025 [-0.0036, +0.0084] | 0.814 | 0.184 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 34 | 0.138 | 0.559 | 0.0613 | +0.0096 [+0.0052, +0.0138] | +0.0011 [-0.0040, +0.0063] | 0.827 | 0.129 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 95 | 0.268 | 0.389 | 0.0621 | +0.0088 [+0.0045, +0.0129] | +0.0013 [-0.0039, +0.0059] | 0.808 | 0.235 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.512, difference +0.1011 [+0.0140, +0.1706]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0938, ΔBrier vs climatology +0.0356 [+0.0224, +0.0489], realised minus predicted +0.0355 [+0.0035, +0.0702]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.505 | 0.1778 | 0.2720 | +0.0375 [+0.0206, +0.0547] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0797 | 0.0159 | +0.0235 [+0.0056, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0095 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0198 | 0.0200 | +0.0043 [-0.0005, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0763 | 0.1165 | +0.0309 [+0.0077, +0.0603] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0133 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0358 | 0.0000 | +0.0292 [+0.0230, +0.0351] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1344 | 0.2439 | -0.0033 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.504 | 0.508 | 0.1824 | 0.2615 | +0.0429 [+0.0260, +0.0610] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1095 | 0.1133 | +0.0313 [+0.0035, +0.0611] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.442 | 0.0492 | 0.0630 | +0.0149 [+0.0107, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0272, +0.1714] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0487, +0.1176] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2194 | 0.2213 |

## risk_logistic+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.594] | 0.231 | 3.35 flat / 1.40 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.560] | 0.231 | 2.65 flat / 1.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.037, 0.292] | 1.500 [0.667, 2.591] | 0.587 [0.258, 1.022] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.308 [0.543, 2.440] | 0.529 [0.215, 0.971] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.269 [0.571, 2.286] | 0.615 [0.243, 1.147] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.577 [0.697, 2.700] | 0.654 [0.280, 1.163] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 2.385 [1.200, 4.000] | 0.913 [0.469, 1.544] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.750] | 4.176 [2.166, 7.078] | 1.441 [0.729, 2.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.778 [0.438, 4.429] | 1.333 [0.281, 3.537] |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 101 | 0.443 | 0.614 | 0.0629 | +0.0085 [-0.0016, +0.0187] | -0.0066 [-0.0158, +0.0021] | 0.870 | 0.420 | yes |
| 2 | 0.676 (147 of 1872 days never flag) | 67 | 0.237 | 0.493 | 0.0708 | +0.0002 [-0.0096, +0.0091] | -0.0098 [-0.0193, -0.0015] | 0.824 | 0.218 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 65 | 0.232 | 0.492 | 0.0746 | -0.0040 [-0.0143, +0.0057] | -0.0103 [-0.0203, -0.0008] | 0.796 | 0.213 | no |
| 4 | 0.703 (147 of 1870 days never flag) | 78 | 0.268 | 0.474 | 0.0723 | -0.0014 [-0.0102, +0.0064] | -0.0099 [-0.0188, -0.0018] | 0.814 | 0.244 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 127 | 0.471 | 0.512 | 0.0725 | -0.0016 [-0.0088, +0.0052] | -0.0091 [-0.0161, -0.0022] | 0.779 | 0.435 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.598 (climatology 0.512, difference +0.0860 [+0.0076, +0.1469]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0339 [+0.0168, +0.0518], realised minus predicted -0.0138 [-0.0478, +0.0233]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.618 | 0.3229 | 0.2720 | +0.0077 [-0.0373, +0.0503] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2056 | 0.0159 | -0.0171 [-0.0410, +0.0042] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0017, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0680 | 0.1165 | +0.0296 [+0.0061, +0.0580] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0089 | 0.0048 | +0.0084 [+0.0065, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1119 | 0.0000 | +0.0111 [+0.0059, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1510 | 0.2439 | -0.0018 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.622 | 0.3208 | 0.2615 | +0.0078 [-0.0312, +0.0454] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1156 | 0.1133 | +0.0309 [+0.0033, +0.0610] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.575 | 0.1023 | 0.0630 | +0.0006 [-0.0096, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0319, +0.1731] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0493, +0.1168] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2902 | 0.2213 |

## risk_logistic+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.714] | 0.231 | 3.77 flat / 1.58 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.226, 0.560] | 0.231 | 2.81 flat / 1.13 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.147, 0.471] | 2.385 [1.200, 3.867] | 0.952 [0.500, 1.538] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.423 [0.571, 2.608] | 0.471 [0.181, 0.891] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.290] | 1.231 [0.514, 2.185] | 0.500 [0.213, 0.896] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.318] | 1.500 [0.632, 2.636] | 0.577 [0.242, 1.057] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.308 [1.188, 3.934] | 0.933 [0.481, 1.600] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.929] | 4.765 [2.786, 7.700] | 1.691 [0.999, 2.727] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.889 (no interval) | 1.361 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 133 | 0.507 | 0.534 | 0.0629 | +0.0085 [-0.0018, +0.0187] | -0.0065 [-0.0156, +0.0020] | 0.870 | 0.471 | no |
| 2 | 0.604 (147 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0694 | +0.0016 [-0.0078, +0.0100] | -0.0084 [-0.0166, -0.0009] | 0.824 | 0.230 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 66 | 0.246 | 0.515 | 0.0725 | -0.0018 [-0.0119, +0.0071] | -0.0081 [-0.0180, +0.0004] | 0.797 | 0.228 | yes |
| 4 | 0.726 (147 of 1870 days never flag) | 75 | 0.261 | 0.480 | 0.0713 | -0.0005 [-0.0086, +0.0071] | -0.0090 [-0.0174, -0.0011] | 0.816 | 0.238 | yes |
| 5 | 0.647 (147 of 1869 days never flag) | 114 | 0.391 | 0.474 | 0.0726 | -0.0017 [-0.0092, +0.0056] | -0.0092 [-0.0170, -0.0020] | 0.785 | 0.357 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.512, difference +0.0610 [-0.0127, +0.1206]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0931, ΔBrier vs climatology +0.0364 [+0.0205, +0.0534], realised minus predicted -0.0136 [-0.0454, +0.0211]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.533 | 0.3266 | 0.2720 | +0.0083 [-0.0374, +0.0521] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2046 | 0.0159 | -0.0171 [-0.0421, +0.0044] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0014, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0659 | 0.1165 | +0.0291 [+0.0061, +0.0562] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0088 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1110 | 0.0000 | +0.0114 [+0.0061, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1496 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.538 | 0.3229 | 0.2615 | +0.0078 [-0.0318, +0.0467] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1161 | 0.1133 | +0.0317 [+0.0021, +0.0620] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.481 | 0.1027 | 0.0630 | +0.0007 [-0.0099, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0330, +0.1761] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1173] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2900 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.296, 0.625] | 0.231 | 3.15 flat / 1.31 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.289, 0.630] | 0.231 | 2.73 flat / 1.14 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.038, 0.304] | 1.500 [0.654, 2.625] | 0.587 [0.261, 1.038] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 1.231 [0.483, 2.231] | 0.500 [0.208, 0.908] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 0.808 [0.300, 1.527] | 0.375 [0.146, 0.700] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.193, 0.500] | 1.577 [0.809, 2.667] | 0.654 [0.359, 1.078] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.154 [1.083, 3.647] | 0.865 [0.464, 1.453] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.384, 0.800] | 4.235 [2.412, 7.143] | 1.529 [0.900, 2.531] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 1.111 [0.231, 2.881] | 0.889 [0.182, 2.358] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 101 | 0.443 | 0.614 | 0.0629 | +0.0085 [-0.0021, +0.0182] | -0.0066 [-0.0161, +0.0019] | 0.870 | 0.420 | no |
| 2 | 0.856 (147 of 1872 days never flag) | 70 | 0.273 | 0.543 | 0.0660 | +0.0050 [-0.0042, +0.0143] | -0.0050 [-0.0141, +0.0035] | 0.840 | 0.255 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 53 | 0.232 | 0.604 | 0.0675 | +0.0032 [-0.0072, +0.0125] | -0.0031 [-0.0130, +0.0061] | 0.827 | 0.220 | yes |
| 4 | 0.721 (126 of 1870 days never flag) | 81 | 0.290 | 0.494 | 0.0656 | +0.0052 [-0.0027, +0.0129] | -0.0032 [-0.0110, +0.0044] | 0.841 | 0.266 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 112 | 0.406 | 0.500 | 0.0651 | +0.0058 [-0.0015, +0.0125] | -0.0018 [-0.0085, +0.0051] | 0.827 | 0.373 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.512, difference +0.1793 [+0.0513, +0.2797]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0809, ΔBrier vs climatology +0.0485 [+0.0303, +0.0678], realised minus predicted -0.0312 [-0.0603, -0.0031]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.618 | 0.3229 | 0.2720 | +0.0077 [-0.0387, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2056 | 0.0159 | -0.0171 [-0.0424, +0.0041] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0019, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0680 | 0.1165 | +0.0296 [+0.0061, +0.0595] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0089 | 0.0048 | +0.0084 [+0.0066, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1119 | 0.0000 | +0.0111 [+0.0056, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1510 | 0.2439 | -0.0018 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.622 | 0.3208 | 0.2615 | +0.0078 [-0.0320, +0.0450] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1156 | 0.1133 | +0.0309 [+0.0025, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.575 | 0.1023 | 0.0630 | +0.0006 [-0.0105, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0291, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0483, +0.1183] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2902 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.731] | 0.231 | 3.46 flat / 1.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.625] | 0.192 | 2.38 flat / 0.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.478] | 2.385 [1.285, 3.810] | 0.952 [0.518, 1.511] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.269 [0.515, 2.251] | 0.471 [0.214, 0.821] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 0.808 [0.294, 1.563] | 0.375 [0.144, 0.697] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.385 [0.600, 2.444] | 0.500 [0.216, 0.880] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 1.769 [0.833, 3.048] | 0.712 [0.353, 1.211] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.706 [2.700, 7.385] | 1.676 [0.987, 2.615] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.626] | 1.111 [0.200, 3.000] | 0.806 [0.115, 2.286] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 133 | 0.507 | 0.534 | 0.0629 | +0.0085 [-0.0012, +0.0190] | -0.0065 [-0.0154, +0.0022] | 0.870 | 0.471 | no |
| 2 | 0.866 (147 of 1872 days never flag) | 77 | 0.317 | 0.571 | 0.0661 | +0.0050 [-0.0047, +0.0140] | -0.0050 [-0.0144, +0.0039] | 0.843 | 0.298 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 54 | 0.239 | 0.611 | 0.0671 | +0.0036 [-0.0065, +0.0126] | -0.0027 [-0.0124, +0.0062] | 0.829 | 0.227 | yes |
| 4 | 0.8 (126 of 1870 days never flag) | 79 | 0.312 | 0.544 | 0.0651 | +0.0057 [-0.0027, +0.0138] | -0.0027 [-0.0112, +0.0052] | 0.842 | 0.291 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 99 | 0.384 | 0.535 | 0.0651 | +0.0058 [-0.0017, +0.0130] | -0.0017 [-0.0085, +0.0054] | 0.828 | 0.357 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1874 [+0.0633, +0.2930]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0799, ΔBrier vs climatology +0.0495 [+0.0307, +0.0693], realised minus predicted -0.0310 [-0.0595, -0.0007]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.533 | 0.3266 | 0.2720 | +0.0083 [-0.0344, +0.0524] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2046 | 0.0159 | -0.0171 [-0.0419, +0.0042] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0017, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0659 | 0.1165 | +0.0291 [+0.0060, +0.0568] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0088 | 0.0048 | +0.0085 [+0.0065, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1110 | 0.0000 | +0.0114 [+0.0057, +0.0172] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1496 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.538 | 0.3229 | 0.2615 | +0.0078 [-0.0292, +0.0471] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1161 | 0.1133 | +0.0317 [+0.0025, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.481 | 0.1027 | 0.0630 | +0.0007 [-0.0092, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0318, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0436, +0.1153] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2900 | 0.2213 |

## risk_logistic+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.607] | 0.269 | 4.65 flat / 2.14 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.556] | 0.231 | 3.81 flat / 1.73 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.885 [0.974, 3.091] | 0.750 [0.402, 1.243] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.103, 0.375] | 1.846 [0.970, 3.053] | 0.808 [0.420, 1.375] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.462 [0.720, 2.478] | 0.654 [0.299, 1.163] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.367] | 1.269 [0.619, 2.258] | 0.606 [0.274, 1.119] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.471] | 3.231 [1.778, 5.348] | 1.481 [0.757, 2.620] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.762] | 5.353 [2.998, 9.154] | 2.162 [1.088, 4.002] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.333 [1.571, 7.200] | 2.111 [0.937, 4.877] |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (147 of 1873 days never flag) | 122 | 0.521 | 0.598 | 0.0584 | +0.0130 [+0.0051, +0.0217] | -0.0021 [-0.0088, +0.0048] | 0.841 | 0.493 | yes |
| 2 | 0.546 (147 of 1872 days never flag) | 81 | 0.237 | 0.407 | 0.0690 | +0.0021 [-0.0044, +0.0086] | -0.0079 [-0.0143, -0.0014] | 0.781 | 0.210 | no |
| 3 | 0.643 (147 of 1871 days never flag) | 74 | 0.261 | 0.486 | 0.0720 | -0.0013 [-0.0080, +0.0054] | -0.0076 [-0.0149, -0.0007] | 0.730 | 0.239 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 63 | 0.217 | 0.476 | 0.0712 | -0.0004 [-0.0069, +0.0060] | -0.0089 [-0.0159, -0.0019] | 0.752 | 0.198 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 148 | 0.464 | 0.432 | 0.0725 | -0.0016 [-0.0080, +0.0046] | -0.0091 [-0.0160, -0.0027] | 0.722 | 0.415 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.598 (climatology 0.512, difference +0.0854 [+0.0048, +0.1499]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0986, ΔBrier vs climatology +0.0309 [+0.0154, +0.0483], realised minus predicted -0.0308 [-0.0641, +0.0072]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.614 | 0.2940 | 0.2720 | +0.0337 [+0.0011, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2137 | 0.0159 | -0.0150 [-0.0358, +0.0017] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0089, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0137 | 0.0200 | +0.0038 [-0.0017, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0667 | 0.1165 | +0.0275 [+0.0065, +0.0547] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0222 | 0.0048 | +0.0080 [+0.0063, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1315 | 0.0000 | +0.0053 [+0.0006, +0.0107] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1281 | 0.2439 | -0.0229 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.607 | 0.2953 | 0.2615 | +0.0321 [+0.0027, +0.0631] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1163 | 0.1133 | +0.0301 [+0.0016, +0.0583] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.568 | 0.1065 | 0.0630 | +0.0060 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3499 | 0.2903 | +0.1030 [+0.0303, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1308 | 0.1461 | +0.0798 [+0.0478, +0.1178] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2859 | 0.2213 |

## risk_logistic+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.720] | 0.269 | 5.00 flat / 2.29 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 3.92 flat / 1.81 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.269, 0.588] | 2.923 [1.756, 4.588] | 1.154 [0.710, 1.786] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.654 [0.833, 2.762] | 0.644 [0.312, 1.100] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.048, 0.273] | 1.038 [0.478, 1.880] | 0.433 [0.194, 0.783] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.320] | 1.231 [0.591, 2.209] | 0.558 [0.258, 1.033] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.469] | 3.154 [1.656, 5.269] | 1.490 [0.733, 2.636] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.485, 0.923] | 5.882 [3.500, 9.462] | 2.397 [1.303, 4.162] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 3.333 [1.727, 7.405] | 2.083 [0.967, 5.083] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (126 of 1873 days never flag) | 158 | 0.586 | 0.519 | 0.0583 | +0.0131 [+0.0052, +0.0217] | -0.0020 [-0.0088, +0.0051] | 0.841 | 0.542 | yes |
| 2 | 0.489 (147 of 1872 days never flag) | 76 | 0.237 | 0.434 | 0.0676 | +0.0035 [-0.0029, +0.0096] | -0.0065 [-0.0125, -0.0006] | 0.781 | 0.213 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 59 | 0.232 | 0.542 | 0.0698 | +0.0008 [-0.0050, +0.0067] | -0.0055 [-0.0112, +0.0005] | 0.731 | 0.216 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 62 | 0.217 | 0.484 | 0.0703 | +0.0005 [-0.0057, +0.0069] | -0.0079 [-0.0145, -0.0010] | 0.754 | 0.199 | yes |
| 5 | 0.498 (147 of 1869 days never flag) | 136 | 0.391 | 0.397 | 0.0726 | -0.0017 [-0.0087, +0.0049] | -0.0092 [-0.0167, -0.0022] | 0.728 | 0.344 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.512, difference +0.0604 [-0.0172, +0.1240]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0961, ΔBrier vs climatology +0.0334 [+0.0182, +0.0498], realised minus predicted -0.0307 [-0.0645, +0.0052]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.518 | 0.2976 | 0.2720 | +0.0343 [+0.0014, +0.0700] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2127 | 0.0159 | -0.0150 [-0.0373, +0.0023] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0136 | 0.0200 | +0.0039 [-0.0016, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0646 | 0.1165 | +0.0269 [+0.0062, +0.0515] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0221 | 0.0048 | +0.0081 [+0.0062, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1305 | 0.0000 | +0.0056 [+0.0006, +0.0112] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1268 | 0.2439 | -0.0244 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.523 | 0.2975 | 0.2615 | +0.0321 [+0.0030, +0.0628] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1168 | 0.1133 | +0.0309 [+0.0029, +0.0603] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.467 | 0.1070 | 0.0630 | +0.0061 [-0.0015, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3465 | 0.2903 | +0.1049 [+0.0345, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1295 | 0.1461 | +0.0774 [+0.0452, +0.1168] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2858 | 0.2213 |

## risk_logistic+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.632] | 0.238 | 4.27 flat / 1.91 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.625] | 0.231 | 3.81 flat / 1.71 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 1.885 [0.969, 3.154] | 0.750 [0.402, 1.268] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 0.885 [0.312, 1.667] | 0.365 [0.134, 0.698] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 0.654 [0.333, 1.131] | 0.356 [0.167, 0.650] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.166, 0.462] | 1.500 [0.733, 2.539] | 0.606 [0.315, 1.023] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.846 [1.412, 4.774] | 1.221 [0.522, 2.195] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.800] | 5.588 [3.262, 9.003] | 2.338 [1.277, 4.050] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.778 [0.800, 4.333] | 1.111 [0.442, 2.950] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (147 of 1873 days never flag) | 122 | 0.521 | 0.598 | 0.0584 | +0.0130 [+0.0055, +0.0217] | -0.0021 [-0.0085, +0.0049] | 0.841 | 0.493 | yes |
| 2 | 0.856 (147 of 1872 days never flag) | 54 | 0.223 | 0.574 | 0.0634 | +0.0076 [+0.0008, +0.0146] | -0.0024 [-0.0093, +0.0047] | 0.804 | 0.210 | yes |
| 3 | 0.466 (147 of 1871 days never flag) | 49 | 0.232 | 0.653 | 0.0643 | +0.0064 [+0.0002, +0.0126] | +0.0001 [-0.0064, +0.0068] | 0.769 | 0.222 | yes |
| 4 | 0.721 (126 of 1870 days never flag) | 81 | 0.304 | 0.519 | 0.0642 | +0.0066 [+0.0003, +0.0128] | -0.0018 [-0.0087, +0.0049] | 0.788 | 0.282 | yes |
| 5 | 0.767 (147 of 1869 days never flag) | 132 | 0.420 | 0.439 | 0.0649 | +0.0061 [+0.0001, +0.0121] | -0.0015 [-0.0075, +0.0053] | 0.781 | 0.378 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.512, difference +0.1799 [+0.0515, +0.2860]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0827, ΔBrier vs climatology +0.0467 [+0.0275, +0.0661], realised minus predicted -0.0498 [-0.0806, -0.0194]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.614 | 0.2940 | 0.2720 | +0.0337 [+0.0025, +0.0666] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2137 | 0.0159 | -0.0150 [-0.0345, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0137 | 0.0200 | +0.0038 [-0.0016, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0667 | 0.1165 | +0.0275 [+0.0061, +0.0541] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0222 | 0.0048 | +0.0080 [+0.0062, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1315 | 0.0000 | +0.0053 [+0.0004, +0.0106] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1281 | 0.2439 | -0.0229 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.607 | 0.2953 | 0.2615 | +0.0321 [+0.0040, +0.0631] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1163 | 0.1133 | +0.0301 [+0.0021, +0.0589] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.568 | 0.1065 | 0.0630 | +0.0060 [-0.0011, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3499 | 0.2903 | +0.1030 [+0.0314, +0.1735] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1308 | 0.1461 | +0.0798 [+0.0495, +0.1160] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2859 | 0.2213 |

## risk_logistic+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.679] | 0.262 | 4.50 flat / 1.92 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.267, 0.581] | 0.231 | 3.27 flat / 1.43 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 2.923 [1.750, 4.467] | 1.154 [0.702, 1.722] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 0.923 [0.312, 1.750] | 0.337 [0.128, 0.619] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 0.654 [0.333, 1.104] | 0.327 [0.155, 0.570] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.150, 0.467] | 1.846 [0.871, 3.177] | 0.654 [0.301, 1.130] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.379] | 2.500 [1.107, 4.305] | 1.135 [0.457, 2.100] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.416, 0.867] | 6.000 [3.583, 9.600] | 2.456 [1.353, 4.206] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.667 [0.765, 3.571] | 0.917 [0.350, 2.209] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (126 of 1873 days never flag) | 158 | 0.586 | 0.519 | 0.0583 | +0.0131 [+0.0049, +0.0212] | -0.0020 [-0.0092, +0.0046] | 0.841 | 0.542 | yes |
| 2 | 0.866 (147 of 1872 days never flag) | 61 | 0.266 | 0.607 | 0.0634 | +0.0076 [+0.0007, +0.0144] | -0.0024 [-0.0093, +0.0046] | 0.807 | 0.252 | yes |
| 3 | 0.466 (147 of 1871 days never flag) | 50 | 0.239 | 0.660 | 0.0639 | +0.0068 [+0.0012, +0.0127] | +0.0005 [-0.0055, +0.0067] | 0.771 | 0.229 | yes |
| 4 | 0.807 (126 of 1870 days never flag) | 97 | 0.355 | 0.505 | 0.0637 | +0.0072 [+0.0009, +0.0135] | -0.0013 [-0.0079, +0.0054] | 0.789 | 0.327 | yes |
| 5 | 0.767 (147 of 1869 days never flag) | 118 | 0.384 | 0.449 | 0.0648 | +0.0061 [-0.0005, +0.0128] | -0.0014 [-0.0081, +0.0057] | 0.779 | 0.347 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1880 [+0.0729, +0.2941]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0817, ΔBrier vs climatology +0.0478 [+0.0289, +0.0673], realised minus predicted -0.0496 [-0.0813, -0.0187]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.518 | 0.2976 | 0.2720 | +0.0343 [+0.0003, +0.0670] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2127 | 0.0159 | -0.0150 [-0.0355, +0.0019] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0136 | 0.0200 | +0.0039 [-0.0017, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0646 | 0.1165 | +0.0269 [+0.0062, +0.0510] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0221 | 0.0048 | +0.0081 [+0.0063, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1305 | 0.0000 | +0.0056 [+0.0005, +0.0110] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1268 | 0.2439 | -0.0244 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.523 | 0.2975 | 0.2615 | +0.0321 [+0.0013, +0.0630] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1168 | 0.1133 | +0.0309 [+0.0031, +0.0602] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.467 | 0.1070 | 0.0630 | +0.0061 [-0.0015, +0.0142] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3465 | 0.2903 | +0.1049 [+0.0307, +0.1769] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1295 | 0.1461 | +0.0774 [+0.0445, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2858 | 0.2213 |

## risk_logistic+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.650] | 0.231 | 3.58 flat / 1.44 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 3.27 flat / 1.24 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.059, 0.346] | 1.462 [0.625, 2.593] | 0.606 [0.268, 1.098] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.292] | 1.500 [0.621, 2.840] | 0.577 [0.241, 1.081] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.269 [0.556, 2.348] | 0.606 [0.250, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.136, 0.412] | 1.769 [0.828, 3.188] | 0.702 [0.309, 1.263] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.478] | 2.885 [1.441, 4.953] | 1.048 [0.520, 1.800] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.833] | 4.647 [2.450, 7.858] | 1.588 [0.816, 2.717] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.556 (no interval) | 1.167 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 89 | 0.364 | 0.573 | 0.0586 | +0.0129 [+0.0034, +0.0227] | -0.0022 [-0.0107, +0.0061] | 0.915 | 0.342 | yes |
| 2 | 0.676 (147 of 1872 days never flag) | 80 | 0.295 | 0.512 | 0.0656 | +0.0055 [-0.0039, +0.0142] | -0.0045 [-0.0130, +0.0037] | 0.884 | 0.272 | no |
| 3 | 0.643 (147 of 1871 days never flag) | 65 | 0.232 | 0.492 | 0.0682 | +0.0025 [-0.0085, +0.0123] | -0.0038 [-0.0145, +0.0056] | 0.890 | 0.213 | no |
| 4 | 0.677 (147 of 1870 days never flag) | 89 | 0.312 | 0.483 | 0.0676 | +0.0032 [-0.0051, +0.0108] | -0.0052 [-0.0135, +0.0029] | 0.846 | 0.285 | no |
| 5 | 0.701 (147 of 1869 days never flag) | 145 | 0.507 | 0.483 | 0.0724 | -0.0015 [-0.0106, +0.0068] | -0.0090 [-0.0180, -0.0005] | 0.820 | 0.464 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.609 (climatology 0.512, difference +0.0964 [+0.0156, +0.1551]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0898, ΔBrier vs climatology +0.0397 [+0.0231, +0.0578], realised minus predicted +0.0039 [-0.0272, +0.0355]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.579 | 0.3238 | 0.2720 | +0.0115 [-0.0306, +0.0550] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0973 | 0.0159 | +0.0043 [-0.0257, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0056 | 0.0200 | +0.0049 [+0.0004, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0770 | 0.1165 | +0.0286 [+0.0068, +0.0559] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0035 | 0.0048 | +0.0094 [+0.0077, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0308 [+0.0245, +0.0369] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0994 | 0.2439 | -0.0110 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.581 | 0.3291 | 0.2615 | +0.0107 [-0.0264, +0.0478] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1120 | 0.1133 | +0.0315 [+0.0031, +0.0597] |
| day_type | ordinary | 1603 | 101 | 0.297 | 0.500 | 0.0794 | 0.0630 | +0.0057 [-0.0036, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0311, +0.1756] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0798 [+0.0496, +0.1176] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.231 | 3.77 flat / 1.59 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.445] | 0.231 | 2.85 flat / 1.14 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 2.231 [1.138, 3.727] | 0.875 [0.458, 1.457] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.300] | 1.462 [0.625, 2.750] | 0.510 [0.216, 0.958] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 1.231 [0.500, 2.222] | 0.471 [0.200, 0.845] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.333] | 1.385 [0.606, 2.435] | 0.567 [0.250, 1.015] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 2.308 [1.120, 3.938] | 0.981 [0.486, 1.713] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.824 [2.808, 7.842] | 1.735 [1.008, 2.850] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.778 [0.533, 4.667] | 1.306 [0.250, 3.669] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (126 of 1873 days never flag) | 120 | 0.443 | 0.517 | 0.0589 | +0.0125 [+0.0023, +0.0225] | -0.0026 [-0.0120, +0.0061] | 0.915 | 0.409 | yes |
| 2 | 0.604 (147 of 1872 days never flag) | 75 | 0.266 | 0.493 | 0.0644 | +0.0067 [-0.0022, +0.0152] | -0.0033 [-0.0116, +0.0045] | 0.886 | 0.244 | no |
| 3 | 0.71 (147 of 1871 days never flag) | 63 | 0.225 | 0.492 | 0.0660 | +0.0047 [-0.0061, +0.0143] | -0.0016 [-0.0120, +0.0076] | 0.893 | 0.206 | no |
| 4 | 0.631 (147 of 1870 days never flag) | 66 | 0.217 | 0.455 | 0.0640 | +0.0068 [-0.0005, +0.0140] | -0.0016 [-0.0091, +0.0060] | 0.880 | 0.197 | no |
| 5 | 0.535 (147 of 1869 days never flag) | 106 | 0.333 | 0.434 | 0.0669 | +0.0041 [-0.0030, +0.0107] | -0.0035 [-0.0110, +0.0035] | 0.826 | 0.299 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.576 (climatology 0.512, difference +0.0635 [-0.0138, +0.1244]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0873, ΔBrier vs climatology +0.0422 [+0.0266, +0.0599], realised minus predicted +0.0051 [-0.0246, +0.0370]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.514 | 0.3281 | 0.2720 | +0.0103 [-0.0327, +0.0542] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0970 | 0.0159 | +0.0040 [-0.0266, +0.0295] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0055 | 0.0200 | +0.0050 [+0.0006, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0750 | 0.1165 | +0.0283 [+0.0066, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0034 | 0.0048 | +0.0095 [+0.0076, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0042 | 0.0000 | +0.0311 [+0.0247, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0981 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.521 | 0.3322 | 0.2615 | +0.0092 [-0.0282, +0.0481] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1127 | 0.1133 | +0.0327 [+0.0036, +0.0638] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.444 | 0.0801 | 0.0630 | +0.0053 [-0.0047, +0.0150] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0309, +0.1746] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1295 | 0.1461 | +0.0774 [+0.0437, +0.1152] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.633] | 0.231 | 3.38 flat / 1.37 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.639] | 0.231 | 3.08 flat / 1.20 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.065, 0.350] | 1.462 [0.636, 2.584] | 0.606 [0.267, 1.058] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.250] | 1.231 [0.476, 2.211] | 0.500 [0.202, 0.881] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.105, 0.368] | 0.846 [0.292, 1.652] | 0.385 [0.136, 0.735] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.227, 0.546] | 1.846 [0.865, 3.143] | 0.721 [0.363, 1.192] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.226, 0.563] | 2.654 [1.363, 4.286] | 0.981 [0.517, 1.563] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 4.765 [2.647, 7.617] | 1.765 [1.012, 2.786] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 0.778 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 89 | 0.364 | 0.573 | 0.0586 | +0.0129 [+0.0026, +0.0226] | -0.0022 [-0.0114, +0.0061] | 0.915 | 0.342 | yes |
| 2 | 0.856 (147 of 1872 days never flag) | 72 | 0.288 | 0.556 | 0.0615 | +0.0096 [-0.0002, +0.0190] | -0.0004 [-0.0102, +0.0087] | 0.892 | 0.269 | yes |
| 3 | 0.706 (147 of 1871 days never flag) | 55 | 0.239 | 0.600 | 0.0619 | +0.0088 [-0.0020, +0.0190] | +0.0025 [-0.0079, +0.0125] | 0.900 | 0.226 | yes |
| 4 | 0.721 (126 of 1870 days never flag) | 95 | 0.341 | 0.495 | 0.0616 | +0.0093 [+0.0017, +0.0167] | +0.0008 [-0.0068, +0.0084] | 0.865 | 0.313 | yes |
| 5 | 0.767 (126 of 1869 days never flag) | 118 | 0.355 | 0.415 | 0.0657 | +0.0052 [-0.0045, +0.0139] | -0.0023 [-0.0113, +0.0060] | 0.853 | 0.315 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.512, difference +0.1793 [+0.0452, +0.2843]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0759, ΔBrier vs climatology +0.0536 [+0.0347, +0.0743], realised minus predicted -0.0120 [-0.0408, +0.0167]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.579 | 0.3238 | 0.2720 | +0.0115 [-0.0324, +0.0533] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0973 | 0.0159 | +0.0043 [-0.0261, +0.0292] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0056 | 0.0200 | +0.0049 [+0.0006, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0770 | 0.1165 | +0.0286 [+0.0067, +0.0547] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0035 | 0.0048 | +0.0094 [+0.0075, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0308 [+0.0244, +0.0368] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0994 | 0.2439 | -0.0110 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.581 | 0.3291 | 0.2615 | +0.0107 [-0.0271, +0.0484] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1120 | 0.1133 | +0.0315 [+0.0027, +0.0605] |
| day_type | ordinary | 1603 | 101 | 0.297 | 0.500 | 0.0794 | 0.0630 | +0.0057 [-0.0045, +0.0157] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0298, +0.1679] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0798 [+0.0494, +0.1163] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.231 | 3.27 flat / 1.27 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.526] | 0.192 | 2.04 flat / 0.76 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.212, 0.565] | 2.231 [1.080, 3.616] | 0.875 [0.435, 1.400] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.269 [0.531, 2.250] | 0.538 [0.227, 0.944] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.333] | 0.769 [0.222, 1.533] | 0.337 [0.103, 0.663] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 1.808 [0.818, 3.118] | 0.644 [0.292, 1.113] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.692 [0.700, 3.056] | 0.635 [0.267, 1.132] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.867] | 4.588 [2.588, 7.429] | 1.647 [0.940, 2.672] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 0.778 (no interval) | 0.556 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (126 of 1873 days never flag) | 120 | 0.443 | 0.517 | 0.0589 | +0.0125 [+0.0026, +0.0221] | -0.0026 [-0.0115, +0.0059] | 0.915 | 0.409 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 79 | 0.331 | 0.582 | 0.0616 | +0.0094 [-0.0004, +0.0186] | -0.0006 [-0.0100, +0.0083] | 0.895 | 0.312 | yes |
| 3 | 0.707 (147 of 1871 days never flag) | 53 | 0.239 | 0.623 | 0.0616 | +0.0091 [-0.0012, +0.0189] | +0.0027 [-0.0073, +0.0124] | 0.903 | 0.228 | yes |
| 4 | 0.7 (126 of 1870 days never flag) | 104 | 0.413 | 0.548 | 0.0585 | +0.0123 [+0.0046, +0.0193] | +0.0038 [-0.0043, +0.0109] | 0.892 | 0.386 | yes |
| 5 | 0.767 (147 of 1869 days never flag) | 88 | 0.319 | 0.500 | 0.0599 | +0.0110 [+0.0040, +0.0181] | +0.0035 [-0.0035, +0.0109] | 0.855 | 0.293 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1887 [+0.0745, +0.2903]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0746, ΔBrier vs climatology +0.0548 [+0.0358, +0.0748], realised minus predicted -0.0101 [-0.0386, +0.0179]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.514 | 0.3281 | 0.2720 | +0.0103 [-0.0349, +0.0517] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0970 | 0.0159 | +0.0040 [-0.0254, +0.0300] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0055 | 0.0200 | +0.0050 [+0.0006, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0750 | 0.1165 | +0.0283 [+0.0072, +0.0540] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0034 | 0.0048 | +0.0095 [+0.0077, +0.0113] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0042 | 0.0000 | +0.0311 [+0.0245, +0.0373] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0981 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.521 | 0.3322 | 0.2615 | +0.0092 [-0.0293, +0.0462] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1127 | 0.1133 | +0.0327 [+0.0042, +0.0614] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.444 | 0.0801 | 0.0630 | +0.0053 [-0.0049, +0.0149] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0341, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1141] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.285, 0.647] | 0.242 | 4.31 flat / 1.95 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.588] | 0.231 | 4.04 flat / 1.76 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.037, 0.294] | 1.731 [0.773, 3.150] | 0.683 [0.309, 1.217] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.038 [0.893, 3.619] | 1.067 [0.435, 1.929] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.062, 0.333] | 2.115 [1.030, 3.697] | 1.106 [0.472, 2.029] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.136, 0.412] | 1.615 [0.833, 2.778] | 0.692 [0.347, 1.220] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 3.808 [2.083, 6.179] | 1.644 [0.841, 2.706] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.350, 0.833] | 5.824 [3.389, 9.586] | 2.294 [1.192, 3.908] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.444 [0.375, 3.881] | 1.306 [0.333, 3.562] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 102 | 0.407 | 0.559 | 0.0521 | +0.0193 [+0.0115, +0.0276] | +0.0042 [-0.0020, +0.0105] | 0.894 | 0.381 | yes |
| 2 | 0.546 (147 of 1872 days never flag) | 88 | 0.252 | 0.398 | 0.0606 | +0.0105 [+0.0039, +0.0168] | +0.0005 [-0.0059, +0.0063] | 0.861 | 0.221 | no |
| 3 | 0.643 (147 of 1871 days never flag) | 92 | 0.268 | 0.402 | 0.0622 | +0.0085 [+0.0016, +0.0151] | +0.0022 [-0.0047, +0.0087] | 0.854 | 0.236 | no |
| 4 | 0.48 (147 of 1870 days never flag) | 84 | 0.304 | 0.500 | 0.0638 | +0.0071 [+0.0008, +0.0133] | -0.0014 [-0.0084, +0.0055] | 0.827 | 0.280 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 171 | 0.522 | 0.421 | 0.0689 | +0.0021 [-0.0044, +0.0081] | -0.0055 [-0.0126, +0.0010] | 0.783 | 0.465 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.608 (climatology 0.512, difference +0.0954 [+0.0158, +0.1584]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0921, ΔBrier vs climatology +0.0374 [+0.0204, +0.0538], realised minus predicted +0.0018 [-0.0321, +0.0378]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.2847 | 0.2720 | +0.0403 [+0.0081, +0.0735] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1359 | 0.0159 | +0.0078 [-0.0154, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0075 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0008, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0747 | 0.1165 | +0.0309 [+0.0084, +0.0595] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0056 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0524 | 0.0000 | +0.0274 [+0.0216, +0.0335] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1278 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.448 | 0.566 | 0.2911 | 0.2615 | +0.0382 [+0.0081, +0.0693] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1134 | 0.1133 | +0.0322 [+0.0053, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.493 | 0.0793 | 0.0630 | +0.0131 [+0.0055, +0.0212] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0304, +0.1708] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0479, +0.1161] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2743 | 0.2213 |

## risk_logistic+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.714] | 0.238 | 4.27 flat / 1.93 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.231 | 3.46 flat / 1.55 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.167, 0.526] | 2.615 [1.316, 4.300] | 0.981 [0.500, 1.615] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.808 [0.786, 3.250] | 0.856 [0.316, 1.672] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.037, 0.281] | 1.423 [0.469, 2.657] | 0.731 [0.203, 1.487] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 1.192 [0.518, 2.158] | 0.529 [0.226, 0.966] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.412] | 2.462 [1.250, 4.151] | 1.067 [0.534, 1.810] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.926] | 5.765 [3.294, 9.539] | 2.324 [1.207, 4.013] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 135 | 0.479 | 0.496 | 0.0524 | +0.0191 [+0.0116, +0.0273] | +0.0040 [-0.0022, +0.0107] | 0.893 | 0.439 | yes |
| 2 | 0.543 (147 of 1872 days never flag) | 80 | 0.237 | 0.412 | 0.0593 | +0.0117 [+0.0055, +0.0182] | +0.0017 [-0.0040, +0.0077] | 0.862 | 0.210 | no |
| 3 | 0.71 (147 of 1871 days never flag) | 62 | 0.181 | 0.403 | 0.0602 | +0.0104 [+0.0045, +0.0165] | +0.0041 [-0.0014, +0.0103] | 0.854 | 0.160 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 64 | 0.239 | 0.516 | 0.0613 | +0.0095 [+0.0035, +0.0158] | +0.0011 [-0.0050, +0.0078] | 0.841 | 0.221 | yes |
| 5 | 0.489 (147 of 1869 days never flag) | 111 | 0.341 | 0.423 | 0.0669 | +0.0040 [-0.0027, +0.0103] | -0.0035 [-0.0104, +0.0033] | 0.797 | 0.304 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0629 [-0.0130, +0.1259]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0887, ΔBrier vs climatology +0.0408 [+0.0262, +0.0571], realised minus predicted +0.0058 [-0.0255, +0.0403]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.492 | 0.2902 | 0.2720 | +0.0396 [+0.0091, +0.0730] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1360 | 0.0159 | +0.0076 [-0.0164, +0.0283] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0005, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0720 | 0.1165 | +0.0305 [+0.0086, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0055 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0532 | 0.0000 | +0.0274 [+0.0213, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1224 | 0.2439 | -0.0133 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.500 | 0.2945 | 0.2615 | +0.0374 [+0.0090, +0.0674] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1139 | 0.1133 | +0.0330 [+0.0037, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.434 | 0.0804 | 0.0630 | +0.0129 [+0.0059, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0345, +0.1711] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0451, +0.1169] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.632] | 0.254 | 4.42 flat / 1.91 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.633] | 0.238 | 4.31 flat / 1.83 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.038, 0.292] | 1.731 [0.722, 3.000] | 0.683 [0.292, 1.181] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.242] | 0.615 [0.105, 1.294] | 0.298 [0.062, 0.596] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 0.577 [0.194, 1.111] | 0.240 [0.093, 0.438] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.517] | 1.923 [1.000, 3.191] | 0.721 [0.394, 1.160] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.769 [2.160, 5.842] | 1.567 [0.829, 2.525] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 6.471 [4.087, 10.252] | 2.676 [1.587, 4.475] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 0.556 [0.000, 1.583] | 0.472 [0.000, 1.396] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 102 | 0.407 | 0.559 | 0.0521 | +0.0193 [+0.0113, +0.0280] | +0.0042 [-0.0020, +0.0107] | 0.894 | 0.381 | yes |
| 2 | 0.856 (147 of 1872 days never flag) | 45 | 0.209 | 0.644 | 0.0557 | +0.0154 [+0.0085, +0.0226] | +0.0054 [-0.0010, +0.0122] | 0.871 | 0.199 | yes |
| 3 | 0.706 (147 of 1871 days never flag) | 50 | 0.254 | 0.700 | 0.0554 | +0.0153 [+0.0094, +0.0217] | +0.0090 [+0.0027, +0.0157] | 0.867 | 0.245 | yes |
| 4 | 0.721 (126 of 1870 days never flag) | 105 | 0.399 | 0.524 | 0.0574 | +0.0135 [+0.0071, +0.0196] | +0.0050 [-0.0018, +0.0116] | 0.849 | 0.370 | yes |
| 5 | 0.767 (126 of 1869 days never flag) | 157 | 0.428 | 0.376 | 0.0617 | +0.0092 [+0.0022, +0.0153] | +0.0017 [-0.0053, +0.0084] | 0.830 | 0.371 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.512, difference +0.1799 [+0.0506, +0.2860]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0765, ΔBrier vs climatology +0.0529 [+0.0345, +0.0718], realised minus predicted -0.0167 [-0.0456, +0.0127]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.2847 | 0.2720 | +0.0403 [+0.0089, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1359 | 0.0159 | +0.0078 [-0.0158, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0075 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0007, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0747 | 0.1165 | +0.0309 [+0.0072, +0.0586] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0056 | 0.0048 | +0.0094 [+0.0075, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0524 | 0.0000 | +0.0274 [+0.0215, +0.0331] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1278 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.448 | 0.566 | 0.2911 | 0.2615 | +0.0382 [+0.0086, +0.0699] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1134 | 0.1133 | +0.0322 [+0.0038, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.493 | 0.0793 | 0.0630 | +0.0131 [+0.0057, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0309, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0477, +0.1165] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2743 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.323, 0.680] | 0.231 | 3.27 flat / 1.26 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.238, 0.542] | 0.192 | 2.08 flat / 0.77 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.542] | 2.615 [1.350, 4.316] | 0.981 [0.500, 1.606] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.286] | 0.692 [0.167, 1.452] | 0.279 [0.072, 0.568] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.042, 0.276] | 0.423 [0.115, 0.840] | 0.173 [0.050, 0.330] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 1.962 [0.897, 3.501] | 0.673 [0.306, 1.200] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 1.692 [0.682, 3.156] | 0.635 [0.259, 1.177] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 4.647 [2.600, 7.700] | 1.662 [0.930, 2.765] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 0.667 (no interval) | 0.500 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 135 | 0.479 | 0.496 | 0.0524 | +0.0191 [+0.0108, +0.0274] | +0.0040 [-0.0026, +0.0104] | 0.893 | 0.439 | yes |
| 2 | 0.866 (147 of 1872 days never flag) | 55 | 0.266 | 0.673 | 0.0559 | +0.0152 [+0.0081, +0.0222] | +0.0052 [-0.0017, +0.0119] | 0.874 | 0.256 | yes |
| 3 | 0.707 (147 of 1871 days never flag) | 45 | 0.246 | 0.756 | 0.0551 | +0.0155 [+0.0098, +0.0216] | +0.0092 [+0.0034, +0.0154] | 0.870 | 0.240 | yes |
| 4 | 0.807 (126 of 1870 days never flag) | 107 | 0.406 | 0.523 | 0.0554 | +0.0155 [+0.0094, +0.0217] | +0.0070 [+0.0005, +0.0136] | 0.857 | 0.376 | yes |
| 5 | 0.767 (147 of 1869 days never flag) | 88 | 0.319 | 0.500 | 0.0597 | +0.0112 [+0.0046, +0.0182] | +0.0037 [-0.0035, +0.0109] | 0.836 | 0.293 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1887 [+0.0694, +0.2888]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0743, ΔBrier vs climatology +0.0552 [+0.0364, +0.0756], realised minus predicted -0.0127 [-0.0420, +0.0168]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.492 | 0.2902 | 0.2720 | +0.0396 [+0.0073, +0.0736] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1360 | 0.0159 | +0.0076 [-0.0161, +0.0291] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0006, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0720 | 0.1165 | +0.0305 [+0.0076, +0.0585] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0055 | 0.0048 | +0.0094 [+0.0077, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0532 | 0.0000 | +0.0274 [+0.0217, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1224 | 0.2439 | -0.0133 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.500 | 0.2945 | 0.2615 | +0.0374 [+0.0068, +0.0681] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1139 | 0.1133 | +0.0330 [+0.0045, +0.0626] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.434 | 0.0804 | 0.0630 | +0.0129 [+0.0053, +0.0210] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0348, +0.1781] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1156] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.192 | 1.92 flat / 1.27 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.115 | 1.19 flat / 0.72 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.714] | 1.692 [1.114, 2.591] | 1.038 [0.618, 1.738] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.038 [0.542, 1.722] | 0.625 [0.250, 1.198] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.077 [0.555, 1.792] | 0.663 [0.262, 1.295] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.115 [0.583, 1.857] | 0.702 [0.293, 1.361] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.154 [0.625, 1.900] | 0.683 [0.279, 1.326] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 2.778 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.144 (105 of 1873 days never flag) | 90 | 0.329 | 0.511 | 0.0590 | +0.0124 [+0.0075, +0.0171] | -0.0027 [-0.0108, +0.0045] | 0.643 | 0.303 | no |
| 2 | 0.326 (147 of 1872 days never flag) | 51 | 0.173 | 0.471 | 0.0671 | +0.0040 [-0.0025, +0.0100] | -0.0060 [-0.0144, +0.0010] | 0.579 | 0.157 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 55 | 0.196 | 0.491 | 0.0688 | +0.0019 [-0.0060, +0.0083] | -0.0045 [-0.0132, +0.0027] | 0.579 | 0.179 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0694 | +0.0014 [-0.0053, +0.0078] | -0.0070 [-0.0150, +0.0007] | 0.578 | 0.179 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 58 | 0.203 | 0.483 | 0.0695 | +0.0015 [-0.0054, +0.0077] | -0.0061 [-0.0143, +0.0012] | 0.577 | 0.186 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.512, difference +0.0835 [-0.0393, +0.1951]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1070, ΔBrier vs climatology +0.0225 [+0.0109, +0.0339], realised minus predicted +0.0762 [+0.0414, +0.1136]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1064 | 0.2720 | -0.0032 [-0.0226, +0.0153] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0254 | 0.0159 | +0.0308 [+0.0204, +0.0398] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0036 [+0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.722 | 0.0369 | 0.1165 | +0.0218 [+0.0063, +0.0409] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0011 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0055 | 0.0000 | +0.0304 [+0.0241, +0.0362] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.0450 | 0.2439 | -0.0046 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.551 | 0.1075 | 0.2615 | +0.0084 [-0.0095, +0.0265] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1021 | 0.1133 | +0.0357 [+0.0082, +0.0629] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.529 | 0.0120 | 0.0630 | +0.0051 [+0.0001, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3212 | 0.2903 | +0.0996 [+0.0457, +0.1509] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1308 | 0.1461 | +0.0731 [+0.0406, +0.1119] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

## risk_logistic_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.219, 0.559] | 0.231 | 4.12 flat / 1.80 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.500] | 0.231 | 3.54 flat / 1.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 1.115 [0.600, 1.792] | 0.452 [0.217, 0.774] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.077, 0.321] | 1.231 [0.687, 1.962] | 0.442 [0.233, 0.721] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.577 [0.880, 2.593] | 0.663 [0.338, 1.167] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 1.500 [0.900, 2.421] | 0.702 [0.368, 1.232] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.423 [1.393, 3.895] | 1.058 [0.589, 1.771] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.235, 0.706] | 3.235 [1.571, 5.688] | 1.088 [0.523, 1.900] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.778 (no interval) | 3.139 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 75 | 0.329 | 0.613 | 0.0491 | +0.0223 [+0.0148, +0.0305] | +0.0072 [+0.0025, +0.0126] | 0.888 | 0.312 | yes |
| 2 | 0.579 (147 of 1872 days never flag) | 67 | 0.252 | 0.522 | 0.0585 | +0.0125 [+0.0074, +0.0184] | +0.0025 [-0.0014, +0.0072] | 0.842 | 0.233 | yes |
| 3 | 0.373 (147 of 1871 days never flag) | 77 | 0.261 | 0.468 | 0.0627 | +0.0080 [+0.0016, +0.0143] | +0.0017 [-0.0046, +0.0077] | 0.812 | 0.237 | yes |
| 4 | 0.361 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0619 | +0.0089 [+0.0027, +0.0153] | +0.0004 [-0.0056, +0.0065] | 0.821 | 0.217 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 108 | 0.326 | 0.417 | 0.0628 | +0.0081 [+0.0027, +0.0132] | +0.0006 [-0.0044, +0.0055] | 0.799 | 0.290 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0100, +0.1941]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0409 [+0.0244, +0.0588], realised minus predicted -0.0037 [-0.0341, +0.0293]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.727 | 0.2477 | 0.2720 | +0.0525 [+0.0247, +0.0816] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1281 | 0.0159 | +0.0146 [-0.0007, +0.0280] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0321 | 0.0200 | +0.0006 [-0.0058, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.619 | 0.1132 | 0.1165 | +0.0338 [+0.0068, +0.0687] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0227 | 0.0048 | +0.0079 [+0.0057, +0.0100] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0688 | 0.0000 | +0.0240 [+0.0184, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1655 | 0.2439 | 0.0378 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.632 | 0.2580 | 0.2615 | +0.0513 [+0.0245, +0.0801] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1114 | 0.1133 | +0.0408 [+0.0128, +0.0719] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.553 | 0.0854 | 0.0630 | +0.0162 [+0.0093, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3212 | 0.2903 | +0.0996 [+0.0482, +0.1478] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1308 | 0.1461 | +0.0731 [+0.0408, +0.1102] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3416 | 0.2213 |

## risk_logistic_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.677] | 0.269 | 4.81 flat / 2.09 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.211, 0.567] | 0.231 | 3.69 flat / 1.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.174, 0.462] | 1.462 [0.886, 2.250] | 0.635 [0.371, 1.019] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.324] | 1.231 [0.692, 2.048] | 0.442 [0.239, 0.768] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 1.577 [0.833, 2.727] | 0.663 [0.324, 1.230] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.500 [0.875, 2.501] | 0.702 [0.371, 1.286] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.526] | 3.000 [1.774, 4.844] | 1.260 [0.750, 2.105] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.440, 0.882] | 4.353 [2.611, 7.000] | 1.588 [0.963, 2.575] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.667 (no interval) | 3.028 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.314 (105 of 1873 days never flag) | 82 | 0.314 | 0.537 | 0.0510 | +0.0205 [+0.0136, +0.0279] | +0.0054 [+0.0010, +0.0100] | 0.805 | 0.292 | no |
| 2 | 0.579 (147 of 1872 days never flag) | 66 | 0.245 | 0.515 | 0.0608 | +0.0103 [+0.0048, +0.0162] | +0.0003 [-0.0044, +0.0051] | 0.752 | 0.226 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 77 | 0.261 | 0.468 | 0.0627 | +0.0079 [+0.0013, +0.0145] | +0.0016 [-0.0047, +0.0078] | 0.747 | 0.237 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0628 | +0.0080 [+0.0018, +0.0143] | -0.0004 [-0.0065, +0.0053] | 0.759 | 0.217 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 141 | 0.457 | 0.447 | 0.0634 | +0.0075 [+0.0015, +0.0132] | -0.0000 [-0.0053, +0.0050] | 0.743 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.512, difference +0.1036 [-0.0114, +0.1993]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0391 [+0.0231, +0.0559], realised minus predicted +0.0459 [+0.0178, +0.0760]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.275 | 0.596 | 0.1781 | 0.2720 | +0.0369 [+0.0121, +0.0653] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0330 | 0.0159 | +0.0236 [+0.0057, +0.0384] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0145 | 0.0200 | +0.0007 [-0.0062, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.583 | 0.0882 | 0.1165 | +0.0329 [+0.0055, +0.0636] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0088 | 0.0048 | +0.0081 [+0.0057, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0067 | 0.0000 | +0.0303 [+0.0242, +0.0364] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1345 | 0.2439 | 0.0355 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.563 | 0.1815 | 0.2615 | +0.0396 [+0.0158, +0.0655] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1059 | 0.1133 | +0.0414 [+0.0138, +0.0709] |
| day_type | ordinary | 1603 | 101 | 0.208 | 0.438 | 0.0412 | 0.0630 | +0.0140 [+0.0077, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0498, +0.1498] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1308 | 0.1461 | +0.0731 [+0.0420, +0.1104] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.679] | 0.269 | 4.58 flat / 1.81 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.562] | 0.231 | 3.08 flat / 1.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.346 [0.645, 2.333] | 0.596 [0.282, 1.050] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.133, 0.409] | 1.769 [1.115, 2.762] | 0.702 [0.410, 1.167] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.467] | 1.308 [0.667, 2.273] | 0.558 [0.265, 1.018] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.467] | 1.808 [0.946, 3.105] | 0.788 [0.389, 1.417] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.061, 0.333] | 1.500 [0.786, 2.501] | 0.625 [0.300, 1.141] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 5.235 [3.285, 8.154] | 1.721 [1.062, 2.688] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.314 (126 of 1873 days never flag) | 78 | 0.307 | 0.551 | 0.0492 | +0.0222 [+0.0158, +0.0294] | +0.0071 [+0.0027, +0.0122] | 0.884 | 0.287 | yes |
| 2 | 0.326 (147 of 1872 days never flag) | 92 | 0.331 | 0.500 | 0.0575 | +0.0136 [+0.0090, +0.0185] | +0.0036 [-0.0007, +0.0080] | 0.832 | 0.304 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 70 | 0.261 | 0.514 | 0.0609 | +0.0097 [+0.0041, +0.0158] | +0.0034 [-0.0024, +0.0100] | 0.807 | 0.241 | yes |
| 4 | 0.361 (147 of 1870 days never flag) | 89 | 0.304 | 0.472 | 0.0603 | +0.0105 [+0.0051, +0.0158] | +0.0021 [-0.0038, +0.0077] | 0.817 | 0.277 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 79 | 0.290 | 0.506 | 0.0609 | +0.0100 [+0.0054, +0.0145] | +0.0025 [-0.0025, +0.0072] | 0.798 | 0.267 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.622 (climatology 0.512, difference +0.1098 [+0.0160, +0.1912]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0894, ΔBrier vs climatology +0.0401 [+0.0239, +0.0568], realised minus predicted +0.0060 [-0.0246, +0.0398]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.275 | 0.560 | 0.2307 | 0.2720 | +0.0468 [+0.0227, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1153 | 0.0159 | +0.0202 [+0.0089, +0.0305] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0156 | 0.0000 | +0.0133 [+0.0116, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0230 | 0.0200 | +0.0027 [-0.0012, +0.0058] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.684 | 0.0974 | 0.1165 | +0.0335 [+0.0081, +0.0657] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0174 | 0.0048 | +0.0089 [+0.0072, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0607 | 0.0000 | +0.0251 [+0.0196, +0.0310] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.1383 | 0.2439 | 0.0357 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.556 | 0.2394 | 0.2615 | +0.0482 [+0.0249, +0.0726] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1100 | 0.1133 | +0.0400 [+0.0130, +0.0693] |
| day_type | ordinary | 1603 | 101 | 0.198 | 0.444 | 0.0743 | 0.0630 | +0.0162 [+0.0102, +0.0229] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0446, +0.1511] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1308 | 0.1461 | +0.0731 [+0.0406, +0.1074] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2519 | 0.2213 |

## risk_logistic_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.216, 0.560] | 0.231 | 3.77 flat / 1.60 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.516] | 0.231 | 3.19 flat / 1.33 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.103, 0.364] | 1.154 [0.611, 1.924] | 0.462 [0.220, 0.810] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.308 [0.706, 2.200] | 0.452 [0.234, 0.781] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 1.462 [0.714, 2.455] | 0.615 [0.280, 1.141] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.346 [0.739, 2.209] | 0.635 [0.301, 1.188] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.308 [1.257, 3.818] | 0.962 [0.500, 1.663] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.706] | 3.235 [1.625, 5.612] | 1.088 [0.550, 1.893] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 2.556 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 77 | 0.336 | 0.610 | 0.0482 | +0.0232 [+0.0162, +0.0311] | +0.0081 [+0.0032, +0.0133] | 0.911 | 0.318 | yes |
| 2 | 0.579 (147 of 1872 days never flag) | 73 | 0.281 | 0.534 | 0.0576 | +0.0134 [+0.0083, +0.0190] | +0.0034 [-0.0007, +0.0079] | 0.883 | 0.261 | yes |
| 3 | 0.373 (147 of 1871 days never flag) | 74 | 0.261 | 0.486 | 0.0608 | +0.0099 [+0.0038, +0.0162] | +0.0036 [-0.0025, +0.0097] | 0.867 | 0.239 | yes |
| 4 | 0.361 (147 of 1870 days never flag) | 68 | 0.239 | 0.485 | 0.0605 | +0.0104 [+0.0042, +0.0163] | +0.0019 [-0.0042, +0.0076] | 0.865 | 0.219 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 105 | 0.326 | 0.429 | 0.0617 | +0.0093 [+0.0039, +0.0144] | +0.0017 [-0.0032, +0.0069] | 0.852 | 0.291 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0138, +0.1940]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0869, ΔBrier vs climatology +0.0426 [+0.0265, +0.0601], realised minus predicted +0.0232 [-0.0090, +0.0562]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.727 | 0.2477 | 0.2720 | +0.0525 [+0.0258, +0.0815] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1278 | 0.0159 | +0.0146 [-0.0009, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0043 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0022 | 0.0200 | +0.0036 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.609 | 0.0966 | 0.1165 | +0.0362 [+0.0088, +0.0721] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0011 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0688 | 0.0000 | +0.0240 [+0.0184, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1655 | 0.2439 | 0.0378 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.352 | 0.629 | 0.2580 | 0.2615 | +0.0513 [+0.0275, +0.0789] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1094 | 0.1133 | +0.0409 [+0.0132, +0.0708] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.542 | 0.0716 | 0.0630 | +0.0173 [+0.0107, +0.0251] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3212 | 0.2903 | +0.0996 [+0.0428, +0.1521] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1308 | 0.1461 | +0.0731 [+0.0417, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3416 | 0.2213 |

## risk_logistic_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 3.27 flat / 1.37 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.476] | 0.192 | 1.92 flat / 0.86 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.227, 0.548] | 1.615 [0.974, 2.588] | 0.625 [0.367, 1.026] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.038 [0.586, 1.688] | 0.471 [0.224, 0.880] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 0.846 [0.450, 1.444] | 0.423 [0.177, 0.852] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 0.962 [0.516, 1.636] | 0.510 [0.218, 1.012] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.500 [0.727, 2.629] | 0.644 [0.278, 1.216] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 3.353 [1.889, 5.700] | 1.088 [0.588, 1.875] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.314 (126 of 1873 days never flag) | 98 | 0.400 | 0.571 | 0.0497 | +0.0218 [+0.0168, +0.0272] | +0.0067 [+0.0021, +0.0112] | 0.897 | 0.376 | no |
| 2 | 0.326 (147 of 1872 days never flag) | 51 | 0.173 | 0.471 | 0.0588 | +0.0123 [+0.0082, +0.0168] | +0.0023 [-0.0024, +0.0068] | 0.846 | 0.157 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 48 | 0.188 | 0.542 | 0.0619 | +0.0088 [+0.0034, +0.0140] | +0.0025 [-0.0038, +0.0084] | 0.814 | 0.176 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 47 | 0.159 | 0.468 | 0.0618 | +0.0091 [+0.0038, +0.0139] | +0.0006 [-0.0056, +0.0062] | 0.826 | 0.145 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 71 | 0.232 | 0.451 | 0.0622 | +0.0087 [+0.0042, +0.0130] | +0.0012 [-0.0040, +0.0058] | 0.807 | 0.209 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.512, difference +0.1011 [+0.0066, +0.1784]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0362 [+0.0226, +0.0502], realised minus predicted +0.0375 [+0.0058, +0.0711]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.589 | 0.1771 | 0.2720 | +0.0380 [+0.0234, +0.0555] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0767 | 0.0159 | +0.0278 [+0.0179, +0.0372] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0029 [-0.0015, +0.0061] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0751 | 0.1165 | +0.0344 [+0.0106, +0.0651] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0119 | 0.0048 | +0.0091 [+0.0073, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0371 | 0.0000 | +0.0288 [+0.0228, +0.0347] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1053 | 0.2439 | 0.0250 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.432 | 0.581 | 0.1828 | 0.2615 | +0.0444 [+0.0278, +0.0633] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1067 | 0.1133 | +0.0386 [+0.0114, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.297 | 0.484 | 0.0487 | 0.0630 | +0.0158 [+0.0118, +0.0207] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0478, +0.1514] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1308 | 0.1461 | +0.0731 [+0.0413, +0.1099] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2207 | 0.2213 |

## risk_logistic_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.154, 0.472] | 0.231 | 3.08 flat / 1.24 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.440] | 0.231 | 2.73 flat / 1.09 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.031, 0.226] | 0.615 [0.281, 1.100] | 0.240 [0.110, 0.427] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.065, 0.320] | 1.423 [0.577, 2.600] | 0.500 [0.194, 0.943] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 2.308 [1.091, 4.000] | 0.885 [0.407, 1.557] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.276] | 1.731 [0.759, 3.096] | 0.750 [0.319, 1.379] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.115 [0.962, 3.786] | 0.875 [0.400, 1.594] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.200, 0.640] | 3.824 [1.840, 6.867] | 1.294 [0.625, 2.297] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.667 (no interval) | 1.139 (no interval) |

Recall with equal weight per regime: 0.153 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 51 | 0.250 | 0.686 | 0.0619 | +0.0095 [-0.0005, +0.0194] | -0.0056 [-0.0146, +0.0027] | 0.873 | 0.241 | no |
| 2 | 0.638 (147 of 1872 days never flag) | 71 | 0.245 | 0.479 | 0.0700 | +0.0010 [-0.0078, +0.0098] | -0.0090 [-0.0172, -0.0010] | 0.826 | 0.223 | no |
| 3 | 0.623 (147 of 1871 days never flag) | 106 | 0.333 | 0.434 | 0.0747 | -0.0040 [-0.0148, +0.0054] | -0.0104 [-0.0210, -0.0008] | 0.801 | 0.299 | no |
| 4 | 0.8 (147 of 1870 days never flag) | 81 | 0.261 | 0.444 | 0.0728 | -0.0019 [-0.0103, +0.0065] | -0.0104 [-0.0187, -0.0021] | 0.816 | 0.235 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 101 | 0.333 | 0.455 | 0.0726 | -0.0017 [-0.0088, +0.0050] | -0.0092 [-0.0166, -0.0022] | 0.785 | 0.302 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.612 (climatology 0.512, difference +0.0998 [-0.0011, +0.1827]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0958, ΔBrier vs climatology +0.0337 [+0.0168, +0.0512], realised minus predicted -0.0105 [-0.0446, +0.0227]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.284 | 0.707 | 0.3222 | 0.2720 | +0.0082 [-0.0350, +0.0508] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2026 | 0.0159 | -0.0128 [-0.0340, +0.0052] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0026, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0667 | 0.1165 | +0.0331 [+0.0092, +0.0656] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1132 | 0.0000 | +0.0107 [+0.0050, +0.0168] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1219 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.280 | 0.700 | 0.3211 | 0.2615 | +0.0093 [-0.0280, +0.0472] |
| day_type | month_end | 150 | 17 | 0.353 | 0.750 | 0.1128 | 0.1133 | +0.0382 [+0.0115, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.188 | 0.633 | 0.1018 | 0.0630 | +0.0015 [-0.0086, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1489] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0411, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.263, 0.600] | 0.231 | 3.38 flat / 1.36 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.501] | 0.231 | 2.96 flat / 1.17 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 1.846 [0.857, 3.269] | 0.663 [0.315, 1.175] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.292] | 1.308 [0.556, 2.500] | 0.442 [0.179, 0.865] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.391] | 1.654 [0.733, 2.955] | 0.596 [0.268, 1.080] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.231 [0.478, 2.334] | 0.452 [0.167, 0.870] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.308 [1.212, 4.000] | 0.962 [0.488, 1.703] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.385, 0.810] | 4.176 [2.333, 7.201] | 1.397 [0.750, 2.429] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.889 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.78 (105 of 1873 days never flag) | 109 | 0.436 | 0.560 | 0.0618 | +0.0097 [-0.0004, +0.0194] | -0.0054 [-0.0145, +0.0029] | 0.876 | 0.408 | no |
| 2 | 0.593 (147 of 1872 days never flag) | 65 | 0.223 | 0.477 | 0.0690 | +0.0021 [-0.0074, +0.0104] | -0.0080 [-0.0169, -0.0003] | 0.828 | 0.203 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 80 | 0.268 | 0.463 | 0.0724 | -0.0017 [-0.0113, +0.0070] | -0.0080 [-0.0175, +0.0004] | 0.803 | 0.243 | no |
| 4 | 0.767 (147 of 1870 days never flag) | 70 | 0.275 | 0.543 | 0.0718 | -0.0010 [-0.0087, +0.0066] | -0.0094 [-0.0175, -0.0020] | 0.818 | 0.257 | no |
| 5 | 0.714 (147 of 1869 days never flag) | 107 | 0.341 | 0.439 | 0.0731 | -0.0022 [-0.0099, +0.0048] | -0.0097 [-0.0177, -0.0025] | 0.789 | 0.306 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.572 (climatology 0.512, difference +0.0594 [-0.0274, +0.1402]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0206, +0.0539], realised minus predicted -0.0102 [-0.0441, +0.0236]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.560 | 0.3272 | 0.2720 | +0.0089 [-0.0381, +0.0531] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2005 | 0.0159 | -0.0120 [-0.0332, +0.0064] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0031, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0652 | 0.1165 | +0.0325 [+0.0081, +0.0629] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1118 | 0.0000 | +0.0113 [+0.0059, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1208 | 0.2439 | 0.0255 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.565 | 0.3242 | 0.2615 | +0.0097 [-0.0311, +0.0483] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1135 | 0.1133 | +0.0383 [+0.0101, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.506 | 0.1025 | 0.0630 | +0.0017 [-0.0088, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0469, +0.1465] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1283 | 0.1461 | +0.0745 [+0.0438, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2938 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.560] | 0.231 | 2.77 flat / 1.15 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.560] | 0.231 | 2.58 flat / 1.11 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.032, 0.233] | 0.615 [0.280, 1.114] | 0.240 [0.112, 0.429] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.032, 0.233] | 0.769 [0.231, 1.591] | 0.269 [0.083, 0.542] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.500 [0.760, 2.600] | 0.673 [0.364, 1.143] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.269 [0.567, 2.294] | 0.529 [0.250, 0.935] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.100, 0.390] | 2.115 [1.074, 3.601] | 0.856 [0.454, 1.422] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.318, 0.737] | 3.412 [1.827, 5.751] | 1.235 [0.688, 2.050] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.556 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 51 | 0.250 | 0.686 | 0.0619 | +0.0095 [-0.0006, +0.0198] | -0.0056 [-0.0143, +0.0026] | 0.873 | 0.241 | no |
| 2 | 0.849 (147 of 1872 days never flag) | 55 | 0.252 | 0.636 | 0.0646 | +0.0065 [-0.0027, +0.0155] | -0.0035 [-0.0124, +0.0050] | 0.846 | 0.240 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 81 | 0.304 | 0.519 | 0.0676 | +0.0031 [-0.0071, +0.0124] | -0.0033 [-0.0131, +0.0062] | 0.825 | 0.282 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 74 | 0.297 | 0.554 | 0.0667 | +0.0041 [-0.0044, +0.0120] | -0.0043 [-0.0128, +0.0034] | 0.842 | 0.278 | yes |
| 5 | 0.855 (147 of 1869 days never flag) | 112 | 0.413 | 0.509 | 0.0666 | +0.0043 [-0.0022, +0.0111] | -0.0032 [-0.0098, +0.0035] | 0.826 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.694 (climatology 0.512, difference +0.1818 [+0.0967, +0.2766]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0284, +0.0667], realised minus predicted -0.0298 [-0.0609, +0.0006]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.284 | 0.707 | 0.3222 | 0.2720 | +0.0082 [-0.0367, +0.0517] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2026 | 0.0159 | -0.0128 [-0.0357, +0.0061] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0027, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0667 | 0.1165 | +0.0331 [+0.0079, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1132 | 0.0000 | +0.0107 [+0.0051, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1219 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.280 | 0.700 | 0.3211 | 0.2615 | +0.0093 [-0.0296, +0.0486] |
| day_type | month_end | 150 | 17 | 0.353 | 0.750 | 0.1128 | 0.1133 | +0.0382 [+0.0104, +0.0702] |
| day_type | ordinary | 1603 | 101 | 0.188 | 0.633 | 0.1018 | 0.0630 | +0.0015 [-0.0086, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1508] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0412, +0.1083] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.556] | 0.192 | 2.42 flat / 0.92 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.225, 0.550] | 0.192 | 2.15 flat / 0.86 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.846 [0.846, 3.334] | 0.663 [0.302, 1.195] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.045, 0.278] | 0.769 [0.231, 1.571] | 0.298 [0.100, 0.583] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 0.808 [0.312, 1.583] | 0.404 [0.167, 0.750] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.346 [0.565, 2.486] | 0.500 [0.217, 0.910] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.471] | 1.577 [0.666, 2.895] | 0.635 [0.290, 1.157] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.273, 0.692] | 3.118 [1.519, 5.636] | 1.074 [0.500, 1.967] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.78 (105 of 1873 days never flag) | 109 | 0.436 | 0.560 | 0.0618 | +0.0097 [-0.0011, +0.0202] | -0.0054 [-0.0148, +0.0032] | 0.876 | 0.408 | no |
| 2 | 0.772 (147 of 1872 days never flag) | 58 | 0.273 | 0.655 | 0.0645 | +0.0065 [-0.0030, +0.0152] | -0.0035 [-0.0126, +0.0048] | 0.848 | 0.262 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 51 | 0.217 | 0.588 | 0.0673 | +0.0034 [-0.0068, +0.0122] | -0.0030 [-0.0128, +0.0057] | 0.826 | 0.205 | yes |
| 4 | 0.8 (105 of 1870 days never flag) | 77 | 0.304 | 0.545 | 0.0660 | +0.0048 [-0.0032, +0.0128] | -0.0037 [-0.0121, +0.0044] | 0.842 | 0.284 | yes |
| 5 | 0.846 (147 of 1869 days never flag) | 89 | 0.348 | 0.539 | 0.0665 | +0.0044 [-0.0029, +0.0116] | -0.0031 [-0.0102, +0.0042] | 0.826 | 0.324 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1655 [+0.0644, +0.2701]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0826, ΔBrier vs climatology +0.0469 [+0.0274, +0.0694], realised minus predicted -0.0294 [-0.0594, +0.0036]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.560 | 0.3272 | 0.2720 | +0.0089 [-0.0382, +0.0539] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2005 | 0.0159 | -0.0120 [-0.0344, +0.0058] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0027, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0652 | 0.1165 | +0.0325 [+0.0076, +0.0626] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0068, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1118 | 0.0000 | +0.0113 [+0.0057, +0.0170] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1208 | 0.2439 | 0.0255 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.565 | 0.3242 | 0.2615 | +0.0097 [-0.0311, +0.0495] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1135 | 0.1133 | +0.0383 [+0.0102, +0.0683] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.506 | 0.1025 | 0.0630 | +0.0017 [-0.0091, +0.0123] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0474, +0.1469] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1283 | 0.1461 | +0.0745 [+0.0424, +0.1142] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2938 | 0.2213 |

## risk_logistic_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.214, 0.562] | 0.250 | 4.38 flat / 1.99 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.550] | 0.231 | 3.85 flat / 1.70 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.115 [0.579, 1.905] | 0.490 [0.250, 0.850] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.385] | 1.808 [0.929, 3.072] | 0.731 [0.357, 1.250] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.400] | 1.692 [0.815, 2.864] | 0.692 [0.321, 1.211] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 1.923 [0.999, 3.233] | 0.827 [0.388, 1.461] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.480] | 2.962 [1.483, 5.002] | 1.413 [0.633, 2.500] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.238, 0.722] | 5.000 [2.533, 8.751] | 2.015 [0.875, 3.875] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 1.944 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 76 | 0.336 | 0.618 | 0.0574 | +0.0140 [+0.0066, +0.0226] | -0.0011 [-0.0069, +0.0054] | 0.847 | 0.319 | no |
| 2 | 0.579 (147 of 1872 days never flag) | 80 | 0.237 | 0.412 | 0.0682 | +0.0029 [-0.0032, +0.0090] | -0.0071 [-0.0133, -0.0006] | 0.784 | 0.210 | no |
| 3 | 0.483 (147 of 1871 days never flag) | 81 | 0.268 | 0.457 | 0.0721 | -0.0014 [-0.0082, +0.0052] | -0.0077 [-0.0148, -0.0009] | 0.732 | 0.243 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 87 | 0.268 | 0.425 | 0.0717 | -0.0009 [-0.0080, +0.0059] | -0.0093 [-0.0172, -0.0018] | 0.755 | 0.239 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 124 | 0.341 | 0.379 | 0.0727 | -0.0017 [-0.0083, +0.0043] | -0.0093 [-0.0166, -0.0026] | 0.726 | 0.296 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0979 [-0.0034, +0.1793]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0988, ΔBrier vs climatology +0.0307 [+0.0146, +0.0474], realised minus predicted -0.0277 [-0.0630, +0.0092]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.667 | 0.2932 | 0.2720 | +0.0342 [+0.0043, +0.0702] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2108 | 0.0159 | -0.0108 [-0.0251, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0025 [-0.0025, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0654 | 0.1165 | +0.0310 [+0.0087, +0.0577] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0064, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1328 | 0.0000 | +0.0049 [-0.0002, +0.0105] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0990 | 0.2439 | 0.0054 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.630 | 0.2957 | 0.2615 | +0.0336 [+0.0056, +0.0664] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1135 | 0.1133 | +0.0374 [+0.0114, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.562 | 0.1060 | 0.0630 | +0.0069 [-0.0002, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3212 | 0.2903 | +0.0996 [+0.0501, +0.1483] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0731 [+0.0420, +0.1101] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.262 | 4.50 flat / 1.99 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.565] | 0.231 | 3.92 flat / 1.73 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.189, 0.500] | 2.038 [1.087, 3.295] | 0.769 [0.403, 1.280] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.369] | 1.654 [0.800, 2.750] | 0.615 [0.283, 1.050] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.846 [0.852, 3.131] | 0.663 [0.304, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.120, 0.421] | 2.000 [1.000, 3.318] | 0.798 [0.395, 1.350] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 2.962 [1.565, 4.846] | 1.423 [0.700, 2.500] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 5.176 [2.850, 8.801] | 2.044 [1.000, 3.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 121 | 0.486 | 0.562 | 0.0572 | +0.0142 [+0.0065, +0.0226] | -0.0009 [-0.0072, +0.0056] | 0.850 | 0.455 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 76 | 0.237 | 0.434 | 0.0672 | +0.0039 [-0.0022, +0.0102] | -0.0061 [-0.0116, -0.0002] | 0.785 | 0.213 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 88 | 0.290 | 0.455 | 0.0697 | +0.0010 [-0.0044, +0.0063] | -0.0053 [-0.0105, +0.0006] | 0.735 | 0.262 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 97 | 0.326 | 0.464 | 0.0708 | +0.0001 [-0.0062, +0.0060] | -0.0084 [-0.0149, -0.0025] | 0.755 | 0.296 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 124 | 0.341 | 0.379 | 0.0732 | -0.0022 [-0.0088, +0.0043] | -0.0098 [-0.0176, -0.0025] | 0.732 | 0.296 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0632 [-0.0255, +0.1421]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0963, ΔBrier vs climatology +0.0332 [+0.0177, +0.0499], realised minus predicted -0.0274 [-0.0626, +0.0096]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.574 | 0.2982 | 0.2720 | +0.0350 [+0.0016, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2086 | 0.0159 | -0.0099 [-0.0240, +0.0027] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0110 | 0.0200 | +0.0026 [-0.0024, +0.0061] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0640 | 0.1165 | +0.0304 [+0.0082, +0.0563] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0065, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1314 | 0.0000 | +0.0055 [+0.0005, +0.0109] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0980 | 0.2439 | 0.0044 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.563 | 0.2988 | 0.2615 | +0.0340 [+0.0041, +0.0652] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1142 | 0.1133 | +0.0375 [+0.0103, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.512 | 0.1068 | 0.0630 | +0.0070 [-0.0007, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0466, +0.1439] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1283 | 0.1461 | +0.0745 [+0.0446, +0.1114] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2896 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.300, 0.630] | 0.231 | 3.88 flat / 1.75 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.629] | 0.231 | 3.69 flat / 1.70 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.115 [0.593, 2.000] | 0.490 [0.250, 0.860] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.233] | 0.423 [0.115, 0.889] | 0.135 [0.040, 0.275] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.278, 0.583] | 1.808 [1.000, 3.039] | 0.837 [0.483, 1.391] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.241, 0.538] | 2.192 [1.281, 3.583] | 0.942 [0.567, 1.517] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 2.692 [1.292, 4.651] | 1.183 [0.500, 2.203] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.318, 0.750] | 4.765 [2.643, 8.251] | 2.044 [1.014, 3.750] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.222 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 76 | 0.336 | 0.618 | 0.0574 | +0.0140 [+0.0062, +0.0223] | -0.0011 [-0.0072, +0.0053] | 0.847 | 0.319 | yes |
| 2 | 0.849 (147 of 1872 days never flag) | 39 | 0.201 | 0.718 | 0.0620 | +0.0091 [+0.0024, +0.0158] | -0.0009 [-0.0074, +0.0057] | 0.812 | 0.195 | no |
| 3 | 0.848 (126 of 1871 days never flag) | 95 | 0.348 | 0.505 | 0.0644 | +0.0063 [+0.0003, +0.0127] | -0.0001 [-0.0061, +0.0066] | 0.770 | 0.321 | no |
| 4 | 0.528 (126 of 1870 days never flag) | 109 | 0.377 | 0.477 | 0.0653 | +0.0055 [-0.0009, +0.0119] | -0.0029 [-0.0098, +0.0037] | 0.791 | 0.344 | yes |
| 5 | 0.855 (147 of 1869 days never flag) | 125 | 0.399 | 0.440 | 0.0663 | +0.0046 [-0.0017, +0.0108] | -0.0029 [-0.0095, +0.0041] | 0.778 | 0.358 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.695 (climatology 0.512, difference +0.1830 [+0.0978, +0.2723]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0447 [+0.0266, +0.0651], realised minus predicted -0.0487 [-0.0806, -0.0151]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.667 | 0.2932 | 0.2720 | +0.0342 [+0.0036, +0.0693] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2108 | 0.0159 | -0.0108 [-0.0252, +0.0015] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0025 [-0.0025, +0.0063] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0654 | 0.1165 | +0.0310 [+0.0081, +0.0583] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0064, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1328 | 0.0000 | +0.0049 [-0.0003, +0.0102] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0990 | 0.2439 | 0.0054 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.630 | 0.2957 | 0.2615 | +0.0336 [+0.0033, +0.0648] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1135 | 0.1133 | +0.0374 [+0.0101, +0.0665] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.562 | 0.1060 | 0.0630 | +0.0069 [-0.0005, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3212 | 0.2903 | +0.0996 [+0.0466, +0.1500] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0731 [+0.0407, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.292, 0.640] | 0.231 | 3.54 flat / 1.56 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.625] | 0.231 | 3.19 flat / 1.47 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.038 [1.088, 3.400] | 0.769 [0.405, 1.286] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.281] | 0.462 [0.148, 0.944] | 0.173 [0.058, 0.347] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.371] | 0.692 [0.333, 1.182] | 0.394 [0.175, 0.685] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.237, 0.536] | 2.077 [1.125, 3.429] | 0.865 [0.476, 1.413] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.190, 0.526] | 2.423 [1.067, 4.353] | 1.115 [0.439, 2.102] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 4.412 [2.179, 7.693] | 1.853 [0.786, 3.501] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 1.889 [0.867, 4.200] | 1.000 [0.431, 2.375] |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 121 | 0.486 | 0.562 | 0.0572 | +0.0142 [+0.0064, +0.0223] | -0.0009 [-0.0072, +0.0059] | 0.850 | 0.455 | yes |
| 2 | 0.772 (147 of 1872 days never flag) | 44 | 0.230 | 0.727 | 0.0619 | +0.0092 [+0.0026, +0.0157] | -0.0008 [-0.0072, +0.0061] | 0.815 | 0.223 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 50 | 0.232 | 0.640 | 0.0641 | +0.0066 [+0.0006, +0.0128] | +0.0002 [-0.0062, +0.0067] | 0.769 | 0.221 | no |
| 4 | 0.866 (105 of 1870 days never flag) | 105 | 0.370 | 0.486 | 0.0646 | +0.0062 [+0.0000, +0.0124] | -0.0023 [-0.0088, +0.0043] | 0.789 | 0.338 | yes |
| 5 | 0.846 (147 of 1869 days never flag) | 115 | 0.377 | 0.452 | 0.0663 | +0.0047 [-0.0018, +0.0108] | -0.0029 [-0.0093, +0.0041] | 0.777 | 0.340 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1661 [+0.0643, +0.2681]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0844, ΔBrier vs climatology +0.0451 [+0.0263, +0.0662], realised minus predicted -0.0484 [-0.0790, -0.0161]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.574 | 0.2982 | 0.2720 | +0.0350 [+0.0007, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2086 | 0.0159 | -0.0099 [-0.0234, +0.0031] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0110 | 0.0200 | +0.0026 [-0.0024, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0640 | 0.1165 | +0.0304 [+0.0085, +0.0558] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0065, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1314 | 0.0000 | +0.0055 [+0.0005, +0.0112] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0980 | 0.2439 | 0.0044 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.563 | 0.2988 | 0.2615 | +0.0340 [+0.0036, +0.0657] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1142 | 0.1133 | +0.0375 [+0.0089, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.512 | 0.1068 | 0.0630 | +0.0070 [-0.0006, +0.0151] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0459, +0.1466] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1283 | 0.1461 | +0.0745 [+0.0436, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2896 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 9 | 0.346 [0.176, 0.531] | 0.231 | 3.50 flat / 1.39 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.500] | 0.231 | 3.12 flat / 1.20 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.043, 0.280] | 0.846 [0.395, 1.500] | 0.327 [0.156, 0.573] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.577 [0.650, 2.941] | 0.538 [0.213, 1.009] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.846 [0.844, 3.250] | 0.721 [0.318, 1.289] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 1.538 [0.692, 2.737] | 0.692 [0.288, 1.264] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.500] | 3.000 [1.533, 5.048] | 1.163 [0.590, 1.938] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.241, 0.727] | 4.529 [2.357, 8.077] | 1.559 [0.809, 2.750] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.300] | 1.556 [0.500, 3.800] | 1.083 [0.250, 3.000] |

Recall with equal weight per regime: 0.168 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 72 | 0.357 | 0.694 | 0.0576 | +0.0138 [+0.0036, +0.0238] | -0.0012 [-0.0102, +0.0072] | 0.919 | 0.344 | yes |
| 2 | 0.638 (147 of 1872 days never flag) | 82 | 0.295 | 0.500 | 0.0648 | +0.0063 [-0.0029, +0.0149] | -0.0037 [-0.0122, +0.0039] | 0.886 | 0.271 | no |
| 3 | 0.623 (147 of 1871 days never flag) | 86 | 0.275 | 0.442 | 0.0682 | +0.0025 [-0.0080, +0.0125] | -0.0039 [-0.0147, +0.0059] | 0.891 | 0.248 | no |
| 4 | 0.677 (147 of 1870 days never flag) | 69 | 0.210 | 0.420 | 0.0681 | +0.0027 [-0.0054, +0.0104] | -0.0057 [-0.0138, +0.0023] | 0.849 | 0.187 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 147 | 0.500 | 0.469 | 0.0726 | -0.0016 [-0.0114, +0.0068] | -0.0092 [-0.0188, -0.0007] | 0.824 | 0.455 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.625 (climatology 0.512, difference +0.1133 [+0.0190, +0.1877]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0902, ΔBrier vs climatology +0.0393 [+0.0224, +0.0586], realised minus predicted +0.0071 [-0.0262, +0.0417]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.721 | 0.3231 | 0.2720 | +0.0120 [-0.0311, +0.0540] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0944 | 0.0159 | +0.0086 [-0.0194, +0.0308] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0036 [-0.0002, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0757 | 0.1165 | +0.0321 [+0.0093, +0.0610] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0078, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0065 | 0.0000 | +0.0304 [+0.0245, +0.0364] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0703 | 0.2439 | 0.0173 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.704 | 0.3294 | 0.2615 | +0.0123 [-0.0276, +0.0516] |
| day_type | month_end | 150 | 17 | 0.353 | 0.600 | 0.1092 | 0.1133 | +0.0389 [+0.0110, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.688 | 0.0789 | 0.0630 | +0.0065 [-0.0039, +0.0165] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.875 | 0.1308 | 0.1461 | +0.0731 [+0.0408, +0.1101] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2847 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.682] | 0.231 | 3.85 flat / 1.56 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.560] | 0.231 | 3.08 flat / 1.24 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.190, 0.520] | 2.308 [1.161, 3.773] | 0.846 [0.419, 1.375] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.286] | 1.308 [0.517, 2.409] | 0.442 [0.167, 0.828] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 1.731 [0.769, 3.000] | 0.577 [0.250, 1.029] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.462 [0.611, 2.650] | 0.577 [0.223, 1.083] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.476] | 2.423 [1.240, 4.048] | 1.038 [0.510, 1.781] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.941 [2.808, 8.083] | 1.735 [0.958, 2.889] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.778 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (105 of 1873 days never flag) | 127 | 0.479 | 0.528 | 0.0578 | +0.0136 [+0.0034, +0.0232] | -0.0015 [-0.0106, +0.0068] | 0.920 | 0.444 | yes |
| 2 | 0.593 (147 of 1872 days never flag) | 66 | 0.230 | 0.485 | 0.0640 | +0.0071 [-0.0026, +0.0158] | -0.0029 [-0.0121, +0.0050] | 0.888 | 0.211 | no |
| 3 | 0.639 (147 of 1871 days never flag) | 83 | 0.275 | 0.458 | 0.0659 | +0.0048 [-0.0066, +0.0144] | -0.0015 [-0.0121, +0.0079] | 0.894 | 0.249 | no |
| 4 | 0.662 (147 of 1870 days never flag) | 82 | 0.319 | 0.537 | 0.0644 | +0.0064 [-0.0012, +0.0134] | -0.0021 [-0.0096, +0.0049] | 0.881 | 0.297 | no |
| 5 | 0.557 (147 of 1869 days never flag) | 111 | 0.348 | 0.432 | 0.0674 | +0.0035 [-0.0037, +0.0105] | -0.0040 [-0.0117, +0.0033] | 0.829 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0632 [-0.0322, +0.1440]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0255, +0.0601], realised minus predicted +0.0088 [-0.0222, +0.0416]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.521 | 0.3287 | 0.2720 | +0.0109 [-0.0337, +0.0521] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0929 | 0.0159 | +0.0091 [-0.0177, +0.0319] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0743 | 0.1165 | +0.0318 [+0.0094, +0.0586] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0051 | 0.0000 | +0.0310 [+0.0241, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0693 | 0.2439 | 0.0163 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.532 | 0.3334 | 0.2615 | +0.0111 [-0.0278, +0.0487] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1101 | 0.1133 | +0.0393 [+0.0095, +0.0699] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.463 | 0.0799 | 0.0630 | +0.0062 [-0.0042, +0.0159] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0475, +0.1473] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0425, +0.1110] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.550] | 0.231 | 2.54 flat / 1.01 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.545] | 0.192 | 2.04 flat / 0.84 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 0.846 [0.414, 1.500] | 0.327 [0.164, 0.583] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.231] | 1.115 [0.364, 2.286] | 0.394 [0.139, 0.800] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.269 [0.536, 2.312] | 0.490 [0.216, 0.880] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 1.385 [0.625, 2.517] | 0.587 [0.288, 1.018] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.038, 0.286] | 1.654 [0.714, 2.945] | 0.596 [0.263, 1.071] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 3.471 [1.888, 6.112] | 1.265 [0.706, 2.208] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.778 (no interval) | 0.528 (no interval) |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 72 | 0.357 | 0.694 | 0.0576 | +0.0138 [+0.0040, +0.0236] | -0.0012 [-0.0095, +0.0064] | 0.919 | 0.344 | yes |
| 2 | 0.849 (147 of 1872 days never flag) | 69 | 0.288 | 0.580 | 0.0600 | +0.0110 [+0.0013, +0.0200] | +0.0010 [-0.0082, +0.0098] | 0.896 | 0.271 | yes |
| 3 | 0.848 (126 of 1871 days never flag) | 72 | 0.283 | 0.542 | 0.0620 | +0.0086 [-0.0024, +0.0179] | +0.0023 [-0.0085, +0.0119] | 0.898 | 0.264 | no |
| 4 | 0.778 (126 of 1870 days never flag) | 80 | 0.319 | 0.550 | 0.0627 | +0.0082 [+0.0004, +0.0157] | -0.0003 [-0.0082, +0.0073] | 0.864 | 0.298 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 91 | 0.348 | 0.527 | 0.0672 | +0.0037 [-0.0054, +0.0121] | -0.0038 [-0.0127, +0.0047] | 0.850 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.694 (climatology 0.512, difference +0.1818 [+0.0954, +0.2710]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0785, ΔBrier vs climatology +0.0510 [+0.0324, +0.0713], realised minus predicted -0.0118 [-0.0420, +0.0190]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.721 | 0.3231 | 0.2720 | +0.0120 [-0.0302, +0.0532] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0944 | 0.0159 | +0.0086 [-0.0190, +0.0310] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0036 [-0.0000, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0757 | 0.1165 | +0.0321 [+0.0099, +0.0596] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0065 | 0.0000 | +0.0304 [+0.0240, +0.0361] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0703 | 0.2439 | 0.0173 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.704 | 0.3294 | 0.2615 | +0.0123 [-0.0245, +0.0493] |
| day_type | month_end | 150 | 17 | 0.353 | 0.600 | 0.1092 | 0.1133 | +0.0389 [+0.0117, +0.0689] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.688 | 0.0789 | 0.0630 | +0.0065 [-0.0034, +0.0165] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0466, +0.1495] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.875 | 0.1308 | 0.1461 | +0.0731 [+0.0398, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2847 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.296, 0.636] | 0.231 | 2.88 flat / 1.12 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.219, 0.556] | 0.192 | 2.12 flat / 0.82 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.522] | 2.308 [1.166, 4.000] | 0.846 [0.427, 1.461] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.000 [0.414, 1.929] | 0.481 [0.219, 0.865] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.692 [0.161, 1.549] | 0.288 [0.070, 0.629] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.846 [0.812, 3.474] | 0.692 [0.320, 1.292] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.471] | 1.769 [0.714, 3.433] | 0.683 [0.300, 1.286] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.318, 0.741] | 3.824 [1.968, 6.688] | 1.368 [0.691, 2.417] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (105 of 1873 days never flag) | 127 | 0.479 | 0.528 | 0.0578 | +0.0136 [+0.0035, +0.0235] | -0.0015 [-0.0104, +0.0069] | 0.920 | 0.444 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 67 | 0.295 | 0.612 | 0.0601 | +0.0110 [+0.0017, +0.0197] | +0.0010 [-0.0078, +0.0093] | 0.898 | 0.280 | yes |
| 3 | 0.836 (147 of 1871 days never flag) | 47 | 0.210 | 0.617 | 0.0619 | +0.0088 [-0.0019, +0.0182] | +0.0025 [-0.0084, +0.0116] | 0.900 | 0.200 | no |
| 4 | 0.7 (105 of 1870 days never flag) | 105 | 0.413 | 0.543 | 0.0595 | +0.0114 [+0.0042, +0.0185] | +0.0029 [-0.0043, +0.0103] | 0.891 | 0.385 | no |
| 5 | 0.846 (147 of 1869 days never flag) | 99 | 0.384 | 0.535 | 0.0613 | +0.0096 [+0.0026, +0.0161] | +0.0021 [-0.0050, +0.0090] | 0.853 | 0.357 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1661 [+0.0682, +0.2659]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0776, ΔBrier vs climatology +0.0518 [+0.0332, +0.0735], realised minus predicted -0.0096 [-0.0383, +0.0214]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.521 | 0.3287 | 0.2720 | +0.0109 [-0.0334, +0.0545] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0929 | 0.0159 | +0.0091 [-0.0188, +0.0316] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [+0.0002, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0743 | 0.1165 | +0.0318 [+0.0089, +0.0605] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0051 | 0.0000 | +0.0310 [+0.0246, +0.0368] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0693 | 0.2439 | 0.0163 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.532 | 0.3334 | 0.2615 | +0.0111 [-0.0284, +0.0494] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1101 | 0.1133 | +0.0393 [+0.0106, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.463 | 0.0799 | 0.0630 | +0.0062 [-0.0044, +0.0163] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0480, +0.1453] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0429, +0.1115] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.606] | 0.231 | 4.15 flat / 1.82 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.606] | 0.231 | 3.96 flat / 1.74 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.032, 0.222] | 1.077 [0.419, 2.087] | 0.365 [0.144, 0.713] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.269] | 1.846 [0.739, 3.333] | 0.894 [0.308, 1.750] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 2.423 [1.143, 4.125] | 1.154 [0.478, 2.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 2.077 [0.943, 3.697] | 1.096 [0.444, 2.114] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.562] | 3.654 [2.036, 5.864] | 1.615 [0.833, 2.719] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.286, 0.789] | 5.706 [3.190, 9.708] | 2.265 [1.163, 3.969] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.972 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 85 | 0.407 | 0.671 | 0.0512 | +0.0203 [+0.0124, +0.0285] | +0.0052 [-0.0007, +0.0111] | 0.901 | 0.391 | yes |
| 2 | 0.579 (147 of 1872 days never flag) | 79 | 0.223 | 0.392 | 0.0598 | +0.0113 [+0.0050, +0.0178] | +0.0013 [-0.0045, +0.0073] | 0.863 | 0.195 | no |
| 3 | 0.483 (147 of 1871 days never flag) | 106 | 0.312 | 0.406 | 0.0623 | +0.0084 [+0.0020, +0.0148] | +0.0021 [-0.0043, +0.0088] | 0.858 | 0.275 | no |
| 4 | 0.48 (147 of 1870 days never flag) | 87 | 0.239 | 0.379 | 0.0642 | +0.0066 [+0.0000, +0.0130] | -0.0019 [-0.0089, +0.0055] | 0.830 | 0.208 | no |
| 5 | 0.552 (147 of 1869 days never flag) | 161 | 0.478 | 0.410 | 0.0690 | +0.0019 [-0.0046, +0.0079] | -0.0056 [-0.0128, +0.0011] | 0.789 | 0.423 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0204, +0.1948]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0924, ΔBrier vs climatology +0.0371 [+0.0212, +0.0547], realised minus predicted +0.0051 [-0.0271, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.667 | 0.2840 | 0.2720 | +0.0408 [+0.0093, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1330 | 0.0159 | +0.0121 [-0.0077, +0.0283] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0032 | 0.0200 | +0.0036 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0734 | 0.1165 | +0.0345 [+0.0094, +0.0662] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0538 | 0.0000 | +0.0269 [+0.0214, +0.0328] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0987 | 0.2439 | 0.0159 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.679 | 0.2915 | 0.2615 | +0.0398 [+0.0095, +0.0713] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1106 | 0.1133 | +0.0395 [+0.0109, +0.0692] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.645 | 0.0788 | 0.0630 | +0.0140 [+0.0065, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0458, +0.1491] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0418, +0.1090] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2756 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.250 | 4.38 flat / 1.93 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.560] | 0.231 | 3.77 flat / 1.67 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.227, 0.556] | 2.538 [1.353, 4.282] | 0.962 [0.523, 1.625] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.885 [0.810, 3.560] | 0.856 [0.300, 1.763] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.524] | 2.769 [1.444, 4.616] | 1.192 [0.556, 2.167] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.692 [0.833, 3.002] | 0.721 [0.342, 1.292] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.038 [1.580, 5.162] | 1.413 [0.667, 2.552] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 5.824 [3.350, 9.702] | 2.294 [1.196, 4.119] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 1.250 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 137 | 0.507 | 0.518 | 0.0512 | +0.0202 [+0.0123, +0.0288] | +0.0051 [-0.0009, +0.0112] | 0.901 | 0.469 | yes |
| 2 | 0.593 (147 of 1872 days never flag) | 85 | 0.259 | 0.424 | 0.0589 | +0.0121 [+0.0060, +0.0187] | +0.0021 [-0.0035, +0.0079] | 0.865 | 0.231 | no |
| 3 | 0.442 (147 of 1871 days never flag) | 120 | 0.348 | 0.400 | 0.0601 | +0.0106 [+0.0054, +0.0163] | +0.0043 [-0.0009, +0.0100] | 0.860 | 0.306 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 87 | 0.312 | 0.494 | 0.0618 | +0.0091 [+0.0035, +0.0147] | +0.0006 [-0.0053, +0.0068] | 0.841 | 0.286 | no |
| 5 | 0.489 (147 of 1869 days never flag) | 129 | 0.362 | 0.388 | 0.0675 | +0.0035 [-0.0036, +0.0100] | -0.0041 [-0.0116, +0.0029] | 0.801 | 0.317 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.577 (climatology 0.512, difference +0.0651 [-0.0283, +0.1509]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0888, ΔBrier vs climatology +0.0407 [+0.0254, +0.0568], realised minus predicted +0.0093 [-0.0226, +0.0439]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.2907 | 0.2720 | +0.0403 [+0.0075, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1319 | 0.0159 | +0.0127 [-0.0058, +0.0301] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0076 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0033 | 0.0200 | +0.0037 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0714 | 0.1165 | +0.0340 [+0.0099, +0.0637] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0540 | 0.0000 | +0.0273 [+0.0217, +0.0334] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0937 | 0.2439 | 0.0154 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.519 | 0.2958 | 0.2615 | +0.0392 [+0.0088, +0.0721] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1113 | 0.1133 | +0.0396 [+0.0110, +0.0709] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.451 | 0.0801 | 0.0630 | +0.0138 [+0.0064, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0430, +0.1462] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0431, +0.1134] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2776 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.630] | 0.231 | 3.58 flat / 1.65 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.622] | 0.231 | 3.50 flat / 1.63 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.026, 0.227] | 1.077 [0.435, 2.053] | 0.365 [0.147, 0.697] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.026, 0.227] | 1.308 [0.305, 2.800] | 0.692 [0.130, 1.580] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.267, 0.579] | 1.846 [0.967, 3.120] | 0.837 [0.466, 1.355] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.238, 0.526] | 2.269 [1.241, 3.722] | 0.942 [0.546, 1.500] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 2.654 [1.270, 4.591] | 1.173 [0.492, 2.179] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.316, 0.733] | 4.824 [2.583, 8.274] | 2.059 [1.000, 3.751] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.222 [0.500, 2.750] | 0.889 [0.325, 2.278] |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 85 | 0.407 | 0.671 | 0.0512 | +0.0203 [+0.0122, +0.0287] | +0.0052 [-0.0006, +0.0112] | 0.901 | 0.391 | yes |
| 2 | 0.849 (147 of 1872 days never flag) | 66 | 0.230 | 0.485 | 0.0542 | +0.0168 [+0.0100, +0.0241] | +0.0068 [+0.0003, +0.0135] | 0.877 | 0.211 | yes |
| 3 | 0.438 (126 of 1871 days never flag) | 98 | 0.362 | 0.510 | 0.0555 | +0.0152 [+0.0089, +0.0217] | +0.0089 [+0.0025, +0.0157] | 0.867 | 0.335 | yes |
| 4 | 0.528 (126 of 1870 days never flag) | 115 | 0.406 | 0.487 | 0.0585 | +0.0124 [+0.0060, +0.0187] | +0.0039 [-0.0031, +0.0109] | 0.848 | 0.372 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 121 | 0.377 | 0.430 | 0.0632 | +0.0077 [+0.0015, +0.0139] | +0.0002 [-0.0062, +0.0070] | 0.827 | 0.337 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.695 (climatology 0.512, difference +0.1824 [+0.0988, +0.2706]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0788, ΔBrier vs climatology +0.0507 [+0.0319, +0.0706], realised minus predicted -0.0157 [-0.0465, +0.0164]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.667 | 0.2840 | 0.2720 | +0.0408 [+0.0099, +0.0756] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1330 | 0.0159 | +0.0121 [-0.0068, +0.0290] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0032 | 0.0200 | +0.0036 [+0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0734 | 0.1165 | +0.0345 [+0.0094, +0.0650] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0538 | 0.0000 | +0.0269 [+0.0213, +0.0329] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0987 | 0.2439 | 0.0159 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.679 | 0.2915 | 0.2615 | +0.0398 [+0.0092, +0.0714] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1106 | 0.1133 | +0.0395 [+0.0122, +0.0696] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.645 | 0.0788 | 0.0630 | +0.0140 [+0.0064, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0460, +0.1502] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0428, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2756 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 3.62 flat / 1.61 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.633] | 0.231 | 2.96 flat / 1.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.542] | 2.538 [1.291, 4.179] | 0.962 [0.500, 1.573] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.048, 0.276] | 1.346 [0.324, 2.790] | 0.702 [0.138, 1.558] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.111, 0.364] | 0.385 [0.097, 0.821] | 0.135 [0.033, 0.283] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.231, 0.542] | 2.269 [1.118, 3.952] | 1.125 [0.500, 2.120] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.469] | 1.808 [0.771, 3.318] | 0.692 [0.312, 1.262] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 4.882 [2.621, 8.134] | 2.029 [0.955, 3.679] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.222 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 137 | 0.507 | 0.518 | 0.0512 | +0.0202 [+0.0123, +0.0285] | +0.0051 [-0.0011, +0.0112] | 0.901 | 0.469 | yes |
| 2 | 0.772 (147 of 1872 days never flag) | 70 | 0.252 | 0.500 | 0.0543 | +0.0168 [+0.0096, +0.0235] | +0.0068 [+0.0002, +0.0135] | 0.879 | 0.232 | yes |
| 3 | 0.836 (147 of 1871 days never flag) | 44 | 0.246 | 0.773 | 0.0554 | +0.0153 [+0.0094, +0.0217] | +0.0090 [+0.0032, +0.0154] | 0.868 | 0.241 | no |
| 4 | 0.476 (105 of 1870 days never flag) | 115 | 0.406 | 0.487 | 0.0563 | +0.0145 [+0.0086, +0.0206] | +0.0061 [-0.0002, +0.0128] | 0.856 | 0.372 | yes |
| 5 | 0.846 (147 of 1869 days never flag) | 100 | 0.384 | 0.530 | 0.0612 | +0.0097 [+0.0034, +0.0159] | +0.0022 [-0.0046, +0.0089] | 0.835 | 0.357 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1668 [+0.0734, +0.2681]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0771, ΔBrier vs climatology +0.0524 [+0.0333, +0.0719], realised minus predicted -0.0116 [-0.0411, +0.0184]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.2907 | 0.2720 | +0.0403 [+0.0076, +0.0757] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1319 | 0.0159 | +0.0127 [-0.0078, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0076 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0033 | 0.0200 | +0.0037 [+0.0002, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0714 | 0.1165 | +0.0340 [+0.0093, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0540 | 0.0000 | +0.0273 [+0.0212, +0.0330] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0937 | 0.2439 | 0.0154 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.519 | 0.2958 | 0.2615 | +0.0392 [+0.0091, +0.0706] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1113 | 0.1133 | +0.0396 [+0.0112, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.451 | 0.0801 | 0.0630 | +0.0138 [+0.0061, +0.0220] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0456, +0.1459] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0425, +0.1129] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2776 | 0.2213 |

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.450, 0.773] | 0.231 | 3.85 flat / 3.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.545] | 0.231 | 3.12 flat / 2.48 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.364, 0.700] | 2.115 [1.324, 3.385] | 1.529 [0.816, 2.682] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 1.423 [0.852, 2.300] | 0.981 [0.493, 1.790] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.455] | 1.769 [1.130, 2.847] | 1.269 [0.707, 2.238] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.500 [1.667, 3.905] | 1.923 [1.169, 3.237] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.000 [1.286, 3.191] | 1.423 [0.796, 2.465] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.529, 0.882] | 1.294 [0.762, 2.154] | 0.559 [0.287, 1.024] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.667 (no interval) | 7.917 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.355 (21 of 1873 days never flag) | 101 | 0.329 | 0.455 | 0.0643 | +0.0071 [+0.0015, +0.0131] | -0.0080 [-0.0162, -0.0004] | 0.645 | 0.297 | no |
| 2 | 0.475 (126 of 1872 days never flag) | 64 | 0.194 | 0.422 | 0.0676 | +0.0034 [-0.0037, +0.0106] | -0.0066 [-0.0150, +0.0013] | 0.575 | 0.173 | no |
| 3 | 0.184 (126 of 1871 days never flag) | 72 | 0.188 | 0.361 | 0.0670 | +0.0037 [-0.0035, +0.0104] | -0.0027 [-0.0104, +0.0047] | 0.582 | 0.162 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 94 | 0.210 | 0.309 | 0.0671 | +0.0037 [-0.0026, +0.0096] | -0.0048 [-0.0123, +0.0018] | 0.579 | 0.173 | no |
| 5 | 0.0988 (126 of 1869 days never flag) | 80 | 0.203 | 0.350 | 0.0663 | +0.0047 [-0.0022, +0.0109] | -0.0029 [-0.0104, +0.0041] | 0.581 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 3.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 3.6 over 1041 days; regime_2021-23: 4.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.642 (climatology 0.512, difference +0.1298 [+0.0281, +0.2339]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1113, ΔBrier vs climatology +0.0182 [+0.0076, +0.0297], realised minus predicted +0.0591 [+0.0253, +0.0967]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.627 | 0.0990 | 0.2720 | -0.0111 [-0.0320, +0.0100] |
| regime | 2020 | 251 | 4 | 0.250 | 0.031 | 0.0630 | 0.0159 | +0.0047 [-0.0118, +0.0203] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0109 | 0.0200 | +0.0018 [-0.0033, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.750 | 0.0489 | 0.1165 | +0.0227 [+0.0039, +0.0475] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0056 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0333 | 0.0000 | +0.0121 [-0.0003, +0.0227] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0819 | 0.2439 | -0.0305 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.352 | 0.603 | 0.1054 | 0.2615 | +0.0034 [-0.0176, +0.0257] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1188 | 0.1133 | +0.0214 [-0.0122, +0.0556] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.444 | 0.0146 | 0.0630 | +0.0008 [-0.0048, +0.0059] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3544 | 0.2903 | +0.0945 [+0.0001, +0.1888] |
| day_type | tax_date | 89 | 13 | 0.846 | 0.458 | 0.2000 | 0.1461 | +0.0663 [+0.0181, +0.1187] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.325, 0.667] | 0.231 | 2.54 flat / 1.84 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.58 flat / 0.99 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.325, 0.667] | 1.962 [1.273, 3.125] | 1.365 [0.759, 2.406] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.166, 0.458] | 1.500 [0.931, 2.333] | 0.913 [0.462, 1.609] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.538 [0.937, 2.375] | 0.981 [0.481, 1.724] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.705, 1.684] | 0.558 [0.276, 0.988] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.176 [0.667, 1.909] | 0.471 [0.224, 0.865] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.111 (no interval) | 4.417 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.26 (126 of 1873 days never flag) | 94 | 0.307 | 0.457 | 0.0648 | +0.0066 [-0.0000, +0.0132] | -0.0084 [-0.0172, +0.0000] | 0.638 | 0.278 | no |
| 2 | 0.171 (126 of 1872 days never flag) | 68 | 0.209 | 0.426 | 0.0687 | +0.0024 [-0.0055, +0.0094] | -0.0076 [-0.0167, -0.0000] | 0.579 | 0.186 | no |
| 3 | 0.294 (126 of 1871 days never flag) | 70 | 0.217 | 0.429 | 0.0679 | +0.0028 [-0.0046, +0.0098] | -0.0035 [-0.0116, +0.0039] | 0.584 | 0.194 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0666 | +0.0042 [-0.0031, +0.0111] | -0.0042 [-0.0124, +0.0035] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 55 | 0.203 | 0.509 | 0.0665 | +0.0044 [-0.0025, +0.0111] | -0.0031 [-0.0114, +0.0046] | 0.584 | 0.187 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.512, difference +0.0867 [-0.0682, +0.2247]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1069, ΔBrier vs climatology +0.0226 [+0.0098, +0.0359], realised minus predicted +0.0552 [+0.0212, +0.0901]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.625 | 0.1190 | 0.2720 | -0.0214 [-0.0472, +0.0047] |
| regime | 2020 | 251 | 4 | 0.250 | 0.034 | 0.0535 | 0.0159 | +0.0165 [+0.0051, +0.0274] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0116 | 0.0200 | +0.0014 [-0.0050, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0522 | 0.1165 | +0.0232 [+0.0036, +0.0459] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0055 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0303 | 0.0000 | +0.0173 [+0.0085, +0.0247] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.0788 | 0.2439 | -0.0198 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.328 | 0.612 | 0.1206 | 0.2615 | -0.0027 [-0.0269, +0.0225] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1438 | 0.1133 | +0.0138 [-0.0251, +0.0536] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.441 | 0.0161 | 0.0630 | +0.0022 [-0.0035, +0.0076] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3214 | 0.2903 | +0.0712 [-0.0019, +0.1363] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2112 | 0.1461 | +0.0525 [+0.0089, +0.0978] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.409, 0.750] | 0.269 | 5.23 flat / 2.36 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 4.08 flat / 1.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.226, 0.556] | 2.423 [1.552, 3.640] | 0.952 [0.574, 1.520] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.069, 0.316] | 1.423 [0.864, 2.280] | 0.538 [0.316, 0.871] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.531] | 2.577 [1.571, 4.084] | 1.087 [0.663, 1.750] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.192 [1.400, 3.412] | 0.933 [0.583, 1.524] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.231, 0.550] | 2.462 [1.533, 3.895] | 1.096 [0.676, 1.767] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 4.824 [2.842, 7.750] | 1.706 [1.000, 2.769] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.000 (no interval) | 3.583 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 135 | 0.514 | 0.533 | 0.0549 | +0.0166 [+0.0078, +0.0256] | +0.0015 [-0.0051, +0.0076] | 0.879 | 0.478 | yes |
| 2 | 0.409 (126 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0601 | +0.0109 [+0.0049, +0.0173] | +0.0009 [-0.0039, +0.0056] | 0.846 | 0.230 | yes |
| 3 | 0.47 (126 of 1871 days never flag) | 116 | 0.355 | 0.422 | 0.0617 | +0.0089 [+0.0030, +0.0153] | +0.0026 [-0.0027, +0.0081] | 0.834 | 0.316 | yes |
| 4 | 0.407 (126 of 1870 days never flag) | 112 | 0.399 | 0.491 | 0.0591 | +0.0117 [+0.0055, +0.0184] | +0.0032 [-0.0022, +0.0090] | 0.847 | 0.366 | yes |
| 5 | 0.465 (126 of 1869 days never flag) | 113 | 0.355 | 0.434 | 0.0599 | +0.0110 [+0.0051, +0.0174] | +0.0035 [-0.0016, +0.0093] | 0.842 | 0.318 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.512, difference +0.1248 [+0.0086, +0.2320]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0410 [+0.0234, +0.0604], realised minus predicted -0.0190 [-0.0489, +0.0130]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.580 | 0.2604 | 0.2720 | +0.0343 [+0.0002, +0.0683] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1562 | 0.0159 | +0.0002 [-0.0148, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0214 | 0.0000 | +0.0130 [+0.0112, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0417 | 0.0200 | -0.0016 [-0.0088, +0.0039] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1284 | 0.1165 | +0.0351 [+0.0021, +0.0751] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0271 | 0.0048 | +0.0072 [+0.0045, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0936 | 0.0000 | +0.0109 [+0.0019, +0.0189] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1994 | 0.2439 | 0.0225 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.583 | 0.2710 | 0.2615 | +0.0401 [+0.0092, +0.0724] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1531 | 0.1133 | +0.0189 [-0.0231, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.511 | 0.0895 | 0.0630 | +0.0133 [+0.0059, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0034, +0.1375] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0098, +0.1012] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.741] | 0.269 | 5.19 flat / 2.37 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.231 | 4.12 flat / 1.83 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.193, 0.514] | 2.115 [1.438, 3.131] | 0.885 [0.536, 1.467] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.321] | 1.423 [0.846, 2.200] | 0.538 [0.315, 0.847] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.471] | 2.577 [1.576, 4.000] | 1.087 [0.654, 1.733] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.381, 3.381] | 0.923 [0.562, 1.510] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.632] | 3.154 [2.000, 4.824] | 1.327 [0.845, 2.094] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.765 [2.899, 7.638] | 1.721 [1.011, 2.813] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.091, 0.571] | 6.000 [3.583, 12.810] | 3.583 [1.954, 8.752] |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 117 | 0.443 | 0.530 | 0.0567 | +0.0147 [+0.0068, +0.0231] | -0.0004 [-0.0068, +0.0059] | 0.795 | 0.411 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0624 | +0.0087 [+0.0021, +0.0155] | -0.0013 [-0.0065, +0.0039] | 0.751 | 0.230 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 114 | 0.341 | 0.412 | 0.0618 | +0.0089 [+0.0023, +0.0153] | +0.0026 [-0.0034, +0.0084] | 0.753 | 0.302 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 110 | 0.391 | 0.491 | 0.0600 | +0.0108 [+0.0045, +0.0170] | +0.0024 [-0.0029, +0.0076] | 0.767 | 0.359 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 152 | 0.507 | 0.461 | 0.0605 | +0.0104 [+0.0042, +0.0170] | +0.0029 [-0.0026, +0.0083] | 0.754 | 0.460 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1023 [-0.0332, +0.2353]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0906, ΔBrier vs climatology +0.0389 [+0.0218, +0.0573], realised minus predicted +0.0262 [-0.0015, +0.0547]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.600 | 0.1907 | 0.2720 | +0.0187 [-0.0118, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0611 | 0.0159 | +0.0093 [-0.0083, +0.0254] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0066 | 0.0000 | +0.0135 [+0.0116, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0241 | 0.0200 | -0.0015 [-0.0094, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.1034 | 0.1165 | +0.0343 [+0.0031, +0.0715] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0132 | 0.0048 | +0.0074 [+0.0046, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0315 | 0.0000 | +0.0172 [+0.0085, +0.0248] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1683 | 0.2439 | 0.0203 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.588 | 0.1945 | 0.2615 | +0.0285 [+0.0001, +0.0585] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1476 | 0.1133 | +0.0195 [-0.0207, +0.0625] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.507 | 0.0453 | 0.0630 | +0.0111 [+0.0044, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0011, +0.1382] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0092, +0.0984] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.706] | 0.269 | 5.46 flat / 2.50 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.246 | 4.38 flat / 1.94 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.556] | 2.308 [1.520, 3.474] | 1.010 [0.625, 1.619] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.080, 0.318] | 1.769 [0.963, 2.905] | 0.625 [0.336, 1.045] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.265, 0.595] | 2.692 [1.610, 4.258] | 1.288 [0.708, 2.197] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.267, 0.594] | 2.808 [1.706, 4.348] | 1.125 [0.680, 1.778] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.038 [1.282, 3.150] | 0.837 [0.509, 1.360] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.824 [3.583, 9.357] | 2.206 [1.272, 3.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.382 (126 of 1873 days never flag) | 127 | 0.479 | 0.528 | 0.0551 | +0.0163 [+0.0089, +0.0244] | +0.0012 [-0.0049, +0.0074] | 0.865 | 0.444 | yes |
| 2 | 0.409 (126 of 1872 days never flag) | 88 | 0.302 | 0.477 | 0.0592 | +0.0119 [+0.0064, +0.0181] | +0.0019 [-0.0027, +0.0068] | 0.825 | 0.276 | yes |
| 3 | 0.294 (126 of 1871 days never flag) | 126 | 0.406 | 0.444 | 0.0601 | +0.0106 [+0.0051, +0.0172] | +0.0043 [-0.0014, +0.0107] | 0.825 | 0.365 | yes |
| 4 | 0.3 (126 of 1870 days never flag) | 141 | 0.493 | 0.482 | 0.0573 | +0.0135 [+0.0080, +0.0197] | +0.0050 [+0.0000, +0.0109] | 0.843 | 0.451 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 101 | 0.348 | 0.475 | 0.0578 | +0.0131 [+0.0074, +0.0190] | +0.0056 [-0.0001, +0.0113] | 0.844 | 0.317 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1286 [+0.0083, +0.2335]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0893, ΔBrier vs climatology +0.0402 [+0.0228, +0.0569], realised minus predicted -0.0103 [-0.0410, +0.0204]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.576 | 0.2415 | 0.2720 | +0.0275 [-0.0047, +0.0596] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1471 | 0.0159 | +0.0054 [-0.0058, +0.0168] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0115, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0336 | 0.0200 | +0.0007 [-0.0050, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1128 | 0.1165 | +0.0352 [+0.0057, +0.0727] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0223 | 0.0048 | +0.0082 [+0.0063, +0.0100] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0884 | 0.0000 | +0.0116 [+0.0025, +0.0196] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1734 | 0.2439 | 0.0226 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.580 | 0.2508 | 0.2615 | +0.0363 [+0.0083, +0.0660] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1501 | 0.1133 | +0.0153 [-0.0248, +0.0562] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.506 | 0.0790 | 0.0630 | +0.0133 [+0.0068, +0.0204] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0019, +0.1378] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0096, +0.1022] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2483 | 0.2213 |

## risk_quantile_skewt_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.739] | 0.269 | 5.00 flat / 2.24 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.323, 0.667] | 0.231 | 3.96 flat / 1.72 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.562] | 2.385 [1.533, 3.611] | 0.942 [0.571, 1.516] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.346 [0.800, 2.137] | 0.500 [0.286, 0.823] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 2.654 [1.667, 4.062] | 1.115 [0.695, 1.724] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.038 [1.276, 3.143] | 0.865 [0.520, 1.400] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.538] | 2.385 [1.435, 3.704] | 1.038 [0.628, 1.658] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 4.824 [2.869, 7.714] | 1.706 [1.000, 2.806] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.333 (no interval) | 3.250 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 134 | 0.514 | 0.537 | 0.0540 | +0.0174 [+0.0090, +0.0264] | +0.0023 [-0.0042, +0.0089] | 0.900 | 0.479 | yes |
| 2 | 0.409 (126 of 1872 days never flag) | 70 | 0.252 | 0.500 | 0.0592 | +0.0118 [+0.0058, +0.0186] | +0.0018 [-0.0027, +0.0067] | 0.880 | 0.232 | yes |
| 3 | 0.47 (126 of 1871 days never flag) | 126 | 0.413 | 0.452 | 0.0598 | +0.0109 [+0.0049, +0.0171] | +0.0045 [-0.0009, +0.0102] | 0.875 | 0.373 | yes |
| 4 | 0.407 (126 of 1870 days never flag) | 108 | 0.399 | 0.509 | 0.0577 | +0.0132 [+0.0069, +0.0197] | +0.0047 [-0.0009, +0.0101] | 0.878 | 0.368 | yes |
| 5 | 0.465 (126 of 1869 days never flag) | 111 | 0.355 | 0.441 | 0.0587 | +0.0122 [+0.0063, +0.0184] | +0.0046 [-0.0007, +0.0105] | 0.874 | 0.319 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.512, difference +0.1248 [+0.0105, +0.2321]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0427 [+0.0244, +0.0614], realised minus predicted +0.0051 [-0.0239, +0.0351]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.580 | 0.2604 | 0.2720 | +0.0343 [-0.0011, +0.0666] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1559 | 0.0159 | +0.0002 [-0.0144, +0.0143] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0070 | 0.0000 | +0.0134 [+0.0117, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0117 | 0.0200 | +0.0014 [-0.0049, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1119 | 0.1165 | +0.0376 [+0.0057, +0.0784] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0055 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0936 | 0.0000 | +0.0109 [+0.0026, +0.0188] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1994 | 0.2439 | 0.0225 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.579 | 0.2710 | 0.2615 | +0.0401 [+0.0090, +0.0728] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1511 | 0.1133 | +0.0190 [-0.0252, +0.0599] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.516 | 0.0757 | 0.0630 | +0.0143 [+0.0069, +0.0223] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0002, +0.1350] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0102, +0.0997] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.375, 0.722] | 0.269 | 4.69 flat / 2.23 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.231 | 3.69 flat / 1.73 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.227, 0.543] | 2.077 [1.359, 3.200] | 1.000 [0.577, 1.688] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.419] | 1.462 [0.916, 2.280] | 0.558 [0.326, 0.914] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 2.500 [1.538, 3.889] | 1.173 [0.693, 1.932] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.207, 0.500] | 1.462 [0.965, 2.250] | 0.712 [0.407, 1.236] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.962 [1.171, 3.200] | 0.875 [0.493, 1.465] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.353 [2.533, 7.134] | 1.500 [0.875, 2.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 5.333 [2.917, 11.802] | 3.611 [1.725, 8.716] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.382 (126 of 1873 days never flag) | 120 | 0.471 | 0.550 | 0.0554 | +0.0160 [+0.0095, +0.0226] | +0.0009 [-0.0056, +0.0073] | 0.879 | 0.440 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 75 | 0.266 | 0.493 | 0.0604 | +0.0107 [+0.0052, +0.0161] | +0.0007 [-0.0047, +0.0057] | 0.848 | 0.244 | no |
| 3 | 0.294 (126 of 1871 days never flag) | 115 | 0.362 | 0.435 | 0.0609 | +0.0097 [+0.0044, +0.0153] | +0.0034 [-0.0023, +0.0090] | 0.833 | 0.325 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 72 | 0.246 | 0.472 | 0.0590 | +0.0118 [+0.0065, +0.0173] | +0.0034 [-0.0020, +0.0087] | 0.844 | 0.224 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 89 | 0.275 | 0.427 | 0.0593 | +0.0116 [+0.0061, +0.0172] | +0.0041 [-0.0017, +0.0098] | 0.840 | 0.246 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.631 (climatology 0.512, difference +0.1192 [+0.0054, +0.2273]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0930, ΔBrier vs climatology +0.0365 [+0.0212, +0.0518], realised minus predicted +0.0189 [-0.0120, +0.0500]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.624 | 0.1897 | 0.2720 | +0.0198 [-0.0072, +0.0437] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.1048 | 0.0159 | +0.0135 [+0.0019, +0.0245] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0121 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0267 | 0.0200 | +0.0008 [-0.0057, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0903 | 0.1165 | +0.0357 [+0.0066, +0.0714] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0163 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0620 | 0.0000 | +0.0157 [+0.0063, +0.0235] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1391 | 0.2439 | 0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.512 | 0.610 | 0.1958 | 0.2615 | +0.0333 [+0.0089, +0.0576] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1484 | 0.1133 | +0.0167 [-0.0255, +0.0558] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.548 | 0.0528 | 0.0630 | +0.0129 [+0.0080, +0.0179] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1362] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0086, +0.1013] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2171 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.667] | 0.231 | 3.85 flat / 1.47 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.231 | 3.23 flat / 1.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.115 [1.208, 3.450] | 0.798 [0.458, 1.310] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.227] | 1.346 [0.727, 2.188] | 0.510 [0.278, 0.833] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 3.077 [1.720, 5.000] | 1.106 [0.608, 1.804] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.154 [1.028, 3.778] | 0.721 [0.337, 1.292] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.419] | 1.962 [0.933, 3.438] | 0.635 [0.300, 1.114] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 4.882 [2.833, 8.000] | 1.618 [0.916, 2.654] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.889 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 112 | 0.407 | 0.509 | 0.0677 | +0.0037 [-0.0070, +0.0141] | -0.0114 [-0.0211, -0.0021] | 0.862 | 0.375 | yes |
| 2 | 0.652 (126 of 1872 days never flag) | 68 | 0.237 | 0.485 | 0.0717 | -0.0006 [-0.0105, +0.0085] | -0.0106 [-0.0193, -0.0023] | 0.823 | 0.217 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 143 | 0.457 | 0.441 | 0.0738 | -0.0031 [-0.0141, +0.0060] | -0.0094 [-0.0201, -0.0008] | 0.812 | 0.410 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 111 | 0.399 | 0.495 | 0.0700 | +0.0009 [-0.0077, +0.0092] | -0.0076 [-0.0158, +0.0007] | 0.829 | 0.366 | no |
| 5 | 0.7 (126 of 1869 days never flag) | 100 | 0.355 | 0.490 | 0.0697 | +0.0012 [-0.0066, +0.0084] | -0.0063 [-0.0142, +0.0007] | 0.811 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.512, difference +0.1061 [+0.0031, +0.2035]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0155, +0.0527], realised minus predicted -0.0269 [-0.0589, +0.0055]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.516 | 0.3348 | 0.2720 | -0.0100 [-0.0551, +0.0358] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2307 | 0.0159 | -0.0271 [-0.0463, -0.0094] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0184 | 0.0000 | +0.0119 [+0.0105, +0.0133] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0160 | 0.0200 | +0.0003 [-0.0063, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0820 | 0.1165 | +0.0344 [+0.0052, +0.0718] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0118 | 0.0048 | +0.0078 [+0.0055, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1381 | 0.0000 | -0.0024 [-0.0130, +0.0074] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1557 | 0.2439 | 0.0113 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.538 | 0.3342 | 0.2615 | -0.0018 [-0.0415, +0.0393] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1545 | 0.1133 | +0.0163 [-0.0259, +0.0584] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.462 | 0.1059 | 0.0630 | -0.0015 [-0.0118, +0.0085] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3214 | 0.2903 | +0.0712 [+0.0005, +0.1352] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0098, +0.0993] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.680] | 0.231 | 3.81 flat / 1.45 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.176, 0.533] | 0.231 | 2.88 flat / 1.10 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.148, 0.471] | 2.077 [1.047, 3.522] | 0.808 [0.430, 1.359] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.105, 0.364] | 2.308 [1.303, 3.759] | 0.798 [0.444, 1.308] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.077, 0.387] | 1.923 [0.885, 3.296] | 0.673 [0.304, 1.152] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.062, 0.348] | 2.308 [1.133, 3.934] | 0.846 [0.420, 1.438] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 1.423 [0.609, 2.650] | 0.529 [0.229, 0.989] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 4.882 [3.000, 7.786] | 1.647 [1.000, 2.611] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 1.778 [0.786, 4.000] | 1.083 [0.389, 2.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 118 | 0.457 | 0.542 | 0.0644 | +0.0070 [-0.0030, +0.0175] | -0.0081 [-0.0171, +0.0005] | 0.860 | 0.426 | yes |
| 2 | 0.626 (126 of 1872 days never flag) | 114 | 0.388 | 0.474 | 0.0699 | +0.0012 [-0.0088, +0.0103] | -0.0088 [-0.0183, -0.0003] | 0.830 | 0.354 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 96 | 0.333 | 0.479 | 0.0732 | -0.0025 [-0.0130, +0.0071] | -0.0088 [-0.0190, +0.0002] | 0.806 | 0.304 | no |
| 4 | 0.703 (126 of 1870 days never flag) | 110 | 0.362 | 0.455 | 0.0732 | -0.0023 [-0.0113, +0.0067] | -0.0108 [-0.0194, -0.0017] | 0.821 | 0.328 | yes |
| 5 | 0.63 (126 of 1869 days never flag) | 72 | 0.254 | 0.486 | 0.0743 | -0.0034 [-0.0115, +0.0047] | -0.0109 [-0.0191, -0.0028] | 0.809 | 0.232 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.512, difference +0.1039 [+0.0245, +0.1829]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0981, ΔBrier vs climatology +0.0314 [+0.0137, +0.0504], realised minus predicted -0.0289 [-0.0613, +0.0043]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.529 | 0.540 | 0.3200 | 0.2720 | +0.0012 [-0.0435, +0.0435] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2229 | 0.0159 | -0.0200 [-0.0404, -0.0017] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0155 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0814 | 0.1165 | +0.0345 [+0.0051, +0.0705] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0117 | 0.0048 | +0.0079 [+0.0058, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1314 | 0.0000 | +0.0030 [-0.0051, +0.0107] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1475 | 0.2439 | 0.0271 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.504 | 0.558 | 0.3230 | 0.2615 | +0.0059 [-0.0336, +0.0464] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1365 | 0.1133 | +0.0304 [-0.0017, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.488 | 0.1035 | 0.0630 | +0.0001 [-0.0101, +0.0102] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0303, +0.1580] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0163, +0.1065] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.231 | 3.81 flat / 1.55 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 2.73 flat / 1.17 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.433] | 2.115 [1.207, 3.429] | 0.798 [0.444, 1.330] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.423 [1.333, 3.934] | 1.058 [0.592, 1.732] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.531] | 1.538 [0.828, 2.500] | 0.779 [0.414, 1.322] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 2.000 [0.917, 3.563] | 0.788 [0.390, 1.381] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.143, 0.414] | 1.346 [0.548, 2.500] | 0.577 [0.261, 1.025] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.481, 0.923] | 4.765 [2.792, 7.770] | 1.676 [0.973, 2.717] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.000 (no interval) | 1.306 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 112 | 0.407 | 0.509 | 0.0677 | +0.0037 [-0.0072, +0.0144] | -0.0114 [-0.0210, -0.0021] | 0.862 | 0.375 | yes |
| 2 | 0.729 (126 of 1872 days never flag) | 126 | 0.453 | 0.500 | 0.0659 | +0.0052 [-0.0049, +0.0150] | -0.0048 [-0.0150, +0.0047] | 0.844 | 0.417 | yes |
| 3 | 0.667 (126 of 1871 days never flag) | 80 | 0.290 | 0.500 | 0.0703 | +0.0004 [-0.0105, +0.0101] | -0.0059 [-0.0171, +0.0039] | 0.820 | 0.267 | yes |
| 4 | 0.701 (126 of 1870 days never flag) | 109 | 0.413 | 0.523 | 0.0653 | +0.0055 [-0.0035, +0.0146] | -0.0030 [-0.0122, +0.0059] | 0.844 | 0.383 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 72 | 0.268 | 0.514 | 0.0694 | +0.0016 [-0.0079, +0.0112] | -0.0060 [-0.0152, +0.0032] | 0.837 | 0.248 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1289 [-0.0295, +0.3063]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0943, ΔBrier vs climatology +0.0352 [+0.0134, +0.0597], realised minus predicted -0.0509 [-0.0820, -0.0191]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.516 | 0.3348 | 0.2720 | -0.0100 [-0.0553, +0.0370] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2307 | 0.0159 | -0.0271 [-0.0472, -0.0088] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0184 | 0.0000 | +0.0119 [+0.0104, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0160 | 0.0200 | +0.0003 [-0.0061, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0820 | 0.1165 | +0.0344 [+0.0052, +0.0733] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0118 | 0.0048 | +0.0078 [+0.0057, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1381 | 0.0000 | -0.0024 [-0.0138, +0.0073] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1557 | 0.2439 | 0.0113 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.538 | 0.3342 | 0.2615 | -0.0018 [-0.0419, +0.0403] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1545 | 0.1133 | +0.0163 [-0.0234, +0.0572] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.462 | 0.1059 | 0.0630 | -0.0015 [-0.0117, +0.0086] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3214 | 0.2903 | +0.0712 [+0.0010, +0.1361] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0103, +0.0964] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.708] | 0.231 | 3.62 flat / 1.45 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.649] | 0.231 | 3.19 flat / 1.34 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 2.077 [1.033, 3.429] | 0.808 [0.419, 1.317] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.227, 0.545] | 2.269 [1.160, 3.722] | 0.904 [0.492, 1.441] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.517] | 2.423 [1.281, 3.826] | 1.019 [0.583, 1.594] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.115, 0.417] | 1.731 [0.682, 3.091] | 0.683 [0.306, 1.180] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.318] | 1.808 [0.815, 3.150] | 0.779 [0.359, 1.346] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.920] | 4.529 [2.450, 7.546] | 1.588 [0.897, 2.641] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.889 [0.850, 4.200] | 1.194 [0.417, 3.051] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 118 | 0.457 | 0.542 | 0.0644 | +0.0070 [-0.0026, +0.0165] | -0.0081 [-0.0164, -0.0000] | 0.860 | 0.426 | yes |
| 2 | 0.591 (126 of 1872 days never flag) | 123 | 0.460 | 0.520 | 0.0660 | +0.0050 [-0.0049, +0.0145] | -0.0050 [-0.0143, +0.0042] | 0.842 | 0.426 | yes |
| 3 | 0.604 (126 of 1871 days never flag) | 118 | 0.399 | 0.466 | 0.0693 | +0.0014 [-0.0092, +0.0115] | -0.0050 [-0.0154, +0.0052] | 0.828 | 0.362 | yes |
| 4 | 0.757 (126 of 1870 days never flag) | 101 | 0.406 | 0.554 | 0.0660 | +0.0048 [-0.0042, +0.0136] | -0.0036 [-0.0123, +0.0054] | 0.845 | 0.380 | yes |
| 5 | 0.663 (126 of 1869 days never flag) | 96 | 0.355 | 0.510 | 0.0686 | +0.0023 [-0.0058, +0.0105] | -0.0052 [-0.0139, +0.0030] | 0.821 | 0.328 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.682 (climatology 0.512, difference +0.1696 [+0.0447, +0.3185]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0910, ΔBrier vs climatology +0.0385 [+0.0168, +0.0610], realised minus predicted -0.0458 [-0.0762, -0.0162]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.529 | 0.540 | 0.3200 | 0.2720 | +0.0012 [-0.0405, +0.0420] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2229 | 0.0159 | -0.0200 [-0.0414, -0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0155 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0814 | 0.1165 | +0.0345 [+0.0052, +0.0721] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0117 | 0.0048 | +0.0079 [+0.0057, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1314 | 0.0000 | +0.0030 [-0.0055, +0.0103] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1475 | 0.2439 | 0.0271 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.504 | 0.558 | 0.3230 | 0.2615 | +0.0059 [-0.0306, +0.0429] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1365 | 0.1133 | +0.0304 [-0.0015, +0.0625] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.488 | 0.1035 | 0.0630 | +0.0001 [-0.0097, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0221, +0.1551] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0176, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.682] | 0.269 | 5.08 flat / 2.23 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.647] | 0.254 | 4.46 flat / 1.97 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.423 [1.370, 3.762] | 0.885 [0.510, 1.393] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.045, 0.278] | 1.346 [0.735, 2.258] | 0.538 [0.293, 0.905] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 2.615 [1.412, 4.200] | 1.010 [0.558, 1.625] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.654 [1.500, 4.333] | 1.087 [0.612, 1.803] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.562] | 3.154 [1.690, 5.238] | 1.500 [0.758, 2.667] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 6.059 [3.545, 10.000] | 2.382 [1.278, 4.282] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.300] | 3.222 [1.727, 7.000] | 1.944 [0.944, 4.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 130 | 0.479 | 0.515 | 0.0631 | +0.0083 [-0.0002, +0.0176] | -0.0068 [-0.0144, +0.0005] | 0.832 | 0.442 | yes |
| 2 | 0.652 (126 of 1872 days never flag) | 64 | 0.209 | 0.453 | 0.0698 | +0.0013 [-0.0057, +0.0078] | -0.0087 [-0.0150, -0.0026] | 0.780 | 0.188 | yes |
| 3 | 0.567 (126 of 1871 days never flag) | 122 | 0.391 | 0.443 | 0.0711 | -0.0004 [-0.0067, +0.0060] | -0.0067 [-0.0131, +0.0001] | 0.750 | 0.352 | no |
| 4 | 0.513 (126 of 1870 days never flag) | 127 | 0.420 | 0.457 | 0.0689 | +0.0019 [-0.0045, +0.0087] | -0.0066 [-0.0129, +0.0002] | 0.775 | 0.380 | no |
| 5 | 0.498 (126 of 1869 days never flag) | 134 | 0.377 | 0.388 | 0.0697 | +0.0012 [-0.0057, +0.0079] | -0.0063 [-0.0135, +0.0008] | 0.764 | 0.329 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.512, difference +0.1061 [+0.0022, +0.2035]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0980, ΔBrier vs climatology +0.0315 [+0.0130, +0.0495], realised minus predicted -0.0433 [-0.0765, -0.0106]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.514 | 0.3059 | 0.2720 | +0.0161 [-0.0193, +0.0531] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2388 | 0.0159 | -0.0251 [-0.0390, -0.0110] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0384 | 0.0000 | +0.0102 [+0.0086, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0205 | 0.0200 | +0.0003 [-0.0059, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0807 | 0.1165 | +0.0323 [+0.0068, +0.0663] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0252 | 0.0048 | +0.0074 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1577 | 0.0000 | -0.0082 [-0.0188, +0.0012] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1329 | 0.2439 | -0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.537 | 0.3087 | 0.2615 | +0.0225 [-0.0087, +0.0583] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1552 | 0.1133 | +0.0155 [-0.0248, +0.0562] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.474 | 0.1102 | 0.0630 | +0.0039 [-0.0037, +0.0121] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0005, +0.1381] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0074, +0.0991] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.269 | 5.42 flat / 2.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.613] | 0.231 | 3.96 flat / 1.79 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 2.538 [1.461, 3.952] | 0.962 [0.550, 1.512] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.105, 0.360] | 2.192 [1.375, 3.263] | 0.865 [0.509, 1.355] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.108, 0.444] | 1.808 [0.931, 3.101] | 0.808 [0.414, 1.385] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.115 [1.861, 4.842] | 1.394 [0.821, 2.221] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.423 [0.806, 2.305] | 0.740 [0.403, 1.250] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.235 [4.000, 9.701] | 2.324 [1.438, 3.627] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 3.889 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 138 | 0.514 | 0.522 | 0.0599 | +0.0115 [+0.0032, +0.0198] | -0.0036 [-0.0101, +0.0030] | 0.829 | 0.476 | yes |
| 2 | 0.551 (126 of 1872 days never flag) | 105 | 0.345 | 0.457 | 0.0680 | +0.0031 [-0.0038, +0.0098] | -0.0069 [-0.0135, +0.0003] | 0.790 | 0.312 | no |
| 3 | 0.504 (126 of 1871 days never flag) | 89 | 0.304 | 0.472 | 0.0705 | +0.0002 [-0.0070, +0.0069] | -0.0062 [-0.0136, +0.0011] | 0.743 | 0.277 | no |
| 4 | 0.513 (126 of 1870 days never flag) | 136 | 0.399 | 0.404 | 0.0721 | -0.0013 [-0.0085, +0.0052] | -0.0097 [-0.0172, -0.0027] | 0.765 | 0.352 | no |
| 5 | 0.517 (126 of 1869 days never flag) | 73 | 0.261 | 0.493 | 0.0744 | -0.0034 [-0.0110, +0.0037] | -0.0110 [-0.0188, -0.0034] | 0.760 | 0.239 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1026 [+0.0223, +0.1873]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1007, ΔBrier vs climatology +0.0288 [+0.0111, +0.0476], realised minus predicted -0.0454 [-0.0756, -0.0110]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.517 | 0.2910 | 0.2720 | +0.0272 [-0.0050, +0.0612] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2310 | 0.0159 | -0.0180 [-0.0316, -0.0051] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0201 | 0.0200 | +0.0007 [-0.0057, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0801 | 0.1165 | +0.0324 [+0.0057, +0.0639] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0251 | 0.0048 | +0.0074 [+0.0055, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1510 | 0.0000 | -0.0028 [-0.0104, +0.0044] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1246 | 0.2439 | 0.0060 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.534 | 0.2976 | 0.2615 | +0.0302 [-0.0017, +0.0627] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1372 | 0.1133 | +0.0296 [-0.0022, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.1077 | 0.0630 | +0.0055 [-0.0025, +0.0131] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0261, +0.1579] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0192, +0.1066] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.269 | 4.62 flat / 1.96 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.303, 0.625] | 0.231 | 3.12 flat / 1.33 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 2.423 [1.414, 4.000] | 0.885 [0.519, 1.462] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 3.308 [2.026, 5.251] | 1.510 [0.896, 2.429] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 1.269 [0.679, 2.050] | 0.644 [0.333, 1.080] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.267, 0.577] | 2.077 [1.118, 3.450] | 0.913 [0.528, 1.512] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.414] | 1.923 [0.857, 3.419] | 0.760 [0.365, 1.313] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.412 [3.321, 8.883] | 2.074 [1.218, 3.521] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 130 | 0.479 | 0.515 | 0.0631 | +0.0083 [-0.0001, +0.0170] | -0.0068 [-0.0144, +0.0007] | 0.832 | 0.442 | yes |
| 2 | 0.543 (126 of 1872 days never flag) | 158 | 0.518 | 0.456 | 0.0632 | +0.0078 [+0.0006, +0.0160] | -0.0022 [-0.0095, +0.0061] | 0.815 | 0.468 | yes |
| 3 | 0.667 (126 of 1871 days never flag) | 75 | 0.304 | 0.560 | 0.0671 | +0.0036 [-0.0044, +0.0114] | -0.0027 [-0.0113, +0.0055] | 0.768 | 0.285 | no |
| 4 | 0.497 (126 of 1870 days never flag) | 110 | 0.406 | 0.509 | 0.0639 | +0.0069 [-0.0003, +0.0144] | -0.0016 [-0.0090, +0.0063] | 0.797 | 0.375 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 99 | 0.355 | 0.495 | 0.0691 | +0.0018 [-0.0071, +0.0103] | -0.0057 [-0.0147, +0.0031] | 0.798 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.643 (climatology 0.512, difference +0.1308 [-0.0403, +0.3013]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0119, +0.0573], realised minus predicted -0.0686 [-0.0998, -0.0357]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.514 | 0.3059 | 0.2720 | +0.0161 [-0.0203, +0.0557] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2388 | 0.0159 | -0.0251 [-0.0392, -0.0111] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0384 | 0.0000 | +0.0102 [+0.0087, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0205 | 0.0200 | +0.0003 [-0.0060, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0807 | 0.1165 | +0.0323 [+0.0053, +0.0657] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0252 | 0.0048 | +0.0074 [+0.0054, +0.0092] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1577 | 0.0000 | -0.0082 [-0.0189, +0.0016] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1329 | 0.2439 | -0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.537 | 0.3087 | 0.2615 | +0.0225 [-0.0092, +0.0577] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1552 | 0.1133 | +0.0155 [-0.0251, +0.0532] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.474 | 0.1102 | 0.0630 | +0.0039 [-0.0036, +0.0122] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0039, +0.1379] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0111, +0.0986] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.793] | 0.254 | 4.42 flat / 1.88 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.389, 0.765] | 0.231 | 3.65 flat / 1.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.478] | 2.538 [1.441, 4.080] | 0.962 [0.552, 1.544] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 2.654 [1.526, 4.143] | 1.144 [0.677, 1.810] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.292, 0.630] | 2.577 [1.439, 4.111] | 1.115 [0.658, 1.767] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.188, 0.519] | 2.385 [1.160, 4.091] | 0.923 [0.479, 1.554] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.189, 0.517] | 1.577 [0.800, 2.789] | 0.788 [0.410, 1.421] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.176 [3.000, 8.572] | 1.941 [1.104, 3.273] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.000 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 138 | 0.514 | 0.522 | 0.0599 | +0.0115 [+0.0039, +0.0198] | -0.0036 [-0.0098, +0.0029] | 0.829 | 0.476 | yes |
| 2 | 0.571 (126 of 1872 days never flag) | 133 | 0.460 | 0.481 | 0.0634 | +0.0077 [+0.0003, +0.0152] | -0.0023 [-0.0095, +0.0055] | 0.813 | 0.421 | yes |
| 3 | 0.604 (126 of 1871 days never flag) | 125 | 0.420 | 0.464 | 0.0661 | +0.0046 [-0.0026, +0.0119] | -0.0018 [-0.0093, +0.0063] | 0.777 | 0.382 | no |
| 4 | 0.659 (126 of 1870 days never flag) | 127 | 0.471 | 0.512 | 0.0646 | +0.0062 [-0.0014, +0.0139] | -0.0022 [-0.0102, +0.0058] | 0.797 | 0.435 | yes |
| 5 | 0.527 (126 of 1869 days never flag) | 93 | 0.377 | 0.559 | 0.0683 | +0.0026 [-0.0053, +0.0109] | -0.0049 [-0.0133, +0.0038] | 0.781 | 0.353 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.684 (climatology 0.512, difference +0.1715 [+0.0411, +0.3196]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0922, ΔBrier vs climatology +0.0373 [+0.0163, +0.0596], realised minus predicted -0.0634 [-0.0956, -0.0313]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.517 | 0.2910 | 0.2720 | +0.0272 [-0.0041, +0.0590] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2310 | 0.0159 | -0.0180 [-0.0321, -0.0043] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0118] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0201 | 0.0200 | +0.0007 [-0.0054, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0801 | 0.1165 | +0.0324 [+0.0055, +0.0642] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0251 | 0.0048 | +0.0074 [+0.0056, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1510 | 0.0000 | -0.0028 [-0.0102, +0.0040] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1246 | 0.2439 | 0.0060 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.534 | 0.2976 | 0.2615 | +0.0302 [-0.0001, +0.0615] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1372 | 0.1133 | +0.0296 [-0.0031, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.1077 | 0.0630 | +0.0055 [-0.0015, +0.0138] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0252, +0.1564] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0173, +0.1059] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.643] | 0.231 | 3.85 flat / 1.47 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.235, 0.600] | 0.231 | 3.35 flat / 1.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.121, 0.429] | 1.962 [1.029, 3.267] | 0.750 [0.402, 1.262] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.280] | 1.346 [0.679, 2.261] | 0.510 [0.259, 0.845] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 2.615 [1.353, 4.296] | 0.952 [0.490, 1.579] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.308 [1.167, 3.875] | 0.846 [0.419, 1.413] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 2.615 [1.333, 4.250] | 0.875 [0.440, 1.429] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 5.059 [2.909, 8.150] | 1.676 [0.944, 2.750] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.556 [0.667, 3.603] | 1.083 [0.417, 2.786] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0633 | +0.0081 [-0.0028, +0.0182] | -0.0070 [-0.0167, +0.0018] | 0.904 | 0.399 | yes |
| 2 | 0.652 (126 of 1872 days never flag) | 72 | 0.266 | 0.514 | 0.0664 | +0.0046 [-0.0049, +0.0141] | -0.0054 [-0.0140, +0.0030] | 0.881 | 0.246 | yes |
| 3 | 0.659 (126 of 1871 days never flag) | 124 | 0.406 | 0.452 | 0.0673 | +0.0034 [-0.0073, +0.0130] | -0.0029 [-0.0141, +0.0062] | 0.897 | 0.367 | no |
| 4 | 0.664 (126 of 1870 days never flag) | 113 | 0.384 | 0.469 | 0.0653 | +0.0055 [-0.0032, +0.0136] | -0.0029 [-0.0117, +0.0051] | 0.860 | 0.349 | no |
| 5 | 0.7 (126 of 1869 days never flag) | 134 | 0.478 | 0.493 | 0.0697 | +0.0013 [-0.0087, +0.0100] | -0.0063 [-0.0159, +0.0022] | 0.846 | 0.439 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.632 (climatology 0.512, difference +0.1195 [+0.0148, +0.2186]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0903, ΔBrier vs climatology +0.0392 [+0.0214, +0.0585], realised minus predicted -0.0114 [-0.0430, +0.0192]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.3357 | 0.2720 | -0.0061 [-0.0513, +0.0369] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1225 | 0.0159 | -0.0057 [-0.0299, +0.0142] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0014 [-0.0045, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0910 | 0.1165 | +0.0335 [+0.0066, +0.0689] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0314 | 0.0000 | +0.0173 [+0.0083, +0.0248] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1042 | 0.2439 | 0.0021 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.472 | 0.567 | 0.3425 | 0.2615 | +0.0011 [-0.0391, +0.0416] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1509 | 0.1133 | +0.0170 [-0.0236, +0.0575] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.494 | 0.0830 | 0.0630 | +0.0036 [-0.0067, +0.0134] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1339] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0085, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2810 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.679] | 0.231 | 4.15 flat / 1.65 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.200, 0.588] | 0.231 | 3.38 flat / 1.32 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.467] | 2.077 [1.040, 3.522] | 0.808 [0.428, 1.353] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.478] | 2.192 [1.182, 3.478] | 0.788 [0.426, 1.261] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.086, 0.400] | 1.923 [0.857, 3.353] | 0.663 [0.284, 1.164] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.120, 0.440] | 2.692 [1.385, 4.429] | 0.981 [0.519, 1.603] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.389] | 1.577 [0.759, 2.714] | 0.615 [0.295, 1.042] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 5.471 [3.439, 8.572] | 1.926 [1.200, 3.039] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 1.667 [0.714, 3.600] | 1.139 [0.389, 2.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 119 | 0.464 | 0.546 | 0.0605 | +0.0109 [+0.0012, +0.0208] | -0.0041 [-0.0126, +0.0040] | 0.904 | 0.433 | yes |
| 2 | 0.625 (126 of 1872 days never flag) | 113 | 0.403 | 0.496 | 0.0648 | +0.0063 [-0.0036, +0.0153] | -0.0037 [-0.0132, +0.0049] | 0.888 | 0.370 | yes |
| 3 | 0.685 (126 of 1871 days never flag) | 98 | 0.348 | 0.490 | 0.0667 | +0.0040 [-0.0082, +0.0143] | -0.0023 [-0.0141, +0.0076] | 0.894 | 0.319 | no |
| 4 | 0.7 (126 of 1870 days never flag) | 127 | 0.413 | 0.449 | 0.0658 | +0.0050 [-0.0032, +0.0129] | -0.0034 [-0.0115, +0.0045] | 0.881 | 0.373 | no |
| 5 | 0.574 (126 of 1869 days never flag) | 84 | 0.312 | 0.512 | 0.0686 | +0.0023 [-0.0058, +0.0103] | -0.0052 [-0.0131, +0.0029] | 0.843 | 0.288 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.612 (climatology 0.512, difference +0.1001 [+0.0216, +0.1839]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0930, ΔBrier vs climatology +0.0364 [+0.0186, +0.0551], realised minus predicted -0.0134 [-0.0435, +0.0190]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.545 | 0.3215 | 0.2720 | +0.0032 [-0.0371, +0.0429] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1153 | 0.0159 | +0.0010 [-0.0252, +0.0228] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0120 | 0.0200 | +0.0018 [-0.0039, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0905 | 0.1165 | +0.0338 [+0.0072, +0.0668] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0063 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0247 | 0.0000 | +0.0226 [+0.0162, +0.0282] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0959 | 0.2439 | 0.0179 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.512 | 0.561 | 0.3322 | 0.2615 | +0.0073 [-0.0289, +0.0459] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1331 | 0.1133 | +0.0314 [+0.0002, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.494 | 0.0809 | 0.0630 | +0.0047 [-0.0051, +0.0140] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0272, +0.1583] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0190, +0.1068] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.316, 0.667] | 0.231 | 3.65 flat / 1.50 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.550] | 0.231 | 2.69 flat / 1.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.962 [1.031, 3.303] | 0.750 [0.395, 1.294] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.423 [1.300, 3.960] | 1.058 [0.589, 1.765] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.478] | 1.654 [0.774, 2.833] | 0.769 [0.375, 1.348] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.552] | 2.308 [1.115, 3.905] | 0.904 [0.468, 1.481] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.417] | 1.346 [0.545, 2.546] | 0.577 [0.259, 1.024] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.706 [2.625, 7.846] | 1.662 [0.941, 2.804] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0633 | +0.0081 [-0.0025, +0.0186] | -0.0070 [-0.0160, +0.0019] | 0.904 | 0.399 | yes |
| 2 | 0.613 (126 of 1872 days never flag) | 129 | 0.475 | 0.512 | 0.0613 | +0.0098 [-0.0000, +0.0195] | -0.0002 [-0.0102, +0.0093] | 0.892 | 0.438 | yes |
| 3 | 0.667 (126 of 1871 days never flag) | 87 | 0.319 | 0.506 | 0.0647 | +0.0060 [-0.0053, +0.0160] | -0.0003 [-0.0114, +0.0096] | 0.891 | 0.294 | yes |
| 4 | 0.701 (126 of 1870 days never flag) | 123 | 0.457 | 0.512 | 0.0613 | +0.0095 [+0.0004, +0.0179] | +0.0011 [-0.0082, +0.0098] | 0.867 | 0.422 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 72 | 0.268 | 0.514 | 0.0699 | +0.0010 [-0.0103, +0.0114] | -0.0065 [-0.0176, +0.0034] | 0.862 | 0.248 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1289 [-0.0351, +0.3087]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0901, ΔBrier vs climatology +0.0393 [+0.0161, +0.0630], realised minus predicted -0.0354 [-0.0658, -0.0056]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.3357 | 0.2720 | -0.0061 [-0.0496, +0.0402] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1225 | 0.0159 | -0.0057 [-0.0294, +0.0155] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0014 [-0.0046, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0910 | 0.1165 | +0.0335 [+0.0058, +0.0684] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0314 | 0.0000 | +0.0173 [+0.0088, +0.0251] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1042 | 0.2439 | 0.0021 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.472 | 0.567 | 0.3425 | 0.2615 | +0.0011 [-0.0395, +0.0421] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1509 | 0.1133 | +0.0170 [-0.0234, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.494 | 0.0830 | 0.0630 | +0.0036 [-0.0067, +0.0135] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1381] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0086, +0.0978] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2810 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.231 | 4.12 flat / 1.68 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.391, 0.767] | 0.231 | 3.65 flat / 1.55 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 2.077 [1.042, 3.448] | 0.808 [0.419, 1.317] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.593] | 2.346 [1.222, 3.833] | 0.923 [0.508, 1.490] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.121, 0.444] | 2.115 [1.136, 3.545] | 0.875 [0.509, 1.417] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.520] | 2.192 [1.077, 3.778] | 0.875 [0.460, 1.473] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.556] | 2.192 [1.083, 3.728] | 1.010 [0.516, 1.719] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.176 [3.000, 8.365] | 1.882 [1.083, 3.040] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.111 (no interval) | 1.306 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 119 | 0.464 | 0.546 | 0.0605 | +0.0109 [+0.0007, +0.0206] | -0.0041 [-0.0132, +0.0037] | 0.904 | 0.433 | yes |
| 2 | 0.591 (126 of 1872 days never flag) | 129 | 0.489 | 0.527 | 0.0616 | +0.0095 [-0.0004, +0.0187] | -0.0005 [-0.0099, +0.0088] | 0.891 | 0.454 | yes |
| 3 | 0.747 (126 of 1871 days never flag) | 108 | 0.384 | 0.491 | 0.0638 | +0.0068 [-0.0044, +0.0176] | +0.0005 [-0.0104, +0.0109] | 0.899 | 0.352 | no |
| 4 | 0.659 (126 of 1870 days never flag) | 121 | 0.464 | 0.529 | 0.0595 | +0.0114 [+0.0032, +0.0199] | +0.0029 [-0.0055, +0.0117] | 0.891 | 0.431 | yes |
| 5 | 0.579 (126 of 1869 days never flag) | 114 | 0.413 | 0.500 | 0.0634 | +0.0075 [-0.0007, +0.0156] | -0.0000 [-0.0082, +0.0084] | 0.851 | 0.380 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.682 (climatology 0.512, difference +0.1702 [+0.0476, +0.3173]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0867, ΔBrier vs climatology +0.0427 [+0.0208, +0.0658], realised minus predicted -0.0294 [-0.0598, +0.0013]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.545 | 0.3215 | 0.2720 | +0.0032 [-0.0382, +0.0447] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1153 | 0.0159 | +0.0010 [-0.0244, +0.0221] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0120 | 0.0200 | +0.0018 [-0.0041, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0905 | 0.1165 | +0.0338 [+0.0065, +0.0691] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0063 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0247 | 0.0000 | +0.0226 [+0.0164, +0.0284] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0959 | 0.2439 | 0.0179 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.512 | 0.561 | 0.3322 | 0.2615 | +0.0073 [-0.0321, +0.0462] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1331 | 0.1133 | +0.0314 [-0.0009, +0.0656] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.494 | 0.0809 | 0.0630 | +0.0047 [-0.0056, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0249, +0.1560] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0188, +0.1050] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.688] | 0.269 | 4.73 flat / 2.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.285, 0.650] | 0.242 | 4.35 flat / 1.89 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.438] | 1.769 [0.962, 2.858] | 0.663 [0.366, 1.077] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.654 [0.690, 3.002] | 0.827 [0.283, 1.675] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.538 [2.000, 5.625] | 1.538 [0.812, 2.565] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.226, 0.556] | 3.038 [1.593, 5.048] | 1.433 [0.686, 2.513] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 3.692 [2.038, 5.889] | 1.529 [0.783, 2.584] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.294 [3.722, 10.184] | 2.456 [1.312, 4.322] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.778 (no interval) | 1.361 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 107 | 0.436 | 0.570 | 0.0569 | +0.0145 [+0.0061, +0.0235] | -0.0006 [-0.0078, +0.0066] | 0.880 | 0.409 | yes |
| 2 | 0.652 (126 of 1872 days never flag) | 75 | 0.230 | 0.427 | 0.0614 | +0.0096 [+0.0025, +0.0171] | -0.0004 [-0.0066, +0.0058] | 0.861 | 0.205 | yes |
| 3 | 0.47 (126 of 1871 days never flag) | 153 | 0.442 | 0.399 | 0.0613 | +0.0094 [+0.0031, +0.0157] | +0.0031 [-0.0032, +0.0094] | 0.872 | 0.389 | no |
| 4 | 0.47 (126 of 1870 days never flag) | 134 | 0.399 | 0.410 | 0.0615 | +0.0094 [+0.0027, +0.0163] | +0.0009 [-0.0057, +0.0076] | 0.844 | 0.353 | no |
| 5 | 0.597 (126 of 1869 days never flag) | 167 | 0.514 | 0.425 | 0.0661 | +0.0048 [-0.0020, +0.0115] | -0.0027 [-0.0095, +0.0043] | 0.818 | 0.459 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.626 (climatology 0.512, difference +0.1136 [+0.0104, +0.2100]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0919, ΔBrier vs climatology +0.0375 [+0.0206, +0.0557], realised minus predicted -0.0125 [-0.0435, +0.0201]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.500 | 0.586 | 0.2966 | 0.2720 | +0.0226 [-0.0131, +0.0612] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1611 | 0.0159 | -0.0022 [-0.0195, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0014 [-0.0047, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0886 | 0.1165 | +0.0358 [+0.0065, +0.0715] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0085 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0786 | 0.0000 | +0.0139 [+0.0054, +0.0215] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1326 | 0.2439 | 0.0007 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.600 | 0.3045 | 0.2615 | +0.0287 [-0.0039, +0.0622] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1523 | 0.1133 | +0.0176 [-0.0254, +0.0569] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.534 | 0.0829 | 0.0630 | +0.0110 [+0.0038, +0.0191] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [-0.0026, +0.1398] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0087, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2719 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.269 | 5.19 flat / 2.44 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.647] | 0.246 | 4.38 flat / 2.11 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.517] | 2.615 [1.462, 4.193] | 0.981 [0.559, 1.587] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 2.115 [1.108, 3.520] | 1.067 [0.479, 1.938] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.115, 0.448] | 2.500 [1.296, 4.305] | 1.231 [0.611, 2.195] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.476] | 3.077 [1.791, 4.934] | 1.385 [0.821, 2.275] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.369] | 1.462 [0.800, 2.401] | 0.788 [0.417, 1.327] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 6.588 [4.190, 10.400] | 2.662 [1.574, 4.403] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 2.556 [1.235, 6.000] | 2.028 [0.805, 5.250] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 141 | 0.521 | 0.518 | 0.0539 | +0.0175 [+0.0093, +0.0261] | +0.0024 [-0.0035, +0.0085] | 0.875 | 0.482 | yes |
| 2 | 0.551 (126 of 1872 days never flag) | 98 | 0.309 | 0.439 | 0.0598 | +0.0113 [+0.0041, +0.0179] | +0.0013 [-0.0054, +0.0078] | 0.866 | 0.278 | yes |
| 3 | 0.504 (126 of 1871 days never flag) | 113 | 0.348 | 0.425 | 0.0609 | +0.0098 [+0.0032, +0.0169] | +0.0035 [-0.0032, +0.0104] | 0.864 | 0.310 | no |
| 4 | 0.471 (126 of 1870 days never flag) | 139 | 0.428 | 0.424 | 0.0631 | +0.0077 [+0.0011, +0.0144] | -0.0007 [-0.0077, +0.0062] | 0.846 | 0.381 | no |
| 5 | 0.517 (126 of 1869 days never flag) | 73 | 0.254 | 0.479 | 0.0686 | +0.0023 [-0.0057, +0.0099] | -0.0053 [-0.0134, +0.0024] | 0.823 | 0.232 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0976 [+0.0183, +0.1842]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0939, ΔBrier vs climatology +0.0356 [+0.0183, +0.0550], realised minus predicted -0.0117 [-0.0425, +0.0217]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.512 | 0.2836 | 0.2720 | +0.0326 [+0.0009, +0.0651] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1543 | 0.0159 | +0.0047 [-0.0129, +0.0210] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0102 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0875 | 0.1165 | +0.0360 [+0.0065, +0.0723] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0084 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0736 | 0.0000 | +0.0190 [+0.0122, +0.0247] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1203 | 0.2439 | 0.0170 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.529 | 0.2945 | 0.2615 | +0.0355 [+0.0053, +0.0687] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1343 | 0.1133 | +0.0317 [-0.0013, +0.0663] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.0811 | 0.0630 | +0.0123 [+0.0050, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0243, +0.1554] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2028 | 0.1461 | +0.0603 [+0.0193, +0.1048] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2717 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.254 | 4.42 flat / 1.99 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.632] | 0.231 | 3.54 flat / 1.67 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.417] | 1.769 [0.950, 2.867] | 0.663 [0.367, 1.088] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 3.115 [1.800, 4.864] | 1.413 [0.812, 2.278] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.174, 0.519] | 2.308 [1.071, 4.000] | 1.192 [0.530, 2.190] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.261, 0.593] | 2.462 [1.278, 4.118] | 1.212 [0.597, 2.163] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.412] | 1.885 [0.833, 3.278] | 0.750 [0.355, 1.275] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.765 [3.333, 9.527] | 2.338 [1.265, 4.157] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.889 [0.818, 4.333] | 1.333 [0.432, 3.500] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 107 | 0.436 | 0.570 | 0.0569 | +0.0145 [+0.0061, +0.0237] | -0.0006 [-0.0071, +0.0064] | 0.880 | 0.409 | yes |
| 2 | 0.477 (126 of 1872 days never flag) | 149 | 0.489 | 0.456 | 0.0555 | +0.0155 [+0.0074, +0.0233] | +0.0055 [-0.0024, +0.0132] | 0.871 | 0.442 | yes |
| 3 | 0.667 (126 of 1871 days never flag) | 111 | 0.370 | 0.459 | 0.0582 | +0.0125 [+0.0046, +0.0201] | +0.0062 [-0.0020, +0.0142] | 0.859 | 0.335 | yes |
| 4 | 0.497 (126 of 1870 days never flag) | 124 | 0.435 | 0.484 | 0.0571 | +0.0137 [+0.0067, +0.0212] | +0.0053 [-0.0020, +0.0129] | 0.848 | 0.398 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 95 | 0.333 | 0.484 | 0.0659 | +0.0050 [-0.0037, +0.0140] | -0.0026 [-0.0121, +0.0065] | 0.837 | 0.305 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.643 (climatology 0.512, difference +0.1308 [-0.0350, +0.3052]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0900, ΔBrier vs climatology +0.0395 [+0.0174, +0.0626], realised minus predicted -0.0379 [-0.0693, -0.0071]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.500 | 0.586 | 0.2966 | 0.2720 | +0.0226 [-0.0129, +0.0600] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1611 | 0.0159 | -0.0022 [-0.0189, +0.0130] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0014 [-0.0044, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0886 | 0.1165 | +0.0358 [+0.0072, +0.0730] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0085 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0786 | 0.0000 | +0.0139 [+0.0052, +0.0216] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1326 | 0.2439 | 0.0007 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.600 | 0.3045 | 0.2615 | +0.0287 [-0.0026, +0.0631] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1523 | 0.1133 | +0.0176 [-0.0239, +0.0571] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.534 | 0.0829 | 0.0630 | +0.0110 [+0.0036, +0.0193] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [-0.0006, +0.1383] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0119, +0.1001] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2719 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.262 | 4.50 flat / 1.98 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.759] | 0.231 | 4.08 flat / 1.83 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.615 [1.406, 4.286] | 0.981 [0.540, 1.606] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 2.385 [1.370, 3.760] | 1.048 [0.612, 1.660] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 2.346 [1.333, 4.000] | 1.163 [0.602, 2.121] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.184, 0.517] | 2.308 [1.058, 4.054] | 0.894 [0.438, 1.529] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.235, 0.556] | 1.808 [0.875, 3.257] | 0.827 [0.417, 1.450] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.941 [3.625, 9.868] | 2.382 [1.328, 4.150] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.778 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 141 | 0.521 | 0.518 | 0.0539 | +0.0175 [+0.0101, +0.0263] | +0.0024 [-0.0035, +0.0087] | 0.875 | 0.482 | yes |
| 2 | 0.49 (126 of 1872 days never flag) | 127 | 0.468 | 0.512 | 0.0558 | +0.0152 [+0.0075, +0.0229] | +0.0052 [-0.0022, +0.0124] | 0.868 | 0.432 | yes |
| 3 | 0.604 (126 of 1871 days never flag) | 115 | 0.391 | 0.470 | 0.0574 | +0.0133 [+0.0057, +0.0208] | +0.0070 [-0.0008, +0.0146] | 0.870 | 0.356 | yes |
| 4 | 0.659 (126 of 1870 days never flag) | 123 | 0.457 | 0.512 | 0.0563 | +0.0145 [+0.0076, +0.0221] | +0.0061 [-0.0016, +0.0139] | 0.859 | 0.422 | yes |
| 5 | 0.527 (126 of 1869 days never flag) | 99 | 0.377 | 0.525 | 0.0632 | +0.0077 [-0.0003, +0.0152] | +0.0002 [-0.0081, +0.0079] | 0.826 | 0.350 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.684 (climatology 0.512, difference +0.1715 [+0.0430, +0.3172]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0858, ΔBrier vs climatology +0.0437 [+0.0237, +0.0650], realised minus predicted -0.0298 [-0.0582, +0.0010]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.512 | 0.2836 | 0.2720 | +0.0326 [+0.0023, +0.0655] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1543 | 0.0159 | +0.0047 [-0.0130, +0.0195] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0102 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0875 | 0.1165 | +0.0360 [+0.0071, +0.0710] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0084 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0736 | 0.0000 | +0.0190 [+0.0131, +0.0246] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1203 | 0.2439 | 0.0170 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.529 | 0.2945 | 0.2615 | +0.0355 [+0.0071, +0.0671] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1343 | 0.1133 | +0.0317 [-0.0015, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.0811 | 0.0630 | +0.0123 [+0.0052, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0260, +0.1590] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2028 | 0.1461 | +0.0603 [+0.0197, +0.1058] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2717 | 0.2213 |

