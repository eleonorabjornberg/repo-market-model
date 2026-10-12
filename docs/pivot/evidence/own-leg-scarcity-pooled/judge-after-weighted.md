# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `d0d268dc1c82…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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
| 1 | 0.0833 (105 of 1873 days never flag) | 79 | 0.307 | 0.544 | 0.0575 | +0.0139 [+0.0085, +0.0196] | -0.0012 [-0.0094, +0.0065] | 0.643 | 0.286 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 56 | 0.187 | 0.464 | 0.0686 | +0.0025 [-0.0039, +0.0081] | -0.0075 [-0.0160, -0.0005] | 0.578 | 0.170 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 55 | 0.203 | 0.509 | 0.0665 | +0.0042 [-0.0024, +0.0101] | -0.0021 [-0.0100, +0.0048] | 0.580 | 0.187 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 50 | 0.188 | 0.520 | 0.0669 | +0.0039 [-0.0029, +0.0099] | -0.0045 [-0.0124, +0.0024] | 0.579 | 0.175 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0697 | +0.0012 [-0.0054, +0.0074] | -0.0063 [-0.0137, +0.0006] | 0.577 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.523 (climatology 0.512, difference +0.0110 [-0.1321, +0.1313]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1044, ΔBrier vs climatology +0.0250 [+0.0161, +0.0339], realised minus predicted +0.0931 [+0.0564, +0.1322]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0959 | 0.2720 | +0.0016 [-0.0200, +0.0242] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0148 | 0.0159 | +0.0396 [+0.0307, +0.0483] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0028 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0390 | 0.1165 | +0.0173 [-0.0006, +0.0406] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.167 | 0.0021 | 0.0048 | +0.0090 [+0.0071, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0021 | 0.0000 | +0.0317 [+0.0250, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0240 | 0.2439 | -0.0030 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.328 | 0.586 | 0.0979 | 0.2615 | +0.0145 [-0.0059, +0.0355] |
| day_type | month_end | 150 | 17 | 0.765 | 0.542 | 0.0987 | 0.1133 | +0.0545 [+0.0304, +0.0791] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2213 | 0.2903 | +0.1280 [+0.0435, +0.2143] |
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
| lead_at_least_1 | 26 | 17 | 0.654 [0.474, 0.812] | 0.411 | 7.88 flat / 3.79 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.645] | 0.280 | 6.00 flat / 2.81 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.433, 0.789] | 5.077 [3.407, 7.410] | 2.173 [1.370, 3.322] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 5.000 [3.235, 7.369] | 2.067 [1.264, 3.197] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.769 [2.960, 7.251] | 2.058 [1.195, 3.298] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.115 [2.519, 6.334] | 1.702 [0.950, 2.763] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.565] | 4.231 [2.586, 6.471] | 1.942 [1.136, 3.100] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.826, 11.455] | 3.147 [1.920, 5.200] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.166, 0.714] | 8.778 [5.769, 16.603] | 5.000 [3.050, 10.314] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 227 | 0.679 | 0.419 | 0.0476 | +0.0238 [+0.0166, +0.0321] | +0.0087 [+0.0039, +0.0140] | 0.897 | 0.602 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 223 | 0.669 | 0.417 | 0.0601 | +0.0110 [+0.0065, +0.0153] | +0.0010 [-0.0020, +0.0040] | 0.845 | 0.594 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 204 | 0.580 | 0.392 | 0.0603 | +0.0103 [+0.0066, +0.0145] | +0.0040 [+0.0011, +0.0073] | 0.814 | 0.508 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 180 | 0.529 | 0.406 | 0.0595 | +0.0114 [+0.0070, +0.0160] | +0.0029 [+0.0003, +0.0058] | 0.820 | 0.467 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 178 | 0.493 | 0.382 | 0.0630 | +0.0079 [+0.0035, +0.0123] | +0.0004 [-0.0027, +0.0032] | 0.789 | 0.429 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0116 [-0.1004, +0.1004]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0841, ΔBrier vs climatology +0.0454 [+0.0318, +0.0607], realised minus predicted +0.0117 [-0.0184, +0.0444]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2373 | 0.2720 | +0.0573 [+0.0304, +0.0862] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1174 | 0.0159 | +0.0233 [+0.0097, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0192 | 0.0000 | +0.0131 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0328 | 0.0200 | +0.0006 [-0.0060, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.529 | 0.1153 | 0.1165 | +0.0293 [+0.0021, +0.0606] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0236 | 0.0048 | +0.0074 [+0.0049, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0654 | 0.0000 | +0.0253 [+0.0194, +0.0316] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.556 | 0.1446 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.712 | 0.418 | 0.2483 | 0.2615 | +0.0573 [+0.0324, +0.0837] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1080 | 0.1133 | +0.0597 [+0.0358, +0.0874] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.372 | 0.0861 | 0.0630 | +0.0160 [+0.0093, +0.0240] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0510, +0.2060] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.0961 | 0.1461 | +0.0685 [+0.0421, +0.0961] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3382 | 0.2213 |

## risk_gbm+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.481, 0.818] | 0.385 | 7.35 flat / 3.67 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.600] | 0.269 | 5.46 flat / 2.65 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 3.577 [2.567, 5.000] | 1.625 [1.119, 2.375] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 3.923 [2.615, 5.737] | 1.635 [1.075, 2.453] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.458] | 3.500 [2.222, 5.260] | 1.577 [0.981, 2.434] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.172, 0.517] | 3.654 [2.386, 5.400] | 1.481 [0.975, 2.167] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.692 [2.394, 5.500] | 1.606 [1.045, 2.417] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.706 [3.629, 8.833] | 2.132 [1.359, 3.321] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.444 (no interval) | 6.583 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 174 | 0.579 | 0.466 | 0.0494 | +0.0220 [+0.0148, +0.0296] | +0.0069 [+0.0018, +0.0121] | 0.805 | 0.525 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 173 | 0.511 | 0.410 | 0.0623 | +0.0087 [+0.0037, +0.0134] | -0.0013 [-0.0053, +0.0024] | 0.750 | 0.452 | no |
| 3 | 0.128 (147 of 1871 days never flag) | 157 | 0.478 | 0.420 | 0.0604 | +0.0103 [+0.0051, +0.0149] | +0.0040 [-0.0006, +0.0079] | 0.747 | 0.426 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 164 | 0.500 | 0.421 | 0.0603 | +0.0105 [+0.0055, +0.0154] | +0.0020 [-0.0015, +0.0056] | 0.759 | 0.445 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 166 | 0.507 | 0.422 | 0.0637 | +0.0072 [+0.0017, +0.0125] | -0.0003 [-0.0043, +0.0037] | 0.742 | 0.452 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.6 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 3.6 over 1041 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.530 (climatology 0.512, difference +0.0178 [-0.1007, +0.1301]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0860, ΔBrier vs climatology +0.0435 [+0.0306, +0.0581], realised minus predicted +0.0619 [+0.0330, +0.0947]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.527 | 0.1676 | 0.2720 | +0.0417 [+0.0143, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0224 | 0.0159 | +0.0323 [+0.0157, +0.0454] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.125 | 0.0152 | 0.0200 | +0.0007 [-0.0068, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.724 | 0.467 | 0.0902 | 0.1165 | +0.0284 [+0.0031, +0.0604] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.067 | 0.0098 | 0.0048 | +0.0076 [+0.0052, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0033 | 0.0000 | +0.0316 [+0.0249, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.700 | 0.500 | 0.1135 | 0.2439 | 0.0371 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.584 | 0.510 | 0.1718 | 0.2615 | +0.0457 [+0.0214, +0.0719] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1025 | 0.1133 | +0.0602 [+0.0346, +0.0877] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.424 | 0.0419 | 0.0630 | +0.0138 [+0.0076, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0438, +0.2071] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.0961 | 0.1461 | +0.0685 [+0.0418, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3822 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.524, 0.857] | 0.375 | 6.96 flat / 3.39 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.393, 0.767] | 0.269 | 5.42 flat / 2.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.680] | 3.500 [2.515, 5.000] | 1.548 [1.057, 2.338] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.650] | 3.308 [2.182, 4.913] | 1.404 [0.960, 2.097] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.244, 0.619] | 3.462 [2.214, 5.208] | 1.452 [0.949, 2.250] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.462 [2.240, 5.222] | 1.500 [1.007, 2.229] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.763] | 3.500 [2.250, 5.287] | 1.644 [1.073, 2.487] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.412 [3.444, 8.601] | 2.015 [1.275, 3.201] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 9.889 [6.562, 18.802] | 6.000 [3.778, 12.818] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 171 | 0.571 | 0.468 | 0.0499 | +0.0215 [+0.0142, +0.0286] | +0.0064 [+0.0011, +0.0117] | 0.804 | 0.519 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 164 | 0.561 | 0.476 | 0.0543 | +0.0168 [+0.0118, +0.0223] | +0.0068 [+0.0021, +0.0119] | 0.801 | 0.512 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 165 | 0.543 | 0.455 | 0.0563 | +0.0144 [+0.0089, +0.0198] | +0.0081 [+0.0032, +0.0130] | 0.778 | 0.492 | no |
| 4 | 0.194 (147 of 1870 days never flag) | 165 | 0.543 | 0.455 | 0.0530 | +0.0178 [+0.0124, +0.0232] | +0.0094 [+0.0051, +0.0141] | 0.808 | 0.492 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 165 | 0.536 | 0.448 | 0.0542 | +0.0168 [+0.0113, +0.0224] | +0.0092 [+0.0048, +0.0141] | 0.804 | 0.484 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.704 (climatology 0.512, difference +0.1918 [+0.0419, +0.3200]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0719, ΔBrier vs climatology +0.0576 [+0.0400, +0.0768], realised minus predicted +0.0312 [+0.0067, +0.0565]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.527 | 0.1692 | 0.2720 | +0.0420 [+0.0131, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0243 | 0.0159 | +0.0310 [+0.0152, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0044 | 0.0000 | +0.0135 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0131 | 0.0200 | -0.0013 [-0.0085, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.724 | 0.477 | 0.0898 | 0.1165 | +0.0279 [+0.0027, +0.0580] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0091 | 0.0048 | +0.0074 [+0.0047, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0030 | 0.0000 | +0.0316 [+0.0251, +0.0386] |
| scarcity_state | 2 | 41 | 10 | 0.700 | 0.438 | 0.1374 | 0.2439 | 0.0348 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.584 | 0.518 | 0.1724 | 0.2615 | +0.0445 [+0.0181, +0.0702] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.0999 | 0.1133 | +0.0579 [+0.0340, +0.0836] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.424 | 0.0425 | 0.0630 | +0.0134 [+0.0067, +0.0199] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2099 | 0.2903 | +0.1309 [+0.0507, +0.2140] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.0988 | 0.1461 | +0.0683 [+0.0392, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3821 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41+iorb (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 19 | 0.731 [0.560, 0.889] | 0.382 | 7.08 flat / 3.46 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.385, 0.762] | 0.269 | 5.42 flat / 2.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

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

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 177 | 0.586 | 0.463 | 0.0498 | +0.0216 [+0.0144, +0.0296] | +0.0065 [+0.0012, +0.0125] | 0.804 | 0.531 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 164 | 0.561 | 0.476 | 0.0543 | +0.0168 [+0.0118, +0.0222] | +0.0068 [+0.0020, +0.0122] | 0.801 | 0.512 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 165 | 0.543 | 0.455 | 0.0563 | +0.0144 [+0.0090, +0.0199] | +0.0081 [+0.0035, +0.0129] | 0.778 | 0.492 | no |
| 4 | 0.194 (147 of 1870 days never flag) | 165 | 0.543 | 0.455 | 0.0530 | +0.0178 [+0.0124, +0.0234] | +0.0094 [+0.0050, +0.0142] | 0.808 | 0.492 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 165 | 0.536 | 0.448 | 0.0542 | +0.0168 [+0.0115, +0.0223] | +0.0092 [+0.0047, +0.0136] | 0.804 | 0.484 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.4 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.704 (climatology 0.512, difference +0.1918 [+0.0357, +0.3321]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0711, ΔBrier vs climatology +0.0584 [+0.0404, +0.0773], realised minus predicted +0.0293 [+0.0056, +0.0553]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.531 | 0.1724 | 0.2720 | +0.0442 [+0.0158, +0.0733] |
| regime | 2020 | 251 | 4 | 0.500 | 0.182 | 0.0282 | 0.0159 | +0.0350 [+0.0212, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0042 | 0.0000 | +0.0136 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0181 | 0.0200 | -0.0056 [-0.0171, +0.0035] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.455 | 0.0895 | 0.1165 | +0.0258 [+0.0024, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0098 | 0.0048 | +0.0064 [+0.0029, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0027 | 0.0000 | +0.0316 [+0.0246, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.700 | 0.412 | 0.1425 | 0.2439 | 0.0321 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.521 | 0.1772 | 0.2615 | +0.0474 [+0.0224, +0.0736] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.0999 | 0.1133 | +0.0579 [+0.0339, +0.0839] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.420 | 0.0445 | 0.0630 | +0.0135 [+0.0073, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2099 | 0.2903 | +0.1309 [+0.0525, +0.2116] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.0988 | 0.1461 | +0.0683 [+0.0375, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3803 | 0.2213 |

## risk_gbm+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.306 | 6.42 flat / 3.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.618] | 0.269 | 5.69 flat / 2.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.387, 0.762] | 3.923 [2.333, 6.167] | 1.644 [0.917, 2.703] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.462 [2.743, 6.938] | 1.865 [1.091, 3.031] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 5.038 [3.028, 7.834] | 2.231 [1.250, 3.672] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.231 [2.484, 6.640] | 1.654 [0.898, 2.734] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 3.769 [2.178, 6.062] | 1.663 [0.913, 2.778] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.176 [4.470, 11.500] | 3.088 [1.783, 5.222] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.000 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 190 | 0.629 | 0.463 | 0.0481 | +0.0233 [+0.0166, +0.0308] | +0.0082 [+0.0034, +0.0134] | 0.888 | 0.570 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 203 | 0.626 | 0.429 | 0.0593 | +0.0118 [+0.0082, +0.0152] | +0.0018 [-0.0015, +0.0051] | 0.831 | 0.559 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 213 | 0.594 | 0.385 | 0.0590 | +0.0117 [+0.0083, +0.0156] | +0.0054 [+0.0016, +0.0093] | 0.803 | 0.519 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 183 | 0.529 | 0.399 | 0.0581 | +0.0127 [+0.0092, +0.0162] | +0.0043 [+0.0016, +0.0072] | 0.809 | 0.465 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 160 | 0.449 | 0.388 | 0.0613 | +0.0096 [+0.0060, +0.0132] | +0.0021 [-0.0009, +0.0050] | 0.780 | 0.393 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.442 | 0.2177 | 0.2720 | +0.0498 [+0.0240, +0.0771] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.1033 | 0.0159 | +0.0291 [+0.0201, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0240 | 0.0200 | +0.0027 [-0.0017, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0986 | 0.1165 | +0.0283 [+0.0050, +0.0582] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0184 | 0.0048 | +0.0084 [+0.0065, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0557 | 0.0000 | +0.0265 [+0.0204, +0.0326] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1148 | 0.2439 | 0.0329 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.466 | 0.2277 | 0.2615 | +0.0528 [+0.0291, +0.0779] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1066 | 0.1133 | +0.0588 [+0.0341, +0.0842] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.412 | 0.0741 | 0.0630 | +0.0154 [+0.0094, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0488, +0.2053] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0961 | 0.1461 | +0.0685 [+0.0420, +0.0959] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.4541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2486 | 0.2213 |

## risk_gbm+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.483, 0.818] | 0.385 | 7.38 flat / 3.49 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.278, 0.643] | 0.269 | 5.58 flat / 2.54 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.433, 0.792] | 5.000 [3.355, 7.364] | 2.154 [1.333, 3.370] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 4.885 [3.121, 7.305] | 2.019 [1.213, 3.205] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.577 [2.807, 6.966] | 1.962 [1.138, 3.154] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.923 [2.375, 6.168] | 1.596 [0.889, 2.656] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.560] | 4.077 [2.500, 6.436] | 1.827 [1.077, 3.000] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.786, 11.445] | 3.147 [1.880, 5.250] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.333 (no interval) | 4.139 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 225 | 0.679 | 0.422 | 0.0467 | +0.0247 [+0.0175, +0.0325] | +0.0096 [+0.0047, +0.0148] | 0.913 | 0.604 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 220 | 0.669 | 0.423 | 0.0591 | +0.0119 [+0.0074, +0.0163] | +0.0019 [-0.0012, +0.0048] | 0.877 | 0.596 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 199 | 0.580 | 0.402 | 0.0584 | +0.0123 [+0.0086, +0.0161] | +0.0059 [+0.0030, +0.0089] | 0.865 | 0.511 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 175 | 0.529 | 0.417 | 0.0580 | +0.0128 [+0.0089, +0.0172] | +0.0044 [+0.0020, +0.0072] | 0.865 | 0.470 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 174 | 0.493 | 0.391 | 0.0619 | +0.0090 [+0.0046, +0.0133] | +0.0015 [-0.0015, +0.0046] | 0.849 | 0.432 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0116 [-0.1013, +0.1034]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0328, +0.0605], realised minus predicted +0.0387 [+0.0087, +0.0716]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2373 | 0.2720 | +0.0573 [+0.0292, +0.0859] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1171 | 0.0159 | +0.0233 [+0.0105, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0047 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0028 | 0.0200 | +0.0037 [-0.0003, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.545 | 0.0987 | 0.1165 | +0.0318 [+0.0046, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0021 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0654 | 0.0000 | +0.0253 [+0.0194, +0.0314] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.556 | 0.1446 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.712 | 0.418 | 0.2483 | 0.2615 | +0.0573 [+0.0318, +0.0820] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1060 | 0.1133 | +0.0598 [+0.0356, +0.0871] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.376 | 0.0723 | 0.0630 | +0.0170 [+0.0102, +0.0242] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0472, +0.2084] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.0961 | 0.1461 | +0.0685 [+0.0413, +0.0938] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3382 | 0.2213 |

## risk_gbm+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.438, 0.800] | 0.385 | 7.46 flat / 3.66 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.243, 0.613] | 0.278 | 5.96 flat / 2.89 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.400, 0.762] | 4.462 [3.034, 6.625] | 1.933 [1.262, 2.958] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.226, 0.556] | 4.346 [2.875, 6.500] | 1.712 [1.129, 2.584] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.692 [2.966, 7.250] | 2.029 [1.250, 3.228] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.385 [2.812, 6.715] | 1.894 [1.144, 3.023] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.385 [2.793, 6.721] | 2.067 [1.243, 3.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.647 [4.050, 10.778] | 2.765 [1.566, 4.844] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 9.000 (no interval) | 5.361 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 209 | 0.664 | 0.445 | 0.0481 | +0.0233 [+0.0177, +0.0293] | +0.0082 [+0.0032, +0.0134] | 0.905 | 0.597 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 199 | 0.619 | 0.432 | 0.0603 | +0.0107 [+0.0075, +0.0139] | +0.0007 [-0.0031, +0.0044] | 0.852 | 0.554 | no |
| 3 | 0.125 (147 of 1871 days never flag) | 202 | 0.580 | 0.396 | 0.0595 | +0.0111 [+0.0077, +0.0150] | +0.0048 [+0.0008, +0.0089] | 0.820 | 0.509 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 186 | 0.522 | 0.387 | 0.0593 | +0.0115 [+0.0079, +0.0153] | +0.0031 [-0.0004, +0.0065] | 0.832 | 0.456 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 183 | 0.500 | 0.377 | 0.0624 | +0.0085 [+0.0048, +0.0120] | +0.0010 [-0.0030, +0.0045] | 0.796 | 0.434 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.518 (climatology 0.512, difference +0.0053 [-0.1142, +0.1111]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0297, +0.0515], realised minus predicted +0.0535 [+0.0202, +0.0884]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.466 | 0.1666 | 0.2720 | +0.0429 [+0.0257, +0.0603] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0661 | 0.0159 | +0.0366 [+0.0281, +0.0449] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0099 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0178 | 0.0200 | +0.0030 [-0.0012, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.516 | 0.0771 | 0.1165 | +0.0299 [+0.0055, +0.0612] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.143 | 0.0128 | 0.0048 | +0.0086 [+0.0066, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0337 | 0.0000 | +0.0301 [+0.0237, +0.0363] |
| scarcity_state | 2 | 41 | 10 | 0.400 | 0.500 | 0.0843 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.456 | 0.1731 | 0.2615 | +0.0505 [+0.0329, +0.0687] |
| day_type | month_end | 150 | 17 | 0.824 | 0.538 | 0.1034 | 0.1133 | +0.0575 [+0.0328, +0.0848] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.405 | 0.0494 | 0.0630 | +0.0156 [+0.0111, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0496, +0.2077] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0961 | 0.1461 | +0.0685 [+0.0414, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.4080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2173 | 0.2213 |

## risk_gbm+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.437, 0.808] | 0.278 | 5.92 flat / 2.77 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.643] | 0.269 | 4.65 flat / 2.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.389, 0.783] | 4.077 [2.514, 6.401] | 1.750 [0.993, 2.903] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.630] | 4.923 [2.966, 7.680] | 2.135 [1.154, 3.562] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.259, 0.630] | 4.423 [2.513, 7.106] | 2.000 [1.041, 3.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.226, 0.583] | 3.731 [1.895, 6.231] | 1.769 [0.796, 3.219] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.577] | 3.846 [2.000, 6.381] | 1.856 [0.848, 3.329] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.647 [4.909, 11.833] | 3.309 [1.981, 5.614] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.416 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 190 | 0.600 | 0.442 | 0.0604 | +0.0110 [+0.0011, +0.0208] | -0.0041 [-0.0123, +0.0042] | 0.873 | 0.539 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 210 | 0.590 | 0.390 | 0.0716 | -0.0005 [-0.0089, +0.0076] | -0.0105 [-0.0182, -0.0033] | 0.816 | 0.516 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 188 | 0.529 | 0.388 | 0.0723 | -0.0017 [-0.0111, +0.0062] | -0.0080 [-0.0169, -0.0004] | 0.798 | 0.463 | yes |
| 4 | 0.655 (147 of 1870 days never flag) | 160 | 0.457 | 0.394 | 0.0703 | +0.0005 [-0.0068, +0.0069] | -0.0079 [-0.0145, -0.0022] | 0.814 | 0.401 | no |
| 5 | 0.446 (147 of 1869 days never flag) | 161 | 0.442 | 0.379 | 0.0729 | -0.0019 [-0.0084, +0.0038] | -0.0095 [-0.0154, -0.0042] | 0.775 | 0.384 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.3118 | 0.2720 | +0.0131 [-0.0304, +0.0570] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0240, +0.0127] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0688 | 0.1165 | +0.0286 [+0.0036, +0.0581] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0084 | 0.0048 | +0.0080 [+0.0061, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1098 | 0.0000 | +0.0120 [+0.0062, +0.0178] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1009 | 0.2439 | 0.0281 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.444 | 0.3114 | 0.2615 | +0.0154 [-0.0232, +0.0525] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1094 | 0.1133 | +0.0570 [+0.0317, +0.0837] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1025 | 0.0630 | +0.0012 [-0.0092, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0503, +0.2063] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0947] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.778] | 0.282 | 6.00 flat / 2.83 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.269 | 4.69 flat / 2.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.375, 0.778] | 4.000 [2.370, 6.250] | 1.673 [0.916, 2.800] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.577] | 4.923 [3.000, 7.625] | 2.163 [1.176, 3.630] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.613] | 4.385 [2.464, 7.000] | 1.962 [0.954, 3.408] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.769 [1.929, 6.250] | 1.779 [0.780, 3.188] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.923 [2.102, 6.418] | 1.933 [0.904, 3.414] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 7.647 [4.863, 12.333] | 3.309 [1.883, 5.773] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.889 [1.285, 6.500] | 1.917 [0.659, 4.917] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 187 | 0.593 | 0.444 | 0.0609 | +0.0105 [+0.0004, +0.0200] | -0.0046 [-0.0129, +0.0032] | 0.870 | 0.533 | no |
| 2 | 0.503 (147 of 1872 days never flag) | 209 | 0.583 | 0.388 | 0.0718 | -0.0007 [-0.0093, +0.0071] | -0.0107 [-0.0191, -0.0034] | 0.814 | 0.509 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 187 | 0.529 | 0.390 | 0.0723 | -0.0016 [-0.0115, +0.0067] | -0.0079 [-0.0174, -0.0001] | 0.801 | 0.463 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 163 | 0.471 | 0.399 | 0.0704 | +0.0004 [-0.0070, +0.0074] | -0.0081 [-0.0149, -0.0018] | 0.818 | 0.414 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 163 | 0.442 | 0.374 | 0.0727 | -0.0017 [-0.0081, +0.0042] | -0.0093 [-0.0155, -0.0038] | 0.779 | 0.383 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.424 | 0.3133 | 0.2720 | +0.0133 [-0.0301, +0.0543] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1939 | 0.0159 | -0.0054 [-0.0268, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0119 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0050 | 0.0200 | +0.0005 [-0.0055, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0684 | 0.1165 | +0.0281 [+0.0054, +0.0560] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0077 [+0.0056, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1096 | 0.0000 | +0.0121 [+0.0066, +0.0181] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1248 | 0.2439 | 0.0259 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.664 | 0.444 | 0.3121 | 0.2615 | +0.0142 [-0.0235, +0.0495] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1068 | 0.1133 | +0.0547 [+0.0325, +0.0782] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1031 | 0.0630 | +0.0008 [-0.0095, +0.0108] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0470, +0.2071] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.433, 0.792] | 0.286 | 6.08 flat / 2.94 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.704] | 0.269 | 5.12 flat / 2.45 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.381, 0.765] | 4.077 [2.424, 6.412] | 1.750 [0.982, 2.920] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.350, 0.731] | 4.385 [2.500, 7.042] | 1.990 [1.044, 3.393] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.538 [2.613, 7.228] | 2.115 [1.156, 3.542] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.962 [2.239, 6.348] | 1.933 [1.008, 3.299] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.769 [2.040, 6.239] | 1.865 [0.938, 3.313] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.118 [4.429, 11.468] | 3.103 [1.750, 5.232] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 4.111 [2.071, 9.250] | 2.639 [1.087, 6.450] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 190 | 0.600 | 0.442 | 0.0604 | +0.0110 [+0.0017, +0.0209] | -0.0041 [-0.0122, +0.0039] | 0.873 | 0.539 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 200 | 0.619 | 0.430 | 0.0649 | +0.0062 [-0.0032, +0.0150] | -0.0038 [-0.0127, +0.0044] | 0.839 | 0.553 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 195 | 0.558 | 0.395 | 0.0687 | +0.0020 [-0.0082, +0.0112] | -0.0043 [-0.0139, +0.0044] | 0.827 | 0.490 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 171 | 0.493 | 0.398 | 0.0650 | +0.0059 [-0.0015, +0.0131] | -0.0026 [-0.0097, +0.0041] | 0.843 | 0.433 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 167 | 0.500 | 0.413 | 0.0652 | +0.0057 [-0.0010, +0.0121] | -0.0018 [-0.0081, +0.0043] | 0.828 | 0.443 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0145, +0.2668]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0818, ΔBrier vs climatology +0.0477 [+0.0295, +0.0684], realised minus predicted -0.0171 [-0.0463, +0.0160]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.3118 | 0.2720 | +0.0131 [-0.0284, +0.0549] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0226, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0688 | 0.1165 | +0.0286 [+0.0048, +0.0604] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0084 | 0.0048 | +0.0080 [+0.0060, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1098 | 0.0000 | +0.0120 [+0.0065, +0.0174] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1009 | 0.2439 | 0.0281 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.444 | 0.3114 | 0.2615 | +0.0154 [-0.0210, +0.0532] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1094 | 0.1133 | +0.0570 [+0.0330, +0.0845] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1025 | 0.0630 | +0.0012 [-0.0087, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0471, +0.2088] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0961 | 0.1461 | +0.0685 [+0.0416, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.269 | 5.73 flat / 2.74 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.310, 0.708] | 0.269 | 4.81 flat / 2.31 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.393, 0.778] | 4.000 [2.345, 6.305] | 1.673 [0.911, 2.816] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.737] | 4.423 [2.524, 7.106] | 1.981 [1.058, 3.342] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.282, 0.667] | 4.385 [2.451, 7.167] | 2.019 [1.043, 3.486] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.808 [2.074, 6.294] | 1.856 [0.909, 3.284] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.615 [1.937, 6.034] | 1.827 [0.884, 3.273] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.556, 1.000] | 7.118 [4.417, 11.445] | 3.103 [1.776, 5.417] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 187 | 0.593 | 0.444 | 0.0609 | +0.0105 [+0.0011, +0.0201] | -0.0046 [-0.0128, +0.0035] | 0.870 | 0.533 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 203 | 0.633 | 0.433 | 0.0652 | +0.0059 [-0.0035, +0.0144] | -0.0041 [-0.0129, +0.0041] | 0.838 | 0.567 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 191 | 0.558 | 0.403 | 0.0688 | +0.0018 [-0.0087, +0.0106] | -0.0045 [-0.0145, +0.0041] | 0.823 | 0.492 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 171 | 0.522 | 0.421 | 0.0643 | +0.0066 [-0.0014, +0.0139] | -0.0019 [-0.0096, +0.0054] | 0.844 | 0.465 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 162 | 0.493 | 0.420 | 0.0647 | +0.0062 [-0.0005, +0.0128] | -0.0013 [-0.0080, +0.0051] | 0.827 | 0.438 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1893 [+0.0390, +0.3183]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0475 [+0.0293, +0.0674], realised minus predicted -0.0179 [-0.0488, +0.0162]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.424 | 0.3133 | 0.2720 | +0.0133 [-0.0292, +0.0558] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1939 | 0.0159 | -0.0054 [-0.0262, +0.0109] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0119 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0050 | 0.0200 | +0.0005 [-0.0050, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0684 | 0.1165 | +0.0281 [+0.0049, +0.0583] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0077 [+0.0056, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1096 | 0.0000 | +0.0121 [+0.0063, +0.0176] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1248 | 0.2439 | 0.0259 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.664 | 0.444 | 0.3121 | 0.2615 | +0.0142 [-0.0216, +0.0515] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1068 | 0.1133 | +0.0547 [+0.0307, +0.0797] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1031 | 0.0630 | +0.0008 [-0.0095, +0.0112] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0496, +0.2096] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0979] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_gbm+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.760] | 0.306 | 6.42 flat / 3.10 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.269 | 5.00 flat / 2.34 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.760] | 4.231 [2.529, 6.465] | 1.817 [1.033, 2.868] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.238, 0.609] | 5.038 [3.067, 7.828] | 2.231 [1.242, 3.717] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.609] | 4.346 [2.310, 7.000] | 1.962 [0.952, 3.422] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.962 [2.117, 6.421] | 1.885 [0.890, 3.329] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 4.038 [2.182, 6.500] | 1.962 [0.942, 3.442] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.647 [4.944, 12.251] | 3.309 [1.943, 5.662] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.111 (no interval) | 2.694 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 196 | 0.614 | 0.439 | 0.0559 | +0.0155 [+0.0082, +0.0238] | +0.0005 [-0.0059, +0.0070] | 0.849 | 0.551 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 212 | 0.583 | 0.382 | 0.0697 | +0.0013 [-0.0044, +0.0070] | -0.0087 [-0.0144, -0.0031] | 0.775 | 0.507 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 187 | 0.536 | 0.396 | 0.0697 | +0.0010 [-0.0038, +0.0057] | -0.0053 [-0.0103, -0.0005] | 0.728 | 0.471 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 168 | 0.471 | 0.387 | 0.0692 | +0.0016 [-0.0031, +0.0061] | -0.0069 [-0.0115, -0.0025] | 0.752 | 0.412 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 166 | 0.442 | 0.367 | 0.0729 | -0.0020 [-0.0072, +0.0029] | -0.0095 [-0.0151, -0.0043] | 0.717 | 0.381 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.419 | 0.2828 | 0.2720 | +0.0391 [+0.0075, +0.0714] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0137, +0.0099] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0086, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0022, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0675 | 0.1165 | +0.0265 [+0.0030, +0.0554] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0218 | 0.0048 | +0.0076 [+0.0058, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1294 | 0.0000 | +0.0062 [+0.0011, +0.0119] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0781 | 0.2439 | 0.0070 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.688 | 0.441 | 0.2860 | 0.2615 | +0.0397 [+0.0114, +0.0682] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1101 | 0.1133 | +0.0563 [+0.0319, +0.0831] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.386 | 0.1068 | 0.0630 | +0.0066 [-0.0009, +0.0146] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0462, +0.2080] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0961 | 0.1461 | +0.0685 [+0.0402, +0.0966] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2839 | 0.2213 |

## risk_gbm+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.424, 0.794] | 0.385 | 7.27 flat / 3.88 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.269 | 5.77 flat / 3.11 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.424, 0.794] | 4.269 [2.677, 6.468] | 1.827 [1.070, 2.902] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 5.000 [3.038, 7.667] | 2.221 [1.249, 3.625] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.308 [2.366, 6.900] | 1.923 [0.948, 3.313] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 4.731 [2.709, 7.560] | 2.596 [1.269, 4.530] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 4.192 [2.379, 6.706] | 2.115 [1.103, 3.608] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.647 [5.035, 11.824] | 3.309 [2.000, 5.445] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.556 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 197 | 0.614 | 0.437 | 0.0564 | +0.0150 [+0.0075, +0.0232] | -0.0000 [-0.0057, +0.0060] | 0.842 | 0.550 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 210 | 0.576 | 0.381 | 0.0699 | +0.0012 [-0.0047, +0.0065] | -0.0088 [-0.0146, -0.0033] | 0.768 | 0.501 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 185 | 0.529 | 0.395 | 0.0696 | +0.0011 [-0.0040, +0.0060] | -0.0052 [-0.0103, -0.0004] | 0.732 | 0.464 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 189 | 0.478 | 0.349 | 0.0694 | +0.0014 [-0.0034, +0.0066] | -0.0070 [-0.0115, -0.0024] | 0.760 | 0.407 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 171 | 0.449 | 0.363 | 0.0727 | -0.0018 [-0.0071, +0.0032] | -0.0093 [-0.0150, -0.0038] | 0.719 | 0.386 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.500 (climatology 0.512, difference -0.0122 [-0.1225, +0.0832]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0944, ΔBrier vs climatology +0.0351 [+0.0216, +0.0503], realised minus predicted -0.0146 [-0.0480, +0.0223]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2844 | 0.2720 | +0.0393 [+0.0063, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2020 | 0.0159 | -0.0034 [-0.0161, +0.0083] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0363 | 0.0000 | +0.0103 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0095 | 0.0200 | +0.0005 [-0.0052, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0671 | 0.1165 | +0.0259 [+0.0045, +0.0515] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0211 | 0.0048 | +0.0073 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1291 | 0.0000 | +0.0063 [+0.0010, +0.0120] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1019 | 0.2439 | 0.0047 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.680 | 0.438 | 0.2866 | 0.2615 | +0.0385 [+0.0083, +0.0682] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1076 | 0.1133 | +0.0540 [+0.0316, +0.0791] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.384 | 0.1074 | 0.0630 | +0.0062 [-0.0014, +0.0143] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0518, +0.2102] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0988 | 0.1461 | +0.0683 [+0.0379, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.790] | 0.293 | 6.19 flat / 3.00 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.294, 0.686] | 0.269 | 5.23 flat / 2.53 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.375, 0.762] | 4.231 [2.548, 6.625] | 1.817 [1.030, 3.011] |
| lead 2 alone (fail) | 26 | 14 | 0.538 [0.343, 0.731] | 4.462 [2.583, 7.160] | 2.048 [1.096, 3.513] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.423 [2.555, 7.106] | 2.038 [1.101, 3.463] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.318, 6.549] | 1.962 [1.036, 3.393] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.277, 6.543] | 2.029 [1.054, 3.519] |
| inside 2018-2019 | 17 | 13 | 0.765 (no interval) | 7.118 (no interval) | 3.103 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 2.806 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 196 | 0.614 | 0.439 | 0.0559 | +0.0155 [+0.0082, +0.0237] | +0.0005 [-0.0056, +0.0068] | 0.849 | 0.551 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 201 | 0.612 | 0.423 | 0.0622 | +0.0088 [+0.0023, +0.0156] | -0.0012 [-0.0077, +0.0056] | 0.805 | 0.545 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 193 | 0.565 | 0.404 | 0.0655 | +0.0052 [-0.0004, +0.0112] | -0.0011 [-0.0068, +0.0049] | 0.773 | 0.499 | no |
| 4 | 0.396 (147 of 1870 days never flag) | 174 | 0.500 | 0.397 | 0.0636 | +0.0073 [+0.0014, +0.0130] | -0.0012 [-0.0070, +0.0047] | 0.794 | 0.439 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 175 | 0.507 | 0.400 | 0.0649 | +0.0060 [+0.0000, +0.0119] | -0.0015 [-0.0079, +0.0049] | 0.783 | 0.447 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0192, +0.2720]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0837, ΔBrier vs climatology +0.0458 [+0.0278, +0.0657], realised minus predicted -0.0358 [-0.0675, -0.0024]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.419 | 0.2828 | 0.2720 | +0.0391 [+0.0085, +0.0728] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0133, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0087, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0025, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0675 | 0.1165 | +0.0265 [+0.0041, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0218 | 0.0048 | +0.0076 [+0.0057, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1294 | 0.0000 | +0.0062 [+0.0009, +0.0119] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0781 | 0.2439 | 0.0070 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.688 | 0.441 | 0.2860 | 0.2615 | +0.0397 [+0.0117, +0.0686] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1101 | 0.1133 | +0.0563 [+0.0325, +0.0810] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.386 | 0.1068 | 0.0630 | +0.0066 [-0.0006, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0469, +0.2050] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0961 | 0.1461 | +0.0685 [+0.0412, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2839 | 0.2213 |

## risk_gbm+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.793] | 0.295 | 6.23 flat / 3.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.304, 0.708] | 0.269 | 5.27 flat / 2.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.423, 0.793] | 4.269 [2.675, 6.786] | 1.827 [1.075, 3.036] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.741] | 4.385 [2.555, 7.077] | 1.971 [1.062, 3.321] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.300, 0.710] | 4.462 [2.571, 7.279] | 2.106 [1.125, 3.583] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.038 [2.304, 6.543] | 1.971 [1.029, 3.394] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.808 [2.178, 6.158] | 1.933 [1.000, 3.337] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.118 [4.444, 11.333] | 3.103 [1.766, 5.401] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 3.028 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 197 | 0.614 | 0.437 | 0.0564 | +0.0150 [+0.0080, +0.0231] | -0.0000 [-0.0060, +0.0060] | 0.842 | 0.550 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 200 | 0.619 | 0.430 | 0.0626 | +0.0085 [+0.0022, +0.0151] | -0.0015 [-0.0081, +0.0052] | 0.805 | 0.553 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 195 | 0.572 | 0.405 | 0.0656 | +0.0050 [-0.0009, +0.0111] | -0.0013 [-0.0073, +0.0050] | 0.769 | 0.506 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 177 | 0.522 | 0.407 | 0.0629 | +0.0080 [+0.0021, +0.0145] | -0.0005 [-0.0065, +0.0060] | 0.794 | 0.461 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 168 | 0.500 | 0.411 | 0.0644 | +0.0065 [+0.0004, +0.0125] | -0.0010 [-0.0074, +0.0054] | 0.779 | 0.443 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1893 [+0.0398, +0.3290]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0839, ΔBrier vs climatology +0.0456 [+0.0277, +0.0660], realised minus predicted -0.0365 [-0.0667, -0.0047]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2844 | 0.2720 | +0.0393 [+0.0072, +0.0745] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2020 | 0.0159 | -0.0034 [-0.0161, +0.0077] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0363 | 0.0000 | +0.0103 [+0.0086, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0095 | 0.0200 | +0.0005 [-0.0054, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0671 | 0.1165 | +0.0259 [+0.0048, +0.0531] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0211 | 0.0048 | +0.0073 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1291 | 0.0000 | +0.0063 [+0.0009, +0.0118] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1019 | 0.2439 | 0.0047 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.680 | 0.438 | 0.2866 | 0.2615 | +0.0385 [+0.0114, +0.0677] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1076 | 0.1133 | +0.0540 [+0.0323, +0.0775] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.384 | 0.1074 | 0.0630 | +0.0062 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0513, +0.2113] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0972] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.735] | 0.297 | 6.27 flat / 3.15 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.643] | 0.269 | 4.77 flat / 2.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.308, 0.704] | 4.731 [2.828, 7.500] | 2.346 [1.326, 3.929] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 5.231 [3.273, 8.173] | 2.298 [1.316, 3.793] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.385 [2.433, 7.126] | 1.981 [1.000, 3.511] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 3.769 [1.963, 6.391] | 1.779 [0.808, 3.270] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.615] | 4.577 [2.652, 7.421] | 2.077 [1.073, 3.661] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.882] | 7.824 [4.856, 12.500] | 3.735 [2.152, 6.398] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 3.333 [1.444, 8.000] | 2.056 [0.797, 5.572] |

Recall with equal weight per regime: 0.387 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 205 | 0.586 | 0.400 | 0.0560 | +0.0154 [+0.0061, +0.0247] | +0.0003 [-0.0079, +0.0078] | 0.919 | 0.515 | yes |
| 2 | 0.5 (147 of 1872 days never flag) | 222 | 0.619 | 0.387 | 0.0663 | +0.0047 [-0.0044, +0.0130] | -0.0053 [-0.0139, +0.0020] | 0.880 | 0.540 | yes |
| 3 | 0.56 (147 of 1871 days never flag) | 188 | 0.536 | 0.394 | 0.0659 | +0.0048 [-0.0055, +0.0137] | -0.0015 [-0.0115, +0.0072] | 0.892 | 0.470 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 160 | 0.449 | 0.388 | 0.0656 | +0.0052 [-0.0021, +0.0113] | -0.0033 [-0.0099, +0.0027] | 0.847 | 0.393 | no |
| 5 | 0.446 (147 of 1869 days never flag) | 196 | 0.558 | 0.393 | 0.0728 | -0.0019 [-0.0108, +0.0062] | -0.0094 [-0.0182, -0.0017] | 0.817 | 0.489 | no |

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
| regime | 2018-19 | 375 | 102 | 0.716 | 0.384 | 0.3126 | 0.2720 | +0.0169 [-0.0246, +0.0564] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0837 | 0.0159 | +0.0174 [-0.0067, +0.0366] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0006 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0000, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0778 | 0.1165 | +0.0277 [+0.0050, +0.0578] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0030 | 0.0048 | +0.0090 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0031 | 0.0000 | +0.0317 [+0.0253, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0494 | 0.2439 | 0.0189 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.402 | 0.3198 | 0.2615 | +0.0183 [-0.0178, +0.0529] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1059 | 0.1133 | +0.0577 [+0.0326, +0.0840] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.347 | 0.0796 | 0.0630 | +0.0063 [-0.0035, +0.0156] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0490, +0.2079] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.692] | 0.274 | 5.85 flat / 2.93 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.611] | 0.269 | 4.77 flat / 2.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.692] | 4.538 [2.730, 7.002] | 2.125 [1.173, 3.515] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.885 [2.956, 7.467] | 2.183 [1.167, 3.597] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.308 [2.399, 6.852] | 1.923 [0.926, 3.290] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.808 [2.038, 6.232] | 1.788 [0.812, 3.125] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.260, 6.579] | 2.029 [1.015, 3.530] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.529 [4.737, 11.938] | 3.441 [2.014, 5.887] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 200 | 0.586 | 0.410 | 0.0569 | +0.0145 [+0.0051, +0.0240] | -0.0006 [-0.0089, +0.0072] | 0.917 | 0.518 | yes |
| 2 | 0.503 (147 of 1872 days never flag) | 207 | 0.576 | 0.386 | 0.0667 | +0.0044 [-0.0045, +0.0123] | -0.0057 [-0.0144, +0.0019] | 0.877 | 0.502 | no |
| 3 | 0.618 (147 of 1871 days never flag) | 185 | 0.529 | 0.395 | 0.0658 | +0.0049 [-0.0053, +0.0135] | -0.0014 [-0.0115, +0.0068] | 0.896 | 0.464 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 163 | 0.464 | 0.393 | 0.0631 | +0.0078 [+0.0010, +0.0140] | -0.0007 [-0.0068, +0.0048] | 0.884 | 0.407 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 168 | 0.449 | 0.369 | 0.0669 | +0.0040 [-0.0019, +0.0095] | -0.0035 [-0.0096, +0.0020] | 0.819 | 0.388 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.499 (climatology 0.512, difference -0.0135 [-0.1307, +0.0836]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0861, ΔBrier vs climatology +0.0434 [+0.0291, +0.0589], realised minus predicted +0.0215 [-0.0098, +0.0565]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.396 | 0.3148 | 0.2720 | +0.0153 [-0.0252, +0.0560] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0864 | 0.0159 | +0.0156 [-0.0099, +0.0360] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0007 | 0.0000 | +0.0137 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0014 | 0.0200 | +0.0016 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0775 | 0.1165 | +0.0273 [+0.0067, +0.0557] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0087 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0028 | 0.0000 | +0.0317 [+0.0247, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0732 | 0.2439 | 0.0166 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.410 | 0.3213 | 0.2615 | +0.0156 [-0.0205, +0.0507] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1035 | 0.1133 | +0.0558 [+0.0329, +0.0823] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0805 | 0.0630 | +0.0054 [-0.0048, +0.0149] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2099 | 0.2903 | +0.1309 [+0.0542, +0.2064] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.0988 | 0.1461 | +0.0683 [+0.0383, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.351, 0.739] | 0.286 | 6.08 flat / 3.05 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.263, 0.667] | 0.269 | 4.62 flat / 2.17 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.706] | 4.731 [2.833, 7.501] | 2.346 [1.274, 3.917] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.320, 0.696] | 4.269 [2.483, 6.915] | 1.990 [1.069, 3.381] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.154 [2.390, 6.765] | 1.952 [1.040, 3.329] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.885 [2.173, 6.349] | 1.856 [0.963, 3.196] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.769 [2.071, 6.261] | 1.837 [0.906, 3.224] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.900] | 7.471 [4.615, 12.385] | 3.529 [1.966, 6.313] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.444 (no interval) | 2.139 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 205 | 0.586 | 0.400 | 0.0560 | +0.0154 [+0.0059, +0.0245] | +0.0003 [-0.0079, +0.0078] | 0.919 | 0.515 | yes |
| 2 | 0.5 (147 of 1872 days never flag) | 195 | 0.604 | 0.431 | 0.0603 | +0.0108 [+0.0015, +0.0189] | +0.0008 [-0.0086, +0.0089] | 0.892 | 0.540 | yes |
| 3 | 0.53 (147 of 1871 days never flag) | 185 | 0.558 | 0.416 | 0.0631 | +0.0076 [-0.0034, +0.0166] | +0.0013 [-0.0096, +0.0102] | 0.899 | 0.496 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 169 | 0.493 | 0.402 | 0.0609 | +0.0099 [+0.0027, +0.0165] | +0.0014 [-0.0054, +0.0082] | 0.868 | 0.434 | no |
| 5 | 0.455 (147 of 1869 days never flag) | 169 | 0.514 | 0.420 | 0.0658 | +0.0052 [-0.0041, +0.0131] | -0.0024 [-0.0106, +0.0053] | 0.856 | 0.458 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.716 | 0.384 | 0.3126 | 0.2720 | +0.0169 [-0.0237, +0.0566] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0837 | 0.0159 | +0.0174 [-0.0071, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0003, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0778 | 0.1165 | +0.0277 [+0.0047, +0.0555] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0030 | 0.0048 | +0.0090 [+0.0072, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0031 | 0.0000 | +0.0317 [+0.0252, +0.0385] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0494 | 0.2439 | 0.0189 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.402 | 0.3198 | 0.2615 | +0.0183 [-0.0183, +0.0531] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1059 | 0.1133 | +0.0577 [+0.0329, +0.0831] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.347 | 0.0796 | 0.0630 | +0.0063 [-0.0039, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0483, +0.2074] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.0961 | 0.1461 | +0.0685 [+0.0427, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.727] | 0.269 | 5.62 flat / 2.80 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.708] | 0.269 | 5.08 flat / 2.39 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.308, 0.692] | 4.538 [2.576, 7.143] | 2.125 [1.129, 3.538] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 4.000 [2.185, 6.475] | 1.856 [0.938, 3.167] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.308, 0.692] | 4.615 [2.608, 7.320] | 2.154 [1.157, 3.611] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.808 [2.091, 6.269] | 1.827 [0.899, 3.222] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.692 [2.026, 6.065] | 1.846 [0.913, 3.278] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.176 [4.333, 11.670] | 3.235 [1.818, 5.650] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 200 | 0.586 | 0.410 | 0.0569 | +0.0145 [+0.0051, +0.0242] | -0.0006 [-0.0089, +0.0074] | 0.917 | 0.518 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 186 | 0.590 | 0.441 | 0.0608 | +0.0103 [+0.0013, +0.0185] | +0.0003 [-0.0086, +0.0084] | 0.893 | 0.530 | yes |
| 3 | 0.599 (147 of 1871 days never flag) | 204 | 0.609 | 0.412 | 0.0634 | +0.0073 [-0.0035, +0.0171] | +0.0010 [-0.0095, +0.0107] | 0.898 | 0.539 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 171 | 0.522 | 0.421 | 0.0577 | +0.0131 [+0.0060, +0.0197] | +0.0047 [-0.0026, +0.0112] | 0.895 | 0.465 | yes |
| 5 | 0.449 (147 of 1869 days never flag) | 165 | 0.500 | 0.418 | 0.0595 | +0.0114 [+0.0053, +0.0182] | +0.0039 [-0.0025, +0.0106] | 0.856 | 0.445 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1899 [+0.0427, +0.3224]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0774, ΔBrier vs climatology +0.0521 [+0.0340, +0.0716], realised minus predicted +0.0022 [-0.0268, +0.0317]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.396 | 0.3148 | 0.2720 | +0.0153 [-0.0263, +0.0564] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0864 | 0.0159 | +0.0156 [-0.0107, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0007 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0014 | 0.0200 | +0.0016 [-0.0033, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0775 | 0.1165 | +0.0273 [+0.0054, +0.0563] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0028 | 0.0000 | +0.0317 [+0.0248, +0.0383] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0732 | 0.2439 | 0.0166 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.410 | 0.3213 | 0.2615 | +0.0156 [-0.0213, +0.0519] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1035 | 0.1133 | +0.0558 [+0.0323, +0.0818] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0805 | 0.0630 | +0.0054 [-0.0047, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2099 | 0.2903 | +0.1309 [+0.0543, +0.2097] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.0988 | 0.1461 | +0.0683 [+0.0390, +0.0977] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.739] | 0.297 | 6.27 flat / 3.34 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.269 | 4.92 flat / 2.36 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.350, 0.739] | 4.885 [3.038, 7.824] | 2.413 [1.360, 4.075] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.885 [3.033, 7.783] | 2.212 [1.275, 3.750] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.385 [2.500, 7.278] | 1.971 [1.009, 3.471] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.115 [2.233, 6.952] | 2.087 [0.981, 3.837] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 4.462 [2.536, 7.346] | 2.019 [1.019, 3.588] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.824 [5.000, 12.923] | 3.735 [2.132, 6.876] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.333 (no interval) | 2.583 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.391 (126 of 1873 days never flag) | 212 | 0.607 | 0.401 | 0.0496 | +0.0218 [+0.0143, +0.0297] | +0.0067 [+0.0010, +0.0127] | 0.903 | 0.534 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 208 | 0.583 | 0.389 | 0.0613 | +0.0097 [+0.0041, +0.0154] | -0.0003 [-0.0056, +0.0045] | 0.854 | 0.509 | no |
| 3 | 0.403 (147 of 1871 days never flag) | 189 | 0.543 | 0.397 | 0.0599 | +0.0108 [+0.0060, +0.0154] | +0.0045 [-0.0001, +0.0091] | 0.856 | 0.478 | no |
| 4 | 0.376 (147 of 1870 days never flag) | 171 | 0.464 | 0.374 | 0.0618 | +0.0091 [+0.0045, +0.0135] | +0.0006 [-0.0038, +0.0048] | 0.829 | 0.402 | no |
| 5 | 0.426 (147 of 1869 days never flag) | 190 | 0.536 | 0.389 | 0.0692 | +0.0017 [-0.0037, +0.0067] | -0.0058 [-0.0117, -0.0003] | 0.782 | 0.469 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.492 (climatology 0.512, difference -0.0197 [-0.1117, +0.0624]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0898, ΔBrier vs climatology +0.0397 [+0.0271, +0.0539], realised minus predicted +0.0212 [-0.0113, +0.0580]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.384 | 0.2736 | 0.2720 | +0.0457 [+0.0147, +0.0775] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1223 | 0.0159 | +0.0209 [+0.0043, +0.0353] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0079 | 0.0000 | +0.0134 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0039 | 0.0200 | +0.0037 [-0.0000, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0755 | 0.1165 | +0.0300 [+0.0055, +0.0612] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0051 | 0.0048 | +0.0090 [+0.0072, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0504 | 0.0000 | +0.0282 [+0.0218, +0.0345] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0778 | 0.2439 | 0.0175 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.664 | 0.399 | 0.2818 | 0.2615 | +0.0459 [+0.0179, +0.0739] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1072 | 0.1133 | +0.0584 [+0.0347, +0.0842] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.345 | 0.0795 | 0.0630 | +0.0137 [+0.0063, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.2213 | 0.2903 | +0.1280 [+0.0485, +0.2109] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.0961 | 0.1461 | +0.0685 [+0.0409, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2722 | 0.2213 |

## risk_gbm+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.346, 0.727] | 0.306 | 6.42 flat / 3.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.269 | 5.27 flat / 2.81 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.346, 0.727] | 4.769 [2.905, 7.286] | 2.298 [1.310, 3.648] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.579] | 4.808 [2.903, 7.424] | 2.163 [1.194, 3.533] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.385 [2.476, 7.002] | 2.000 [1.008, 3.380] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.538 [2.441, 7.421] | 2.490 [1.148, 4.529] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 3.846 [2.057, 6.217] | 1.856 [0.875, 3.226] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.529 [4.749, 12.071] | 3.441 [2.021, 5.778] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (126 of 1873 days never flag) | 207 | 0.593 | 0.401 | 0.0504 | +0.0210 [+0.0137, +0.0295] | +0.0059 [-0.0001, +0.0122] | 0.897 | 0.521 | yes |
| 2 | 0.452 (147 of 1872 days never flag) | 205 | 0.576 | 0.390 | 0.0617 | +0.0094 [+0.0036, +0.0151] | -0.0006 [-0.0063, +0.0046] | 0.849 | 0.503 | no |
| 3 | 0.368 (147 of 1871 days never flag) | 190 | 0.551 | 0.400 | 0.0600 | +0.0107 [+0.0055, +0.0155] | +0.0044 [-0.0003, +0.0092] | 0.857 | 0.485 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 184 | 0.478 | 0.359 | 0.0604 | +0.0105 [+0.0055, +0.0150] | +0.0020 [-0.0024, +0.0062] | 0.845 | 0.410 | yes |
| 5 | 0.489 (147 of 1869 days never flag) | 161 | 0.442 | 0.379 | 0.0670 | +0.0039 [-0.0012, +0.0088] | -0.0036 [-0.0091, +0.0019] | 0.792 | 0.384 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.512, difference -0.0147 [-0.1229, +0.0768]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0872, ΔBrier vs climatology +0.0423 [+0.0285, +0.0569], realised minus predicted +0.0221 [-0.0105, +0.0568]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.396 | 0.2769 | 0.2720 | +0.0447 [+0.0131, +0.0776] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1254 | 0.0159 | +0.0193 [+0.0030, +0.0347] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0081 | 0.0000 | +0.0134 [+0.0117, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0018 | 0.0200 | +0.0016 [-0.0030, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0745 | 0.1165 | +0.0296 [+0.0063, +0.0590] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0044 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0518 | 0.0000 | +0.0280 [+0.0216, +0.0343] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0976 | 0.2439 | 0.0158 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.402 | 0.2836 | 0.2615 | +0.0437 [+0.0161, +0.0738] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1047 | 0.1133 | +0.0561 [+0.0322, +0.0814] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.353 | 0.0807 | 0.0630 | +0.0130 [+0.0058, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0526, +0.2114] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.0988 | 0.1461 | +0.0683 [+0.0373, +0.0988] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2718 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.348, 0.731] | 0.282 | 6.00 flat / 3.17 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.654] | 0.269 | 4.65 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.731] | 4.885 [3.040, 7.625] | 2.413 [1.383, 4.001] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 3.962 [2.286, 6.529] | 1.865 [0.979, 3.221] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.115 [2.387, 6.744] | 1.933 [1.016, 3.303] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.038 [2.312, 6.600] | 2.096 [1.062, 3.659] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.731 [2.069, 6.143] | 1.856 [0.913, 3.250] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.471 [4.571, 12.111] | 3.529 [1.984, 6.233] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.391 (126 of 1873 days never flag) | 212 | 0.607 | 0.401 | 0.0496 | +0.0218 [+0.0140, +0.0297] | +0.0067 [+0.0009, +0.0126] | 0.903 | 0.534 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 183 | 0.576 | 0.437 | 0.0545 | +0.0165 [+0.0098, +0.0230] | +0.0065 [+0.0001, +0.0130] | 0.871 | 0.516 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 185 | 0.565 | 0.422 | 0.0566 | +0.0141 [+0.0082, +0.0203] | +0.0078 [+0.0020, +0.0139] | 0.871 | 0.503 | yes |
| 4 | 0.376 (147 of 1870 days never flag) | 173 | 0.493 | 0.393 | 0.0567 | +0.0141 [+0.0086, +0.0196] | +0.0056 [-0.0001, +0.0112] | 0.851 | 0.432 | no |
| 5 | 0.426 (147 of 1869 days never flag) | 166 | 0.500 | 0.416 | 0.0618 | +0.0092 [+0.0032, +0.0154] | +0.0016 [-0.0048, +0.0078] | 0.829 | 0.444 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0178, +0.2693]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0776, ΔBrier vs climatology +0.0519 [+0.0344, +0.0709], realised minus predicted -0.0023 [-0.0330, +0.0273]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.384 | 0.2736 | 0.2720 | +0.0457 [+0.0136, +0.0778] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1223 | 0.0159 | +0.0209 [+0.0043, +0.0354] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0079 | 0.0000 | +0.0134 [+0.0118, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0039 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0755 | 0.1165 | +0.0300 [+0.0052, +0.0623] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0051 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0504 | 0.0000 | +0.0282 [+0.0220, +0.0345] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0778 | 0.2439 | 0.0175 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.664 | 0.399 | 0.2818 | 0.2615 | +0.0459 [+0.0173, +0.0746] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1072 | 0.1133 | +0.0584 [+0.0337, +0.0833] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.345 | 0.0795 | 0.0630 | +0.0137 [+0.0064, +0.0215] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.2213 | 0.2903 | +0.1280 [+0.0491, +0.2110] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.0961 | 0.1461 | +0.0685 [+0.0424, +0.0948] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2722 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.348, 0.727] | 0.291 | 6.15 flat / 3.43 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.692] | 0.269 | 5.54 flat / 2.96 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.727] | 4.769 [2.844, 7.334] | 2.298 [1.316, 3.684] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 3.962 [2.167, 6.391] | 1.837 [0.928, 3.089] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.303, 0.704] | 4.615 [2.636, 7.263] | 2.144 [1.155, 3.536] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.385 [2.417, 7.183] | 2.462 [1.167, 4.472] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.192 [2.280, 6.867] | 2.433 [1.152, 4.420] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.882] | 7.176 [4.260, 11.636] | 3.235 [1.775, 5.611] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 3.806 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (126 of 1873 days never flag) | 207 | 0.593 | 0.401 | 0.0504 | +0.0210 [+0.0132, +0.0291] | +0.0059 [+0.0001, +0.0120] | 0.897 | 0.521 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 185 | 0.590 | 0.443 | 0.0550 | +0.0161 [+0.0094, +0.0227] | +0.0061 [-0.0005, +0.0123] | 0.871 | 0.530 | yes |
| 3 | 0.368 (147 of 1871 days never flag) | 204 | 0.609 | 0.412 | 0.0569 | +0.0138 [+0.0077, +0.0201] | +0.0075 [+0.0016, +0.0135] | 0.866 | 0.539 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 185 | 0.514 | 0.384 | 0.0546 | +0.0163 [+0.0100, +0.0226] | +0.0078 [+0.0015, +0.0143] | 0.863 | 0.449 | yes |
| 5 | 0.723 (147 of 1869 days never flag) | 176 | 0.486 | 0.381 | 0.0594 | +0.0116 [+0.0054, +0.0178] | +0.0040 [-0.0024, +0.0106] | 0.832 | 0.423 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1899 [+0.0366, +0.3187]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0771, ΔBrier vs climatology +0.0524 [+0.0346, +0.0715], realised minus predicted +0.0003 [-0.0289, +0.0299]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.396 | 0.2769 | 0.2720 | +0.0447 [+0.0133, +0.0778] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1254 | 0.0159 | +0.0193 [+0.0024, +0.0338] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0081 | 0.0000 | +0.0134 [+0.0117, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0018 | 0.0200 | +0.0016 [-0.0031, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0745 | 0.1165 | +0.0296 [+0.0065, +0.0605] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0044 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0518 | 0.0000 | +0.0280 [+0.0218, +0.0342] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0976 | 0.2439 | 0.0158 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.402 | 0.2836 | 0.2615 | +0.0437 [+0.0145, +0.0740] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1047 | 0.1133 | +0.0561 [+0.0309, +0.0812] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.353 | 0.0807 | 0.0630 | +0.0130 [+0.0055, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0542, +0.2103] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.0988 | 0.1461 | +0.0683 [+0.0380, +0.0994] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2718 | 0.2213 |

## risk_gbm+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.710] | 0.192 | 2.19 flat / 1.48 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.192 | 1.81 flat / 1.23 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.423 [0.974, 2.091] | 0.760 [0.477, 1.217] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.594, 1.516] | 0.548 [0.302, 0.926] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.385 [0.864, 2.160] | 0.885 [0.471, 1.560] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.154 [0.704, 1.824] | 0.683 [0.370, 1.174] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.600] | 1.115 [0.666, 1.783] | 0.760 [0.393, 1.333] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.667 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 79 | 0.300 | 0.532 | 0.0580 | +0.0134 [+0.0080, +0.0191] | -0.0017 [-0.0097, +0.0061] | 0.642 | 0.279 | no |
| 2 | 0.111 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0591 | +0.0119 [+0.0070, +0.0168] | +0.0019 [-0.0050, +0.0085] | 0.639 | 0.259 | no |
| 3 | 0.115 (147 of 1871 days never flag) | 76 | 0.290 | 0.526 | 0.0605 | +0.0102 [+0.0048, +0.0154] | +0.0039 [-0.0027, +0.0099] | 0.636 | 0.269 | no |
| 4 | 0.12 (147 of 1870 days never flag) | 67 | 0.268 | 0.552 | 0.0587 | +0.0121 [+0.0071, +0.0170] | +0.0037 [-0.0025, +0.0096] | 0.633 | 0.251 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 65 | 0.261 | 0.554 | 0.0596 | +0.0114 [+0.0065, +0.0160] | +0.0038 [-0.0022, +0.0095] | 0.632 | 0.244 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1902 [+0.0363, +0.3262]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0855, ΔBrier vs climatology +0.0439 [+0.0317, +0.0572], realised minus predicted +0.0590 [+0.0302, +0.0902]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0211, +0.0239] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0167 | 0.0159 | +0.0382 [+0.0294, +0.0470] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0007 | 0.0000 | +0.0137 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0007 | 0.0200 | +0.0016 [-0.0030, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.562 | 0.0386 | 0.1165 | +0.0168 [+0.0005, +0.0385] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0014 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0018 | 0.0000 | +0.0317 [+0.0251, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0479 | 0.2439 | -0.0053 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.571 | 0.0985 | 0.2615 | +0.0133 [-0.0073, +0.0339] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0961 | 0.1133 | +0.0522 [+0.0290, +0.0759] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.500 | 0.0133 | 0.0630 | +0.0045 [-0.0005, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2099 | 0.2903 | +0.1309 [+0.0527, +0.2129] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.0988 | 0.1461 | +0.0683 [+0.0393, +0.0972] |

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
| lead_at_least_3 | 26 | 8 | 0.308 [0.158, 0.460] | 0.154 | 1.50 flat / 1.03 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.719] | 1.500 [1.000, 2.286] | 0.971 [0.556, 1.633] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.655, 1.778] | 0.644 [0.302, 1.174] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.385 [0.857, 2.227] | 0.913 [0.464, 1.638] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.231 [0.727, 1.955] | 0.760 [0.364, 1.359] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.667 [1.769, 8.500] | 3.306 [1.479, 8.002] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 82 | 0.307 | 0.524 | 0.0586 | +0.0129 [+0.0079, +0.0176] | -0.0022 [-0.0100, +0.0046] | 0.643 | 0.285 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 53 | 0.173 | 0.453 | 0.0686 | +0.0024 [-0.0042, +0.0085] | -0.0076 [-0.0164, +0.0001] | 0.578 | 0.156 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 62 | 0.188 | 0.419 | 0.0674 | +0.0033 [-0.0034, +0.0093] | -0.0030 [-0.0113, +0.0038] | 0.580 | 0.168 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 57 | 0.203 | 0.491 | 0.0660 | +0.0048 [-0.0017, +0.0111] | -0.0036 [-0.0111, +0.0031] | 0.580 | 0.186 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0055, +0.0071] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.539 (climatology 0.512, difference +0.0266 [-0.1146, +0.1515]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1041, ΔBrier vs climatology +0.0253 [+0.0163, +0.0348], realised minus predicted +0.0899 [+0.0555, +0.1265]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0972 | 0.2720 | -0.0015 [-0.0206, +0.0159] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0237 | 0.0159 | +0.0335 [+0.0228, +0.0443] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [+0.0001, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0377 | 0.1165 | +0.0199 [+0.0032, +0.0405] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0058 | 0.0000 | +0.0309 [+0.0245, +0.0370] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.667 | 0.0203 | 0.2439 | 0.0057 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.1021 | 0.2615 | +0.0089 [-0.0095, +0.0255] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.1003 | 0.1133 | +0.0379 [+0.0140, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0129 | 0.0630 | +0.0054 [+0.0003, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2030 | 0.2903 | +0.1126 [+0.0332, +0.1946] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1168 | 0.1461 | +0.0706 [+0.0489, +0.0946] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2084 | 0.2213 |

## risk_gbm_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.520, 0.850] | 0.411 | 7.88 flat / 3.77 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.321, 0.682] | 0.288 | 6.15 flat / 2.93 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.440, 0.800] | 5.077 [3.348, 7.455] | 2.192 [1.351, 3.461] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.207, 7.400] | 2.029 [1.250, 3.234] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.692 [2.889, 7.286] | 2.038 [1.194, 3.274] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.263, 0.600] | 4.385 [2.710, 6.789] | 1.913 [1.142, 3.070] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 4.423 [2.703, 6.929] | 2.087 [1.241, 3.395] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.471 [4.773, 11.779] | 3.176 [1.867, 5.251] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 8.667 (no interval) | 4.889 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 228 | 0.686 | 0.421 | 0.0486 | +0.0228 [+0.0155, +0.0309] | +0.0077 [+0.0030, +0.0129] | 0.899 | 0.610 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 222 | 0.669 | 0.419 | 0.0601 | +0.0110 [+0.0069, +0.0151] | +0.0010 [-0.0021, +0.0039] | 0.836 | 0.595 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 200 | 0.565 | 0.390 | 0.0613 | +0.0094 [+0.0056, +0.0132] | +0.0031 [+0.0001, +0.0061] | 0.812 | 0.495 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 192 | 0.565 | 0.406 | 0.0585 | +0.0123 [+0.0074, +0.0173] | +0.0038 [+0.0007, +0.0072] | 0.838 | 0.499 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 184 | 0.500 | 0.375 | 0.0630 | +0.0080 [+0.0035, +0.0120] | +0.0004 [-0.0026, +0.0034] | 0.782 | 0.434 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.534 (climatology 0.512, difference +0.0222 [-0.1006, +0.1277]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0448 [+0.0306, +0.0605], realised minus predicted +0.0098 [-0.0214, +0.0442]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.420 | 0.2386 | 0.2720 | +0.0542 [+0.0257, +0.0845] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1263 | 0.0159 | +0.0173 [+0.0016, +0.0307] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0321 | 0.0200 | +0.0008 [-0.0060, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.581 | 0.1139 | 0.1165 | +0.0318 [+0.0048, +0.0663] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0225 | 0.0048 | +0.0080 [+0.0057, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0691 | 0.0000 | +0.0246 [+0.0189, +0.0302] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.625 | 0.1409 | 0.2439 | 0.0481 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.720 | 0.419 | 0.2526 | 0.2615 | +0.0517 [+0.0258, +0.0791] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1097 | 0.1133 | +0.0430 [+0.0192, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.372 | 0.0863 | 0.0630 | +0.0165 [+0.0094, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2030 | 0.2903 | +0.1126 [+0.0371, +0.1936] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0951] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.517, 0.850] | 0.385 | 7.27 flat / 3.64 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.640] | 0.269 | 5.38 flat / 2.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 3.462 [2.429, 5.100] | 1.644 [1.108, 2.528] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.516] | 3.808 [2.562, 5.653] | 1.558 [1.013, 2.364] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 3.500 [2.233, 5.353] | 1.596 [1.008, 2.500] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.567] | 3.808 [2.500, 5.715] | 1.606 [1.050, 2.430] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.731 [2.367, 5.600] | 1.625 [1.042, 2.475] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 5.765 [3.759, 9.154] | 2.191 [1.416, 3.568] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.111 (no interval) | 6.389 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 172 | 0.586 | 0.477 | 0.0505 | +0.0209 [+0.0140, +0.0279] | +0.0058 [+0.0012, +0.0105] | 0.805 | 0.534 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 171 | 0.518 | 0.421 | 0.0623 | +0.0087 [+0.0040, +0.0133] | -0.0013 [-0.0054, +0.0025] | 0.749 | 0.461 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 156 | 0.471 | 0.417 | 0.0613 | +0.0094 [+0.0044, +0.0142] | +0.0030 [-0.0014, +0.0070] | 0.746 | 0.419 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 173 | 0.536 | 0.428 | 0.0594 | +0.0114 [+0.0060, +0.0167] | +0.0030 [-0.0008, +0.0067] | 0.763 | 0.479 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 166 | 0.500 | 0.416 | 0.0636 | +0.0073 [+0.0021, +0.0121] | -0.0002 [-0.0043, +0.0036] | 0.740 | 0.444 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.544 (climatology 0.512, difference +0.0322 [-0.0976, +0.1388]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0429 [+0.0300, +0.0571], realised minus predicted +0.0588 [+0.0304, +0.0903]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.544 | 0.1689 | 0.2720 | +0.0386 [+0.0127, +0.0658] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0313 | 0.0159 | +0.0263 [+0.0081, +0.0404] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.167 | 0.0145 | 0.0200 | +0.0009 [-0.0065, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.514 | 0.0889 | 0.1165 | +0.0310 [+0.0055, +0.0607] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.111 | 0.0086 | 0.0048 | +0.0082 [+0.0059, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0070 | 0.0000 | +0.0308 [+0.0244, +0.0366] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.500 | 0.1098 | 0.2439 | 0.0458 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.608 | 0.521 | 0.1761 | 0.2615 | +0.0401 [+0.0146, +0.0649] |
| day_type | month_end | 150 | 17 | 0.824 | 0.538 | 0.1041 | 0.1133 | +0.0436 [+0.0174, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.443 | 0.0421 | 0.0630 | +0.0143 [+0.0078, +0.0210] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1126 [+0.0341, +0.1908] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0952] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3903 | 0.2213 |

## risk_gbm_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.464, 0.833] | 0.358 | 6.69 flat / 3.24 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.269 | 5.77 flat / 2.71 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.428, 0.800] | 4.577 [2.931, 7.000] | 1.971 [1.213, 3.163] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.600] | 4.462 [2.733, 7.000] | 1.837 [1.078, 3.068] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.923 [2.967, 7.740] | 2.202 [1.213, 3.667] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.637] | 4.385 [2.621, 6.884] | 1.837 [1.060, 3.060] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 3.962 [2.343, 6.391] | 1.808 [1.033, 3.090] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.176 [4.416, 11.400] | 3.088 [1.760, 5.171] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 5.778 (no interval) | 3.528 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 213 | 0.671 | 0.441 | 0.0487 | +0.0227 [+0.0162, +0.0302] | +0.0076 [+0.0030, +0.0127] | 0.893 | 0.603 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 203 | 0.626 | 0.429 | 0.0594 | +0.0116 [+0.0085, +0.0151] | +0.0016 [-0.0017, +0.0051] | 0.820 | 0.559 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 208 | 0.580 | 0.385 | 0.0598 | +0.0109 [+0.0075, +0.0145] | +0.0045 [+0.0011, +0.0085] | 0.802 | 0.506 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 192 | 0.565 | 0.406 | 0.0567 | +0.0141 [+0.0099, +0.0183] | +0.0056 [+0.0026, +0.0089] | 0.835 | 0.499 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 166 | 0.457 | 0.380 | 0.0613 | +0.0096 [+0.0062, +0.0130] | +0.0021 [-0.0010, +0.0050] | 0.772 | 0.397 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.535 (climatology 0.512, difference +0.0228 [-0.0941, +0.1215]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0857, ΔBrier vs climatology +0.0437 [+0.0300, +0.0589], realised minus predicted +0.0197 [-0.0113, +0.0551]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.440 | 0.2205 | 0.2720 | +0.0484 [+0.0229, +0.0773] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1138 | 0.0159 | +0.0229 [+0.0100, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0155 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0227 | 0.0200 | +0.0029 [-0.0014, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.556 | 0.0976 | 0.1165 | +0.0320 [+0.0078, +0.0614] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0170 | 0.0048 | +0.0090 [+0.0071, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0607 | 0.0000 | +0.0257 [+0.0200, +0.0314] |
| scarcity_state | 2 | 41 | 10 | 0.400 | 0.667 | 0.1137 | 0.2439 | 0.0482 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.712 | 0.434 | 0.2331 | 0.2615 | +0.0486 [+0.0250, +0.0746] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1082 | 0.1133 | +0.0422 [+0.0179, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.399 | 0.0748 | 0.0630 | +0.0165 [+0.0103, +0.0237] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2030 | 0.2903 | +0.1126 [+0.0372, +0.1918] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1168 | 0.1461 | +0.0706 [+0.0489, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0837 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2566 | 0.2213 |

## risk_gbm_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.857] | 0.385 | 7.38 flat / 3.47 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 5.73 flat / 2.66 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.115 [3.455, 7.417] | 2.212 [1.401, 3.400] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.846 [3.138, 7.211] | 1.981 [1.217, 3.063] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.500 [2.743, 6.960] | 1.942 [1.141, 3.136] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.192 [2.555, 6.365] | 1.808 [1.048, 2.917] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.269 [2.617, 6.534] | 1.971 [1.154, 3.153] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.471 [4.909, 11.714] | 3.176 [1.945, 5.269] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 7.222 [4.437, 13.600] | 4.028 [2.346, 8.625] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 229 | 0.686 | 0.419 | 0.0478 | +0.0237 [+0.0164, +0.0313] | +0.0086 [+0.0041, +0.0137] | 0.914 | 0.609 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 219 | 0.669 | 0.425 | 0.0592 | +0.0119 [+0.0075, +0.0160] | +0.0019 [-0.0012, +0.0049] | 0.875 | 0.596 | yes |
| 3 | 0.241 (147 of 1871 days never flag) | 195 | 0.565 | 0.400 | 0.0594 | +0.0113 [+0.0077, +0.0153] | +0.0050 [+0.0020, +0.0081] | 0.862 | 0.498 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 187 | 0.565 | 0.417 | 0.0571 | +0.0138 [+0.0093, +0.0187] | +0.0053 [+0.0024, +0.0087] | 0.874 | 0.502 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 180 | 0.500 | 0.383 | 0.0618 | +0.0091 [+0.0049, +0.0132] | +0.0016 [-0.0015, +0.0046] | 0.846 | 0.436 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.534 (climatology 0.512, difference +0.0222 [-0.0983, +0.1196]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0831, ΔBrier vs climatology +0.0463 [+0.0324, +0.0618], realised minus predicted +0.0369 [+0.0061, +0.0695]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.420 | 0.2386 | 0.2720 | +0.0542 [+0.0277, +0.0836] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1260 | 0.0159 | +0.0173 [+0.0018, +0.0320] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0043 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0022 | 0.0200 | +0.0038 [-0.0002, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.545 | 0.0974 | 0.1165 | +0.0343 [+0.0077, +0.0644] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0691 | 0.0000 | +0.0246 [+0.0191, +0.0303] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.625 | 0.1409 | 0.2439 | 0.0481 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.720 | 0.413 | 0.2526 | 0.2615 | +0.0517 [+0.0265, +0.0789] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1076 | 0.1133 | +0.0431 [+0.0173, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.372 | 0.0725 | 0.0630 | +0.0175 [+0.0106, +0.0249] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2030 | 0.2903 | +0.1126 [+0.0335, +0.1904] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0931] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.471, 0.833] | 0.385 | 7.35 flat / 3.63 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.643] | 0.269 | 5.73 flat / 2.72 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.763] | 4.577 [3.085, 6.882] | 2.106 [1.336, 3.323] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.229, 0.550] | 4.308 [2.793, 6.467] | 1.692 [1.090, 2.604] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.615 [2.842, 7.157] | 2.058 [1.217, 3.342] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.577 [2.943, 7.000] | 2.058 [1.274, 3.278] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.385 [2.760, 6.768] | 2.048 [1.226, 3.328] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.706 [4.080, 10.750] | 2.824 [1.590, 4.767] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.751] | 8.556 [5.599, 16.750] | 5.167 [3.143, 11.000] |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 212 | 0.664 | 0.439 | 0.0492 | +0.0222 [+0.0169, +0.0277] | +0.0071 [+0.0023, +0.0116] | 0.908 | 0.596 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 199 | 0.626 | 0.437 | 0.0603 | +0.0107 [+0.0074, +0.0138] | +0.0007 [-0.0037, +0.0045] | 0.845 | 0.561 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 196 | 0.551 | 0.388 | 0.0605 | +0.0102 [+0.0067, +0.0135] | +0.0039 [-0.0003, +0.0077] | 0.824 | 0.481 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 196 | 0.558 | 0.393 | 0.0584 | +0.0125 [+0.0085, +0.0165] | +0.0040 [+0.0001, +0.0077] | 0.841 | 0.489 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 182 | 0.493 | 0.374 | 0.0624 | +0.0085 [+0.0051, +0.0118] | +0.0010 [-0.0028, +0.0044] | 0.791 | 0.427 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.526 (climatology 0.512, difference +0.0141 [-0.1025, +0.1244]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0897, ΔBrier vs climatology +0.0398 [+0.0288, +0.0513], realised minus predicted +0.0507 [+0.0176, +0.0856]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.466 | 0.1679 | 0.2720 | +0.0397 [+0.0236, +0.0565] |
| regime | 2020 | 251 | 4 | 0.250 | 0.050 | 0.0750 | 0.0159 | +0.0305 [+0.0195, +0.0408] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0032 [-0.0013, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.552 | 0.0758 | 0.1165 | +0.0324 [+0.0085, +0.0609] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0117 | 0.0048 | +0.0092 [+0.0073, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0375 | 0.0000 | +0.0293 [+0.0233, +0.0352] |
| scarcity_state | 2 | 41 | 10 | 0.400 | 0.500 | 0.0806 | 0.2439 | 0.0353 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.456 | 0.1774 | 0.2615 | +0.0449 [+0.0275, +0.0625] |
| day_type | month_end | 150 | 17 | 0.824 | 0.519 | 0.1050 | 0.1133 | +0.0408 [+0.0165, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.404 | 0.0496 | 0.0630 | +0.0161 [+0.0117, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1126 [+0.0374, +0.1919] |
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
| lead_at_least_1 | 26 | 16 | 0.615 [0.437, 0.792] | 0.351 | 6.58 flat / 3.13 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.613] | 0.269 | 5.31 flat / 2.50 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.767] | 4.808 [2.965, 7.319] | 2.183 [1.250, 3.492] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.607] | 4.885 [2.954, 7.500] | 2.125 [1.146, 3.476] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 4.615 [2.658, 7.200] | 2.173 [1.160, 3.550] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.231 [2.474, 6.650] | 1.933 [0.988, 3.268] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 3.808 [2.000, 6.185] | 1.837 [0.857, 3.238] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.955] | 7.647 [4.908, 11.932] | 3.309 [1.932, 5.584] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 4.556 [2.333, 9.752] | 2.806 [1.204, 6.720] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 211 | 0.614 | 0.408 | 0.0615 | +0.0099 [+0.0001, +0.0193] | -0.0051 [-0.0140, +0.0029] | 0.874 | 0.542 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 210 | 0.597 | 0.395 | 0.0716 | -0.0006 [-0.0096, +0.0072] | -0.0106 [-0.0192, -0.0031] | 0.817 | 0.524 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 192 | 0.522 | 0.375 | 0.0733 | -0.0026 [-0.0115, +0.0051] | -0.0089 [-0.0175, -0.0013] | 0.796 | 0.452 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 180 | 0.507 | 0.389 | 0.0694 | +0.0015 [-0.0058, +0.0085] | -0.0070 [-0.0137, -0.0006] | 0.823 | 0.444 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 159 | 0.435 | 0.377 | 0.0728 | -0.0019 [-0.0084, +0.0035] | -0.0094 [-0.0158, -0.0040] | 0.770 | 0.378 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.501 (climatology 0.512, difference -0.0110 [-0.1232, +0.0940]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0224, +0.0512], realised minus predicted +0.0046 [-0.0308, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.398 | 0.3131 | 0.2720 | +0.0099 [-0.0341, +0.0495] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2009 | 0.0159 | -0.0101 [-0.0343, +0.0089] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0064 | 0.0200 | +0.0027 [-0.0027, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0674 | 0.1165 | +0.0312 [+0.0072, +0.0606] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0072 | 0.0048 | +0.0086 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1136 | 0.0000 | +0.0113 [+0.0058, +0.0169] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0972 | 0.2439 | 0.0369 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.680 | 0.405 | 0.3157 | 0.2615 | +0.0098 [-0.0291, +0.0446] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1110 | 0.1133 | +0.0404 [+0.0156, +0.0675] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.349 | 0.1027 | 0.0630 | +0.0017 [-0.0087, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0339, +0.1905] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0923] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2962 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.368, 0.778] | 0.276 | 5.88 flat / 2.76 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.269 | 4.69 flat / 2.21 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.368, 0.778] | 4.692 [2.853, 7.080] | 2.115 [1.202, 3.375] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 4.731 [2.760, 7.333] | 2.058 [1.064, 3.408] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.607] | 4.423 [2.416, 6.953] | 2.000 [1.000, 3.363] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.564] | 3.808 [2.000, 6.108] | 1.788 [0.836, 3.100] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.564] | 3.885 [2.065, 6.269] | 1.885 [0.879, 3.303] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.958] | 7.647 [4.857, 11.616] | 3.309 [1.946, 5.364] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.556 [1.143, 6.168] | 1.722 [0.573, 4.750] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 206 | 0.600 | 0.408 | 0.0617 | +0.0097 [-0.0002, +0.0192] | -0.0054 [-0.0137, +0.0022] | 0.874 | 0.530 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 202 | 0.568 | 0.391 | 0.0721 | -0.0011 [-0.0095, +0.0068] | -0.0111 [-0.0191, -0.0036] | 0.814 | 0.497 | no |
| 3 | 0.534 (147 of 1871 days never flag) | 187 | 0.522 | 0.385 | 0.0728 | -0.0021 [-0.0122, +0.0057] | -0.0084 [-0.0180, -0.0009] | 0.797 | 0.455 | no |
| 4 | 0.527 (147 of 1870 days never flag) | 164 | 0.471 | 0.396 | 0.0705 | +0.0003 [-0.0075, +0.0073] | -0.0082 [-0.0152, -0.0014] | 0.819 | 0.414 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 162 | 0.442 | 0.377 | 0.0729 | -0.0020 [-0.0083, +0.0037] | -0.0095 [-0.0156, -0.0038] | 0.771 | 0.384 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.512, difference -0.0138 [-0.1284, +0.0885]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0918, ΔBrier vs climatology +0.0377 [+0.0232, +0.0544], realised minus predicted +0.0039 [-0.0299, +0.0400]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.3159 | 0.2720 | +0.0093 [-0.0342, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1988 | 0.0159 | -0.0092 [-0.0323, +0.0093] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0045 | 0.0200 | -0.0001 [-0.0066, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0654 | 0.1165 | +0.0318 [+0.0097, +0.0597] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0080 [+0.0058, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1120 | 0.0000 | +0.0117 [+0.0061, +0.0177] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1019 | 0.2439 | 0.0494 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.408 | 0.3169 | 0.2615 | +0.0086 [-0.0288, +0.0447] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1089 | 0.1133 | +0.0435 [+0.0219, +0.0664] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.353 | 0.1032 | 0.0630 | +0.0011 [-0.0098, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0365, +0.1928] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0943] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.368, 0.767] | 0.291 | 6.15 flat / 3.01 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.308, 0.706] | 0.269 | 5.04 flat / 2.47 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.368, 0.767] | 4.808 [2.913, 7.350] | 2.183 [1.240, 3.529] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.304, 0.700] | 4.808 [2.869, 7.486] | 2.202 [1.230, 3.607] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.304, 0.700] | 4.577 [2.633, 7.251] | 2.192 [1.180, 3.635] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 3.808 [1.958, 6.224] | 1.913 [0.939, 3.274] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 4.077 [2.182, 6.591] | 2.029 [1.007, 3.448] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.118 [4.438, 11.504] | 3.103 [1.771, 5.322] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 211 | 0.614 | 0.408 | 0.0615 | +0.0099 [+0.0001, +0.0193] | -0.0051 [-0.0137, +0.0026] | 0.874 | 0.542 | no |
| 2 | 0.435 (147 of 1872 days never flag) | 213 | 0.633 | 0.413 | 0.0650 | +0.0060 [-0.0035, +0.0153] | -0.0040 [-0.0134, +0.0044] | 0.846 | 0.561 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 200 | 0.587 | 0.405 | 0.0673 | +0.0034 [-0.0061, +0.0122] | -0.0029 [-0.0123, +0.0059] | 0.830 | 0.518 | yes |
| 4 | 0.522 (147 of 1870 days never flag) | 168 | 0.500 | 0.411 | 0.0650 | +0.0059 [-0.0023, +0.0133] | -0.0026 [-0.0109, +0.0049] | 0.843 | 0.443 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 175 | 0.500 | 0.394 | 0.0665 | +0.0044 [-0.0025, +0.0109] | -0.0031 [-0.0102, +0.0032] | 0.819 | 0.439 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1658 [+0.0518, +0.2840]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0450 [+0.0244, +0.0673], realised minus predicted -0.0207 [-0.0524, +0.0120]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.398 | 0.3131 | 0.2720 | +0.0099 [-0.0329, +0.0526] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2009 | 0.0159 | -0.0101 [-0.0344, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0064 | 0.0200 | +0.0027 [-0.0021, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0674 | 0.1165 | +0.0312 [+0.0066, +0.0611] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0072 | 0.0048 | +0.0086 [+0.0068, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1136 | 0.0000 | +0.0113 [+0.0059, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0972 | 0.2439 | 0.0369 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.680 | 0.405 | 0.3157 | 0.2615 | +0.0098 [-0.0290, +0.0465] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1110 | 0.1133 | +0.0404 [+0.0156, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.349 | 0.1027 | 0.0630 | +0.0017 [-0.0088, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0359, +0.1919] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0945] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2962 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.370, 0.769] | 0.269 | 5.54 flat / 2.65 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.285, 0.692] | 0.269 | 4.69 flat / 2.28 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.370, 0.769] | 4.692 [2.956, 7.130] | 2.115 [1.236, 3.434] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.462 [2.652, 7.000] | 1.990 [1.089, 3.292] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.192 [2.333, 6.750] | 1.933 [1.018, 3.284] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.808 [2.052, 6.211] | 1.904 [0.947, 3.303] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.923 [2.194, 6.321] | 1.971 [1.017, 3.381] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.000 [4.368, 11.231] | 3.074 [1.760, 5.143] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.778 (no interval) | 1.861 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 206 | 0.600 | 0.408 | 0.0617 | +0.0097 [-0.0000, +0.0195] | -0.0054 [-0.0136, +0.0025] | 0.874 | 0.530 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 202 | 0.619 | 0.426 | 0.0658 | +0.0053 [-0.0035, +0.0138] | -0.0047 [-0.0135, +0.0034] | 0.839 | 0.552 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 187 | 0.565 | 0.417 | 0.0669 | +0.0038 [-0.0052, +0.0127] | -0.0025 [-0.0116, +0.0060] | 0.825 | 0.502 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 171 | 0.522 | 0.421 | 0.0649 | +0.0060 [-0.0025, +0.0146] | -0.0025 [-0.0106, +0.0061] | 0.845 | 0.465 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 171 | 0.500 | 0.404 | 0.0662 | +0.0047 [-0.0020, +0.0114] | -0.0028 [-0.0094, +0.0041] | 0.821 | 0.441 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.3159 | 0.2720 | +0.0093 [-0.0343, +0.0511] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1988 | 0.0159 | -0.0092 [-0.0313, +0.0102] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0105, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0045 | 0.0200 | -0.0001 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0654 | 0.1165 | +0.0318 [+0.0096, +0.0601] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0080 [+0.0058, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1120 | 0.0000 | +0.0117 [+0.0058, +0.0179] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1019 | 0.2439 | 0.0494 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.408 | 0.3169 | 0.2615 | +0.0086 [-0.0288, +0.0458] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1089 | 0.1133 | +0.0435 [+0.0210, +0.0666] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.353 | 0.1032 | 0.0630 | +0.0011 [-0.0096, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0325, +0.1916] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.458, 0.826] | 0.368 | 6.85 flat / 3.36 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.269 | 5.27 flat / 2.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.419, 0.800] | 4.654 [2.969, 6.947] | 2.010 [1.230, 3.191] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.238, 0.600] | 4.923 [2.963, 7.478] | 2.144 [1.196, 3.460] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.611] | 4.462 [2.484, 6.955] | 2.077 [1.055, 3.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 4.077 [2.333, 6.435] | 1.904 [0.982, 3.219] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 4.192 [2.395, 6.636] | 2.106 [1.103, 3.554] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 7.647 [4.952, 11.875] | 3.309 [1.985, 5.501] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 5.333 (no interval) | 3.444 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 210 | 0.636 | 0.424 | 0.0569 | +0.0145 [+0.0069, +0.0226] | -0.0006 [-0.0069, +0.0054] | 0.852 | 0.566 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 210 | 0.590 | 0.390 | 0.0698 | +0.0013 [-0.0041, +0.0065] | -0.0087 [-0.0146, -0.0032] | 0.773 | 0.516 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 188 | 0.522 | 0.383 | 0.0706 | +0.0000 [-0.0047, +0.0044] | -0.0063 [-0.0112, -0.0017] | 0.726 | 0.455 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 174 | 0.493 | 0.391 | 0.0683 | +0.0025 [-0.0028, +0.0075] | -0.0059 [-0.0110, -0.0011] | 0.768 | 0.432 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 170 | 0.442 | 0.359 | 0.0728 | -0.0019 [-0.0073, +0.0032] | -0.0094 [-0.0153, -0.0038] | 0.709 | 0.379 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.512, difference -0.0153 [-0.1294, +0.0940]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0960, ΔBrier vs climatology +0.0335 [+0.0199, +0.0483], realised minus predicted -0.0133 [-0.0493, +0.0253]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.418 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0687] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2090 | 0.0159 | -0.0081 [-0.0241, +0.0060] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0109 | 0.0200 | +0.0027 [-0.0030, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0662 | 0.1165 | +0.0290 [+0.0078, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0206 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1332 | 0.0000 | +0.0055 [+0.0001, +0.0108] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0744 | 0.2439 | 0.0157 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.420 | 0.2903 | 0.2615 | +0.0341 [+0.0043, +0.0649] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1118 | 0.1133 | +0.0396 [+0.0167, +0.0640] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.369 | 0.1070 | 0.0630 | +0.0071 [-0.0005, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0356, +0.1888] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0484, +0.0944] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2920 | 0.2213 |

## risk_gbm_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.774] | 0.349 | 6.54 flat / 3.15 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.618] | 0.269 | 5.08 flat / 2.43 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.774] | 4.885 [3.057, 7.550] | 2.202 [1.280, 3.597] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.588] | 4.962 [2.998, 7.783] | 2.212 [1.219, 3.751] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.233, 0.625] | 4.308 [2.344, 7.056] | 1.923 [0.932, 3.375] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.577] | 4.000 [2.207, 6.546] | 1.865 [0.932, 3.313] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.577] | 4.192 [2.346, 6.833] | 2.106 [1.068, 3.707] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.647 [4.832, 12.105] | 3.309 [1.929, 5.776] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 4.444 [2.308, 10.000] | 2.861 [1.300, 7.250] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 214 | 0.621 | 0.407 | 0.0572 | +0.0142 [+0.0066, +0.0228] | -0.0009 [-0.0066, +0.0054] | 0.850 | 0.548 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 209 | 0.576 | 0.383 | 0.0703 | +0.0008 [-0.0050, +0.0063] | -0.0092 [-0.0151, -0.0033] | 0.770 | 0.501 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 185 | 0.529 | 0.395 | 0.0701 | +0.0006 [-0.0040, +0.0050] | -0.0058 [-0.0108, -0.0009] | 0.728 | 0.464 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 169 | 0.471 | 0.385 | 0.0695 | +0.0013 [-0.0038, +0.0063] | -0.0071 [-0.0122, -0.0021] | 0.762 | 0.411 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 171 | 0.449 | 0.363 | 0.0729 | -0.0020 [-0.0078, +0.0030] | -0.0095 [-0.0155, -0.0039] | 0.709 | 0.386 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.495 (climatology 0.512, difference -0.0169 [-0.1304, +0.0848]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0345 [+0.0206, +0.0496], realised minus predicted -0.0138 [-0.0497, +0.0250]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.2869 | 0.2720 | +0.0353 [+0.0025, +0.0716] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2069 | 0.0159 | -0.0072 [-0.0222, +0.0072] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0090 | 0.0200 | -0.0000 [-0.0064, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0642 | 0.1165 | +0.0297 [+0.0090, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0200 | 0.0048 | +0.0076 [+0.0055, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1316 | 0.0000 | +0.0059 [+0.0008, +0.0116] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0790 | 0.2439 | 0.0282 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.408 | 0.2915 | 0.2615 | +0.0329 [+0.0033, +0.0651] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1096 | 0.1133 | +0.0427 [+0.0224, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.353 | 0.1075 | 0.0630 | +0.0065 [-0.0011, +0.0153] |
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
| lead_at_least_1 | 26 | 17 | 0.654 [0.471, 0.826] | 0.297 | 6.27 flat / 3.01 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.348, 0.727] | 0.269 | 5.23 flat / 2.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 4.654 [2.970, 7.125] | 2.010 [1.198, 3.250] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.615 [2.666, 7.351] | 2.125 [1.169, 3.567] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.385 [2.417, 7.100] | 2.058 [1.083, 3.490] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.308, 0.682] | 4.000 [2.195, 6.688] | 1.990 [1.043, 3.441] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 4.269 [2.444, 7.000] | 2.135 [1.129, 3.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.118 [4.500, 11.500] | 3.103 [1.779, 5.413] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.667 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 210 | 0.636 | 0.424 | 0.0569 | +0.0145 [+0.0068, +0.0228] | -0.0006 [-0.0065, +0.0058] | 0.852 | 0.566 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 206 | 0.619 | 0.417 | 0.0624 | +0.0087 [+0.0018, +0.0158] | -0.0013 [-0.0085, +0.0056] | 0.815 | 0.549 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 195 | 0.587 | 0.415 | 0.0641 | +0.0066 [+0.0004, +0.0131] | +0.0003 [-0.0061, +0.0067] | 0.774 | 0.521 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 174 | 0.507 | 0.402 | 0.0636 | +0.0073 [+0.0010, +0.0133] | -0.0012 [-0.0076, +0.0051] | 0.795 | 0.447 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 182 | 0.514 | 0.390 | 0.0662 | +0.0047 [-0.0018, +0.0110] | -0.0029 [-0.0094, +0.0040] | 0.772 | 0.450 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1665 [+0.0511, +0.2853]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0860, ΔBrier vs climatology +0.0435 [+0.0244, +0.0650], realised minus predicted -0.0400 [-0.0718, -0.0060]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.418 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0706] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2090 | 0.0159 | -0.0081 [-0.0243, +0.0055] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0109 | 0.0200 | +0.0027 [-0.0022, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0662 | 0.1165 | +0.0290 [+0.0070, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0206 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1332 | 0.0000 | +0.0055 [+0.0003, +0.0109] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0744 | 0.2439 | 0.0157 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.420 | 0.2903 | 0.2615 | +0.0341 [+0.0033, +0.0648] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1118 | 0.1133 | +0.0396 [+0.0164, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.369 | 0.1070 | 0.0630 | +0.0071 [-0.0006, +0.0155] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0339, +0.1887] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0478, +0.0937] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2920 | 0.2213 |

## risk_gbm_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.381, 0.767] | 0.293 | 6.19 flat / 3.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.706] | 0.269 | 5.31 flat / 2.68 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.381, 0.767] | 4.885 [3.033, 7.517] | 2.202 [1.315, 3.609] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.577 [2.666, 7.251] | 2.087 [1.169, 3.476] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.346 [2.437, 7.002] | 2.048 [1.102, 3.520] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.077 [2.285, 6.644] | 2.029 [1.086, 3.527] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.269 [2.500, 6.886] | 2.231 [1.260, 3.780] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.000 [4.350, 11.231] | 3.074 [1.795, 5.264] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.667 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 214 | 0.621 | 0.407 | 0.0572 | +0.0142 [+0.0067, +0.0222] | -0.0009 [-0.0067, +0.0050] | 0.850 | 0.548 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 204 | 0.612 | 0.417 | 0.0631 | +0.0079 [+0.0013, +0.0143] | -0.0021 [-0.0088, +0.0044] | 0.805 | 0.543 | yes |
| 3 | 0.363 (147 of 1871 days never flag) | 193 | 0.580 | 0.415 | 0.0637 | +0.0070 [+0.0011, +0.0134] | +0.0007 [-0.0054, +0.0074] | 0.768 | 0.515 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 178 | 0.522 | 0.404 | 0.0635 | +0.0074 [+0.0008, +0.0140] | -0.0011 [-0.0079, +0.0061] | 0.798 | 0.461 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 181 | 0.507 | 0.387 | 0.0659 | +0.0050 [-0.0014, +0.0111] | -0.0025 [-0.0093, +0.0042] | 0.773 | 0.443 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.512, difference +0.2074 [+0.0600, +0.3396]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0268, +0.0642], realised minus predicted -0.0386 [-0.0698, -0.0044]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.2869 | 0.2720 | +0.0353 [+0.0035, +0.0676] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2069 | 0.0159 | -0.0072 [-0.0222, +0.0062] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0090 | 0.0200 | -0.0000 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0642 | 0.1165 | +0.0297 [+0.0093, +0.0557] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0200 | 0.0048 | +0.0076 [+0.0056, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1316 | 0.0000 | +0.0059 [+0.0008, +0.0116] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0790 | 0.2439 | 0.0282 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.408 | 0.2915 | 0.2615 | +0.0329 [+0.0040, +0.0629] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1096 | 0.1133 | +0.0427 [+0.0207, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.353 | 0.1075 | 0.0630 | +0.0065 [-0.0010, +0.0148] |
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
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.731] | 0.306 | 6.42 flat / 3.19 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.615] | 0.269 | 4.96 flat / 2.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.308, 0.704] | 5.115 [3.214, 7.800] | 2.481 [1.433, 4.084] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 5.000 [3.107, 7.751] | 2.192 [1.237, 3.645] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.462 [2.529, 7.063] | 2.058 [1.062, 3.513] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.962 [2.249, 6.356] | 1.808 [0.875, 3.173] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.500 [2.580, 7.179] | 2.029 [1.018, 3.530] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.385, 0.895] | 7.824 [4.951, 12.618] | 3.735 [2.178, 6.573] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 3.778 [1.667, 9.000] | 2.167 [0.833, 5.627] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (126 of 1873 days never flag) | 222 | 0.636 | 0.401 | 0.0571 | +0.0143 [+0.0046, +0.0237] | -0.0008 [-0.0089, +0.0068] | 0.920 | 0.559 | yes |
| 2 | 0.5 (147 of 1872 days never flag) | 215 | 0.612 | 0.395 | 0.0664 | +0.0047 [-0.0048, +0.0124] | -0.0053 [-0.0141, +0.0022] | 0.879 | 0.536 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 189 | 0.529 | 0.386 | 0.0668 | +0.0039 [-0.0060, +0.0125] | -0.0024 [-0.0117, +0.0057] | 0.891 | 0.462 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 171 | 0.493 | 0.398 | 0.0647 | +0.0061 [-0.0011, +0.0126] | -0.0023 [-0.0090, +0.0037] | 0.855 | 0.433 | no |
| 5 | 0.455 (147 of 1869 days never flag) | 192 | 0.543 | 0.391 | 0.0727 | -0.0018 [-0.0108, +0.0060] | -0.0093 [-0.0181, -0.0018] | 0.814 | 0.476 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.513 (climatology 0.512, difference +0.0013 [-0.0974, +0.1058]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0873, ΔBrier vs climatology +0.0422 [+0.0274, +0.0587], realised minus predicted +0.0217 [-0.0109, +0.0567]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.394 | 0.3139 | 0.2720 | +0.0138 [-0.0278, +0.0533] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0927 | 0.0159 | +0.0113 [-0.0168, +0.0345] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0028 | 0.0200 | +0.0038 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.611 | 0.0764 | 0.1165 | +0.0302 [+0.0088, +0.0588] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0018 | 0.0048 | +0.0095 [+0.0080, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0069 | 0.0000 | +0.0309 [+0.0243, +0.0373] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0457 | 0.2439 | 0.0276 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.398 | 0.3240 | 0.2615 | +0.0127 [-0.0242, +0.0488] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1075 | 0.1133 | +0.0411 [+0.0185, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.346 | 0.0799 | 0.0630 | +0.0068 [-0.0033, +0.0166] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0383, +0.1920] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0481, +0.0937] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2894 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.300, 0.700] | 0.276 | 5.88 flat / 2.80 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.269 | 4.69 flat / 2.14 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.300, 0.700] | 4.808 [2.900, 7.656] | 2.221 [1.255, 3.742] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.207, 0.579] | 4.769 [2.814, 7.637] | 2.096 [1.137, 3.552] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.346 [2.400, 7.143] | 1.942 [0.968, 3.456] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.885 [2.077, 6.445] | 1.779 [0.837, 3.250] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.962 [2.142, 6.601] | 1.904 [0.917, 3.536] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.529 [4.583, 12.357] | 3.441 [1.962, 6.017] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.778 [1.118, 7.000] | 1.583 [0.500, 4.550] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (126 of 1873 days never flag) | 212 | 0.621 | 0.410 | 0.0578 | +0.0136 [+0.0042, +0.0233] | -0.0014 [-0.0095, +0.0063] | 0.920 | 0.549 | yes |
| 2 | 0.575 (147 of 1872 days never flag) | 203 | 0.568 | 0.389 | 0.0671 | +0.0040 [-0.0050, +0.0118] | -0.0060 [-0.0147, +0.0016] | 0.878 | 0.497 | no |
| 3 | 0.534 (147 of 1871 days never flag) | 186 | 0.529 | 0.392 | 0.0663 | +0.0044 [-0.0059, +0.0132] | -0.0019 [-0.0117, +0.0065] | 0.893 | 0.464 | no |
| 4 | 0.527 (147 of 1870 days never flag) | 166 | 0.471 | 0.392 | 0.0632 | +0.0076 [+0.0007, +0.0138] | -0.0008 [-0.0074, +0.0055] | 0.883 | 0.413 | yes |
| 5 | 0.449 (147 of 1869 days never flag) | 165 | 0.449 | 0.376 | 0.0672 | +0.0037 [-0.0026, +0.0097] | -0.0038 [-0.0098, +0.0020] | 0.814 | 0.390 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.406 | 0.3174 | 0.2720 | +0.0113 [-0.0310, +0.0525] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0912 | 0.0159 | +0.0118 [-0.0144, +0.0351] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0011 [-0.0041, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0745 | 0.1165 | +0.0311 [+0.0100, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0313 [+0.0247, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0503 | 0.2439 | 0.0401 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.410 | 0.3262 | 0.2615 | +0.0100 [-0.0267, +0.0460] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1056 | 0.1133 | +0.0446 [+0.0230, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.360 | 0.0806 | 0.0630 | +0.0056 [-0.0046, +0.0156] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0331, +0.1941] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0477, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2827 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.305, 0.700] | 0.297 | 6.27 flat / 3.12 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.276, 0.655] | 0.269 | 4.62 flat / 2.20 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.305, 0.700] | 5.115 [3.193, 7.901] | 2.481 [1.426, 4.174] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.654 [2.889, 7.222] | 2.144 [1.240, 3.540] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.115 [2.381, 6.525] | 1.971 [1.069, 3.334] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 3.885 [2.130, 6.287] | 1.904 [0.981, 3.318] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.115 [2.357, 6.667] | 2.010 [1.028, 3.490] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.391, 0.889] | 7.471 [4.651, 12.455] | 3.529 [1.986, 6.400] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.000 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (126 of 1873 days never flag) | 222 | 0.636 | 0.401 | 0.0571 | +0.0143 [+0.0049, +0.0236] | -0.0008 [-0.0089, +0.0074] | 0.920 | 0.559 | yes |
| 2 | 0.435 (147 of 1872 days never flag) | 208 | 0.626 | 0.418 | 0.0605 | +0.0106 [+0.0011, +0.0196] | +0.0006 [-0.0085, +0.0089] | 0.897 | 0.556 | yes |
| 3 | 0.428 (147 of 1871 days never flag) | 189 | 0.594 | 0.434 | 0.0617 | +0.0090 [-0.0014, +0.0185] | +0.0027 [-0.0074, +0.0121] | 0.902 | 0.532 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 170 | 0.500 | 0.406 | 0.0609 | +0.0099 [+0.0024, +0.0175] | +0.0014 [-0.0063, +0.0088] | 0.868 | 0.442 | no |
| 5 | 0.455 (147 of 1869 days never flag) | 178 | 0.514 | 0.399 | 0.0671 | +0.0038 [-0.0055, +0.0123] | -0.0037 [-0.0128, +0.0044] | 0.849 | 0.453 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1658 [+0.0511, +0.2833]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0798, ΔBrier vs climatology +0.0497 [+0.0304, +0.0710], realised minus predicted -0.0023 [-0.0328, +0.0309]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.394 | 0.3139 | 0.2720 | +0.0138 [-0.0264, +0.0547] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0927 | 0.0159 | +0.0113 [-0.0177, +0.0349] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0158] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0028 | 0.0200 | +0.0038 [+0.0000, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.611 | 0.0764 | 0.1165 | +0.0302 [+0.0089, +0.0569] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0018 | 0.0048 | +0.0095 [+0.0078, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0069 | 0.0000 | +0.0309 [+0.0245, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0457 | 0.2439 | 0.0276 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.398 | 0.3240 | 0.2615 | +0.0127 [-0.0222, +0.0491] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1075 | 0.1133 | +0.0411 [+0.0176, +0.0659] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.346 | 0.0799 | 0.0630 | +0.0068 [-0.0030, +0.0163] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0335, +0.1895] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0493, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2894 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.708] | 0.269 | 5.65 flat / 2.75 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.294, 0.714] | 0.269 | 4.92 flat / 2.33 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.708] | 4.808 [2.878, 7.334] | 2.221 [1.232, 3.598] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 4.192 [2.363, 6.560] | 1.913 [0.977, 3.207] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.304, 0.708] | 4.346 [2.406, 6.927] | 1.962 [0.981, 3.343] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.846 [1.971, 6.300] | 1.913 [0.921, 3.369] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 4.000 [2.219, 6.391] | 1.990 [1.006, 3.438] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.059 [4.111, 11.638] | 3.206 [1.739, 5.567] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 3.000 [1.333, 6.800] | 1.889 [0.656, 4.952] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (126 of 1873 days never flag) | 212 | 0.621 | 0.410 | 0.0578 | +0.0136 [+0.0042, +0.0229] | -0.0014 [-0.0098, +0.0062] | 0.920 | 0.549 | yes |
| 2 | 0.526 (147 of 1872 days never flag) | 192 | 0.597 | 0.432 | 0.0613 | +0.0097 [+0.0007, +0.0186] | -0.0003 [-0.0089, +0.0081] | 0.893 | 0.534 | yes |
| 3 | 0.652 (147 of 1871 days never flag) | 196 | 0.601 | 0.423 | 0.0614 | +0.0093 [-0.0014, +0.0186] | +0.0030 [-0.0074, +0.0120] | 0.900 | 0.536 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 171 | 0.514 | 0.415 | 0.0583 | +0.0125 [+0.0049, +0.0201] | +0.0041 [-0.0035, +0.0116] | 0.895 | 0.457 | yes |
| 5 | 0.449 (147 of 1869 days never flag) | 174 | 0.507 | 0.402 | 0.0610 | +0.0099 [+0.0031, +0.0164] | +0.0024 [-0.0044, +0.0091] | 0.852 | 0.447 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.406 | 0.3174 | 0.2720 | +0.0113 [-0.0297, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0912 | 0.0159 | +0.0118 [-0.0167, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0011 [-0.0043, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0745 | 0.1165 | +0.0311 [+0.0103, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0313 [+0.0246, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0503 | 0.2439 | 0.0401 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.410 | 0.3262 | 0.2615 | +0.0100 [-0.0269, +0.0462] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1056 | 0.1133 | +0.0446 [+0.0225, +0.0699] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.360 | 0.0806 | 0.0630 | +0.0056 [-0.0047, +0.0155] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0355, +0.1932] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0488, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2827 | 0.2213 |

## risk_gbm_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.769] | 0.346 | 6.50 flat / 3.51 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.269 | 5.12 flat / 2.57 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.333, 0.741] | 5.077 [3.090, 7.880] | 2.500 [1.398, 4.195] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.243, 0.607] | 4.769 [2.789, 7.483] | 2.125 [1.143, 3.550] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.462 [2.500, 7.235] | 2.077 [1.080, 3.536] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 4.077 [2.192, 6.667] | 2.038 [0.941, 3.636] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.571] | 4.538 [2.522, 7.333] | 2.125 [1.056, 3.662] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.824 [4.857, 12.369] | 3.735 [2.111, 6.377] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.083, 0.778] | 4.000 [1.583, 10.000] | 3.083 [1.018, 8.709] |

Recall with equal weight per regime: 0.362 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (126 of 1873 days never flag) | 221 | 0.636 | 0.403 | 0.0507 | +0.0207 [+0.0130, +0.0294] | +0.0056 [-0.0003, +0.0117] | 0.905 | 0.560 | yes |
| 2 | 0.444 (147 of 1872 days never flag) | 206 | 0.590 | 0.398 | 0.0614 | +0.0097 [+0.0043, +0.0152] | -0.0003 [-0.0057, +0.0047] | 0.852 | 0.518 | no |
| 3 | 0.403 (147 of 1871 days never flag) | 190 | 0.536 | 0.389 | 0.0608 | +0.0099 [+0.0055, +0.0145] | +0.0035 [-0.0007, +0.0078] | 0.857 | 0.469 | no |
| 4 | 0.376 (147 of 1870 days never flag) | 173 | 0.486 | 0.387 | 0.0608 | +0.0100 [+0.0048, +0.0151] | +0.0015 [-0.0034, +0.0064] | 0.839 | 0.424 | no |
| 5 | 0.426 (147 of 1869 days never flag) | 191 | 0.529 | 0.382 | 0.0692 | +0.0018 [-0.0037, +0.0070] | -0.0058 [-0.0118, -0.0000] | 0.777 | 0.461 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.508 (climatology 0.512, difference -0.0047 [-0.1012, +0.0944]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0260, +0.0553], realised minus predicted +0.0193 [-0.0152, +0.0546]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.394 | 0.2748 | 0.2720 | +0.0425 [+0.0112, +0.0777] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1312 | 0.0159 | +0.0148 [-0.0056, +0.0328] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0038 [+0.0003, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.846 | 0.0741 | 0.1165 | +0.0325 [+0.0094, +0.0629] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0039 | 0.0048 | +0.0095 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0541 | 0.0000 | +0.0275 [+0.0216, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0740 | 0.2439 | 0.0262 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.397 | 0.2861 | 0.2615 | +0.0402 [+0.0106, +0.0725] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1088 | 0.1133 | +0.0418 [+0.0186, +0.0685] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.348 | 0.0797 | 0.0630 | +0.0142 [+0.0067, +0.0227] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0390, +0.1911] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0478, +0.0949] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2803 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.333, 0.739] | 0.299 | 6.31 flat / 3.45 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.621] | 0.269 | 5.19 flat / 2.75 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.333, 0.739] | 4.654 [2.739, 7.308] | 2.221 [1.211, 3.702] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.808 [2.771, 7.525] | 2.192 [1.141, 3.667] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.233, 0.615] | 4.308 [2.299, 6.951] | 1.923 [0.901, 3.340] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.577 [2.417, 7.648] | 2.529 [1.134, 4.613] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 3.846 [1.952, 6.500] | 1.846 [0.790, 3.372] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.895] | 7.529 [4.611, 12.429] | 3.441 [1.922, 6.036] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.000 [1.077, 10.750] | 3.472 [0.611, 10.102] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (126 of 1873 days never flag) | 206 | 0.607 | 0.413 | 0.0512 | +0.0202 [+0.0127, +0.0282] | +0.0051 [-0.0008, +0.0110] | 0.904 | 0.537 | yes |
| 2 | 0.452 (147 of 1872 days never flag) | 205 | 0.576 | 0.390 | 0.0620 | +0.0090 [+0.0034, +0.0147] | -0.0010 [-0.0067, +0.0043] | 0.850 | 0.503 | no |
| 3 | 0.368 (147 of 1871 days never flag) | 187 | 0.543 | 0.401 | 0.0605 | +0.0102 [+0.0054, +0.0150] | +0.0038 [-0.0009, +0.0083] | 0.855 | 0.479 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 183 | 0.464 | 0.350 | 0.0605 | +0.0103 [+0.0054, +0.0151] | +0.0019 [-0.0032, +0.0068] | 0.845 | 0.395 | yes |
| 5 | 0.489 (147 of 1869 days never flag) | 161 | 0.442 | 0.379 | 0.0672 | +0.0037 [-0.0011, +0.0090] | -0.0038 [-0.0091, +0.0017] | 0.784 | 0.384 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.491 (climatology 0.512, difference -0.0213 [-0.1310, +0.0810]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0876, ΔBrier vs climatology +0.0419 [+0.0284, +0.0573], realised minus predicted +0.0228 [-0.0103, +0.0591]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.406 | 0.2794 | 0.2720 | +0.0407 [+0.0093, +0.0725] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1302 | 0.0159 | +0.0155 [-0.0048, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0013 | 0.0200 | +0.0011 [-0.0042, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0716 | 0.1165 | +0.0333 [+0.0106, +0.0610] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0034 | 0.0048 | +0.0089 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0542 | 0.0000 | +0.0276 [+0.0213, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0747 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.410 | 0.2885 | 0.2615 | +0.0382 [+0.0100, +0.0682] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.1068 | 0.1133 | +0.0449 [+0.0232, +0.0695] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.363 | 0.0808 | 0.0630 | +0.0132 [+0.0059, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0320, +0.1895] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0481, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2732 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.774] | 0.288 | 6.12 flat / 3.21 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.308, 0.682] | 0.269 | 4.69 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.346, 0.743] | 5.077 [3.166, 8.000] | 2.500 [1.454, 4.167] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.308 [2.536, 6.889] | 2.029 [1.121, 3.375] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.077 [2.350, 6.561] | 1.952 [1.066, 3.350] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.312, 0.696] | 4.077 [2.261, 6.709] | 2.154 [1.120, 3.845] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.038 [2.260, 6.651] | 1.990 [1.022, 3.523] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.909] | 7.471 [4.524, 12.377] | 3.529 [1.966, 6.344] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.556 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.362 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (126 of 1873 days never flag) | 221 | 0.636 | 0.403 | 0.0507 | +0.0207 [+0.0129, +0.0295] | +0.0056 [-0.0004, +0.0116] | 0.905 | 0.560 | yes |
| 2 | 0.435 (147 of 1872 days never flag) | 196 | 0.604 | 0.429 | 0.0547 | +0.0164 [+0.0092, +0.0237] | +0.0064 [-0.0006, +0.0133] | 0.877 | 0.540 | yes |
| 3 | 0.428 (147 of 1871 days never flag) | 188 | 0.594 | 0.436 | 0.0551 | +0.0155 [+0.0093, +0.0220] | +0.0092 [+0.0030, +0.0157] | 0.872 | 0.533 | yes |
| 4 | 0.522 (147 of 1870 days never flag) | 175 | 0.500 | 0.394 | 0.0567 | +0.0141 [+0.0080, +0.0206] | +0.0056 [-0.0009, +0.0126] | 0.848 | 0.439 | no |
| 5 | 0.426 (147 of 1869 days never flag) | 174 | 0.500 | 0.397 | 0.0631 | +0.0078 [+0.0012, +0.0140] | +0.0003 [-0.0065, +0.0070] | 0.821 | 0.439 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.394 | 0.2748 | 0.2720 | +0.0425 [+0.0109, +0.0762] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1312 | 0.0159 | +0.0148 [-0.0050, +0.0317] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0038 [+0.0001, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.846 | 0.0741 | 0.1165 | +0.0325 [+0.0098, +0.0625] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0039 | 0.0048 | +0.0095 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0541 | 0.0000 | +0.0275 [+0.0215, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0740 | 0.2439 | 0.0262 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.397 | 0.2861 | 0.2615 | +0.0402 [+0.0102, +0.0720] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1088 | 0.1133 | +0.0418 [+0.0172, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.348 | 0.0797 | 0.0630 | +0.0142 [+0.0068, +0.0228] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0328, +0.1876] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0931] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2803 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.345, 0.742] | 0.282 | 6.00 flat / 3.32 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.304, 0.714] | 0.269 | 5.50 flat / 2.96 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.345, 0.742] | 4.654 [2.817, 7.174] | 2.221 [1.257, 3.646] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.077 [2.371, 6.500] | 1.875 [1.000, 3.261] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.308, 0.714] | 4.500 [2.640, 7.112] | 2.087 [1.132, 3.555] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.500 [2.500, 7.612] | 2.567 [1.202, 4.786] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.500 [2.533, 7.588] | 2.548 [1.204, 4.678] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.409, 0.900] | 7.059 [4.333, 11.455] | 3.206 [1.804, 5.525] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.000 [1.250, 11.200] | 3.528 [0.841, 10.752] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (126 of 1873 days never flag) | 206 | 0.607 | 0.413 | 0.0512 | +0.0202 [+0.0125, +0.0280] | +0.0051 [-0.0009, +0.0109] | 0.904 | 0.537 | yes |
| 2 | 0.526 (147 of 1872 days never flag) | 189 | 0.597 | 0.439 | 0.0556 | +0.0155 [+0.0089, +0.0228] | +0.0055 [-0.0008, +0.0123] | 0.871 | 0.536 | yes |
| 3 | 0.363 (147 of 1871 days never flag) | 202 | 0.616 | 0.421 | 0.0549 | +0.0158 [+0.0100, +0.0219] | +0.0095 [+0.0038, +0.0153] | 0.867 | 0.548 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 188 | 0.514 | 0.378 | 0.0551 | +0.0157 [+0.0095, +0.0225] | +0.0072 [+0.0007, +0.0142] | 0.863 | 0.447 | yes |
| 5 | 0.528 (147 of 1869 days never flag) | 186 | 0.500 | 0.371 | 0.0608 | +0.0101 [+0.0037, +0.0166] | +0.0026 [-0.0041, +0.0092] | 0.826 | 0.432 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.512, difference +0.2074 [+0.0613, +0.3406]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0781, ΔBrier vs climatology +0.0514 [+0.0325, +0.0715], realised minus predicted -0.0023 [-0.0322, +0.0283]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.406 | 0.2794 | 0.2720 | +0.0407 [+0.0091, +0.0712] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1302 | 0.0159 | +0.0155 [-0.0040, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0013 | 0.0200 | +0.0011 [-0.0050, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0716 | 0.1165 | +0.0333 [+0.0108, +0.0615] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0034 | 0.0048 | +0.0089 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0542 | 0.0000 | +0.0276 [+0.0213, +0.0337] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0747 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.410 | 0.2885 | 0.2615 | +0.0382 [+0.0087, +0.0667] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.1068 | 0.1133 | +0.0449 [+0.0227, +0.0693] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.363 | 0.0808 | 0.0630 | +0.0132 [+0.0058, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0286, +0.1963] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0478, +0.0962] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2732 | 0.2213 |

## risk_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.231 | 3.23 flat / 2.47 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.552] | 0.192 | 2.31 flat / 1.73 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.769] | 2.192 [1.500, 3.408] | 1.538 [0.960, 2.548] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.846 [1.162, 2.923] | 1.375 [0.789, 2.352] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.167, 0.469] | 1.769 [1.138, 2.778] | 1.221 [0.700, 2.111] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.233, 0.552] | 2.115 [1.368, 3.360] | 1.625 [0.942, 2.750] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.387, 3.364] | 1.577 [0.892, 2.704] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 6.556 (no interval) | 5.806 (no interval) |

Recall with equal weight per regime: 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0478 (105 of 1873 days never flag) | 103 | 0.329 | 0.447 | 0.0600 | +0.0114 [+0.0062, +0.0165] | -0.0037 [-0.0121, +0.0040] | 0.642 | 0.296 | no |
| 2 | 0.0131 (147 of 1872 days never flag) | 76 | 0.201 | 0.368 | 0.0678 | +0.0032 [-0.0033, +0.0091] | -0.0068 [-0.0148, +0.0004] | 0.579 | 0.174 | no |
| 3 | 0.118 (147 of 1871 days never flag) | 75 | 0.210 | 0.387 | 0.0687 | +0.0019 [-0.0054, +0.0087] | -0.0044 [-0.0133, +0.0033] | 0.578 | 0.184 | no |
| 4 | 0.0243 (147 of 1870 days never flag) | 86 | 0.225 | 0.360 | 0.0689 | +0.0019 [-0.0049, +0.0081] | -0.0065 [-0.0151, +0.0011] | 0.578 | 0.193 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 86 | 0.217 | 0.349 | 0.0693 | +0.0016 [-0.0056, +0.0080] | -0.0059 [-0.0144, +0.0015] | 0.577 | 0.185 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.588 (climatology 0.512, difference +0.0754 [-0.0491, +0.1806]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1079, ΔBrier vs climatology +0.0216 [+0.0098, +0.0329], realised minus predicted +0.0742 [+0.0405, +0.1110]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1071 | 0.2720 | -0.0038 [-0.0245, +0.0163] |
| regime | 2020 | 251 | 4 | 0.250 | 0.043 | 0.0283 | 0.0159 | +0.0266 [+0.0104, +0.0402] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0048 | 0.0200 | +0.0049 [+0.0006, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.619 | 0.0382 | 0.1165 | +0.0183 [+0.0033, +0.0374] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.143 | 0.0025 | 0.0048 | +0.0094 [+0.0077, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0041 | 0.0000 | +0.0308 [+0.0245, +0.0367] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.500 | 0.0741 | 0.2439 | -0.0329 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.538 | 0.1072 | 0.2615 | +0.0069 [-0.0120, +0.0248] |
| day_type | month_end | 150 | 17 | 0.765 | 0.419 | 0.1048 | 0.1133 | +0.0284 [+0.0008, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.447 | 0.0125 | 0.0630 | +0.0043 [-0.0009, +0.0090] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3499 | 0.2903 | +0.1030 [+0.0321, +0.1692] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.476 | 0.1308 | 0.1461 | +0.0798 [+0.0478, +0.1161] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2023 | 0.2213 |

## risk_logistic+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.718] | 0.385 | 7.23 flat / 3.40 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.282 | 6.04 flat / 2.79 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.560] | 4.269 [2.615, 6.543] | 1.875 [1.089, 3.013] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.205, 7.364] | 2.067 [1.250, 3.264] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 4.615 [2.846, 7.113] | 2.029 [1.182, 3.250] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.269 [2.615, 6.551] | 1.885 [1.081, 3.092] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.645] | 4.962 [3.103, 7.519] | 2.202 [1.312, 3.501] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.824] | 6.471 [3.949, 10.267] | 2.574 [1.425, 4.376] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.667 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 199 | 0.629 | 0.442 | 0.0501 | +0.0213 [+0.0138, +0.0290] | +0.0062 [+0.0006, +0.0117] | 0.879 | 0.565 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 223 | 0.676 | 0.422 | 0.0593 | +0.0118 [+0.0060, +0.0178] | +0.0018 [-0.0029, +0.0064] | 0.841 | 0.602 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 203 | 0.601 | 0.409 | 0.0626 | +0.0080 [+0.0014, +0.0146] | +0.0017 [-0.0046, +0.0076] | 0.812 | 0.532 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 181 | 0.507 | 0.387 | 0.0614 | +0.0094 [+0.0033, +0.0152] | +0.0009 [-0.0048, +0.0065] | 0.820 | 0.443 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 212 | 0.601 | 0.392 | 0.0627 | +0.0083 [+0.0031, +0.0136] | +0.0007 [-0.0039, +0.0051] | 0.797 | 0.527 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.621 (climatology 0.512, difference +0.1086 [+0.0223, +0.1877]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0406 [+0.0244, +0.0581], realised minus predicted -0.0058 [-0.0354, +0.0263]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.453 | 0.2485 | 0.2720 | +0.0519 [+0.0244, +0.0802] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1310 | 0.0159 | +0.0103 [-0.0136, +0.0275] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0188 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0349 | 0.0200 | +0.0019 [-0.0051, +0.0080] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.576 | 0.1145 | 0.1165 | +0.0303 [+0.0036, +0.0614] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0241 | 0.0048 | +0.0078 [+0.0056, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0674 | 0.0000 | +0.0244 [+0.0187, +0.0299] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.500 | 0.1946 | 0.2439 | 0.0094 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.448 | 0.2576 | 0.2615 | +0.0497 [+0.0238, +0.0757] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1142 | 0.1133 | +0.0335 [+0.0050, +0.0634] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.396 | 0.0859 | 0.0630 | +0.0153 [+0.0084, +0.0225] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0288, +0.1764] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0482, +0.1158] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3403 | 0.2213 |

## risk_logistic+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.478, 0.818] | 0.418 | 8.00 flat / 4.06 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.667] | 0.286 | 6.12 flat / 3.12 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.645] | 3.808 [2.750, 5.313] | 1.750 [1.212, 2.562] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 3.846 [2.577, 5.601] | 1.558 [1.033, 2.326] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.462] | 3.423 [2.182, 5.211] | 1.510 [0.951, 2.360] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.120, 0.419] | 3.731 [2.535, 5.438] | 1.817 [1.192, 2.750] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.321, 0.680] | 4.269 [2.857, 6.292] | 2.067 [1.398, 3.070] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.765 [4.545, 10.167] | 2.750 [1.815, 4.173] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.333 (no interval) | 6.528 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0864 (105 of 1873 days never flag) | 183 | 0.600 | 0.459 | 0.0519 | +0.0195 [+0.0127, +0.0271] | +0.0044 [-0.0011, +0.0101] | 0.802 | 0.543 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 177 | 0.554 | 0.435 | 0.0615 | +0.0095 [+0.0036, +0.0156] | -0.0005 [-0.0054, +0.0045] | 0.752 | 0.496 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 158 | 0.500 | 0.437 | 0.0627 | +0.0080 [+0.0011, +0.0146] | +0.0017 [-0.0047, +0.0079] | 0.746 | 0.449 | no |
| 4 | 0.107 (147 of 1870 days never flag) | 157 | 0.435 | 0.382 | 0.0623 | +0.0085 [+0.0028, +0.0143] | +0.0001 [-0.0054, +0.0056] | 0.758 | 0.379 | no |
| 5 | 0.103 (147 of 1869 days never flag) | 184 | 0.529 | 0.397 | 0.0633 | +0.0076 [+0.0020, +0.0131] | +0.0001 [-0.0049, +0.0048] | 0.743 | 0.465 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0979 [-0.0161, +0.1873]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0913, ΔBrier vs climatology +0.0382 [+0.0211, +0.0539], realised minus predicted +0.0444 [+0.0151, +0.0726]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.504 | 0.1788 | 0.2720 | +0.0363 [+0.0110, +0.0633] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0359 | 0.0159 | +0.0193 [-0.0051, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0173 | 0.0200 | +0.0020 [-0.0056, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.513 | 0.0894 | 0.1165 | +0.0294 [+0.0050, +0.0613] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.111 | 0.0102 | 0.0048 | +0.0081 [+0.0057, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0053 | 0.0000 | +0.0307 [+0.0244, +0.0370] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.417 | 0.1636 | 0.2439 | 0.0072 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.491 | 0.1811 | 0.2615 | +0.0381 [+0.0154, +0.0633] |
| day_type | month_end | 150 | 17 | 0.824 | 0.519 | 0.1087 | 0.1133 | +0.0340 [+0.0044, +0.0651] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.433 | 0.0417 | 0.0630 | +0.0131 [+0.0069, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3499 | 0.2903 | +0.1030 [+0.0283, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1308 | 0.1461 | +0.0798 [+0.0501, +0.1180] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3843 | 0.2213 |

## risk_logistic+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.419, 0.741] | 0.373 | 6.92 flat / 3.23 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.677] | 0.271 | 5.85 flat / 2.68 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.630] | 4.731 [3.000, 7.044] | 2.212 [1.350, 3.448] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.759, 6.953] | 1.875 [1.060, 3.074] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.263, 0.588] | 4.269 [2.588, 6.700] | 1.846 [1.052, 3.063] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.500 [2.749, 6.875] | 2.115 [1.203, 3.393] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.640] | 5.154 [3.240, 7.786] | 2.298 [1.365, 3.632] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.917] | 7.941 [5.222, 12.375] | 3.368 [2.016, 5.614] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.100, 0.556] | 5.000 [2.667, 10.667] | 2.972 [1.515, 6.876] |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (126 of 1873 days never flag) | 203 | 0.571 | 0.394 | 0.0502 | +0.0212 [+0.0143, +0.0282] | +0.0062 [+0.0011, +0.0115] | 0.876 | 0.500 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 204 | 0.626 | 0.426 | 0.0583 | +0.0128 [+0.0078, +0.0180] | +0.0028 [-0.0021, +0.0078] | 0.830 | 0.558 | no |
| 3 | 0.248 (147 of 1871 days never flag) | 190 | 0.572 | 0.416 | 0.0611 | +0.0096 [+0.0028, +0.0157] | +0.0032 [-0.0034, +0.0097] | 0.805 | 0.508 | yes |
| 4 | 0.243 (147 of 1870 days never flag) | 180 | 0.457 | 0.350 | 0.0602 | +0.0106 [+0.0058, +0.0156] | +0.0021 [-0.0031, +0.0077] | 0.812 | 0.389 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 213 | 0.572 | 0.371 | 0.0610 | +0.0100 [+0.0053, +0.0142] | +0.0024 [-0.0023, +0.0069] | 0.792 | 0.495 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1023 [+0.0175, +0.1786]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0899, ΔBrier vs climatology +0.0395 [+0.0240, +0.0564], realised minus predicted +0.0037 [-0.0282, +0.0364]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.385 | 0.2314 | 0.2720 | +0.0463 [+0.0212, +0.0731] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1169 | 0.0159 | +0.0160 [-0.0038, +0.0306] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0133 [+0.0115, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0263 | 0.0200 | +0.0041 [-0.0004, +0.0087] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.579 | 0.0994 | 0.1165 | +0.0299 [+0.0064, +0.0589] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0192 | 0.0048 | +0.0088 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0583 | 0.0000 | +0.0256 [+0.0200, +0.0310] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1671 | 0.2439 | 0.0068 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.400 | 0.2389 | 0.2615 | +0.0467 [+0.0235, +0.0698] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1128 | 0.1133 | +0.0326 [+0.0030, +0.0610] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.338 | 0.0748 | 0.0630 | +0.0153 [+0.0092, +0.0221] |
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
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.361 | 6.73 flat / 3.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 5.62 flat / 2.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.192 [2.552, 6.522] | 1.856 [1.083, 3.060] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.846 [3.093, 7.333] | 2.019 [1.225, 3.250] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 4.423 [2.708, 6.923] | 1.933 [1.143, 3.210] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.077 [2.440, 6.429] | 1.779 [1.012, 2.956] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.808 [2.961, 7.417] | 2.087 [1.212, 3.368] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.833] | 6.471 [3.765, 10.714] | 2.574 [1.381, 4.526] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.222 (no interval) | 4.111 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 197 | 0.629 | 0.447 | 0.0492 | +0.0222 [+0.0147, +0.0304] | +0.0071 [+0.0017, +0.0130] | 0.907 | 0.566 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 220 | 0.676 | 0.427 | 0.0584 | +0.0127 [+0.0069, +0.0183] | +0.0027 [-0.0018, +0.0076] | 0.882 | 0.604 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 198 | 0.601 | 0.419 | 0.0607 | +0.0100 [+0.0036, +0.0165] | +0.0036 [-0.0028, +0.0098] | 0.866 | 0.535 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 177 | 0.514 | 0.401 | 0.0600 | +0.0109 [+0.0051, +0.0166] | +0.0024 [-0.0033, +0.0078] | 0.863 | 0.453 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 208 | 0.601 | 0.399 | 0.0615 | +0.0094 [+0.0043, +0.0144] | +0.0019 [-0.0028, +0.0063] | 0.851 | 0.529 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.621 (climatology 0.512, difference +0.1086 [+0.0217, +0.1862]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0872, ΔBrier vs climatology +0.0423 [+0.0261, +0.0597], realised minus predicted +0.0203 [-0.0110, +0.0514]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.453 | 0.2485 | 0.2720 | +0.0519 [+0.0251, +0.0810] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1307 | 0.0159 | +0.0103 [-0.0121, +0.0280] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0049 | 0.0200 | +0.0049 [+0.0006, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.594 | 0.0979 | 0.1165 | +0.0327 [+0.0063, +0.0644] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0025 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0674 | 0.0000 | +0.0244 [+0.0188, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.500 | 0.1946 | 0.2439 | 0.0094 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.448 | 0.2576 | 0.2615 | +0.0497 [+0.0238, +0.0758] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1121 | 0.1133 | +0.0336 [+0.0051, +0.0659] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.401 | 0.0721 | 0.0630 | +0.0164 [+0.0097, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0305, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0490, +0.1171] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3403 | 0.2213 |

## risk_logistic+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.852] | 0.397 | 7.65 flat / 3.69 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.368, 0.714] | 0.282 | 6.04 flat / 2.89 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.759] | 5.154 [3.479, 7.600] | 2.279 [1.464, 3.515] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.257, 0.606] | 4.923 [3.193, 7.456] | 2.115 [1.281, 3.355] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 4.154 [2.444, 6.600] | 1.856 [1.045, 3.114] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.385 [2.758, 6.793] | 2.010 [1.214, 3.250] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.231 [3.353, 7.895] | 2.394 [1.507, 3.781] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.588, 11.365] | 2.926 [1.720, 5.002] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 8.556 [5.375, 16.671] | 5.139 [2.979, 11.381] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.185 (126 of 1873 days never flag) | 231 | 0.693 | 0.420 | 0.0506 | +0.0208 [+0.0154, +0.0264] | +0.0057 [+0.0003, +0.0110] | 0.887 | 0.616 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 224 | 0.691 | 0.429 | 0.0595 | +0.0115 [+0.0070, +0.0161] | +0.0015 [-0.0033, +0.0064] | 0.843 | 0.617 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 186 | 0.565 | 0.419 | 0.0618 | +0.0088 [+0.0032, +0.0145] | +0.0025 [-0.0036, +0.0084] | 0.814 | 0.503 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 187 | 0.529 | 0.390 | 0.0613 | +0.0096 [+0.0052, +0.0138] | +0.0011 [-0.0040, +0.0063] | 0.827 | 0.463 | no |
| 5 | 0.123 (147 of 1869 days never flag) | 220 | 0.609 | 0.382 | 0.0621 | +0.0088 [+0.0045, +0.0129] | +0.0013 [-0.0039, +0.0059] | 0.808 | 0.530 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.512, difference +0.1011 [+0.0140, +0.1706]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0938, ΔBrier vs climatology +0.0356 [+0.0224, +0.0489], realised minus predicted +0.0355 [+0.0035, +0.0702]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.432 | 0.1778 | 0.2720 | +0.0375 [+0.0206, +0.0547] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0797 | 0.0159 | +0.0235 [+0.0056, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0095 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0198 | 0.0200 | +0.0043 [-0.0005, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.533 | 0.0763 | 0.1165 | +0.0309 [+0.0077, +0.0603] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0133 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0358 | 0.0000 | +0.0292 [+0.0230, +0.0351] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.375 | 0.1344 | 0.2439 | -0.0033 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.744 | 0.433 | 0.1824 | 0.2615 | +0.0429 [+0.0260, +0.0610] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1095 | 0.1133 | +0.0313 [+0.0035, +0.0611] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.382 | 0.0492 | 0.0630 | +0.0149 [+0.0107, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3499 | 0.2903 | +0.1030 [+0.0272, +0.1714] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1308 | 0.1461 | +0.0798 [+0.0487, +0.1176] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2194 | 0.2213 |

## risk_logistic+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.281, 0.636] | 0.271 | 5.81 flat / 2.80 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.640] | 0.269 | 5.12 flat / 2.47 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.444] | 3.885 [2.069, 6.319] | 1.769 [0.871, 3.001] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.385 [2.667, 6.734] | 1.798 [1.015, 2.888] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.524] | 3.846 [2.182, 6.087] | 1.683 [0.898, 2.792] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 3.462 [1.926, 5.589] | 1.606 [0.841, 2.700] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.524, 7.385] | 2.183 [1.131, 3.733] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.818] | 6.706 [3.909, 10.734] | 2.735 [1.467, 4.765] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.111 [2.000, 9.603] | 2.917 [1.179, 7.292] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 175 | 0.529 | 0.423 | 0.0629 | +0.0085 [-0.0016, +0.0187] | -0.0066 [-0.0158, +0.0021] | 0.870 | 0.470 | yes |
| 2 | 0.546 (147 of 1872 days never flag) | 199 | 0.612 | 0.427 | 0.0708 | +0.0002 [-0.0096, +0.0091] | -0.0098 [-0.0193, -0.0015] | 0.824 | 0.546 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 171 | 0.514 | 0.415 | 0.0746 | -0.0040 [-0.0143, +0.0057] | -0.0103 [-0.0203, -0.0008] | 0.796 | 0.457 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 150 | 0.435 | 0.400 | 0.0723 | -0.0014 [-0.0102, +0.0064] | -0.0099 [-0.0188, -0.0018] | 0.814 | 0.383 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 193 | 0.543 | 0.389 | 0.0725 | -0.0016 [-0.0088, +0.0052] | -0.0091 [-0.0161, -0.0022] | 0.779 | 0.475 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.598 (climatology 0.512, difference +0.0860 [+0.0076, +0.1469]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0339 [+0.0168, +0.0518], realised minus predicted -0.0138 [-0.0478, +0.0233]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.419 | 0.3229 | 0.2720 | +0.0077 [-0.0373, +0.0503] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2056 | 0.0159 | -0.0171 [-0.0410, +0.0042] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0017, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0680 | 0.1165 | +0.0296 [+0.0061, +0.0580] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0089 | 0.0048 | +0.0084 [+0.0065, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1119 | 0.0000 | +0.0111 [+0.0059, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1510 | 0.2439 | -0.0018 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.584 | 0.424 | 0.3208 | 0.2615 | +0.0078 [-0.0312, +0.0454] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.1156 | 0.1133 | +0.0309 [+0.0033, +0.0610] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.371 | 0.1023 | 0.0630 | +0.0006 [-0.0096, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0319, +0.1731] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1308 | 0.1461 | +0.0798 [+0.0493, +0.1168] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2902 | 0.2213 |

## risk_logistic+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.286 | 6.08 flat / 2.89 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.640] | 0.269 | 4.92 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 5.115 [3.227, 7.643] | 2.202 [1.286, 3.444] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.610] | 4.077 [2.400, 6.364] | 1.596 [0.855, 2.625] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.654 [1.938, 5.870] | 1.490 [0.741, 2.531] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 3.077 [1.542, 5.137] | 1.356 [0.629, 2.407] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.610] | 4.692 [2.733, 7.455] | 2.308 [1.235, 3.922] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.706 [5.000, 12.000] | 3.191 [1.889, 5.209] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 222 | 0.636 | 0.401 | 0.0629 | +0.0085 [-0.0018, +0.0187] | -0.0065 [-0.0156, +0.0020] | 0.870 | 0.559 | no |
| 2 | 0.543 (147 of 1872 days never flag) | 189 | 0.597 | 0.439 | 0.0694 | +0.0016 [-0.0078, +0.0100] | -0.0084 [-0.0166, -0.0009] | 0.824 | 0.536 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 167 | 0.522 | 0.431 | 0.0725 | -0.0018 [-0.0119, +0.0071] | -0.0081 [-0.0180, +0.0004] | 0.797 | 0.467 | yes |
| 4 | 0.631 (147 of 1870 days never flag) | 139 | 0.428 | 0.424 | 0.0713 | -0.0005 [-0.0086, +0.0071] | -0.0090 [-0.0174, -0.0011] | 0.816 | 0.381 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 197 | 0.543 | 0.381 | 0.0726 | -0.0017 [-0.0092, +0.0056] | -0.0092 [-0.0170, -0.0020] | 0.785 | 0.473 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.512, difference +0.0610 [-0.0127, +0.1206]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0931, ΔBrier vs climatology +0.0364 [+0.0205, +0.0534], realised minus predicted -0.0136 [-0.0454, +0.0211]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.399 | 0.3266 | 0.2720 | +0.0083 [-0.0374, +0.0521] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2046 | 0.0159 | -0.0171 [-0.0421, +0.0044] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0014, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0659 | 0.1165 | +0.0291 [+0.0061, +0.0562] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0088 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1110 | 0.0000 | +0.0114 [+0.0061, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1496 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.402 | 0.3229 | 0.2615 | +0.0078 [-0.0318, +0.0467] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1161 | 0.1133 | +0.0317 [+0.0021, +0.0620] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.355 | 0.1027 | 0.0630 | +0.0007 [-0.0099, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0330, +0.1761] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1173] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2900 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.714] | 0.269 | 4.92 flat / 2.30 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.360, 0.714] | 0.269 | 4.65 flat / 2.17 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.440] | 3.885 [2.125, 6.364] | 1.769 [0.885, 3.054] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.062, 0.350] | 3.538 [1.812, 5.910] | 1.683 [0.808, 2.973] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.480] | 3.731 [2.000, 6.177] | 1.721 [0.845, 3.052] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.227, 0.550] | 3.500 [2.000, 5.600] | 1.500 [0.804, 2.531] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.571] | 3.346 [1.815, 5.500] | 1.481 [0.760, 2.548] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.444, 0.867] | 6.588 [4.000, 10.616] | 2.735 [1.536, 4.688] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.778 [0.538, 4.500] | 1.472 [0.375, 4.000] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 175 | 0.529 | 0.423 | 0.0629 | +0.0085 [-0.0021, +0.0182] | -0.0066 [-0.0161, +0.0019] | 0.870 | 0.470 | no |
| 2 | 0.856 (147 of 1872 days never flag) | 153 | 0.439 | 0.399 | 0.0660 | +0.0050 [-0.0042, +0.0143] | -0.0050 [-0.0141, +0.0035] | 0.840 | 0.386 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 171 | 0.536 | 0.433 | 0.0675 | +0.0032 [-0.0072, +0.0125] | -0.0031 [-0.0130, +0.0061] | 0.827 | 0.480 | yes |
| 4 | 0.721 (126 of 1870 days never flag) | 158 | 0.486 | 0.424 | 0.0656 | +0.0052 [-0.0027, +0.0129] | -0.0032 [-0.0110, +0.0044] | 0.841 | 0.433 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 153 | 0.478 | 0.431 | 0.0651 | +0.0058 [-0.0015, +0.0125] | -0.0018 [-0.0085, +0.0051] | 0.827 | 0.428 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.657 | 0.419 | 0.3229 | 0.2720 | +0.0077 [-0.0387, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2056 | 0.0159 | -0.0171 [-0.0424, +0.0041] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0019, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0680 | 0.1165 | +0.0296 [+0.0061, +0.0595] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0089 | 0.0048 | +0.0084 [+0.0066, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1119 | 0.0000 | +0.0111 [+0.0056, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1510 | 0.2439 | -0.0018 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.584 | 0.424 | 0.3208 | 0.2615 | +0.0078 [-0.0320, +0.0450] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.1156 | 0.1133 | +0.0309 [+0.0025, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.371 | 0.1023 | 0.0630 | +0.0006 [-0.0105, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0291, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1308 | 0.1461 | +0.0798 [+0.0483, +0.1183] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2902 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.387, 0.762] | 0.269 | 5.54 flat / 2.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.321, 0.667] | 0.231 | 4.08 flat / 1.99 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.654] | 5.115 [3.267, 7.609] | 2.202 [1.331, 3.490] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.500] | 4.038 [2.154, 6.584] | 1.827 [0.930, 3.162] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.484] | 3.500 [1.786, 5.924] | 1.663 [0.793, 3.017] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.560] | 3.615 [1.941, 5.923] | 1.712 [0.833, 3.047] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.000 [1.467, 5.042] | 1.365 [0.636, 2.413] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 7.471 [4.882, 11.235] | 3.044 [1.879, 4.861] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.626] | 1.889 [0.500, 5.000] | 1.583 [0.375, 4.500] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 222 | 0.636 | 0.401 | 0.0629 | +0.0085 [-0.0012, +0.0190] | -0.0065 [-0.0154, +0.0022] | 0.870 | 0.559 | no |
| 2 | 0.866 (147 of 1872 days never flag) | 176 | 0.511 | 0.403 | 0.0661 | +0.0050 [-0.0047, +0.0140] | -0.0050 [-0.0144, +0.0039] | 0.843 | 0.450 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 155 | 0.464 | 0.413 | 0.0671 | +0.0036 [-0.0065, +0.0126] | -0.0027 [-0.0124, +0.0062] | 0.829 | 0.411 | yes |
| 4 | 0.8 (126 of 1870 days never flag) | 161 | 0.486 | 0.416 | 0.0651 | +0.0057 [-0.0027, +0.0138] | -0.0027 [-0.0112, +0.0052] | 0.842 | 0.431 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 139 | 0.442 | 0.439 | 0.0651 | +0.0058 [-0.0017, +0.0130] | -0.0017 [-0.0085, +0.0054] | 0.828 | 0.397 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1874 [+0.0633, +0.2930]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0799, ΔBrier vs climatology +0.0495 [+0.0307, +0.0693], realised minus predicted -0.0310 [-0.0595, -0.0007]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.399 | 0.3266 | 0.2720 | +0.0083 [-0.0344, +0.0524] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2046 | 0.0159 | -0.0171 [-0.0419, +0.0042] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0017, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0659 | 0.1165 | +0.0291 [+0.0060, +0.0568] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0088 | 0.0048 | +0.0085 [+0.0065, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1110 | 0.0000 | +0.0114 [+0.0057, +0.0172] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1496 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.402 | 0.3229 | 0.2615 | +0.0078 [-0.0292, +0.0471] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1161 | 0.1133 | +0.0317 [+0.0025, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.355 | 0.1027 | 0.0630 | +0.0007 [-0.0092, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0318, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1295 | 0.1461 | +0.0774 [+0.0436, +0.1153] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2900 | 0.2213 |

## risk_logistic+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.282, 0.650] | 0.269 | 5.69 flat / 2.68 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.650] | 0.269 | 4.69 flat / 2.12 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 3.808 [2.185, 6.067] | 1.740 [0.987, 2.903] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.462 [2.700, 6.914] | 1.856 [1.070, 3.034] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 3.885 [2.160, 6.227] | 1.702 [0.930, 2.863] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.516] | 3.462 [1.933, 5.667] | 1.596 [0.853, 2.775] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.192 [2.389, 6.696] | 1.856 [1.043, 3.084] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.826] | 6.294 [3.750, 10.232] | 2.500 [1.386, 4.417] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.556 [2.461, 9.252] | 3.028 [1.525, 6.702] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 178 | 0.564 | 0.444 | 0.0584 | +0.0130 [+0.0051, +0.0217] | -0.0021 [-0.0088, +0.0048] | 0.841 | 0.507 | yes |
| 2 | 0.473 (147 of 1872 days never flag) | 199 | 0.597 | 0.417 | 0.0690 | +0.0021 [-0.0044, +0.0086] | -0.0079 [-0.0143, -0.0014] | 0.781 | 0.530 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 176 | 0.543 | 0.426 | 0.0720 | -0.0013 [-0.0080, +0.0054] | -0.0076 [-0.0149, -0.0007] | 0.730 | 0.485 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 151 | 0.442 | 0.404 | 0.0712 | -0.0004 [-0.0069, +0.0060] | -0.0089 [-0.0159, -0.0019] | 0.752 | 0.390 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 185 | 0.551 | 0.411 | 0.0725 | -0.0016 [-0.0080, +0.0046] | -0.0091 [-0.0160, -0.0027] | 0.722 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.598 (climatology 0.512, difference +0.0854 [+0.0048, +0.1499]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0986, ΔBrier vs climatology +0.0309 [+0.0154, +0.0483], realised minus predicted -0.0308 [-0.0641, +0.0072]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.450 | 0.2940 | 0.2720 | +0.0337 [+0.0011, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2137 | 0.0159 | -0.0150 [-0.0358, +0.0017] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0089, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0137 | 0.0200 | +0.0038 [-0.0017, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0667 | 0.1165 | +0.0275 [+0.0065, +0.0547] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0222 | 0.0048 | +0.0080 [+0.0063, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1315 | 0.0000 | +0.0053 [+0.0006, +0.0107] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1281 | 0.2439 | -0.0229 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.453 | 0.2953 | 0.2615 | +0.0321 [+0.0027, +0.0631] |
| day_type | month_end | 150 | 17 | 0.588 | 0.556 | 0.1163 | 0.1133 | +0.0301 [+0.0016, +0.0583] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.400 | 0.1065 | 0.0630 | +0.0060 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0303, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0478, +0.1178] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2859 | 0.2213 |

## risk_logistic+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.373 | 6.92 flat / 3.42 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.645] | 0.269 | 5.42 flat / 2.70 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.370, 0.714] | 5.038 [3.319, 7.616] | 2.173 [1.350, 3.410] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.231 [2.500, 6.774] | 1.644 [0.905, 2.737] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.769 [2.071, 6.239] | 1.587 [0.826, 2.726] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.577 [2.000, 5.834] | 1.615 [0.850, 2.800] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.885 [2.823, 7.775] | 2.413 [1.299, 4.055] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.706 [5.071, 11.900] | 3.191 [1.916, 5.250] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.444 [2.857, 12.254] | 3.861 [1.775, 9.438] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.363 (126 of 1873 days never flag) | 226 | 0.679 | 0.420 | 0.0583 | +0.0131 [+0.0052, +0.0217] | -0.0020 [-0.0088, +0.0051] | 0.841 | 0.603 | yes |
| 2 | 0.489 (147 of 1872 days never flag) | 195 | 0.612 | 0.436 | 0.0676 | +0.0035 [-0.0029, +0.0096] | -0.0065 [-0.0125, -0.0006] | 0.781 | 0.548 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 172 | 0.536 | 0.430 | 0.0698 | +0.0008 [-0.0050, +0.0067] | -0.0055 [-0.0112, +0.0005] | 0.731 | 0.480 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 153 | 0.435 | 0.392 | 0.0703 | +0.0005 [-0.0057, +0.0069] | -0.0079 [-0.0145, -0.0010] | 0.754 | 0.381 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 203 | 0.551 | 0.374 | 0.0726 | -0.0017 [-0.0087, +0.0049] | -0.0092 [-0.0167, -0.0022] | 0.728 | 0.477 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.512, difference +0.0604 [-0.0172, +0.1240]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0961, ΔBrier vs climatology +0.0334 [+0.0182, +0.0498], realised minus predicted -0.0307 [-0.0645, +0.0052]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.421 | 0.2976 | 0.2720 | +0.0343 [+0.0014, +0.0700] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2127 | 0.0159 | -0.0150 [-0.0373, +0.0023] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0136 | 0.0200 | +0.0039 [-0.0016, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0646 | 0.1165 | +0.0269 [+0.0062, +0.0515] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0221 | 0.0048 | +0.0081 [+0.0062, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1305 | 0.0000 | +0.0056 [+0.0006, +0.0112] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1268 | 0.2439 | -0.0244 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.744 | 0.427 | 0.2975 | 0.2615 | +0.0321 [+0.0030, +0.0628] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1168 | 0.1133 | +0.0309 [+0.0029, +0.0603] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.376 | 0.1070 | 0.0630 | +0.0061 [-0.0015, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3465 | 0.2903 | +0.1049 [+0.0345, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1295 | 0.1461 | +0.0774 [+0.0452, +0.1168] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2858 | 0.2213 |

## risk_logistic+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.715] | 0.276 | 5.88 flat / 2.78 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.375, 0.706] | 0.269 | 4.88 flat / 2.27 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.520] | 3.808 [2.212, 6.002] | 1.740 [0.960, 2.840] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.480] | 4.038 [2.286, 6.438] | 1.971 [1.048, 3.262] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 3.423 [1.895, 5.566] | 1.519 [0.774, 2.611] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.261, 0.585] | 3.885 [2.316, 6.143] | 1.740 [1.000, 2.844] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.226, 0.562] | 3.731 [2.107, 5.959] | 1.721 [0.944, 2.869] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 6.588 [3.937, 10.644] | 2.735 [1.511, 4.695] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.556 [2.500, 10.143] | 2.861 [1.500, 7.002] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 178 | 0.564 | 0.444 | 0.0584 | +0.0130 [+0.0055, +0.0217] | -0.0021 [-0.0085, +0.0049] | 0.841 | 0.507 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 171 | 0.475 | 0.386 | 0.0634 | +0.0076 [+0.0008, +0.0146] | -0.0024 [-0.0093, +0.0047] | 0.804 | 0.414 | yes |
| 3 | 0.466 (147 of 1871 days never flag) | 165 | 0.551 | 0.461 | 0.0643 | +0.0064 [+0.0002, +0.0126] | +0.0001 [-0.0064, +0.0068] | 0.769 | 0.499 | yes |
| 4 | 0.452 (126 of 1870 days never flag) | 170 | 0.500 | 0.406 | 0.0642 | +0.0066 [+0.0003, +0.0128] | -0.0018 [-0.0087, +0.0049] | 0.788 | 0.442 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 164 | 0.486 | 0.409 | 0.0649 | +0.0061 [+0.0001, +0.0121] | -0.0015 [-0.0075, +0.0053] | 0.781 | 0.429 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.512, difference +0.1799 [+0.0515, +0.2860]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0827, ΔBrier vs climatology +0.0467 [+0.0275, +0.0661], realised minus predicted -0.0498 [-0.0806, -0.0194]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.450 | 0.2940 | 0.2720 | +0.0337 [+0.0025, +0.0666] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2137 | 0.0159 | -0.0150 [-0.0345, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0137 | 0.0200 | +0.0038 [-0.0016, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0667 | 0.1165 | +0.0275 [+0.0061, +0.0541] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0222 | 0.0048 | +0.0080 [+0.0062, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1315 | 0.0000 | +0.0053 [+0.0004, +0.0106] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1281 | 0.2439 | -0.0229 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.453 | 0.2953 | 0.2615 | +0.0321 [+0.0040, +0.0631] |
| day_type | month_end | 150 | 17 | 0.588 | 0.556 | 0.1163 | 0.1133 | +0.0301 [+0.0021, +0.0589] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.400 | 0.1065 | 0.0630 | +0.0060 [-0.0011, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0314, +0.1735] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0495, +0.1160] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2859 | 0.2213 |

## risk_logistic+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.393, 0.750] | 0.346 | 6.50 flat / 3.02 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 4.73 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.357, 0.714] | 5.038 [3.300, 7.385] | 2.173 [1.367, 3.322] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.613] | 4.500 [2.583, 7.059] | 2.077 [1.125, 3.433] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.476] | 3.154 [1.600, 5.226] | 1.423 [0.700, 2.475] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.258, 0.583] | 4.038 [2.320, 6.421] | 2.019 [1.086, 3.399] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 3.385 [1.844, 5.501] | 1.606 [0.854, 2.712] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.917] | 7.471 [4.823, 11.500] | 3.044 [1.849, 4.956] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.667 [2.467, 9.800] | 2.972 [1.400, 7.000] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.363 (126 of 1873 days never flag) | 226 | 0.679 | 0.420 | 0.0583 | +0.0131 [+0.0049, +0.0212] | -0.0020 [-0.0092, +0.0046] | 0.841 | 0.603 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 193 | 0.547 | 0.394 | 0.0634 | +0.0076 [+0.0007, +0.0144] | -0.0024 [-0.0093, +0.0046] | 0.807 | 0.479 | yes |
| 3 | 0.466 (147 of 1871 days never flag) | 147 | 0.471 | 0.442 | 0.0639 | +0.0068 [+0.0012, +0.0127] | +0.0005 [-0.0055, +0.0067] | 0.771 | 0.424 | yes |
| 4 | 0.452 (126 of 1870 days never flag) | 173 | 0.493 | 0.393 | 0.0637 | +0.0072 [+0.0009, +0.0135] | -0.0013 [-0.0079, +0.0054] | 0.789 | 0.432 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 151 | 0.457 | 0.417 | 0.0648 | +0.0061 [-0.0005, +0.0128] | -0.0014 [-0.0081, +0.0057] | 0.779 | 0.406 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1880 [+0.0729, +0.2941]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0817, ΔBrier vs climatology +0.0478 [+0.0289, +0.0673], realised minus predicted -0.0496 [-0.0813, -0.0187]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.421 | 0.2976 | 0.2720 | +0.0343 [+0.0003, +0.0670] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2127 | 0.0159 | -0.0150 [-0.0355, +0.0019] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0136 | 0.0200 | +0.0039 [-0.0017, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0646 | 0.1165 | +0.0269 [+0.0062, +0.0510] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0221 | 0.0048 | +0.0081 [+0.0063, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1305 | 0.0000 | +0.0056 [+0.0005, +0.0110] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1268 | 0.2439 | -0.0244 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.744 | 0.427 | 0.2975 | 0.2615 | +0.0321 [+0.0013, +0.0630] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1168 | 0.1133 | +0.0309 [+0.0031, +0.0602] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.376 | 0.1070 | 0.0630 | +0.0061 [-0.0015, +0.0142] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3465 | 0.2903 | +0.1049 [+0.0307, +0.1769] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1295 | 0.1461 | +0.0774 [+0.0445, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2858 | 0.2213 |

## risk_logistic+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.650] | 0.284 | 6.04 flat / 3.00 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.275, 0.637] | 0.269 | 5.54 flat / 2.74 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.444] | 4.038 [2.278, 6.542] | 1.837 [0.965, 3.125] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 4.423 [2.708, 6.962] | 1.837 [1.061, 3.065] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.531] | 4.462 [2.583, 7.150] | 2.106 [1.140, 3.575] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.471] | 3.385 [1.818, 5.600] | 1.529 [0.779, 2.690] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 5.269 [3.296, 8.143] | 2.606 [1.526, 4.227] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.833] | 7.588 [4.857, 11.728] | 3.353 [2.032, 5.438] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 180 | 0.536 | 0.417 | 0.0586 | +0.0129 [+0.0034, +0.0227] | -0.0022 [-0.0107, +0.0061] | 0.915 | 0.475 | yes |
| 2 | 0.546 (147 of 1872 days never flag) | 201 | 0.619 | 0.428 | 0.0656 | +0.0055 [-0.0039, +0.0142] | -0.0045 [-0.0130, +0.0037] | 0.884 | 0.552 | no |
| 3 | 0.621 (147 of 1871 days never flag) | 188 | 0.522 | 0.383 | 0.0682 | +0.0025 [-0.0085, +0.0123] | -0.0038 [-0.0145, +0.0056] | 0.890 | 0.455 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 149 | 0.442 | 0.409 | 0.0676 | +0.0032 [-0.0051, +0.0108] | -0.0052 [-0.0135, +0.0029] | 0.846 | 0.391 | no |
| 5 | 0.455 (147 of 1869 days never flag) | 214 | 0.558 | 0.360 | 0.0724 | -0.0015 [-0.0106, +0.0068] | -0.0090 [-0.0180, -0.0005] | 0.820 | 0.479 | no |

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
| regime | 2018-19 | 375 | 102 | 0.667 | 0.415 | 0.3238 | 0.2720 | +0.0115 [-0.0306, +0.0550] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0973 | 0.0159 | +0.0043 [-0.0257, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0056 | 0.0200 | +0.0049 [+0.0004, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0770 | 0.1165 | +0.0286 [+0.0068, +0.0559] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0035 | 0.0048 | +0.0094 [+0.0077, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0308 [+0.0245, +0.0369] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0994 | 0.2439 | -0.0110 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.592 | 0.418 | 0.3291 | 0.2615 | +0.0107 [-0.0264, +0.0478] |
| day_type | month_end | 150 | 17 | 0.529 | 0.529 | 0.1120 | 0.1133 | +0.0315 [+0.0031, +0.0597] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.368 | 0.0794 | 0.0630 | +0.0057 [-0.0036, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0311, +0.1756] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1308 | 0.1461 | +0.0798 [+0.0496, +0.1176] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.760] | 0.274 | 5.85 flat / 2.79 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.259, 0.593] | 0.231 | 4.15 flat / 1.82 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.240, 0.606] | 4.808 [2.961, 7.316] | 2.260 [1.298, 3.609] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.115 [2.458, 6.371] | 1.635 [0.906, 2.723] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.538] | 3.577 [1.937, 5.826] | 1.452 [0.727, 2.528] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.433] | 3.115 [1.588, 5.167] | 1.365 [0.647, 2.427] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 3.385 [1.786, 5.574] | 1.577 [0.767, 2.764] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 7.706 [4.957, 11.815] | 3.324 [1.982, 5.361] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 2.333 [0.800, 6.144] | 1.778 [0.487, 4.793] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (126 of 1873 days never flag) | 204 | 0.564 | 0.387 | 0.0589 | +0.0125 [+0.0023, +0.0225] | -0.0026 [-0.0120, +0.0061] | 0.915 | 0.492 | yes |
| 2 | 0.543 (147 of 1872 days never flag) | 190 | 0.597 | 0.437 | 0.0644 | +0.0067 [-0.0022, +0.0152] | -0.0033 [-0.0116, +0.0045] | 0.886 | 0.535 | no |
| 3 | 0.618 (147 of 1871 days never flag) | 166 | 0.529 | 0.440 | 0.0660 | +0.0047 [-0.0061, +0.0143] | -0.0016 [-0.0120, +0.0076] | 0.893 | 0.475 | no |
| 4 | 0.631 (147 of 1870 days never flag) | 140 | 0.428 | 0.421 | 0.0640 | +0.0068 [-0.0005, +0.0140] | -0.0016 [-0.0091, +0.0060] | 0.880 | 0.381 | no |
| 5 | 0.5 (147 of 1869 days never flag) | 148 | 0.435 | 0.405 | 0.0669 | +0.0041 [-0.0030, +0.0107] | -0.0035 [-0.0110, +0.0035] | 0.826 | 0.384 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.576 (climatology 0.512, difference +0.0635 [-0.0138, +0.1244]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0873, ΔBrier vs climatology +0.0422 [+0.0266, +0.0599], realised minus predicted +0.0051 [-0.0246, +0.0370]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.384 | 0.3281 | 0.2720 | +0.0103 [-0.0327, +0.0542] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0970 | 0.0159 | +0.0040 [-0.0266, +0.0295] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0055 | 0.0200 | +0.0050 [+0.0006, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0750 | 0.1165 | +0.0283 [+0.0066, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0034 | 0.0048 | +0.0095 [+0.0076, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0042 | 0.0000 | +0.0311 [+0.0247, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0981 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.388 | 0.3322 | 0.2615 | +0.0092 [-0.0282, +0.0481] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1127 | 0.1133 | +0.0327 [+0.0036, +0.0638] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.333 | 0.0801 | 0.0630 | +0.0053 [-0.0047, +0.0150] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0309, +0.1746] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1295 | 0.1461 | +0.0774 [+0.0437, +0.1152] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.269 | 5.69 flat / 2.61 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.714] | 0.269 | 5.19 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.440] | 4.038 [2.281, 6.441] | 1.837 [0.956, 3.074] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.154, 0.483] | 3.962 [2.250, 6.390] | 1.894 [1.008, 3.175] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.483] | 3.462 [1.808, 5.773] | 1.644 [0.794, 2.954] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.654 [2.037, 5.844] | 1.538 [0.802, 2.540] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.885 [2.999, 7.446] | 2.192 [1.231, 3.632] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.864] | 7.235 [4.500, 11.184] | 3.015 [1.761, 4.938] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.778 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 180 | 0.536 | 0.417 | 0.0586 | +0.0129 [+0.0026, +0.0226] | -0.0022 [-0.0114, +0.0061] | 0.915 | 0.475 | yes |
| 2 | 0.5 (147 of 1872 days never flag) | 169 | 0.475 | 0.391 | 0.0615 | +0.0096 [-0.0002, +0.0190] | -0.0004 [-0.0102, +0.0087] | 0.892 | 0.415 | yes |
| 3 | 0.706 (147 of 1871 days never flag) | 154 | 0.464 | 0.416 | 0.0619 | +0.0088 [-0.0020, +0.0190] | +0.0025 [-0.0079, +0.0125] | 0.900 | 0.412 | yes |
| 4 | 0.721 (126 of 1870 days never flag) | 165 | 0.507 | 0.424 | 0.0616 | +0.0093 [+0.0017, +0.0167] | +0.0008 [-0.0068, +0.0084] | 0.865 | 0.452 | yes |
| 5 | 0.455 (126 of 1869 days never flag) | 199 | 0.522 | 0.362 | 0.0657 | +0.0052 [-0.0045, +0.0139] | -0.0023 [-0.0113, +0.0060] | 0.853 | 0.448 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.512, difference +0.1793 [+0.0452, +0.2843]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0759, ΔBrier vs climatology +0.0536 [+0.0347, +0.0743], realised minus predicted -0.0120 [-0.0408, +0.0167]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.415 | 0.3238 | 0.2720 | +0.0115 [-0.0324, +0.0533] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0973 | 0.0159 | +0.0043 [-0.0261, +0.0292] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0056 | 0.0200 | +0.0049 [+0.0006, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0770 | 0.1165 | +0.0286 [+0.0067, +0.0547] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0035 | 0.0048 | +0.0094 [+0.0075, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0308 [+0.0244, +0.0368] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0994 | 0.2439 | -0.0110 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.592 | 0.418 | 0.3291 | 0.2615 | +0.0107 [-0.0271, +0.0484] |
| day_type | month_end | 150 | 17 | 0.529 | 0.529 | 0.1120 | 0.1133 | +0.0315 [+0.0027, +0.0605] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.368 | 0.0794 | 0.0630 | +0.0057 [-0.0045, +0.0157] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0298, +0.1679] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1308 | 0.1461 | +0.0798 [+0.0494, +0.1163] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.269 | 5.58 flat / 2.70 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.323, 0.667] | 0.231 | 4.08 flat / 1.94 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.241, 0.613] | 4.808 [2.816, 7.361] | 2.260 [1.228, 3.647] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.176, 0.533] | 4.154 [2.266, 6.708] | 1.894 [0.943, 3.250] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.114, 0.444] | 3.423 [1.677, 5.818] | 1.606 [0.701, 2.935] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 3.615 [1.909, 6.000] | 1.702 [0.776, 3.063] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 3.115 [1.647, 5.167] | 1.394 [0.696, 2.470] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 7.353 [4.636, 11.590] | 3.250 [1.866, 5.500] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.222 (no interval) | 1.667 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (126 of 1873 days never flag) | 204 | 0.564 | 0.387 | 0.0589 | +0.0125 [+0.0026, +0.0221] | -0.0026 [-0.0115, +0.0059] | 0.915 | 0.492 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 184 | 0.547 | 0.413 | 0.0616 | +0.0094 [-0.0004, +0.0186] | -0.0006 [-0.0100, +0.0083] | 0.895 | 0.484 | yes |
| 3 | 0.707 (147 of 1871 days never flag) | 152 | 0.457 | 0.414 | 0.0616 | +0.0091 [-0.0012, +0.0189] | +0.0027 [-0.0073, +0.0124] | 0.903 | 0.405 | yes |
| 4 | 0.7 (126 of 1870 days never flag) | 160 | 0.478 | 0.412 | 0.0585 | +0.0123 [+0.0046, +0.0193] | +0.0038 [-0.0043, +0.0109] | 0.892 | 0.424 | yes |
| 5 | 0.449 (147 of 1869 days never flag) | 143 | 0.449 | 0.434 | 0.0599 | +0.0110 [+0.0040, +0.0181] | +0.0035 [-0.0035, +0.0109] | 0.855 | 0.402 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1887 [+0.0745, +0.2903]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0746, ΔBrier vs climatology +0.0548 [+0.0358, +0.0748], realised minus predicted -0.0101 [-0.0386, +0.0179]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.384 | 0.3281 | 0.2720 | +0.0103 [-0.0349, +0.0517] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0970 | 0.0159 | +0.0040 [-0.0254, +0.0300] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0055 | 0.0200 | +0.0050 [+0.0006, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0750 | 0.1165 | +0.0283 [+0.0072, +0.0540] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0034 | 0.0048 | +0.0095 [+0.0077, +0.0113] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0042 | 0.0000 | +0.0311 [+0.0245, +0.0373] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0981 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.388 | 0.3322 | 0.2615 | +0.0092 [-0.0293, +0.0462] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1127 | 0.1133 | +0.0327 [+0.0042, +0.0614] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.333 | 0.0801 | 0.0630 | +0.0053 [-0.0049, +0.0149] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0341, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1141] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.285, 0.647] | 0.301 | 6.35 flat / 3.38 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 5.65 flat / 2.96 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.190, 0.520] | 3.846 [2.178, 6.161] | 1.750 [0.967, 2.838] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 4.231 [2.478, 6.609] | 1.808 [1.022, 2.880] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.210, 0.572] | 4.500 [2.545, 7.209] | 2.144 [1.139, 3.581] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 3.615 [2.000, 5.920] | 1.788 [0.937, 2.956] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 5.231 [3.103, 8.134] | 2.596 [1.468, 4.201] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.350, 0.833] | 7.588 [4.857, 12.000] | 3.353 [1.989, 5.520] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 4.000 [1.667, 10.008] | 3.444 [1.288, 9.200] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 180 | 0.571 | 0.444 | 0.0521 | +0.0193 [+0.0115, +0.0276] | +0.0042 [-0.0020, +0.0105] | 0.894 | 0.514 | yes |
| 2 | 0.444 (147 of 1872 days never flag) | 193 | 0.597 | 0.430 | 0.0606 | +0.0105 [+0.0039, +0.0168] | +0.0005 [-0.0059, +0.0063] | 0.861 | 0.534 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 193 | 0.551 | 0.394 | 0.0622 | +0.0085 [+0.0016, +0.0151] | +0.0022 [-0.0047, +0.0087] | 0.854 | 0.483 | no |
| 4 | 0.48 (147 of 1870 days never flag) | 155 | 0.442 | 0.394 | 0.0638 | +0.0071 [+0.0008, +0.0133] | -0.0014 [-0.0084, +0.0055] | 0.827 | 0.388 | no |
| 5 | 0.426 (147 of 1869 days never flag) | 211 | 0.543 | 0.355 | 0.0689 | +0.0021 [-0.0044, +0.0081] | -0.0055 [-0.0126, +0.0010] | 0.783 | 0.465 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.608 (climatology 0.512, difference +0.0954 [+0.0158, +0.1584]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0921, ΔBrier vs climatology +0.0374 [+0.0204, +0.0538], realised minus predicted +0.0018 [-0.0321, +0.0378]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.444 | 0.2847 | 0.2720 | +0.0403 [+0.0081, +0.0735] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1359 | 0.0159 | +0.0078 [-0.0154, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0075 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0008, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0747 | 0.1165 | +0.0309 [+0.0084, +0.0595] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0056 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0524 | 0.0000 | +0.0274 [+0.0216, +0.0335] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1278 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.451 | 0.2911 | 0.2615 | +0.0382 [+0.0081, +0.0693] |
| day_type | month_end | 150 | 17 | 0.588 | 0.556 | 0.1134 | 0.1133 | +0.0322 [+0.0053, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.401 | 0.0793 | 0.0630 | +0.0131 [+0.0055, +0.0212] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0304, +0.1708] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0479, +0.1161] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2743 | 0.2213 |

## risk_logistic+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.373 | 6.92 flat / 3.84 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.594] | 0.269 | 5.46 flat / 3.05 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.679] | 4.654 [2.904, 7.053] | 2.212 [1.295, 3.511] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.500 [2.625, 6.883] | 1.846 [1.014, 2.975] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.846 [2.080, 6.125] | 1.663 [0.884, 2.775] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 4.000 [2.222, 6.571] | 2.173 [1.086, 3.800] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 3.885 [2.040, 6.370] | 2.000 [0.963, 3.531] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.824 [4.944, 12.072] | 3.441 [2.033, 5.607] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.222 (no interval) | 4.583 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.363 (126 of 1873 days never flag) | 206 | 0.607 | 0.413 | 0.0524 | +0.0191 [+0.0116, +0.0273] | +0.0040 [-0.0022, +0.0107] | 0.893 | 0.537 | yes |
| 2 | 0.452 (147 of 1872 days never flag) | 201 | 0.604 | 0.418 | 0.0593 | +0.0117 [+0.0055, +0.0182] | +0.0017 [-0.0040, +0.0077] | 0.862 | 0.537 | no |
| 3 | 0.368 (147 of 1871 days never flag) | 176 | 0.551 | 0.432 | 0.0602 | +0.0104 [+0.0045, +0.0165] | +0.0041 [-0.0014, +0.0103] | 0.854 | 0.493 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 164 | 0.435 | 0.366 | 0.0613 | +0.0095 [+0.0035, +0.0158] | +0.0011 [-0.0050, +0.0078] | 0.841 | 0.375 | yes |
| 5 | 0.489 (147 of 1869 days never flag) | 160 | 0.428 | 0.369 | 0.0669 | +0.0040 [-0.0027, +0.0103] | -0.0035 [-0.0104, +0.0033] | 0.797 | 0.369 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0629 [-0.0130, +0.1259]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0887, ΔBrier vs climatology +0.0408 [+0.0262, +0.0571], realised minus predicted +0.0058 [-0.0255, +0.0403]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.408 | 0.2902 | 0.2720 | +0.0396 [+0.0091, +0.0730] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1360 | 0.0159 | +0.0076 [-0.0164, +0.0283] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0005, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0720 | 0.1165 | +0.0305 [+0.0086, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0055 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0532 | 0.0000 | +0.0274 [+0.0213, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1224 | 0.2439 | -0.0133 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.664 | 0.417 | 0.2945 | 0.2615 | +0.0374 [+0.0090, +0.0674] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1139 | 0.1133 | +0.0330 [+0.0037, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.360 | 0.0804 | 0.0630 | +0.0129 [+0.0059, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3465 | 0.2903 | +0.1049 [+0.0345, +0.1711] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1295 | 0.1461 | +0.0774 [+0.0451, +0.1169] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.714] | 0.276 | 5.88 flat / 2.92 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.722] | 0.269 | 5.58 flat / 2.79 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 3.846 [2.238, 6.067] | 1.750 [0.968, 2.864] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 3.538 [1.838, 5.846] | 1.683 [0.800, 2.960] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.529] | 3.692 [1.999, 6.106] | 1.846 [0.932, 3.193] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.632] | 4.038 [2.344, 6.335] | 1.875 [1.024, 3.053] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.636] | 4.962 [3.000, 7.556] | 2.327 [1.320, 3.786] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 7.235 [4.625, 11.310] | 3.015 [1.833, 4.958] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 3.333 [1.332, 8.000] | 2.750 [0.893, 7.301] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 180 | 0.571 | 0.444 | 0.0521 | +0.0193 [+0.0113, +0.0280] | +0.0042 [-0.0020, +0.0107] | 0.894 | 0.514 | yes |
| 2 | 0.856 (147 of 1872 days never flag) | 154 | 0.446 | 0.403 | 0.0557 | +0.0154 [+0.0085, +0.0226] | +0.0054 [-0.0010, +0.0122] | 0.871 | 0.393 | yes |
| 3 | 0.362 (147 of 1871 days never flag) | 162 | 0.478 | 0.407 | 0.0554 | +0.0153 [+0.0094, +0.0217] | +0.0090 [+0.0027, +0.0157] | 0.867 | 0.423 | yes |
| 4 | 0.721 (126 of 1870 days never flag) | 178 | 0.529 | 0.410 | 0.0574 | +0.0135 [+0.0071, +0.0196] | +0.0050 [-0.0018, +0.0116] | 0.849 | 0.468 | yes |
| 5 | 0.426 (126 of 1869 days never flag) | 199 | 0.507 | 0.352 | 0.0617 | +0.0092 [+0.0022, +0.0153] | +0.0017 [-0.0053, +0.0084] | 0.830 | 0.433 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.512, difference +0.1799 [+0.0506, +0.2860]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0765, ΔBrier vs climatology +0.0529 [+0.0345, +0.0718], realised minus predicted -0.0167 [-0.0456, +0.0127]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.444 | 0.2847 | 0.2720 | +0.0403 [+0.0089, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1359 | 0.0159 | +0.0078 [-0.0158, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0075 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0007, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0747 | 0.1165 | +0.0309 [+0.0072, +0.0586] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0056 | 0.0048 | +0.0094 [+0.0075, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0524 | 0.0000 | +0.0274 [+0.0215, +0.0331] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1278 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.451 | 0.2911 | 0.2615 | +0.0382 [+0.0086, +0.0699] |
| day_type | month_end | 150 | 17 | 0.588 | 0.556 | 0.1134 | 0.1133 | +0.0322 [+0.0038, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.401 | 0.0793 | 0.0630 | +0.0131 [+0.0057, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0309, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0477, +0.1165] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2743 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.297 | 6.27 flat / 3.44 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.630] | 0.269 | 4.65 flat / 2.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.686] | 4.654 [2.925, 6.900] | 2.212 [1.320, 3.438] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.138, 0.500] | 4.077 [2.178, 6.619] | 1.837 [0.904, 3.159] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.474] | 3.077 [1.555, 5.137] | 1.433 [0.681, 2.525] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 4.346 [2.333, 7.143] | 2.433 [1.106, 4.393] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.423] | 3.462 [1.677, 5.889] | 1.692 [0.731, 3.060] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.471, 0.923] | 7.353 [4.550, 11.584] | 3.250 [1.864, 5.353] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.222 (no interval) | 3.806 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.363 (126 of 1873 days never flag) | 206 | 0.607 | 0.413 | 0.0524 | +0.0191 [+0.0108, +0.0274] | +0.0040 [-0.0026, +0.0104] | 0.893 | 0.537 | yes |
| 2 | 0.866 (147 of 1872 days never flag) | 180 | 0.532 | 0.411 | 0.0559 | +0.0152 [+0.0081, +0.0222] | +0.0052 [-0.0017, +0.0119] | 0.874 | 0.471 | yes |
| 3 | 0.368 (147 of 1871 days never flag) | 145 | 0.471 | 0.448 | 0.0551 | +0.0155 [+0.0098, +0.0216] | +0.0092 [+0.0034, +0.0154] | 0.870 | 0.425 | yes |
| 4 | 0.807 (126 of 1870 days never flag) | 179 | 0.478 | 0.369 | 0.0554 | +0.0155 [+0.0094, +0.0217] | +0.0070 [+0.0005, +0.0136] | 0.857 | 0.413 | yes |
| 5 | 0.767 (147 of 1869 days never flag) | 148 | 0.420 | 0.392 | 0.0597 | +0.0112 [+0.0046, +0.0182] | +0.0037 [-0.0035, +0.0109] | 0.836 | 0.368 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1887 [+0.0694, +0.2888]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0743, ΔBrier vs climatology +0.0552 [+0.0364, +0.0756], realised minus predicted -0.0127 [-0.0420, +0.0168]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.408 | 0.2902 | 0.2720 | +0.0396 [+0.0073, +0.0736] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1360 | 0.0159 | +0.0076 [-0.0161, +0.0291] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0006, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0720 | 0.1165 | +0.0305 [+0.0076, +0.0585] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0055 | 0.0048 | +0.0094 [+0.0077, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0532 | 0.0000 | +0.0274 [+0.0217, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1224 | 0.2439 | -0.0133 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.664 | 0.417 | 0.2945 | 0.2615 | +0.0374 [+0.0068, +0.0681] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1139 | 0.1133 | +0.0330 [+0.0045, +0.0626] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.360 | 0.0804 | 0.0630 | +0.0129 [+0.0053, +0.0210] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3465 | 0.2903 | +0.1049 [+0.0348, +0.1781] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1156] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.231 | 2.81 flat / 2.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.185, 0.500] | 0.192 | 2.04 flat / 1.46 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.762] | 2.192 [1.464, 3.419] | 1.538 [0.921, 2.600] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.469] | 1.769 [1.094, 2.883] | 1.269 [0.684, 2.271] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.577 [0.880, 2.640] | 1.163 [0.571, 2.121] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.423 [0.771, 2.381] | 1.010 [0.449, 1.889] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.038 [1.297, 3.294] | 1.462 [0.804, 2.600] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.333 (no interval) | 4.667 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.052 (105 of 1873 days never flag) | 104 | 0.336 | 0.452 | 0.0590 | +0.0124 [+0.0075, +0.0171] | -0.0027 [-0.0108, +0.0045] | 0.643 | 0.303 | no |
| 2 | 0.326 (147 of 1872 days never flag) | 75 | 0.209 | 0.387 | 0.0671 | +0.0040 [-0.0025, +0.0100] | -0.0060 [-0.0144, +0.0010] | 0.579 | 0.182 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 68 | 0.196 | 0.397 | 0.0688 | +0.0019 [-0.0060, +0.0083] | -0.0045 [-0.0132, +0.0027] | 0.579 | 0.172 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 64 | 0.196 | 0.422 | 0.0694 | +0.0014 [-0.0053, +0.0078] | -0.0070 [-0.0150, +0.0007] | 0.578 | 0.174 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 83 | 0.217 | 0.361 | 0.0695 | +0.0015 [-0.0054, +0.0077] | -0.0061 [-0.0143, +0.0012] | 0.577 | 0.187 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.512, difference +0.0835 [-0.0393, +0.1951]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1070, ΔBrier vs climatology +0.0225 [+0.0109, +0.0339], realised minus predicted +0.0762 [+0.0414, +0.1136]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1064 | 0.2720 | -0.0032 [-0.0226, +0.0153] |
| regime | 2020 | 251 | 4 | 0.250 | 0.036 | 0.0254 | 0.0159 | +0.0308 [+0.0204, +0.0398] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0036 [+0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.737 | 0.0369 | 0.1165 | +0.0218 [+0.0063, +0.0409] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0011 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0055 | 0.0000 | +0.0304 [+0.0241, +0.0362] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.600 | 0.0450 | 0.2439 | -0.0046 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.544 | 0.1075 | 0.2615 | +0.0084 [-0.0095, +0.0265] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1021 | 0.1133 | +0.0357 [+0.0082, +0.0629] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.462 | 0.0120 | 0.0630 | +0.0051 [+0.0001, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3212 | 0.2903 | +0.0996 [+0.0457, +0.1509] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.435 | 0.1308 | 0.1461 | +0.0731 [+0.0406, +0.1119] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

## risk_logistic_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.722] | 0.385 | 7.12 flat / 3.29 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.324, 0.667] | 0.280 | 6.00 flat / 2.76 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.154 [2.500, 6.347] | 1.798 [1.033, 2.875] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.885 [3.133, 7.251] | 2.010 [1.227, 3.105] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.654 [2.864, 7.073] | 2.010 [1.191, 3.191] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.231 [2.611, 6.500] | 1.894 [1.087, 3.007] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.647] | 5.038 [3.184, 7.571] | 2.260 [1.346, 3.510] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.818, 10.167] | 2.574 [1.379, 4.334] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.333 (no interval) | 4.639 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (147 of 1873 days never flag) | 189 | 0.579 | 0.429 | 0.0491 | +0.0223 [+0.0148, +0.0305] | +0.0072 [+0.0025, +0.0126] | 0.888 | 0.516 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 222 | 0.683 | 0.428 | 0.0585 | +0.0125 [+0.0074, +0.0184] | +0.0025 [-0.0014, +0.0072] | 0.842 | 0.610 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 204 | 0.601 | 0.407 | 0.0627 | +0.0080 [+0.0016, +0.0143] | +0.0017 [-0.0046, +0.0077] | 0.812 | 0.532 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 182 | 0.522 | 0.396 | 0.0619 | +0.0089 [+0.0027, +0.0153] | +0.0004 [-0.0056, +0.0065] | 0.821 | 0.458 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 213 | 0.594 | 0.385 | 0.0628 | +0.0081 [+0.0027, +0.0132] | +0.0006 [-0.0044, +0.0055] | 0.799 | 0.519 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0100, +0.1941]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0409 [+0.0244, +0.0588], realised minus predicted -0.0037 [-0.0341, +0.0293]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.432 | 0.2477 | 0.2720 | +0.0525 [+0.0247, +0.0816] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.1281 | 0.0159 | +0.0146 [-0.0007, +0.0280] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0321 | 0.0200 | +0.0006 [-0.0058, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.576 | 0.1132 | 0.1165 | +0.0338 [+0.0068, +0.0687] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0227 | 0.0048 | +0.0079 [+0.0057, +0.0100] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0688 | 0.0000 | +0.0240 [+0.0184, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.556 | 0.1655 | 0.2439 | 0.0378 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.431 | 0.2580 | 0.2615 | +0.0513 [+0.0245, +0.0801] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1114 | 0.1133 | +0.0408 [+0.0128, +0.0719] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.384 | 0.0854 | 0.0630 | +0.0162 [+0.0093, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3212 | 0.2903 | +0.0996 [+0.0482, +0.1478] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1308 | 0.1461 | +0.0731 [+0.0408, +0.1102] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3416 | 0.2213 |

## risk_logistic_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.815] | 0.404 | 7.77 flat / 3.86 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.667] | 0.269 | 5.81 flat / 2.82 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.684] | 4.000 [2.878, 5.750] | 1.913 [1.323, 2.870] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.808 [2.545, 5.706] | 1.519 [1.018, 2.316] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.423 [2.162, 5.385] | 1.481 [0.920, 2.410] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.654 [2.472, 5.476] | 1.712 [1.121, 2.650] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.316, 0.679] | 4.154 [2.788, 6.259] | 1.952 [1.308, 3.039] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.765 [4.500, 10.252] | 2.750 [1.787, 4.251] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.667 (no interval) | 5.944 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.144 (105 of 1873 days never flag) | 191 | 0.621 | 0.455 | 0.0510 | +0.0205 [+0.0136, +0.0279] | +0.0054 [+0.0010, +0.0100] | 0.805 | 0.561 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 176 | 0.554 | 0.438 | 0.0608 | +0.0103 [+0.0048, +0.0162] | +0.0003 [-0.0044, +0.0051] | 0.752 | 0.497 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 159 | 0.507 | 0.440 | 0.0627 | +0.0079 [+0.0013, +0.0145] | +0.0016 [-0.0047, +0.0078] | 0.747 | 0.456 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 157 | 0.449 | 0.395 | 0.0628 | +0.0080 [+0.0018, +0.0143] | -0.0004 [-0.0065, +0.0053] | 0.759 | 0.394 | no |
| 5 | 0.172 (147 of 1869 days never flag) | 181 | 0.529 | 0.403 | 0.0634 | +0.0075 [+0.0015, +0.0132] | -0.0000 [-0.0053, +0.0050] | 0.743 | 0.467 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.512, difference +0.1036 [-0.0114, +0.1993]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0391 [+0.0231, +0.0559], realised minus predicted +0.0459 [+0.0178, +0.0760]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.508 | 0.1781 | 0.2720 | +0.0369 [+0.0121, +0.0653] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0330 | 0.0159 | +0.0236 [+0.0057, +0.0384] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.167 | 0.0145 | 0.0200 | +0.0007 [-0.0062, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.759 | 0.500 | 0.0882 | 0.1165 | +0.0329 [+0.0055, +0.0636] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.083 | 0.0088 | 0.0048 | +0.0081 [+0.0057, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0067 | 0.0000 | +0.0303 [+0.0242, +0.0364] |
| scarcity_state | 2 | 41 | 10 | 0.600 | 0.462 | 0.1345 | 0.2439 | 0.0355 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.497 | 0.1815 | 0.2615 | +0.0396 [+0.0158, +0.0655] |
| day_type | month_end | 150 | 17 | 0.882 | 0.556 | 0.1059 | 0.1133 | +0.0414 [+0.0138, +0.0709] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.422 | 0.0412 | 0.0630 | +0.0140 [+0.0077, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3212 | 0.2903 | +0.0996 [+0.0498, +0.1498] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1308 | 0.1461 | +0.0731 [+0.0420, +0.1104] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.719] | 0.365 | 6.81 flat / 3.08 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.654] | 0.269 | 5.69 flat / 2.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.588] | 4.115 [2.499, 6.294] | 1.750 [1.010, 2.794] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 4.423 [2.709, 6.843] | 1.817 [1.062, 2.942] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 4.231 [2.536, 6.653] | 1.798 [1.024, 2.950] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.800, 6.955] | 2.144 [1.250, 3.429] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 5.115 [3.318, 7.636] | 2.308 [1.405, 3.592] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.059 [5.524, 12.250] | 3.441 [2.180, 5.500] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 2.389 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.314 (126 of 1873 days never flag) | 185 | 0.557 | 0.422 | 0.0492 | +0.0222 [+0.0158, +0.0294] | +0.0071 [+0.0027, +0.0122] | 0.884 | 0.495 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 203 | 0.633 | 0.433 | 0.0575 | +0.0136 [+0.0090, +0.0185] | +0.0036 [-0.0007, +0.0080] | 0.832 | 0.567 | no |
| 3 | 0.248 (147 of 1871 days never flag) | 190 | 0.580 | 0.421 | 0.0609 | +0.0097 [+0.0041, +0.0158] | +0.0034 [-0.0024, +0.0100] | 0.807 | 0.516 | yes |
| 4 | 0.243 (147 of 1870 days never flag) | 187 | 0.500 | 0.369 | 0.0603 | +0.0105 [+0.0051, +0.0158] | +0.0021 [-0.0038, +0.0077] | 0.817 | 0.432 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 211 | 0.565 | 0.370 | 0.0609 | +0.0100 [+0.0054, +0.0145] | +0.0025 [-0.0025, +0.0072] | 0.798 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.622 (climatology 0.512, difference +0.1098 [+0.0160, +0.1912]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0894, ΔBrier vs climatology +0.0401 [+0.0239, +0.0568], realised minus predicted +0.0060 [-0.0246, +0.0398]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.401 | 0.2307 | 0.2720 | +0.0468 [+0.0227, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1153 | 0.0159 | +0.0202 [+0.0089, +0.0305] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0156 | 0.0000 | +0.0133 [+0.0116, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0230 | 0.0200 | +0.0027 [-0.0012, +0.0058] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.684 | 0.0974 | 0.1165 | +0.0335 [+0.0081, +0.0657] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0174 | 0.0048 | +0.0089 [+0.0072, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0607 | 0.0000 | +0.0251 [+0.0196, +0.0310] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.1383 | 0.2439 | 0.0357 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.419 | 0.2394 | 0.2615 | +0.0482 [+0.0249, +0.0726] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1100 | 0.1133 | +0.0400 [+0.0130, +0.0693] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.368 | 0.0743 | 0.0630 | +0.0162 [+0.0102, +0.0229] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0446, +0.1511] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1308 | 0.1461 | +0.0731 [+0.0406, +0.1074] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2519 | 0.2213 |

## risk_logistic_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.353 | 6.62 flat / 2.99 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.677] | 0.269 | 5.62 flat / 2.50 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.500, 6.333] | 1.779 [1.033, 2.834] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.769 [3.000, 7.126] | 1.962 [1.173, 3.074] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.462 [2.667, 6.864] | 1.913 [1.065, 3.100] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.381, 6.351] | 1.798 [0.983, 2.947] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.885 [2.999, 7.371] | 2.144 [1.224, 3.389] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.846, 10.067] | 2.574 [1.389, 4.263] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 6.889 (no interval) | 3.778 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (147 of 1873 days never flag) | 187 | 0.579 | 0.433 | 0.0482 | +0.0232 [+0.0162, +0.0311] | +0.0081 [+0.0032, +0.0133] | 0.911 | 0.517 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 219 | 0.683 | 0.434 | 0.0576 | +0.0134 [+0.0083, +0.0190] | +0.0034 [-0.0007, +0.0079] | 0.883 | 0.612 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 199 | 0.601 | 0.417 | 0.0608 | +0.0099 [+0.0038, +0.0162] | +0.0036 [-0.0025, +0.0097] | 0.867 | 0.535 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 179 | 0.529 | 0.408 | 0.0605 | +0.0104 [+0.0042, +0.0163] | +0.0019 [-0.0042, +0.0076] | 0.865 | 0.468 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 209 | 0.594 | 0.392 | 0.0617 | +0.0093 [+0.0039, +0.0144] | +0.0017 [-0.0032, +0.0069] | 0.852 | 0.521 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0138, +0.1940]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0869, ΔBrier vs climatology +0.0426 [+0.0265, +0.0601], realised minus predicted +0.0232 [-0.0090, +0.0562]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.432 | 0.2477 | 0.2720 | +0.0525 [+0.0258, +0.0815] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.1278 | 0.0159 | +0.0146 [-0.0009, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0043 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0022 | 0.0200 | +0.0036 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.594 | 0.0966 | 0.1165 | +0.0362 [+0.0088, +0.0721] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0011 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0688 | 0.0000 | +0.0240 [+0.0184, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.556 | 0.1655 | 0.2439 | 0.0378 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.431 | 0.2580 | 0.2615 | +0.0513 [+0.0275, +0.0789] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1094 | 0.1133 | +0.0409 [+0.0132, +0.0708] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.389 | 0.0716 | 0.0630 | +0.0173 [+0.0107, +0.0251] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3212 | 0.2903 | +0.0996 [+0.0428, +0.1521] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1308 | 0.1461 | +0.0731 [+0.0417, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3416 | 0.2213 |

## risk_logistic_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.480, 0.821] | 0.385 | 7.35 flat / 3.48 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.654] | 0.269 | 5.81 flat / 2.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.038 [3.378, 7.591] | 2.163 [1.372, 3.465] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 5.000 [3.280, 7.619] | 2.087 [1.307, 3.322] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.423 [2.722, 7.000] | 1.952 [1.150, 3.250] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.385 [2.727, 6.813] | 2.010 [1.183, 3.243] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 5.038 [3.208, 7.847] | 2.375 [1.469, 3.766] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 0.952] | 7.000 [4.399, 11.000] | 2.838 [1.647, 4.694] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.000 (no interval) | 4.694 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.144 (126 of 1873 days never flag) | 231 | 0.714 | 0.433 | 0.0497 | +0.0218 [+0.0168, +0.0272] | +0.0067 [+0.0021, +0.0112] | 0.897 | 0.639 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 227 | 0.698 | 0.427 | 0.0588 | +0.0123 [+0.0082, +0.0168] | +0.0023 [-0.0024, +0.0068] | 0.846 | 0.623 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 194 | 0.572 | 0.407 | 0.0619 | +0.0088 [+0.0034, +0.0140] | +0.0025 [-0.0038, +0.0084] | 0.814 | 0.506 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 187 | 0.529 | 0.390 | 0.0618 | +0.0091 [+0.0038, +0.0139] | +0.0006 [-0.0056, +0.0062] | 0.826 | 0.463 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 214 | 0.601 | 0.388 | 0.0622 | +0.0087 [+0.0042, +0.0130] | +0.0012 [-0.0040, +0.0058] | 0.807 | 0.526 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.512, difference +0.1011 [+0.0066, +0.1784]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0362 [+0.0226, +0.0502], realised minus predicted +0.0375 [+0.0058, +0.0711]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.794 | 0.440 | 0.1771 | 0.2720 | +0.0380 [+0.0234, +0.0555] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0767 | 0.0159 | +0.0278 [+0.0179, +0.0372] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0029 [-0.0015, +0.0061] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.548 | 0.0751 | 0.1165 | +0.0344 [+0.0106, +0.0651] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0119 | 0.0048 | +0.0091 [+0.0073, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0371 | 0.0000 | +0.0288 [+0.0228, +0.0347] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1053 | 0.2439 | 0.0250 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.768 | 0.444 | 0.1828 | 0.2615 | +0.0444 [+0.0278, +0.0633] |
| day_type | month_end | 150 | 17 | 0.882 | 0.625 | 0.1067 | 0.1133 | +0.0386 [+0.0114, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.693 | 0.391 | 0.0487 | 0.0630 | +0.0158 [+0.0118, +0.0207] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3212 | 0.2903 | +0.0996 [+0.0478, +0.1514] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1308 | 0.1461 | +0.0731 [+0.0413, +0.1099] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2207 | 0.2213 |

## risk_logistic_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 5.38 flat / 2.53 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.647] | 0.269 | 4.88 flat / 2.35 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.429] | 3.692 [2.030, 6.000] | 1.663 [0.808, 2.859] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 4.731 [2.808, 7.458] | 2.058 [1.106, 3.407] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 3.923 [2.228, 6.317] | 1.673 [0.889, 2.802] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.560] | 3.885 [2.054, 6.423] | 1.981 [0.971, 3.425] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.615 [2.636, 7.401] | 2.231 [1.161, 3.789] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.824] | 6.706 [4.042, 10.801] | 2.735 [1.483, 4.667] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.889 (no interval) | 2.139 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 163 | 0.479 | 0.411 | 0.0619 | +0.0095 [-0.0005, +0.0194] | -0.0056 [-0.0146, +0.0027] | 0.873 | 0.423 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 206 | 0.597 | 0.403 | 0.0700 | +0.0010 [-0.0078, +0.0098] | -0.0090 [-0.0172, -0.0010] | 0.826 | 0.526 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 174 | 0.522 | 0.414 | 0.0747 | -0.0040 [-0.0148, +0.0054] | -0.0104 [-0.0210, -0.0008] | 0.801 | 0.463 | no |
| 4 | 0.519 (147 of 1870 days never flag) | 163 | 0.449 | 0.380 | 0.0728 | -0.0019 [-0.0103, +0.0065] | -0.0104 [-0.0187, -0.0021] | 0.816 | 0.391 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 193 | 0.529 | 0.378 | 0.0726 | -0.0017 [-0.0088, +0.0050] | -0.0092 [-0.0166, -0.0022] | 0.785 | 0.460 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.612 (climatology 0.512, difference +0.0998 [-0.0011, +0.1827]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0958, ΔBrier vs climatology +0.0337 [+0.0168, +0.0512], realised minus predicted -0.0105 [-0.0446, +0.0227]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.403 | 0.3222 | 0.2720 | +0.0082 [-0.0350, +0.0508] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2026 | 0.0159 | -0.0128 [-0.0340, +0.0052] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0026, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0667 | 0.1165 | +0.0331 [+0.0092, +0.0656] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1132 | 0.0000 | +0.0107 [+0.0050, +0.0168] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1219 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.414 | 0.3211 | 0.2615 | +0.0093 [-0.0280, +0.0472] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.1128 | 0.1133 | +0.0382 [+0.0115, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.362 | 0.1018 | 0.0630 | +0.0015 [-0.0086, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1489] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1308 | 0.1461 | +0.0731 [+0.0411, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.720] | 0.269 | 5.50 flat / 2.56 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.619] | 0.269 | 4.92 flat / 2.34 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.258, 0.600] | 3.885 [2.192, 6.360] | 1.769 [0.904, 3.114] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.654 [2.783, 7.409] | 1.981 [1.060, 3.422] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.257, 0.619] | 3.846 [2.139, 6.301] | 1.596 [0.846, 2.758] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.538] | 3.769 [2.000, 6.500] | 1.865 [0.893, 3.415] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.257, 0.619] | 4.154 [2.448, 6.667] | 1.827 [1.000, 3.084] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.929] | 6.824 [4.273, 11.085] | 2.765 [1.533, 4.840] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.167 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 178 | 0.550 | 0.433 | 0.0618 | +0.0097 [-0.0004, +0.0194] | -0.0054 [-0.0145, +0.0029] | 0.876 | 0.492 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 204 | 0.597 | 0.407 | 0.0690 | +0.0021 [-0.0074, +0.0104] | -0.0080 [-0.0169, -0.0003] | 0.828 | 0.527 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 174 | 0.536 | 0.425 | 0.0724 | -0.0017 [-0.0113, +0.0070] | -0.0080 [-0.0175, +0.0004] | 0.803 | 0.479 | no |
| 4 | 0.662 (147 of 1870 days never flag) | 160 | 0.449 | 0.388 | 0.0718 | -0.0010 [-0.0087, +0.0066] | -0.0094 [-0.0175, -0.0020] | 0.818 | 0.393 | no |
| 5 | 0.503 (147 of 1869 days never flag) | 183 | 0.543 | 0.410 | 0.0731 | -0.0022 [-0.0099, +0.0048] | -0.0097 [-0.0177, -0.0025] | 0.789 | 0.481 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.572 (climatology 0.512, difference +0.0594 [-0.0274, +0.1402]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0206, +0.0539], realised minus predicted -0.0102 [-0.0441, +0.0236]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.3272 | 0.2720 | +0.0089 [-0.0381, +0.0531] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2005 | 0.0159 | -0.0120 [-0.0332, +0.0064] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0031, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0652 | 0.1165 | +0.0325 [+0.0081, +0.0629] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1118 | 0.0000 | +0.0113 [+0.0059, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1208 | 0.2439 | 0.0255 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.608 | 0.432 | 0.3242 | 0.2615 | +0.0097 [-0.0311, +0.0483] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1135 | 0.1133 | +0.0383 [+0.0101, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.370 | 0.1025 | 0.0630 | +0.0017 [-0.0088, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0469, +0.1465] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1283 | 0.1461 | +0.0745 [+0.0438, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2938 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.739] | 0.269 | 4.73 flat / 2.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.407, 0.750] | 0.254 | 4.46 flat / 2.30 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.444] | 3.692 [1.970, 6.072] | 1.663 [0.812, 2.900] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.438] | 3.615 [1.833, 6.044] | 1.644 [0.757, 2.886] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 3.423 [1.913, 5.589] | 1.558 [0.828, 2.660] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.300, 0.636] | 4.115 [2.323, 6.600] | 2.058 [1.103, 3.448] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 3.923 [2.167, 6.336] | 1.990 [1.007, 3.417] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.706 [3.262, 9.500] | 2.485 [1.307, 4.404] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 2.889 (no interval) | 2.194 (no interval) |

Recall with equal weight per regime: 0.437 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 163 | 0.479 | 0.411 | 0.0619 | +0.0095 [-0.0006, +0.0198] | -0.0056 [-0.0143, +0.0026] | 0.873 | 0.423 | no |
| 2 | 0.849 (147 of 1872 days never flag) | 155 | 0.439 | 0.394 | 0.0646 | +0.0065 [-0.0027, +0.0155] | -0.0035 [-0.0124, +0.0050] | 0.846 | 0.385 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 160 | 0.514 | 0.444 | 0.0676 | +0.0031 [-0.0071, +0.0124] | -0.0033 [-0.0131, +0.0062] | 0.825 | 0.463 | no |
| 4 | 0.528 (126 of 1870 days never flag) | 176 | 0.500 | 0.392 | 0.0667 | +0.0041 [-0.0044, +0.0120] | -0.0043 [-0.0128, +0.0034] | 0.842 | 0.438 | yes |
| 5 | 0.456 (147 of 1869 days never flag) | 165 | 0.457 | 0.382 | 0.0666 | +0.0043 [-0.0022, +0.0111] | -0.0032 [-0.0098, +0.0035] | 0.826 | 0.398 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.694 (climatology 0.512, difference +0.1818 [+0.0967, +0.2766]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0284, +0.0667], realised minus predicted -0.0298 [-0.0609, +0.0006]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.403 | 0.3222 | 0.2720 | +0.0082 [-0.0367, +0.0517] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2026 | 0.0159 | -0.0128 [-0.0357, +0.0061] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0027, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0667 | 0.1165 | +0.0331 [+0.0079, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1132 | 0.0000 | +0.0107 [+0.0051, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1219 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.414 | 0.3211 | 0.2615 | +0.0093 [-0.0296, +0.0486] |
| day_type | month_end | 150 | 17 | 0.529 | 0.600 | 0.1128 | 0.1133 | +0.0382 [+0.0104, +0.0702] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.362 | 0.1018 | 0.0630 | +0.0015 [-0.0086, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1508] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1308 | 0.1461 | +0.0731 [+0.0412, +0.1083] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.714] | 0.269 | 4.73 flat / 2.35 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.258 | 4.50 flat / 2.27 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.885 [2.120, 6.200] | 1.769 [0.902, 3.011] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.435] | 3.500 [1.731, 5.889] | 1.615 [0.726, 2.838] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 2.462 [1.217, 4.188] | 0.990 [0.509, 1.650] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 4.231 [2.478, 6.800] | 2.096 [1.114, 3.567] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.808 [2.000, 6.302] | 1.923 [0.903, 3.367] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.857] | 5.647 [3.185, 9.401] | 2.412 [1.234, 4.266] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.000 (no interval) | 2.222 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 178 | 0.550 | 0.433 | 0.0618 | +0.0097 [-0.0011, +0.0202] | -0.0054 [-0.0148, +0.0032] | 0.876 | 0.492 | no |
| 2 | 0.772 (147 of 1872 days never flag) | 154 | 0.453 | 0.409 | 0.0645 | +0.0065 [-0.0030, +0.0152] | -0.0035 [-0.0126, +0.0048] | 0.848 | 0.401 | yes |
| 3 | 0.625 (147 of 1871 days never flag) | 128 | 0.464 | 0.500 | 0.0673 | +0.0034 [-0.0068, +0.0122] | -0.0030 [-0.0128, +0.0057] | 0.826 | 0.427 | yes |
| 4 | 0.476 (105 of 1870 days never flag) | 179 | 0.500 | 0.385 | 0.0660 | +0.0048 [-0.0032, +0.0128] | -0.0037 [-0.0121, +0.0044] | 0.842 | 0.436 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 164 | 0.471 | 0.396 | 0.0665 | +0.0044 [-0.0029, +0.0116] | -0.0031 [-0.0102, +0.0042] | 0.826 | 0.414 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1655 [+0.0644, +0.2701]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0826, ΔBrier vs climatology +0.0469 [+0.0274, +0.0694], realised minus predicted -0.0294 [-0.0594, +0.0036]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.3272 | 0.2720 | +0.0089 [-0.0382, +0.0539] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2005 | 0.0159 | -0.0120 [-0.0344, +0.0058] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0027, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0652 | 0.1165 | +0.0325 [+0.0076, +0.0626] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0068, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1118 | 0.0000 | +0.0113 [+0.0057, +0.0170] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1208 | 0.2439 | 0.0255 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.608 | 0.432 | 0.3242 | 0.2615 | +0.0097 [-0.0311, +0.0495] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1135 | 0.1133 | +0.0383 [+0.0102, +0.0683] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.370 | 0.1025 | 0.0630 | +0.0017 [-0.0091, +0.0123] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0474, +0.1469] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1283 | 0.1461 | +0.0745 [+0.0424, +0.1142] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2938 | 0.2213 |

## risk_logistic_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.281, 0.650] | 0.276 | 5.88 flat / 2.77 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.269 | 4.77 flat / 2.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.885 [2.108, 6.314] | 1.769 [0.890, 2.941] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.962 [2.961, 7.667] | 2.183 [1.186, 3.590] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.281, 0.650] | 3.923 [2.129, 6.276] | 1.683 [0.860, 2.785] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.615 [2.000, 5.957] | 1.673 [0.869, 2.834] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.269 [2.458, 6.778] | 1.904 [1.049, 3.104] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.833] | 6.706 [3.879, 10.934] | 2.735 [1.428, 4.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (147 of 1873 days never flag) | 173 | 0.514 | 0.416 | 0.0574 | +0.0140 [+0.0066, +0.0226] | -0.0011 [-0.0069, +0.0054] | 0.847 | 0.456 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 213 | 0.604 | 0.394 | 0.0682 | +0.0029 [-0.0032, +0.0090] | -0.0071 [-0.0133, -0.0006] | 0.784 | 0.530 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 177 | 0.543 | 0.424 | 0.0721 | -0.0014 [-0.0082, +0.0052] | -0.0077 [-0.0148, -0.0009] | 0.732 | 0.485 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 156 | 0.449 | 0.397 | 0.0717 | -0.0009 [-0.0080, +0.0059] | -0.0093 [-0.0172, -0.0018] | 0.755 | 0.395 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 185 | 0.536 | 0.400 | 0.0727 | -0.0017 [-0.0083, +0.0043] | -0.0093 [-0.0166, -0.0026] | 0.726 | 0.472 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0979 [-0.0034, +0.1793]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0988, ΔBrier vs climatology +0.0307 [+0.0146, +0.0474], realised minus predicted -0.0277 [-0.0630, +0.0092]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.408 | 0.2932 | 0.2720 | +0.0342 [+0.0043, +0.0702] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2108 | 0.0159 | -0.0108 [-0.0251, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0025 [-0.0025, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0654 | 0.1165 | +0.0310 [+0.0087, +0.0577] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0064, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1328 | 0.0000 | +0.0049 [-0.0002, +0.0105] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0990 | 0.2439 | 0.0054 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.418 | 0.2957 | 0.2615 | +0.0336 [+0.0056, +0.0664] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1135 | 0.1133 | +0.0374 [+0.0114, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.363 | 0.1060 | 0.0630 | +0.0069 [-0.0002, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3212 | 0.2903 | +0.0996 [+0.0501, +0.1483] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1308 | 0.1461 | +0.0731 [+0.0420, +0.1101] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.710] | 0.280 | 5.96 flat / 2.79 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.650] | 0.269 | 4.81 flat / 2.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.300, 0.632] | 4.000 [2.222, 6.309] | 1.827 [0.949, 3.033] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.600] | 4.577 [2.742, 7.039] | 1.817 [1.018, 2.973] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.731 [2.000, 6.050] | 1.519 [0.750, 2.605] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.522] | 3.577 [1.928, 5.720] | 1.654 [0.878, 2.808] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.423 [2.621, 6.876] | 2.010 [1.150, 3.229] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.824 [4.040, 11.000] | 2.765 [1.500, 4.806] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 185 | 0.579 | 0.438 | 0.0572 | +0.0142 [+0.0065, +0.0226] | -0.0009 [-0.0072, +0.0056] | 0.850 | 0.519 | no |
| 2 | 0.384 (147 of 1872 days never flag) | 204 | 0.612 | 0.417 | 0.0672 | +0.0039 [-0.0022, +0.0102] | -0.0061 [-0.0116, -0.0002] | 0.785 | 0.543 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 171 | 0.536 | 0.433 | 0.0697 | +0.0010 [-0.0044, +0.0063] | -0.0053 [-0.0105, +0.0006] | 0.735 | 0.480 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 155 | 0.449 | 0.400 | 0.0708 | +0.0001 [-0.0062, +0.0060] | -0.0084 [-0.0149, -0.0025] | 0.755 | 0.396 | no |
| 5 | 0.467 (147 of 1869 days never flag) | 192 | 0.558 | 0.401 | 0.0732 | -0.0022 [-0.0088, +0.0043] | -0.0098 [-0.0176, -0.0025] | 0.732 | 0.492 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0632 [-0.0255, +0.1421]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0963, ΔBrier vs climatology +0.0332 [+0.0177, +0.0499], realised minus predicted -0.0274 [-0.0626, +0.0096]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.2982 | 0.2720 | +0.0350 [+0.0016, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.2086 | 0.0159 | -0.0099 [-0.0240, +0.0027] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0110 | 0.0200 | +0.0026 [-0.0024, +0.0061] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0640 | 0.1165 | +0.0304 [+0.0082, +0.0563] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0065, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1314 | 0.0000 | +0.0055 [+0.0005, +0.0109] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0980 | 0.2439 | 0.0044 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.437 | 0.2988 | 0.2615 | +0.0340 [+0.0041, +0.0652] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1142 | 0.1133 | +0.0375 [+0.0103, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.371 | 0.1068 | 0.0630 | +0.0070 [-0.0007, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0466, +0.1439] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1283 | 0.1461 | +0.0745 [+0.0446, +0.1114] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2896 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.375, 0.710] | 0.269 | 5.19 flat / 2.57 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.368, 0.714] | 0.269 | 4.77 flat / 2.41 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.517] | 3.885 [2.148, 6.375] | 1.769 [0.935, 3.054] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.226, 0.568] | 3.538 [1.963, 5.849] | 1.567 [0.814, 2.707] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.375, 0.710] | 3.500 [1.974, 5.769] | 1.625 [0.893, 2.750] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.300, 0.625] | 4.308 [2.517, 6.963] | 2.135 [1.202, 3.590] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 3.538 [1.999, 5.833] | 1.673 [0.904, 2.848] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 5.706 [3.230, 9.627] | 2.485 [1.302, 4.375] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 2.722 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (147 of 1873 days never flag) | 173 | 0.514 | 0.416 | 0.0574 | +0.0140 [+0.0062, +0.0223] | -0.0011 [-0.0072, +0.0053] | 0.847 | 0.456 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 160 | 0.489 | 0.425 | 0.0620 | +0.0091 [+0.0024, +0.0158] | -0.0009 [-0.0074, +0.0057] | 0.812 | 0.436 | no |
| 3 | 0.438 (126 of 1871 days never flag) | 164 | 0.529 | 0.445 | 0.0644 | +0.0063 [+0.0003, +0.0127] | -0.0001 [-0.0061, +0.0066] | 0.770 | 0.476 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 182 | 0.507 | 0.385 | 0.0653 | +0.0055 [-0.0009, +0.0119] | -0.0029 [-0.0098, +0.0037] | 0.791 | 0.443 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 157 | 0.471 | 0.414 | 0.0663 | +0.0046 [-0.0017, +0.0108] | -0.0029 [-0.0095, +0.0041] | 0.778 | 0.418 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.695 (climatology 0.512, difference +0.1830 [+0.0978, +0.2723]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0447 [+0.0266, +0.0651], realised minus predicted -0.0487 [-0.0806, -0.0151]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.408 | 0.2932 | 0.2720 | +0.0342 [+0.0036, +0.0693] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2108 | 0.0159 | -0.0108 [-0.0252, +0.0015] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0025 [-0.0025, +0.0063] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0654 | 0.1165 | +0.0310 [+0.0081, +0.0583] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0064, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1328 | 0.0000 | +0.0049 [-0.0003, +0.0102] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0990 | 0.2439 | 0.0054 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.418 | 0.2957 | 0.2615 | +0.0336 [+0.0033, +0.0648] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1135 | 0.1133 | +0.0374 [+0.0101, +0.0665] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.363 | 0.1060 | 0.0630 | +0.0069 [-0.0005, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3212 | 0.2903 | +0.0996 [+0.0466, +0.1500] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1308 | 0.1461 | +0.0731 [+0.0407, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.722] | 0.269 | 5.04 flat / 2.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.667] | 0.231 | 4.19 flat / 1.97 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.636] | 4.000 [2.150, 6.476] | 1.827 [0.875, 3.132] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 3.500 [1.894, 5.801] | 1.558 [0.808, 2.631] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 2.500 [1.231, 4.278] | 1.000 [0.510, 1.693] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.636] | 3.692 [2.125, 5.959] | 1.683 [0.929, 2.800] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.577 [1.909, 5.909] | 1.712 [0.905, 2.875] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.423, 0.875] | 5.647 [3.055, 9.251] | 2.412 [1.176, 4.270] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 3.889 [2.077, 8.000] | 2.333 [1.167, 5.188] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 185 | 0.579 | 0.438 | 0.0572 | +0.0142 [+0.0064, +0.0223] | -0.0009 [-0.0072, +0.0059] | 0.850 | 0.519 | yes |
| 2 | 0.396 (147 of 1872 days never flag) | 160 | 0.496 | 0.431 | 0.0619 | +0.0092 [+0.0026, +0.0157] | -0.0008 [-0.0072, +0.0061] | 0.815 | 0.444 | no |
| 3 | 0.43 (147 of 1871 days never flag) | 129 | 0.464 | 0.496 | 0.0641 | +0.0066 [+0.0006, +0.0128] | +0.0002 [-0.0062, +0.0067] | 0.769 | 0.426 | no |
| 4 | 0.407 (105 of 1870 days never flag) | 165 | 0.500 | 0.418 | 0.0646 | +0.0062 [+0.0000, +0.0124] | -0.0023 [-0.0088, +0.0043] | 0.789 | 0.445 | yes |
| 5 | 0.427 (147 of 1869 days never flag) | 160 | 0.486 | 0.419 | 0.0663 | +0.0047 [-0.0018, +0.0108] | -0.0029 [-0.0093, +0.0041] | 0.777 | 0.432 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1661 [+0.0643, +0.2681]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0844, ΔBrier vs climatology +0.0451 [+0.0263, +0.0662], realised minus predicted -0.0484 [-0.0790, -0.0161]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.2982 | 0.2720 | +0.0350 [+0.0007, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.2086 | 0.0159 | -0.0099 [-0.0234, +0.0031] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0110 | 0.0200 | +0.0026 [-0.0024, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0640 | 0.1165 | +0.0304 [+0.0085, +0.0558] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0065, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1314 | 0.0000 | +0.0055 [+0.0005, +0.0112] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0980 | 0.2439 | 0.0044 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.437 | 0.2988 | 0.2615 | +0.0340 [+0.0036, +0.0657] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1142 | 0.1133 | +0.0375 [+0.0089, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.371 | 0.1068 | 0.0630 | +0.0070 [-0.0006, +0.0151] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0459, +0.1466] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1283 | 0.1461 | +0.0745 [+0.0436, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2896 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.281, 0.650] | 0.269 | 5.54 flat / 2.60 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 4.92 flat / 2.32 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.444] | 3.731 [1.969, 6.105] | 1.702 [0.845, 2.913] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.962 [2.966, 7.708] | 2.183 [1.200, 3.552] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.243, 0.613] | 4.038 [2.250, 6.421] | 1.788 [0.936, 2.943] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 3.962 [2.047, 6.544] | 1.971 [0.943, 3.450] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.692 [2.641, 7.481] | 2.250 [1.179, 3.778] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.765 [4.000, 11.000] | 2.794 [1.513, 4.771] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.222 [1.294, 7.750] | 2.222 [0.729, 5.688] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 163 | 0.471 | 0.405 | 0.0576 | +0.0138 [+0.0036, +0.0238] | -0.0012 [-0.0102, +0.0072] | 0.919 | 0.415 | yes |
| 2 | 0.5 (147 of 1872 days never flag) | 215 | 0.619 | 0.400 | 0.0648 | +0.0063 [-0.0029, +0.0149] | -0.0037 [-0.0122, +0.0039] | 0.886 | 0.544 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 178 | 0.529 | 0.410 | 0.0682 | +0.0025 [-0.0080, +0.0125] | -0.0039 [-0.0147, +0.0059] | 0.891 | 0.468 | no |
| 4 | 0.519 (147 of 1870 days never flag) | 166 | 0.457 | 0.380 | 0.0681 | +0.0027 [-0.0054, +0.0104] | -0.0057 [-0.0138, +0.0023] | 0.849 | 0.397 | no |
| 5 | 0.455 (147 of 1869 days never flag) | 197 | 0.543 | 0.381 | 0.0726 | -0.0016 [-0.0114, +0.0068] | -0.0092 [-0.0188, -0.0007] | 0.824 | 0.473 | no |

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
| regime | 2018-19 | 375 | 102 | 0.578 | 0.399 | 0.3231 | 0.2720 | +0.0120 [-0.0311, +0.0540] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0944 | 0.0159 | +0.0086 [-0.0194, +0.0308] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0036 [-0.0002, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0757 | 0.1165 | +0.0321 [+0.0093, +0.0610] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0078, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0065 | 0.0000 | +0.0304 [+0.0245, +0.0364] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0703 | 0.2439 | 0.0173 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.407 | 0.3294 | 0.2615 | +0.0123 [-0.0276, +0.0516] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.1092 | 0.1133 | +0.0389 [+0.0110, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.357 | 0.0789 | 0.0630 | +0.0065 [-0.0039, +0.0165] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1308 | 0.1461 | +0.0731 [+0.0408, +0.1101] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2847 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.714] | 0.269 | 5.73 flat / 2.64 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.611] | 0.269 | 4.77 flat / 2.27 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.263, 0.593] | 3.885 [2.138, 6.250] | 1.769 [0.926, 2.948] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 5.000 [3.095, 7.629] | 2.115 [1.196, 3.417] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.846 [2.148, 6.121] | 1.615 [0.830, 2.732] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 3.808 [2.030, 6.251] | 1.875 [0.905, 3.208] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 3.500 [1.944, 5.728] | 1.606 [0.827, 2.719] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.882 [4.181, 10.929] | 2.824 [1.559, 4.733] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.556 (no interval) | 2.306 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 178 | 0.550 | 0.433 | 0.0578 | +0.0136 [+0.0034, +0.0232] | -0.0015 [-0.0106, +0.0068] | 0.920 | 0.492 | yes |
| 2 | 0.575 (147 of 1872 days never flag) | 219 | 0.640 | 0.406 | 0.0640 | +0.0071 [-0.0026, +0.0158] | -0.0029 [-0.0121, +0.0050] | 0.888 | 0.565 | no |
| 3 | 0.618 (147 of 1871 days never flag) | 175 | 0.543 | 0.429 | 0.0659 | +0.0048 [-0.0066, +0.0144] | -0.0015 [-0.0121, +0.0079] | 0.894 | 0.486 | no |
| 4 | 0.662 (147 of 1870 days never flag) | 160 | 0.442 | 0.381 | 0.0644 | +0.0064 [-0.0012, +0.0134] | -0.0021 [-0.0096, +0.0049] | 0.881 | 0.385 | no |
| 5 | 0.5 (147 of 1869 days never flag) | 153 | 0.449 | 0.405 | 0.0674 | +0.0035 [-0.0037, +0.0105] | -0.0040 [-0.0117, +0.0033] | 0.829 | 0.397 | no |

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
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.3287 | 0.2720 | +0.0109 [-0.0337, +0.0521] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0929 | 0.0159 | +0.0091 [-0.0177, +0.0319] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0743 | 0.1165 | +0.0318 [+0.0094, +0.0586] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0051 | 0.0000 | +0.0310 [+0.0241, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0693 | 0.2439 | 0.0163 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.608 | 0.432 | 0.3334 | 0.2615 | +0.0111 [-0.0278, +0.0487] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1101 | 0.1133 | +0.0393 [+0.0095, +0.0699] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.370 | 0.0799 | 0.0630 | +0.0062 [-0.0042, +0.0159] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0475, +0.1473] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1283 | 0.1461 | +0.0745 [+0.0425, +0.1110] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.714] | 0.269 | 4.85 flat / 2.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.254 | 4.46 flat / 2.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 3.731 [2.025, 6.231] | 1.702 [0.853, 3.001] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 4.038 [2.294, 6.579] | 1.913 [1.015, 3.276] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.333, 0.677] | 3.346 [1.869, 5.550] | 1.538 [0.792, 2.704] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.304, 0.632] | 4.192 [2.417, 6.739] | 2.048 [1.104, 3.474] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.478] | 3.962 [2.207, 6.520] | 1.990 [1.029, 3.479] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.870] | 5.706 [3.210, 9.762] | 2.485 [1.323, 4.550] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.194 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 163 | 0.471 | 0.405 | 0.0576 | +0.0138 [+0.0040, +0.0236] | -0.0012 [-0.0095, +0.0064] | 0.919 | 0.415 | yes |
| 2 | 0.5 (147 of 1872 days never flag) | 174 | 0.496 | 0.397 | 0.0600 | +0.0110 [+0.0013, +0.0200] | +0.0010 [-0.0082, +0.0098] | 0.896 | 0.436 | yes |
| 3 | 0.848 (126 of 1871 days never flag) | 157 | 0.507 | 0.446 | 0.0620 | +0.0086 [-0.0024, +0.0179] | +0.0023 [-0.0085, +0.0119] | 0.898 | 0.457 | no |
| 4 | 0.528 (126 of 1870 days never flag) | 178 | 0.500 | 0.388 | 0.0627 | +0.0082 [+0.0004, +0.0157] | -0.0003 [-0.0082, +0.0073] | 0.864 | 0.437 | no |
| 5 | 0.455 (147 of 1869 days never flag) | 167 | 0.464 | 0.383 | 0.0672 | +0.0037 [-0.0054, +0.0121] | -0.0038 [-0.0127, +0.0047] | 0.850 | 0.404 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.694 (climatology 0.512, difference +0.1818 [+0.0954, +0.2710]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0785, ΔBrier vs climatology +0.0510 [+0.0324, +0.0713], realised minus predicted -0.0118 [-0.0420, +0.0190]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.399 | 0.3231 | 0.2720 | +0.0120 [-0.0302, +0.0532] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0944 | 0.0159 | +0.0086 [-0.0190, +0.0310] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0036 [-0.0000, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0757 | 0.1165 | +0.0321 [+0.0099, +0.0596] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0065 | 0.0000 | +0.0304 [+0.0240, +0.0361] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0703 | 0.2439 | 0.0173 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.407 | 0.3294 | 0.2615 | +0.0123 [-0.0245, +0.0493] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.1092 | 0.1133 | +0.0389 [+0.0117, +0.0689] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.357 | 0.0789 | 0.0630 | +0.0065 [-0.0034, +0.0165] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0466, +0.1495] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1308 | 0.1461 | +0.0731 [+0.0398, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2847 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.722] | 0.269 | 4.73 flat / 2.27 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.667] | 0.242 | 4.35 flat / 2.14 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.885 [2.174, 6.471] | 1.769 [0.900, 3.066] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.923 [2.181, 6.584] | 1.846 [0.943, 3.214] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.189, 0.520] | 3.115 [1.542, 5.502] | 1.423 [0.659, 2.629] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.115 [2.333, 6.790] | 1.990 [1.018, 3.479] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.846 [2.071, 6.543] | 1.933 [0.960, 3.453] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.529 [3.038, 9.472] | 2.353 [1.147, 4.319] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 178 | 0.550 | 0.433 | 0.0578 | +0.0136 [+0.0035, +0.0235] | -0.0015 [-0.0104, +0.0069] | 0.920 | 0.492 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 170 | 0.489 | 0.400 | 0.0601 | +0.0110 [+0.0017, +0.0197] | +0.0010 [-0.0078, +0.0093] | 0.898 | 0.430 | yes |
| 3 | 0.836 (147 of 1871 days never flag) | 145 | 0.464 | 0.441 | 0.0619 | +0.0088 [-0.0019, +0.0182] | +0.0025 [-0.0084, +0.0116] | 0.900 | 0.417 | no |
| 4 | 0.476 (105 of 1870 days never flag) | 177 | 0.507 | 0.395 | 0.0595 | +0.0114 [+0.0042, +0.0185] | +0.0029 [-0.0043, +0.0103] | 0.891 | 0.445 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 166 | 0.478 | 0.398 | 0.0613 | +0.0096 [+0.0026, +0.0161] | +0.0021 [-0.0050, +0.0090] | 0.853 | 0.420 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.3287 | 0.2720 | +0.0109 [-0.0334, +0.0545] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0929 | 0.0159 | +0.0091 [-0.0188, +0.0316] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [+0.0002, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0743 | 0.1165 | +0.0318 [+0.0089, +0.0605] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0051 | 0.0000 | +0.0310 [+0.0246, +0.0368] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0693 | 0.2439 | 0.0163 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.608 | 0.432 | 0.3334 | 0.2615 | +0.0111 [-0.0284, +0.0494] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1101 | 0.1133 | +0.0393 [+0.0106, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.370 | 0.0799 | 0.0630 | +0.0062 [-0.0044, +0.0163] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0480, +0.1453] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1283 | 0.1461 | +0.0745 [+0.0429, +0.1115] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.640] | 0.269 | 5.65 flat / 2.85 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.276, 0.640] | 0.269 | 5.12 flat / 2.57 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.192, 0.512] | 3.923 [2.250, 6.300] | 1.837 [0.966, 3.110] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.769 [2.857, 7.400] | 2.154 [1.216, 3.528] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 3.923 [2.258, 6.224] | 1.683 [0.910, 2.808] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.556] | 3.846 [2.222, 6.305] | 1.942 [1.055, 3.338] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.562] | 4.615 [2.740, 7.313] | 2.202 [1.212, 3.712] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.824] | 6.765 [4.130, 10.929] | 2.794 [1.567, 4.793] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.556 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.391 (147 of 1873 days never flag) | 173 | 0.507 | 0.410 | 0.0512 | +0.0203 [+0.0124, +0.0285] | +0.0052 [-0.0007, +0.0111] | 0.901 | 0.448 | yes |
| 2 | 0.444 (147 of 1872 days never flag) | 208 | 0.604 | 0.404 | 0.0598 | +0.0113 [+0.0050, +0.0178] | +0.0013 [-0.0045, +0.0073] | 0.863 | 0.533 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 178 | 0.551 | 0.427 | 0.0623 | +0.0084 [+0.0020, +0.0148] | +0.0021 [-0.0043, +0.0088] | 0.858 | 0.492 | no |
| 4 | 0.411 (147 of 1870 days never flag) | 162 | 0.449 | 0.383 | 0.0642 | +0.0066 [+0.0000, +0.0130] | -0.0019 [-0.0089, +0.0055] | 0.830 | 0.392 | no |
| 5 | 0.426 (147 of 1869 days never flag) | 193 | 0.529 | 0.378 | 0.0690 | +0.0019 [-0.0046, +0.0079] | -0.0056 [-0.0128, +0.0011] | 0.789 | 0.460 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0204, +0.1948]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0924, ΔBrier vs climatology +0.0371 [+0.0212, +0.0547], realised minus predicted +0.0051 [-0.0271, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.399 | 0.2840 | 0.2720 | +0.0408 [+0.0093, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1330 | 0.0159 | +0.0121 [-0.0077, +0.0283] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0036 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.909 | 0.0734 | 0.1165 | +0.0345 [+0.0094, +0.0662] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0538 | 0.0000 | +0.0269 [+0.0214, +0.0328] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0987 | 0.2439 | 0.0159 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.408 | 0.2915 | 0.2615 | +0.0398 [+0.0095, +0.0713] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1106 | 0.1133 | +0.0395 [+0.0109, +0.0692] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.351 | 0.0788 | 0.0630 | +0.0140 [+0.0065, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0458, +0.1491] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1308 | 0.1461 | +0.0731 [+0.0418, +0.1090] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2756 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.293 | 6.19 flat / 3.33 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.609] | 0.269 | 5.46 flat / 3.00 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.296, 0.629] | 4.000 [2.285, 6.500] | 1.856 [0.989, 3.158] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 4.654 [2.806, 7.314] | 2.010 [1.106, 3.355] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.616] | 3.731 [2.038, 6.134] | 1.519 [0.781, 2.616] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.526] | 4.115 [2.342, 6.850] | 2.269 [1.125, 4.013] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.038 [2.273, 6.800] | 2.067 [1.040, 3.572] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.941 [4.266, 11.154] | 2.882 [1.643, 4.893] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 4.167 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (105 of 1873 days never flag) | 186 | 0.586 | 0.441 | 0.0512 | +0.0202 [+0.0123, +0.0288] | +0.0051 [-0.0009, +0.0112] | 0.901 | 0.526 | yes |
| 2 | 0.384 (147 of 1872 days never flag) | 205 | 0.604 | 0.410 | 0.0589 | +0.0121 [+0.0060, +0.0187] | +0.0021 [-0.0035, +0.0079] | 0.865 | 0.534 | no |
| 3 | 0.368 (147 of 1871 days never flag) | 172 | 0.543 | 0.436 | 0.0601 | +0.0106 [+0.0054, +0.0163] | +0.0043 [-0.0009, +0.0100] | 0.860 | 0.488 | no |
| 4 | 0.418 (147 of 1870 days never flag) | 168 | 0.442 | 0.363 | 0.0618 | +0.0091 [+0.0035, +0.0147] | +0.0006 [-0.0053, +0.0068] | 0.841 | 0.380 | no |
| 5 | 0.467 (147 of 1869 days never flag) | 166 | 0.442 | 0.367 | 0.0675 | +0.0035 [-0.0036, +0.0100] | -0.0041 [-0.0116, +0.0029] | 0.801 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.577 (climatology 0.512, difference +0.0651 [-0.0283, +0.1509]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0888, ΔBrier vs climatology +0.0407 [+0.0254, +0.0568], realised minus predicted +0.0093 [-0.0226, +0.0439]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.2907 | 0.2720 | +0.0403 [+0.0075, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1319 | 0.0159 | +0.0127 [-0.0058, +0.0301] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0076 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0033 | 0.0200 | +0.0037 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.846 | 0.0714 | 0.1165 | +0.0340 [+0.0099, +0.0637] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0540 | 0.0000 | +0.0273 [+0.0217, +0.0334] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0937 | 0.2439 | 0.0154 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.440 | 0.2958 | 0.2615 | +0.0392 [+0.0088, +0.0721] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1113 | 0.1133 | +0.0396 [+0.0110, +0.0709] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.373 | 0.0801 | 0.0630 | +0.0138 [+0.0064, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3184 | 0.2903 | +0.0979 [+0.0430, +0.1462] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1283 | 0.1461 | +0.0745 [+0.0431, +0.1134] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2776 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.711] | 0.269 | 4.81 flat / 2.51 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.262 | 4.54 flat / 2.41 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.184, 0.520] | 3.923 [2.172, 6.333] | 1.837 [0.947, 3.112] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.615] | 3.846 [2.077, 6.333] | 1.856 [0.935, 3.179] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 4.038 [2.286, 6.500] | 2.019 [1.065, 3.368] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.300, 0.625] | 4.423 [2.528, 7.044] | 2.337 [1.206, 3.977] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 3.308 [1.782, 5.522] | 1.529 [0.771, 2.677] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 5.706 [3.142, 9.468] | 2.485 [1.276, 4.350] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.111 [1.111, 7.750] | 2.556 [0.708, 7.003] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.391 (147 of 1873 days never flag) | 173 | 0.507 | 0.410 | 0.0512 | +0.0203 [+0.0122, +0.0287] | +0.0052 [-0.0006, +0.0112] | 0.901 | 0.448 | yes |
| 2 | 0.378 (147 of 1872 days never flag) | 168 | 0.489 | 0.405 | 0.0542 | +0.0168 [+0.0100, +0.0241] | +0.0068 [+0.0003, +0.0135] | 0.877 | 0.432 | yes |
| 3 | 0.438 (126 of 1871 days never flag) | 176 | 0.514 | 0.403 | 0.0555 | +0.0152 [+0.0089, +0.0217] | +0.0089 [+0.0025, +0.0157] | 0.867 | 0.454 | yes |
| 4 | 0.528 (126 of 1870 days never flag) | 184 | 0.500 | 0.375 | 0.0585 | +0.0124 [+0.0060, +0.0187] | +0.0039 [-0.0031, +0.0109] | 0.848 | 0.434 | no |
| 5 | 0.41 (147 of 1869 days never flag) | 150 | 0.464 | 0.427 | 0.0632 | +0.0077 [+0.0015, +0.0139] | +0.0002 [-0.0062, +0.0070] | 0.827 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.695 (climatology 0.512, difference +0.1824 [+0.0988, +0.2706]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0788, ΔBrier vs climatology +0.0507 [+0.0319, +0.0706], realised minus predicted -0.0157 [-0.0465, +0.0164]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.399 | 0.2840 | 0.2720 | +0.0408 [+0.0099, +0.0756] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1330 | 0.0159 | +0.0121 [-0.0068, +0.0290] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0036 [+0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.909 | 0.0734 | 0.1165 | +0.0345 [+0.0094, +0.0650] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0538 | 0.0000 | +0.0269 [+0.0213, +0.0329] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0987 | 0.2439 | 0.0159 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.408 | 0.2915 | 0.2615 | +0.0398 [+0.0092, +0.0714] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1106 | 0.1133 | +0.0395 [+0.0122, +0.0696] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.351 | 0.0788 | 0.0630 | +0.0140 [+0.0064, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0460, +0.1502] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1308 | 0.1461 | +0.0731 [+0.0428, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2756 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.269 | 5.15 flat / 2.82 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.667] | 0.269 | 4.77 flat / 2.68 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.625] | 4.000 [2.241, 6.556] | 1.856 [0.954, 3.227] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 3.923 [2.122, 6.550] | 1.885 [0.950, 3.284] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 3.154 [1.593, 5.333] | 1.423 [0.692, 2.529] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.625] | 4.077 [2.265, 6.750] | 2.202 [1.081, 3.989] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 3.808 [2.038, 6.467] | 1.952 [0.965, 3.442] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.529 [3.000, 9.235] | 2.353 [1.136, 4.227] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 3.694 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (105 of 1873 days never flag) | 186 | 0.586 | 0.441 | 0.0512 | +0.0202 [+0.0123, +0.0285] | +0.0051 [-0.0011, +0.0112] | 0.901 | 0.526 | yes |
| 2 | 0.37 (147 of 1872 days never flag) | 171 | 0.496 | 0.404 | 0.0543 | +0.0168 [+0.0096, +0.0235] | +0.0068 [+0.0002, +0.0135] | 0.879 | 0.438 | yes |
| 3 | 0.368 (147 of 1871 days never flag) | 147 | 0.471 | 0.442 | 0.0554 | +0.0153 [+0.0094, +0.0217] | +0.0090 [+0.0032, +0.0154] | 0.868 | 0.424 | no |
| 4 | 0.407 (105 of 1870 days never flag) | 175 | 0.500 | 0.394 | 0.0563 | +0.0145 [+0.0086, +0.0206] | +0.0061 [-0.0002, +0.0128] | 0.856 | 0.439 | yes |
| 5 | 0.427 (147 of 1869 days never flag) | 164 | 0.471 | 0.396 | 0.0612 | +0.0097 [+0.0034, +0.0159] | +0.0022 [-0.0046, +0.0089] | 0.835 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1668 [+0.0734, +0.2681]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0771, ΔBrier vs climatology +0.0524 [+0.0333, +0.0719], realised minus predicted -0.0116 [-0.0411, +0.0184]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.431 | 0.2907 | 0.2720 | +0.0403 [+0.0076, +0.0757] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1319 | 0.0159 | +0.0127 [-0.0078, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0076 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0033 | 0.0200 | +0.0037 [+0.0002, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.846 | 0.0714 | 0.1165 | +0.0340 [+0.0093, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0540 | 0.0000 | +0.0273 [+0.0212, +0.0330] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0937 | 0.2439 | 0.0154 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.440 | 0.2958 | 0.2615 | +0.0392 [+0.0091, +0.0706] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1113 | 0.1133 | +0.0396 [+0.0112, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.373 | 0.0801 | 0.0630 | +0.0138 [+0.0061, +0.0220] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3184 | 0.2903 | +0.0979 [+0.0456, +0.1459] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1283 | 0.1461 | +0.0745 [+0.0425, +0.1129] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2776 | 0.2213 |

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.450, 0.773] | 0.269 | 5.00 flat / 4.26 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.545] | 0.231 | 3.85 flat / 3.21 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.407, 0.739] | 2.769 [1.812, 4.381] | 2.106 [1.243, 3.609] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 2.269 [1.500, 3.571] | 1.712 [1.033, 2.917] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 2.269 [1.500, 3.584] | 1.692 [1.008, 2.900] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 3.308 [2.205, 5.227] | 2.731 [1.720, 4.588] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.269 [1.459, 3.619] | 1.692 [0.969, 2.965] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.529, 0.882] | 1.294 [0.762, 2.154] | 0.559 [0.287, 1.024] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 12.000 (no interval) | 11.250 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.097 (21 of 1873 days never flag) | 119 | 0.336 | 0.395 | 0.0643 | +0.0071 [+0.0015, +0.0131] | -0.0080 [-0.0162, -0.0004] | 0.645 | 0.294 | no |
| 2 | 0.0847 (126 of 1872 days never flag) | 87 | 0.201 | 0.322 | 0.0676 | +0.0034 [-0.0037, +0.0106] | -0.0066 [-0.0150, +0.0013] | 0.575 | 0.167 | no |
| 3 | 0.0873 (126 of 1871 days never flag) | 86 | 0.196 | 0.314 | 0.0670 | +0.0037 [-0.0035, +0.0104] | -0.0027 [-0.0104, +0.0047] | 0.582 | 0.162 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 115 | 0.210 | 0.252 | 0.0671 | +0.0037 [-0.0026, +0.0096] | -0.0048 [-0.0123, +0.0018] | 0.579 | 0.160 | no |
| 5 | 0.0988 (126 of 1869 days never flag) | 87 | 0.203 | 0.322 | 0.0663 | +0.0047 [-0.0022, +0.0109] | -0.0029 [-0.0104, +0.0041] | 0.581 | 0.169 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 4.4 over 1041 days; regime_2021-23: 5.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 7.5 over 1041 days; regime_2021-23: 10.8 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.642 (climatology 0.512, difference +0.1298 [+0.0281, +0.2339]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1113, ΔBrier vs climatology +0.0182 [+0.0076, +0.0297], realised minus predicted +0.0591 [+0.0253, +0.0967]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.627 | 0.0990 | 0.2720 | -0.0111 [-0.0320, +0.0100] |
| regime | 2020 | 251 | 4 | 0.250 | 0.024 | 0.0630 | 0.0159 | +0.0047 [-0.0118, +0.0203] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0109 | 0.0200 | +0.0018 [-0.0033, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.650 | 0.0489 | 0.1165 | +0.0227 [+0.0039, +0.0475] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.111 | 0.0056 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0333 | 0.0000 | +0.0121 [-0.0003, +0.0227] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.286 | 0.0819 | 0.2439 | -0.0305 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.352 | 0.603 | 0.1054 | 0.2615 | +0.0034 [-0.0176, +0.0257] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1188 | 0.1133 | +0.0214 [-0.0122, +0.0556] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.410 | 0.0146 | 0.0630 | +0.0008 [-0.0048, +0.0059] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.375 | 0.3544 | 0.2903 | +0.0945 [+0.0001, +0.1888] |
| day_type | tax_date | 89 | 13 | 0.923 | 0.387 | 0.2000 | 0.1461 | +0.0663 [+0.0181, +0.1187] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.231 | 2.81 flat / 2.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.58 flat / 0.99 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.750] | 2.346 [1.517, 3.751] | 1.692 [0.963, 2.938] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.166, 0.458] | 1.846 [1.158, 2.900] | 1.260 [0.660, 2.203] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.538 [0.937, 2.375] | 0.981 [0.481, 1.724] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.705, 1.684] | 0.558 [0.276, 0.988] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.176 [0.667, 1.909] | 0.471 [0.224, 0.865] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.889 (no interval) | 5.194 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.124 (126 of 1873 days never flag) | 107 | 0.329 | 0.430 | 0.0648 | +0.0066 [-0.0000, +0.0132] | -0.0084 [-0.0172, +0.0000] | 0.638 | 0.293 | no |
| 2 | 0.171 (126 of 1872 days never flag) | 77 | 0.209 | 0.377 | 0.0687 | +0.0024 [-0.0055, +0.0094] | -0.0076 [-0.0167, -0.0000] | 0.579 | 0.181 | no |
| 3 | 0.163 (126 of 1871 days never flag) | 70 | 0.217 | 0.429 | 0.0679 | +0.0028 [-0.0046, +0.0098] | -0.0035 [-0.0116, +0.0039] | 0.584 | 0.194 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0666 | +0.0042 [-0.0031, +0.0111] | -0.0042 [-0.0124, +0.0035] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 55 | 0.203 | 0.509 | 0.0665 | +0.0044 [-0.0025, +0.0111] | -0.0031 [-0.0114, +0.0046] | 0.584 | 0.187 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
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
| regime | 2020 | 251 | 4 | 0.250 | 0.029 | 0.0535 | 0.0159 | +0.0165 [+0.0051, +0.0274] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0116 | 0.0200 | +0.0014 [-0.0050, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0522 | 0.1165 | +0.0232 [+0.0036, +0.0459] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0055 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0303 | 0.0000 | +0.0173 [+0.0085, +0.0247] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.0788 | 0.2439 | -0.0198 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.618 | 0.1206 | 0.2615 | -0.0027 [-0.0269, +0.0225] |
| day_type | month_end | 150 | 17 | 0.765 | 0.419 | 0.1438 | 0.1133 | +0.0138 [-0.0251, +0.0536] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.459 | 0.0161 | 0.0630 | +0.0022 [-0.0035, +0.0076] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3214 | 0.2903 | +0.0712 [-0.0019, +0.1363] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.385 | 0.2112 | 0.1461 | +0.0525 [+0.0089, +0.0978] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.792] | 0.418 | 8.00 flat / 3.90 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.368, 0.714] | 0.299 | 6.35 flat / 2.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.758] | 5.269 [3.541, 7.714] | 2.462 [1.565, 3.767] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 5.038 [3.344, 7.502] | 2.067 [1.304, 3.196] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.679] | 5.077 [3.300, 7.619] | 2.212 [1.387, 3.443] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.643] | 4.577 [2.973, 7.000] | 2.048 [1.267, 3.259] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 5.192 [3.384, 7.800] | 2.308 [1.461, 3.584] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 7.000 [4.500, 10.909] | 2.779 [1.678, 4.625] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.889 (no interval) | 6.028 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.26 (126 of 1873 days never flag) | 229 | 0.657 | 0.402 | 0.0549 | +0.0166 [+0.0078, +0.0256] | +0.0015 [-0.0051, +0.0076] | 0.879 | 0.578 | yes |
| 2 | 0.276 (126 of 1872 days never flag) | 227 | 0.691 | 0.423 | 0.0601 | +0.0109 [+0.0049, +0.0173] | +0.0009 [-0.0039, +0.0056] | 0.846 | 0.615 | yes |
| 3 | 0.25 (126 of 1871 days never flag) | 225 | 0.674 | 0.413 | 0.0617 | +0.0089 [+0.0030, +0.0153] | +0.0026 [-0.0027, +0.0081] | 0.834 | 0.598 | yes |
| 4 | 0.255 (126 of 1870 days never flag) | 197 | 0.565 | 0.396 | 0.0591 | +0.0117 [+0.0055, +0.0184] | +0.0032 [-0.0022, +0.0090] | 0.847 | 0.497 | yes |
| 5 | 0.325 (126 of 1869 days never flag) | 223 | 0.638 | 0.395 | 0.0599 | +0.0110 [+0.0051, +0.0174] | +0.0035 [-0.0016, +0.0093] | 0.842 | 0.560 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.512, difference +0.1248 [+0.0086, +0.2320]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0410 [+0.0234, +0.0604], realised minus predicted -0.0190 [-0.0489, +0.0130]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.437 | 0.2604 | 0.2720 | +0.0343 [+0.0002, +0.0683] |
| regime | 2020 | 251 | 4 | 0.250 | 0.034 | 0.1562 | 0.0159 | +0.0002 [-0.0148, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0214 | 0.0000 | +0.0130 [+0.0112, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0417 | 0.0200 | -0.0016 [-0.0088, +0.0039] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.567 | 0.1284 | 0.1165 | +0.0351 [+0.0021, +0.0751] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0271 | 0.0048 | +0.0072 [+0.0045, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0936 | 0.0000 | +0.0109 [+0.0019, +0.0189] |
| scarcity_state | 2 | 41 | 10 | 0.400 | 0.444 | 0.1994 | 0.2439 | 0.0225 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.435 | 0.2710 | 0.2615 | +0.0401 [+0.0092, +0.0724] |
| day_type | month_end | 150 | 17 | 0.765 | 0.520 | 0.1531 | 0.1133 | +0.0189 [-0.0231, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.364 | 0.0895 | 0.0630 | +0.0133 [+0.0059, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3214 | 0.2903 | +0.0712 [-0.0034, +0.1375] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.2112 | 0.1461 | +0.0525 [+0.0098, +0.1012] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.824] | 0.421 | 8.04 flat / 4.21 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.280 | 6.00 flat / 3.04 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.676] | 3.654 [2.550, 5.400] | 1.817 [1.148, 2.967] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 4.115 [2.870, 5.947] | 1.663 [1.143, 2.473] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.227, 0.536] | 3.731 [2.441, 5.706] | 1.788 [1.142, 2.848] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.542] | 3.923 [2.733, 5.778] | 1.913 [1.277, 2.946] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.321, 0.667] | 4.115 [2.742, 6.105] | 1.962 [1.282, 3.044] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [4.083, 9.786] | 2.441 [1.562, 3.834] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.167, 0.714] | 11.444 [7.444, 23.750] | 7.556 [4.481, 17.881] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.26 (126 of 1873 days never flag) | 179 | 0.600 | 0.469 | 0.0567 | +0.0147 [+0.0068, +0.0231] | -0.0004 [-0.0068, +0.0059] | 0.795 | 0.545 | no |
| 2 | 0.164 (126 of 1872 days never flag) | 185 | 0.561 | 0.422 | 0.0624 | +0.0087 [+0.0021, +0.0155] | -0.0013 [-0.0065, +0.0039] | 0.751 | 0.499 | no |
| 3 | 0.294 (126 of 1871 days never flag) | 166 | 0.500 | 0.416 | 0.0618 | +0.0089 [+0.0023, +0.0153] | +0.0026 [-0.0034, +0.0084] | 0.753 | 0.444 | no |
| 4 | 0.194 (126 of 1870 days never flag) | 168 | 0.478 | 0.393 | 0.0600 | +0.0108 [+0.0045, +0.0170] | +0.0024 [-0.0029, +0.0076] | 0.767 | 0.419 | no |
| 5 | 0.218 (126 of 1869 days never flag) | 182 | 0.543 | 0.412 | 0.0605 | +0.0104 [+0.0042, +0.0170] | +0.0029 [-0.0026, +0.0083] | 0.754 | 0.482 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1023 [-0.0332, +0.2353]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0906, ΔBrier vs climatology +0.0389 [+0.0218, +0.0573], realised minus predicted +0.0262 [-0.0015, +0.0547]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.564 | 0.1907 | 0.2720 | +0.0187 [-0.0118, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.033 | 0.0611 | 0.0159 | +0.0093 [-0.0083, +0.0254] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0066 | 0.0000 | +0.0135 [+0.0116, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0241 | 0.0200 | -0.0015 [-0.0094, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.556 | 0.1034 | 0.1165 | +0.0343 [+0.0031, +0.0715] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0132 | 0.0048 | +0.0074 [+0.0046, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0315 | 0.0000 | +0.0172 [+0.0085, +0.0248] |
| scarcity_state | 2 | 41 | 10 | 0.500 | 0.500 | 0.1683 | 0.2439 | 0.0203 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.542 | 0.1945 | 0.2615 | +0.0285 [+0.0001, +0.0585] |
| day_type | month_end | 150 | 17 | 0.882 | 0.517 | 0.1476 | 0.1133 | +0.0195 [-0.0207, +0.0625] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.458 | 0.0453 | 0.0630 | +0.0111 [+0.0044, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3214 | 0.2903 | +0.0712 [+0.0011, +0.1382] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2112 | 0.1461 | +0.0525 [+0.0092, +0.0984] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.394 | 7.62 flat / 3.94 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.682] | 0.346 | 6.58 flat / 3.22 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 4.615 [2.938, 7.067] | 2.240 [1.383, 3.599] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.767, 6.953] | 1.865 [1.080, 3.033] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.077 [3.077, 7.957] | 2.385 [1.327, 4.087] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 4.731 [3.000, 7.223] | 2.250 [1.341, 3.594] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.269 [3.348, 7.875] | 2.385 [1.483, 3.739] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.000 [5.214, 12.500] | 3.559 [2.145, 5.887] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.889 (no interval) | 4.667 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.26 (126 of 1873 days never flag) | 206 | 0.614 | 0.417 | 0.0551 | +0.0163 [+0.0089, +0.0244] | +0.0012 [-0.0049, +0.0074] | 0.865 | 0.545 | yes |
| 2 | 0.276 (126 of 1872 days never flag) | 207 | 0.640 | 0.430 | 0.0592 | +0.0119 [+0.0064, +0.0181] | +0.0019 [-0.0027, +0.0068] | 0.825 | 0.572 | yes |
| 3 | 0.248 (126 of 1871 days never flag) | 214 | 0.594 | 0.383 | 0.0601 | +0.0106 [+0.0051, +0.0172] | +0.0043 [-0.0014, +0.0107] | 0.825 | 0.518 | yes |
| 4 | 0.243 (126 of 1870 days never flag) | 196 | 0.529 | 0.372 | 0.0573 | +0.0135 [+0.0080, +0.0197] | +0.0050 [+0.0000, +0.0109] | 0.843 | 0.458 | no |
| 5 | 0.242 (126 of 1869 days never flag) | 222 | 0.616 | 0.383 | 0.0578 | +0.0131 [+0.0074, +0.0190] | +0.0056 [-0.0001, +0.0113] | 0.844 | 0.537 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1286 [+0.0083, +0.2335]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0893, ΔBrier vs climatology +0.0402 [+0.0228, +0.0569], realised minus predicted -0.0103 [-0.0410, +0.0204]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.434 | 0.2415 | 0.2720 | +0.0275 [-0.0047, +0.0596] |
| regime | 2020 | 251 | 4 | 0.250 | 0.045 | 0.1471 | 0.0159 | +0.0054 [-0.0058, +0.0168] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0115, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0336 | 0.0200 | +0.0007 [-0.0050, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.652 | 0.1128 | 0.1165 | +0.0352 [+0.0057, +0.0727] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0223 | 0.0048 | +0.0082 [+0.0063, +0.0100] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0884 | 0.0000 | +0.0116 [+0.0025, +0.0196] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.1734 | 0.2439 | 0.0226 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.664 | 0.454 | 0.2508 | 0.2615 | +0.0363 [+0.0083, +0.0660] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.1501 | 0.1133 | +0.0153 [-0.0248, +0.0562] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.381 | 0.0790 | 0.0630 | +0.0133 [+0.0068, +0.0204] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3214 | 0.2903 | +0.0712 [-0.0019, +0.1378] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.2112 | 0.1461 | +0.0525 [+0.0096, +0.1022] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2483 | 0.2213 |

## risk_quantile_skewt_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.781] | 0.387 | 7.50 flat / 3.61 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.704] | 0.278 | 5.96 flat / 2.69 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.391, 0.750] | 5.192 [3.417, 7.715] | 2.442 [1.537, 3.868] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.923 [3.205, 7.354] | 2.019 [1.250, 3.163] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.316, 0.677] | 4.885 [3.115, 7.368] | 2.115 [1.288, 3.375] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.423 [2.774, 6.808] | 1.952 [1.156, 3.125] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.316, 0.680] | 5.038 [3.233, 7.525] | 2.192 [1.351, 3.459] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 7.000 [4.498, 10.910] | 2.779 [1.625, 4.700] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.444 (no interval) | 5.167 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.26 (126 of 1873 days never flag) | 227 | 0.657 | 0.405 | 0.0540 | +0.0174 [+0.0090, +0.0264] | +0.0023 [-0.0042, +0.0089] | 0.900 | 0.579 | yes |
| 2 | 0.276 (126 of 1872 days never flag) | 224 | 0.691 | 0.429 | 0.0592 | +0.0118 [+0.0058, +0.0186] | +0.0018 [-0.0027, +0.0067] | 0.880 | 0.617 | yes |
| 3 | 0.25 (126 of 1871 days never flag) | 220 | 0.674 | 0.423 | 0.0598 | +0.0109 [+0.0049, +0.0171] | +0.0045 [-0.0009, +0.0102] | 0.875 | 0.601 | yes |
| 4 | 0.255 (126 of 1870 days never flag) | 194 | 0.572 | 0.407 | 0.0577 | +0.0132 [+0.0069, +0.0197] | +0.0047 [-0.0009, +0.0101] | 0.878 | 0.506 | yes |
| 5 | 0.325 (126 of 1869 days never flag) | 219 | 0.638 | 0.402 | 0.0587 | +0.0122 [+0.0063, +0.0184] | +0.0046 [-0.0007, +0.0105] | 0.874 | 0.562 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.512, difference +0.1248 [+0.0105, +0.2321]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0427 [+0.0244, +0.0614], realised minus predicted +0.0051 [-0.0239, +0.0351]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.437 | 0.2604 | 0.2720 | +0.0343 [-0.0011, +0.0666] |
| regime | 2020 | 251 | 4 | 0.250 | 0.034 | 0.1559 | 0.0159 | +0.0002 [-0.0144, +0.0143] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0070 | 0.0000 | +0.0134 [+0.0117, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0117 | 0.0200 | +0.0014 [-0.0049, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.586 | 0.1119 | 0.1165 | +0.0376 [+0.0057, +0.0784] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0055 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0936 | 0.0000 | +0.0109 [+0.0026, +0.0188] |
| scarcity_state | 2 | 41 | 10 | 0.400 | 0.444 | 0.1994 | 0.2439 | 0.0225 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.435 | 0.2710 | 0.2615 | +0.0401 [+0.0090, +0.0728] |
| day_type | month_end | 150 | 17 | 0.765 | 0.520 | 0.1511 | 0.1133 | +0.0190 [-0.0252, +0.0599] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.368 | 0.0757 | 0.0630 | +0.0143 [+0.0069, +0.0223] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3214 | 0.2903 | +0.0712 [-0.0002, +0.1350] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.2112 | 0.1461 | +0.0525 [+0.0102, +0.0997] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.499, 0.815] | 0.423 | 8.12 flat / 4.21 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.364, 0.708] | 0.346 | 6.58 flat / 3.23 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.364, 0.714] | 4.885 [3.230, 7.533] | 2.510 [1.579, 4.149] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.320, 0.688] | 5.500 [3.781, 8.167] | 2.394 [1.586, 3.760] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.324, 0.680] | 5.385 [3.595, 8.214] | 2.567 [1.630, 4.066] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.846 [3.150, 7.445] | 2.365 [1.475, 3.870] |
| lead 5 alone (fail) | 26 | 14 | 0.538 [0.375, 0.714] | 5.423 [3.562, 8.200] | 2.625 [1.652, 4.162] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.765 [4.315, 10.847] | 2.706 [1.591, 4.688] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.249, 0.833] | 10.667 [6.818, 21.750] | 7.056 [4.022, 16.189] |

Recall with equal weight per regime: 0.501 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.26 (126 of 1873 days never flag) | 209 | 0.586 | 0.392 | 0.0554 | +0.0160 [+0.0095, +0.0226] | +0.0009 [-0.0056, +0.0073] | 0.879 | 0.512 | no |
| 2 | 0.138 (126 of 1872 days never flag) | 241 | 0.705 | 0.407 | 0.0604 | +0.0107 [+0.0052, +0.0161] | +0.0007 [-0.0047, +0.0057] | 0.848 | 0.623 | no |
| 3 | 0.163 (126 of 1871 days never flag) | 231 | 0.659 | 0.394 | 0.0609 | +0.0097 [+0.0044, +0.0153] | +0.0034 [-0.0023, +0.0090] | 0.833 | 0.579 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 202 | 0.551 | 0.376 | 0.0590 | +0.0118 [+0.0065, +0.0173] | +0.0034 [-0.0020, +0.0087] | 0.844 | 0.478 | no |
| 5 | 0.167 (126 of 1869 days never flag) | 231 | 0.652 | 0.390 | 0.0593 | +0.0116 [+0.0061, +0.0172] | +0.0041 [-0.0017, +0.0098] | 0.840 | 0.571 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.631 (climatology 0.512, difference +0.1192 [+0.0054, +0.2273]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0930, ΔBrier vs climatology +0.0365 [+0.0212, +0.0518], realised minus predicted +0.0189 [-0.0120, +0.0500]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.449 | 0.1897 | 0.2720 | +0.0198 [-0.0072, +0.0437] |
| regime | 2020 | 251 | 4 | 0.250 | 0.030 | 0.1048 | 0.0159 | +0.0135 [+0.0019, +0.0245] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0121 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0267 | 0.0200 | +0.0008 [-0.0057, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.0903 | 0.1165 | +0.0357 [+0.0066, +0.0714] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0163 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0620 | 0.0000 | +0.0157 [+0.0063, +0.0235] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1391 | 0.2439 | 0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.447 | 0.1958 | 0.2615 | +0.0333 [+0.0089, +0.0576] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1484 | 0.1133 | +0.0167 [-0.0255, +0.0558] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.360 | 0.0528 | 0.0630 | +0.0129 [+0.0080, +0.0179] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1362] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2112 | 0.1461 | +0.0525 [+0.0086, +0.1013] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2171 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.688] | 0.293 | 6.19 flat / 3.03 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.643] | 0.269 | 5.35 flat / 2.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.688] | 4.692 [2.889, 7.273] | 2.135 [1.200, 3.462] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 4.308 [2.613, 6.667] | 1.721 [0.976, 2.875] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.923 [2.920, 7.682] | 2.260 [1.240, 3.742] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.231 [2.450, 6.824] | 2.125 [1.121, 3.611] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.652] | 4.885 [2.931, 7.685] | 2.356 [1.302, 3.888] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 7.353 [4.750, 11.309] | 2.985 [1.733, 4.950] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 4.000 (no interval) | 3.111 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 206 | 0.600 | 0.408 | 0.0677 | +0.0037 [-0.0070, +0.0141] | -0.0114 [-0.0211, -0.0021] | 0.862 | 0.530 | yes |
| 2 | 0.577 (126 of 1872 days never flag) | 197 | 0.612 | 0.431 | 0.0717 | -0.0006 [-0.0105, +0.0085] | -0.0106 [-0.0193, -0.0023] | 0.823 | 0.547 | yes |
| 3 | 0.567 (126 of 1871 days never flag) | 212 | 0.609 | 0.396 | 0.0738 | -0.0031 [-0.0141, +0.0060] | -0.0094 [-0.0201, -0.0008] | 0.812 | 0.535 | no |
| 4 | 0.549 (126 of 1870 days never flag) | 178 | 0.493 | 0.382 | 0.0700 | +0.0009 [-0.0077, +0.0092] | -0.0076 [-0.0158, +0.0007] | 0.829 | 0.429 | no |
| 5 | 0.519 (126 of 1869 days never flag) | 206 | 0.572 | 0.383 | 0.0697 | +0.0012 [-0.0066, +0.0084] | -0.0063 [-0.0142, +0.0007] | 0.811 | 0.499 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.512, difference +0.1061 [+0.0031, +0.2035]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0155, +0.0527], realised minus predicted -0.0269 [-0.0589, +0.0055]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.408 | 0.3348 | 0.2720 | -0.0100 [-0.0551, +0.0358] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.2307 | 0.0159 | -0.0271 [-0.0463, -0.0094] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0184 | 0.0000 | +0.0119 [+0.0105, +0.0133] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0160 | 0.0200 | +0.0003 [-0.0063, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0820 | 0.1165 | +0.0344 [+0.0052, +0.0718] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0118 | 0.0048 | +0.0078 [+0.0055, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1381 | 0.0000 | -0.0024 [-0.0130, +0.0074] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1557 | 0.2439 | 0.0113 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.421 | 0.3342 | 0.2615 | -0.0018 [-0.0415, +0.0393] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1545 | 0.1133 | +0.0163 [-0.0259, +0.0584] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.356 | 0.1059 | 0.0630 | -0.0015 [-0.0118, +0.0085] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0005, +0.1352] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0098, +0.0993] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.680] | 0.291 | 6.15 flat / 2.99 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.619] | 0.269 | 4.85 flat / 2.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.154 [2.444, 6.573] | 1.952 [1.080, 3.250] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.846 [2.939, 7.557] | 2.144 [1.188, 3.548] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.231 [2.517, 6.715] | 1.846 [1.075, 3.039] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 4.231 [2.562, 6.697] | 1.942 [1.136, 3.179] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.522] | 3.538 [1.999, 5.810] | 1.663 [0.900, 2.846] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.176 [4.476, 11.438] | 2.971 [1.694, 5.021] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.222 [2.235, 9.500] | 3.028 [1.400, 7.460] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.471 (126 of 1873 days never flag) | 185 | 0.550 | 0.416 | 0.0644 | +0.0070 [-0.0030, +0.0175] | -0.0081 [-0.0171, +0.0005] | 0.860 | 0.488 | yes |
| 2 | 0.551 (126 of 1872 days never flag) | 211 | 0.612 | 0.403 | 0.0699 | +0.0012 [-0.0088, +0.0103] | -0.0088 [-0.0183, -0.0003] | 0.830 | 0.539 | yes |
| 3 | 0.537 (126 of 1871 days never flag) | 191 | 0.587 | 0.424 | 0.0732 | -0.0025 [-0.0130, +0.0071] | -0.0088 [-0.0190, +0.0002] | 0.806 | 0.523 | no |
| 4 | 0.553 (126 of 1870 days never flag) | 180 | 0.507 | 0.389 | 0.0732 | -0.0023 [-0.0113, +0.0067] | -0.0108 [-0.0194, -0.0017] | 0.821 | 0.444 | yes |
| 5 | 0.517 (126 of 1869 days never flag) | 165 | 0.529 | 0.442 | 0.0743 | -0.0034 [-0.0115, +0.0047] | -0.0109 [-0.0191, -0.0028] | 0.809 | 0.476 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.512, difference +0.1039 [+0.0245, +0.1829]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0981, ΔBrier vs climatology +0.0314 [+0.0137, +0.0504], realised minus predicted -0.0289 [-0.0613, +0.0043]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.3200 | 0.2720 | +0.0012 [-0.0435, +0.0435] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.2229 | 0.0159 | -0.0200 [-0.0404, -0.0017] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0155 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0814 | 0.1165 | +0.0345 [+0.0051, +0.0705] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0117 | 0.0048 | +0.0079 [+0.0058, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1314 | 0.0000 | +0.0030 [-0.0051, +0.0107] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1475 | 0.2439 | 0.0271 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.424 | 0.3230 | 0.2615 | +0.0059 [-0.0336, +0.0464] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1365 | 0.1133 | +0.0304 [-0.0017, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.355 | 0.1035 | 0.0630 | +0.0001 [-0.0101, +0.0102] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0303, +0.1580] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.2028 | 0.1461 | +0.0603 [+0.0163, +0.1065] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.800] | 0.269 | 5.73 flat / 2.74 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.381, 0.760] | 0.231 | 4.04 flat / 1.97 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 4.692 [2.893, 7.287] | 2.135 [1.216, 3.552] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.308 [2.514, 6.955] | 2.115 [1.167, 3.590] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.308 [1.783, 5.528] | 1.538 [0.798, 2.706] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.290, 0.636] | 3.615 [2.088, 5.945] | 1.712 [0.973, 2.871] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.296, 0.639] | 3.231 [1.697, 5.410] | 1.462 [0.740, 2.579] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.471 [3.933, 10.563] | 2.676 [1.488, 4.701] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.861 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 206 | 0.600 | 0.408 | 0.0677 | +0.0037 [-0.0072, +0.0144] | -0.0114 [-0.0210, -0.0021] | 0.862 | 0.530 | yes |
| 2 | 0.543 (126 of 1872 days never flag) | 188 | 0.547 | 0.404 | 0.0659 | +0.0052 [-0.0049, +0.0150] | -0.0048 [-0.0150, +0.0047] | 0.844 | 0.482 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 154 | 0.493 | 0.442 | 0.0703 | +0.0004 [-0.0105, +0.0101] | -0.0059 [-0.0171, +0.0039] | 0.820 | 0.443 | yes |
| 4 | 0.497 (126 of 1870 days never flag) | 163 | 0.500 | 0.423 | 0.0653 | +0.0055 [-0.0035, +0.0146] | -0.0030 [-0.0122, +0.0059] | 0.844 | 0.446 | yes |
| 5 | 0.6 (126 of 1869 days never flag) | 152 | 0.493 | 0.447 | 0.0694 | +0.0016 [-0.0079, +0.0112] | -0.0060 [-0.0152, +0.0032] | 0.837 | 0.444 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1289 [-0.0295, +0.3063]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0943, ΔBrier vs climatology +0.0352 [+0.0134, +0.0597], realised minus predicted -0.0509 [-0.0820, -0.0191]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.408 | 0.3348 | 0.2720 | -0.0100 [-0.0553, +0.0370] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.2307 | 0.0159 | -0.0271 [-0.0472, -0.0088] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0184 | 0.0000 | +0.0119 [+0.0104, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0160 | 0.0200 | +0.0003 [-0.0061, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0820 | 0.1165 | +0.0344 [+0.0052, +0.0733] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0118 | 0.0048 | +0.0078 [+0.0057, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1381 | 0.0000 | -0.0024 [-0.0138, +0.0073] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1557 | 0.2439 | 0.0113 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.656 | 0.421 | 0.3342 | 0.2615 | -0.0018 [-0.0419, +0.0403] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1545 | 0.1133 | +0.0163 [-0.0234, +0.0572] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.356 | 0.1059 | 0.0630 | -0.0015 [-0.0117, +0.0086] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0010, +0.1361] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0103, +0.0964] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.789] | 0.269 | 5.31 flat / 2.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.393, 0.750] | 0.269 | 4.62 flat / 2.29 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.633] | 4.154 [2.384, 6.462] | 1.952 [1.067, 3.143] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.300, 0.629] | 3.692 [2.143, 5.824] | 1.663 [0.908, 2.750] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.304, 0.684] | 3.846 [2.130, 6.000] | 1.721 [0.935, 2.817] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.548] | 3.615 [1.833, 6.043] | 1.798 [0.839, 3.137] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.269 [1.667, 5.353] | 1.548 [0.759, 2.621] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.639, 10.183] | 2.618 [1.395, 4.472] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.601] | 3.556 [1.818, 7.505] | 2.389 [0.950, 5.833] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.471 (126 of 1873 days never flag) | 185 | 0.550 | 0.416 | 0.0644 | +0.0070 [-0.0026, +0.0165] | -0.0081 [-0.0164, -0.0000] | 0.860 | 0.488 | yes |
| 2 | 0.571 (126 of 1872 days never flag) | 172 | 0.547 | 0.442 | 0.0660 | +0.0050 [-0.0049, +0.0145] | -0.0050 [-0.0143, +0.0042] | 0.842 | 0.491 | yes |
| 3 | 0.604 (126 of 1871 days never flag) | 178 | 0.565 | 0.438 | 0.0693 | +0.0014 [-0.0092, +0.0115] | -0.0050 [-0.0154, +0.0052] | 0.828 | 0.508 | yes |
| 4 | 0.659 (126 of 1870 days never flag) | 161 | 0.486 | 0.416 | 0.0660 | +0.0048 [-0.0042, +0.0136] | -0.0036 [-0.0123, +0.0054] | 0.845 | 0.431 | yes |
| 5 | 0.527 (126 of 1869 days never flag) | 152 | 0.486 | 0.441 | 0.0686 | +0.0023 [-0.0058, +0.0105] | -0.0052 [-0.0139, +0.0030] | 0.821 | 0.436 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.3200 | 0.2720 | +0.0012 [-0.0405, +0.0420] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.2229 | 0.0159 | -0.0200 [-0.0414, -0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0155 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0814 | 0.1165 | +0.0345 [+0.0052, +0.0721] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0117 | 0.0048 | +0.0079 [+0.0057, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1314 | 0.0000 | +0.0030 [-0.0055, +0.0103] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1475 | 0.2439 | 0.0271 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.424 | 0.3230 | 0.2615 | +0.0059 [-0.0306, +0.0429] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1365 | 0.1133 | +0.0304 [-0.0015, +0.0625] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.355 | 0.1035 | 0.0630 | +0.0001 [-0.0097, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0221, +0.1551] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.2028 | 0.1461 | +0.0603 [+0.0176, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.715] | 0.356 | 6.65 flat / 3.24 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.680] | 0.269 | 5.65 flat / 2.75 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.682] | 4.269 [2.555, 6.591] | 1.846 [1.022, 3.047] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.423 [2.667, 6.913] | 1.760 [0.968, 2.917] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.846 [2.786, 7.683] | 2.221 [1.175, 3.788] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 4.423 [2.600, 7.125] | 2.202 [1.177, 3.833] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 5.115 [3.045, 7.955] | 2.481 [1.380, 4.153] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 7.353 [4.591, 11.572] | 2.985 [1.697, 5.119] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.333 [2.867, 12.000] | 3.722 [1.854, 9.083] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 197 | 0.614 | 0.437 | 0.0631 | +0.0083 [-0.0002, +0.0176] | -0.0068 [-0.0144, +0.0005] | 0.832 | 0.550 | yes |
| 2 | 0.489 (126 of 1872 days never flag) | 200 | 0.612 | 0.425 | 0.0698 | +0.0013 [-0.0057, +0.0078] | -0.0087 [-0.0150, -0.0026] | 0.780 | 0.545 | yes |
| 3 | 0.431 (126 of 1871 days never flag) | 211 | 0.616 | 0.403 | 0.0711 | -0.0004 [-0.0067, +0.0060] | -0.0067 [-0.0131, +0.0001] | 0.750 | 0.543 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 184 | 0.500 | 0.375 | 0.0689 | +0.0019 [-0.0045, +0.0087] | -0.0066 [-0.0129, +0.0002] | 0.775 | 0.434 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 213 | 0.580 | 0.376 | 0.0697 | +0.0012 [-0.0057, +0.0079] | -0.0063 [-0.0135, +0.0008] | 0.764 | 0.503 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.512, difference +0.1061 [+0.0022, +0.2035]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0980, ΔBrier vs climatology +0.0315 [+0.0130, +0.0495], realised minus predicted -0.0433 [-0.0765, -0.0106]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.435 | 0.3059 | 0.2720 | +0.0161 [-0.0193, +0.0531] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2388 | 0.0159 | -0.0251 [-0.0390, -0.0110] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0384 | 0.0000 | +0.0102 [+0.0086, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0205 | 0.0200 | +0.0003 [-0.0059, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0807 | 0.1165 | +0.0323 [+0.0068, +0.0663] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0252 | 0.0048 | +0.0074 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1577 | 0.0000 | -0.0082 [-0.0188, +0.0012] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1329 | 0.2439 | -0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.452 | 0.3087 | 0.2615 | +0.0225 [-0.0087, +0.0583] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1552 | 0.1133 | +0.0155 [-0.0248, +0.0562] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.391 | 0.1102 | 0.0630 | +0.0039 [-0.0037, +0.0121] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0005, +0.1381] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0074, +0.0991] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.714] | 0.303 | 6.38 flat / 3.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.269 | 5.12 flat / 2.45 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.231 [2.540, 6.480] | 1.971 [1.094, 3.191] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.773, 6.826] | 1.894 [1.091, 2.990] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.231 [2.478, 6.600] | 1.885 [1.043, 3.042] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.462 [2.690, 6.895] | 2.135 [1.250, 3.388] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 3.731 [2.146, 5.913] | 1.788 [0.989, 2.951] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.118 [4.520, 11.100] | 2.912 [1.679, 4.792] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.000 (no interval) | 3.389 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.471 (126 of 1873 days never flag) | 189 | 0.564 | 0.418 | 0.0599 | +0.0115 [+0.0032, +0.0198] | -0.0036 [-0.0101, +0.0030] | 0.829 | 0.501 | yes |
| 2 | 0.489 (126 of 1872 days never flag) | 202 | 0.612 | 0.421 | 0.0680 | +0.0031 [-0.0038, +0.0098] | -0.0069 [-0.0135, +0.0003] | 0.790 | 0.544 | no |
| 3 | 0.466 (126 of 1871 days never flag) | 194 | 0.609 | 0.433 | 0.0705 | +0.0002 [-0.0070, +0.0069] | -0.0062 [-0.0136, +0.0011] | 0.743 | 0.545 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 187 | 0.514 | 0.380 | 0.0721 | -0.0013 [-0.0085, +0.0052] | -0.0097 [-0.0172, -0.0027] | 0.765 | 0.448 | no |
| 5 | 0.498 (126 of 1869 days never flag) | 170 | 0.529 | 0.429 | 0.0744 | -0.0034 [-0.0110, +0.0037] | -0.0110 [-0.0188, -0.0034] | 0.760 | 0.473 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1026 [+0.0223, +0.1873]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1007, ΔBrier vs climatology +0.0288 [+0.0111, +0.0476], realised minus predicted -0.0454 [-0.0756, -0.0110]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.2910 | 0.2720 | +0.0272 [-0.0050, +0.0612] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2310 | 0.0159 | -0.0180 [-0.0316, -0.0051] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0201 | 0.0200 | +0.0007 [-0.0057, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0801 | 0.1165 | +0.0324 [+0.0057, +0.0639] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0251 | 0.0048 | +0.0074 [+0.0055, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1510 | 0.0000 | -0.0028 [-0.0104, +0.0044] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1246 | 0.2439 | 0.0060 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.428 | 0.2976 | 0.2615 | +0.0302 [-0.0017, +0.0627] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1372 | 0.1133 | +0.0296 [-0.0022, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.359 | 0.1077 | 0.0630 | +0.0055 [-0.0025, +0.0131] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0261, +0.1579] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.2028 | 0.1461 | +0.0603 [+0.0192, +0.1066] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.269 | 5.62 flat / 2.66 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.367, 0.727] | 0.231 | 4.04 flat / 1.98 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 4.269 [2.718, 6.601] | 1.846 [1.091, 3.011] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 4.308 [2.577, 6.920] | 2.144 [1.236, 3.542] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 3.462 [2.000, 5.667] | 1.654 [0.885, 2.778] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.625] | 3.577 [2.100, 5.847] | 1.721 [1.018, 2.880] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.565] | 3.077 [1.591, 5.279] | 1.365 [0.667, 2.408] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 6.471 [4.048, 10.444] | 2.676 [1.525, 4.715] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.000 (no interval) | 2.639 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 197 | 0.614 | 0.437 | 0.0631 | +0.0083 [-0.0001, +0.0170] | -0.0068 [-0.0144, +0.0007] | 0.832 | 0.550 | yes |
| 2 | 0.477 (126 of 1872 days never flag) | 186 | 0.532 | 0.398 | 0.0632 | +0.0078 [+0.0006, +0.0160] | -0.0022 [-0.0095, +0.0061] | 0.815 | 0.468 | yes |
| 3 | 0.466 (126 of 1871 days never flag) | 162 | 0.522 | 0.444 | 0.0671 | +0.0036 [-0.0044, +0.0114] | -0.0027 [-0.0113, +0.0055] | 0.768 | 0.470 | no |
| 4 | 0.451 (126 of 1870 days never flag) | 162 | 0.500 | 0.426 | 0.0639 | +0.0069 [-0.0003, +0.0144] | -0.0016 [-0.0090, +0.0063] | 0.797 | 0.446 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 144 | 0.464 | 0.444 | 0.0691 | +0.0018 [-0.0071, +0.0103] | -0.0057 [-0.0147, +0.0031] | 0.798 | 0.418 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.643 (climatology 0.512, difference +0.1308 [-0.0403, +0.3013]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0119, +0.0573], realised minus predicted -0.0686 [-0.0998, -0.0357]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.435 | 0.3059 | 0.2720 | +0.0161 [-0.0203, +0.0557] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2388 | 0.0159 | -0.0251 [-0.0392, -0.0111] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0384 | 0.0000 | +0.0102 [+0.0087, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0205 | 0.0200 | +0.0003 [-0.0060, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0807 | 0.1165 | +0.0323 [+0.0053, +0.0657] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0252 | 0.0048 | +0.0074 [+0.0054, +0.0092] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1577 | 0.0000 | -0.0082 [-0.0189, +0.0016] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1329 | 0.2439 | -0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.452 | 0.3087 | 0.2615 | +0.0225 [-0.0092, +0.0577] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1552 | 0.1133 | +0.0155 [-0.0251, +0.0532] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.391 | 0.1102 | 0.0630 | +0.0039 [-0.0036, +0.0122] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0039, +0.1379] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0111, +0.0986] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.793] | 0.269 | 5.65 flat / 2.77 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.389, 0.765] | 0.269 | 5.12 flat / 2.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.645] | 4.231 [2.521, 6.612] | 1.971 [1.107, 3.211] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 3.654 [2.071, 5.895] | 1.654 [0.913, 2.739] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.364, 0.714] | 4.000 [2.289, 6.334] | 1.837 [1.053, 3.014] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.257, 0.600] | 4.115 [2.310, 6.700] | 2.183 [1.193, 3.649] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.385 [1.785, 5.576] | 1.615 [0.840, 2.751] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.615, 10.385] | 2.618 [1.432, 4.590] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.471 (126 of 1873 days never flag) | 189 | 0.564 | 0.418 | 0.0599 | +0.0115 [+0.0039, +0.0198] | -0.0036 [-0.0098, +0.0029] | 0.829 | 0.501 | yes |
| 2 | 0.49 (126 of 1872 days never flag) | 169 | 0.532 | 0.438 | 0.0634 | +0.0077 [+0.0003, +0.0152] | -0.0023 [-0.0095, +0.0055] | 0.813 | 0.478 | yes |
| 3 | 0.466 (126 of 1871 days never flag) | 184 | 0.580 | 0.435 | 0.0661 | +0.0046 [-0.0026, +0.0119] | -0.0018 [-0.0093, +0.0063] | 0.777 | 0.520 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 178 | 0.514 | 0.399 | 0.0646 | +0.0062 [-0.0014, +0.0139] | -0.0022 [-0.0102, +0.0058] | 0.797 | 0.453 | yes |
| 5 | 0.527 (126 of 1869 days never flag) | 155 | 0.486 | 0.432 | 0.0683 | +0.0026 [-0.0053, +0.0109] | -0.0049 [-0.0133, +0.0038] | 0.781 | 0.435 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.684 (climatology 0.512, difference +0.1715 [+0.0411, +0.3196]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0922, ΔBrier vs climatology +0.0373 [+0.0163, +0.0596], realised minus predicted -0.0634 [-0.0956, -0.0313]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.2910 | 0.2720 | +0.0272 [-0.0041, +0.0590] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2310 | 0.0159 | -0.0180 [-0.0321, -0.0043] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0118] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0201 | 0.0200 | +0.0007 [-0.0054, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0801 | 0.1165 | +0.0324 [+0.0055, +0.0642] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0251 | 0.0048 | +0.0074 [+0.0056, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1510 | 0.0000 | -0.0028 [-0.0102, +0.0040] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1246 | 0.2439 | 0.0060 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.428 | 0.2976 | 0.2615 | +0.0302 [-0.0001, +0.0615] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1372 | 0.1133 | +0.0296 [-0.0031, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.359 | 0.1077 | 0.0630 | +0.0055 [-0.0015, +0.0138] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0252, +0.1564] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.2028 | 0.1461 | +0.0603 [+0.0173, +0.1059] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.677] | 0.308 | 6.46 flat / 3.10 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.269 | 5.31 flat / 2.54 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 4.769 [3.000, 7.368] | 2.144 [1.239, 3.500] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.550] | 4.500 [2.815, 6.957] | 1.808 [1.076, 2.892] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 4.654 [2.792, 7.334] | 2.154 [1.163, 3.631] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.583] | 4.346 [2.600, 6.801] | 2.125 [1.164, 3.561] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.636] | 4.923 [3.031, 7.667] | 2.356 [1.338, 3.903] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.353 [4.667, 11.500] | 3.029 [1.764, 5.017] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.778 [2.417, 11.000] | 3.222 [1.484, 8.056] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 213 | 0.636 | 0.418 | 0.0633 | +0.0081 [-0.0028, +0.0182] | -0.0070 [-0.0167, +0.0018] | 0.904 | 0.564 | yes |
| 2 | 0.5 (126 of 1872 days never flag) | 204 | 0.626 | 0.426 | 0.0664 | +0.0046 [-0.0049, +0.0141] | -0.0054 [-0.0140, +0.0030] | 0.881 | 0.558 | yes |
| 3 | 0.567 (126 of 1871 days never flag) | 198 | 0.558 | 0.389 | 0.0673 | +0.0034 [-0.0073, +0.0130] | -0.0029 [-0.0141, +0.0062] | 0.897 | 0.488 | no |
| 4 | 0.549 (126 of 1870 days never flag) | 181 | 0.493 | 0.376 | 0.0653 | +0.0055 [-0.0032, +0.0136] | -0.0029 [-0.0117, +0.0051] | 0.860 | 0.428 | no |
| 5 | 0.597 (126 of 1869 days never flag) | 209 | 0.587 | 0.388 | 0.0697 | +0.0013 [-0.0087, +0.0100] | -0.0063 [-0.0159, +0.0022] | 0.846 | 0.513 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.424 | 0.3357 | 0.2720 | -0.0061 [-0.0513, +0.0369] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1225 | 0.0159 | -0.0057 [-0.0299, +0.0142] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0014 [-0.0045, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0910 | 0.1165 | +0.0335 [+0.0066, +0.0689] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0314 | 0.0000 | +0.0173 [+0.0083, +0.0248] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1042 | 0.2439 | 0.0021 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.431 | 0.3425 | 0.2615 | +0.0011 [-0.0391, +0.0416] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1509 | 0.1133 | +0.0170 [-0.0236, +0.0575] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.369 | 0.0830 | 0.0630 | +0.0036 [-0.0067, +0.0134] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1339] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0085, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2810 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.704] | 0.297 | 6.27 flat / 2.98 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.276, 0.652] | 0.269 | 4.62 flat / 2.12 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.281, 0.630] | 4.385 [2.580, 6.731] | 2.010 [1.088, 3.222] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.885 [2.920, 7.501] | 2.183 [1.196, 3.547] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.572] | 3.923 [2.193, 6.214] | 1.721 [0.914, 2.781] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.586] | 4.269 [2.466, 6.514] | 1.923 [1.068, 3.055] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 3.423 [1.786, 5.501] | 1.654 [0.830, 2.750] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.235 [4.688, 11.167] | 3.029 [1.768, 4.951] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.444 [2.214, 9.603] | 2.889 [1.312, 6.786] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.471 (126 of 1873 days never flag) | 194 | 0.571 | 0.412 | 0.0605 | +0.0109 [+0.0012, +0.0208] | -0.0041 [-0.0126, +0.0040] | 0.904 | 0.506 | yes |
| 2 | 0.551 (126 of 1872 days never flag) | 212 | 0.612 | 0.401 | 0.0648 | +0.0063 [-0.0036, +0.0153] | -0.0037 [-0.0132, +0.0049] | 0.888 | 0.538 | yes |
| 3 | 0.537 (126 of 1871 days never flag) | 178 | 0.551 | 0.427 | 0.0667 | +0.0040 [-0.0082, +0.0143] | -0.0023 [-0.0141, +0.0076] | 0.894 | 0.492 | no |
| 4 | 0.553 (126 of 1870 days never flag) | 183 | 0.522 | 0.393 | 0.0658 | +0.0050 [-0.0032, +0.0129] | -0.0034 [-0.0115, +0.0045] | 0.881 | 0.458 | no |
| 5 | 0.5 (126 of 1869 days never flag) | 151 | 0.449 | 0.411 | 0.0686 | +0.0023 [-0.0058, +0.0103] | -0.0052 [-0.0131, +0.0029] | 0.843 | 0.398 | no |

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
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.3215 | 0.2720 | +0.0032 [-0.0371, +0.0429] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1153 | 0.0159 | +0.0010 [-0.0252, +0.0228] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0120 | 0.0200 | +0.0018 [-0.0039, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0905 | 0.1165 | +0.0338 [+0.0072, +0.0668] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0063 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0247 | 0.0000 | +0.0226 [+0.0162, +0.0282] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.0959 | 0.2439 | 0.0179 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.419 | 0.3322 | 0.2615 | +0.0073 [-0.0289, +0.0459] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1331 | 0.1133 | +0.0314 [+0.0002, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.353 | 0.0809 | 0.0630 | +0.0047 [-0.0051, +0.0140] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0272, +0.1583] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.2028 | 0.1461 | +0.0603 [+0.0190, +0.1068] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.417, 0.792] | 0.269 | 5.62 flat / 2.62 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.391, 0.760] | 0.242 | 4.35 flat / 2.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.312, 0.680] | 4.769 [2.892, 7.264] | 2.144 [1.191, 3.501] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.320, 0.679] | 4.385 [2.562, 6.897] | 2.135 [1.175, 3.544] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.606] | 3.808 [2.000, 6.218] | 1.904 [0.921, 3.265] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.285, 0.630] | 3.500 [2.000, 5.581] | 1.625 [0.891, 2.713] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 3.115 [1.607, 5.112] | 1.375 [0.660, 2.375] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 0.960] | 6.412 [3.818, 10.401] | 2.662 [1.427, 4.594] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.111 (no interval) | 2.528 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 213 | 0.636 | 0.418 | 0.0633 | +0.0081 [-0.0025, +0.0186] | -0.0070 [-0.0160, +0.0019] | 0.904 | 0.564 | yes |
| 2 | 0.613 (126 of 1872 days never flag) | 192 | 0.561 | 0.406 | 0.0613 | +0.0098 [-0.0000, +0.0195] | -0.0002 [-0.0102, +0.0093] | 0.892 | 0.495 | yes |
| 3 | 0.667 (126 of 1871 days never flag) | 167 | 0.493 | 0.407 | 0.0647 | +0.0060 [-0.0053, +0.0160] | -0.0003 [-0.0114, +0.0096] | 0.891 | 0.436 | yes |
| 4 | 0.497 (126 of 1870 days never flag) | 161 | 0.507 | 0.435 | 0.0613 | +0.0095 [+0.0004, +0.0179] | +0.0011 [-0.0082, +0.0098] | 0.867 | 0.455 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 150 | 0.500 | 0.460 | 0.0699 | +0.0010 [-0.0103, +0.0114] | -0.0065 [-0.0176, +0.0034] | 0.862 | 0.453 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.424 | 0.3357 | 0.2720 | -0.0061 [-0.0496, +0.0402] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1225 | 0.0159 | -0.0057 [-0.0294, +0.0155] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0014 [-0.0046, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0910 | 0.1165 | +0.0335 [+0.0058, +0.0684] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0314 | 0.0000 | +0.0173 [+0.0088, +0.0251] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1042 | 0.2439 | 0.0021 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.431 | 0.3425 | 0.2615 | +0.0011 [-0.0395, +0.0421] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1509 | 0.1133 | +0.0170 [-0.0234, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.369 | 0.0830 | 0.0630 | +0.0036 [-0.0067, +0.0135] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1381] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0086, +0.0978] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2810 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.269 | 5.73 flat / 2.67 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.391, 0.767] | 0.269 | 4.96 flat / 2.40 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.385 [2.636, 6.751] | 2.010 [1.133, 3.185] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 3.769 [2.120, 5.917] | 1.683 [0.902, 2.731] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.312, 0.692] | 4.115 [2.363, 6.465] | 1.856 [1.027, 2.982] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 3.731 [1.967, 6.091] | 1.827 [0.886, 3.102] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 3.385 [1.815, 5.526] | 1.606 [0.808, 2.712] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.529 [3.833, 10.308] | 2.706 [1.500, 4.451] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.471 (126 of 1873 days never flag) | 194 | 0.571 | 0.412 | 0.0605 | +0.0109 [+0.0007, +0.0206] | -0.0041 [-0.0132, +0.0037] | 0.904 | 0.506 | yes |
| 2 | 0.571 (126 of 1872 days never flag) | 176 | 0.561 | 0.443 | 0.0616 | +0.0095 [-0.0004, +0.0187] | -0.0005 [-0.0099, +0.0088] | 0.891 | 0.505 | yes |
| 3 | 0.604 (126 of 1871 days never flag) | 188 | 0.587 | 0.431 | 0.0638 | +0.0068 [-0.0044, +0.0176] | +0.0005 [-0.0104, +0.0109] | 0.899 | 0.525 | no |
| 4 | 0.659 (126 of 1870 days never flag) | 164 | 0.486 | 0.409 | 0.0595 | +0.0114 [+0.0032, +0.0199] | +0.0029 [-0.0055, +0.0117] | 0.891 | 0.430 | yes |
| 5 | 0.5 (126 of 1869 days never flag) | 157 | 0.500 | 0.439 | 0.0634 | +0.0075 [-0.0007, +0.0156] | -0.0000 [-0.0082, +0.0084] | 0.851 | 0.449 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.3215 | 0.2720 | +0.0032 [-0.0382, +0.0447] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1153 | 0.0159 | +0.0010 [-0.0244, +0.0221] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0120 | 0.0200 | +0.0018 [-0.0041, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0905 | 0.1165 | +0.0338 [+0.0065, +0.0691] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0063 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0247 | 0.0000 | +0.0226 [+0.0164, +0.0284] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.0959 | 0.2439 | 0.0179 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.419 | 0.3322 | 0.2615 | +0.0073 [-0.0321, +0.0462] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1331 | 0.1133 | +0.0314 [-0.0009, +0.0656] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.353 | 0.0809 | 0.0630 | +0.0047 [-0.0056, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0249, +0.1560] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.2028 | 0.1461 | +0.0603 [+0.0188, +0.1050] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.720] | 0.301 | 6.35 flat / 3.29 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.316, 0.682] | 0.269 | 5.42 flat / 2.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.688] | 4.115 [2.423, 6.410] | 1.827 [1.016, 2.963] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.308 [2.556, 6.704] | 1.760 [1.000, 2.859] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.769 [2.724, 7.667] | 2.288 [1.198, 3.902] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.462 [2.499, 7.351] | 2.356 [1.162, 4.120] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.846 [2.799, 7.700] | 2.317 [1.217, 3.977] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.353 [4.619, 11.917] | 3.029 [1.711, 5.271] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 3.778 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 195 | 0.629 | 0.451 | 0.0569 | +0.0145 [+0.0061, +0.0235] | -0.0006 [-0.0078, +0.0066] | 0.880 | 0.567 | yes |
| 2 | 0.409 (126 of 1872 days never flag) | 197 | 0.612 | 0.431 | 0.0614 | +0.0096 [+0.0025, +0.0171] | -0.0004 [-0.0066, +0.0058] | 0.861 | 0.547 | yes |
| 3 | 0.403 (126 of 1871 days never flag) | 203 | 0.572 | 0.389 | 0.0613 | +0.0094 [+0.0031, +0.0157] | +0.0031 [-0.0032, +0.0094] | 0.872 | 0.501 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 184 | 0.493 | 0.370 | 0.0615 | +0.0094 [+0.0027, +0.0163] | +0.0009 [-0.0057, +0.0076] | 0.844 | 0.426 | no |
| 5 | 0.426 (126 of 1869 days never flag) | 205 | 0.572 | 0.385 | 0.0661 | +0.0048 [-0.0020, +0.0115] | -0.0027 [-0.0095, +0.0043] | 0.818 | 0.500 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.626 (climatology 0.512, difference +0.1136 [+0.0104, +0.2100]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0919, ΔBrier vs climatology +0.0375 [+0.0206, +0.0557], realised minus predicted -0.0125 [-0.0435, +0.0201]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.452 | 0.2966 | 0.2720 | +0.0226 [-0.0131, +0.0612] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1611 | 0.0159 | -0.0022 [-0.0195, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0014 [-0.0047, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.846 | 0.0886 | 0.1165 | +0.0358 [+0.0065, +0.0715] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0085 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0786 | 0.0000 | +0.0139 [+0.0054, +0.0215] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1326 | 0.2439 | 0.0007 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.688 | 0.467 | 0.3045 | 0.2615 | +0.0287 [-0.0039, +0.0622] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1523 | 0.1133 | +0.0176 [-0.0254, +0.0569] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.407 | 0.0829 | 0.0630 | +0.0110 [+0.0038, +0.0191] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0026, +0.1398] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0087, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2719 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.363 | 6.77 flat / 3.79 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.647] | 0.269 | 5.77 flat / 3.28 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.192 [2.516, 6.526] | 2.019 [1.150, 3.293] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 5.038 [3.083, 7.619] | 2.394 [1.392, 3.824] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.000 [2.290, 6.407] | 1.817 [1.023, 2.964] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.579] | 5.000 [3.031, 7.864] | 2.750 [1.534, 4.700] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 4.000 [2.214, 6.410] | 2.096 [1.073, 3.588] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 7.235 [4.609, 11.364] | 3.029 [1.812, 4.929] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 5.889 [2.554, 16.000] | 5.222 [1.982, 14.875] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (126 of 1873 days never flag) | 186 | 0.550 | 0.414 | 0.0539 | +0.0175 [+0.0093, +0.0261] | +0.0024 [-0.0035, +0.0085] | 0.875 | 0.487 | yes |
| 2 | 0.414 (126 of 1872 days never flag) | 216 | 0.612 | 0.394 | 0.0598 | +0.0113 [+0.0041, +0.0179] | +0.0013 [-0.0054, +0.0078] | 0.866 | 0.536 | yes |
| 3 | 0.41 (126 of 1871 days never flag) | 181 | 0.558 | 0.425 | 0.0609 | +0.0098 [+0.0032, +0.0169] | +0.0035 [-0.0032, +0.0104] | 0.864 | 0.498 | no |
| 4 | 0.459 (126 of 1870 days never flag) | 201 | 0.514 | 0.353 | 0.0631 | +0.0077 [+0.0011, +0.0144] | -0.0007 [-0.0077, +0.0062] | 0.846 | 0.439 | no |
| 5 | 0.489 (126 of 1869 days never flag) | 166 | 0.449 | 0.373 | 0.0686 | +0.0023 [-0.0057, +0.0099] | -0.0053 [-0.0134, +0.0024] | 0.823 | 0.389 | no |

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
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.2836 | 0.2720 | +0.0326 [+0.0009, +0.0651] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.1543 | 0.0159 | +0.0047 [-0.0129, +0.0210] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0102 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0875 | 0.1165 | +0.0360 [+0.0065, +0.0723] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0084 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0736 | 0.0000 | +0.0190 [+0.0122, +0.0247] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1203 | 0.2439 | 0.0170 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.426 | 0.2945 | 0.2615 | +0.0355 [+0.0053, +0.0687] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1343 | 0.1133 | +0.0317 [-0.0013, +0.0663] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.355 | 0.0811 | 0.0630 | +0.0123 [+0.0050, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0243, +0.1554] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.500 | 0.2028 | 0.1461 | +0.0603 [+0.0193, +0.1048] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2717 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.417, 0.792] | 0.269 | 5.50 flat / 2.83 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.391, 0.769] | 0.262 | 4.54 flat / 2.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.682] | 4.115 [2.470, 6.334] | 1.827 [1.030, 2.974] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 4.154 [2.333, 6.558] | 2.067 [1.134, 3.412] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 3.962 [2.190, 6.350] | 2.029 [1.067, 3.469] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.630] | 3.692 [2.081, 5.895] | 1.933 [1.062, 3.250] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.115 [1.512, 5.133] | 1.375 [0.661, 2.355] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.412 [3.772, 10.429] | 2.662 [1.458, 4.688] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.778 [1.599, 9.333] | 3.139 [1.091, 8.418] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 195 | 0.629 | 0.451 | 0.0569 | +0.0145 [+0.0061, +0.0237] | -0.0006 [-0.0071, +0.0064] | 0.880 | 0.567 | yes |
| 2 | 0.477 (126 of 1872 days never flag) | 184 | 0.547 | 0.413 | 0.0555 | +0.0155 [+0.0074, +0.0233] | +0.0055 [-0.0024, +0.0132] | 0.871 | 0.484 | yes |
| 3 | 0.394 (126 of 1871 days never flag) | 175 | 0.522 | 0.411 | 0.0582 | +0.0125 [+0.0046, +0.0201] | +0.0062 [-0.0020, +0.0142] | 0.859 | 0.462 | yes |
| 4 | 0.451 (126 of 1870 days never flag) | 165 | 0.500 | 0.418 | 0.0571 | +0.0137 [+0.0067, +0.0212] | +0.0053 [-0.0020, +0.0129] | 0.848 | 0.445 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 149 | 0.493 | 0.456 | 0.0659 | +0.0050 [-0.0037, +0.0140] | -0.0026 [-0.0121, +0.0065] | 0.837 | 0.446 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.643 (climatology 0.512, difference +0.1308 [-0.0350, +0.3052]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0900, ΔBrier vs climatology +0.0395 [+0.0174, +0.0626], realised minus predicted -0.0379 [-0.0693, -0.0071]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.452 | 0.2966 | 0.2720 | +0.0226 [-0.0129, +0.0600] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1611 | 0.0159 | -0.0022 [-0.0189, +0.0130] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0014 [-0.0044, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.846 | 0.0886 | 0.1165 | +0.0358 [+0.0072, +0.0730] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0085 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0786 | 0.0000 | +0.0139 [+0.0052, +0.0216] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1326 | 0.2439 | 0.0007 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.688 | 0.467 | 0.3045 | 0.2615 | +0.0287 [-0.0026, +0.0631] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1523 | 0.1133 | +0.0176 [-0.0239, +0.0571] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.407 | 0.0829 | 0.0630 | +0.0110 [+0.0036, +0.0193] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0006, +0.1383] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0119, +0.1001] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2719 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.280 | 5.96 flat / 3.27 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.759] | 0.269 | 5.54 flat / 3.10 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.637] | 4.192 [2.454, 6.709] | 2.019 [1.131, 3.420] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 4.115 [2.333, 6.715] | 2.000 [1.092, 3.421] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.357, 0.714] | 4.231 [2.538, 6.700] | 1.962 [1.160, 3.266] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.346 [2.351, 7.462] | 2.500 [1.223, 4.668] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.257, 0.600] | 3.192 [1.645, 5.385] | 1.500 [0.759, 2.675] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.529 [4.000, 10.771] | 2.706 [1.535, 4.750] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.889 (no interval) | 4.333 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.417 (126 of 1873 days never flag) | 186 | 0.550 | 0.414 | 0.0539 | +0.0175 [+0.0101, +0.0263] | +0.0024 [-0.0035, +0.0087] | 0.875 | 0.487 | yes |
| 2 | 0.49 (126 of 1872 days never flag) | 183 | 0.547 | 0.415 | 0.0558 | +0.0152 [+0.0075, +0.0229] | +0.0052 [-0.0022, +0.0124] | 0.868 | 0.485 | yes |
| 3 | 0.429 (126 of 1871 days never flag) | 195 | 0.616 | 0.436 | 0.0574 | +0.0133 [+0.0057, +0.0208] | +0.0070 [-0.0008, +0.0146] | 0.870 | 0.552 | yes |
| 4 | 0.659 (126 of 1870 days never flag) | 179 | 0.478 | 0.369 | 0.0563 | +0.0145 [+0.0076, +0.0221] | +0.0061 [-0.0016, +0.0139] | 0.859 | 0.413 | yes |
| 5 | 0.527 (126 of 1869 days never flag) | 150 | 0.486 | 0.447 | 0.0632 | +0.0077 [-0.0003, +0.0152] | +0.0002 [-0.0081, +0.0079] | 0.826 | 0.438 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.684 (climatology 0.512, difference +0.1715 [+0.0430, +0.3172]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0858, ΔBrier vs climatology +0.0437 [+0.0237, +0.0650], realised minus predicted -0.0298 [-0.0582, +0.0010]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.418 | 0.2836 | 0.2720 | +0.0326 [+0.0023, +0.0655] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.1543 | 0.0159 | +0.0047 [-0.0130, +0.0195] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0102 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0875 | 0.1165 | +0.0360 [+0.0071, +0.0710] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0084 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0736 | 0.0000 | +0.0190 [+0.0131, +0.0246] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1203 | 0.2439 | 0.0170 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.426 | 0.2945 | 0.2615 | +0.0355 [+0.0071, +0.0671] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1343 | 0.1133 | +0.0317 [-0.0015, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.355 | 0.0811 | 0.0630 | +0.0123 [+0.0052, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3025 | 0.2903 | +0.0954 [+0.0260, +0.1590] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.500 | 0.2028 | 0.1461 | +0.0603 [+0.0197, +0.1058] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2717 | 0.2213 |

