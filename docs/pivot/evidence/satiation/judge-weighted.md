# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `e936998e873a…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

## calendar_climatology (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.212, 0.576] | 0.269 | 5.65 flat / 3.29 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

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

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.267 (84 of 1873 days never flag) | 258 | 0.600 | 0.326 | 0.0714 | +0.0000 [+0.0000, +0.0000] | -0.0151 [-0.0211, -0.0097] | 0.586 | 0.500 | no |
| 2 | 0.267 (147 of 1872 days never flag) | 213 | 0.496 | 0.324 | 0.0711 | +0.0000 [+0.0000, +0.0000] | -0.0100 [-0.0146, -0.0054] | 0.586 | 0.413 | no |
| 3 | 0.267 (147 of 1871 days never flag) | 213 | 0.493 | 0.319 | 0.0707 | +0.0000 [+0.0000, +0.0000] | -0.0063 [-0.0098, -0.0028] | 0.585 | 0.409 | no |
| 4 | 0.267 (147 of 1870 days never flag) | 213 | 0.486 | 0.315 | 0.0708 | +0.0000 [+0.0000, +0.0000] | -0.0085 [-0.0120, -0.0048] | 0.580 | 0.401 | no |
| 5 | 0.267 (147 of 1869 days never flag) | 213 | 0.478 | 0.310 | 0.0709 | +0.0000 [+0.0000, +0.0000] | -0.0075 [-0.0114, -0.0036] | 0.578 | 0.393 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.512 (climatology 0.512, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1757, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0470 [-0.1017, +0.0117]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.386 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0645 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0913 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1596 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1021 | 0.2439 | 0.0000 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.375 | 0.1369 | 0.2615 | +0.0000 [+0.0000, +0.0000] |
| day_type | month_end | 150 | 17 | 0.588 | 0.345 | 0.1364 | 0.1133 | +0.0000 [+0.0000, +0.0000] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.341 | 0.1006 | 0.0630 | +0.0000 [+0.0000, +0.0000] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.235 | 0.4089 | 0.2903 | +0.0000 [+0.0000, +0.0000] |
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
| lead_at_least_1 | 26 | 12 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.256, 0.600] | 0.368 | 6.88 flat / 3.20 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

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

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.185 (147 of 1873 days never flag) | 286 | 0.736 | 0.360 | 0.0563 | +0.0151 [+0.0094, +0.0214] | +0.0000 [+0.0000, +0.0000] | 0.876 | 0.630 | no |
| 2 | 0.225 (147 of 1872 days never flag) | 215 | 0.655 | 0.423 | 0.0611 | +0.0100 [+0.0056, +0.0146] | +0.0000 [+0.0000, +0.0000] | 0.817 | 0.583 | no |
| 3 | 0.239 (147 of 1871 days never flag) | 243 | 0.645 | 0.366 | 0.0644 | +0.0063 [+0.0030, +0.0098] | +0.0000 [+0.0000, +0.0000] | 0.765 | 0.556 | no |
| 4 | 0.208 (189 of 1870 days never flag) | 222 | 0.594 | 0.369 | 0.0624 | +0.0085 [+0.0047, +0.0121] | +0.0000 [+0.0000, +0.0000] | 0.788 | 0.513 | no |
| 5 | 0.221 (189 of 1869 days never flag) | 199 | 0.587 | 0.407 | 0.0634 | +0.0075 [+0.0036, +0.0114] | +0.0000 [+0.0000, +0.0000] | 0.772 | 0.519 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.506 (climatology 0.512, difference -0.0059 [-0.0893, +0.0823]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0510, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.824 | 0.377 | 0.1679 | 0.2720 | +0.0168 [-0.0027, +0.0376] |
| regime | 2020 | 251 | 4 | 0.250 | 0.042 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.486 | 0.0978 | 0.1165 | +0.0256 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.167 | 0.0240 | 0.0048 | +0.0080 [+0.0058, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0873 | 0.0000 | +0.0224 [+0.0166, +0.0283] |
| scarcity_state | 2 | 41 | 10 | 0.400 | 0.400 | 0.1445 | 0.2439 | 0.0333 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.784 | 0.368 | 0.1830 | 0.2615 | +0.0241 [+0.0043, +0.0450] |
| day_type | month_end | 150 | 17 | 0.824 | 0.609 | 0.0778 | 0.1133 | +0.0212 [+0.0029, +0.0434] |
| day_type | ordinary | 1603 | 101 | 0.752 | 0.313 | 0.0774 | 0.0630 | +0.0125 [+0.0072, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.0845 | 0.2903 | +0.0604 [-0.0440, +0.1631] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.0819 | 0.1461 | +0.0355 [+0.0130, +0.0568] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1364 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3171 | 0.2213 |

## ngboost_laplace (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.650] | 0.269 | 4.73 flat / 2.01 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.760] | 3.308 [1.966, 5.211] | 1.413 [0.780, 2.348] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 3.462 [2.053, 5.334] | 1.423 [0.784, 2.283] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.189, 0.515] | 3.269 [1.914, 5.167] | 1.288 [0.694, 2.090] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 3.577 [2.095, 5.591] | 1.596 [0.833, 2.630] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.546] | 4.077 [2.484, 6.222] | 1.731 [0.970, 2.782] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.647 [5.161, 11.572] | 3.265 [2.039, 5.319] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 0.889 (no interval) | 0.583 (no interval) |

Recall with equal weight per regime: 0.426 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.334 (126 of 1873 days never flag) | 161 | 0.536 | 0.466 | 0.0462 | +0.0252 [+0.0186, +0.0323] | +0.0101 [+0.0050, +0.0152] | 0.928 | 0.486 | no |
| 2 | 0.297 (147 of 1872 days never flag) | 150 | 0.432 | 0.400 | 0.0568 | +0.0143 [+0.0086, +0.0201] | +0.0043 [-0.0009, +0.0092] | 0.899 | 0.380 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 144 | 0.428 | 0.410 | 0.0595 | +0.0112 [+0.0046, +0.0169] | +0.0049 [-0.0008, +0.0100] | 0.892 | 0.378 | no |
| 4 | 0.302 (126 of 1870 days never flag) | 133 | 0.290 | 0.301 | 0.0615 | +0.0093 [+0.0028, +0.0154] | +0.0008 [-0.0050, +0.0062] | 0.873 | 0.236 | no |
| 5 | 0.32 (126 of 1869 days never flag) | 163 | 0.413 | 0.350 | 0.0637 | +0.0072 [-0.0004, +0.0140] | -0.0003 [-0.0076, +0.0060] | 0.862 | 0.352 | no |

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
| regime | 2018-19 | 375 | 102 | 0.608 | 0.437 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0503 | 0.0159 | +0.0329 [+0.0235, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.917 | 0.0443 | 0.1165 | +0.0287 [+0.0113, +0.0503] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0096 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0260 | 0.0000 | +0.0283 [+0.0221, +0.0343] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 1.000 | 0.0561 | 0.2439 | +0.0463 [+0.0179, +0.0828] |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.458 | 0.2024 | 0.2615 | +0.0552 [+0.0317, +0.0794] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.0819 | 0.1133 | +0.0481 [+0.0291, +0.0671] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.395 | 0.0518 | 0.0630 | +0.0187 [+0.0123, +0.0262] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.1699 | 0.2903 | +0.1308 [+0.0495, +0.2125] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.0904 | 0.1461 | +0.0670 [+0.0493, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## projected_fitted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.263, 0.667] | 0.280 | 5.96 flat / 3.13 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.150, 0.484] | 0.231 | 4.19 flat / 2.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.227, 0.625] | 4.654 [3.067, 7.037] | 2.096 [1.324, 3.313] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.530] | 3.500 [2.099, 5.526] | 1.596 [0.910, 2.667] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.147, 0.482] | 3.769 [2.290, 6.053] | 1.933 [1.034, 3.376] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.087, 0.393] | 3.038 [1.767, 5.050] | 1.721 [0.858, 3.198] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.043, 0.273] | 1.269 [0.600, 2.333] | 0.596 [0.280, 1.095] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.938] | 7.294 [4.889, 11.204] | 3.118 [1.905, 5.228] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 3.444 [1.000, 9.573] | 3.167 [0.795, 8.900] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.474 (126 of 1873 days never flag) | 206 | 0.607 | 0.413 | 0.0554 | +0.0160 [+0.0078, +0.0253] | +0.0009 [-0.0062, +0.0087] | 0.884 | 0.537 | no |
| 2 | 0.407 (147 of 1872 days never flag) | 164 | 0.525 | 0.445 | 0.0596 | +0.0114 [+0.0039, +0.0201] | +0.0014 [-0.0065, +0.0102] | 0.856 | 0.473 | no |
| 3 | 0.559 (147 of 1871 days never flag) | 166 | 0.493 | 0.410 | 0.0640 | +0.0067 [-0.0019, +0.0159] | +0.0004 [-0.0086, +0.0097] | 0.832 | 0.436 | no |
| 4 | 0.456 (147 of 1870 days never flag) | 135 | 0.406 | 0.415 | 0.0624 | +0.0084 [+0.0004, +0.0172] | -0.0000 [-0.0084, +0.0089] | 0.836 | 0.360 | no |
| 5 | 0.621 (147 of 1869 days never flag) | 62 | 0.210 | 0.468 | 0.0708 | +0.0001 [-0.0121, +0.0110] | -0.0075 [-0.0190, +0.0034] | 0.816 | 0.191 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.582 (climatology 0.512, difference +0.0698 [-0.0377, +0.1588]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0979, ΔBrier vs climatology +0.0315 [+0.0159, +0.0484], realised minus predicted +0.0096 [-0.0262, +0.0444]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.804 | 0.423 | 0.3283 | 0.2720 | +0.0329 [-0.0082, +0.0773] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1281 | 0.0159 | +0.0179 [+0.0093, +0.0249] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0117, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0040 | 0.0200 | +0.0017 [-0.0029, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.103 | 0.750 | 0.0287 | 0.1165 | +0.0111 [+0.0034, +0.0198] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0051 | 0.0048 | +0.0090 [+0.0073, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0795 | 0.0000 | +0.0205 [+0.0170, +0.0238] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0775 | 0.2439 | -0.0072 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.680 | 0.425 | 0.2878 | 0.2615 | +0.0304 [-0.0015, +0.0655] |
| day_type | month_end | 150 | 17 | 0.588 | 0.556 | 0.1211 | 0.1133 | +0.0333 [+0.0132, +0.0555] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.382 | 0.0800 | 0.0630 | +0.0117 [+0.0035, +0.0207] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.444 | 0.3015 | 0.2903 | +0.0664 [+0.0263, +0.1018] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1702 | 0.1461 | +0.0472 [+0.0137, +0.0831] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.3079 | 0.2213 |

## projected_hinge_fixed (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.241, 0.619] | 0.269 | 5.77 flat / 2.80 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.174, 0.538] | 0.231 | 4.15 flat / 2.05 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.769 [3.096, 7.002] | 2.144 [1.308, 3.312] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.962 [2.368, 6.137] | 1.942 [1.080, 3.126] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.808 [2.225, 5.923] | 1.808 [0.975, 2.934] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.147, 0.471] | 3.115 [1.682, 5.048] | 1.606 [0.802, 2.703] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 1.308 [0.600, 2.333] | 0.606 [0.265, 1.083] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.889] | 7.647 [5.069, 11.335] | 3.250 [1.958, 5.229] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 2.222 (no interval) | 1.944 (no interval) |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.474 (126 of 1873 days never flag) | 208 | 0.600 | 0.404 | 0.0550 | +0.0164 [+0.0083, +0.0252] | +0.0014 [-0.0060, +0.0090] | 0.896 | 0.528 | no |
| 2 | 0.515 (147 of 1872 days never flag) | 177 | 0.532 | 0.418 | 0.0598 | +0.0112 [+0.0029, +0.0193] | +0.0012 [-0.0072, +0.0097] | 0.868 | 0.473 | no |
| 3 | 0.484 (147 of 1871 days never flag) | 167 | 0.493 | 0.407 | 0.0627 | +0.0080 [-0.0011, +0.0168] | +0.0017 [-0.0076, +0.0103] | 0.838 | 0.436 | no |
| 4 | 0.456 (147 of 1870 days never flag) | 134 | 0.384 | 0.396 | 0.0625 | +0.0083 [-0.0001, +0.0174] | -0.0001 [-0.0090, +0.0092] | 0.844 | 0.337 | no |
| 5 | 0.675 (147 of 1869 days never flag) | 62 | 0.203 | 0.452 | 0.0695 | +0.0015 [-0.0105, +0.0131] | -0.0061 [-0.0175, +0.0051] | 0.815 | 0.183 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.562 (climatology 0.512, difference +0.0497 [-0.0517, +0.1379]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0943, ΔBrier vs climatology +0.0352 [+0.0196, +0.0510], realised minus predicted +0.0274 [-0.0050, +0.0633]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.804 | 0.416 | 0.3207 | 0.2720 | +0.0352 [-0.0047, +0.0752] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0865 | 0.0159 | +0.0207 [+0.0055, +0.0346] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0067 | 0.0200 | +0.0021 [-0.0020, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.069 | 0.667 | 0.0253 | 0.1165 | +0.0065 [+0.0005, +0.0139] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0071 | 0.0048 | +0.0091 [+0.0075, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0201 | 0.0000 | +0.0308 [+0.0249, +0.0366] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1004 | 0.2439 | -0.0445 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.412 | 0.2881 | 0.2615 | +0.0282 [-0.0037, +0.0604] |
| day_type | month_end | 150 | 17 | 0.588 | 0.500 | 0.1111 | 0.1133 | +0.0314 [+0.0120, +0.0530] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.365 | 0.0730 | 0.0630 | +0.0118 [+0.0038, +0.0203] |
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
| lead_at_least_1 | 26 | 11 | 0.423 [0.238, 0.611] | 0.269 | 5.73 flat / 2.78 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.182, 0.531] | 0.231 | 4.04 flat / 2.04 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.238, 0.611] | 4.769 [3.000, 7.154] | 2.144 [1.273, 3.355] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.474] | 3.154 [1.750, 5.161] | 1.654 [0.839, 2.869] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 3.577 [2.037, 5.700] | 1.731 [0.906, 2.945] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.143, 0.474] | 3.192 [1.708, 5.308] | 1.683 [0.844, 2.941] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.385] | 2.000 [0.880, 3.697] | 0.827 [0.379, 1.525] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.409, 0.882] | 7.647 [5.000, 11.692] | 3.250 [1.941, 5.233] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 2.111 [0.500, 5.669] | 1.889 [0.361, 5.335] |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.465 (126 of 1873 days never flag) | 209 | 0.607 | 0.407 | 0.0539 | +0.0175 [+0.0096, +0.0270] | +0.0024 [-0.0042, +0.0105] | 0.920 | 0.536 | no |
| 2 | 0.514 (147 of 1872 days never flag) | 139 | 0.410 | 0.410 | 0.0588 | +0.0123 [+0.0045, +0.0209] | +0.0023 [-0.0060, +0.0106] | 0.907 | 0.363 | no |
| 3 | 0.483 (147 of 1871 days never flag) | 152 | 0.428 | 0.388 | 0.0619 | +0.0088 [+0.0000, +0.0183] | +0.0024 [-0.0064, +0.0120] | 0.901 | 0.374 | no |
| 4 | 0.501 (147 of 1870 days never flag) | 137 | 0.391 | 0.394 | 0.0612 | +0.0096 [+0.0007, +0.0188] | +0.0011 [-0.0080, +0.0104] | 0.899 | 0.343 | no |
| 5 | 0.53 (147 of 1869 days never flag) | 98 | 0.333 | 0.469 | 0.0632 | +0.0077 [-0.0016, +0.0171] | +0.0002 [-0.0091, +0.0097] | 0.879 | 0.303 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.512, difference +0.0610 [-0.0332, +0.1420]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0887, ΔBrier vs climatology +0.0407 [+0.0265, +0.0565], realised minus predicted +0.0386 [+0.0073, +0.0724]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.804 | 0.416 | 0.3229 | 0.2720 | +0.0352 [-0.0021, +0.0787] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0731 | 0.0159 | +0.0217 [+0.0065, +0.0360] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0022 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0021 [-0.0020, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.103 | 0.750 | 0.0329 | 0.1165 | +0.0134 [+0.0049, +0.0234] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0032 | 0.0048 | +0.0092 [+0.0075, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0067 | 0.0000 | +0.0315 [+0.0248, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1201 | 0.2439 | -0.0256 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.680 | 0.415 | 0.2924 | 0.2615 | +0.0303 [+0.0002, +0.0656] |
| day_type | month_end | 150 | 17 | 0.588 | 0.500 | 0.1086 | 0.1133 | +0.0330 [+0.0127, +0.0563] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.368 | 0.0711 | 0.0630 | +0.0124 [+0.0047, +0.0213] |
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
| lead_at_least_1 | 26 | 13 | 0.500 [0.316, 0.692] | 0.423 | 8.15 flat / 4.85 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.640] | 0.349 | 6.62 flat / 4.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 6.077 [4.036, 9.002] | 3.077 [1.994, 4.807] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.808 [3.067, 7.318] | 2.625 [1.647, 4.207] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.650] | 5.885 [3.846, 8.957] | 3.519 [2.257, 5.643] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.568] | 4.462 [2.857, 6.880] | 2.500 [1.604, 3.984] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.121, 0.444] | 3.615 [2.174, 5.696] | 1.856 [1.140, 2.978] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.786] | 5.353 [2.947, 9.054] | 2.279 [1.141, 4.167] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 13.444 (no interval) | 9.694 (no interval) |

Recall with equal weight per regime: 0.332 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.188 (105 of 1873 days never flag) | 251 | 0.664 | 0.371 | 0.0539 | +0.0175 [+0.0100, +0.0260] | +0.0024 [-0.0036, +0.0084] | 0.866 | 0.573 | no |
| 2 | 0.267 (126 of 1872 days never flag) | 204 | 0.568 | 0.387 | 0.0566 | +0.0145 [+0.0072, +0.0226] | +0.0045 [-0.0020, +0.0113] | 0.819 | 0.496 | no |
| 3 | 0.205 (126 of 1871 days never flag) | 233 | 0.580 | 0.343 | 0.0607 | +0.0100 [+0.0020, +0.0186] | +0.0037 [-0.0042, +0.0119] | 0.786 | 0.491 | no |
| 4 | 0.235 (147 of 1870 days never flag) | 190 | 0.536 | 0.389 | 0.0587 | +0.0122 [+0.0050, +0.0200] | +0.0037 [-0.0024, +0.0102] | 0.811 | 0.469 | no |
| 5 | 0.359 (147 of 1869 days never flag) | 152 | 0.420 | 0.382 | 0.0624 | +0.0086 [+0.0010, +0.0170] | +0.0010 [-0.0051, +0.0079] | 0.785 | 0.366 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.6 over 1041 days; regime_2021-23: 2.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 3.1 over 1041 days; regime_2021-23: 3.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 6.1 over 1041 days; regime_2021-23: 9.1 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 3.1 over 1041 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 2.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.526 (climatology 0.512, difference +0.0135 [-0.0881, +0.1429]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0177, +0.0529], realised minus predicted +0.0114 [-0.0237, +0.0461]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.430 | 0.1637 | 0.2720 | +0.0266 [+0.0051, +0.0513] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0877 | 0.0159 | +0.0304 [+0.0221, +0.0385] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0311 | 0.0000 | +0.0103 [+0.0070, +0.0132] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0244 | 0.0200 | +0.0024 [-0.0015, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.931 | 0.397 | 0.1827 | 0.1165 | +0.0275 [-0.0133, +0.0788] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.067 | 0.0296 | 0.0048 | +0.0056 [+0.0028, +0.0083] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0646 | 0.0000 | +0.0254 [+0.0199, +0.0310] |
| scarcity_state | 2 | 41 | 10 | 1.000 | 0.303 | 0.4360 | 0.2439 | 0.0430 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.434 | 0.1870 | 0.2615 | +0.0359 [+0.0138, +0.0606] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1161 | 0.1133 | +0.0397 [+0.0114, +0.0727] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.350 | 0.0717 | 0.0630 | +0.0122 [+0.0057, +0.0196] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3472 | 0.2903 | +0.1099 [+0.0564, +0.1629] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.357 | 0.1706 | 0.1461 | +0.0435 [+0.0200, +0.0690] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0046 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2985 | 0.2213 |

## risk_gbm (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.154 | 1.42 flat / 0.95 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.310, 0.667] | 1.385 [0.914, 2.053] | 0.798 [0.500, 1.286] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.455] | 1.154 [0.667, 1.909] | 0.683 [0.327, 1.292] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.038 [0.606, 1.714] | 0.587 [0.282, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 0.923 [0.543, 1.500] | 0.471 [0.232, 0.888] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.231 [0.731, 2.002] | 0.760 [0.379, 1.398] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.800] | 1.353 [0.800, 2.250] | 0.618 [0.321, 1.167] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.556 [1.800, 8.200] | 3.111 [1.477, 7.568] |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 78 | 0.300 | 0.538 | 0.0577 | +0.0137 [+0.0082, +0.0193] | -0.0014 [-0.0097, +0.0063] | 0.642 | 0.279 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 55 | 0.180 | 0.455 | 0.0687 | +0.0024 [-0.0040, +0.0080] | -0.0076 [-0.0161, -0.0005] | 0.578 | 0.163 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0667 | +0.0040 [-0.0025, +0.0098] | -0.0023 [-0.0102, +0.0044] | 0.579 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 49 | 0.181 | 0.510 | 0.0668 | +0.0040 [-0.0028, +0.0099] | -0.0045 [-0.0121, +0.0023] | 0.579 | 0.167 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0053, +0.0074] | -0.0062 [-0.0136, +0.0007] | 0.577 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0116 [-0.1321, +0.1327]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1047, ΔBrier vs climatology +0.0248 [+0.0158, +0.0336], realised minus predicted +0.0931 [+0.0563, +0.1320]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0959 | 0.2720 | +0.0016 [-0.0200, +0.0242] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0148 | 0.0159 | +0.0396 [+0.0307, +0.0483] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0028 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0386 | 0.1165 | +0.0155 [-0.0024, +0.0394] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.167 | 0.0022 | 0.0048 | +0.0089 [+0.0069, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0021 | 0.0000 | +0.0317 [+0.0250, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0190 | 0.2439 | -0.0107 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.0978 | 0.2615 | +0.0144 [-0.0060, +0.0352] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0985 | 0.1133 | +0.0543 [+0.0303, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2204 | 0.2903 | +0.1155 [+0.0314, +0.2020] |
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
| lead_at_least_1 | 26 | 10 | 0.385 [0.212, 0.571] | 0.231 | 2.77 flat / 1.76 weighted | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.208, 0.576] | 0.192 | 2.08 flat / 1.39 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 0.962 [0.560, 1.524] | 0.500 [0.250, 0.850] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 1.538 [0.929, 2.500] | 1.058 [0.576, 1.834] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.115 [0.645, 1.790] | 0.750 [0.371, 1.306] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 1.462 [0.750, 2.522] | 0.981 [0.448, 1.772] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.346 [0.769, 2.174] | 0.904 [0.481, 1.533] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.714] | 2.471 [1.214, 4.429] | 1.221 [0.472, 2.412] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 2.778 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 71 | 0.329 | 0.648 | 0.0599 | +0.0116 [+0.0063, +0.0165] | -0.0035 [-0.0113, +0.0037] | 0.723 | 0.314 | no |
| 2 | 0.0312 (147 of 1872 days never flag) | 76 | 0.259 | 0.474 | 0.0628 | +0.0082 [+0.0024, +0.0141] | -0.0018 [-0.0091, +0.0052] | 0.696 | 0.236 | no |
| 3 | 0.0323 (147 of 1871 days never flag) | 67 | 0.275 | 0.567 | 0.0635 | +0.0072 [+0.0009, +0.0127] | +0.0008 [-0.0059, +0.0070] | 0.694 | 0.259 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 69 | 0.225 | 0.449 | 0.0645 | +0.0063 [+0.0008, +0.0118] | -0.0021 [-0.0084, +0.0039] | 0.689 | 0.203 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 66 | 0.225 | 0.470 | 0.0627 | +0.0082 [+0.0027, +0.0136] | +0.0007 [-0.0057, +0.0067] | 0.681 | 0.204 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1890 [+0.0444, +0.3107]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1019, ΔBrier vs climatology +0.0275 [+0.0164, +0.0393], realised minus predicted +0.1004 [+0.0647, +0.1393]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.655 | 0.0653 | 0.2720 | -0.0020 [-0.0236, +0.0186] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0346, +0.0500] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0013 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0047, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0165 | 0.1165 | +0.0049 [-0.0043, +0.0151] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0010 | 0.0048 | +0.0089 [+0.0070, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0014 | 0.0000 | +0.0318 [+0.0249, +0.0383] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0061 | 0.2439 | -0.0107 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.667 | 0.0609 | 0.2615 | +0.0060 [-0.0125, +0.0229] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.0401 | 0.1133 | +0.0298 [+0.0161, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.692 | 0.0117 | 0.0630 | +0.0071 [+0.0020, +0.0116] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0102, +0.1953] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.0269 | 0.1461 | +0.0292 [-0.0010, +0.0578] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6331 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_fitted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.200, 0.583] | 0.231 | 2.73 flat / 1.79 weighted | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.206, 0.565] | 0.192 | 2.15 flat / 1.50 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.483] | 0.962 [0.556, 1.500] | 0.500 [0.257, 0.844] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.154, 0.481] | 1.500 [0.875, 2.444] | 1.048 [0.548, 1.800] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.542] | 1.154 [0.640, 1.842] | 0.779 [0.379, 1.347] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.536] | 1.308 [0.607, 2.304] | 0.846 [0.350, 1.565] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 1.462 [0.844, 2.320] | 1.019 [0.539, 1.731] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.722] | 2.412 [1.200, 4.267] | 1.235 [0.473, 2.425] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 71 | 0.329 | 0.648 | 0.0599 | +0.0115 [+0.0063, +0.0166] | -0.0036 [-0.0114, +0.0035] | 0.732 | 0.314 | no |
| 2 | 0.0312 (147 of 1872 days never flag) | 75 | 0.259 | 0.480 | 0.0629 | +0.0082 [+0.0022, +0.0139] | -0.0018 [-0.0090, +0.0049] | 0.703 | 0.236 | no |
| 3 | 0.0323 (147 of 1871 days never flag) | 68 | 0.275 | 0.559 | 0.0635 | +0.0071 [+0.0009, +0.0129] | +0.0008 [-0.0063, +0.0070] | 0.706 | 0.258 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 65 | 0.225 | 0.477 | 0.0647 | +0.0061 [+0.0001, +0.0117] | -0.0023 [-0.0095, +0.0040] | 0.690 | 0.205 | no |
| 5 | 0.04 (147 of 1869 days never flag) | 69 | 0.225 | 0.449 | 0.0627 | +0.0083 [+0.0024, +0.0136] | +0.0007 [-0.0058, +0.0067] | 0.687 | 0.203 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1890 [+0.0356, +0.3144]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1023, ΔBrier vs climatology +0.0272 [+0.0162, +0.0388], realised minus predicted +0.1010 [+0.0658, +0.1371]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.655 | 0.0655 | 0.2720 | -0.0020 [-0.0236, +0.0192] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0348, +0.0501] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0046, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0156 | 0.1165 | +0.0047 [-0.0051, +0.0139] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0004 | 0.0048 | +0.0089 [+0.0070, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0011 | 0.0000 | +0.0318 [+0.0253, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0052 | 0.2439 | -0.0114 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.667 | 0.0610 | 0.2615 | +0.0059 [-0.0116, +0.0230] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.0399 | 0.1133 | +0.0298 [+0.0171, +0.0432] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.692 | 0.0113 | 0.0630 | +0.0070 [+0.0021, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0185, +0.1959] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.0269 | 0.1461 | +0.0292 [-0.0008, +0.0572] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6388 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_hinge_fixed (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.208, 0.571] | 0.231 | 3.27 flat / 1.98 weighted | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.206, 0.571] | 0.192 | 2.12 flat / 1.48 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 1.538 [0.875, 2.542] | 0.712 [0.391, 1.167] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 1.500 [0.903, 2.371] | 1.048 [0.577, 1.784] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.529] | 1.154 [0.652, 1.867] | 0.779 [0.385, 1.339] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.269 [0.611, 2.250] | 0.827 [0.344, 1.542] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 1.423 [0.842, 2.333] | 1.010 [0.542, 1.734] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.709] | 2.412 [1.227, 4.251] | 1.235 [0.464, 2.382] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.889 (no interval) | 3.389 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 91 | 0.364 | 0.560 | 0.0600 | +0.0114 [+0.0062, +0.0163] | -0.0036 [-0.0115, +0.0033] | 0.722 | 0.341 | no |
| 2 | 0.0312 (147 of 1872 days never flag) | 75 | 0.259 | 0.480 | 0.0630 | +0.0081 [+0.0020, +0.0140] | -0.0019 [-0.0095, +0.0051] | 0.671 | 0.236 | no |
| 3 | 0.0323 (147 of 1871 days never flag) | 68 | 0.275 | 0.559 | 0.0636 | +0.0071 [+0.0010, +0.0128] | +0.0008 [-0.0058, +0.0071] | 0.689 | 0.258 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 64 | 0.225 | 0.484 | 0.0649 | +0.0060 [-0.0001, +0.0111] | -0.0025 [-0.0093, +0.0034] | 0.673 | 0.206 | no |
| 5 | 0.04 (147 of 1869 days never flag) | 68 | 0.225 | 0.456 | 0.0628 | +0.0081 [+0.0023, +0.0136] | +0.0006 [-0.0058, +0.0067] | 0.667 | 0.203 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1890 [+0.0479, +0.3155]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1024, ΔBrier vs climatology +0.0270 [+0.0160, +0.0389], realised minus predicted +0.1014 [+0.0671, +0.1375]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.655 | 0.0655 | 0.2720 | -0.0020 [-0.0239, +0.0187] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0350, +0.0504] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0043, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.429 | 0.0144 | 0.1165 | +0.0040 [-0.0052, +0.0135] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0001 | 0.0048 | +0.0089 [+0.0070, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0011 | 0.0000 | +0.0318 [+0.0252, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0030 | 0.2439 | -0.0134 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.568 | 0.0607 | 0.2615 | +0.0057 [-0.0128, +0.0226] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.0398 | 0.1133 | +0.0297 [+0.0163, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.307 | 0.534 | 0.0110 | 0.0630 | +0.0069 [+0.0019, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0146, +0.1996] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.0269 | 0.1461 | +0.0292 [-0.0028, +0.0577] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_rolling (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.616] | 0.269 | 4.69 flat / 2.60 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.615] | 0.231 | 3.62 flat / 1.93 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.182, 0.530] | 2.538 [1.518, 4.048] | 1.125 [0.679, 1.824] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.179, 0.526] | 2.308 [1.344, 3.792] | 1.279 [0.740, 2.173] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 2.385 [1.394, 3.800] | 1.173 [0.683, 1.950] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.210, 0.571] | 2.538 [1.500, 4.087] | 1.231 [0.741, 2.030] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 2.115 [1.178, 3.500] | 0.981 [0.569, 1.597] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.300, 0.778] | 3.706 [1.916, 6.500] | 1.382 [0.714, 2.429] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.556 (no interval) | 4.889 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 130 | 0.457 | 0.492 | 0.0581 | +0.0133 [+0.0081, +0.0191] | -0.0018 [-0.0090, +0.0051] | 0.758 | 0.419 | no |
| 2 | 0.103 (147 of 1872 days never flag) | 114 | 0.388 | 0.474 | 0.0598 | +0.0113 [+0.0054, +0.0170] | +0.0012 [-0.0059, +0.0077] | 0.740 | 0.354 | no |
| 3 | 0.104 (147 of 1871 days never flag) | 122 | 0.435 | 0.492 | 0.0592 | +0.0115 [+0.0057, +0.0168] | +0.0052 [-0.0011, +0.0108] | 0.745 | 0.399 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 123 | 0.413 | 0.463 | 0.0585 | +0.0123 [+0.0076, +0.0169] | +0.0038 [-0.0012, +0.0082] | 0.755 | 0.375 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 116 | 0.442 | 0.526 | 0.0578 | +0.0132 [+0.0078, +0.0182] | +0.0056 [+0.0003, +0.0104] | 0.747 | 0.410 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 2.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 3.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1890 [+0.0278, +0.3226]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0949, ΔBrier vs climatology +0.0346 [+0.0224, +0.0472], realised minus predicted +0.0965 [+0.0628, +0.1328]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.557 | 0.0840 | 0.2720 | +0.0028 [-0.0195, +0.0288] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0348, +0.0503] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0011 | 0.0000 | +0.0137 [+0.0119, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0004 | 0.0200 | +0.0010 [-0.0048, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.483 | 0.0226 | 0.1165 | +0.0113 [+0.0022, +0.0224] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0010 | 0.0048 | +0.0088 [+0.0069, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0014 | 0.0000 | +0.0317 [+0.0251, +0.0383] |
| scarcity_state | 2 | 41 | 10 | 0.400 | 0.333 | 0.0393 | 0.2439 | 0.0208 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.556 | 0.0758 | 0.2615 | +0.0104 [-0.0087, +0.0314] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.0397 | 0.1133 | +0.0295 [+0.0167, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.454 | 0.0170 | 0.0630 | +0.0092 [+0.0037, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0150, +0.1971] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.0269 | 0.1461 | +0.0292 [-0.0031, +0.0578] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.4613 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.524, 0.857] | 0.375 | 6.96 flat / 3.39 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.393, 0.767] | 0.269 | 5.38 flat / 2.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.680] | 3.538 [2.559, 5.002] | 1.558 [1.070, 2.350] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.650] | 3.269 [2.139, 4.880] | 1.394 [0.947, 2.084] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.244, 0.619] | 3.423 [2.178, 5.167] | 1.442 [0.936, 2.237] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.462 [2.240, 5.222] | 1.500 [1.007, 2.229] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.763] | 3.500 [2.250, 5.287] | 1.644 [1.073, 2.487] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.412 [3.444, 8.601] | 2.015 [1.275, 3.201] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 9.889 [6.562, 18.802] | 6.000 [3.778, 12.818] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 172 | 0.571 | 0.465 | 0.0498 | +0.0216 [+0.0142, +0.0289] | +0.0065 [+0.0011, +0.0118] | 0.804 | 0.518 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 163 | 0.561 | 0.479 | 0.0544 | +0.0166 [+0.0116, +0.0221] | +0.0066 [+0.0019, +0.0117] | 0.800 | 0.512 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 163 | 0.536 | 0.454 | 0.0570 | +0.0137 [+0.0083, +0.0189] | +0.0074 [+0.0025, +0.0124] | 0.776 | 0.485 | no |
| 4 | 0.194 (147 of 1870 days never flag) | 165 | 0.543 | 0.455 | 0.0532 | +0.0176 [+0.0122, +0.0229] | +0.0092 [+0.0049, +0.0138] | 0.807 | 0.492 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 165 | 0.536 | 0.448 | 0.0539 | +0.0170 [+0.0115, +0.0226] | +0.0095 [+0.0051, +0.0144] | 0.804 | 0.484 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.512, difference +0.2031 [+0.0519, +0.3299]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0726, ΔBrier vs climatology +0.0569 [+0.0394, +0.0760], realised minus predicted +0.0315 [+0.0067, +0.0570]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.527 | 0.1692 | 0.2720 | +0.0420 [+0.0131, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0244 | 0.0159 | +0.0309 [+0.0152, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0042 | 0.0000 | +0.0136 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0129 | 0.0200 | -0.0015 [-0.0087, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.724 | 0.467 | 0.0907 | 0.1165 | +0.0286 [+0.0022, +0.0591] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0090 | 0.0048 | +0.0072 [+0.0045, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0031 | 0.0000 | +0.0316 [+0.0251, +0.0385] |
| scarcity_state | 2 | 41 | 10 | 0.700 | 0.438 | 0.1308 | 0.2439 | 0.0369 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.584 | 0.514 | 0.1733 | 0.2615 | +0.0450 [+0.0184, +0.0708] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1010 | 0.1133 | +0.0595 [+0.0350, +0.0859] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.424 | 0.0425 | 0.0630 | +0.0134 [+0.0067, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0406, +0.2112] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.0989 | 0.1461 | +0.0689 [+0.0406, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3821 | 0.2213 |

## risk_gbm+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.710] | 0.192 | 2.15 flat / 1.44 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.192 | 1.81 flat / 1.23 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.385 [0.947, 2.048] | 0.750 [0.462, 1.205] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.571, 1.528] | 0.577 [0.309, 0.987] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.385 [0.864, 2.160] | 0.885 [0.471, 1.560] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.154 [0.704, 1.824] | 0.683 [0.370, 1.174] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.600] | 1.115 [0.666, 1.783] | 0.760 [0.393, 1.333] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.556 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 77 | 0.293 | 0.532 | 0.0579 | +0.0135 [+0.0081, +0.0193] | -0.0016 [-0.0095, +0.0062] | 0.642 | 0.272 | no |
| 2 | 0.111 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0593 | +0.0117 [+0.0069, +0.0165] | +0.0017 [-0.0052, +0.0083] | 0.639 | 0.259 | no |
| 3 | 0.115 (147 of 1871 days never flag) | 76 | 0.290 | 0.526 | 0.0612 | +0.0095 [+0.0041, +0.0147] | +0.0032 [-0.0037, +0.0092] | 0.636 | 0.269 | no |
| 4 | 0.12 (147 of 1870 days never flag) | 67 | 0.268 | 0.552 | 0.0589 | +0.0119 [+0.0070, +0.0167] | +0.0034 [-0.0027, +0.0094] | 0.633 | 0.251 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 65 | 0.261 | 0.554 | 0.0593 | +0.0116 [+0.0067, +0.0163] | +0.0041 [-0.0020, +0.0098] | 0.632 | 0.244 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.714 (climatology 0.512, difference +0.2015 [+0.0462, +0.3361]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0429 [+0.0308, +0.0563], realised minus predicted +0.0594 [+0.0304, +0.0911]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0211, +0.0239] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0168 | 0.0159 | +0.0382 [+0.0294, +0.0470] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0005 | 0.0200 | +0.0014 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0395 | 0.1165 | +0.0174 [+0.0002, +0.0403] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0013 | 0.0048 | +0.0085 [+0.0065, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0019 | 0.0000 | +0.0317 [+0.0251, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0413 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.0993 | 0.2615 | +0.0138 [-0.0070, +0.0348] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0972 | 0.1133 | +0.0538 [+0.0302, +0.0783] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0133 | 0.0630 | +0.0045 [-0.0005, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0440, +0.2077] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0989 | 0.1461 | +0.0689 [+0.0408, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2001 | 0.2213 |

## risk_gbm_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.419] | 0.154 | 1.50 flat / 1.03 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.719] | 1.500 [1.000, 2.286] | 0.971 [0.556, 1.633] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.655, 1.778] | 0.644 [0.302, 1.174] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.385 [0.857, 2.227] | 0.913 [0.464, 1.638] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.231 [0.727, 1.955] | 0.760 [0.364, 1.359] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.667 [1.769, 8.500] | 3.306 [1.479, 8.002] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 82 | 0.307 | 0.524 | 0.0592 | +0.0122 [+0.0075, +0.0168] | -0.0029 [-0.0106, +0.0039] | 0.643 | 0.285 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 53 | 0.173 | 0.453 | 0.0691 | +0.0020 [-0.0047, +0.0081] | -0.0080 [-0.0168, -0.0003] | 0.578 | 0.156 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 61 | 0.181 | 0.410 | 0.0677 | +0.0029 [-0.0038, +0.0089] | -0.0034 [-0.0115, +0.0034] | 0.579 | 0.160 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0668 | +0.0040 [-0.0023, +0.0100] | -0.0044 [-0.0120, +0.0023] | 0.579 | 0.179 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0055, +0.0072] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.538 (climatology 0.512, difference +0.0253 [-0.1145, +0.1506]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1058, ΔBrier vs climatology +0.0237 [+0.0147, +0.0331], realised minus predicted +0.0905 [+0.0559, +0.1277]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0972 | 0.2720 | -0.0015 [-0.0206, +0.0159] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0253 | 0.0159 | +0.0329 [+0.0223, +0.0434] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [+0.0001, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0354 | 0.1165 | +0.0158 [+0.0016, +0.0330] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0072 | 0.0000 | +0.0304 [+0.0242, +0.0363] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.667 | 0.0151 | 0.2439 | -0.0010 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.1014 | 0.2615 | +0.0073 [-0.0104, +0.0235] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0983 | 0.1133 | +0.0339 [+0.0115, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0128 | 0.0630 | +0.0052 [+0.0001, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2030 | 0.2903 | +0.1101 [+0.0294, +0.1928] |
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
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.231 | 3.31 flat / 2.55 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.552] | 0.192 | 2.31 flat / 1.73 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.357, 0.727] | 2.423 [1.680, 3.696] | 1.740 [1.113, 2.830] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.692 [1.031, 2.706] | 1.279 [0.717, 2.203] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.167, 0.469] | 1.808 [1.130, 2.905] | 1.337 [0.742, 2.317] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.233, 0.552] | 2.231 [1.432, 3.524] | 1.712 [0.992, 2.912] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.387, 3.364] | 1.577 [0.892, 2.704] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 6.778 (no interval) | 6.028 (no interval) |

Recall with equal weight per regime: 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.043 (105 of 1873 days never flag) | 109 | 0.329 | 0.422 | 0.0606 | +0.0108 [+0.0056, +0.0158] | -0.0043 [-0.0128, +0.0035] | 0.642 | 0.292 | no |
| 2 | 0.0176 (147 of 1872 days never flag) | 72 | 0.201 | 0.389 | 0.0676 | +0.0035 [-0.0030, +0.0092] | -0.0065 [-0.0146, +0.0005] | 0.579 | 0.176 | no |
| 3 | 0.0841 (147 of 1871 days never flag) | 76 | 0.210 | 0.382 | 0.0689 | +0.0018 [-0.0055, +0.0085] | -0.0045 [-0.0134, +0.0031] | 0.579 | 0.183 | no |
| 4 | 0.0243 (147 of 1870 days never flag) | 89 | 0.225 | 0.348 | 0.0688 | +0.0020 [-0.0047, +0.0081] | -0.0065 [-0.0150, +0.0012] | 0.578 | 0.191 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 86 | 0.217 | 0.349 | 0.0690 | +0.0019 [-0.0052, +0.0083] | -0.0056 [-0.0140, +0.0017] | 0.577 | 0.185 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.586 (climatology 0.512, difference +0.0735 [-0.0503, +0.1793]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0220 [+0.0108, +0.0330], realised minus predicted +0.0748 [+0.0408, +0.1112]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1074 | 0.2720 | -0.0026 [-0.0240, +0.0179] |
| regime | 2020 | 251 | 4 | 0.250 | 0.043 | 0.0308 | 0.0159 | +0.0252 [+0.0095, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.200 | 0.0059 | 0.0200 | +0.0050 [+0.0008, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.542 | 0.0332 | 0.1165 | +0.0133 [+0.0003, +0.0294] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.083 | 0.0032 | 0.0048 | +0.0093 [+0.0075, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0063 | 0.0000 | +0.0294 [+0.0236, +0.0347] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.0662 | 0.2439 | -0.0396 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.544 | 0.1049 | 0.2615 | +0.0062 [-0.0124, +0.0237] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1022 | 0.1133 | +0.0282 [+0.0011, +0.0563] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.450 | 0.0126 | 0.0630 | +0.0040 [-0.0012, +0.0088] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3561 | 0.2903 | +0.0892 [+0.0158, +0.1596] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1296 | 0.1461 | +0.0774 [+0.0463, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2020 | 0.2213 |

## risk_logistic+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.519, 0.857] | 0.401 | 7.73 flat / 3.91 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.444, 0.783] | 0.269 | 5.77 flat / 2.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 3.962 [2.875, 5.619] | 1.990 [1.384, 2.985] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.632] | 4.154 [2.926, 5.913] | 1.875 [1.326, 2.739] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.111, 0.435] | 2.577 [1.600, 3.941] | 1.183 [0.764, 1.838] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.385 [2.345, 4.889] | 1.596 [1.116, 2.347] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.412, 0.739] | 4.423 [3.122, 6.267] | 2.048 [1.450, 2.947] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.412 [4.304, 9.715] | 2.618 [1.724, 4.051] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.222 (no interval) | 6.361 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 186 | 0.593 | 0.446 | 0.0523 | +0.0191 [+0.0123, +0.0264] | +0.0040 [-0.0014, +0.0097] | 0.801 | 0.533 | no |
| 2 | 0.131 (126 of 1872 days never flag) | 184 | 0.547 | 0.413 | 0.0557 | +0.0154 [+0.0098, +0.0216] | +0.0054 [+0.0004, +0.0108] | 0.800 | 0.484 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 128 | 0.442 | 0.477 | 0.0551 | +0.0156 [+0.0100, +0.0211] | +0.0093 [+0.0042, +0.0146] | 0.779 | 0.403 | no |
| 4 | 0.163 (126 of 1870 days never flag) | 161 | 0.529 | 0.453 | 0.0544 | +0.0164 [+0.0113, +0.0217] | +0.0079 [+0.0035, +0.0127] | 0.805 | 0.478 | no |
| 5 | 0.132 (126 of 1869 days never flag) | 199 | 0.609 | 0.422 | 0.0548 | +0.0161 [+0.0109, +0.0217] | +0.0086 [+0.0041, +0.0134] | 0.804 | 0.542 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 3.1 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1880 [+0.0711, +0.2804]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0722, ΔBrier vs climatology +0.0573 [+0.0396, +0.0772], realised minus predicted +0.0195 [-0.0043, +0.0462]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.521 | 0.1820 | 0.2720 | +0.0382 [+0.0132, +0.0653] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0359 | 0.0159 | +0.0193 [-0.0049, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.100 | 0.0182 | 0.0200 | +0.0021 [-0.0046, +0.0081] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.475 | 0.0821 | 0.1165 | +0.0236 [+0.0017, +0.0507] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.062 | 0.0107 | 0.0048 | +0.0080 [+0.0057, +0.0100] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0059 | 0.0000 | +0.0299 [+0.0235, +0.0359] |
| scarcity_state | 2 | 41 | 10 | 0.600 | 0.429 | 0.1517 | 0.2439 | 0.0066 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.608 | 0.500 | 0.1802 | 0.2615 | +0.0373 [+0.0146, +0.0618] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1046 | 0.1133 | +0.0362 [+0.0093, +0.0647] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.420 | 0.0422 | 0.0630 | +0.0129 [+0.0066, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3546 | 0.2903 | +0.0906 [+0.0222, +0.1607] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1246 | 0.1461 | +0.0764 [+0.0442, +0.1149] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.800] | 0.231 | 3.54 flat / 2.83 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.429, 0.793] | 0.231 | 3.38 flat / 2.72 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.361, 0.719] | 2.385 [1.643, 3.668] | 1.702 [1.098, 2.829] |
| lead 2 alone (pass) | 26 | 16 | 0.615 [0.429, 0.800] | 2.231 [1.500, 3.474] | 1.596 [1.000, 2.675] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.318, 0.696] | 2.462 [1.667, 3.882] | 1.913 [1.235, 3.188] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.333, 0.677] | 2.269 [1.529, 3.609] | 1.721 [1.096, 2.896] |
| lead 5 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 2.731 [1.872, 4.250] | 2.125 [1.371, 3.488] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.368, 0.810] | 1.471 [0.870, 2.417] | 0.706 [0.359, 1.333] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 7.444 (no interval) | 6.833 (no interval) |

Recall with equal weight per regime: 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0483 (105 of 1873 days never flag) | 107 | 0.321 | 0.421 | 0.0604 | +0.0110 [+0.0058, +0.0158] | -0.0041 [-0.0125, +0.0039] | 0.641 | 0.286 | no |
| 2 | 0.0436 (126 of 1872 days never flag) | 106 | 0.345 | 0.453 | 0.0606 | +0.0105 [+0.0053, +0.0154] | +0.0005 [-0.0068, +0.0073] | 0.639 | 0.312 | no |
| 3 | 0.025 (147 of 1871 days never flag) | 109 | 0.326 | 0.413 | 0.0593 | +0.0114 [+0.0062, +0.0163] | +0.0051 [-0.0016, +0.0110] | 0.638 | 0.289 | no |
| 4 | 0.092 (126 of 1870 days never flag) | 101 | 0.304 | 0.416 | 0.0601 | +0.0107 [+0.0055, +0.0154] | +0.0022 [-0.0044, +0.0083] | 0.632 | 0.270 | no |
| 5 | 0.0254 (126 of 1869 days never flag) | 115 | 0.319 | 0.383 | 0.0602 | +0.0107 [+0.0058, +0.0156] | +0.0032 [-0.0032, +0.0094] | 0.633 | 0.278 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 4.1 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 4.6 over 1041 days; regime_2021-23: 2.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1877 [+0.0672, +0.2856]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0846, ΔBrier vs climatology +0.0449 [+0.0325, +0.0588], realised minus predicted +0.0458 [+0.0174, +0.0765]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1103 | 0.2720 | -0.0019 [-0.0231, +0.0187] |
| regime | 2020 | 251 | 4 | 0.250 | 0.038 | 0.0283 | 0.0159 | +0.0266 [+0.0117, +0.0388] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0058 | 0.0200 | +0.0050 [+0.0011, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0309 | 0.1165 | +0.0125 [+0.0008, +0.0272] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.100 | 0.0030 | 0.0048 | +0.0094 [+0.0076, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0047 | 0.0000 | +0.0300 [+0.0240, +0.0358] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.0622 | 0.2439 | -0.0335 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.538 | 0.1062 | 0.2615 | +0.0061 [-0.0121, +0.0241] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1008 | 0.1133 | +0.0305 [+0.0038, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.405 | 0.0129 | 0.0630 | +0.0040 [-0.0012, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3546 | 0.2903 | +0.0906 [+0.0189, +0.1627] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.474 | 0.1246 | 0.1461 | +0.0764 [+0.0461, +0.1173] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.231 | 2.88 flat / 2.18 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.192 | 1.96 flat / 1.47 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.714] | 2.308 [1.515, 3.625] | 1.654 [0.984, 2.776] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.469] | 1.692 [1.000, 2.789] | 1.221 [0.643, 2.175] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.577 [0.880, 2.640] | 1.163 [0.571, 2.121] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.423 [0.771, 2.381] | 1.010 [0.449, 1.889] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.962 [1.192, 3.211] | 1.471 [0.801, 2.617] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.556 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.068 (105 of 1873 days never flag) | 106 | 0.329 | 0.434 | 0.0596 | +0.0118 [+0.0070, +0.0164] | -0.0033 [-0.0115, +0.0041] | 0.643 | 0.294 | no |
| 2 | 0.33 (147 of 1872 days never flag) | 73 | 0.209 | 0.397 | 0.0672 | +0.0039 [-0.0026, +0.0099] | -0.0061 [-0.0146, +0.0009] | 0.579 | 0.183 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 68 | 0.196 | 0.397 | 0.0689 | +0.0018 [-0.0060, +0.0080] | -0.0045 [-0.0131, +0.0025] | 0.579 | 0.172 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 64 | 0.196 | 0.422 | 0.0689 | +0.0019 [-0.0048, +0.0080] | -0.0065 [-0.0146, +0.0010] | 0.578 | 0.174 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 80 | 0.210 | 0.362 | 0.0687 | +0.0023 [-0.0045, +0.0084] | -0.0053 [-0.0131, +0.0019] | 0.577 | 0.181 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.512, difference +0.0823 [-0.0399, +0.1941]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0239 [+0.0136, +0.0345], realised minus predicted +0.0775 [+0.0426, +0.1148]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1080 | 0.2720 | -0.0024 [-0.0224, +0.0166] |
| regime | 2020 | 251 | 4 | 0.250 | 0.032 | 0.0294 | 0.0159 | +0.0298 [+0.0202, +0.0383] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.722 | 0.0311 | 0.1165 | +0.0168 [+0.0040, +0.0338] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0092 | 0.0000 | +0.0292 [+0.0231, +0.0347] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.0366 | 0.2439 | -0.0128 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.544 | 0.1059 | 0.2615 | +0.0074 [-0.0099, +0.0249] |
| day_type | month_end | 150 | 17 | 0.765 | 0.433 | 0.0996 | 0.1133 | +0.0352 [+0.0096, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.439 | 0.0123 | 0.0630 | +0.0047 [-0.0004, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1520] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1332 | 0.1461 | +0.0711 [+0.0381, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2040 | 0.2213 |

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.269 | 5.08 flat / 4.36 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 4.12 flat / 3.48 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.360, 0.719] | 2.692 [1.743, 4.250] | 2.048 [1.194, 3.531] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.517] | 2.462 [1.631, 3.812] | 1.846 [1.093, 3.150] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 2.423 [1.600, 3.833] | 1.846 [1.106, 3.150] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 3.423 [2.286, 5.438] | 2.846 [1.793, 4.812] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.136, 0.429] | 2.500 [1.613, 4.063] | 2.010 [1.161, 3.476] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 1.412 [0.833, 2.400] | 0.706 [0.352, 1.375] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 12.000 (no interval) | 11.250 (no interval) |

Recall with equal weight per regime: 0.382 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.148 (42 of 1873 days never flag) | 116 | 0.329 | 0.397 | 0.0632 | +0.0082 [+0.0025, +0.0141] | -0.0069 [-0.0152, +0.0007] | 0.645 | 0.288 | no |
| 2 | 0.283 (126 of 1872 days never flag) | 94 | 0.216 | 0.319 | 0.0676 | +0.0034 [-0.0039, +0.0105] | -0.0066 [-0.0149, +0.0014] | 0.578 | 0.179 | no |
| 3 | 0.092 (126 of 1871 days never flag) | 90 | 0.196 | 0.300 | 0.0669 | +0.0038 [-0.0032, +0.0106] | -0.0025 [-0.0103, +0.0048] | 0.581 | 0.159 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 118 | 0.210 | 0.246 | 0.0672 | +0.0037 [-0.0026, +0.0097] | -0.0048 [-0.0124, +0.0018] | 0.580 | 0.159 | no |
| 5 | 0.0988 (126 of 1869 days never flag) | 92 | 0.196 | 0.293 | 0.0669 | +0.0040 [-0.0026, +0.0101] | -0.0035 [-0.0110, +0.0034] | 0.581 | 0.158 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 3.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 8.2 over 1041 days; regime_2021-23: 12.1 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 3.9 over 1041 days; regime_2021-23: 5.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1292 [+0.0297, +0.2331]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1101, ΔBrier vs climatology +0.0193 [+0.0086, +0.0311], realised minus predicted +0.0574 [+0.0238, +0.0943]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.588 | 0.1014 | 0.2720 | -0.0090 [-0.0307, +0.0131] |
| regime | 2020 | 251 | 4 | 0.250 | 0.025 | 0.0608 | 0.0159 | +0.0085 [-0.0055, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0110 | 0.0200 | +0.0019 [-0.0033, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0481 | 0.1165 | +0.0239 [+0.0054, +0.0480] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.167 | 0.0055 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0325 | 0.0000 | +0.0147 [+0.0052, +0.0236] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.375 | 0.0724 | 0.2439 | -0.0134 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.575 | 0.1073 | 0.2615 | +0.0045 [-0.0167, +0.0274] |
| day_type | month_end | 150 | 17 | 0.765 | 0.382 | 0.1226 | 0.1133 | +0.0234 [-0.0109, +0.0571] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.425 | 0.0150 | 0.0630 | +0.0014 [-0.0042, +0.0066] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3534 | 0.2903 | +0.1102 [+0.0260, +0.1974] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.357 | 0.1886 | 0.1461 | +0.0706 [+0.0331, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.231 | 2.88 flat / 2.14 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.542] | 0.154 | 1.65 flat / 1.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.750] | 2.308 [1.517, 3.625] | 1.615 [0.942, 2.803] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 2.000 [1.243, 3.214] | 1.442 [0.774, 2.534] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 1.500 [0.900, 2.400] | 1.000 [0.500, 1.781] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.719, 1.667] | 0.558 [0.286, 0.991] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.294 [0.731, 2.091] | 0.529 [0.250, 0.969] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.889 (no interval) | 5.194 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.154 (105 of 1873 days never flag) | 107 | 0.336 | 0.439 | 0.0630 | +0.0084 [+0.0021, +0.0147] | -0.0067 [-0.0153, +0.0016] | 0.635 | 0.301 | no |
| 2 | 0.11 (147 of 1872 days never flag) | 82 | 0.216 | 0.366 | 0.0687 | +0.0024 [-0.0054, +0.0093] | -0.0076 [-0.0168, -0.0001] | 0.582 | 0.186 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 69 | 0.217 | 0.435 | 0.0670 | +0.0037 [-0.0037, +0.0105] | -0.0026 [-0.0108, +0.0047] | 0.585 | 0.195 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0669 | +0.0039 [-0.0034, +0.0110] | -0.0045 [-0.0128, +0.0033] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 53 | 0.188 | 0.491 | 0.0670 | +0.0039 [-0.0030, +0.0107] | -0.0036 [-0.0120, +0.0040] | 0.585 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.512, difference +0.0873 [-0.0682, +0.2241]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1051, ΔBrier vs climatology +0.0244 [+0.0124, +0.0374], realised minus predicted +0.0555 [+0.0217, +0.0899]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1199 | 0.2720 | -0.0169 [-0.0413, +0.0085] |
| regime | 2020 | 251 | 4 | 0.250 | 0.030 | 0.0469 | 0.0159 | +0.0220 [+0.0121, +0.0313] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0048, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0509 | 0.1165 | +0.0242 [+0.0051, +0.0465] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0057 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0253 | 0.0000 | +0.0214 [+0.0142, +0.0276] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.0719 | 0.2439 | -0.0114 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.606 | 0.1208 | 0.2615 | +0.0009 [-0.0223, +0.0254] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1397 | 0.1133 | +0.0244 [-0.0130, +0.0627] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.462 | 0.0159 | 0.0630 | +0.0028 [-0.0028, +0.0082] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3234 | 0.2903 | +0.0724 [-0.0002, +0.1368] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.370 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1034] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## structural_fitted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.267, 0.652] | 0.269 | 5.00 flat / 2.23 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.263, 0.652] | 0.250 | 4.42 flat / 2.08 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.238, 0.613] | 2.346 [1.500, 3.616] | 1.000 [0.592, 1.612] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 2.154 [1.304, 3.500] | 0.913 [0.509, 1.536] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.519] | 1.692 [0.947, 2.864] | 0.837 [0.426, 1.468] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.520] | 2.577 [1.559, 4.126] | 1.250 [0.695, 2.076] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.235, 0.613] | 4.000 [2.400, 6.308] | 1.837 [1.081, 3.031] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.471, 0.929] | 5.706 [3.555, 9.250] | 2.382 [1.342, 4.159] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 3.667 (no interval) | 1.944 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.328 (126 of 1873 days never flag) | 126 | 0.464 | 0.516 | 0.0529 | +0.0185 [+0.0103, +0.0272] | +0.0034 [-0.0029, +0.0101] | 0.875 | 0.429 | yes |
| 2 | 0.382 (126 of 1872 days never flag) | 111 | 0.396 | 0.495 | 0.0578 | +0.0133 [+0.0053, +0.0222] | +0.0033 [-0.0043, +0.0113] | 0.836 | 0.363 | yes |
| 3 | 0.424 (126 of 1871 days never flag) | 93 | 0.355 | 0.527 | 0.0629 | +0.0078 [-0.0008, +0.0169] | +0.0014 [-0.0069, +0.0103] | 0.794 | 0.330 | yes |
| 4 | 0.436 (126 of 1870 days never flag) | 120 | 0.384 | 0.442 | 0.0629 | +0.0080 [-0.0007, +0.0161] | -0.0005 [-0.0088, +0.0069] | 0.805 | 0.345 | yes |
| 5 | 0.251 (126 of 1869 days never flag) | 175 | 0.514 | 0.406 | 0.0633 | +0.0076 [+0.0007, +0.0143] | +0.0001 [-0.0062, +0.0061] | 0.786 | 0.454 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.625 (climatology 0.512, difference +0.1130 [-0.0225, +0.2401]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0448 [+0.0247, +0.0654], realised minus predicted -0.0192 [-0.0492, +0.0114]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.545 | 0.2944 | 0.2720 | +0.0321 [-0.0052, +0.0719] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1111 | 0.0159 | +0.0268 [+0.0154, +0.0377] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0197 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0234 | 0.0200 | +0.0009 [-0.0043, +0.0048] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0746 | 0.1165 | +0.0231 [+0.0031, +0.0482] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0193 | 0.0048 | +0.0086 [+0.0067, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0656 | 0.0000 | +0.0266 [+0.0205, +0.0326] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1007 | 0.2439 | 0.0272 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.533 | 0.2775 | 0.2615 | +0.0342 [+0.0035, +0.0688] |
| day_type | month_end | 150 | 17 | 0.765 | 0.684 | 0.1569 | 0.1133 | +0.0390 [+0.0091, +0.0689] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.444 | 0.0832 | 0.0630 | +0.0123 [+0.0044, +0.0204] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2018 | 0.2903 | +0.1343 [+0.0722, +0.1947] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1610 | 0.1461 | +0.0557 [+0.0092, +0.1014] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2826 | 0.2213 |

## structural_liquidity (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.652] | 0.269 | 5.00 flat / 2.23 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.647] | 0.250 | 4.42 flat / 2.08 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 2.346 [1.500, 3.625] | 1.000 [0.583, 1.618] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.552] | 2.154 [1.259, 3.550] | 0.913 [0.500, 1.534] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.692 [0.926, 2.864] | 0.837 [0.424, 1.466] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.520] | 2.577 [1.543, 4.150] | 1.250 [0.691, 2.078] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.613] | 4.000 [2.389, 6.228] | 1.837 [1.071, 2.959] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.706 [3.417, 9.233] | 2.382 [1.295, 4.150] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 3.667 [1.857, 7.500] | 1.944 [0.821, 4.450] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.328 (126 of 1873 days never flag) | 126 | 0.464 | 0.516 | 0.0529 | +0.0185 [+0.0104, +0.0277] | +0.0034 [-0.0029, +0.0101] | 0.875 | 0.429 | yes |
| 2 | 0.382 (126 of 1872 days never flag) | 111 | 0.396 | 0.495 | 0.0578 | +0.0133 [+0.0051, +0.0215] | +0.0033 [-0.0041, +0.0109] | 0.836 | 0.363 | yes |
| 3 | 0.424 (126 of 1871 days never flag) | 93 | 0.355 | 0.527 | 0.0629 | +0.0078 [-0.0017, +0.0166] | +0.0014 [-0.0075, +0.0100] | 0.794 | 0.330 | yes |
| 4 | 0.436 (126 of 1870 days never flag) | 120 | 0.384 | 0.442 | 0.0629 | +0.0080 [-0.0003, +0.0154] | -0.0005 [-0.0086, +0.0069] | 0.805 | 0.345 | yes |
| 5 | 0.251 (126 of 1869 days never flag) | 175 | 0.514 | 0.406 | 0.0633 | +0.0076 [+0.0008, +0.0140] | +0.0001 [-0.0057, +0.0059] | 0.786 | 0.454 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.625 (climatology 0.512, difference +0.1130 [-0.0169, +0.2386]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0448 [+0.0244, +0.0655], realised minus predicted -0.0192 [-0.0486, +0.0123]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.545 | 0.2944 | 0.2720 | +0.0321 [-0.0050, +0.0708] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1111 | 0.0159 | +0.0268 [+0.0160, +0.0373] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0197 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0234 | 0.0200 | +0.0009 [-0.0041, +0.0049] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0746 | 0.1165 | +0.0231 [+0.0027, +0.0495] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0193 | 0.0048 | +0.0086 [+0.0067, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0656 | 0.0000 | +0.0266 [+0.0207, +0.0328] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1007 | 0.2439 | 0.0272 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.533 | 0.2775 | 0.2615 | +0.0342 [+0.0029, +0.0663] |
| day_type | month_end | 150 | 17 | 0.765 | 0.684 | 0.1569 | 0.1133 | +0.0390 [+0.0091, +0.0702] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.444 | 0.0832 | 0.0630 | +0.0123 [+0.0044, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2018 | 0.2903 | +0.1343 [+0.0762, +0.1967] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1610 | 0.1461 | +0.0557 [+0.0113, +0.0996] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2826 | 0.2213 |

## structural_rolling (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.853] | 0.308 | 6.46 flat / 3.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 18 | 0.692 [0.520, 0.857] | 0.274 | 5.88 flat / 3.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 3.654 [2.303, 5.619] | 1.433 [0.803, 2.438] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.296, 0.633] | 3.577 [2.135, 5.586] | 1.519 [0.824, 2.551] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.500 [2.892, 6.950] | 2.404 [1.444, 3.938] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 4.192 [2.666, 6.421] | 1.962 [1.162, 3.132] |
| lead 5 alone (fail) | 26 | 16 | 0.615 [0.440, 0.783] | 4.231 [2.581, 6.548] | 2.058 [1.200, 3.263] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 5.412 [2.944, 9.000] | 2.382 [1.211, 4.205] |
| outside 2018-2019 | 9 | 6 | 0.667 [0.375, 0.909] | 8.444 [5.333, 16.200] | 5.278 [2.969, 11.503] |

Recall with equal weight per regime: 0.551 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.179 (126 of 1873 days never flag) | 186 | 0.650 | 0.489 | 0.0477 | +0.0237 [+0.0158, +0.0328] | +0.0086 [+0.0039, +0.0139] | 0.889 | 0.595 | no |
| 2 | 0.338 (126 of 1872 days never flag) | 170 | 0.554 | 0.453 | 0.0522 | +0.0189 [+0.0123, +0.0262] | +0.0089 [+0.0037, +0.0144] | 0.850 | 0.500 | no |
| 3 | 0.227 (126 of 1871 days never flag) | 195 | 0.565 | 0.400 | 0.0550 | +0.0156 [+0.0086, +0.0230] | +0.0093 [+0.0035, +0.0156] | 0.813 | 0.498 | no |
| 4 | 0.199 (126 of 1870 days never flag) | 186 | 0.558 | 0.414 | 0.0533 | +0.0176 [+0.0113, +0.0253] | +0.0091 [+0.0042, +0.0149] | 0.843 | 0.495 | no |
| 5 | 0.209 (126 of 1869 days never flag) | 191 | 0.587 | 0.424 | 0.0549 | +0.0160 [+0.0102, +0.0229] | +0.0085 [+0.0042, +0.0136] | 0.787 | 0.523 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 3.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.644 (climatology 0.512, difference +0.1317 [-0.0241, +0.3343]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0762, ΔBrier vs climatology +0.0533 [+0.0331, +0.0757], realised minus predicted +0.0058 [-0.0225, +0.0377]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.492 | 0.1815 | 0.2720 | +0.0385 [+0.0157, +0.0652] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0859 | 0.0159 | +0.0325 [+0.0219, +0.0421] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0181 | 0.0000 | +0.0134 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0224 | 0.0200 | +0.0007 [-0.0046, +0.0048] |
| regime | 2025-26 | 249 | 29 | 0.828 | 0.533 | 0.1463 | 0.1165 | +0.0467 [+0.0057, +0.0970] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0188 | 0.0048 | +0.0084 [+0.0064, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0575 | 0.0000 | +0.0254 [+0.0154, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.800 | 0.500 | 0.2912 | 0.2439 | 0.1056 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.500 | 0.2000 | 0.2615 | +0.0488 [+0.0251, +0.0758] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1217 | 0.1133 | +0.0417 [+0.0140, +0.0742] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.453 | 0.0672 | 0.0630 | +0.0174 [+0.0103, +0.0260] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.1889 | 0.2903 | +0.1586 [+0.0838, +0.2360] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.556 | 0.1496 | 0.1461 | +0.0591 [+0.0322, +0.0852] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0218 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3089 | 0.2213 |

