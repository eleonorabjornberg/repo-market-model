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

- h = 1: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.457 (climatology 0.457, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1757, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0470 [-0.1017, +0.0117]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.386 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0645 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0907 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1572 | 0.0031 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0728 | 0.4146 | 0.0000 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.372 | 0.1413 | 0.2474 | +0.0000 [+0.0000, +0.0000] |
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

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.477 (climatology 0.457, difference +0.0203 [-0.0817, +0.1399]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0510, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.824 | 0.377 | 0.1679 | 0.2720 | +0.0168 [-0.0027, +0.0376] |
| regime | 2020 | 251 | 4 | 0.250 | 0.042 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.486 | 0.0978 | 0.1165 | +0.0256 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0233 | 0.0048 | +0.0080 [+0.0059, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0891 | 0.0031 | +0.0206 [+0.0144, +0.0267] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.562 | 0.2311 | 0.4146 | 0.0897 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.795 | 0.359 | 0.1759 | 0.2474 | +0.0203 [+0.0030, +0.0386] |
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
| regime | 2018-19 | 375 | 102 | 0.608 | 0.437 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0503 | 0.0159 | +0.0329 [+0.0235, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.917 | 0.0443 | 0.1165 | +0.0287 [+0.0113, +0.0503] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.333 | 0.0268 | 0.0031 | +0.0285 [+0.0229, +0.0343] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | 0.0409 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.598 | 0.455 | 0.2024 | 0.2474 | +0.0558 [+0.0323, +0.0805] |
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
| 1 | 0.0833 (105 of 1873 days never flag) | 78 | 0.300 | 0.538 | 0.0577 | +0.0137 [+0.0082, +0.0193] | -0.0014 [-0.0097, +0.0063] | 0.642 | 0.279 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 55 | 0.180 | 0.455 | 0.0687 | +0.0024 [-0.0040, +0.0080] | -0.0076 [-0.0161, -0.0005] | 0.578 | 0.163 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0667 | +0.0040 [-0.0025, +0.0098] | -0.0023 [-0.0102, +0.0044] | 0.579 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 49 | 0.181 | 0.510 | 0.0668 | +0.0040 [-0.0028, +0.0099] | -0.0045 [-0.0121, +0.0023] | 0.579 | 0.167 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0053, +0.0074] | -0.0062 [-0.0136, +0.0007] | 0.577 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

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
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.167 | 0.0022 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0035 | 0.0031 | +0.0296 [+0.0218, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0274 | 0.4146 | -0.0074 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0971 | 0.2474 | +0.0155 [-0.0047, +0.0366] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0985 | 0.1133 | +0.0543 [+0.0303, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2204 | 0.2903 | +0.1155 [+0.0314, +0.2020] |
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
| lead_at_least_1 | 26 | 17 | 0.654 [0.474, 0.812] | 0.411 | 7.88 flat / 3.79 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.645] | 0.280 | 6.00 flat / 2.81 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.760] | 5.115 [3.425, 7.474] | 2.183 [1.371, 3.329] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 5.000 [3.235, 7.369] | 2.067 [1.264, 3.197] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.769 [2.960, 7.251] | 2.058 [1.195, 3.298] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.115 [2.519, 6.334] | 1.702 [0.950, 2.763] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.231 [2.586, 6.471] | 1.942 [1.136, 3.100] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.826, 11.455] | 3.147 [1.920, 5.200] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.166, 0.714] | 8.778 [5.769, 16.603] | 5.000 [3.050, 10.314] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 227 | 0.671 | 0.414 | 0.0478 | +0.0236 [+0.0164, +0.0318] | +0.0085 [+0.0037, +0.0138] | 0.892 | 0.595 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 223 | 0.669 | 0.417 | 0.0601 | +0.0109 [+0.0065, +0.0151] | +0.0009 [-0.0021, +0.0040] | 0.837 | 0.594 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 203 | 0.572 | 0.389 | 0.0605 | +0.0101 [+0.0065, +0.0142] | +0.0038 [+0.0011, +0.0070] | 0.810 | 0.501 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 180 | 0.529 | 0.406 | 0.0594 | +0.0114 [+0.0070, +0.0161] | +0.0030 [+0.0004, +0.0058] | 0.822 | 0.467 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 179 | 0.500 | 0.385 | 0.0629 | +0.0080 [+0.0036, +0.0123] | +0.0004 [-0.0025, +0.0033] | 0.790 | 0.436 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.465 (climatology 0.457, difference +0.0078 [-0.1078, +0.1043]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0843, ΔBrier vs climatology +0.0452 [+0.0316, +0.0605], realised minus predicted +0.0117 [-0.0185, +0.0443]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2373 | 0.2720 | +0.0573 [+0.0304, +0.0862] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1174 | 0.0159 | +0.0233 [+0.0097, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0192 | 0.0000 | +0.0131 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0328 | 0.0200 | +0.0006 [-0.0060, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.500 | 0.1149 | 0.1165 | +0.0275 [+0.0002, +0.0591] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0230 | 0.0048 | +0.0075 [+0.0051, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0681 | 0.0031 | +0.0221 [+0.0146, +0.0292] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.2116 | 0.4146 | 0.0619 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.411 | 0.2433 | 0.2474 | +0.0564 [+0.0318, +0.0827] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1078 | 0.1133 | +0.0595 [+0.0357, +0.0870] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.370 | 0.0861 | 0.0630 | +0.0160 [+0.0093, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2204 | 0.2903 | +0.1155 [+0.0378, +0.1950] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.0958 | 0.1461 | +0.0686 [+0.0421, +0.0963] |

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
| 1 | 0.121 (105 of 1873 days never flag) | 174 | 0.579 | 0.466 | 0.0497 | +0.0218 [+0.0145, +0.0293] | +0.0067 [+0.0016, +0.0119] | 0.804 | 0.525 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 174 | 0.518 | 0.414 | 0.0624 | +0.0087 [+0.0038, +0.0133] | -0.0013 [-0.0055, +0.0024] | 0.749 | 0.459 | no |
| 3 | 0.128 (147 of 1871 days never flag) | 156 | 0.471 | 0.417 | 0.0606 | +0.0101 [+0.0050, +0.0146] | +0.0038 [-0.0008, +0.0076] | 0.747 | 0.419 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 164 | 0.500 | 0.421 | 0.0603 | +0.0106 [+0.0055, +0.0156] | +0.0021 [-0.0014, +0.0056] | 0.760 | 0.445 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 166 | 0.507 | 0.422 | 0.0636 | +0.0073 [+0.0018, +0.0125] | -0.0002 [-0.0042, +0.0037] | 0.742 | 0.452 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.4 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 3.4 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.487 (climatology 0.457, difference +0.0300 [-0.0960, +0.1429]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0862, ΔBrier vs climatology +0.0433 [+0.0303, +0.0579], realised minus predicted +0.0618 [+0.0331, +0.0951]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.527 | 0.1676 | 0.2720 | +0.0417 [+0.0143, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0224 | 0.0159 | +0.0323 [+0.0157, +0.0454] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.125 | 0.0152 | 0.0200 | +0.0007 [-0.0068, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.724 | 0.467 | 0.0899 | 0.1165 | +0.0266 [+0.0009, +0.0587] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.071 | 0.0090 | 0.0048 | +0.0078 [+0.0053, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0085 | 0.0031 | +0.0282 [+0.0200, +0.0355] |
| scarcity_state | 2 | 41 | 17 | 0.647 | 0.579 | 0.1827 | 0.4146 | 0.0599 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.590 | 0.504 | 0.1657 | 0.2474 | +0.0446 [+0.0203, +0.0703] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1023 | 0.1133 | +0.0600 [+0.0346, +0.0873] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.424 | 0.0419 | 0.0630 | +0.0138 [+0.0076, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0326, +0.1953] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.0958 | 0.1461 | +0.0686 [+0.0419, +0.0958] |

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

- h = 1: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.457, difference +0.2581 [+0.0710, +0.4127]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0726, ΔBrier vs climatology +0.0569 [+0.0394, +0.0760], realised minus predicted +0.0315 [+0.0067, +0.0570]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.527 | 0.1692 | 0.2720 | +0.0420 [+0.0131, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0244 | 0.0159 | +0.0309 [+0.0152, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0042 | 0.0000 | +0.0136 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0129 | 0.0200 | -0.0015 [-0.0087, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.724 | 0.467 | 0.0907 | 0.1165 | +0.0286 [+0.0022, +0.0591] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0079 | 0.0048 | +0.0074 [+0.0050, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0096 | 0.0031 | +0.0277 [+0.0187, +0.0358] |
| scarcity_state | 2 | 41 | 17 | 0.647 | 0.550 | 0.2003 | 0.4146 | +0.0733 [-0.0010, +0.1500] |
| scarcity_state | 3 | 473 | 117 | 0.590 | 0.507 | 0.1671 | 0.2474 | +0.0438 [+0.0178, +0.0695] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1010 | 0.1133 | +0.0595 [+0.0350, +0.0859] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.424 | 0.0425 | 0.0630 | +0.0134 [+0.0067, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0406, +0.2112] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.0989 | 0.1461 | +0.0689 [+0.0406, +0.0981] |

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
| lead_at_least_3 | 26 | 15 | 0.577 [0.385, 0.762] | 0.269 | 5.38 flat / 2.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.367, 0.704] | 3.692 [2.658, 5.143] | 1.635 [1.132, 2.431] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.652] | 3.269 [2.130, 4.741] | 1.394 [0.938, 2.060] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 3.423 [2.174, 5.100] | 1.442 [0.929, 2.209] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.265, 0.667] | 3.462 [2.216, 5.111] | 1.500 [1.000, 2.234] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.762] | 3.500 [2.219, 5.200] | 1.644 [1.087, 2.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.967] | 5.412 [3.360, 8.309] | 2.015 [1.250, 3.143] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 10.222 (no interval) | 6.194 (no interval) |

Recall with equal weight per regime: 0.641 (2018-19 13/17, 2020 2/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 178 | 0.586 | 0.461 | 0.0497 | +0.0217 [+0.0145, +0.0298] | +0.0066 [+0.0013, +0.0125] | 0.805 | 0.530 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 163 | 0.561 | 0.479 | 0.0544 | +0.0166 [+0.0116, +0.0220] | +0.0066 [+0.0018, +0.0120] | 0.800 | 0.512 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 163 | 0.536 | 0.454 | 0.0570 | +0.0137 [+0.0085, +0.0190] | +0.0074 [+0.0028, +0.0122] | 0.776 | 0.485 | no |
| 4 | 0.194 (147 of 1870 days never flag) | 165 | 0.543 | 0.455 | 0.0532 | +0.0176 [+0.0122, +0.0232] | +0.0092 [+0.0049, +0.0139] | 0.807 | 0.492 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 165 | 0.536 | 0.448 | 0.0539 | +0.0170 [+0.0117, +0.0225] | +0.0095 [+0.0050, +0.0139] | 0.804 | 0.484 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.457, difference +0.2581 [+0.0630, +0.4287]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0718, ΔBrier vs climatology +0.0577 [+0.0397, +0.0765], realised minus predicted +0.0295 [+0.0055, +0.0555]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.531 | 0.1724 | 0.2720 | +0.0442 [+0.0158, +0.0733] |
| regime | 2020 | 251 | 4 | 0.500 | 0.182 | 0.0283 | 0.0159 | +0.0350 [+0.0212, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0179 | 0.0200 | -0.0058 [-0.0174, +0.0034] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.444 | 0.0904 | 0.1165 | +0.0264 [+0.0024, +0.0563] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0088 | 0.0048 | +0.0064 [+0.0030, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0095 | 0.0031 | +0.0275 [+0.0183, +0.0351] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.526 | 0.1962 | 0.4146 | 0.0665 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.514 | 0.1722 | 0.2474 | +0.0473 [+0.0228, +0.0731] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1010 | 0.1133 | +0.0595 [+0.0347, +0.0862] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.420 | 0.0445 | 0.0630 | +0.0136 [+0.0073, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0432, +0.2095] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.0989 | 0.1461 | +0.0689 [+0.0395, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3803 | 0.2213 |

## risk_gbm+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.308 | 6.46 flat / 3.09 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.618] | 0.269 | 5.69 flat / 2.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.387, 0.762] | 4.115 [2.533, 6.458] | 1.692 [0.962, 2.750] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.462 [2.743, 6.938] | 1.865 [1.091, 3.031] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 5.038 [3.028, 7.834] | 2.231 [1.250, 3.672] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.231 [2.484, 6.640] | 1.654 [0.898, 2.734] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 3.769 [2.178, 6.062] | 1.663 [0.913, 2.778] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.176 [4.470, 11.500] | 3.088 [1.783, 5.222] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.111 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 198 | 0.650 | 0.460 | 0.0484 | +0.0230 [+0.0162, +0.0305] | +0.0080 [+0.0031, +0.0132] | 0.880 | 0.588 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 203 | 0.626 | 0.429 | 0.0594 | +0.0117 [+0.0082, +0.0151] | +0.0017 [-0.0019, +0.0051] | 0.821 | 0.559 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 212 | 0.587 | 0.382 | 0.0592 | +0.0115 [+0.0082, +0.0152] | +0.0052 [+0.0015, +0.0089] | 0.800 | 0.511 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 183 | 0.529 | 0.399 | 0.0580 | +0.0129 [+0.0093, +0.0164] | +0.0044 [+0.0018, +0.0072] | 0.813 | 0.465 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 161 | 0.457 | 0.391 | 0.0613 | +0.0097 [+0.0062, +0.0132] | +0.0021 [-0.0008, +0.0051] | 0.781 | 0.400 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.442 | 0.2177 | 0.2720 | +0.0498 [+0.0240, +0.0771] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.1033 | 0.0159 | +0.0291 [+0.0201, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0240 | 0.0200 | +0.0027 [-0.0017, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.583 | 0.0982 | 0.1165 | +0.0264 [+0.0028, +0.0561] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0183 | 0.0048 | +0.0082 [+0.0062, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0569 | 0.0031 | +0.0245 [+0.0174, +0.0309] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.750 | 0.1680 | 0.4146 | 0.0483 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.450 | 0.2235 | 0.2474 | +0.0524 [+0.0297, +0.0773] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1064 | 0.1133 | +0.0586 [+0.0341, +0.0839] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.415 | 0.0740 | 0.0630 | +0.0154 [+0.0093, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0375, +0.1956] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.0958 | 0.1461 | +0.0686 [+0.0421, +0.0963] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.4541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2486 | 0.2213 |

## risk_gbm+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.483, 0.818] | 0.392 | 7.58 flat / 3.60 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.278, 0.643] | 0.269 | 5.69 flat / 2.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.389, 0.760] | 5.077 [3.428, 7.479] | 2.173 [1.354, 3.397] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 4.923 [3.148, 7.365] | 2.038 [1.231, 3.219] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.615 [2.829, 7.044] | 1.981 [1.153, 3.175] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.962 [2.407, 6.211] | 1.615 [0.902, 2.667] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.115 [2.538, 6.500] | 1.865 [1.104, 3.036] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.786, 11.445] | 3.147 [1.880, 5.250] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.889 (no interval) | 4.444 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 226 | 0.671 | 0.416 | 0.0472 | +0.0243 [+0.0170, +0.0321] | +0.0092 [+0.0042, +0.0143] | 0.911 | 0.595 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 221 | 0.669 | 0.421 | 0.0594 | +0.0117 [+0.0071, +0.0160] | +0.0017 [-0.0016, +0.0047] | 0.872 | 0.595 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 199 | 0.572 | 0.397 | 0.0588 | +0.0119 [+0.0083, +0.0155] | +0.0055 [+0.0028, +0.0084] | 0.859 | 0.503 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 176 | 0.529 | 0.415 | 0.0581 | +0.0127 [+0.0085, +0.0172] | +0.0043 [+0.0019, +0.0071] | 0.865 | 0.470 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 176 | 0.500 | 0.392 | 0.0619 | +0.0090 [+0.0046, +0.0133] | +0.0015 [-0.0015, +0.0045] | 0.848 | 0.438 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.465 (climatology 0.457, difference +0.0078 [-0.1074, +0.1053]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0834, ΔBrier vs climatology +0.0461 [+0.0323, +0.0603], realised minus predicted +0.0381 [+0.0083, +0.0711]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2373 | 0.2720 | +0.0573 [+0.0292, +0.0859] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1174 | 0.0159 | +0.0233 [+0.0105, +0.0358] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0050 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0028 | 0.0200 | +0.0037 [-0.0002, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.500 | 0.1013 | 0.1165 | +0.0284 [+0.0006, +0.0621] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0022 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0681 | 0.0031 | +0.0221 [+0.0149, +0.0291] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.2116 | 0.4146 | 0.0619 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.411 | 0.2433 | 0.2474 | +0.0564 [+0.0311, +0.0810] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1058 | 0.1133 | +0.0595 [+0.0355, +0.0867] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.372 | 0.0729 | 0.0630 | +0.0167 [+0.0098, +0.0240] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2204 | 0.2903 | +0.1155 [+0.0353, +0.1964] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.0958 | 0.1461 | +0.0686 [+0.0413, +0.0941] |

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
| 1 | 0.121 (105 of 1873 days never flag) | 209 | 0.664 | 0.445 | 0.0484 | +0.0230 [+0.0175, +0.0290] | +0.0080 [+0.0030, +0.0132] | 0.899 | 0.597 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 201 | 0.633 | 0.438 | 0.0604 | +0.0107 [+0.0074, +0.0138] | +0.0007 [-0.0032, +0.0044] | 0.847 | 0.568 | no |
| 3 | 0.125 (147 of 1871 days never flag) | 201 | 0.572 | 0.393 | 0.0598 | +0.0109 [+0.0076, +0.0146] | +0.0046 [+0.0007, +0.0086] | 0.817 | 0.502 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 186 | 0.522 | 0.387 | 0.0592 | +0.0116 [+0.0079, +0.0154] | +0.0032 [-0.0002, +0.0065] | 0.832 | 0.456 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 183 | 0.500 | 0.377 | 0.0624 | +0.0086 [+0.0049, +0.0120] | +0.0010 [-0.0029, +0.0045] | 0.797 | 0.434 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.456 (climatology 0.457, difference -0.0009 [-0.1197, +0.1142]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0897, ΔBrier vs climatology +0.0398 [+0.0295, +0.0513], realised minus predicted +0.0534 [+0.0201, +0.0884]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.466 | 0.1666 | 0.2720 | +0.0429 [+0.0257, +0.0603] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0661 | 0.0159 | +0.0366 [+0.0281, +0.0449] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0099 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0178 | 0.0200 | +0.0030 [-0.0012, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.516 | 0.0768 | 0.1165 | +0.0281 [+0.0036, +0.0597] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.167 | 0.0126 | 0.0048 | +0.0085 [+0.0065, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0358 | 0.0031 | +0.0277 [+0.0204, +0.0345] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.1195 | 0.4146 | 0.0486 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.452 | 0.1702 | 0.2474 | +0.0496 [+0.0327, +0.0674] |
| day_type | month_end | 150 | 17 | 0.824 | 0.538 | 0.1032 | 0.1133 | +0.0572 [+0.0328, +0.0846] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.405 | 0.0494 | 0.0630 | +0.0155 [+0.0111, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0360, +0.1988] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0958 | 0.1461 | +0.0686 [+0.0415, +0.0975] |

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
| 1 | 0.638 (105 of 1873 days never flag) | 190 | 0.600 | 0.442 | 0.0606 | +0.0108 [+0.0009, +0.0206] | -0.0043 [-0.0126, +0.0039] | 0.871 | 0.539 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 210 | 0.590 | 0.390 | 0.0716 | -0.0006 [-0.0090, +0.0075] | -0.0106 [-0.0183, -0.0034] | 0.816 | 0.516 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 188 | 0.529 | 0.388 | 0.0726 | -0.0019 [-0.0112, +0.0059] | -0.0082 [-0.0171, -0.0007] | 0.795 | 0.463 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 160 | 0.457 | 0.394 | 0.0702 | +0.0006 [-0.0067, +0.0070] | -0.0078 [-0.0144, -0.0020] | 0.815 | 0.401 | no |
| 5 | 0.446 (147 of 1869 days never flag) | 161 | 0.442 | 0.379 | 0.0728 | -0.0019 [-0.0083, +0.0039] | -0.0094 [-0.0153, -0.0041] | 0.776 | 0.384 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.3118 | 0.2720 | +0.0131 [-0.0304, +0.0570] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0240, +0.0127] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0684 | 0.1165 | +0.0268 [+0.0013, +0.0566] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0074 | 0.0048 | +0.0080 [+0.0061, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1089 | 0.0031 | +0.0102 [+0.0039, +0.0164] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1375 | 0.4146 | 0.0461 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.441 | 0.3117 | 0.2474 | +0.0141 [-0.0237, +0.0511] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1092 | 0.1133 | +0.0568 [+0.0315, +0.0835] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1025 | 0.0630 | +0.0012 [-0.0092, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0346, +0.1936] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0958 | 0.1461 | +0.0686 [+0.0412, +0.0950] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.778] | 0.284 | 6.04 flat / 2.87 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.269 | 4.69 flat / 2.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.375, 0.778] | 4.038 [2.414, 6.300] | 1.712 [0.948, 2.849] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.577] | 4.923 [3.000, 7.625] | 2.163 [1.176, 3.630] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.613] | 4.385 [2.464, 7.000] | 1.962 [0.954, 3.408] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.769 [1.929, 6.250] | 1.779 [0.780, 3.188] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.923 [2.102, 6.418] | 1.933 [0.904, 3.414] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 7.647 [4.863, 12.333] | 3.309 [1.883, 5.773] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 3.000 [1.374, 6.802] | 2.028 [0.765, 5.108] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 188 | 0.593 | 0.441 | 0.0608 | +0.0106 [+0.0006, +0.0201] | -0.0045 [-0.0128, +0.0035] | 0.871 | 0.532 | yes |
| 2 | 0.503 (147 of 1872 days never flag) | 209 | 0.583 | 0.388 | 0.0720 | -0.0009 [-0.0095, +0.0070] | -0.0109 [-0.0193, -0.0036] | 0.810 | 0.509 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 186 | 0.522 | 0.387 | 0.0728 | -0.0022 [-0.0120, +0.0059] | -0.0085 [-0.0178, -0.0007] | 0.798 | 0.456 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 162 | 0.464 | 0.395 | 0.0709 | -0.0001 [-0.0073, +0.0066] | -0.0085 [-0.0152, -0.0023] | 0.816 | 0.407 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 162 | 0.435 | 0.370 | 0.0728 | -0.0018 [-0.0082, +0.0040] | -0.0094 [-0.0156, -0.0039] | 0.779 | 0.376 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.424 | 0.3133 | 0.2720 | +0.0133 [-0.0301, +0.0543] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1940 | 0.0159 | -0.0054 [-0.0268, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0048 | 0.0200 | +0.0003 [-0.0060, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0693 | 0.1165 | +0.0287 [+0.0051, +0.0574] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0064 | 0.0048 | +0.0077 [+0.0055, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1100 | 0.0031 | +0.0097 [+0.0032, +0.0166] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1551 | 0.4146 | 0.0595 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.441 | 0.3130 | 0.2474 | +0.0133 [-0.0243, +0.0487] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1079 | 0.1133 | +0.0563 [+0.0334, +0.0804] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1031 | 0.0630 | +0.0009 [-0.0095, +0.0109] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0355, +0.2028] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0989 | 0.1461 | +0.0689 [+0.0401, +0.0975] |

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
| 1 | 0.638 (105 of 1873 days never flag) | 190 | 0.600 | 0.442 | 0.0606 | +0.0108 [+0.0015, +0.0207] | -0.0043 [-0.0124, +0.0036] | 0.871 | 0.539 | yes |
| 2 | 0.716 (147 of 1872 days never flag) | 199 | 0.612 | 0.427 | 0.0650 | +0.0060 [-0.0034, +0.0148] | -0.0040 [-0.0128, +0.0042] | 0.837 | 0.546 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 195 | 0.558 | 0.395 | 0.0687 | +0.0020 [-0.0083, +0.0111] | -0.0043 [-0.0138, +0.0044] | 0.826 | 0.490 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 170 | 0.486 | 0.394 | 0.0650 | +0.0058 [-0.0016, +0.0130] | -0.0027 [-0.0098, +0.0041] | 0.840 | 0.426 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 167 | 0.500 | 0.413 | 0.0653 | +0.0056 [-0.0011, +0.0122] | -0.0019 [-0.0081, +0.0042] | 0.828 | 0.443 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.664 (climatology 0.457, difference +0.2071 [+0.0396, +0.3632]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0824, ΔBrier vs climatology +0.0471 [+0.0291, +0.0679], realised minus predicted -0.0169 [-0.0464, +0.0164]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.3118 | 0.2720 | +0.0131 [-0.0284, +0.0549] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0226, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0684 | 0.1165 | +0.0268 [+0.0030, +0.0587] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0074 | 0.0048 | +0.0080 [+0.0060, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1089 | 0.0031 | +0.0102 [+0.0039, +0.0159] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1375 | 0.4146 | +0.0461 [-0.0194, +0.1240] |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.441 | 0.3117 | 0.2474 | +0.0141 [-0.0216, +0.0523] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1092 | 0.1133 | +0.0568 [+0.0329, +0.0841] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1025 | 0.0630 | +0.0012 [-0.0087, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0351, +0.1989] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0958 | 0.1461 | +0.0686 [+0.0417, +0.0961] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.269 | 5.77 flat / 2.81 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.310, 0.708] | 0.269 | 4.81 flat / 2.34 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.393, 0.778] | 4.038 [2.389, 6.389] | 1.712 [0.952, 2.870] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.737] | 4.462 [2.562, 7.131] | 1.990 [1.071, 3.352] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.282, 0.667] | 4.423 [2.500, 7.201] | 2.058 [1.077, 3.556] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.808 [2.074, 6.294] | 1.856 [0.909, 3.284] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.577 [1.893, 6.000] | 1.817 [0.871, 3.268] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.556, 1.000] | 7.118 [4.417, 11.445] | 3.103 [1.776, 5.417] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.250 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 188 | 0.593 | 0.441 | 0.0608 | +0.0106 [+0.0011, +0.0202] | -0.0045 [-0.0128, +0.0038] | 0.871 | 0.532 | yes |
| 2 | 0.653 (147 of 1872 days never flag) | 204 | 0.633 | 0.431 | 0.0654 | +0.0057 [-0.0036, +0.0142] | -0.0043 [-0.0130, +0.0039] | 0.835 | 0.566 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 191 | 0.551 | 0.398 | 0.0696 | +0.0011 [-0.0095, +0.0098] | -0.0052 [-0.0151, +0.0034] | 0.818 | 0.484 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 170 | 0.514 | 0.418 | 0.0645 | +0.0063 [-0.0015, +0.0136] | -0.0021 [-0.0097, +0.0051] | 0.843 | 0.457 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 162 | 0.500 | 0.426 | 0.0645 | +0.0065 [-0.0004, +0.0130] | -0.0011 [-0.0077, +0.0053] | 0.826 | 0.446 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.713 (climatology 0.457, difference +0.2556 [+0.0750, +0.4175]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0828, ΔBrier vs climatology +0.0467 [+0.0285, +0.0663], realised minus predicted -0.0174 [-0.0486, +0.0167]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.424 | 0.3133 | 0.2720 | +0.0133 [-0.0292, +0.0558] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1940 | 0.0159 | -0.0054 [-0.0262, +0.0109] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0048 | 0.0200 | +0.0003 [-0.0054, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0693 | 0.1165 | +0.0287 [+0.0049, +0.0601] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0064 | 0.0048 | +0.0077 [+0.0055, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1100 | 0.0031 | +0.0097 [+0.0031, +0.0160] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1551 | 0.4146 | 0.0595 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.441 | 0.3130 | 0.2474 | +0.0133 [-0.0222, +0.0497] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1079 | 0.1133 | +0.0563 [+0.0321, +0.0818] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.386 | 0.1031 | 0.0630 | +0.0009 [-0.0095, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0397, +0.2077] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.889 | 0.0989 | 0.1461 | +0.0689 [+0.0400, +0.0982] |

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
| 1 | 0.517 (105 of 1873 days never flag) | 196 | 0.614 | 0.439 | 0.0561 | +0.0153 [+0.0079, +0.0235] | +0.0002 [-0.0061, +0.0067] | 0.845 | 0.551 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 212 | 0.583 | 0.382 | 0.0698 | +0.0013 [-0.0044, +0.0070] | -0.0087 [-0.0146, -0.0031] | 0.771 | 0.507 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 187 | 0.536 | 0.396 | 0.0699 | +0.0008 [-0.0040, +0.0054] | -0.0055 [-0.0105, -0.0008] | 0.725 | 0.471 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 168 | 0.471 | 0.387 | 0.0692 | +0.0017 [-0.0031, +0.0063] | -0.0068 [-0.0113, -0.0025] | 0.754 | 0.412 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 166 | 0.442 | 0.367 | 0.0728 | -0.0019 [-0.0071, +0.0030] | -0.0094 [-0.0149, -0.0042] | 0.717 | 0.381 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.419 | 0.2828 | 0.2720 | +0.0391 [+0.0075, +0.0714] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0137, +0.0099] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0086, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0022, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0671 | 0.1165 | +0.0247 [+0.0015, +0.0539] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0207 | 0.0048 | +0.0076 [+0.0057, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1277 | 0.0031 | +0.0050 [-0.0007, +0.0111] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1227 | 0.4146 | 0.0270 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.438 | 0.2857 | 0.2474 | +0.0383 [+0.0102, +0.0673] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1099 | 0.1133 | +0.0561 [+0.0318, +0.0827] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.386 | 0.1068 | 0.0630 | +0.0066 [-0.0009, +0.0146] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0345, +0.1949] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0958 | 0.1461 | +0.0686 [+0.0402, +0.0966] |

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
| 1 | 0.517 (105 of 1873 days never flag) | 197 | 0.614 | 0.437 | 0.0563 | +0.0151 [+0.0076, +0.0233] | +0.0000 [-0.0056, +0.0062] | 0.843 | 0.550 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 210 | 0.576 | 0.381 | 0.0701 | +0.0010 [-0.0050, +0.0064] | -0.0090 [-0.0148, -0.0035] | 0.764 | 0.501 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 184 | 0.522 | 0.391 | 0.0702 | +0.0005 [-0.0044, +0.0052] | -0.0058 [-0.0108, -0.0012] | 0.728 | 0.457 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 188 | 0.471 | 0.346 | 0.0699 | +0.0010 [-0.0037, +0.0058] | -0.0075 [-0.0120, -0.0028] | 0.756 | 0.400 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 170 | 0.442 | 0.359 | 0.0728 | -0.0019 [-0.0073, +0.0031] | -0.0094 [-0.0150, -0.0040] | 0.719 | 0.379 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.434 (climatology 0.457, difference -0.0235 [-0.1336, +0.0861]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0344 [+0.0211, +0.0494], realised minus predicted -0.0138 [-0.0477, +0.0235]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2844 | 0.2720 | +0.0393 [+0.0063, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2021 | 0.0159 | -0.0034 [-0.0161, +0.0082] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0103 [+0.0087, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0093 | 0.0200 | +0.0003 [-0.0055, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0680 | 0.1165 | +0.0266 [+0.0041, +0.0537] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0197 | 0.0048 | +0.0072 [+0.0052, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1287 | 0.0031 | +0.0045 [-0.0014, +0.0106] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1402 | 0.4146 | 0.0404 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.435 | 0.2871 | 0.2474 | +0.0375 [+0.0083, +0.0669] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1086 | 0.1133 | +0.0556 [+0.0327, +0.0812] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.384 | 0.1074 | 0.0630 | +0.0062 [-0.0013, +0.0143] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0412, +0.2055] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0989 | 0.1461 | +0.0689 [+0.0391, +0.0975] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.790] | 0.295 | 6.23 flat / 3.04 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.294, 0.686] | 0.269 | 5.27 flat / 2.57 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.375, 0.762] | 4.231 [2.548, 6.625] | 1.817 [1.030, 3.011] |
| lead 2 alone (fail) | 26 | 14 | 0.538 [0.343, 0.731] | 4.462 [2.583, 7.160] | 2.048 [1.096, 3.513] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.462 [2.586, 7.143] | 2.077 [1.125, 3.516] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.318, 6.549] | 1.962 [1.036, 3.393] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.277, 6.543] | 2.029 [1.054, 3.519] |
| inside 2018-2019 | 17 | 13 | 0.765 (no interval) | 7.118 (no interval) | 3.103 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 2.917 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 196 | 0.614 | 0.439 | 0.0561 | +0.0153 [+0.0080, +0.0234] | +0.0002 [-0.0058, +0.0067] | 0.845 | 0.551 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 200 | 0.604 | 0.420 | 0.0624 | +0.0087 [+0.0022, +0.0155] | -0.0013 [-0.0079, +0.0056] | 0.804 | 0.537 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 194 | 0.565 | 0.402 | 0.0655 | +0.0052 [-0.0005, +0.0112] | -0.0011 [-0.0070, +0.0049] | 0.771 | 0.498 | no |
| 4 | 0.396 (147 of 1870 days never flag) | 173 | 0.493 | 0.393 | 0.0636 | +0.0072 [+0.0013, +0.0130] | -0.0012 [-0.0072, +0.0049] | 0.789 | 0.432 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 175 | 0.507 | 0.400 | 0.0650 | +0.0059 [-0.0001, +0.0119] | -0.0016 [-0.0080, +0.0049] | 0.781 | 0.447 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.664 (climatology 0.457, difference +0.2071 [+0.0457, +0.3541]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0843, ΔBrier vs climatology +0.0452 [+0.0274, +0.0652], realised minus predicted -0.0357 [-0.0676, -0.0021]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.419 | 0.2828 | 0.2720 | +0.0391 [+0.0085, +0.0728] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0133, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0087, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0025, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0671 | 0.1165 | +0.0247 [+0.0021, +0.0541] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0207 | 0.0048 | +0.0076 [+0.0057, +0.0094] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1277 | 0.0031 | +0.0050 [-0.0008, +0.0110] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1227 | 0.4146 | 0.0270 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.438 | 0.2857 | 0.2474 | +0.0383 [+0.0107, +0.0672] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1099 | 0.1133 | +0.0561 [+0.0325, +0.0806] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.386 | 0.1068 | 0.0630 | +0.0066 [-0.0007, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0340, +0.1947] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0958 | 0.1461 | +0.0686 [+0.0412, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2839 | 0.2213 |

## risk_gbm+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.793] | 0.295 | 6.23 flat / 3.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.304, 0.708] | 0.269 | 5.27 flat / 2.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.423, 0.793] | 4.269 [2.675, 6.786] | 1.827 [1.075, 3.036] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.741] | 4.423 [2.583, 7.108] | 1.981 [1.069, 3.330] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.500 [2.609, 7.313] | 2.115 [1.130, 3.589] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.038 [2.304, 6.543] | 1.971 [1.029, 3.394] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.808 [2.179, 6.174] | 1.962 [1.023, 3.370] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.118 [4.444, 11.333] | 3.103 [1.766, 5.401] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 3.111 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 197 | 0.614 | 0.437 | 0.0563 | +0.0151 [+0.0081, +0.0233] | +0.0000 [-0.0060, +0.0061] | 0.843 | 0.550 | yes |
| 2 | 0.401 (147 of 1872 days never flag) | 201 | 0.619 | 0.428 | 0.0628 | +0.0083 [+0.0020, +0.0148] | -0.0017 [-0.0082, +0.0049] | 0.802 | 0.552 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 194 | 0.558 | 0.397 | 0.0664 | +0.0043 [-0.0015, +0.0101] | -0.0020 [-0.0081, +0.0043] | 0.764 | 0.490 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 177 | 0.522 | 0.407 | 0.0631 | +0.0077 [+0.0019, +0.0143] | -0.0007 [-0.0067, +0.0058] | 0.791 | 0.461 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 169 | 0.507 | 0.414 | 0.0642 | +0.0068 [+0.0006, +0.0128] | -0.0008 [-0.0072, +0.0058] | 0.779 | 0.450 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.713 (climatology 0.457, difference +0.2556 [+0.0730, +0.4226]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0446 [+0.0274, +0.0645], realised minus predicted -0.0359 [-0.0663, -0.0037]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2844 | 0.2720 | +0.0393 [+0.0072, +0.0745] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2021 | 0.0159 | -0.0034 [-0.0161, +0.0077] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0103 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0093 | 0.0200 | +0.0003 [-0.0057, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0680 | 0.1165 | +0.0266 [+0.0046, +0.0550] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0197 | 0.0048 | +0.0072 [+0.0052, +0.0090] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1287 | 0.0031 | +0.0045 [-0.0014, +0.0105] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1402 | 0.4146 | 0.0404 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.435 | 0.2871 | 0.2474 | +0.0375 [+0.0098, +0.0669] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1086 | 0.1133 | +0.0556 [+0.0332, +0.0799] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.384 | 0.1074 | 0.0630 | +0.0062 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0381, +0.2092] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0989 | 0.1461 | +0.0689 [+0.0398, +0.0971] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.424, 0.800] | 0.271 | 5.81 flat / 2.69 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.643] | 0.269 | 4.73 flat / 2.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.774] | 4.538 [2.727, 7.167] | 1.990 [1.138, 3.328] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.654 [2.839, 7.381] | 2.106 [1.125, 3.605] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.385 [2.433, 7.126] | 1.981 [1.000, 3.511] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.000 [2.184, 6.725] | 1.837 [0.875, 3.366] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.615] | 4.500 [2.565, 7.351] | 2.058 [1.048, 3.641] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.588 [4.889, 11.820] | 3.235 [1.913, 5.306] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 2.444 [0.936, 6.167] | 1.667 [0.500, 4.816] |

Recall with equal weight per regime: 0.416 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 203 | 0.607 | 0.419 | 0.0601 | +0.0113 [+0.0007, +0.0213] | -0.0037 [-0.0137, +0.0053] | 0.889 | 0.539 | yes |
| 2 | 0.575 (147 of 1872 days never flag) | 197 | 0.547 | 0.386 | 0.0693 | +0.0018 [-0.0072, +0.0099] | -0.0082 [-0.0170, -0.0006] | 0.843 | 0.477 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 188 | 0.536 | 0.394 | 0.0685 | +0.0022 [-0.0077, +0.0108] | -0.0041 [-0.0138, +0.0044] | 0.848 | 0.470 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 176 | 0.522 | 0.409 | 0.0667 | +0.0041 [-0.0033, +0.0103] | -0.0043 [-0.0113, +0.0019] | 0.837 | 0.462 | no |
| 5 | 0.446 (147 of 1869 days never flag) | 192 | 0.543 | 0.391 | 0.0735 | -0.0026 [-0.0122, +0.0056] | -0.0101 [-0.0197, -0.0019] | 0.807 | 0.476 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.404 | 0.3144 | 0.2720 | +0.0058 [-0.0440, +0.0510] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1416 | 0.0159 | +0.0115 [-0.0117, +0.0298] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0093 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0000, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0704 | 0.1165 | +0.0229 [+0.0014, +0.0521] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0032 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0649 | 0.0031 | +0.0232 [+0.0164, +0.0301] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0875 | 0.4146 | 0.0235 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.418 | 0.3190 | 0.2474 | +0.0078 [-0.0345, +0.0458] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1079 | 0.1133 | +0.0573 [+0.0322, +0.0838] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.364 | 0.0919 | 0.0630 | +0.0018 [-0.0100, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0372, +0.1973] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0958 | 0.1461 | +0.0686 [+0.0409, +0.0959] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2740 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.381, 0.769] | 0.276 | 5.88 flat / 2.84 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.611] | 0.269 | 4.88 flat / 2.29 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.381, 0.769] | 4.577 [2.823, 6.934] | 2.000 [1.125, 3.232] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.176, 0.520] | 4.538 [2.652, 7.040] | 2.106 [1.109, 3.501] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.346 [2.440, 6.854] | 1.942 [0.941, 3.297] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.038 [2.250, 6.522] | 1.846 [0.871, 3.212] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.692 [2.738, 7.286] | 2.231 [1.166, 3.733] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.588 [4.867, 11.668] | 3.235 [1.958, 5.328] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 2.083 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 203 | 0.600 | 0.414 | 0.0602 | +0.0112 [+0.0004, +0.0212] | -0.0039 [-0.0140, +0.0049] | 0.888 | 0.531 | yes |
| 2 | 0.503 (147 of 1872 days never flag) | 192 | 0.532 | 0.385 | 0.0696 | +0.0015 [-0.0073, +0.0093] | -0.0085 [-0.0175, -0.0008] | 0.838 | 0.464 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 186 | 0.529 | 0.392 | 0.0688 | +0.0019 [-0.0079, +0.0100] | -0.0044 [-0.0144, +0.0036] | 0.848 | 0.464 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 178 | 0.529 | 0.410 | 0.0674 | +0.0034 [-0.0040, +0.0098] | -0.0050 [-0.0120, +0.0013] | 0.839 | 0.468 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 196 | 0.536 | 0.378 | 0.0735 | -0.0026 [-0.0119, +0.0055] | -0.0101 [-0.0191, -0.0023] | 0.810 | 0.466 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.402 | 0.3160 | 0.2720 | +0.0061 [-0.0406, +0.0508] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1437 | 0.0159 | +0.0101 [-0.0143, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0014 [-0.0038, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0713 | 0.1165 | +0.0248 [+0.0042, +0.0524] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0021 | 0.0048 | +0.0084 [+0.0065, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0660 | 0.0031 | +0.0228 [+0.0150, +0.0299] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1051 | 0.4146 | 0.0370 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.413 | 0.3204 | 0.2474 | +0.0070 [-0.0334, +0.0455] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1066 | 0.1133 | +0.0569 [+0.0339, +0.0832] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.364 | 0.0925 | 0.0630 | +0.0015 [-0.0105, +0.0120] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2074 | 0.2903 | +0.1247 [+0.0450, +0.2039] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.0989 | 0.1461 | +0.0689 [+0.0395, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.436, 0.800] | 0.269 | 5.62 flat / 2.62 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.704] | 0.269 | 4.81 flat / 2.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.387, 0.769] | 4.538 [2.689, 7.096] | 1.990 [1.121, 3.283] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.312, 0.692] | 4.346 [2.500, 7.000] | 1.981 [1.073, 3.333] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.462 [2.556, 7.167] | 2.058 [1.100, 3.456] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.808 [2.097, 6.250] | 1.837 [0.940, 3.181] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.692 [2.000, 6.143] | 1.817 [0.890, 3.209] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.611, 11.534] | 2.985 [1.750, 5.109] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.917 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 203 | 0.607 | 0.419 | 0.0601 | +0.0113 [+0.0003, +0.0215] | -0.0037 [-0.0141, +0.0053] | 0.889 | 0.539 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 195 | 0.590 | 0.421 | 0.0630 | +0.0080 [-0.0015, +0.0162] | -0.0020 [-0.0117, +0.0062] | 0.861 | 0.525 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 194 | 0.565 | 0.402 | 0.0655 | +0.0052 [-0.0057, +0.0141] | -0.0011 [-0.0119, +0.0078] | 0.865 | 0.498 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 166 | 0.486 | 0.404 | 0.0622 | +0.0087 [+0.0014, +0.0153] | +0.0002 [-0.0069, +0.0073] | 0.855 | 0.428 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 165 | 0.500 | 0.418 | 0.0667 | +0.0043 [-0.0052, +0.0124] | -0.0033 [-0.0118, +0.0047] | 0.847 | 0.445 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.404 | 0.3144 | 0.2720 | +0.0058 [-0.0429, +0.0510] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1416 | 0.0159 | +0.0115 [-0.0122, +0.0306] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0093 | 0.0000 | +0.0128 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0003, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0704 | 0.1165 | +0.0229 [+0.0014, +0.0502] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0032 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0649 | 0.0031 | +0.0232 [+0.0165, +0.0304] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0875 | 0.4146 | +0.0235 [-0.0110, +0.0737] |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.418 | 0.3190 | 0.2474 | +0.0078 [-0.0350, +0.0467] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1079 | 0.1133 | +0.0573 [+0.0325, +0.0825] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.364 | 0.0919 | 0.0630 | +0.0018 [-0.0101, +0.0122] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0320, +0.1961] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0958 | 0.1461 | +0.0686 [+0.0427, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2740 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.438, 0.790] | 0.269 | 5.42 flat / 2.56 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.708] | 0.269 | 4.69 flat / 2.24 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.765] | 4.577 [2.692, 7.101] | 2.000 [1.081, 3.240] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.321, 0.688] | 4.385 [2.417, 7.000] | 1.962 [1.033, 3.299] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 4.423 [2.470, 7.076] | 2.048 [1.073, 3.487] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.731 [2.000, 6.235] | 1.808 [0.886, 3.185] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.577 [1.884, 6.000] | 1.788 [0.852, 3.191] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.476, 11.364] | 2.985 [1.700, 4.964] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.111 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 203 | 0.600 | 0.414 | 0.0602 | +0.0112 [+0.0006, +0.0218] | -0.0039 [-0.0143, +0.0052] | 0.888 | 0.531 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 198 | 0.604 | 0.424 | 0.0634 | +0.0077 [-0.0012, +0.0158] | -0.0023 [-0.0115, +0.0060] | 0.860 | 0.539 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 193 | 0.565 | 0.404 | 0.0663 | +0.0044 [-0.0063, +0.0141] | -0.0019 [-0.0123, +0.0076] | 0.860 | 0.499 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 168 | 0.514 | 0.423 | 0.0616 | +0.0092 [+0.0016, +0.0160] | +0.0008 [-0.0069, +0.0079] | 0.858 | 0.458 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 162 | 0.500 | 0.426 | 0.0658 | +0.0051 [-0.0041, +0.0139] | -0.0024 [-0.0115, +0.0064] | 0.845 | 0.446 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.402 | 0.3160 | 0.2720 | +0.0061 [-0.0439, +0.0532] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1437 | 0.0159 | +0.0101 [-0.0149, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0014 [-0.0036, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0713 | 0.1165 | +0.0248 [+0.0036, +0.0528] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0021 | 0.0048 | +0.0084 [+0.0064, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0660 | 0.0031 | +0.0228 [+0.0150, +0.0301] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1051 | 0.4146 | 0.0370 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.413 | 0.3204 | 0.2474 | +0.0070 [-0.0361, +0.0472] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1066 | 0.1133 | +0.0569 [+0.0334, +0.0829] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.364 | 0.0925 | 0.0630 | +0.0015 [-0.0104, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2074 | 0.2903 | +0.1247 [+0.0424, +0.2057] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.0989 | 0.1461 | +0.0689 [+0.0398, +0.0977] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_gbm+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.760] | 0.269 | 5.69 flat / 2.71 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.269 | 4.65 flat / 2.10 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.760] | 4.577 [2.794, 7.208] | 2.029 [1.169, 3.333] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.577 [2.778, 7.312] | 2.144 [1.208, 3.684] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.346 [2.454, 7.250] | 1.962 [1.000, 3.463] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.000 [2.233, 6.679] | 1.837 [0.875, 3.350] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 4.462 [2.536, 7.346] | 2.019 [1.019, 3.588] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.588 [5.000, 12.000] | 3.235 [1.987, 5.515] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.111 (no interval) | 1.722 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 204 | 0.607 | 0.417 | 0.0535 | +0.0179 [+0.0101, +0.0259] | +0.0028 [-0.0035, +0.0092] | 0.875 | 0.538 | yes |
| 2 | 0.398 (147 of 1872 days never flag) | 194 | 0.540 | 0.387 | 0.0657 | +0.0053 [-0.0009, +0.0115] | -0.0047 [-0.0109, +0.0008] | 0.830 | 0.471 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 187 | 0.536 | 0.396 | 0.0646 | +0.0061 [+0.0005, +0.0113] | -0.0002 [-0.0059, +0.0050] | 0.827 | 0.471 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 178 | 0.536 | 0.416 | 0.0644 | +0.0064 [+0.0013, +0.0112] | -0.0021 [-0.0070, +0.0026] | 0.821 | 0.476 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 190 | 0.536 | 0.389 | 0.0693 | +0.0016 [-0.0039, +0.0067] | -0.0059 [-0.0120, -0.0002] | 0.782 | 0.469 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.404 | 0.2800 | 0.2720 | +0.0371 [+0.0034, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1646 | 0.0159 | +0.0112 [-0.0039, +0.0241] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0141 | 0.0000 | +0.0125 [+0.0110, +0.0142] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0038 | 0.0200 | +0.0037 [-0.0000, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0680 | 0.1165 | +0.0261 [+0.0027, +0.0556] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0058 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0877 | 0.0031 | +0.0185 [+0.0122, +0.0249] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0948 | 0.4146 | 0.0254 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.416 | 0.2886 | 0.2474 | +0.0369 [+0.0073, +0.0668] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1084 | 0.1133 | +0.0573 [+0.0338, +0.0828] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0893 | 0.0630 | +0.0095 [+0.0015, +0.0172] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0349, +0.1997] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0958 | 0.1461 | +0.0686 [+0.0411, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2398 | 0.2213 |

## risk_gbm+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.795] | 0.276 | 5.88 flat / 2.83 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.269 | 4.81 flat / 2.23 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.795] | 4.692 [2.932, 7.111] | 2.058 [1.185, 3.310] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.536] | 4.500 [2.675, 7.000] | 2.096 [1.129, 3.444] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.308 [2.428, 6.896] | 1.923 [0.955, 3.250] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.077 [2.266, 6.501] | 1.856 [0.894, 3.205] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.654 [2.676, 7.347] | 2.192 [1.167, 3.706] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.588 [4.947, 11.876] | 3.235 [1.964, 5.375] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 207 | 0.607 | 0.411 | 0.0537 | +0.0177 [+0.0100, +0.0266] | +0.0026 [-0.0038, +0.0093] | 0.874 | 0.537 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 191 | 0.532 | 0.387 | 0.0660 | +0.0050 [-0.0015, +0.0112] | -0.0050 [-0.0115, +0.0008] | 0.826 | 0.465 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 185 | 0.529 | 0.395 | 0.0648 | +0.0058 [-0.0002, +0.0112] | -0.0005 [-0.0062, +0.0048] | 0.829 | 0.464 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 180 | 0.536 | 0.411 | 0.0651 | +0.0057 [+0.0003, +0.0104] | -0.0028 [-0.0079, +0.0021] | 0.821 | 0.475 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 195 | 0.536 | 0.379 | 0.0693 | +0.0016 [-0.0039, +0.0069] | -0.0059 [-0.0120, -0.0000] | 0.784 | 0.466 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.402 | 0.2816 | 0.2720 | +0.0374 [+0.0036, +0.0721] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1666 | 0.0159 | +0.0098 [-0.0062, +0.0242] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0125 [+0.0109, +0.0142] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0015 | 0.0200 | +0.0014 [-0.0033, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0689 | 0.1165 | +0.0281 [+0.0048, +0.0562] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0047 | 0.0048 | +0.0084 [+0.0064, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0887 | 0.0031 | +0.0181 [+0.0112, +0.0246] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1124 | 0.4146 | 0.0388 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.409 | 0.2899 | 0.2474 | +0.0361 [+0.0072, +0.0674] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1071 | 0.1133 | +0.0569 [+0.0325, +0.0828] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.359 | 0.0899 | 0.0630 | +0.0092 [+0.0015, +0.0177] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0409, +0.2097] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.0989 | 0.1461 | +0.0689 [+0.0389, +0.0989] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2396 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.433, 0.800] | 0.269 | 5.54 flat / 2.59 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.306, 0.696] | 0.269 | 4.73 flat / 2.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.781] | 4.577 [2.833, 7.135] | 2.029 [1.188, 3.275] |
| lead 2 alone (fail) | 26 | 14 | 0.538 [0.348, 0.731] | 4.385 [2.606, 7.001] | 2.019 [1.083, 3.407] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.304, 0.704] | 4.423 [2.629, 7.088] | 2.038 [1.081, 3.427] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.769 [2.120, 6.191] | 1.827 [0.932, 3.160] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.731 [2.069, 6.143] | 1.856 [0.913, 3.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.562, 11.375] | 2.985 [1.739, 5.094] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.444 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 204 | 0.607 | 0.417 | 0.0535 | +0.0179 [+0.0098, +0.0258] | +0.0028 [-0.0035, +0.0091] | 0.875 | 0.538 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 197 | 0.597 | 0.421 | 0.0589 | +0.0122 [+0.0052, +0.0190] | +0.0022 [-0.0049, +0.0090] | 0.849 | 0.531 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 194 | 0.572 | 0.407 | 0.0609 | +0.0097 [+0.0031, +0.0165] | +0.0034 [-0.0030, +0.0101] | 0.847 | 0.506 | no |
| 4 | 0.396 (147 of 1870 days never flag) | 166 | 0.493 | 0.410 | 0.0594 | +0.0114 [+0.0053, +0.0172] | +0.0029 [-0.0031, +0.0090] | 0.839 | 0.436 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 166 | 0.500 | 0.416 | 0.0620 | +0.0089 [+0.0028, +0.0152] | +0.0014 [-0.0052, +0.0077] | 0.828 | 0.444 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.404 | 0.2800 | 0.2720 | +0.0371 [+0.0030, +0.0714] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1646 | 0.0159 | +0.0112 [-0.0046, +0.0247] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0141 | 0.0000 | +0.0125 [+0.0110, +0.0141] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0038 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0680 | 0.1165 | +0.0261 [+0.0029, +0.0561] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0058 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0877 | 0.0031 | +0.0185 [+0.0124, +0.0247] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0948 | 0.4146 | 0.0254 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.416 | 0.2886 | 0.2474 | +0.0369 [+0.0061, +0.0673] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1084 | 0.1133 | +0.0573 [+0.0332, +0.0822] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0893 | 0.0630 | +0.0095 [+0.0017, +0.0175] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0324, +0.2003] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.0958 | 0.1461 | +0.0686 [+0.0424, +0.0952] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2398 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.792] | 0.269 | 5.54 flat / 2.63 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.692] | 0.269 | 4.73 flat / 2.27 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.435, 0.792] | 4.692 [2.828, 7.091] | 2.058 [1.155, 3.290] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.316, 0.688] | 4.423 [2.515, 6.931] | 1.971 [1.030, 3.240] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.278, 0.654] | 4.500 [2.520, 7.131] | 2.115 [1.137, 3.500] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.731 [2.037, 6.041] | 1.808 [0.901, 3.083] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.577 [1.880, 5.793] | 1.788 [0.871, 3.074] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.412, 11.417] | 2.985 [1.685, 5.028] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.444 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 207 | 0.607 | 0.411 | 0.0537 | +0.0177 [+0.0096, +0.0260] | +0.0026 [-0.0038, +0.0090] | 0.874 | 0.537 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 199 | 0.604 | 0.422 | 0.0592 | +0.0118 [+0.0046, +0.0186] | +0.0018 [-0.0054, +0.0085] | 0.848 | 0.538 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 196 | 0.572 | 0.403 | 0.0618 | +0.0089 [+0.0022, +0.0157] | +0.0026 [-0.0040, +0.0094] | 0.841 | 0.505 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 169 | 0.522 | 0.426 | 0.0589 | +0.0119 [+0.0053, +0.0185] | +0.0035 [-0.0033, +0.0102] | 0.841 | 0.466 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 162 | 0.500 | 0.426 | 0.0612 | +0.0097 [+0.0035, +0.0163] | +0.0022 [-0.0045, +0.0090] | 0.823 | 0.446 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.713 (climatology 0.457, difference +0.2563 [+0.0674, +0.4122]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0806, ΔBrier vs climatology +0.0488 [+0.0314, +0.0676], realised minus predicted -0.0038 [-0.0351, +0.0269]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.402 | 0.2816 | 0.2720 | +0.0374 [+0.0029, +0.0721] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1666 | 0.0159 | +0.0098 [-0.0062, +0.0234] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0125 [+0.0109, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0015 | 0.0200 | +0.0014 [-0.0035, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0689 | 0.1165 | +0.0281 [+0.0055, +0.0587] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0047 | 0.0048 | +0.0084 [+0.0064, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0887 | 0.0031 | +0.0181 [+0.0112, +0.0246] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1124 | 0.4146 | 0.0388 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.409 | 0.2899 | 0.2474 | +0.0361 [+0.0052, +0.0675] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1071 | 0.1133 | +0.0569 [+0.0320, +0.0820] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.359 | 0.0899 | 0.0630 | +0.0092 [+0.0013, +0.0175] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0427, +0.2059] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.0989 | 0.1461 | +0.0689 [+0.0389, +0.0993] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2396 | 0.2213 |

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

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.714 (climatology 0.457, difference +0.2566 [+0.0629, +0.4146]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0429 [+0.0308, +0.0563], realised minus predicted +0.0594 [+0.0304, +0.0911]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0211, +0.0239] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0168 | 0.0159 | +0.0382 [+0.0294, +0.0470] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0005 | 0.0200 | +0.0014 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0395 | 0.1165 | +0.0174 [+0.0002, +0.0403] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0012 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0046 | 0.0031 | +0.0291 [+0.0209, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0449 | 0.4146 | 0.0060 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0984 | 0.2474 | +0.0146 [-0.0055, +0.0359] |
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

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
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
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0354 | 0.1165 | +0.0158 [+0.0016, +0.0330] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0072 | 0.0031 | +0.0290 [+0.0225, +0.0354] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0352 | 0.4146 | -0.0002 [-0.0278, +0.0371] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.565 | 0.1006 | 0.2474 | +0.0080 [-0.0097, +0.0247] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0983 | 0.1133 | +0.0339 [+0.0115, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0128 | 0.0630 | +0.0052 [+0.0001, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2030 | 0.2903 | +0.1101 [+0.0294, +0.1928] |
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
| lead_at_least_1 | 26 | 18 | 0.692 [0.520, 0.850] | 0.416 | 7.96 flat / 3.85 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.652] | 0.288 | 6.15 flat / 2.93 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.440, 0.800] | 5.192 [3.444, 7.619] | 2.279 [1.430, 3.600] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.207, 7.400] | 2.029 [1.250, 3.234] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.769 [2.941, 7.392] | 2.058 [1.214, 3.282] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 4.385 [2.710, 6.789] | 1.913 [1.142, 3.070] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.423 [2.703, 6.929] | 2.087 [1.241, 3.395] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.471 [4.773, 11.779] | 3.176 [1.867, 5.251] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 8.889 (no interval) | 5.111 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 231 | 0.686 | 0.416 | 0.0493 | +0.0221 [+0.0150, +0.0301] | +0.0071 [+0.0024, +0.0121] | 0.896 | 0.608 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 222 | 0.669 | 0.419 | 0.0605 | +0.0105 [+0.0064, +0.0147] | +0.0005 [-0.0026, +0.0036] | 0.827 | 0.595 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 201 | 0.558 | 0.383 | 0.0616 | +0.0091 [+0.0053, +0.0128] | +0.0027 [-0.0002, +0.0057] | 0.803 | 0.486 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 188 | 0.536 | 0.394 | 0.0594 | +0.0115 [+0.0069, +0.0160] | +0.0030 [+0.0001, +0.0063] | 0.833 | 0.470 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 183 | 0.493 | 0.372 | 0.0630 | +0.0080 [+0.0035, +0.0121] | +0.0004 [-0.0027, +0.0034] | 0.782 | 0.426 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.470 (climatology 0.457, difference +0.0128 [-0.1151, +0.1356]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0858, ΔBrier vs climatology +0.0437 [+0.0298, +0.0593], realised minus predicted +0.0101 [-0.0214, +0.0449]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.420 | 0.2386 | 0.2720 | +0.0542 [+0.0257, +0.0845] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1280 | 0.0159 | +0.0166 [+0.0011, +0.0300] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0321 | 0.0200 | +0.0008 [-0.0060, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.1117 | 0.1165 | +0.0278 [+0.0022, +0.0605] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0217 | 0.0048 | +0.0082 [+0.0060, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0717 | 0.0031 | +0.0216 [+0.0151, +0.0276] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2195 | 0.4146 | 0.0692 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.412 | 0.2469 | 0.2474 | +0.0489 [+0.0240, +0.0753] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1076 | 0.1133 | +0.0390 [+0.0158, +0.0634] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.370 | 0.0863 | 0.0630 | +0.0163 [+0.0092, +0.0242] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2030 | 0.2903 | +0.1101 [+0.0330, +0.1908] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1197 | 0.1461 | +0.0681 [+0.0467, +0.0928] |

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
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.269 | 5.38 flat / 2.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 3.385 [2.367, 4.929] | 1.567 [1.045, 2.389] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.516] | 3.808 [2.562, 5.653] | 1.558 [1.013, 2.364] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 3.500 [2.233, 5.353] | 1.596 [1.008, 2.500] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 3.808 [2.500, 5.715] | 1.606 [1.050, 2.430] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.210, 0.571] | 3.731 [2.367, 5.600] | 1.625 [1.042, 2.475] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 5.765 [3.759, 9.154] | 2.191 [1.416, 3.568] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.111 (no interval) | 6.389 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 170 | 0.586 | 0.482 | 0.0511 | +0.0203 [+0.0135, +0.0272] | +0.0052 [+0.0007, +0.0098] | 0.805 | 0.535 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 171 | 0.518 | 0.421 | 0.0628 | +0.0083 [+0.0035, +0.0129] | -0.0017 [-0.0059, +0.0021] | 0.748 | 0.461 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 155 | 0.464 | 0.413 | 0.0617 | +0.0090 [+0.0040, +0.0138] | +0.0027 [-0.0017, +0.0065] | 0.745 | 0.411 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 169 | 0.507 | 0.414 | 0.0602 | +0.0106 [+0.0055, +0.0155] | +0.0021 [-0.0015, +0.0055] | 0.761 | 0.450 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 166 | 0.500 | 0.416 | 0.0636 | +0.0073 [+0.0021, +0.0122] | -0.0002 [-0.0043, +0.0036] | 0.740 | 0.444 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.457, difference +0.0407 [-0.0963, +0.1618]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0878, ΔBrier vs climatology +0.0417 [+0.0289, +0.0553], realised minus predicted +0.0592 [+0.0303, +0.0907]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.544 | 0.1689 | 0.2720 | +0.0386 [+0.0127, +0.0658] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.0329 | 0.0159 | +0.0256 [+0.0080, +0.0396] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0145 | 0.0200 | +0.0009 [-0.0065, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.529 | 0.0867 | 0.1165 | +0.0269 [+0.0031, +0.0546] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0076 | 0.0048 | +0.0084 [+0.0062, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0121 | 0.0031 | +0.0276 [+0.0203, +0.0338] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.571 | 0.1906 | 0.4146 | 0.0671 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.514 | 0.1693 | 0.2474 | +0.0372 [+0.0134, +0.0612] |
| day_type | month_end | 150 | 17 | 0.824 | 0.538 | 0.1021 | 0.1133 | +0.0395 [+0.0145, +0.0650] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.454 | 0.0421 | 0.0630 | +0.0141 [+0.0076, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1101 [+0.0304, +0.1894] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1197 | 0.1461 | +0.0681 [+0.0458, +0.0933] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3903 | 0.2213 |

## risk_gbm_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.800] | 0.358 | 6.69 flat / 3.24 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.269 | 5.77 flat / 2.71 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.769] | 4.577 [2.937, 7.000] | 1.971 [1.220, 3.155] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.600] | 4.462 [2.733, 7.000] | 1.837 [1.078, 3.068] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 5.000 [3.050, 7.835] | 2.221 [1.238, 3.695] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.385 [2.621, 6.884] | 1.837 [1.060, 3.060] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 3.962 [2.343, 6.391] | 1.808 [1.033, 3.090] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.176 [4.416, 11.400] | 3.088 [1.760, 5.171] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.778 (no interval) | 3.528 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 212 | 0.664 | 0.439 | 0.0493 | +0.0221 [+0.0157, +0.0295] | +0.0070 [+0.0025, +0.0120] | 0.891 | 0.596 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 203 | 0.626 | 0.429 | 0.0598 | +0.0112 [+0.0080, +0.0146] | +0.0012 [-0.0022, +0.0047] | 0.810 | 0.559 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 209 | 0.572 | 0.378 | 0.0602 | +0.0105 [+0.0072, +0.0141] | +0.0042 [+0.0007, +0.0081] | 0.793 | 0.497 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 187 | 0.529 | 0.390 | 0.0577 | +0.0131 [+0.0094, +0.0167] | +0.0047 [+0.0017, +0.0078] | 0.829 | 0.463 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 165 | 0.449 | 0.376 | 0.0613 | +0.0096 [+0.0062, +0.0129] | +0.0021 [-0.0010, +0.0050] | 0.773 | 0.390 | no |

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
| regime | 2018-19 | 375 | 102 | 0.755 | 0.440 | 0.2205 | 0.2720 | +0.0484 [+0.0229, +0.0773] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1155 | 0.0159 | +0.0222 [+0.0095, +0.0341] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0155 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0227 | 0.0200 | +0.0029 [-0.0014, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.560 | 0.0952 | 0.1165 | +0.0279 [+0.0056, +0.0558] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0168 | 0.0048 | +0.0089 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0615 | 0.0031 | +0.0238 [+0.0178, +0.0297] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.1795 | 0.4146 | 0.0631 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.428 | 0.2283 | 0.2474 | +0.0463 [+0.0232, +0.0723] |
| day_type | month_end | 150 | 17 | 0.765 | 0.542 | 0.1062 | 0.1133 | +0.0381 [+0.0148, +0.0630] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.395 | 0.0747 | 0.0630 | +0.0163 [+0.0102, +0.0236] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2030 | 0.2903 | +0.1101 [+0.0330, +0.1898] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1197 | 0.1461 | +0.0681 [+0.0457, +0.0916] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0837 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2566 | 0.2213 |

## risk_gbm_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.857] | 0.397 | 7.65 flat / 3.65 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.285, 0.639] | 0.271 | 5.85 flat / 2.74 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.154 [3.475, 7.500] | 2.269 [1.458, 3.500] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.885 [3.172, 7.250] | 2.000 [1.233, 3.079] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.615 [2.867, 7.074] | 1.981 [1.171, 3.203] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.231 [2.606, 6.417] | 1.827 [1.070, 2.950] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 4.308 [2.647, 6.580] | 2.010 [1.186, 3.202] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.471 [4.909, 11.714] | 3.176 [1.945, 5.269] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 8.000 [5.083, 15.000] | 4.556 [2.731, 9.750] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 230 | 0.686 | 0.417 | 0.0486 | +0.0228 [+0.0157, +0.0304] | +0.0077 [+0.0033, +0.0127] | 0.912 | 0.608 | yes |
| 2 | 0.233 (147 of 1872 days never flag) | 220 | 0.669 | 0.423 | 0.0598 | +0.0113 [+0.0069, +0.0155] | +0.0013 [-0.0017, +0.0044] | 0.870 | 0.596 | yes |
| 3 | 0.241 (147 of 1871 days never flag) | 197 | 0.558 | 0.391 | 0.0599 | +0.0108 [+0.0072, +0.0147] | +0.0045 [+0.0016, +0.0074] | 0.855 | 0.489 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 184 | 0.536 | 0.402 | 0.0581 | +0.0128 [+0.0087, +0.0172] | +0.0043 [+0.0015, +0.0075] | 0.869 | 0.473 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 180 | 0.493 | 0.378 | 0.0620 | +0.0090 [+0.0048, +0.0131] | +0.0014 [-0.0017, +0.0045] | 0.844 | 0.428 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.470 (climatology 0.457, difference +0.0128 [-0.1137, +0.1261]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0449 [+0.0312, +0.0600], realised minus predicted +0.0367 [+0.0059, +0.0695]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.420 | 0.2386 | 0.2720 | +0.0542 [+0.0277, +0.0836] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1280 | 0.0159 | +0.0166 [+0.0013, +0.0311] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0045 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [-0.0002, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.0981 | 0.1165 | +0.0286 [+0.0038, +0.0577] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0717 | 0.0031 | +0.0216 [+0.0153, +0.0276] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2195 | 0.4146 | 0.0692 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.412 | 0.2469 | 0.2474 | +0.0489 [+0.0239, +0.0764] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1056 | 0.1133 | +0.0391 [+0.0146, +0.0638] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.372 | 0.0731 | 0.0630 | +0.0171 [+0.0102, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2030 | 0.2903 | +0.1101 [+0.0303, +0.1887] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1197 | 0.1461 | +0.0681 [+0.0458, +0.0909] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.471, 0.833] | 0.385 | 7.35 flat / 3.65 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.269 | 5.69 flat / 2.70 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.763] | 4.615 [3.121, 6.941] | 2.144 [1.371, 3.400] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.229, 0.550] | 4.308 [2.793, 6.467] | 1.692 [1.090, 2.604] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.500 [2.703, 7.046] | 2.010 [1.177, 3.287] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.577 [2.943, 7.000] | 2.058 [1.274, 3.278] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 4.385 [2.760, 6.768] | 2.048 [1.226, 3.328] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.706 [4.080, 10.750] | 2.824 [1.590, 4.767] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.751] | 8.556 [5.545, 17.000] | 5.222 [3.115, 11.301] |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 213 | 0.664 | 0.437 | 0.0498 | +0.0216 [+0.0164, +0.0270] | +0.0065 [+0.0017, +0.0109] | 0.905 | 0.595 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 199 | 0.626 | 0.437 | 0.0608 | +0.0103 [+0.0070, +0.0134] | +0.0003 [-0.0041, +0.0040] | 0.836 | 0.561 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 190 | 0.529 | 0.384 | 0.0608 | +0.0098 [+0.0064, +0.0132] | +0.0035 [-0.0006, +0.0073] | 0.812 | 0.461 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 195 | 0.551 | 0.390 | 0.0592 | +0.0116 [+0.0080, +0.0152] | +0.0032 [-0.0007, +0.0067] | 0.838 | 0.482 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 182 | 0.493 | 0.374 | 0.0624 | +0.0085 [+0.0051, +0.0118] | +0.0010 [-0.0028, +0.0044] | 0.791 | 0.427 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.462 (climatology 0.457, difference +0.0047 [-0.1137, +0.1288]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0912, ΔBrier vs climatology +0.0382 [+0.0274, +0.0494], realised minus predicted +0.0513 [+0.0181, +0.0868]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.466 | 0.1679 | 0.2720 | +0.0397 [+0.0236, +0.0565] |
| regime | 2020 | 251 | 4 | 0.250 | 0.048 | 0.0767 | 0.0159 | +0.0298 [+0.0191, +0.0399] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0032 [-0.0013, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.552 | 0.0736 | 0.1165 | +0.0284 [+0.0062, +0.0551] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0113 | 0.0048 | +0.0091 [+0.0073, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0394 | 0.0031 | +0.0272 [+0.0210, +0.0330] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.1273 | 0.4146 | +0.0558 [-0.0078, +0.1172] |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.450 | 0.1737 | 0.2474 | +0.0421 [+0.0258, +0.0585] |
| day_type | month_end | 150 | 17 | 0.824 | 0.519 | 0.1030 | 0.1133 | +0.0368 [+0.0140, +0.0590] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.404 | 0.0496 | 0.0630 | +0.0159 [+0.0116, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1101 [+0.0335, +0.1910] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1197 | 0.1461 | +0.0681 [+0.0447, +0.0917] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2254 | 0.2213 |

## risk_gbm_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.767] | 0.308 | 6.46 flat / 3.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.613] | 0.269 | 5.12 flat / 2.45 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.767] | 4.808 [2.965, 7.319] | 2.183 [1.250, 3.492] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.577] | 4.923 [2.974, 7.546] | 2.135 [1.163, 3.479] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 4.615 [2.658, 7.200] | 2.173 [1.160, 3.550] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.038 [2.316, 6.348] | 1.885 [0.950, 3.204] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 3.808 [2.000, 6.185] | 1.837 [0.857, 3.238] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.955] | 7.647 [4.908, 11.932] | 3.309 [1.932, 5.584] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 4.222 [2.143, 9.000] | 2.722 [1.143, 6.562] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 210 | 0.607 | 0.405 | 0.0621 | +0.0093 [-0.0004, +0.0185] | -0.0058 [-0.0144, +0.0021] | 0.873 | 0.535 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 210 | 0.590 | 0.390 | 0.0720 | -0.0010 [-0.0101, +0.0068] | -0.0110 [-0.0197, -0.0036] | 0.813 | 0.516 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 192 | 0.522 | 0.375 | 0.0736 | -0.0030 [-0.0119, +0.0047] | -0.0093 [-0.0179, -0.0016] | 0.791 | 0.452 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 170 | 0.471 | 0.382 | 0.0702 | +0.0006 [-0.0064, +0.0073] | -0.0078 [-0.0144, -0.0014] | 0.818 | 0.410 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 159 | 0.435 | 0.377 | 0.0728 | -0.0019 [-0.0084, +0.0035] | -0.0094 [-0.0157, -0.0040] | 0.770 | 0.378 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.444 (climatology 0.457, difference -0.0128 [-0.1462, +0.1177]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0945, ΔBrier vs climatology +0.0350 [+0.0212, +0.0497], realised minus predicted +0.0052 [-0.0306, +0.0422]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.398 | 0.3131 | 0.2720 | +0.0099 [-0.0341, +0.0495] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2026 | 0.0159 | -0.0107 [-0.0348, +0.0082] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0064 | 0.0200 | +0.0027 [-0.0027, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0652 | 0.1165 | +0.0271 [+0.0049, +0.0550] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0061 | 0.0048 | +0.0087 [+0.0069, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1125 | 0.0031 | +0.0096 [+0.0039, +0.0152] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1454 | 0.4146 | +0.0534 [-0.0190, +0.1306] |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.399 | 0.3152 | 0.2474 | +0.0067 [-0.0323, +0.0409] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1090 | 0.1133 | +0.0364 [+0.0123, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.349 | 0.1026 | 0.0630 | +0.0016 [-0.0087, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0293, +0.1890] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0460, +0.0905] |

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
| 1 | 0.451 (105 of 1873 days never flag) | 206 | 0.600 | 0.408 | 0.0624 | +0.0090 [-0.0007, +0.0184] | -0.0061 [-0.0143, +0.0013] | 0.871 | 0.530 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 202 | 0.568 | 0.391 | 0.0723 | -0.0013 [-0.0097, +0.0065] | -0.0113 [-0.0193, -0.0038] | 0.810 | 0.497 | no |
| 3 | 0.534 (147 of 1871 days never flag) | 187 | 0.522 | 0.385 | 0.0730 | -0.0023 [-0.0123, +0.0056] | -0.0086 [-0.0182, -0.0011] | 0.793 | 0.455 | no |
| 4 | 0.527 (147 of 1870 days never flag) | 164 | 0.471 | 0.396 | 0.0713 | -0.0005 [-0.0080, +0.0065] | -0.0089 [-0.0161, -0.0021] | 0.814 | 0.414 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 162 | 0.442 | 0.377 | 0.0728 | -0.0019 [-0.0081, +0.0038] | -0.0094 [-0.0154, -0.0038] | 0.772 | 0.384 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.448 (climatology 0.457, difference -0.0088 [-0.1372, +0.1229]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0927, ΔBrier vs climatology +0.0368 [+0.0223, +0.0534], realised minus predicted +0.0048 [-0.0292, +0.0415]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.3159 | 0.2720 | +0.0093 [-0.0342, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1987 | 0.0159 | -0.0092 [-0.0324, +0.0093] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0046 | 0.0200 | +0.0000 [-0.0063, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0597 | 0.1165 | +0.0266 [+0.0053, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0055 | 0.0048 | +0.0081 [+0.0061, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1095 | 0.0031 | +0.0105 [+0.0046, +0.0165] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1388 | 0.4146 | +0.0500 [-0.0209, +0.1222] |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.405 | 0.3156 | 0.2474 | +0.0063 [-0.0307, +0.0426] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1062 | 0.1133 | +0.0404 [+0.0198, +0.0623] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.353 | 0.1030 | 0.0630 | +0.0008 [-0.0099, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0190, +0.1808] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0482, +0.0942] |

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
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 3.846 [2.000, 6.280] | 1.923 [0.945, 3.275] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 4.077 [2.182, 6.591] | 2.029 [1.007, 3.448] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.118 [4.438, 11.504] | 3.103 [1.771, 5.322] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 210 | 0.607 | 0.405 | 0.0621 | +0.0093 [-0.0004, +0.0185] | -0.0058 [-0.0142, +0.0019] | 0.873 | 0.535 | no |
| 2 | 0.435 (147 of 1872 days never flag) | 213 | 0.633 | 0.413 | 0.0657 | +0.0054 [-0.0040, +0.0145] | -0.0047 [-0.0140, +0.0038] | 0.841 | 0.561 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 199 | 0.580 | 0.402 | 0.0677 | +0.0030 [-0.0065, +0.0118] | -0.0033 [-0.0128, +0.0054] | 0.825 | 0.511 | yes |
| 4 | 0.522 (147 of 1870 days never flag) | 170 | 0.507 | 0.412 | 0.0652 | +0.0057 [-0.0028, +0.0132] | -0.0028 [-0.0112, +0.0047] | 0.842 | 0.450 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 174 | 0.493 | 0.391 | 0.0665 | +0.0045 [-0.0025, +0.0110] | -0.0031 [-0.0102, +0.0033] | 0.822 | 0.432 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2234 [+0.0692, +0.3738]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0234, +0.0665], realised minus predicted -0.0205 [-0.0526, +0.0125]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.398 | 0.3131 | 0.2720 | +0.0099 [-0.0329, +0.0526] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2026 | 0.0159 | -0.0107 [-0.0349, +0.0084] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0064 | 0.0200 | +0.0027 [-0.0021, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0652 | 0.1165 | +0.0271 [+0.0046, +0.0541] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0061 | 0.0048 | +0.0087 [+0.0069, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1125 | 0.0031 | +0.0096 [+0.0041, +0.0155] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1454 | 0.4146 | 0.0534 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.399 | 0.3152 | 0.2474 | +0.0067 [-0.0311, +0.0421] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1090 | 0.1133 | +0.0364 [+0.0131, +0.0593] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.349 | 0.1026 | 0.0630 | +0.0016 [-0.0090, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0319, +0.1905] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0459, +0.0921] |

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
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.423 [2.625, 6.945] | 1.981 [1.083, 3.292] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.269 [2.433, 6.850] | 1.952 [1.033, 3.300] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.808 [2.052, 6.211] | 1.904 [0.947, 3.303] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.846 [2.130, 6.239] | 1.952 [1.000, 3.350] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.000 [4.368, 11.231] | 3.074 [1.760, 5.143] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.778 (no interval) | 1.861 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 206 | 0.600 | 0.408 | 0.0624 | +0.0090 [-0.0006, +0.0186] | -0.0061 [-0.0141, +0.0017] | 0.871 | 0.530 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 201 | 0.619 | 0.428 | 0.0657 | +0.0054 [-0.0034, +0.0140] | -0.0046 [-0.0133, +0.0035] | 0.837 | 0.552 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 189 | 0.565 | 0.413 | 0.0676 | +0.0031 [-0.0061, +0.0117] | -0.0033 [-0.0123, +0.0051] | 0.823 | 0.501 | yes |
| 4 | 0.615 (147 of 1870 days never flag) | 171 | 0.522 | 0.421 | 0.0655 | +0.0054 [-0.0031, +0.0139] | -0.0031 [-0.0111, +0.0055] | 0.841 | 0.465 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 170 | 0.507 | 0.412 | 0.0652 | +0.0057 [-0.0012, +0.0126] | -0.0018 [-0.0086, +0.0053] | 0.820 | 0.449 | no |

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
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.3159 | 0.2720 | +0.0093 [-0.0343, +0.0511] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1987 | 0.0159 | -0.0092 [-0.0314, +0.0102] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0105, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0046 | 0.0200 | +0.0000 [-0.0058, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0597 | 0.1165 | +0.0266 [+0.0053, +0.0536] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0055 | 0.0048 | +0.0081 [+0.0061, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1095 | 0.0031 | +0.0105 [+0.0044, +0.0166] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1388 | 0.4146 | 0.0500 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.405 | 0.3156 | 0.2474 | +0.0063 [-0.0311, +0.0435] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1062 | 0.1133 | +0.0404 [+0.0188, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.353 | 0.1030 | 0.0630 | +0.0008 [-0.0098, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0160, +0.1802] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0478, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.769] | 0.368 | 6.85 flat / 3.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.269 | 5.23 flat / 2.59 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.769] | 4.692 [3.000, 7.000] | 2.048 [1.261, 3.250] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.962 [3.000, 7.522] | 2.154 [1.196, 3.460] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.611] | 4.462 [2.484, 6.955] | 2.077 [1.055, 3.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 3.962 [2.219, 6.224] | 1.856 [0.921, 3.161] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 4.192 [2.395, 6.636] | 2.106 [1.103, 3.554] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 7.647 [4.952, 11.875] | 3.309 [1.985, 5.501] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.333 (no interval) | 3.500 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 209 | 0.621 | 0.416 | 0.0576 | +0.0139 [+0.0064, +0.0218] | -0.0012 [-0.0075, +0.0047] | 0.850 | 0.551 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 210 | 0.583 | 0.386 | 0.0702 | +0.0009 [-0.0045, +0.0061] | -0.0091 [-0.0150, -0.0036] | 0.767 | 0.508 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 188 | 0.522 | 0.383 | 0.0710 | -0.0003 [-0.0049, +0.0040] | -0.0066 [-0.0115, -0.0020] | 0.718 | 0.455 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 168 | 0.471 | 0.387 | 0.0691 | +0.0017 [-0.0035, +0.0066] | -0.0068 [-0.0118, -0.0018] | 0.760 | 0.412 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 170 | 0.442 | 0.359 | 0.0728 | -0.0019 [-0.0074, +0.0032] | -0.0094 [-0.0153, -0.0039] | 0.709 | 0.379 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.436 (climatology 0.457, difference -0.0210 [-0.1556, +0.1142]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0976, ΔBrier vs climatology +0.0319 [+0.0184, +0.0460], realised minus predicted -0.0125 [-0.0489, +0.0262]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.418 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0687] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2107 | 0.0159 | -0.0087 [-0.0246, +0.0052] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0109 | 0.0200 | +0.0027 [-0.0030, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0639 | 0.1165 | +0.0249 [+0.0060, +0.0489] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0194 | 0.0048 | +0.0082 [+0.0065, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1313 | 0.0031 | +0.0045 [-0.0009, +0.0100] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1305 | 0.4146 | 0.0343 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.414 | 0.2893 | 0.2474 | +0.0308 [+0.0018, +0.0611] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.1097 | 0.1133 | +0.0356 [+0.0138, +0.0591] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.365 | 0.1069 | 0.0630 | +0.0069 [-0.0006, +0.0151] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0322, +0.1868] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0453, +0.0927] |

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
| 1 | 0.451 (105 of 1873 days never flag) | 213 | 0.614 | 0.404 | 0.0579 | +0.0135 [+0.0060, +0.0221] | -0.0016 [-0.0073, +0.0048] | 0.847 | 0.541 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 209 | 0.576 | 0.383 | 0.0705 | +0.0006 [-0.0051, +0.0061] | -0.0094 [-0.0154, -0.0036] | 0.766 | 0.501 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 185 | 0.529 | 0.395 | 0.0703 | +0.0004 [-0.0041, +0.0048] | -0.0059 [-0.0110, -0.0011] | 0.722 | 0.464 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 169 | 0.471 | 0.385 | 0.0702 | +0.0006 [-0.0046, +0.0056] | -0.0079 [-0.0130, -0.0027] | 0.756 | 0.411 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 171 | 0.449 | 0.363 | 0.0728 | -0.0019 [-0.0076, +0.0031] | -0.0094 [-0.0154, -0.0038] | 0.710 | 0.386 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.441 (climatology 0.457, difference -0.0156 [-0.1420, +0.1098]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0962, ΔBrier vs climatology +0.0333 [+0.0197, +0.0483], realised minus predicted -0.0128 [-0.0489, +0.0263]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.2869 | 0.2720 | +0.0353 [+0.0025, +0.0716] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2068 | 0.0159 | -0.0072 [-0.0222, +0.0071] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0091 | 0.0200 | +0.0001 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0584 | 0.1165 | +0.0245 [+0.0054, +0.0483] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0188 | 0.0048 | +0.0077 [+0.0057, +0.0094] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1283 | 0.0031 | +0.0053 [+0.0002, +0.0109] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1240 | 0.4146 | 0.0309 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.402 | 0.2897 | 0.2474 | +0.0305 [+0.0013, +0.0620] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1069 | 0.1133 | +0.0396 [+0.0202, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.353 | 0.1073 | 0.0630 | +0.0062 [-0.0013, +0.0149] |
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
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.773] | 0.299 | 6.31 flat / 3.05 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.300, 0.696] | 0.269 | 5.23 flat / 2.52 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.773] | 4.692 [3.025, 7.154] | 2.048 [1.224, 3.303] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.615 [2.666, 7.351] | 2.125 [1.169, 3.567] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.385 [2.417, 7.100] | 2.058 [1.083, 3.490] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 4.038 [2.250, 6.720] | 2.000 [1.054, 3.450] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 4.269 [2.444, 7.000] | 2.135 [1.129, 3.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.118 [4.500, 11.500] | 3.103 [1.779, 5.413] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 209 | 0.621 | 0.416 | 0.0576 | +0.0139 [+0.0063, +0.0221] | -0.0012 [-0.0072, +0.0050] | 0.850 | 0.551 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 206 | 0.619 | 0.417 | 0.0631 | +0.0080 [+0.0013, +0.0149] | -0.0020 [-0.0090, +0.0049] | 0.807 | 0.549 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 194 | 0.580 | 0.412 | 0.0645 | +0.0062 [+0.0000, +0.0126] | -0.0001 [-0.0064, +0.0061] | 0.770 | 0.514 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 176 | 0.514 | 0.403 | 0.0638 | +0.0071 [+0.0006, +0.0133] | -0.0014 [-0.0077, +0.0048] | 0.791 | 0.454 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 182 | 0.514 | 0.390 | 0.0662 | +0.0047 [-0.0018, +0.0111] | -0.0028 [-0.0095, +0.0041] | 0.775 | 0.450 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2240 [+0.0689, +0.3747]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0870, ΔBrier vs climatology +0.0425 [+0.0231, +0.0642], realised minus predicted -0.0398 [-0.0716, -0.0053]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.418 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0706] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2107 | 0.0159 | -0.0087 [-0.0247, +0.0048] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0109 | 0.0200 | +0.0027 [-0.0022, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0639 | 0.1165 | +0.0249 [+0.0049, +0.0488] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0194 | 0.0048 | +0.0082 [+0.0065, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1313 | 0.0031 | +0.0045 [-0.0009, +0.0101] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1305 | 0.4146 | +0.0343 [-0.0196, +0.0902] |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.414 | 0.2893 | 0.2474 | +0.0308 [+0.0013, +0.0619] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.1097 | 0.1133 | +0.0356 [+0.0139, +0.0587] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.365 | 0.1069 | 0.0630 | +0.0069 [-0.0007, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0311, +0.1868] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0445, +0.0914] |

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
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.577 [2.678, 7.261] | 2.115 [1.177, 3.533] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.423 [2.529, 7.104] | 2.067 [1.120, 3.536] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.077 [2.285, 6.644] | 2.029 [1.086, 3.527] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.192 [2.429, 6.818] | 2.212 [1.240, 3.773] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.000 [4.350, 11.231] | 3.074 [1.795, 5.264] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.667 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 213 | 0.614 | 0.404 | 0.0579 | +0.0135 [+0.0061, +0.0214] | -0.0016 [-0.0073, +0.0043] | 0.847 | 0.541 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 204 | 0.612 | 0.417 | 0.0631 | +0.0080 [+0.0013, +0.0144] | -0.0020 [-0.0086, +0.0044] | 0.803 | 0.543 | no |
| 3 | 0.363 (147 of 1871 days never flag) | 195 | 0.580 | 0.410 | 0.0644 | +0.0063 [+0.0006, +0.0124] | -0.0001 [-0.0058, +0.0064] | 0.766 | 0.513 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 178 | 0.522 | 0.404 | 0.0640 | +0.0068 [+0.0001, +0.0135] | -0.0017 [-0.0086, +0.0054] | 0.791 | 0.461 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 180 | 0.514 | 0.394 | 0.0649 | +0.0060 [-0.0008, +0.0123] | -0.0015 [-0.0085, +0.0054] | 0.775 | 0.452 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.721 (climatology 0.457, difference +0.2638 [+0.0826, +0.4376]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0853, ΔBrier vs climatology +0.0441 [+0.0261, +0.0643], realised minus predicted -0.0384 [-0.0698, -0.0042]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.400 | 0.2869 | 0.2720 | +0.0353 [+0.0035, +0.0676] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2068 | 0.0159 | -0.0072 [-0.0222, +0.0061] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0091 | 0.0200 | +0.0001 [-0.0059, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0584 | 0.1165 | +0.0245 [+0.0051, +0.0482] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0188 | 0.0048 | +0.0077 [+0.0057, +0.0094] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1283 | 0.0031 | +0.0053 [+0.0001, +0.0112] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1240 | 0.4146 | 0.0309 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.402 | 0.2897 | 0.2474 | +0.0305 [+0.0019, +0.0600] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1069 | 0.1133 | +0.0396 [+0.0185, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.353 | 0.1073 | 0.0630 | +0.0062 [-0.0013, +0.0146] |
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
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.778] | 0.280 | 5.96 flat / 2.78 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.615] | 0.269 | 4.88 flat / 2.23 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.778] | 4.808 [3.034, 7.280] | 2.096 [1.229, 3.387] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 4.462 [2.611, 7.000] | 2.058 [1.112, 3.461] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.462 [2.529, 7.063] | 2.058 [1.062, 3.513] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 4.115 [2.391, 6.580] | 1.846 [0.913, 3.219] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.423 [2.514, 7.048] | 2.010 [1.000, 3.514] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.588 [5.000, 11.917] | 3.235 [1.961, 5.375] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 2.889 [1.250, 7.000] | 1.917 [0.633, 5.167] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 212 | 0.621 | 0.410 | 0.0615 | +0.0099 [-0.0012, +0.0199] | -0.0052 [-0.0151, +0.0036] | 0.891 | 0.549 | yes |
| 2 | 0.575 (147 of 1872 days never flag) | 191 | 0.540 | 0.393 | 0.0697 | +0.0014 [-0.0082, +0.0090] | -0.0086 [-0.0178, -0.0009] | 0.840 | 0.473 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 189 | 0.529 | 0.386 | 0.0696 | +0.0011 [-0.0084, +0.0093] | -0.0052 [-0.0143, +0.0030] | 0.843 | 0.462 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 181 | 0.536 | 0.409 | 0.0667 | +0.0041 [-0.0033, +0.0106] | -0.0043 [-0.0116, +0.0021] | 0.841 | 0.474 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 188 | 0.529 | 0.388 | 0.0735 | -0.0026 [-0.0118, +0.0055] | -0.0101 [-0.0192, -0.0020] | 0.803 | 0.463 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.455 (climatology 0.457, difference -0.0025 [-0.1209, +0.1303]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0912, ΔBrier vs climatology +0.0383 [+0.0240, +0.0540], realised minus predicted +0.0232 [-0.0107, +0.0596]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.407 | 0.3157 | 0.2720 | +0.0027 [-0.0475, +0.0470] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1522 | 0.0159 | +0.0048 [-0.0218, +0.0271] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0088 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0028 | 0.0200 | +0.0038 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.667 | 0.0672 | 0.1165 | +0.0232 [+0.0050, +0.0471] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0018 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0686 | 0.0031 | +0.0227 [+0.0165, +0.0291] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0954 | 0.4146 | 0.0308 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.404 | 0.3226 | 0.2474 | +0.0003 [-0.0404, +0.0396] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1077 | 0.1133 | +0.0369 [+0.0150, +0.0607] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.357 | 0.0920 | 0.0630 | +0.0022 [-0.0100, +0.0129] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0346, +0.1904] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0455, +0.0919] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2821 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.765] | 0.269 | 5.73 flat / 2.62 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.269 | 4.73 flat / 2.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.389, 0.765] | 4.692 [2.905, 7.319] | 2.029 [1.162, 3.406] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.526] | 4.423 [2.619, 7.083] | 2.019 [1.067, 3.468] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.346 [2.400, 7.143] | 1.942 [0.968, 3.456] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.038 [2.250, 6.647] | 1.817 [0.870, 3.265] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.538 [2.560, 7.401] | 2.096 [1.065, 3.750] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.588 [4.800, 12.102] | 3.235 [1.928, 5.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.222 [0.833, 5.505] | 1.444 [0.400, 4.250] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 208 | 0.614 | 0.413 | 0.0619 | +0.0095 [-0.0009, +0.0198] | -0.0055 [-0.0154, +0.0031] | 0.891 | 0.544 | no |
| 2 | 0.575 (147 of 1872 days never flag) | 187 | 0.518 | 0.385 | 0.0700 | +0.0011 [-0.0078, +0.0088] | -0.0089 [-0.0176, -0.0010] | 0.838 | 0.452 | no |
| 3 | 0.534 (147 of 1871 days never flag) | 186 | 0.529 | 0.392 | 0.0689 | +0.0018 [-0.0082, +0.0105] | -0.0045 [-0.0141, +0.0038] | 0.846 | 0.464 | no |
| 4 | 0.527 (147 of 1870 days never flag) | 179 | 0.536 | 0.413 | 0.0678 | +0.0030 [-0.0044, +0.0097] | -0.0054 [-0.0131, +0.0015] | 0.835 | 0.476 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 192 | 0.536 | 0.385 | 0.0736 | -0.0026 [-0.0120, +0.0055] | -0.0102 [-0.0193, -0.0023] | 0.804 | 0.468 | no |

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
| regime | 2018-19 | 375 | 102 | 0.755 | 0.410 | 0.3185 | 0.2720 | +0.0021 [-0.0475, +0.0484] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1483 | 0.0159 | +0.0063 [-0.0187, +0.0282] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0090 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0010 | 0.0200 | +0.0012 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.667 | 0.0617 | 0.1165 | +0.0227 [+0.0047, +0.0459] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0088 [+0.0070, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0656 | 0.0031 | +0.0235 [+0.0170, +0.0303] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0888 | 0.4146 | 0.0274 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.410 | 0.3230 | 0.2474 | -0.0000 [-0.0413, +0.0391] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1049 | 0.1133 | +0.0409 [+0.0199, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.361 | 0.0924 | 0.0630 | +0.0015 [-0.0106, +0.0123] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0197, +0.1816] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0481, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2752 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.384, 0.769] | 0.271 | 5.81 flat / 2.66 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.306, 0.696] | 0.269 | 4.81 flat / 2.28 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.384, 0.769] | 4.808 [3.031, 7.308] | 2.096 [1.242, 3.417] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.305, 0.700] | 4.769 [2.905, 7.354] | 2.154 [1.242, 3.511] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.305, 0.700] | 4.423 [2.600, 6.905] | 2.077 [1.152, 3.450] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 3.846 [2.091, 6.278] | 1.894 [0.975, 3.323] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.038 [2.278, 6.534] | 1.990 [1.015, 3.486] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 7.176 [4.533, 11.538] | 2.985 [1.750, 5.091] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 212 | 0.621 | 0.410 | 0.0615 | +0.0099 [-0.0009, +0.0201] | -0.0052 [-0.0155, +0.0041] | 0.891 | 0.549 | yes |
| 2 | 0.435 (147 of 1872 days never flag) | 210 | 0.619 | 0.410 | 0.0637 | +0.0074 [-0.0020, +0.0160] | -0.0027 [-0.0120, +0.0056] | 0.864 | 0.547 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 197 | 0.594 | 0.416 | 0.0644 | +0.0062 [-0.0042, +0.0155] | -0.0001 [-0.0101, +0.0094] | 0.864 | 0.528 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 170 | 0.507 | 0.412 | 0.0623 | +0.0085 [+0.0007, +0.0162] | +0.0001 [-0.0081, +0.0078] | 0.857 | 0.450 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 173 | 0.493 | 0.393 | 0.0678 | +0.0031 [-0.0066, +0.0118] | -0.0044 [-0.0141, +0.0041] | 0.842 | 0.432 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2234 [+0.0651, +0.3719]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0825, ΔBrier vs climatology +0.0470 [+0.0284, +0.0678], realised minus predicted -0.0027 [-0.0341, +0.0314]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.407 | 0.3157 | 0.2720 | +0.0027 [-0.0467, +0.0491] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1522 | 0.0159 | +0.0048 [-0.0228, +0.0272] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0088 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0028 | 0.0200 | +0.0038 [+0.0000, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.667 | 0.0672 | 0.1165 | +0.0232 [+0.0055, +0.0452] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0018 | 0.0048 | +0.0094 [+0.0077, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0686 | 0.0031 | +0.0227 [+0.0166, +0.0290] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0954 | 0.4146 | +0.0308 [-0.0127, +0.0806] |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.404 | 0.3226 | 0.2474 | +0.0003 [-0.0413, +0.0419] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1077 | 0.1133 | +0.0369 [+0.0144, +0.0602] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.357 | 0.0920 | 0.0630 | +0.0022 [-0.0099, +0.0130] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0298, +0.1879] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0459, +0.0920] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2821 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.774] | 0.269 | 5.50 flat / 2.55 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.294, 0.714] | 0.269 | 4.65 flat / 2.26 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.389, 0.774] | 4.692 [2.806, 7.072] | 2.029 [1.145, 3.312] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.304, 0.708] | 4.462 [2.529, 7.000] | 1.990 [1.034, 3.320] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.304, 0.708] | 4.231 [2.294, 6.750] | 1.933 [0.957, 3.294] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.846 [1.971, 6.300] | 1.913 [0.921, 3.369] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.846 [2.037, 6.261] | 1.952 [0.969, 3.375] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.059 [4.294, 11.335] | 2.956 [1.661, 4.980] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 2.556 [1.077, 6.000] | 1.778 [0.573, 4.800] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 208 | 0.614 | 0.413 | 0.0619 | +0.0095 [-0.0012, +0.0194] | -0.0055 [-0.0156, +0.0032] | 0.891 | 0.544 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 201 | 0.612 | 0.423 | 0.0637 | +0.0074 [-0.0016, +0.0162] | -0.0026 [-0.0115, +0.0059] | 0.862 | 0.545 | no |
| 3 | 0.652 (147 of 1871 days never flag) | 190 | 0.580 | 0.421 | 0.0644 | +0.0063 [-0.0043, +0.0154] | -0.0000 [-0.0101, +0.0086] | 0.863 | 0.516 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 172 | 0.522 | 0.419 | 0.0626 | +0.0083 [+0.0001, +0.0160] | -0.0002 [-0.0083, +0.0081] | 0.856 | 0.464 | yes |
| 5 | 0.449 (147 of 1869 days never flag) | 170 | 0.507 | 0.412 | 0.0666 | +0.0043 [-0.0056, +0.0129] | -0.0032 [-0.0126, +0.0057] | 0.843 | 0.449 | no |

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
| regime | 2018-19 | 375 | 102 | 0.755 | 0.410 | 0.3185 | 0.2720 | +0.0021 [-0.0475, +0.0464] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1483 | 0.0159 | +0.0063 [-0.0206, +0.0282] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0090 | 0.0000 | +0.0128 [+0.0111, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0010 | 0.0200 | +0.0012 [-0.0040, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.667 | 0.0617 | 0.1165 | +0.0227 [+0.0055, +0.0456] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0088 [+0.0070, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0656 | 0.0031 | +0.0235 [+0.0172, +0.0300] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0888 | 0.4146 | 0.0274 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.410 | 0.3230 | 0.2474 | -0.0000 [-0.0419, +0.0399] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1049 | 0.1133 | +0.0409 [+0.0197, +0.0646] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.361 | 0.0924 | 0.0630 | +0.0015 [-0.0106, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0191, +0.1811] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0494, +0.0954] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2752 | 0.2213 |

## risk_gbm_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.387, 0.769] | 0.271 | 5.81 flat / 2.81 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.269 | 4.85 flat / 2.29 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.387, 0.769] | 4.654 [2.818, 7.195] | 2.058 [1.160, 3.367] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 4.500 [2.631, 7.058] | 2.067 [1.086, 3.476] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.423 [2.457, 7.154] | 2.038 [1.050, 3.488] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 4.000 [2.208, 6.500] | 1.808 [0.870, 3.191] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.571] | 4.538 [2.522, 7.333] | 2.125 [1.056, 3.662] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.588 [4.874, 11.716] | 3.235 [1.919, 5.304] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 2.444 [0.916, 6.500] | 2.000 [0.609, 5.752] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 207 | 0.614 | 0.415 | 0.0550 | +0.0164 [+0.0088, +0.0252] | +0.0014 [-0.0051, +0.0077] | 0.879 | 0.544 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 192 | 0.540 | 0.391 | 0.0661 | +0.0049 [-0.0012, +0.0110] | -0.0051 [-0.0113, +0.0006] | 0.827 | 0.472 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 188 | 0.529 | 0.388 | 0.0656 | +0.0050 [-0.0003, +0.0105] | -0.0013 [-0.0067, +0.0038] | 0.824 | 0.463 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 178 | 0.536 | 0.416 | 0.0644 | +0.0064 [+0.0008, +0.0116] | -0.0020 [-0.0076, +0.0033] | 0.823 | 0.476 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 191 | 0.529 | 0.382 | 0.0693 | +0.0016 [-0.0040, +0.0070] | -0.0059 [-0.0121, -0.0001] | 0.776 | 0.461 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.444 (climatology 0.457, difference -0.0128 [-0.1269, +0.1107]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0231, +0.0518], realised minus predicted +0.0198 [-0.0150, +0.0562]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.407 | 0.2813 | 0.2720 | +0.0340 [+0.0000, +0.0712] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1752 | 0.0159 | +0.0045 [-0.0151, +0.0211] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0137 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0031 | 0.0200 | +0.0038 [+0.0002, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0648 | 0.1165 | +0.0264 [+0.0066, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0045 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0913 | 0.0031 | +0.0180 [+0.0127, +0.0235] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1027 | 0.4146 | 0.0327 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.410 | 0.2921 | 0.2474 | +0.0295 [-0.0002, +0.0637] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1082 | 0.1133 | +0.0369 [+0.0147, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0894 | 0.0630 | +0.0099 [+0.0020, +0.0186] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0355, +0.1896] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0452, +0.0924] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2479 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.371, 0.773] | 0.271 | 5.81 flat / 2.78 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.621] | 0.269 | 4.77 flat / 2.21 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.371, 0.773] | 4.654 [2.805, 7.150] | 2.058 [1.152, 3.393] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.167, 0.529] | 4.500 [2.551, 7.106] | 2.125 [1.095, 3.583] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.233, 0.615] | 4.308 [2.299, 6.951] | 1.923 [0.901, 3.340] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.038 [2.148, 6.647] | 1.817 [0.828, 3.240] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.233, 0.615] | 4.615 [2.571, 7.412] | 2.173 [1.083, 3.751] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.588 [4.916, 12.143] | 3.235 [1.913, 5.517] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 2.444 [1.000, 6.000] | 1.917 [0.588, 5.322] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 206 | 0.607 | 0.413 | 0.0553 | +0.0161 [+0.0086, +0.0242] | +0.0010 [-0.0055, +0.0073] | 0.877 | 0.537 | no |
| 2 | 0.448 (147 of 1872 days never flag) | 191 | 0.532 | 0.387 | 0.0664 | +0.0046 [-0.0020, +0.0108] | -0.0054 [-0.0119, +0.0005] | 0.825 | 0.465 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 185 | 0.529 | 0.395 | 0.0650 | +0.0057 [+0.0000, +0.0115] | -0.0006 [-0.0062, +0.0048] | 0.824 | 0.464 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 179 | 0.536 | 0.413 | 0.0655 | +0.0053 [-0.0003, +0.0105] | -0.0031 [-0.0090, +0.0025] | 0.820 | 0.476 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 194 | 0.536 | 0.381 | 0.0694 | +0.0016 [-0.0035, +0.0071] | -0.0060 [-0.0116, +0.0001] | 0.777 | 0.467 | no |

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
| regime | 2018-19 | 375 | 102 | 0.755 | 0.410 | 0.2841 | 0.2720 | +0.0334 [+0.0003, +0.0672] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1713 | 0.0159 | +0.0060 [-0.0134, +0.0223] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0142] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0012 [-0.0039, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0593 | 0.1165 | +0.0259 [+0.0066, +0.0513] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0039 | 0.0048 | +0.0088 [+0.0068, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0883 | 0.0031 | +0.0188 [+0.0132, +0.0243] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0961 | 0.4146 | 0.0293 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.410 | 0.2926 | 0.2474 | +0.0291 [+0.0001, +0.0608] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1054 | 0.1133 | +0.0409 [+0.0204, +0.0639] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0898 | 0.0630 | +0.0091 [+0.0013, +0.0172] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0167, +0.1783] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0486, +0.0957] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2410 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.390, 0.774] | 0.269 | 5.50 flat / 2.58 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.296, 0.700] | 0.269 | 4.77 flat / 2.26 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.390, 0.774] | 4.654 [2.851, 7.191] | 2.058 [1.179, 3.364] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.303, 0.708] | 4.615 [2.705, 7.283] | 2.115 [1.183, 3.500] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.303, 0.708] | 4.385 [2.562, 6.955] | 2.058 [1.136, 3.465] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 3.846 [2.107, 6.358] | 1.894 [0.984, 3.325] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.038 [2.260, 6.651] | 1.990 [1.022, 3.523] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.550, 11.400] | 2.985 [1.704, 5.096] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.333 (no interval) | 1.806 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 207 | 0.614 | 0.415 | 0.0550 | +0.0164 [+0.0083, +0.0253] | +0.0014 [-0.0053, +0.0077] | 0.879 | 0.544 | yes |
| 2 | 0.435 (147 of 1872 days never flag) | 206 | 0.619 | 0.417 | 0.0595 | +0.0115 [+0.0044, +0.0192] | +0.0015 [-0.0060, +0.0085] | 0.852 | 0.549 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 196 | 0.594 | 0.418 | 0.0599 | +0.0108 [+0.0037, +0.0174] | +0.0044 [-0.0021, +0.0113] | 0.846 | 0.528 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 171 | 0.514 | 0.415 | 0.0596 | +0.0112 [+0.0049, +0.0181] | +0.0028 [-0.0039, +0.0098] | 0.839 | 0.457 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 174 | 0.500 | 0.397 | 0.0632 | +0.0077 [+0.0009, +0.0141] | +0.0002 [-0.0067, +0.0072] | 0.822 | 0.439 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.681 (climatology 0.457, difference +0.2240 [+0.0717, +0.3694]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0823, ΔBrier vs climatology +0.0472 [+0.0277, +0.0671], realised minus predicted -0.0077 [-0.0394, +0.0252]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.407 | 0.2813 | 0.2720 | +0.0340 [-0.0004, +0.0697] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1752 | 0.0159 | +0.0045 [-0.0145, +0.0204] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0137 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0031 | 0.0200 | +0.0038 [+0.0001, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0648 | 0.1165 | +0.0264 [+0.0071, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0045 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0913 | 0.0031 | +0.0180 [+0.0126, +0.0233] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1027 | 0.4146 | 0.0327 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.410 | 0.2921 | 0.2474 | +0.0295 [-0.0007, +0.0620] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1082 | 0.1133 | +0.0369 [+0.0134, +0.0615] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0894 | 0.0630 | +0.0099 [+0.0021, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0299, +0.1854] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0457, +0.0911] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2479 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.381, 0.774] | 0.269 | 5.50 flat / 2.63 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.304, 0.714] | 0.269 | 4.81 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.381, 0.774] | 4.654 [2.881, 7.002] | 2.058 [1.194, 3.375] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.308, 0.714] | 4.500 [2.655, 7.048] | 2.029 [1.104, 3.445] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.308, 0.714] | 4.346 [2.500, 6.938] | 1.990 [1.045, 3.458] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.885 [2.148, 6.321] | 1.923 [0.974, 3.422] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.962 [2.250, 6.376] | 2.067 [1.095, 3.659] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.059 [4.400, 11.251] | 2.956 [1.726, 5.015] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.556 [1.117, 6.337] | 2.028 [0.725, 5.609] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.451 (105 of 1873 days never flag) | 206 | 0.607 | 0.413 | 0.0553 | +0.0161 [+0.0083, +0.0239] | +0.0010 [-0.0056, +0.0071] | 0.877 | 0.537 | no |
| 2 | 0.448 (147 of 1872 days never flag) | 202 | 0.612 | 0.421 | 0.0595 | +0.0115 [+0.0043, +0.0191] | +0.0015 [-0.0054, +0.0087] | 0.849 | 0.544 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 194 | 0.587 | 0.418 | 0.0599 | +0.0108 [+0.0044, +0.0172] | +0.0045 [-0.0019, +0.0108] | 0.844 | 0.522 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 173 | 0.522 | 0.416 | 0.0599 | +0.0110 [+0.0043, +0.0179] | +0.0025 [-0.0043, +0.0098] | 0.839 | 0.463 | yes |
| 5 | 0.424 (147 of 1869 days never flag) | 173 | 0.507 | 0.405 | 0.0620 | +0.0090 [+0.0021, +0.0160] | +0.0014 [-0.0057, +0.0087] | 0.819 | 0.448 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.457, difference +0.2625 [+0.0816, +0.4334]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0810, ΔBrier vs climatology +0.0485 [+0.0294, +0.0689], realised minus predicted -0.0063 [-0.0373, +0.0258]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.410 | 0.2841 | 0.2720 | +0.0334 [-0.0013, +0.0655] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1713 | 0.0159 | +0.0060 [-0.0118, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0012 [-0.0046, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0593 | 0.1165 | +0.0259 [+0.0064, +0.0506] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0039 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0883 | 0.0031 | +0.0188 [+0.0133, +0.0244] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0961 | 0.4146 | 0.0293 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.410 | 0.2926 | 0.2474 | +0.0291 [-0.0018, +0.0589] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1054 | 0.1133 | +0.0409 [+0.0194, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.361 | 0.0898 | 0.0630 | +0.0091 [+0.0010, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0152, +0.1835] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0488, +0.0963] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2410 | 0.2213 |

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

- h = 1: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.457, difference +0.1155 [-0.0282, +0.2340]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0220 [+0.0108, +0.0330], realised minus predicted +0.0748 [+0.0408, +0.1112]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1074 | 0.2720 | -0.0026 [-0.0240, +0.0179] |
| regime | 2020 | 251 | 4 | 0.250 | 0.043 | 0.0308 | 0.0159 | +0.0252 [+0.0095, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.200 | 0.0059 | 0.0200 | +0.0050 [+0.0008, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.542 | 0.0332 | 0.1165 | +0.0133 [+0.0003, +0.0294] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.077 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0069 | 0.0031 | +0.0280 [+0.0221, +0.0336] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0360 | 0.4146 | 0.0046 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.513 | 0.1081 | 0.2474 | +0.0032 [-0.0160, +0.0217] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1022 | 0.1133 | +0.0282 [+0.0011, +0.0563] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.450 | 0.0126 | 0.0630 | +0.0040 [-0.0012, +0.0088] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3561 | 0.2903 | +0.0892 [+0.0158, +0.1596] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1296 | 0.1461 | +0.0774 [+0.0463, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2020 | 0.2213 |

## risk_logistic+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.480, 0.826] | 0.409 | 7.85 flat / 3.67 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.284 | 6.08 flat / 2.83 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.393, 0.750] | 5.346 [3.621, 7.688] | 2.279 [1.458, 3.456] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.885 [3.138, 7.278] | 2.019 [1.218, 3.182] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 4.577 [2.806, 7.050] | 2.019 [1.172, 3.250] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.231 [2.591, 6.500] | 1.846 [1.058, 3.016] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.645] | 4.962 [3.105, 7.530] | 2.202 [1.329, 3.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.548, 0.957] | 7.294 [4.809, 11.091] | 2.868 [1.750, 4.625] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.889 (no interval) | 5.194 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 238 | 0.707 | 0.416 | 0.0507 | +0.0207 [+0.0134, +0.0281] | +0.0056 [-0.0002, +0.0112] | 0.879 | 0.627 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 221 | 0.676 | 0.425 | 0.0590 | +0.0120 [+0.0064, +0.0180] | +0.0020 [-0.0025, +0.0065] | 0.841 | 0.603 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 202 | 0.601 | 0.411 | 0.0628 | +0.0079 [+0.0015, +0.0142] | +0.0016 [-0.0047, +0.0073] | 0.812 | 0.533 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 180 | 0.507 | 0.389 | 0.0614 | +0.0094 [+0.0034, +0.0152] | +0.0010 [-0.0046, +0.0065] | 0.819 | 0.444 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 212 | 0.601 | 0.392 | 0.0623 | +0.0086 [+0.0037, +0.0137] | +0.0011 [-0.0032, +0.0053] | 0.796 | 0.527 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0285, +0.2530]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0883, ΔBrier vs climatology +0.0412 [+0.0257, +0.0584], realised minus predicted -0.0048 [-0.0344, +0.0272]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.425 | 0.2488 | 0.2720 | +0.0531 [+0.0255, +0.0814] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.1335 | 0.0159 | +0.0089 [-0.0140, +0.0258] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0190 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0359 | 0.0200 | +0.0019 [-0.0049, +0.0081] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.1095 | 0.1165 | +0.0252 [+0.0011, +0.0534] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0240 | 0.0048 | +0.0079 [+0.0056, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0715 | 0.0031 | +0.0206 [+0.0145, +0.0260] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2203 | 0.4146 | 0.0739 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.769 | 0.415 | 0.2543 | 0.2474 | +0.0441 [+0.0164, +0.0687] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1115 | 0.1133 | +0.0333 [+0.0061, +0.0619] |
| day_type | ordinary | 1603 | 101 | 0.703 | 0.376 | 0.0861 | 0.0630 | +0.0151 [+0.0083, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3561 | 0.2903 | +0.0892 [+0.0129, +0.1670] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1296 | 0.1461 | +0.0774 [+0.0469, +0.1125] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3400 | 0.2213 |

## risk_logistic+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.520, 0.857] | 0.418 | 8.00 flat / 4.12 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.353, 0.714] | 0.291 | 6.19 flat / 3.20 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.645] | 3.692 [2.600, 5.185] | 1.788 [1.188, 2.688] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.467] | 3.885 [2.604, 5.653] | 1.596 [1.059, 2.382] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.462] | 3.462 [2.193, 5.250] | 1.577 [0.994, 2.464] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.148, 0.462] | 3.808 [2.589, 5.556] | 1.894 [1.242, 2.881] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 4.423 [2.967, 6.474] | 2.192 [1.484, 3.294] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.765 [4.545, 10.167] | 2.750 [1.815, 4.173] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.333 (no interval) | 6.694 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.105 (105 of 1873 days never flag) | 176 | 0.571 | 0.455 | 0.0525 | +0.0189 [+0.0122, +0.0264] | +0.0038 [-0.0018, +0.0096] | 0.801 | 0.516 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 177 | 0.547 | 0.429 | 0.0613 | +0.0098 [+0.0039, +0.0157] | -0.0002 [-0.0051, +0.0047] | 0.752 | 0.488 | no |
| 3 | 0.128 (147 of 1871 days never flag) | 159 | 0.500 | 0.434 | 0.0628 | +0.0079 [+0.0011, +0.0144] | +0.0015 [-0.0048, +0.0076] | 0.746 | 0.448 | no |
| 4 | 0.107 (147 of 1870 days never flag) | 159 | 0.435 | 0.377 | 0.0623 | +0.0086 [+0.0029, +0.0143] | +0.0001 [-0.0053, +0.0056] | 0.758 | 0.378 | no |
| 5 | 0.103 (147 of 1869 days never flag) | 187 | 0.522 | 0.385 | 0.0630 | +0.0079 [+0.0025, +0.0134] | +0.0004 [-0.0044, +0.0050] | 0.743 | 0.455 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.457, difference +0.1358 [+0.0033, +0.2420]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0908, ΔBrier vs climatology +0.0386 [+0.0219, +0.0543], realised minus predicted +0.0450 [+0.0160, +0.0733]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.504 | 0.1791 | 0.2720 | +0.0375 [+0.0124, +0.0643] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.0384 | 0.0159 | +0.0179 [-0.0056, +0.0369] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.167 | 0.0183 | 0.0200 | +0.0020 [-0.0055, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.552 | 0.0845 | 0.1165 | +0.0244 [+0.0024, +0.0530] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.125 | 0.0099 | 0.0048 | +0.0082 [+0.0057, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0119 | 0.0031 | +0.0266 [+0.0198, +0.0330] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.1914 | 0.4146 | 0.0719 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.477 | 0.1768 | 0.2474 | +0.0324 [+0.0082, +0.0578] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1060 | 0.1133 | +0.0339 [+0.0051, +0.0632] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.426 | 0.0419 | 0.0630 | +0.0129 [+0.0068, +0.0197] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3561 | 0.2903 | +0.0892 [+0.0134, +0.1635] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1296 | 0.1461 | +0.0774 [+0.0481, +0.1152] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3840 | 0.2213 |

## risk_logistic+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.481, 0.818] | 0.385 | 7.19 flat / 3.39 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.677] | 0.271 | 5.85 flat / 2.70 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 4.885 [3.185, 7.313] | 2.154 [1.359, 3.389] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.423 [2.677, 6.875] | 1.827 [1.023, 3.011] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.263, 0.588] | 4.192 [2.500, 6.609] | 1.817 [1.027, 3.034] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.462 [2.724, 6.833] | 2.077 [1.180, 3.348] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.640] | 5.192 [3.269, 7.813] | 2.337 [1.417, 3.640] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.118 [5.350, 12.502] | 3.471 [2.083, 5.700] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.167, 0.728] | 5.444 [3.000, 11.432] | 3.250 [1.678, 7.500] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 220 | 0.664 | 0.423 | 0.0508 | +0.0206 [+0.0139, +0.0274] | +0.0055 [+0.0005, +0.0110] | 0.877 | 0.591 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 202 | 0.626 | 0.431 | 0.0580 | +0.0130 [+0.0083, +0.0182] | +0.0030 [-0.0016, +0.0079] | 0.830 | 0.560 | no |
| 3 | 0.248 (147 of 1871 days never flag) | 188 | 0.572 | 0.420 | 0.0613 | +0.0094 [+0.0028, +0.0152] | +0.0031 [-0.0034, +0.0094] | 0.804 | 0.510 | yes |
| 4 | 0.222 (147 of 1870 days never flag) | 179 | 0.457 | 0.352 | 0.0602 | +0.0106 [+0.0059, +0.0156] | +0.0022 [-0.0029, +0.0077] | 0.812 | 0.390 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 214 | 0.572 | 0.369 | 0.0606 | +0.0103 [+0.0059, +0.0144] | +0.0028 [-0.0016, +0.0070] | 0.790 | 0.494 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.597 (climatology 0.457, difference +0.1399 [+0.0283, +0.2419]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0894, ΔBrier vs climatology +0.0401 [+0.0252, +0.0567], realised minus predicted +0.0047 [-0.0271, +0.0378]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.765 | 0.422 | 0.2317 | 0.2720 | +0.0475 [+0.0222, +0.0737] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1198 | 0.0159 | +0.0146 [-0.0046, +0.0285] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0133 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0281 | 0.0200 | +0.0042 [-0.0000, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.619 | 0.0944 | 0.1165 | +0.0246 [+0.0036, +0.0502] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0199 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0613 | 0.0031 | +0.0228 [+0.0170, +0.0281] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.625 | 0.1770 | 0.4146 | 0.0637 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.422 | 0.2366 | 0.2474 | +0.0416 [+0.0178, +0.0647] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1101 | 0.1133 | +0.0325 [+0.0041, +0.0599] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.384 | 0.0752 | 0.0630 | +0.0150 [+0.0090, +0.0217] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3561 | 0.2903 | +0.0892 [+0.0140, +0.1626] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1296 | 0.1461 | +0.0774 [+0.0454, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2503 | 0.2213 |

## risk_logistic+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.818] | 0.389 | 7.54 flat / 3.48 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 5.77 flat / 2.63 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.394, 0.759] | 5.308 [3.600, 7.707] | 2.269 [1.464, 3.517] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.808 [3.074, 7.308] | 1.990 [1.210, 3.177] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 4.423 [2.708, 6.920] | 1.942 [1.155, 3.217] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.077 [2.444, 6.417] | 1.760 [1.000, 2.914] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.846 [3.000, 7.455] | 2.125 [1.278, 3.386] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.294 [4.759, 11.417] | 2.868 [1.714, 4.806] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.000 (no interval) | 4.639 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 237 | 0.707 | 0.418 | 0.0500 | +0.0214 [+0.0139, +0.0293] | +0.0063 [+0.0008, +0.0121] | 0.904 | 0.628 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 219 | 0.676 | 0.429 | 0.0583 | +0.0128 [+0.0072, +0.0183] | +0.0028 [-0.0016, +0.0077] | 0.878 | 0.604 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 198 | 0.601 | 0.419 | 0.0611 | +0.0096 [+0.0034, +0.0160] | +0.0033 [-0.0030, +0.0092] | 0.861 | 0.535 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 177 | 0.514 | 0.401 | 0.0601 | +0.0107 [+0.0050, +0.0165] | +0.0023 [-0.0033, +0.0075] | 0.862 | 0.453 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 209 | 0.601 | 0.397 | 0.0613 | +0.0096 [+0.0047, +0.0144] | +0.0021 [-0.0022, +0.0063] | 0.850 | 0.529 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0282, +0.2427]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0427 [+0.0269, +0.0596], realised minus predicted +0.0202 [-0.0104, +0.0514]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.425 | 0.2488 | 0.2720 | +0.0531 [+0.0259, +0.0821] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.1335 | 0.0159 | +0.0089 [-0.0128, +0.0260] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0049 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0008, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.0959 | 0.1165 | +0.0261 [+0.0025, +0.0547] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0715 | 0.0031 | +0.0206 [+0.0146, +0.0260] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2203 | 0.4146 | 0.0739 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.769 | 0.415 | 0.2543 | 0.2474 | +0.0441 [+0.0179, +0.0710] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1095 | 0.1133 | +0.0334 [+0.0058, +0.0639] |
| day_type | ordinary | 1603 | 101 | 0.703 | 0.378 | 0.0729 | 0.0630 | +0.0158 [+0.0092, +0.0233] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3561 | 0.2903 | +0.0892 [+0.0150, +0.1628] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1296 | 0.1461 | +0.0774 [+0.0471, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3400 | 0.2213 |

## risk_logistic+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.852] | 0.389 | 7.54 flat / 3.65 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.368, 0.714] | 0.282 | 6.04 flat / 2.89 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.759] | 4.769 [3.100, 7.150] | 2.163 [1.361, 3.395] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.645] | 5.154 [3.416, 7.685] | 2.240 [1.389, 3.513] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 4.231 [2.526, 6.706] | 1.875 [1.080, 3.111] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.346 [2.730, 6.750] | 1.971 [1.190, 3.183] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.192 [3.323, 7.819] | 2.356 [1.483, 3.713] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.571, 11.335] | 2.912 [1.687, 4.979] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 8.222 [5.143, 16.200] | 5.056 [2.917, 11.375] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 213 | 0.636 | 0.418 | 0.0513 | +0.0202 [+0.0150, +0.0256] | +0.0051 [-0.0003, +0.0104] | 0.891 | 0.564 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 231 | 0.698 | 0.420 | 0.0593 | +0.0118 [+0.0075, +0.0162] | +0.0018 [-0.0030, +0.0066] | 0.845 | 0.621 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 188 | 0.565 | 0.415 | 0.0620 | +0.0087 [+0.0031, +0.0142] | +0.0024 [-0.0036, +0.0081] | 0.815 | 0.502 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 186 | 0.529 | 0.392 | 0.0612 | +0.0096 [+0.0053, +0.0138] | +0.0012 [-0.0039, +0.0063] | 0.827 | 0.464 | no |
| 5 | 0.123 (147 of 1869 days never flag) | 219 | 0.609 | 0.384 | 0.0617 | +0.0092 [+0.0049, +0.0131] | +0.0017 [-0.0034, +0.0061] | 0.808 | 0.531 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.457, difference +0.1367 [+0.0227, +0.2248]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0934, ΔBrier vs climatology +0.0361 [+0.0231, +0.0490], realised minus predicted +0.0364 [+0.0043, +0.0713]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.426 | 0.1781 | 0.2720 | +0.0386 [+0.0216, +0.0559] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0821 | 0.0159 | +0.0221 [+0.0043, +0.0353] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0098 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0209 | 0.0200 | +0.0043 [-0.0003, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0714 | 0.1165 | +0.0258 [+0.0050, +0.0523] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0136 | 0.0048 | +0.0089 [+0.0069, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0392 | 0.0031 | +0.0262 [+0.0201, +0.0316] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1281 | 0.4146 | 0.0606 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.424 | 0.1812 | 0.2474 | +0.0373 [+0.0206, +0.0543] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1069 | 0.1133 | +0.0311 [+0.0043, +0.0591] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.378 | 0.0494 | 0.0630 | +0.0146 [+0.0106, +0.0191] |
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
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.760] | 0.293 | 6.19 flat / 2.94 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.640] | 0.269 | 5.12 flat / 2.47 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.846 [3.000, 7.400] | 2.077 [1.202, 3.310] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.231 [2.517, 6.600] | 1.750 [0.961, 2.833] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.524] | 3.846 [2.182, 6.087] | 1.683 [0.898, 2.792] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 3.423 [1.903, 5.563] | 1.567 [0.817, 2.625] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.480, 7.263] | 2.144 [1.104, 3.698] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.529 [4.904, 11.468] | 3.029 [1.783, 5.001] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.667 [1.538, 9.000] | 2.778 [1.050, 7.127] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 209 | 0.593 | 0.397 | 0.0635 | +0.0079 [-0.0023, +0.0181] | -0.0072 [-0.0166, +0.0017] | 0.868 | 0.520 | no |
| 2 | 0.518 (147 of 1872 days never flag) | 193 | 0.597 | 0.430 | 0.0705 | +0.0005 [-0.0092, +0.0092] | -0.0095 [-0.0189, -0.0013] | 0.824 | 0.534 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 171 | 0.514 | 0.415 | 0.0748 | -0.0041 [-0.0143, +0.0054] | -0.0104 [-0.0204, -0.0010] | 0.796 | 0.457 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 149 | 0.435 | 0.403 | 0.0722 | -0.0014 [-0.0101, +0.0063] | -0.0098 [-0.0186, -0.0017] | 0.814 | 0.383 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 192 | 0.543 | 0.391 | 0.0722 | -0.0012 [-0.0084, +0.0053] | -0.0088 [-0.0155, -0.0021] | 0.778 | 0.476 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.584 (climatology 0.457, difference +0.1273 [+0.0186, +0.2218]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0951, ΔBrier vs climatology +0.0344 [+0.0175, +0.0519], realised minus predicted -0.0130 [-0.0467, +0.0245]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.401 | 0.3233 | 0.2720 | +0.0088 [-0.0363, +0.0522] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2080 | 0.0159 | -0.0185 [-0.0417, +0.0021] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0102 | 0.0200 | +0.0038 [-0.0015, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0630 | 0.1165 | +0.0245 [+0.0037, +0.0501] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0084 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1123 | 0.0031 | +0.0086 [+0.0034, +0.0139] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1462 | 0.4146 | 0.0581 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.394 | 0.3227 | 0.2474 | +0.0018 [-0.0364, +0.0408] |
| day_type | month_end | 150 | 17 | 0.529 | 0.529 | 0.1129 | 0.1133 | +0.0307 [+0.0041, +0.0593] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.353 | 0.1024 | 0.0630 | +0.0003 [-0.0099, +0.0103] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0155, +0.1627] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1296 | 0.1461 | +0.0774 [+0.0473, +0.1139] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2899 | 0.2213 |

## risk_logistic+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.278 | 5.92 flat / 2.81 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.640] | 0.269 | 4.88 flat / 2.35 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.692 [2.842, 7.114] | 2.038 [1.134, 3.250] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.692 [2.788, 7.273] | 2.048 [1.092, 3.388] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.654 [1.938, 5.870] | 1.490 [0.741, 2.531] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.467] | 3.000 [1.478, 5.000] | 1.279 [0.571, 2.296] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.610] | 4.615 [2.643, 7.353] | 2.231 [1.169, 3.804] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.471 [4.761, 11.701] | 3.059 [1.750, 5.100] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 208 | 0.614 | 0.413 | 0.0633 | +0.0081 [-0.0019, +0.0183] | -0.0070 [-0.0161, +0.0017] | 0.869 | 0.544 | no |
| 2 | 0.543 (147 of 1872 days never flag) | 203 | 0.583 | 0.399 | 0.0694 | +0.0017 [-0.0077, +0.0101] | -0.0083 [-0.0166, -0.0008] | 0.825 | 0.512 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 167 | 0.522 | 0.431 | 0.0723 | -0.0016 [-0.0116, +0.0072] | -0.0079 [-0.0179, +0.0005] | 0.797 | 0.467 | yes |
| 4 | 0.649 (147 of 1870 days never flag) | 138 | 0.435 | 0.435 | 0.0705 | +0.0003 [-0.0075, +0.0077] | -0.0082 [-0.0161, -0.0004] | 0.816 | 0.390 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 195 | 0.543 | 0.385 | 0.0724 | -0.0015 [-0.0088, +0.0056] | -0.0090 [-0.0165, -0.0019] | 0.783 | 0.474 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.553 (climatology 0.457, difference +0.0961 [+0.0019, +0.1765]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0927, ΔBrier vs climatology +0.0368 [+0.0213, +0.0535], realised minus predicted -0.0127 [-0.0449, +0.0221]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.409 | 0.3261 | 0.2720 | +0.0095 [-0.0359, +0.0536] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2055 | 0.0159 | -0.0171 [-0.0401, +0.0028] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0101 | 0.0200 | +0.0039 [-0.0011, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0606 | 0.1165 | +0.0238 [+0.0036, +0.0482] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0083 | 0.0048 | +0.0085 [+0.0065, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1106 | 0.0031 | +0.0091 [+0.0035, +0.0152] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1450 | 0.4146 | 0.0566 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.408 | 0.3238 | 0.2474 | +0.0024 [-0.0364, +0.0413] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1115 | 0.1133 | +0.0330 [+0.0058, +0.0603] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.365 | 0.1027 | 0.0630 | +0.0004 [-0.0103, +0.0105] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0144, +0.1657] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1246 | 0.1461 | +0.0764 [+0.0442, +0.1162] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.394, 0.760] | 0.291 | 6.15 flat / 2.96 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.360, 0.714] | 0.269 | 5.00 flat / 2.42 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 4.846 [3.000, 7.392] | 2.077 [1.215, 3.369] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.062, 0.350] | 3.654 [1.909, 6.120] | 1.712 [0.842, 3.024] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.519] | 4.000 [2.383, 6.312] | 2.000 [1.120, 3.280] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.259, 0.594] | 3.731 [2.125, 5.890] | 1.567 [0.847, 2.618] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.571] | 3.346 [1.815, 5.500] | 1.481 [0.760, 2.548] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 8.000 [5.300, 12.154] | 3.485 [2.150, 5.667] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 2.667 [1.200, 6.200] | 1.972 [0.750, 5.000] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 209 | 0.593 | 0.397 | 0.0635 | +0.0079 [-0.0026, +0.0174] | -0.0072 [-0.0168, +0.0013] | 0.868 | 0.520 | no |
| 2 | 0.864 (147 of 1872 days never flag) | 156 | 0.439 | 0.391 | 0.0667 | +0.0044 [-0.0049, +0.0135] | -0.0056 [-0.0147, +0.0028] | 0.837 | 0.384 | yes |
| 3 | 0.415 (147 of 1871 days never flag) | 170 | 0.478 | 0.388 | 0.0681 | +0.0026 [-0.0073, +0.0116] | -0.0037 [-0.0136, +0.0052] | 0.824 | 0.418 | yes |
| 4 | 0.683 (126 of 1870 days never flag) | 167 | 0.507 | 0.419 | 0.0659 | +0.0050 [-0.0030, +0.0126] | -0.0035 [-0.0112, +0.0041] | 0.840 | 0.451 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 152 | 0.471 | 0.428 | 0.0653 | +0.0057 [-0.0015, +0.0124] | -0.0019 [-0.0087, +0.0049] | 0.827 | 0.421 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.457, difference +0.2431 [+0.0700, +0.3883]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0821, ΔBrier vs climatology +0.0474 [+0.0291, +0.0668], realised minus predicted -0.0306 [-0.0602, -0.0024]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.401 | 0.3233 | 0.2720 | +0.0088 [-0.0379, +0.0515] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2080 | 0.0159 | -0.0185 [-0.0436, +0.0024] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0102 | 0.0200 | +0.0038 [-0.0017, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0630 | 0.1165 | +0.0245 [+0.0035, +0.0513] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0084 | 0.0048 | +0.0084 [+0.0065, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1123 | 0.0031 | +0.0086 [+0.0031, +0.0140] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1462 | 0.4146 | 0.0581 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.394 | 0.3227 | 0.2474 | +0.0018 [-0.0390, +0.0385] |
| day_type | month_end | 150 | 17 | 0.529 | 0.529 | 0.1129 | 0.1133 | +0.0307 [+0.0035, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.353 | 0.1024 | 0.0630 | +0.0003 [-0.0108, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0148, +0.1625] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1296 | 0.1461 | +0.0774 [+0.0470, +0.1154] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2899 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.806] | 0.269 | 5.65 flat / 2.68 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.321, 0.667] | 0.258 | 4.50 flat / 2.26 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.654] | 4.692 [2.897, 7.168] | 2.038 [1.156, 3.338] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.171, 0.542] | 4.154 [2.280, 6.714] | 1.856 [0.954, 3.199] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.484] | 3.346 [1.784, 5.501] | 1.558 [0.800, 2.685] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.560] | 3.769 [2.045, 6.188] | 1.808 [0.907, 3.185] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.077 [1.500, 5.167] | 1.413 [0.669, 2.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.941 [4.333, 10.714] | 2.838 [1.658, 4.626] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.626] | 3.222 [1.583, 8.000] | 2.389 [1.019, 6.375] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 208 | 0.614 | 0.413 | 0.0633 | +0.0081 [-0.0015, +0.0184] | -0.0070 [-0.0159, +0.0016] | 0.869 | 0.544 | no |
| 2 | 0.875 (147 of 1872 days never flag) | 183 | 0.540 | 0.410 | 0.0666 | +0.0044 [-0.0050, +0.0134] | -0.0056 [-0.0150, +0.0033] | 0.840 | 0.477 | yes |
| 3 | 0.421 (147 of 1871 days never flag) | 151 | 0.464 | 0.424 | 0.0677 | +0.0030 [-0.0071, +0.0118] | -0.0033 [-0.0130, +0.0054] | 0.827 | 0.414 | yes |
| 4 | 0.786 (126 of 1870 days never flag) | 164 | 0.478 | 0.402 | 0.0657 | +0.0051 [-0.0033, +0.0131] | -0.0033 [-0.0118, +0.0046] | 0.841 | 0.422 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 141 | 0.442 | 0.433 | 0.0654 | +0.0055 [-0.0019, +0.0124] | -0.0020 [-0.0088, +0.0049] | 0.826 | 0.396 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2500 [+0.0821, +0.3936]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0815, ΔBrier vs climatology +0.0480 [+0.0295, +0.0676], realised minus predicted -0.0306 [-0.0597, +0.0007]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.409 | 0.3261 | 0.2720 | +0.0095 [-0.0332, +0.0536] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2055 | 0.0159 | -0.0171 [-0.0404, +0.0029] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0101 | 0.0200 | +0.0039 [-0.0014, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0606 | 0.1165 | +0.0238 [+0.0034, +0.0481] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0083 | 0.0048 | +0.0085 [+0.0066, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1106 | 0.0031 | +0.0091 [+0.0033, +0.0149] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1450 | 0.4146 | 0.0566 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.408 | 0.3238 | 0.2474 | +0.0024 [-0.0344, +0.0426] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1115 | 0.1133 | +0.0330 [+0.0064, +0.0614] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.365 | 0.1027 | 0.0630 | +0.0004 [-0.0094, +0.0106] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0134, +0.1624] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1246 | 0.1461 | +0.0764 [+0.0436, +0.1134] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.351 | 6.58 flat / 3.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.650] | 0.269 | 4.69 flat / 2.12 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.316, 0.677] | 5.308 [3.485, 7.965] | 2.394 [1.500, 3.772] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.385 [2.625, 6.826] | 1.808 [1.026, 2.955] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 3.885 [2.160, 6.227] | 1.702 [0.930, 2.863] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.516] | 3.423 [1.904, 5.615] | 1.558 [0.823, 2.714] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.154 [2.357, 6.656] | 1.817 [1.030, 3.046] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.471 [4.956, 11.600] | 2.971 [1.819, 5.036] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.889 [2.667, 10.000] | 3.361 [1.670, 7.458] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 228 | 0.643 | 0.395 | 0.0590 | +0.0124 [+0.0045, +0.0209] | -0.0027 [-0.0094, +0.0043] | 0.840 | 0.563 | yes |
| 2 | 0.489 (147 of 1872 days never flag) | 198 | 0.604 | 0.424 | 0.0687 | +0.0024 [-0.0040, +0.0088] | -0.0076 [-0.0139, -0.0012] | 0.781 | 0.539 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 174 | 0.529 | 0.420 | 0.0721 | -0.0015 [-0.0080, +0.0051] | -0.0078 [-0.0149, -0.0010] | 0.730 | 0.471 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 150 | 0.442 | 0.407 | 0.0712 | -0.0003 [-0.0067, +0.0060] | -0.0088 [-0.0158, -0.0018] | 0.752 | 0.391 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 184 | 0.551 | 0.413 | 0.0722 | -0.0013 [-0.0075, +0.0047] | -0.0088 [-0.0154, -0.0024] | 0.721 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [+0.0107, +0.2165]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0981, ΔBrier vs climatology +0.0314 [+0.0164, +0.0485], realised minus predicted -0.0298 [-0.0634, +0.0079]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.401 | 0.2943 | 0.2720 | +0.0349 [+0.0022, +0.0700] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.2161 | 0.0159 | -0.0164 [-0.0369, -0.0002] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0089, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0147 | 0.0200 | +0.0039 [-0.0015, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0617 | 0.1165 | +0.0224 [+0.0038, +0.0467] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0217 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1310 | 0.0031 | +0.0034 [-0.0011, +0.0082] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1313 | 0.4146 | +0.0390 [-0.0215, +0.0970] |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.394 | 0.2967 | 0.2474 | +0.0260 [-0.0047, +0.0582] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1136 | 0.1133 | +0.0299 [+0.0021, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.352 | 0.1067 | 0.0630 | +0.0057 [-0.0015, +0.0140] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0151, +0.1614] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0461, +0.1146] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2856 | 0.2213 |

## risk_logistic+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.358 | 6.69 flat / 3.28 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.645] | 0.269 | 5.31 flat / 2.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.682] | 4.615 [2.926, 7.091] | 2.010 [1.194, 3.211] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.308 [2.566, 6.875] | 1.760 [0.987, 2.926] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.654 [2.000, 6.096] | 1.500 [0.757, 2.613] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.471] | 3.346 [1.769, 5.537] | 1.481 [0.741, 2.605] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.808 [2.788, 7.667] | 2.337 [1.250, 3.941] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.471 [4.800, 11.668] | 3.059 [1.793, 5.135] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.222 [2.733, 11.750] | 3.694 [1.704, 9.064] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (126 of 1873 days never flag) | 210 | 0.643 | 0.429 | 0.0588 | +0.0127 [+0.0049, +0.0211] | -0.0024 [-0.0093, +0.0047] | 0.839 | 0.574 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 195 | 0.597 | 0.426 | 0.0675 | +0.0035 [-0.0027, +0.0097] | -0.0065 [-0.0124, -0.0005] | 0.781 | 0.532 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 168 | 0.529 | 0.435 | 0.0697 | +0.0010 [-0.0046, +0.0069] | -0.0053 [-0.0108, +0.0006] | 0.731 | 0.474 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 148 | 0.442 | 0.412 | 0.0695 | +0.0013 [-0.0043, +0.0074] | -0.0071 [-0.0132, -0.0008] | 0.753 | 0.392 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 201 | 0.551 | 0.378 | 0.0724 | -0.0015 [-0.0082, +0.0050] | -0.0090 [-0.0162, -0.0022] | 0.727 | 0.479 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.553 (climatology 0.457, difference +0.0961 [-0.0024, +0.1802]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0957, ΔBrier vs climatology +0.0338 [+0.0191, +0.0499], realised minus predicted -0.0296 [-0.0637, +0.0060]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.434 | 0.2972 | 0.2720 | +0.0356 [+0.0024, +0.0708] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2136 | 0.0159 | -0.0150 [-0.0348, +0.0013] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0146 | 0.0200 | +0.0040 [-0.0013, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0594 | 0.1165 | +0.0217 [+0.0035, +0.0436] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0216 | 0.0048 | +0.0080 [+0.0062, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1294 | 0.0031 | +0.0040 [-0.0012, +0.0096] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1301 | 0.4146 | 0.0375 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.428 | 0.2979 | 0.2474 | +0.0266 [-0.0041, +0.0573] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1123 | 0.1133 | +0.0322 [+0.0066, +0.0593] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.388 | 0.1070 | 0.0630 | +0.0058 [-0.0018, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0181, +0.1607] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0450, +0.1158] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.762] | 0.363 | 6.77 flat / 3.28 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.375, 0.706] | 0.269 | 5.35 flat / 2.61 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.682] | 5.308 [3.444, 7.900] | 2.394 [1.477, 3.765] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.129, 0.424] | 4.077 [2.304, 6.526] | 2.029 [1.090, 3.382] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.187, 0.517] | 3.808 [2.161, 6.000] | 1.846 [0.989, 3.115] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.115 [2.444, 6.421] | 1.808 [1.050, 2.925] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.226, 0.562] | 3.731 [2.107, 5.959] | 1.721 [0.944, 2.869] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.000 [5.348, 12.126] | 3.485 [2.150, 5.635] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.444 [2.453, 10.000] | 2.889 [1.479, 7.002] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 228 | 0.643 | 0.395 | 0.0590 | +0.0124 [+0.0050, +0.0209] | -0.0027 [-0.0093, +0.0044] | 0.840 | 0.563 | no |
| 2 | 0.864 (147 of 1872 days never flag) | 170 | 0.460 | 0.376 | 0.0640 | +0.0070 [+0.0004, +0.0137] | -0.0030 [-0.0100, +0.0041] | 0.803 | 0.399 | yes |
| 3 | 0.415 (147 of 1871 days never flag) | 165 | 0.478 | 0.400 | 0.0649 | +0.0058 [-0.0001, +0.0116] | -0.0005 [-0.0067, +0.0057] | 0.765 | 0.421 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 180 | 0.529 | 0.406 | 0.0645 | +0.0064 [+0.0001, +0.0123] | -0.0021 [-0.0090, +0.0045] | 0.786 | 0.467 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 164 | 0.486 | 0.409 | 0.0650 | +0.0060 [-0.0000, +0.0120] | -0.0016 [-0.0077, +0.0052] | 0.780 | 0.429 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.457, difference +0.2437 [+0.0712, +0.3893]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0839, ΔBrier vs climatology +0.0456 [+0.0265, +0.0646], realised minus predicted -0.0489 [-0.0799, -0.0172]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.401 | 0.2943 | 0.2720 | +0.0349 [+0.0036, +0.0675] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.2161 | 0.0159 | -0.0164 [-0.0354, -0.0001] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0147 | 0.0200 | +0.0039 [-0.0015, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0617 | 0.1165 | +0.0224 [+0.0036, +0.0463] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0217 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1310 | 0.0031 | +0.0034 [-0.0012, +0.0084] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1313 | 0.4146 | +0.0390 [-0.0214, +0.1015] |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.394 | 0.2967 | 0.2474 | +0.0260 [-0.0033, +0.0581] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1136 | 0.1133 | +0.0299 [+0.0035, +0.0574] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.352 | 0.1067 | 0.0630 | +0.0057 [-0.0014, +0.0137] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0156, +0.1616] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0475, +0.1137] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2856 | 0.2213 |

## risk_logistic+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.288 | 6.12 flat / 2.88 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 4.69 flat / 2.34 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.310, 0.682] | 4.615 [2.879, 6.948] | 2.010 [1.208, 3.147] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.565] | 4.577 [2.636, 7.174] | 2.154 [1.192, 3.524] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.476] | 3.077 [1.529, 5.168] | 1.375 [0.653, 2.417] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 4.115 [2.333, 6.524] | 2.010 [1.078, 3.395] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 3.385 [1.818, 5.524] | 1.577 [0.815, 2.663] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.941 [4.263, 10.909] | 2.838 [1.631, 4.767] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.556 [2.417, 9.667] | 2.944 [1.386, 6.941] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (126 of 1873 days never flag) | 210 | 0.643 | 0.429 | 0.0588 | +0.0127 [+0.0048, +0.0207] | -0.0024 [-0.0095, +0.0043] | 0.839 | 0.574 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 196 | 0.554 | 0.393 | 0.0640 | +0.0071 [+0.0002, +0.0137] | -0.0029 [-0.0099, +0.0040] | 0.806 | 0.485 | yes |
| 3 | 0.421 (147 of 1871 days never flag) | 144 | 0.464 | 0.444 | 0.0645 | +0.0062 [+0.0008, +0.0119] | -0.0001 [-0.0058, +0.0059] | 0.768 | 0.418 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 175 | 0.493 | 0.389 | 0.0643 | +0.0065 [+0.0004, +0.0128] | -0.0019 [-0.0086, +0.0049] | 0.787 | 0.431 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 151 | 0.457 | 0.417 | 0.0651 | +0.0058 [-0.0005, +0.0124] | -0.0017 [-0.0084, +0.0053] | 0.778 | 0.406 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2500 [+0.0925, +0.3901]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0832, ΔBrier vs climatology +0.0462 [+0.0279, +0.0655], realised minus predicted -0.0489 [-0.0807, -0.0179]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.434 | 0.2972 | 0.2720 | +0.0356 [+0.0019, +0.0681] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.2136 | 0.0159 | -0.0150 [-0.0332, +0.0004] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0361 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0146 | 0.0200 | +0.0040 [-0.0014, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0594 | 0.1165 | +0.0217 [+0.0041, +0.0427] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0216 | 0.0048 | +0.0080 [+0.0062, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1294 | 0.0031 | +0.0040 [-0.0012, +0.0095] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1301 | 0.4146 | +0.0375 [-0.0217, +0.0899] |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.428 | 0.2979 | 0.2474 | +0.0266 [-0.0049, +0.0570] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1123 | 0.1133 | +0.0322 [+0.0061, +0.0587] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.388 | 0.1070 | 0.0630 | +0.0058 [-0.0017, +0.0138] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0150, +0.1665] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0439, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.368 | 6.85 flat / 3.36 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.275, 0.637] | 0.269 | 5.62 flat / 2.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.654] | 5.769 [3.773, 8.612] | 2.615 [1.619, 4.066] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 4.385 [2.703, 6.840] | 1.865 [1.106, 3.070] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.531] | 3.808 [2.100, 6.251] | 1.663 [0.884, 2.888] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.471] | 4.000 [2.350, 6.429] | 1.942 [1.076, 3.231] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 5.154 [3.200, 7.952] | 2.548 [1.478, 4.133] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 9.059 [6.278, 13.200] | 3.941 [2.548, 6.058] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 2.250 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 237 | 0.621 | 0.367 | 0.0630 | +0.0085 [-0.0026, +0.0193] | -0.0066 [-0.0171, +0.0029] | 0.884 | 0.535 | yes |
| 2 | 0.518 (147 of 1872 days never flag) | 199 | 0.612 | 0.427 | 0.0682 | +0.0029 [-0.0064, +0.0114] | -0.0071 [-0.0158, +0.0011] | 0.851 | 0.546 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 171 | 0.522 | 0.421 | 0.0707 | -0.0000 [-0.0111, +0.0097] | -0.0064 [-0.0170, +0.0032] | 0.849 | 0.465 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 164 | 0.435 | 0.366 | 0.0687 | +0.0021 [-0.0063, +0.0099] | -0.0063 [-0.0150, +0.0022] | 0.835 | 0.375 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 209 | 0.543 | 0.359 | 0.0729 | -0.0020 [-0.0115, +0.0065] | -0.0095 [-0.0190, -0.0007] | 0.810 | 0.466 | no |

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
| regime | 2018-19 | 375 | 102 | 0.814 | 0.366 | 0.3259 | 0.2720 | +0.0016 [-0.0505, +0.0527] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1577 | 0.0159 | -0.0029 [-0.0314, +0.0207] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0066 | 0.0200 | +0.0050 [+0.0007, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0650 | 0.1165 | +0.0206 [+0.0035, +0.0430] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0091 [+0.0074, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0683 | 0.0031 | +0.0217 [+0.0158, +0.0273] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0962 | 0.4146 | 0.0355 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.364 | 0.3300 | 0.2474 | -0.0045 [-0.0483, +0.0372] |
| day_type | month_end | 150 | 17 | 0.529 | 0.529 | 0.1116 | 0.1133 | +0.0312 [+0.0032, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.323 | 0.0918 | 0.0630 | +0.0009 [-0.0104, +0.0121] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0125, +0.1653] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1296 | 0.1461 | +0.0774 [+0.0477, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2758 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.760] | 0.349 | 6.54 flat / 3.17 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.281, 0.640] | 0.269 | 5.46 flat / 2.71 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.658] | 4.962 [3.161, 7.429] | 2.135 [1.259, 3.393] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.586] | 4.885 [3.042, 7.558] | 2.173 [1.260, 3.542] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.538] | 3.577 [1.958, 5.833] | 1.433 [0.717, 2.500] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.467] | 3.769 [2.151, 6.074] | 1.760 [0.907, 2.964] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.577 [2.615, 7.375] | 2.192 [1.115, 3.737] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 8.588 [5.786, 12.728] | 3.765 [2.327, 5.922] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 2.667 [0.941, 6.400] | 2.056 [0.614, 5.252] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 217 | 0.629 | 0.406 | 0.0627 | +0.0087 [-0.0028, +0.0193] | -0.0064 [-0.0176, +0.0036] | 0.884 | 0.554 | yes |
| 2 | 0.543 (147 of 1872 days never flag) | 210 | 0.597 | 0.395 | 0.0670 | +0.0040 [-0.0046, +0.0121] | -0.0060 [-0.0144, +0.0020] | 0.851 | 0.524 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 166 | 0.529 | 0.440 | 0.0682 | +0.0025 [-0.0077, +0.0118] | -0.0039 [-0.0140, +0.0052] | 0.851 | 0.475 | no |
| 4 | 0.649 (147 of 1870 days never flag) | 158 | 0.435 | 0.380 | 0.0670 | +0.0038 [-0.0041, +0.0112] | -0.0047 [-0.0127, +0.0031] | 0.837 | 0.378 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 194 | 0.543 | 0.387 | 0.0731 | -0.0022 [-0.0118, +0.0066] | -0.0097 [-0.0199, -0.0007] | 0.814 | 0.475 | no |

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
| regime | 2018-19 | 375 | 102 | 0.784 | 0.404 | 0.3287 | 0.2720 | +0.0023 [-0.0477, +0.0515] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1551 | 0.0159 | -0.0016 [-0.0294, +0.0214] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0065 | 0.0200 | +0.0051 [+0.0010, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.667 | 0.0626 | 0.1165 | +0.0199 [+0.0029, +0.0408] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0040 | 0.0048 | +0.0092 [+0.0074, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0667 | 0.0031 | +0.0222 [+0.0161, +0.0280] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0950 | 0.4146 | 0.0340 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.399 | 0.3312 | 0.2474 | -0.0039 [-0.0471, +0.0392] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1103 | 0.1133 | +0.0335 [+0.0073, +0.0623] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.358 | 0.0921 | 0.0630 | +0.0010 [-0.0105, +0.0116] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0144, +0.1665] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1246 | 0.1461 | +0.0764 [+0.0430, +0.1143] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2774 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.299 | 6.31 flat / 3.05 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.714] | 0.269 | 5.73 flat / 2.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.652] | 5.769 [3.680, 8.391] | 2.615 [1.530, 4.012] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.091, 0.400] | 3.654 [1.965, 6.000] | 1.779 [0.909, 3.026] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.520] | 3.885 [2.194, 6.106] | 1.962 [1.058, 3.177] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.731 [2.130, 5.941] | 1.567 [0.826, 2.570] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.846 [2.941, 7.410] | 2.183 [1.217, 3.625] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.647 [5.750, 13.000] | 3.735 [2.304, 5.964] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.889 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 237 | 0.621 | 0.367 | 0.0630 | +0.0085 [-0.0031, +0.0188] | -0.0066 [-0.0177, +0.0030] | 0.884 | 0.535 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 157 | 0.446 | 0.395 | 0.0647 | +0.0064 [-0.0034, +0.0156] | -0.0036 [-0.0136, +0.0054] | 0.860 | 0.391 | no |
| 3 | 0.723 (147 of 1871 days never flag) | 167 | 0.478 | 0.395 | 0.0648 | +0.0058 [-0.0046, +0.0154] | -0.0005 [-0.0107, +0.0093] | 0.864 | 0.420 | no |
| 4 | 0.683 (126 of 1870 days never flag) | 167 | 0.507 | 0.419 | 0.0630 | +0.0078 [+0.0003, +0.0153] | -0.0006 [-0.0086, +0.0070] | 0.854 | 0.451 | no |
| 5 | 0.449 (126 of 1869 days never flag) | 195 | 0.500 | 0.354 | 0.0666 | +0.0043 [-0.0057, +0.0132] | -0.0032 [-0.0127, +0.0055] | 0.844 | 0.427 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.457, difference +0.2431 [+0.0667, +0.3973]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0788, ΔBrier vs climatology +0.0507 [+0.0326, +0.0702], realised minus predicted -0.0126 [-0.0424, +0.0180]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.366 | 0.3259 | 0.2720 | +0.0016 [-0.0519, +0.0501] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1577 | 0.0159 | -0.0029 [-0.0318, +0.0205] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0066 | 0.0200 | +0.0050 [+0.0008, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0650 | 0.1165 | +0.0206 [+0.0036, +0.0419] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0041 | 0.0048 | +0.0091 [+0.0072, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0683 | 0.0031 | +0.0217 [+0.0160, +0.0272] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0962 | 0.4146 | 0.0355 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.364 | 0.3300 | 0.2474 | -0.0045 [-0.0494, +0.0377] |
| day_type | month_end | 150 | 17 | 0.529 | 0.529 | 0.1116 | 0.1133 | +0.0312 [+0.0033, +0.0582] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.323 | 0.0918 | 0.0630 | +0.0009 [-0.0110, +0.0122] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3561 | 0.2903 | +0.0892 [+0.0141, +0.1580] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1296 | 0.1461 | +0.0774 [+0.0479, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2758 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.800] | 0.269 | 5.58 flat / 2.62 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.323, 0.667] | 0.231 | 4.15 flat / 2.09 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.655] | 4.962 [3.132, 7.485] | 2.135 [1.240, 3.434] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.167, 0.538] | 4.192 [2.343, 6.721] | 1.904 [0.961, 3.263] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.478] | 3.154 [1.610, 5.333] | 1.490 [0.716, 2.645] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 3.808 [2.064, 6.239] | 1.817 [0.875, 3.188] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 3.615 [1.833, 6.106] | 1.788 [0.833, 3.239] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.636, 11.317] | 2.941 [1.731, 4.975] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 2.000 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.744 (126 of 1873 days never flag) | 217 | 0.629 | 0.406 | 0.0627 | +0.0087 [-0.0022, +0.0190] | -0.0064 [-0.0169, +0.0031] | 0.884 | 0.554 | yes |
| 2 | 0.625 (147 of 1872 days never flag) | 188 | 0.568 | 0.420 | 0.0646 | +0.0064 [-0.0031, +0.0156] | -0.0036 [-0.0130, +0.0056] | 0.862 | 0.505 | yes |
| 3 | 0.421 (147 of 1871 days never flag) | 146 | 0.464 | 0.438 | 0.0644 | +0.0063 [-0.0038, +0.0155] | -0.0001 [-0.0102, +0.0092] | 0.866 | 0.416 | no |
| 4 | 0.786 (126 of 1870 days never flag) | 166 | 0.486 | 0.404 | 0.0628 | +0.0080 [-0.0001, +0.0152] | -0.0005 [-0.0090, +0.0072] | 0.854 | 0.428 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 155 | 0.442 | 0.394 | 0.0668 | +0.0042 [-0.0058, +0.0132] | -0.0034 [-0.0134, +0.0059] | 0.843 | 0.388 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2494 [+0.0883, +0.3895]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0781, ΔBrier vs climatology +0.0513 [+0.0334, +0.0708], realised minus predicted -0.0125 [-0.0421, +0.0175]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.784 | 0.404 | 0.3287 | 0.2720 | +0.0023 [-0.0494, +0.0499] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1551 | 0.0159 | -0.0016 [-0.0283, +0.0220] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0065 | 0.0200 | +0.0051 [+0.0009, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.667 | 0.0626 | 0.1165 | +0.0199 [+0.0036, +0.0399] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0040 | 0.0048 | +0.0092 [+0.0075, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0667 | 0.0031 | +0.0222 [+0.0161, +0.0279] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0950 | 0.4146 | 0.0340 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.399 | 0.3312 | 0.2474 | -0.0039 [-0.0472, +0.0362] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1103 | 0.1133 | +0.0335 [+0.0070, +0.0599] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.358 | 0.0921 | 0.0630 | +0.0010 [-0.0105, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3546 | 0.2903 | +0.0906 [+0.0192, +0.1643] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1246 | 0.1461 | +0.0764 [+0.0440, +0.1125] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2774 | 0.2213 |

## risk_logistic+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.762] | 0.382 | 7.08 flat / 3.57 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 5.54 flat / 2.79 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 6.192 [4.133, 9.111] | 2.923 [1.845, 4.397] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 4.346 [2.600, 6.721] | 1.856 [1.055, 2.944] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.210, 0.572] | 3.808 [2.107, 6.185] | 1.683 [0.894, 2.730] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 3.962 [2.241, 6.276] | 1.923 [1.028, 3.173] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 5.154 [3.047, 8.002] | 2.548 [1.416, 4.118] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 9.059 [6.316, 13.563] | 3.941 [2.531, 6.208] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 3.333 [1.384, 8.000] | 2.861 [1.083, 7.375] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 253 | 0.657 | 0.364 | 0.0564 | +0.0150 [+0.0069, +0.0234] | -0.0001 [-0.0071, +0.0071] | 0.875 | 0.564 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 198 | 0.612 | 0.429 | 0.0646 | +0.0064 [-0.0007, +0.0133] | -0.0036 [-0.0106, +0.0028] | 0.839 | 0.546 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 173 | 0.536 | 0.428 | 0.0668 | +0.0039 [-0.0036, +0.0106] | -0.0024 [-0.0098, +0.0043] | 0.829 | 0.479 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 164 | 0.442 | 0.372 | 0.0664 | +0.0044 [-0.0024, +0.0109] | -0.0041 [-0.0117, +0.0032] | 0.818 | 0.383 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 209 | 0.543 | 0.359 | 0.0687 | +0.0022 [-0.0041, +0.0081] | -0.0053 [-0.0124, +0.0012] | 0.782 | 0.466 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.591 (climatology 0.457, difference +0.1342 [+0.0254, +0.2233]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0929, ΔBrier vs climatology +0.0366 [+0.0202, +0.0526], realised minus predicted +0.0019 [-0.0327, +0.0376]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.366 | 0.2915 | 0.2720 | +0.0329 [-0.0034, +0.0693] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.1806 | 0.0159 | -0.0033 [-0.0249, +0.0152] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0069 | 0.0200 | +0.0050 [+0.0010, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0626 | 0.1165 | +0.0239 [+0.0054, +0.0474] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0068 | 0.0048 | +0.0091 [+0.0072, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0910 | 0.0031 | +0.0170 [+0.0122, +0.0219] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1035 | 0.4146 | 0.0374 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.761 | 0.362 | 0.2996 | 0.2474 | +0.0246 [-0.0074, +0.0567] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1121 | 0.1133 | +0.0312 [+0.0054, +0.0596] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.319 | 0.0892 | 0.0630 | +0.0086 [+0.0007, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0127, +0.1598] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0463, +0.1137] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2416 | 0.2213 |

## risk_logistic+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.361 | 6.73 flat / 3.41 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.643] | 0.269 | 5.54 flat / 2.81 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.314, 0.680] | 4.654 [2.999, 6.944] | 2.048 [1.271, 3.159] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.385 [2.528, 6.793] | 1.846 [1.066, 2.927] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.654 [1.926, 5.858] | 1.500 [0.741, 2.550] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.152, 0.474] | 3.885 [2.165, 6.167] | 1.846 [0.991, 3.103] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.577 [2.535, 7.250] | 2.192 [1.112, 3.705] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.588 [5.727, 12.717] | 3.765 [2.338, 5.947] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 2.750 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (126 of 1873 days never flag) | 210 | 0.636 | 0.424 | 0.0562 | +0.0152 [+0.0076, +0.0235] | +0.0002 [-0.0066, +0.0073] | 0.874 | 0.566 | yes |
| 2 | 0.402 (147 of 1872 days never flag) | 199 | 0.612 | 0.427 | 0.0635 | +0.0076 [+0.0009, +0.0142] | -0.0024 [-0.0086, +0.0041] | 0.839 | 0.546 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 169 | 0.536 | 0.438 | 0.0643 | +0.0064 [-0.0001, +0.0127] | +0.0000 [-0.0060, +0.0065] | 0.830 | 0.481 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 162 | 0.442 | 0.377 | 0.0648 | +0.0061 [-0.0003, +0.0124] | -0.0024 [-0.0087, +0.0046] | 0.820 | 0.384 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 194 | 0.543 | 0.387 | 0.0689 | +0.0020 [-0.0050, +0.0085] | -0.0055 [-0.0129, +0.0016] | 0.787 | 0.475 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.563 (climatology 0.457, difference +0.1054 [+0.0139, +0.1875]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0906, ΔBrier vs climatology +0.0389 [+0.0247, +0.0549], realised minus predicted +0.0021 [-0.0300, +0.0379]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.784 | 0.428 | 0.2943 | 0.2720 | +0.0336 [+0.0011, +0.0692] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1781 | 0.0159 | -0.0019 [-0.0230, +0.0162] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0109, +0.0142] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0068 | 0.0200 | +0.0051 [+0.0008, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0602 | 0.1165 | +0.0231 [+0.0055, +0.0454] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0066 | 0.0048 | +0.0092 [+0.0073, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0894 | 0.0031 | +0.0175 [+0.0122, +0.0229] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1023 | 0.4146 | 0.0359 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.422 | 0.3007 | 0.2474 | +0.0252 [-0.0048, +0.0568] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1107 | 0.1133 | +0.0335 [+0.0067, +0.0618] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.382 | 0.0895 | 0.0630 | +0.0087 [+0.0013, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0178, +0.1621] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0438, +0.1156] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2432 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.757] | 0.356 | 6.65 flat / 3.25 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.722] | 0.274 | 5.88 flat / 2.92 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.682] | 6.192 [4.071, 8.945] | 2.923 [1.830, 4.387] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.114, 0.438] | 3.808 [2.074, 6.139] | 1.904 [0.985, 3.230] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 3.769 [2.161, 5.870] | 1.837 [0.983, 3.047] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.632] | 3.846 [2.200, 6.000] | 1.654 [0.914, 2.672] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.636] | 5.000 [3.035, 7.578] | 2.337 [1.327, 3.792] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.647 [5.857, 13.077] | 3.735 [2.347, 6.001] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 2.889 [1.214, 6.505] | 2.333 [0.857, 5.667] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 253 | 0.657 | 0.364 | 0.0564 | +0.0150 [+0.0068, +0.0239] | -0.0001 [-0.0069, +0.0070] | 0.875 | 0.564 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 163 | 0.460 | 0.393 | 0.0605 | +0.0105 [+0.0033, +0.0179] | +0.0005 [-0.0066, +0.0079] | 0.850 | 0.403 | yes |
| 3 | 0.415 (147 of 1871 days never flag) | 164 | 0.478 | 0.402 | 0.0603 | +0.0104 [+0.0041, +0.0170] | +0.0040 [-0.0027, +0.0109] | 0.848 | 0.422 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 173 | 0.529 | 0.422 | 0.0603 | +0.0105 [+0.0039, +0.0168] | +0.0021 [-0.0051, +0.0090] | 0.842 | 0.471 | yes |
| 5 | 0.424 (126 of 1869 days never flag) | 200 | 0.507 | 0.350 | 0.0620 | +0.0089 [+0.0019, +0.0150] | +0.0014 [-0.0056, +0.0082] | 0.828 | 0.432 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.457, difference +0.2431 [+0.0720, +0.3916]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0792, ΔBrier vs climatology +0.0503 [+0.0323, +0.0689], realised minus predicted -0.0174 [-0.0472, +0.0138]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.814 | 0.366 | 0.2915 | 0.2720 | +0.0329 [-0.0021, +0.0680] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.1806 | 0.0159 | -0.0033 [-0.0247, +0.0159] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0109, +0.0142] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0069 | 0.0200 | +0.0050 [+0.0009, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0626 | 0.1165 | +0.0239 [+0.0046, +0.0475] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0068 | 0.0048 | +0.0091 [+0.0072, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0910 | 0.0031 | +0.0170 [+0.0120, +0.0218] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1035 | 0.4146 | 0.0374 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.761 | 0.362 | 0.2996 | 0.2474 | +0.0246 [-0.0077, +0.0580] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1121 | 0.1133 | +0.0312 [+0.0041, +0.0591] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.319 | 0.0892 | 0.0630 | +0.0086 [+0.0009, +0.0169] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0160, +0.1619] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0454, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2416 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.269 | 5.62 flat / 2.65 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 4.19 flat / 2.10 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.692] | 4.654 [2.963, 6.905] | 2.048 [1.257, 3.213] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.207, 0.571] | 4.346 [2.423, 6.917] | 2.058 [1.089, 3.438] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.474] | 3.038 [1.513, 5.092] | 1.365 [0.643, 2.400] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 3.885 [2.111, 6.321] | 1.894 [0.950, 3.260] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.500] | 3.692 [1.882, 6.227] | 1.837 [0.854, 3.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.176 [4.588, 11.300] | 2.941 [1.716, 4.932] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (126 of 1873 days never flag) | 210 | 0.636 | 0.424 | 0.0562 | +0.0152 [+0.0070, +0.0237] | +0.0002 [-0.0070, +0.0071] | 0.874 | 0.566 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 193 | 0.576 | 0.415 | 0.0605 | +0.0106 [+0.0031, +0.0179] | +0.0006 [-0.0069, +0.0077] | 0.853 | 0.510 | yes |
| 3 | 0.421 (147 of 1871 days never flag) | 143 | 0.464 | 0.448 | 0.0599 | +0.0108 [+0.0045, +0.0171] | +0.0045 [-0.0018, +0.0109] | 0.852 | 0.418 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 168 | 0.486 | 0.399 | 0.0601 | +0.0107 [+0.0042, +0.0172] | +0.0023 [-0.0047, +0.0093] | 0.841 | 0.427 | yes |
| 5 | 0.424 (147 of 1869 days never flag) | 157 | 0.442 | 0.389 | 0.0621 | +0.0088 [+0.0020, +0.0158] | +0.0013 [-0.0063, +0.0086] | 0.827 | 0.387 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2500 [+0.0923, +0.3881]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0786, ΔBrier vs climatology +0.0509 [+0.0329, +0.0706], realised minus predicted -0.0174 [-0.0480, +0.0139]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.784 | 0.428 | 0.2943 | 0.2720 | +0.0336 [-0.0021, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1781 | 0.0159 | -0.0019 [-0.0227, +0.0174] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0140 | 0.0000 | +0.0126 [+0.0110, +0.0142] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0068 | 0.0200 | +0.0051 [+0.0010, +0.0097] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0602 | 0.1165 | +0.0231 [+0.0049, +0.0463] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0066 | 0.0048 | +0.0092 [+0.0074, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0894 | 0.0031 | +0.0175 [+0.0125, +0.0231] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1023 | 0.4146 | 0.0359 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.422 | 0.3007 | 0.2474 | +0.0252 [-0.0068, +0.0579] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1107 | 0.1133 | +0.0335 [+0.0068, +0.0604] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.382 | 0.0895 | 0.0630 | +0.0087 [+0.0006, +0.0170] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0178, +0.1659] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0440, +0.1140] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2432 | 0.2213 |

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

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [-0.0214, +0.2463]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0239 [+0.0136, +0.0345], realised minus predicted +0.0775 [+0.0426, +0.1148]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1080 | 0.2720 | -0.0024 [-0.0224, +0.0166] |
| regime | 2020 | 251 | 4 | 0.250 | 0.032 | 0.0294 | 0.0159 | +0.0298 [+0.0202, +0.0383] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.722 | 0.0311 | 0.1165 | +0.0168 [+0.0040, +0.0338] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0092 | 0.0031 | +0.0279 [+0.0218, +0.0337] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0421 | 0.4146 | 0.0149 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.519 | 0.1063 | 0.2474 | +0.0057 [-0.0113, +0.0230] |
| day_type | month_end | 150 | 17 | 0.765 | 0.433 | 0.0996 | 0.1133 | +0.0352 [+0.0096, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.439 | 0.0123 | 0.0630 | +0.0047 [-0.0004, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1520] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1332 | 0.1461 | +0.0711 [+0.0381, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2040 | 0.2213 |

## risk_logistic_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.679] | 0.385 | 7.15 flat / 3.33 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.324, 0.667] | 0.280 | 6.00 flat / 2.76 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.242, 0.609] | 4.577 [2.808, 6.901] | 1.971 [1.159, 3.072] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 4.808 [3.059, 7.143] | 1.962 [1.188, 3.018] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.615 [2.846, 7.000] | 2.000 [1.192, 3.179] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.192 [2.588, 6.476] | 1.885 [1.077, 2.989] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.647] | 5.038 [3.190, 7.524] | 2.260 [1.386, 3.486] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.818, 10.167] | 2.574 [1.379, 4.334] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 8.444 (no interval) | 4.750 (no interval) |

Recall with equal weight per regime: 0.372 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 209 | 0.643 | 0.431 | 0.0497 | +0.0217 [+0.0143, +0.0296] | +0.0066 [+0.0019, +0.0120] | 0.887 | 0.574 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 218 | 0.669 | 0.427 | 0.0586 | +0.0124 [+0.0073, +0.0182] | +0.0024 [-0.0014, +0.0071] | 0.842 | 0.597 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 202 | 0.594 | 0.406 | 0.0628 | +0.0079 [+0.0018, +0.0140] | +0.0016 [-0.0043, +0.0073] | 0.812 | 0.525 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 178 | 0.500 | 0.388 | 0.0615 | +0.0094 [+0.0035, +0.0157] | +0.0009 [-0.0047, +0.0068] | 0.820 | 0.437 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 213 | 0.594 | 0.385 | 0.0620 | +0.0089 [+0.0039, +0.0138] | +0.0014 [-0.0028, +0.0057] | 0.797 | 0.519 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0169, +0.2528]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0870, ΔBrier vs climatology +0.0425 [+0.0268, +0.0599], realised minus predicted -0.0019 [-0.0322, +0.0307]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.440 | 0.2494 | 0.2720 | +0.0533 [+0.0256, +0.0823] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1320 | 0.0159 | +0.0135 [-0.0012, +0.0264] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0188 | 0.0000 | +0.0132 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0327 | 0.0200 | +0.0009 [-0.0055, +0.0058] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.1073 | 0.1165 | +0.0288 [+0.0041, +0.0593] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0222 | 0.0048 | +0.0082 [+0.0061, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0738 | 0.0031 | +0.0205 [+0.0142, +0.0265] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2264 | 0.4146 | +0.0842 [-0.0045, +0.1737] |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.428 | 0.2526 | 0.2474 | +0.0467 [+0.0216, +0.0732] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1089 | 0.1133 | +0.0404 [+0.0147, +0.0692] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.383 | 0.0858 | 0.0630 | +0.0158 [+0.0089, +0.0234] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3198 | 0.2903 | +0.0954 [+0.0435, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1332 | 0.1461 | +0.0711 [+0.0381, +0.1090] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3420 | 0.2213 |

## risk_logistic_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.815] | 0.421 | 8.04 flat / 4.12 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.667] | 0.278 | 5.96 flat / 2.97 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.684] | 4.077 [2.931, 5.864] | 2.010 [1.393, 3.060] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.846 [2.566, 5.778] | 1.558 [1.045, 2.364] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.615 [2.306, 5.714] | 1.673 [1.040, 2.750] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.654 [2.472, 5.476] | 1.712 [1.121, 2.650] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.316, 0.679] | 4.115 [2.750, 6.200] | 1.913 [1.284, 2.929] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.765 [4.500, 10.252] | 2.750 [1.787, 4.251] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.444 (no interval) | 6.722 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (105 of 1873 days never flag) | 193 | 0.621 | 0.451 | 0.0516 | +0.0199 [+0.0132, +0.0270] | +0.0048 [+0.0004, +0.0093] | 0.804 | 0.560 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 177 | 0.554 | 0.435 | 0.0609 | +0.0102 [+0.0048, +0.0160] | +0.0002 [-0.0045, +0.0051] | 0.752 | 0.496 | no |
| 3 | 0.128 (147 of 1871 days never flag) | 164 | 0.507 | 0.427 | 0.0628 | +0.0079 [+0.0013, +0.0142] | +0.0015 [-0.0045, +0.0075] | 0.748 | 0.453 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 157 | 0.449 | 0.395 | 0.0623 | +0.0085 [+0.0026, +0.0144] | +0.0000 [-0.0054, +0.0056] | 0.758 | 0.394 | no |
| 5 | 0.172 (147 of 1869 days never flag) | 180 | 0.529 | 0.406 | 0.0627 | +0.0083 [+0.0027, +0.0136] | +0.0007 [-0.0038, +0.0055] | 0.744 | 0.467 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.457, difference +0.1421 [+0.0012, +0.2594]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0406 [+0.0256, +0.0566], realised minus predicted +0.0472 [+0.0192, +0.0765]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.508 | 0.1797 | 0.2720 | +0.0377 [+0.0125, +0.0659] |
| regime | 2020 | 251 | 4 | 0.250 | 0.053 | 0.0370 | 0.0159 | +0.0225 [+0.0051, +0.0368] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.167 | 0.0151 | 0.0200 | +0.0010 [-0.0058, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.759 | 0.500 | 0.0823 | 0.1165 | +0.0279 [+0.0032, +0.0559] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.091 | 0.0082 | 0.0048 | +0.0084 [+0.0062, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0142 | 0.0031 | +0.0265 [+0.0196, +0.0327] |
| scarcity_state | 2 | 41 | 17 | 0.706 | 0.600 | 0.1975 | 0.4146 | +0.0822 [-0.0034, +0.1683] |
| scarcity_state | 3 | 473 | 117 | 0.632 | 0.484 | 0.1750 | 0.2474 | +0.0349 [+0.0125, +0.0594] |
| day_type | month_end | 150 | 17 | 0.882 | 0.556 | 0.1034 | 0.1133 | +0.0409 [+0.0150, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.416 | 0.0416 | 0.0630 | +0.0136 [+0.0073, +0.0205] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0427, +0.1489] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1332 | 0.1461 | +0.0711 [+0.0394, +0.1092] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3860 | 0.2213 |

## risk_logistic_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.719] | 0.365 | 6.81 flat / 3.08 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.654] | 0.269 | 5.69 flat / 2.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.682] | 4.500 [2.763, 6.819] | 1.856 [1.095, 2.950] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 4.346 [2.631, 6.765] | 1.769 [1.023, 2.881] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 4.192 [2.500, 6.593] | 1.788 [1.029, 2.947] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.800, 6.955] | 2.144 [1.250, 3.429] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 5.115 [3.320, 7.637] | 2.308 [1.424, 3.588] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.059 [5.524, 12.250] | 3.441 [2.180, 5.500] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 2.389 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (126 of 1873 days never flag) | 201 | 0.600 | 0.418 | 0.0498 | +0.0216 [+0.0154, +0.0284] | +0.0065 [+0.0021, +0.0115] | 0.882 | 0.532 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 199 | 0.619 | 0.432 | 0.0576 | +0.0135 [+0.0090, +0.0183] | +0.0035 [-0.0006, +0.0080] | 0.831 | 0.554 | no |
| 3 | 0.248 (147 of 1871 days never flag) | 188 | 0.572 | 0.420 | 0.0610 | +0.0097 [+0.0043, +0.0155] | +0.0033 [-0.0023, +0.0097] | 0.807 | 0.510 | yes |
| 4 | 0.243 (147 of 1870 days never flag) | 187 | 0.500 | 0.369 | 0.0599 | +0.0110 [+0.0060, +0.0161] | +0.0025 [-0.0027, +0.0078] | 0.816 | 0.432 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 211 | 0.565 | 0.370 | 0.0602 | +0.0108 [+0.0065, +0.0149] | +0.0032 [-0.0011, +0.0074] | 0.796 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.457, difference +0.1424 [+0.0193, +0.2505]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0879, ΔBrier vs climatology +0.0416 [+0.0266, +0.0576], realised minus predicted +0.0078 [-0.0228, +0.0415]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.406 | 0.2323 | 0.2720 | +0.0476 [+0.0233, +0.0731] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1212 | 0.0159 | +0.0189 [+0.0086, +0.0289] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0133 [+0.0116, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0238 | 0.0200 | +0.0031 [-0.0009, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.647 | 0.0914 | 0.1165 | +0.0282 [+0.0057, +0.0561] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0176 | 0.0048 | +0.0089 [+0.0072, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0655 | 0.0031 | +0.0225 [+0.0169, +0.0285] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1850 | 0.4146 | 0.0742 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.411 | 0.2348 | 0.2474 | +0.0442 [+0.0224, +0.0667] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1075 | 0.1133 | +0.0395 [+0.0145, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.361 | 0.0750 | 0.0630 | +0.0157 [+0.0098, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0386, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1332 | 0.1461 | +0.0711 [+0.0380, +0.1071] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2523 | 0.2213 |

## risk_logistic_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.667] | 0.368 | 6.85 flat / 3.13 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.677] | 0.269 | 5.73 flat / 2.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.538 [2.821, 6.906] | 1.962 [1.166, 3.076] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.731 [2.968, 7.095] | 1.933 [1.160, 3.033] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.462 [2.666, 6.923] | 1.923 [1.088, 3.073] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.387, 6.369] | 1.808 [0.992, 2.950] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.923 [3.038, 7.455] | 2.183 [1.276, 3.409] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.846, 10.067] | 2.574 [1.389, 4.263] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 7.556 (no interval) | 4.194 (no interval) |

Recall with equal weight per regime: 0.372 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 208 | 0.643 | 0.433 | 0.0491 | +0.0224 [+0.0155, +0.0301] | +0.0073 [+0.0025, +0.0125] | 0.908 | 0.575 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 216 | 0.669 | 0.431 | 0.0579 | +0.0132 [+0.0082, +0.0186] | +0.0032 [-0.0008, +0.0077] | 0.879 | 0.598 | yes |
| 3 | 0.25 (147 of 1871 days never flag) | 198 | 0.594 | 0.414 | 0.0611 | +0.0096 [+0.0038, +0.0156] | +0.0033 [-0.0025, +0.0092] | 0.863 | 0.527 | yes |
| 4 | 0.255 (147 of 1870 days never flag) | 177 | 0.514 | 0.401 | 0.0602 | +0.0107 [+0.0050, +0.0165] | +0.0022 [-0.0032, +0.0076] | 0.864 | 0.453 | yes |
| 5 | 0.245 (147 of 1869 days never flag) | 210 | 0.594 | 0.390 | 0.0610 | +0.0099 [+0.0049, +0.0148] | +0.0024 [-0.0018, +0.0070] | 0.851 | 0.520 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0195, +0.2564]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0855, ΔBrier vs climatology +0.0440 [+0.0286, +0.0609], realised minus predicted +0.0242 [-0.0069, +0.0572]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.440 | 0.2494 | 0.2720 | +0.0533 [+0.0268, +0.0818] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1320 | 0.0159 | +0.0135 [-0.0018, +0.0260] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0046 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0002, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.0937 | 0.1165 | +0.0296 [+0.0050, +0.0625] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0738 | 0.0031 | +0.0205 [+0.0143, +0.0265] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2264 | 0.4146 | 0.0842 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.428 | 0.2526 | 0.2474 | +0.0467 [+0.0237, +0.0734] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1069 | 0.1133 | +0.0404 [+0.0151, +0.0675] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.385 | 0.0726 | 0.0630 | +0.0165 [+0.0101, +0.0243] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3198 | 0.2903 | +0.0954 [+0.0374, +0.1520] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1332 | 0.1461 | +0.0711 [+0.0386, +0.1084] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3420 | 0.2213 |

## risk_logistic_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.480, 0.821] | 0.387 | 7.50 flat / 3.60 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.688] | 0.276 | 5.92 flat / 2.82 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.077 [3.393, 7.634] | 2.269 [1.458, 3.603] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 5.038 [3.316, 7.641] | 2.125 [1.345, 3.364] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 4.577 [2.871, 7.182] | 1.990 [1.191, 3.283] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.385 [2.727, 6.813] | 2.010 [1.183, 3.243] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 5.000 [3.185, 7.765] | 2.337 [1.463, 3.695] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 0.952] | 7.059 [4.474, 11.000] | 2.868 [1.690, 4.717] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.333 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (126 of 1873 days never flag) | 226 | 0.671 | 0.416 | 0.0503 | +0.0211 [+0.0165, +0.0264] | +0.0061 [+0.0015, +0.0106] | 0.899 | 0.595 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 228 | 0.698 | 0.425 | 0.0589 | +0.0122 [+0.0081, +0.0165] | +0.0022 [-0.0024, +0.0066] | 0.846 | 0.622 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 202 | 0.601 | 0.411 | 0.0620 | +0.0087 [+0.0035, +0.0137] | +0.0024 [-0.0036, +0.0081] | 0.815 | 0.533 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 187 | 0.529 | 0.390 | 0.0613 | +0.0095 [+0.0048, +0.0141] | +0.0011 [-0.0047, +0.0065] | 0.826 | 0.463 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 213 | 0.601 | 0.390 | 0.0614 | +0.0095 [+0.0054, +0.0135] | +0.0020 [-0.0027, +0.0062] | 0.806 | 0.526 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.589 (climatology 0.457, difference +0.1317 [+0.0089, +0.2280]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0917, ΔBrier vs climatology +0.0377 [+0.0250, +0.0510], realised minus predicted +0.0391 [+0.0076, +0.0728]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.429 | 0.1787 | 0.2720 | +0.0388 [+0.0239, +0.0559] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0807 | 0.0159 | +0.0267 [+0.0175, +0.0357] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0095 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0177 | 0.0200 | +0.0033 [-0.0011, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.533 | 0.0692 | 0.1165 | +0.0293 [+0.0085, +0.0567] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0118 | 0.0048 | +0.0091 [+0.0073, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0415 | 0.0031 | +0.0261 [+0.0203, +0.0317] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.1343 | 0.4146 | +0.0709 [+0.0125, +0.1384] |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.421 | 0.1794 | 0.2474 | +0.0398 [+0.0252, +0.0562] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1043 | 0.1133 | +0.0382 [+0.0122, +0.0657] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.376 | 0.0491 | 0.0630 | +0.0153 [+0.0114, +0.0201] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0398, +0.1512] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1332 | 0.1461 | +0.0711 [+0.0382, +0.1094] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2211 | 0.2213 |

## risk_logistic_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 5.42 flat / 2.54 weighted | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.647] | 0.269 | 4.88 flat / 2.35 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.172, 0.542] | 4.077 [2.222, 6.572] | 1.769 [0.881, 2.987] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.211, 0.579] | 4.808 [2.889, 7.539] | 2.077 [1.120, 3.438] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.579] | 3.923 [2.228, 6.317] | 1.673 [0.889, 2.802] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.528] | 3.846 [2.031, 6.336] | 1.942 [0.949, 3.392] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.500 [2.500, 7.226] | 2.115 [1.097, 3.609] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.824] | 6.706 [4.042, 10.801] | 2.735 [1.483, 4.667] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.167 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.8 (147 of 1873 days never flag) | 178 | 0.514 | 0.404 | 0.0625 | +0.0089 [-0.0009, +0.0185] | -0.0062 [-0.0153, +0.0021] | 0.871 | 0.453 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 208 | 0.597 | 0.399 | 0.0702 | +0.0009 [-0.0079, +0.0097] | -0.0091 [-0.0174, -0.0012] | 0.826 | 0.525 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 173 | 0.514 | 0.410 | 0.0748 | -0.0041 [-0.0149, +0.0052] | -0.0104 [-0.0209, -0.0012] | 0.802 | 0.456 | no |
| 4 | 0.519 (147 of 1870 days never flag) | 161 | 0.442 | 0.379 | 0.0723 | -0.0015 [-0.0096, +0.0066] | -0.0099 [-0.0180, -0.0020] | 0.816 | 0.384 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 190 | 0.529 | 0.384 | 0.0718 | -0.0009 [-0.0076, +0.0055] | -0.0084 [-0.0150, -0.0018] | 0.784 | 0.461 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.457, difference +0.1392 [+0.0032, +0.2580]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0943, ΔBrier vs climatology +0.0352 [+0.0190, +0.0521], realised minus predicted -0.0086 [-0.0412, +0.0248]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.412 | 0.3238 | 0.2720 | +0.0090 [-0.0339, +0.0519] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2066 | 0.0159 | -0.0138 [-0.0348, +0.0039] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0028 [-0.0023, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0609 | 0.1165 | +0.0281 [+0.0069, +0.0562] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0068, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1146 | 0.0031 | +0.0085 [+0.0026, +0.0149] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1523 | 0.4146 | +0.0684 [-0.0070, +0.1543] |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.404 | 0.3209 | 0.2474 | +0.0044 [-0.0323, +0.0411] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.1103 | 0.1133 | +0.0377 [+0.0126, +0.0635] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.356 | 0.1021 | 0.0630 | +0.0010 [-0.0090, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0400, +0.1487] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1332 | 0.1461 | +0.0711 [+0.0385, +0.1092] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2919 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.720] | 0.280 | 5.96 flat / 2.74 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.619] | 0.269 | 4.73 flat / 2.14 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 3.808 [2.135, 6.273] | 1.692 [0.846, 2.990] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.962 [3.097, 7.714] | 2.096 [1.173, 3.542] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.257, 0.619] | 3.962 [2.281, 6.410] | 1.663 [0.900, 2.828] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.538] | 3.462 [1.916, 5.741] | 1.519 [0.790, 2.642] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.545] | 3.923 [2.207, 6.421] | 1.702 [0.898, 2.908] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.929] | 6.941 [4.408, 11.202] | 2.838 [1.619, 4.904] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.111 (no interval) | 2.556 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 173 | 0.529 | 0.428 | 0.0621 | +0.0093 [-0.0007, +0.0191] | -0.0058 [-0.0147, +0.0025] | 0.873 | 0.471 | no |
| 2 | 0.445 (147 of 1872 days never flag) | 214 | 0.612 | 0.397 | 0.0693 | +0.0018 [-0.0078, +0.0100] | -0.0082 [-0.0172, -0.0006] | 0.827 | 0.537 | no |
| 3 | 0.424 (147 of 1871 days never flag) | 175 | 0.522 | 0.411 | 0.0724 | -0.0017 [-0.0113, +0.0069] | -0.0081 [-0.0176, +0.0004] | 0.804 | 0.462 | no |
| 4 | 0.43 (147 of 1870 days never flag) | 151 | 0.442 | 0.404 | 0.0710 | -0.0001 [-0.0077, +0.0071] | -0.0086 [-0.0163, -0.0015] | 0.818 | 0.390 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 175 | 0.529 | 0.417 | 0.0724 | -0.0015 [-0.0087, +0.0053] | -0.0090 [-0.0164, -0.0022] | 0.789 | 0.470 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.553 (climatology 0.457, difference +0.0957 [-0.0097, +0.1924]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0920, ΔBrier vs climatology +0.0375 [+0.0222, +0.0548], realised minus predicted -0.0081 [-0.0420, +0.0250]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.422 | 0.3266 | 0.2720 | +0.0107 [-0.0365, +0.0546] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2027 | 0.0159 | -0.0126 [-0.0342, +0.0051] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0029 [-0.0025, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0590 | 0.1165 | +0.0275 [+0.0065, +0.0546] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1124 | 0.0031 | +0.0088 [+0.0030, +0.0149] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1506 | 0.4146 | +0.0653 [-0.0127, +0.1424] |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.424 | 0.3219 | 0.2474 | +0.0062 [-0.0343, +0.0438] |
| day_type | month_end | 150 | 17 | 0.706 | 0.667 | 0.1083 | 0.1133 | +0.0403 [+0.0146, +0.0679] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.360 | 0.1025 | 0.0630 | +0.0011 [-0.0094, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0464, +0.1425] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0417, +0.1102] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2978 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.783] | 0.269 | 5.35 flat / 2.60 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 4.62 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 4.077 [2.237, 6.602] | 1.769 [0.905, 3.029] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.438] | 4.077 [2.310, 6.460] | 1.933 [1.019, 3.250] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 3.731 [2.190, 6.000] | 1.760 [1.009, 2.945] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.320, 0.682] | 4.077 [2.286, 6.579] | 2.010 [1.067, 3.355] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 3.885 [2.136, 6.286] | 1.952 [0.965, 3.367] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.353 [3.762, 10.385] | 2.662 [1.473, 4.641] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.444 (no interval) | 2.472 (no interval) |

Recall with equal weight per regime: 0.416 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.8 (147 of 1873 days never flag) | 178 | 0.514 | 0.404 | 0.0625 | +0.0089 [-0.0010, +0.0187] | -0.0062 [-0.0151, +0.0021] | 0.871 | 0.453 | no |
| 2 | 0.458 (147 of 1872 days never flag) | 172 | 0.475 | 0.384 | 0.0655 | +0.0055 [-0.0033, +0.0143] | -0.0045 [-0.0131, +0.0041] | 0.844 | 0.414 | no |
| 3 | 0.443 (126 of 1871 days never flag) | 169 | 0.522 | 0.426 | 0.0686 | +0.0020 [-0.0080, +0.0109] | -0.0043 [-0.0139, +0.0049] | 0.824 | 0.466 | no |
| 4 | 0.53 (126 of 1870 days never flag) | 177 | 0.514 | 0.401 | 0.0666 | +0.0042 [-0.0041, +0.0121] | -0.0042 [-0.0125, +0.0035] | 0.841 | 0.453 | yes |
| 5 | 0.456 (147 of 1869 days never flag) | 163 | 0.449 | 0.380 | 0.0667 | +0.0043 [-0.0022, +0.0108] | -0.0033 [-0.0098, +0.0034] | 0.825 | 0.391 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.686 (climatology 0.457, difference +0.2293 [+0.1055, +0.3568]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0837, ΔBrier vs climatology +0.0458 [+0.0281, +0.0656], realised minus predicted -0.0277 [-0.0590, +0.0035]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.412 | 0.3238 | 0.2720 | +0.0090 [-0.0360, +0.0530] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2066 | 0.0159 | -0.0138 [-0.0362, +0.0045] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0028 [-0.0022, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0609 | 0.1165 | +0.0281 [+0.0056, +0.0557] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0068, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1146 | 0.0031 | +0.0085 [+0.0028, +0.0141] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1523 | 0.4146 | +0.0684 [-0.0095, +0.1529] |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.404 | 0.3209 | 0.2474 | +0.0044 [-0.0349, +0.0427] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.1103 | 0.1133 | +0.0377 [+0.0123, +0.0662] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.356 | 0.1021 | 0.0630 | +0.0010 [-0.0089, +0.0112] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0403, +0.1494] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1332 | 0.1461 | +0.0711 [+0.0387, +0.1082] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2919 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.406, 0.750] | 0.293 | 6.19 flat / 2.90 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.682] | 0.269 | 4.77 flat / 2.42 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.212, 0.560] | 3.808 [2.080, 6.104] | 1.692 [0.836, 2.869] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 5.192 [3.281, 7.850] | 2.317 [1.348, 3.671] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.346 [1.806, 5.500] | 1.558 [0.821, 2.706] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 4.346 [2.516, 6.926] | 2.163 [1.162, 3.644] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.526] | 3.808 [2.000, 6.296] | 1.923 [0.922, 3.375] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 7.176 [4.600, 11.143] | 2.971 [1.784, 4.876] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.778 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 173 | 0.529 | 0.428 | 0.0621 | +0.0093 [-0.0010, +0.0195] | -0.0058 [-0.0152, +0.0029] | 0.873 | 0.471 | no |
| 2 | 0.45 (126 of 1872 days never flag) | 217 | 0.590 | 0.378 | 0.0651 | +0.0059 [-0.0037, +0.0145] | -0.0041 [-0.0132, +0.0042] | 0.847 | 0.512 | no |
| 3 | 0.446 (147 of 1871 days never flag) | 151 | 0.464 | 0.424 | 0.0681 | +0.0026 [-0.0077, +0.0113] | -0.0037 [-0.0135, +0.0048] | 0.825 | 0.414 | no |
| 4 | 0.492 (126 of 1870 days never flag) | 181 | 0.493 | 0.376 | 0.0665 | +0.0044 [-0.0037, +0.0124] | -0.0041 [-0.0125, +0.0038] | 0.841 | 0.428 | yes |
| 5 | 0.457 (147 of 1869 days never flag) | 160 | 0.442 | 0.381 | 0.0668 | +0.0041 [-0.0030, +0.0112] | -0.0034 [-0.0104, +0.0038] | 0.824 | 0.385 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.690 (climatology 0.457, difference +0.2325 [+0.1031, +0.3727]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0276, +0.0683], realised minus predicted -0.0277 [-0.0574, +0.0058]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.422 | 0.3266 | 0.2720 | +0.0107 [-0.0360, +0.0556] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2027 | 0.0159 | -0.0126 [-0.0343, +0.0048] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0070 | 0.0200 | +0.0029 [-0.0023, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0590 | 0.1165 | +0.0275 [+0.0060, +0.0539] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0087 [+0.0070, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1124 | 0.0031 | +0.0088 [+0.0027, +0.0148] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1506 | 0.4146 | 0.0653 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.424 | 0.3219 | 0.2474 | +0.0062 [-0.0333, +0.0455] |
| day_type | month_end | 150 | 17 | 0.706 | 0.667 | 0.1083 | 0.1133 | +0.0403 [+0.0134, +0.0679] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.360 | 0.1025 | 0.0630 | +0.0011 [-0.0097, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0459, +0.1450] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0403, +0.1137] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2978 | 0.2213 |

## risk_logistic_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.281, 0.650] | 0.284 | 6.04 flat / 2.81 weighted | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.269 | 4.77 flat / 2.15 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.115 [2.351, 6.458] | 1.731 [0.928, 2.813] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.885 [2.875, 7.550] | 2.135 [1.135, 3.529] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.618] | 3.885 [2.083, 6.263] | 1.673 [0.851, 2.767] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.615 [2.000, 5.957] | 1.673 [0.869, 2.834] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.154 [2.333, 6.601] | 1.788 [0.956, 2.917] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.833] | 6.706 [3.879, 10.934] | 2.735 [1.428, 4.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 189 | 0.586 | 0.434 | 0.0580 | +0.0134 [+0.0062, +0.0217] | -0.0017 [-0.0075, +0.0049] | 0.846 | 0.524 | no |
| 2 | 0.381 (147 of 1872 days never flag) | 212 | 0.612 | 0.401 | 0.0683 | +0.0028 [-0.0032, +0.0089] | -0.0072 [-0.0133, -0.0009] | 0.782 | 0.538 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 175 | 0.536 | 0.423 | 0.0721 | -0.0014 [-0.0081, +0.0050] | -0.0078 [-0.0146, -0.0012] | 0.732 | 0.478 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 156 | 0.449 | 0.397 | 0.0712 | -0.0004 [-0.0070, +0.0060] | -0.0089 [-0.0162, -0.0018] | 0.754 | 0.395 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 182 | 0.536 | 0.407 | 0.0719 | -0.0009 [-0.0069, +0.0048] | -0.0085 [-0.0150, -0.0020] | 0.725 | 0.474 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.457, difference +0.1361 [+0.0069, +0.2496]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0972, ΔBrier vs climatology +0.0322 [+0.0168, +0.0486], realised minus predicted -0.0258 [-0.0610, +0.0114]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.435 | 0.2948 | 0.2720 | +0.0350 [+0.0048, +0.0709] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2147 | 0.0159 | -0.0118 [-0.0256, +0.0004] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0115 | 0.0200 | +0.0029 [-0.0022, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0596 | 0.1165 | +0.0259 [+0.0065, +0.0493] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0199 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1334 | 0.0031 | +0.0033 [-0.0018, +0.0090] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1375 | 0.4146 | 0.0493 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.667 | 0.429 | 0.2950 | 0.2474 | +0.0286 [+0.0016, +0.0611] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1110 | 0.1133 | +0.0370 [+0.0118, +0.0646] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.378 | 0.1064 | 0.0630 | +0.0064 [-0.0005, +0.0150] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0433, +0.1471] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1332 | 0.1461 | +0.0711 [+0.0389, +0.1082] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2876 | 0.2213 |

## risk_logistic_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.710] | 0.276 | 5.88 flat / 2.63 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.269 | 4.73 flat / 2.14 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.846 [2.259, 6.000] | 1.683 [0.933, 2.763] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.600] | 4.308 [2.525, 6.667] | 1.663 [0.910, 2.761] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.692 [1.969, 6.000] | 1.481 [0.722, 2.558] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.522] | 3.423 [1.829, 5.501] | 1.500 [0.771, 2.584] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.167, 0.533] | 4.231 [2.429, 6.682] | 1.904 [1.075, 3.071] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.706 [4.042, 10.734] | 2.706 [1.518, 4.617] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.331 (105 of 1873 days never flag) | 179 | 0.564 | 0.441 | 0.0576 | +0.0138 [+0.0062, +0.0218] | -0.0012 [-0.0074, +0.0052] | 0.848 | 0.507 | no |
| 2 | 0.361 (147 of 1872 days never flag) | 197 | 0.612 | 0.431 | 0.0674 | +0.0036 [-0.0024, +0.0100] | -0.0064 [-0.0119, -0.0005] | 0.783 | 0.547 | no |
| 3 | 0.424 (147 of 1871 days never flag) | 168 | 0.522 | 0.429 | 0.0698 | +0.0009 [-0.0045, +0.0063] | -0.0054 [-0.0107, +0.0005] | 0.735 | 0.466 | no |
| 4 | 0.43 (147 of 1870 days never flag) | 150 | 0.442 | 0.407 | 0.0699 | +0.0009 [-0.0048, +0.0066] | -0.0075 [-0.0133, -0.0019] | 0.755 | 0.391 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 184 | 0.536 | 0.402 | 0.0724 | -0.0015 [-0.0077, +0.0047] | -0.0090 [-0.0163, -0.0020] | 0.730 | 0.473 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.551 (climatology 0.457, difference +0.0939 [-0.0117, +0.1875]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0345 [+0.0193, +0.0507], realised minus predicted -0.0253 [-0.0603, +0.0117]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.447 | 0.2977 | 0.2720 | +0.0367 [+0.0030, +0.0701] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2108 | 0.0159 | -0.0106 [-0.0241, +0.0012] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0358 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0115 | 0.0200 | +0.0029 [-0.0020, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0578 | 0.1165 | +0.0254 [+0.0060, +0.0476] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0199 | 0.0048 | +0.0082 [+0.0066, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1312 | 0.0031 | +0.0036 [-0.0018, +0.0094] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1357 | 0.4146 | 0.0462 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.436 | 0.2960 | 0.2474 | +0.0303 [+0.0006, +0.0605] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1090 | 0.1133 | +0.0395 [+0.0138, +0.0665] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.380 | 0.1068 | 0.0630 | +0.0065 [-0.0012, +0.0147] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3205 | 0.2903 | +0.0964 [+0.0460, +0.1407] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0423, +0.1115] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2935 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.762] | 0.269 | 5.69 flat / 2.66 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.364, 0.714] | 0.269 | 4.85 flat / 2.41 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.115 [2.400, 6.643] | 1.731 [0.969, 2.914] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.194, 0.517] | 3.462 [1.893, 5.778] | 1.538 [0.800, 2.663] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.292, 0.643] | 3.615 [2.083, 5.880] | 1.635 [0.906, 2.766] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 4.385 [2.615, 7.000] | 2.144 [1.219, 3.607] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 3.500 [1.952, 5.808] | 1.635 [0.875, 2.811] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.353 [3.769, 10.463] | 2.662 [1.461, 4.584] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 2.667 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 189 | 0.586 | 0.434 | 0.0580 | +0.0134 [+0.0057, +0.0213] | -0.0017 [-0.0078, +0.0046] | 0.846 | 0.524 | no |
| 2 | 0.394 (147 of 1872 days never flag) | 156 | 0.475 | 0.423 | 0.0629 | +0.0082 [+0.0014, +0.0149] | -0.0018 [-0.0083, +0.0049] | 0.811 | 0.423 | no |
| 3 | 0.443 (126 of 1871 days never flag) | 166 | 0.522 | 0.434 | 0.0654 | +0.0053 [-0.0005, +0.0115] | -0.0011 [-0.0070, +0.0052] | 0.766 | 0.467 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 185 | 0.514 | 0.384 | 0.0652 | +0.0056 [-0.0007, +0.0118] | -0.0028 [-0.0095, +0.0039] | 0.790 | 0.449 | yes |
| 5 | 0.387 (147 of 1869 days never flag) | 155 | 0.464 | 0.413 | 0.0664 | +0.0046 [-0.0017, +0.0108] | -0.0030 [-0.0094, +0.0041] | 0.775 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.688 (climatology 0.457, difference +0.2306 [+0.1064, +0.3600]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0854, ΔBrier vs climatology +0.0441 [+0.0266, +0.0647], realised minus predicted -0.0465 [-0.0785, -0.0127]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.435 | 0.2948 | 0.2720 | +0.0350 [+0.0041, +0.0699] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2147 | 0.0159 | -0.0118 [-0.0254, -0.0001] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0118] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0115 | 0.0200 | +0.0029 [-0.0022, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0596 | 0.1165 | +0.0259 [+0.0057, +0.0500] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0199 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1334 | 0.0031 | +0.0033 [-0.0020, +0.0087] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1375 | 0.4146 | 0.0493 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.667 | 0.429 | 0.2950 | 0.2474 | +0.0286 [+0.0005, +0.0585] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1110 | 0.1133 | +0.0370 [+0.0113, +0.0640] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.378 | 0.1064 | 0.0630 | +0.0064 [-0.0010, +0.0143] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1506] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1332 | 0.1461 | +0.0711 [+0.0377, +0.1093] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2876 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.762] | 0.295 | 6.23 flat / 2.87 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.321, 0.677] | 0.269 | 4.73 flat / 2.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.846 [2.231, 6.106] | 1.683 [0.904, 2.751] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.333, 0.686] | 4.577 [2.815, 6.875] | 1.923 [1.132, 3.046] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.174, 0.545] | 3.115 [1.545, 5.381] | 1.385 [0.643, 2.409] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.385 [2.500, 6.900] | 2.163 [1.150, 3.633] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.538] | 3.538 [1.882, 5.822] | 1.702 [0.896, 2.875] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.929] | 7.176 [4.391, 11.273] | 2.971 [1.710, 4.917] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 4.444 [2.400, 9.202] | 2.667 [1.271, 6.250] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.331 (105 of 1873 days never flag) | 179 | 0.564 | 0.441 | 0.0576 | +0.0138 [+0.0061, +0.0216] | -0.0012 [-0.0074, +0.0055] | 0.848 | 0.507 | no |
| 2 | 0.386 (126 of 1872 days never flag) | 200 | 0.583 | 0.405 | 0.0625 | +0.0085 [+0.0021, +0.0151] | -0.0015 [-0.0078, +0.0055] | 0.813 | 0.514 | no |
| 3 | 0.446 (147 of 1871 days never flag) | 145 | 0.464 | 0.441 | 0.0649 | +0.0058 [-0.0001, +0.0120] | -0.0005 [-0.0069, +0.0059] | 0.766 | 0.417 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 182 | 0.493 | 0.374 | 0.0650 | +0.0058 [-0.0004, +0.0119] | -0.0027 [-0.0092, +0.0039] | 0.789 | 0.427 | no |
| 5 | 0.438 (147 of 1869 days never flag) | 155 | 0.457 | 0.406 | 0.0665 | +0.0044 [-0.0019, +0.0104] | -0.0031 [-0.0097, +0.0038] | 0.775 | 0.403 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.690 (climatology 0.457, difference +0.2325 [+0.1054, +0.3633]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0447 [+0.0263, +0.0654], realised minus predicted -0.0465 [-0.0772, -0.0132]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.447 | 0.2977 | 0.2720 | +0.0367 [+0.0032, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.2108 | 0.0159 | -0.0106 [-0.0239, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0358 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0115 | 0.0200 | +0.0029 [-0.0021, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0578 | 0.1165 | +0.0254 [+0.0063, +0.0474] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0199 | 0.0048 | +0.0082 [+0.0066, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1312 | 0.0031 | +0.0036 [-0.0016, +0.0096] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1357 | 0.4146 | +0.0462 [-0.0117, +0.1057] |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.436 | 0.2960 | 0.2474 | +0.0303 [+0.0009, +0.0611] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1090 | 0.1133 | +0.0395 [+0.0139, +0.0668] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.380 | 0.1068 | 0.0630 | +0.0065 [-0.0009, +0.0145] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3205 | 0.2903 | +0.0964 [+0.0465, +0.1429] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0426, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2935 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.720] | 0.358 | 6.69 flat / 3.21 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 5.50 flat / 2.75 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.280, 0.654] | 5.385 [3.360, 8.158] | 2.452 [1.422, 3.882] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.207, 0.583] | 5.038 [3.073, 7.770] | 2.212 [1.234, 3.579] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.583] | 3.885 [2.160, 6.263] | 1.654 [0.850, 2.750] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.575] | 4.615 [2.647, 7.333] | 2.394 [1.287, 3.953] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.500 [2.499, 7.240] | 2.115 [1.080, 3.588] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.941 [6.148, 13.333] | 3.897 [2.444, 6.058] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 2.444 [0.875, 6.008] | 1.917 [0.558, 5.100] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (126 of 1873 days never flag) | 217 | 0.550 | 0.355 | 0.0620 | +0.0094 [-0.0019, +0.0199] | -0.0056 [-0.0170, +0.0039] | 0.888 | 0.469 | no |
| 2 | 0.575 (147 of 1872 days never flag) | 216 | 0.612 | 0.394 | 0.0678 | +0.0033 [-0.0059, +0.0114] | -0.0067 [-0.0155, +0.0010] | 0.852 | 0.536 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 173 | 0.522 | 0.416 | 0.0707 | -0.0000 [-0.0103, +0.0099] | -0.0063 [-0.0168, +0.0034] | 0.851 | 0.463 | no |
| 4 | 0.519 (147 of 1870 days never flag) | 182 | 0.449 | 0.341 | 0.0688 | +0.0020 [-0.0061, +0.0094] | -0.0064 [-0.0146, +0.0015] | 0.838 | 0.380 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 190 | 0.529 | 0.384 | 0.0726 | -0.0016 [-0.0116, +0.0068] | -0.0092 [-0.0191, -0.0005] | 0.814 | 0.461 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.355 | 0.3264 | 0.2720 | +0.0018 [-0.0510, +0.0508] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1562 | 0.0159 | +0.0017 [-0.0245, +0.0223] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0111, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0001, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0628 | 0.1165 | +0.0242 [+0.0067, +0.0464] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0024 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0706 | 0.0031 | +0.0216 [+0.0162, +0.0270] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1023 | 0.4146 | 0.0458 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.355 | 0.3283 | 0.2474 | -0.0019 [-0.0477, +0.0402] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1090 | 0.1133 | +0.0382 [+0.0115, +0.0657] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.302 | 0.0915 | 0.0630 | +0.0017 [-0.0106, +0.0128] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0398, +0.1503] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1332 | 0.1461 | +0.0711 [+0.0382, +0.1087] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2778 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.714] | 0.358 | 6.69 flat / 3.12 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.611] | 0.269 | 5.19 flat / 2.48 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.567] | 4.923 [3.087, 7.333] | 2.260 [1.292, 3.522] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.962 [3.079, 7.542] | 2.135 [1.204, 3.435] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.885 [2.200, 6.161] | 1.635 [0.848, 2.738] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 4.077 [2.444, 6.303] | 1.904 [1.055, 3.037] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 3.962 [2.266, 6.306] | 1.712 [0.911, 2.868] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.706 [6.000, 13.000] | 3.779 [2.368, 5.900] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.889 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 203 | 0.536 | 0.369 | 0.0615 | +0.0099 [-0.0011, +0.0201] | -0.0052 [-0.0155, +0.0039] | 0.889 | 0.462 | no |
| 2 | 0.445 (147 of 1872 days never flag) | 216 | 0.626 | 0.403 | 0.0669 | +0.0041 [-0.0053, +0.0125] | -0.0059 [-0.0149, +0.0022] | 0.854 | 0.551 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 174 | 0.529 | 0.420 | 0.0683 | +0.0023 [-0.0087, +0.0117] | -0.0040 [-0.0143, +0.0053] | 0.854 | 0.471 | no |
| 4 | 0.43 (147 of 1870 days never flag) | 168 | 0.449 | 0.369 | 0.0675 | +0.0034 [-0.0044, +0.0103] | -0.0051 [-0.0131, +0.0022] | 0.839 | 0.388 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 176 | 0.529 | 0.415 | 0.0731 | -0.0022 [-0.0126, +0.0067] | -0.0097 [-0.0198, -0.0007] | 0.820 | 0.469 | no |

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
| regime | 2018-19 | 375 | 102 | 0.667 | 0.360 | 0.3293 | 0.2720 | +0.0035 [-0.0474, +0.0484] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1524 | 0.0159 | +0.0029 [-0.0224, +0.0236] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0112, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.636 | 0.0610 | 0.1165 | +0.0236 [+0.0065, +0.0443] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0685 | 0.0031 | +0.0218 [+0.0158, +0.0275] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1006 | 0.4146 | 0.0427 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.365 | 0.3293 | 0.2474 | -0.0002 [-0.0436, +0.0411] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1070 | 0.1133 | +0.0408 [+0.0139, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.303 | 0.0919 | 0.0630 | +0.0018 [-0.0104, +0.0126] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0473, +0.1441] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0406, +0.1106] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2837 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.760] | 0.288 | 6.12 flat / 2.97 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.254 | 4.46 flat / 2.24 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.645] | 5.385 [3.409, 8.200] | 2.452 [1.408, 3.955] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 4.615 [2.778, 7.228] | 2.135 [1.208, 3.563] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.258, 0.600] | 3.615 [2.105, 5.883] | 1.702 [0.935, 2.917] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 4.115 [2.367, 6.620] | 2.000 [1.060, 3.376] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.478] | 3.846 [2.103, 6.364] | 1.933 [0.969, 3.419] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 8.059 [5.312, 12.636] | 3.544 [2.144, 5.834] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.444 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (126 of 1873 days never flag) | 217 | 0.550 | 0.355 | 0.0620 | +0.0094 [-0.0018, +0.0197] | -0.0056 [-0.0156, +0.0034] | 0.888 | 0.469 | no |
| 2 | 0.458 (126 of 1872 days never flag) | 188 | 0.489 | 0.362 | 0.0635 | +0.0075 [-0.0020, +0.0163] | -0.0025 [-0.0121, +0.0063] | 0.865 | 0.420 | no |
| 3 | 0.852 (126 of 1871 days never flag) | 164 | 0.507 | 0.427 | 0.0654 | +0.0053 [-0.0052, +0.0143] | -0.0010 [-0.0120, +0.0083] | 0.863 | 0.453 | no |
| 4 | 0.53 (126 of 1870 days never flag) | 178 | 0.514 | 0.399 | 0.0637 | +0.0071 [-0.0008, +0.0145] | -0.0014 [-0.0098, +0.0065] | 0.854 | 0.453 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 162 | 0.449 | 0.383 | 0.0680 | +0.0029 [-0.0065, +0.0113] | -0.0046 [-0.0141, +0.0041] | 0.840 | 0.392 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.355 | 0.3264 | 0.2720 | +0.0018 [-0.0497, +0.0508] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1562 | 0.0159 | +0.0017 [-0.0241, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0003, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0628 | 0.1165 | +0.0242 [+0.0064, +0.0470] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0024 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0706 | 0.0031 | +0.0216 [+0.0159, +0.0269] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1023 | 0.4146 | 0.0458 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.355 | 0.3283 | 0.2474 | -0.0019 [-0.0448, +0.0391] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1090 | 0.1133 | +0.0382 [+0.0124, +0.0666] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.302 | 0.0915 | 0.0630 | +0.0017 [-0.0103, +0.0129] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0391, +0.1510] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1332 | 0.1461 | +0.0711 [+0.0367, +0.1093] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2778 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.758] | 0.297 | 6.27 flat / 2.96 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.640] | 0.235 | 4.27 flat / 2.12 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.923 [3.000, 7.522] | 2.260 [1.258, 3.603] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 5.115 [3.159, 7.833] | 2.279 [1.326, 3.650] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.481] | 3.154 [1.583, 5.552] | 1.462 [0.682, 2.683] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.192 [2.423, 6.852] | 2.067 [1.103, 3.531] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.167, 0.533] | 3.577 [1.838, 6.131] | 1.750 [0.808, 3.193] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.118 [5.235, 12.447] | 3.559 [2.156, 5.750] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.778 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (105 of 1873 days never flag) | 203 | 0.536 | 0.369 | 0.0615 | +0.0099 [-0.0016, +0.0204] | -0.0052 [-0.0155, +0.0043] | 0.889 | 0.462 | no |
| 2 | 0.45 (126 of 1872 days never flag) | 215 | 0.590 | 0.381 | 0.0631 | +0.0079 [-0.0013, +0.0163] | -0.0021 [-0.0110, +0.0065] | 0.867 | 0.513 | no |
| 3 | 0.863 (147 of 1871 days never flag) | 144 | 0.449 | 0.431 | 0.0648 | +0.0059 [-0.0050, +0.0150] | -0.0005 [-0.0114, +0.0085] | 0.864 | 0.402 | no |
| 4 | 0.492 (126 of 1870 days never flag) | 176 | 0.486 | 0.381 | 0.0636 | +0.0072 [-0.0007, +0.0147] | -0.0012 [-0.0092, +0.0067] | 0.854 | 0.423 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 154 | 0.442 | 0.396 | 0.0682 | +0.0028 [-0.0068, +0.0114] | -0.0048 [-0.0146, +0.0042] | 0.840 | 0.388 | no |

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
| regime | 2018-19 | 375 | 102 | 0.667 | 0.360 | 0.3293 | 0.2720 | +0.0035 [-0.0478, +0.0524] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1524 | 0.0159 | +0.0029 [-0.0224, +0.0237] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0034 | 0.0200 | +0.0040 [+0.0005, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.636 | 0.0610 | 0.1165 | +0.0236 [+0.0061, +0.0466] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0685 | 0.0031 | +0.0218 [+0.0160, +0.0276] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1006 | 0.4146 | 0.0427 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.365 | 0.3293 | 0.2474 | -0.0002 [-0.0444, +0.0405] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1070 | 0.1133 | +0.0408 [+0.0149, +0.0683] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.303 | 0.0919 | 0.0630 | +0.0018 [-0.0104, +0.0132] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3205 | 0.2903 | +0.0964 [+0.0477, +0.1427] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0406, +0.1119] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2837 | 0.2213 |

## risk_logistic_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.719] | 0.363 | 6.77 flat / 3.29 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.276, 0.640] | 0.269 | 5.50 flat / 2.75 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.281, 0.650] | 5.654 [3.565, 8.208] | 2.606 [1.559, 3.950] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.923 [3.000, 7.546] | 2.212 [1.273, 3.587] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.846 [2.193, 6.177] | 1.635 [0.847, 2.766] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.259, 0.593] | 4.154 [2.400, 6.391] | 2.038 [1.131, 3.269] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.562] | 4.462 [2.593, 7.134] | 2.077 [1.115, 3.531] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 8.941 [6.000, 13.154] | 3.897 [2.409, 6.000] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 2.139 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (126 of 1873 days never flag) | 229 | 0.586 | 0.358 | 0.0554 | +0.0160 [+0.0082, +0.0243] | +0.0009 [-0.0058, +0.0075] | 0.880 | 0.501 | no |
| 2 | 0.448 (147 of 1872 days never flag) | 214 | 0.619 | 0.402 | 0.0642 | +0.0068 [+0.0001, +0.0135] | -0.0032 [-0.0097, +0.0031] | 0.841 | 0.545 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 172 | 0.522 | 0.419 | 0.0668 | +0.0039 [-0.0031, +0.0106] | -0.0024 [-0.0093, +0.0044] | 0.833 | 0.464 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 171 | 0.457 | 0.368 | 0.0665 | +0.0043 [-0.0024, +0.0108] | -0.0041 [-0.0115, +0.0033] | 0.820 | 0.394 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 189 | 0.529 | 0.386 | 0.0684 | +0.0026 [-0.0037, +0.0083] | -0.0050 [-0.0119, +0.0014] | 0.788 | 0.462 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.355 | 0.2920 | 0.2720 | +0.0330 [-0.0021, +0.0683] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1792 | 0.0159 | +0.0014 [-0.0168, +0.0162] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0037 | 0.0200 | +0.0040 [+0.0002, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0604 | 0.1165 | +0.0274 [+0.0071, +0.0533] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0050 | 0.0048 | +0.0093 [+0.0077, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0934 | 0.0031 | +0.0169 [+0.0120, +0.0221] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1096 | 0.4146 | +0.0477 [+0.0041, +0.0965] |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.357 | 0.2978 | 0.2474 | +0.0272 [-0.0032, +0.0594] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1095 | 0.1133 | +0.0383 [+0.0115, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.303 | 0.0889 | 0.0630 | +0.0093 [+0.0016, +0.0178] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.571 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1501] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1332 | 0.1461 | +0.0711 [+0.0387, +0.1075] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2436 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.349 | 6.54 flat / 3.11 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.609] | 0.269 | 4.88 flat / 2.27 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 5.154 [3.321, 7.750] | 2.462 [1.484, 3.931] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 4.808 [2.931, 7.566] | 2.096 [1.198, 3.424] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.616] | 3.692 [2.000, 6.101] | 1.481 [0.750, 2.552] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.000 [2.343, 6.407] | 1.885 [1.046, 3.120] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.546] | 3.923 [2.194, 6.389] | 1.673 [0.879, 2.869] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 8.706 [5.938, 13.223] | 3.779 [2.385, 6.025] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.444 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.414 (105 of 1873 days never flag) | 212 | 0.557 | 0.368 | 0.0550 | +0.0164 [+0.0085, +0.0250] | +0.0013 [-0.0052, +0.0081] | 0.882 | 0.480 | no |
| 2 | 0.445 (147 of 1872 days never flag) | 209 | 0.604 | 0.402 | 0.0634 | +0.0077 [+0.0013, +0.0144] | -0.0023 [-0.0085, +0.0039] | 0.842 | 0.532 | no |
| 3 | 0.424 (147 of 1871 days never flag) | 169 | 0.529 | 0.432 | 0.0644 | +0.0063 [+0.0003, +0.0123] | -0.0001 [-0.0060, +0.0061] | 0.834 | 0.474 | no |
| 4 | 0.43 (147 of 1870 days never flag) | 166 | 0.449 | 0.373 | 0.0652 | +0.0056 [-0.0003, +0.0114] | -0.0028 [-0.0091, +0.0035] | 0.821 | 0.389 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 175 | 0.529 | 0.417 | 0.0689 | +0.0020 [-0.0049, +0.0086] | -0.0055 [-0.0129, +0.0017] | 0.792 | 0.470 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.565 (climatology 0.457, difference +0.1076 [+0.0058, +0.2018]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0899, ΔBrier vs climatology +0.0395 [+0.0247, +0.0557], realised minus predicted +0.0069 [-0.0256, +0.0422]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.360 | 0.2949 | 0.2720 | +0.0348 [-0.0003, +0.0707] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1753 | 0.0159 | +0.0026 [-0.0142, +0.0183] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0040 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0586 | 0.1165 | +0.0268 [+0.0076, +0.0506] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0049 | 0.0048 | +0.0094 [+0.0077, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0912 | 0.0031 | +0.0171 [+0.0119, +0.0229] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1079 | 0.4146 | 0.0446 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.361 | 0.2988 | 0.2474 | +0.0290 [-0.0012, +0.0611] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1075 | 0.1133 | +0.0408 [+0.0150, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.302 | 0.0893 | 0.0630 | +0.0094 [+0.0015, +0.0180] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3205 | 0.2903 | +0.0964 [+0.0443, +0.1443] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0413, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2495 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.394, 0.750] | 0.282 | 6.00 flat / 2.88 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.667] | 0.246 | 4.38 flat / 2.16 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 5.654 [3.559, 8.280] | 2.606 [1.535, 4.015] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.636] | 4.115 [2.458, 6.450] | 1.808 [1.026, 2.948] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.593] | 3.538 [2.000, 5.667] | 1.615 [0.875, 2.708] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 4.231 [2.448, 6.708] | 2.058 [1.101, 3.426] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.481] | 3.269 [1.756, 5.474] | 1.490 [0.741, 2.611] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.059 [5.071, 12.154] | 3.544 [2.015, 5.656] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 2.111 [0.800, 5.000] | 1.639 [0.500, 4.250] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (126 of 1873 days never flag) | 229 | 0.586 | 0.358 | 0.0554 | +0.0160 [+0.0080, +0.0246] | +0.0009 [-0.0054, +0.0075] | 0.880 | 0.501 | no |
| 2 | 0.448 (126 of 1872 days never flag) | 177 | 0.504 | 0.395 | 0.0594 | +0.0117 [+0.0045, +0.0190] | +0.0017 [-0.0055, +0.0087] | 0.857 | 0.442 | no |
| 3 | 0.443 (126 of 1871 days never flag) | 163 | 0.514 | 0.436 | 0.0609 | +0.0098 [+0.0029, +0.0165] | +0.0035 [-0.0031, +0.0102] | 0.847 | 0.461 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 181 | 0.514 | 0.392 | 0.0610 | +0.0098 [+0.0031, +0.0165] | +0.0013 [-0.0060, +0.0084] | 0.842 | 0.451 | no |
| 5 | 0.41 (147 of 1869 days never flag) | 148 | 0.457 | 0.426 | 0.0634 | +0.0075 [+0.0014, +0.0138] | +0.0000 [-0.0065, +0.0067] | 0.825 | 0.407 | no |

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
| regime | 2018-19 | 375 | 102 | 0.735 | 0.355 | 0.2920 | 0.2720 | +0.0330 [-0.0004, +0.0702] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1792 | 0.0159 | +0.0014 [-0.0162, +0.0167] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0144] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0037 | 0.0200 | +0.0040 [+0.0003, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0604 | 0.1165 | +0.0274 [+0.0072, +0.0531] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0050 | 0.0048 | +0.0093 [+0.0077, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0934 | 0.0031 | +0.0169 [+0.0120, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1096 | 0.4146 | +0.0477 [+0.0039, +0.0999] |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.357 | 0.2978 | 0.2474 | +0.0272 [-0.0035, +0.0605] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1095 | 0.1133 | +0.0383 [+0.0121, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.303 | 0.0889 | 0.0630 | +0.0093 [+0.0014, +0.0178] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.571 | 0.3198 | 0.2903 | +0.0954 [+0.0393, +0.1501] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1332 | 0.1461 | +0.0711 [+0.0405, +0.1094] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2436 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.286 | 6.08 flat / 2.90 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.640] | 0.231 | 4.23 flat / 2.11 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 5.154 [3.200, 7.760] | 2.462 [1.399, 3.938] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.333, 0.679] | 4.769 [2.903, 7.311] | 2.067 [1.200, 3.307] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.150, 0.472] | 3.077 [1.543, 5.273] | 1.375 [0.646, 2.462] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 4.154 [2.332, 6.751] | 2.048 [1.062, 3.488] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 3.731 [1.968, 6.365] | 1.875 [0.885, 3.320] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.118 [5.200, 12.432] | 3.559 [2.102, 5.825] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.222 (no interval) | 1.667 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.414 (105 of 1873 days never flag) | 212 | 0.557 | 0.368 | 0.0550 | +0.0164 [+0.0084, +0.0250] | +0.0013 [-0.0055, +0.0078] | 0.882 | 0.480 | no |
| 2 | 0.448 (126 of 1872 days never flag) | 207 | 0.597 | 0.401 | 0.0590 | +0.0121 [+0.0046, +0.0190] | +0.0021 [-0.0050, +0.0092] | 0.859 | 0.526 | no |
| 3 | 0.446 (147 of 1871 days never flag) | 143 | 0.457 | 0.441 | 0.0603 | +0.0104 [+0.0038, +0.0170] | +0.0041 [-0.0025, +0.0108] | 0.848 | 0.410 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 175 | 0.486 | 0.383 | 0.0609 | +0.0100 [+0.0037, +0.0164] | +0.0015 [-0.0050, +0.0085] | 0.841 | 0.423 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 158 | 0.442 | 0.386 | 0.0635 | +0.0074 [+0.0009, +0.0136] | -0.0001 [-0.0072, +0.0068] | 0.825 | 0.386 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.690 (climatology 0.457, difference +0.2325 [+0.1076, +0.3648]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0802, ΔBrier vs climatology +0.0493 [+0.0310, +0.0688], realised minus predicted -0.0147 [-0.0461, +0.0174]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.360 | 0.2949 | 0.2720 | +0.0348 [+0.0000, +0.0727] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.1753 | 0.0159 | +0.0026 [-0.0159, +0.0173] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0138 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0040 [+0.0005, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0586 | 0.1165 | +0.0268 [+0.0073, +0.0513] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0049 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0912 | 0.0031 | +0.0171 [+0.0120, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1079 | 0.4146 | 0.0446 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.361 | 0.2988 | 0.2474 | +0.0290 [-0.0021, +0.0612] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1075 | 0.1133 | +0.0408 [+0.0146, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.302 | 0.0893 | 0.0630 | +0.0094 [+0.0012, +0.0179] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3205 | 0.2903 | +0.0964 [+0.0461, +0.1405] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0412, +0.1126] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2495 | 0.2213 |

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

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 3.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 8.3 over 1035 days; regime_2021-23: 12.1 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 4.1 over 1035 days; regime_2021-23: 5.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.457, difference +0.1837 [+0.0710, +0.2966]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1101, ΔBrier vs climatology +0.0193 [+0.0086, +0.0311], realised minus predicted +0.0574 [+0.0238, +0.0943]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.588 | 0.1014 | 0.2720 | -0.0090 [-0.0307, +0.0131] |
| regime | 2020 | 251 | 4 | 0.250 | 0.025 | 0.0608 | 0.0159 | +0.0085 [-0.0055, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0110 | 0.0200 | +0.0019 [-0.0033, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0481 | 0.1165 | +0.0239 [+0.0054, +0.0480] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.167 | 0.0056 | 0.0048 | +0.0087 [+0.0068, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.031 | 0.0339 | 0.0031 | +0.0134 [+0.0040, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1154 | 0.4146 | 0.0760 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.542 | 0.1028 | 0.2474 | -0.0022 [-0.0208, +0.0174] |
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

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.457, difference +0.1367 [-0.0372, +0.2817]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1051, ΔBrier vs climatology +0.0244 [+0.0124, +0.0374], realised minus predicted +0.0555 [+0.0217, +0.0899]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1199 | 0.2720 | -0.0169 [-0.0413, +0.0085] |
| regime | 2020 | 251 | 4 | 0.250 | 0.030 | 0.0469 | 0.0159 | +0.0220 [+0.0121, +0.0313] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0048, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0509 | 0.1165 | +0.0242 [+0.0051, +0.0465] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.036 | 0.0271 | 0.0031 | +0.0196 [+0.0120, +0.0263] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.0959 | 0.4146 | 0.0536 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.580 | 0.1179 | 0.2474 | -0.0036 [-0.0259, +0.0196] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1397 | 0.1133 | +0.0244 [-0.0130, +0.0627] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.462 | 0.0159 | 0.0630 | +0.0028 [-0.0028, +0.0082] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3234 | 0.2903 | +0.0724 [-0.0002, +0.1368] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.370 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1034] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.792] | 0.423 | 8.15 flat / 4.08 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.368, 0.714] | 0.368 | 6.88 flat / 3.38 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.758] | 4.846 [3.153, 7.292] | 2.231 [1.396, 3.459] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 4.269 [2.806, 6.391] | 1.587 [1.043, 2.381] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.679] | 5.615 [3.652, 8.500] | 2.635 [1.603, 4.195] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.643] | 4.577 [2.967, 7.002] | 2.048 [1.266, 3.251] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 5.231 [3.428, 7.858] | 2.365 [1.500, 3.671] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 7.118 [4.416, 11.182] | 2.926 [1.703, 4.940] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.111 (no interval) | 6.250 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 218 | 0.657 | 0.422 | 0.0531 | +0.0183 [+0.0099, +0.0272] | +0.0032 [-0.0028, +0.0091] | 0.880 | 0.584 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 206 | 0.683 | 0.461 | 0.0601 | +0.0109 [+0.0048, +0.0174] | +0.0009 [-0.0038, +0.0057] | 0.846 | 0.619 | yes |
| 3 | 0.25 (126 of 1871 days never flag) | 239 | 0.674 | 0.389 | 0.0609 | +0.0098 [+0.0042, +0.0160] | +0.0035 [-0.0017, +0.0089] | 0.839 | 0.590 | yes |
| 4 | 0.255 (126 of 1870 days never flag) | 197 | 0.565 | 0.396 | 0.0594 | +0.0114 [+0.0051, +0.0183] | +0.0029 [-0.0025, +0.0088] | 0.849 | 0.497 | yes |
| 5 | 0.325 (126 of 1869 days never flag) | 224 | 0.638 | 0.393 | 0.0604 | +0.0106 [+0.0045, +0.0168] | +0.0030 [-0.0021, +0.0089] | 0.840 | 0.559 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.638 (climatology 0.457, difference +0.1812 [+0.0344, +0.3293]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0426 [+0.0255, +0.0618], realised minus predicted -0.0187 [-0.0484, +0.0128]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.456 | 0.2613 | 0.2720 | +0.0388 [+0.0076, +0.0711] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.1496 | 0.0159 | +0.0057 [-0.0080, +0.0179] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0215 | 0.0000 | +0.0130 [+0.0112, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0419 | 0.0200 | -0.0015 [-0.0086, +0.0039] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.567 | 0.1272 | 0.1165 | +0.0361 [+0.0035, +0.0761] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0266 | 0.0048 | +0.0074 [+0.0051, +0.0095] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0917 | 0.0031 | +0.0122 [+0.0038, +0.0191] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2801 | 0.4146 | +0.1230 [-0.0069, +0.2480] |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.439 | 0.2642 | 0.2474 | +0.0374 [+0.0092, +0.0655] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1490 | 0.1133 | +0.0296 [-0.0091, +0.0687] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.383 | 0.0893 | 0.0630 | +0.0139 [+0.0066, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3234 | 0.2903 | +0.0724 [-0.0026, +0.1384] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.2039 | 0.1461 | +0.0602 [+0.0211, +0.1061] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.824] | 0.399 | 7.69 flat / 3.90 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.274 | 5.88 flat / 2.97 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.676] | 3.885 [2.774, 5.696] | 1.865 [1.227, 2.989] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 3.538 [2.285, 5.333] | 1.462 [0.932, 2.271] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.227, 0.536] | 3.654 [2.333, 5.572] | 1.760 [1.099, 2.800] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.542] | 3.846 [2.679, 5.651] | 1.865 [1.250, 2.868] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.321, 0.667] | 4.154 [2.800, 6.177] | 2.000 [1.318, 3.096] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.412 [4.250, 9.900] | 2.500 [1.629, 3.947] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.167, 0.714] | 10.111 [6.498, 21.250] | 6.556 [3.886, 15.381] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 186 | 0.607 | 0.457 | 0.0549 | +0.0165 [+0.0089, +0.0248] | +0.0014 [-0.0045, +0.0074] | 0.793 | 0.549 | no |
| 2 | 0.431 (147 of 1872 days never flag) | 167 | 0.540 | 0.449 | 0.0624 | +0.0087 [+0.0021, +0.0154] | -0.0013 [-0.0065, +0.0039] | 0.753 | 0.486 | no |
| 3 | 0.169 (126 of 1871 days never flag) | 165 | 0.507 | 0.424 | 0.0609 | +0.0098 [+0.0034, +0.0159] | +0.0035 [-0.0022, +0.0089] | 0.755 | 0.452 | no |
| 4 | 0.194 (126 of 1870 days never flag) | 166 | 0.478 | 0.398 | 0.0603 | +0.0105 [+0.0042, +0.0168] | +0.0021 [-0.0032, +0.0074] | 0.767 | 0.421 | no |
| 5 | 0.218 (126 of 1869 days never flag) | 183 | 0.543 | 0.410 | 0.0610 | +0.0099 [+0.0038, +0.0166] | +0.0024 [-0.0032, +0.0079] | 0.754 | 0.481 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.611 (climatology 0.457, difference +0.1539 [-0.0041, +0.3022]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0888, ΔBrier vs climatology +0.0407 [+0.0240, +0.0588], realised minus predicted +0.0265 [-0.0007, +0.0545]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.525 | 0.1916 | 0.2720 | +0.0232 [-0.0055, +0.0539] |
| regime | 2020 | 251 | 4 | 0.250 | 0.037 | 0.0545 | 0.0159 | +0.0147 [-0.0015, +0.0294] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0067 | 0.0000 | +0.0134 [+0.0115, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0243 | 0.0200 | -0.0014 [-0.0092, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.556 | 0.1021 | 0.1165 | +0.0353 [+0.0043, +0.0720] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0126 | 0.0048 | +0.0076 [+0.0051, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0321 | 0.0031 | +0.0182 [+0.0098, +0.0252] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.667 | 0.2513 | 0.4146 | +0.1209 [-0.0095, +0.2456] |
| scarcity_state | 3 | 473 | 117 | 0.632 | 0.500 | 0.1866 | 0.2474 | +0.0256 [+0.0006, +0.0513] |
| day_type | month_end | 150 | 17 | 0.882 | 0.517 | 0.1435 | 0.1133 | +0.0301 [-0.0079, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.440 | 0.0451 | 0.0630 | +0.0117 [+0.0052, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3234 | 0.2903 | +0.0724 [+0.0022, +0.1388] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2039 | 0.1461 | +0.0602 [+0.0201, +0.1035] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.413 | 7.92 flat / 4.05 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.682] | 0.354 | 6.69 flat / 3.34 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 4.846 [3.119, 7.257] | 2.231 [1.410, 3.536] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.423 [2.645, 6.842] | 1.827 [1.040, 2.968] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.038 [3.000, 7.924] | 2.404 [1.348, 4.146] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 4.769 [3.031, 7.333] | 2.288 [1.378, 3.688] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.643] | 5.346 [3.405, 8.002] | 2.462 [1.535, 3.909] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.588 [5.812, 13.000] | 3.794 [2.359, 6.146] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.667 (no interval) | 4.528 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 213 | 0.621 | 0.408 | 0.0534 | +0.0180 [+0.0110, +0.0257] | +0.0030 [-0.0026, +0.0089] | 0.865 | 0.549 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 204 | 0.640 | 0.436 | 0.0592 | +0.0119 [+0.0064, +0.0181] | +0.0019 [-0.0028, +0.0068] | 0.825 | 0.574 | yes |
| 3 | 0.248 (126 of 1871 days never flag) | 213 | 0.594 | 0.385 | 0.0592 | +0.0115 [+0.0060, +0.0179] | +0.0052 [-0.0003, +0.0113] | 0.832 | 0.519 | yes |
| 4 | 0.243 (126 of 1870 days never flag) | 197 | 0.529 | 0.371 | 0.0576 | +0.0132 [+0.0076, +0.0196] | +0.0048 [-0.0004, +0.0107] | 0.844 | 0.457 | no |
| 5 | 0.242 (126 of 1869 days never flag) | 223 | 0.609 | 0.377 | 0.0583 | +0.0126 [+0.0069, +0.0186] | +0.0051 [-0.0005, +0.0109] | 0.842 | 0.528 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 no (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.642 (climatology 0.457, difference +0.1849 [+0.0258, +0.3217]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0876, ΔBrier vs climatology +0.0419 [+0.0250, +0.0587], realised minus predicted -0.0100 [-0.0406, +0.0204]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.407 | 0.2424 | 0.2720 | +0.0320 [+0.0027, +0.0622] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1402 | 0.0159 | +0.0109 [+0.0007, +0.0208] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0131 [+0.0115, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0338 | 0.0200 | +0.0008 [-0.0048, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.652 | 0.1117 | 0.1165 | +0.0362 [+0.0072, +0.0731] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0226 | 0.0048 | +0.0081 [+0.0063, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0842 | 0.0031 | +0.0140 [+0.0062, +0.0206] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.700 | 0.2415 | 0.4146 | +0.1166 [-0.0026, +0.2258] |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.420 | 0.2448 | 0.2474 | +0.0340 [+0.0083, +0.0603] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1460 | 0.1133 | +0.0259 [-0.0105, +0.0645] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.366 | 0.0788 | 0.0630 | +0.0139 [+0.0074, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3234 | 0.2903 | +0.0724 [+0.0001, +0.1384] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1073] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2483 | 0.2213 |

## risk_quantile_skewt_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.781] | 0.409 | 7.85 flat / 3.88 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.704] | 0.349 | 6.62 flat / 3.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.391, 0.750] | 4.808 [3.114, 7.273] | 2.221 [1.370, 3.554] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.192 [2.733, 6.263] | 1.558 [1.020, 2.334] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.316, 0.677] | 5.462 [3.454, 8.421] | 2.558 [1.490, 4.161] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.462 [2.800, 6.812] | 1.971 [1.180, 3.134] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.316, 0.680] | 5.154 [3.348, 7.667] | 2.308 [1.446, 3.632] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 7.118 [4.454, 11.309] | 2.926 [1.658, 4.972] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.222 (no interval) | 5.694 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 217 | 0.657 | 0.424 | 0.0524 | +0.0190 [+0.0108, +0.0279] | +0.0039 [-0.0019, +0.0101] | 0.899 | 0.585 | yes |
| 2 | 0.276 (147 of 1872 days never flag) | 204 | 0.683 | 0.466 | 0.0594 | +0.0117 [+0.0057, +0.0184] | +0.0017 [-0.0028, +0.0066] | 0.877 | 0.621 | yes |
| 3 | 0.25 (126 of 1871 days never flag) | 235 | 0.674 | 0.396 | 0.0591 | +0.0115 [+0.0057, +0.0176] | +0.0052 [+0.0001, +0.0107] | 0.873 | 0.592 | yes |
| 4 | 0.255 (126 of 1870 days never flag) | 194 | 0.565 | 0.402 | 0.0582 | +0.0127 [+0.0061, +0.0193] | +0.0042 [-0.0015, +0.0097] | 0.878 | 0.498 | yes |
| 5 | 0.325 (126 of 1869 days never flag) | 222 | 0.638 | 0.396 | 0.0593 | +0.0116 [+0.0056, +0.0179] | +0.0041 [-0.0015, +0.0100] | 0.871 | 0.560 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.638 (climatology 0.457, difference +0.1812 [+0.0299, +0.3201]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0854, ΔBrier vs climatology +0.0441 [+0.0263, +0.0625], realised minus predicted +0.0046 [-0.0238, +0.0344]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.456 | 0.2613 | 0.2720 | +0.0388 [+0.0065, +0.0699] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.1496 | 0.0159 | +0.0057 [-0.0089, +0.0183] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0073 | 0.0000 | +0.0134 [+0.0117, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0047, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.567 | 0.1136 | 0.1165 | +0.0370 [+0.0052, +0.0781] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0917 | 0.0031 | +0.0122 [+0.0042, +0.0191] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2801 | 0.4146 | 0.1230 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.439 | 0.2642 | 0.2474 | +0.0374 [+0.0101, +0.0659] |
| day_type | month_end | 150 | 17 | 0.765 | 0.565 | 0.1470 | 0.1133 | +0.0296 [-0.0099, +0.0687] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.386 | 0.0761 | 0.0630 | +0.0147 [+0.0075, +0.0225] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3234 | 0.2903 | +0.0724 [+0.0018, +0.1358] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.2039 | 0.1461 | +0.0602 [+0.0217, +0.1047] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 19 | 0.731 [0.560, 0.882] | 0.423 | 8.73 flat / 4.55 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.741] | 0.385 | 7.12 flat / 3.59 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 17 | 0.654 [0.471, 0.833] | 5.500 [3.791, 8.182] | 2.663 [1.750, 4.260] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.652] | 5.308 [3.590, 8.060] | 2.337 [1.520, 3.714] |
| lead 3 alone (fail) | 26 | 14 | 0.538 [0.364, 0.720] | 6.038 [4.062, 9.084] | 3.019 [1.898, 4.844] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 4.885 [3.226, 7.435] | 2.308 [1.470, 3.708] |
| lead 5 alone (fail) | 26 | 14 | 0.538 [0.375, 0.714] | 5.385 [3.531, 8.150] | 2.587 [1.664, 4.047] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 0.963] | 7.353 [4.824, 11.602] | 3.015 [1.809, 5.156] |
| outside 2018-2019 | 9 | 6 | 0.667 [0.333, 0.938] | 11.333 [7.428, 22.752] | 7.444 [4.400, 16.750] |

Recall with equal weight per regime: 0.566 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 237 | 0.671 | 0.397 | 0.0536 | +0.0178 [+0.0117, +0.0241] | +0.0027 [-0.0032, +0.0089] | 0.879 | 0.589 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 234 | 0.691 | 0.410 | 0.0604 | +0.0107 [+0.0051, +0.0160] | +0.0007 [-0.0047, +0.0057] | 0.847 | 0.611 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 251 | 0.681 | 0.375 | 0.0601 | +0.0106 [+0.0055, +0.0159] | +0.0043 [-0.0012, +0.0098] | 0.840 | 0.591 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 205 | 0.565 | 0.380 | 0.0593 | +0.0116 [+0.0062, +0.0172] | +0.0031 [-0.0024, +0.0086] | 0.845 | 0.492 | no |
| 5 | 0.167 (126 of 1869 days never flag) | 228 | 0.638 | 0.386 | 0.0598 | +0.0112 [+0.0057, +0.0168] | +0.0036 [-0.0021, +0.0094] | 0.839 | 0.557 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.631 (climatology 0.457, difference +0.1737 [+0.0285, +0.2963]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0912, ΔBrier vs climatology +0.0383 [+0.0234, +0.0535], realised minus predicted +0.0192 [-0.0113, +0.0501]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.438 | 0.1906 | 0.2720 | +0.0244 [+0.0004, +0.0463] |
| regime | 2020 | 251 | 4 | 0.250 | 0.031 | 0.0982 | 0.0159 | +0.0189 [+0.0093, +0.0279] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0122 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0269 | 0.0200 | +0.0008 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.545 | 0.0890 | 0.1165 | +0.0367 [+0.0080, +0.0722] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0162 | 0.0048 | +0.0083 [+0.0064, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0594 | 0.0031 | +0.0178 [+0.0095, +0.0247] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.600 | 0.1880 | 0.4146 | 0.1096 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.426 | 0.1910 | 0.2474 | +0.0305 [+0.0104, +0.0505] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1443 | 0.1133 | +0.0273 [-0.0104, +0.0649] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.373 | 0.0526 | 0.0630 | +0.0135 [+0.0088, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3234 | 0.2903 | +0.0724 [+0.0015, +0.1362] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2039 | 0.1461 | +0.0602 [+0.0194, +0.1048] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.2171 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.688] | 0.288 | 6.12 flat / 2.94 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.643] | 0.269 | 5.38 flat / 2.63 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.688] | 4.269 [2.435, 6.783] | 1.904 [0.990, 3.210] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 4.500 [2.778, 6.950] | 1.846 [1.081, 3.050] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.308 [2.575, 6.750] | 1.875 [1.083, 3.125] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.231 [2.450, 6.824] | 2.125 [1.121, 3.611] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.652] | 4.885 [2.931, 7.685] | 2.356 [1.302, 3.888] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 7.059 [4.478, 11.000] | 2.868 [1.635, 4.797] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 4.333 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.675 (105 of 1873 days never flag) | 195 | 0.600 | 0.431 | 0.0659 | +0.0055 [-0.0047, +0.0156] | -0.0096 [-0.0191, -0.0005] | 0.862 | 0.536 | yes |
| 2 | 0.577 (147 of 1872 days never flag) | 204 | 0.626 | 0.426 | 0.0717 | -0.0006 [-0.0106, +0.0085] | -0.0106 [-0.0192, -0.0023] | 0.821 | 0.558 | yes |
| 3 | 0.47 (126 of 1871 days never flag) | 196 | 0.609 | 0.429 | 0.0729 | -0.0022 [-0.0132, +0.0069] | -0.0085 [-0.0193, +0.0003] | 0.815 | 0.544 | no |
| 4 | 0.549 (126 of 1870 days never flag) | 178 | 0.493 | 0.382 | 0.0703 | +0.0006 [-0.0078, +0.0090] | -0.0079 [-0.0162, +0.0004] | 0.829 | 0.429 | no |
| 5 | 0.519 (126 of 1869 days never flag) | 206 | 0.572 | 0.383 | 0.0702 | +0.0007 [-0.0070, +0.0080] | -0.0068 [-0.0148, +0.0003] | 0.810 | 0.499 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.617 (climatology 0.457, difference +0.1599 [+0.0266, +0.2811]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0938, ΔBrier vs climatology +0.0357 [+0.0175, +0.0542], realised minus predicted -0.0266 [-0.0581, +0.0056]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.424 | 0.3357 | 0.2720 | -0.0054 [-0.0501, +0.0398] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2241 | 0.0159 | -0.0216 [-0.0408, -0.0044] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0185 | 0.0000 | +0.0118 [+0.0104, +0.0133] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0162 | 0.0200 | +0.0004 [-0.0060, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0807 | 0.1165 | +0.0355 [+0.0064, +0.0731] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0111 | 0.0048 | +0.0079 [+0.0058, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1325 | 0.0031 | +0.0002 [-0.0087, +0.0082] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.2060 | 0.4146 | 0.1072 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.425 | 0.3325 | 0.2474 | -0.0049 [-0.0419, +0.0344] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1504 | 0.1133 | +0.0269 [-0.0124, +0.0662] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.373 | 0.1057 | 0.0630 | -0.0008 [-0.0111, +0.0090] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0026, +0.1363] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0216, +0.1041] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.680] | 0.351 | 6.58 flat / 3.24 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.652] | 0.269 | 5.69 flat / 2.89 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.680] | 4.846 [3.079, 7.375] | 2.077 [1.210, 3.365] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.269 [2.576, 6.769] | 1.740 [0.977, 2.921] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.077 [2.360, 6.542] | 1.673 [0.927, 2.812] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.178, 0.524] | 3.769 [2.206, 6.063] | 1.808 [1.022, 2.989] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 5.038 [3.000, 7.936] | 2.567 [1.448, 4.242] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.647 [5.056, 11.901] | 3.118 [1.848, 5.179] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.556 [2.364, 10.500] | 3.472 [1.583, 8.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 214 | 0.629 | 0.411 | 0.0647 | +0.0067 [-0.0032, +0.0173] | -0.0084 [-0.0173, +0.0002] | 0.863 | 0.556 | yes |
| 2 | 0.546 (126 of 1872 days never flag) | 196 | 0.612 | 0.434 | 0.0703 | +0.0007 [-0.0096, +0.0098] | -0.0093 [-0.0188, -0.0007] | 0.832 | 0.547 | yes |
| 3 | 0.49 (126 of 1871 days never flag) | 189 | 0.601 | 0.439 | 0.0727 | -0.0020 [-0.0126, +0.0073] | -0.0084 [-0.0185, +0.0005] | 0.809 | 0.540 | no |
| 4 | 0.507 (126 of 1870 days never flag) | 165 | 0.486 | 0.406 | 0.0723 | -0.0015 [-0.0100, +0.0074] | -0.0099 [-0.0185, -0.0012] | 0.820 | 0.429 | yes |
| 5 | 0.519 (126 of 1869 days never flag) | 209 | 0.565 | 0.373 | 0.0729 | -0.0020 [-0.0099, +0.0057] | -0.0096 [-0.0174, -0.0016] | 0.811 | 0.490 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.457, difference +0.1589 [+0.0660, +0.2371]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0344 [+0.0164, +0.0533], realised minus predicted -0.0282 [-0.0603, +0.0043]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.401 | 0.3235 | 0.2720 | -0.0022 [-0.0471, +0.0405] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2170 | 0.0159 | -0.0169 [-0.0378, +0.0016] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0104, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0157 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0808 | 0.1165 | +0.0345 [+0.0053, +0.0705] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0108 | 0.0048 | +0.0079 [+0.0060, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1281 | 0.0031 | +0.0024 [-0.0059, +0.0102] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.2065 | 0.4146 | 0.1073 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.405 | 0.3221 | 0.2474 | -0.0019 [-0.0391, +0.0373] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1372 | 0.1133 | +0.0251 [-0.0090, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.355 | 0.1034 | 0.0630 | -0.0001 [-0.0104, +0.0098] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0334, +0.1645] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0208, +0.1143] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.800] | 0.269 | 5.19 flat / 2.46 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.381, 0.760] | 0.231 | 3.92 flat / 1.92 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.682] | 4.269 [2.439, 6.850] | 1.904 [1.015, 3.270] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.962 [2.189, 6.527] | 1.894 [0.981, 3.309] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.423 [1.886, 5.700] | 1.625 [0.875, 2.808] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.350, 0.714] | 3.462 [1.964, 5.692] | 1.567 [0.867, 2.679] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.296, 0.639] | 3.231 [1.697, 5.410] | 1.462 [0.740, 2.579] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.412 [3.869, 10.556] | 2.676 [1.477, 4.709] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.889 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.675 (105 of 1873 days never flag) | 195 | 0.600 | 0.431 | 0.0659 | +0.0055 [-0.0051, +0.0159] | -0.0096 [-0.0190, -0.0006] | 0.862 | 0.536 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 175 | 0.518 | 0.411 | 0.0660 | +0.0050 [-0.0050, +0.0148] | -0.0050 [-0.0150, +0.0043] | 0.834 | 0.459 | yes |
| 3 | 0.625 (126 of 1871 days never flag) | 158 | 0.500 | 0.437 | 0.0705 | +0.0002 [-0.0104, +0.0101] | -0.0061 [-0.0173, +0.0039] | 0.824 | 0.449 | yes |
| 4 | 0.712 (126 of 1870 days never flag) | 160 | 0.507 | 0.438 | 0.0661 | +0.0047 [-0.0047, +0.0141] | -0.0038 [-0.0130, +0.0053] | 0.849 | 0.455 | yes |
| 5 | 0.6 (126 of 1869 days never flag) | 152 | 0.493 | 0.447 | 0.0697 | +0.0013 [-0.0082, +0.0107] | -0.0063 [-0.0155, +0.0029] | 0.835 | 0.444 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.716 | 0.424 | 0.3357 | 0.2720 | -0.0054 [-0.0510, +0.0403] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2241 | 0.0159 | -0.0216 [-0.0411, -0.0044] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0185 | 0.0000 | +0.0118 [+0.0104, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0162 | 0.0200 | +0.0004 [-0.0060, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0807 | 0.1165 | +0.0355 [+0.0066, +0.0734] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0111 | 0.0048 | +0.0079 [+0.0059, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1325 | 0.0031 | +0.0002 [-0.0092, +0.0086] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.2060 | 0.4146 | +0.1072 [-0.0106, +0.2297] |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.425 | 0.3325 | 0.2474 | -0.0049 [-0.0441, +0.0344] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1504 | 0.1133 | +0.0269 [-0.0085, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.373 | 0.1057 | 0.0630 | -0.0008 [-0.0111, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0032, +0.1372] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0224, +0.1026] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.789] | 0.280 | 5.96 flat / 2.70 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.429, 0.792] | 0.269 | 5.15 flat / 2.47 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.680] | 4.846 [2.969, 7.235] | 2.077 [1.189, 3.250] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.300, 0.629] | 4.115 [2.312, 6.500] | 1.952 [1.037, 3.214] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.647] | 4.231 [2.499, 6.458] | 1.808 [1.039, 2.852] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.280, 0.636] | 4.192 [2.235, 6.654] | 1.933 [0.969, 3.218] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.364, 0.710] | 3.538 [1.931, 5.652] | 1.635 [0.850, 2.715] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.833, 11.500] | 3.000 [1.807, 4.855] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.601] | 3.222 [1.615, 7.000] | 2.139 [0.807, 5.201] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 214 | 0.629 | 0.411 | 0.0647 | +0.0067 [-0.0030, +0.0163] | -0.0084 [-0.0169, -0.0003] | 0.863 | 0.556 | yes |
| 2 | 0.587 (126 of 1872 days never flag) | 183 | 0.547 | 0.415 | 0.0658 | +0.0053 [-0.0046, +0.0149] | -0.0047 [-0.0142, +0.0045] | 0.843 | 0.485 | yes |
| 3 | 0.607 (126 of 1871 days never flag) | 195 | 0.616 | 0.436 | 0.0707 | -0.0000 [-0.0111, +0.0105] | -0.0063 [-0.0174, +0.0040] | 0.820 | 0.552 | yes |
| 4 | 0.67 (126 of 1870 days never flag) | 181 | 0.522 | 0.398 | 0.0657 | +0.0052 [-0.0037, +0.0137] | -0.0033 [-0.0119, +0.0054] | 0.844 | 0.459 | yes |
| 5 | 0.494 (126 of 1869 days never flag) | 163 | 0.514 | 0.436 | 0.0679 | +0.0030 [-0.0049, +0.0109] | -0.0045 [-0.0127, +0.0034] | 0.828 | 0.461 | yes |

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
| regime | 2018-19 | 375 | 102 | 0.755 | 0.401 | 0.3235 | 0.2720 | -0.0022 [-0.0447, +0.0399] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2170 | 0.0159 | -0.0169 [-0.0388, +0.0015] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0157 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0808 | 0.1165 | +0.0345 [+0.0053, +0.0720] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0108 | 0.0048 | +0.0079 [+0.0059, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1281 | 0.0031 | +0.0024 [-0.0067, +0.0103] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.2065 | 0.4146 | 0.1073 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.405 | 0.3221 | 0.2474 | -0.0019 [-0.0371, +0.0349] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1372 | 0.1133 | +0.0251 [-0.0096, +0.0583] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.355 | 0.1034 | 0.0630 | -0.0001 [-0.0101, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0258, +0.1621] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0204, +0.1113] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.715] | 0.308 | 6.46 flat / 3.13 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.680] | 0.269 | 5.73 flat / 2.83 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.682] | 4.385 [2.455, 6.955] | 1.933 [1.008, 3.290] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.346 [2.566, 6.843] | 1.788 [0.979, 2.984] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.231 [2.422, 6.750] | 1.837 [1.000, 3.092] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 4.423 [2.600, 7.125] | 2.202 [1.177, 3.833] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 5.115 [3.045, 7.955] | 2.481 [1.380, 4.153] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 7.059 [4.286, 11.250] | 2.868 [1.607, 4.965] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.333 [2.889, 11.671] | 3.639 [1.805, 8.833] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 200 | 0.614 | 0.430 | 0.0614 | +0.0100 [+0.0019, +0.0190] | -0.0050 [-0.0123, +0.0021] | 0.833 | 0.549 | yes |
| 2 | 0.431 (147 of 1872 days never flag) | 198 | 0.612 | 0.429 | 0.0698 | +0.0013 [-0.0057, +0.0080] | -0.0087 [-0.0149, -0.0026] | 0.778 | 0.546 | no |
| 3 | 0.431 (126 of 1871 days never flag) | 196 | 0.623 | 0.439 | 0.0702 | +0.0005 [-0.0058, +0.0068] | -0.0058 [-0.0121, +0.0009] | 0.753 | 0.560 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 184 | 0.500 | 0.375 | 0.0692 | +0.0016 [-0.0050, +0.0084] | -0.0068 [-0.0133, +0.0000] | 0.776 | 0.434 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 213 | 0.580 | 0.376 | 0.0702 | +0.0007 [-0.0062, +0.0075] | -0.0068 [-0.0141, +0.0003] | 0.761 | 0.503 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.457, difference +0.1593 [+0.0202, +0.2828]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0963, ΔBrier vs climatology +0.0332 [+0.0149, +0.0508], realised minus predicted -0.0430 [-0.0759, -0.0106]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.424 | 0.3068 | 0.2720 | +0.0206 [-0.0133, +0.0563] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2323 | 0.0159 | -0.0196 [-0.0328, -0.0070] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0385 | 0.0000 | +0.0102 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0207 | 0.0200 | +0.0004 [-0.0057, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0794 | 0.1165 | +0.0333 [+0.0080, +0.0665] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0244 | 0.0048 | +0.0074 [+0.0055, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1512 | 0.0031 | -0.0050 [-0.0135, +0.0027] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1912 | 0.4146 | 0.0881 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.426 | 0.3066 | 0.2474 | +0.0193 [-0.0095, +0.0500] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1511 | 0.1133 | +0.0261 [-0.0130, +0.0655] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.373 | 0.1099 | 0.0630 | +0.0045 [-0.0029, +0.0125] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0018, +0.1389] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0185, +0.1041] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.375 | 6.96 flat / 3.38 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.650] | 0.271 | 5.85 flat / 2.95 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.680] | 5.000 [3.200, 7.322] | 2.115 [1.238, 3.357] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.789, 6.800] | 1.894 [1.100, 2.976] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.115 [2.357, 6.412] | 1.769 [0.955, 2.860] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.560] | 3.846 [2.281, 6.000] | 1.846 [1.054, 2.986] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 5.269 [3.250, 7.962] | 2.683 [1.529, 4.295] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.647 [5.050, 11.573] | 3.118 [1.854, 4.992] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 5.667 (no interval) | 3.861 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (126 of 1873 days never flag) | 220 | 0.643 | 0.409 | 0.0602 | +0.0112 [+0.0029, +0.0197] | -0.0039 [-0.0103, +0.0029] | 0.830 | 0.568 | yes |
| 2 | 0.489 (126 of 1872 days never flag) | 202 | 0.612 | 0.421 | 0.0685 | +0.0026 [-0.0043, +0.0095] | -0.0074 [-0.0140, -0.0003] | 0.794 | 0.544 | no |
| 3 | 0.431 (126 of 1871 days never flag) | 191 | 0.609 | 0.440 | 0.0701 | +0.0006 [-0.0063, +0.0073] | -0.0057 [-0.0129, +0.0014] | 0.746 | 0.547 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 168 | 0.493 | 0.405 | 0.0713 | -0.0004 [-0.0073, +0.0058] | -0.0089 [-0.0157, -0.0023] | 0.766 | 0.435 | yes |
| 5 | 0.498 (126 of 1869 days never flag) | 216 | 0.572 | 0.366 | 0.0730 | -0.0021 [-0.0094, +0.0048] | -0.0096 [-0.0172, -0.0022] | 0.763 | 0.493 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.612 (climatology 0.457, difference +0.1546 [+0.0599, +0.2391]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0977, ΔBrier vs climatology +0.0318 [+0.0145, +0.0504], realised minus predicted -0.0447 [-0.0743, -0.0112]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.401 | 0.2945 | 0.2720 | +0.0238 [-0.0083, +0.0582] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2251 | 0.0159 | -0.0149 [-0.0288, -0.0014] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0202 | 0.0200 | +0.0007 [-0.0057, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0795 | 0.1165 | +0.0323 [+0.0057, +0.0636] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0241 | 0.0048 | +0.0075 [+0.0056, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1469 | 0.0031 | -0.0028 [-0.0104, +0.0044] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1917 | 0.4146 | 0.0882 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.404 | 0.2962 | 0.2474 | +0.0223 [-0.0067, +0.0516] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1379 | 0.1133 | +0.0243 [-0.0105, +0.0590] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.354 | 0.1077 | 0.0630 | +0.0052 [-0.0025, +0.0129] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0295, +0.1667] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0225, +0.1139] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.269 | 5.58 flat / 2.63 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.367, 0.727] | 0.231 | 4.12 flat / 2.01 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 4.385 [2.585, 6.955] | 1.933 [1.066, 3.182] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 4.231 [2.522, 6.800] | 2.087 [1.176, 3.466] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 3.538 [2.045, 5.808] | 1.702 [0.937, 2.814] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.360, 0.714] | 3.654 [2.172, 5.932] | 1.692 [0.966, 2.800] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.565] | 3.077 [1.591, 5.279] | 1.365 [0.667, 2.408] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 6.412 [3.947, 10.333] | 2.676 [1.523, 4.698] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.000 (no interval) | 2.556 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 200 | 0.614 | 0.430 | 0.0614 | +0.0100 [+0.0020, +0.0188] | -0.0050 [-0.0120, +0.0021] | 0.833 | 0.549 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 183 | 0.525 | 0.399 | 0.0634 | +0.0077 [+0.0007, +0.0158] | -0.0023 [-0.0093, +0.0057] | 0.803 | 0.462 | yes |
| 3 | 0.462 (126 of 1871 days never flag) | 164 | 0.522 | 0.439 | 0.0673 | +0.0034 [-0.0047, +0.0113] | -0.0029 [-0.0113, +0.0055] | 0.772 | 0.469 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 166 | 0.514 | 0.428 | 0.0647 | +0.0061 [-0.0012, +0.0136] | -0.0024 [-0.0103, +0.0055] | 0.805 | 0.460 | yes |
| 5 | 0.743 (126 of 1869 days never flag) | 144 | 0.464 | 0.444 | 0.0694 | +0.0015 [-0.0073, +0.0099] | -0.0060 [-0.0149, +0.0028] | 0.796 | 0.418 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.638 (climatology 0.457, difference +0.1809 [-0.0241, +0.3816]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0934, ΔBrier vs climatology +0.0361 [+0.0148, +0.0594], realised minus predicted -0.0689 [-0.1001, -0.0363]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.424 | 0.3068 | 0.2720 | +0.0206 [-0.0142, +0.0588] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2323 | 0.0159 | -0.0196 [-0.0326, -0.0071] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0385 | 0.0000 | +0.0102 [+0.0087, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0207 | 0.0200 | +0.0004 [-0.0059, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0794 | 0.1165 | +0.0333 [+0.0067, +0.0663] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0244 | 0.0048 | +0.0074 [+0.0056, +0.0092] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1512 | 0.0031 | -0.0050 [-0.0135, +0.0031] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1912 | 0.4146 | +0.0881 [-0.0145, +0.1888] |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.426 | 0.3066 | 0.2474 | +0.0193 [-0.0100, +0.0502] |
| day_type | month_end | 150 | 17 | 0.765 | 0.650 | 0.1511 | 0.1133 | +0.0261 [-0.0118, +0.0629] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.373 | 0.1099 | 0.0630 | +0.0045 [-0.0028, +0.0128] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0045, +0.1386] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1033] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.793] | 0.358 | 6.69 flat / 3.22 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.429, 0.800] | 0.274 | 5.88 flat / 2.96 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.316, 0.680] | 5.000 [3.218, 7.572] | 2.115 [1.250, 3.334] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 3.615 [2.030, 5.858] | 1.654 [0.917, 2.760] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.364, 0.714] | 4.385 [2.619, 6.750] | 1.923 [1.143, 3.053] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.323, 0.679] | 4.731 [2.828, 7.421] | 2.356 [1.354, 3.875] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.367, 0.715] | 3.846 [2.270, 6.106] | 1.827 [1.038, 3.026] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.833, 11.728] | 3.000 [1.819, 5.026] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.333 (no interval) | 3.639 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (126 of 1873 days never flag) | 220 | 0.643 | 0.409 | 0.0602 | +0.0112 [+0.0035, +0.0195] | -0.0039 [-0.0100, +0.0025] | 0.830 | 0.568 | yes |
| 2 | 0.486 (126 of 1872 days never flag) | 168 | 0.532 | 0.440 | 0.0632 | +0.0079 [+0.0005, +0.0155] | -0.0021 [-0.0093, +0.0058] | 0.814 | 0.478 | yes |
| 3 | 0.466 (126 of 1871 days never flag) | 203 | 0.645 | 0.438 | 0.0675 | +0.0032 [-0.0045, +0.0111] | -0.0031 [-0.0113, +0.0051] | 0.769 | 0.579 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 198 | 0.543 | 0.379 | 0.0643 | +0.0066 [-0.0006, +0.0139] | -0.0019 [-0.0094, +0.0056] | 0.796 | 0.472 | yes |
| 5 | 0.494 (126 of 1869 days never flag) | 172 | 0.522 | 0.419 | 0.0676 | +0.0033 [-0.0039, +0.0113] | -0.0042 [-0.0121, +0.0042] | 0.787 | 0.464 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.675 (climatology 0.457, difference +0.2181 [+0.0470, +0.4003]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0162, +0.0591], realised minus predicted -0.0635 [-0.0959, -0.0320]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.401 | 0.2945 | 0.2720 | +0.0238 [-0.0082, +0.0567] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.2251 | 0.0159 | -0.0149 [-0.0294, -0.0011] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0118] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0202 | 0.0200 | +0.0007 [-0.0054, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0795 | 0.1165 | +0.0323 [+0.0056, +0.0640] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0241 | 0.0048 | +0.0075 [+0.0056, +0.0091] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1469 | 0.0031 | -0.0028 [-0.0106, +0.0042] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1917 | 0.4146 | 0.0882 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.404 | 0.2962 | 0.2474 | +0.0223 [-0.0063, +0.0521] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1379 | 0.1133 | +0.0243 [-0.0110, +0.0607] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.354 | 0.1077 | 0.0630 | +0.0052 [-0.0017, +0.0135] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0304, +0.1641] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0206, +0.1138] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.677] | 0.385 | 7.19 flat / 3.46 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.274 | 5.88 flat / 2.94 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 5.692 [3.667, 8.317] | 2.606 [1.562, 4.056] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 3.538 [2.136, 5.381] | 1.337 [0.810, 2.046] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 4.269 [2.560, 6.709] | 1.865 [1.070, 3.072] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.583] | 4.962 [3.032, 7.594] | 2.567 [1.461, 4.238] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.636] | 4.846 [2.939, 7.579] | 2.337 [1.310, 3.888] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 8.941 [6.066, 13.401] | 3.897 [2.410, 6.167] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 3.889 [1.857, 8.842] | 2.639 [1.135, 6.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 234 | 0.614 | 0.368 | 0.0653 | +0.0061 [-0.0058, +0.0168] | -0.0090 [-0.0204, +0.0006] | 0.875 | 0.529 | yes |
| 2 | 0.575 (147 of 1872 days never flag) | 172 | 0.576 | 0.465 | 0.0693 | +0.0018 [-0.0078, +0.0108] | -0.0082 [-0.0171, -0.0000] | 0.848 | 0.522 | no |
| 3 | 0.566 (126 of 1871 days never flag) | 195 | 0.609 | 0.431 | 0.0688 | +0.0019 [-0.0089, +0.0114] | -0.0044 [-0.0151, +0.0048] | 0.862 | 0.545 | no |
| 4 | 0.549 (126 of 1870 days never flag) | 197 | 0.493 | 0.345 | 0.0668 | +0.0041 [-0.0048, +0.0121] | -0.0044 [-0.0134, +0.0040] | 0.849 | 0.418 | no |
| 5 | 0.597 (126 of 1869 days never flag) | 205 | 0.572 | 0.385 | 0.0709 | -0.0000 [-0.0104, +0.0088] | -0.0075 [-0.0178, +0.0013] | 0.836 | 0.500 | no |

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
| regime | 2018-19 | 375 | 102 | 0.725 | 0.359 | 0.3383 | 0.2720 | -0.0127 [-0.0664, +0.0371] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1738 | 0.0159 | -0.0061 [-0.0292, +0.0134] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0116 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0126 | 0.0200 | +0.0015 [-0.0043, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0826 | 0.1165 | +0.0315 [+0.0072, +0.0624] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0068 | 0.0048 | +0.0086 [+0.0066, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0885 | 0.0031 | +0.0133 [+0.0052, +0.0201] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1560 | 0.4146 | +0.0846 [-0.0059, +0.1719] |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.359 | 0.3399 | 0.2474 | -0.0112 [-0.0553, +0.0299] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1491 | 0.1133 | +0.0274 [-0.0107, +0.0664] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.309 | 0.0950 | 0.0630 | -0.0002 [-0.0126, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0015, +0.1352] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0206, +0.1019] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.679] | 0.385 | 7.42 flat / 3.69 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.622] | 0.284 | 6.08 flat / 3.18 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.310, 0.679] | 5.923 [3.913, 8.501] | 2.644 [1.616, 3.990] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.577 [2.806, 6.846] | 1.894 [1.087, 2.900] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.572] | 3.769 [2.050, 6.000] | 1.548 [0.776, 2.534] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.167, 0.524] | 4.654 [2.880, 6.876] | 2.298 [1.348, 3.539] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.572] | 4.769 [2.778, 7.502] | 2.337 [1.262, 3.925] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 9.059 [6.166, 13.267] | 3.971 [2.486, 6.160] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.333 [2.100, 10.000] | 3.167 [1.386, 8.000] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 247 | 0.664 | 0.377 | 0.0642 | +0.0072 [-0.0039, +0.0179] | -0.0078 [-0.0177, +0.0014] | 0.877 | 0.575 | yes |
| 2 | 0.546 (126 of 1872 days never flag) | 207 | 0.633 | 0.425 | 0.0680 | +0.0031 [-0.0065, +0.0118] | -0.0069 [-0.0164, +0.0017] | 0.855 | 0.564 | no |
| 3 | 0.49 (126 of 1871 days never flag) | 174 | 0.551 | 0.437 | 0.0686 | +0.0021 [-0.0096, +0.0121] | -0.0043 [-0.0156, +0.0056] | 0.858 | 0.494 | no |
| 4 | 0.507 (126 of 1870 days never flag) | 188 | 0.486 | 0.356 | 0.0688 | +0.0020 [-0.0065, +0.0100] | -0.0064 [-0.0149, +0.0018] | 0.841 | 0.416 | no |
| 5 | 0.648 (126 of 1869 days never flag) | 201 | 0.558 | 0.383 | 0.0737 | -0.0028 [-0.0133, +0.0067] | -0.0103 [-0.0210, -0.0004] | 0.836 | 0.486 | no |

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
| regime | 2018-19 | 375 | 102 | 0.794 | 0.367 | 0.3261 | 0.2720 | -0.0095 [-0.0592, +0.0356] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1666 | 0.0159 | -0.0014 [-0.0273, +0.0198] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0114 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0121 | 0.0200 | +0.0018 [-0.0040, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0827 | 0.1165 | +0.0305 [+0.0065, +0.0608] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0087 [+0.0068, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0841 | 0.0031 | +0.0155 [+0.0076, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1565 | 0.4146 | 0.0847 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.369 | 0.3295 | 0.2474 | -0.0082 [-0.0495, +0.0331] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1359 | 0.1133 | +0.0256 [-0.0086, +0.0628] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.322 | 0.0928 | 0.0630 | +0.0005 [-0.0109, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0320, +0.1660] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0217, +0.1150] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.417, 0.792] | 0.291 | 6.15 flat / 2.93 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.391, 0.760] | 0.231 | 3.85 flat / 1.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.312, 0.680] | 5.692 [3.695, 8.250] | 2.606 [1.559, 4.022] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.647] | 3.846 [2.066, 6.182] | 1.865 [0.939, 3.143] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.606] | 3.462 [1.857, 5.592] | 1.663 [0.850, 2.816] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.348, 0.714] | 3.423 [1.866, 5.462] | 1.529 [0.807, 2.553] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 3.038 [1.529, 5.045] | 1.356 [0.639, 2.353] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 0.960] | 8.000 [5.142, 12.095] | 3.529 [2.087, 5.784] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.806 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 234 | 0.614 | 0.368 | 0.0653 | +0.0061 [-0.0057, +0.0172] | -0.0090 [-0.0194, +0.0010] | 0.875 | 0.529 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 173 | 0.525 | 0.422 | 0.0640 | +0.0070 [-0.0026, +0.0166] | -0.0030 [-0.0127, +0.0065] | 0.856 | 0.467 | yes |
| 3 | 0.674 (126 of 1871 days never flag) | 159 | 0.500 | 0.434 | 0.0672 | +0.0034 [-0.0077, +0.0135] | -0.0029 [-0.0141, +0.0072] | 0.862 | 0.448 | no |
| 4 | 0.712 (126 of 1870 days never flag) | 159 | 0.507 | 0.440 | 0.0633 | +0.0076 [-0.0016, +0.0160] | -0.0009 [-0.0104, +0.0083] | 0.861 | 0.456 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 146 | 0.486 | 0.459 | 0.0710 | -0.0001 [-0.0117, +0.0098] | -0.0076 [-0.0191, +0.0025] | 0.852 | 0.440 | no |

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
| regime | 2018-19 | 375 | 102 | 0.725 | 0.359 | 0.3383 | 0.2720 | -0.0127 [-0.0621, +0.0398] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1738 | 0.0159 | -0.0061 [-0.0290, +0.0141] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0116 | 0.0000 | +0.0126 [+0.0110, +0.0143] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0126 | 0.0200 | +0.0015 [-0.0045, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0826 | 0.1165 | +0.0315 [+0.0065, +0.0630] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0068 | 0.0048 | +0.0086 [+0.0066, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0885 | 0.0031 | +0.0133 [+0.0058, +0.0200] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1560 | 0.4146 | 0.0846 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.359 | 0.3399 | 0.2474 | -0.0112 [-0.0536, +0.0334] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1491 | 0.1133 | +0.0274 [-0.0098, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.309 | 0.0950 | 0.0630 | -0.0002 [-0.0120, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0018, +0.1388] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0199, +0.1039] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.365 | 6.81 flat / 3.18 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.429, 0.807] | 0.269 | 5.42 flat / 2.58 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.688] | 5.923 [3.925, 8.601] | 2.644 [1.599, 4.019] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 4.077 [2.233, 6.438] | 1.933 [1.015, 3.134] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.500 [2.842, 6.889] | 1.913 [1.148, 3.021] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.654] | 4.154 [2.214, 6.616] | 1.913 [0.952, 3.177] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 3.692 [2.088, 5.834] | 1.692 [0.900, 2.786] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 8.706 [5.889, 12.688] | 3.750 [2.344, 5.834] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.669 (126 of 1873 days never flag) | 247 | 0.664 | 0.377 | 0.0642 | +0.0072 [-0.0044, +0.0178] | -0.0078 [-0.0189, +0.0011] | 0.877 | 0.575 | yes |
| 2 | 0.587 (126 of 1872 days never flag) | 181 | 0.540 | 0.414 | 0.0638 | +0.0073 [-0.0029, +0.0162] | -0.0027 [-0.0122, +0.0066] | 0.865 | 0.478 | yes |
| 3 | 0.607 (126 of 1871 days never flag) | 203 | 0.623 | 0.424 | 0.0675 | +0.0032 [-0.0082, +0.0138] | -0.0031 [-0.0145, +0.0074] | 0.859 | 0.556 | no |
| 4 | 0.67 (126 of 1870 days never flag) | 180 | 0.522 | 0.400 | 0.0628 | +0.0080 [-0.0005, +0.0166] | -0.0004 [-0.0091, +0.0084] | 0.858 | 0.459 | no |
| 5 | 0.494 (126 of 1869 days never flag) | 166 | 0.507 | 0.422 | 0.0693 | +0.0017 [-0.0087, +0.0111] | -0.0059 [-0.0165, +0.0037] | 0.847 | 0.452 | no |

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
| regime | 2018-19 | 375 | 102 | 0.794 | 0.367 | 0.3261 | 0.2720 | -0.0095 [-0.0595, +0.0368] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1666 | 0.0159 | -0.0014 [-0.0261, +0.0190] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0114 | 0.0000 | +0.0126 [+0.0109, +0.0144] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0121 | 0.0200 | +0.0018 [-0.0041, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0827 | 0.1165 | +0.0305 [+0.0058, +0.0620] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0087 [+0.0066, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0841 | 0.0031 | +0.0155 [+0.0077, +0.0225] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1565 | 0.4146 | 0.0847 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.369 | 0.3295 | 0.2474 | -0.0082 [-0.0520, +0.0325] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1359 | 0.1133 | +0.0256 [-0.0077, +0.0613] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.322 | 0.0928 | 0.0630 | +0.0005 [-0.0119, +0.0109] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0284, +0.1659] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0223, +0.1114] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2738 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.720] | 0.368 | 6.85 flat / 3.35 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.316, 0.682] | 0.269 | 5.77 flat / 2.88 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.688] | 5.538 [3.500, 8.212] | 2.567 [1.510, 4.014] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.423 [2.648, 6.870] | 1.885 [1.083, 3.022] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 4.077 [2.303, 6.500] | 1.712 [0.917, 2.869] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.885 [2.880, 7.600] | 2.548 [1.388, 4.190] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.846 [2.799, 7.700] | 2.317 [1.217, 3.977] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 8.941 [5.879, 13.572] | 3.897 [2.382, 6.296] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.889 (no interval) | 2.306 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 229 | 0.607 | 0.371 | 0.0588 | +0.0126 [+0.0042, +0.0215] | -0.0025 [-0.0095, +0.0048] | 0.858 | 0.524 | yes |
| 2 | 0.448 (147 of 1872 days never flag) | 201 | 0.619 | 0.428 | 0.0657 | +0.0053 [-0.0024, +0.0131] | -0.0047 [-0.0115, +0.0021] | 0.832 | 0.552 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 190 | 0.609 | 0.442 | 0.0649 | +0.0058 [-0.0010, +0.0126] | -0.0005 [-0.0070, +0.0064] | 0.845 | 0.548 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 196 | 0.500 | 0.352 | 0.0645 | +0.0063 [-0.0008, +0.0135] | -0.0021 [-0.0092, +0.0049] | 0.834 | 0.427 | no |
| 5 | 0.424 (126 of 1869 days never flag) | 205 | 0.572 | 0.385 | 0.0667 | +0.0042 [-0.0027, +0.0108] | -0.0033 [-0.0103, +0.0037] | 0.815 | 0.500 | no |

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
| regime | 2018-19 | 375 | 102 | 0.725 | 0.359 | 0.3039 | 0.2720 | +0.0186 [-0.0157, +0.0573] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1967 | 0.0159 | -0.0064 [-0.0229, +0.0089] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0164 | 0.0000 | +0.0124 [+0.0107, +0.0140] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0015 [-0.0045, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0803 | 0.1165 | +0.0348 [+0.0074, +0.0672] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0094 | 0.0048 | +0.0086 [+0.0066, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1112 | 0.0031 | +0.0086 [+0.0011, +0.0156] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.1633 | 0.4146 | +0.0865 [-0.0033, +0.1743] |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.364 | 0.3094 | 0.2474 | +0.0179 [-0.0124, +0.0506] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1496 | 0.1133 | +0.0274 [-0.0106, +0.0639] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.312 | 0.0925 | 0.0630 | +0.0075 [-0.0002, +0.0159] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [-0.0004, +0.1404] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0192, +0.1024] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2395 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.682] | 0.385 | 7.12 flat / 3.58 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.647] | 0.276 | 5.92 flat / 3.11 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 5.846 [3.937, 8.515] | 2.625 [1.630, 4.023] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.577 [2.862, 6.950] | 1.990 [1.202, 3.110] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.212, 0.583] | 3.731 [2.061, 6.002] | 1.529 [0.800, 2.596] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 4.538 [2.846, 6.792] | 2.260 [1.346, 3.510] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.000, 7.643] | 2.510 [1.443, 4.125] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 9.059 [6.133, 13.314] | 3.971 [2.517, 6.137] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 3.444 [1.625, 8.333] | 2.833 [1.156, 7.352] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (126 of 1873 days never flag) | 244 | 0.657 | 0.377 | 0.0576 | +0.0138 [+0.0055, +0.0224] | -0.0013 [-0.0079, +0.0054] | 0.858 | 0.569 | yes |
| 2 | 0.532 (126 of 1872 days never flag) | 206 | 0.626 | 0.422 | 0.0644 | +0.0067 [-0.0009, +0.0138] | -0.0034 [-0.0104, +0.0034] | 0.844 | 0.557 | no |
| 3 | 0.487 (126 of 1871 days never flag) | 173 | 0.551 | 0.439 | 0.0647 | +0.0060 [-0.0013, +0.0134] | -0.0004 [-0.0076, +0.0069] | 0.839 | 0.495 | no |
| 4 | 0.463 (126 of 1870 days never flag) | 185 | 0.486 | 0.362 | 0.0665 | +0.0043 [-0.0029, +0.0111] | -0.0042 [-0.0115, +0.0030] | 0.825 | 0.417 | no |
| 5 | 0.519 (126 of 1869 days never flag) | 207 | 0.565 | 0.377 | 0.0695 | +0.0014 [-0.0062, +0.0089] | -0.0061 [-0.0144, +0.0015] | 0.816 | 0.491 | no |

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
| regime | 2018-19 | 375 | 102 | 0.794 | 0.367 | 0.2917 | 0.2720 | +0.0218 [-0.0125, +0.0566] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1896 | 0.0159 | -0.0017 [-0.0188, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0124 [+0.0108, +0.0141] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0804 | 0.1165 | +0.0338 [+0.0064, +0.0672] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0092 | 0.0048 | +0.0086 [+0.0067, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1068 | 0.0031 | +0.0108 [+0.0030, +0.0175] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.1638 | 0.4146 | 0.0866 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.370 | 0.2990 | 0.2474 | +0.0209 [-0.0088, +0.0534] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1364 | 0.1133 | +0.0256 [-0.0086, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.322 | 0.0903 | 0.0630 | +0.0081 [+0.0005, +0.0162] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0275, +0.1636] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0224, +0.1118] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2396 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.417, 0.792] | 0.286 | 6.08 flat / 2.96 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.391, 0.769] | 0.231 | 3.77 flat / 1.84 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 5.538 [3.441, 8.042] | 2.567 [1.500, 3.897] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 4.000 [2.206, 6.348] | 2.019 [1.083, 3.376] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 3.462 [1.875, 5.539] | 1.654 [0.875, 2.772] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.355, 0.714] | 3.423 [1.826, 5.446] | 1.548 [0.817, 2.587] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.115 [1.512, 5.133] | 1.375 [0.661, 2.355] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 8.000 [5.176, 12.224] | 3.529 [2.113, 5.823] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 2.444 [1.083, 5.667] | 1.889 [0.672, 4.834] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 229 | 0.607 | 0.371 | 0.0588 | +0.0126 [+0.0041, +0.0219] | -0.0025 [-0.0095, +0.0049] | 0.858 | 0.524 | yes |
| 2 | 0.608 (126 of 1872 days never flag) | 178 | 0.532 | 0.416 | 0.0599 | +0.0112 [+0.0027, +0.0191] | +0.0012 [-0.0071, +0.0090] | 0.841 | 0.472 | yes |
| 3 | 0.674 (126 of 1871 days never flag) | 161 | 0.514 | 0.441 | 0.0627 | +0.0080 [-0.0005, +0.0160] | +0.0016 [-0.0072, +0.0101] | 0.843 | 0.463 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 159 | 0.507 | 0.440 | 0.0606 | +0.0103 [+0.0027, +0.0180] | +0.0018 [-0.0061, +0.0099] | 0.845 | 0.456 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 148 | 0.486 | 0.453 | 0.0664 | +0.0045 [-0.0043, +0.0134] | -0.0030 [-0.0126, +0.0062] | 0.834 | 0.439 | no |

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
| regime | 2018-19 | 375 | 102 | 0.725 | 0.359 | 0.3039 | 0.2720 | +0.0186 [-0.0182, +0.0570] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1967 | 0.0159 | -0.0064 [-0.0223, +0.0080] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0164 | 0.0000 | +0.0124 [+0.0107, +0.0141] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0015 [-0.0043, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0803 | 0.1165 | +0.0348 [+0.0085, +0.0689] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0094 | 0.0048 | +0.0086 [+0.0067, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1112 | 0.0031 | +0.0086 [+0.0006, +0.0152] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.1633 | 0.4146 | 0.0865 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.364 | 0.3094 | 0.2474 | +0.0179 [-0.0142, +0.0512] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1496 | 0.1133 | +0.0274 [-0.0099, +0.0667] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.312 | 0.0925 | 0.0630 | +0.0075 [-0.0005, +0.0160] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0001, +0.1390] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2039 | 0.1461 | +0.0602 [+0.0220, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2395 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.361 | 6.73 flat / 3.30 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.433, 0.793] | 0.269 | 5.58 flat / 2.75 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.679] | 5.846 [3.928, 8.530] | 2.625 [1.630, 4.031] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 3.423 [1.848, 5.667] | 1.538 [0.824, 2.672] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.316, 0.682] | 4.500 [2.821, 7.000] | 1.933 [1.163, 3.112] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.321, 0.667] | 4.462 [2.556, 7.182] | 2.221 [1.239, 3.789] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 3.692 [2.129, 6.000] | 1.692 [0.926, 2.885] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.706 [6.000, 13.183] | 3.750 [2.381, 6.045] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.000 (no interval) | 2.444 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (126 of 1873 days never flag) | 244 | 0.657 | 0.377 | 0.0576 | +0.0138 [+0.0061, +0.0228] | -0.0013 [-0.0077, +0.0055] | 0.858 | 0.569 | yes |
| 2 | 0.448 (126 of 1872 days never flag) | 164 | 0.540 | 0.457 | 0.0596 | +0.0114 [+0.0032, +0.0195] | +0.0014 [-0.0066, +0.0092] | 0.853 | 0.488 | yes |
| 3 | 0.607 (126 of 1871 days never flag) | 204 | 0.630 | 0.426 | 0.0629 | +0.0077 [-0.0013, +0.0158] | +0.0014 [-0.0076, +0.0098] | 0.841 | 0.563 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 191 | 0.543 | 0.393 | 0.0601 | +0.0107 [+0.0035, +0.0183] | +0.0023 [-0.0055, +0.0101] | 0.838 | 0.477 | no |
| 5 | 0.494 (126 of 1869 days never flag) | 166 | 0.507 | 0.422 | 0.0646 | +0.0063 [-0.0014, +0.0138] | -0.0012 [-0.0092, +0.0066] | 0.821 | 0.452 | no |

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
| regime | 2018-19 | 375 | 102 | 0.794 | 0.367 | 0.2917 | 0.2720 | +0.0218 [-0.0114, +0.0571] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1896 | 0.0159 | -0.0017 [-0.0197, +0.0129] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0124 [+0.0108, +0.0140] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0044, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0804 | 0.1165 | +0.0338 [+0.0067, +0.0666] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0092 | 0.0048 | +0.0086 [+0.0067, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1068 | 0.0031 | +0.0108 [+0.0035, +0.0173] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.1638 | 0.4146 | 0.0866 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.370 | 0.2990 | 0.2474 | +0.0209 [-0.0079, +0.0531] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1364 | 0.1133 | +0.0256 [-0.0087, +0.0618] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.322 | 0.0903 | 0.0630 | +0.0081 [+0.0005, +0.0162] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.2995 | 0.2903 | +0.1011 [+0.0304, +0.1662] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2003 | 0.1461 | +0.0655 [+0.0227, +0.1139] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2396 | 0.2213 |

