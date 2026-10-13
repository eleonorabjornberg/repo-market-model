# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `532a238c5dda…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## hierarchical_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.385 | 7.15 flat / 3.38 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.682] | 0.299 | 6.35 flat / 2.98 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.680] | 5.154 [3.100, 7.818] | 2.308 [1.265, 3.708] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 4.385 [2.599, 6.572] | 1.750 [0.984, 2.775] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 4.038 [2.269, 6.218] | 1.615 [0.852, 2.633] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 4.577 [2.709, 6.913] | 2.058 [1.125, 3.222] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.682] | 6.231 [4.000, 9.080] | 2.913 [1.714, 4.500] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 8.765 [5.863, 13.167] | 3.882 [2.400, 6.151] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.111 (no interval) | 2.417 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.336 (147 of 1873 days never flag) | 225 | 0.650 | 0.404 | 0.0530 | +0.0184 [+0.0114, +0.0260] | +0.0034 [-0.0007, +0.0073] | 0.880 | 0.573 | yes |
| 2 | 0.373 (147 of 1872 days never flag) | 200 | 0.619 | 0.430 | 0.0589 | +0.0121 [+0.0066, +0.0178] | +0.0021 [-0.0016, +0.0061] | 0.847 | 0.553 | yes |
| 3 | 0.383 (147 of 1871 days never flag) | 185 | 0.580 | 0.432 | 0.0607 | +0.0100 [+0.0053, +0.0146] | +0.0037 [-0.0001, +0.0076] | 0.834 | 0.519 | yes |
| 4 | 0.407 (147 of 1870 days never flag) | 187 | 0.493 | 0.364 | 0.0603 | +0.0105 [+0.0057, +0.0154] | +0.0020 [-0.0023, +0.0062] | 0.833 | 0.424 | yes |
| 5 | 0.451 (126 of 1869 days never flag) | 244 | 0.594 | 0.336 | 0.0608 | +0.0101 [+0.0050, +0.0151] | +0.0026 [-0.0020, +0.0071] | 0.827 | 0.501 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.578 (climatology 0.512, difference +0.0657 [-0.0144, +0.1400]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0390 [+0.0269, +0.0533], realised minus predicted +0.0465 [+0.0139, +0.0831]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2190 | 0.2720 | +0.0265 [+0.0024, +0.0512] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1363 | 0.0159 | +0.0181 [+0.0037, +0.0311] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0085 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0065 | 0.0200 | +0.0013 [-0.0036, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.552 | 0.1189 | 0.1165 | +0.0382 [+0.0069, +0.0750] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0083 | 0.0048 | +0.0088 [+0.0070, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0586 | 0.0000 | +0.0271 [+0.0214, +0.0325] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.600 | 0.1890 | 0.2439 | 0.0578 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.400 | 0.2493 | 0.2615 | +0.0303 [+0.0057, +0.0563] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1016 | 0.1133 | +0.0440 [+0.0227, +0.0682] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.359 | 0.0752 | 0.0630 | +0.0128 [+0.0065, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2214 | 0.2903 | +0.0754 [+0.0169, +0.1274] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1263 | 0.1461 | +0.0569 [+0.0308, +0.0829] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2425 | 0.2213 |

## hierarchical_logistic_fed_repo (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.409, 0.750] | 0.380 | 7.04 flat / 3.17 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.355, 0.720] | 0.360 | 6.77 flat / 3.09 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.682] | 4.692 [2.769, 7.305] | 2.010 [1.081, 3.333] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.500 [2.735, 6.867] | 1.760 [1.009, 2.840] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.462 [2.735, 6.783] | 1.788 [1.025, 2.917] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.639] | 5.115 [3.237, 7.682] | 2.298 [1.370, 3.630] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 6.385 [4.235, 9.333] | 2.942 [1.765, 4.543] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.765 [5.826, 13.236] | 3.882 [2.396, 6.225] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.778 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.336 (147 of 1873 days never flag) | 210 | 0.629 | 0.419 | 0.0543 | +0.0171 [+0.0102, +0.0245] | +0.0020 [-0.0022, +0.0062] | 0.877 | 0.558 | yes |
| 2 | 0.373 (147 of 1872 days never flag) | 203 | 0.619 | 0.424 | 0.0600 | +0.0111 [+0.0051, +0.0168] | +0.0011 [-0.0034, +0.0052] | 0.850 | 0.551 | yes |
| 3 | 0.383 (147 of 1871 days never flag) | 198 | 0.594 | 0.414 | 0.0605 | +0.0101 [+0.0049, +0.0151] | +0.0038 [-0.0003, +0.0077] | 0.843 | 0.527 | yes |
| 4 | 0.362 (147 of 1870 days never flag) | 210 | 0.558 | 0.367 | 0.0596 | +0.0113 [+0.0058, +0.0167] | +0.0028 [-0.0021, +0.0078] | 0.843 | 0.481 | yes |
| 5 | 0.457 (126 of 1869 days never flag) | 250 | 0.609 | 0.336 | 0.0622 | +0.0087 [+0.0027, +0.0145] | +0.0012 [-0.0045, +0.0065] | 0.828 | 0.513 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.609 (climatology 0.512, difference +0.0970 [+0.0115, +0.1981]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0894, ΔBrier vs climatology +0.0401 [+0.0273, +0.0548], realised minus predicted +0.0424 [+0.0101, +0.0770]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2374 | 0.2720 | +0.0171 [-0.0113, +0.0465] |
| regime | 2020 | 251 | 4 | 0.500 | 0.222 | 0.1149 | 0.0159 | +0.0278 [+0.0171, +0.0377] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0136 [+0.0120, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0054 | 0.0200 | +0.0013 [-0.0037, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0969 | 0.1165 | +0.0324 [+0.0069, +0.0645] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0091 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0527 | 0.0000 | +0.0283 [+0.0221, +0.0342] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1231 | 0.2439 | 0.0440 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.696 | 0.418 | 0.2497 | 0.2615 | +0.0256 [-0.0001, +0.0535] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.0978 | 0.1133 | +0.0412 [+0.0223, +0.0626] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.371 | 0.0740 | 0.0630 | +0.0113 [+0.0044, +0.0186] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2040 | 0.2903 | +0.0796 [+0.0219, +0.1321] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1215 | 0.1461 | +0.0589 [+0.0344, +0.0846] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.667 | 0.500 | 0.1756 | 0.2213 |

## hierarchical_logistic_fed_repo_sameday (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.440, 0.783] | 0.380 | 7.04 flat / 3.15 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.760] | 0.360 | 6.77 flat / 3.07 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.357, 0.708] | 4.808 [2.884, 7.316] | 2.010 [1.065, 3.217] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.613] | 4.308 [2.542, 6.600] | 1.779 [0.991, 2.857] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.613] | 4.192 [2.484, 6.456] | 1.644 [0.902, 2.691] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.613] | 5.577 [3.545, 8.357] | 2.615 [1.500, 4.208] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.389, 0.758] | 6.500 [4.356, 9.476] | 2.990 [1.848, 4.625] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.765 [6.000, 13.183] | 3.882 [2.442, 6.160] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.778 (no interval) | 1.778 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.321 (147 of 1873 days never flag) | 216 | 0.650 | 0.421 | 0.0536 | +0.0178 [+0.0110, +0.0252] | +0.0027 [-0.0014, +0.0069] | 0.880 | 0.578 | yes |
| 2 | 0.373 (147 of 1872 days never flag) | 196 | 0.604 | 0.429 | 0.0603 | +0.0107 [+0.0049, +0.0164] | +0.0007 [-0.0041, +0.0053] | 0.844 | 0.540 | yes |
| 3 | 0.383 (147 of 1871 days never flag) | 190 | 0.587 | 0.426 | 0.0611 | +0.0096 [+0.0042, +0.0146] | +0.0032 [-0.0010, +0.0072] | 0.837 | 0.524 | yes |
| 4 | 0.407 (147 of 1870 days never flag) | 216 | 0.514 | 0.329 | 0.0604 | +0.0104 [+0.0050, +0.0159] | +0.0020 [-0.0026, +0.0068] | 0.845 | 0.431 | yes |
| 5 | 0.362 (126 of 1869 days never flag) | 257 | 0.638 | 0.342 | 0.0615 | +0.0094 [+0.0032, +0.0151] | +0.0019 [-0.0040, +0.0074] | 0.828 | 0.540 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.600 (climatology 0.512, difference +0.0882 [-0.0178, +0.1956]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0883, ΔBrier vs climatology +0.0412 [+0.0283, +0.0560], realised minus predicted +0.0415 [+0.0095, +0.0763]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2354 | 0.2720 | +0.0182 [-0.0092, +0.0454] |
| regime | 2020 | 251 | 4 | 0.750 | 0.231 | 0.1140 | 0.0159 | +0.0299 [+0.0195, +0.0401] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0088 | 0.0000 | +0.0136 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0039 | 0.0200 | +0.0012 [-0.0037, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.609 | 0.0858 | 0.1165 | +0.0343 [+0.0103, +0.0676] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0075 | 0.0048 | +0.0089 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0497 | 0.0000 | +0.0288 [+0.0227, +0.0350] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 1.000 | 0.1062 | 0.2439 | 0.0623 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.712 | 0.416 | 0.2470 | 0.2615 | +0.0263 [+0.0011, +0.0519] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.0941 | 0.1133 | +0.0400 [+0.0222, +0.0606] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.373 | 0.0719 | 0.0630 | +0.0122 [+0.0054, +0.0194] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.1985 | 0.2903 | +0.0833 [+0.0198, +0.1388] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1150 | 0.1461 | +0.0593 [+0.0348, +0.0866] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 1.000 | 0.375 | 0.2132 | 0.2213 |

## hierarchical_logistic_srf (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.741] | 0.385 | 7.23 flat / 3.30 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.760] | 0.352 | 6.65 flat / 3.06 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.312, 0.677] | 4.962 [3.038, 7.625] | 2.144 [1.177, 3.579] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.312, 0.677] | 4.654 [2.793, 7.000] | 1.817 [1.021, 2.876] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 4.885 [2.960, 7.438] | 2.058 [1.145, 3.333] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.312, 0.677] | 5.038 [3.000, 7.522] | 2.279 [1.286, 3.549] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.389, 0.741] | 6.385 [4.111, 9.228] | 2.942 [1.740, 4.596] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.471, 0.909] | 8.765 [5.782, 13.445] | 3.882 [2.343, 6.265] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.194 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.321 (147 of 1873 days never flag) | 219 | 0.643 | 0.411 | 0.0530 | +0.0184 [+0.0115, +0.0256] | +0.0033 [-0.0005, +0.0068] | 0.892 | 0.568 | yes |
| 2 | 0.373 (147 of 1872 days never flag) | 214 | 0.669 | 0.435 | 0.0584 | +0.0127 [+0.0069, +0.0187] | +0.0027 [-0.0014, +0.0068] | 0.861 | 0.599 | yes |
| 3 | 0.383 (147 of 1871 days never flag) | 211 | 0.609 | 0.398 | 0.0602 | +0.0104 [+0.0057, +0.0150] | +0.0041 [+0.0002, +0.0082] | 0.848 | 0.535 | yes |
| 4 | 0.407 (147 of 1870 days never flag) | 206 | 0.543 | 0.364 | 0.0594 | +0.0114 [+0.0065, +0.0160] | +0.0030 [-0.0016, +0.0072] | 0.849 | 0.468 | yes |
| 5 | 0.413 (126 of 1869 days never flag) | 252 | 0.623 | 0.341 | 0.0604 | +0.0105 [+0.0052, +0.0156] | +0.0030 [-0.0021, +0.0076] | 0.836 | 0.527 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.598 (climatology 0.512, difference +0.0857 [-0.0092, +0.1857]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0884, ΔBrier vs climatology +0.0410 [+0.0282, +0.0556], realised minus predicted +0.0487 [+0.0170, +0.0825]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2226 | 0.2720 | +0.0220 [-0.0026, +0.0471] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1021 | 0.0159 | +0.0267 [+0.0146, +0.0367] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0068 | 0.0000 | +0.0137 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0053 | 0.0200 | +0.0013 [-0.0036, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.536 | 0.1106 | 0.1165 | +0.0358 [+0.0064, +0.0713] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0075 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0407 | 0.0000 | +0.0296 [+0.0235, +0.0355] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.1435 | 0.2439 | 0.0483 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.704 | 0.409 | 0.2442 | 0.2615 | +0.0293 [+0.0048, +0.0551] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.0954 | 0.1133 | +0.0446 [+0.0236, +0.0698] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.364 | 0.0697 | 0.0630 | +0.0126 [+0.0060, +0.0193] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2045 | 0.2903 | +0.0810 [+0.0251, +0.1343] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1206 | 0.1461 | +0.0570 [+0.0296, +0.0843] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2428 | 0.2213 |

## hierarchical_logistic_srf_sameday (candidate): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.375 | 6.96 flat / 3.19 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.758] | 0.349 | 6.62 flat / 3.05 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.690] | 4.731 [2.758, 7.552] | 2.048 [1.076, 3.517] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 4.615 [2.865, 7.000] | 1.856 [1.072, 2.990] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 4.231 [2.469, 6.520] | 1.635 [0.886, 2.680] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.318, 0.690] | 4.962 [3.087, 7.333] | 2.202 [1.293, 3.463] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 6.269 [4.111, 9.238] | 2.894 [1.710, 4.605] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.765 [5.823, 13.092] | 3.882 [2.361, 6.292] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.556 [1.333, 8.168] | 1.889 [0.646, 4.752] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.336 (147 of 1873 days never flag) | 214 | 0.650 | 0.425 | 0.0519 | +0.0195 [+0.0127, +0.0271] | +0.0044 [+0.0007, +0.0081] | 0.896 | 0.579 | yes |
| 2 | 0.373 (147 of 1872 days never flag) | 211 | 0.655 | 0.431 | 0.0582 | +0.0129 [+0.0074, +0.0187] | +0.0029 [-0.0012, +0.0071] | 0.866 | 0.585 | yes |
| 3 | 0.383 (147 of 1871 days never flag) | 196 | 0.623 | 0.439 | 0.0605 | +0.0102 [+0.0055, +0.0151] | +0.0039 [+0.0000, +0.0083] | 0.847 | 0.560 | yes |
| 4 | 0.372 (147 of 1870 days never flag) | 202 | 0.529 | 0.361 | 0.0600 | +0.0108 [+0.0061, +0.0156] | +0.0024 [-0.0022, +0.0067] | 0.855 | 0.455 | yes |
| 5 | 0.466 (126 of 1869 days never flag) | 248 | 0.616 | 0.343 | 0.0598 | +0.0111 [+0.0059, +0.0161] | +0.0036 [-0.0013, +0.0082] | 0.840 | 0.522 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.512, difference +0.0814 [-0.0294, +0.1828]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0406 [+0.0284, +0.0544], realised minus predicted +0.0499 [+0.0176, +0.0851]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2238 | 0.2720 | +0.0240 [-0.0001, +0.0514] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0973 | 0.0159 | +0.0272 [+0.0157, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0059 | 0.0000 | +0.0137 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0044 | 0.0200 | +0.0012 [-0.0041, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.630 | 0.1052 | 0.1165 | +0.0409 [+0.0100, +0.0799] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0089 [+0.0070, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0360 | 0.0000 | +0.0300 [+0.0239, +0.0363] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.667 | 0.1416 | 0.2439 | 0.0642 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.712 | 0.422 | 0.2429 | 0.2615 | +0.0320 [+0.0075, +0.0591] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.0944 | 0.1133 | +0.0456 [+0.0241, +0.0714] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.374 | 0.0682 | 0.0630 | +0.0139 [+0.0074, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2000 | 0.2903 | +0.0740 [+0.0189, +0.1252] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1167 | 0.1461 | +0.0576 [+0.0312, +0.0851] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2430 | 0.2213 |

## published_v1 (baseline): FAIL at +5 bp

Tier 1 no, tier 3 yes, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 yes, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.720] | 0.385 | 7.38 flat / 3.06 weighted | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.682] | 0.303 | 6.42 flat / 2.71 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 5.692 [3.906, 8.133] | 2.308 [1.432, 3.548] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.474] | 5.615 [3.774, 8.056] | 2.356 [1.470, 3.607] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.379] | 4.538 [2.869, 6.778] | 1.942 [1.086, 3.133] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 5.731 [3.844, 8.251] | 2.375 [1.462, 3.619] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.320, 0.680] | 5.538 [3.684, 8.000] | 2.385 [1.468, 3.650] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 8.647 [5.952, 12.813] | 3.706 [2.333, 6.018] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 5.000 [2.667, 9.751] | 1.833 [0.925, 3.562] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.246 (126 of 1873 days never flag) | 242 | 0.671 | 0.388 | 0.0496 | +0.0219 [+0.0139, +0.0309] | +0.0068 [+0.0022, +0.0122] | 0.898 | 0.586 | yes |
| 2 | 0.269 (126 of 1872 days never flag) | 233 | 0.626 | 0.373 | 0.0530 | +0.0180 [+0.0112, +0.0255] | +0.0080 [+0.0029, +0.0135] | 0.881 | 0.542 | yes |
| 3 | 0.277 (126 of 1871 days never flag) | 188 | 0.507 | 0.372 | 0.0541 | +0.0166 [+0.0099, +0.0244] | +0.0103 [+0.0052, +0.0164] | 0.887 | 0.439 | yes |
| 4 | 0.283 (126 of 1870 days never flag) | 229 | 0.580 | 0.349 | 0.0567 | +0.0141 [+0.0078, +0.0213] | +0.0057 [+0.0011, +0.0112] | 0.871 | 0.494 | yes |
| 5 | 0.284 (126 of 1869 days never flag) | 227 | 0.601 | 0.366 | 0.0574 | +0.0136 [+0.0066, +0.0208] | +0.0060 [+0.0007, +0.0117] | 0.876 | 0.518 | yes |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 yes, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.712 (climatology 0.512, difference +0.1996 [+0.0727, +0.2914]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0302, +0.0598], realised minus predicted +0.0422 [+0.0127, +0.0756]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.385 | 0.2612 | 0.2720 | +0.0460 [+0.0127, +0.0833] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0935 | 0.0159 | +0.0328 [+0.0266, +0.0391] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0320 | 0.0000 | +0.0127 [+0.0111, +0.0144] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0255 | 0.0200 | +0.0010 [-0.0043, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.436 | 0.1116 | 0.1165 | +0.0229 [-0.0053, +0.0574] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0293 | 0.0048 | +0.0080 [+0.0061, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0627 | 0.0000 | +0.0267 [+0.0212, +0.0319] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.500 | 0.1266 | 0.2439 | 0.0248 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.720 | 0.390 | 0.2599 | 0.2615 | +0.0485 [+0.0200, +0.0816] |
| day_type | month_end | 150 | 17 | 0.824 | 0.609 | 0.1021 | 0.1133 | +0.0421 [+0.0202, +0.0713] |
| day_type | ordinary | 1603 | 101 | 0.683 | 0.342 | 0.0934 | 0.0630 | +0.0169 [+0.0088, +0.0259] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1348 | 0.2903 | +0.0922 [+0.0137, +0.1746] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1164 | 0.1461 | +0.0534 [+0.0285, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1018 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2480 | 0.2213 |

