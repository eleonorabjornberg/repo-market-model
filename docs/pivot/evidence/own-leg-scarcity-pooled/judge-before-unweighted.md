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

- h = 1: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.457 (climatology 0.457, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1757, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0470 [-0.1017, +0.0117]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.436 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0645 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0907 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1572 | 0.0031 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0728 | 0.4146 | 0.0000 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.424 | 0.1413 | 0.2474 | +0.0000 [+0.0000, +0.0000] |
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

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.477 (climatology 0.457, difference +0.0203 [-0.0817, +0.1399]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0510, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.451 | 0.455 | 0.1679 | 0.2720 | +0.0168 [-0.0027, +0.0376] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.0978 | 0.1165 | +0.0256 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0233 | 0.0048 | +0.0080 [+0.0059, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0891 | 0.0031 | +0.0206 [+0.0144, +0.0267] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2311 | 0.4146 | 0.0897 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.453 | 0.457 | 0.1759 | 0.2474 | +0.0203 [+0.0030, +0.0386] |
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

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.556 (climatology 0.457, difference +0.0986 [-0.0464, +0.1907]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0303, +0.0551], realised minus predicted +0.0654 [+0.0350, +0.0998]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.577 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0503 | 0.0159 | +0.0329 [+0.0235, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.909 | 0.0443 | 0.1165 | +0.0287 [+0.0113, +0.0503] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0268 | 0.0031 | +0.0285 [+0.0229, +0.0343] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | 0.0409 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.547 | 0.593 | 0.2024 | 0.2474 | +0.0558 [+0.0323, +0.0805] |
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
| 1 | 0.121 (105 of 1873 days never flag) | 77 | 0.300 | 0.545 | 0.0577 | +0.0137 [+0.0082, +0.0193] | -0.0014 [-0.0097, +0.0063] | 0.642 | 0.280 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 53 | 0.180 | 0.472 | 0.0687 | +0.0024 [-0.0040, +0.0080] | -0.0076 [-0.0161, -0.0005] | 0.578 | 0.164 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0667 | +0.0040 [-0.0025, +0.0098] | -0.0023 [-0.0102, +0.0044] | 0.579 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 46 | 0.167 | 0.500 | 0.0668 | +0.0040 [-0.0028, +0.0099] | -0.0045 [-0.0121, +0.0023] | 0.579 | 0.153 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 48 | 0.152 | 0.438 | 0.0696 | +0.0013 [-0.0053, +0.0074] | -0.0062 [-0.0136, +0.0007] | 0.577 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.486 (climatology 0.457, difference +0.0291 [-0.1218, +0.1504]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1047, ΔBrier vs climatology +0.0248 [+0.0158, +0.0336], realised minus predicted +0.0931 [+0.0563, +0.1320]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0959 | 0.2720 | +0.0016 [-0.0200, +0.0242] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0148 | 0.0159 | +0.0396 [+0.0307, +0.0483] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0028 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0386 | 0.1165 | +0.0155 [-0.0024, +0.0394] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0022 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0035 | 0.0031 | +0.0296 [+0.0218, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0274 | 0.4146 | -0.0074 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0971 | 0.2474 | +0.0155 [-0.0047, +0.0366] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0985 | 0.1133 | +0.0543 [+0.0303, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0314, +0.2020] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0958 | 0.1461 | +0.0686 [+0.0412, +0.0953] |

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
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 1.346 [0.758, 2.179] | 0.587 [0.299, 1.046] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.962 [1.815, 4.467] | 1.163 [0.726, 1.786] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 2.808 [1.515, 4.530] | 1.154 [0.570, 1.975] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.308 [1.419, 3.501] | 0.808 [0.500, 1.239] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.538 [1.444, 4.000] | 0.952 [0.552, 1.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.833, 9.910] | 2.632 [1.517, 4.469] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 5.111 [3.000, 10.008] | 2.639 [1.519, 5.438] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 99 | 0.457 | 0.646 | 0.0478 | +0.0236 [+0.0164, +0.0318] | +0.0085 [+0.0037, +0.0138] | 0.892 | 0.437 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 139 | 0.446 | 0.446 | 0.0601 | +0.0109 [+0.0065, +0.0151] | +0.0009 [-0.0021, +0.0040] | 0.837 | 0.402 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 132 | 0.428 | 0.447 | 0.0605 | +0.0101 [+0.0065, +0.0142] | +0.0038 [+0.0011, +0.0070] | 0.810 | 0.385 | no |
| 4 | 0.335 (147 of 1870 days never flag) | 118 | 0.420 | 0.492 | 0.0594 | +0.0114 [+0.0070, +0.0161] | +0.0030 [+0.0004, +0.0058] | 0.822 | 0.386 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 117 | 0.370 | 0.436 | 0.0629 | +0.0080 [+0.0036, +0.0123] | +0.0004 [-0.0025, +0.0033] | 0.790 | 0.331 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.465 (climatology 0.457, difference +0.0078 [-0.1078, +0.1043]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0843, ΔBrier vs climatology +0.0452 [+0.0316, +0.0605], realised minus predicted +0.0117 [-0.0185, +0.0443]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2373 | 0.2720 | +0.0573 [+0.0304, +0.0862] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1174 | 0.0159 | +0.0233 [+0.0097, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0192 | 0.0000 | +0.0131 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0328 | 0.0200 | +0.0006 [-0.0060, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.1149 | 0.1165 | +0.0275 [+0.0002, +0.0591] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0230 | 0.0048 | +0.0075 [+0.0051, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0681 | 0.0031 | +0.0221 [+0.0146, +0.0292] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2116 | 0.4146 | 0.0619 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.530 | 0.660 | 0.2433 | 0.2474 | +0.0564 [+0.0318, +0.0827] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1078 | 0.1133 | +0.0595 [+0.0357, +0.0870] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.603 | 0.0861 | 0.0630 | +0.0160 [+0.0093, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0378, +0.1950] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0421, +0.0963] |

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
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.285, 0.643] | 0.846 [0.500, 1.360] | 0.375 [0.210, 0.638] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.538 [1.600, 3.790] | 1.000 [0.614, 1.566] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.458] | 2.962 [1.815, 4.474] | 1.135 [0.712, 1.700] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.409] | 2.154 [1.304, 3.348] | 0.798 [0.491, 1.250] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.423 [1.478, 3.778] | 1.029 [0.620, 1.652] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 5.000 [3.000, 7.924] | 1.882 [1.118, 3.096] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 6.889 (no interval) | 3.833 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 67 | 0.321 | 0.672 | 0.0497 | +0.0218 [+0.0145, +0.0293] | +0.0067 [+0.0016, +0.0119] | 0.804 | 0.309 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 120 | 0.388 | 0.450 | 0.0624 | +0.0087 [+0.0038, +0.0133] | -0.0013 [-0.0055, +0.0024] | 0.749 | 0.350 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 134 | 0.413 | 0.425 | 0.0606 | +0.0101 [+0.0050, +0.0146] | +0.0038 [-0.0008, +0.0076] | 0.747 | 0.369 | no |
| 4 | 0.258 (147 of 1870 days never flag) | 109 | 0.384 | 0.486 | 0.0603 | +0.0106 [+0.0055, +0.0156] | +0.0021 [-0.0014, +0.0056] | 0.760 | 0.352 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 111 | 0.348 | 0.432 | 0.0636 | +0.0073 [+0.0018, +0.0125] | -0.0002 [-0.0042, +0.0037] | 0.742 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.487 (climatology 0.457, difference +0.0300 [-0.0960, +0.1429]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0862, ΔBrier vs climatology +0.0433 [+0.0303, +0.0579], realised minus predicted +0.0618 [+0.0331, +0.0951]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.1676 | 0.2720 | +0.0417 [+0.0143, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0224 | 0.0159 | +0.0323 [+0.0157, +0.0454] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0152 | 0.0200 | +0.0007 [-0.0068, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0899 | 0.1165 | +0.0266 [+0.0009, +0.0587] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0090 | 0.0048 | +0.0078 [+0.0053, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0085 | 0.0031 | +0.0282 [+0.0200, +0.0355] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1827 | 0.4146 | 0.0599 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.368 | 0.694 | 0.1657 | 0.2474 | +0.0446 [+0.0203, +0.0703] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1023 | 0.1133 | +0.0600 [+0.0346, +0.0873] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0419 | 0.0630 | +0.0138 [+0.0076, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0326, +0.1953] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0419, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3822 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.417, 0.741] | 0.242 | 4.31 flat / 2.04 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.231 | 3.46 flat / 1.63 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 0.808 [0.435, 1.321] | 0.337 [0.176, 0.575] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.231, 0.562] | 1.654 [1.000, 2.609] | 0.663 [0.397, 1.056] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.531] | 1.808 [1.138, 2.770] | 0.798 [0.484, 1.275] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.216, 0.571] | 1.577 [0.935, 2.440] | 0.654 [0.393, 1.036] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.645] | 2.346 [1.457, 3.667] | 1.135 [0.703, 1.784] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.437, 0.875] | 3.647 [2.111, 6.083] | 1.441 [0.839, 2.423] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.166, 0.714] | 5.556 [3.153, 11.337] | 3.167 [1.786, 6.801] |

Recall with equal weight per regime: 0.437 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 65 | 0.314 | 0.677 | 0.0498 | +0.0216 [+0.0142, +0.0289] | +0.0065 [+0.0011, +0.0118] | 0.804 | 0.302 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 96 | 0.381 | 0.552 | 0.0544 | +0.0166 [+0.0116, +0.0221] | +0.0066 [+0.0019, +0.0117] | 0.800 | 0.356 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 93 | 0.333 | 0.495 | 0.0570 | +0.0137 [+0.0083, +0.0189] | +0.0074 [+0.0025, +0.0124] | 0.776 | 0.306 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 93 | 0.377 | 0.559 | 0.0532 | +0.0176 [+0.0122, +0.0229] | +0.0092 [+0.0049, +0.0138] | 0.807 | 0.353 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 123 | 0.449 | 0.504 | 0.0539 | +0.0170 [+0.0115, +0.0226] | +0.0095 [+0.0051, +0.0144] | 0.804 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.457, difference +0.2581 [+0.0710, +0.4127]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0726, ΔBrier vs climatology +0.0569 [+0.0394, +0.0760], realised minus predicted +0.0315 [+0.0067, +0.0570]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.694 | 0.1692 | 0.2720 | +0.0420 [+0.0131, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0244 | 0.0159 | +0.0309 [+0.0152, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0129 | 0.0200 | -0.0015 [-0.0087, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0907 | 0.1165 | +0.0286 [+0.0022, +0.0591] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0079 | 0.0048 | +0.0074 [+0.0050, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0096 | 0.0031 | +0.0277 [+0.0187, +0.0358] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2003 | 0.4146 | +0.0733 [-0.0010, +0.1500] |
| scarcity_state | 3 | 473 | 117 | 0.359 | 0.700 | 0.1671 | 0.2474 | +0.0438 [+0.0178, +0.0695] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1010 | 0.1133 | +0.0595 [+0.0350, +0.0859] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0425 | 0.0630 | +0.0134 [+0.0067, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0406, +0.2112] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0989 | 0.1461 | +0.0689 [+0.0406, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3821 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41+iorb (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.440, 0.786] | 0.246 | 4.35 flat / 2.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.652] | 0.231 | 3.46 flat / 1.63 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.677] | 0.846 [0.476, 1.333] | 0.375 [0.203, 0.616] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.216, 0.565] | 1.654 [0.973, 2.600] | 0.663 [0.391, 1.059] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.808 [1.128, 2.800] | 0.798 [0.478, 1.286] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 1.577 [0.944, 2.423] | 0.654 [0.391, 1.044] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.346 [1.444, 3.654] | 1.135 [0.724, 1.780] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.428, 0.867] | 3.647 [2.125, 5.938] | 1.441 [0.833, 2.400] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.667 (no interval) | 3.278 (no interval) |

Recall with equal weight per regime: 0.562 (2018-19 11/17, 2020 2/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 68 | 0.329 | 0.676 | 0.0497 | +0.0217 [+0.0145, +0.0298] | +0.0066 [+0.0013, +0.0125] | 0.805 | 0.316 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 96 | 0.381 | 0.552 | 0.0544 | +0.0166 [+0.0116, +0.0220] | +0.0066 [+0.0018, +0.0120] | 0.800 | 0.356 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 93 | 0.333 | 0.495 | 0.0570 | +0.0137 [+0.0085, +0.0190] | +0.0074 [+0.0028, +0.0122] | 0.776 | 0.306 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 93 | 0.377 | 0.559 | 0.0532 | +0.0176 [+0.0122, +0.0232] | +0.0092 [+0.0049, +0.0139] | 0.807 | 0.353 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 123 | 0.449 | 0.504 | 0.0539 | +0.0170 [+0.0117, +0.0225] | +0.0095 [+0.0050, +0.0139] | 0.804 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.457, difference +0.2581 [+0.0630, +0.4287]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0718, ΔBrier vs climatology +0.0577 [+0.0397, +0.0765], realised minus predicted +0.0295 [+0.0055, +0.0555]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.343 | 0.700 | 0.1724 | 0.2720 | +0.0442 [+0.0158, +0.0733] |
| regime | 2020 | 251 | 4 | 0.500 | 0.500 | 0.0283 | 0.0159 | +0.0350 [+0.0212, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0179 | 0.0200 | -0.0058 [-0.0174, +0.0034] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0904 | 0.1165 | +0.0264 [+0.0024, +0.0563] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0088 | 0.0048 | +0.0064 [+0.0030, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0095 | 0.0031 | +0.0275 [+0.0183, +0.0351] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1962 | 0.4146 | 0.0665 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.376 | 0.710 | 0.1722 | 0.2474 | +0.0473 [+0.0228, +0.0731] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1010 | 0.1133 | +0.0595 [+0.0347, +0.0862] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.600 | 0.0445 | 0.0630 | +0.0136 [+0.0073, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0432, +0.2095] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0989 | 0.1461 | +0.0689 [+0.0395, +0.0976] |

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
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 1.231 [0.679, 2.056] | 0.538 [0.292, 0.909] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.769 [1.749, 4.185] | 1.096 [0.687, 1.700] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.962 [1.741, 4.697] | 1.231 [0.676, 2.058] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.469] | 2.385 [1.316, 3.929] | 0.846 [0.463, 1.391] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.417] | 2.154 [1.316, 3.333] | 0.865 [0.518, 1.381] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.353 [3.950, 10.000] | 2.588 [1.526, 4.313] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.889 (no interval) | 2.222 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 80 | 0.343 | 0.600 | 0.0484 | +0.0230 [+0.0162, +0.0305] | +0.0080 [+0.0031, +0.0132] | 0.880 | 0.324 | yes |
| 2 | 0.257 (147 of 1872 days never flag) | 133 | 0.439 | 0.459 | 0.0594 | +0.0117 [+0.0082, +0.0151] | +0.0017 [-0.0019, +0.0051] | 0.821 | 0.397 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 134 | 0.413 | 0.425 | 0.0592 | +0.0115 [+0.0082, +0.0152] | +0.0052 [+0.0015, +0.0089] | 0.800 | 0.369 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 117 | 0.399 | 0.470 | 0.0580 | +0.0129 [+0.0093, +0.0164] | +0.0044 [+0.0018, +0.0072] | 0.813 | 0.363 | no |
| 5 | 0.258 (147 of 1869 days never flag) | 108 | 0.377 | 0.481 | 0.0613 | +0.0097 [+0.0062, +0.0132] | +0.0021 [-0.0008, +0.0051] | 0.781 | 0.344 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.466 (climatology 0.457, difference +0.0084 [-0.1143, +0.1115]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0858, ΔBrier vs climatology +0.0437 [+0.0308, +0.0574], realised minus predicted +0.0219 [-0.0102, +0.0582]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.576 | 0.2177 | 0.2720 | +0.0498 [+0.0240, +0.0771] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.1033 | 0.0159 | +0.0291 [+0.0201, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0240 | 0.0200 | +0.0027 [-0.0017, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0982 | 0.1165 | +0.0264 [+0.0028, +0.0561] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0183 | 0.0048 | +0.0082 [+0.0062, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0569 | 0.0031 | +0.0245 [+0.0174, +0.0309] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.500 | 0.1680 | 0.4146 | 0.0483 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.402 | 0.610 | 0.2235 | 0.2474 | +0.0524 [+0.0297, +0.0773] |
| day_type | month_end | 150 | 17 | 0.706 | 0.706 | 0.1064 | 0.1133 | +0.0586 [+0.0341, +0.0839] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.500 | 0.0740 | 0.0630 | +0.0154 [+0.0093, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0375, +0.1956] |
| day_type | tax_date | 89 | 13 | 0.538 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0421, +0.0963] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.4541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2486 | 0.2213 |

## risk_gbm+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.433, 0.792] | 0.269 | 5.73 flat / 2.58 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.600] | 0.250 | 4.42 flat / 1.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.647] | 1.308 [0.737, 2.131] | 0.577 [0.296, 1.042] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.962 [1.895, 4.451] | 1.163 [0.732, 1.784] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.923 [1.636, 4.700] | 1.183 [0.603, 2.037] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 2.269 [1.393, 3.572] | 0.788 [0.491, 1.250] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.462 [1.400, 4.040] | 0.894 [0.514, 1.453] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.846, 9.834] | 2.632 [1.490, 4.475] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.778 (no interval) | 2.472 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 98 | 0.457 | 0.653 | 0.0472 | +0.0243 [+0.0170, +0.0321] | +0.0092 [+0.0042, +0.0143] | 0.911 | 0.438 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 141 | 0.460 | 0.454 | 0.0594 | +0.0117 [+0.0071, +0.0160] | +0.0017 [-0.0016, +0.0047] | 0.872 | 0.416 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 137 | 0.442 | 0.445 | 0.0588 | +0.0119 [+0.0083, +0.0155] | +0.0055 [+0.0028, +0.0084] | 0.859 | 0.398 | no |
| 4 | 0.335 (147 of 1870 days never flag) | 118 | 0.428 | 0.500 | 0.0581 | +0.0127 [+0.0085, +0.0172] | +0.0043 [+0.0019, +0.0071] | 0.865 | 0.393 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 115 | 0.370 | 0.443 | 0.0619 | +0.0090 [+0.0046, +0.0133] | +0.0015 [-0.0015, +0.0045] | 0.848 | 0.333 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.465 (climatology 0.457, difference +0.0078 [-0.1074, +0.1053]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0834, ΔBrier vs climatology +0.0461 [+0.0323, +0.0603], realised minus predicted +0.0381 [+0.0083, +0.0711]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2373 | 0.2720 | +0.0573 [+0.0292, +0.0859] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1174 | 0.0159 | +0.0233 [+0.0105, +0.0358] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0050 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0037 [-0.0002, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.1013 | 0.1165 | +0.0284 [+0.0006, +0.0621] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0022 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0681 | 0.0031 | +0.0221 [+0.0149, +0.0291] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2116 | 0.4146 | 0.0619 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.530 | 0.660 | 0.2433 | 0.2474 | +0.0564 [+0.0311, +0.0810] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1058 | 0.1133 | +0.0595 [+0.0355, +0.0867] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.611 | 0.0729 | 0.0630 | +0.0167 [+0.0098, +0.0240] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0353, +0.1964] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0413, +0.0941] |

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
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 1.385 [0.848, 2.188] | 0.548 [0.333, 0.893] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.457] | 1.308 [0.824, 2.000] | 0.596 [0.310, 1.030] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.077 [0.667, 1.667] | 0.462 [0.250, 0.779] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.000 [0.615, 1.550] | 0.375 [0.210, 0.625] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.231 [0.774, 1.913] | 0.625 [0.352, 1.060] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.812] | 2.412 [1.500, 4.077] | 0.971 [0.579, 1.688] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 2.639 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 93 | 0.407 | 0.613 | 0.0484 | +0.0230 [+0.0175, +0.0290] | +0.0080 [+0.0030, +0.0132] | 0.899 | 0.386 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 66 | 0.230 | 0.485 | 0.0604 | +0.0107 [+0.0074, +0.0138] | +0.0007 [-0.0032, +0.0044] | 0.847 | 0.211 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 55 | 0.196 | 0.491 | 0.0598 | +0.0109 [+0.0076, +0.0146] | +0.0046 [+0.0007, +0.0086] | 0.817 | 0.179 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 54 | 0.203 | 0.519 | 0.0592 | +0.0116 [+0.0079, +0.0154] | +0.0032 [-0.0002, +0.0065] | 0.832 | 0.188 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 57 | 0.181 | 0.439 | 0.0624 | +0.0086 [+0.0049, +0.0120] | +0.0010 [-0.0029, +0.0045] | 0.797 | 0.163 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.456 (climatology 0.457, difference -0.0009 [-0.1197, +0.1142]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0897, ΔBrier vs climatology +0.0398 [+0.0295, +0.0513], realised minus predicted +0.0534 [+0.0201, +0.0884]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.608 | 0.1666 | 0.2720 | +0.0429 [+0.0257, +0.0603] |
| regime | 2020 | 251 | 4 | 0.250 | 1.000 | 0.0661 | 0.0159 | +0.0366 [+0.0281, +0.0449] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0099 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0178 | 0.0200 | +0.0030 [-0.0012, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.611 | 0.0768 | 0.1165 | +0.0281 [+0.0036, +0.0597] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0126 | 0.0048 | +0.0085 [+0.0065, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0358 | 0.0031 | +0.0277 [+0.0204, +0.0345] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.600 | 0.1195 | 0.4146 | 0.0486 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.462 | 0.621 | 0.1702 | 0.2474 | +0.0496 [+0.0327, +0.0674] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1032 | 0.1133 | +0.0572 [+0.0328, +0.0846] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.586 | 0.0494 | 0.0630 | +0.0155 [+0.0111, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0360, +0.1988] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.0958 | 0.1461 | +0.0686 [+0.0415, +0.0975] |

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
| 1 | 0.638 (105 of 1873 days never flag) | 87 | 0.336 | 0.540 | 0.0606 | +0.0108 [+0.0009, +0.0206] | -0.0043 [-0.0126, +0.0039] | 0.871 | 0.313 | no |
| 2 | 0.605 (147 of 1872 days never flag) | 125 | 0.410 | 0.456 | 0.0716 | -0.0006 [-0.0090, +0.0075] | -0.0106 [-0.0183, -0.0034] | 0.816 | 0.371 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 121 | 0.406 | 0.463 | 0.0726 | -0.0019 [-0.0112, +0.0059] | -0.0082 [-0.0171, -0.0007] | 0.795 | 0.368 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 104 | 0.384 | 0.510 | 0.0702 | +0.0006 [-0.0067, +0.0070] | -0.0078 [-0.0144, -0.0020] | 0.815 | 0.355 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 106 | 0.355 | 0.462 | 0.0728 | -0.0019 [-0.0083, +0.0039] | -0.0094 [-0.0153, -0.0041] | 0.776 | 0.322 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.428 (climatology 0.457, difference -0.0291 [-0.1388, +0.0832]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0934, ΔBrier vs climatology +0.0361 [+0.0226, +0.0504], realised minus predicted +0.0060 [-0.0287, +0.0432]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.507 | 0.3118 | 0.2720 | +0.0131 [-0.0304, +0.0570] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0240, +0.0127] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0684 | 0.1165 | +0.0268 [+0.0013, +0.0566] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0074 | 0.0048 | +0.0080 [+0.0061, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1089 | 0.0031 | +0.0102 [+0.0039, +0.0164] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1375 | 0.4146 | 0.0461 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.393 | 0.541 | 0.3117 | 0.2474 | +0.0141 [-0.0237, +0.0511] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1092 | 0.1133 | +0.0568 [+0.0315, +0.0835] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1025 | 0.0630 | +0.0012 [-0.0092, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0346, +0.1936] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0412, +0.0950] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.778] | 0.231 | 3.88 flat / 1.49 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.567] | 0.231 | 3.12 flat / 1.06 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.688] | 1.500 [0.731, 2.612] | 0.673 [0.304, 1.196] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 2.192 [1.097, 3.709] | 0.702 [0.324, 1.214] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 2.538 [1.300, 4.311] | 0.837 [0.417, 1.432] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 2.000 [0.914, 3.654] | 0.635 [0.271, 1.191] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.000 [0.968, 3.565] | 0.673 [0.320, 1.198] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 5.235 [3.130, 8.571] | 1.971 [1.125, 3.342] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.333 [0.498, 3.000] | 0.583 [0.175, 1.393] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 85 | 0.329 | 0.541 | 0.0608 | +0.0106 [+0.0006, +0.0201] | -0.0045 [-0.0128, +0.0035] | 0.871 | 0.306 | yes |
| 2 | 0.668 (147 of 1872 days never flag) | 109 | 0.374 | 0.477 | 0.0720 | -0.0009 [-0.0095, +0.0070] | -0.0109 [-0.0193, -0.0036] | 0.810 | 0.341 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 122 | 0.406 | 0.459 | 0.0728 | -0.0022 [-0.0120, +0.0059] | -0.0085 [-0.0178, -0.0007] | 0.798 | 0.368 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 105 | 0.384 | 0.505 | 0.0709 | -0.0001 [-0.0073, +0.0066] | -0.0085 [-0.0152, -0.0023] | 0.816 | 0.354 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 100 | 0.348 | 0.480 | 0.0728 | -0.0018 [-0.0082, +0.0040] | -0.0094 [-0.0156, -0.0039] | 0.779 | 0.318 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.442 (climatology 0.457, difference -0.0147 [-0.1277, +0.0943]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0919, ΔBrier vs climatology +0.0375 [+0.0235, +0.0531], realised minus predicted +0.0035 [-0.0320, +0.0394]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.514 | 0.3133 | 0.2720 | +0.0133 [-0.0301, +0.0543] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1940 | 0.0159 | -0.0054 [-0.0268, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0048 | 0.0200 | +0.0003 [-0.0060, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0693 | 0.1165 | +0.0287 [+0.0051, +0.0574] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0064 | 0.0048 | +0.0077 [+0.0055, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1100 | 0.0031 | +0.0097 [+0.0032, +0.0166] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1551 | 0.4146 | 0.0595 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.385 | 0.542 | 0.3130 | 0.2474 | +0.0133 [-0.0243, +0.0487] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1079 | 0.1133 | +0.0563 [+0.0334, +0.0804] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1031 | 0.0630 | +0.0009 [-0.0095, +0.0109] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0355, +0.2028] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0989 | 0.1461 | +0.0689 [+0.0401, +0.0975] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.714] | 0.231 | 3.00 flat / 1.34 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.615] | 0.192 | 2.35 flat / 0.94 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 1.538 [0.733, 2.630] | 0.712 [0.333, 1.224] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 1.962 [0.928, 3.459] | 0.779 [0.400, 1.320] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 2.000 [1.000, 3.429] | 0.788 [0.398, 1.320] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.560] | 1.846 [0.857, 3.222] | 0.692 [0.328, 1.183] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.000 [0.978, 3.421] | 0.798 [0.416, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 3.824 [2.035, 6.727] | 1.559 [0.812, 2.751] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.444 [0.500, 3.333] | 0.917 [0.262, 2.393] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 87 | 0.336 | 0.540 | 0.0606 | +0.0108 [+0.0015, +0.0207] | -0.0043 [-0.0124, +0.0036] | 0.871 | 0.313 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 111 | 0.432 | 0.541 | 0.0650 | +0.0060 [-0.0034, +0.0148] | -0.0040 [-0.0128, +0.0042] | 0.837 | 0.402 | no |
| 3 | 0.615 (147 of 1871 days never flag) | 107 | 0.399 | 0.514 | 0.0687 | +0.0020 [-0.0083, +0.0111] | -0.0043 [-0.0138, +0.0044] | 0.826 | 0.369 | no |
| 4 | 0.754 (147 of 1870 days never flag) | 100 | 0.377 | 0.520 | 0.0650 | +0.0058 [-0.0016, +0.0130] | -0.0027 [-0.0098, +0.0041] | 0.840 | 0.349 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 112 | 0.435 | 0.536 | 0.0653 | +0.0056 [-0.0011, +0.0122] | -0.0019 [-0.0081, +0.0042] | 0.828 | 0.405 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.664 (climatology 0.457, difference +0.2071 [+0.0396, +0.3632]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0824, ΔBrier vs climatology +0.0471 [+0.0291, +0.0679], realised minus predicted -0.0169 [-0.0464, +0.0164]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.507 | 0.3118 | 0.2720 | +0.0131 [-0.0284, +0.0549] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0226, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0684 | 0.1165 | +0.0268 [+0.0030, +0.0587] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0074 | 0.0048 | +0.0080 [+0.0060, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1089 | 0.0031 | +0.0102 [+0.0039, +0.0159] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1375 | 0.4146 | +0.0461 [-0.0194, +0.1240] |
| scarcity_state | 3 | 473 | 117 | 0.393 | 0.541 | 0.3117 | 0.2474 | +0.0141 [-0.0216, +0.0523] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1092 | 0.1133 | +0.0568 [+0.0329, +0.0841] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1025 | 0.0630 | +0.0012 [-0.0087, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0351, +0.1989] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0417, +0.0961] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.719] | 0.231 | 3.31 flat / 1.48 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.192 | 2.46 flat / 1.04 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.696] | 1.500 [0.727, 2.625] | 0.673 [0.311, 1.242] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.154 [1.052, 3.800] | 0.827 [0.430, 1.413] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 2.154 [1.050, 3.783] | 0.865 [0.452, 1.471] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.219, 0.571] | 1.962 [0.952, 3.389] | 0.779 [0.387, 1.359] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 1.885 [0.850, 3.357] | 0.769 [0.375, 1.336] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 4.059 [2.312, 7.000] | 1.618 [0.920, 2.896] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.889 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 85 | 0.329 | 0.541 | 0.0608 | +0.0106 [+0.0011, +0.0202] | -0.0045 [-0.0128, +0.0038] | 0.871 | 0.306 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 116 | 0.432 | 0.517 | 0.0654 | +0.0057 [-0.0036, +0.0142] | -0.0043 [-0.0130, +0.0039] | 0.835 | 0.399 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 112 | 0.406 | 0.500 | 0.0696 | +0.0011 [-0.0095, +0.0098] | -0.0052 [-0.0151, +0.0034] | 0.818 | 0.373 | no |
| 4 | 0.641 (147 of 1870 days never flag) | 105 | 0.391 | 0.514 | 0.0645 | +0.0063 [-0.0015, +0.0136] | -0.0021 [-0.0097, +0.0051] | 0.843 | 0.362 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 109 | 0.435 | 0.550 | 0.0645 | +0.0065 [-0.0004, +0.0130] | -0.0011 [-0.0077, +0.0053] | 0.826 | 0.406 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.713 (climatology 0.457, difference +0.2556 [+0.0750, +0.4175]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0828, ΔBrier vs climatology +0.0467 [+0.0285, +0.0663], realised minus predicted -0.0174 [-0.0486, +0.0167]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.514 | 0.3133 | 0.2720 | +0.0133 [-0.0292, +0.0558] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1940 | 0.0159 | -0.0054 [-0.0262, +0.0109] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0048 | 0.0200 | +0.0003 [-0.0054, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0693 | 0.1165 | +0.0287 [+0.0049, +0.0601] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0064 | 0.0048 | +0.0077 [+0.0055, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1100 | 0.0031 | +0.0097 [+0.0031, +0.0160] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1551 | 0.4146 | 0.0595 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.385 | 0.542 | 0.3130 | 0.2474 | +0.0133 [-0.0222, +0.0497] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1079 | 0.1133 | +0.0563 [+0.0321, +0.0818] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1031 | 0.0630 | +0.0009 [-0.0095, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0397, +0.2077] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0989 | 0.1461 | +0.0689 [+0.0400, +0.0982] |

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
| 1 | 0.517 (105 of 1873 days never flag) | 93 | 0.386 | 0.581 | 0.0561 | +0.0153 [+0.0079, +0.0235] | +0.0002 [-0.0061, +0.0067] | 0.845 | 0.363 | yes |
| 2 | 0.489 (147 of 1872 days never flag) | 133 | 0.388 | 0.406 | 0.0698 | +0.0013 [-0.0044, +0.0070] | -0.0087 [-0.0146, -0.0031] | 0.771 | 0.343 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 126 | 0.428 | 0.468 | 0.0699 | +0.0008 [-0.0040, +0.0054] | -0.0055 [-0.0105, -0.0008] | 0.725 | 0.389 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 119 | 0.413 | 0.479 | 0.0692 | +0.0017 [-0.0031, +0.0063] | -0.0068 [-0.0113, -0.0025] | 0.754 | 0.377 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 131 | 0.370 | 0.389 | 0.0728 | -0.0019 [-0.0071, +0.0030] | -0.0094 [-0.0149, -0.0042] | 0.717 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.429 (climatology 0.457, difference -0.0285 [-0.1407, +0.0861]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0964, ΔBrier vs climatology +0.0331 [+0.0200, +0.0467], realised minus predicted -0.0115 [-0.0466, +0.0269]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.566 | 0.2828 | 0.2720 | +0.0391 [+0.0075, +0.0714] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0137, +0.0099] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0086, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0022, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0671 | 0.1165 | +0.0247 [+0.0015, +0.0539] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0207 | 0.0048 | +0.0076 [+0.0057, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1277 | 0.0031 | +0.0050 [-0.0007, +0.0111] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1227 | 0.4146 | 0.0270 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.584 | 0.2857 | 0.2474 | +0.0383 [+0.0102, +0.0673] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1099 | 0.1133 | +0.0561 [+0.0318, +0.0827] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.507 | 0.1068 | 0.0630 | +0.0066 [-0.0009, +0.0146] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0345, +0.1949] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0958 | 0.1461 | +0.0686 [+0.0402, +0.0966] |

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
| 1 | 0.517 (105 of 1873 days never flag) | 94 | 0.386 | 0.574 | 0.0563 | +0.0151 [+0.0076, +0.0233] | +0.0000 [-0.0056, +0.0062] | 0.843 | 0.363 | yes |
| 2 | 0.489 (147 of 1872 days never flag) | 139 | 0.424 | 0.424 | 0.0701 | +0.0010 [-0.0050, +0.0064] | -0.0090 [-0.0148, -0.0035] | 0.764 | 0.378 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 122 | 0.406 | 0.459 | 0.0702 | +0.0005 [-0.0044, +0.0052] | -0.0058 [-0.0108, -0.0012] | 0.728 | 0.368 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 120 | 0.413 | 0.475 | 0.0699 | +0.0010 [-0.0037, +0.0058] | -0.0075 [-0.0120, -0.0028] | 0.756 | 0.377 | no |
| 5 | 0.491 (147 of 1869 days never flag) | 132 | 0.370 | 0.386 | 0.0728 | -0.0019 [-0.0073, +0.0031] | -0.0094 [-0.0150, -0.0040] | 0.719 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.434 (climatology 0.457, difference -0.0235 [-0.1336, +0.0861]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0344 [+0.0211, +0.0494], realised minus predicted -0.0138 [-0.0477, +0.0235]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.573 | 0.2844 | 0.2720 | +0.0393 [+0.0063, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2021 | 0.0159 | -0.0034 [-0.0161, +0.0082] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0103 [+0.0087, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0093 | 0.0200 | +0.0003 [-0.0055, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0680 | 0.1165 | +0.0266 [+0.0041, +0.0537] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0197 | 0.0048 | +0.0072 [+0.0052, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1287 | 0.0031 | +0.0045 [-0.0014, +0.0106] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1402 | 0.4146 | 0.0404 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.436 | 0.580 | 0.2871 | 0.2474 | +0.0375 [+0.0083, +0.0669] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1086 | 0.1133 | +0.0556 [+0.0327, +0.0812] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.500 | 0.1074 | 0.0630 | +0.0062 [-0.0013, +0.0143] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0412, +0.2055] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0989 | 0.1461 | +0.0689 [+0.0391, +0.0975] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.363, 0.719] | 0.231 | 4.19 flat / 2.01 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.606] | 0.231 | 3.46 flat / 1.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.650] | 1.500 [0.875, 2.476] | 0.663 [0.353, 1.163] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.923 [0.900, 3.500] | 0.760 [0.383, 1.319] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 1.731 [0.867, 3.040] | 0.769 [0.417, 1.306] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.231 [1.231, 3.773] | 0.933 [0.534, 1.538] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.808 [1.429, 4.900] | 1.269 [0.589, 2.330] |
| inside 2018-2019 | 17 | 11 | 0.647 (no interval) | 5.000 (no interval) | 2.279 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.500 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 93 | 0.386 | 0.581 | 0.0561 | +0.0153 [+0.0080, +0.0234] | +0.0002 [-0.0058, +0.0067] | 0.845 | 0.363 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 106 | 0.403 | 0.528 | 0.0624 | +0.0087 [+0.0022, +0.0155] | -0.0013 [-0.0079, +0.0056] | 0.804 | 0.374 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 92 | 0.341 | 0.511 | 0.0655 | +0.0052 [-0.0005, +0.0112] | -0.0011 [-0.0070, +0.0049] | 0.771 | 0.315 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 111 | 0.384 | 0.477 | 0.0636 | +0.0072 [+0.0013, +0.0130] | -0.0012 [-0.0072, +0.0049] | 0.789 | 0.351 | yes |
| 5 | 0.698 (147 of 1869 days never flag) | 133 | 0.435 | 0.451 | 0.0650 | +0.0059 [-0.0001, +0.0119] | -0.0016 [-0.0080, +0.0049] | 0.781 | 0.393 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.664 (climatology 0.457, difference +0.2071 [+0.0457, +0.3541]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0843, ΔBrier vs climatology +0.0452 [+0.0274, +0.0652], realised minus predicted -0.0357 [-0.0676, -0.0021]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.566 | 0.2828 | 0.2720 | +0.0391 [+0.0085, +0.0728] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0133, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0087, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0025, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0671 | 0.1165 | +0.0247 [+0.0021, +0.0541] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0207 | 0.0048 | +0.0076 [+0.0057, +0.0094] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1277 | 0.0031 | +0.0050 [-0.0008, +0.0110] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1227 | 0.4146 | 0.0270 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.584 | 0.2857 | 0.2474 | +0.0383 [+0.0107, +0.0672] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1099 | 0.1133 | +0.0561 [+0.0325, +0.0806] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.507 | 0.1068 | 0.0630 | +0.0066 [-0.0007, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0340, +0.1947] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0958 | 0.1461 | +0.0686 [+0.0412, +0.0969] |

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
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.577] | 1.962 [1.000, 3.375] | 0.827 [0.452, 1.397] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.038 [1.129, 3.444] | 0.846 [0.466, 1.423] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.692 [1.367, 4.728] | 1.240 [0.565, 2.296] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.875] | 5.176 [2.920, 9.000] | 2.324 [1.183, 4.364] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 1.472 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 94 | 0.386 | 0.574 | 0.0563 | +0.0151 [+0.0081, +0.0233] | +0.0000 [-0.0060, +0.0061] | 0.843 | 0.363 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 112 | 0.403 | 0.500 | 0.0628 | +0.0083 [+0.0020, +0.0148] | -0.0017 [-0.0082, +0.0049] | 0.802 | 0.371 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 101 | 0.362 | 0.495 | 0.0664 | +0.0043 [-0.0015, +0.0101] | -0.0020 [-0.0081, +0.0043] | 0.764 | 0.333 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 108 | 0.399 | 0.509 | 0.0631 | +0.0077 [+0.0019, +0.0143] | -0.0007 [-0.0067, +0.0058] | 0.791 | 0.368 | yes |
| 5 | 0.723 (147 of 1869 days never flag) | 129 | 0.428 | 0.457 | 0.0642 | +0.0068 [+0.0006, +0.0128] | -0.0008 [-0.0072, +0.0058] | 0.779 | 0.387 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.713 (climatology 0.457, difference +0.2556 [+0.0730, +0.4226]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0446 [+0.0274, +0.0645], realised minus predicted -0.0359 [-0.0663, -0.0037]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.573 | 0.2844 | 0.2720 | +0.0393 [+0.0072, +0.0745] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2021 | 0.0159 | -0.0034 [-0.0161, +0.0077] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0103 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0093 | 0.0200 | +0.0003 [-0.0057, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0680 | 0.1165 | +0.0266 [+0.0046, +0.0550] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0197 | 0.0048 | +0.0072 [+0.0052, +0.0090] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1287 | 0.0031 | +0.0045 [-0.0014, +0.0105] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1402 | 0.4146 | 0.0404 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.436 | 0.580 | 0.2871 | 0.2474 | +0.0375 [+0.0098, +0.0669] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1086 | 0.1133 | +0.0556 [+0.0332, +0.0799] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.500 | 0.1074 | 0.0630 | +0.0062 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0381, +0.2092] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0989 | 0.1461 | +0.0689 [+0.0398, +0.0971] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.774] | 0.231 | 3.73 flat / 1.42 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 3.08 flat / 1.06 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.353, 0.737] | 2.231 [1.207, 3.667] | 0.865 [0.490, 1.398] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.080, 0.400] | 1.923 [0.909, 3.294] | 0.692 [0.315, 1.188] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.535] | 2.462 [1.207, 4.185] | 0.837 [0.417, 1.417] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.524] | 2.000 [0.857, 3.606] | 0.663 [0.276, 1.198] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.447] | 2.269 [1.091, 3.900] | 0.769 [0.367, 1.320] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 5.059 [2.954, 8.214] | 1.809 [1.054, 2.922] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 1.222 [0.444, 2.800] | 0.694 [0.225, 1.750] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 125 | 0.479 | 0.536 | 0.0601 | +0.0113 [+0.0007, +0.0213] | -0.0037 [-0.0137, +0.0053] | 0.889 | 0.445 | yes |
| 2 | 0.605 (147 of 1872 days never flag) | 96 | 0.331 | 0.479 | 0.0693 | +0.0018 [-0.0072, +0.0099] | -0.0082 [-0.0170, -0.0006] | 0.843 | 0.302 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 126 | 0.449 | 0.492 | 0.0685 | +0.0022 [-0.0077, +0.0108] | -0.0041 [-0.0138, +0.0044] | 0.848 | 0.412 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 106 | 0.391 | 0.509 | 0.0667 | +0.0041 [-0.0033, +0.0103] | -0.0043 [-0.0113, +0.0019] | 0.837 | 0.361 | no |
| 5 | 0.667 (147 of 1869 days never flag) | 115 | 0.406 | 0.487 | 0.0735 | -0.0026 [-0.0122, +0.0056] | -0.0101 [-0.0197, -0.0019] | 0.807 | 0.372 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.438 (climatology 0.457, difference -0.0194 [-0.1234, +0.0777]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0391 [+0.0257, +0.0537], realised minus predicted +0.0239 [-0.0094, +0.0605]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.513 | 0.3144 | 0.2720 | +0.0058 [-0.0440, +0.0510] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1416 | 0.0159 | +0.0115 [-0.0117, +0.0298] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0093 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0000, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0704 | 0.1165 | +0.0229 [+0.0014, +0.0521] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0032 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0649 | 0.0031 | +0.0232 [+0.0164, +0.0301] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0875 | 0.4146 | 0.0235 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.537 | 0.3190 | 0.2474 | +0.0078 [-0.0345, +0.0458] |
| day_type | month_end | 150 | 17 | 0.706 | 0.750 | 0.1079 | 0.1133 | +0.0573 [+0.0322, +0.0838] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.474 | 0.0919 | 0.0630 | +0.0018 [-0.0100, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0372, +0.1973] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0958 | 0.1461 | +0.0686 [+0.0409, +0.0959] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2740 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.381, 0.769] | 0.231 | 3.77 flat / 1.42 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.562] | 0.231 | 3.00 flat / 1.00 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.733] | 2.154 [1.171, 3.455] | 0.817 [0.457, 1.304] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.115, 0.435] | 2.269 [1.185, 3.762] | 0.808 [0.398, 1.370] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.147, 0.481] | 2.269 [1.038, 3.857] | 0.721 [0.308, 1.250] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.038 [0.952, 3.587] | 0.673 [0.296, 1.207] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.480] | 2.231 [1.100, 3.808] | 0.750 [0.364, 1.289] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.176 [3.142, 8.375] | 1.838 [1.107, 3.000] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 122 | 0.471 | 0.541 | 0.0602 | +0.0112 [+0.0004, +0.0212] | -0.0039 [-0.0140, +0.0049] | 0.888 | 0.439 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 113 | 0.388 | 0.478 | 0.0696 | +0.0015 [-0.0073, +0.0093] | -0.0085 [-0.0175, -0.0008] | 0.838 | 0.354 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 118 | 0.428 | 0.500 | 0.0688 | +0.0019 [-0.0079, +0.0100] | -0.0044 [-0.0144, +0.0036] | 0.848 | 0.393 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 107 | 0.391 | 0.505 | 0.0674 | +0.0034 [-0.0040, +0.0098] | -0.0050 [-0.0120, +0.0013] | 0.839 | 0.361 | no |
| 5 | 0.616 (147 of 1869 days never flag) | 114 | 0.406 | 0.491 | 0.0735 | -0.0026 [-0.0119, +0.0055] | -0.0101 [-0.0191, -0.0023] | 0.810 | 0.372 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.455 (climatology 0.457, difference -0.0019 [-0.1098, +0.1083]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0891, ΔBrier vs climatology +0.0404 [+0.0266, +0.0552], realised minus predicted +0.0219 [-0.0103, +0.0581]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.523 | 0.3160 | 0.2720 | +0.0061 [-0.0406, +0.0508] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1437 | 0.0159 | +0.0101 [-0.0143, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0014 [-0.0038, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0713 | 0.1165 | +0.0248 [+0.0042, +0.0524] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0021 | 0.0048 | +0.0084 [+0.0065, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0660 | 0.0031 | +0.0228 [+0.0150, +0.0299] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1051 | 0.4146 | 0.0370 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.542 | 0.3204 | 0.2474 | +0.0070 [-0.0334, +0.0455] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1066 | 0.1133 | +0.0569 [+0.0339, +0.0832] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.479 | 0.0925 | 0.0630 | +0.0015 [-0.0105, +0.0120] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0450, +0.2039] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0989 | 0.1461 | +0.0689 [+0.0395, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.231 | 3.35 flat / 1.37 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.263, 0.667] | 0.231 | 2.65 flat / 1.04 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.727] | 2.231 [1.200, 3.692] | 0.865 [0.475, 1.417] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.258, 0.609] | 1.385 [0.633, 2.545] | 0.596 [0.293, 1.040] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 2.308 [1.161, 3.953] | 0.904 [0.474, 1.513] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.579] | 1.923 [0.886, 3.530] | 0.712 [0.333, 1.299] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 1.923 [0.875, 3.353] | 0.769 [0.395, 1.292] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.917] | 4.412 [2.478, 7.286] | 1.662 [0.961, 2.775] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 125 | 0.479 | 0.536 | 0.0601 | +0.0113 [+0.0003, +0.0215] | -0.0037 [-0.0141, +0.0053] | 0.889 | 0.445 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 85 | 0.353 | 0.576 | 0.0630 | +0.0080 [-0.0015, +0.0162] | -0.0020 [-0.0117, +0.0062] | 0.861 | 0.332 | no |
| 3 | 0.615 (147 of 1871 days never flag) | 119 | 0.428 | 0.496 | 0.0655 | +0.0052 [-0.0057, +0.0141] | -0.0011 [-0.0119, +0.0078] | 0.865 | 0.393 | no |
| 4 | 0.754 (147 of 1870 days never flag) | 107 | 0.413 | 0.533 | 0.0622 | +0.0087 [+0.0014, +0.0153] | +0.0002 [-0.0069, +0.0073] | 0.855 | 0.384 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 110 | 0.435 | 0.545 | 0.0667 | +0.0043 [-0.0052, +0.0124] | -0.0033 [-0.0118, +0.0047] | 0.847 | 0.406 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.664 (climatology 0.457, difference +0.2071 [+0.0388, +0.3523]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0795, ΔBrier vs climatology +0.0500 [+0.0323, +0.0699], realised minus predicted +0.0013 [-0.0297, +0.0329]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.513 | 0.3144 | 0.2720 | +0.0058 [-0.0429, +0.0510] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1416 | 0.0159 | +0.0115 [-0.0122, +0.0306] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0093 | 0.0000 | +0.0128 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0003, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0704 | 0.1165 | +0.0229 [+0.0014, +0.0502] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0032 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0649 | 0.0031 | +0.0232 [+0.0165, +0.0304] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0875 | 0.4146 | +0.0235 [-0.0110, +0.0737] |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.537 | 0.3190 | 0.2474 | +0.0078 [-0.0350, +0.0467] |
| day_type | month_end | 150 | 17 | 0.706 | 0.750 | 0.1079 | 0.1133 | +0.0573 [+0.0325, +0.0825] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.474 | 0.0919 | 0.0630 | +0.0018 [-0.0101, +0.0122] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0320, +0.1961] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0958 | 0.1461 | +0.0686 [+0.0427, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2740 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.231 | 3.42 flat / 1.44 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.269, 0.667] | 0.231 | 2.58 flat / 1.06 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.355, 0.722] | 2.154 [1.138, 3.600] | 0.817 [0.432, 1.359] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 1.846 [0.840, 3.160] | 0.769 [0.380, 1.287] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.077 [1.000, 3.637] | 0.837 [0.437, 1.408] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.923 [0.965, 3.334] | 0.760 [0.396, 1.302] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 1.846 [0.852, 3.222] | 0.750 [0.387, 1.273] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.529 [2.704, 7.385] | 1.691 [1.000, 2.764] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.972 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 122 | 0.471 | 0.541 | 0.0602 | +0.0112 [+0.0006, +0.0218] | -0.0039 [-0.0143, +0.0052] | 0.888 | 0.439 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 101 | 0.381 | 0.525 | 0.0634 | +0.0077 [-0.0012, +0.0158] | -0.0023 [-0.0115, +0.0060] | 0.860 | 0.354 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 111 | 0.413 | 0.514 | 0.0663 | +0.0044 [-0.0063, +0.0141] | -0.0019 [-0.0123, +0.0076] | 0.860 | 0.382 | no |
| 4 | 0.641 (147 of 1870 days never flag) | 107 | 0.413 | 0.533 | 0.0616 | +0.0092 [+0.0016, +0.0160] | +0.0008 [-0.0069, +0.0079] | 0.858 | 0.384 | no |
| 5 | 0.723 (147 of 1869 days never flag) | 107 | 0.428 | 0.551 | 0.0658 | +0.0051 [-0.0041, +0.0139] | -0.0024 [-0.0115, +0.0064] | 0.845 | 0.400 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.713 (climatology 0.457, difference +0.2563 [+0.0659, +0.4180]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0802, ΔBrier vs climatology +0.0492 [+0.0318, +0.0683], realised minus predicted +0.0008 [-0.0296, +0.0317]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.523 | 0.3160 | 0.2720 | +0.0061 [-0.0439, +0.0532] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1437 | 0.0159 | +0.0101 [-0.0149, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0014 [-0.0036, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0713 | 0.1165 | +0.0248 [+0.0036, +0.0528] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0021 | 0.0048 | +0.0084 [+0.0064, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0660 | 0.0031 | +0.0228 [+0.0150, +0.0301] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1051 | 0.4146 | 0.0370 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.542 | 0.3204 | 0.2474 | +0.0070 [-0.0361, +0.0472] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1066 | 0.1133 | +0.0569 [+0.0334, +0.0829] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.479 | 0.0925 | 0.0630 | +0.0015 [-0.0104, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0424, +0.2057] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0989 | 0.1461 | +0.0689 [+0.0398, +0.0977] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_gbm+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.760] | 0.258 | 4.46 flat / 1.91 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 3.88 flat / 1.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.310, 0.682] | 2.115 [1.190, 3.355] | 0.817 [0.467, 1.316] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 3.038 [1.666, 5.000] | 1.221 [0.629, 2.088] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.538 [1.929, 5.895] | 1.433 [0.704, 2.510] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.522] | 2.731 [1.321, 4.783] | 1.144 [0.470, 2.170] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.529] | 3.115 [1.625, 5.278] | 1.308 [0.607, 2.371] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.294 [3.913, 10.183] | 2.574 [1.484, 4.412] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.000 (no interval) | 0.667 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 123 | 0.486 | 0.553 | 0.0535 | +0.0179 [+0.0101, +0.0259] | +0.0028 [-0.0035, +0.0092] | 0.875 | 0.454 | yes |
| 2 | 0.532 (147 of 1872 days never flag) | 134 | 0.396 | 0.410 | 0.0657 | +0.0053 [-0.0009, +0.0115] | -0.0047 [-0.0109, +0.0008] | 0.830 | 0.350 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 163 | 0.514 | 0.436 | 0.0646 | +0.0061 [+0.0005, +0.0113] | -0.0002 [-0.0059, +0.0050] | 0.827 | 0.461 | no |
| 4 | 0.524 (147 of 1870 days never flag) | 128 | 0.413 | 0.445 | 0.0644 | +0.0064 [+0.0013, +0.0112] | -0.0021 [-0.0070, +0.0026] | 0.821 | 0.372 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 140 | 0.428 | 0.421 | 0.0693 | +0.0016 [-0.0039, +0.0067] | -0.0059 [-0.0120, -0.0002] | 0.782 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.441 (climatology 0.457, difference -0.0160 [-0.1142, +0.0913]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0917, ΔBrier vs climatology +0.0377 [+0.0252, +0.0516], realised minus predicted +0.0208 [-0.0116, +0.0578]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.536 | 0.2800 | 0.2720 | +0.0371 [+0.0034, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1646 | 0.0159 | +0.0112 [-0.0039, +0.0241] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0141 | 0.0000 | +0.0125 [+0.0110, +0.0142] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0038 | 0.0200 | +0.0037 [-0.0000, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0680 | 0.1165 | +0.0261 [+0.0027, +0.0556] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0058 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0877 | 0.0031 | +0.0185 [+0.0122, +0.0249] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0948 | 0.4146 | 0.0254 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.554 | 0.2886 | 0.2474 | +0.0369 [+0.0073, +0.0668] |
| day_type | month_end | 150 | 17 | 0.706 | 0.750 | 0.1084 | 0.1133 | +0.0573 [+0.0338, +0.0828] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.500 | 0.0893 | 0.0630 | +0.0095 [+0.0015, +0.0172] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0349, +0.1997] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.0958 | 0.1461 | +0.0686 [+0.0411, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2398 | 0.2213 |

## risk_gbm+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.795] | 0.269 | 4.62 flat / 1.99 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.88 flat / 1.59 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.391, 0.760] | 2.615 [1.536, 4.067] | 1.019 [0.609, 1.594] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.483] | 3.115 [1.692, 5.000] | 1.269 [0.641, 2.120] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.462 [1.812, 5.561] | 1.356 [0.633, 2.321] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.188, 0.522] | 2.808 [1.367, 4.715] | 1.163 [0.487, 2.107] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 3.154 [1.680, 5.143] | 1.356 [0.653, 2.348] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.294 [3.818, 10.201] | 2.574 [1.440, 4.450] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 0.889 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 137 | 0.493 | 0.504 | 0.0537 | +0.0177 [+0.0100, +0.0266] | +0.0026 [-0.0038, +0.0093] | 0.874 | 0.454 | yes |
| 2 | 0.532 (147 of 1872 days never flag) | 141 | 0.432 | 0.426 | 0.0660 | +0.0050 [-0.0015, +0.0112] | -0.0050 [-0.0115, +0.0008] | 0.826 | 0.385 | no |
| 3 | 0.726 (147 of 1871 days never flag) | 159 | 0.500 | 0.434 | 0.0648 | +0.0058 [-0.0002, +0.0112] | -0.0005 [-0.0062, +0.0048] | 0.829 | 0.448 | no |
| 4 | 0.524 (147 of 1870 days never flag) | 129 | 0.406 | 0.434 | 0.0651 | +0.0057 [+0.0003, +0.0104] | -0.0028 [-0.0079, +0.0021] | 0.821 | 0.364 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 141 | 0.428 | 0.418 | 0.0693 | +0.0016 [-0.0039, +0.0069] | -0.0059 [-0.0120, -0.0000] | 0.784 | 0.380 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.445 (climatology 0.457, difference -0.0122 [-0.1067, +0.0863]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0906, ΔBrier vs climatology +0.0389 [+0.0254, +0.0529], realised minus predicted +0.0187 [-0.0158, +0.0550]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.492 | 0.2816 | 0.2720 | +0.0374 [+0.0036, +0.0721] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1666 | 0.0159 | +0.0098 [-0.0062, +0.0242] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0125 [+0.0109, +0.0142] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0015 | 0.0200 | +0.0014 [-0.0033, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0689 | 0.1165 | +0.0281 [+0.0048, +0.0562] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0047 | 0.0048 | +0.0084 [+0.0064, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0887 | 0.0031 | +0.0181 [+0.0112, +0.0246] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1124 | 0.4146 | 0.0388 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.504 | 0.2899 | 0.2474 | +0.0361 [+0.0072, +0.0674] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1071 | 0.1133 | +0.0569 [+0.0325, +0.0828] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.444 | 0.0899 | 0.0630 | +0.0092 [+0.0015, +0.0177] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0409, +0.2097] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.0989 | 0.1461 | +0.0689 [+0.0389, +0.0989] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2396 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.765] | 0.231 | 4.08 flat / 1.87 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.654] | 0.231 | 3.46 flat / 1.57 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.696] | 2.115 [1.242, 3.364] | 0.817 [0.487, 1.309] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.609] | 1.808 [0.857, 3.292] | 0.731 [0.371, 1.279] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.346 [1.265, 3.936] | 0.971 [0.547, 1.602] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.619] | 2.654 [1.318, 4.650] | 1.192 [0.536, 2.203] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.000 [1.604, 5.035] | 1.346 [0.674, 2.384] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 5.471 [3.214, 8.858] | 2.353 [1.308, 4.083] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 0.944 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 123 | 0.486 | 0.553 | 0.0535 | +0.0179 [+0.0098, +0.0258] | +0.0028 [-0.0035, +0.0091] | 0.875 | 0.454 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 105 | 0.417 | 0.552 | 0.0589 | +0.0122 [+0.0052, +0.0190] | +0.0022 [-0.0049, +0.0090] | 0.849 | 0.390 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 117 | 0.406 | 0.479 | 0.0609 | +0.0097 [+0.0031, +0.0165] | +0.0034 [-0.0030, +0.0101] | 0.847 | 0.371 | no |
| 4 | 0.554 (147 of 1870 days never flag) | 127 | 0.420 | 0.457 | 0.0594 | +0.0114 [+0.0053, +0.0172] | +0.0029 [-0.0031, +0.0090] | 0.839 | 0.380 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 145 | 0.486 | 0.462 | 0.0620 | +0.0089 [+0.0028, +0.0152] | +0.0014 [-0.0052, +0.0077] | 0.828 | 0.440 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.664 (climatology 0.457, difference +0.2071 [+0.0395, +0.3575]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0798, ΔBrier vs climatology +0.0496 [+0.0324, +0.0683], realised minus predicted -0.0036 [-0.0348, +0.0267]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.536 | 0.2800 | 0.2720 | +0.0371 [+0.0030, +0.0714] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1646 | 0.0159 | +0.0112 [-0.0046, +0.0247] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0141 | 0.0000 | +0.0125 [+0.0110, +0.0141] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0038 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0680 | 0.1165 | +0.0261 [+0.0029, +0.0561] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0058 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0877 | 0.0031 | +0.0185 [+0.0124, +0.0247] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0948 | 0.4146 | 0.0254 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.554 | 0.2886 | 0.2474 | +0.0369 [+0.0061, +0.0673] |
| day_type | month_end | 150 | 17 | 0.706 | 0.750 | 0.1084 | 0.1133 | +0.0573 [+0.0332, +0.0822] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.500 | 0.0893 | 0.0630 | +0.0095 [+0.0017, +0.0175] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0324, +0.2003] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.0958 | 0.1461 | +0.0686 [+0.0424, +0.0952] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2398 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.231 | 4.19 flat / 1.92 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.269, 0.654] | 0.231 | 3.31 flat / 1.51 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 2.615 [1.500, 4.136] | 1.019 [0.600, 1.602] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.462 [1.231, 4.167] | 0.962 [0.515, 1.600] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.212, 0.571] | 2.077 [0.947, 3.680] | 0.827 [0.419, 1.435] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 2.423 [1.200, 4.162] | 1.154 [0.512, 2.151] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 2.923 [1.473, 4.880] | 1.327 [0.645, 2.352] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.913] | 5.647 [3.285, 9.125] | 2.397 [1.292, 4.179] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 1.028 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 137 | 0.493 | 0.504 | 0.0537 | +0.0177 [+0.0096, +0.0260] | +0.0026 [-0.0038, +0.0090] | 0.874 | 0.454 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 125 | 0.439 | 0.488 | 0.0592 | +0.0118 [+0.0046, +0.0186] | +0.0018 [-0.0054, +0.0085] | 0.848 | 0.402 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 111 | 0.413 | 0.514 | 0.0618 | +0.0089 [+0.0022, +0.0157] | +0.0026 [-0.0040, +0.0094] | 0.841 | 0.382 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 118 | 0.399 | 0.466 | 0.0589 | +0.0119 [+0.0053, +0.0185] | +0.0035 [-0.0033, +0.0102] | 0.841 | 0.362 | no |
| 5 | 0.723 (147 of 1869 days never flag) | 142 | 0.478 | 0.465 | 0.0612 | +0.0097 [+0.0035, +0.0163] | +0.0022 [-0.0045, +0.0090] | 0.823 | 0.434 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.713 (climatology 0.457, difference +0.2563 [+0.0674, +0.4122]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0806, ΔBrier vs climatology +0.0488 [+0.0314, +0.0676], realised minus predicted -0.0038 [-0.0351, +0.0269]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.492 | 0.2816 | 0.2720 | +0.0374 [+0.0029, +0.0721] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1666 | 0.0159 | +0.0098 [-0.0062, +0.0234] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0125 [+0.0109, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0015 | 0.0200 | +0.0014 [-0.0035, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0689 | 0.1165 | +0.0281 [+0.0055, +0.0587] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0047 | 0.0048 | +0.0084 [+0.0064, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0887 | 0.0031 | +0.0181 [+0.0112, +0.0246] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1124 | 0.4146 | 0.0388 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.504 | 0.2899 | 0.2474 | +0.0361 [+0.0052, +0.0675] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1071 | 0.1133 | +0.0569 [+0.0320, +0.0820] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.444 | 0.0899 | 0.0630 | +0.0092 [+0.0013, +0.0175] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0427, +0.2059] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.0989 | 0.1461 | +0.0689 [+0.0389, +0.0993] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2396 | 0.2213 |

## risk_gbm+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.710] | 0.192 | 2.00 flat / 1.29 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.154 | 1.58 flat / 1.03 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.346 [0.912, 2.000] | 0.712 [0.438, 1.150] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.571, 1.528] | 0.577 [0.309, 0.987] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.077 [0.636, 1.720] | 0.654 [0.336, 1.156] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.038 [0.606, 1.650] | 0.567 [0.288, 0.980] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.600] | 1.038 [0.607, 1.690] | 0.712 [0.357, 1.263] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.111 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 76 | 0.293 | 0.539 | 0.0579 | +0.0135 [+0.0081, +0.0193] | -0.0016 [-0.0095, +0.0062] | 0.642 | 0.273 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0593 | +0.0117 [+0.0069, +0.0165] | +0.0017 [-0.0052, +0.0083] | 0.639 | 0.259 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 63 | 0.254 | 0.556 | 0.0612 | +0.0095 [+0.0041, +0.0147] | +0.0032 [-0.0037, +0.0092] | 0.636 | 0.237 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 64 | 0.268 | 0.578 | 0.0589 | +0.0119 [+0.0070, +0.0167] | +0.0034 [-0.0027, +0.0094] | 0.633 | 0.253 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 63 | 0.261 | 0.571 | 0.0593 | +0.0116 [+0.0067, +0.0163] | +0.0041 [-0.0020, +0.0098] | 0.632 | 0.245 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.714 (climatology 0.457, difference +0.2566 [+0.0629, +0.4146]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0429 [+0.0308, +0.0563], realised minus predicted +0.0594 [+0.0304, +0.0911]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0211, +0.0239] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0168 | 0.0159 | +0.0382 [+0.0294, +0.0470] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0005 | 0.0200 | +0.0014 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0395 | 0.1165 | +0.0174 [+0.0002, +0.0403] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0012 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0046 | 0.0031 | +0.0291 [+0.0209, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0449 | 0.4146 | 0.0060 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0984 | 0.2474 | +0.0146 [-0.0055, +0.0359] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0972 | 0.1133 | +0.0538 [+0.0302, +0.0783] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.500 | 0.0133 | 0.0630 | +0.0045 [-0.0005, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0440, +0.2077] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0989 | 0.1461 | +0.0689 [+0.0408, +0.0969] |

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
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.419] | 0.115 | 1.35 flat / 0.88 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 1.500 [1.000, 2.286] | 0.971 [0.556, 1.633] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 0.962 [0.542, 1.524] | 0.490 [0.212, 0.917] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.269 [0.760, 2.042] | 0.798 [0.391, 1.445] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.077 [0.630, 1.684] | 0.606 [0.276, 1.107] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.222 [1.500, 7.400] | 2.861 [1.222, 7.000] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 81 | 0.300 | 0.519 | 0.0592 | +0.0122 [+0.0075, +0.0168] | -0.0029 [-0.0106, +0.0039] | 0.643 | 0.277 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 49 | 0.173 | 0.490 | 0.0691 | +0.0020 [-0.0047, +0.0081] | -0.0080 [-0.0168, -0.0003] | 0.578 | 0.158 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 55 | 0.159 | 0.400 | 0.0677 | +0.0029 [-0.0038, +0.0089] | -0.0034 [-0.0115, +0.0034] | 0.579 | 0.140 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0668 | +0.0040 [-0.0023, +0.0100] | -0.0044 [-0.0120, +0.0023] | 0.579 | 0.179 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 49 | 0.152 | 0.429 | 0.0696 | +0.0013 [-0.0055, +0.0072] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.136 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.457, difference +0.0410 [-0.1104, +0.1732]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1058, ΔBrier vs climatology +0.0237 [+0.0147, +0.0331], realised minus predicted +0.0905 [+0.0559, +0.1277]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0972 | 0.2720 | -0.0015 [-0.0206, +0.0159] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0253 | 0.0159 | +0.0329 [+0.0223, +0.0434] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [+0.0001, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0354 | 0.1165 | +0.0158 [+0.0016, +0.0330] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0072 | 0.0031 | +0.0290 [+0.0225, +0.0354] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0352 | 0.4146 | -0.0002 [-0.0278, +0.0371] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.565 | 0.1006 | 0.2474 | +0.0080 [-0.0097, +0.0247] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0983 | 0.1133 | +0.0339 [+0.0115, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0128 | 0.0630 | +0.0052 [+0.0001, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1101 [+0.0294, +0.1928] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1197 | 0.1461 | +0.0681 [+0.0463, +0.0927] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2084 | 0.2213 |

## risk_gbm_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.769] | 0.286 | 6.08 flat / 2.76 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.619] | 0.254 | 4.46 flat / 1.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.923 [1.909, 4.364] | 1.192 [0.727, 1.904] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.923 [1.806, 4.462] | 1.154 [0.707, 1.792] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 2.885 [1.636, 4.643] | 1.231 [0.636, 2.087] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.808 [1.034, 2.900] | 0.606 [0.342, 0.977] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.387] | 2.654 [1.538, 4.304] | 1.038 [0.600, 1.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.118 [3.749, 9.819] | 2.574 [1.428, 4.340] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.000 (no interval) | 3.111 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 157 | 0.579 | 0.516 | 0.0493 | +0.0221 [+0.0150, +0.0301] | +0.0071 [+0.0024, +0.0121] | 0.896 | 0.535 | yes |
| 2 | 0.315 (147 of 1872 days never flag) | 136 | 0.432 | 0.441 | 0.0605 | +0.0105 [+0.0064, +0.0147] | +0.0005 [-0.0026, +0.0036] | 0.827 | 0.388 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 134 | 0.428 | 0.440 | 0.0616 | +0.0091 [+0.0053, +0.0128] | +0.0027 [-0.0002, +0.0057] | 0.803 | 0.384 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 101 | 0.391 | 0.535 | 0.0594 | +0.0115 [+0.0069, +0.0160] | +0.0030 [+0.0001, +0.0063] | 0.833 | 0.364 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 119 | 0.362 | 0.420 | 0.0630 | +0.0080 [+0.0035, +0.0121] | +0.0004 [-0.0027, +0.0034] | 0.782 | 0.322 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.470 (climatology 0.457, difference +0.0128 [-0.1151, +0.1356]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0858, ΔBrier vs climatology +0.0437 [+0.0298, +0.0593], realised minus predicted +0.0101 [-0.0214, +0.0449]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0542 [+0.0257, +0.0845] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1280 | 0.0159 | +0.0166 [+0.0011, +0.0300] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0321 | 0.0200 | +0.0008 [-0.0060, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.522 | 0.1117 | 0.1165 | +0.0278 [+0.0022, +0.0605] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0217 | 0.0048 | +0.0082 [+0.0060, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0717 | 0.0031 | +0.0216 [+0.0151, +0.0276] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.500 | 0.2195 | 0.4146 | 0.0692 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.524 | 0.2469 | 0.2474 | +0.0489 [+0.0240, +0.0753] |
| day_type | month_end | 150 | 17 | 0.588 | 0.526 | 0.1076 | 0.1133 | +0.0390 [+0.0158, +0.0634] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.479 | 0.0863 | 0.0630 | +0.0163 [+0.0092, +0.0242] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0330, +0.1908] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0467, +0.0928] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.77 flat / 2.58 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.520] | 0.242 | 4.35 flat / 1.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 2.500 [1.655, 3.765] | 0.952 [0.613, 1.477] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.615 [1.633, 3.950] | 1.029 [0.631, 1.563] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.885 [1.739, 4.500] | 1.115 [0.686, 1.750] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 2.154 [1.333, 3.333] | 0.837 [0.520, 1.338] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.121, 0.435] | 2.346 [1.400, 3.696] | 0.990 [0.591, 1.583] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 5.000 [3.056, 8.167] | 1.882 [1.125, 3.200] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 7.222 (no interval) | 3.889 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 136 | 0.507 | 0.522 | 0.0511 | +0.0203 [+0.0135, +0.0272] | +0.0052 [+0.0007, +0.0098] | 0.805 | 0.470 | no |
| 2 | 0.315 (147 of 1872 days never flag) | 122 | 0.388 | 0.443 | 0.0628 | +0.0083 [+0.0035, +0.0129] | -0.0017 [-0.0059, +0.0021] | 0.748 | 0.349 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 130 | 0.399 | 0.423 | 0.0617 | +0.0090 [+0.0040, +0.0138] | +0.0027 [-0.0017, +0.0065] | 0.745 | 0.355 | no |
| 4 | 0.265 (147 of 1870 days never flag) | 109 | 0.384 | 0.486 | 0.0602 | +0.0106 [+0.0055, +0.0155] | +0.0021 [-0.0015, +0.0055] | 0.761 | 0.352 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 107 | 0.333 | 0.430 | 0.0636 | +0.0073 [+0.0021, +0.0122] | -0.0002 [-0.0043, +0.0036] | 0.740 | 0.298 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.457, difference +0.0407 [-0.0963, +0.1618]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0878, ΔBrier vs climatology +0.0417 [+0.0289, +0.0553], realised minus predicted +0.0592 [+0.0303, +0.0907]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.559 | 0.1689 | 0.2720 | +0.0386 [+0.0127, +0.0658] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0329 | 0.0159 | +0.0256 [+0.0080, +0.0396] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0145 | 0.0200 | +0.0009 [-0.0065, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.522 | 0.0867 | 0.1165 | +0.0269 [+0.0031, +0.0546] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0076 | 0.0048 | +0.0084 [+0.0062, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0121 | 0.0031 | +0.0276 [+0.0203, +0.0338] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.500 | 0.1906 | 0.4146 | 0.0671 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.533 | 0.1693 | 0.2474 | +0.0372 [+0.0134, +0.0612] |
| day_type | month_end | 150 | 17 | 0.588 | 0.526 | 0.1021 | 0.1133 | +0.0395 [+0.0145, +0.0650] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.480 | 0.0421 | 0.0630 | +0.0141 [+0.0076, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0304, +0.1894] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0458, +0.0933] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3903 | 0.2213 |

## risk_gbm_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.765] | 0.269 | 5.77 flat / 2.62 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.565] | 0.250 | 4.42 flat / 1.98 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.650] | 2.500 [1.560, 3.870] | 1.058 [0.661, 1.641] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.462] | 2.808 [1.775, 4.300] | 1.106 [0.685, 1.750] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 2.885 [1.667, 4.696] | 1.240 [0.666, 2.145] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.474] | 2.500 [1.390, 4.087] | 0.933 [0.500, 1.525] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.385 [1.517, 3.692] | 1.048 [0.635, 1.671] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 6.471 [4.000, 10.309] | 2.632 [1.538, 4.438] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 135 | 0.500 | 0.519 | 0.0493 | +0.0221 [+0.0157, +0.0295] | +0.0070 [+0.0025, +0.0120] | 0.891 | 0.462 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 134 | 0.439 | 0.455 | 0.0598 | +0.0112 [+0.0080, +0.0146] | +0.0012 [-0.0022, +0.0047] | 0.810 | 0.397 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 130 | 0.399 | 0.423 | 0.0602 | +0.0105 [+0.0072, +0.0141] | +0.0042 [+0.0007, +0.0081] | 0.793 | 0.355 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 120 | 0.399 | 0.458 | 0.0577 | +0.0131 [+0.0094, +0.0167] | +0.0047 [+0.0017, +0.0078] | 0.829 | 0.361 | no |
| 5 | 0.265 (147 of 1869 days never flag) | 113 | 0.370 | 0.451 | 0.0613 | +0.0096 [+0.0062, +0.0129] | +0.0021 [-0.0010, +0.0050] | 0.773 | 0.334 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.470 (climatology 0.457, difference +0.0128 [-0.1139, +0.1291]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0870, ΔBrier vs climatology +0.0424 [+0.0291, +0.0571], realised minus predicted +0.0202 [-0.0111, +0.0560]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.523 | 0.2205 | 0.2720 | +0.0484 [+0.0229, +0.0773] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1155 | 0.0159 | +0.0222 [+0.0095, +0.0341] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0155 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0227 | 0.0200 | +0.0029 [-0.0014, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.647 | 0.0952 | 0.1165 | +0.0279 [+0.0056, +0.0558] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0168 | 0.0048 | +0.0089 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0615 | 0.0031 | +0.0238 [+0.0178, +0.0297] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1795 | 0.4146 | 0.0631 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.516 | 0.2283 | 0.2474 | +0.0463 [+0.0232, +0.0723] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.1062 | 0.1133 | +0.0381 [+0.0148, +0.0630] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.474 | 0.0747 | 0.0630 | +0.0163 [+0.0102, +0.0236] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0330, +0.1898] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1197 | 0.1461 | +0.0681 [+0.0457, +0.0916] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0837 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2566 | 0.2213 |

## risk_gbm_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.769] | 0.278 | 5.92 flat / 2.68 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.242 | 4.35 flat / 1.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.885 [1.882, 4.295] | 1.183 [0.750, 1.893] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.000 [1.906, 4.522] | 1.183 [0.761, 1.813] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.520] | 3.000 [1.750, 4.778] | 1.260 [0.690, 2.103] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.885 [1.038, 3.077] | 0.615 [0.341, 1.000] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.577 [1.448, 4.131] | 0.981 [0.558, 1.565] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.118 [3.818, 9.909] | 2.574 [1.515, 4.344] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 5.556 [3.286, 10.573] | 2.889 [1.682, 6.000] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 156 | 0.579 | 0.519 | 0.0486 | +0.0228 [+0.0157, +0.0304] | +0.0077 [+0.0033, +0.0127] | 0.912 | 0.535 | yes |
| 2 | 0.315 (147 of 1872 days never flag) | 139 | 0.439 | 0.439 | 0.0598 | +0.0113 [+0.0069, +0.0155] | +0.0013 [-0.0017, +0.0044] | 0.870 | 0.394 | yes |
| 3 | 0.458 (147 of 1871 days never flag) | 138 | 0.435 | 0.435 | 0.0599 | +0.0108 [+0.0072, +0.0147] | +0.0045 [+0.0016, +0.0074] | 0.855 | 0.390 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 105 | 0.406 | 0.533 | 0.0581 | +0.0128 [+0.0087, +0.0172] | +0.0043 [+0.0015, +0.0075] | 0.869 | 0.378 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 117 | 0.362 | 0.427 | 0.0620 | +0.0090 [+0.0048, +0.0131] | +0.0014 [-0.0017, +0.0045] | 0.844 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.470 (climatology 0.457, difference +0.0128 [-0.1137, +0.1261]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0449 [+0.0312, +0.0600], realised minus predicted +0.0367 [+0.0059, +0.0695]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0542 [+0.0277, +0.0836] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1280 | 0.0159 | +0.0166 [+0.0013, +0.0311] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0045 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [-0.0002, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.522 | 0.0981 | 0.1165 | +0.0286 [+0.0038, +0.0577] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0009 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0717 | 0.0031 | +0.0216 [+0.0153, +0.0276] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.500 | 0.2195 | 0.4146 | 0.0692 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.524 | 0.2469 | 0.2474 | +0.0489 [+0.0239, +0.0764] |
| day_type | month_end | 150 | 17 | 0.588 | 0.526 | 0.1056 | 0.1133 | +0.0391 [+0.0146, +0.0638] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.483 | 0.0731 | 0.0630 | +0.0171 [+0.0102, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0303, +0.1887] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0458, +0.0909] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 3.58 flat / 1.80 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.130, 0.424] | 0.192 | 2.00 flat / 1.08 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.645] | 2.154 [1.457, 3.263] | 0.923 [0.609, 1.457] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 1.269 [0.815, 1.957] | 0.558 [0.300, 0.957] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.077 [0.636, 1.714] | 0.462 [0.236, 0.831] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.115 [0.682, 1.727] | 0.462 [0.250, 0.786] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.100, 0.379] | 1.423 [0.912, 2.263] | 0.769 [0.430, 1.307] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.812] | 2.706 [1.636, 4.556] | 1.044 [0.604, 1.808] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 5.222 [3.111, 10.667] | 3.222 [1.750, 7.083] |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 121 | 0.464 | 0.537 | 0.0498 | +0.0216 [+0.0164, +0.0270] | +0.0065 [+0.0017, +0.0109] | 0.905 | 0.432 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 65 | 0.230 | 0.492 | 0.0608 | +0.0103 [+0.0070, +0.0134] | +0.0003 [-0.0041, +0.0040] | 0.836 | 0.211 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 53 | 0.181 | 0.472 | 0.0608 | +0.0098 [+0.0064, +0.0132] | +0.0035 [-0.0006, +0.0073] | 0.812 | 0.165 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 57 | 0.203 | 0.491 | 0.0592 | +0.0116 [+0.0080, +0.0152] | +0.0032 [-0.0007, +0.0067] | 0.838 | 0.186 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 61 | 0.174 | 0.393 | 0.0624 | +0.0085 [+0.0051, +0.0118] | +0.0010 [-0.0028, +0.0044] | 0.791 | 0.153 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.462 (climatology 0.457, difference +0.0047 [-0.1137, +0.1288]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0912, ΔBrier vs climatology +0.0382 [+0.0274, +0.0494], realised minus predicted +0.0513 [+0.0181, +0.0868]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.576 | 0.1679 | 0.2720 | +0.0397 [+0.0236, +0.0565] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0767 | 0.0159 | +0.0298 [+0.0191, +0.0399] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0032 [-0.0013, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0736 | 0.1165 | +0.0284 [+0.0062, +0.0551] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0113 | 0.0048 | +0.0091 [+0.0073, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0394 | 0.0031 | +0.0272 [+0.0210, +0.0330] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.600 | 0.1273 | 0.4146 | +0.0558 [-0.0078, +0.1172] |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.550 | 0.1737 | 0.2474 | +0.0421 [+0.0258, +0.0585] |
| day_type | month_end | 150 | 17 | 0.647 | 0.500 | 0.1030 | 0.1133 | +0.0368 [+0.0140, +0.0590] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.513 | 0.0496 | 0.0630 | +0.0159 [+0.0116, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2030 | 0.2903 | +0.1101 [+0.0335, +0.1910] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1197 | 0.1461 | +0.0681 [+0.0447, +0.0917] |

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
| 1 | 0.681 (105 of 1873 days never flag) | 134 | 0.507 | 0.530 | 0.0621 | +0.0093 [-0.0004, +0.0185] | -0.0058 [-0.0144, +0.0021] | 0.873 | 0.471 | no |
| 2 | 0.603 (147 of 1872 days never flag) | 109 | 0.374 | 0.477 | 0.0720 | -0.0010 [-0.0101, +0.0068] | -0.0110 [-0.0197, -0.0036] | 0.813 | 0.341 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 121 | 0.399 | 0.455 | 0.0736 | -0.0030 [-0.0119, +0.0047] | -0.0093 [-0.0179, -0.0016] | 0.791 | 0.360 | no |
| 4 | 0.643 (147 of 1870 days never flag) | 95 | 0.355 | 0.516 | 0.0702 | +0.0006 [-0.0064, +0.0073] | -0.0078 [-0.0144, -0.0014] | 0.818 | 0.329 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 102 | 0.355 | 0.480 | 0.0728 | -0.0019 [-0.0084, +0.0035] | -0.0094 [-0.0157, -0.0040] | 0.770 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.444 (climatology 0.457, difference -0.0128 [-0.1462, +0.1177]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0945, ΔBrier vs climatology +0.0350 [+0.0212, +0.0497], realised minus predicted +0.0052 [-0.0306, +0.0422]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.3131 | 0.2720 | +0.0099 [-0.0341, +0.0495] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2026 | 0.0159 | -0.0107 [-0.0348, +0.0082] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0027 [-0.0027, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0652 | 0.1165 | +0.0271 [+0.0049, +0.0550] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0061 | 0.0048 | +0.0087 [+0.0069, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1125 | 0.0031 | +0.0096 [+0.0039, +0.0152] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1454 | 0.4146 | +0.0534 [-0.0190, +0.1306] |
| scarcity_state | 3 | 473 | 117 | 0.598 | 0.526 | 0.3152 | 0.2474 | +0.0067 [-0.0323, +0.0409] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1090 | 0.1133 | +0.0364 [+0.0123, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.490 | 0.1026 | 0.0630 | +0.0016 [-0.0087, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0293, +0.1890] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1197 | 0.1461 | +0.0681 [+0.0460, +0.0905] |

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
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.077 [1.742, 4.862] | 1.183 [0.674, 1.889] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.379] | 2.269 [1.148, 3.728] | 0.808 [0.402, 1.357] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.136, 0.483] | 2.462 [1.185, 4.139] | 0.817 [0.383, 1.398] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.378] | 1.846 [0.842, 3.218] | 0.625 [0.284, 1.119] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.154 [1.062, 3.694] | 0.769 [0.378, 1.327] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.958] | 5.176 [3.083, 8.385] | 1.971 [1.148, 3.306] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.667 [0.750, 3.625] | 0.833 [0.333, 1.959] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 159 | 0.564 | 0.497 | 0.0624 | +0.0090 [-0.0007, +0.0184] | -0.0061 [-0.0143, +0.0013] | 0.871 | 0.518 | no |
| 2 | 0.607 (147 of 1872 days never flag) | 109 | 0.360 | 0.459 | 0.0723 | -0.0013 [-0.0097, +0.0065] | -0.0113 [-0.0193, -0.0038] | 0.810 | 0.326 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 119 | 0.399 | 0.462 | 0.0730 | -0.0023 [-0.0123, +0.0056] | -0.0086 [-0.0182, -0.0011] | 0.793 | 0.362 | no |
| 4 | 0.588 (147 of 1870 days never flag) | 98 | 0.362 | 0.510 | 0.0713 | -0.0005 [-0.0080, +0.0065] | -0.0089 [-0.0161, -0.0021] | 0.814 | 0.335 | yes |
| 5 | 0.575 (147 of 1869 days never flag) | 105 | 0.355 | 0.467 | 0.0728 | -0.0019 [-0.0081, +0.0038] | -0.0094 [-0.0154, -0.0038] | 0.772 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.448 (climatology 0.457, difference -0.0088 [-0.1372, +0.1229]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0927, ΔBrier vs climatology +0.0368 [+0.0223, +0.0534], realised minus predicted +0.0048 [-0.0292, +0.0415]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.487 | 0.3159 | 0.2720 | +0.0093 [-0.0342, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1987 | 0.0159 | -0.0092 [-0.0324, +0.0093] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0046 | 0.0200 | +0.0000 [-0.0063, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0597 | 0.1165 | +0.0266 [+0.0053, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0055 | 0.0048 | +0.0081 [+0.0061, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1095 | 0.0031 | +0.0105 [+0.0046, +0.0165] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1388 | 0.4146 | +0.0500 [-0.0209, +0.1222] |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.497 | 0.3156 | 0.2474 | +0.0063 [-0.0307, +0.0426] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1062 | 0.1133 | +0.0404 [+0.0198, +0.0623] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.450 | 0.1030 | 0.0630 | +0.0008 [-0.0099, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0190, +0.1808] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1094 | 0.1461 | +0.0713 [+0.0482, +0.0942] |

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
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 2.115 [1.000, 3.783] | 0.846 [0.432, 1.467] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 1.962 [1.036, 3.333] | 0.798 [0.435, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 4.529 [2.562, 7.644] | 1.824 [1.042, 3.146] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.889 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (105 of 1873 days never flag) | 134 | 0.507 | 0.530 | 0.0621 | +0.0093 [-0.0004, +0.0185] | -0.0058 [-0.0142, +0.0019] | 0.873 | 0.471 | no |
| 2 | 0.599 (147 of 1872 days never flag) | 104 | 0.424 | 0.567 | 0.0657 | +0.0054 [-0.0040, +0.0145] | -0.0047 [-0.0140, +0.0038] | 0.841 | 0.398 | no |
| 3 | 0.593 (147 of 1871 days never flag) | 115 | 0.435 | 0.522 | 0.0677 | +0.0030 [-0.0065, +0.0118] | -0.0033 [-0.0128, +0.0054] | 0.825 | 0.403 | yes |
| 4 | 0.765 (147 of 1870 days never flag) | 116 | 0.442 | 0.526 | 0.0652 | +0.0057 [-0.0028, +0.0132] | -0.0028 [-0.0112, +0.0047] | 0.842 | 0.410 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 104 | 0.384 | 0.510 | 0.0665 | +0.0045 [-0.0025, +0.0110] | -0.0031 [-0.0102, +0.0033] | 0.822 | 0.355 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2234 [+0.0692, +0.3738]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0234, +0.0665], realised minus predicted -0.0205 [-0.0526, +0.0125]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.3131 | 0.2720 | +0.0099 [-0.0329, +0.0526] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2026 | 0.0159 | -0.0107 [-0.0349, +0.0084] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0027 [-0.0021, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0652 | 0.1165 | +0.0271 [+0.0046, +0.0541] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0061 | 0.0048 | +0.0087 [+0.0069, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1125 | 0.0031 | +0.0096 [+0.0041, +0.0155] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1454 | 0.4146 | 0.0534 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.598 | 0.526 | 0.3152 | 0.2474 | +0.0067 [-0.0311, +0.0421] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1090 | 0.1133 | +0.0364 [+0.0131, +0.0593] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.490 | 0.1026 | 0.0630 | +0.0016 [-0.0090, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0319, +0.1905] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1197 | 0.1461 | +0.0681 [+0.0459, +0.0921] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2962 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.345, 0.727] | 0.231 | 3.77 flat / 1.58 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.231, 0.611] | 0.192 | 2.38 flat / 0.99 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 3.077 [1.724, 5.000] | 1.183 [0.667, 1.920] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.231 [1.100, 3.950] | 0.827 [0.425, 1.427] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.615 [0.725, 2.900] | 0.625 [0.307, 1.109] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.885 [0.896, 3.318] | 0.769 [0.392, 1.326] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.077 [0.968, 3.750] | 0.827 [0.423, 1.429] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.882 [2.850, 8.314] | 1.926 [1.104, 3.312] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 0.917 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 159 | 0.564 | 0.497 | 0.0624 | +0.0090 [-0.0006, +0.0186] | -0.0061 [-0.0141, +0.0017] | 0.871 | 0.518 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 118 | 0.432 | 0.508 | 0.0657 | +0.0054 [-0.0034, +0.0140] | -0.0046 [-0.0133, +0.0035] | 0.837 | 0.398 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 94 | 0.377 | 0.553 | 0.0676 | +0.0031 [-0.0061, +0.0117] | -0.0033 [-0.0123, +0.0051] | 0.823 | 0.353 | yes |
| 4 | 0.713 (147 of 1870 days never flag) | 107 | 0.420 | 0.542 | 0.0655 | +0.0054 [-0.0031, +0.0139] | -0.0031 [-0.0111, +0.0055] | 0.841 | 0.392 | yes |
| 5 | 0.601 (147 of 1869 days never flag) | 116 | 0.449 | 0.534 | 0.0652 | +0.0057 [-0.0012, +0.0126] | -0.0018 [-0.0086, +0.0053] | 0.820 | 0.418 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.457, difference +0.2625 [+0.0822, +0.4394]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0837, ΔBrier vs climatology +0.0458 [+0.0266, +0.0664], realised minus predicted -0.0190 [-0.0502, +0.0138]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.487 | 0.3159 | 0.2720 | +0.0093 [-0.0343, +0.0511] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1987 | 0.0159 | -0.0092 [-0.0314, +0.0102] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0105, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0046 | 0.0200 | +0.0000 [-0.0058, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0597 | 0.1165 | +0.0266 [+0.0053, +0.0536] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0055 | 0.0048 | +0.0081 [+0.0061, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1095 | 0.0031 | +0.0105 [+0.0044, +0.0166] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1388 | 0.4146 | 0.0500 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.497 | 0.3156 | 0.2474 | +0.0063 [-0.0311, +0.0435] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1062 | 0.1133 | +0.0404 [+0.0188, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.450 | 0.1030 | 0.0630 | +0.0008 [-0.0098, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0160, +0.1802] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1094 | 0.1461 | +0.0713 [+0.0478, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.769] | 0.269 | 5.12 flat / 2.28 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.231 | 4.23 flat / 1.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.731 [1.667, 4.182] | 1.106 [0.670, 1.776] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 2.654 [1.500, 4.084] | 0.990 [0.552, 1.539] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.538 [1.272, 4.227] | 0.913 [0.472, 1.517] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.471] | 2.385 [1.241, 4.050] | 0.817 [0.414, 1.375] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 3.038 [1.520, 5.159] | 1.308 [0.609, 2.380] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 6.412 [3.900, 10.211] | 2.735 [1.571, 4.728] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 1.417 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 150 | 0.564 | 0.527 | 0.0576 | +0.0139 [+0.0064, +0.0218] | -0.0012 [-0.0075, +0.0047] | 0.850 | 0.523 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 117 | 0.345 | 0.410 | 0.0702 | +0.0009 [-0.0045, +0.0061] | -0.0091 [-0.0150, -0.0036] | 0.767 | 0.306 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 122 | 0.406 | 0.459 | 0.0710 | -0.0003 [-0.0049, +0.0040] | -0.0066 [-0.0115, -0.0020] | 0.718 | 0.368 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 118 | 0.406 | 0.475 | 0.0691 | +0.0017 [-0.0035, +0.0066] | -0.0068 [-0.0118, -0.0018] | 0.760 | 0.370 | yes |
| 5 | 0.498 (147 of 1869 days never flag) | 130 | 0.370 | 0.392 | 0.0728 | -0.0019 [-0.0074, +0.0032] | -0.0094 [-0.0153, -0.0039] | 0.709 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.436 (climatology 0.457, difference -0.0210 [-0.1556, +0.1142]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0976, ΔBrier vs climatology +0.0319 [+0.0184, +0.0460], realised minus predicted -0.0125 [-0.0489, +0.0262]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.519 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0687] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2107 | 0.0159 | -0.0087 [-0.0246, +0.0052] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0027 [-0.0030, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0639 | 0.1165 | +0.0249 [+0.0060, +0.0489] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0194 | 0.0048 | +0.0082 [+0.0065, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1313 | 0.0031 | +0.0045 [-0.0009, +0.0100] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1305 | 0.4146 | 0.0343 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.524 | 0.2893 | 0.2474 | +0.0308 [+0.0018, +0.0611] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1097 | 0.1133 | +0.0356 [+0.0138, +0.0591] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.491 | 0.1069 | 0.0630 | +0.0069 [-0.0006, +0.0151] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0322, +0.1868] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1197 | 0.1461 | +0.0681 [+0.0453, +0.0927] |

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
| 1 | 0.517 (105 of 1873 days never flag) | 173 | 0.600 | 0.486 | 0.0579 | +0.0135 [+0.0060, +0.0221] | -0.0016 [-0.0073, +0.0048] | 0.847 | 0.549 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 115 | 0.345 | 0.417 | 0.0705 | +0.0006 [-0.0051, +0.0061] | -0.0094 [-0.0154, -0.0036] | 0.766 | 0.307 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 121 | 0.406 | 0.463 | 0.0703 | +0.0004 [-0.0041, +0.0048] | -0.0059 [-0.0110, -0.0011] | 0.722 | 0.368 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 116 | 0.406 | 0.483 | 0.0702 | +0.0006 [-0.0046, +0.0056] | -0.0079 [-0.0130, -0.0027] | 0.756 | 0.371 | yes |
| 5 | 0.498 (147 of 1869 days never flag) | 133 | 0.377 | 0.391 | 0.0728 | -0.0019 [-0.0076, +0.0031] | -0.0094 [-0.0154, -0.0038] | 0.710 | 0.330 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.441 (climatology 0.457, difference -0.0156 [-0.1420, +0.1098]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0962, ΔBrier vs climatology +0.0333 [+0.0197, +0.0483], realised minus predicted -0.0128 [-0.0489, +0.0263]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.481 | 0.2869 | 0.2720 | +0.0353 [+0.0025, +0.0716] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2068 | 0.0159 | -0.0072 [-0.0222, +0.0071] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0091 | 0.0200 | +0.0001 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0584 | 0.1165 | +0.0245 [+0.0054, +0.0483] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0188 | 0.0048 | +0.0077 [+0.0057, +0.0094] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1283 | 0.0031 | +0.0053 [+0.0002, +0.0109] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1240 | 0.4146 | 0.0309 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.482 | 0.2897 | 0.2474 | +0.0305 [+0.0013, +0.0620] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1069 | 0.1133 | +0.0396 [+0.0202, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.441 | 0.1073 | 0.0630 | +0.0062 [-0.0013, +0.0149] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0159, +0.1835] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0482, +0.0967] |

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
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 3.38 flat / 1.50 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.594] | 2.731 [1.680, 4.308] | 1.106 [0.655, 1.792] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.192 [1.125, 3.810] | 0.856 [0.463, 1.431] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 1.962 [0.957, 3.423] | 0.798 [0.409, 1.364] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.154 [1.129, 3.692] | 0.904 [0.493, 1.524] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.846 [1.474, 4.824] | 1.288 [0.606, 2.333] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.706 [3.400, 9.445] | 2.544 [1.438, 4.470] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.222 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 150 | 0.564 | 0.527 | 0.0576 | +0.0139 [+0.0063, +0.0221] | -0.0012 [-0.0072, +0.0050] | 0.850 | 0.523 | no |
| 2 | 0.599 (147 of 1872 days never flag) | 117 | 0.432 | 0.513 | 0.0631 | +0.0080 [+0.0013, +0.0149] | -0.0020 [-0.0090, +0.0049] | 0.807 | 0.399 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 111 | 0.435 | 0.541 | 0.0645 | +0.0062 [+0.0000, +0.0126] | -0.0001 [-0.0064, +0.0061] | 0.770 | 0.405 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 114 | 0.420 | 0.509 | 0.0638 | +0.0071 [+0.0006, +0.0133] | -0.0014 [-0.0077, +0.0048] | 0.791 | 0.388 | yes |
| 5 | 0.655 (147 of 1869 days never flag) | 131 | 0.413 | 0.435 | 0.0662 | +0.0047 [-0.0018, +0.0111] | -0.0028 [-0.0095, +0.0041] | 0.775 | 0.370 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2240 [+0.0689, +0.3747]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0870, ΔBrier vs climatology +0.0425 [+0.0231, +0.0642], realised minus predicted -0.0398 [-0.0716, -0.0053]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.519 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0706] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2107 | 0.0159 | -0.0087 [-0.0247, +0.0048] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0027 [-0.0022, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0639 | 0.1165 | +0.0249 [+0.0049, +0.0488] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0194 | 0.0048 | +0.0082 [+0.0065, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1313 | 0.0031 | +0.0045 [-0.0009, +0.0101] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1305 | 0.4146 | +0.0343 [-0.0196, +0.0902] |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.524 | 0.2893 | 0.2474 | +0.0308 [+0.0013, +0.0619] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1097 | 0.1133 | +0.0356 [+0.0139, +0.0587] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.491 | 0.1069 | 0.0630 | +0.0069 [-0.0007, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0311, +0.1868] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1197 | 0.1461 | +0.0681 [+0.0445, +0.0914] |

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
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.962 [1.058, 3.353] | 0.750 [0.420, 1.250] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.769 [0.906, 3.087] | 0.692 [0.364, 1.213] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.962 [1.000, 3.400] | 0.827 [0.453, 1.398] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 3.077 [1.666, 5.276] | 1.442 [0.750, 2.524] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 6.000 [3.625, 9.779] | 2.632 [1.500, 4.625] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.556 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 173 | 0.600 | 0.486 | 0.0579 | +0.0135 [+0.0061, +0.0214] | -0.0016 [-0.0073, +0.0043] | 0.847 | 0.549 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 103 | 0.374 | 0.505 | 0.0631 | +0.0080 [+0.0013, +0.0144] | -0.0020 [-0.0086, +0.0044] | 0.803 | 0.345 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 99 | 0.384 | 0.535 | 0.0644 | +0.0063 [+0.0006, +0.0124] | -0.0001 [-0.0058, +0.0064] | 0.766 | 0.358 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 106 | 0.399 | 0.519 | 0.0640 | +0.0068 [+0.0001, +0.0135] | -0.0017 [-0.0086, +0.0054] | 0.791 | 0.369 | yes |
| 5 | 0.528 (147 of 1869 days never flag) | 142 | 0.449 | 0.437 | 0.0649 | +0.0060 [-0.0008, +0.0123] | -0.0015 [-0.0085, +0.0054] | 0.775 | 0.403 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.721 (climatology 0.457, difference +0.2638 [+0.0826, +0.4376]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0853, ΔBrier vs climatology +0.0441 [+0.0261, +0.0643], realised minus predicted -0.0384 [-0.0698, -0.0042]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.481 | 0.2869 | 0.2720 | +0.0353 [+0.0035, +0.0676] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2068 | 0.0159 | -0.0072 [-0.0222, +0.0061] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0091 | 0.0200 | +0.0001 [-0.0059, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0584 | 0.1165 | +0.0245 [+0.0051, +0.0482] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0188 | 0.0048 | +0.0077 [+0.0057, +0.0094] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1283 | 0.0031 | +0.0053 [+0.0001, +0.0112] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1240 | 0.4146 | 0.0309 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.482 | 0.2897 | 0.2474 | +0.0305 [+0.0019, +0.0600] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1069 | 0.1133 | +0.0396 [+0.0185, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.441 | 0.1073 | 0.0630 | +0.0062 [-0.0013, +0.0146] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0179, +0.1780] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0485, +0.0953] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2851 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.700] | 0.231 | 3.31 flat / 1.28 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.485] | 0.231 | 2.73 flat / 0.96 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.654] | 2.692 [1.438, 4.400] | 0.990 [0.554, 1.593] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 1.846 [0.826, 3.200] | 0.702 [0.310, 1.235] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.105, 0.444] | 2.500 [1.227, 4.231] | 0.875 [0.425, 1.500] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 1.692 [0.750, 3.126] | 0.548 [0.227, 1.050] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 1.846 [0.810, 3.286] | 0.625 [0.274, 1.125] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.882] | 4.471 [2.588, 7.333] | 1.603 [0.940, 2.659] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 1.111 [0.312, 2.667] | 0.667 [0.156, 1.875] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (105 of 1873 days never flag) | 145 | 0.536 | 0.517 | 0.0615 | +0.0099 [-0.0012, +0.0199] | -0.0052 [-0.0151, +0.0036] | 0.891 | 0.495 | yes |
| 2 | 0.603 (147 of 1872 days never flag) | 95 | 0.338 | 0.495 | 0.0697 | +0.0014 [-0.0082, +0.0090] | -0.0086 [-0.0178, -0.0009] | 0.840 | 0.310 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 124 | 0.428 | 0.476 | 0.0696 | +0.0011 [-0.0084, +0.0093] | -0.0052 [-0.0143, +0.0030] | 0.843 | 0.390 | no |
| 4 | 0.643 (147 of 1870 days never flag) | 88 | 0.319 | 0.500 | 0.0667 | +0.0041 [-0.0033, +0.0106] | -0.0043 [-0.0116, +0.0021] | 0.841 | 0.293 | no |
| 5 | 0.683 (147 of 1869 days never flag) | 96 | 0.348 | 0.500 | 0.0735 | -0.0026 [-0.0118, +0.0055] | -0.0101 [-0.0192, -0.0020] | 0.803 | 0.320 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.455 (climatology 0.457, difference -0.0025 [-0.1209, +0.1303]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0912, ΔBrier vs climatology +0.0383 [+0.0240, +0.0540], realised minus predicted +0.0232 [-0.0107, +0.0596]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.504 | 0.3157 | 0.2720 | +0.0027 [-0.0475, +0.0470] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1522 | 0.0159 | +0.0048 [-0.0218, +0.0271] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0088 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0038 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0672 | 0.1165 | +0.0232 [+0.0050, +0.0471] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0018 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0686 | 0.0031 | +0.0227 [+0.0165, +0.0291] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0954 | 0.4146 | 0.0308 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.632 | 0.514 | 0.3226 | 0.2474 | +0.0003 [-0.0404, +0.0396] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1077 | 0.1133 | +0.0369 [+0.0150, +0.0607] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.478 | 0.0920 | 0.0630 | +0.0022 [-0.0100, +0.0129] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0346, +0.1904] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1197 | 0.1461 | +0.0681 [+0.0455, +0.0919] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2821 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.765] | 0.231 | 3.58 flat / 1.30 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.148, 0.483] | 0.231 | 2.65 flat / 0.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 3.115 [1.765, 5.100] | 1.106 [0.628, 1.803] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.118, 0.438] | 1.923 [0.919, 3.364] | 0.721 [0.341, 1.271] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.500] | 2.423 [1.200, 4.200] | 0.798 [0.379, 1.403] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.692 [0.764, 3.092] | 0.548 [0.235, 1.022] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 1.923 [0.893, 3.381] | 0.644 [0.292, 1.147] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.000 [2.956, 8.250] | 1.794 [1.080, 2.978] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 0.889 [0.200, 2.000] | 0.361 [0.075, 0.900] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 161 | 0.571 | 0.497 | 0.0619 | +0.0095 [-0.0009, +0.0198] | -0.0055 [-0.0154, +0.0031] | 0.891 | 0.525 | no |
| 2 | 0.607 (147 of 1872 days never flag) | 95 | 0.324 | 0.474 | 0.0700 | +0.0011 [-0.0078, +0.0088] | -0.0089 [-0.0176, -0.0010] | 0.838 | 0.295 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 123 | 0.435 | 0.488 | 0.0689 | +0.0018 [-0.0082, +0.0105] | -0.0045 [-0.0141, +0.0038] | 0.846 | 0.398 | no |
| 4 | 0.714 (147 of 1870 days never flag) | 90 | 0.333 | 0.511 | 0.0678 | +0.0030 [-0.0044, +0.0097] | -0.0054 [-0.0131, +0.0015] | 0.835 | 0.308 | no |
| 5 | 0.691 (147 of 1869 days never flag) | 99 | 0.355 | 0.495 | 0.0736 | -0.0026 [-0.0120, +0.0055] | -0.0102 [-0.0193, -0.0023] | 0.804 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.464 (climatology 0.457, difference +0.0072 [-0.1063, +0.1348]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0899, ΔBrier vs climatology +0.0396 [+0.0264, +0.0553], realised minus predicted +0.0234 [-0.0098, +0.0580]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.487 | 0.3185 | 0.2720 | +0.0021 [-0.0475, +0.0484] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1483 | 0.0159 | +0.0063 [-0.0187, +0.0282] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0090 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0010 | 0.0200 | +0.0012 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0617 | 0.1165 | +0.0227 [+0.0047, +0.0459] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0088 [+0.0070, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0656 | 0.0031 | +0.0235 [+0.0170, +0.0303] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0888 | 0.4146 | 0.0274 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.497 | 0.3230 | 0.2474 | -0.0000 [-0.0413, +0.0391] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1049 | 0.1133 | +0.0409 [+0.0199, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.454 | 0.0924 | 0.0630 | +0.0015 [-0.0106, +0.0123] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0197, +0.1816] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1094 | 0.1461 | +0.0713 [+0.0481, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2752 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.384, 0.769] | 0.231 | 3.77 flat / 1.47 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.276, 0.655] | 0.231 | 2.73 flat / 1.09 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.285, 0.647] | 2.692 [1.469, 4.348] | 0.990 [0.546, 1.574] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 2.115 [1.000, 3.549] | 0.846 [0.444, 1.375] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.038 [0.950, 3.556] | 0.827 [0.424, 1.392] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.077 [1.000, 3.566] | 0.827 [0.431, 1.375] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 2.385 [1.280, 3.846] | 0.923 [0.508, 1.464] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 5.000 [2.909, 8.274] | 1.838 [1.087, 3.031] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 0.778 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (105 of 1873 days never flag) | 145 | 0.536 | 0.517 | 0.0615 | +0.0099 [-0.0009, +0.0201] | -0.0052 [-0.0155, +0.0041] | 0.891 | 0.495 | yes |
| 2 | 0.599 (147 of 1872 days never flag) | 120 | 0.468 | 0.542 | 0.0637 | +0.0074 [-0.0020, +0.0160] | -0.0027 [-0.0120, +0.0056] | 0.864 | 0.436 | no |
| 3 | 0.593 (147 of 1871 days never flag) | 114 | 0.442 | 0.535 | 0.0644 | +0.0062 [-0.0042, +0.0155] | -0.0001 [-0.0101, +0.0094] | 0.864 | 0.411 | no |
| 4 | 0.765 (147 of 1870 days never flag) | 115 | 0.442 | 0.530 | 0.0623 | +0.0085 [+0.0007, +0.0162] | +0.0001 [-0.0081, +0.0078] | 0.857 | 0.411 | no |
| 5 | 0.69 (147 of 1869 days never flag) | 127 | 0.471 | 0.512 | 0.0678 | +0.0031 [-0.0066, +0.0118] | -0.0044 [-0.0141, +0.0041] | 0.842 | 0.435 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2234 [+0.0651, +0.3719]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0825, ΔBrier vs climatology +0.0470 [+0.0284, +0.0678], realised minus predicted -0.0027 [-0.0341, +0.0314]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.504 | 0.3157 | 0.2720 | +0.0027 [-0.0467, +0.0491] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1522 | 0.0159 | +0.0048 [-0.0228, +0.0272] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0088 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0038 [+0.0000, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0672 | 0.1165 | +0.0232 [+0.0055, +0.0452] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0018 | 0.0048 | +0.0094 [+0.0077, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0686 | 0.0031 | +0.0227 [+0.0166, +0.0290] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0954 | 0.4146 | +0.0308 [-0.0127, +0.0806] |
| scarcity_state | 3 | 473 | 117 | 0.632 | 0.514 | 0.3226 | 0.2474 | +0.0003 [-0.0413, +0.0419] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1077 | 0.1133 | +0.0369 [+0.0144, +0.0602] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.478 | 0.0920 | 0.0630 | +0.0022 [-0.0099, +0.0130] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0298, +0.1879] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1197 | 0.1461 | +0.0681 [+0.0459, +0.0920] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2821 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.774] | 0.231 | 3.62 flat / 1.41 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.676] | 0.231 | 2.50 flat / 1.01 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 3.115 [1.658, 5.000] | 1.106 [0.600, 1.750] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 2.615 [1.333, 4.333] | 0.981 [0.523, 1.600] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.500 [0.633, 2.737] | 0.587 [0.271, 1.028] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.923 [0.917, 3.334] | 0.779 [0.402, 1.345] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 2.231 [1.033, 3.834] | 0.856 [0.426, 1.447] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 4.941 [2.833, 8.333] | 1.824 [1.042, 3.025] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 1.111 [0.444, 2.500] | 0.639 [0.212, 1.625] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 161 | 0.571 | 0.497 | 0.0619 | +0.0095 [-0.0012, +0.0194] | -0.0055 [-0.0156, +0.0032] | 0.891 | 0.525 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 134 | 0.475 | 0.493 | 0.0637 | +0.0074 [-0.0016, +0.0162] | -0.0026 [-0.0115, +0.0059] | 0.862 | 0.436 | no |
| 3 | 0.652 (147 of 1871 days never flag) | 92 | 0.384 | 0.576 | 0.0644 | +0.0063 [-0.0043, +0.0154] | -0.0000 [-0.0101, +0.0086] | 0.863 | 0.362 | no |
| 4 | 0.713 (147 of 1870 days never flag) | 110 | 0.435 | 0.545 | 0.0626 | +0.0083 [+0.0001, +0.0160] | -0.0002 [-0.0083, +0.0081] | 0.856 | 0.406 | yes |
| 5 | 0.758 (147 of 1869 days never flag) | 126 | 0.493 | 0.540 | 0.0666 | +0.0043 [-0.0056, +0.0129] | -0.0032 [-0.0126, +0.0057] | 0.843 | 0.459 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.457, difference +0.2625 [+0.0816, +0.4406]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0810, ΔBrier vs climatology +0.0485 [+0.0303, +0.0695], realised minus predicted -0.0009 [-0.0330, +0.0318]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.487 | 0.3185 | 0.2720 | +0.0021 [-0.0475, +0.0464] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1483 | 0.0159 | +0.0063 [-0.0206, +0.0282] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0090 | 0.0000 | +0.0128 [+0.0111, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0010 | 0.0200 | +0.0012 [-0.0040, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0617 | 0.1165 | +0.0227 [+0.0055, +0.0456] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0088 [+0.0070, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0656 | 0.0031 | +0.0235 [+0.0172, +0.0300] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0888 | 0.4146 | 0.0274 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.497 | 0.3230 | 0.2474 | -0.0000 [-0.0419, +0.0399] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1049 | 0.1133 | +0.0409 [+0.0197, +0.0646] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.454 | 0.0924 | 0.0630 | +0.0015 [-0.0106, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0191, +0.1811] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1094 | 0.1461 | +0.0713 [+0.0494, +0.0954] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2752 | 0.2213 |

## risk_gbm_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.387, 0.769] | 0.258 | 4.46 flat / 1.91 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.92 flat / 1.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.655] | 3.192 [1.818, 5.000] | 1.183 [0.702, 1.864] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 2.654 [1.385, 4.349] | 1.115 [0.552, 1.907] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.577 [1.923, 5.750] | 1.471 [0.733, 2.524] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.471] | 2.808 [1.360, 4.715] | 1.163 [0.478, 2.125] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 3.115 [1.600, 5.087] | 1.308 [0.605, 2.315] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 6.294 [3.772, 10.004] | 2.574 [1.433, 4.376] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 1.000 [0.332, 2.432] | 0.667 [0.146, 1.938] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.63 (105 of 1873 days never flag) | 162 | 0.564 | 0.488 | 0.0550 | +0.0164 [+0.0088, +0.0252] | +0.0014 [-0.0051, +0.0077] | 0.879 | 0.516 | yes |
| 2 | 0.532 (147 of 1872 days never flag) | 118 | 0.353 | 0.415 | 0.0661 | +0.0049 [-0.0012, +0.0110] | -0.0051 [-0.0113, +0.0006] | 0.827 | 0.313 | no |
| 3 | 0.652 (147 of 1871 days never flag) | 163 | 0.507 | 0.429 | 0.0656 | +0.0050 [-0.0003, +0.0105] | -0.0013 [-0.0067, +0.0038] | 0.824 | 0.454 | no |
| 4 | 0.524 (147 of 1870 days never flag) | 128 | 0.399 | 0.430 | 0.0644 | +0.0064 [+0.0008, +0.0116] | -0.0020 [-0.0076, +0.0033] | 0.823 | 0.356 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 140 | 0.428 | 0.421 | 0.0693 | +0.0016 [-0.0040, +0.0070] | -0.0059 [-0.0121, -0.0001] | 0.776 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.444 (climatology 0.457, difference -0.0128 [-0.1269, +0.1107]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0231, +0.0518], realised minus predicted +0.0198 [-0.0150, +0.0562]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.477 | 0.2813 | 0.2720 | +0.0340 [+0.0000, +0.0712] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1752 | 0.0159 | +0.0045 [-0.0151, +0.0211] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0137 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0031 | 0.0200 | +0.0038 [+0.0002, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0648 | 0.1165 | +0.0264 [+0.0066, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0045 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0913 | 0.0031 | +0.0180 [+0.0127, +0.0235] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1027 | 0.4146 | 0.0327 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.667 | 0.484 | 0.2921 | 0.2474 | +0.0295 [-0.0002, +0.0637] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1082 | 0.1133 | +0.0369 [+0.0147, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.446 | 0.0894 | 0.0630 | +0.0099 [+0.0020, +0.0186] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0355, +0.1896] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1197 | 0.1461 | +0.0681 [+0.0452, +0.0924] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2479 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.371, 0.773] | 0.246 | 4.35 flat / 1.80 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.621] | 0.231 | 3.88 flat / 1.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.692] | 3.231 [1.846, 5.106] | 1.135 [0.639, 1.800] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 2.615 [1.292, 4.348] | 1.106 [0.509, 1.935] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.167, 0.528] | 3.500 [1.833, 5.667] | 1.394 [0.641, 2.411] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 2.846 [1.323, 4.875] | 1.173 [0.466, 2.181] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 3.192 [1.600, 5.316] | 1.356 [0.593, 2.441] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.294 [3.818, 10.336] | 2.574 [1.417, 4.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 0.667 [0.231, 1.400] | 0.333 [0.083, 0.822] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 166 | 0.586 | 0.494 | 0.0553 | +0.0161 [+0.0086, +0.0242] | +0.0010 [-0.0055, +0.0073] | 0.877 | 0.537 | no |
| 2 | 0.532 (147 of 1872 days never flag) | 116 | 0.345 | 0.414 | 0.0664 | +0.0046 [-0.0020, +0.0108] | -0.0054 [-0.0119, +0.0005] | 0.825 | 0.306 | no |
| 3 | 0.534 (147 of 1871 days never flag) | 160 | 0.500 | 0.431 | 0.0650 | +0.0057 [+0.0000, +0.0115] | -0.0006 [-0.0062, +0.0048] | 0.824 | 0.447 | no |
| 4 | 0.524 (147 of 1870 days never flag) | 131 | 0.413 | 0.435 | 0.0655 | +0.0053 [-0.0003, +0.0105] | -0.0031 [-0.0090, +0.0025] | 0.820 | 0.370 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 143 | 0.435 | 0.420 | 0.0694 | +0.0016 [-0.0035, +0.0071] | -0.0060 [-0.0116, +0.0001] | 0.777 | 0.387 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.452 (climatology 0.457, difference -0.0056 [-0.1120, +0.1108]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0914, ΔBrier vs climatology +0.0380 [+0.0244, +0.0531], realised minus predicted +0.0197 [-0.0148, +0.0579]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.477 | 0.2841 | 0.2720 | +0.0334 [+0.0003, +0.0672] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1713 | 0.0159 | +0.0060 [-0.0134, +0.0223] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0142] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0012 [-0.0039, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0593 | 0.1165 | +0.0259 [+0.0066, +0.0513] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0039 | 0.0048 | +0.0088 [+0.0068, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0883 | 0.0031 | +0.0188 [+0.0132, +0.0243] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0961 | 0.4146 | 0.0293 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.491 | 0.2926 | 0.2474 | +0.0291 [+0.0001, +0.0608] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1054 | 0.1133 | +0.0409 [+0.0204, +0.0639] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.447 | 0.0898 | 0.0630 | +0.0091 [+0.0013, +0.0172] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0167, +0.1783] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1094 | 0.1461 | +0.0713 [+0.0486, +0.0957] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2410 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.390, 0.774] | 0.246 | 4.35 flat / 1.87 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.267, 0.652] | 0.231 | 3.38 flat / 1.51 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.654] | 3.192 [1.800, 5.137] | 1.183 [0.677, 1.881] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 2.038 [0.963, 3.500] | 0.827 [0.428, 1.398] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.000 [0.909, 3.567] | 0.808 [0.398, 1.412] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.615 [1.333, 4.429] | 1.260 [0.597, 2.267] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 3.038 [1.643, 5.000] | 1.365 [0.680, 2.389] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.059 [3.599, 9.883] | 2.515 [1.396, 4.308] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.63 (105 of 1873 days never flag) | 162 | 0.564 | 0.488 | 0.0550 | +0.0164 [+0.0083, +0.0253] | +0.0014 [-0.0053, +0.0077] | 0.879 | 0.516 | yes |
| 2 | 0.599 (147 of 1872 days never flag) | 115 | 0.446 | 0.539 | 0.0595 | +0.0115 [+0.0044, +0.0192] | +0.0015 [-0.0060, +0.0085] | 0.852 | 0.415 | no |
| 3 | 0.593 (147 of 1871 days never flag) | 113 | 0.442 | 0.540 | 0.0599 | +0.0108 [+0.0037, +0.0174] | +0.0044 [-0.0021, +0.0113] | 0.846 | 0.412 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 124 | 0.406 | 0.452 | 0.0596 | +0.0112 [+0.0049, +0.0181] | +0.0028 [-0.0039, +0.0098] | 0.839 | 0.367 | no |
| 5 | 0.655 (147 of 1869 days never flag) | 140 | 0.442 | 0.436 | 0.0632 | +0.0077 [+0.0009, +0.0141] | +0.0002 [-0.0067, +0.0072] | 0.822 | 0.396 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2240 [+0.0717, +0.3694]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0823, ΔBrier vs climatology +0.0472 [+0.0277, +0.0671], realised minus predicted -0.0077 [-0.0394, +0.0252]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.477 | 0.2813 | 0.2720 | +0.0340 [-0.0004, +0.0697] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1752 | 0.0159 | +0.0045 [-0.0145, +0.0204] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0137 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0031 | 0.0200 | +0.0038 [+0.0001, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0648 | 0.1165 | +0.0264 [+0.0071, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0045 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0913 | 0.0031 | +0.0180 [+0.0126, +0.0233] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1027 | 0.4146 | 0.0327 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.667 | 0.484 | 0.2921 | 0.2474 | +0.0295 [-0.0007, +0.0620] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1082 | 0.1133 | +0.0369 [+0.0134, +0.0615] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.446 | 0.0894 | 0.0630 | +0.0099 [+0.0021, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1101 [+0.0299, +0.1854] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1197 | 0.1461 | +0.0681 [+0.0457, +0.0911] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2479 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.381, 0.774] | 0.238 | 4.27 flat / 1.88 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.667] | 0.231 | 3.31 flat / 1.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.316, 0.696] | 3.231 [1.875, 5.143] | 1.135 [0.651, 1.784] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 2.846 [1.500, 4.637] | 1.269 [0.610, 2.205] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 1.962 [0.933, 3.485] | 0.740 [0.366, 1.294] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 2.538 [1.270, 4.364] | 1.231 [0.583, 2.239] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.115 [1.692, 5.150] | 1.442 [0.750, 2.482] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.941 [3.524, 9.702] | 2.485 [1.400, 4.292] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.111 [0.500, 2.500] | 0.722 [0.271, 1.812] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 166 | 0.586 | 0.494 | 0.0553 | +0.0161 [+0.0083, +0.0239] | +0.0010 [-0.0056, +0.0071] | 0.877 | 0.537 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 135 | 0.439 | 0.452 | 0.0595 | +0.0115 [+0.0043, +0.0191] | +0.0015 [-0.0054, +0.0087] | 0.849 | 0.396 | no |
| 3 | 0.652 (147 of 1871 days never flag) | 111 | 0.435 | 0.541 | 0.0599 | +0.0108 [+0.0044, +0.0172] | +0.0045 [-0.0019, +0.0108] | 0.844 | 0.405 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 122 | 0.406 | 0.459 | 0.0599 | +0.0110 [+0.0043, +0.0179] | +0.0025 [-0.0043, +0.0098] | 0.839 | 0.368 | yes |
| 5 | 0.528 (147 of 1869 days never flag) | 150 | 0.500 | 0.460 | 0.0620 | +0.0090 [+0.0021, +0.0160] | +0.0014 [-0.0057, +0.0087] | 0.819 | 0.453 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.457, difference +0.2625 [+0.0816, +0.4334]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0810, ΔBrier vs climatology +0.0485 [+0.0294, +0.0689], realised minus predicted -0.0063 [-0.0373, +0.0258]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.477 | 0.2841 | 0.2720 | +0.0334 [-0.0013, +0.0655] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1713 | 0.0159 | +0.0060 [-0.0118, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0012 [-0.0046, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0593 | 0.1165 | +0.0259 [+0.0064, +0.0506] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0039 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0883 | 0.0031 | +0.0188 [+0.0133, +0.0244] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0961 | 0.4146 | 0.0293 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.491 | 0.2926 | 0.2474 | +0.0291 [-0.0018, +0.0589] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1054 | 0.1133 | +0.0409 [+0.0194, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.447 | 0.0898 | 0.0630 | +0.0091 [+0.0010, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0152, +0.1835] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1094 | 0.1461 | +0.0713 [+0.0488, +0.0963] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2410 | 0.2213 |

## risk_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.724] | 0.192 | 2.42 flat / 1.75 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.65 flat / 1.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.684] | 1.846 [1.243, 2.833] | 1.192 [0.727, 1.989] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.000 [0.536, 1.707] | 0.587 [0.236, 1.156] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.192 [0.694, 1.960] | 0.779 [0.387, 1.413] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.538 [0.943, 2.481] | 1.077 [0.566, 1.904] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.423 [0.871, 2.300] | 0.933 [0.483, 1.643] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.222 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.105 (105 of 1873 days never flag) | 91 | 0.307 | 0.473 | 0.0606 | +0.0108 [+0.0056, +0.0158] | -0.0043 [-0.0128, +0.0035] | 0.642 | 0.279 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 54 | 0.201 | 0.519 | 0.0676 | +0.0035 [-0.0030, +0.0092] | -0.0065 [-0.0146, +0.0005] | 0.579 | 0.186 | no |
| 3 | 0.0841 (147 of 1871 days never flag) | 59 | 0.203 | 0.475 | 0.0689 | +0.0018 [-0.0055, +0.0085] | -0.0045 [-0.0134, +0.0031] | 0.579 | 0.185 | no |
| 4 | 0.107 (147 of 1870 days never flag) | 66 | 0.188 | 0.394 | 0.0688 | +0.0020 [-0.0047, +0.0081] | -0.0065 [-0.0150, +0.0012] | 0.578 | 0.165 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 59 | 0.159 | 0.373 | 0.0690 | +0.0019 [-0.0052, +0.0083] | -0.0056 [-0.0140, +0.0017] | 0.577 | 0.138 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.457, difference +0.1155 [-0.0282, +0.2340]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0220 [+0.0108, +0.0330], realised minus predicted +0.0748 [+0.0408, +0.1112]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1074 | 0.2720 | -0.0026 [-0.0240, +0.0179] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0308 | 0.0159 | +0.0252 [+0.0095, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0059 | 0.0200 | +0.0050 [+0.0008, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0332 | 0.1165 | +0.0133 [+0.0003, +0.0294] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0069 | 0.0031 | +0.0280 [+0.0221, +0.0336] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0360 | 0.4146 | 0.0046 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.506 | 0.1081 | 0.2474 | +0.0032 [-0.0160, +0.0217] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1022 | 0.1133 | +0.0282 [+0.0011, +0.0563] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.455 | 0.0126 | 0.0630 | +0.0040 [-0.0012, +0.0088] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3561 | 0.2903 | +0.0892 [+0.0158, +0.1596] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1296 | 0.1461 | +0.0774 [+0.0463, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2020 | 0.2213 |

## risk_logistic+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 4.77 flat / 2.18 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.517] | 0.231 | 3.38 flat / 1.46 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.417] | 2.385 [1.556, 3.563] | 1.000 [0.625, 1.547] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.538 [0.937, 2.455] | 0.663 [0.375, 1.125] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.154 [0.656, 1.889] | 0.567 [0.283, 1.056] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.231 [0.710, 2.000] | 0.548 [0.286, 0.974] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.692 [1.613, 4.207] | 1.096 [0.648, 1.741] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.437, 0.867] | 3.941 [2.411, 6.358] | 1.368 [0.812, 2.215] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.333 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 130 | 0.486 | 0.523 | 0.0507 | +0.0207 [+0.0134, +0.0281] | +0.0056 [-0.0002, +0.0112] | 0.879 | 0.450 | yes |
| 2 | 0.366 (147 of 1872 days never flag) | 75 | 0.252 | 0.467 | 0.0590 | +0.0120 [+0.0064, +0.0180] | +0.0020 [-0.0025, +0.0065] | 0.841 | 0.229 | yes |
| 3 | 0.366 (147 of 1871 days never flag) | 61 | 0.225 | 0.508 | 0.0628 | +0.0079 [+0.0015, +0.0142] | +0.0016 [-0.0047, +0.0073] | 0.812 | 0.207 | yes |
| 4 | 0.498 (147 of 1870 days never flag) | 66 | 0.246 | 0.515 | 0.0614 | +0.0094 [+0.0034, +0.0152] | +0.0010 [-0.0046, +0.0065] | 0.819 | 0.228 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 132 | 0.449 | 0.470 | 0.0623 | +0.0086 [+0.0037, +0.0137] | +0.0011 [-0.0032, +0.0053] | 0.796 | 0.409 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0285, +0.2530]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0883, ΔBrier vs climatology +0.0412 [+0.0257, +0.0584], realised minus predicted -0.0048 [-0.0344, +0.0272]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.583 | 0.2488 | 0.2720 | +0.0531 [+0.0255, +0.0814] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1335 | 0.0159 | +0.0089 [-0.0140, +0.0258] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0190 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0359 | 0.0200 | +0.0019 [-0.0049, +0.0081] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.1095 | 0.1165 | +0.0252 [+0.0011, +0.0534] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0240 | 0.0048 | +0.0079 [+0.0056, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0715 | 0.0031 | +0.0206 [+0.0145, +0.0260] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.2203 | 0.4146 | 0.0739 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.538 | 0.548 | 0.2543 | 0.2474 | +0.0441 [+0.0164, +0.0687] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1115 | 0.1133 | +0.0333 [+0.0061, +0.0619] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.500 | 0.0861 | 0.0630 | +0.0151 [+0.0083, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0129, +0.1670] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0469, +0.1125] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3400 | 0.2213 |

## risk_logistic+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.720] | 0.269 | 5.35 flat / 2.44 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.219, 0.548] | 0.231 | 3.73 flat / 1.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.346 [1.583, 3.435] | 1.029 [0.664, 1.615] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.385] | 1.538 [0.928, 2.412] | 0.663 [0.375, 1.110] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 1.577 [0.862, 2.633] | 0.692 [0.367, 1.207] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.192 [0.677, 1.944] | 0.538 [0.275, 0.950] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.478] | 3.000 [1.756, 4.667] | 1.212 [0.720, 1.903] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.481, 0.920] | 4.824 [2.866, 7.667] | 1.765 [1.062, 2.840] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.333 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (105 of 1873 days never flag) | 123 | 0.443 | 0.504 | 0.0525 | +0.0189 [+0.0122, +0.0264] | +0.0038 [-0.0018, +0.0096] | 0.801 | 0.408 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 75 | 0.252 | 0.467 | 0.0613 | +0.0098 [+0.0039, +0.0157] | -0.0002 [-0.0051, +0.0047] | 0.752 | 0.229 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 78 | 0.268 | 0.474 | 0.0628 | +0.0079 [+0.0011, +0.0144] | +0.0015 [-0.0048, +0.0076] | 0.746 | 0.244 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 65 | 0.246 | 0.523 | 0.0623 | +0.0086 [+0.0029, +0.0143] | +0.0001 [-0.0053, +0.0056] | 0.758 | 0.228 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 141 | 0.457 | 0.447 | 0.0630 | +0.0079 [+0.0025, +0.0134] | +0.0004 [-0.0044, +0.0050] | 0.743 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.457, difference +0.1358 [+0.0033, +0.2420]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0908, ΔBrier vs climatology +0.0386 [+0.0219, +0.0543], realised minus predicted +0.0450 [+0.0160, +0.0733]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.562 | 0.1791 | 0.2720 | +0.0375 [+0.0124, +0.0643] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0384 | 0.0159 | +0.0179 [-0.0056, +0.0369] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0183 | 0.0200 | +0.0020 [-0.0055, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0845 | 0.1165 | +0.0244 [+0.0024, +0.0530] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0099 | 0.0048 | +0.0082 [+0.0057, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0119 | 0.0031 | +0.0266 [+0.0198, +0.0330] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1914 | 0.4146 | 0.0719 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.487 | 0.528 | 0.1768 | 0.2474 | +0.0324 [+0.0082, +0.0578] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.1060 | 0.1133 | +0.0339 [+0.0051, +0.0632] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.474 | 0.0419 | 0.0630 | +0.0129 [+0.0068, +0.0197] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0134, +0.1635] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0481, +0.1152] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3840 | 0.2213 |

## risk_logistic+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.12 flat / 2.19 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 3.27 flat / 1.23 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.500 [2.276, 5.144] | 1.442 [0.967, 2.143] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.133, 0.409] | 1.538 [0.917, 2.429] | 0.635 [0.342, 1.090] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.094, 0.375] | 1.308 [0.656, 2.286] | 0.587 [0.268, 1.088] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.364] | 1.731 [0.862, 3.039] | 0.702 [0.336, 1.265] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.080, 0.313] | 1.962 [1.143, 3.158] | 0.712 [0.388, 1.184] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.882 [3.714, 9.236] | 2.059 [1.292, 3.192] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 3.667 [1.857, 8.168] | 2.444 [1.154, 5.917] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 173 | 0.586 | 0.474 | 0.0508 | +0.0206 [+0.0139, +0.0274] | +0.0055 [+0.0005, +0.0110] | 0.877 | 0.533 | yes |
| 2 | 0.366 (147 of 1872 days never flag) | 84 | 0.317 | 0.524 | 0.0580 | +0.0130 [+0.0083, +0.0182] | +0.0030 [-0.0016, +0.0079] | 0.830 | 0.293 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 73 | 0.283 | 0.534 | 0.0613 | +0.0094 [+0.0028, +0.0152] | +0.0031 [-0.0034, +0.0094] | 0.804 | 0.263 | yes |
| 4 | 0.498 (147 of 1870 days never flag) | 84 | 0.283 | 0.464 | 0.0602 | +0.0106 [+0.0059, +0.0156] | +0.0022 [-0.0029, +0.0077] | 0.812 | 0.257 | no |
| 5 | 0.388 (147 of 1869 days never flag) | 110 | 0.428 | 0.536 | 0.0606 | +0.0103 [+0.0059, +0.0144] | +0.0028 [-0.0016, +0.0070] | 0.790 | 0.398 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.597 (climatology 0.457, difference +0.1399 [+0.0283, +0.2419]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0894, ΔBrier vs climatology +0.0401 [+0.0252, +0.0567], realised minus predicted +0.0047 [-0.0271, +0.0378]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.486 | 0.2317 | 0.2720 | +0.0475 [+0.0222, +0.0737] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1198 | 0.0159 | +0.0146 [-0.0046, +0.0285] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0133 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0281 | 0.0200 | +0.0042 [-0.0000, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.556 | 0.0944 | 0.1165 | +0.0246 [+0.0036, +0.0502] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0199 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0613 | 0.0031 | +0.0228 [+0.0170, +0.0281] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1770 | 0.4146 | 0.0637 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.478 | 0.2366 | 0.2474 | +0.0416 [+0.0178, +0.0647] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1101 | 0.1133 | +0.0325 [+0.0041, +0.0599] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.442 | 0.0752 | 0.0630 | +0.0150 [+0.0090, +0.0217] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0140, +0.1626] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0454, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2503 | 0.2213 |

## risk_logistic+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.265 | 4.54 flat / 2.07 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.515] | 0.231 | 3.15 flat / 1.35 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.138, 0.409] | 2.346 [1.545, 3.480] | 0.990 [0.640, 1.536] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.500 [0.909, 2.392] | 0.644 [0.359, 1.100] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.077 [0.618, 1.750] | 0.538 [0.259, 1.000] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.316] | 1.154 [0.643, 1.900] | 0.519 [0.260, 0.929] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.128, 0.429] | 2.615 [1.500, 4.191] | 1.038 [0.600, 1.650] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.428, 0.867] | 3.941 [2.357, 6.462] | 1.368 [0.802, 2.250] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.667 (no interval) | 3.389 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 129 | 0.486 | 0.527 | 0.0500 | +0.0214 [+0.0139, +0.0293] | +0.0063 [+0.0008, +0.0121] | 0.904 | 0.451 | yes |
| 2 | 0.366 (147 of 1872 days never flag) | 74 | 0.252 | 0.473 | 0.0583 | +0.0128 [+0.0072, +0.0183] | +0.0028 [-0.0016, +0.0077] | 0.878 | 0.229 | yes |
| 3 | 0.366 (147 of 1871 days never flag) | 59 | 0.225 | 0.525 | 0.0611 | +0.0096 [+0.0034, +0.0160] | +0.0033 [-0.0030, +0.0092] | 0.861 | 0.208 | yes |
| 4 | 0.498 (147 of 1870 days never flag) | 64 | 0.246 | 0.531 | 0.0601 | +0.0107 [+0.0050, +0.0165] | +0.0023 [-0.0033, +0.0075] | 0.862 | 0.229 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 130 | 0.449 | 0.477 | 0.0613 | +0.0096 [+0.0047, +0.0144] | +0.0021 [-0.0022, +0.0063] | 0.850 | 0.410 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0282, +0.2427]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0427 [+0.0269, +0.0596], realised minus predicted +0.0202 [-0.0104, +0.0514]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.583 | 0.2488 | 0.2720 | +0.0531 [+0.0259, +0.0821] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1335 | 0.0159 | +0.0089 [-0.0128, +0.0260] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0049 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0008, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0959 | 0.1165 | +0.0261 [+0.0025, +0.0547] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0715 | 0.0031 | +0.0206 [+0.0146, +0.0260] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.2203 | 0.4146 | 0.0739 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.538 | 0.548 | 0.2543 | 0.2474 | +0.0441 [+0.0179, +0.0710] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1095 | 0.1133 | +0.0334 [+0.0058, +0.0639] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.506 | 0.0729 | 0.0630 | +0.0158 [+0.0092, +0.0233] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0150, +0.1628] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0471, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3400 | 0.2213 |

## risk_logistic+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.750] | 0.238 | 4.27 flat / 1.99 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.195, 0.500] | 0.231 | 2.69 flat / 1.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.368, 0.714] | 2.846 [1.928, 4.201] | 1.202 [0.790, 1.855] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.381] | 0.923 [0.500, 1.526] | 0.442 [0.193, 0.844] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.885 [0.469, 1.482] | 0.471 [0.208, 0.920] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 1.000 [0.478, 1.765] | 0.452 [0.196, 0.852] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.379] | 2.308 [1.343, 3.773] | 1.019 [0.586, 1.685] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 3.824 [2.214, 6.357] | 1.294 [0.765, 2.135] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 5.111 [2.823, 11.000] | 3.306 [1.694, 7.875] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 150 | 0.543 | 0.507 | 0.0513 | +0.0202 [+0.0150, +0.0256] | +0.0051 [-0.0003, +0.0104] | 0.891 | 0.500 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 47 | 0.165 | 0.489 | 0.0593 | +0.0118 [+0.0075, +0.0162] | +0.0018 [-0.0030, +0.0066] | 0.845 | 0.152 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 49 | 0.188 | 0.531 | 0.0620 | +0.0087 [+0.0031, +0.0142] | +0.0024 [-0.0036, +0.0081] | 0.815 | 0.175 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 53 | 0.196 | 0.509 | 0.0612 | +0.0096 [+0.0053, +0.0138] | +0.0012 [-0.0039, +0.0063] | 0.827 | 0.181 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 97 | 0.268 | 0.381 | 0.0617 | +0.0092 [+0.0049, +0.0131] | +0.0017 [-0.0034, +0.0061] | 0.808 | 0.233 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.457, difference +0.1367 [+0.0227, +0.2248]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0934, ΔBrier vs climatology +0.0361 [+0.0231, +0.0490], realised minus predicted +0.0364 [+0.0043, +0.0713]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.539 | 0.1781 | 0.2720 | +0.0386 [+0.0216, +0.0559] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0821 | 0.0159 | +0.0221 [+0.0043, +0.0353] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0098 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0209 | 0.0200 | +0.0043 [-0.0003, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0714 | 0.1165 | +0.0258 [+0.0050, +0.0523] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0136 | 0.0048 | +0.0089 [+0.0069, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0392 | 0.0031 | +0.0262 [+0.0201, +0.0316] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1281 | 0.4146 | 0.0606 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.526 | 0.1812 | 0.2474 | +0.0373 [+0.0206, +0.0543] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1069 | 0.1133 | +0.0311 [+0.0043, +0.0591] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.476 | 0.0494 | 0.0630 | +0.0146 [+0.0106, +0.0191] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3561 | 0.2903 | +0.0892 [+0.0131, +0.1635] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1296 | 0.1461 | +0.0774 [+0.0467, +0.1146] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2191 | 0.2213 |

## risk_logistic+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 3.35 flat / 1.39 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.560] | 0.231 | 2.62 flat / 1.03 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.368] | 1.885 [0.941, 3.177] | 0.721 [0.362, 1.221] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.192 [0.469, 2.294] | 0.500 [0.190, 0.941] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.192 [0.500, 2.212] | 0.567 [0.211, 1.083] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.577 [0.697, 2.700] | 0.654 [0.280, 1.163] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 2.346 [1.160, 3.924] | 0.875 [0.447, 1.482] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 4.294 [2.500, 6.900] | 1.456 [0.830, 2.375] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.556 [0.250, 4.000] | 1.278 [0.214, 3.500] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 105 | 0.400 | 0.533 | 0.0635 | +0.0079 [-0.0023, +0.0181] | -0.0072 [-0.0166, +0.0017] | 0.868 | 0.372 | no |
| 2 | 0.668 (147 of 1872 days never flag) | 59 | 0.201 | 0.475 | 0.0705 | +0.0005 [-0.0092, +0.0092] | -0.0095 [-0.0189, -0.0013] | 0.824 | 0.184 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 63 | 0.232 | 0.508 | 0.0748 | -0.0041 [-0.0143, +0.0054] | -0.0104 [-0.0204, -0.0010] | 0.796 | 0.214 | no |
| 4 | 0.703 (147 of 1870 days never flag) | 78 | 0.268 | 0.474 | 0.0722 | -0.0014 [-0.0101, +0.0063] | -0.0098 [-0.0186, -0.0017] | 0.814 | 0.244 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 126 | 0.471 | 0.516 | 0.0722 | -0.0012 [-0.0084, +0.0053] | -0.0088 [-0.0155, -0.0021] | 0.778 | 0.436 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.584 (climatology 0.457, difference +0.1273 [+0.0186, +0.2218]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0951, ΔBrier vs climatology +0.0344 [+0.0175, +0.0519], realised minus predicted -0.0130 [-0.0467, +0.0245]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.542 | 0.3233 | 0.2720 | +0.0088 [-0.0363, +0.0522] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2080 | 0.0159 | -0.0185 [-0.0417, +0.0021] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0102 | 0.0200 | +0.0038 [-0.0015, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0630 | 0.1165 | +0.0245 [+0.0037, +0.0501] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0084 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1123 | 0.0031 | +0.0086 [+0.0034, +0.0139] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1462 | 0.4146 | 0.0581 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.470 | 0.529 | 0.3227 | 0.2474 | +0.0018 [-0.0364, +0.0408] |
| day_type | month_end | 150 | 17 | 0.412 | 0.538 | 0.1129 | 0.1133 | +0.0307 [+0.0041, +0.0593] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.487 | 0.1024 | 0.0630 | +0.0003 [-0.0099, +0.0103] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0155, +0.1627] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1296 | 0.1461 | +0.0774 [+0.0473, +0.1139] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2899 | 0.2213 |

## risk_logistic+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.346, 0.720] | 0.231 | 3.92 flat / 1.59 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.565] | 0.231 | 2.96 flat / 1.14 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.524] | 2.654 [1.375, 4.250] | 1.019 [0.550, 1.631] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.048, 0.286] | 1.423 [0.577, 2.619] | 0.500 [0.203, 0.927] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.577 [0.629, 2.839] | 0.548 [0.225, 0.988] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.364] | 1.423 [0.571, 2.534] | 0.500 [0.193, 0.909] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.391] | 2.038 [1.037, 3.476] | 0.837 [0.417, 1.438] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 5.118 [3.000, 8.273] | 1.779 [1.045, 2.844] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.667 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.241 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 130 | 0.436 | 0.469 | 0.0633 | +0.0081 [-0.0019, +0.0183] | -0.0070 [-0.0161, +0.0017] | 0.869 | 0.396 | no |
| 2 | 0.602 (147 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0694 | +0.0017 [-0.0077, +0.0101] | -0.0083 [-0.0166, -0.0008] | 0.825 | 0.230 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 82 | 0.297 | 0.500 | 0.0723 | -0.0016 [-0.0116, +0.0072] | -0.0079 [-0.0179, +0.0005] | 0.797 | 0.273 | yes |
| 4 | 0.75 (147 of 1870 days never flag) | 74 | 0.268 | 0.500 | 0.0705 | +0.0003 [-0.0075, +0.0077] | -0.0082 [-0.0161, -0.0004] | 0.816 | 0.247 | no |
| 5 | 0.644 (147 of 1869 days never flag) | 100 | 0.341 | 0.470 | 0.0724 | -0.0015 [-0.0088, +0.0056] | -0.0090 [-0.0165, -0.0019] | 0.783 | 0.310 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.553 (climatology 0.457, difference +0.0961 [+0.0019, +0.1765]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0927, ΔBrier vs climatology +0.0368 [+0.0213, +0.0535], realised minus predicted -0.0127 [-0.0449, +0.0221]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.471 | 0.3261 | 0.2720 | +0.0095 [-0.0359, +0.0536] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2055 | 0.0159 | -0.0171 [-0.0401, +0.0028] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0101 | 0.0200 | +0.0039 [-0.0011, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0606 | 0.1165 | +0.0238 [+0.0036, +0.0482] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0083 | 0.0048 | +0.0085 [+0.0065, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1106 | 0.0031 | +0.0091 [+0.0035, +0.0152] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1450 | 0.4146 | 0.0566 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.465 | 0.3238 | 0.2474 | +0.0024 [-0.0364, +0.0413] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1115 | 0.1133 | +0.0330 [+0.0058, +0.0603] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.406 | 0.1027 | 0.0630 | +0.0004 [-0.0103, +0.0105] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0144, +0.1657] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1246 | 0.1461 | +0.0764 [+0.0442, +0.1162] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.296, 0.625] | 0.231 | 3.65 flat / 1.45 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.289, 0.630] | 0.231 | 3.00 flat / 1.22 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.100, 0.381] | 1.885 [0.958, 3.259] | 0.721 [0.348, 1.250] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 1.308 [0.571, 2.348] | 0.519 [0.226, 0.935] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.045, 0.281] | 0.808 [0.300, 1.520] | 0.375 [0.155, 0.688] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.231, 0.550] | 1.962 [1.037, 3.269] | 0.769 [0.431, 1.261] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.154 [1.083, 3.647] | 0.865 [0.464, 1.453] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.384, 0.800] | 4.882 [2.935, 7.947] | 1.721 [1.037, 2.792] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 1.333 [0.389, 3.400] | 0.944 [0.235, 2.500] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 105 | 0.400 | 0.533 | 0.0635 | +0.0079 [-0.0026, +0.0174] | -0.0072 [-0.0168, +0.0013] | 0.868 | 0.372 | no |
| 2 | 0.864 (147 of 1872 days never flag) | 72 | 0.273 | 0.528 | 0.0667 | +0.0044 [-0.0049, +0.0135] | -0.0056 [-0.0147, +0.0028] | 0.837 | 0.254 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 53 | 0.232 | 0.604 | 0.0681 | +0.0026 [-0.0073, +0.0116] | -0.0037 [-0.0136, +0.0052] | 0.824 | 0.220 | yes |
| 4 | 0.683 (126 of 1870 days never flag) | 100 | 0.355 | 0.490 | 0.0659 | +0.0050 [-0.0030, +0.0126] | -0.0035 [-0.0112, +0.0041] | 0.840 | 0.326 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 112 | 0.406 | 0.500 | 0.0653 | +0.0057 [-0.0015, +0.0124] | -0.0019 [-0.0087, +0.0049] | 0.827 | 0.373 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.457, difference +0.2431 [+0.0700, +0.3883]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0821, ΔBrier vs climatology +0.0474 [+0.0291, +0.0668], realised minus predicted -0.0306 [-0.0602, -0.0024]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.542 | 0.3233 | 0.2720 | +0.0088 [-0.0379, +0.0515] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2080 | 0.0159 | -0.0185 [-0.0436, +0.0024] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0102 | 0.0200 | +0.0038 [-0.0017, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0630 | 0.1165 | +0.0245 [+0.0035, +0.0513] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0084 | 0.0048 | +0.0084 [+0.0065, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1123 | 0.0031 | +0.0086 [+0.0031, +0.0140] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1462 | 0.4146 | 0.0581 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.470 | 0.529 | 0.3227 | 0.2474 | +0.0018 [-0.0390, +0.0385] |
| day_type | month_end | 150 | 17 | 0.412 | 0.538 | 0.1129 | 0.1133 | +0.0307 [+0.0035, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.487 | 0.1024 | 0.0630 | +0.0003 [-0.0108, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0148, +0.1625] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1296 | 0.1461 | +0.0774 [+0.0470, +0.1154] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2899 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.690] | 0.231 | 3.65 flat / 1.47 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.261, 0.577] | 0.192 | 2.31 flat / 0.98 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.176, 0.530] | 2.654 [1.428, 4.149] | 1.019 [0.562, 1.596] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.385 [0.606, 2.380] | 0.500 [0.240, 0.852] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 0.808 [0.292, 1.560] | 0.375 [0.148, 0.702] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.308 [0.555, 2.391] | 0.519 [0.230, 0.923] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.731 [0.792, 3.000] | 0.702 [0.342, 1.202] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.824 [2.824, 7.467] | 1.691 [1.000, 2.614] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.444 [0.455, 3.750] | 1.056 [0.303, 2.876] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 130 | 0.436 | 0.469 | 0.0633 | +0.0081 [-0.0015, +0.0184] | -0.0070 [-0.0159, +0.0016] | 0.869 | 0.396 | no |
| 2 | 0.875 (147 of 1872 days never flag) | 83 | 0.338 | 0.566 | 0.0666 | +0.0044 [-0.0050, +0.0134] | -0.0056 [-0.0150, +0.0033] | 0.840 | 0.317 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 52 | 0.225 | 0.596 | 0.0677 | +0.0030 [-0.0071, +0.0118] | -0.0033 [-0.0130, +0.0054] | 0.827 | 0.213 | yes |
| 4 | 0.786 (126 of 1870 days never flag) | 79 | 0.326 | 0.570 | 0.0657 | +0.0051 [-0.0033, +0.0131] | -0.0033 [-0.0118, +0.0046] | 0.841 | 0.306 | yes |
| 5 | 0.6 (147 of 1869 days never flag) | 97 | 0.377 | 0.536 | 0.0654 | +0.0055 [-0.0019, +0.0124] | -0.0020 [-0.0088, +0.0049] | 0.826 | 0.351 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2500 [+0.0821, +0.3936]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0815, ΔBrier vs climatology +0.0480 [+0.0295, +0.0676], realised minus predicted -0.0306 [-0.0597, +0.0007]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.471 | 0.3261 | 0.2720 | +0.0095 [-0.0332, +0.0536] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2055 | 0.0159 | -0.0171 [-0.0404, +0.0029] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0101 | 0.0200 | +0.0039 [-0.0014, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0606 | 0.1165 | +0.0238 [+0.0034, +0.0481] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0083 | 0.0048 | +0.0085 [+0.0066, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1106 | 0.0031 | +0.0091 [+0.0033, +0.0149] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1450 | 0.4146 | 0.0566 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.465 | 0.3238 | 0.2474 | +0.0024 [-0.0344, +0.0426] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1115 | 0.1133 | +0.0330 [+0.0064, +0.0614] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.406 | 0.1027 | 0.0630 | +0.0004 [-0.0094, +0.0106] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0134, +0.1624] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1246 | 0.1461 | +0.0764 [+0.0436, +0.1134] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 4.73 flat / 2.18 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.556] | 0.231 | 3.77 flat / 1.69 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 2.462 [1.437, 3.800] | 0.990 [0.589, 1.569] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.808 [0.956, 2.953] | 0.798 [0.412, 1.356] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 1.231 [0.500, 2.214] | 0.538 [0.197, 1.024] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.367] | 1.231 [0.592, 2.188] | 0.567 [0.261, 1.039] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.471] | 3.192 [1.750, 5.304] | 1.442 [0.730, 2.533] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.471 [3.300, 9.188] | 2.176 [1.174, 3.908] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.333 [1.571, 7.333] | 2.194 [0.970, 5.125] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 132 | 0.486 | 0.515 | 0.0590 | +0.0124 [+0.0045, +0.0209] | -0.0027 [-0.0094, +0.0043] | 0.840 | 0.449 | yes |
| 2 | 0.518 (147 of 1872 days never flag) | 78 | 0.223 | 0.397 | 0.0687 | +0.0024 [-0.0040, +0.0088] | -0.0076 [-0.0139, -0.0012] | 0.781 | 0.196 | no |
| 3 | 0.714 (147 of 1871 days never flag) | 67 | 0.254 | 0.522 | 0.0721 | -0.0015 [-0.0080, +0.0051] | -0.0078 [-0.0149, -0.0010] | 0.730 | 0.235 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 62 | 0.217 | 0.484 | 0.0712 | -0.0003 [-0.0067, +0.0060] | -0.0088 [-0.0158, -0.0018] | 0.752 | 0.199 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 147 | 0.464 | 0.435 | 0.0722 | -0.0013 [-0.0075, +0.0047] | -0.0088 [-0.0154, -0.0024] | 0.721 | 0.416 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [+0.0107, +0.2165]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0981, ΔBrier vs climatology +0.0314 [+0.0164, +0.0485], realised minus predicted -0.0298 [-0.0634, +0.0079]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.527 | 0.2943 | 0.2720 | +0.0349 [+0.0022, +0.0700] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2161 | 0.0159 | -0.0164 [-0.0369, -0.0002] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0089, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0147 | 0.0200 | +0.0039 [-0.0015, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0617 | 0.1165 | +0.0224 [+0.0038, +0.0467] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0217 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1310 | 0.0031 | +0.0034 [-0.0011, +0.0082] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1313 | 0.4146 | +0.0390 [-0.0215, +0.0970] |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.516 | 0.2967 | 0.2474 | +0.0260 [-0.0047, +0.0582] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.1136 | 0.1133 | +0.0299 [+0.0021, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.474 | 0.1067 | 0.0630 | +0.0057 [-0.0015, +0.0140] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.3561 | 0.2903 | +0.0892 [+0.0151, +0.1614] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1296 | 0.1461 | +0.0774 [+0.0461, +0.1146] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2856 | 0.2213 |

## risk_logistic+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.15 flat / 2.33 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.556] | 0.231 | 4.19 flat / 1.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.192 [1.931, 4.955] | 1.250 [0.762, 1.938] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.654 [0.821, 2.778] | 0.673 [0.329, 1.154] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.324] | 1.731 [0.788, 3.056] | 0.635 [0.302, 1.094] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.103, 0.367] | 1.154 [0.545, 2.100] | 0.481 [0.228, 0.875] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.469] | 3.077 [1.583, 5.182] | 1.442 [0.693, 2.553] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 6.235 [3.720, 10.000] | 2.485 [1.387, 4.318] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 3.111 [1.538, 7.200] | 2.028 [0.928, 5.002] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (126 of 1873 days never flag) | 154 | 0.507 | 0.461 | 0.0588 | +0.0127 [+0.0049, +0.0211] | -0.0024 [-0.0093, +0.0047] | 0.839 | 0.459 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 74 | 0.223 | 0.419 | 0.0675 | +0.0035 [-0.0027, +0.0097] | -0.0065 [-0.0124, -0.0005] | 0.781 | 0.198 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 87 | 0.304 | 0.483 | 0.0697 | +0.0010 [-0.0046, +0.0069] | -0.0053 [-0.0108, +0.0006] | 0.731 | 0.278 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 61 | 0.225 | 0.508 | 0.0695 | +0.0013 [-0.0043, +0.0074] | -0.0071 [-0.0132, -0.0008] | 0.753 | 0.207 | yes |
| 5 | 0.498 (147 of 1869 days never flag) | 133 | 0.384 | 0.398 | 0.0724 | -0.0015 [-0.0082, +0.0050] | -0.0090 [-0.0162, -0.0022] | 0.727 | 0.338 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.553 (climatology 0.457, difference +0.0961 [-0.0024, +0.1802]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0957, ΔBrier vs climatology +0.0338 [+0.0191, +0.0499], realised minus predicted -0.0296 [-0.0637, +0.0060]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.463 | 0.2972 | 0.2720 | +0.0356 [+0.0024, +0.0708] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2136 | 0.0159 | -0.0150 [-0.0348, +0.0013] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0146 | 0.0200 | +0.0040 [-0.0013, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.667 | 0.0594 | 0.1165 | +0.0217 [+0.0035, +0.0436] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0216 | 0.0048 | +0.0080 [+0.0062, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1294 | 0.0031 | +0.0040 [-0.0012, +0.0096] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1301 | 0.4146 | 0.0375 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.581 | 0.459 | 0.2979 | 0.2474 | +0.0266 [-0.0041, +0.0573] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.1123 | 0.1133 | +0.0322 [+0.0066, +0.0593] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.408 | 0.1070 | 0.0630 | +0.0058 [-0.0018, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.3546 | 0.2903 | +0.0906 [+0.0181, +0.1607] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1246 | 0.1461 | +0.0764 [+0.0450, +0.1158] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.632] | 0.269 | 4.81 flat / 2.12 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.625] | 0.231 | 4.04 flat / 1.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.415] | 2.462 [1.444, 3.941] | 0.990 [0.586, 1.592] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 1.000 [0.394, 1.844] | 0.394 [0.161, 0.731] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 0.654 [0.323, 1.118] | 0.356 [0.161, 0.645] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 1.731 [0.857, 2.947] | 0.683 [0.360, 1.141] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.114, 0.444] | 2.885 [1.444, 4.815] | 1.231 [0.536, 2.204] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.800] | 6.118 [3.700, 9.500] | 2.485 [1.413, 4.182] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 2.333 [1.143, 5.504] | 1.444 [0.656, 3.608] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 132 | 0.486 | 0.515 | 0.0590 | +0.0124 [+0.0050, +0.0209] | -0.0027 [-0.0093, +0.0044] | 0.840 | 0.449 | no |
| 2 | 0.864 (147 of 1872 days never flag) | 57 | 0.223 | 0.544 | 0.0640 | +0.0070 [+0.0004, +0.0137] | -0.0030 [-0.0100, +0.0041] | 0.803 | 0.208 | yes |
| 3 | 0.466 (147 of 1871 days never flag) | 50 | 0.239 | 0.660 | 0.0649 | +0.0058 [-0.0001, +0.0116] | -0.0005 [-0.0067, +0.0057] | 0.765 | 0.229 | no |
| 4 | 0.683 (126 of 1870 days never flag) | 90 | 0.326 | 0.500 | 0.0645 | +0.0064 [+0.0001, +0.0123] | -0.0021 [-0.0090, +0.0045] | 0.786 | 0.300 | yes |
| 5 | 0.767 (147 of 1869 days never flag) | 132 | 0.413 | 0.432 | 0.0650 | +0.0060 [-0.0000, +0.0120] | -0.0016 [-0.0077, +0.0052] | 0.780 | 0.370 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.457, difference +0.2437 [+0.0712, +0.3893]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0839, ΔBrier vs climatology +0.0456 [+0.0265, +0.0646], realised minus predicted -0.0489 [-0.0799, -0.0172]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.527 | 0.2943 | 0.2720 | +0.0349 [+0.0036, +0.0675] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2161 | 0.0159 | -0.0164 [-0.0354, -0.0001] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0147 | 0.0200 | +0.0039 [-0.0015, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0617 | 0.1165 | +0.0224 [+0.0036, +0.0463] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0217 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1310 | 0.0031 | +0.0034 [-0.0012, +0.0084] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1313 | 0.4146 | +0.0390 [-0.0214, +0.1015] |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.516 | 0.2967 | 0.2474 | +0.0260 [-0.0033, +0.0581] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.1136 | 0.1133 | +0.0299 [+0.0035, +0.0574] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.474 | 0.1067 | 0.0630 | +0.0057 [-0.0014, +0.0137] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.3561 | 0.2903 | +0.0892 [+0.0156, +0.1616] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1296 | 0.1461 | +0.0774 [+0.0475, +0.1137] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2856 | 0.2213 |

## risk_logistic+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.640] | 0.269 | 4.69 flat / 2.03 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.550] | 0.231 | 3.38 flat / 1.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.200, 0.560] | 3.192 [1.912, 4.790] | 1.250 [0.759, 1.880] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.077 [0.434, 1.917] | 0.375 [0.160, 0.667] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.280] | 0.654 [0.333, 1.120] | 0.327 [0.155, 0.594] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 1.846 [0.909, 3.154] | 0.702 [0.359, 1.194] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.056, 0.334] | 2.538 [1.159, 4.345] | 1.144 [0.467, 2.125] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.416, 0.867] | 6.176 [3.722, 9.818] | 2.500 [1.387, 4.250] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.333] | 1.889 [0.875, 4.167] | 1.139 [0.458, 2.786] |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (126 of 1873 days never flag) | 154 | 0.507 | 0.461 | 0.0588 | +0.0127 [+0.0048, +0.0207] | -0.0024 [-0.0095, +0.0043] | 0.839 | 0.459 | no |
| 2 | 0.875 (147 of 1872 days never flag) | 68 | 0.288 | 0.588 | 0.0640 | +0.0071 [+0.0002, +0.0137] | -0.0029 [-0.0099, +0.0040] | 0.806 | 0.272 | yes |
| 3 | 0.466 (147 of 1871 days never flag) | 48 | 0.225 | 0.646 | 0.0645 | +0.0062 [+0.0008, +0.0119] | -0.0001 [-0.0058, +0.0059] | 0.768 | 0.215 | no |
| 4 | 0.786 (126 of 1870 days never flag) | 103 | 0.399 | 0.534 | 0.0643 | +0.0065 [+0.0004, +0.0128] | -0.0019 [-0.0086, +0.0049] | 0.787 | 0.371 | yes |
| 5 | 0.773 (147 of 1869 days never flag) | 119 | 0.384 | 0.445 | 0.0651 | +0.0058 [-0.0005, +0.0124] | -0.0017 [-0.0084, +0.0053] | 0.778 | 0.346 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2500 [+0.0925, +0.3901]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0832, ΔBrier vs climatology +0.0462 [+0.0279, +0.0655], realised minus predicted -0.0489 [-0.0807, -0.0179]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.463 | 0.2972 | 0.2720 | +0.0356 [+0.0019, +0.0681] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2136 | 0.0159 | -0.0150 [-0.0332, +0.0004] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0146 | 0.0200 | +0.0040 [-0.0014, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.667 | 0.0594 | 0.1165 | +0.0217 [+0.0041, +0.0427] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0216 | 0.0048 | +0.0080 [+0.0062, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1294 | 0.0031 | +0.0040 [-0.0012, +0.0095] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1301 | 0.4146 | +0.0375 [-0.0217, +0.0899] |
| scarcity_state | 3 | 473 | 117 | 0.581 | 0.459 | 0.2979 | 0.2474 | +0.0266 [-0.0049, +0.0570] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.1123 | 0.1133 | +0.0322 [+0.0061, +0.0587] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.408 | 0.1070 | 0.0630 | +0.0058 [-0.0017, +0.0138] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.3546 | 0.2903 | +0.0906 [+0.0150, +0.1665] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1246 | 0.1461 | +0.0764 [+0.0439, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.290, 0.640] | 0.231 | 4.08 flat / 1.65 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.185, 0.519] | 0.231 | 3.15 flat / 1.18 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 2.500 [1.265, 4.080] | 1.000 [0.528, 1.625] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.292] | 1.192 [0.467, 2.286] | 0.500 [0.190, 0.950] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.273] | 1.154 [0.441, 2.200] | 0.519 [0.170, 1.024] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.923 [0.893, 3.438] | 0.750 [0.333, 1.361] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.444] | 2.885 [1.418, 4.955] | 1.029 [0.509, 1.776] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.867] | 5.647 [3.399, 8.801] | 1.971 [1.172, 3.068] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.111 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 126 | 0.436 | 0.484 | 0.0630 | +0.0085 [-0.0026, +0.0193] | -0.0066 [-0.0171, +0.0029] | 0.884 | 0.398 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 59 | 0.201 | 0.475 | 0.0682 | +0.0029 [-0.0064, +0.0114] | -0.0071 [-0.0158, +0.0011] | 0.851 | 0.184 | no |
| 3 | 0.714 (147 of 1871 days never flag) | 62 | 0.232 | 0.516 | 0.0707 | -0.0000 [-0.0111, +0.0097] | -0.0064 [-0.0170, +0.0032] | 0.849 | 0.215 | no |
| 4 | 0.703 (147 of 1870 days never flag) | 97 | 0.341 | 0.485 | 0.0687 | +0.0021 [-0.0063, +0.0099] | -0.0063 [-0.0150, +0.0022] | 0.835 | 0.312 | no |
| 5 | 0.701 (147 of 1869 days never flag) | 144 | 0.500 | 0.479 | 0.0729 | -0.0020 [-0.0115, +0.0065] | -0.0095 [-0.0190, -0.0007] | 0.810 | 0.457 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.457, difference +0.1370 [+0.0240, +0.2219]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0911, ΔBrier vs climatology +0.0384 [+0.0224, +0.0561], realised minus predicted +0.0048 [-0.0268, +0.0369]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.479 | 0.3259 | 0.2720 | +0.0016 [-0.0505, +0.0527] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1577 | 0.0159 | -0.0029 [-0.0314, +0.0207] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0066 | 0.0200 | +0.0050 [+0.0007, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0650 | 0.1165 | +0.0206 [+0.0035, +0.0430] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0091 [+0.0074, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0683 | 0.0031 | +0.0217 [+0.0158, +0.0273] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0962 | 0.4146 | 0.0355 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.480 | 0.3300 | 0.2474 | -0.0045 [-0.0483, +0.0372] |
| day_type | month_end | 150 | 17 | 0.412 | 0.538 | 0.1116 | 0.1133 | +0.0312 [+0.0032, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.433 | 0.0918 | 0.0630 | +0.0009 [-0.0104, +0.0121] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0125, +0.1653] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1296 | 0.1461 | +0.0774 [+0.0477, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2758 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.688] | 0.231 | 3.85 flat / 1.52 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.154, 0.467] | 0.231 | 2.58 flat / 0.97 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 2.808 [1.548, 4.455] | 1.058 [0.603, 1.673] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.346 [0.517, 2.607] | 0.481 [0.189, 0.934] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.000, 0.233] | 1.115 [0.429, 2.167] | 0.394 [0.145, 0.781] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.133, 0.417] | 1.462 [0.640, 2.625] | 0.519 [0.228, 0.941] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.087, 0.385] | 2.269 [1.111, 3.857] | 0.856 [0.404, 1.486] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.235 [3.167, 8.182] | 1.794 [1.098, 2.818] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.333] | 1.222 [0.200, 3.333] | 1.000 [0.147, 2.917] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 145 | 0.514 | 0.497 | 0.0627 | +0.0087 [-0.0028, +0.0193] | -0.0064 [-0.0176, +0.0036] | 0.884 | 0.472 | yes |
| 2 | 0.602 (147 of 1872 days never flag) | 71 | 0.259 | 0.507 | 0.0670 | +0.0040 [-0.0046, +0.0121] | -0.0060 [-0.0144, +0.0020] | 0.851 | 0.239 | no |
| 3 | 0.756 (147 of 1871 days never flag) | 65 | 0.261 | 0.554 | 0.0682 | +0.0025 [-0.0077, +0.0118] | -0.0039 [-0.0140, +0.0052] | 0.851 | 0.244 | no |
| 4 | 0.649 (147 of 1870 days never flag) | 80 | 0.304 | 0.525 | 0.0670 | +0.0038 [-0.0041, +0.0112] | -0.0047 [-0.0127, +0.0031] | 0.837 | 0.282 | no |
| 5 | 0.712 (147 of 1869 days never flag) | 122 | 0.457 | 0.516 | 0.0731 | -0.0022 [-0.0118, +0.0066] | -0.0097 [-0.0199, -0.0007] | 0.814 | 0.422 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.562 (climatology 0.457, difference +0.1045 [+0.0109, +0.1871]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0887, ΔBrier vs climatology +0.0408 [+0.0259, +0.0575], realised minus predicted +0.0053 [-0.0252, +0.0382]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.500 | 0.3287 | 0.2720 | +0.0023 [-0.0477, +0.0515] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1551 | 0.0159 | -0.0016 [-0.0294, +0.0214] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0065 | 0.0200 | +0.0051 [+0.0010, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0626 | 0.1165 | +0.0199 [+0.0029, +0.0408] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0040 | 0.0048 | +0.0092 [+0.0074, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0667 | 0.0031 | +0.0222 [+0.0161, +0.0280] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0950 | 0.4146 | 0.0340 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.493 | 0.3312 | 0.2474 | -0.0039 [-0.0471, +0.0392] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1103 | 0.1133 | +0.0335 [+0.0073, +0.0623] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.448 | 0.0921 | 0.0630 | +0.0010 [-0.0105, +0.0116] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0144, +0.1665] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1246 | 0.1461 | +0.0764 [+0.0430, +0.1143] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2774 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.593] | 0.231 | 3.62 flat / 1.44 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.231 | 3.19 flat / 1.21 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.500 [1.289, 4.034] | 1.000 [0.529, 1.586] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.303] | 1.154 [0.500, 2.000] | 0.577 [0.260, 0.988] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.050, 0.280] | 0.808 [0.259, 1.618] | 0.346 [0.112, 0.693] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.227, 0.546] | 2.154 [1.136, 3.556] | 0.827 [0.452, 1.324] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.188, 0.526] | 2.654 [1.364, 4.278] | 0.981 [0.516, 1.566] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 5.176 [3.000, 8.215] | 1.882 [1.087, 2.946] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.667 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 126 | 0.436 | 0.484 | 0.0630 | +0.0085 [-0.0031, +0.0188] | -0.0066 [-0.0177, +0.0030] | 0.884 | 0.398 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 64 | 0.245 | 0.531 | 0.0647 | +0.0064 [-0.0034, +0.0156] | -0.0036 [-0.0136, +0.0054] | 0.860 | 0.227 | no |
| 3 | 0.723 (147 of 1871 days never flag) | 52 | 0.225 | 0.596 | 0.0648 | +0.0058 [-0.0046, +0.0154] | -0.0005 [-0.0107, +0.0093] | 0.864 | 0.213 | no |
| 4 | 0.683 (126 of 1870 days never flag) | 110 | 0.391 | 0.491 | 0.0630 | +0.0078 [+0.0003, +0.0153] | -0.0006 [-0.0086, +0.0070] | 0.854 | 0.359 | no |
| 5 | 0.767 (126 of 1869 days never flag) | 117 | 0.348 | 0.410 | 0.0666 | +0.0043 [-0.0057, +0.0132] | -0.0032 [-0.0127, +0.0055] | 0.844 | 0.308 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.457, difference +0.2431 [+0.0667, +0.3973]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0788, ΔBrier vs climatology +0.0507 [+0.0326, +0.0702], realised minus predicted -0.0126 [-0.0424, +0.0180]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.479 | 0.3259 | 0.2720 | +0.0016 [-0.0519, +0.0501] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1577 | 0.0159 | -0.0029 [-0.0318, +0.0205] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0066 | 0.0200 | +0.0050 [+0.0008, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0650 | 0.1165 | +0.0206 [+0.0036, +0.0419] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0091 [+0.0072, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0683 | 0.0031 | +0.0217 [+0.0160, +0.0272] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0962 | 0.4146 | 0.0355 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.480 | 0.3300 | 0.2474 | -0.0045 [-0.0494, +0.0377] |
| day_type | month_end | 150 | 17 | 0.412 | 0.538 | 0.1116 | 0.1133 | +0.0312 [+0.0033, +0.0582] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.433 | 0.0918 | 0.0630 | +0.0009 [-0.0110, +0.0122] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0141, +0.1580] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1296 | 0.1461 | +0.0774 [+0.0479, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2758 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.280, 0.643] | 0.231 | 3.23 flat / 1.27 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.212, 0.538] | 0.192 | 2.00 flat / 0.82 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.207, 0.565] | 2.808 [1.500, 4.393] | 1.058 [0.575, 1.625] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.087, 0.407] | 1.692 [0.733, 3.000] | 0.702 [0.321, 1.205] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.059, 0.346] | 1.115 [0.400, 2.000] | 0.462 [0.175, 0.824] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 1.308 [0.556, 2.333] | 0.519 [0.229, 0.913] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.036, 0.294] | 1.385 [0.517, 2.462] | 0.548 [0.226, 0.964] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.867] | 4.412 [2.545, 7.000] | 1.574 [0.926, 2.472] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.000 (no interval) | 0.694 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 145 | 0.514 | 0.497 | 0.0627 | +0.0087 [-0.0022, +0.0190] | -0.0064 [-0.0169, +0.0031] | 0.884 | 0.472 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 95 | 0.367 | 0.537 | 0.0646 | +0.0064 [-0.0031, +0.0156] | -0.0036 [-0.0130, +0.0056] | 0.862 | 0.342 | yes |
| 3 | 0.709 (147 of 1871 days never flag) | 65 | 0.261 | 0.554 | 0.0644 | +0.0063 [-0.0038, +0.0155] | -0.0001 [-0.0102, +0.0092] | 0.866 | 0.244 | no |
| 4 | 0.786 (126 of 1870 days never flag) | 79 | 0.326 | 0.570 | 0.0628 | +0.0080 [-0.0001, +0.0152] | -0.0005 [-0.0090, +0.0072] | 0.854 | 0.306 | no |
| 5 | 0.773 (147 of 1869 days never flag) | 75 | 0.283 | 0.520 | 0.0668 | +0.0042 [-0.0058, +0.0132] | -0.0034 [-0.0134, +0.0059] | 0.843 | 0.262 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2494 [+0.0883, +0.3895]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0781, ΔBrier vs climatology +0.0513 [+0.0334, +0.0708], realised minus predicted -0.0125 [-0.0421, +0.0175]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.500 | 0.3287 | 0.2720 | +0.0023 [-0.0494, +0.0499] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1551 | 0.0159 | -0.0016 [-0.0283, +0.0220] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0065 | 0.0200 | +0.0051 [+0.0009, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0626 | 0.1165 | +0.0199 [+0.0036, +0.0399] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0040 | 0.0048 | +0.0092 [+0.0075, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0667 | 0.0031 | +0.0222 [+0.0161, +0.0279] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0950 | 0.4146 | 0.0340 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.493 | 0.3312 | 0.2474 | -0.0039 [-0.0472, +0.0362] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1103 | 0.1133 | +0.0335 [+0.0070, +0.0599] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.448 | 0.0921 | 0.0630 | +0.0010 [-0.0105, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0192, +0.1643] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1246 | 0.1461 | +0.0764 [+0.0440, +0.1125] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2774 | 0.2213 |

## risk_logistic+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.714] | 0.269 | 4.88 flat / 2.17 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.588] | 0.231 | 4.00 flat / 1.72 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 3.000 [1.640, 4.764] | 1.154 [0.648, 1.829] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.923 [0.889, 3.393] | 0.923 [0.402, 1.641] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.273] | 1.231 [0.517, 2.278] | 0.538 [0.192, 1.038] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 1.423 [0.704, 2.486] | 0.615 [0.304, 1.084] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 3.769 [2.055, 6.118] | 1.606 [0.805, 2.670] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.483, 0.917] | 6.824 [4.307, 10.445] | 2.676 [1.555, 4.334] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.222 [0.300, 3.400] | 1.222 [0.300, 3.400] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 147 | 0.493 | 0.469 | 0.0564 | +0.0150 [+0.0069, +0.0234] | -0.0001 [-0.0071, +0.0071] | 0.875 | 0.448 | yes |
| 2 | 0.554 (147 of 1872 days never flag) | 81 | 0.223 | 0.383 | 0.0646 | +0.0064 [-0.0007, +0.0133] | -0.0036 [-0.0106, +0.0028] | 0.839 | 0.194 | no |
| 3 | 0.714 (147 of 1871 days never flag) | 65 | 0.239 | 0.508 | 0.0668 | +0.0039 [-0.0036, +0.0106] | -0.0024 [-0.0098, +0.0043] | 0.829 | 0.221 | no |
| 4 | 0.524 (147 of 1870 days never flag) | 76 | 0.283 | 0.513 | 0.0664 | +0.0044 [-0.0024, +0.0109] | -0.0041 [-0.0117, +0.0032] | 0.818 | 0.261 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 170 | 0.522 | 0.424 | 0.0687 | +0.0022 [-0.0041, +0.0081] | -0.0053 [-0.0124, +0.0012] | 0.782 | 0.465 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.591 (climatology 0.457, difference +0.1342 [+0.0254, +0.2233]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0929, ΔBrier vs climatology +0.0366 [+0.0202, +0.0526], realised minus predicted +0.0019 [-0.0327, +0.0376]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.453 | 0.2915 | 0.2720 | +0.0329 [-0.0034, +0.0693] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1806 | 0.0159 | -0.0033 [-0.0249, +0.0152] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0069 | 0.0200 | +0.0050 [+0.0010, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0626 | 0.1165 | +0.0239 [+0.0054, +0.0474] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0068 | 0.0048 | +0.0091 [+0.0072, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0910 | 0.0031 | +0.0170 [+0.0122, +0.0219] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1035 | 0.4146 | 0.0374 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.462 | 0.2996 | 0.2474 | +0.0246 [-0.0074, +0.0567] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.1121 | 0.1133 | +0.0312 [+0.0054, +0.0596] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.414 | 0.0892 | 0.0630 | +0.0086 [+0.0007, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0127, +0.1598] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1296 | 0.1461 | +0.0774 [+0.0463, +0.1137] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2416 | 0.2213 |

## risk_logistic+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.333, 0.722] | 0.269 | 4.69 flat / 2.07 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.159, 0.471] | 0.231 | 3.42 flat / 1.53 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.207, 0.579] | 3.346 [1.921, 5.222] | 1.250 [0.742, 1.948] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.385] | 1.731 [0.750, 3.137] | 0.827 [0.337, 1.550] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.026, 0.227] | 1.192 [0.444, 2.269] | 0.413 [0.148, 0.793] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.385 [0.655, 2.421] | 0.548 [0.265, 0.948] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 3.000 [1.538, 5.042] | 1.375 [0.677, 2.400] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.471 [3.923, 10.273] | 2.544 [1.437, 4.250] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.333 (no interval) | 1.167 (no interval) |

Recall with equal weight per regime: 0.241 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 166 | 0.564 | 0.476 | 0.0562 | +0.0152 [+0.0076, +0.0235] | +0.0002 [-0.0066, +0.0073] | 0.874 | 0.514 | yes |
| 2 | 0.543 (147 of 1872 days never flag) | 77 | 0.230 | 0.416 | 0.0635 | +0.0076 [+0.0009, +0.0142] | -0.0024 [-0.0086, +0.0041] | 0.839 | 0.204 | no |
| 3 | 0.756 (147 of 1871 days never flag) | 66 | 0.254 | 0.530 | 0.0643 | +0.0064 [-0.0001, +0.0127] | +0.0000 [-0.0060, +0.0065] | 0.830 | 0.236 | no |
| 4 | 0.524 (147 of 1870 days never flag) | 76 | 0.290 | 0.526 | 0.0648 | +0.0061 [-0.0003, +0.0124] | -0.0024 [-0.0087, +0.0046] | 0.820 | 0.269 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 138 | 0.435 | 0.435 | 0.0689 | +0.0020 [-0.0050, +0.0085] | -0.0055 [-0.0129, +0.0016] | 0.787 | 0.390 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.563 (climatology 0.457, difference +0.1054 [+0.0139, +0.1875]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0906, ΔBrier vs climatology +0.0389 [+0.0247, +0.0549], realised minus predicted +0.0021 [-0.0300, +0.0379]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.474 | 0.2943 | 0.2720 | +0.0336 [+0.0011, +0.0692] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1781 | 0.0159 | -0.0019 [-0.0230, +0.0162] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0109, +0.0142] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0068 | 0.0200 | +0.0051 [+0.0008, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.800 | 0.0602 | 0.1165 | +0.0231 [+0.0055, +0.0454] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0066 | 0.0048 | +0.0092 [+0.0073, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0894 | 0.0031 | +0.0175 [+0.0122, +0.0229] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1023 | 0.4146 | 0.0359 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.472 | 0.3007 | 0.2474 | +0.0252 [-0.0048, +0.0568] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1107 | 0.1133 | +0.0335 [+0.0067, +0.0618] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.430 | 0.0895 | 0.0630 | +0.0087 [+0.0013, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3546 | 0.2903 | +0.0906 [+0.0178, +0.1621] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1246 | 0.1461 | +0.0764 [+0.0438, +0.1156] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2432 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.600] | 0.265 | 4.54 flat / 1.94 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 4.23 flat / 1.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 3.000 [1.645, 4.722] | 1.154 [0.644, 1.816] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.242] | 0.846 [0.240, 1.613] | 0.356 [0.110, 0.673] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.000, 0.229] | 0.769 [0.226, 1.556] | 0.298 [0.090, 0.592] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.517] | 2.577 [1.355, 4.211] | 1.163 [0.555, 2.065] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.769 [2.148, 5.843] | 1.567 [0.827, 2.538] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 6.706 [4.266, 10.557] | 2.735 [1.632, 4.570] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.308] | 0.444 [0.000, 1.333] | 0.444 [0.000, 1.333] |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 147 | 0.493 | 0.469 | 0.0564 | +0.0150 [+0.0068, +0.0239] | -0.0001 [-0.0069, +0.0070] | 0.875 | 0.448 | yes |
| 2 | 0.864 (147 of 1872 days never flag) | 53 | 0.223 | 0.585 | 0.0605 | +0.0105 [+0.0033, +0.0179] | +0.0005 [-0.0066, +0.0079] | 0.850 | 0.210 | yes |
| 3 | 0.723 (147 of 1871 days never flag) | 56 | 0.261 | 0.643 | 0.0603 | +0.0104 [+0.0041, +0.0170] | +0.0040 [-0.0027, +0.0109] | 0.848 | 0.249 | no |
| 4 | 0.683 (126 of 1870 days never flag) | 120 | 0.384 | 0.442 | 0.0603 | +0.0105 [+0.0039, +0.0168] | +0.0021 [-0.0051, +0.0090] | 0.842 | 0.345 | yes |
| 5 | 0.767 (126 of 1869 days never flag) | 156 | 0.420 | 0.372 | 0.0620 | +0.0089 [+0.0019, +0.0150] | +0.0014 [-0.0056, +0.0082] | 0.828 | 0.364 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.457, difference +0.2431 [+0.0720, +0.3916]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0792, ΔBrier vs climatology +0.0503 [+0.0323, +0.0689], realised minus predicted -0.0174 [-0.0472, +0.0138]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.453 | 0.2915 | 0.2720 | +0.0329 [-0.0021, +0.0680] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1806 | 0.0159 | -0.0033 [-0.0247, +0.0159] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0109, +0.0142] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0069 | 0.0200 | +0.0050 [+0.0009, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0626 | 0.1165 | +0.0239 [+0.0046, +0.0475] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0068 | 0.0048 | +0.0091 [+0.0072, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0910 | 0.0031 | +0.0170 [+0.0120, +0.0218] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1035 | 0.4146 | 0.0374 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.462 | 0.2996 | 0.2474 | +0.0246 [-0.0077, +0.0580] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.1121 | 0.1133 | +0.0312 [+0.0041, +0.0591] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.414 | 0.0892 | 0.0630 | +0.0086 [+0.0009, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0160, +0.1619] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1296 | 0.1461 | +0.0774 [+0.0454, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2416 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.280, 0.647] | 0.242 | 4.31 flat / 1.88 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.548] | 0.231 | 3.23 flat / 1.44 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.205, 0.579] | 3.346 [1.954, 5.148] | 1.250 [0.750, 1.942] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.053, 0.348] | 1.385 [0.485, 2.556] | 0.510 [0.188, 0.954] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.034, 0.292] | 1.077 [0.363, 1.968] | 0.413 [0.140, 0.760] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.501] | 2.538 [1.286, 4.333] | 1.173 [0.540, 2.141] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.059, 0.333] | 2.500 [1.136, 4.291] | 1.135 [0.463, 2.087] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 6.118 [3.695, 9.751] | 2.485 [1.380, 4.222] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.889 (no interval) | 0.722 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 166 | 0.564 | 0.476 | 0.0562 | +0.0152 [+0.0070, +0.0237] | +0.0002 [-0.0070, +0.0071] | 0.874 | 0.514 | yes |
| 2 | 0.875 (147 of 1872 days never flag) | 83 | 0.338 | 0.566 | 0.0605 | +0.0106 [+0.0031, +0.0179] | +0.0006 [-0.0069, +0.0077] | 0.853 | 0.317 | yes |
| 3 | 0.709 (147 of 1871 days never flag) | 69 | 0.297 | 0.594 | 0.0599 | +0.0108 [+0.0045, +0.0171] | +0.0045 [-0.0018, +0.0109] | 0.852 | 0.281 | no |
| 4 | 0.786 (126 of 1870 days never flag) | 120 | 0.391 | 0.450 | 0.0601 | +0.0107 [+0.0042, +0.0172] | +0.0023 [-0.0047, +0.0093] | 0.841 | 0.353 | yes |
| 5 | 0.773 (147 of 1869 days never flag) | 115 | 0.362 | 0.435 | 0.0621 | +0.0088 [+0.0020, +0.0158] | +0.0013 [-0.0063, +0.0086] | 0.827 | 0.325 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2500 [+0.0923, +0.3881]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0786, ΔBrier vs climatology +0.0509 [+0.0329, +0.0706], realised minus predicted -0.0174 [-0.0480, +0.0139]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.474 | 0.2943 | 0.2720 | +0.0336 [-0.0021, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1781 | 0.0159 | -0.0019 [-0.0227, +0.0174] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0110, +0.0142] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0068 | 0.0200 | +0.0051 [+0.0010, +0.0097] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.800 | 0.0602 | 0.1165 | +0.0231 [+0.0049, +0.0463] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0066 | 0.0048 | +0.0092 [+0.0074, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0894 | 0.0031 | +0.0175 [+0.0125, +0.0231] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1023 | 0.4146 | 0.0359 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.472 | 0.3007 | 0.2474 | +0.0252 [-0.0068, +0.0579] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1107 | 0.1133 | +0.0335 [+0.0068, +0.0604] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.430 | 0.0895 | 0.0630 | +0.0087 [+0.0006, +0.0170] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3546 | 0.2903 | +0.0906 [+0.0178, +0.1659] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1246 | 0.1461 | +0.0764 [+0.0440, +0.1140] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2432 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.192 | 2.04 flat / 1.41 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.115 | 1.19 flat / 0.72 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.680] | 1.769 [1.167, 2.750] | 1.163 [0.698, 1.952] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.000 [0.513, 1.667] | 0.615 [0.239, 1.188] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.389] | 1.000 [0.481, 1.714] | 0.644 [0.237, 1.277] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.115 [0.583, 1.857] | 0.702 [0.293, 1.361] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.154 [0.625, 1.900] | 0.683 [0.279, 1.326] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 2.750 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (105 of 1873 days never flag) | 90 | 0.314 | 0.489 | 0.0596 | +0.0118 [+0.0070, +0.0164] | -0.0033 [-0.0115, +0.0041] | 0.643 | 0.288 | no |
| 2 | 0.33 (147 of 1872 days never flag) | 50 | 0.173 | 0.480 | 0.0672 | +0.0039 [-0.0026, +0.0099] | -0.0061 [-0.0146, +0.0009] | 0.579 | 0.158 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 49 | 0.167 | 0.469 | 0.0689 | +0.0018 [-0.0060, +0.0080] | -0.0045 [-0.0131, +0.0025] | 0.579 | 0.152 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0689 | +0.0019 [-0.0048, +0.0080] | -0.0065 [-0.0146, +0.0010] | 0.578 | 0.179 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 57 | 0.196 | 0.474 | 0.0687 | +0.0023 [-0.0045, +0.0084] | -0.0053 [-0.0131, +0.0019] | 0.577 | 0.178 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [-0.0214, +0.2463]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0239 [+0.0136, +0.0345], realised minus predicted +0.0775 [+0.0426, +0.1148]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1080 | 0.2720 | -0.0024 [-0.0224, +0.0166] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.0294 | 0.0159 | +0.0298 [+0.0202, +0.0383] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0311 | 0.1165 | +0.0168 [+0.0040, +0.0338] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0092 | 0.0031 | +0.0279 [+0.0218, +0.0337] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0421 | 0.4146 | 0.0149 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1063 | 0.2474 | +0.0057 [-0.0113, +0.0230] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.0996 | 0.1133 | +0.0352 [+0.0096, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.471 | 0.0123 | 0.0630 | +0.0047 [-0.0004, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1520] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1332 | 0.1461 | +0.0711 [+0.0381, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2040 | 0.2213 |

## risk_logistic_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.259, 0.593] | 0.242 | 4.31 flat / 1.85 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.548] | 0.231 | 3.62 flat / 1.54 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.615 [0.909, 2.526] | 0.587 [0.326, 0.947] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.077, 0.321] | 1.385 [0.826, 2.125] | 0.529 [0.312, 0.842] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.615 [0.921, 2.647] | 0.673 [0.350, 1.177] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 1.500 [0.900, 2.421] | 0.702 [0.368, 1.232] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.308 [1.316, 3.668] | 0.942 [0.537, 1.512] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.750] | 3.353 [1.687, 5.750] | 1.132 [0.562, 1.955] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.111 (no interval) | 3.194 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 96 | 0.386 | 0.562 | 0.0497 | +0.0217 [+0.0143, +0.0296] | +0.0066 [+0.0019, +0.0120] | 0.887 | 0.361 | yes |
| 2 | 0.381 (147 of 1872 days never flag) | 73 | 0.266 | 0.507 | 0.0586 | +0.0124 [+0.0073, +0.0182] | +0.0024 [-0.0014, +0.0071] | 0.842 | 0.245 | yes |
| 3 | 0.374 (147 of 1871 days never flag) | 80 | 0.275 | 0.475 | 0.0628 | +0.0079 [+0.0018, +0.0140] | +0.0016 [-0.0043, +0.0073] | 0.812 | 0.251 | yes |
| 4 | 0.361 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0615 | +0.0094 [+0.0035, +0.0157] | +0.0009 [-0.0047, +0.0068] | 0.820 | 0.217 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 105 | 0.326 | 0.429 | 0.0620 | +0.0089 [+0.0039, +0.0138] | +0.0014 [-0.0028, +0.0057] | 0.797 | 0.291 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0169, +0.2528]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0870, ΔBrier vs climatology +0.0425 [+0.0268, +0.0599], realised minus predicted -0.0019 [-0.0322, +0.0307]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.402 | 0.651 | 0.2494 | 0.2720 | +0.0533 [+0.0256, +0.0823] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1320 | 0.0159 | +0.0135 [-0.0012, +0.0264] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0188 | 0.0000 | +0.0132 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0327 | 0.0200 | +0.0009 [-0.0055, +0.0058] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.1073 | 0.1165 | +0.0288 [+0.0041, +0.0593] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0222 | 0.0048 | +0.0082 [+0.0061, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0738 | 0.0031 | +0.0205 [+0.0142, +0.0265] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.2264 | 0.4146 | +0.0842 [-0.0045, +0.1737] |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.590 | 0.2526 | 0.2474 | +0.0467 [+0.0216, +0.0732] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1089 | 0.1133 | +0.0404 [+0.0147, +0.0692] |
| day_type | ordinary | 1603 | 101 | 0.307 | 0.484 | 0.0858 | 0.0630 | +0.0158 [+0.0089, +0.0234] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0435, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1332 | 0.1461 | +0.0711 [+0.0381, +0.1090] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3420 | 0.2213 |

## risk_logistic_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.714] | 0.269 | 4.96 flat / 2.14 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 3.77 flat / 1.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.174, 0.462] | 1.731 [1.064, 2.612] | 0.702 [0.420, 1.107] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.324] | 1.385 [0.846, 2.250] | 0.529 [0.317, 0.869] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.615 [0.879, 2.737] | 0.673 [0.337, 1.226] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.500 [0.875, 2.501] | 0.702 [0.371, 1.286] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.526] | 2.885 [1.714, 4.630] | 1.144 [0.685, 1.837] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.412 [2.667, 7.000] | 1.603 [0.976, 2.591] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.000 (no interval) | 3.167 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 94 | 0.350 | 0.521 | 0.0516 | +0.0199 [+0.0132, +0.0270] | +0.0048 [+0.0004, +0.0093] | 0.804 | 0.324 | no |
| 2 | 0.381 (147 of 1872 days never flag) | 73 | 0.266 | 0.507 | 0.0609 | +0.0102 [+0.0048, +0.0160] | +0.0002 [-0.0045, +0.0051] | 0.752 | 0.245 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 80 | 0.275 | 0.475 | 0.0628 | +0.0079 [+0.0013, +0.0142] | +0.0015 [-0.0045, +0.0075] | 0.748 | 0.251 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0623 | +0.0085 [+0.0026, +0.0144] | +0.0000 [-0.0054, +0.0056] | 0.758 | 0.217 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 138 | 0.457 | 0.457 | 0.0627 | +0.0083 [+0.0027, +0.0136] | +0.0007 [-0.0038, +0.0055] | 0.744 | 0.413 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.457, difference +0.1421 [+0.0012, +0.2594]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0406 [+0.0256, +0.0566], realised minus predicted +0.0472 [+0.0192, +0.0765]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.581 | 0.1797 | 0.2720 | +0.0377 [+0.0125, +0.0659] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0370 | 0.0159 | +0.0225 [+0.0051, +0.0368] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0151 | 0.0200 | +0.0010 [-0.0058, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0823 | 0.1165 | +0.0279 [+0.0032, +0.0559] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0082 | 0.0048 | +0.0084 [+0.0062, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0142 | 0.0031 | +0.0265 [+0.0196, +0.0327] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.1975 | 0.4146 | +0.0822 [-0.0034, +0.1683] |
| scarcity_state | 3 | 473 | 117 | 0.376 | 0.543 | 0.1750 | 0.2474 | +0.0349 [+0.0125, +0.0594] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1034 | 0.1133 | +0.0409 [+0.0150, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.424 | 0.0416 | 0.0630 | +0.0136 [+0.0073, +0.0205] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0427, +0.1489] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1332 | 0.1461 | +0.0711 [+0.0394, +0.1092] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3860 | 0.2213 |

## risk_logistic_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.679] | 0.262 | 4.50 flat / 1.78 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.562] | 0.231 | 3.08 flat / 1.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.731 [0.913, 2.905] | 0.702 [0.375, 1.192] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.103, 0.368] | 1.500 [0.913, 2.368] | 0.587 [0.330, 0.985] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.308 [0.636, 2.286] | 0.558 [0.265, 1.020] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.467] | 1.808 [0.946, 3.105] | 0.788 [0.389, 1.417] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.061, 0.333] | 1.346 [0.684, 2.300] | 0.500 [0.250, 0.864] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 5.118 [3.181, 8.000] | 1.676 [1.026, 2.625] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (126 of 1873 days never flag) | 93 | 0.343 | 0.516 | 0.0498 | +0.0216 [+0.0154, +0.0284] | +0.0065 [+0.0021, +0.0115] | 0.882 | 0.317 | yes |
| 2 | 0.33 (147 of 1872 days never flag) | 80 | 0.295 | 0.512 | 0.0576 | +0.0135 [+0.0090, +0.0183] | +0.0035 [-0.0006, +0.0080] | 0.831 | 0.272 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 70 | 0.261 | 0.514 | 0.0610 | +0.0097 [+0.0043, +0.0155] | +0.0033 [-0.0023, +0.0097] | 0.807 | 0.241 | yes |
| 4 | 0.361 (147 of 1870 days never flag) | 89 | 0.304 | 0.472 | 0.0599 | +0.0110 [+0.0060, +0.0161] | +0.0025 [-0.0027, +0.0078] | 0.816 | 0.277 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 75 | 0.290 | 0.533 | 0.0602 | +0.0108 [+0.0065, +0.0149] | +0.0032 [-0.0011, +0.0074] | 0.796 | 0.270 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.457, difference +0.1424 [+0.0193, +0.2505]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0879, ΔBrier vs climatology +0.0416 [+0.0266, +0.0576], realised minus predicted +0.0078 [-0.0228, +0.0415]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.343 | 0.522 | 0.2323 | 0.2720 | +0.0476 [+0.0233, +0.0731] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1212 | 0.0159 | +0.0189 [+0.0086, +0.0289] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0133 [+0.0116, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0238 | 0.0200 | +0.0031 [-0.0009, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.647 | 0.0914 | 0.1165 | +0.0282 [+0.0057, +0.0561] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0176 | 0.0048 | +0.0089 [+0.0072, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0655 | 0.0031 | +0.0225 [+0.0169, +0.0285] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1850 | 0.4146 | 0.0742 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.368 | 0.512 | 0.2348 | 0.2474 | +0.0442 [+0.0224, +0.0667] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1075 | 0.1133 | +0.0395 [+0.0145, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.238 | 0.407 | 0.0750 | 0.0630 | +0.0157 [+0.0098, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0386, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1332 | 0.1461 | +0.0711 [+0.0380, +0.1071] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2523 | 0.2213 |

## risk_logistic_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 4.15 flat / 1.77 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.546] | 0.231 | 3.42 flat / 1.44 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.129, 0.414] | 1.577 [0.857, 2.520] | 0.577 [0.315, 0.945] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.385 [0.800, 2.222] | 0.529 [0.306, 0.869] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.577 [0.838, 2.611] | 0.663 [0.326, 1.193] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.385 [0.762, 2.278] | 0.654 [0.318, 1.221] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.231 [1.200, 3.616] | 0.885 [0.471, 1.469] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.308, 0.765] | 3.353 [1.722, 5.727] | 1.132 [0.580, 1.958] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.667 (no interval) | 2.972 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 95 | 0.386 | 0.568 | 0.0491 | +0.0224 [+0.0155, +0.0301] | +0.0073 [+0.0025, +0.0125] | 0.908 | 0.362 | yes |
| 2 | 0.381 (147 of 1872 days never flag) | 73 | 0.266 | 0.507 | 0.0579 | +0.0132 [+0.0082, +0.0186] | +0.0032 [-0.0008, +0.0077] | 0.879 | 0.245 | yes |
| 3 | 0.374 (147 of 1871 days never flag) | 80 | 0.283 | 0.487 | 0.0611 | +0.0096 [+0.0038, +0.0156] | +0.0033 [-0.0025, +0.0092] | 0.863 | 0.259 | yes |
| 4 | 0.361 (147 of 1870 days never flag) | 69 | 0.239 | 0.478 | 0.0602 | +0.0107 [+0.0050, +0.0165] | +0.0022 [-0.0032, +0.0076] | 0.864 | 0.218 | yes |
| 5 | 0.334 (147 of 1869 days never flag) | 103 | 0.326 | 0.437 | 0.0610 | +0.0099 [+0.0049, +0.0148] | +0.0024 [-0.0018, +0.0070] | 0.851 | 0.293 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0195, +0.2564]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0855, ΔBrier vs climatology +0.0440 [+0.0286, +0.0609], realised minus predicted +0.0242 [-0.0069, +0.0572]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.402 | 0.651 | 0.2494 | 0.2720 | +0.0533 [+0.0268, +0.0818] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1320 | 0.0159 | +0.0135 [-0.0018, +0.0260] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0046 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0002, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0937 | 0.1165 | +0.0296 [+0.0050, +0.0625] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0738 | 0.0031 | +0.0205 [+0.0143, +0.0265] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.2264 | 0.4146 | 0.0842 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.590 | 0.2526 | 0.2474 | +0.0467 [+0.0237, +0.0734] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1069 | 0.1133 | +0.0404 [+0.0151, +0.0675] |
| day_type | ordinary | 1603 | 101 | 0.307 | 0.492 | 0.0726 | 0.0630 | +0.0165 [+0.0101, +0.0243] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0374, +0.1520] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1332 | 0.1461 | +0.0711 [+0.0386, +0.1084] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3420 | 0.2213 |

## risk_logistic_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 3.73 flat / 1.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.524] | 0.192 | 2.35 flat / 0.98 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.294, 0.621] | 2.462 [1.643, 3.737] | 0.885 [0.571, 1.364] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 0.923 [0.536, 1.471] | 0.385 [0.192, 0.688] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.346 [0.684, 2.321] | 0.577 [0.271, 1.068] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 0.962 [0.516, 1.636] | 0.510 [0.218, 1.012] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.346 [0.607, 2.400] | 0.519 [0.215, 0.958] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 4.059 [2.470, 6.701] | 1.353 [0.810, 2.229] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (126 of 1873 days never flag) | 140 | 0.543 | 0.543 | 0.0503 | +0.0211 [+0.0165, +0.0264] | +0.0061 [+0.0015, +0.0106] | 0.899 | 0.506 | no |
| 2 | 0.33 (147 of 1872 days never flag) | 48 | 0.173 | 0.500 | 0.0589 | +0.0122 [+0.0081, +0.0165] | +0.0022 [-0.0024, +0.0066] | 0.846 | 0.159 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 66 | 0.225 | 0.470 | 0.0620 | +0.0087 [+0.0035, +0.0137] | +0.0024 [-0.0036, +0.0081] | 0.815 | 0.204 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 47 | 0.159 | 0.468 | 0.0613 | +0.0095 [+0.0048, +0.0141] | +0.0011 [-0.0047, +0.0065] | 0.826 | 0.145 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 67 | 0.232 | 0.478 | 0.0614 | +0.0095 [+0.0054, +0.0135] | +0.0020 [-0.0027, +0.0062] | 0.806 | 0.212 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.589 (climatology 0.457, difference +0.1317 [+0.0089, +0.2280]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0917, ΔBrier vs climatology +0.0377 [+0.0250, +0.0510], realised minus predicted +0.0391 [+0.0076, +0.0728]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.552 | 0.1787 | 0.2720 | +0.0388 [+0.0239, +0.0559] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0807 | 0.0159 | +0.0267 [+0.0175, +0.0357] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0095 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0177 | 0.0200 | +0.0033 [-0.0011, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0692 | 0.1165 | +0.0293 [+0.0085, +0.0567] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0118 | 0.0048 | +0.0091 [+0.0073, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0415 | 0.0031 | +0.0261 [+0.0203, +0.0317] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1343 | 0.4146 | +0.0709 [+0.0125, +0.1384] |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.541 | 0.1794 | 0.2474 | +0.0398 [+0.0252, +0.0562] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1043 | 0.1133 | +0.0382 [+0.0122, +0.0657] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.500 | 0.0491 | 0.0630 | +0.0153 [+0.0114, +0.0201] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0398, +0.1512] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1332 | 0.1461 | +0.0711 [+0.0382, +0.1094] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2211 | 0.2213 |

## risk_logistic_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.158, 0.471] | 0.231 | 3.04 flat / 1.20 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.160, 0.476] | 0.231 | 2.77 flat / 1.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.000 [0.409, 1.846] | 0.346 [0.160, 0.607] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.286] | 1.346 [0.536, 2.481] | 0.481 [0.179, 0.903] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.062, 0.321] | 1.885 [0.875, 3.217] | 0.740 [0.320, 1.323] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.276] | 1.654 [0.698, 2.945] | 0.673 [0.292, 1.219] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.000 [0.875, 3.572] | 0.760 [0.345, 1.350] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.261, 0.684] | 3.882 [1.923, 6.813] | 1.309 [0.661, 2.304] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.444 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.8 (147 of 1873 days never flag) | 67 | 0.293 | 0.612 | 0.0625 | +0.0089 [-0.0009, +0.0185] | -0.0062 [-0.0153, +0.0021] | 0.871 | 0.278 | no |
| 2 | 0.638 (147 of 1872 days never flag) | 65 | 0.216 | 0.462 | 0.0702 | +0.0009 [-0.0079, +0.0097] | -0.0091 [-0.0174, -0.0012] | 0.826 | 0.196 | no |
| 3 | 0.62 (147 of 1871 days never flag) | 88 | 0.283 | 0.443 | 0.0748 | -0.0041 [-0.0149, +0.0052] | -0.0104 [-0.0209, -0.0012] | 0.802 | 0.254 | no |
| 4 | 0.8 (147 of 1870 days never flag) | 79 | 0.261 | 0.456 | 0.0723 | -0.0015 [-0.0096, +0.0066] | -0.0099 [-0.0180, -0.0020] | 0.816 | 0.236 | no |
| 5 | 0.567 (147 of 1869 days never flag) | 98 | 0.333 | 0.469 | 0.0718 | -0.0009 [-0.0076, +0.0055] | -0.0084 [-0.0150, -0.0018] | 0.784 | 0.303 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.457, difference +0.1392 [+0.0032, +0.2580]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0943, ΔBrier vs climatology +0.0352 [+0.0190, +0.0521], realised minus predicted -0.0086 [-0.0412, +0.0248]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.382 | 0.629 | 0.3238 | 0.2720 | +0.0090 [-0.0339, +0.0519] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2066 | 0.0159 | -0.0138 [-0.0348, +0.0039] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0028 [-0.0023, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0609 | 0.1165 | +0.0281 [+0.0069, +0.0562] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0068, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1146 | 0.0031 | +0.0085 [+0.0026, +0.0149] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1523 | 0.4146 | +0.0684 [-0.0070, +0.1543] |
| scarcity_state | 3 | 473 | 117 | 0.350 | 0.612 | 0.3209 | 0.2474 | +0.0044 [-0.0323, +0.0411] |
| day_type | month_end | 150 | 17 | 0.294 | 0.714 | 0.1103 | 0.1133 | +0.0377 [+0.0126, +0.0635] |
| day_type | ordinary | 1603 | 101 | 0.238 | 0.522 | 0.1021 | 0.0630 | +0.0010 [-0.0090, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0400, +0.1487] |
| day_type | tax_date | 89 | 13 | 0.615 | 1.000 | 0.1332 | 0.1461 | +0.0711 [+0.0385, +0.1092] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2919 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.560] | 0.231 | 3.12 flat / 1.19 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.120, 0.429] | 0.231 | 2.69 flat / 1.02 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 1.538 [0.687, 2.813] | 0.548 [0.250, 0.992] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.222] | 1.269 [0.552, 2.412] | 0.433 [0.177, 0.833] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 1.885 [0.903, 3.287] | 0.625 [0.286, 1.100] |
| lead 4 alone (fail) | 26 | 3 | 0.115 [0.030, 0.226] | 1.077 [0.409, 2.070] | 0.385 [0.141, 0.750] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 2.038 [1.000, 3.608] | 0.808 [0.400, 1.429] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.385, 0.810] | 4.059 [2.300, 6.923] | 1.353 [0.766, 2.304] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.333 (no interval) | 0.889 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 96 | 0.400 | 0.583 | 0.0621 | +0.0093 [-0.0007, +0.0191] | -0.0058 [-0.0147, +0.0025] | 0.873 | 0.377 | no |
| 2 | 0.604 (147 of 1872 days never flag) | 62 | 0.209 | 0.468 | 0.0693 | +0.0018 [-0.0078, +0.0100] | -0.0082 [-0.0172, -0.0006] | 0.827 | 0.190 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 91 | 0.304 | 0.462 | 0.0724 | -0.0017 [-0.0113, +0.0069] | -0.0081 [-0.0176, +0.0004] | 0.804 | 0.276 | no |
| 4 | 0.761 (147 of 1870 days never flag) | 54 | 0.188 | 0.481 | 0.0710 | -0.0001 [-0.0077, +0.0071] | -0.0086 [-0.0163, -0.0015] | 0.818 | 0.172 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 98 | 0.326 | 0.459 | 0.0724 | -0.0015 [-0.0087, +0.0053] | -0.0090 [-0.0164, -0.0022] | 0.789 | 0.295 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.553 (climatology 0.457, difference +0.0957 [-0.0097, +0.1924]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0920, ΔBrier vs climatology +0.0375 [+0.0222, +0.0548], realised minus predicted -0.0081 [-0.0420, +0.0250]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.529 | 0.587 | 0.3266 | 0.2720 | +0.0107 [-0.0365, +0.0546] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2027 | 0.0159 | -0.0126 [-0.0342, +0.0051] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0029 [-0.0025, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0590 | 0.1165 | +0.0275 [+0.0065, +0.0546] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1124 | 0.0031 | +0.0088 [+0.0030, +0.0149] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1506 | 0.4146 | +0.0653 [-0.0127, +0.1424] |
| scarcity_state | 3 | 473 | 117 | 0.479 | 0.583 | 0.3219 | 0.2474 | +0.0062 [-0.0343, +0.0438] |
| day_type | month_end | 150 | 17 | 0.412 | 0.636 | 0.1083 | 0.1133 | +0.0403 [+0.0146, +0.0679] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.529 | 0.1025 | 0.0630 | +0.0011 [-0.0094, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0464, +0.1425] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1254 | 0.1461 | +0.0736 [+0.0417, +0.1102] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2978 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.280, 0.657] | 0.231 | 3.23 flat / 1.28 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.231 | 2.81 flat / 1.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.000 [0.433, 1.870] | 0.346 [0.167, 0.619] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.032, 0.233] | 0.692 [0.167, 1.500] | 0.250 [0.066, 0.516] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.769 [0.966, 2.968] | 0.750 [0.429, 1.239] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.565] | 1.846 [0.880, 3.192] | 0.712 [0.368, 1.194] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.069, 0.346] | 2.115 [1.080, 3.579] | 0.856 [0.460, 1.409] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.867] | 4.353 [2.461, 7.188] | 1.529 [0.882, 2.481] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.111 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.8 (147 of 1873 days never flag) | 67 | 0.293 | 0.612 | 0.0625 | +0.0089 [-0.0010, +0.0187] | -0.0062 [-0.0151, +0.0021] | 0.871 | 0.278 | no |
| 2 | 0.855 (147 of 1872 days never flag) | 53 | 0.252 | 0.660 | 0.0655 | +0.0055 [-0.0033, +0.0143] | -0.0045 [-0.0131, +0.0041] | 0.844 | 0.241 | no |
| 3 | 0.625 (126 of 1871 days never flag) | 98 | 0.377 | 0.531 | 0.0686 | +0.0020 [-0.0080, +0.0109] | -0.0043 [-0.0139, +0.0049] | 0.824 | 0.350 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 106 | 0.420 | 0.547 | 0.0666 | +0.0042 [-0.0041, +0.0121] | -0.0042 [-0.0125, +0.0035] | 0.841 | 0.393 | yes |
| 5 | 0.855 (147 of 1869 days never flag) | 110 | 0.399 | 0.500 | 0.0667 | +0.0043 [-0.0022, +0.0108] | -0.0033 [-0.0098, +0.0034] | 0.825 | 0.367 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.686 (climatology 0.457, difference +0.2293 [+0.1055, +0.3568]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0837, ΔBrier vs climatology +0.0458 [+0.0281, +0.0656], realised minus predicted -0.0277 [-0.0590, +0.0035]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.382 | 0.629 | 0.3238 | 0.2720 | +0.0090 [-0.0360, +0.0530] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2066 | 0.0159 | -0.0138 [-0.0362, +0.0045] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0028 [-0.0022, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0609 | 0.1165 | +0.0281 [+0.0056, +0.0557] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0068, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1146 | 0.0031 | +0.0085 [+0.0028, +0.0141] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1523 | 0.4146 | +0.0684 [-0.0095, +0.1529] |
| scarcity_state | 3 | 473 | 117 | 0.350 | 0.612 | 0.3209 | 0.2474 | +0.0044 [-0.0349, +0.0427] |
| day_type | month_end | 150 | 17 | 0.294 | 0.714 | 0.1103 | 0.1133 | +0.0377 [+0.0123, +0.0662] |
| day_type | ordinary | 1603 | 101 | 0.238 | 0.522 | 0.1021 | 0.0630 | +0.0010 [-0.0089, +0.0112] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0403, +0.1494] |
| day_type | tax_date | 89 | 13 | 0.615 | 1.000 | 0.1332 | 0.1461 | +0.0711 [+0.0387, +0.1082] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2919 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.226, 0.548] | 0.231 | 3.46 flat / 1.36 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.500] | 0.192 | 2.19 flat / 0.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.538 [0.695, 2.834] | 0.548 [0.250, 1.000] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.962 [0.955, 3.231] | 0.731 [0.375, 1.205] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 0.808 [0.316, 1.571] | 0.375 [0.151, 0.706] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.464] | 1.154 [0.500, 2.091] | 0.481 [0.215, 0.870] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.075, 0.333] | 1.692 [0.769, 3.000] | 0.750 [0.370, 1.323] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.316, 0.750] | 4.706 [2.750, 7.625] | 1.647 [0.973, 2.692] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.111 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 96 | 0.400 | 0.583 | 0.0621 | +0.0093 [-0.0010, +0.0195] | -0.0058 [-0.0152, +0.0029] | 0.873 | 0.377 | no |
| 2 | 0.831 (126 of 1872 days never flag) | 102 | 0.367 | 0.500 | 0.0651 | +0.0059 [-0.0037, +0.0145] | -0.0041 [-0.0132, +0.0042] | 0.847 | 0.337 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 50 | 0.210 | 0.580 | 0.0681 | +0.0026 [-0.0077, +0.0113] | -0.0037 [-0.0135, +0.0048] | 0.825 | 0.198 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 63 | 0.239 | 0.524 | 0.0665 | +0.0044 [-0.0037, +0.0124] | -0.0041 [-0.0125, +0.0038] | 0.841 | 0.222 | yes |
| 5 | 0.872 (147 of 1869 days never flag) | 86 | 0.304 | 0.488 | 0.0668 | +0.0041 [-0.0030, +0.0112] | -0.0034 [-0.0104, +0.0038] | 0.824 | 0.279 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.690 (climatology 0.457, difference +0.2325 [+0.1031, +0.3727]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0276, +0.0683], realised minus predicted -0.0277 [-0.0574, +0.0058]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.529 | 0.587 | 0.3266 | 0.2720 | +0.0107 [-0.0360, +0.0556] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2027 | 0.0159 | -0.0126 [-0.0343, +0.0048] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0029 [-0.0023, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0590 | 0.1165 | +0.0275 [+0.0060, +0.0539] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0070, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1124 | 0.0031 | +0.0088 [+0.0027, +0.0148] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1506 | 0.4146 | 0.0653 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.479 | 0.583 | 0.3219 | 0.2474 | +0.0062 [-0.0333, +0.0455] |
| day_type | month_end | 150 | 17 | 0.412 | 0.636 | 0.1083 | 0.1133 | +0.0403 [+0.0134, +0.0679] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.529 | 0.1025 | 0.0630 | +0.0011 [-0.0097, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0459, +0.1450] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1254 | 0.1461 | +0.0736 [+0.0403, +0.1137] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2978 | 0.2213 |

## risk_logistic_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.600] | 0.250 | 4.38 flat / 1.95 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.556] | 0.231 | 3.92 flat / 1.73 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.500 [0.784, 2.519] | 0.567 [0.304, 0.943] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.385] | 1.731 [0.889, 2.958] | 0.692 [0.338, 1.182] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.435] | 1.731 [0.867, 2.867] | 0.702 [0.336, 1.208] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.846 [0.947, 3.131] | 0.779 [0.383, 1.352] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.444] | 2.846 [1.394, 4.838] | 1.308 [0.575, 2.348] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.296, 0.769] | 5.059 [2.600, 8.752] | 2.029 [0.904, 3.875] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 1.806 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (147 of 1873 days never flag) | 92 | 0.379 | 0.576 | 0.0580 | +0.0134 [+0.0062, +0.0217] | -0.0017 [-0.0075, +0.0049] | 0.846 | 0.356 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 76 | 0.223 | 0.408 | 0.0683 | +0.0028 [-0.0032, +0.0089] | -0.0072 [-0.0133, -0.0009] | 0.782 | 0.197 | no |
| 3 | 0.507 (147 of 1871 days never flag) | 83 | 0.275 | 0.458 | 0.0721 | -0.0014 [-0.0081, +0.0050] | -0.0078 [-0.0146, -0.0012] | 0.732 | 0.249 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 84 | 0.261 | 0.429 | 0.0712 | -0.0004 [-0.0070, +0.0060] | -0.0089 [-0.0162, -0.0018] | 0.754 | 0.233 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 120 | 0.333 | 0.383 | 0.0719 | -0.0009 [-0.0069, +0.0048] | -0.0085 [-0.0150, -0.0020] | 0.725 | 0.291 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.457, difference +0.1361 [+0.0069, +0.2496]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0972, ΔBrier vs climatology +0.0322 [+0.0168, +0.0486], realised minus predicted -0.0258 [-0.0610, +0.0114]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.608 | 0.2948 | 0.2720 | +0.0350 [+0.0048, +0.0709] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2147 | 0.0159 | -0.0118 [-0.0256, +0.0004] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0115 | 0.0200 | +0.0029 [-0.0022, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0596 | 0.1165 | +0.0259 [+0.0065, +0.0493] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0199 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1334 | 0.0031 | +0.0033 [-0.0018, +0.0090] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1375 | 0.4146 | 0.0493 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.436 | 0.580 | 0.2950 | 0.2474 | +0.0286 [+0.0016, +0.0611] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1110 | 0.1133 | +0.0370 [+0.0118, +0.0646] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.523 | 0.1064 | 0.0630 | +0.0064 [-0.0005, +0.0150] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.571 | 0.3198 | 0.2903 | +0.0954 [+0.0433, +0.1471] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1332 | 0.1461 | +0.0711 [+0.0389, +0.1082] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2876 | 0.2213 |

## risk_logistic_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.640] | 0.231 | 4.19 flat / 1.74 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.565] | 0.231 | 3.27 flat / 1.28 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.474] | 2.154 [1.151, 3.500] | 0.827 [0.444, 1.339] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.808 [0.929, 2.955] | 0.663 [0.336, 1.096] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.409] | 1.885 [0.900, 3.200] | 0.654 [0.315, 1.094] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.103, 0.367] | 1.731 [0.791, 2.952] | 0.644 [0.305, 1.100] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 2.308 [1.217, 3.783] | 0.971 [0.509, 1.588] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 4.882 [2.800, 8.084] | 1.794 [0.984, 3.072] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 2.889 (no interval) | 1.639 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 124 | 0.486 | 0.548 | 0.0576 | +0.0138 [+0.0062, +0.0218] | -0.0012 [-0.0074, +0.0052] | 0.848 | 0.453 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 83 | 0.259 | 0.434 | 0.0674 | +0.0036 [-0.0024, +0.0100] | -0.0064 [-0.0119, -0.0005] | 0.783 | 0.232 | no |
| 3 | 0.452 (147 of 1871 days never flag) | 91 | 0.304 | 0.462 | 0.0698 | +0.0009 [-0.0045, +0.0063] | -0.0054 [-0.0107, +0.0005] | 0.735 | 0.276 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 80 | 0.254 | 0.438 | 0.0699 | +0.0009 [-0.0048, +0.0066] | -0.0075 [-0.0133, -0.0019] | 0.755 | 0.228 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 105 | 0.326 | 0.429 | 0.0724 | -0.0015 [-0.0077, +0.0047] | -0.0090 [-0.0163, -0.0020] | 0.730 | 0.291 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.551 (climatology 0.457, difference +0.0939 [-0.0117, +0.1875]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0345 [+0.0193, +0.0507], realised minus predicted -0.0253 [-0.0603, +0.0117]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.561 | 0.2977 | 0.2720 | +0.0367 [+0.0030, +0.0701] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2108 | 0.0159 | -0.0106 [-0.0241, +0.0012] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0358 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0115 | 0.0200 | +0.0029 [-0.0020, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.778 | 0.0578 | 0.1165 | +0.0254 [+0.0060, +0.0476] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0199 | 0.0048 | +0.0082 [+0.0066, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1312 | 0.0031 | +0.0036 [-0.0018, +0.0094] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1357 | 0.4146 | 0.0462 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.545 | 0.2960 | 0.2474 | +0.0303 [+0.0006, +0.0605] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1090 | 0.1133 | +0.0395 [+0.0138, +0.0665] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.495 | 0.1068 | 0.0630 | +0.0065 [-0.0012, +0.0147] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3205 | 0.2903 | +0.0964 [+0.0460, +0.1407] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1254 | 0.1461 | +0.0736 [+0.0423, +0.1115] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2935 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.258 | 4.46 flat / 1.94 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.630] | 0.231 | 3.92 flat / 1.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.071, 0.346] | 1.500 [0.788, 2.536] | 0.567 [0.309, 0.952] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.233] | 0.654 [0.167, 1.500] | 0.231 [0.060, 0.521] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.193, 0.500] | 2.038 [1.148, 3.286] | 0.904 [0.537, 1.445] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.269, 0.591] | 2.538 [1.428, 4.219] | 1.000 [0.595, 1.614] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 2.769 [1.375, 4.750] | 1.221 [0.537, 2.250] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.875] | 5.588 [3.294, 9.333] | 2.294 [1.259, 4.001] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.333 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (147 of 1873 days never flag) | 92 | 0.379 | 0.576 | 0.0580 | +0.0134 [+0.0057, +0.0213] | -0.0017 [-0.0078, +0.0046] | 0.846 | 0.356 | no |
| 2 | 0.855 (147 of 1872 days never flag) | 50 | 0.237 | 0.660 | 0.0629 | +0.0082 [+0.0014, +0.0149] | -0.0018 [-0.0083, +0.0049] | 0.811 | 0.228 | no |
| 3 | 0.466 (126 of 1871 days never flag) | 108 | 0.399 | 0.509 | 0.0654 | +0.0053 [-0.0005, +0.0115] | -0.0011 [-0.0070, +0.0052] | 0.766 | 0.368 | no |
| 4 | 0.53 (126 of 1870 days never flag) | 132 | 0.478 | 0.500 | 0.0652 | +0.0056 [-0.0007, +0.0118] | -0.0028 [-0.0095, +0.0039] | 0.790 | 0.440 | yes |
| 5 | 0.855 (147 of 1869 days never flag) | 127 | 0.399 | 0.433 | 0.0664 | +0.0046 [-0.0017, +0.0108] | -0.0030 [-0.0094, +0.0041] | 0.775 | 0.357 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.688 (climatology 0.457, difference +0.2306 [+0.1064, +0.3600]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0854, ΔBrier vs climatology +0.0441 [+0.0266, +0.0647], realised minus predicted -0.0465 [-0.0785, -0.0127]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.608 | 0.2948 | 0.2720 | +0.0350 [+0.0041, +0.0699] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2147 | 0.0159 | -0.0118 [-0.0254, -0.0001] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0115 | 0.0200 | +0.0029 [-0.0022, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0596 | 0.1165 | +0.0259 [+0.0057, +0.0500] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0199 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1334 | 0.0031 | +0.0033 [-0.0020, +0.0087] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1375 | 0.4146 | 0.0493 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.436 | 0.580 | 0.2950 | 0.2474 | +0.0286 [+0.0005, +0.0585] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1110 | 0.1133 | +0.0370 [+0.0113, +0.0640] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.523 | 0.1064 | 0.0630 | +0.0064 [-0.0010, +0.0143] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.571 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1506] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1332 | 0.1461 | +0.0711 [+0.0377, +0.1093] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2876 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.231, 0.545] | 0.231 | 3.96 flat / 1.54 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.200, 0.500] | 0.231 | 2.65 flat / 1.12 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 2.154 [1.133, 3.594] | 0.827 [0.450, 1.368] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 2.115 [1.100, 3.438] | 0.760 [0.404, 1.238] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 0.654 [0.308, 1.133] | 0.356 [0.149, 0.640] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.077 [1.194, 3.304] | 0.933 [0.546, 1.484] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.577 [0.567, 3.000] | 0.577 [0.214, 1.078] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.733] | 5.000 [2.923, 8.000] | 1.779 [1.029, 2.862] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.333] | 2.000 [1.000, 4.333] | 1.083 [0.482, 2.608] |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 124 | 0.486 | 0.548 | 0.0576 | +0.0138 [+0.0061, +0.0216] | -0.0012 [-0.0074, +0.0055] | 0.848 | 0.453 | no |
| 2 | 0.831 (126 of 1872 days never flag) | 107 | 0.374 | 0.486 | 0.0625 | +0.0085 [+0.0021, +0.0151] | -0.0015 [-0.0078, +0.0055] | 0.813 | 0.342 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 48 | 0.225 | 0.646 | 0.0649 | +0.0058 [-0.0001, +0.0120] | -0.0005 [-0.0069, +0.0059] | 0.766 | 0.215 | no |
| 4 | 0.492 (126 of 1870 days never flag) | 100 | 0.333 | 0.460 | 0.0650 | +0.0058 [-0.0004, +0.0119] | -0.0027 [-0.0092, +0.0039] | 0.789 | 0.302 | no |
| 5 | 0.872 (147 of 1869 days never flag) | 86 | 0.326 | 0.523 | 0.0665 | +0.0044 [-0.0019, +0.0104] | -0.0031 [-0.0097, +0.0038] | 0.775 | 0.302 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.690 (climatology 0.457, difference +0.2325 [+0.1054, +0.3633]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0447 [+0.0263, +0.0654], realised minus predicted -0.0465 [-0.0772, -0.0132]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.561 | 0.2977 | 0.2720 | +0.0367 [+0.0032, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2108 | 0.0159 | -0.0106 [-0.0239, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0358 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0115 | 0.0200 | +0.0029 [-0.0021, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.778 | 0.0578 | 0.1165 | +0.0254 [+0.0063, +0.0474] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0199 | 0.0048 | +0.0082 [+0.0066, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1312 | 0.0031 | +0.0036 [-0.0016, +0.0096] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1357 | 0.4146 | +0.0462 [-0.0117, +0.1057] |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.545 | 0.2960 | 0.2474 | +0.0303 [+0.0009, +0.0611] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1090 | 0.1133 | +0.0395 [+0.0139, +0.0668] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.495 | 0.1068 | 0.0630 | +0.0065 [-0.0009, +0.0145] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3205 | 0.2903 | +0.0964 [+0.0465, +0.1429] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1254 | 0.1461 | +0.0736 [+0.0426, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2935 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 4.04 flat / 1.54 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.172, 0.526] | 0.231 | 3.12 flat / 1.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.151, 0.485] | 2.462 [1.258, 4.043] | 0.875 [0.456, 1.442] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.192 [0.461, 2.261] | 0.442 [0.161, 0.856] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.333] | 1.923 [0.946, 3.270] | 0.750 [0.349, 1.324] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 1.692 [0.741, 3.050] | 0.683 [0.293, 1.250] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.444] | 2.385 [1.154, 4.174] | 0.885 [0.435, 1.521] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.434, 0.867] | 5.647 [3.478, 9.003] | 1.926 [1.171, 3.075] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.000 [0.167, 2.750] | 0.806 [0.083, 2.350] |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (126 of 1873 days never flag) | 129 | 0.464 | 0.504 | 0.0620 | +0.0094 [-0.0019, +0.0199] | -0.0056 [-0.0170, +0.0039] | 0.888 | 0.427 | no |
| 2 | 0.625 (147 of 1872 days never flag) | 60 | 0.209 | 0.483 | 0.0678 | +0.0033 [-0.0059, +0.0114] | -0.0067 [-0.0155, +0.0010] | 0.852 | 0.191 | no |
| 3 | 0.62 (147 of 1871 days never flag) | 89 | 0.283 | 0.438 | 0.0707 | -0.0000 [-0.0103, +0.0099] | -0.0063 [-0.0168, +0.0034] | 0.851 | 0.254 | no |
| 4 | 0.714 (147 of 1870 days never flag) | 79 | 0.254 | 0.443 | 0.0688 | +0.0020 [-0.0061, +0.0094] | -0.0064 [-0.0146, +0.0015] | 0.838 | 0.228 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 127 | 0.471 | 0.512 | 0.0726 | -0.0016 [-0.0116, +0.0068] | -0.0092 [-0.0191, -0.0005] | 0.814 | 0.435 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.607 (climatology 0.457, difference +0.1496 [+0.0261, +0.2537]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0903, ΔBrier vs climatology +0.0391 [+0.0232, +0.0572], realised minus predicted +0.0093 [-0.0245, +0.0442]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.500 | 0.3264 | 0.2720 | +0.0018 [-0.0510, +0.0508] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1562 | 0.0159 | +0.0017 [-0.0245, +0.0223] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0111, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0001, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0628 | 0.1165 | +0.0242 [+0.0067, +0.0464] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0024 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0706 | 0.0031 | +0.0216 [+0.0162, +0.0270] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1023 | 0.4146 | 0.0458 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.504 | 0.3283 | 0.2474 | -0.0019 [-0.0477, +0.0402] |
| day_type | month_end | 150 | 17 | 0.412 | 0.636 | 0.1090 | 0.1133 | +0.0382 [+0.0115, +0.0657] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.456 | 0.0915 | 0.0630 | +0.0017 [-0.0106, +0.0128] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0398, +0.1503] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1332 | 0.1461 | +0.0711 [+0.0382, +0.1087] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2778 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.258, 0.609] | 0.231 | 3.81 flat / 1.45 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.481] | 0.231 | 3.00 flat / 1.09 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.481] | 2.269 [1.125, 3.667] | 0.846 [0.433, 1.343] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.077 [0.364, 2.048] | 0.385 [0.129, 0.741] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.846 [0.840, 3.177] | 0.577 [0.250, 1.014] |
| lead 4 alone (fail) | 26 | 3 | 0.115 [0.029, 0.231] | 0.962 [0.308, 1.875] | 0.346 [0.102, 0.695] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.083, 0.394] | 2.385 [1.151, 4.000] | 0.904 [0.438, 1.546] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.857] | 5.471 [3.332, 8.584] | 1.897 [1.147, 2.967] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.667 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 117 | 0.414 | 0.496 | 0.0615 | +0.0099 [-0.0011, +0.0201] | -0.0052 [-0.0155, +0.0039] | 0.889 | 0.380 | no |
| 2 | 0.604 (147 of 1872 days never flag) | 58 | 0.216 | 0.517 | 0.0669 | +0.0041 [-0.0053, +0.0125] | -0.0059 [-0.0149, +0.0022] | 0.854 | 0.200 | no |
| 3 | 0.638 (147 of 1871 days never flag) | 90 | 0.304 | 0.467 | 0.0683 | +0.0023 [-0.0087, +0.0117] | -0.0040 [-0.0143, +0.0053] | 0.854 | 0.277 | no |
| 4 | 0.665 (147 of 1870 days never flag) | 46 | 0.152 | 0.457 | 0.0675 | +0.0034 [-0.0044, +0.0103] | -0.0051 [-0.0131, +0.0022] | 0.839 | 0.138 | no |
| 5 | 0.711 (147 of 1869 days never flag) | 126 | 0.464 | 0.508 | 0.0731 | -0.0022 [-0.0126, +0.0067] | -0.0097 [-0.0198, -0.0007] | 0.820 | 0.428 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.568 (climatology 0.457, difference +0.1111 [+0.0069, +0.2064]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0880, ΔBrier vs climatology +0.0415 [+0.0256, +0.0583], realised minus predicted +0.0101 [-0.0217, +0.0437]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.487 | 0.3293 | 0.2720 | +0.0035 [-0.0474, +0.0484] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.1524 | 0.0159 | +0.0029 [-0.0224, +0.0236] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0610 | 0.1165 | +0.0236 [+0.0065, +0.0443] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0685 | 0.0031 | +0.0218 [+0.0158, +0.0275] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1006 | 0.4146 | 0.0427 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.496 | 0.3293 | 0.2474 | -0.0002 [-0.0436, +0.0411] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1070 | 0.1133 | +0.0408 [+0.0139, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.427 | 0.0919 | 0.0630 | +0.0018 [-0.0104, +0.0126] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0473, +0.1441] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1254 | 0.1461 | +0.0736 [+0.0406, +0.1106] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2837 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.278, 0.640] | 0.231 | 3.35 flat / 1.36 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.595] | 0.192 | 2.31 flat / 0.92 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.462 [1.289, 4.044] | 0.875 [0.458, 1.440] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.103, 0.385] | 1.577 [0.731, 2.783] | 0.712 [0.375, 1.210] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 1.692 [0.833, 2.867] | 0.663 [0.346, 1.095] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.219, 0.552] | 2.077 [1.077, 3.483] | 0.808 [0.448, 1.327] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.038, 0.286] | 1.654 [0.714, 2.945] | 0.596 [0.263, 1.071] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 4.765 [2.800, 7.668] | 1.750 [1.038, 2.884] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.667 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (126 of 1873 days never flag) | 129 | 0.464 | 0.504 | 0.0620 | +0.0094 [-0.0018, +0.0197] | -0.0056 [-0.0156, +0.0034] | 0.888 | 0.427 | no |
| 2 | 0.625 (126 of 1872 days never flag) | 83 | 0.302 | 0.506 | 0.0635 | +0.0075 [-0.0020, +0.0163] | -0.0025 [-0.0121, +0.0063] | 0.865 | 0.278 | no |
| 3 | 0.852 (126 of 1871 days never flag) | 94 | 0.362 | 0.532 | 0.0654 | +0.0053 [-0.0052, +0.0143] | -0.0010 [-0.0120, +0.0083] | 0.863 | 0.337 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 111 | 0.413 | 0.514 | 0.0637 | +0.0071 [-0.0008, +0.0145] | -0.0014 [-0.0098, +0.0065] | 0.854 | 0.382 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 91 | 0.348 | 0.527 | 0.0680 | +0.0029 [-0.0065, +0.0113] | -0.0046 [-0.0141, +0.0041] | 0.840 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.686 (climatology 0.457, difference +0.2293 [+0.1086, +0.3544]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0809, ΔBrier vs climatology +0.0486 [+0.0310, +0.0681], realised minus predicted -0.0105 [-0.0414, +0.0218]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.500 | 0.3264 | 0.2720 | +0.0018 [-0.0497, +0.0508] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1562 | 0.0159 | +0.0017 [-0.0241, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0003, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0628 | 0.1165 | +0.0242 [+0.0064, +0.0470] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0024 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0706 | 0.0031 | +0.0216 [+0.0159, +0.0269] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1023 | 0.4146 | 0.0458 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.504 | 0.3283 | 0.2474 | -0.0019 [-0.0448, +0.0391] |
| day_type | month_end | 150 | 17 | 0.412 | 0.636 | 0.1090 | 0.1133 | +0.0382 [+0.0124, +0.0666] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.456 | 0.0915 | 0.0630 | +0.0017 [-0.0103, +0.0129] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0391, +0.1510] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1332 | 0.1461 | +0.0711 [+0.0367, +0.1093] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2778 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.214, 0.562] | 0.231 | 3.35 flat / 1.29 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.176, 0.500] | 0.192 | 1.85 flat / 0.73 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.148, 0.481] | 2.269 [1.125, 3.773] | 0.846 [0.435, 1.400] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.421] | 2.154 [1.153, 3.500] | 0.846 [0.474, 1.346] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.042, 0.280] | 0.731 [0.189, 1.591] | 0.327 [0.098, 0.694] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.467] | 1.346 [0.591, 2.552] | 0.529 [0.231, 0.982] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.385 [0.526, 2.690] | 0.519 [0.214, 0.984] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.370, 0.810] | 4.824 [2.857, 7.668] | 1.750 [1.050, 2.783] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.556 (no interval) | 0.417 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 117 | 0.414 | 0.496 | 0.0615 | +0.0099 [-0.0016, +0.0204] | -0.0052 [-0.0155, +0.0043] | 0.889 | 0.380 | no |
| 2 | 0.625 (126 of 1872 days never flag) | 111 | 0.396 | 0.495 | 0.0631 | +0.0079 [-0.0013, +0.0163] | -0.0021 [-0.0110, +0.0065] | 0.867 | 0.363 | no |
| 3 | 0.863 (147 of 1871 days never flag) | 47 | 0.203 | 0.596 | 0.0648 | +0.0059 [-0.0050, +0.0150] | -0.0005 [-0.0114, +0.0085] | 0.864 | 0.192 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 75 | 0.290 | 0.533 | 0.0636 | +0.0072 [-0.0007, +0.0147] | -0.0012 [-0.0092, +0.0067] | 0.854 | 0.270 | no |
| 5 | 0.872 (147 of 1869 days never flag) | 76 | 0.290 | 0.526 | 0.0682 | +0.0028 [-0.0068, +0.0114] | -0.0048 [-0.0146, +0.0042] | 0.840 | 0.269 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.688 (climatology 0.457, difference +0.2312 [+0.1049, +0.3598]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0801, ΔBrier vs climatology +0.0494 [+0.0316, +0.0698], realised minus predicted -0.0103 [-0.0398, +0.0223]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.487 | 0.3293 | 0.2720 | +0.0035 [-0.0478, +0.0524] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.1524 | 0.0159 | +0.0029 [-0.0224, +0.0237] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0005, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0610 | 0.1165 | +0.0236 [+0.0061, +0.0466] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0685 | 0.0031 | +0.0218 [+0.0160, +0.0276] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1006 | 0.4146 | 0.0427 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.496 | 0.3293 | 0.2474 | -0.0002 [-0.0444, +0.0405] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1070 | 0.1133 | +0.0408 [+0.0149, +0.0683] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.427 | 0.0919 | 0.0630 | +0.0018 [-0.0104, +0.0132] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0477, +0.1427] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1254 | 0.1461 | +0.0736 [+0.0406, +0.1119] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2837 | 0.2213 |

## risk_logistic_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.690] | 0.269 | 4.81 flat / 2.04 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.233, 0.611] | 0.231 | 3.88 flat / 1.67 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.435] | 2.654 [1.435, 4.177] | 0.942 [0.489, 1.466] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.292] | 1.654 [0.692, 2.955] | 0.769 [0.287, 1.431] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.435] | 2.846 [1.485, 4.667] | 1.317 [0.621, 2.334] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.769 [0.895, 3.077] | 0.760 [0.379, 1.342] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.480] | 2.962 [1.548, 4.924] | 1.308 [0.617, 2.334] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 6.882 [4.333, 10.701] | 2.691 [1.568, 4.322] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.889 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (126 of 1873 days never flag) | 141 | 0.514 | 0.511 | 0.0554 | +0.0160 [+0.0082, +0.0243] | +0.0009 [-0.0058, +0.0075] | 0.880 | 0.474 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 72 | 0.209 | 0.403 | 0.0642 | +0.0068 [+0.0001, +0.0135] | -0.0032 [-0.0097, +0.0031] | 0.841 | 0.184 | no |
| 3 | 0.532 (147 of 1871 days never flag) | 119 | 0.326 | 0.378 | 0.0668 | +0.0039 [-0.0031, +0.0106] | -0.0024 [-0.0093, +0.0044] | 0.833 | 0.283 | no |
| 4 | 0.519 (147 of 1870 days never flag) | 79 | 0.239 | 0.418 | 0.0665 | +0.0043 [-0.0024, +0.0108] | -0.0041 [-0.0115, +0.0033] | 0.820 | 0.213 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 138 | 0.442 | 0.442 | 0.0684 | +0.0026 [-0.0037, +0.0083] | -0.0050 [-0.0119, +0.0014] | 0.788 | 0.398 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.605 (climatology 0.457, difference +0.1474 [+0.0279, +0.2623]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0922, ΔBrier vs climatology +0.0373 [+0.0221, +0.0542], realised minus predicted +0.0063 [-0.0262, +0.0425]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.500 | 0.2920 | 0.2720 | +0.0330 [-0.0021, +0.0683] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1792 | 0.0159 | +0.0014 [-0.0168, +0.0162] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0037 | 0.0200 | +0.0040 [+0.0002, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0604 | 0.1165 | +0.0274 [+0.0071, +0.0533] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0050 | 0.0048 | +0.0093 [+0.0077, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0934 | 0.0031 | +0.0169 [+0.0120, +0.0221] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1096 | 0.4146 | +0.0477 [+0.0041, +0.0965] |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.507 | 0.2978 | 0.2474 | +0.0272 [-0.0032, +0.0594] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1095 | 0.1133 | +0.0383 [+0.0115, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.464 | 0.0889 | 0.0630 | +0.0093 [+0.0016, +0.0178] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1501] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1332 | 0.1461 | +0.0711 [+0.0387, +0.1075] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2436 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.688] | 0.269 | 4.62 flat / 1.92 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.609] | 0.231 | 3.88 flat / 1.64 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 2.808 [1.552, 4.467] | 1.010 [0.562, 1.594] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.577 [0.628, 2.889] | 0.721 [0.257, 1.397] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 2.962 [1.469, 5.048] | 1.192 [0.510, 2.188] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.654 [0.750, 2.917] | 0.625 [0.285, 1.109] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.143, 0.485] | 3.000 [1.591, 5.091] | 1.365 [0.660, 2.433] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.706 [4.250, 10.500] | 2.632 [1.553, 4.432] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.667 (no interval) | 0.583 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 139 | 0.471 | 0.475 | 0.0550 | +0.0164 [+0.0085, +0.0250] | +0.0013 [-0.0052, +0.0081] | 0.882 | 0.429 | no |
| 2 | 0.532 (147 of 1872 days never flag) | 72 | 0.223 | 0.431 | 0.0634 | +0.0077 [+0.0013, +0.0144] | -0.0023 [-0.0085, +0.0039] | 0.842 | 0.199 | no |
| 3 | 0.638 (147 of 1871 days never flag) | 128 | 0.370 | 0.398 | 0.0644 | +0.0063 [+0.0003, +0.0123] | -0.0001 [-0.0060, +0.0061] | 0.834 | 0.325 | no |
| 4 | 0.524 (147 of 1870 days never flag) | 77 | 0.246 | 0.442 | 0.0652 | +0.0056 [-0.0003, +0.0114] | -0.0028 [-0.0091, +0.0035] | 0.821 | 0.222 | no |
| 5 | 0.519 (147 of 1869 days never flag) | 139 | 0.442 | 0.439 | 0.0689 | +0.0020 [-0.0049, +0.0086] | -0.0055 [-0.0129, +0.0017] | 0.792 | 0.397 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.565 (climatology 0.457, difference +0.1076 [+0.0058, +0.2018]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0899, ΔBrier vs climatology +0.0395 [+0.0247, +0.0557], realised minus predicted +0.0069 [-0.0256, +0.0422]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.459 | 0.2949 | 0.2720 | +0.0348 [-0.0003, +0.0707] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.1753 | 0.0159 | +0.0026 [-0.0142, +0.0183] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0037 | 0.0200 | +0.0040 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0586 | 0.1165 | +0.0268 [+0.0076, +0.0506] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0049 | 0.0048 | +0.0094 [+0.0077, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0912 | 0.0031 | +0.0171 [+0.0119, +0.0229] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1079 | 0.4146 | 0.0446 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.471 | 0.2988 | 0.2474 | +0.0290 [-0.0012, +0.0611] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1075 | 0.1133 | +0.0408 [+0.0150, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.407 | 0.0893 | 0.0630 | +0.0094 [+0.0015, +0.0180] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0443, +0.1443] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1254 | 0.1461 | +0.0736 [+0.0413, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2495 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.258 | 4.46 flat / 1.90 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.667] | 0.231 | 3.54 flat / 1.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.435] | 2.654 [1.478, 4.231] | 0.942 [0.524, 1.513] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.962 [0.250, 1.883] | 0.356 [0.096, 0.716] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.692 [0.889, 2.813] | 0.625 [0.344, 1.019] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.632] | 3.346 [1.846, 5.481] | 1.519 [0.790, 2.560] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 2.654 [1.270, 4.591] | 1.173 [0.492, 2.179] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.529 [4.000, 10.154] | 2.662 [1.516, 4.478] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 0.556 [0.182, 1.333] | 0.472 [0.125, 1.208] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (126 of 1873 days never flag) | 141 | 0.514 | 0.511 | 0.0554 | +0.0160 [+0.0080, +0.0246] | +0.0009 [-0.0054, +0.0075] | 0.880 | 0.474 | no |
| 2 | 0.855 (126 of 1872 days never flag) | 55 | 0.216 | 0.545 | 0.0594 | +0.0117 [+0.0045, +0.0190] | +0.0017 [-0.0055, +0.0087] | 0.857 | 0.201 | no |
| 3 | 0.852 (126 of 1871 days never flag) | 99 | 0.399 | 0.556 | 0.0609 | +0.0098 [+0.0029, +0.0165] | +0.0035 [-0.0031, +0.0102] | 0.847 | 0.373 | no |
| 4 | 0.53 (126 of 1870 days never flag) | 153 | 0.478 | 0.431 | 0.0610 | +0.0098 [+0.0031, +0.0165] | +0.0013 [-0.0060, +0.0084] | 0.842 | 0.428 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 121 | 0.377 | 0.430 | 0.0634 | +0.0075 [+0.0014, +0.0138] | +0.0000 [-0.0065, +0.0067] | 0.825 | 0.337 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.688 (climatology 0.457, difference +0.2306 [+0.1125, +0.3599]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0809, ΔBrier vs climatology +0.0486 [+0.0303, +0.0676], realised minus predicted -0.0147 [-0.0461, +0.0185]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.500 | 0.2920 | 0.2720 | +0.0330 [-0.0004, +0.0702] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1792 | 0.0159 | +0.0014 [-0.0162, +0.0167] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0144] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0037 | 0.0200 | +0.0040 [+0.0003, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0604 | 0.1165 | +0.0274 [+0.0072, +0.0531] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0050 | 0.0048 | +0.0093 [+0.0077, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0934 | 0.0031 | +0.0169 [+0.0120, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1096 | 0.4146 | +0.0477 [+0.0039, +0.0999] |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.507 | 0.2978 | 0.2474 | +0.0272 [-0.0035, +0.0605] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1095 | 0.1133 | +0.0383 [+0.0121, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.464 | 0.0889 | 0.0630 | +0.0093 [+0.0014, +0.0178] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0393, +0.1501] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1332 | 0.1461 | +0.0711 [+0.0405, +0.1094] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2436 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.240, 0.600] | 0.250 | 4.38 flat / 1.80 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.567] | 0.231 | 3.12 flat / 1.37 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.136, 0.469] | 2.808 [1.500, 4.409] | 1.010 [0.538, 1.580] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 1.615 [0.700, 2.789] | 0.596 [0.271, 1.010] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.031, 0.222] | 0.731 [0.200, 1.500] | 0.288 [0.091, 0.593] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.150, 0.458] | 2.577 [1.267, 4.421] | 1.183 [0.509, 2.190] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.429] | 2.538 [1.133, 4.451] | 1.115 [0.428, 2.129] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 6.588 [4.053, 10.202] | 2.676 [1.536, 4.430] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.222 (no interval) | 0.139 (no interval) |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 139 | 0.471 | 0.475 | 0.0550 | +0.0164 [+0.0084, +0.0250] | +0.0013 [-0.0055, +0.0078] | 0.882 | 0.429 | no |
| 2 | 0.831 (126 of 1872 days never flag) | 87 | 0.324 | 0.517 | 0.0590 | +0.0121 [+0.0046, +0.0190] | +0.0021 [-0.0050, +0.0092] | 0.859 | 0.300 | no |
| 3 | 0.863 (147 of 1871 days never flag) | 52 | 0.239 | 0.635 | 0.0603 | +0.0104 [+0.0038, +0.0170] | +0.0041 [-0.0025, +0.0108] | 0.848 | 0.228 | no |
| 4 | 0.868 (126 of 1870 days never flag) | 116 | 0.355 | 0.422 | 0.0609 | +0.0100 [+0.0037, +0.0164] | +0.0015 [-0.0050, +0.0085] | 0.841 | 0.316 | no |
| 5 | 0.872 (147 of 1869 days never flag) | 117 | 0.370 | 0.436 | 0.0635 | +0.0074 [+0.0009, +0.0136] | -0.0001 [-0.0072, +0.0068] | 0.825 | 0.331 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.690 (climatology 0.457, difference +0.2325 [+0.1076, +0.3648]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0802, ΔBrier vs climatology +0.0493 [+0.0310, +0.0688], realised minus predicted -0.0147 [-0.0461, +0.0174]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.459 | 0.2949 | 0.2720 | +0.0348 [+0.0000, +0.0727] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.1753 | 0.0159 | +0.0026 [-0.0159, +0.0173] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0037 | 0.0200 | +0.0040 [+0.0005, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0586 | 0.1165 | +0.0268 [+0.0073, +0.0513] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0049 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0912 | 0.0031 | +0.0171 [+0.0120, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1079 | 0.4146 | 0.0446 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.471 | 0.2988 | 0.2474 | +0.0290 [-0.0021, +0.0612] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1075 | 0.1133 | +0.0408 [+0.0146, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.407 | 0.0893 | 0.0630 | +0.0094 [+0.0012, +0.0179] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0461, +0.1405] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1254 | 0.1461 | +0.0736 [+0.0412, +0.1126] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2495 | 0.2213 |

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.231 | 4.12 flat / 3.39 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 3.19 flat / 2.56 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.680] | 2.423 [1.555, 3.824] | 1.798 [1.029, 3.097] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 1.538 [0.964, 2.424] | 0.981 [0.500, 1.750] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.414] | 1.577 [0.938, 2.579] | 1.106 [0.554, 1.968] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.538 [1.697, 4.000] | 1.962 [1.209, 3.319] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.136, 0.429] | 1.846 [1.132, 3.000] | 1.375 [0.750, 2.500] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 1.412 [0.833, 2.400] | 0.706 [0.352, 1.375] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.222 (no interval) | 8.472 (no interval) |

Recall with equal weight per regime: 0.332 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.148 (42 of 1873 days never flag) | 107 | 0.314 | 0.411 | 0.0632 | +0.0082 [+0.0025, +0.0141] | -0.0069 [-0.0152, +0.0007] | 0.645 | 0.278 | no |
| 2 | 0.283 (126 of 1872 days never flag) | 69 | 0.209 | 0.420 | 0.0676 | +0.0034 [-0.0039, +0.0105] | -0.0066 [-0.0149, +0.0014] | 0.578 | 0.186 | no |
| 3 | 0.184 (126 of 1871 days never flag) | 67 | 0.188 | 0.388 | 0.0669 | +0.0038 [-0.0032, +0.0106] | -0.0025 [-0.0103, +0.0048] | 0.581 | 0.165 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 95 | 0.210 | 0.305 | 0.0672 | +0.0037 [-0.0026, +0.0097] | -0.0048 [-0.0124, +0.0018] | 0.580 | 0.172 | no |
| 5 | 0.402 (126 of 1869 days never flag) | 74 | 0.188 | 0.351 | 0.0669 | +0.0040 [-0.0026, +0.0101] | -0.0035 [-0.0110, +0.0034] | 0.581 | 0.161 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 4.1 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 3.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.457, difference +0.1837 [+0.0710, +0.2966]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1101, ΔBrier vs climatology +0.0193 [+0.0086, +0.0311], realised minus predicted +0.0574 [+0.0238, +0.0943]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.588 | 0.1014 | 0.2720 | -0.0090 [-0.0307, +0.0131] |
| regime | 2020 | 251 | 4 | 0.250 | 0.029 | 0.0608 | 0.0159 | +0.0085 [-0.0055, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0110 | 0.0200 | +0.0019 [-0.0033, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.0481 | 0.1165 | +0.0239 [+0.0054, +0.0480] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0056 | 0.0048 | +0.0087 [+0.0068, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.038 | 0.0339 | 0.0031 | +0.0134 [+0.0040, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.1154 | 0.4146 | 0.0760 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.325 | 0.535 | 0.1028 | 0.2474 | -0.0022 [-0.0208, +0.0174] |
| day_type | month_end | 150 | 17 | 0.765 | 0.419 | 0.1226 | 0.1133 | +0.0234 [-0.0109, +0.0571] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.395 | 0.0150 | 0.0630 | +0.0014 [-0.0042, +0.0066] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3534 | 0.2903 | +0.1102 [+0.0260, +0.1974] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.417 | 0.1886 | 0.1461 | +0.0706 [+0.0331, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.231 | 2.54 flat / 1.80 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.542] | 0.154 | 1.65 flat / 1.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.325, 0.667] | 1.885 [1.222, 2.952] | 1.250 [0.704, 2.179] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 1.654 [1.000, 2.579] | 1.096 [0.559, 1.943] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 1.500 [0.900, 2.400] | 1.000 [0.500, 1.781] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.719, 1.667] | 0.558 [0.286, 0.991] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.294 [0.731, 2.091] | 0.529 [0.250, 0.969] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.889 (no interval) | 4.194 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 93 | 0.314 | 0.473 | 0.0630 | +0.0084 [+0.0021, +0.0147] | -0.0067 [-0.0153, +0.0016] | 0.635 | 0.286 | no |
| 2 | 0.431 (147 of 1872 days never flag) | 73 | 0.216 | 0.411 | 0.0687 | +0.0024 [-0.0054, +0.0093] | -0.0076 [-0.0168, -0.0001] | 0.582 | 0.191 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 69 | 0.217 | 0.435 | 0.0670 | +0.0037 [-0.0037, +0.0105] | -0.0026 [-0.0108, +0.0047] | 0.585 | 0.195 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0669 | +0.0039 [-0.0034, +0.0110] | -0.0045 [-0.0128, +0.0033] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 53 | 0.188 | 0.491 | 0.0670 | +0.0039 [-0.0030, +0.0107] | -0.0036 [-0.0120, +0.0040] | 0.585 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.457, difference +0.1367 [-0.0372, +0.2817]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1051, ΔBrier vs climatology +0.0244 [+0.0124, +0.0374], realised minus predicted +0.0555 [+0.0217, +0.0899]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1199 | 0.2720 | -0.0169 [-0.0413, +0.0085] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.0469 | 0.0159 | +0.0220 [+0.0121, +0.0313] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0048, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0509 | 0.1165 | +0.0242 [+0.0051, +0.0465] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0271 | 0.0031 | +0.0196 [+0.0120, +0.0263] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0959 | 0.4146 | 0.0536 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.1179 | 0.2474 | -0.0036 [-0.0259, +0.0196] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1397 | 0.1133 | +0.0244 [-0.0130, +0.0627] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.471 | 0.0159 | 0.0630 | +0.0028 [-0.0028, +0.0082] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3234 | 0.2903 | +0.0724 [-0.0002, +0.1368] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1034] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.409, 0.750] | 0.269 | 4.65 flat / 1.97 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 3.88 flat / 1.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.692 [1.000, 2.696] | 0.606 [0.348, 0.974] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.029, 0.222] | 1.231 [0.708, 2.042] | 0.538 [0.296, 0.898] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.531] | 1.885 [1.000, 3.235] | 0.750 [0.407, 1.272] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.192 [1.400, 3.412] | 0.933 [0.583, 1.524] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.231, 0.550] | 2.462 [1.533, 3.895] | 1.096 [0.676, 1.767] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 4.529 [2.600, 7.300] | 1.588 [0.924, 2.600] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.889 (no interval) | 2.694 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 109 | 0.464 | 0.596 | 0.0531 | +0.0183 [+0.0099, +0.0272] | +0.0032 [-0.0028, +0.0091] | 0.880 | 0.439 | yes |
| 2 | 0.431 (189 of 1872 days never flag) | 63 | 0.223 | 0.492 | 0.0601 | +0.0109 [+0.0048, +0.0174] | +0.0009 [-0.0038, +0.0057] | 0.846 | 0.205 | yes |
| 3 | 0.47 (126 of 1871 days never flag) | 95 | 0.333 | 0.484 | 0.0609 | +0.0098 [+0.0042, +0.0160] | +0.0035 [-0.0017, +0.0089] | 0.839 | 0.305 | yes |
| 4 | 0.407 (126 of 1870 days never flag) | 112 | 0.399 | 0.491 | 0.0594 | +0.0114 [+0.0051, +0.0183] | +0.0029 [-0.0025, +0.0088] | 0.849 | 0.366 | yes |
| 5 | 0.465 (126 of 1869 days never flag) | 113 | 0.355 | 0.434 | 0.0604 | +0.0106 [+0.0045, +0.0168] | +0.0030 [-0.0021, +0.0089] | 0.840 | 0.318 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.638 (climatology 0.457, difference +0.1812 [+0.0344, +0.3293]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0426 [+0.0255, +0.0618], realised minus predicted -0.0187 [-0.0484, +0.0128]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.500 | 0.637 | 0.2613 | 0.2720 | +0.0388 [+0.0076, +0.0711] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1496 | 0.0159 | +0.0057 [-0.0080, +0.0179] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0215 | 0.0000 | +0.0130 [+0.0112, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0419 | 0.0200 | -0.0015 [-0.0086, +0.0039] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1272 | 0.1165 | +0.0361 [+0.0035, +0.0761] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0266 | 0.0048 | +0.0074 [+0.0051, +0.0095] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0917 | 0.0031 | +0.0122 [+0.0038, +0.0191] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2801 | 0.4146 | +0.1230 [-0.0069, +0.2480] |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.624 | 0.2642 | 0.2474 | +0.0374 [+0.0092, +0.0655] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1490 | 0.1133 | +0.0296 [-0.0091, +0.0687] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.562 | 0.0893 | 0.0630 | +0.0139 [+0.0066, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [-0.0026, +0.1384] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.2039 | 0.1461 | +0.0602 [+0.0211, +0.1061] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.741] | 0.269 | 5.00 flat / 2.22 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.231 | 3.85 flat / 1.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.193, 0.514] | 2.308 [1.481, 3.429] | 1.000 [0.613, 1.583] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.031, 0.227] | 1.231 [0.708, 1.955] | 0.538 [0.297, 0.900] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.471] | 1.846 [0.970, 3.107] | 0.731 [0.393, 1.229] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.381, 3.381] | 0.923 [0.562, 1.510] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.632] | 3.154 [2.000, 4.824] | 1.327 [0.845, 2.094] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.765 [2.956, 7.584] | 1.676 [1.016, 2.705] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.091, 0.571] | 5.444 [3.286, 11.667] | 3.250 [1.821, 7.753] |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 119 | 0.421 | 0.496 | 0.0549 | +0.0165 [+0.0089, +0.0248] | +0.0014 [-0.0045, +0.0074] | 0.793 | 0.387 | no |
| 2 | 0.431 (189 of 1872 days never flag) | 63 | 0.223 | 0.492 | 0.0624 | +0.0087 [+0.0021, +0.0154] | -0.0013 [-0.0065, +0.0039] | 0.753 | 0.205 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 92 | 0.319 | 0.478 | 0.0609 | +0.0098 [+0.0034, +0.0159] | +0.0035 [-0.0022, +0.0089] | 0.755 | 0.291 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 110 | 0.391 | 0.491 | 0.0603 | +0.0105 [+0.0042, +0.0168] | +0.0021 [-0.0032, +0.0074] | 0.767 | 0.359 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 152 | 0.507 | 0.461 | 0.0610 | +0.0099 [+0.0038, +0.0166] | +0.0024 [-0.0032, +0.0079] | 0.754 | 0.460 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.611 (climatology 0.457, difference +0.1539 [-0.0041, +0.3022]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0888, ΔBrier vs climatology +0.0407 [+0.0240, +0.0588], realised minus predicted +0.0265 [-0.0007, +0.0545]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.529 | 0.1916 | 0.2720 | +0.0232 [-0.0055, +0.0539] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0545 | 0.0159 | +0.0147 [-0.0015, +0.0294] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0067 | 0.0000 | +0.0134 [+0.0115, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0243 | 0.0200 | -0.0014 [-0.0092, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1021 | 0.1165 | +0.0353 [+0.0043, +0.0720] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0126 | 0.0048 | +0.0076 [+0.0051, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0321 | 0.0031 | +0.0182 [+0.0098, +0.0252] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2513 | 0.4146 | +0.1209 [-0.0095, +0.2456] |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.525 | 0.1866 | 0.2474 | +0.0256 [+0.0006, +0.0513] |
| day_type | month_end | 150 | 17 | 0.706 | 0.667 | 0.1435 | 0.1133 | +0.0301 [-0.0079, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.434 | 0.0451 | 0.0630 | +0.0117 [+0.0052, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0022, +0.1388] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2039 | 0.1461 | +0.0602 [+0.0201, +0.1035] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.706] | 0.269 | 5.38 flat / 2.26 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.231 | 4.19 flat / 1.81 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.556] | 2.154 [1.310, 3.350] | 0.808 [0.483, 1.298] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.050, 0.276] | 1.231 [0.666, 2.091] | 0.490 [0.258, 0.859] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 2.269 [1.187, 3.808] | 1.038 [0.518, 1.857] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.267, 0.594] | 2.846 [1.743, 4.421] | 1.163 [0.704, 1.830] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.000 [1.250, 3.105] | 0.827 [0.500, 1.342] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.294 [4.052, 9.695] | 2.338 [1.406, 3.817] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.667 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 117 | 0.436 | 0.521 | 0.0534 | +0.0180 [+0.0110, +0.0257] | +0.0030 [-0.0026, +0.0089] | 0.865 | 0.403 | yes |
| 2 | 0.431 (168 of 1872 days never flag) | 70 | 0.273 | 0.543 | 0.0592 | +0.0119 [+0.0064, +0.0181] | +0.0019 [-0.0028, +0.0068] | 0.825 | 0.255 | yes |
| 3 | 0.47 (126 of 1871 days never flag) | 117 | 0.420 | 0.496 | 0.0592 | +0.0115 [+0.0060, +0.0179] | +0.0052 [-0.0003, +0.0113] | 0.832 | 0.386 | yes |
| 4 | 0.3 (126 of 1870 days never flag) | 141 | 0.486 | 0.475 | 0.0576 | +0.0132 [+0.0076, +0.0196] | +0.0048 [-0.0004, +0.0107] | 0.844 | 0.443 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 100 | 0.348 | 0.480 | 0.0583 | +0.0126 [+0.0069, +0.0186] | +0.0051 [-0.0005, +0.0109] | 0.842 | 0.318 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.642 (climatology 0.457, difference +0.1849 [+0.0258, +0.3217]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0876, ΔBrier vs climatology +0.0419 [+0.0250, +0.0587], realised minus predicted -0.0100 [-0.0406, +0.0204]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.461 | 0.511 | 0.2424 | 0.2720 | +0.0320 [+0.0027, +0.0622] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1402 | 0.0159 | +0.0109 [+0.0007, +0.0208] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0131 [+0.0115, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0338 | 0.0200 | +0.0008 [-0.0048, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.706 | 0.1117 | 0.1165 | +0.0362 [+0.0072, +0.0731] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0226 | 0.0048 | +0.0081 [+0.0063, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0842 | 0.0031 | +0.0140 [+0.0062, +0.0206] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.750 | 0.2415 | 0.4146 | +0.1166 [-0.0026, +0.2258] |
| scarcity_state | 3 | 473 | 117 | 0.462 | 0.519 | 0.2448 | 0.2474 | +0.0340 [+0.0083, +0.0603] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1460 | 0.1133 | +0.0259 [-0.0105, +0.0645] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.456 | 0.0788 | 0.0630 | +0.0139 [+0.0074, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0001, +0.1384] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1073] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2483 | 0.2213 |

## risk_quantile_skewt_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.739] | 0.258 | 4.46 flat / 1.88 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.323, 0.667] | 0.231 | 3.69 flat / 1.53 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 1.654 [1.000, 2.656] | 0.596 [0.356, 0.974] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.024, 0.227] | 1.192 [0.686, 1.952] | 0.519 [0.295, 0.891] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 1.846 [0.964, 3.074] | 0.740 [0.396, 1.250] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.077 [1.310, 3.185] | 0.885 [0.536, 1.421] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.538] | 2.385 [1.435, 3.704] | 1.038 [0.628, 1.658] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 4.529 [2.667, 7.286] | 1.588 [0.926, 2.584] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.417 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 108 | 0.464 | 0.602 | 0.0524 | +0.0190 [+0.0108, +0.0279] | +0.0039 [-0.0019, +0.0101] | 0.899 | 0.439 | yes |
| 2 | 0.431 (189 of 1872 days never flag) | 62 | 0.223 | 0.500 | 0.0594 | +0.0117 [+0.0057, +0.0184] | +0.0017 [-0.0028, +0.0066] | 0.877 | 0.205 | yes |
| 3 | 0.47 (126 of 1871 days never flag) | 94 | 0.333 | 0.489 | 0.0591 | +0.0115 [+0.0057, +0.0176] | +0.0052 [+0.0001, +0.0107] | 0.873 | 0.306 | yes |
| 4 | 0.407 (126 of 1870 days never flag) | 109 | 0.399 | 0.505 | 0.0582 | +0.0127 [+0.0061, +0.0193] | +0.0042 [-0.0015, +0.0097] | 0.878 | 0.367 | yes |
| 5 | 0.465 (126 of 1869 days never flag) | 111 | 0.355 | 0.441 | 0.0593 | +0.0116 [+0.0056, +0.0179] | +0.0041 [-0.0015, +0.0100] | 0.871 | 0.319 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.638 (climatology 0.457, difference +0.1812 [+0.0299, +0.3201]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0854, ΔBrier vs climatology +0.0441 [+0.0263, +0.0625], realised minus predicted +0.0046 [-0.0238, +0.0344]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.500 | 0.637 | 0.2613 | 0.2720 | +0.0388 [+0.0065, +0.0699] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1496 | 0.0159 | +0.0057 [-0.0089, +0.0183] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0073 | 0.0000 | +0.0134 [+0.0117, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0047, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1136 | 0.1165 | +0.0370 [+0.0052, +0.0781] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0917 | 0.0031 | +0.0122 [+0.0042, +0.0191] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2801 | 0.4146 | 0.1230 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.624 | 0.2642 | 0.2474 | +0.0374 [+0.0101, +0.0659] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1470 | 0.1133 | +0.0296 [-0.0099, +0.0687] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.569 | 0.0761 | 0.0630 | +0.0147 [+0.0075, +0.0225] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0018, +0.1358] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.2039 | 0.1461 | +0.0602 [+0.0217, +0.1047] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.760] | 0.269 | 4.85 flat / 2.28 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.231 | 3.77 flat / 1.77 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 2.423 [1.618, 3.692] | 1.058 [0.646, 1.732] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.048, 0.280] | 1.308 [0.731, 2.150] | 0.558 [0.293, 0.971] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.529] | 2.654 [1.600, 4.167] | 1.231 [0.728, 2.022] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.207, 0.500] | 1.462 [0.964, 2.250] | 0.712 [0.406, 1.219] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.923 [1.143, 3.167] | 0.865 [0.484, 1.457] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.706 [2.857, 7.583] | 1.647 [1.009, 2.667] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 5.111 [2.778, 11.500] | 3.472 [1.643, 8.439] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 137 | 0.529 | 0.540 | 0.0536 | +0.0178 [+0.0117, +0.0241] | +0.0027 [-0.0032, +0.0089] | 0.879 | 0.492 | no |
| 2 | 0.431 (189 of 1872 days never flag) | 81 | 0.338 | 0.580 | 0.0604 | +0.0107 [+0.0051, +0.0160] | +0.0007 [-0.0047, +0.0057] | 0.847 | 0.319 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 121 | 0.377 | 0.430 | 0.0601 | +0.0106 [+0.0055, +0.0159] | +0.0043 [-0.0012, +0.0098] | 0.840 | 0.337 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 72 | 0.246 | 0.472 | 0.0593 | +0.0116 [+0.0062, +0.0172] | +0.0031 [-0.0024, +0.0086] | 0.845 | 0.224 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 88 | 0.275 | 0.432 | 0.0598 | +0.0112 [+0.0057, +0.0168] | +0.0036 [-0.0021, +0.0094] | 0.839 | 0.246 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.631 (climatology 0.457, difference +0.1737 [+0.0285, +0.2963]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0912, ΔBrier vs climatology +0.0383 [+0.0234, +0.0535], realised minus predicted +0.0192 [-0.0113, +0.0501]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.573 | 0.1906 | 0.2720 | +0.0244 [+0.0004, +0.0463] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0982 | 0.0159 | +0.0189 [+0.0093, +0.0279] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0122 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0269 | 0.0200 | +0.0008 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.765 | 0.0890 | 0.1165 | +0.0367 [+0.0080, +0.0722] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0162 | 0.0048 | +0.0083 [+0.0064, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0594 | 0.0031 | +0.0178 [+0.0095, +0.0247] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1880 | 0.4146 | 0.1096 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.581 | 0.571 | 0.1910 | 0.2474 | +0.0305 [+0.0104, +0.0505] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1443 | 0.1133 | +0.0273 [-0.0104, +0.0649] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.516 | 0.0526 | 0.0630 | +0.0135 [+0.0088, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0015, +0.1362] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.2039 | 0.1461 | +0.0602 [+0.0194, +0.1048] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2171 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.667] | 0.231 | 3.77 flat / 1.43 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.231 | 3.31 flat / 1.22 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 1.769 [0.912, 3.000] | 0.673 [0.350, 1.147] |
| lead 2 alone (fail) | 26 | 1 | 0.038 [0.000, 0.107] | 1.077 [0.500, 1.862] | 0.404 [0.189, 0.684] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 2.923 [1.599, 4.792] | 1.106 [0.603, 1.800] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.269 [1.118, 3.938] | 0.837 [0.412, 1.459] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.419] | 1.962 [0.933, 3.438] | 0.635 [0.300, 1.114] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 4.824 [2.765, 7.884] | 1.618 [0.905, 2.667] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.778 (no interval) | 1.083 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.747 (105 of 1873 days never flag) | 99 | 0.379 | 0.535 | 0.0659 | +0.0055 [-0.0047, +0.0156] | -0.0096 [-0.0191, -0.0005] | 0.862 | 0.352 | yes |
| 2 | 0.648 (189 of 1872 days never flag) | 57 | 0.209 | 0.509 | 0.0717 | -0.0006 [-0.0106, +0.0085] | -0.0106 [-0.0192, -0.0023] | 0.821 | 0.192 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 137 | 0.442 | 0.445 | 0.0729 | -0.0022 [-0.0132, +0.0069] | -0.0085 [-0.0193, +0.0003] | 0.815 | 0.398 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 114 | 0.399 | 0.482 | 0.0703 | +0.0006 [-0.0078, +0.0090] | -0.0079 [-0.0162, +0.0004] | 0.829 | 0.364 | no |
| 5 | 0.7 (126 of 1869 days never flag) | 100 | 0.355 | 0.490 | 0.0702 | +0.0007 [-0.0070, +0.0080] | -0.0068 [-0.0148, +0.0003] | 0.810 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.617 (climatology 0.457, difference +0.1599 [+0.0266, +0.2811]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0938, ΔBrier vs climatology +0.0357 [+0.0175, +0.0542], realised minus predicted -0.0266 [-0.0581, +0.0056]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.537 | 0.3357 | 0.2720 | -0.0054 [-0.0501, +0.0398] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2241 | 0.0159 | -0.0216 [-0.0408, -0.0044] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0185 | 0.0000 | +0.0118 [+0.0104, +0.0133] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0162 | 0.0200 | +0.0004 [-0.0060, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0807 | 0.1165 | +0.0355 [+0.0064, +0.0731] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0111 | 0.0048 | +0.0079 [+0.0058, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1325 | 0.0031 | +0.0002 [-0.0087, +0.0082] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.2060 | 0.4146 | 0.1072 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.538 | 0.3325 | 0.2474 | -0.0049 [-0.0419, +0.0344] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1504 | 0.1133 | +0.0269 [-0.0124, +0.0662] |
| day_type | ordinary | 1603 | 101 | 0.307 | 0.463 | 0.1057 | 0.0630 | -0.0008 [-0.0111, +0.0090] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [+0.0026, +0.1363] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.2039 | 0.1461 | +0.0602 [+0.0216, +0.1041] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.280, 0.652] | 0.231 | 3.62 flat / 1.32 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.522] | 0.231 | 2.81 flat / 1.02 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.425] | 1.654 [0.964, 2.586] | 0.625 [0.356, 1.008] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.615 [0.719, 3.000] | 0.529 [0.231, 0.989] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.062, 0.333] | 1.769 [0.852, 3.059] | 0.596 [0.284, 1.033] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.273] | 2.000 [0.960, 3.474] | 0.721 [0.359, 1.250] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 1.731 [0.818, 3.133] | 0.615 [0.290, 1.111] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 4.706 [2.764, 7.563] | 1.559 [0.893, 2.536] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.556 [0.749, 3.400] | 0.861 [0.357, 2.101] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 90 | 0.336 | 0.522 | 0.0647 | +0.0067 [-0.0032, +0.0173] | -0.0084 [-0.0173, +0.0002] | 0.863 | 0.311 | yes |
| 2 | 0.667 (126 of 1872 days never flag) | 83 | 0.295 | 0.494 | 0.0703 | +0.0007 [-0.0096, +0.0098] | -0.0093 [-0.0188, -0.0007] | 0.832 | 0.271 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 87 | 0.297 | 0.471 | 0.0727 | -0.0020 [-0.0126, +0.0073] | -0.0084 [-0.0185, +0.0005] | 0.809 | 0.271 | no |
| 4 | 0.702 (126 of 1870 days never flag) | 101 | 0.355 | 0.485 | 0.0723 | -0.0015 [-0.0100, +0.0074] | -0.0099 [-0.0185, -0.0012] | 0.820 | 0.325 | yes |
| 5 | 0.648 (126 of 1869 days never flag) | 86 | 0.297 | 0.477 | 0.0729 | -0.0020 [-0.0099, +0.0057] | -0.0096 [-0.0174, -0.0016] | 0.811 | 0.271 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.457, difference +0.1589 [+0.0660, +0.2371]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0344 [+0.0164, +0.0533], realised minus predicted -0.0282 [-0.0603, +0.0043]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.363 | 0.514 | 0.3235 | 0.2720 | -0.0022 [-0.0471, +0.0405] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2170 | 0.0159 | -0.0169 [-0.0378, +0.0016] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0104, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0157 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0808 | 0.1165 | +0.0345 [+0.0053, +0.0705] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0108 | 0.0048 | +0.0079 [+0.0060, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1281 | 0.0031 | +0.0024 [-0.0059, +0.0102] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.2065 | 0.4146 | 0.1073 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.368 | 0.524 | 0.3221 | 0.2474 | -0.0019 [-0.0391, +0.0373] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1372 | 0.1133 | +0.0251 [-0.0090, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.417 | 0.1034 | 0.0630 | -0.0001 [-0.0104, +0.0098] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0334, +0.1645] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2003 | 0.1461 | +0.0655 [+0.0208, +0.1143] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.316, 0.680] | 0.231 | 3.42 flat / 1.39 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.572] | 0.192 | 2.19 flat / 1.01 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.433] | 1.769 [0.900, 3.036] | 0.673 [0.341, 1.175] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.226, 0.538] | 2.192 [1.182, 3.609] | 0.875 [0.474, 1.441] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.519] | 1.692 [0.857, 2.909] | 0.817 [0.425, 1.405] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.152, 0.480] | 1.462 [0.680, 2.563] | 0.625 [0.315, 1.068] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.143, 0.414] | 1.346 [0.548, 2.500] | 0.577 [0.261, 1.025] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.235 [2.454, 6.889] | 1.500 [0.896, 2.417] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.889 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.747 (105 of 1873 days never flag) | 99 | 0.379 | 0.535 | 0.0659 | +0.0055 [-0.0051, +0.0159] | -0.0096 [-0.0190, -0.0006] | 0.862 | 0.352 | yes |
| 2 | 0.68 (126 of 1872 days never flag) | 115 | 0.417 | 0.504 | 0.0660 | +0.0050 [-0.0050, +0.0148] | -0.0050 [-0.0150, +0.0043] | 0.834 | 0.384 | yes |
| 3 | 0.674 (126 of 1871 days never flag) | 88 | 0.319 | 0.500 | 0.0705 | +0.0002 [-0.0104, +0.0101] | -0.0061 [-0.0173, +0.0039] | 0.824 | 0.293 | yes |
| 4 | 0.745 (126 of 1870 days never flag) | 78 | 0.290 | 0.513 | 0.0661 | +0.0047 [-0.0047, +0.0141] | -0.0038 [-0.0130, +0.0053] | 0.849 | 0.268 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 72 | 0.268 | 0.514 | 0.0697 | +0.0013 [-0.0082, +0.0107] | -0.0063 [-0.0155, +0.0029] | 0.835 | 0.248 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.457, difference +0.1802 [-0.0122, +0.3877]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0922, ΔBrier vs climatology +0.0373 [+0.0160, +0.0618], realised minus predicted -0.0513 [-0.0815, -0.0201]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.537 | 0.3357 | 0.2720 | -0.0054 [-0.0510, +0.0403] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2241 | 0.0159 | -0.0216 [-0.0411, -0.0044] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0185 | 0.0000 | +0.0118 [+0.0104, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0162 | 0.0200 | +0.0004 [-0.0060, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0807 | 0.1165 | +0.0355 [+0.0066, +0.0734] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0111 | 0.0048 | +0.0079 [+0.0059, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1325 | 0.0031 | +0.0002 [-0.0092, +0.0086] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.2060 | 0.4146 | +0.1072 [-0.0106, +0.2297] |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.538 | 0.3325 | 0.2474 | -0.0049 [-0.0441, +0.0344] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1504 | 0.1133 | +0.0269 [-0.0085, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.307 | 0.463 | 0.1057 | 0.0630 | -0.0008 [-0.0111, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [+0.0032, +0.1372] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.2039 | 0.1461 | +0.0602 [+0.0224, +0.1026] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 3.62 flat / 1.37 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.643] | 0.231 | 3.04 flat / 1.17 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 1.654 [0.917, 2.522] | 0.625 [0.344, 0.982] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.227, 0.545] | 2.308 [1.200, 3.765] | 0.942 [0.538, 1.500] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.231 [1.241, 3.523] | 0.904 [0.517, 1.427] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.517] | 1.385 [0.522, 2.522] | 0.529 [0.217, 0.933] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.467] | 1.808 [0.872, 3.074] | 0.712 [0.366, 1.182] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.423, 0.857] | 4.706 [2.800, 7.462] | 1.632 [1.000, 2.601] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.556 [0.714, 3.250] | 0.861 [0.327, 2.036] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 90 | 0.336 | 0.522 | 0.0647 | +0.0067 [-0.0030, +0.0163] | -0.0084 [-0.0169, -0.0003] | 0.863 | 0.311 | yes |
| 2 | 0.739 (126 of 1872 days never flag) | 120 | 0.432 | 0.500 | 0.0658 | +0.0053 [-0.0046, +0.0149] | -0.0047 [-0.0142, +0.0045] | 0.843 | 0.397 | yes |
| 3 | 0.74 (126 of 1871 days never flag) | 120 | 0.449 | 0.517 | 0.0707 | -0.0000 [-0.0111, +0.0105] | -0.0063 [-0.0174, +0.0040] | 0.820 | 0.416 | yes |
| 4 | 0.67 (126 of 1870 days never flag) | 86 | 0.362 | 0.581 | 0.0657 | +0.0052 [-0.0037, +0.0137] | -0.0033 [-0.0119, +0.0054] | 0.844 | 0.342 | yes |
| 5 | 0.665 (126 of 1869 days never flag) | 98 | 0.370 | 0.520 | 0.0679 | +0.0030 [-0.0049, +0.0109] | -0.0045 [-0.0127, +0.0034] | 0.828 | 0.342 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.674 (climatology 0.457, difference +0.2168 [+0.0559, +0.3935]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0914, ΔBrier vs climatology +0.0381 [+0.0167, +0.0602], realised minus predicted -0.0460 [-0.0765, -0.0162]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.363 | 0.514 | 0.3235 | 0.2720 | -0.0022 [-0.0447, +0.0399] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2170 | 0.0159 | -0.0169 [-0.0388, +0.0015] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0157 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0808 | 0.1165 | +0.0345 [+0.0053, +0.0720] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0108 | 0.0048 | +0.0079 [+0.0059, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1281 | 0.0031 | +0.0024 [-0.0067, +0.0103] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.2065 | 0.4146 | 0.1073 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.368 | 0.524 | 0.3221 | 0.2474 | -0.0019 [-0.0371, +0.0349] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1372 | 0.1133 | +0.0251 [-0.0096, +0.0583] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.417 | 0.1034 | 0.0630 | -0.0001 [-0.0101, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0258, +0.1621] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2003 | 0.1461 | +0.0655 [+0.0204, +0.1113] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.682] | 0.269 | 5.00 flat / 2.19 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.647] | 0.258 | 4.50 flat / 1.99 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.654 [0.923, 2.750] | 0.606 [0.352, 1.000] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.167] | 1.077 [0.500, 1.893] | 0.433 [0.197, 0.771] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 2.308 [1.226, 3.778] | 0.933 [0.508, 1.542] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.538 [1.417, 4.116] | 0.971 [0.554, 1.580] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.562] | 3.154 [1.690, 5.238] | 1.500 [0.758, 2.667] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 6.000 [3.368, 9.923] | 2.382 [1.261, 4.278] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.300] | 3.111 [1.667, 6.750] | 1.833 [0.885, 4.417] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.675 (105 of 1873 days never flag) | 104 | 0.436 | 0.587 | 0.0614 | +0.0100 [+0.0019, +0.0190] | -0.0050 [-0.0123, +0.0021] | 0.833 | 0.411 | yes |
| 2 | 0.648 (189 of 1872 days never flag) | 53 | 0.180 | 0.472 | 0.0698 | +0.0013 [-0.0057, +0.0080] | -0.0087 [-0.0149, -0.0026] | 0.778 | 0.164 | no |
| 3 | 0.466 (126 of 1871 days never flag) | 111 | 0.370 | 0.459 | 0.0702 | +0.0005 [-0.0058, +0.0068] | -0.0058 [-0.0121, +0.0009] | 0.753 | 0.335 | no |
| 4 | 0.513 (126 of 1870 days never flag) | 123 | 0.413 | 0.463 | 0.0692 | +0.0016 [-0.0050, +0.0084] | -0.0068 [-0.0133, +0.0000] | 0.776 | 0.375 | no |
| 5 | 0.498 (126 of 1869 days never flag) | 134 | 0.377 | 0.388 | 0.0702 | +0.0007 [-0.0062, +0.0075] | -0.0068 [-0.0141, +0.0003] | 0.761 | 0.329 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.457, difference +0.1593 [+0.0202, +0.2828]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0963, ΔBrier vs climatology +0.0332 [+0.0149, +0.0508], realised minus predicted -0.0430 [-0.0759, -0.0106]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.598 | 0.3068 | 0.2720 | +0.0206 [-0.0133, +0.0563] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2323 | 0.0159 | -0.0196 [-0.0328, -0.0070] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0385 | 0.0000 | +0.0102 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0207 | 0.0200 | +0.0004 [-0.0057, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0794 | 0.1165 | +0.0333 [+0.0080, +0.0665] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0244 | 0.0048 | +0.0074 [+0.0055, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1512 | 0.0031 | -0.0050 [-0.0135, +0.0027] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.1912 | 0.4146 | 0.0881 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.479 | 0.589 | 0.3066 | 0.2474 | +0.0193 [-0.0095, +0.0500] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1511 | 0.1133 | +0.0261 [-0.0130, +0.0655] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.542 | 0.1099 | 0.0630 | +0.0045 [-0.0029, +0.0125] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [+0.0018, +0.1389] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.2039 | 0.1461 | +0.0602 [+0.0185, +0.1041] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.269 | 5.50 flat / 2.48 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.208, 0.565] | 0.269 | 4.62 flat / 2.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.438] | 1.885 [1.133, 2.867] | 0.692 [0.397, 1.078] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.409] | 2.077 [1.185, 3.320] | 0.846 [0.451, 1.375] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.387] | 1.385 [0.719, 2.334] | 0.567 [0.297, 0.967] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.067, 0.321] | 2.308 [1.357, 3.567] | 1.077 [0.637, 1.712] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.469] | 3.115 [1.690, 5.100] | 1.519 [0.762, 2.605] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.471 [4.000, 10.059] | 2.559 [1.450, 4.250] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 3.667 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 103 | 0.386 | 0.524 | 0.0602 | +0.0112 [+0.0029, +0.0197] | -0.0039 [-0.0103, +0.0029] | 0.830 | 0.357 | yes |
| 2 | 0.546 (126 of 1872 days never flag) | 92 | 0.273 | 0.413 | 0.0685 | +0.0026 [-0.0043, +0.0095] | -0.0074 [-0.0140, -0.0003] | 0.794 | 0.242 | no |
| 3 | 0.49 (126 of 1871 days never flag) | 73 | 0.268 | 0.507 | 0.0701 | +0.0006 [-0.0063, +0.0073] | -0.0057 [-0.0129, +0.0014] | 0.746 | 0.247 | no |
| 4 | 0.507 (126 of 1870 days never flag) | 109 | 0.355 | 0.450 | 0.0713 | -0.0004 [-0.0073, +0.0058] | -0.0089 [-0.0157, -0.0023] | 0.766 | 0.320 | yes |
| 5 | 0.648 (126 of 1869 days never flag) | 130 | 0.355 | 0.377 | 0.0730 | -0.0021 [-0.0094, +0.0048] | -0.0096 [-0.0172, -0.0022] | 0.763 | 0.308 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.612 (climatology 0.457, difference +0.1546 [+0.0599, +0.2391]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0977, ΔBrier vs climatology +0.0318 [+0.0145, +0.0504], realised minus predicted -0.0447 [-0.0743, -0.0112]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.412 | 0.519 | 0.2945 | 0.2720 | +0.0238 [-0.0083, +0.0582] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2251 | 0.0159 | -0.0149 [-0.0288, -0.0014] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0202 | 0.0200 | +0.0007 [-0.0057, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0795 | 0.1165 | +0.0323 [+0.0057, +0.0636] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0241 | 0.0048 | +0.0075 [+0.0056, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1469 | 0.0031 | -0.0028 [-0.0104, +0.0044] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.1917 | 0.4146 | 0.0882 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.527 | 0.2962 | 0.2474 | +0.0223 [-0.0067, +0.0516] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1379 | 0.1133 | +0.0243 [-0.0105, +0.0590] |
| day_type | ordinary | 1603 | 101 | 0.317 | 0.438 | 0.1077 | 0.0630 | +0.0052 [-0.0025, +0.0129] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0295, +0.1667] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2003 | 0.1461 | +0.0655 [+0.0225, +0.1139] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.231 | 4.08 flat / 1.62 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.256, 0.600] | 0.231 | 2.81 flat / 1.22 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 1.654 [0.954, 2.773] | 0.606 [0.353, 1.013] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.222, 0.545] | 2.231 [1.217, 3.700] | 0.894 [0.518, 1.489] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.193, 0.500] | 1.346 [0.667, 2.417] | 0.663 [0.329, 1.205] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.242, 0.600] | 2.000 [1.037, 3.276] | 0.856 [0.465, 1.400] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.414] | 1.923 [0.857, 3.419] | 0.760 [0.365, 1.313] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.941 [3.000, 8.111] | 1.765 [1.091, 2.885] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.444 (no interval) | 1.333 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.675 (105 of 1873 days never flag) | 104 | 0.436 | 0.587 | 0.0614 | +0.0100 [+0.0020, +0.0188] | -0.0050 [-0.0120, +0.0021] | 0.833 | 0.411 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 111 | 0.381 | 0.477 | 0.0634 | +0.0077 [+0.0007, +0.0158] | -0.0023 [-0.0093, +0.0057] | 0.803 | 0.348 | yes |
| 3 | 0.674 (126 of 1871 days never flag) | 77 | 0.304 | 0.545 | 0.0673 | +0.0034 [-0.0047, +0.0113] | -0.0029 [-0.0113, +0.0055] | 0.772 | 0.284 | no |
| 4 | 0.712 (126 of 1870 days never flag) | 99 | 0.341 | 0.475 | 0.0647 | +0.0061 [-0.0012, +0.0136] | -0.0024 [-0.0103, +0.0055] | 0.805 | 0.311 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 99 | 0.355 | 0.495 | 0.0694 | +0.0015 [-0.0073, +0.0099] | -0.0060 [-0.0149, +0.0028] | 0.796 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.638 (climatology 0.457, difference +0.1809 [-0.0241, +0.3816]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0934, ΔBrier vs climatology +0.0361 [+0.0148, +0.0594], realised minus predicted -0.0689 [-0.1001, -0.0363]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.598 | 0.3068 | 0.2720 | +0.0206 [-0.0142, +0.0588] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2323 | 0.0159 | -0.0196 [-0.0326, -0.0071] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0385 | 0.0000 | +0.0102 [+0.0087, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0207 | 0.0200 | +0.0004 [-0.0059, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0794 | 0.1165 | +0.0333 [+0.0067, +0.0663] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0244 | 0.0048 | +0.0074 [+0.0056, +0.0092] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1512 | 0.0031 | -0.0050 [-0.0135, +0.0031] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.1912 | 0.4146 | +0.0881 [-0.0145, +0.1888] |
| scarcity_state | 3 | 473 | 117 | 0.479 | 0.589 | 0.3066 | 0.2474 | +0.0193 [-0.0100, +0.0502] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1511 | 0.1133 | +0.0261 [-0.0118, +0.0629] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.542 | 0.1099 | 0.0630 | +0.0045 [-0.0028, +0.0128] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [+0.0045, +0.1386] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1033] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 4.85 flat / 1.95 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.759] | 0.231 | 4.08 flat / 1.67 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.435] | 1.885 [1.091, 2.938] | 0.692 [0.398, 1.109] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 2.846 [1.607, 4.485] | 1.212 [0.692, 1.938] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.385 [1.351, 3.773] | 0.971 [0.573, 1.530] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.187, 0.522] | 2.038 [1.033, 3.445] | 0.750 [0.393, 1.270] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.680] | 2.654 [1.538, 4.227] | 1.154 [0.682, 1.895] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.929] | 5.882 [3.667, 9.418] | 2.176 [1.341, 3.556] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.889 (no interval) | 1.528 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 103 | 0.386 | 0.524 | 0.0602 | +0.0112 [+0.0035, +0.0195] | -0.0039 [-0.0100, +0.0025] | 0.830 | 0.357 | yes |
| 2 | 0.587 (126 of 1872 days never flag) | 137 | 0.453 | 0.460 | 0.0632 | +0.0079 [+0.0005, +0.0155] | -0.0021 [-0.0093, +0.0058] | 0.814 | 0.411 | yes |
| 3 | 0.607 (126 of 1871 days never flag) | 129 | 0.486 | 0.519 | 0.0675 | +0.0032 [-0.0045, +0.0111] | -0.0031 [-0.0113, +0.0051] | 0.769 | 0.450 | no |
| 4 | 0.67 (126 of 1870 days never flag) | 115 | 0.449 | 0.539 | 0.0643 | +0.0066 [-0.0006, +0.0139] | -0.0019 [-0.0094, +0.0056] | 0.796 | 0.419 | yes |
| 5 | 0.591 (126 of 1869 days never flag) | 133 | 0.464 | 0.481 | 0.0676 | +0.0033 [-0.0039, +0.0113] | -0.0042 [-0.0121, +0.0042] | 0.787 | 0.424 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.675 (climatology 0.457, difference +0.2181 [+0.0470, +0.4003]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0162, +0.0591], realised minus predicted -0.0635 [-0.0959, -0.0320]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.412 | 0.519 | 0.2945 | 0.2720 | +0.0238 [-0.0082, +0.0567] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2251 | 0.0159 | -0.0149 [-0.0294, -0.0011] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0118] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0202 | 0.0200 | +0.0007 [-0.0054, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0795 | 0.1165 | +0.0323 [+0.0056, +0.0640] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0241 | 0.0048 | +0.0075 [+0.0056, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1469 | 0.0031 | -0.0028 [-0.0106, +0.0042] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.1917 | 0.4146 | 0.0882 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.527 | 0.2962 | 0.2474 | +0.0223 [-0.0063, +0.0521] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1379 | 0.1133 | +0.0243 [-0.0110, +0.0607] |
| day_type | ordinary | 1603 | 101 | 0.317 | 0.438 | 0.1077 | 0.0630 | +0.0052 [-0.0017, +0.0135] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0304, +0.1641] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2003 | 0.1461 | +0.0655 [+0.0206, +0.1138] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.643] | 0.235 | 4.23 flat / 1.60 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.235, 0.600] | 0.231 | 3.38 flat / 1.20 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.476] | 2.846 [1.615, 4.412] | 1.096 [0.621, 1.703] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.167] | 1.231 [0.541, 2.134] | 0.442 [0.205, 0.750] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.560] | 2.885 [1.540, 4.723] | 1.058 [0.562, 1.718] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.269 [1.138, 3.843] | 0.837 [0.408, 1.403] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.471] | 2.077 [1.042, 3.429] | 0.692 [0.347, 1.145] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 5.706 [3.562, 8.917] | 1.926 [1.176, 2.976] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.444 [0.625, 3.337] | 0.972 [0.350, 2.500] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.747 (105 of 1873 days never flag) | 132 | 0.414 | 0.439 | 0.0653 | +0.0061 [-0.0058, +0.0168] | -0.0090 [-0.0204, +0.0006] | 0.875 | 0.372 | yes |
| 2 | 0.625 (189 of 1872 days never flag) | 63 | 0.223 | 0.492 | 0.0693 | +0.0018 [-0.0078, +0.0108] | -0.0082 [-0.0171, -0.0000] | 0.848 | 0.205 | no |
| 3 | 0.645 (126 of 1871 days never flag) | 136 | 0.442 | 0.449 | 0.0688 | +0.0019 [-0.0089, +0.0114] | -0.0044 [-0.0151, +0.0048] | 0.862 | 0.399 | no |
| 4 | 0.664 (126 of 1870 days never flag) | 113 | 0.391 | 0.478 | 0.0668 | +0.0041 [-0.0048, +0.0121] | -0.0044 [-0.0134, +0.0040] | 0.849 | 0.357 | no |
| 5 | 0.7 (126 of 1869 days never flag) | 116 | 0.449 | 0.534 | 0.0709 | -0.0000 [-0.0104, +0.0088] | -0.0075 [-0.0178, +0.0013] | 0.836 | 0.418 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.634 (climatology 0.457, difference +0.1765 [+0.0338, +0.3078]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0902, ΔBrier vs climatology +0.0392 [+0.0222, +0.0576], realised minus predicted -0.0107 [-0.0419, +0.0199]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.425 | 0.3383 | 0.2720 | -0.0127 [-0.0664, +0.0371] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1738 | 0.0159 | -0.0061 [-0.0292, +0.0134] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0116 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0126 | 0.0200 | +0.0015 [-0.0043, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0826 | 0.1165 | +0.0315 [+0.0072, +0.0624] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0068 | 0.0048 | +0.0086 [+0.0066, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0885 | 0.0031 | +0.0133 [+0.0052, +0.0201] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1560 | 0.4146 | +0.0846 [-0.0059, +0.1719] |
| scarcity_state | 3 | 473 | 117 | 0.462 | 0.435 | 0.3399 | 0.2474 | -0.0112 [-0.0553, +0.0299] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1491 | 0.1133 | +0.0274 [-0.0107, +0.0664] |
| day_type | ordinary | 1603 | 101 | 0.347 | 0.361 | 0.0950 | 0.0630 | -0.0002 [-0.0126, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [+0.0015, +0.1352] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2039 | 0.1461 | +0.0602 [+0.0206, +0.1019] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.241, 0.593] | 0.231 | 4.00 flat / 1.51 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.179, 0.526] | 0.231 | 3.00 flat / 1.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.424] | 2.577 [1.500, 3.905] | 1.010 [0.592, 1.522] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.577 [0.679, 2.895] | 0.519 [0.220, 0.967] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 1.808 [0.838, 3.072] | 0.606 [0.277, 1.040] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.056, 0.343] | 2.192 [1.091, 3.638] | 0.779 [0.391, 1.288] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.115, 0.438] | 2.038 [1.000, 3.429] | 0.731 [0.379, 1.225] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.800] | 5.471 [3.466, 8.267] | 1.912 [1.183, 2.912] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 1.222 [0.600, 2.667] | 0.750 [0.292, 1.850] |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 132 | 0.464 | 0.492 | 0.0642 | +0.0072 [-0.0039, +0.0179] | -0.0078 [-0.0177, +0.0014] | 0.877 | 0.426 | yes |
| 2 | 0.625 (126 of 1872 days never flag) | 84 | 0.309 | 0.512 | 0.0680 | +0.0031 [-0.0065, +0.0118] | -0.0069 [-0.0164, +0.0017] | 0.855 | 0.286 | no |
| 3 | 0.683 (126 of 1871 days never flag) | 90 | 0.312 | 0.478 | 0.0686 | +0.0021 [-0.0096, +0.0121] | -0.0043 [-0.0156, +0.0056] | 0.858 | 0.284 | no |
| 4 | 0.702 (126 of 1870 days never flag) | 106 | 0.355 | 0.462 | 0.0688 | +0.0020 [-0.0065, +0.0100] | -0.0064 [-0.0149, +0.0018] | 0.841 | 0.322 | no |
| 5 | 0.705 (126 of 1869 days never flag) | 113 | 0.435 | 0.531 | 0.0737 | -0.0028 [-0.0133, +0.0067] | -0.0103 [-0.0210, -0.0004] | 0.836 | 0.404 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.457, difference +0.1661 [+0.0732, +0.2494]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0914, ΔBrier vs climatology +0.0380 [+0.0207, +0.0559], realised minus predicted -0.0122 [-0.0426, +0.0200]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.482 | 0.3261 | 0.2720 | -0.0095 [-0.0592, +0.0356] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1666 | 0.0159 | -0.0014 [-0.0273, +0.0198] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0114 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0121 | 0.0200 | +0.0018 [-0.0040, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0827 | 0.1165 | +0.0305 [+0.0065, +0.0608] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0087 [+0.0068, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0841 | 0.0031 | +0.0155 [+0.0076, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1565 | 0.4146 | 0.0847 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.492 | 0.3295 | 0.2474 | -0.0082 [-0.0495, +0.0331] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1359 | 0.1133 | +0.0256 [-0.0086, +0.0628] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.427 | 0.0928 | 0.0630 | +0.0005 [-0.0109, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0320, +0.1660] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.2003 | 0.1461 | +0.0655 [+0.0217, +0.1150] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.682] | 0.231 | 3.73 flat / 1.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.185, 0.526] | 0.192 | 2.00 flat / 0.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.136, 0.480] | 2.846 [1.607, 4.445] | 1.096 [0.633, 1.714] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 1.923 [0.957, 3.273] | 0.808 [0.420, 1.350] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 1.423 [0.650, 2.579] | 0.683 [0.315, 1.242] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.136, 0.478] | 1.462 [0.690, 2.600] | 0.625 [0.316, 1.069] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.424] | 1.346 [0.545, 2.546] | 0.577 [0.259, 1.024] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.917] | 4.882 [2.889, 7.601] | 1.779 [1.071, 2.781] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.556 (no interval) | 1.083 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.747 (105 of 1873 days never flag) | 132 | 0.414 | 0.439 | 0.0653 | +0.0061 [-0.0057, +0.0172] | -0.0090 [-0.0194, +0.0010] | 0.875 | 0.372 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 102 | 0.374 | 0.510 | 0.0640 | +0.0070 [-0.0026, +0.0166] | -0.0030 [-0.0127, +0.0065] | 0.856 | 0.345 | yes |
| 3 | 0.674 (126 of 1871 days never flag) | 79 | 0.304 | 0.532 | 0.0672 | +0.0034 [-0.0077, +0.0135] | -0.0029 [-0.0141, +0.0072] | 0.862 | 0.283 | no |
| 4 | 0.712 (126 of 1870 days never flag) | 78 | 0.290 | 0.513 | 0.0633 | +0.0076 [-0.0016, +0.0160] | -0.0009 [-0.0104, +0.0083] | 0.861 | 0.268 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 73 | 0.275 | 0.521 | 0.0710 | -0.0001 [-0.0117, +0.0098] | -0.0076 [-0.0191, +0.0025] | 0.852 | 0.255 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.457, difference +0.1802 [-0.0209, +0.3825]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0174, +0.0625], realised minus predicted -0.0356 [-0.0662, -0.0057]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.425 | 0.3383 | 0.2720 | -0.0127 [-0.0621, +0.0398] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1738 | 0.0159 | -0.0061 [-0.0290, +0.0141] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0116 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0126 | 0.0200 | +0.0015 [-0.0045, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0826 | 0.1165 | +0.0315 [+0.0065, +0.0630] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0068 | 0.0048 | +0.0086 [+0.0066, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0885 | 0.0031 | +0.0133 [+0.0058, +0.0200] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1560 | 0.4146 | 0.0846 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.462 | 0.435 | 0.3399 | 0.2474 | -0.0112 [-0.0536, +0.0334] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1491 | 0.1133 | +0.0274 [-0.0098, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.347 | 0.361 | 0.0950 | 0.0630 | -0.0002 [-0.0120, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [+0.0018, +0.1388] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2039 | 0.1461 | +0.0602 [+0.0199, +0.1039] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.682] | 0.231 | 3.88 flat / 1.47 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.654] | 0.231 | 2.73 flat / 1.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 2.577 [1.571, 3.876] | 1.010 [0.611, 1.544] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.593] | 2.308 [1.185, 3.765] | 0.942 [0.518, 1.516] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.385] | 1.769 [0.906, 2.958] | 0.760 [0.420, 1.240] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 1.962 [0.827, 3.462] | 0.731 [0.323, 1.286] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 2.077 [1.050, 3.464] | 0.798 [0.425, 1.312] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.294 [3.385, 8.182] | 1.897 [1.194, 2.917] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.667 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 132 | 0.464 | 0.492 | 0.0642 | +0.0072 [-0.0044, +0.0178] | -0.0078 [-0.0189, +0.0011] | 0.877 | 0.426 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 125 | 0.468 | 0.520 | 0.0638 | +0.0073 [-0.0029, +0.0162] | -0.0027 [-0.0122, +0.0066] | 0.865 | 0.433 | yes |
| 3 | 0.74 (126 of 1871 days never flag) | 94 | 0.348 | 0.511 | 0.0675 | +0.0032 [-0.0082, +0.0138] | -0.0031 [-0.0145, +0.0074] | 0.859 | 0.321 | no |
| 4 | 0.67 (126 of 1870 days never flag) | 104 | 0.384 | 0.510 | 0.0628 | +0.0080 [-0.0005, +0.0166] | -0.0004 [-0.0091, +0.0084] | 0.858 | 0.355 | no |
| 5 | 0.746 (126 of 1869 days never flag) | 107 | 0.384 | 0.495 | 0.0693 | +0.0017 [-0.0087, +0.0111] | -0.0059 [-0.0165, +0.0037] | 0.847 | 0.353 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.673 (climatology 0.457, difference +0.2156 [+0.0591, +0.3913]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0887, ΔBrier vs climatology +0.0408 [+0.0196, +0.0628], realised minus predicted -0.0301 [-0.0605, +0.0009]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.482 | 0.3261 | 0.2720 | -0.0095 [-0.0595, +0.0368] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1666 | 0.0159 | -0.0014 [-0.0261, +0.0190] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0114 | 0.0000 | +0.0126 [+0.0109, +0.0144] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0121 | 0.0200 | +0.0018 [-0.0041, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0827 | 0.1165 | +0.0305 [+0.0058, +0.0620] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0087 [+0.0066, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0841 | 0.0031 | +0.0155 [+0.0077, +0.0225] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1565 | 0.4146 | 0.0847 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.492 | 0.3295 | 0.2474 | -0.0082 [-0.0520, +0.0325] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1359 | 0.1133 | +0.0256 [-0.0077, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.427 | 0.0928 | 0.0630 | +0.0005 [-0.0119, +0.0109] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0284, +0.1659] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.2003 | 0.1461 | +0.0655 [+0.0223, +0.1114] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.688] | 0.269 | 5.04 flat / 2.18 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.285, 0.650] | 0.242 | 4.35 flat / 1.89 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.486] | 2.654 [1.500, 4.161] | 1.029 [0.587, 1.600] |
| lead 2 alone (fail) | 26 | 1 | 0.038 [0.000, 0.107] | 1.308 [0.462, 2.462] | 0.625 [0.195, 1.264] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 3.500 [1.923, 5.637] | 1.567 [0.804, 2.661] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.187, 0.522] | 2.500 [1.290, 4.243] | 0.952 [0.500, 1.598] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.346 [1.863, 5.389] | 1.538 [0.787, 2.630] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.882 [4.295, 10.833] | 2.691 [1.533, 4.517] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.556 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.675 (105 of 1873 days never flag) | 132 | 0.450 | 0.477 | 0.0588 | +0.0126 [+0.0042, +0.0215] | -0.0025 [-0.0095, +0.0048] | 0.858 | 0.410 | yes |
| 2 | 0.648 (189 of 1872 days never flag) | 59 | 0.180 | 0.424 | 0.0657 | +0.0053 [-0.0024, +0.0131] | -0.0047 [-0.0115, +0.0021] | 0.832 | 0.160 | no |
| 3 | 0.566 (126 of 1871 days never flag) | 151 | 0.435 | 0.397 | 0.0649 | +0.0058 [-0.0010, +0.0126] | -0.0005 [-0.0070, +0.0064] | 0.845 | 0.382 | no |
| 4 | 0.524 (126 of 1870 days never flag) | 121 | 0.406 | 0.463 | 0.0645 | +0.0063 [-0.0008, +0.0135] | -0.0021 [-0.0092, +0.0049] | 0.834 | 0.368 | no |
| 5 | 0.519 (126 of 1869 days never flag) | 155 | 0.493 | 0.439 | 0.0667 | +0.0042 [-0.0027, +0.0108] | -0.0033 [-0.0103, +0.0037] | 0.815 | 0.442 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.628 (climatology 0.457, difference +0.1705 [+0.0316, +0.2997]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0916, ΔBrier vs climatology +0.0379 [+0.0214, +0.0557], realised minus predicted -0.0126 [-0.0434, +0.0203]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.465 | 0.3039 | 0.2720 | +0.0186 [-0.0157, +0.0573] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1967 | 0.0159 | -0.0064 [-0.0229, +0.0089] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0164 | 0.0000 | +0.0124 [+0.0107, +0.0140] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0015 [-0.0045, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0803 | 0.1165 | +0.0348 [+0.0074, +0.0672] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0094 | 0.0048 | +0.0086 [+0.0066, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1112 | 0.0031 | +0.0086 [+0.0011, +0.0156] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1633 | 0.4146 | +0.0865 [-0.0033, +0.1743] |
| scarcity_state | 3 | 473 | 117 | 0.504 | 0.476 | 0.3094 | 0.2474 | +0.0179 [-0.0124, +0.0506] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1496 | 0.1133 | +0.0274 [-0.0106, +0.0639] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.412 | 0.0925 | 0.0630 | +0.0075 [-0.0002, +0.0159] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [-0.0004, +0.1404] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2039 | 0.1461 | +0.0602 [+0.0192, +0.1024] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2395 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.682] | 0.269 | 5.42 flat / 2.46 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.647] | 0.250 | 4.42 flat / 2.00 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.435] | 2.615 [1.565, 4.000] | 1.010 [0.607, 1.548] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.419] | 2.077 [1.066, 3.534] | 0.981 [0.467, 1.734] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.438] | 2.308 [1.083, 4.000] | 0.990 [0.402, 1.913] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 2.923 [1.625, 4.737] | 1.442 [0.780, 2.441] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.560] | 3.346 [1.951, 5.308] | 1.596 [0.879, 2.667] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 7.235 [4.799, 11.067] | 2.912 [1.800, 4.667] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 2.000 [1.000, 4.750] | 1.611 [0.632, 4.250] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 139 | 0.507 | 0.511 | 0.0576 | +0.0138 [+0.0055, +0.0224] | -0.0013 [-0.0079, +0.0054] | 0.858 | 0.468 | yes |
| 2 | 0.546 (126 of 1872 days never flag) | 92 | 0.273 | 0.413 | 0.0644 | +0.0067 [-0.0009, +0.0138] | -0.0034 [-0.0104, +0.0034] | 0.844 | 0.242 | no |
| 3 | 0.683 (126 of 1871 days never flag) | 104 | 0.319 | 0.423 | 0.0647 | +0.0060 [-0.0013, +0.0134] | -0.0004 [-0.0076, +0.0069] | 0.839 | 0.284 | no |
| 4 | 0.524 (126 of 1870 days never flag) | 127 | 0.370 | 0.402 | 0.0665 | +0.0043 [-0.0029, +0.0111] | -0.0042 [-0.0115, +0.0030] | 0.825 | 0.326 | no |
| 5 | 0.648 (126 of 1869 days never flag) | 154 | 0.486 | 0.435 | 0.0695 | +0.0014 [-0.0062, +0.0089] | -0.0061 [-0.0144, +0.0015] | 0.816 | 0.435 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.457, difference +0.1608 [+0.0666, +0.2441]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0930, ΔBrier vs climatology +0.0365 [+0.0195, +0.0552], realised minus predicted -0.0144 [-0.0453, +0.0194]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.500 | 0.2917 | 0.2720 | +0.0218 [-0.0125, +0.0566] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1896 | 0.0159 | -0.0017 [-0.0188, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0124 [+0.0108, +0.0141] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0804 | 0.1165 | +0.0338 [+0.0064, +0.0672] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0092 | 0.0048 | +0.0086 [+0.0067, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1068 | 0.0031 | +0.0108 [+0.0030, +0.0175] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1638 | 0.4146 | 0.0866 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.511 | 0.2990 | 0.2474 | +0.0209 [-0.0088, +0.0534] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1364 | 0.1133 | +0.0256 [-0.0086, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.454 | 0.0903 | 0.0630 | +0.0081 [+0.0005, +0.0162] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0275, +0.1636] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2003 | 0.1461 | +0.0655 [+0.0224, +0.1118] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2396 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.269 | 4.73 flat / 2.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.606] | 0.231 | 3.12 flat / 1.53 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.136, 0.478] | 2.654 [1.435, 4.147] | 1.029 [0.567, 1.606] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 2.077 [1.042, 3.400] | 0.846 [0.442, 1.391] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.458] | 1.808 [0.848, 3.000] | 0.817 [0.395, 1.382] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 2.385 [1.097, 4.054] | 1.183 [0.533, 2.143] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.151, 0.467] | 1.885 [0.833, 3.278] | 0.750 [0.355, 1.275] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.529 [4.045, 10.250] | 2.647 [1.545, 4.469] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.333 [0.571, 3.000] | 1.000 [0.308, 2.625] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.675 (105 of 1873 days never flag) | 132 | 0.450 | 0.477 | 0.0588 | +0.0126 [+0.0041, +0.0219] | -0.0025 [-0.0095, +0.0049] | 0.858 | 0.410 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 108 | 0.388 | 0.500 | 0.0599 | +0.0112 [+0.0027, +0.0191] | +0.0012 [-0.0071, +0.0090] | 0.841 | 0.357 | yes |
| 3 | 0.674 (126 of 1871 days never flag) | 97 | 0.362 | 0.515 | 0.0627 | +0.0080 [-0.0005, +0.0160] | +0.0016 [-0.0072, +0.0101] | 0.843 | 0.335 | no |
| 4 | 0.712 (126 of 1870 days never flag) | 108 | 0.333 | 0.426 | 0.0606 | +0.0103 [+0.0027, +0.0180] | +0.0018 [-0.0061, +0.0099] | 0.845 | 0.298 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 97 | 0.348 | 0.495 | 0.0664 | +0.0045 [-0.0043, +0.0134] | -0.0030 [-0.0126, +0.0062] | 0.834 | 0.320 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.638 (climatology 0.457, difference +0.1809 [-0.0193, +0.3849]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0892, ΔBrier vs climatology +0.0402 [+0.0186, +0.0634], realised minus predicted -0.0389 [-0.0696, -0.0081]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.465 | 0.3039 | 0.2720 | +0.0186 [-0.0182, +0.0570] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1967 | 0.0159 | -0.0064 [-0.0223, +0.0080] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0164 | 0.0000 | +0.0124 [+0.0107, +0.0141] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0015 [-0.0043, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0803 | 0.1165 | +0.0348 [+0.0085, +0.0689] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0094 | 0.0048 | +0.0086 [+0.0067, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1112 | 0.0031 | +0.0086 [+0.0006, +0.0152] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1633 | 0.4146 | 0.0865 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.504 | 0.476 | 0.3094 | 0.2474 | +0.0179 [-0.0142, +0.0512] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1496 | 0.1133 | +0.0274 [-0.0099, +0.0667] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.412 | 0.0925 | 0.0630 | +0.0075 [-0.0005, +0.0160] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3234 | 0.2903 | +0.0724 [+0.0001, +0.1390] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2039 | 0.1461 | +0.0602 [+0.0220, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2395 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.710] | 0.269 | 4.96 flat / 2.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.364, 0.714] | 0.231 | 4.08 flat / 1.81 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.107, 0.429] | 2.615 [1.567, 4.000] | 1.010 [0.603, 1.570] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.595] | 2.654 [1.368, 4.477] | 1.067 [0.598, 1.750] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.121, 0.423] | 1.885 [1.034, 3.077] | 0.779 [0.457, 1.250] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 2.500 [1.238, 4.167] | 0.913 [0.465, 1.544] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.269 [1.820, 5.350] | 1.481 [0.774, 2.566] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 7.000 [4.615, 11.091] | 2.809 [1.712, 4.688] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.778 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 139 | 0.507 | 0.511 | 0.0576 | +0.0138 [+0.0061, +0.0228] | -0.0013 [-0.0077, +0.0055] | 0.858 | 0.468 | yes |
| 2 | 0.587 (126 of 1872 days never flag) | 139 | 0.504 | 0.504 | 0.0596 | +0.0114 [+0.0032, +0.0195] | +0.0014 [-0.0066, +0.0092] | 0.853 | 0.464 | yes |
| 3 | 0.607 (126 of 1871 days never flag) | 107 | 0.420 | 0.542 | 0.0629 | +0.0077 [-0.0013, +0.0158] | +0.0014 [-0.0076, +0.0098] | 0.841 | 0.392 | no |
| 4 | 0.67 (126 of 1870 days never flag) | 129 | 0.464 | 0.496 | 0.0601 | +0.0107 [+0.0035, +0.0183] | +0.0023 [-0.0055, +0.0101] | 0.838 | 0.426 | no |
| 5 | 0.591 (126 of 1869 days never flag) | 144 | 0.428 | 0.410 | 0.0646 | +0.0063 [-0.0014, +0.0138] | -0.0012 [-0.0092, +0.0066] | 0.821 | 0.378 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.674 (climatology 0.457, difference +0.2168 [+0.0476, +0.3920]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0409 [+0.0215, +0.0617], realised minus predicted -0.0335 [-0.0625, -0.0028]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.500 | 0.2917 | 0.2720 | +0.0218 [-0.0114, +0.0571] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1896 | 0.0159 | -0.0017 [-0.0197, +0.0129] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0124 [+0.0108, +0.0140] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0044, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0804 | 0.1165 | +0.0338 [+0.0067, +0.0666] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0092 | 0.0048 | +0.0086 [+0.0067, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1068 | 0.0031 | +0.0108 [+0.0035, +0.0173] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1638 | 0.4146 | 0.0866 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.511 | 0.2990 | 0.2474 | +0.0209 [-0.0079, +0.0531] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1364 | 0.1133 | +0.0256 [-0.0087, +0.0618] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.454 | 0.0903 | 0.0630 | +0.0081 [+0.0005, +0.0162] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2995 | 0.2903 | +0.1011 [+0.0304, +0.1662] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2003 | 0.1461 | +0.0655 [+0.0227, +0.1139] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2396 | 0.2213 |

