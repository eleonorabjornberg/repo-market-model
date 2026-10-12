# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `3c716e7f0d09…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

- h = 1: scarcity_state_0: 3.4 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 no (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 yes. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.512, difference +0.2031 [+0.0494, +0.3418]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0718, ΔBrier vs climatology +0.0577 [+0.0397, +0.0765], realised minus predicted +0.0295 [+0.0055, +0.0555]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.531 | 0.1724 | 0.2720 | +0.0442 [+0.0158, +0.0733] |
| regime | 2020 | 251 | 4 | 0.500 | 0.182 | 0.0283 | 0.0159 | +0.0350 [+0.0212, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0179 | 0.0200 | -0.0058 [-0.0174, +0.0034] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.444 | 0.0904 | 0.1165 | +0.0264 [+0.0024, +0.0563] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0097 | 0.0048 | +0.0062 [+0.0027, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0029 | 0.0000 | +0.0316 [+0.0245, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.700 | 0.412 | 0.1359 | 0.2439 | 0.0342 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.517 | 0.1781 | 0.2615 | +0.0479 [+0.0229, +0.0742] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1010 | 0.1133 | +0.0595 [+0.0347, +0.0862] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.420 | 0.0445 | 0.0630 | +0.0136 [+0.0073, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0432, +0.2095] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.0989 | 0.1461 | +0.0689 [+0.0395, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3803 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41+iorb+tailcap50 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.720] | 0.192 | 2.19 flat / 1.48 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.192 | 1.85 flat / 1.25 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.682] | 1.423 [0.968, 2.158] | 0.788 [0.493, 1.300] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 0.962 [0.576, 1.579] | 0.577 [0.320, 1.031] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.579] | 1.385 [0.857, 2.251] | 0.885 [0.484, 1.605] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.579] | 1.154 [0.722, 1.875] | 0.683 [0.371, 1.208] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.154 [0.703, 1.867] | 0.779 [0.423, 1.395] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.842, 2.333] | 0.647 [0.336, 1.161] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.750] | 3.667 [2.000, 8.750] | 3.056 [1.516, 8.000] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 78 | 0.293 | 0.526 | 0.0579 | +0.0135 [+0.0077, +0.0191] | -0.0016 [-0.0105, +0.0060] | 0.632 | 0.272 | no |
| 2 | 0.111 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0594 | +0.0117 [+0.0066, +0.0165] | +0.0017 [-0.0056, +0.0083] | 0.628 | 0.259 | no |
| 3 | 0.115 (147 of 1871 days never flag) | 75 | 0.283 | 0.520 | 0.0613 | +0.0093 [+0.0041, +0.0142] | +0.0030 [-0.0035, +0.0091] | 0.624 | 0.262 | no |
| 4 | 0.12 (147 of 1870 days never flag) | 68 | 0.275 | 0.559 | 0.0588 | +0.0120 [+0.0072, +0.0167] | +0.0035 [-0.0029, +0.0096] | 0.624 | 0.258 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 67 | 0.268 | 0.552 | 0.0592 | +0.0117 [+0.0070, +0.0160] | +0.0041 [-0.0018, +0.0097] | 0.625 | 0.251 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.512, difference +0.2031 [+0.0535, +0.3339]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0864, ΔBrier vs climatology +0.0431 [+0.0303, +0.0567], realised minus predicted +0.0567 [+0.0283, +0.0894]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0218, +0.0237] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0168 | 0.0159 | +0.0382 [+0.0295, +0.0469] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0023 | 0.0000 | +0.0137 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0009 | 0.0200 | +0.0014 [-0.0037, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0395 | 0.1165 | +0.0174 [-0.0002, +0.0407] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0026 | 0.0048 | +0.0085 [+0.0064, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0021 | 0.0000 | +0.0317 [+0.0250, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0413 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.0993 | 0.2615 | +0.0138 [-0.0072, +0.0339] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0972 | 0.1133 | +0.0538 [+0.0309, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.469 | 0.0142 | 0.0630 | +0.0045 [-0.0009, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0417, +0.2080] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0989 | 0.1461 | +0.0689 [+0.0402, +0.0953] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2001 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | false alarms per onset (a day flagged at any horizon is one) | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.852] | 0.231 | 3.35 flat / 1.88 weighted | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 14 | 0.538 [0.344, 0.731] | 0.231 | 2.88 flat / 1.62 weighted | reported only; meets far recall: yes |

Tier 1 at each lead alone, inside and outside the early years, and by regime (reported; not part of the pass rule):

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.370, 0.706] | 1.846 [1.200, 2.800] | 0.962 [0.618, 1.524] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.285, 0.643] | 1.500 [0.828, 2.471] | 0.779 [0.444, 1.271] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.600] | 1.962 [1.172, 3.084] | 1.077 [0.629, 1.779] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.654] | 1.769 [1.000, 2.833] | 0.894 [0.512, 1.457] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.333, 0.731] | 1.846 [1.067, 2.936] | 1.038 [0.609, 1.719] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 3.176 [1.750, 5.401] | 1.265 [0.706, 2.157] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 3.667 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 92 | 0.314 | 0.478 | 0.0570 | +0.0145 [+0.0085, +0.0202] | -0.0006 [-0.0089, +0.0067] | 0.640 | 0.287 | no |
| 2 | 0.111 (147 of 1872 days never flag) | 84 | 0.324 | 0.536 | 0.0583 | +0.0128 [+0.0080, +0.0175] | +0.0028 [-0.0042, +0.0091] | 0.655 | 0.301 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 95 | 0.319 | 0.463 | 0.0608 | +0.0099 [+0.0048, +0.0147] | +0.0036 [-0.0028, +0.0092] | 0.640 | 0.289 | no |
| 4 | 0.12 (147 of 1870 days never flag) | 89 | 0.312 | 0.483 | 0.0580 | +0.0128 [+0.0080, +0.0176] | +0.0044 [-0.0019, +0.0106] | 0.652 | 0.285 | no |
| 5 | 0.172 (147 of 1869 days never flag) | 93 | 0.326 | 0.484 | 0.0579 | +0.0130 [+0.0088, +0.0172] | +0.0055 [-0.0003, +0.0110] | 0.658 | 0.298 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with enough pressure days): 2018-19 no, 2025-26 no. Reported, too few pressure days to test: 2020 yes (4 pressure days), 2021-23 no (0 pressure days), 2024 yes (5 pressure days).

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.512, difference +0.2031 [+0.0618, +0.3351]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0846, ΔBrier vs climatology +0.0449 [+0.0321, +0.0593], realised minus predicted +0.0537 [+0.0225, +0.0854]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.324 | 0.500 | 0.1071 | 0.2720 | +0.0041 [-0.0198, +0.0257] |
| regime | 2020 | 251 | 4 | 0.500 | 0.200 | 0.0208 | 0.0159 | +0.0422 [+0.0351, +0.0497] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0027 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0009 | 0.0200 | +0.0014 [-0.0035, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0395 | 0.1165 | +0.0174 [-0.0004, +0.0399] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0029 | 0.0048 | +0.0085 [+0.0064, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0021 | 0.0000 | +0.0317 [+0.0245, +0.0384] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0413 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.518 | 0.1090 | 0.2615 | +0.0177 [-0.0040, +0.0380] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0972 | 0.1133 | +0.0538 [+0.0309, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.391 | 0.0172 | 0.0630 | +0.0056 [+0.0004, +0.0105] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0400, +0.2085] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0989 | 0.1461 | +0.0689 [+0.0392, +0.0987] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2001 | 0.2213 |

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

