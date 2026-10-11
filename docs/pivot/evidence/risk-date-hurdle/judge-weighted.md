# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `3121c6e2cf7e…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## risk_gbm+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.437, 0.808] | 0.269 | 4.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.643] | 0.250 | 4.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 190 | 0.600 | 0.442 | 0.0606 | +0.0108 [+0.0009, +0.0206] | -0.0043 [-0.0126, +0.0039] | 0.871 | 0.539 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 210 | 0.590 | 0.390 | 0.0716 | -0.0006 [-0.0090, +0.0075] | -0.0106 [-0.0183, -0.0034] | 0.816 | 0.516 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 188 | 0.529 | 0.388 | 0.0726 | -0.0019 [-0.0112, +0.0059] | -0.0082 [-0.0171, -0.0007] | 0.795 | 0.463 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 160 | 0.457 | 0.394 | 0.0702 | +0.0006 [-0.0067, +0.0070] | -0.0078 [-0.0144, -0.0020] | 0.815 | 0.401 | no |
| 5 | 0.446 (147 of 1869 days never flag) | 161 | 0.442 | 0.379 | 0.0728 | -0.0019 [-0.0083, +0.0039] | -0.0094 [-0.0153, -0.0041] | 0.776 | 0.384 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.760] | 0.269 | 5.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.242 | 4.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 196 | 0.614 | 0.439 | 0.0561 | +0.0153 [+0.0079, +0.0235] | +0.0002 [-0.0061, +0.0067] | 0.845 | 0.551 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 212 | 0.583 | 0.382 | 0.0698 | +0.0013 [-0.0044, +0.0070] | -0.0087 [-0.0146, -0.0031] | 0.771 | 0.507 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 187 | 0.536 | 0.396 | 0.0699 | +0.0008 [-0.0040, +0.0054] | -0.0055 [-0.0105, -0.0008] | 0.725 | 0.471 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 168 | 0.471 | 0.387 | 0.0692 | +0.0017 [-0.0031, +0.0063] | -0.0068 [-0.0113, -0.0025] | 0.754 | 0.412 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 166 | 0.442 | 0.367 | 0.0728 | -0.0019 [-0.0071, +0.0030] | -0.0094 [-0.0149, -0.0042] | 0.717 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.424, 0.800] | 0.269 | 4.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.643] | 0.262 | 4.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 203 | 0.607 | 0.419 | 0.0601 | +0.0113 [+0.0007, +0.0213] | -0.0037 [-0.0137, +0.0053] | 0.889 | 0.539 | no |
| 2 | 0.575 (147 of 1872 days never flag) | 197 | 0.547 | 0.386 | 0.0693 | +0.0018 [-0.0072, +0.0099] | -0.0082 [-0.0170, -0.0006] | 0.843 | 0.477 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 188 | 0.536 | 0.394 | 0.0685 | +0.0022 [-0.0077, +0.0108] | -0.0041 [-0.0138, +0.0044] | 0.848 | 0.470 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 176 | 0.522 | 0.409 | 0.0667 | +0.0041 [-0.0033, +0.0103] | -0.0043 [-0.0113, +0.0019] | 0.837 | 0.462 | no |
| 5 | 0.446 (147 of 1869 days never flag) | 192 | 0.543 | 0.391 | 0.0735 | -0.0026 [-0.0122, +0.0056] | -0.0101 [-0.0197, -0.0019] | 0.807 | 0.476 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.760] | 0.269 | 4.58 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.258 | 4.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (105 of 1873 days never flag) | 204 | 0.607 | 0.417 | 0.0535 | +0.0179 [+0.0101, +0.0259] | +0.0028 [-0.0035, +0.0092] | 0.875 | 0.538 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 194 | 0.540 | 0.387 | 0.0657 | +0.0053 [-0.0009, +0.0115] | -0.0047 [-0.0109, +0.0008] | 0.830 | 0.471 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 187 | 0.536 | 0.396 | 0.0646 | +0.0061 [+0.0005, +0.0113] | -0.0002 [-0.0059, +0.0050] | 0.827 | 0.471 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 178 | 0.536 | 0.416 | 0.0644 | +0.0064 [+0.0013, +0.0112] | -0.0021 [-0.0070, +0.0026] | 0.821 | 0.476 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 190 | 0.536 | 0.389 | 0.0693 | +0.0016 [-0.0039, +0.0067] | -0.0059 [-0.0120, -0.0002] | 0.782 | 0.469 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.767] | 0.269 | 4.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.613] | 0.269 | 4.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 210 | 0.607 | 0.405 | 0.0621 | +0.0093 [-0.0004, +0.0185] | -0.0058 [-0.0144, +0.0021] | 0.873 | 0.535 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 210 | 0.590 | 0.390 | 0.0720 | -0.0010 [-0.0101, +0.0068] | -0.0110 [-0.0197, -0.0036] | 0.813 | 0.516 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 192 | 0.522 | 0.375 | 0.0736 | -0.0030 [-0.0119, +0.0047] | -0.0093 [-0.0179, -0.0016] | 0.791 | 0.452 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 170 | 0.471 | 0.382 | 0.0702 | +0.0006 [-0.0064, +0.0073] | -0.0078 [-0.0144, -0.0014] | 0.818 | 0.410 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 159 | 0.435 | 0.377 | 0.0728 | -0.0019 [-0.0084, +0.0035] | -0.0094 [-0.0157, -0.0040] | 0.770 | 0.378 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.769] | 0.269 | 4.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.254 | 4.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 209 | 0.621 | 0.416 | 0.0576 | +0.0139 [+0.0064, +0.0218] | -0.0012 [-0.0075, +0.0047] | 0.850 | 0.551 | no |
| 2 | 0.401 (147 of 1872 days never flag) | 210 | 0.583 | 0.386 | 0.0702 | +0.0009 [-0.0045, +0.0061] | -0.0091 [-0.0150, -0.0036] | 0.767 | 0.508 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 188 | 0.522 | 0.383 | 0.0710 | -0.0003 [-0.0049, +0.0040] | -0.0066 [-0.0115, -0.0020] | 0.718 | 0.455 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 168 | 0.471 | 0.387 | 0.0691 | +0.0017 [-0.0035, +0.0066] | -0.0068 [-0.0118, -0.0018] | 0.760 | 0.412 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 170 | 0.442 | 0.359 | 0.0728 | -0.0019 [-0.0074, +0.0032] | -0.0094 [-0.0153, -0.0039] | 0.709 | 0.379 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.778] | 0.269 | 4.81 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.615] | 0.262 | 4.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 212 | 0.621 | 0.410 | 0.0615 | +0.0099 [-0.0012, +0.0199] | -0.0052 [-0.0151, +0.0036] | 0.891 | 0.549 | no |
| 2 | 0.575 (147 of 1872 days never flag) | 191 | 0.540 | 0.393 | 0.0697 | +0.0014 [-0.0082, +0.0090] | -0.0086 [-0.0178, -0.0009] | 0.840 | 0.473 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 189 | 0.529 | 0.386 | 0.0696 | +0.0011 [-0.0084, +0.0093] | -0.0052 [-0.0143, +0.0030] | 0.843 | 0.462 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 181 | 0.536 | 0.409 | 0.0667 | +0.0041 [-0.0033, +0.0106] | -0.0043 [-0.0116, +0.0021] | 0.841 | 0.474 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 188 | 0.529 | 0.388 | 0.0735 | -0.0026 [-0.0118, +0.0055] | -0.0101 [-0.0192, -0.0020] | 0.803 | 0.463 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.387, 0.769] | 0.269 | 4.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.265 | 4.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 207 | 0.614 | 0.415 | 0.0550 | +0.0164 [+0.0088, +0.0252] | +0.0014 [-0.0051, +0.0077] | 0.879 | 0.544 | no |
| 2 | 0.448 (147 of 1872 days never flag) | 192 | 0.540 | 0.391 | 0.0661 | +0.0049 [-0.0012, +0.0110] | -0.0051 [-0.0113, +0.0006] | 0.827 | 0.472 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 188 | 0.529 | 0.388 | 0.0656 | +0.0050 [-0.0003, +0.0105] | -0.0013 [-0.0067, +0.0038] | 0.824 | 0.463 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 178 | 0.536 | 0.416 | 0.0644 | +0.0064 [+0.0008, +0.0116] | -0.0020 [-0.0076, +0.0033] | 0.823 | 0.476 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 191 | 0.529 | 0.382 | 0.0693 | +0.0016 [-0.0040, +0.0070] | -0.0059 [-0.0121, -0.0001] | 0.776 | 0.461 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.760] | 0.269 | 4.85 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.640] | 0.258 | 4.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 209 | 0.593 | 0.397 | 0.0635 | +0.0079 [-0.0023, +0.0181] | -0.0072 [-0.0166, +0.0017] | 0.868 | 0.520 | no |
| 2 | 0.518 (147 of 1872 days never flag) | 193 | 0.597 | 0.430 | 0.0705 | +0.0005 [-0.0092, +0.0092] | -0.0095 [-0.0189, -0.0013] | 0.824 | 0.534 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 171 | 0.514 | 0.415 | 0.0748 | -0.0041 [-0.0143, +0.0054] | -0.0104 [-0.0204, -0.0010] | 0.796 | 0.457 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 149 | 0.435 | 0.403 | 0.0722 | -0.0014 [-0.0101, +0.0063] | -0.0098 [-0.0186, -0.0017] | 0.814 | 0.383 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 192 | 0.543 | 0.391 | 0.0722 | -0.0012 [-0.0084, +0.0053] | -0.0088 [-0.0155, -0.0021] | 0.778 | 0.476 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.269 | 5.31 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.650] | 0.231 | 4.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 228 | 0.643 | 0.395 | 0.0590 | +0.0124 [+0.0045, +0.0209] | -0.0027 [-0.0094, +0.0043] | 0.840 | 0.563 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 198 | 0.604 | 0.424 | 0.0687 | +0.0024 [-0.0040, +0.0088] | -0.0076 [-0.0139, -0.0012] | 0.781 | 0.539 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 174 | 0.529 | 0.420 | 0.0721 | -0.0015 [-0.0080, +0.0051] | -0.0078 [-0.0149, -0.0010] | 0.730 | 0.471 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 150 | 0.442 | 0.407 | 0.0712 | -0.0003 [-0.0067, +0.0060] | -0.0088 [-0.0158, -0.0018] | 0.752 | 0.391 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 184 | 0.551 | 0.413 | 0.0722 | -0.0013 [-0.0075, +0.0047] | -0.0088 [-0.0154, -0.0024] | 0.721 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.77 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.275, 0.637] | 0.269 | 5.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.778 (126 of 1873 days never flag) | 237 | 0.621 | 0.367 | 0.0630 | +0.0085 [-0.0026, +0.0193] | -0.0066 [-0.0171, +0.0029] | 0.884 | 0.535 | no |
| 2 | 0.518 (147 of 1872 days never flag) | 199 | 0.612 | 0.427 | 0.0682 | +0.0029 [-0.0064, +0.0114] | -0.0071 [-0.0158, +0.0011] | 0.851 | 0.546 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 171 | 0.522 | 0.421 | 0.0707 | -0.0000 [-0.0111, +0.0097] | -0.0064 [-0.0170, +0.0032] | 0.849 | 0.465 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 164 | 0.435 | 0.366 | 0.0687 | +0.0021 [-0.0063, +0.0099] | -0.0063 [-0.0150, +0.0022] | 0.835 | 0.375 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 209 | 0.543 | 0.359 | 0.0729 | -0.0020 [-0.0115, +0.0065] | -0.0095 [-0.0190, -0.0007] | 0.810 | 0.466 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.762] | 0.293 | 6.19 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 5.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (126 of 1873 days never flag) | 253 | 0.657 | 0.364 | 0.0564 | +0.0150 [+0.0069, +0.0234] | -0.0001 [-0.0071, +0.0071] | 0.875 | 0.564 | no |
| 2 | 0.448 (147 of 1872 days never flag) | 198 | 0.612 | 0.429 | 0.0646 | +0.0064 [-0.0007, +0.0133] | -0.0036 [-0.0106, +0.0028] | 0.839 | 0.546 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 173 | 0.536 | 0.428 | 0.0668 | +0.0039 [-0.0036, +0.0106] | -0.0024 [-0.0098, +0.0043] | 0.829 | 0.479 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 164 | 0.442 | 0.372 | 0.0664 | +0.0044 [-0.0024, +0.0109] | -0.0041 [-0.0117, +0.0032] | 0.818 | 0.383 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 209 | 0.543 | 0.359 | 0.0687 | +0.0022 [-0.0041, +0.0081] | -0.0053 [-0.0124, +0.0012] | 0.782 | 0.466 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 4.81 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.647] | 0.258 | 4.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.8 (147 of 1873 days never flag) | 178 | 0.514 | 0.404 | 0.0625 | +0.0089 [-0.0009, +0.0185] | -0.0062 [-0.0153, +0.0021] | 0.871 | 0.453 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 208 | 0.597 | 0.399 | 0.0702 | +0.0009 [-0.0079, +0.0097] | -0.0091 [-0.0174, -0.0012] | 0.826 | 0.525 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 173 | 0.514 | 0.410 | 0.0748 | -0.0041 [-0.0149, +0.0052] | -0.0104 [-0.0209, -0.0012] | 0.802 | 0.456 | no |
| 4 | 0.519 (147 of 1870 days never flag) | 161 | 0.442 | 0.379 | 0.0723 | -0.0015 [-0.0096, +0.0066] | -0.0099 [-0.0180, -0.0020] | 0.816 | 0.384 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 190 | 0.529 | 0.384 | 0.0718 | -0.0009 [-0.0076, +0.0055] | -0.0084 [-0.0150, -0.0018] | 0.784 | 0.461 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.281, 0.650] | 0.269 | 4.88 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.231 | 4.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (147 of 1873 days never flag) | 189 | 0.586 | 0.434 | 0.0580 | +0.0134 [+0.0062, +0.0217] | -0.0017 [-0.0075, +0.0049] | 0.846 | 0.524 | no |
| 2 | 0.381 (147 of 1872 days never flag) | 212 | 0.612 | 0.401 | 0.0683 | +0.0028 [-0.0032, +0.0089] | -0.0072 [-0.0133, -0.0009] | 0.782 | 0.538 | no |
| 3 | 0.431 (147 of 1871 days never flag) | 175 | 0.536 | 0.423 | 0.0721 | -0.0014 [-0.0081, +0.0050] | -0.0078 [-0.0146, -0.0012] | 0.732 | 0.478 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 156 | 0.449 | 0.397 | 0.0712 | -0.0004 [-0.0070, +0.0060] | -0.0089 [-0.0162, -0.0018] | 0.754 | 0.395 | no |
| 5 | 0.387 (147 of 1869 days never flag) | 182 | 0.536 | 0.407 | 0.0719 | -0.0009 [-0.0069, +0.0048] | -0.0085 [-0.0150, -0.0020] | 0.725 | 0.474 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.720] | 0.269 | 5.38 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.636] | 0.269 | 4.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (126 of 1873 days never flag) | 217 | 0.550 | 0.355 | 0.0620 | +0.0094 [-0.0019, +0.0199] | -0.0056 [-0.0170, +0.0039] | 0.888 | 0.469 | no |
| 2 | 0.575 (147 of 1872 days never flag) | 216 | 0.612 | 0.394 | 0.0678 | +0.0033 [-0.0059, +0.0114] | -0.0067 [-0.0155, +0.0010] | 0.852 | 0.536 | no |
| 3 | 0.611 (147 of 1871 days never flag) | 173 | 0.522 | 0.416 | 0.0707 | -0.0000 [-0.0103, +0.0099] | -0.0063 [-0.0168, +0.0034] | 0.851 | 0.463 | no |
| 4 | 0.519 (147 of 1870 days never flag) | 182 | 0.449 | 0.341 | 0.0688 | +0.0020 [-0.0061, +0.0094] | -0.0064 [-0.0146, +0.0015] | 0.838 | 0.380 | no |
| 5 | 0.449 (147 of 1869 days never flag) | 190 | 0.529 | 0.384 | 0.0726 | -0.0016 [-0.0116, +0.0068] | -0.0092 [-0.0191, -0.0005] | 0.814 | 0.461 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_logistic_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.719] | 0.269 | 5.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.276, 0.640] | 0.254 | 4.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.515 (126 of 1873 days never flag) | 229 | 0.586 | 0.358 | 0.0554 | +0.0160 [+0.0082, +0.0243] | +0.0009 [-0.0058, +0.0075] | 0.880 | 0.501 | no |
| 2 | 0.448 (147 of 1872 days never flag) | 214 | 0.619 | 0.402 | 0.0642 | +0.0068 [+0.0001, +0.0135] | -0.0032 [-0.0097, +0.0031] | 0.841 | 0.545 | no |
| 3 | 0.487 (147 of 1871 days never flag) | 172 | 0.522 | 0.419 | 0.0668 | +0.0039 [-0.0031, +0.0106] | -0.0024 [-0.0093, +0.0044] | 0.833 | 0.464 | no |
| 4 | 0.465 (147 of 1870 days never flag) | 171 | 0.457 | 0.368 | 0.0665 | +0.0043 [-0.0024, +0.0108] | -0.0041 [-0.0115, +0.0033] | 0.820 | 0.394 | no |
| 5 | 0.424 (147 of 1869 days never flag) | 189 | 0.529 | 0.386 | 0.0684 | +0.0026 [-0.0037, +0.0083] | -0.0050 [-0.0119, +0.0014] | 0.788 | 0.462 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_quantile_skewt_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.688] | 0.269 | 4.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.643] | 0.269 | 4.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.675 (105 of 1873 days never flag) | 195 | 0.600 | 0.431 | 0.0659 | +0.0055 [-0.0047, +0.0156] | -0.0096 [-0.0191, -0.0005] | 0.862 | 0.536 | no |
| 2 | 0.577 (147 of 1872 days never flag) | 204 | 0.626 | 0.426 | 0.0717 | -0.0006 [-0.0106, +0.0085] | -0.0106 [-0.0192, -0.0023] | 0.821 | 0.558 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 196 | 0.609 | 0.429 | 0.0729 | -0.0022 [-0.0132, +0.0069] | -0.0085 [-0.0193, +0.0003] | 0.815 | 0.544 | no |
| 4 | 0.549 (126 of 1870 days never flag) | 178 | 0.493 | 0.382 | 0.0703 | +0.0006 [-0.0078, +0.0090] | -0.0079 [-0.0162, +0.0004] | 0.829 | 0.429 | no |
| 5 | 0.519 (126 of 1869 days never flag) | 206 | 0.572 | 0.383 | 0.0702 | +0.0007 [-0.0070, +0.0080] | -0.0068 [-0.0148, +0.0003] | 0.810 | 0.499 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_quantile_skewt_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.715] | 0.269 | 5.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.680] | 0.269 | 5.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 200 | 0.614 | 0.430 | 0.0614 | +0.0100 [+0.0019, +0.0190] | -0.0050 [-0.0123, +0.0021] | 0.833 | 0.549 | no |
| 2 | 0.431 (147 of 1872 days never flag) | 198 | 0.612 | 0.429 | 0.0698 | +0.0013 [-0.0057, +0.0080] | -0.0087 [-0.0149, -0.0026] | 0.778 | 0.546 | no |
| 3 | 0.431 (126 of 1871 days never flag) | 196 | 0.623 | 0.439 | 0.0702 | +0.0005 [-0.0058, +0.0068] | -0.0058 [-0.0121, +0.0009] | 0.753 | 0.560 | no |
| 4 | 0.452 (126 of 1870 days never flag) | 184 | 0.500 | 0.375 | 0.0692 | +0.0016 [-0.0050, +0.0084] | -0.0068 [-0.0133, +0.0000] | 0.776 | 0.434 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 213 | 0.580 | 0.376 | 0.0702 | +0.0007 [-0.0062, +0.0075] | -0.0068 [-0.0141, +0.0003] | 0.761 | 0.503 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_quantile_skewt_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.677] | 0.269 | 5.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.269 | 4.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 234 | 0.614 | 0.368 | 0.0653 | +0.0061 [-0.0058, +0.0168] | -0.0090 [-0.0204, +0.0006] | 0.875 | 0.529 | no |
| 2 | 0.575 (147 of 1872 days never flag) | 172 | 0.576 | 0.465 | 0.0693 | +0.0018 [-0.0078, +0.0108] | -0.0082 [-0.0171, -0.0000] | 0.848 | 0.522 | no |
| 3 | 0.566 (126 of 1871 days never flag) | 195 | 0.609 | 0.431 | 0.0688 | +0.0019 [-0.0089, +0.0114] | -0.0044 [-0.0151, +0.0048] | 0.862 | 0.545 | no |
| 4 | 0.549 (126 of 1870 days never flag) | 197 | 0.493 | 0.345 | 0.0668 | +0.0041 [-0.0048, +0.0121] | -0.0044 [-0.0134, +0.0040] | 0.849 | 0.418 | no |
| 5 | 0.597 (126 of 1869 days never flag) | 205 | 0.572 | 0.385 | 0.0709 | -0.0000 [-0.0104, +0.0088] | -0.0075 [-0.0178, +0.0013] | 0.836 | 0.500 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_quantile_skewt_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.720] | 0.269 | 5.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.316, 0.682] | 0.269 | 4.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 229 | 0.607 | 0.371 | 0.0588 | +0.0126 [+0.0042, +0.0215] | -0.0025 [-0.0095, +0.0048] | 0.858 | 0.524 | no |
| 2 | 0.448 (147 of 1872 days never flag) | 201 | 0.619 | 0.428 | 0.0657 | +0.0053 [-0.0024, +0.0131] | -0.0047 [-0.0115, +0.0021] | 0.832 | 0.552 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 190 | 0.609 | 0.442 | 0.0649 | +0.0058 [-0.0010, +0.0126] | -0.0005 [-0.0070, +0.0064] | 0.845 | 0.548 | no |
| 4 | 0.465 (126 of 1870 days never flag) | 196 | 0.500 | 0.352 | 0.0645 | +0.0063 [-0.0008, +0.0135] | -0.0021 [-0.0092, +0.0049] | 0.834 | 0.427 | no |
| 5 | 0.424 (126 of 1869 days never flag) | 205 | 0.572 | 0.385 | 0.0667 | +0.0042 [-0.0027, +0.0108] | -0.0033 [-0.0103, +0.0037] | 0.815 | 0.500 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

