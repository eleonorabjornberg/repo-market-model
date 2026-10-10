# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `5897a0c95499…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## risk_gbm+early_prior (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.677] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.132, 0.419] | 0.154 | 1.58 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0777 (105 of 1873 days never flag) | 89 | 0.300 | 0.472 | 0.0579 | +0.0135 [+0.0077, +0.0190] | -0.0016 [-0.0102, +0.0061] | 0.642 | 0.273 | no |
| 2 | 0.0167 (147 of 1872 days never flag) | 68 | 0.201 | 0.412 | 0.0688 | +0.0023 [-0.0045, +0.0080] | -0.0077 [-0.0166, -0.0005] | 0.578 | 0.178 | no |
| 3 | 0.0193 (147 of 1871 days never flag) | 68 | 0.196 | 0.397 | 0.0668 | +0.0039 [-0.0026, +0.0098] | -0.0024 [-0.0099, +0.0043] | 0.579 | 0.172 | no |
| 4 | 0.0227 (147 of 1870 days never flag) | 66 | 0.188 | 0.394 | 0.0669 | +0.0039 [-0.0031, +0.0099] | -0.0046 [-0.0124, +0.0022] | 0.579 | 0.165 | no |
| 5 | 0.102 (147 of 1869 days never flag) | 61 | 0.159 | 0.361 | 0.0697 | +0.0012 [-0.0053, +0.0072] | -0.0063 [-0.0139, +0.0006] | 0.577 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.487 (climatology 0.457, difference +0.0297 [-0.1129, +0.1585]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1048, ΔBrier vs climatology +0.0247 [+0.0157, +0.0333], realised minus predicted +0.0925 [+0.0576, +0.1310]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.0960 | 0.2720 | +0.0007 [-0.0218, +0.0223] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0148 | 0.0159 | +0.0396 [+0.0309, +0.0485] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0028 | 0.0200 | +0.0037 [-0.0001, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0386 | 0.1165 | +0.0155 [-0.0022, +0.0394] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.143 | 0.0022 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0035 | 0.0031 | +0.0296 [+0.0221, +0.0365] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0264 | 0.4146 | -0.0093 [-0.0315, +0.0249] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.534 | 0.0972 | 0.2474 | +0.0149 [-0.0062, +0.0354] |
| day_type | month_end | 150 | 17 | 0.706 | 0.462 | 0.0994 | 0.1133 | +0.0548 [+0.0311, +0.0797] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.429 | 0.0127 | 0.0630 | +0.0048 [-0.0005, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.2360 | 0.2903 | +0.1201 [+0.0503, +0.1913] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.0885 | 0.1461 | +0.0632 [+0.0371, +0.0889] |

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

## risk_gbm+every_day+early_prior (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.478, 0.824] | 0.269 | 5.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.647] | 0.269 | 4.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 227 | 0.671 | 0.414 | 0.0480 | +0.0234 [+0.0160, +0.0313] | +0.0083 [+0.0035, +0.0137] | 0.883 | 0.595 | no |
| 2 | 0.257 (147 of 1872 days never flag) | 218 | 0.655 | 0.417 | 0.0603 | +0.0108 [+0.0065, +0.0151] | +0.0008 [-0.0024, +0.0041] | 0.826 | 0.581 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 198 | 0.572 | 0.399 | 0.0607 | +0.0100 [+0.0063, +0.0140] | +0.0037 [+0.0008, +0.0068] | 0.798 | 0.504 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 200 | 0.565 | 0.390 | 0.0595 | +0.0114 [+0.0069, +0.0158] | +0.0029 [+0.0003, +0.0057] | 0.813 | 0.495 | no |
| 5 | 0.245 (168 of 1869 days never flag) | 212 | 0.601 | 0.392 | 0.0630 | +0.0079 [+0.0034, +0.0123] | +0.0004 [-0.0027, +0.0033] | 0.780 | 0.527 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.467 (climatology 0.457, difference +0.0097 [-0.0902, +0.1022]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0842, ΔBrier vs climatology +0.0453 [+0.0321, +0.0588], realised minus predicted +0.0110 [-0.0188, +0.0429]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2374 | 0.2720 | +0.0564 [+0.0277, +0.0866] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1174 | 0.0159 | +0.0233 [+0.0095, +0.0350] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0192 | 0.0000 | +0.0131 [+0.0114, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0328 | 0.0200 | +0.0006 [-0.0057, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.500 | 0.1149 | 0.1165 | +0.0275 [+0.0003, +0.0601] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0230 | 0.0048 | +0.0075 [+0.0051, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0681 | 0.0031 | +0.0221 [+0.0144, +0.0289] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.2106 | 0.4146 | 0.0600 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.411 | 0.2435 | 0.2474 | +0.0558 [+0.0304, +0.0827] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1088 | 0.1133 | +0.0599 [+0.0345, +0.0867] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.370 | 0.0862 | 0.0630 | +0.0159 [+0.0089, +0.0241] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2360 | 0.2903 | +0.1201 [+0.0507, +0.1907] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.0885 | 0.1461 | +0.0632 [+0.0376, +0.0891] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3382 | 0.2213 |

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

## risk_gbm_base+early_prior (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.348, 0.727] | 0.192 | 1.77 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.160, 0.457] | 0.154 | 1.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0777 (105 of 1873 days never flag) | 89 | 0.307 | 0.483 | 0.0594 | +0.0121 [+0.0073, +0.0168] | -0.0030 [-0.0117, +0.0039] | 0.642 | 0.281 | no |
| 2 | 0.0167 (147 of 1872 days never flag) | 62 | 0.180 | 0.403 | 0.0692 | +0.0019 [-0.0046, +0.0079] | -0.0081 [-0.0162, -0.0006] | 0.578 | 0.159 | no |
| 3 | 0.101 (147 of 1871 days never flag) | 68 | 0.188 | 0.382 | 0.0679 | +0.0028 [-0.0042, +0.0086] | -0.0035 [-0.0111, +0.0031] | 0.579 | 0.164 | no |
| 4 | 0.102 (147 of 1870 days never flag) | 66 | 0.203 | 0.424 | 0.0669 | +0.0039 [-0.0024, +0.0099] | -0.0045 [-0.0118, +0.0022] | 0.579 | 0.181 | no |
| 5 | 0.102 (147 of 1869 days never flag) | 60 | 0.152 | 0.350 | 0.0697 | +0.0012 [-0.0051, +0.0069] | -0.0063 [-0.0141, +0.0004] | 0.576 | 0.130 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.502 (climatology 0.457, difference +0.0447 [-0.1170, +0.1769]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1060, ΔBrier vs climatology +0.0235 [+0.0150, +0.0322], realised minus predicted +0.0900 [+0.0531, +0.1275]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.574 | 0.0973 | 0.2720 | -0.0024 [-0.0215, +0.0150] |
| regime | 2020 | 251 | 4 | 0.250 | 0.048 | 0.0253 | 0.0159 | +0.0329 [+0.0222, +0.0431] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [+0.0001, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0354 | 0.1165 | +0.0158 [+0.0019, +0.0333] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0072 | 0.0031 | +0.0290 [+0.0225, +0.0352] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0342 | 0.4146 | -0.0021 [-0.0272, +0.0313] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.534 | 0.1008 | 0.2474 | +0.0074 [-0.0096, +0.0242] |
| day_type | month_end | 150 | 17 | 0.706 | 0.462 | 0.0992 | 0.1133 | +0.0343 [+0.0120, +0.0560] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.485 | 0.0129 | 0.0630 | +0.0052 [+0.0003, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2186 | 0.2903 | +0.1146 [+0.0447, +0.1844] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.450 | 0.1124 | 0.1461 | +0.0627 [+0.0421, +0.0855] |

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

## risk_gbm_base+every_day+early_prior (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.464, 0.821] | 0.269 | 5.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.281, 0.643] | 0.269 | 5.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.211 (105 of 1873 days never flag) | 229 | 0.686 | 0.419 | 0.0495 | +0.0220 [+0.0150, +0.0302] | +0.0069 [+0.0024, +0.0117] | 0.888 | 0.609 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 217 | 0.647 | 0.415 | 0.0607 | +0.0104 [+0.0063, +0.0146] | +0.0004 [-0.0027, +0.0035] | 0.816 | 0.574 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 194 | 0.558 | 0.397 | 0.0618 | +0.0089 [+0.0054, +0.0126] | +0.0026 [-0.0002, +0.0056] | 0.791 | 0.490 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 206 | 0.572 | 0.383 | 0.0594 | +0.0114 [+0.0070, +0.0160] | +0.0029 [-0.0002, +0.0063] | 0.824 | 0.499 | no |
| 5 | 0.245 (168 of 1869 days never flag) | 214 | 0.587 | 0.379 | 0.0631 | +0.0079 [+0.0036, +0.0122] | +0.0003 [-0.0027, +0.0035] | 0.772 | 0.510 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.475 (climatology 0.457, difference +0.0178 [-0.0810, +0.1297]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0859, ΔBrier vs climatology +0.0436 [+0.0301, +0.0582], realised minus predicted +0.0095 [-0.0204, +0.0416]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.425 | 0.2387 | 0.2720 | +0.0533 [+0.0266, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1280 | 0.0159 | +0.0166 [+0.0000, +0.0302] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0321 | 0.0200 | +0.0008 [-0.0057, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.1117 | 0.1165 | +0.0278 [+0.0028, +0.0588] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0217 | 0.0048 | +0.0082 [+0.0060, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0717 | 0.0031 | +0.0216 [+0.0151, +0.0277] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2184 | 0.4146 | 0.0673 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.416 | 0.2470 | 0.2474 | +0.0484 [+0.0234, +0.0761] |
| day_type | month_end | 150 | 17 | 0.824 | 0.560 | 0.1086 | 0.1133 | +0.0394 [+0.0156, +0.0640] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.374 | 0.0863 | 0.0630 | +0.0163 [+0.0095, +0.0244] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2186 | 0.2903 | +0.1146 [+0.0456, +0.1815] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1124 | 0.1461 | +0.0627 [+0.0416, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3463 | 0.2213 |

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

## risk_logistic+early_prior (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.792] | 0.192 | 2.00 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.235, 0.552] | 0.192 | 1.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.043 (105 of 1873 days never flag) | 97 | 0.321 | 0.464 | 0.0604 | +0.0110 [+0.0056, +0.0159] | -0.0041 [-0.0124, +0.0038] | 0.643 | 0.291 | no |
| 2 | 0.1 (147 of 1872 days never flag) | 69 | 0.209 | 0.420 | 0.0677 | +0.0034 [-0.0032, +0.0092] | -0.0067 [-0.0147, +0.0005] | 0.579 | 0.186 | no |
| 3 | 0.0193 (147 of 1871 days never flag) | 77 | 0.217 | 0.390 | 0.0680 | +0.0027 [-0.0046, +0.0090] | -0.0036 [-0.0116, +0.0033] | 0.580 | 0.190 | no |
| 4 | 0.0243 (147 of 1870 days never flag) | 81 | 0.225 | 0.383 | 0.0693 | +0.0015 [-0.0050, +0.0079] | -0.0069 [-0.0148, +0.0003] | 0.579 | 0.196 | no |
| 5 | 0.0227 (147 of 1869 days never flag) | 75 | 0.217 | 0.400 | 0.0699 | +0.0011 [-0.0059, +0.0070] | -0.0065 [-0.0142, +0.0003] | 0.579 | 0.191 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.539 (climatology 0.457, difference +0.0823 [-0.0677, +0.2145]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1084, ΔBrier vs climatology +0.0211 [+0.0114, +0.0304], realised minus predicted +0.0841 [+0.0487, +0.1261]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.1086 | 0.2720 | -0.0017 [-0.0230, +0.0182] |
| regime | 2020 | 251 | 4 | 0.250 | 0.053 | 0.0308 | 0.0159 | +0.0252 [+0.0100, +0.0380] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0059 | 0.0200 | +0.0050 [+0.0009, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0332 | 0.1165 | +0.0133 [+0.0012, +0.0289] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.111 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0069 | 0.0031 | +0.0280 [+0.0219, +0.0337] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0390 | 0.4146 | 0.0103 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1087 | 0.2474 | +0.0034 [-0.0162, +0.0220] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1049 | 0.1133 | +0.0303 [+0.0017, +0.0589] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.486 | 0.0129 | 0.0630 | +0.0041 [-0.0011, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3374 | 0.2903 | +0.0797 [+0.0002, +0.1584] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.474 | 0.1310 | 0.1461 | +0.0783 [+0.0473, +0.1160] |

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

## risk_logistic+every_day+early_prior (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.815] | 0.269 | 5.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.632] | 0.269 | 4.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.224 (105 of 1873 days never flag) | 231 | 0.679 | 0.411 | 0.0505 | +0.0209 [+0.0134, +0.0286] | +0.0058 [+0.0005, +0.0114] | 0.899 | 0.600 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 221 | 0.676 | 0.425 | 0.0592 | +0.0119 [+0.0069, +0.0174] | +0.0019 [-0.0018, +0.0054] | 0.847 | 0.603 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 202 | 0.601 | 0.411 | 0.0619 | +0.0088 [+0.0032, +0.0137] | +0.0025 [-0.0026, +0.0066] | 0.819 | 0.533 | no |
| 4 | 0.222 (147 of 1870 days never flag) | 203 | 0.558 | 0.379 | 0.0618 | +0.0090 [+0.0041, +0.0141] | +0.0006 [-0.0038, +0.0048] | 0.828 | 0.485 | no |
| 5 | 0.245 (168 of 1869 days never flag) | 211 | 0.594 | 0.389 | 0.0632 | +0.0077 [+0.0030, +0.0123] | +0.0002 [-0.0037, +0.0036] | 0.808 | 0.520 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.544 (climatology 0.457, difference +0.0873 [-0.0289, +0.2046]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0258, +0.0558], realised minus predicted +0.0047 [-0.0263, +0.0399]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.421 | 0.2500 | 0.2720 | +0.0540 [+0.0271, +0.0830] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.1335 | 0.0159 | +0.0089 [-0.0131, +0.0269] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0190 | 0.0000 | +0.0132 [+0.0114, +0.0150] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0359 | 0.0200 | +0.0019 [-0.0048, +0.0079] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.545 | 0.1095 | 0.1165 | +0.0252 [+0.0006, +0.0551] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0240 | 0.0048 | +0.0079 [+0.0056, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0715 | 0.0031 | +0.0206 [+0.0142, +0.0261] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2232 | 0.4146 | 0.0796 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.411 | 0.2550 | 0.2474 | +0.0443 [+0.0178, +0.0716] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1143 | 0.1133 | +0.0355 [+0.0066, +0.0646] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.370 | 0.0864 | 0.0630 | +0.0152 [+0.0082, +0.0230] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3374 | 0.2903 | +0.0797 [+0.0042, +0.1555] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1310 | 0.1461 | +0.0783 [+0.0477, +0.1137] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3400 | 0.2213 |

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

## risk_logistic_base+early_prior (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.192 | 1.96 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.166, 0.450] | 0.154 | 1.58 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0777 (105 of 1873 days never flag) | 97 | 0.329 | 0.474 | 0.0595 | +0.0119 [+0.0067, +0.0168] | -0.0032 [-0.0112, +0.0039] | 0.643 | 0.299 | no |
| 2 | 0.1 (147 of 1872 days never flag) | 70 | 0.209 | 0.414 | 0.0675 | +0.0036 [-0.0034, +0.0095] | -0.0064 [-0.0148, +0.0007] | 0.579 | 0.185 | no |
| 3 | 0.101 (147 of 1871 days never flag) | 70 | 0.210 | 0.414 | 0.0686 | +0.0021 [-0.0048, +0.0083] | -0.0042 [-0.0121, +0.0028] | 0.580 | 0.186 | no |
| 4 | 0.102 (147 of 1870 days never flag) | 69 | 0.203 | 0.406 | 0.0694 | +0.0015 [-0.0052, +0.0079] | -0.0070 [-0.0147, +0.0004] | 0.579 | 0.179 | no |
| 5 | 0.102 (147 of 1869 days never flag) | 69 | 0.203 | 0.406 | 0.0692 | +0.0018 [-0.0046, +0.0077] | -0.0058 [-0.0137, +0.0011] | 0.579 | 0.179 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.551 (climatology 0.457, difference +0.0942 [-0.0472, +0.2232]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1061, ΔBrier vs climatology +0.0234 [+0.0140, +0.0327], realised minus predicted +0.0855 [+0.0504, +0.1201]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.564 | 0.1090 | 0.2720 | -0.0018 [-0.0227, +0.0172] |
| regime | 2020 | 251 | 4 | 0.250 | 0.042 | 0.0294 | 0.0159 | +0.0298 [+0.0208, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0001, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.765 | 0.0311 | 0.1165 | +0.0168 [+0.0034, +0.0327] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0092 | 0.0031 | +0.0279 [+0.0222, +0.0337] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0424 | 0.4146 | 0.0154 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.533 | 0.1071 | 0.2474 | +0.0062 [-0.0124, +0.0234] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1024 | 0.1133 | +0.0380 [+0.0104, +0.0649] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.486 | 0.0127 | 0.0630 | +0.0046 [-0.0005, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.2959 | 0.2903 | +0.0905 [+0.0284, +0.1527] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.450 | 0.1346 | 0.1461 | +0.0720 [+0.0401, +0.1081] |

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

## risk_logistic_base+every_day+early_prior (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.778] | 0.269 | 5.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.680] | 0.269 | 5.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.224 (105 of 1873 days never flag) | 232 | 0.686 | 0.414 | 0.0496 | +0.0218 [+0.0144, +0.0302] | +0.0067 [+0.0020, +0.0122] | 0.900 | 0.607 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 218 | 0.669 | 0.427 | 0.0590 | +0.0121 [+0.0076, +0.0170] | +0.0021 [-0.0009, +0.0051] | 0.847 | 0.597 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 202 | 0.594 | 0.406 | 0.0625 | +0.0082 [+0.0032, +0.0134] | +0.0019 [-0.0029, +0.0060] | 0.817 | 0.525 | no |
| 4 | 0.255 (147 of 1870 days never flag) | 208 | 0.580 | 0.385 | 0.0619 | +0.0089 [+0.0039, +0.0142] | +0.0005 [-0.0043, +0.0048] | 0.829 | 0.506 | no |
| 5 | 0.245 (168 of 1869 days never flag) | 215 | 0.609 | 0.391 | 0.0625 | +0.0084 [+0.0039, +0.0129] | +0.0009 [-0.0028, +0.0044] | 0.811 | 0.533 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.554 (climatology 0.457, difference +0.0973 [-0.0158, +0.2093]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0877, ΔBrier vs climatology +0.0418 [+0.0268, +0.0572], realised minus predicted +0.0063 [-0.0244, +0.0393]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.420 | 0.2504 | 0.2720 | +0.0539 [+0.0264, +0.0832] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.1320 | 0.0159 | +0.0135 [-0.0018, +0.0262] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0188 | 0.0000 | +0.0132 [+0.0116, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0327 | 0.0200 | +0.0009 [-0.0056, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.1073 | 0.1165 | +0.0288 [+0.0045, +0.0609] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0222 | 0.0048 | +0.0082 [+0.0062, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0738 | 0.0031 | +0.0205 [+0.0140, +0.0265] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2266 | 0.4146 | +0.0847 [-0.0032, +0.1804] |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.411 | 0.2534 | 0.2474 | +0.0471 [+0.0218, +0.0745] |
| day_type | month_end | 150 | 17 | 0.882 | 0.600 | 0.1117 | 0.1133 | +0.0432 [+0.0169, +0.0711] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.367 | 0.0862 | 0.0630 | +0.0157 [+0.0087, +0.0236] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.2959 | 0.2903 | +0.0905 [+0.0248, +0.1538] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1346 | 0.1461 | +0.0720 [+0.0395, +0.1098] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3420 | 0.2213 |

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

## risk_quantile_skewt_base+early_prior (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.192 | 2.12 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.192 | 1.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.154 (105 of 1873 days never flag) | 101 | 0.329 | 0.455 | 0.0607 | +0.0107 [+0.0050, +0.0161] | -0.0044 [-0.0126, +0.0028] | 0.647 | 0.297 | no |
| 2 | 0.1 (147 of 1872 days never flag) | 76 | 0.216 | 0.395 | 0.0671 | +0.0039 [-0.0031, +0.0101] | -0.0061 [-0.0146, +0.0012] | 0.583 | 0.189 | no |
| 3 | 0.101 (147 of 1871 days never flag) | 80 | 0.217 | 0.375 | 0.0681 | +0.0025 [-0.0052, +0.0091] | -0.0038 [-0.0118, +0.0032] | 0.582 | 0.189 | no |
| 4 | 0.102 (147 of 1870 days never flag) | 77 | 0.210 | 0.377 | 0.0679 | +0.0029 [-0.0043, +0.0091] | -0.0056 [-0.0135, +0.0011] | 0.585 | 0.182 | no |
| 5 | 0.102 (147 of 1869 days never flag) | 76 | 0.210 | 0.382 | 0.0684 | +0.0025 [-0.0047, +0.0086] | -0.0050 [-0.0131, +0.0015] | 0.582 | 0.183 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.554 (climatology 0.457, difference +0.0967 [-0.0418, +0.2254]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1045, ΔBrier vs climatology +0.0249 [+0.0157, +0.0349], realised minus predicted +0.0704 [+0.0378, +0.1076]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.625 | 0.1055 | 0.2720 | -0.0054 [-0.0274, +0.0151] |
| regime | 2020 | 251 | 4 | 0.250 | 0.033 | 0.0469 | 0.0159 | +0.0220 [+0.0122, +0.0312] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0047, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0509 | 0.1165 | +0.0242 [+0.0057, +0.0470] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0059 | 0.0048 | +0.0086 [+0.0066, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.040 | 0.0271 | 0.0031 | +0.0196 [+0.0114, +0.0258] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.0989 | 0.4146 | 0.0595 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.591 | 0.1062 | 0.2474 | +0.0050 [-0.0154, +0.0233] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1307 | 0.1133 | +0.0328 [+0.0014, +0.0661] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.472 | 0.0138 | 0.0630 | +0.0043 [-0.0015, +0.0089] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3172 | 0.2903 | +0.1212 [+0.0542, +0.1906] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.385 | 0.1981 | 0.1461 | +0.0503 [+0.0144, +0.0911] |

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

## risk_quantile_skewt_base+every_day+early_prior (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.469, 0.821] | 0.269 | 5.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 5.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 235 | 0.671 | 0.400 | 0.0508 | +0.0206 [+0.0130, +0.0288] | +0.0055 [+0.0006, +0.0108] | 0.898 | 0.590 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 223 | 0.691 | 0.430 | 0.0586 | +0.0125 [+0.0075, +0.0180] | +0.0025 [-0.0009, +0.0058] | 0.847 | 0.617 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 208 | 0.609 | 0.404 | 0.0620 | +0.0086 [+0.0036, +0.0141] | +0.0023 [-0.0017, +0.0069] | 0.817 | 0.537 | no |
| 4 | 0.255 (147 of 1870 days never flag) | 214 | 0.601 | 0.388 | 0.0605 | +0.0103 [+0.0047, +0.0162] | +0.0019 [-0.0023, +0.0062] | 0.835 | 0.526 | no |
| 5 | 0.245 (168 of 1869 days never flag) | 221 | 0.630 | 0.394 | 0.0618 | +0.0092 [+0.0043, +0.0145] | +0.0016 [-0.0019, +0.0055] | 0.820 | 0.553 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.457, difference +0.1155 [-0.0047, +0.2509]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0864, ΔBrier vs climatology +0.0431 [+0.0284, +0.0590], realised minus predicted -0.0036 [-0.0337, +0.0280]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.425 | 0.2469 | 0.2720 | +0.0503 [+0.0259, +0.0781] |
| regime | 2020 | 251 | 4 | 0.250 | 0.038 | 0.1496 | 0.0159 | +0.0057 [-0.0088, +0.0186] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0215 | 0.0000 | +0.0130 [+0.0113, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0419 | 0.0200 | -0.0015 [-0.0082, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.1272 | 0.1165 | +0.0361 [+0.0040, +0.0767] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0266 | 0.0048 | +0.0074 [+0.0050, +0.0095] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0917 | 0.0031 | +0.0122 [+0.0043, +0.0192] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2832 | 0.4146 | +0.1288 [+0.0085, +0.2561] |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.414 | 0.2525 | 0.2474 | +0.0459 [+0.0226, +0.0711] |
| day_type | month_end | 150 | 17 | 0.824 | 0.519 | 0.1401 | 0.1133 | +0.0379 [+0.0057, +0.0743] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.363 | 0.0872 | 0.0630 | +0.0154 [+0.0088, +0.0229] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3172 | 0.2903 | +0.1212 [+0.0555, +0.1889] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.474 | 0.1981 | 0.1461 | +0.0503 [+0.0153, +0.0919] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3379 | 0.2213 |

