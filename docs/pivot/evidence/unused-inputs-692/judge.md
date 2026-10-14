# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `19657ffd11f6…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## risk_gbm_base_dealer (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.394, 0.757] | 0.192 | 2.04 flat / 1.41 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.500] | 0.115 | 1.31 flat / 0.84 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.394, 0.757] | 1.385 [0.861, 2.174] | 0.904 [0.513, 1.546] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.458] | 1.154 [0.682, 1.818] | 0.663 [0.329, 1.177] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 1.154 [0.692, 1.833] | 0.683 [0.337, 1.224] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.419] | 1.000 [0.560, 1.607] | 0.529 [0.228, 0.962] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.115 [0.640, 1.778] | 0.644 [0.300, 1.150] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.812] | 1.412 [0.812, 2.294] | 0.676 [0.323, 1.271] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 3.222 (no interval) | 2.806 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 79 | 0.307 | 0.544 | 0.0585 | +0.0130 [+0.0077, +0.0176] | -0.0021 [-0.0098, +0.0052] | 0.643 | 0.286 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 58 | 0.201 | 0.483 | 0.0683 | +0.0028 [-0.0039, +0.0088] | -0.0072 [-0.0158, +0.0003] | 0.578 | 0.184 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 59 | 0.210 | 0.492 | 0.0656 | +0.0051 [-0.0017, +0.0108] | -0.0012 [-0.0091, +0.0054] | 0.580 | 0.193 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 49 | 0.167 | 0.469 | 0.0677 | +0.0031 [-0.0036, +0.0091] | -0.0054 [-0.0131, +0.0015] | 0.579 | 0.152 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 51 | 0.159 | 0.431 | 0.0692 | +0.0017 [-0.0048, +0.0077] | -0.0058 [-0.0135, +0.0006] | 0.576 | 0.143 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.528 (climatology 0.512, difference +0.0153 [-0.1197, +0.1411]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1038, ΔBrier vs climatology +0.0257 [+0.0163, +0.0355], realised minus predicted +0.0910 [+0.0549, +0.1294]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.1035 | 0.2720 | -0.0001 [-0.0190, +0.0194] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0149 | 0.0159 | +0.0354 [+0.0251, +0.0453] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0008 | 0.0200 | +0.0020 [-0.0025, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0353 | 0.1165 | +0.0185 [+0.0035, +0.0377] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0011 | 0.0048 | +0.0086 [+0.0065, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0039 | 0.0000 | +0.0314 [+0.0245, +0.0379] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.750 | 0.0453 | 0.2439 | 0.0380 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.312 | 0.582 | 0.0992 | 0.2615 | +0.0082 [-0.0098, +0.0253] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1008 | 0.1133 | +0.0384 [+0.0156, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0122 | 0.0630 | +0.0049 [-0.0002, +0.0094] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2125 | 0.2903 | +0.0939 [+0.0071, +0.1792] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.625 | 0.1170 | 0.1461 | +0.0871 [+0.0620, +0.1134] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4121 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2610 | 0.2213 |

## risk_gbm_base_policy (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.714] | 0.192 | 1.88 flat / 1.31 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.115 | 1.27 flat / 0.80 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.357, 0.714] | 1.308 [0.818, 2.075] | 0.865 [0.491, 1.485] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 0.808 [0.435, 1.334] | 0.375 [0.149, 0.742] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.161, 0.467] | 1.000 [0.568, 1.632] | 0.548 [0.250, 1.012] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.467] | 0.846 [0.474, 1.375] | 0.394 [0.167, 0.750] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 1.077 [0.613, 1.700] | 0.606 [0.271, 1.114] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.815] | 1.294 [0.759, 2.214] | 0.603 [0.306, 1.125] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.000 [1.429, 6.800] | 2.639 [1.159, 6.335] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 76 | 0.300 | 0.553 | 0.0587 | +0.0127 [+0.0074, +0.0181] | -0.0024 [-0.0106, +0.0050] | 0.643 | 0.280 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 44 | 0.165 | 0.523 | 0.0684 | +0.0027 [-0.0039, +0.0087] | -0.0073 [-0.0154, +0.0002] | 0.578 | 0.153 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 51 | 0.181 | 0.490 | 0.0672 | +0.0035 [-0.0033, +0.0094] | -0.0028 [-0.0105, +0.0038] | 0.580 | 0.166 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 50 | 0.203 | 0.560 | 0.0670 | +0.0038 [-0.0024, +0.0100] | -0.0046 [-0.0121, +0.0021] | 0.580 | 0.190 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 49 | 0.152 | 0.429 | 0.0684 | +0.0025 [-0.0040, +0.0085] | -0.0050 [-0.0127, +0.0016] | 0.577 | 0.136 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.558 (climatology 0.512, difference +0.0454 [-0.0947, +0.1684]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1034, ΔBrier vs climatology +0.0261 [+0.0171, +0.0351], realised minus predicted +0.0943 [+0.0590, +0.1308]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.612 | 0.0868 | 0.2720 | -0.0044 [-0.0269, +0.0165] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0152 | 0.0159 | +0.0368 [+0.0276, +0.0455] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0019 | 0.0200 | +0.0035 [-0.0004, +0.0063] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0320 | 0.1165 | +0.0199 [+0.0050, +0.0391] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0011 | 0.0048 | +0.0094 [+0.0078, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0042 | 0.0000 | +0.0314 [+0.0251, +0.0375] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.667 | 0.0223 | 0.2439 | 0.0128 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.312 | 0.609 | 0.0871 | 0.2615 | +0.0075 [-0.0128, +0.0267] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0895 | 0.1133 | +0.0391 [+0.0177, +0.0601] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.552 | 0.0118 | 0.0630 | +0.0051 [+0.0000, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.2037 | 0.2903 | +0.1293 [+0.0579, +0.2050] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.0718 | 0.1461 | +0.0647 [+0.0378, +0.0910] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.7478 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2478 | 0.2213 |

## risk_gbm_base_settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.760] | 0.192 | 2.38 flat / 1.72 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.200, 0.500] | 0.154 | 1.69 flat / 1.19 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 1.385 [0.914, 2.106] | 0.856 [0.500, 1.429] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 1.038 [0.615, 1.680] | 0.567 [0.279, 1.012] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.166, 0.467] | 1.231 [0.750, 2.000] | 0.750 [0.363, 1.388] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 1.038 [0.606, 1.737] | 0.567 [0.259, 1.083] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 1.423 [0.844, 2.333] | 0.971 [0.477, 1.750] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.818] | 1.412 [0.800, 2.333] | 0.676 [0.325, 1.281] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 4.222 (no interval) | 3.694 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 77 | 0.293 | 0.532 | 0.0592 | +0.0123 [+0.0069, +0.0173] | -0.0028 [-0.0110, +0.0044] | 0.643 | 0.272 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 50 | 0.165 | 0.460 | 0.0689 | +0.0021 [-0.0047, +0.0081] | -0.0079 [-0.0164, -0.0003] | 0.577 | 0.150 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 58 | 0.188 | 0.448 | 0.0681 | +0.0026 [-0.0045, +0.0092] | -0.0037 [-0.0120, +0.0038] | 0.579 | 0.170 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 53 | 0.188 | 0.491 | 0.0667 | +0.0041 [-0.0025, +0.0100] | -0.0043 [-0.0120, +0.0022] | 0.579 | 0.173 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 59 | 0.159 | 0.373 | 0.0685 | +0.0024 [-0.0044, +0.0080] | -0.0051 [-0.0134, +0.0014] | 0.578 | 0.138 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.541 (climatology 0.512, difference +0.0291 [-0.0946, +0.1378]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1066, ΔBrier vs climatology +0.0228 [+0.0138, +0.0327], realised minus predicted +0.0906 [+0.0561, +0.1279]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0958 | 0.2720 | -0.0012 [-0.0213, +0.0175] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0206 | 0.0159 | +0.0357 [+0.0252, +0.0458] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0005 | 0.0200 | +0.0015 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0362 | 0.1165 | +0.0150 [-0.0007, +0.0344] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0007 | 0.0048 | +0.0089 [+0.0070, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0053 | 0.0000 | +0.0309 [+0.0249, +0.0377] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.0113 | 0.2439 | -0.0104 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.588 | 0.0994 | 0.2615 | +0.0093 [-0.0097, +0.0271] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0969 | 0.1133 | +0.0421 [+0.0201, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.516 | 0.0122 | 0.0630 | +0.0049 [-0.0005, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.571 | 0.1682 | 0.2903 | +0.0757 [-0.0132, +0.1620] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1245 | 0.1461 | +0.0716 [+0.0464, +0.0990] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4908 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2004 | 0.2213 |

## risk_gbm_dealer (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.192 | 2.00 flat / 1.38 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.435] | 0.154 | 1.46 flat / 0.99 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.192 [0.742, 1.810] | 0.654 [0.370, 1.078] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.458] | 1.231 [0.750, 1.910] | 0.740 [0.375, 1.312] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.414] | 1.077 [0.640, 1.667] | 0.625 [0.312, 1.109] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.120, 0.414] | 0.923 [0.541, 1.421] | 0.471 [0.239, 0.820] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.379] | 1.154 [0.683, 1.833] | 0.683 [0.331, 1.214] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.800] | 1.353 [0.778, 2.250] | 0.618 [0.293, 1.125] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.806 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 73 | 0.300 | 0.575 | 0.0586 | +0.0128 [+0.0071, +0.0183] | -0.0023 [-0.0107, +0.0052] | 0.643 | 0.282 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 56 | 0.173 | 0.429 | 0.0682 | +0.0029 [-0.0034, +0.0085] | -0.0071 [-0.0152, +0.0002] | 0.578 | 0.154 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 56 | 0.203 | 0.500 | 0.0665 | +0.0042 [-0.0029, +0.0103] | -0.0022 [-0.0103, +0.0046] | 0.579 | 0.187 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 49 | 0.181 | 0.510 | 0.0675 | +0.0034 [-0.0035, +0.0094] | -0.0051 [-0.0133, +0.0017] | 0.579 | 0.167 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 52 | 0.159 | 0.423 | 0.0694 | +0.0015 [-0.0054, +0.0077] | -0.0060 [-0.0140, +0.0009] | 0.577 | 0.142 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.518 (climatology 0.512, difference +0.0053 [-0.1382, +0.1309]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1049, ΔBrier vs climatology +0.0246 [+0.0153, +0.0339], realised minus predicted +0.0940 [+0.0579, +0.1329]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.1000 | 0.2720 | -0.0000 [-0.0221, +0.0205] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0125 | 0.0159 | +0.0397 [+0.0317, +0.0483] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0004 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0025 | 0.0200 | +0.0041 [+0.0002, +0.0076] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0382 | 0.1165 | +0.0110 [-0.0054, +0.0332] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0025 | 0.0048 | +0.0084 [+0.0059, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0016 | 0.0000 | +0.0318 [+0.0251, +0.0383] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0117 | 0.2439 | 0.0001 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.588 | 0.0992 | 0.2615 | +0.0112 [-0.0091, +0.0313] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.1031 | 0.1133 | +0.0509 [+0.0285, +0.0744] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.556 | 0.0122 | 0.0630 | +0.0042 [-0.0015, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2462 | 0.2903 | +0.0944 [-0.0024, +0.1864] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.0935 | 0.1461 | +0.0758 [+0.0506, +0.1007] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6580 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2088 | 0.2213 |

## risk_gbm_policy (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.677] | 0.192 | 1.96 flat / 1.38 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.130, 0.423] | 0.115 | 1.35 flat / 0.88 weighted | reported only; meets far recall: no |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.677] | 1.192 [0.758, 1.842] | 0.750 [0.440, 1.269] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 1.154 [0.694, 1.818] | 0.683 [0.348, 1.216] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 0.923 [0.556, 1.444] | 0.471 [0.250, 0.818] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 0.769 [0.439, 1.191] | 0.317 [0.155, 0.538] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.115 [0.676, 1.742] | 0.644 [0.323, 1.163] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.368, 0.813] | 1.294 [0.750, 2.154] | 0.603 [0.308, 1.125] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.861 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 72 | 0.293 | 0.569 | 0.0578 | +0.0136 [+0.0076, +0.0191] | -0.0014 [-0.0101, +0.0062] | 0.642 | 0.275 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 55 | 0.180 | 0.455 | 0.0683 | +0.0028 [-0.0042, +0.0085] | -0.0072 [-0.0161, -0.0000] | 0.578 | 0.163 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 52 | 0.203 | 0.538 | 0.0670 | +0.0037 [-0.0033, +0.0097] | -0.0026 [-0.0107, +0.0037] | 0.580 | 0.189 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 46 | 0.188 | 0.565 | 0.0671 | +0.0038 [-0.0029, +0.0099] | -0.0047 [-0.0121, +0.0022] | 0.579 | 0.177 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 50 | 0.152 | 0.420 | 0.0693 | +0.0016 [-0.0050, +0.0078] | -0.0059 [-0.0136, +0.0011] | 0.578 | 0.135 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.525 (climatology 0.512, difference +0.0128 [-0.1168, +0.1361]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1036, ΔBrier vs climatology +0.0259 [+0.0165, +0.0357], realised minus predicted +0.0944 [+0.0588, +0.1313]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.284 | 0.617 | 0.0915 | 0.2720 | -0.0001 [-0.0239, +0.0219] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0127 | 0.0159 | +0.0405 [+0.0328, +0.0486] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.400 | 1.000 | 0.0044 | 0.0200 | +0.0062 [+0.0011, +0.0126] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0317 | 0.1165 | +0.0143 [-0.0000, +0.0337] |
| scarcity_state | 0 | 1041 | 5 | 0.400 | 0.400 | 0.0023 | 0.0048 | +0.0097 [+0.0078, +0.0117] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0019 | 0.0000 | +0.0317 [+0.0249, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 1.000 | 0.0118 | 0.2439 | -0.0024 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.304 | 0.603 | 0.0908 | 0.2615 | +0.0118 [-0.0097, +0.0312] |
| day_type | month_end | 150 | 17 | 0.706 | 0.480 | 0.0940 | 0.1133 | +0.0509 [+0.0277, +0.0732] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.593 | 0.0119 | 0.0630 | +0.0046 [-0.0008, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2256 | 0.2903 | +0.1304 [+0.0517, +0.2167] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.0760 | 0.1461 | +0.0726 [+0.0421, +0.1023] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.7523 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2014 | 0.2213 |

## risk_gbm_settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.192 | 2.31 flat / 1.64 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.161, 0.458] | 0.154 | 1.58 flat / 1.11 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.654] | 1.308 [0.857, 1.955] | 0.769 [0.471, 1.275] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 1.154 [0.704, 1.800] | 0.654 [0.321, 1.175] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.429] | 1.038 [0.625, 1.650] | 0.587 [0.288, 1.060] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.133, 0.429] | 0.885 [0.517, 1.435] | 0.433 [0.216, 0.774] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 1.269 [0.733, 2.059] | 0.817 [0.388, 1.481] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.385, 0.824] | 1.412 [0.833, 2.385] | 0.676 [0.333, 1.308] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 4.000 [2.100, 9.000] | 3.472 [1.656, 8.375] |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 77 | 0.307 | 0.558 | 0.0577 | +0.0138 [+0.0080, +0.0192] | -0.0013 [-0.0101, +0.0062] | 0.642 | 0.288 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 54 | 0.173 | 0.444 | 0.0684 | +0.0026 [-0.0039, +0.0085] | -0.0074 [-0.0155, -0.0001] | 0.578 | 0.155 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 55 | 0.203 | 0.509 | 0.0673 | +0.0034 [-0.0033, +0.0095] | -0.0029 [-0.0105, +0.0038] | 0.579 | 0.187 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 50 | 0.196 | 0.540 | 0.0668 | +0.0040 [-0.0023, +0.0096] | -0.0044 [-0.0117, +0.0019] | 0.580 | 0.182 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 58 | 0.181 | 0.431 | 0.0680 | +0.0029 [-0.0036, +0.0088] | -0.0046 [-0.0120, +0.0021] | 0.578 | 0.162 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.544 (climatology 0.512, difference +0.0316 [-0.0964, +0.1448]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1050, ΔBrier vs climatology +0.0244 [+0.0152, +0.0343], realised minus predicted +0.0929 [+0.0575, +0.1281]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.0961 | 0.2720 | +0.0015 [-0.0217, +0.0219] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0127 | 0.0159 | +0.0400 [+0.0314, +0.0486] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0009 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.400 | 1.000 | 0.0031 | 0.0200 | +0.0049 [+0.0007, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.600 | 0.0403 | 0.1165 | +0.0146 [-0.0049, +0.0411] |
| scarcity_state | 0 | 1041 | 5 | 0.400 | 0.333 | 0.0022 | 0.0048 | +0.0095 [+0.0077, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0018 | 0.0000 | +0.0317 [+0.0251, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0279 | 0.2439 | -0.0319 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.328 | 0.603 | 0.0977 | 0.2615 | +0.0152 [-0.0061, +0.0345] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.0997 | 0.1133 | +0.0557 [+0.0345, +0.0794] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.552 | 0.0126 | 0.0630 | +0.0049 [-0.0004, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.1978 | 0.2903 | +0.1051 [+0.0255, +0.1869] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1061 | 0.1461 | +0.0702 [+0.0372, +0.1053] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6724 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

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

## risk_logistic_base_dealer (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.481, 0.810] | 0.231 | 3.27 flat / 2.54 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.192 | 2.38 flat / 1.84 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.409, 0.737] | 2.269 [1.535, 3.501] | 1.692 [1.040, 2.799] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.423] | 1.846 [1.125, 3.050] | 1.385 [0.743, 2.466] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.136, 0.423] | 1.577 [0.897, 2.667] | 1.163 [0.565, 2.158] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.480] | 2.038 [1.250, 3.333] | 1.548 [0.833, 2.736] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.516] | 2.115 [1.323, 3.429] | 1.615 [0.879, 2.861] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.571, 0.923] | 1.412 [0.812, 2.273] | 0.647 [0.342, 1.179] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 6.778 (no interval) | 6.111 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0251 (84 of 1873 days never flag) | 107 | 0.343 | 0.449 | 0.0618 | +0.0096 [+0.0045, +0.0143] | -0.0055 [-0.0140, +0.0020] | 0.643 | 0.309 | no |
| 2 | 0.0664 (147 of 1872 days never flag) | 76 | 0.201 | 0.368 | 0.0691 | +0.0019 [-0.0044, +0.0079] | -0.0081 [-0.0163, -0.0007] | 0.578 | 0.174 | no |
| 3 | 0.207 (147 of 1871 days never flag) | 69 | 0.203 | 0.406 | 0.0698 | +0.0009 [-0.0063, +0.0073] | -0.0054 [-0.0132, +0.0020] | 0.579 | 0.179 | no |
| 4 | 0.0546 (147 of 1870 days never flag) | 82 | 0.210 | 0.354 | 0.0702 | +0.0007 [-0.0059, +0.0067] | -0.0078 [-0.0159, -0.0006] | 0.578 | 0.180 | no |
| 5 | 0.393 (147 of 1869 days never flag) | 84 | 0.210 | 0.345 | 0.0694 | +0.0015 [-0.0055, +0.0078] | -0.0060 [-0.0141, +0.0011] | 0.578 | 0.178 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.592 (climatology 0.512, difference +0.0798 [-0.0434, +0.1942]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1080, ΔBrier vs climatology +0.0215 [+0.0108, +0.0327], realised minus predicted +0.0722 [+0.0379, +0.1084]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.607 | 0.1095 | 0.2720 | -0.0064 [-0.0265, +0.0112] |
| regime | 2020 | 251 | 4 | 0.250 | 0.037 | 0.0366 | 0.0159 | +0.0237 [+0.0128, +0.0332] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0039 | 0.0200 | +0.0047 [+0.0006, +0.0086] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0472 | 0.1165 | +0.0119 [-0.0045, +0.0318] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.125 | 0.0035 | 0.0048 | +0.0083 [+0.0058, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0163 | 0.0000 | +0.0227 [+0.0163, +0.0285] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0396 | 0.2439 | 0.0037 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.605 | 0.1102 | 0.2615 | +0.0044 [-0.0142, +0.0221] |
| day_type | month_end | 150 | 17 | 0.824 | 0.424 | 0.1079 | 0.1133 | +0.0310 [+0.0053, +0.0583] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.459 | 0.0128 | 0.0630 | +0.0042 [-0.0010, +0.0086] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.500 | 0.3780 | 0.2903 | +0.0717 [-0.0136, +0.1525] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.435 | 0.1644 | 0.1461 | +0.0495 [+0.0091, +0.0911] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4002 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_logistic_base_policy (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.394, 0.758] | 0.231 | 3.69 flat / 2.93 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.515] | 0.192 | 2.27 flat / 1.69 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.367, 0.719] | 2.423 [1.667, 3.667] | 1.798 [1.176, 2.912] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.846 [1.235, 2.833] | 1.240 [0.769, 2.074] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.462] | 1.731 [1.100, 2.790] | 1.212 [0.677, 2.150] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.462] | 1.885 [1.200, 3.056] | 1.365 [0.763, 2.432] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.192 [1.419, 3.445] | 1.644 [0.965, 2.803] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.812] | 1.471 [0.833, 2.412] | 0.706 [0.342, 1.317] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 7.889 (no interval) | 7.139 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0171 (105 of 1873 days never flag) | 109 | 0.329 | 0.422 | 0.0606 | +0.0108 [+0.0052, +0.0161] | -0.0043 [-0.0122, +0.0026] | 0.643 | 0.292 | no |
| 2 | 0.00714 (147 of 1872 days never flag) | 77 | 0.209 | 0.377 | 0.0662 | +0.0048 [-0.0026, +0.0110] | -0.0052 [-0.0138, +0.0018] | 0.579 | 0.181 | no |
| 3 | 0.023 (147 of 1871 days never flag) | 74 | 0.210 | 0.392 | 0.0659 | +0.0048 [-0.0019, +0.0111] | -0.0015 [-0.0090, +0.0053] | 0.580 | 0.184 | no |
| 4 | 0.155 (147 of 1870 days never flag) | 78 | 0.210 | 0.372 | 0.0685 | +0.0024 [-0.0047, +0.0088] | -0.0061 [-0.0142, +0.0014] | 0.579 | 0.182 | no |
| 5 | 0.0159 (147 of 1869 days never flag) | 87 | 0.217 | 0.345 | 0.0687 | +0.0022 [-0.0045, +0.0086] | -0.0053 [-0.0133, +0.0021] | 0.578 | 0.184 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.9 over 1041 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 3.4 over 1041 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.512, difference +0.0810 [-0.0525, +0.2133]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1022, ΔBrier vs climatology +0.0273 [+0.0160, +0.0391], realised minus predicted +0.0782 [+0.0448, +0.1143]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1124 | 0.2720 | -0.0110 [-0.0312, +0.0085] |
| regime | 2020 | 251 | 4 | 0.250 | 0.053 | 0.0150 | 0.0159 | +0.0348 [+0.0252, +0.0439] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0004 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.167 | 0.0048 | 0.0200 | +0.0049 [+0.0008, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.591 | 0.0412 | 0.1165 | +0.0163 [+0.0004, +0.0353] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.062 | 0.0031 | 0.0048 | +0.0089 [+0.0068, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0036 | 0.0000 | +0.0311 [+0.0247, +0.0374] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.667 | 0.0311 | 0.2439 | 0.0055 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.551 | 0.1090 | 0.2615 | +0.0021 [-0.0173, +0.0214] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1082 | 0.1133 | +0.0281 [-0.0009, +0.0596] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.419 | 0.0122 | 0.0630 | +0.0036 [-0.0016, +0.0084] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.400 | 0.3443 | 0.2903 | +0.1098 [+0.0358, +0.1816] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.1267 | 0.1461 | +0.0763 [+0.0436, +0.1151] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2664 | 0.2213 |

## risk_logistic_base_settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.750] | 0.231 | 3.04 flat / 2.28 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.229, 0.552] | 0.192 | 2.23 flat / 1.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.353, 0.706] | 2.308 [1.529, 3.530] | 1.654 [0.991, 2.750] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.161, 0.464] | 1.769 [1.088, 2.850] | 1.269 [0.680, 2.238] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.412] | 1.577 [0.925, 2.600] | 1.135 [0.565, 2.040] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.538 [0.905, 2.500] | 1.038 [0.515, 1.900] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.231, 0.548] | 2.231 [1.458, 3.455] | 1.596 [0.925, 2.715] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.812] | 1.471 [0.857, 2.400] | 0.706 [0.346, 1.316] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.200, 0.857] | 6.000 [3.286, 13.342] | 5.250 [2.608, 12.506] |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0846 (105 of 1873 days never flag) | 106 | 0.329 | 0.434 | 0.0600 | +0.0114 [+0.0061, +0.0161] | -0.0037 [-0.0121, +0.0034] | 0.643 | 0.294 | no |
| 2 | 0.0208 (147 of 1872 days never flag) | 75 | 0.209 | 0.387 | 0.0669 | +0.0041 [-0.0022, +0.0099] | -0.0059 [-0.0138, +0.0016] | 0.579 | 0.182 | no |
| 3 | 0.439 (147 of 1871 days never flag) | 68 | 0.196 | 0.397 | 0.0683 | +0.0023 [-0.0046, +0.0085] | -0.0040 [-0.0118, +0.0028] | 0.579 | 0.172 | no |
| 4 | 0.301 (147 of 1870 days never flag) | 67 | 0.196 | 0.403 | 0.0694 | +0.0014 [-0.0056, +0.0078] | -0.0071 [-0.0154, +0.0006] | 0.577 | 0.173 | no |
| 5 | 0.346 (126 of 1869 days never flag) | 89 | 0.225 | 0.348 | 0.0695 | +0.0014 [-0.0053, +0.0073] | -0.0061 [-0.0141, +0.0010] | 0.577 | 0.191 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.590 (climatology 0.512, difference +0.0779 [-0.0435, +0.1828]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0240 [+0.0140, +0.0343], realised minus predicted +0.0765 [+0.0427, +0.1140]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1105 | 0.2720 | -0.0035 [-0.0247, +0.0153] |
| regime | 2020 | 251 | 4 | 0.250 | 0.032 | 0.0292 | 0.0159 | +0.0289 [+0.0194, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0033 | 0.0200 | +0.0044 [+0.0005, +0.0081] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.722 | 0.0312 | 0.1165 | +0.0160 [+0.0034, +0.0329] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0016 | 0.0048 | +0.0096 [+0.0079, +0.0113] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0090 | 0.0000 | +0.0285 [+0.0226, +0.0346] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.0374 | 0.2439 | -0.0123 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.544 | 0.1079 | 0.2615 | +0.0061 [-0.0125, +0.0236] |
| day_type | month_end | 150 | 17 | 0.765 | 0.433 | 0.1012 | 0.1133 | +0.0352 [+0.0088, +0.0595] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.429 | 0.0126 | 0.0630 | +0.0045 [-0.0009, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3399 | 0.2903 | +0.0866 [+0.0305, +0.1407] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.429 | 0.1318 | 0.1461 | +0.0686 [+0.0351, +0.1064] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2040 | 0.2213 |

## risk_logistic_dealer (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.231 | 3.77 flat / 3.01 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.231 | 2.65 flat / 2.08 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.368, 0.719] | 2.577 [1.769, 4.000] | 1.952 [1.224, 3.251] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.423] | 2.000 [1.269, 3.294] | 1.510 [0.860, 2.657] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.161, 0.471] | 1.692 [1.000, 2.810] | 1.250 [0.659, 2.251] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.471] | 2.308 [1.500, 3.722] | 1.760 [1.038, 3.038] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.231 [1.393, 3.684] | 1.731 [0.958, 3.113] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.455] | 0.706 [0.350, 1.304] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.200, 0.875] | 8.111 [4.665, 19.000] | 7.361 [3.967, 18.003] |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0335 (105 of 1873 days never flag) | 112 | 0.321 | 0.402 | 0.0636 | +0.0078 [+0.0026, +0.0128] | -0.0073 [-0.0159, +0.0005] | 0.642 | 0.283 | no |
| 2 | 0.0727 (147 of 1872 days never flag) | 79 | 0.194 | 0.342 | 0.0704 | +0.0007 [-0.0064, +0.0068] | -0.0093 [-0.0184, -0.0014] | 0.578 | 0.164 | no |
| 3 | 0.077 (147 of 1871 days never flag) | 73 | 0.210 | 0.397 | 0.0705 | +0.0002 [-0.0071, +0.0067] | -0.0061 [-0.0150, +0.0013] | 0.579 | 0.185 | no |
| 4 | 0.0211 (147 of 1870 days never flag) | 88 | 0.203 | 0.318 | 0.0710 | -0.0001 [-0.0068, +0.0064] | -0.0086 [-0.0169, -0.0010] | 0.578 | 0.168 | no |
| 5 | 0.114 (147 of 1869 days never flag) | 85 | 0.196 | 0.318 | 0.0702 | +0.0007 [-0.0061, +0.0073] | -0.0068 [-0.0149, +0.0006] | 0.577 | 0.162 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.4 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 3.4 over 1041 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.588 (climatology 0.512, difference +0.0754 [-0.0446, +0.1928]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1132, ΔBrier vs climatology +0.0163 [+0.0046, +0.0277], realised minus predicted +0.0675 [+0.0315, +0.1043]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.564 | 0.1095 | 0.2720 | -0.0059 [-0.0252, +0.0131] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.0448 | 0.0159 | +0.0131 [-0.0041, +0.0288] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0002 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0053 | 0.0200 | +0.0050 [+0.0010, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.444 | 0.0471 | 0.1165 | +0.0081 [-0.0073, +0.0259] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.071 | 0.0041 | 0.0048 | +0.0082 [+0.0057, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0195 | 0.0000 | +0.0180 [+0.0062, +0.0271] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.0773 | 0.2439 | -0.0389 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.545 | 0.1087 | 0.2615 | +0.0043 [-0.0134, +0.0221] |
| day_type | month_end | 150 | 17 | 0.706 | 0.364 | 0.1146 | 0.1133 | +0.0202 [-0.0070, +0.0475] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.419 | 0.0127 | 0.0630 | +0.0038 [-0.0011, +0.0084] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3987 | 0.2903 | +0.0519 [-0.0489, +0.1447] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1746 | 0.1461 | +0.0436 [-0.0028, +0.0914] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_logistic_policy (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.231 | 3.65 flat / 2.89 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.556] | 0.231 | 2.54 flat / 1.93 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.353, 0.714] | 2.500 [1.724, 3.850] | 1.846 [1.169, 3.013] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 1.846 [1.210, 2.882] | 1.240 [0.730, 2.130] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 2.077 [1.320, 3.319] | 1.558 [0.909, 2.690] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.227, 0.552] | 2.038 [1.310, 3.211] | 1.490 [0.844, 2.560] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 2.154 [1.393, 3.421] | 1.548 [0.887, 2.688] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.812] | 1.471 [0.833, 2.500] | 0.706 [0.337, 1.360] |
| outside 2018-2019 | 9 | 6 | 0.667 [0.333, 1.000] | 7.778 [4.600, 17.333] | 7.028 [3.916, 16.500] |

Recall with equal weight per regime: 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0115 (105 of 1873 days never flag) | 110 | 0.321 | 0.409 | 0.0611 | +0.0103 [+0.0047, +0.0156] | -0.0048 [-0.0129, +0.0027] | 0.642 | 0.284 | no |
| 2 | 0.00765 (147 of 1872 days never flag) | 78 | 0.216 | 0.385 | 0.0678 | +0.0032 [-0.0041, +0.0095] | -0.0068 [-0.0154, +0.0007] | 0.579 | 0.188 | no |
| 3 | 0.00952 (147 of 1871 days never flag) | 84 | 0.217 | 0.357 | 0.0667 | +0.0040 [-0.0032, +0.0104] | -0.0023 [-0.0103, +0.0049] | 0.580 | 0.186 | no |
| 4 | 0.0126 (147 of 1870 days never flag) | 84 | 0.225 | 0.369 | 0.0676 | +0.0032 [-0.0037, +0.0094] | -0.0053 [-0.0131, +0.0019] | 0.580 | 0.194 | no |
| 5 | 0.118 (147 of 1869 days never flag) | 86 | 0.217 | 0.349 | 0.0691 | +0.0019 [-0.0051, +0.0080] | -0.0057 [-0.0136, +0.0017] | 0.577 | 0.185 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.1 over 1041 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 2.9 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.589 (climatology 0.512, difference +0.0767 [-0.0563, +0.2056]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0240 [+0.0127, +0.0356], realised minus predicted +0.0747 [+0.0400, +0.1109]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1094 | 0.2720 | -0.0087 [-0.0307, +0.0124] |
| regime | 2020 | 251 | 4 | 0.250 | 0.042 | 0.0225 | 0.0159 | +0.0286 [+0.0152, +0.0400] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.167 | 0.0056 | 0.0200 | +0.0050 [+0.0006, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0439 | 0.1165 | +0.0152 [-0.0005, +0.0335] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.077 | 0.0034 | 0.0048 | +0.0088 [+0.0065, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0039 | 0.0000 | +0.0306 [+0.0246, +0.0364] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.0651 | 0.2439 | -0.0292 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.538 | 0.1084 | 0.2615 | +0.0037 [-0.0158, +0.0232] |
| day_type | month_end | 150 | 17 | 0.765 | 0.382 | 0.1139 | 0.1133 | +0.0232 [-0.0056, +0.0548] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.425 | 0.0123 | 0.0630 | +0.0036 [-0.0018, +0.0085] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.400 | 0.3666 | 0.2903 | +0.0824 [-0.0069, +0.1672] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.429 | 0.1242 | 0.1461 | +0.0834 [+0.0516, +0.1189] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2340 | 0.2213 |

## risk_logistic_settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.231 | 3.62 flat / 2.86 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.261, 0.586] | 0.231 | 2.65 flat / 2.02 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.348, 0.714] | 2.577 [1.771, 4.067] | 1.894 [1.203, 3.230] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.458] | 1.654 [1.028, 2.762] | 1.183 [0.640, 2.141] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 1.654 [1.000, 2.762] | 1.212 [0.634, 2.219] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.545] | 2.192 [1.444, 3.542] | 1.644 [0.987, 2.870] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.219, 0.548] | 2.462 [1.656, 3.842] | 1.827 [1.129, 3.109] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.818] | 1.471 [0.846, 2.500] | 0.706 [0.328, 1.346] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 7.667 (no interval) | 6.917 (no interval) |

Recall with equal weight per regime: 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0146 (105 of 1873 days never flag) | 112 | 0.321 | 0.402 | 0.0607 | +0.0107 [+0.0054, +0.0152] | -0.0044 [-0.0131, +0.0029] | 0.642 | 0.283 | no |
| 2 | 0.0174 (147 of 1872 days never flag) | 72 | 0.209 | 0.403 | 0.0673 | +0.0037 [-0.0027, +0.0094] | -0.0063 [-0.0141, +0.0008] | 0.579 | 0.184 | no |
| 3 | 0.191 (147 of 1871 days never flag) | 71 | 0.203 | 0.394 | 0.0689 | +0.0018 [-0.0050, +0.0079] | -0.0045 [-0.0126, +0.0024] | 0.579 | 0.178 | no |
| 4 | 0.0201 (147 of 1870 days never flag) | 88 | 0.225 | 0.352 | 0.0691 | +0.0018 [-0.0051, +0.0077] | -0.0067 [-0.0146, +0.0007] | 0.577 | 0.192 | no |
| 5 | 0.00472 (126 of 1869 days never flag) | 94 | 0.217 | 0.319 | 0.0702 | +0.0008 [-0.0066, +0.0070] | -0.0068 [-0.0155, +0.0004] | 0.577 | 0.180 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 2.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 3.6 over 1041 days; regime_2021-23: 2.4 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0629 [-0.0614, +0.1685]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1085, ΔBrier vs climatology +0.0210 [+0.0102, +0.0316], realised minus predicted +0.0745 [+0.0404, +0.1111]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1079 | 0.2720 | -0.0026 [-0.0245, +0.0160] |
| regime | 2020 | 251 | 4 | 0.250 | 0.037 | 0.0297 | 0.0159 | +0.0259 [+0.0120, +0.0376] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0158] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0061 | 0.0200 | +0.0050 [+0.0008, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.0344 | 0.1165 | +0.0119 [-0.0003, +0.0285] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.091 | 0.0033 | 0.0048 | +0.0092 [+0.0074, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0057 | 0.0000 | +0.0295 [+0.0236, +0.0353] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.0716 | 0.2439 | -0.0444 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.538 | 0.1051 | 0.2615 | +0.0063 [-0.0113, +0.0226] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1030 | 0.1133 | +0.0293 [+0.0037, +0.0551] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.405 | 0.0125 | 0.0630 | +0.0040 [-0.0012, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.400 | 0.3745 | 0.2903 | +0.0736 [+0.0048, +0.1405] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1263 | 0.1461 | +0.0774 [+0.0463, +0.1145] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2019 | 0.2213 |

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

## risk_quantile_skewt_base_policy (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.750] | 0.231 | 3.04 flat / 2.32 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.115 | 1.31 flat / 0.78 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.389, 0.750] | 2.577 [1.697, 4.133] | 1.856 [1.095, 3.219] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.368] | 1.385 [0.868, 2.167] | 0.885 [0.482, 1.525] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.136, 0.407] | 0.846 [0.500, 1.364] | 0.433 [0.216, 0.800] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 0.846 [0.480, 1.346] | 0.356 [0.163, 0.667] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.424] | 1.038 [0.606, 1.708] | 0.663 [0.331, 1.224] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.812] | 1.412 [0.786, 2.364] | 0.676 [0.319, 1.275] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 6.111 (no interval) | 5.417 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0724 (84 of 1873 days never flag) | 113 | 0.329 | 0.407 | 0.0647 | +0.0067 [+0.0003, +0.0131] | -0.0084 [-0.0170, -0.0000] | 0.644 | 0.290 | no |
| 2 | 0.0614 (147 of 1872 days never flag) | 58 | 0.158 | 0.379 | 0.0735 | -0.0025 [-0.0114, +0.0055] | -0.0125 [-0.0218, -0.0039] | 0.566 | 0.138 | no |
| 3 | 0.203 (126 of 1871 days never flag) | 45 | 0.167 | 0.511 | 0.0686 | +0.0021 [-0.0058, +0.0094] | -0.0042 [-0.0127, +0.0036] | 0.586 | 0.154 | no |
| 4 | 0.302 (126 of 1870 days never flag) | 43 | 0.152 | 0.488 | 0.0727 | -0.0019 [-0.0102, +0.0055] | -0.0103 [-0.0191, -0.0023] | 0.578 | 0.139 | no |
| 5 | 0.225 (126 of 1869 days never flag) | 46 | 0.138 | 0.413 | 0.0710 | -0.0000 [-0.0083, +0.0074] | -0.0076 [-0.0166, +0.0004] | 0.580 | 0.122 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.632 (climatology 0.512, difference +0.1198 [-0.0028, +0.2377]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1169, ΔBrier vs climatology +0.0126 [-0.0008, +0.0255], realised minus predicted +0.0626 [+0.0284, +0.0998]; calibrated no, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.556 | 0.1277 | 0.2720 | -0.0230 [-0.0492, +0.0033] |
| regime | 2020 | 251 | 4 | 0.250 | 0.031 | 0.0372 | 0.0159 | +0.0212 [+0.0097, +0.0319] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0020 | 0.0000 | +0.0137 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0079 | 0.0200 | +0.0017 [-0.0037, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0453 | 0.1165 | +0.0207 [+0.0023, +0.0441] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.167 | 0.0037 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0191 | 0.0000 | +0.0193 [+0.0101, +0.0276] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.0627 | 0.2439 | -0.0218 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.545 | 0.1246 | 0.2615 | -0.0040 [-0.0271, +0.0205] |
| day_type | month_end | 150 | 17 | 0.706 | 0.353 | 0.1440 | 0.1133 | +0.0065 [-0.0296, +0.0462] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.429 | 0.0146 | 0.0630 | +0.0021 [-0.0036, +0.0071] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.2920 | 0.2903 | +0.0806 [+0.0118, +0.1446] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.400 | 0.2013 | 0.1461 | +0.0647 [+0.0023, +0.1360] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4287 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2058 | 0.2213 |

## risk_quantile_skewt_base_settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.361, 0.720] | 0.231 | 2.92 flat / 2.22 weighted | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.193, 0.500] | 0.192 | 2.15 flat / 1.60 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.682] | 2.115 [1.405, 3.333] | 1.548 [0.924, 2.647] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.000 [1.290, 3.158] | 1.385 [0.767, 2.469] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.000 [1.226, 3.235] | 1.471 [0.776, 2.667] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.923 [1.172, 3.091] | 1.365 [0.689, 2.425] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.923 [1.151, 3.125] | 1.394 [0.716, 2.527] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.824] | 1.294 [0.765, 2.201] | 0.588 [0.278, 1.175] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 6.000 (no interval) | 5.306 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.262 (63 of 1873 days never flag) | 97 | 0.300 | 0.433 | 0.0628 | +0.0086 [+0.0020, +0.0154] | -0.0065 [-0.0154, +0.0023] | 0.645 | 0.268 | no |
| 2 | 0.104 (126 of 1872 days never flag) | 82 | 0.216 | 0.366 | 0.0679 | +0.0031 [-0.0043, +0.0097] | -0.0069 [-0.0155, +0.0009] | 0.577 | 0.186 | no |
| 3 | 0.233 (126 of 1871 days never flag) | 82 | 0.217 | 0.366 | 0.0664 | +0.0043 [-0.0034, +0.0112] | -0.0020 [-0.0108, +0.0059] | 0.583 | 0.187 | no |
| 4 | 0.49 (126 of 1870 days never flag) | 79 | 0.210 | 0.367 | 0.0676 | +0.0032 [-0.0039, +0.0101] | -0.0052 [-0.0135, +0.0022] | 0.581 | 0.181 | no |
| 5 | 0.263 (126 of 1869 days never flag) | 77 | 0.196 | 0.351 | 0.0667 | +0.0042 [-0.0027, +0.0107] | -0.0033 [-0.0112, +0.0043] | 0.586 | 0.167 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.512, difference +0.0710 [-0.0779, +0.2074]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1045, ΔBrier vs climatology +0.0249 [+0.0121, +0.0376], realised minus predicted +0.0523 [+0.0205, +0.0861]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.284 | 0.604 | 0.1308 | 0.2720 | -0.0076 [-0.0330, +0.0200] |
| regime | 2020 | 251 | 4 | 0.250 | 0.034 | 0.0636 | 0.0159 | +0.0110 [+0.0001, +0.0215] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0051 | 0.0000 | +0.0132 [+0.0116, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0113 | 0.0200 | +0.0014 [-0.0047, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0516 | 0.1165 | +0.0238 [+0.0047, +0.0472] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0064 | 0.0048 | +0.0086 [+0.0066, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0394 | 0.0000 | +0.0129 [+0.0049, +0.0201] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.0783 | 0.2439 | -0.0113 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.615 | 0.1303 | 0.2615 | +0.0073 [-0.0173, +0.0341] |
| day_type | month_end | 150 | 17 | 0.706 | 0.400 | 0.1583 | 0.1133 | +0.0132 [-0.0215, +0.0495] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.455 | 0.0178 | 0.0630 | +0.0032 [-0.0028, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3618 | 0.2903 | +0.1280 [+0.0556, +0.2084] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.375 | 0.2365 | 0.1461 | +0.0553 [+0.0074, +0.1112] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

