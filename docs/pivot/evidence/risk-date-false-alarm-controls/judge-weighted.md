# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `64ef2d8bd981…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

## calendar_climatology (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.667] | 0.358 | 6.69 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.212, 0.576] | 0.269 | 5.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.267 (84 of 1873 days never flag) | 258 | 0.600 | 0.326 | 0.0714 | +0.0000 [+0.0000, +0.0000] | -0.0151 [-0.0211, -0.0097] | 0.586 | 0.500 | no |
| 2 | 0.267 (147 of 1872 days never flag) | 213 | 0.496 | 0.324 | 0.0711 | +0.0000 [+0.0000, +0.0000] | -0.0100 [-0.0146, -0.0054] | 0.586 | 0.413 | no |
| 3 | 0.267 (147 of 1871 days never flag) | 213 | 0.493 | 0.319 | 0.0707 | +0.0000 [+0.0000, +0.0000] | -0.0063 [-0.0098, -0.0028] | 0.585 | 0.409 | no |
| 4 | 0.267 (147 of 1870 days never flag) | 213 | 0.486 | 0.315 | 0.0708 | +0.0000 [+0.0000, +0.0000] | -0.0085 [-0.0120, -0.0048] | 0.580 | 0.401 | no |
| 5 | 0.267 (147 of 1869 days never flag) | 213 | 0.478 | 0.310 | 0.0709 | +0.0000 [+0.0000, +0.0000] | -0.0075 [-0.0114, -0.0036] | 0.578 | 0.393 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 4.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.273, 0.650] | 0.380 | 7.04 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.256, 0.600] | 0.276 | 5.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.185 (147 of 1873 days never flag) | 286 | 0.736 | 0.360 | 0.0563 | +0.0151 [+0.0094, +0.0214] | +0.0000 [+0.0000, +0.0000] | 0.876 | 0.630 | no |
| 2 | 0.225 (147 of 1872 days never flag) | 215 | 0.655 | 0.423 | 0.0611 | +0.0100 [+0.0056, +0.0146] | +0.0000 [+0.0000, +0.0000] | 0.817 | 0.583 | no |
| 3 | 0.239 (147 of 1871 days never flag) | 243 | 0.645 | 0.366 | 0.0644 | +0.0063 [+0.0030, +0.0098] | +0.0000 [+0.0000, +0.0000] | 0.765 | 0.556 | no |
| 4 | 0.208 (189 of 1870 days never flag) | 222 | 0.594 | 0.369 | 0.0624 | +0.0085 [+0.0047, +0.0121] | +0.0000 [+0.0000, +0.0000] | 0.788 | 0.513 | no |
| 5 | 0.221 (189 of 1869 days never flag) | 199 | 0.587 | 0.407 | 0.0634 | +0.0075 [+0.0036, +0.0114] | +0.0000 [+0.0000, +0.0000] | 0.772 | 0.519 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

## risk_gbm (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.667] | 0.154 | 1.38 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.115 | 1.23 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 78 | 0.300 | 0.538 | 0.0577 | +0.0137 [+0.0082, +0.0193] | -0.0014 [-0.0097, +0.0063] | 0.642 | 0.279 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 55 | 0.180 | 0.455 | 0.0687 | +0.0024 [-0.0040, +0.0080] | -0.0076 [-0.0161, -0.0005] | 0.578 | 0.163 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0667 | +0.0040 [-0.0025, +0.0098] | -0.0023 [-0.0102, +0.0044] | 0.579 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 49 | 0.181 | 0.510 | 0.0668 | +0.0040 [-0.0028, +0.0099] | -0.0045 [-0.0121, +0.0023] | 0.579 | 0.167 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0053, +0.0074] | -0.0062 [-0.0136, +0.0007] | 0.577 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.474, 0.812] | 0.269 | 5.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.645] | 0.269 | 4.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 227 | 0.671 | 0.414 | 0.0478 | +0.0236 [+0.0164, +0.0318] | +0.0085 [+0.0037, +0.0138] | 0.892 | 0.595 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 223 | 0.669 | 0.417 | 0.0601 | +0.0109 [+0.0065, +0.0151] | +0.0009 [-0.0021, +0.0040] | 0.837 | 0.594 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 203 | 0.572 | 0.389 | 0.0605 | +0.0101 [+0.0065, +0.0142] | +0.0038 [+0.0011, +0.0070] | 0.810 | 0.501 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 180 | 0.529 | 0.406 | 0.0594 | +0.0114 [+0.0070, +0.0161] | +0.0030 [+0.0004, +0.0058] | 0.822 | 0.467 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 179 | 0.500 | 0.385 | 0.0629 | +0.0080 [+0.0036, +0.0123] | +0.0004 [-0.0025, +0.0033] | 0.790 | 0.436 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.481, 0.818] | 0.231 | 3.92 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.600] | 0.231 | 3.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 174 | 0.579 | 0.466 | 0.0497 | +0.0218 [+0.0145, +0.0293] | +0.0067 [+0.0016, +0.0119] | 0.804 | 0.525 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 174 | 0.518 | 0.414 | 0.0624 | +0.0087 [+0.0038, +0.0133] | -0.0013 [-0.0055, +0.0024] | 0.749 | 0.459 | no |
| 3 | 0.128 (147 of 1871 days never flag) | 156 | 0.471 | 0.417 | 0.0606 | +0.0101 [+0.0050, +0.0146] | +0.0038 [-0.0008, +0.0076] | 0.747 | 0.419 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 164 | 0.500 | 0.421 | 0.0603 | +0.0106 [+0.0055, +0.0156] | +0.0021 [-0.0014, +0.0056] | 0.760 | 0.445 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 166 | 0.507 | 0.422 | 0.0636 | +0.0073 [+0.0018, +0.0125] | -0.0002 [-0.0042, +0.0037] | 0.742 | 0.452 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.4 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 3.4 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

## risk_gbm+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.269 | 5.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.618] | 0.269 | 5.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 198 | 0.650 | 0.460 | 0.0484 | +0.0230 [+0.0162, +0.0305] | +0.0080 [+0.0031, +0.0132] | 0.880 | 0.588 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 203 | 0.626 | 0.429 | 0.0594 | +0.0117 [+0.0082, +0.0151] | +0.0017 [-0.0019, +0.0051] | 0.821 | 0.559 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 212 | 0.587 | 0.382 | 0.0592 | +0.0115 [+0.0082, +0.0152] | +0.0052 [+0.0015, +0.0089] | 0.800 | 0.511 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 183 | 0.529 | 0.399 | 0.0580 | +0.0129 [+0.0093, +0.0164] | +0.0044 [+0.0018, +0.0072] | 0.813 | 0.465 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 161 | 0.457 | 0.391 | 0.0613 | +0.0097 [+0.0062, +0.0132] | +0.0021 [-0.0008, +0.0051] | 0.781 | 0.400 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.483, 0.818] | 0.269 | 5.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.278, 0.643] | 0.269 | 4.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 226 | 0.671 | 0.416 | 0.0472 | +0.0243 [+0.0170, +0.0321] | +0.0092 [+0.0042, +0.0143] | 0.911 | 0.595 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 221 | 0.669 | 0.421 | 0.0594 | +0.0117 [+0.0071, +0.0160] | +0.0017 [-0.0016, +0.0047] | 0.872 | 0.595 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 199 | 0.572 | 0.397 | 0.0588 | +0.0119 [+0.0083, +0.0155] | +0.0055 [+0.0028, +0.0084] | 0.859 | 0.503 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 176 | 0.529 | 0.415 | 0.0581 | +0.0127 [+0.0085, +0.0172] | +0.0043 [+0.0019, +0.0071] | 0.865 | 0.470 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 176 | 0.500 | 0.392 | 0.0619 | +0.0090 [+0.0046, +0.0133] | +0.0015 [-0.0015, +0.0045] | 0.848 | 0.438 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.438, 0.800] | 0.269 | 4.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.243, 0.613] | 0.269 | 4.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 209 | 0.664 | 0.445 | 0.0484 | +0.0230 [+0.0175, +0.0290] | +0.0080 [+0.0030, +0.0132] | 0.899 | 0.597 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 201 | 0.633 | 0.438 | 0.0604 | +0.0107 [+0.0074, +0.0138] | +0.0007 [-0.0032, +0.0044] | 0.847 | 0.568 | no |
| 3 | 0.125 (147 of 1871 days never flag) | 201 | 0.572 | 0.393 | 0.0598 | +0.0109 [+0.0076, +0.0146] | +0.0046 [+0.0007, +0.0086] | 0.817 | 0.502 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 186 | 0.522 | 0.387 | 0.0592 | +0.0116 [+0.0079, +0.0154] | +0.0032 [-0.0002, +0.0065] | 0.832 | 0.456 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 183 | 0.500 | 0.377 | 0.0624 | +0.0086 [+0.0049, +0.0120] | +0.0010 [-0.0029, +0.0045] | 0.797 | 0.434 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

## risk_gbm_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.419] | 0.154 | 1.38 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 82 | 0.307 | 0.524 | 0.0592 | +0.0122 [+0.0075, +0.0168] | -0.0029 [-0.0106, +0.0039] | 0.643 | 0.285 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 53 | 0.173 | 0.453 | 0.0691 | +0.0020 [-0.0047, +0.0081] | -0.0080 [-0.0168, -0.0003] | 0.578 | 0.156 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 61 | 0.181 | 0.410 | 0.0677 | +0.0029 [-0.0038, +0.0089] | -0.0034 [-0.0115, +0.0034] | 0.579 | 0.160 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0668 | +0.0040 [-0.0023, +0.0100] | -0.0044 [-0.0120, +0.0023] | 0.579 | 0.179 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0055, +0.0072] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.520, 0.850] | 0.269 | 5.19 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.652] | 0.269 | 4.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 231 | 0.686 | 0.416 | 0.0493 | +0.0221 [+0.0150, +0.0301] | +0.0071 [+0.0024, +0.0121] | 0.896 | 0.608 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 222 | 0.669 | 0.419 | 0.0605 | +0.0105 [+0.0064, +0.0147] | +0.0005 [-0.0026, +0.0036] | 0.827 | 0.595 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 201 | 0.558 | 0.383 | 0.0616 | +0.0091 [+0.0053, +0.0128] | +0.0027 [-0.0002, +0.0057] | 0.803 | 0.486 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 188 | 0.536 | 0.394 | 0.0594 | +0.0115 [+0.0069, +0.0160] | +0.0030 [+0.0001, +0.0063] | 0.833 | 0.470 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 183 | 0.493 | 0.372 | 0.0630 | +0.0080 [+0.0035, +0.0121] | +0.0004 [-0.0027, +0.0034] | 0.782 | 0.426 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.517, 0.850] | 0.231 | 3.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 3.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 170 | 0.586 | 0.482 | 0.0511 | +0.0203 [+0.0135, +0.0272] | +0.0052 [+0.0007, +0.0098] | 0.805 | 0.535 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 171 | 0.518 | 0.421 | 0.0628 | +0.0083 [+0.0035, +0.0129] | -0.0017 [-0.0059, +0.0021] | 0.748 | 0.461 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 155 | 0.464 | 0.413 | 0.0617 | +0.0090 [+0.0040, +0.0138] | +0.0027 [-0.0017, +0.0065] | 0.745 | 0.411 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 169 | 0.507 | 0.414 | 0.0602 | +0.0106 [+0.0055, +0.0155] | +0.0021 [-0.0015, +0.0055] | 0.761 | 0.450 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 166 | 0.500 | 0.416 | 0.0636 | +0.0073 [+0.0021, +0.0122] | -0.0002 [-0.0043, +0.0036] | 0.740 | 0.444 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.800] | 0.269 | 5.00 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.269 | 5.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 212 | 0.664 | 0.439 | 0.0493 | +0.0221 [+0.0157, +0.0295] | +0.0070 [+0.0025, +0.0120] | 0.891 | 0.596 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 203 | 0.626 | 0.429 | 0.0598 | +0.0112 [+0.0080, +0.0146] | +0.0012 [-0.0022, +0.0047] | 0.810 | 0.559 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 209 | 0.572 | 0.378 | 0.0602 | +0.0105 [+0.0072, +0.0141] | +0.0042 [+0.0007, +0.0081] | 0.793 | 0.497 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 187 | 0.529 | 0.390 | 0.0577 | +0.0131 [+0.0094, +0.0167] | +0.0047 [+0.0017, +0.0078] | 0.829 | 0.463 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 165 | 0.449 | 0.376 | 0.0613 | +0.0096 [+0.0062, +0.0129] | +0.0021 [-0.0010, +0.0050] | 0.773 | 0.390 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.857] | 0.269 | 5.15 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.285, 0.639] | 0.269 | 4.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 230 | 0.686 | 0.417 | 0.0486 | +0.0228 [+0.0157, +0.0304] | +0.0077 [+0.0033, +0.0127] | 0.912 | 0.608 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 220 | 0.669 | 0.423 | 0.0598 | +0.0113 [+0.0069, +0.0155] | +0.0013 [-0.0017, +0.0044] | 0.870 | 0.596 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 197 | 0.558 | 0.391 | 0.0599 | +0.0108 [+0.0072, +0.0147] | +0.0045 [+0.0016, +0.0074] | 0.855 | 0.489 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 184 | 0.536 | 0.402 | 0.0581 | +0.0128 [+0.0087, +0.0172] | +0.0043 [+0.0015, +0.0075] | 0.869 | 0.473 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 180 | 0.493 | 0.378 | 0.0620 | +0.0090 [+0.0048, +0.0131] | +0.0014 [-0.0017, +0.0045] | 0.844 | 0.428 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.471, 0.833] | 0.269 | 4.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.269 | 4.58 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 213 | 0.664 | 0.437 | 0.0498 | +0.0216 [+0.0164, +0.0270] | +0.0065 [+0.0017, +0.0109] | 0.905 | 0.595 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 199 | 0.626 | 0.437 | 0.0608 | +0.0103 [+0.0070, +0.0134] | +0.0003 [-0.0041, +0.0040] | 0.836 | 0.561 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 190 | 0.529 | 0.384 | 0.0608 | +0.0098 [+0.0064, +0.0132] | +0.0035 [-0.0006, +0.0073] | 0.812 | 0.461 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 195 | 0.551 | 0.390 | 0.0592 | +0.0116 [+0.0080, +0.0152] | +0.0032 [-0.0007, +0.0067] | 0.838 | 0.482 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 182 | 0.493 | 0.374 | 0.0624 | +0.0085 [+0.0051, +0.0118] | +0.0010 [-0.0028, +0.0044] | 0.791 | 0.427 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

## risk_logistic (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.552] | 0.192 | 2.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.043 (105 of 1873 days never flag) | 109 | 0.329 | 0.422 | 0.0606 | +0.0108 [+0.0056, +0.0158] | -0.0043 [-0.0128, +0.0035] | 0.642 | 0.292 | no |
| 2 | 0.0176 (147 of 1872 days never flag) | 72 | 0.201 | 0.389 | 0.0676 | +0.0035 [-0.0030, +0.0092] | -0.0065 [-0.0146, +0.0005] | 0.579 | 0.176 | no |
| 3 | 0.0841 (147 of 1871 days never flag) | 76 | 0.210 | 0.382 | 0.0689 | +0.0018 [-0.0055, +0.0085] | -0.0045 [-0.0134, +0.0031] | 0.579 | 0.183 | no |
| 4 | 0.0243 (147 of 1870 days never flag) | 89 | 0.225 | 0.348 | 0.0688 | +0.0020 [-0.0047, +0.0081] | -0.0065 [-0.0150, +0.0012] | 0.578 | 0.191 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 86 | 0.217 | 0.349 | 0.0690 | +0.0019 [-0.0052, +0.0083] | -0.0056 [-0.0140, +0.0017] | 0.577 | 0.185 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.480, 0.826] | 0.269 | 5.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 4.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 238 | 0.707 | 0.416 | 0.0507 | +0.0207 [+0.0134, +0.0281] | +0.0056 [-0.0002, +0.0112] | 0.879 | 0.627 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 221 | 0.676 | 0.425 | 0.0590 | +0.0120 [+0.0064, +0.0180] | +0.0020 [-0.0025, +0.0065] | 0.841 | 0.603 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 202 | 0.601 | 0.411 | 0.0628 | +0.0079 [+0.0015, +0.0142] | +0.0016 [-0.0047, +0.0073] | 0.812 | 0.533 | no |
| 4 | 0.255 (147 of 1870 days never flag) | 180 | 0.507 | 0.389 | 0.0614 | +0.0094 [+0.0034, +0.0152] | +0.0010 [-0.0046, +0.0065] | 0.819 | 0.444 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 212 | 0.601 | 0.392 | 0.0623 | +0.0086 [+0.0037, +0.0137] | +0.0011 [-0.0032, +0.0053] | 0.796 | 0.527 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.520, 0.857] | 0.250 | 4.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.353, 0.714] | 0.250 | 4.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.105 (105 of 1873 days never flag) | 176 | 0.571 | 0.455 | 0.0525 | +0.0189 [+0.0122, +0.0264] | +0.0038 [-0.0018, +0.0096] | 0.801 | 0.516 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 177 | 0.547 | 0.429 | 0.0613 | +0.0098 [+0.0039, +0.0157] | -0.0002 [-0.0051, +0.0047] | 0.752 | 0.488 | no |
| 3 | 0.128 (147 of 1871 days never flag) | 159 | 0.500 | 0.434 | 0.0628 | +0.0079 [+0.0011, +0.0144] | +0.0015 [-0.0048, +0.0076] | 0.746 | 0.448 | no |
| 4 | 0.107 (147 of 1870 days never flag) | 159 | 0.435 | 0.377 | 0.0623 | +0.0086 [+0.0029, +0.0143] | +0.0001 [-0.0053, +0.0056] | 0.758 | 0.378 | no |
| 5 | 0.103 (147 of 1869 days never flag) | 187 | 0.522 | 0.385 | 0.0630 | +0.0079 [+0.0025, +0.0134] | +0.0004 [-0.0044, +0.0050] | 0.743 | 0.455 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.481, 0.818] | 0.269 | 5.19 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.677] | 0.269 | 5.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 220 | 0.664 | 0.423 | 0.0508 | +0.0206 [+0.0139, +0.0274] | +0.0055 [+0.0005, +0.0110] | 0.877 | 0.591 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 202 | 0.626 | 0.431 | 0.0580 | +0.0130 [+0.0083, +0.0182] | +0.0030 [-0.0016, +0.0079] | 0.830 | 0.560 | no |
| 3 | 0.248 (147 of 1871 days never flag) | 188 | 0.572 | 0.420 | 0.0613 | +0.0094 [+0.0028, +0.0152] | +0.0031 [-0.0034, +0.0094] | 0.804 | 0.510 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 179 | 0.457 | 0.352 | 0.0602 | +0.0106 [+0.0059, +0.0156] | +0.0022 [-0.0029, +0.0077] | 0.812 | 0.390 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 214 | 0.572 | 0.369 | 0.0606 | +0.0103 [+0.0059, +0.0144] | +0.0028 [-0.0016, +0.0070] | 0.790 | 0.494 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.818] | 0.269 | 5.31 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 4.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 237 | 0.707 | 0.418 | 0.0500 | +0.0214 [+0.0139, +0.0293] | +0.0063 [+0.0008, +0.0121] | 0.904 | 0.628 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 219 | 0.676 | 0.429 | 0.0583 | +0.0128 [+0.0072, +0.0183] | +0.0028 [-0.0016, +0.0077] | 0.878 | 0.604 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 198 | 0.601 | 0.419 | 0.0611 | +0.0096 [+0.0034, +0.0160] | +0.0033 [-0.0030, +0.0092] | 0.861 | 0.535 | no |
| 4 | 0.255 (147 of 1870 days never flag) | 177 | 0.514 | 0.401 | 0.0601 | +0.0107 [+0.0050, +0.0165] | +0.0023 [-0.0033, +0.0075] | 0.862 | 0.453 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 209 | 0.601 | 0.397 | 0.0613 | +0.0096 [+0.0047, +0.0144] | +0.0021 [-0.0022, +0.0063] | 0.850 | 0.529 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.522, 0.852] | 0.269 | 5.19 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.368, 0.714] | 0.269 | 5.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 213 | 0.636 | 0.418 | 0.0513 | +0.0202 [+0.0150, +0.0256] | +0.0051 [-0.0003, +0.0104] | 0.891 | 0.564 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 231 | 0.698 | 0.420 | 0.0593 | +0.0118 [+0.0075, +0.0162] | +0.0018 [-0.0030, +0.0066] | 0.845 | 0.621 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 188 | 0.565 | 0.415 | 0.0620 | +0.0087 [+0.0031, +0.0142] | +0.0024 [-0.0036, +0.0081] | 0.815 | 0.502 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 186 | 0.529 | 0.392 | 0.0612 | +0.0096 [+0.0053, +0.0138] | +0.0012 [-0.0039, +0.0063] | 0.827 | 0.464 | no |
| 5 | 0.123 (147 of 1869 days never flag) | 219 | 0.609 | 0.384 | 0.0617 | +0.0092 [+0.0049, +0.0131] | +0.0017 [-0.0034, +0.0061] | 0.808 | 0.531 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.192 | 2.31 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.192 | 1.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.068 (105 of 1873 days never flag) | 106 | 0.329 | 0.434 | 0.0596 | +0.0118 [+0.0070, +0.0164] | -0.0033 [-0.0115, +0.0041] | 0.643 | 0.294 | no |
| 2 | 0.33 (147 of 1872 days never flag) | 73 | 0.209 | 0.397 | 0.0672 | +0.0039 [-0.0026, +0.0099] | -0.0061 [-0.0146, +0.0009] | 0.579 | 0.183 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 68 | 0.196 | 0.397 | 0.0689 | +0.0018 [-0.0060, +0.0080] | -0.0045 [-0.0131, +0.0025] | 0.579 | 0.172 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 64 | 0.196 | 0.422 | 0.0689 | +0.0019 [-0.0048, +0.0080] | -0.0065 [-0.0146, +0.0010] | 0.578 | 0.174 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 80 | 0.210 | 0.362 | 0.0687 | +0.0023 [-0.0045, +0.0084] | -0.0053 [-0.0131, +0.0019] | 0.577 | 0.181 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.679] | 0.269 | 5.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.324, 0.667] | 0.269 | 5.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 209 | 0.643 | 0.431 | 0.0497 | +0.0217 [+0.0143, +0.0296] | +0.0066 [+0.0019, +0.0120] | 0.887 | 0.574 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 218 | 0.669 | 0.427 | 0.0586 | +0.0124 [+0.0073, +0.0182] | +0.0024 [-0.0014, +0.0071] | 0.842 | 0.597 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 202 | 0.594 | 0.406 | 0.0628 | +0.0079 [+0.0018, +0.0140] | +0.0016 [-0.0043, +0.0073] | 0.812 | 0.525 | no |
| 4 | 0.255 (147 of 1870 days never flag) | 178 | 0.500 | 0.388 | 0.0615 | +0.0094 [+0.0035, +0.0157] | +0.0009 [-0.0047, +0.0068] | 0.820 | 0.437 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 213 | 0.594 | 0.385 | 0.0620 | +0.0089 [+0.0039, +0.0138] | +0.0014 [-0.0028, +0.0057] | 0.797 | 0.519 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.815] | 0.231 | 4.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.667] | 0.231 | 4.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (105 of 1873 days never flag) | 193 | 0.621 | 0.451 | 0.0516 | +0.0199 [+0.0132, +0.0270] | +0.0048 [+0.0004, +0.0093] | 0.804 | 0.560 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 177 | 0.554 | 0.435 | 0.0609 | +0.0102 [+0.0048, +0.0160] | +0.0002 [-0.0045, +0.0051] | 0.752 | 0.496 | no |
| 3 | 0.128 (147 of 1871 days never flag) | 164 | 0.507 | 0.427 | 0.0628 | +0.0079 [+0.0013, +0.0142] | +0.0015 [-0.0045, +0.0075] | 0.748 | 0.453 | no |
| 4 | 0.163 (147 of 1870 days never flag) | 157 | 0.449 | 0.395 | 0.0623 | +0.0085 [+0.0026, +0.0144] | +0.0000 [-0.0054, +0.0056] | 0.758 | 0.394 | no |
| 5 | 0.172 (147 of 1869 days never flag) | 180 | 0.529 | 0.406 | 0.0627 | +0.0083 [+0.0027, +0.0136] | +0.0007 [-0.0038, +0.0055] | 0.744 | 0.467 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.719] | 0.269 | 5.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.654] | 0.269 | 5.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (126 of 1873 days never flag) | 201 | 0.600 | 0.418 | 0.0498 | +0.0216 [+0.0154, +0.0284] | +0.0065 [+0.0021, +0.0115] | 0.882 | 0.532 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 199 | 0.619 | 0.432 | 0.0576 | +0.0135 [+0.0090, +0.0183] | +0.0035 [-0.0006, +0.0080] | 0.831 | 0.554 | no |
| 3 | 0.248 (147 of 1871 days never flag) | 188 | 0.572 | 0.420 | 0.0610 | +0.0097 [+0.0043, +0.0155] | +0.0033 [-0.0023, +0.0097] | 0.807 | 0.510 | no |
| 4 | 0.243 (147 of 1870 days never flag) | 187 | 0.500 | 0.369 | 0.0599 | +0.0110 [+0.0060, +0.0161] | +0.0025 [-0.0027, +0.0078] | 0.816 | 0.432 | no |
| 5 | 0.242 (147 of 1869 days never flag) | 211 | 0.565 | 0.370 | 0.0602 | +0.0108 [+0.0065, +0.0149] | +0.0032 [-0.0011, +0.0074] | 0.796 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.667] | 0.269 | 4.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.677] | 0.269 | 4.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 208 | 0.643 | 0.433 | 0.0491 | +0.0224 [+0.0155, +0.0301] | +0.0073 [+0.0025, +0.0125] | 0.908 | 0.575 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 216 | 0.669 | 0.431 | 0.0579 | +0.0132 [+0.0082, +0.0186] | +0.0032 [-0.0008, +0.0077] | 0.879 | 0.598 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 198 | 0.594 | 0.414 | 0.0611 | +0.0096 [+0.0038, +0.0156] | +0.0033 [-0.0025, +0.0092] | 0.863 | 0.527 | no |
| 4 | 0.255 (147 of 1870 days never flag) | 177 | 0.514 | 0.401 | 0.0602 | +0.0107 [+0.0050, +0.0165] | +0.0022 [-0.0032, +0.0076] | 0.864 | 0.453 | no |
| 5 | 0.245 (147 of 1869 days never flag) | 210 | 0.594 | 0.390 | 0.0610 | +0.0099 [+0.0049, +0.0148] | +0.0024 [-0.0018, +0.0070] | 0.851 | 0.520 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.480, 0.821] | 0.269 | 5.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.688] | 0.269 | 5.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (126 of 1873 days never flag) | 226 | 0.671 | 0.416 | 0.0503 | +0.0211 [+0.0165, +0.0264] | +0.0061 [+0.0015, +0.0106] | 0.899 | 0.595 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 228 | 0.698 | 0.425 | 0.0589 | +0.0122 [+0.0081, +0.0165] | +0.0022 [-0.0024, +0.0066] | 0.846 | 0.622 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 202 | 0.601 | 0.411 | 0.0620 | +0.0087 [+0.0035, +0.0137] | +0.0024 [-0.0036, +0.0081] | 0.815 | 0.533 | no |
| 4 | 0.127 (147 of 1870 days never flag) | 187 | 0.529 | 0.390 | 0.0613 | +0.0095 [+0.0048, +0.0141] | +0.0011 [-0.0047, +0.0065] | 0.826 | 0.463 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 213 | 0.601 | 0.390 | 0.0614 | +0.0095 [+0.0054, +0.0135] | +0.0020 [-0.0027, +0.0062] | 0.806 | 0.526 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.231 | 3.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 3.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.148 (42 of 1873 days never flag) | 116 | 0.329 | 0.397 | 0.0632 | +0.0082 [+0.0025, +0.0141] | -0.0069 [-0.0152, +0.0007] | 0.645 | 0.288 | no |
| 2 | 0.283 (126 of 1872 days never flag) | 94 | 0.216 | 0.319 | 0.0676 | +0.0034 [-0.0039, +0.0105] | -0.0066 [-0.0149, +0.0014] | 0.578 | 0.179 | no |
| 3 | 0.092 (126 of 1871 days never flag) | 90 | 0.196 | 0.300 | 0.0669 | +0.0038 [-0.0032, +0.0106] | -0.0025 [-0.0103, +0.0048] | 0.581 | 0.159 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 118 | 0.210 | 0.246 | 0.0672 | +0.0037 [-0.0026, +0.0097] | -0.0048 [-0.0124, +0.0018] | 0.580 | 0.159 | no |
| 5 | 0.0988 (126 of 1869 days never flag) | 92 | 0.196 | 0.293 | 0.0669 | +0.0040 [-0.0026, +0.0101] | -0.0035 [-0.0110, +0.0034] | 0.581 | 0.158 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 3.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 8.3 over 1035 days; regime_2021-23: 12.1 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 4.1 over 1035 days; regime_2021-23: 5.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.192 | 2.31 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.542] | 0.154 | 1.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.154 (105 of 1873 days never flag) | 107 | 0.336 | 0.439 | 0.0630 | +0.0084 [+0.0021, +0.0147] | -0.0067 [-0.0153, +0.0016] | 0.635 | 0.301 | no |
| 2 | 0.11 (147 of 1872 days never flag) | 82 | 0.216 | 0.366 | 0.0687 | +0.0024 [-0.0054, +0.0093] | -0.0076 [-0.0168, -0.0001] | 0.582 | 0.186 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 69 | 0.217 | 0.435 | 0.0670 | +0.0037 [-0.0037, +0.0105] | -0.0026 [-0.0108, +0.0047] | 0.585 | 0.195 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0669 | +0.0039 [-0.0034, +0.0110] | -0.0045 [-0.0128, +0.0033] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 53 | 0.188 | 0.491 | 0.0670 | +0.0039 [-0.0030, +0.0107] | -0.0036 [-0.0120, +0.0040] | 0.585 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.792] | 0.269 | 5.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.368, 0.714] | 0.269 | 5.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 218 | 0.657 | 0.422 | 0.0531 | +0.0183 [+0.0099, +0.0272] | +0.0032 [-0.0028, +0.0091] | 0.880 | 0.584 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 206 | 0.683 | 0.461 | 0.0601 | +0.0109 [+0.0048, +0.0174] | +0.0009 [-0.0038, +0.0057] | 0.846 | 0.619 | no |
| 3 | 0.25 (126 of 1871 days never flag) | 239 | 0.674 | 0.389 | 0.0609 | +0.0098 [+0.0042, +0.0160] | +0.0035 [-0.0017, +0.0089] | 0.839 | 0.590 | no |
| 4 | 0.255 (126 of 1870 days never flag) | 197 | 0.565 | 0.396 | 0.0594 | +0.0114 [+0.0051, +0.0183] | +0.0029 [-0.0025, +0.0088] | 0.849 | 0.497 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 224 | 0.638 | 0.393 | 0.0604 | +0.0106 [+0.0045, +0.0168] | +0.0030 [-0.0021, +0.0089] | 0.840 | 0.559 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.824] | 0.231 | 4.15 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.231 | 4.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 186 | 0.607 | 0.457 | 0.0549 | +0.0165 [+0.0089, +0.0248] | +0.0014 [-0.0045, +0.0074] | 0.793 | 0.549 | no |
| 2 | 0.431 (147 of 1872 days never flag) | 167 | 0.540 | 0.449 | 0.0624 | +0.0087 [+0.0021, +0.0154] | -0.0013 [-0.0065, +0.0039] | 0.753 | 0.486 | no |
| 3 | 0.169 (126 of 1871 days never flag) | 165 | 0.507 | 0.424 | 0.0609 | +0.0098 [+0.0034, +0.0159] | +0.0035 [-0.0022, +0.0089] | 0.755 | 0.452 | no |
| 4 | 0.194 (126 of 1870 days never flag) | 166 | 0.478 | 0.398 | 0.0603 | +0.0105 [+0.0042, +0.0168] | +0.0021 [-0.0032, +0.0074] | 0.767 | 0.421 | no |
| 5 | 0.218 (126 of 1869 days never flag) | 183 | 0.543 | 0.410 | 0.0610 | +0.0099 [+0.0038, +0.0166] | +0.0024 [-0.0032, +0.0079] | 0.754 | 0.481 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.682] | 0.269 | 5.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 213 | 0.621 | 0.408 | 0.0534 | +0.0180 [+0.0110, +0.0257] | +0.0030 [-0.0026, +0.0089] | 0.865 | 0.549 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 204 | 0.640 | 0.436 | 0.0592 | +0.0119 [+0.0064, +0.0181] | +0.0019 [-0.0028, +0.0068] | 0.825 | 0.574 | no |
| 3 | 0.248 (126 of 1871 days never flag) | 213 | 0.594 | 0.385 | 0.0592 | +0.0115 [+0.0060, +0.0179] | +0.0052 [-0.0003, +0.0113] | 0.832 | 0.519 | no |
| 4 | 0.243 (126 of 1870 days never flag) | 197 | 0.529 | 0.371 | 0.0576 | +0.0132 [+0.0076, +0.0196] | +0.0048 [-0.0004, +0.0107] | 0.844 | 0.457 | no |
| 5 | 0.242 (126 of 1869 days never flag) | 223 | 0.609 | 0.377 | 0.0583 | +0.0126 [+0.0069, +0.0186] | +0.0051 [-0.0005, +0.0109] | 0.842 | 0.528 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.781] | 0.269 | 5.46 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.704] | 0.269 | 5.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 217 | 0.657 | 0.424 | 0.0524 | +0.0190 [+0.0108, +0.0279] | +0.0039 [-0.0019, +0.0101] | 0.899 | 0.585 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 204 | 0.683 | 0.466 | 0.0594 | +0.0117 [+0.0057, +0.0184] | +0.0017 [-0.0028, +0.0066] | 0.877 | 0.621 | no |
| 3 | 0.25 (126 of 1871 days never flag) | 235 | 0.674 | 0.396 | 0.0591 | +0.0115 [+0.0057, +0.0176] | +0.0052 [+0.0001, +0.0107] | 0.873 | 0.592 | no |
| 4 | 0.255 (126 of 1870 days never flag) | 194 | 0.565 | 0.402 | 0.0582 | +0.0127 [+0.0061, +0.0193] | +0.0042 [-0.0015, +0.0097] | 0.878 | 0.498 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 222 | 0.638 | 0.396 | 0.0593 | +0.0116 [+0.0056, +0.0179] | +0.0041 [-0.0015, +0.0100] | 0.871 | 0.560 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 19 | 0.731 [0.560, 0.882] | 0.282 | 6.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.741] | 0.282 | 6.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 237 | 0.671 | 0.397 | 0.0536 | +0.0178 [+0.0117, +0.0241] | +0.0027 [-0.0032, +0.0089] | 0.879 | 0.589 | no |
| 2 | 0.138 (147 of 1872 days never flag) | 234 | 0.691 | 0.410 | 0.0604 | +0.0107 [+0.0051, +0.0160] | +0.0007 [-0.0047, +0.0057] | 0.847 | 0.611 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 251 | 0.681 | 0.375 | 0.0601 | +0.0106 [+0.0055, +0.0159] | +0.0043 [-0.0012, +0.0098] | 0.840 | 0.591 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 205 | 0.565 | 0.380 | 0.0593 | +0.0116 [+0.0062, +0.0172] | +0.0031 [-0.0024, +0.0086] | 0.845 | 0.492 | no |
| 5 | 0.167 (126 of 1869 days never flag) | 228 | 0.638 | 0.386 | 0.0598 | +0.0112 [+0.0057, +0.0168] | +0.0036 [-0.0021, +0.0094] | 0.839 | 0.557 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

