# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `c2049daaca93…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## projected_fitted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.148, 0.480] | 0.231 | 3.88 flat / 1.75 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 6 | 0.231 [0.091, 0.391] | 0.231 | 2.77 flat / 1.31 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.432] | 2.308 [1.318, 3.715] | 0.788 [0.446, 1.270] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.087, 0.400] | 2.346 [1.294, 3.926] | 1.058 [0.542, 1.847] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.038 [1.150, 3.305] | 0.971 [0.494, 1.674] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.061, 0.348] | 1.808 [0.933, 3.067] | 0.865 [0.402, 1.567] |
| lead 5 alone (fail) | 26 | 3 | 0.115 [0.030, 0.226] | 0.885 [0.333, 1.714] | 0.385 [0.144, 0.764] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.263, 0.692] | 5.235 [3.381, 8.252] | 2.074 [1.230, 3.438] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.333 [0.000, 4.168] | 1.139 [0.000, 3.750] |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.619 (126 of 1873 days never flag) | 127 | 0.479 | 0.528 | 0.0554 | +0.0160 [+0.0078, +0.0253] | +0.0009 [-0.0062, +0.0087] | 0.884 | 0.444 | no |
| 2 | 0.642 (147 of 1872 days never flag) | 113 | 0.374 | 0.460 | 0.0596 | +0.0114 [+0.0039, +0.0201] | +0.0014 [-0.0065, +0.0102] | 0.856 | 0.339 | no |
| 3 | 0.662 (147 of 1871 days never flag) | 92 | 0.283 | 0.424 | 0.0638 | +0.0069 [-0.0017, +0.0159] | +0.0006 [-0.0083, +0.0098] | 0.832 | 0.252 | no |
| 4 | 0.776 (147 of 1870 days never flag) | 85 | 0.275 | 0.447 | 0.0634 | +0.0074 [-0.0007, +0.0164] | -0.0011 [-0.0096, +0.0080] | 0.834 | 0.248 | no |
| 5 | 0.785 (147 of 1869 days never flag) | 47 | 0.174 | 0.511 | 0.0722 | -0.0013 [-0.0140, +0.0098] | -0.0089 [-0.0210, +0.0020] | 0.815 | 0.161 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.457, difference +0.0666 [-0.0351, +0.1564]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0984, ΔBrier vs climatology +0.0310 [+0.0152, +0.0483], realised minus predicted +0.0083 [-0.0280, +0.0430]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.532 | 0.3283 | 0.2720 | +0.0329 [-0.0082, +0.0773] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1281 | 0.0159 | +0.0179 [+0.0093, +0.0249] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0117, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0040 | 0.0200 | +0.0017 [-0.0029, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0287 | 0.1165 | +0.0111 [+0.0034, +0.0198] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0048 | 0.0048 | +0.0089 [+0.0072, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0770 | 0.0031 | +0.0199 [+0.0162, +0.0234] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0703 | 0.4146 | 0.0230 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.528 | 0.2921 | 0.2474 | +0.0284 [-0.0041, +0.0644] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.1211 | 0.1133 | +0.0333 [+0.0132, +0.0555] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.490 | 0.0800 | 0.0630 | +0.0117 [+0.0035, +0.0207] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3015 | 0.2903 | +0.0664 [+0.0263, +0.1018] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1702 | 0.1461 | +0.0472 [+0.0137, +0.0831] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.3079 | 0.2213 |

## projected_hinge_fixed (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.154, 0.462] | 0.231 | 3.77 flat / 1.63 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.120, 0.438] | 0.231 | 2.62 flat / 1.13 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 2.346 [1.333, 3.625] | 0.817 [0.452, 1.283] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 2.231 [1.189, 3.524] | 1.000 [0.500, 1.660] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.364] | 2.077 [1.120, 3.273] | 0.885 [0.467, 1.429] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.615 [0.739, 2.690] | 0.683 [0.293, 1.175] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 0.962 [0.379, 1.810] | 0.385 [0.153, 0.721] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.269, 0.667] | 5.294 [3.296, 8.003] | 2.074 [1.183, 3.327] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.889 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.575 (126 of 1873 days never flag) | 125 | 0.457 | 0.512 | 0.0550 | +0.0164 [+0.0083, +0.0252] | +0.0014 [-0.0060, +0.0090] | 0.896 | 0.422 | no |
| 2 | 0.639 (147 of 1872 days never flag) | 109 | 0.367 | 0.468 | 0.0598 | +0.0112 [+0.0029, +0.0193] | +0.0012 [-0.0072, +0.0097] | 0.868 | 0.333 | no |
| 3 | 0.64 (147 of 1871 days never flag) | 94 | 0.290 | 0.426 | 0.0625 | +0.0082 [-0.0008, +0.0169] | +0.0018 [-0.0073, +0.0105] | 0.837 | 0.259 | no |
| 4 | 0.775 (147 of 1870 days never flag) | 82 | 0.290 | 0.488 | 0.0630 | +0.0078 [-0.0005, +0.0170] | -0.0006 [-0.0093, +0.0085] | 0.844 | 0.266 | no |
| 5 | 0.779 (147 of 1869 days never flag) | 48 | 0.167 | 0.479 | 0.0703 | +0.0006 [-0.0111, +0.0121] | -0.0069 [-0.0181, +0.0043] | 0.819 | 0.152 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.512 (climatology 0.457, difference +0.0548 [-0.0507, +0.1438]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0941, ΔBrier vs climatology +0.0353 [+0.0201, +0.0511], realised minus predicted +0.0263 [-0.0061, +0.0622]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.521 | 0.3207 | 0.2720 | +0.0352 [-0.0047, +0.0752] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0865 | 0.0159 | +0.0207 [+0.0055, +0.0346] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0067 | 0.0200 | +0.0021 [-0.0020, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0253 | 0.1165 | +0.0065 [+0.0005, +0.0139] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0070 | 0.0048 | +0.0090 [+0.0074, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0197 | 0.0031 | +0.0296 [+0.0236, +0.0355] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0495 | 0.4146 | 0.0066 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.547 | 0.512 | 0.2956 | 0.2474 | +0.0246 [-0.0081, +0.0583] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.1111 | 0.1133 | +0.0314 [+0.0120, +0.0530] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.473 | 0.0730 | 0.0630 | +0.0118 [+0.0038, +0.0203] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2760 | 0.2903 | +0.0731 [+0.0281, +0.1163] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1486 | 0.1461 | +0.0554 [+0.0192, +0.0920] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2848 | 0.2213 |

## projected_reserves (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.156, 0.471] | 0.231 | 3.35 flat / 1.41 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.130, 0.429] | 0.192 | 2.23 flat / 1.03 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.091, 0.370] | 2.346 [1.323, 3.737] | 0.817 [0.450, 1.313] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 1.885 [0.900, 3.300] | 0.750 [0.360, 1.324] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.346 [0.538, 2.579] | 0.567 [0.237, 1.071] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.087, 0.379] | 1.731 [0.818, 3.000] | 0.721 [0.329, 1.241] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.115 [0.458, 2.091] | 0.490 [0.200, 0.957] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.263, 0.692] | 4.647 [2.833, 7.385] | 1.735 [1.000, 2.808] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 0.889 [0.000, 2.750] | 0.806 [0.000, 2.562] |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.572 (126 of 1873 days never flag) | 125 | 0.457 | 0.512 | 0.0539 | +0.0175 [+0.0096, +0.0270] | +0.0024 [-0.0042, +0.0105] | 0.920 | 0.422 | no |
| 2 | 0.636 (147 of 1872 days never flag) | 101 | 0.374 | 0.515 | 0.0588 | +0.0123 [+0.0045, +0.0209] | +0.0023 [-0.0060, +0.0106] | 0.907 | 0.346 | no |
| 3 | 0.657 (147 of 1871 days never flag) | 63 | 0.203 | 0.444 | 0.0617 | +0.0089 [+0.0003, +0.0184] | +0.0026 [-0.0062, +0.0121] | 0.901 | 0.183 | no |
| 4 | 0.746 (147 of 1870 days never flag) | 85 | 0.290 | 0.471 | 0.0613 | +0.0095 [+0.0008, +0.0185] | +0.0010 [-0.0080, +0.0101] | 0.899 | 0.264 | no |
| 5 | 0.687 (147 of 1869 days never flag) | 54 | 0.181 | 0.463 | 0.0639 | +0.0070 [-0.0023, +0.0164] | -0.0005 [-0.0099, +0.0091] | 0.883 | 0.164 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.526 (climatology 0.457, difference +0.0691 [-0.0244, +0.1470]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0887, ΔBrier vs climatology +0.0408 [+0.0265, +0.0566], realised minus predicted +0.0377 [+0.0063, +0.0714]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.521 | 0.3229 | 0.2720 | +0.0352 [-0.0021, +0.0787] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0731 | 0.0159 | +0.0217 [+0.0065, +0.0360] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0022 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0021 [-0.0020, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0329 | 0.1165 | +0.0134 [+0.0049, +0.0234] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0031 | 0.0048 | +0.0090 [+0.0073, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0074 | 0.0031 | +0.0307 [+0.0240, +0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0776 | 0.4146 | 0.0364 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.547 | 0.512 | 0.2987 | 0.2474 | +0.0255 [-0.0048, +0.0617] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.1086 | 0.1133 | +0.0330 [+0.0127, +0.0563] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.473 | 0.0711 | 0.0630 | +0.0124 [+0.0047, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2623 | 0.2903 | +0.0859 [+0.0399, +0.1290] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1323 | 0.1461 | +0.0591 [+0.0226, +0.0966] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2844 | 0.2213 |

## projected_rolling (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.261, 0.593] | 0.269 | 5.23 flat / 2.88 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.259, 0.593] | 0.231 | 3.96 flat / 2.08 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 3.115 [1.928, 4.810] | 1.452 [0.885, 2.365] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.455] | 3.077 [1.852, 4.818] | 1.471 [0.879, 2.417] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.593] | 3.231 [1.937, 5.155] | 1.587 [0.922, 2.664] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 3.038 [1.740, 4.889] | 1.317 [0.750, 2.167] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.444] | 2.308 [1.208, 3.875] | 1.048 [0.573, 1.762] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.231, 0.619] | 3.235 [1.789, 5.556] | 1.265 [0.676, 2.251] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.000 (no interval) | 5.944 (no interval) |

Recall with equal weight per regime: 0.303 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.286 (105 of 1873 days never flag) | 156 | 0.536 | 0.481 | 0.0539 | +0.0175 [+0.0100, +0.0260] | +0.0024 [-0.0036, +0.0084] | 0.866 | 0.489 | no |
| 2 | 0.267 (126 of 1872 days never flag) | 149 | 0.496 | 0.463 | 0.0566 | +0.0145 [+0.0072, +0.0226] | +0.0045 [-0.0020, +0.0113] | 0.819 | 0.450 | no |
| 3 | 0.281 (126 of 1871 days never flag) | 155 | 0.514 | 0.458 | 0.0606 | +0.0101 [+0.0020, +0.0186] | +0.0038 [-0.0040, +0.0119] | 0.788 | 0.466 | no |
| 4 | 0.353 (147 of 1870 days never flag) | 146 | 0.486 | 0.459 | 0.0589 | +0.0119 [+0.0048, +0.0196] | +0.0035 [-0.0024, +0.0100] | 0.814 | 0.440 | no |
| 5 | 0.43 (147 of 1869 days never flag) | 108 | 0.348 | 0.444 | 0.0628 | +0.0081 [+0.0004, +0.0167] | +0.0006 [-0.0058, +0.0077] | 0.788 | 0.313 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 2.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.533 (climatology 0.457, difference +0.0754 [-0.0418, +0.2148]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0953, ΔBrier vs climatology +0.0342 [+0.0179, +0.0532], realised minus predicted +0.0085 [-0.0263, +0.0430]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.576 | 0.1637 | 0.2720 | +0.0266 [+0.0051, +0.0513] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0877 | 0.0159 | +0.0304 [+0.0221, +0.0385] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0311 | 0.0000 | +0.0103 [+0.0070, +0.0132] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0244 | 0.0200 | +0.0024 [-0.0015, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.862 | 0.455 | 0.1827 | 0.1165 | +0.0275 [-0.0133, +0.0788] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.100 | 0.0281 | 0.0048 | +0.0062 [+0.0038, +0.0086] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.077 | 0.0789 | 0.0031 | +0.0198 [+0.0099, +0.0276] |
| scarcity_state | 2 | 41 | 17 | 0.882 | 0.517 | 0.5206 | 0.4146 | +0.1298 [-0.0959, +0.3484] |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.558 | 0.1738 | 0.2474 | +0.0308 [+0.0112, +0.0518] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1161 | 0.1133 | +0.0397 [+0.0114, +0.0727] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.463 | 0.0717 | 0.0630 | +0.0122 [+0.0057, +0.0196] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3472 | 0.2903 | +0.1099 [+0.0564, +0.1629] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.474 | 0.1706 | 0.1461 | +0.0435 [+0.0200, +0.0690] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0046 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2985 | 0.2213 |

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

## risk_gbm+combined (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.212, 0.571] | 0.192 | 1.85 flat / 1.07 weighted | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.208, 0.576] | 0.154 | 1.46 flat / 0.90 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.391] | 0.808 [0.417, 1.348] | 0.462 [0.214, 0.810] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 0.808 [0.316, 1.524] | 0.490 [0.170, 0.972] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.440] | 1.077 [0.483, 1.909] | 0.702 [0.261, 1.366] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.477] | 1.115 [0.478, 2.062] | 0.712 [0.250, 1.396] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.000 [0.379, 1.895] | 0.644 [0.205, 1.302] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.714] | 2.059 [0.827, 4.000] | 1.074 [0.317, 2.292] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0415 (168 of 1873 days never flag) | 63 | 0.300 | 0.667 | 0.0599 | +0.0116 [+0.0063, +0.0165] | -0.0035 [-0.0113, +0.0037] | 0.723 | 0.288 | no |
| 2 | 0.103 (168 of 1872 days never flag) | 50 | 0.209 | 0.580 | 0.0641 | +0.0069 [+0.0003, +0.0138] | -0.0031 [-0.0110, +0.0048] | 0.698 | 0.197 | no |
| 3 | 0.104 (168 of 1871 days never flag) | 59 | 0.225 | 0.525 | 0.0656 | +0.0051 [-0.0031, +0.0122] | -0.0012 [-0.0095, +0.0063] | 0.702 | 0.208 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0683 | +0.0026 [-0.0046, +0.0100] | -0.0059 [-0.0137, +0.0020] | 0.675 | 0.193 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 56 | 0.217 | 0.536 | 0.0672 | +0.0038 [-0.0048, +0.0113] | -0.0038 [-0.0125, +0.0040] | 0.676 | 0.202 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0522, +0.3886]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1028, ΔBrier vs climatology +0.0267 [+0.0151, +0.0389], realised minus predicted +0.0976 [+0.0620, +0.1357]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.0653 | 0.2720 | -0.0020 [-0.0236, +0.0186] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0346, +0.0500] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0013 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0047, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0165 | 0.1165 | +0.0049 [-0.0043, +0.0151] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0010 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0014 | 0.0031 | +0.0302 [+0.0231, +0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0130 | 0.4146 | -0.0298 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.350 | 0.672 | 0.0609 | 0.2474 | +0.0084 [-0.0102, +0.0257] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.0401 | 0.1133 | +0.0298 [+0.0161, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.238 | 0.667 | 0.0117 | 0.0630 | +0.0071 [+0.0020, +0.0116] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.1190 | 0.2903 | +0.1049 [+0.0102, +0.1953] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.0269 | 0.1461 | +0.0292 [-0.0010, +0.0578] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6331 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_fitted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.200, 0.583] | 0.192 | 1.81 flat / 1.06 weighted | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.206, 0.565] | 0.154 | 1.38 flat / 0.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.094, 0.391] | 0.808 [0.409, 1.333] | 0.462 [0.211, 0.804] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.389] | 0.808 [0.320, 1.486] | 0.490 [0.173, 0.929] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.115, 0.448] | 1.077 [0.500, 1.870] | 0.702 [0.262, 1.324] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 1.077 [0.455, 2.000] | 0.702 [0.259, 1.367] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 0.846 [0.379, 1.520] | 0.529 [0.212, 1.017] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.722] | 2.000 [0.789, 3.790] | 1.059 [0.321, 2.208] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0415 (168 of 1873 days never flag) | 63 | 0.300 | 0.667 | 0.0599 | +0.0115 [+0.0063, +0.0166] | -0.0036 [-0.0114, +0.0035] | 0.732 | 0.288 | no |
| 2 | 0.103 (168 of 1872 days never flag) | 48 | 0.194 | 0.562 | 0.0643 | +0.0068 [-0.0003, +0.0136] | -0.0032 [-0.0110, +0.0042] | 0.699 | 0.182 | no |
| 3 | 0.104 (168 of 1871 days never flag) | 59 | 0.225 | 0.525 | 0.0657 | +0.0050 [-0.0030, +0.0126] | -0.0013 [-0.0102, +0.0061] | 0.702 | 0.208 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 57 | 0.210 | 0.509 | 0.0683 | +0.0026 [-0.0056, +0.0099] | -0.0059 [-0.0147, +0.0019] | 0.684 | 0.194 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 52 | 0.217 | 0.577 | 0.0668 | +0.0041 [-0.0044, +0.0114] | -0.0034 [-0.0120, +0.0042] | 0.677 | 0.205 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0481, +0.3967]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1028, ΔBrier vs climatology +0.0267 [+0.0152, +0.0386], realised minus predicted +0.0982 [+0.0630, +0.1341]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.0655 | 0.2720 | -0.0020 [-0.0236, +0.0192] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0348, +0.0501] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0046, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0156 | 0.1165 | +0.0047 [-0.0051, +0.0139] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0004 | 0.0048 | +0.0088 [+0.0069, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0012 | 0.0031 | +0.0302 [+0.0232, +0.0368] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0117 | 0.4146 | -0.0309 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.350 | 0.672 | 0.0611 | 0.2474 | +0.0084 [-0.0103, +0.0260] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.0399 | 0.1133 | +0.0298 [+0.0171, +0.0432] |
| day_type | ordinary | 1603 | 101 | 0.238 | 0.667 | 0.0113 | 0.0630 | +0.0070 [+0.0021, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.1190 | 0.2903 | +0.1049 [+0.0185, +0.1959] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.0269 | 0.1461 | +0.0292 [-0.0008, +0.0572] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6388 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_hinge_fixed (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.208, 0.571] | 0.192 | 1.81 flat / 1.06 weighted | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.206, 0.571] | 0.154 | 1.38 flat / 0.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.391] | 0.808 [0.429, 1.348] | 0.462 [0.226, 0.813] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.391] | 0.808 [0.333, 1.455] | 0.490 [0.177, 0.947] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.115, 0.440] | 1.077 [0.517, 1.904] | 0.702 [0.278, 1.352] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 1.077 [0.471, 2.000] | 0.702 [0.260, 1.392] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 0.846 [0.391, 1.517] | 0.529 [0.210, 0.992] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.709] | 2.000 [0.824, 3.833] | 1.059 [0.333, 2.195] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0415 (168 of 1873 days never flag) | 63 | 0.300 | 0.667 | 0.0600 | +0.0114 [+0.0062, +0.0163] | -0.0036 [-0.0115, +0.0033] | 0.722 | 0.288 | no |
| 2 | 0.103 (168 of 1872 days never flag) | 48 | 0.194 | 0.562 | 0.0643 | +0.0067 [-0.0005, +0.0135] | -0.0033 [-0.0116, +0.0045] | 0.688 | 0.182 | no |
| 3 | 0.104 (168 of 1871 days never flag) | 59 | 0.225 | 0.525 | 0.0657 | +0.0049 [-0.0029, +0.0121] | -0.0014 [-0.0097, +0.0063] | 0.688 | 0.208 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 57 | 0.210 | 0.509 | 0.0684 | +0.0025 [-0.0061, +0.0093] | -0.0060 [-0.0147, +0.0013] | 0.667 | 0.194 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 52 | 0.217 | 0.577 | 0.0668 | +0.0041 [-0.0043, +0.0113] | -0.0034 [-0.0122, +0.0043] | 0.663 | 0.205 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0581, +0.3896]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1029, ΔBrier vs climatology +0.0266 [+0.0153, +0.0389], realised minus predicted +0.0985 [+0.0638, +0.1355]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.0655 | 0.2720 | -0.0020 [-0.0239, +0.0187] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0350, +0.0504] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0043, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0144 | 0.1165 | +0.0040 [-0.0052, +0.0135] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0001 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0011 | 0.0031 | +0.0302 [+0.0233, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0088 | 0.4146 | -0.0335 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.350 | 0.672 | 0.0608 | 0.2474 | +0.0083 [-0.0104, +0.0257] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.0398 | 0.1133 | +0.0297 [+0.0163, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.238 | 0.667 | 0.0110 | 0.0630 | +0.0069 [+0.0019, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.1190 | 0.2903 | +0.1049 [+0.0146, +0.1996] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.0269 | 0.1461 | +0.0292 [-0.0028, +0.0577] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_rolling (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.616] | 0.231 | 3.15 flat / 1.58 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.615] | 0.231 | 2.58 flat / 1.21 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 1.462 [0.680, 2.550] | 0.654 [0.336, 1.125] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 1.500 [0.840, 2.481] | 0.779 [0.423, 1.383] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.885 [1.067, 3.048] | 0.952 [0.543, 1.563] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.654 [0.857, 2.733] | 0.721 [0.387, 1.195] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 1.846 [0.944, 3.059] | 0.808 [0.423, 1.364] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.300, 0.778] | 3.000 [1.389, 5.455] | 1.103 [0.527, 1.983] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.444 (no interval) | 2.472 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0711 (147 of 1873 days never flag) | 97 | 0.421 | 0.608 | 0.0581 | +0.0133 [+0.0081, +0.0191] | -0.0018 [-0.0090, +0.0051] | 0.758 | 0.400 | no |
| 2 | 0.103 (147 of 1872 days never flag) | 83 | 0.317 | 0.530 | 0.0598 | +0.0113 [+0.0054, +0.0170] | +0.0013 [-0.0059, +0.0077] | 0.729 | 0.294 | no |
| 3 | 0.125 (147 of 1871 days never flag) | 100 | 0.370 | 0.510 | 0.0590 | +0.0117 [+0.0060, +0.0170] | +0.0054 [-0.0009, +0.0110] | 0.745 | 0.341 | no |
| 4 | 0.139 (147 of 1870 days never flag) | 96 | 0.384 | 0.552 | 0.0596 | +0.0112 [+0.0059, +0.0162] | +0.0028 [-0.0027, +0.0077] | 0.747 | 0.359 | no |
| 5 | 0.122 (147 of 1869 days never flag) | 101 | 0.384 | 0.525 | 0.0590 | +0.0120 [+0.0064, +0.0170] | +0.0044 [-0.0013, +0.0096] | 0.756 | 0.356 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0363, +0.4045]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0962, ΔBrier vs climatology +0.0332 [+0.0213, +0.0453], realised minus predicted +0.0957 [+0.0617, +0.1322]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.451 | 0.590 | 0.0840 | 0.2720 | +0.0028 [-0.0195, +0.0288] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0053 | 0.0159 | +0.0422 [+0.0348, +0.0503] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0011 | 0.0000 | +0.0137 [+0.0119, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0004 | 0.0200 | +0.0010 [-0.0048, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.923 | 0.0226 | 0.1165 | +0.0113 [+0.0022, +0.0224] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0009 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0021 | 0.0031 | +0.0302 [+0.0230, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.857 | 0.0460 | 0.4146 | 0.0057 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.453 | 0.616 | 0.0757 | 0.2474 | +0.0125 [-0.0069, +0.0337] |
| day_type | month_end | 150 | 17 | 0.529 | 0.750 | 0.0397 | 0.1133 | +0.0295 [+0.0167, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.554 | 0.0170 | 0.0630 | +0.0092 [+0.0037, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1190 | 0.2903 | +0.1049 [+0.0150, +0.1971] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0269 | 0.1461 | +0.0292 [-0.0031, +0.0578] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.4613 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

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

## risk_logistic+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.351, 0.708] | 0.269 | 5.12 flat / 2.32 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.625] | 0.231 | 3.38 flat / 1.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 2.500 [1.667, 3.720] | 1.125 [0.738, 1.719] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.577 [0.765, 2.678] | 0.587 [0.282, 1.000] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 0.846 [0.469, 1.369] | 0.423 [0.224, 0.739] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.458] | 1.423 [0.810, 2.286] | 0.548 [0.321, 0.864] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.219, 0.562] | 2.692 [1.767, 4.000] | 1.269 [0.847, 1.897] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.864] | 5.353 [3.455, 8.308] | 2.162 [1.395, 3.429] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.667 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (105 of 1873 days never flag) | 130 | 0.464 | 0.500 | 0.0523 | +0.0191 [+0.0123, +0.0264] | +0.0040 [-0.0014, +0.0097] | 0.801 | 0.427 | no |
| 2 | 0.875 (126 of 1872 days never flag) | 82 | 0.295 | 0.500 | 0.0557 | +0.0154 [+0.0098, +0.0216] | +0.0054 [+0.0004, +0.0108] | 0.800 | 0.271 | no |
| 3 | 0.421 (147 of 1871 days never flag) | 52 | 0.217 | 0.577 | 0.0551 | +0.0156 [+0.0100, +0.0211] | +0.0093 [+0.0042, +0.0146] | 0.779 | 0.205 | no |
| 4 | 0.786 (126 of 1870 days never flag) | 89 | 0.377 | 0.584 | 0.0544 | +0.0164 [+0.0113, +0.0217] | +0.0079 [+0.0035, +0.0127] | 0.805 | 0.355 | no |
| 5 | 0.334 (126 of 1869 days never flag) | 130 | 0.435 | 0.462 | 0.0548 | +0.0161 [+0.0109, +0.0217] | +0.0086 [+0.0041, +0.0134] | 0.804 | 0.394 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.708 (climatology 0.457, difference +0.2513 [+0.0892, +0.3945]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0722, ΔBrier vs climatology +0.0573 [+0.0396, +0.0772], realised minus predicted +0.0195 [-0.0043, +0.0462]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.541 | 0.1820 | 0.2720 | +0.0382 [+0.0132, +0.0653] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0359 | 0.0159 | +0.0193 [-0.0049, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0182 | 0.0200 | +0.0021 [-0.0046, +0.0081] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0821 | 0.1165 | +0.0236 [+0.0017, +0.0507] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0098 | 0.0048 | +0.0083 [+0.0059, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0102 | 0.0031 | +0.0271 [+0.0200, +0.0339] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1902 | 0.4146 | 0.0703 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.517 | 0.1779 | 0.2474 | +0.0329 [+0.0093, +0.0578] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1046 | 0.1133 | +0.0362 [+0.0093, +0.0647] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.455 | 0.0422 | 0.0630 | +0.0129 [+0.0066, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0222, +0.1607] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0442, +0.1149] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.760] | 0.192 | 2.42 flat / 1.77 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.361, 0.714] | 0.192 | 2.00 flat / 1.39 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.324, 0.682] | 1.731 [1.160, 2.667] | 1.125 [0.687, 1.929] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.361, 0.719] | 1.538 [0.972, 2.450] | 1.000 [0.562, 1.763] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.167, 0.530] | 1.192 [0.697, 1.957] | 0.788 [0.425, 1.412] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.633] | 1.577 [1.045, 2.444] | 1.048 [0.641, 1.759] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.364, 0.714] | 1.808 [1.192, 2.790] | 1.202 [0.725, 2.013] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.368, 0.810] | 1.471 [0.870, 2.417] | 0.706 [0.359, 1.333] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 4.222 (no interval) | 3.778 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 88 | 0.307 | 0.489 | 0.0604 | +0.0110 [+0.0058, +0.0158] | -0.0041 [-0.0125, +0.0039] | 0.641 | 0.281 | no |
| 2 | 0.131 (126 of 1872 days never flag) | 86 | 0.331 | 0.535 | 0.0606 | +0.0105 [+0.0053, +0.0154] | +0.0005 [-0.0068, +0.0073] | 0.639 | 0.308 | no |
| 3 | 0.421 (147 of 1871 days never flag) | 72 | 0.297 | 0.569 | 0.0593 | +0.0114 [+0.0062, +0.0163] | +0.0051 [-0.0016, +0.0110] | 0.638 | 0.279 | no |
| 4 | 0.092 (126 of 1870 days never flag) | 82 | 0.297 | 0.500 | 0.0601 | +0.0107 [+0.0055, +0.0154] | +0.0022 [-0.0044, +0.0083] | 0.632 | 0.273 | no |
| 5 | 0.0786 (126 of 1869 days never flag) | 89 | 0.304 | 0.472 | 0.0602 | +0.0107 [+0.0058, +0.0156] | +0.0032 [-0.0032, +0.0094] | 0.633 | 0.277 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.708 (climatology 0.457, difference +0.2509 [+0.0893, +0.4002]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0846, ΔBrier vs climatology +0.0449 [+0.0325, +0.0588], realised minus predicted +0.0458 [+0.0174, +0.0765]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.574 | 0.1103 | 0.2720 | -0.0019 [-0.0231, +0.0187] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0283 | 0.0159 | +0.0266 [+0.0117, +0.0388] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0058 | 0.0200 | +0.0050 [+0.0011, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0309 | 0.1165 | +0.0125 [+0.0008, +0.0272] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0030 | 0.0048 | +0.0092 [+0.0074, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0053 | 0.0031 | +0.0285 [+0.0222, +0.0350] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0348 | 0.4146 | 0.0030 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1092 | 0.2474 | +0.0037 [-0.0151, +0.0222] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1008 | 0.1133 | +0.0305 [+0.0038, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0129 | 0.0630 | +0.0040 [-0.0012, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3546 | 0.2903 | +0.0906 [+0.0189, +0.1627] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1246 | 0.1461 | +0.0764 [+0.0461, +0.1173] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

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

## structural_fitted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.217, 0.560] | 0.192 | 2.42 flat / 1.01 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.417] | 0.154 | 1.65 flat / 0.71 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 1.192 [0.618, 2.046] | 0.404 [0.205, 0.700] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.321] | 1.423 [0.708, 2.385] | 0.567 [0.225, 1.050] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.346 [0.571, 2.375] | 0.538 [0.194, 1.000] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.276] | 1.077 [0.433, 1.955] | 0.490 [0.147, 0.975] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.045, 0.269] | 0.462 [0.138, 0.929] | 0.192 [0.054, 0.382] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.810] | 3.529 [1.954, 5.877] | 1.500 [0.710, 2.697] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.333 (no interval) | 0.083 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.606 (126 of 1873 days never flag) | 85 | 0.386 | 0.635 | 0.0529 | +0.0185 [+0.0103, +0.0272] | +0.0034 [-0.0029, +0.0101] | 0.875 | 0.368 | yes |
| 2 | 0.833 (126 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0645 | +0.0066 [-0.0036, +0.0171] | -0.0034 [-0.0137, +0.0060] | 0.830 | 0.230 | yes |
| 3 | 0.814 (126 of 1871 days never flag) | 71 | 0.261 | 0.507 | 0.0691 | +0.0015 [-0.0106, +0.0135] | -0.0048 [-0.0167, +0.0071] | 0.804 | 0.241 | yes |
| 4 | 0.943 (126 of 1870 days never flag) | 50 | 0.159 | 0.440 | 0.0703 | +0.0006 [-0.0127, +0.0124] | -0.0079 [-0.0204, +0.0031] | 0.811 | 0.143 | yes |
| 5 | 0.89 (147 of 1869 days never flag) | 31 | 0.138 | 0.613 | 0.0730 | -0.0021 [-0.0152, +0.0092] | -0.0096 [-0.0215, +0.0007] | 0.796 | 0.131 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.570 (climatology 0.457, difference +0.1130 [-0.0716, +0.2689]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0447 [+0.0267, +0.0639], realised minus predicted -0.0060 [-0.0356, +0.0257]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.641 | 0.2944 | 0.2720 | +0.0321 [-0.0052, +0.0719] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1111 | 0.0159 | +0.0268 [+0.0154, +0.0377] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0197 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0234 | 0.0200 | +0.0009 [-0.0043, +0.0048] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.667 | 0.0746 | 0.1165 | +0.0231 [+0.0031, +0.0482] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0189 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0666 | 0.0031 | +0.0251 [+0.0190, +0.0311] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1730 | 0.4146 | 0.0733 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.634 | 0.2732 | 0.2474 | +0.0312 [+0.0012, +0.0644] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1569 | 0.1133 | +0.0390 [+0.0091, +0.0689] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.589 | 0.0832 | 0.0630 | +0.0123 [+0.0044, +0.0204] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2018 | 0.2903 | +0.1343 [+0.0722, +0.1947] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1610 | 0.1461 | +0.0557 [+0.0092, +0.1014] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2826 | 0.2213 |

## structural_liquidity (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.217, 0.552] | 0.192 | 2.42 flat / 1.01 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.130, 0.421] | 0.154 | 1.65 flat / 0.71 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.552] | 1.192 [0.606, 2.105] | 0.404 [0.196, 0.711] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.423 [0.680, 2.409] | 0.567 [0.220, 1.068] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.379] | 1.346 [0.571, 2.438] | 0.538 [0.200, 1.029] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.042, 0.276] | 1.077 [0.433, 1.948] | 0.490 [0.150, 0.987] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 0.462 [0.138, 0.947] | 0.192 [0.054, 0.388] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 3.529 [1.933, 5.941] | 1.500 [0.683, 2.695] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 0.333 [0.000, 0.833] | 0.083 [0.000, 0.208] |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.606 (126 of 1873 days never flag) | 85 | 0.386 | 0.635 | 0.0529 | +0.0185 [+0.0104, +0.0277] | +0.0034 [-0.0029, +0.0101] | 0.875 | 0.368 | yes |
| 2 | 0.833 (126 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0645 | +0.0066 [-0.0044, +0.0159] | -0.0034 [-0.0133, +0.0059] | 0.830 | 0.230 | yes |
| 3 | 0.814 (126 of 1871 days never flag) | 71 | 0.261 | 0.507 | 0.0691 | +0.0015 [-0.0115, +0.0132] | -0.0048 [-0.0175, +0.0065] | 0.804 | 0.241 | yes |
| 4 | 0.943 (126 of 1870 days never flag) | 50 | 0.159 | 0.440 | 0.0703 | +0.0006 [-0.0124, +0.0114] | -0.0079 [-0.0201, +0.0026] | 0.811 | 0.143 | yes |
| 5 | 0.89 (147 of 1869 days never flag) | 31 | 0.138 | 0.613 | 0.0730 | -0.0021 [-0.0147, +0.0091] | -0.0096 [-0.0214, +0.0009] | 0.796 | 0.131 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.570 (climatology 0.457, difference +0.1130 [-0.0692, +0.2704]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0447 [+0.0261, +0.0645], realised minus predicted -0.0060 [-0.0350, +0.0251]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.641 | 0.2944 | 0.2720 | +0.0321 [-0.0050, +0.0708] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1111 | 0.0159 | +0.0268 [+0.0160, +0.0373] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0197 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0234 | 0.0200 | +0.0009 [-0.0041, +0.0049] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.667 | 0.0746 | 0.1165 | +0.0231 [+0.0027, +0.0495] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0189 | 0.0048 | +0.0085 [+0.0066, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0666 | 0.0031 | +0.0251 [+0.0191, +0.0315] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1730 | 0.4146 | +0.0733 [-0.0174, +0.1691] |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.634 | 0.2732 | 0.2474 | +0.0312 [+0.0013, +0.0620] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1569 | 0.1133 | +0.0390 [+0.0091, +0.0702] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.589 | 0.0832 | 0.0630 | +0.0123 [+0.0044, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2018 | 0.2903 | +0.1343 [+0.0762, +0.1967] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1610 | 0.1461 | +0.0557 [+0.0113, +0.0996] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2826 | 0.2213 |

## structural_rolling (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.259, 0.600] | 0.231 | 4.19 flat / 1.69 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.593] | 0.231 | 3.58 flat / 1.46 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.519] | 1.654 [1.000, 2.548] | 0.471 [0.269, 0.750] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.519] | 2.538 [1.571, 3.846] | 0.923 [0.518, 1.490] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.515] | 2.423 [1.500, 3.667] | 0.923 [0.500, 1.475] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.615 [1.611, 4.000] | 0.981 [0.580, 1.546] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.435] | 1.923 [1.061, 3.150] | 0.798 [0.396, 1.364] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.214, 0.625] | 3.471 [2.000, 5.813] | 1.309 [0.675, 2.275] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 5.556 [2.800, 10.333] | 2.417 [1.033, 5.002] |

Recall with equal weight per regime: 0.303 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.327 (126 of 1873 days never flag) | 113 | 0.500 | 0.619 | 0.0477 | +0.0237 [+0.0158, +0.0328] | +0.0086 [+0.0039, +0.0139] | 0.889 | 0.475 | no |
| 2 | 0.383 (126 of 1872 days never flag) | 135 | 0.496 | 0.511 | 0.0567 | +0.0144 [+0.0055, +0.0239] | +0.0044 [-0.0028, +0.0119] | 0.855 | 0.458 | no |
| 3 | 0.362 (126 of 1871 days never flag) | 123 | 0.435 | 0.488 | 0.0593 | +0.0114 [+0.0016, +0.0208] | +0.0050 [-0.0034, +0.0133] | 0.833 | 0.398 | no |
| 4 | 0.31 (126 of 1870 days never flag) | 131 | 0.457 | 0.481 | 0.0589 | +0.0119 [+0.0033, +0.0212] | +0.0034 [-0.0034, +0.0107] | 0.863 | 0.417 | no |
| 5 | 0.36 (147 of 1869 days never flag) | 99 | 0.355 | 0.495 | 0.0601 | +0.0108 [+0.0025, +0.0196] | +0.0033 [-0.0030, +0.0098] | 0.848 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.645 (climatology 0.457, difference +0.1880 [-0.0447, +0.4340]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0795, ΔBrier vs climatology +0.0500 [+0.0316, +0.0714], realised minus predicted +0.0252 [-0.0036, +0.0577]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.461 | 0.653 | 0.1815 | 0.2720 | +0.0385 [+0.0157, +0.0652] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0859 | 0.0159 | +0.0325 [+0.0219, +0.0421] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0181 | 0.0000 | +0.0134 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0224 | 0.0200 | +0.0007 [-0.0046, +0.0048] |
| regime | 2025-26 | 249 | 29 | 0.759 | 0.611 | 0.1463 | 0.1165 | +0.0467 [+0.0057, +0.0970] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0181 | 0.0048 | +0.0084 [+0.0065, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.250 | 0.0664 | 0.0031 | +0.0229 [+0.0117, +0.0318] |
| scarcity_state | 2 | 41 | 17 | 0.706 | 0.667 | 0.3719 | 0.4146 | 0.1906 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.487 | 0.640 | 0.1894 | 0.2474 | +0.0432 [+0.0228, +0.0667] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1217 | 0.1133 | +0.0417 [+0.0140, +0.0742] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.592 | 0.0672 | 0.0630 | +0.0174 [+0.0103, +0.0260] |
| day_type | quarter_end | 31 | 9 | 0.556 | 1.000 | 0.1889 | 0.2903 | +0.1586 [+0.0838, +0.2360] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.588 | 0.1496 | 0.1461 | +0.0591 [+0.0322, +0.0852] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0218 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3089 | 0.2213 |

