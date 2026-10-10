# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `997256b1b6f8…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## balance_sheet_hierarchical_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.359, 0.719] | 0.231 | 3.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.312 (126 of 1873 days never flag) | 220 | 0.629 | 0.400 | 0.0530 | +0.0184 [+0.0116, +0.0256] | +0.0033 [-0.0010, +0.0076] | 0.896 | 0.552 | no |
| 2 | 0.381 (126 of 1872 days never flag) | 151 | 0.331 | 0.305 | 0.0582 | +0.0128 [+0.0066, +0.0194] | +0.0028 [-0.0019, +0.0077] | 0.882 | 0.270 | no |
| 3 | 0.358 (126 of 1871 days never flag) | 137 | 0.297 | 0.299 | 0.0594 | +0.0113 [+0.0045, +0.0180] | +0.0049 [-0.0005, +0.0106] | 0.875 | 0.242 | no |
| 4 | 0.352 (126 of 1870 days never flag) | 138 | 0.399 | 0.399 | 0.0604 | +0.0104 [+0.0030, +0.0178] | +0.0020 [-0.0046, +0.0085] | 0.871 | 0.351 | no |
| 5 | 0.358 (147 of 1869 days never flag) | 72 | 0.210 | 0.403 | 0.0612 | +0.0097 [+0.0008, +0.0172] | +0.0022 [-0.0060, +0.0088] | 0.855 | 0.185 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.457, difference +0.1527 [+0.0117, +0.2712]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0781, ΔBrier vs climatology +0.0514 [+0.0361, +0.0692], realised minus predicted +0.0205 [-0.0075, +0.0502]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.400 | 0.2508 | 0.2720 | +0.0312 [+0.0072, +0.0569] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1251 | 0.0159 | +0.0190 [+0.0071, +0.0305] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0056 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0046 | 0.0200 | +0.0015 [-0.0037, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.452 | 0.1466 | 0.1165 | +0.0292 [-0.0016, +0.0670] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0078 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0584 | 0.0031 | +0.0250 [+0.0185, +0.0310] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.2635 | 0.4146 | 0.1193 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.389 | 0.2739 | 0.2474 | +0.0262 [+0.0039, +0.0500] |
| day_type | month_end | 150 | 17 | 0.824 | 0.636 | 0.1157 | 0.1133 | +0.0561 [+0.0309, +0.0841] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.341 | 0.0815 | 0.0630 | +0.0110 [+0.0046, +0.0179] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2245 | 0.2903 | +0.1135 [+0.0492, +0.1793] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1387 | 0.1461 | +0.0546 [+0.0236, +0.0858] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0741 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2357 | 0.2213 |

## balance_sheet_scarcity_gbm (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.308, 0.688] | 0.269 | 5.27 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.562] | 0.258 | 4.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.386 (126 of 1873 days never flag) | 232 | 0.679 | 0.409 | 0.0548 | +0.0166 [+0.0096, +0.0247] | +0.0015 [-0.0033, +0.0063] | 0.840 | 0.600 | no |
| 2 | 0.39 (126 of 1872 days never flag) | 203 | 0.568 | 0.389 | 0.0574 | +0.0136 [+0.0074, +0.0198] | +0.0036 [-0.0015, +0.0091] | 0.827 | 0.497 | no |
| 3 | 0.353 (126 of 1871 days never flag) | 161 | 0.319 | 0.273 | 0.0621 | +0.0086 [+0.0030, +0.0140] | +0.0023 [-0.0032, +0.0073] | 0.808 | 0.251 | no |
| 4 | 0.315 (147 of 1870 days never flag) | 131 | 0.362 | 0.382 | 0.0657 | +0.0051 [-0.0006, +0.0103] | -0.0033 [-0.0084, +0.0015] | 0.700 | 0.316 | no |
| 5 | 0.356 (147 of 1869 days never flag) | 122 | 0.290 | 0.328 | 0.0652 | +0.0057 [-0.0024, +0.0127] | -0.0018 [-0.0088, +0.0043] | 0.775 | 0.242 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.580 (climatology 0.457, difference +0.1233 [-0.0339, +0.2651]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0846, ΔBrier vs climatology +0.0449 [+0.0297, +0.0619], realised minus predicted +0.0222 [-0.0088, +0.0544]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.398 | 0.2148 | 0.2720 | +0.0140 [-0.0087, +0.0387] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1108 | 0.0159 | +0.0238 [+0.0113, +0.0354] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0139 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0054 | 0.0200 | +0.0011 [-0.0043, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.576 | 0.1495 | 0.1165 | +0.0380 [+0.0015, +0.0813] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0178 | 0.0048 | +0.0075 [+0.0054, +0.0095] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0496 | 0.0031 | +0.0268 [+0.0209, +0.0327] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2688 | 0.4146 | 0.1445 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.394 | 0.2364 | 0.2474 | +0.0183 [-0.0028, +0.0420] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1037 | 0.1133 | +0.0494 [+0.0266, +0.0775] |
| day_type | ordinary | 1603 | 101 | 0.713 | 0.365 | 0.0814 | 0.0630 | +0.0110 [+0.0040, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1218 | 0.2903 | +0.0611 [-0.0429, +0.1641] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.0844 | 0.1461 | +0.0459 [+0.0292, +0.0633] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.3393 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2121 | 0.2213 |

## base_adaptive_offset (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 5 | 0.192 [0.067, 0.333] | 0.115 | 1.19 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.000, 0.222] | 0.115 | 1.19 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.712 (147 of 1873 days never flag) | 45 | 0.214 | 0.667 | 0.0665 | +0.0049 [-0.0123, +0.0207] | -0.0102 [-0.0257, +0.0037] | 0.922 | 0.206 | no |
| 2 | 0.836 (147 of 1872 days never flag) | 36 | 0.137 | 0.528 | 0.0773 | -0.0062 [-0.0267, +0.0115] | -0.0162 [-0.0358, +0.0005] | 0.901 | 0.127 | no |
| 3 | 0.838 (147 of 1871 days never flag) | 28 | 0.109 | 0.536 | 0.0792 | -0.0085 [-0.0277, +0.0090] | -0.0149 [-0.0333, +0.0023] | 0.895 | 0.101 | no |
| 4 | 0.823 (147 of 1870 days never flag) | 37 | 0.152 | 0.568 | 0.0751 | -0.0043 [-0.0219, +0.0129] | -0.0127 [-0.0299, +0.0042] | 0.900 | 0.143 | no |
| 5 | 0.735 (147 of 1869 days never flag) | 51 | 0.145 | 0.392 | 0.0715 | -0.0006 [-0.0181, +0.0151] | -0.0081 [-0.0249, +0.0070] | 0.900 | 0.127 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.670 (climatology 0.457, difference +0.2131 [+0.0308, +0.3574]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0841, ΔBrier vs climatology +0.0454 [+0.0213, +0.0720], realised minus predicted +0.0034 [-0.0253, +0.0342]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.216 | 0.710 | 0.4968 | 0.2720 | -0.0479 [-0.1324, +0.0286] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0253 | 0.0159 | +0.0344 [+0.0226, +0.0444] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0049 | 0.0200 | +0.0049 [+0.0006, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.636 | 0.0886 | 0.1165 | +0.0281 [+0.0060, +0.0567] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0028 | 0.0048 | +0.0095 [+0.0078, +0.0112] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0029 | 0.0031 | +0.0301 [+0.0228, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.500 | 0.1981 | 0.4146 | +0.1186 [+0.0410, +0.2131] |
| scarcity_state | 3 | 473 | 117 | 0.231 | 0.675 | 0.4314 | 0.2474 | -0.0322 [-0.1000, +0.0284] |
| day_type | month_end | 150 | 17 | 0.353 | 0.750 | 0.1398 | 0.1133 | +0.0341 [-0.0005, +0.0688] |
| day_type | ordinary | 1603 | 101 | 0.119 | 0.571 | 0.1080 | 0.0630 | -0.0035 [-0.0226, +0.0129] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3463 | 0.2903 | +0.1414 [+0.0685, +0.2138] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.750 | 0.1260 | 0.1461 | +0.0600 [+0.0192, +0.1048] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0027 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.3221 | 0.2213 |

## base_online_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 4 | 0.154 [0.042, 0.286] | 0.115 | 0.85 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.000, 0.222] | 0.115 | 0.85 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.82 (147 of 1873 days never flag) | 31 | 0.164 | 0.742 | 0.0663 | +0.0051 [-0.0125, +0.0204] | -0.0100 [-0.0262, +0.0036] | 0.915 | 0.160 | no |
| 2 | 0.836 (147 of 1872 days never flag) | 31 | 0.129 | 0.581 | 0.0763 | -0.0053 [-0.0259, +0.0123] | -0.0153 [-0.0353, +0.0016] | 0.892 | 0.122 | no |
| 3 | 0.838 (147 of 1871 days never flag) | 26 | 0.109 | 0.577 | 0.0774 | -0.0067 [-0.0254, +0.0113] | -0.0130 [-0.0311, +0.0038] | 0.892 | 0.102 | no |
| 4 | 0.823 (147 of 1870 days never flag) | 25 | 0.116 | 0.640 | 0.0728 | -0.0020 [-0.0200, +0.0142] | -0.0105 [-0.0281, +0.0053] | 0.896 | 0.111 | no |
| 5 | 0.735 (147 of 1869 days never flag) | 37 | 0.109 | 0.405 | 0.0700 | +0.0009 [-0.0154, +0.0161] | -0.0066 [-0.0222, +0.0081] | 0.871 | 0.096 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.662 (climatology 0.457, difference +0.2049 [+0.0237, +0.3601]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0197, +0.0691], realised minus predicted +0.0007 [-0.0311, +0.0316]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.176 | 0.750 | 0.4944 | 0.2720 | -0.0492 [-0.1338, +0.0280] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0445 | 0.0159 | +0.0363 [+0.0284, +0.0448] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0019 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0077 | 0.0200 | +0.0047 [+0.0005, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.714 | 0.0885 | 0.1165 | +0.0294 [+0.0077, +0.0565] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0063 | 0.0048 | +0.0095 [+0.0078, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0114 | 0.0031 | +0.0299 [+0.0228, +0.0376] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1775 | 0.4146 | 0.1176 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.188 | 0.733 | 0.4324 | 0.2474 | -0.0313 [-0.1008, +0.0306] |
| day_type | month_end | 150 | 17 | 0.235 | 0.800 | 0.1392 | 0.1133 | +0.0313 [-0.0012, +0.0629] |
| day_type | ordinary | 1603 | 101 | 0.109 | 0.688 | 0.1128 | 0.0630 | -0.0036 [-0.0229, +0.0128] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.3086 | 0.2903 | +0.1610 [+0.1027, +0.2277] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.667 | 0.1200 | 0.1461 | +0.0622 [+0.0203, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.0200 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2586 | 0.2213 |

## extreme_value_tail (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.240, 0.600] | 0.269 | 5.04 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.179, 0.529] | 0.231 | 3.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.326 (126 of 1873 days never flag) | 213 | 0.586 | 0.385 | 0.0520 | +0.0194 [+0.0134, +0.0262] | +0.0043 [-0.0017, +0.0101] | 0.921 | 0.510 | no |
| 2 | 0.356 (147 of 1872 days never flag) | 144 | 0.446 | 0.431 | 0.0554 | +0.0157 [+0.0101, +0.0222] | +0.0057 [-0.0004, +0.0121] | 0.909 | 0.399 | no |
| 3 | 0.364 (147 of 1871 days never flag) | 143 | 0.428 | 0.413 | 0.0564 | +0.0142 [+0.0085, +0.0205] | +0.0079 [+0.0019, +0.0142] | 0.904 | 0.379 | no |
| 4 | 0.354 (147 of 1870 days never flag) | 143 | 0.442 | 0.427 | 0.0558 | +0.0150 [+0.0092, +0.0210] | +0.0066 [+0.0003, +0.0130] | 0.906 | 0.395 | no |
| 5 | 0.35 (147 of 1869 days never flag) | 143 | 0.420 | 0.406 | 0.0564 | +0.0145 [+0.0092, +0.0203] | +0.0070 [+0.0010, +0.0132] | 0.905 | 0.371 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.611 (climatology 0.457, difference +0.1536 [+0.0379, +0.2488]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0864, ΔBrier vs climatology +0.0431 [+0.0308, +0.0564], realised minus predicted +0.0683 [+0.0364, +0.1016]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.382 | 0.2680 | 0.2720 | +0.0378 [+0.0106, +0.0698] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0397 | 0.0159 | +0.0354 [+0.0268, +0.0441] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0000 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0022 [-0.0016, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.750 | 0.0259 | 0.1165 | +0.0094 [+0.0013, +0.0191] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0091 [+0.0074, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0005 | 0.0031 | +0.0302 [+0.0229, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.500 | 0.0509 | 0.4146 | +0.0066 [-0.0153, +0.0368] |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.384 | 0.2417 | 0.2474 | +0.0357 [+0.0140, +0.0604] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0800 | 0.1133 | +0.0290 [+0.0188, +0.0400] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.335 | 0.0564 | 0.0630 | +0.0142 [+0.0082, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2083 | 0.2903 | +0.1148 [+0.0604, +0.1722] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.0927 | 0.1461 | +0.0629 [+0.0363, +0.0926] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1546 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2533 | 0.2213 |

## hierarchical_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.319 | 6.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.682] | 0.319 | 6.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.336 (147 of 1873 days never flag) | 225 | 0.650 | 0.404 | 0.0530 | +0.0184 [+0.0114, +0.0260] | +0.0034 [-0.0007, +0.0073] | 0.880 | 0.573 | no |
| 2 | 0.373 (147 of 1872 days never flag) | 200 | 0.619 | 0.430 | 0.0589 | +0.0121 [+0.0066, +0.0178] | +0.0021 [-0.0016, +0.0061] | 0.847 | 0.553 | no |
| 3 | 0.383 (147 of 1871 days never flag) | 185 | 0.580 | 0.432 | 0.0607 | +0.0100 [+0.0053, +0.0146] | +0.0037 [-0.0001, +0.0076] | 0.834 | 0.519 | no |
| 4 | 0.407 (147 of 1870 days never flag) | 187 | 0.493 | 0.364 | 0.0603 | +0.0105 [+0.0057, +0.0154] | +0.0020 [-0.0023, +0.0062] | 0.833 | 0.424 | no |
| 5 | 0.451 (126 of 1869 days never flag) | 244 | 0.594 | 0.336 | 0.0608 | +0.0101 [+0.0050, +0.0151] | +0.0026 [-0.0020, +0.0071] | 0.827 | 0.501 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.552 (climatology 0.457, difference +0.0945 [-0.0037, +0.1778]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0390 [+0.0269, +0.0533], realised minus predicted +0.0465 [+0.0139, +0.0831]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2190 | 0.2720 | +0.0265 [+0.0024, +0.0512] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.1363 | 0.0159 | +0.0181 [+0.0037, +0.0311] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0085 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0065 | 0.0200 | +0.0013 [-0.0036, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.552 | 0.1189 | 0.1165 | +0.0382 [+0.0069, +0.0750] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0590 | 0.0031 | +0.0263 [+0.0203, +0.0319] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2358 | 0.4146 | 0.1250 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.394 | 0.2484 | 0.2474 | +0.0249 [+0.0018, +0.0497] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1016 | 0.1133 | +0.0440 [+0.0227, +0.0682] |
| day_type | ordinary | 1603 | 101 | 0.644 | 0.359 | 0.0752 | 0.0630 | +0.0128 [+0.0065, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2214 | 0.2903 | +0.0754 [+0.0169, +0.1274] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1263 | 0.1461 | +0.0569 [+0.0308, +0.0829] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2425 | 0.2213 |

## hierarchical_logistic_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.192 | 2.46 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 13 | 0.500 [0.321, 0.683] | 0.192 | 2.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.336 (147 of 1873 days never flag) | 92 | 0.307 | 0.467 | 0.0530 | +0.0184 [+0.0118, +0.0257] | +0.0034 [-0.0007, +0.0071] | 0.880 | 0.279 | no |
| 2 | 0.373 (147 of 1872 days never flag) | 64 | 0.165 | 0.359 | 0.0589 | +0.0121 [+0.0068, +0.0180] | +0.0021 [-0.0016, +0.0063] | 0.847 | 0.142 | no |
| 3 | 0.383 (147 of 1871 days never flag) | 59 | 0.152 | 0.356 | 0.0607 | +0.0100 [+0.0050, +0.0147] | +0.0037 [-0.0000, +0.0075] | 0.834 | 0.130 | no |
| 4 | 0.407 (147 of 1870 days never flag) | 68 | 0.246 | 0.500 | 0.0603 | +0.0105 [+0.0056, +0.0153] | +0.0020 [-0.0024, +0.0063] | 0.833 | 0.227 | no |
| 5 | 0.451 (126 of 1869 days never flag) | 102 | 0.275 | 0.373 | 0.0608 | +0.0101 [+0.0050, +0.0151] | +0.0026 [-0.0021, +0.0070] | 0.827 | 0.238 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.552 (climatology 0.457, difference +0.0945 [+0.0003, +0.1840]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0390 [+0.0269, +0.0525], realised minus predicted +0.0465 [+0.0130, +0.0809]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.324 | 0.452 | 0.2190 | 0.2720 | +0.0265 [+0.0034, +0.0525] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1363 | 0.0159 | +0.0181 [+0.0030, +0.0306] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0085 | 0.0000 | +0.0137 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0065 | 0.0200 | +0.0013 [-0.0038, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.1189 | 0.1165 | +0.0382 [+0.0081, +0.0733] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0590 | 0.0031 | +0.0263 [+0.0204, +0.0318] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.2358 | 0.4146 | +0.1250 [+0.0041, +0.2202] |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.449 | 0.2484 | 0.2474 | +0.0249 [+0.0028, +0.0497] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1016 | 0.1133 | +0.0440 [+0.0226, +0.0691] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.406 | 0.0752 | 0.0630 | +0.0128 [+0.0066, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2214 | 0.2903 | +0.0754 [+0.0165, +0.1327] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.556 | 0.1263 | 0.1461 | +0.0569 [+0.0326, +0.0844] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2425 | 0.2213 |

## hierarchical_logistic_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.217, 0.560] | 0.115 | 1.12 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.138, 0.484] | 0.115 | 1.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.336 (147 of 1873 days never flag) | 48 | 0.150 | 0.438 | 0.0530 | +0.0184 [+0.0115, +0.0263] | +0.0034 [-0.0004, +0.0072] | 0.880 | 0.134 | no |
| 2 | 0.373 (147 of 1872 days never flag) | 41 | 0.129 | 0.439 | 0.0589 | +0.0121 [+0.0064, +0.0176] | +0.0021 [-0.0018, +0.0060] | 0.847 | 0.116 | no |
| 3 | 0.383 (147 of 1871 days never flag) | 37 | 0.116 | 0.432 | 0.0607 | +0.0100 [+0.0054, +0.0146] | +0.0037 [+0.0001, +0.0077] | 0.834 | 0.104 | no |
| 4 | 0.407 (147 of 1870 days never flag) | 38 | 0.123 | 0.447 | 0.0603 | +0.0105 [+0.0059, +0.0152] | +0.0020 [-0.0021, +0.0066] | 0.833 | 0.111 | no |
| 5 | 0.451 (126 of 1869 days never flag) | 44 | 0.109 | 0.341 | 0.0608 | +0.0101 [+0.0051, +0.0154] | +0.0026 [-0.0020, +0.0073] | 0.827 | 0.092 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.552 (climatology 0.457, difference +0.0945 [-0.0038, +0.1754]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0390 [+0.0264, +0.0540], realised minus predicted +0.0465 [+0.0139, +0.0820]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.137 | 0.424 | 0.2190 | 0.2720 | +0.0265 [+0.0035, +0.0518] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1363 | 0.0159 | +0.0181 [+0.0038, +0.0307] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0085 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0065 | 0.0200 | +0.0013 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.750 | 0.1189 | 0.1165 | +0.0382 [+0.0081, +0.0767] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0590 | 0.0031 | +0.0263 [+0.0202, +0.0321] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.2358 | 0.4146 | 0.1250 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.154 | 0.400 | 0.2484 | 0.2474 | +0.0249 [+0.0030, +0.0487] |
| day_type | month_end | 150 | 17 | 0.176 | 0.600 | 0.1016 | 0.1133 | +0.0440 [+0.0235, +0.0684] |
| day_type | ordinary | 1603 | 101 | 0.119 | 0.343 | 0.0752 | 0.0630 | +0.0128 [+0.0064, +0.0201] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.2214 | 0.2903 | +0.0754 [+0.0169, +0.1300] |
| day_type | tax_date | 89 | 13 | 0.231 | 1.000 | 0.1263 | 0.1461 | +0.0569 [+0.0316, +0.0859] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2425 | 0.2213 |

## hierarchical_logistic_fed_repo (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.409, 0.750] | 0.269 | 5.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.355, 0.720] | 0.269 | 5.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.397 (147 of 1873 days never flag) | 171 | 0.514 | 0.421 | 0.0555 | +0.0160 [+0.0107, +0.0222] | +0.0009 [-0.0022, +0.0039] | 0.835 | 0.457 | no |
| 2 | 0.353 (147 of 1872 days never flag) | 152 | 0.446 | 0.408 | 0.0633 | +0.0077 [+0.0032, +0.0126] | -0.0023 [-0.0054, +0.0008] | 0.763 | 0.394 | no |
| 3 | 0.368 (147 of 1871 days never flag) | 176 | 0.500 | 0.392 | 0.0635 | +0.0072 [+0.0027, +0.0117] | +0.0008 [-0.0026, +0.0044] | 0.762 | 0.438 | no |
| 4 | 0.298 (147 of 1870 days never flag) | 180 | 0.500 | 0.383 | 0.0637 | +0.0071 [+0.0028, +0.0117] | -0.0013 [-0.0047, +0.0024] | 0.753 | 0.436 | no |
| 5 | 0.341 (126 of 1869 days never flag) | 213 | 0.478 | 0.310 | 0.0635 | +0.0074 [+0.0028, +0.0119] | -0.0001 [-0.0040, +0.0038] | 0.757 | 0.393 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.457, difference +0.1176 [+0.0133, +0.2434]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0933, ΔBrier vs climatology +0.0361 [+0.0242, +0.0494], realised minus predicted +0.0342 [+0.0005, +0.0703]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.408 | 0.2164 | 0.2720 | +0.0190 [-0.0015, +0.0425] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1562 | 0.0159 | +0.0186 [+0.0094, +0.0270] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0129 | 0.0200 | +0.0015 [-0.0032, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0987 | 0.1165 | +0.0322 [+0.0077, +0.0625] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0184 | 0.0048 | +0.0086 [+0.0068, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0947 | 0.0031 | +0.0206 [+0.0151, +0.0260] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1610 | 0.4146 | 0.0814 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.598 | 0.414 | 0.2317 | 0.2474 | +0.0233 [+0.0049, +0.0455] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1054 | 0.1133 | +0.0332 [+0.0139, +0.0543] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.361 | 0.0828 | 0.0630 | +0.0108 [+0.0057, +0.0168] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2072 | 0.2903 | +0.0896 [+0.0290, +0.1456] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1233 | 0.1461 | +0.0545 [+0.0341, +0.0760] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0403 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2034 | 0.2213 |

## hierarchical_logistic_fed_repo_sameday (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.758] | 0.283 | 5.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.760] | 0.283 | 5.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.313 (126 of 1873 days never flag) | 207 | 0.593 | 0.401 | 0.0544 | +0.0170 [+0.0112, +0.0236] | +0.0019 [-0.0017, +0.0055] | 0.833 | 0.521 | no |
| 2 | 0.362 (147 of 1872 days never flag) | 163 | 0.511 | 0.436 | 0.0622 | +0.0089 [+0.0046, +0.0132] | -0.0011 [-0.0044, +0.0023] | 0.792 | 0.458 | no |
| 3 | 0.343 (147 of 1871 days never flag) | 149 | 0.442 | 0.409 | 0.0645 | +0.0062 [+0.0018, +0.0103] | -0.0001 [-0.0034, +0.0031] | 0.744 | 0.391 | no |
| 4 | 0.36 (147 of 1870 days never flag) | 189 | 0.514 | 0.376 | 0.0632 | +0.0076 [+0.0031, +0.0123] | -0.0009 [-0.0043, +0.0030] | 0.754 | 0.446 | no |
| 5 | 0.328 (126 of 1869 days never flag) | 226 | 0.522 | 0.319 | 0.0640 | +0.0070 [+0.0026, +0.0114] | -0.0006 [-0.0044, +0.0031] | 0.734 | 0.433 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.564 (climatology 0.457, difference +0.1064 [-0.0070, +0.2472]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0914, ΔBrier vs climatology +0.0380 [+0.0265, +0.0515], realised minus predicted +0.0313 [-0.0033, +0.0680]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.389 | 0.2171 | 0.2720 | +0.0219 [+0.0009, +0.0444] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1566 | 0.0159 | +0.0200 [+0.0110, +0.0287] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0220 | 0.0000 | +0.0131 [+0.0115, +0.0149] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0108 | 0.0200 | +0.0014 [-0.0031, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.591 | 0.0948 | 0.1165 | +0.0341 [+0.0103, +0.0672] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0166 | 0.0048 | +0.0086 [+0.0068, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0927 | 0.0031 | +0.0210 [+0.0158, +0.0264] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.1471 | 0.4146 | 0.0867 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.392 | 0.2332 | 0.2474 | +0.0266 [+0.0061, +0.0482] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1026 | 0.1133 | +0.0324 [+0.0125, +0.0531] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.345 | 0.0816 | 0.0630 | +0.0121 [+0.0067, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2095 | 0.2903 | +0.0915 [+0.0269, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1220 | 0.1461 | +0.0532 [+0.0330, +0.0767] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0310 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2138 | 0.2213 |

## hierarchical_logistic_net (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.762] | 0.269 | 5.46 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.172, 0.526] | 0.231 | 4.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.368 (126 of 1873 days never flag) | 214 | 0.650 | 0.425 | 0.0540 | +0.0175 [+0.0113, +0.0242] | +0.0024 [-0.0016, +0.0061] | 0.850 | 0.579 | no |
| 2 | 0.356 (126 of 1872 days never flag) | 219 | 0.554 | 0.352 | 0.0597 | +0.0114 [+0.0062, +0.0166] | +0.0014 [-0.0028, +0.0053] | 0.837 | 0.472 | no |
| 3 | 0.364 (168 of 1871 days never flag) | 174 | 0.471 | 0.374 | 0.0619 | +0.0088 [+0.0042, +0.0133] | +0.0024 [-0.0014, +0.0063] | 0.824 | 0.408 | no |
| 4 | 0.37 (189 of 1870 days never flag) | 138 | 0.406 | 0.406 | 0.0619 | +0.0089 [+0.0042, +0.0135] | +0.0005 [-0.0041, +0.0048] | 0.807 | 0.358 | no |
| 5 | 0.413 (168 of 1869 days never flag) | 159 | 0.420 | 0.365 | 0.0622 | +0.0087 [+0.0037, +0.0138] | +0.0012 [-0.0036, +0.0062] | 0.794 | 0.362 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.523 (climatology 0.457, difference +0.0660 [-0.0294, +0.1634]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0939, ΔBrier vs climatology +0.0356 [+0.0241, +0.0481], realised minus predicted +0.0423 [+0.0096, +0.0768]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.418 | 0.2122 | 0.2720 | +0.0250 [+0.0039, +0.0472] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1535 | 0.0159 | +0.0150 [+0.0019, +0.0268] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0133 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0092 | 0.0200 | +0.0015 [-0.0029, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.600 | 0.1082 | 0.1165 | +0.0365 [+0.0080, +0.0740] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0109 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0712 | 0.0031 | +0.0239 [+0.0183, +0.0293] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.2176 | 0.4146 | 0.1085 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.411 | 0.2411 | 0.2474 | +0.0241 [+0.0032, +0.0459] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.1018 | 0.1133 | +0.0425 [+0.0218, +0.0667] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.376 | 0.0774 | 0.0630 | +0.0118 [+0.0059, +0.0180] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2435 | 0.2903 | +0.1078 [+0.0596, +0.1528] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1173 | 0.1461 | +0.0463 [+0.0247, +0.0688] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0681 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2254 | 0.2213 |

## hierarchical_logistic_srf (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.741] | 0.269 | 5.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.760] | 0.269 | 5.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.325 (147 of 1873 days never flag) | 182 | 0.543 | 0.418 | 0.0545 | +0.0169 [+0.0108, +0.0238] | +0.0018 [-0.0014, +0.0050] | 0.843 | 0.482 | no |
| 2 | 0.368 (147 of 1872 days never flag) | 163 | 0.489 | 0.417 | 0.0622 | +0.0088 [+0.0041, +0.0140] | -0.0012 [-0.0044, +0.0020] | 0.783 | 0.434 | no |
| 3 | 0.37 (147 of 1871 days never flag) | 168 | 0.471 | 0.387 | 0.0637 | +0.0070 [+0.0028, +0.0110] | +0.0007 [-0.0025, +0.0040] | 0.766 | 0.412 | no |
| 4 | 0.352 (147 of 1870 days never flag) | 163 | 0.471 | 0.399 | 0.0633 | +0.0076 [+0.0035, +0.0117] | -0.0009 [-0.0043, +0.0026] | 0.762 | 0.414 | no |
| 5 | 0.342 (126 of 1869 days never flag) | 216 | 0.500 | 0.319 | 0.0627 | +0.0082 [+0.0036, +0.0131] | +0.0007 [-0.0032, +0.0046] | 0.772 | 0.415 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.558 (climatology 0.457, difference +0.1008 [+0.0015, +0.2215]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0931, ΔBrier vs climatology +0.0364 [+0.0248, +0.0494], realised minus predicted +0.0377 [+0.0030, +0.0737]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.408 | 0.2121 | 0.2720 | +0.0212 [+0.0016, +0.0433] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1564 | 0.0159 | +0.0180 [+0.0084, +0.0260] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0226 | 0.0000 | +0.0131 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0140 | 0.0200 | +0.0015 [-0.0030, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.560 | 0.1143 | 0.1165 | +0.0366 [+0.0081, +0.0709] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0178 | 0.0048 | +0.0086 [+0.0067, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0949 | 0.0031 | +0.0206 [+0.0152, +0.0258] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.2087 | 0.4146 | +0.1051 [+0.0033, +0.1818] |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.407 | 0.2325 | 0.2474 | +0.0250 [+0.0051, +0.0457] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1081 | 0.1133 | +0.0356 [+0.0132, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.355 | 0.0833 | 0.0630 | +0.0116 [+0.0059, +0.0178] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2144 | 0.2903 | +0.0952 [+0.0340, +0.1534] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1265 | 0.1461 | +0.0534 [+0.0312, +0.0756] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0322 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2228 | 0.2213 |

## hierarchical_logistic_srf_sameday (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.758] | 0.269 | 5.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.384 (126 of 1873 days never flag) | 199 | 0.564 | 0.397 | 0.0538 | +0.0177 [+0.0116, +0.0245] | +0.0026 [-0.0007, +0.0060] | 0.836 | 0.495 | no |
| 2 | 0.351 (147 of 1872 days never flag) | 167 | 0.525 | 0.437 | 0.0614 | +0.0097 [+0.0051, +0.0145] | -0.0003 [-0.0034, +0.0029] | 0.802 | 0.471 | no |
| 3 | 0.326 (147 of 1871 days never flag) | 152 | 0.464 | 0.421 | 0.0643 | +0.0064 [+0.0023, +0.0105] | +0.0000 [-0.0032, +0.0034] | 0.750 | 0.413 | no |
| 4 | 0.327 (147 of 1870 days never flag) | 172 | 0.464 | 0.372 | 0.0634 | +0.0075 [+0.0035, +0.0116] | -0.0010 [-0.0045, +0.0027] | 0.760 | 0.401 | no |
| 5 | 0.34 (126 of 1869 days never flag) | 219 | 0.514 | 0.324 | 0.0631 | +0.0078 [+0.0032, +0.0128] | +0.0003 [-0.0035, +0.0043] | 0.748 | 0.429 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.558 (climatology 0.457, difference +0.1008 [-0.0072, +0.2197]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0929, ΔBrier vs climatology +0.0366 [+0.0247, +0.0495], realised minus predicted +0.0358 [+0.0022, +0.0733]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.379 | 0.2136 | 0.2720 | +0.0227 [+0.0030, +0.0464] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1586 | 0.0159 | +0.0172 [+0.0084, +0.0254] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0227 | 0.0000 | +0.0131 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0142 | 0.0200 | +0.0015 [-0.0033, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.650 | 0.1148 | 0.1165 | +0.0405 [+0.0104, +0.0784] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0180 | 0.0048 | +0.0086 [+0.0069, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0956 | 0.0031 | +0.0203 [+0.0153, +0.0255] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.2113 | 0.4146 | 0.1244 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.385 | 0.2342 | 0.2474 | +0.0263 [+0.0069, +0.0487] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1080 | 0.1133 | +0.0356 [+0.0139, +0.0614] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.333 | 0.0841 | 0.0630 | +0.0126 [+0.0068, +0.0192] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2190 | 0.2903 | +0.0950 [+0.0338, +0.1536] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1256 | 0.1461 | +0.0522 [+0.0297, +0.0757] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0304 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2214 | 0.2213 |

## ngboost_laplace (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.826] | 0.231 | 4.08 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.650] | 0.231 | 4.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.334 (126 of 1873 days never flag) | 161 | 0.536 | 0.466 | 0.0462 | +0.0252 [+0.0186, +0.0323] | +0.0101 [+0.0050, +0.0152] | 0.928 | 0.486 | no |
| 2 | 0.297 (147 of 1872 days never flag) | 150 | 0.432 | 0.400 | 0.0568 | +0.0143 [+0.0086, +0.0201] | +0.0043 [-0.0009, +0.0092] | 0.899 | 0.380 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 144 | 0.428 | 0.410 | 0.0595 | +0.0112 [+0.0046, +0.0169] | +0.0049 [-0.0008, +0.0100] | 0.892 | 0.378 | no |
| 4 | 0.302 (126 of 1870 days never flag) | 133 | 0.290 | 0.301 | 0.0615 | +0.0093 [+0.0028, +0.0154] | +0.0008 [-0.0050, +0.0062] | 0.873 | 0.236 | no |
| 5 | 0.32 (126 of 1869 days never flag) | 163 | 0.413 | 0.350 | 0.0637 | +0.0072 [-0.0004, +0.0140] | -0.0003 [-0.0076, +0.0060] | 0.862 | 0.352 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## ngboost_laplace_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.474, 0.828] | 0.192 | 1.73 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.647] | 0.192 | 1.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.334 (126 of 1873 days never flag) | 66 | 0.250 | 0.530 | 0.0462 | +0.0252 [+0.0185, +0.0328] | +0.0101 [+0.0052, +0.0151] | 0.928 | 0.232 | no |
| 2 | 0.297 (147 of 1872 days never flag) | 50 | 0.151 | 0.420 | 0.0568 | +0.0143 [+0.0090, +0.0196] | +0.0043 [-0.0009, +0.0089] | 0.899 | 0.134 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 48 | 0.152 | 0.438 | 0.0595 | +0.0112 [+0.0050, +0.0173] | +0.0049 [-0.0007, +0.0102] | 0.892 | 0.137 | no |
| 4 | 0.302 (126 of 1870 days never flag) | 60 | 0.138 | 0.317 | 0.0615 | +0.0093 [+0.0032, +0.0160] | +0.0008 [-0.0048, +0.0064] | 0.873 | 0.114 | no |
| 5 | 0.32 (126 of 1869 days never flag) | 67 | 0.159 | 0.328 | 0.0637 | +0.0072 [+0.0002, +0.0144] | -0.0003 [-0.0072, +0.0062] | 0.862 | 0.133 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.556 (climatology 0.457, difference +0.0986 [-0.0509, +0.1901]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0303, +0.0558], realised minus predicted +0.0654 [+0.0341, +0.0987]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.245 | 0.490 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0853] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0503 | 0.0159 | +0.0329 [+0.0231, +0.0420] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0005, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.276 | 1.000 | 0.0443 | 0.1165 | +0.0287 [+0.0116, +0.0512] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0080, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.333 | 0.0268 | 0.0031 | +0.0285 [+0.0230, +0.0338] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | +0.0409 [+0.0046, +0.0673] |
| scarcity_state | 3 | 473 | 117 | 0.256 | 0.508 | 0.2024 | 0.2474 | +0.0558 [+0.0323, +0.0822] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.0819 | 0.1133 | +0.0481 [+0.0294, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.395 | 0.0518 | 0.0630 | +0.0187 [+0.0122, +0.0259] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.750 | 0.1699 | 0.2903 | +0.1308 [+0.0516, +0.2165] |
| day_type | tax_date | 89 | 13 | 0.462 | 1.000 | 0.0904 | 0.1461 | +0.0670 [+0.0496, +0.0853] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## ngboost_laplace_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.609] | 0.115 | 0.85 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 5 | 0.192 [0.074, 0.323] | 0.115 | 0.85 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.334 (126 of 1873 days never flag) | 48 | 0.207 | 0.604 | 0.0462 | +0.0252 [+0.0184, +0.0329] | +0.0101 [+0.0051, +0.0151] | 0.928 | 0.196 | no |
| 2 | 0.297 (147 of 1872 days never flag) | 33 | 0.108 | 0.455 | 0.0568 | +0.0143 [+0.0089, +0.0198] | +0.0043 [-0.0010, +0.0090] | 0.899 | 0.098 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 31 | 0.109 | 0.484 | 0.0595 | +0.0112 [+0.0048, +0.0174] | +0.0049 [-0.0005, +0.0103] | 0.892 | 0.099 | no |
| 4 | 0.302 (126 of 1870 days never flag) | 26 | 0.051 | 0.269 | 0.0615 | +0.0093 [+0.0030, +0.0154] | +0.0008 [-0.0050, +0.0062] | 0.873 | 0.040 | no |
| 5 | 0.32 (126 of 1869 days never flag) | 31 | 0.065 | 0.290 | 0.0637 | +0.0072 [+0.0001, +0.0138] | -0.0003 [-0.0070, +0.0058] | 0.862 | 0.053 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.556 (climatology 0.457, difference +0.0986 [-0.0574, +0.1872]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0304, +0.0550], realised minus predicted +0.0654 [+0.0339, +0.0998]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.186 | 0.576 | 0.2236 | 0.2720 | +0.0543 [+0.0260, +0.0848] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0503 | 0.0159 | +0.0329 [+0.0236, +0.0420] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.276 | 1.000 | 0.0443 | 0.1165 | +0.0287 [+0.0111, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0080, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.333 | 0.0268 | 0.0031 | +0.0285 [+0.0229, +0.0344] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | 0.0409 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.205 | 0.585 | 0.2024 | 0.2474 | +0.0558 [+0.0326, +0.0810] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.0819 | 0.1133 | +0.0481 [+0.0300, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.139 | 0.483 | 0.0518 | 0.0630 | +0.0187 [+0.0121, +0.0266] |
| day_type | quarter_end | 31 | 9 | 0.222 | 0.667 | 0.1699 | 0.2903 | +0.1308 [+0.0497, +0.2105] |
| day_type | tax_date | 89 | 13 | 0.462 | 1.000 | 0.0904 | 0.1461 | +0.0670 [+0.0483, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## onset_gbm_class_weight+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 9 | 0.346 [0.178, 0.530] | 0.269 | 4.65 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.481] | 0.269 | 4.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.296 (126 of 1873 days never flag) | 172 | 0.393 | 0.320 | 0.0706 | +0.0008 [-0.0028, +0.0040] | -0.0143 [-0.0212, -0.0085] | 0.525 | 0.325 | no |
| 2 | 0.313 (147 of 1872 days never flag) | 157 | 0.353 | 0.312 | 0.0751 | -0.0040 [-0.0095, +0.0008] | -0.0140 [-0.0202, -0.0085] | 0.485 | 0.290 | no |
| 3 | 0.288 (147 of 1871 days never flag) | 125 | 0.239 | 0.264 | 0.0739 | -0.0032 [-0.0085, +0.0013] | -0.0096 [-0.0160, -0.0044] | 0.421 | 0.186 | no |
| 4 | 0.311 (147 of 1870 days never flag) | 146 | 0.341 | 0.322 | 0.0757 | -0.0048 [-0.0112, +0.0003] | -0.0133 [-0.0202, -0.0075] | 0.419 | 0.283 | no |
| 5 | 0.298 (126 of 1869 days never flag) | 166 | 0.326 | 0.271 | 0.0720 | -0.0011 [-0.0056, +0.0030] | -0.0086 [-0.0135, -0.0044] | 0.552 | 0.256 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.457, difference +0.0673 [-0.0236, +0.1891]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1159, ΔBrier vs climatology +0.0136 [+0.0058, +0.0220], realised minus predicted +0.0173 [-0.0224, +0.0633]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.377 | 0.1185 | 0.2720 | -0.0106 [-0.0256, +0.0041] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2041 | 0.0159 | +0.0026 [-0.0048, +0.0097] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0713 | 0.0000 | +0.0078 [+0.0066, +0.0090] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0399 | 0.0200 | +0.0012 [-0.0020, +0.0037] |
| regime | 2025-26 | 249 | 29 | 0.000 | 0.000 | 0.0514 | 0.1165 | -0.0052 [-0.0112, -0.0006] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0567 | 0.0048 | +0.0052 [+0.0039, +0.0065] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1410 | 0.0031 | +0.0071 [+0.0027, +0.0114] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0669 | 0.4146 | -0.0126 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.470 | 0.324 | 0.1366 | 0.2474 | -0.0120 [-0.0241, -0.0006] |
| day_type | month_end | 150 | 17 | 0.412 | 0.438 | 0.1136 | 0.1133 | +0.0091 [-0.0017, +0.0196] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.284 | 0.0876 | 0.0630 | -0.0017 [-0.0045, +0.0007] |
| day_type | quarter_end | 31 | 9 | 0.111 | 0.250 | 0.1115 | 0.2903 | +0.0060 [-0.1023, +0.1222] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.1213 | 0.1461 | +0.0297 [+0.0063, +0.0508] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.6209 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2044 | 0.2213 |

## onset_gbm_class_weight_funding+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 9 | 0.346 [0.179, 0.534] | 0.269 | 4.62 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.483] | 0.269 | 4.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.296 (126 of 1873 days never flag) | 171 | 0.393 | 0.322 | 0.0706 | +0.0009 [-0.0026, +0.0040] | -0.0142 [-0.0209, -0.0083] | 0.531 | 0.326 | no |
| 2 | 0.313 (147 of 1872 days never flag) | 157 | 0.353 | 0.312 | 0.0751 | -0.0040 [-0.0096, +0.0006] | -0.0140 [-0.0203, -0.0088] | 0.485 | 0.290 | no |
| 3 | 0.288 (147 of 1871 days never flag) | 125 | 0.239 | 0.264 | 0.0740 | -0.0033 [-0.0086, +0.0010] | -0.0096 [-0.0157, -0.0045] | 0.414 | 0.186 | no |
| 4 | 0.311 (147 of 1870 days never flag) | 146 | 0.341 | 0.322 | 0.0759 | -0.0050 [-0.0112, +0.0004] | -0.0135 [-0.0202, -0.0078] | 0.413 | 0.283 | no |
| 5 | 0.298 (126 of 1869 days never flag) | 167 | 0.341 | 0.281 | 0.0720 | -0.0010 [-0.0053, +0.0029] | -0.0086 [-0.0135, -0.0042] | 0.548 | 0.271 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.526 (climatology 0.457, difference +0.0691 [-0.0229, +0.1950]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1162, ΔBrier vs climatology +0.0133 [+0.0053, +0.0220], realised minus predicted +0.0168 [-0.0238, +0.0603]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.377 | 0.1185 | 0.2720 | -0.0106 [-0.0248, +0.0034] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2041 | 0.0159 | +0.0026 [-0.0049, +0.0099] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0712 | 0.0000 | +0.0078 [+0.0066, +0.0090] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0398 | 0.0200 | +0.0011 [-0.0022, +0.0037] |
| regime | 2025-26 | 249 | 29 | 0.000 | 0.000 | 0.0545 | 0.1165 | -0.0047 [-0.0111, +0.0001] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0570 | 0.0048 | +0.0052 [+0.0039, +0.0064] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1412 | 0.0031 | +0.0071 [+0.0029, +0.0116] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0762 | 0.4146 | -0.0071 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.470 | 0.324 | 0.1366 | 0.2474 | -0.0122 [-0.0238, -0.0010] |
| day_type | month_end | 150 | 17 | 0.412 | 0.438 | 0.1145 | 0.1133 | +0.0090 [-0.0010, +0.0214] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.286 | 0.0880 | 0.0630 | -0.0015 [-0.0043, +0.0009] |
| day_type | quarter_end | 31 | 9 | 0.111 | 0.250 | 0.1094 | 0.2903 | +0.0012 [-0.1133, +0.1156] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.1215 | 0.1461 | +0.0294 [+0.0061, +0.0502] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.6209 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2044 | 0.2213 |

## onset_gbm_focal+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.266 | 4.58 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.259, 0.600] | 0.231 | 4.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.277 (126 of 1873 days never flag) | 156 | 0.329 | 0.295 | 0.0681 | +0.0033 [+0.0006, +0.0060] | -0.0118 [-0.0178, -0.0061] | 0.650 | 0.265 | no |
| 2 | 0.294 (147 of 1872 days never flag) | 170 | 0.367 | 0.300 | 0.0699 | +0.0011 [-0.0024, +0.0043] | -0.0089 [-0.0137, -0.0044] | 0.659 | 0.298 | no |
| 3 | 0.452 (147 of 1871 days never flag) | 137 | 0.290 | 0.292 | 0.0683 | +0.0023 [-0.0012, +0.0055] | -0.0040 [-0.0087, -0.0001] | 0.617 | 0.234 | no |
| 4 | 0.343 (126 of 1870 days never flag) | 154 | 0.355 | 0.318 | 0.0698 | +0.0010 [-0.0028, +0.0044] | -0.0074 [-0.0128, -0.0029] | 0.617 | 0.294 | no |
| 5 | 0.335 (126 of 1869 days never flag) | 151 | 0.355 | 0.325 | 0.0660 | +0.0049 [+0.0013, +0.0085] | -0.0026 [-0.0067, +0.0015] | 0.736 | 0.296 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.542 (climatology 0.457, difference +0.0848 [-0.0023, +0.1843]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1090, ΔBrier vs climatology +0.0204 [+0.0127, +0.0284], realised minus predicted +0.0103 [-0.0309, +0.0558]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.357 | 0.1505 | 0.2720 | -0.0000 [-0.0109, +0.0112] |
| regime | 2020 | 251 | 4 | 0.250 | 0.036 | 0.2061 | 0.0159 | +0.0009 [-0.0076, +0.0091] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0680 | 0.0000 | +0.0081 [+0.0068, +0.0094] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0377 | 0.0200 | +0.0010 [-0.0020, +0.0035] |
| regime | 2025-26 | 249 | 29 | 0.000 | 0.000 | 0.0517 | 0.1165 | -0.0011 [-0.0046, +0.0023] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0542 | 0.0048 | +0.0053 [+0.0040, +0.0066] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1400 | 0.0031 | +0.0068 [+0.0020, +0.0116] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0752 | 0.4146 | -0.0046 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.393 | 0.303 | 0.1625 | 0.2474 | -0.0027 [-0.0119, +0.0066] |
| day_type | month_end | 150 | 17 | 0.412 | 0.467 | 0.1259 | 0.1133 | +0.0141 [+0.0049, +0.0244] |
| day_type | ordinary | 1603 | 101 | 0.317 | 0.252 | 0.0920 | 0.0630 | +0.0001 [-0.0021, +0.0022] |
| day_type | quarter_end | 31 | 9 | 0.111 | 0.250 | 0.1367 | 0.2903 | +0.0303 [-0.0714, +0.1348] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.1203 | 0.1461 | +0.0340 [+0.0098, +0.0543] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6458 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2158 | 0.2213 |

## onset_logistic+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.700] | 0.269 | 5.77 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.565] | 0.242 | 4.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.302 (126 of 1873 days never flag) | 220 | 0.500 | 0.318 | 0.0623 | +0.0092 [+0.0060, +0.0120] | -0.0059 [-0.0121, -0.0004] | 0.686 | 0.413 | no |
| 2 | 0.297 (147 of 1872 days never flag) | 159 | 0.410 | 0.358 | 0.0636 | +0.0075 [+0.0048, +0.0103] | -0.0025 [-0.0074, +0.0019] | 0.707 | 0.351 | no |
| 3 | 0.295 (147 of 1871 days never flag) | 136 | 0.297 | 0.301 | 0.0646 | +0.0061 [+0.0018, +0.0096] | -0.0003 [-0.0062, +0.0044] | 0.723 | 0.242 | no |
| 4 | 0.301 (147 of 1870 days never flag) | 140 | 0.319 | 0.314 | 0.0638 | +0.0070 [+0.0034, +0.0104] | -0.0015 [-0.0069, +0.0033] | 0.748 | 0.263 | no |
| 5 | 0.314 (147 of 1869 days never flag) | 174 | 0.442 | 0.351 | 0.0629 | +0.0081 [+0.0043, +0.0114] | +0.0005 [-0.0047, +0.0053] | 0.781 | 0.377 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.457, difference +0.1386 [+0.0775, +0.2307]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1047, ΔBrier vs climatology +0.0247 [+0.0182, +0.0316], realised minus predicted +0.0395 [+0.0006, +0.0804]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.363 | 0.1406 | 0.2720 | +0.0046 [-0.0073, +0.0158] |
| regime | 2020 | 251 | 4 | 0.250 | 0.029 | 0.1413 | 0.0159 | +0.0189 [+0.0073, +0.0292] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0492 | 0.0000 | +0.0100 [+0.0085, +0.0116] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0213 | 0.0200 | +0.0041 [+0.0015, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.103 | 0.600 | 0.0578 | 0.1165 | +0.0087 [+0.0018, +0.0174] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0398 | 0.0048 | +0.0070 [+0.0057, +0.0084] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0766 | 0.0031 | +0.0217 [+0.0155, +0.0274] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0669 | 0.4146 | +0.0063 [-0.0148, +0.0237] |
| scarcity_state | 3 | 473 | 117 | 0.581 | 0.319 | 0.1604 | 0.2474 | +0.0056 [-0.0045, +0.0157] |
| day_type | month_end | 150 | 17 | 0.471 | 0.348 | 0.1290 | 0.1133 | +0.0242 [+0.0110, +0.0400] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.275 | 0.0660 | 0.0630 | +0.0048 [+0.0019, +0.0077] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3017 | 0.2903 | +0.0670 [+0.0163, +0.1153] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1152 | 0.1461 | +0.0413 [+0.0262, +0.0582] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.6460 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.1735 | 0.2213 |

## onset_logistic_class_weight+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.227, 0.538] | 0.231 | 2.92 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.000, 0.227] | 0.077 | 0.35 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.433 (126 of 1873 days never flag) | 108 | 0.229 | 0.296 | 0.0658 | +0.0056 [-0.0073, +0.0166] | -0.0094 [-0.0209, +0.0006] | 0.826 | 0.185 | no |
| 2 | 0.412 (147 of 1872 days never flag) | 22 | 0.086 | 0.545 | 0.0776 | -0.0065 [-0.0236, +0.0071] | -0.0165 [-0.0331, -0.0029] | 0.803 | 0.081 | no |
| 3 | 0.619 (147 of 1871 days never flag) | 13 | 0.036 | 0.385 | 0.0760 | -0.0053 [-0.0239, +0.0100] | -0.0116 [-0.0295, +0.0039] | 0.866 | 0.032 | no |
| 4 | 0.526 (147 of 1870 days never flag) | 7 | 0.029 | 0.571 | 0.0721 | -0.0013 [-0.0190, +0.0137] | -0.0098 [-0.0276, +0.0049] | 0.859 | 0.027 | no |
| 5 | 0.663 (147 of 1869 days never flag) | 16 | 0.051 | 0.438 | 0.0712 | -0.0003 [-0.0198, +0.0154] | -0.0078 [-0.0270, +0.0076] | 0.859 | 0.046 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.669 (climatology 0.457, difference +0.2118 [+0.0766, +0.3508]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0235, +0.0676], realised minus predicted -0.0271 [-0.0578, +0.0038]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.245 | 0.278 | 0.2986 | 0.2720 | -0.0222 [-0.0825, +0.0282] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1368 | 0.0159 | +0.0194 [+0.0074, +0.0300] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0374 | 0.0000 | +0.0116 [+0.0100, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0211 | 0.0200 | +0.0051 [+0.0027, +0.0080] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.429 | 0.1206 | 0.1165 | +0.0162 [-0.0038, +0.0409] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0373 | 0.0048 | +0.0069 [+0.0051, +0.0088] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0719 | 0.0031 | +0.0218 [+0.0152, +0.0283] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1363 | 0.4146 | 0.0620 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.256 | 0.294 | 0.3004 | 0.2474 | -0.0131 [-0.0616, +0.0284] |
| day_type | month_end | 150 | 17 | 0.294 | 0.556 | 0.1462 | 0.1133 | +0.0251 [+0.0073, +0.0457] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.200 | 0.1024 | 0.0630 | -0.0007 [-0.0143, +0.0102] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.500 | 0.3764 | 0.2903 | +0.0954 [+0.0558, +0.1377] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.667 | 0.1333 | 0.1461 | +0.0562 [+0.0270, +0.0916] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.6076 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1780 | 0.2213 |

## onset_logistic_class_weight_funding+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.273, 0.594] | 0.231 | 2.85 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 4 | 0.154 [0.045, 0.281] | 0.115 | 0.69 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.433 (126 of 1873 days never flag) | 108 | 0.243 | 0.315 | 0.0649 | +0.0065 [-0.0066, +0.0171] | -0.0086 [-0.0206, +0.0013] | 0.832 | 0.200 | no |
| 2 | 0.412 (147 of 1872 days never flag) | 27 | 0.094 | 0.481 | 0.0761 | -0.0051 [-0.0225, +0.0096] | -0.0151 [-0.0312, -0.0009] | 0.822 | 0.085 | no |
| 3 | 0.619 (147 of 1871 days never flag) | 18 | 0.058 | 0.444 | 0.0751 | -0.0044 [-0.0232, +0.0111] | -0.0107 [-0.0286, +0.0038] | 0.873 | 0.052 | no |
| 4 | 0.526 (147 of 1870 days never flag) | 14 | 0.058 | 0.571 | 0.0709 | -0.0000 [-0.0174, +0.0147] | -0.0085 [-0.0259, +0.0065] | 0.871 | 0.055 | no |
| 5 | 0.663 (147 of 1869 days never flag) | 36 | 0.130 | 0.500 | 0.0688 | +0.0022 [-0.0175, +0.0199] | -0.0054 [-0.0235, +0.0115] | 0.879 | 0.120 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2494 [+0.0838, +0.4137]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0800, ΔBrier vs climatology +0.0494 [+0.0290, +0.0736], realised minus predicted -0.0208 [-0.0493, +0.0106]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.245 | 0.278 | 0.2986 | 0.2720 | -0.0222 [-0.0818, +0.0297] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1310 | 0.0159 | +0.0202 [+0.0080, +0.0316] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0226 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0193 | 0.0200 | +0.0051 [+0.0022, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.571 | 0.1182 | 0.1165 | +0.0182 [-0.0047, +0.0468] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0271 | 0.0048 | +0.0078 [+0.0058, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0639 | 0.0031 | +0.0229 [+0.0157, +0.0295] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1314 | 0.4146 | 0.0614 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.265 | 0.307 | 0.2999 | 0.2474 | -0.0123 [-0.0620, +0.0294] |
| day_type | month_end | 150 | 17 | 0.353 | 0.600 | 0.1428 | 0.1133 | +0.0310 [+0.0103, +0.0558] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.225 | 0.0952 | 0.0630 | -0.0002 [-0.0147, +0.0108] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.500 | 0.3529 | 0.2903 | +0.0936 [+0.0541, +0.1289] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.625 | 0.1232 | 0.1461 | +0.0560 [+0.0283, +0.0916] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.6076 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1780 | 0.2213 |

## onset_logistic_net+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.323, 0.680] | 0.269 | 5.27 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.567] | 0.269 | 4.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.357 (126 of 1873 days never flag) | 171 | 0.393 | 0.322 | 0.0635 | +0.0079 [+0.0045, +0.0112] | -0.0072 [-0.0134, -0.0012] | 0.679 | 0.326 | no |
| 2 | 0.289 (126 of 1872 days never flag) | 197 | 0.432 | 0.305 | 0.0649 | +0.0062 [+0.0034, +0.0089] | -0.0038 [-0.0088, +0.0008] | 0.691 | 0.353 | no |
| 3 | 0.312 (147 of 1871 days never flag) | 144 | 0.246 | 0.236 | 0.0654 | +0.0053 [+0.0011, +0.0091] | -0.0010 [-0.0070, +0.0043] | 0.737 | 0.183 | no |
| 4 | 0.37 (147 of 1870 days never flag) | 122 | 0.246 | 0.279 | 0.0682 | +0.0026 [-0.0019, +0.0066] | -0.0058 [-0.0114, -0.0008] | 0.637 | 0.196 | no |
| 5 | 0.285 (147 of 1869 days never flag) | 190 | 0.500 | 0.363 | 0.0622 | +0.0088 [+0.0051, +0.0121] | +0.0012 [-0.0039, +0.0060] | 0.792 | 0.430 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.603 (climatology 0.457, difference +0.1461 [+0.0899, +0.2311]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0220 [+0.0159, +0.0284], realised minus predicted +0.0339 [-0.0057, +0.0747]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.380 | 0.1417 | 0.2720 | +0.0042 [-0.0072, +0.0156] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1559 | 0.0159 | +0.0107 [-0.0056, +0.0255] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0515 | 0.0000 | +0.0100 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0230 | 0.0200 | +0.0036 [+0.0009, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0582 | 0.1165 | +0.0085 [+0.0024, +0.0160] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0421 | 0.0048 | +0.0069 [+0.0056, +0.0082] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0813 | 0.0031 | +0.0211 [+0.0156, +0.0270] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.500 | 0.0745 | 0.4146 | 0.0049 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.453 | 0.319 | 0.1651 | 0.2474 | +0.0013 [-0.0106, +0.0130] |
| day_type | month_end | 150 | 17 | 0.471 | 0.381 | 0.1323 | 0.1133 | +0.0245 [+0.0110, +0.0390] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.260 | 0.0698 | 0.0630 | +0.0035 [+0.0003, +0.0065] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2939 | 0.2903 | +0.0575 [+0.0055, +0.1067] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1141 | 0.1461 | +0.0425 [+0.0278, +0.0578] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.5799 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1682 | 0.2213 |

## onset_logistic_policy+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.478, 0.818] | 0.297 | 6.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.688] | 0.269 | 4.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.255 (126 of 1873 days never flag) | 243 | 0.600 | 0.346 | 0.0573 | +0.0141 [+0.0108, +0.0179] | -0.0010 [-0.0063, +0.0038] | 0.776 | 0.508 | no |
| 2 | 0.267 (126 of 1872 days never flag) | 225 | 0.475 | 0.293 | 0.0604 | +0.0106 [+0.0077, +0.0138] | +0.0006 [-0.0035, +0.0049] | 0.765 | 0.383 | no |
| 3 | 0.245 (147 of 1871 days never flag) | 138 | 0.341 | 0.341 | 0.0607 | +0.0100 [+0.0055, +0.0139] | +0.0036 [-0.0019, +0.0084] | 0.789 | 0.288 | no |
| 4 | 0.289 (147 of 1870 days never flag) | 168 | 0.399 | 0.327 | 0.0603 | +0.0105 [+0.0067, +0.0144] | +0.0021 [-0.0028, +0.0069] | 0.791 | 0.333 | no |
| 5 | 0.243 (147 of 1869 days never flag) | 181 | 0.413 | 0.315 | 0.0608 | +0.0101 [+0.0061, +0.0139] | +0.0026 [-0.0019, +0.0070] | 0.798 | 0.341 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.457, difference +0.1799 [+0.0695, +0.3101]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0928, ΔBrier vs climatology +0.0367 [+0.0270, +0.0473], realised minus predicted +0.0362 [+0.0026, +0.0726]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.361 | 0.1424 | 0.2720 | +0.0145 [+0.0049, +0.0246] |
| regime | 2020 | 251 | 4 | 0.750 | 0.111 | 0.1036 | 0.0159 | +0.0280 [+0.0186, +0.0371] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0405 | 0.0000 | +0.0100 [+0.0080, +0.0120] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0207 | 0.0200 | +0.0046 [+0.0013, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.556 | 0.0723 | 0.1165 | +0.0214 [+0.0059, +0.0411] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0320 | 0.0048 | +0.0078 [+0.0064, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0569 | 0.0031 | +0.0232 [+0.0150, +0.0312] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0988 | 0.4146 | 0.0482 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.343 | 0.1632 | 0.2474 | +0.0187 [+0.0088, +0.0297] |
| day_type | month_end | 150 | 17 | 0.647 | 0.423 | 0.1263 | 0.1133 | +0.0343 [+0.0174, +0.0539] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.305 | 0.0588 | 0.0630 | +0.0093 [+0.0066, +0.0123] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3191 | 0.2903 | +0.0695 [+0.0099, +0.1262] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1089 | 0.1461 | +0.0475 [+0.0329, +0.0648] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.5832 | 0.4822 |
| mar-2020 | 10 | 3 | 1.000 | 1.000 | 0.1666 | 0.2213 |

## published_v1 (baseline): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.720] | 0.269 | 5.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.682] | 0.269 | 5.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.246 (126 of 1873 days never flag) | 242 | 0.671 | 0.388 | 0.0496 | +0.0219 [+0.0139, +0.0309] | +0.0068 [+0.0022, +0.0122] | 0.898 | 0.586 | no |
| 2 | 0.269 (126 of 1872 days never flag) | 233 | 0.626 | 0.373 | 0.0530 | +0.0180 [+0.0112, +0.0255] | +0.0080 [+0.0029, +0.0135] | 0.881 | 0.542 | no |
| 3 | 0.277 (126 of 1871 days never flag) | 188 | 0.507 | 0.372 | 0.0541 | +0.0166 [+0.0099, +0.0244] | +0.0103 [+0.0052, +0.0164] | 0.887 | 0.439 | no |
| 4 | 0.283 (126 of 1870 days never flag) | 229 | 0.580 | 0.349 | 0.0567 | +0.0141 [+0.0078, +0.0213] | +0.0057 [+0.0011, +0.0112] | 0.871 | 0.494 | no |
| 5 | 0.284 (126 of 1869 days never flag) | 227 | 0.601 | 0.366 | 0.0574 | +0.0136 [+0.0066, +0.0208] | +0.0060 [+0.0007, +0.0117] | 0.876 | 0.518 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.697 (climatology 0.457, difference +0.2403 [+0.0957, +0.3431]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0302, +0.0598], realised minus predicted +0.0422 [+0.0127, +0.0756]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.385 | 0.2612 | 0.2720 | +0.0460 [+0.0127, +0.0833] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0935 | 0.0159 | +0.0328 [+0.0266, +0.0391] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0320 | 0.0000 | +0.0127 [+0.0111, +0.0144] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0255 | 0.0200 | +0.0010 [-0.0043, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.436 | 0.1116 | 0.1165 | +0.0229 [-0.0053, +0.0574] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0287 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0638 | 0.0031 | +0.0250 [+0.0189, +0.0303] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.667 | 0.1980 | 0.4146 | +0.0840 [-0.0308, +0.2028] |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.379 | 0.2559 | 0.2474 | +0.0446 [+0.0172, +0.0763] |
| day_type | month_end | 150 | 17 | 0.824 | 0.609 | 0.1021 | 0.1133 | +0.0421 [+0.0202, +0.0713] |
| day_type | ordinary | 1603 | 101 | 0.683 | 0.342 | 0.0934 | 0.0630 | +0.0169 [+0.0088, +0.0259] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1348 | 0.2903 | +0.0922 [+0.0137, +0.1746] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1164 | 0.1461 | +0.0534 [+0.0285, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1018 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2480 | 0.2213 |

## published_v1_blend_equal (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.312, 0.680] | 0.269 | 5.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.679] | 0.269 | 5.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.303 (126 of 1873 days never flag) | 219 | 0.657 | 0.420 | 0.0489 | +0.0225 [+0.0144, +0.0309] | +0.0074 [+0.0026, +0.0126] | 0.903 | 0.584 | no |
| 2 | 0.269 (126 of 1872 days never flag) | 233 | 0.626 | 0.373 | 0.0530 | +0.0180 [+0.0113, +0.0255] | +0.0080 [+0.0031, +0.0138] | 0.881 | 0.542 | no |
| 3 | 0.277 (126 of 1871 days never flag) | 188 | 0.507 | 0.372 | 0.0541 | +0.0166 [+0.0097, +0.0239] | +0.0103 [+0.0051, +0.0161] | 0.887 | 0.439 | no |
| 4 | 0.283 (126 of 1870 days never flag) | 229 | 0.580 | 0.349 | 0.0567 | +0.0141 [+0.0077, +0.0211] | +0.0057 [+0.0010, +0.0111] | 0.871 | 0.494 | no |
| 5 | 0.284 (126 of 1869 days never flag) | 227 | 0.601 | 0.366 | 0.0574 | +0.0136 [+0.0071, +0.0214] | +0.0060 [+0.0009, +0.0122] | 0.876 | 0.518 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.697 (climatology 0.457, difference +0.2403 [+0.0953, +0.3402]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0826, ΔBrier vs climatology +0.0469 [+0.0328, +0.0627], realised minus predicted +0.0383 [+0.0086, +0.0707]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2709 | 0.2720 | +0.0443 [+0.0115, +0.0791] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0917 | 0.0159 | +0.0334 [+0.0271, +0.0396] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0279 | 0.0000 | +0.0130 [+0.0114, +0.0147] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0211 | 0.0200 | +0.0019 [-0.0020, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.472 | 0.1012 | 0.1165 | +0.0281 [-0.0004, +0.0637] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0245 | 0.0048 | +0.0085 [+0.0069, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0563 | 0.0031 | +0.0263 [+0.0203, +0.0318] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.700 | 0.1590 | 0.4146 | +0.0888 [-0.0188, +0.1958] |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.407 | 0.2660 | 0.2474 | +0.0449 [+0.0170, +0.0751] |
| day_type | month_end | 150 | 17 | 0.824 | 0.667 | 0.1071 | 0.1133 | +0.0476 [+0.0254, +0.0761] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.364 | 0.0912 | 0.0630 | +0.0168 [+0.0086, +0.0254] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.750 | 0.1245 | 0.2903 | +0.0865 [+0.0041, +0.1748] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1104 | 0.1461 | +0.0605 [+0.0377, +0.0852] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1324 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2298 | 0.2213 |

## published_v1_calendar_switch (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.762] | 0.269 | 5.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.677] | 0.269 | 5.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.262 (126 of 1873 days never flag) | 244 | 0.693 | 0.398 | 0.0484 | +0.0230 [+0.0149, +0.0319] | +0.0079 [+0.0029, +0.0135] | 0.896 | 0.608 | no |
| 2 | 0.269 (126 of 1872 days never flag) | 233 | 0.626 | 0.373 | 0.0530 | +0.0180 [+0.0114, +0.0257] | +0.0080 [+0.0031, +0.0140] | 0.881 | 0.542 | no |
| 3 | 0.277 (126 of 1871 days never flag) | 188 | 0.507 | 0.372 | 0.0541 | +0.0166 [+0.0099, +0.0242] | +0.0103 [+0.0050, +0.0166] | 0.887 | 0.439 | no |
| 4 | 0.283 (126 of 1870 days never flag) | 229 | 0.580 | 0.349 | 0.0567 | +0.0141 [+0.0079, +0.0211] | +0.0057 [+0.0009, +0.0111] | 0.871 | 0.494 | no |
| 5 | 0.284 (126 of 1869 days never flag) | 227 | 0.601 | 0.366 | 0.0574 | +0.0136 [+0.0067, +0.0206] | +0.0060 [+0.0008, +0.0118] | 0.876 | 0.518 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.697 (climatology 0.457, difference +0.2403 [+0.1038, +0.3421]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0823, ΔBrier vs climatology +0.0472 [+0.0336, +0.0626], realised minus predicted +0.0391 [+0.0091, +0.0719]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.397 | 0.2755 | 0.2720 | +0.0518 [+0.0188, +0.0878] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0905 | 0.0159 | +0.0318 [+0.0242, +0.0389] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0302 | 0.0000 | +0.0128 [+0.0111, +0.0146] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0226 | 0.0200 | +0.0005 [-0.0053, +0.0049] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.462 | 0.1084 | 0.1165 | +0.0239 [-0.0010, +0.0557] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0268 | 0.0048 | +0.0080 [+0.0060, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0579 | 0.0031 | +0.0259 [+0.0195, +0.0319] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.636 | 0.1835 | 0.4146 | 0.0713 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.769 | 0.391 | 0.2689 | 0.2474 | +0.0497 [+0.0213, +0.0798] |
| day_type | month_end | 150 | 17 | 0.882 | 0.600 | 0.1131 | 0.1133 | +0.0496 [+0.0278, +0.0768] |
| day_type | ordinary | 1603 | 101 | 0.693 | 0.348 | 0.0944 | 0.0630 | +0.0172 [+0.0086, +0.0268] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.750 | 0.1142 | 0.2903 | +0.0785 [-0.0047, +0.1667] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1043 | 0.1461 | +0.0634 [+0.0412, +0.0885] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1570 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2696 | 0.2213 |

## published_v1_nowcast (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.269 | 5.46 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.296, 0.630] | 0.269 | 5.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.245 (126 of 1873 days never flag) | 232 | 0.643 | 0.388 | 0.0493 | +0.0221 [+0.0142, +0.0308] | +0.0070 [+0.0024, +0.0123] | 0.895 | 0.561 | no |
| 2 | 0.268 (126 of 1872 days never flag) | 226 | 0.626 | 0.385 | 0.0518 | +0.0193 [+0.0123, +0.0269] | +0.0093 [+0.0040, +0.0155] | 0.884 | 0.546 | no |
| 3 | 0.26 (147 of 1871 days never flag) | 191 | 0.551 | 0.398 | 0.0534 | +0.0173 [+0.0104, +0.0252] | +0.0110 [+0.0057, +0.0174] | 0.887 | 0.484 | no |
| 4 | 0.27 (126 of 1870 days never flag) | 218 | 0.558 | 0.353 | 0.0558 | +0.0151 [+0.0082, +0.0223] | +0.0066 [+0.0015, +0.0125] | 0.876 | 0.477 | no |
| 5 | 0.283 (126 of 1869 days never flag) | 218 | 0.587 | 0.372 | 0.0562 | +0.0148 [+0.0078, +0.0218] | +0.0072 [+0.0019, +0.0134] | 0.879 | 0.508 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.677 (climatology 0.457, difference +0.2200 [+0.0939, +0.3287]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0312, +0.0590], realised minus predicted +0.0440 [+0.0149, +0.0750]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.380 | 0.2615 | 0.2720 | +0.0449 [+0.0115, +0.0809] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0985 | 0.0159 | +0.0317 [+0.0251, +0.0383] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0329 | 0.0000 | +0.0126 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0260 | 0.0200 | +0.0012 [-0.0038, +0.0048] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.459 | 0.1080 | 0.1165 | +0.0275 [-0.0029, +0.0657] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0290 | 0.0048 | +0.0081 [+0.0063, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0651 | 0.0031 | +0.0246 [+0.0185, +0.0302] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.667 | 0.2038 | 0.4146 | 0.1010 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.379 | 0.2566 | 0.2474 | +0.0442 [+0.0170, +0.0746] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1051 | 0.1133 | +0.0443 [+0.0212, +0.0739] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.342 | 0.0940 | 0.0630 | +0.0170 [+0.0090, +0.0262] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1335 | 0.2903 | +0.0895 [+0.0062, +0.1759] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.1151 | 0.1461 | +0.0522 [+0.0268, +0.0783] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1299 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2474 | 0.2213 |

## published_v1_nowcast_substituted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.200, 0.567] | 0.281 | 5.96 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.556] | 0.278 | 5.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.287 (126 of 1873 days never flag) | 236 | 0.600 | 0.356 | 0.0540 | +0.0174 [+0.0103, +0.0257] | +0.0024 [-0.0024, +0.0076] | 0.879 | 0.512 | no |
| 2 | 0.322 (126 of 1872 days never flag) | 216 | 0.540 | 0.347 | 0.0563 | +0.0148 [+0.0086, +0.0212] | +0.0048 [-0.0002, +0.0103] | 0.869 | 0.458 | no |
| 3 | 0.307 (126 of 1871 days never flag) | 204 | 0.486 | 0.328 | 0.0588 | +0.0119 [+0.0068, +0.0180] | +0.0056 [+0.0011, +0.0107] | 0.855 | 0.406 | no |
| 4 | 0.454 (126 of 1870 days never flag) | 224 | 0.500 | 0.308 | 0.0601 | +0.0107 [+0.0053, +0.0167] | +0.0023 [-0.0023, +0.0073] | 0.846 | 0.411 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 210 | 0.493 | 0.324 | 0.0596 | +0.0113 [+0.0056, +0.0174] | +0.0038 [-0.0009, +0.0092] | 0.849 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.633 (climatology 0.457, difference +0.1755 [+0.0567, +0.2631]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0933, ΔBrier vs climatology +0.0362 [+0.0251, +0.0486], realised minus predicted +0.0425 [+0.0084, +0.0781]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.370 | 0.2614 | 0.2720 | +0.0405 [+0.0087, +0.0763] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1474 | 0.0159 | +0.0126 [+0.0021, +0.0215] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0265 | 0.0000 | +0.0130 [+0.0114, +0.0149] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0185 | 0.0200 | +0.0019 [-0.0020, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0835 | 0.1165 | +0.0165 [-0.0015, +0.0386] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0241 | 0.0048 | +0.0084 [+0.0068, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0900 | 0.0031 | +0.0180 [+0.0132, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.667 | 0.1384 | 0.4146 | 0.0497 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.349 | 0.2548 | 0.2474 | +0.0340 [+0.0076, +0.0639] |
| day_type | month_end | 150 | 17 | 0.765 | 0.591 | 0.0974 | 0.1133 | +0.0260 [+0.0107, +0.0430] |
| day_type | ordinary | 1603 | 101 | 0.614 | 0.313 | 0.0945 | 0.0630 | +0.0139 [+0.0062, +0.0230] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.1339 | 0.2903 | +0.0698 [-0.0168, +0.1592] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.545 | 0.1115 | 0.1461 | +0.0485 [+0.0284, +0.0722] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2716 | 0.2213 |

## published_v1_predicted_turn_switch (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.773] | 0.269 | 5.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.692] | 0.269 | 5.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.262 (126 of 1873 days never flag) | 244 | 0.679 | 0.389 | 0.0489 | +0.0225 [+0.0147, +0.0313] | +0.0074 [+0.0024, +0.0131] | 0.900 | 0.593 | no |
| 2 | 0.269 (126 of 1872 days never flag) | 233 | 0.626 | 0.373 | 0.0530 | +0.0180 [+0.0113, +0.0252] | +0.0080 [+0.0032, +0.0137] | 0.881 | 0.542 | no |
| 3 | 0.277 (126 of 1871 days never flag) | 188 | 0.507 | 0.372 | 0.0541 | +0.0166 [+0.0100, +0.0240] | +0.0103 [+0.0052, +0.0163] | 0.887 | 0.439 | no |
| 4 | 0.283 (126 of 1870 days never flag) | 229 | 0.580 | 0.349 | 0.0567 | +0.0141 [+0.0079, +0.0212] | +0.0057 [+0.0011, +0.0108] | 0.871 | 0.494 | no |
| 5 | 0.284 (126 of 1869 days never flag) | 227 | 0.601 | 0.366 | 0.0574 | +0.0136 [+0.0067, +0.0206] | +0.0060 [+0.0008, +0.0119] | 0.876 | 0.518 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.697 (climatology 0.457, difference +0.2403 [+0.1001, +0.3424]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0447 [+0.0307, +0.0605], realised minus predicted +0.0411 [+0.0102, +0.0735]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.391 | 0.2661 | 0.2720 | +0.0502 [+0.0163, +0.0851] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0935 | 0.0159 | +0.0324 [+0.0257, +0.0389] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0320 | 0.0000 | +0.0127 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0249 | 0.0200 | +0.0000 [-0.0060, +0.0048] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.436 | 0.1110 | 0.1165 | +0.0228 [-0.0057, +0.0563] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0285 | 0.0048 | +0.0078 [+0.0058, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0630 | 0.0031 | +0.0252 [+0.0187, +0.0306] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.667 | 0.1998 | 0.4146 | +0.0865 [-0.0311, +0.1983] |
| scarcity_state | 3 | 473 | 117 | 0.744 | 0.383 | 0.2599 | 0.2474 | +0.0473 [+0.0194, +0.0764] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1085 | 0.1133 | +0.0488 [+0.0261, +0.0763] |
| day_type | ordinary | 1603 | 101 | 0.693 | 0.345 | 0.0940 | 0.0630 | +0.0173 [+0.0089, +0.0267] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1211 | 0.2903 | +0.0779 [-0.0050, +0.1655] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1164 | 0.1461 | +0.0534 [+0.0272, +0.0790] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1018 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2480 | 0.2213 |

## rare_gbm_balanced_bootstrap+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 7 | 0.269 [0.105, 0.438] | 0.192 | 2.19 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 6 | 0.231 [0.080, 0.394] | 0.192 | 2.19 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.562 (126 of 1873 days never flag) | 65 | 0.214 | 0.462 | 0.0625 | +0.0089 [-0.0020, +0.0189] | -0.0062 [-0.0156, +0.0020] | 0.853 | 0.194 | no |
| 2 | 0.694 (147 of 1872 days never flag) | 44 | 0.122 | 0.386 | 0.0727 | -0.0016 [-0.0147, +0.0095] | -0.0116 [-0.0233, -0.0016] | 0.800 | 0.107 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 15 | 0.065 | 0.600 | 0.0676 | +0.0031 [-0.0110, +0.0154] | -0.0032 [-0.0169, +0.0084] | 0.866 | 0.062 | no |
| 4 | 0.517 (126 of 1870 days never flag) | 69 | 0.167 | 0.333 | 0.0723 | -0.0015 [-0.0126, +0.0088] | -0.0099 [-0.0203, -0.0004] | 0.823 | 0.140 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 87 | 0.217 | 0.345 | 0.0724 | -0.0015 [-0.0129, +0.0091] | -0.0090 [-0.0200, +0.0004] | 0.807 | 0.184 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.548 (climatology 0.457, difference +0.0911 [-0.0501, +0.1945]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0844, ΔBrier vs climatology +0.0451 [+0.0270, +0.0645], realised minus predicted +0.0016 [-0.0283, +0.0352]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.235 | 0.407 | 0.3483 | 0.2720 | -0.0221 [-0.0739, +0.0258] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0961 | 0.0159 | +0.0314 [+0.0235, +0.0393] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0117 | 0.0000 | +0.0136 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0098 | 0.0200 | +0.0018 [-0.0023, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.207 | 1.000 | 0.0584 | 0.1165 | +0.0255 [+0.0079, +0.0479] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0113 | 0.0048 | +0.0088 [+0.0071, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0417 | 0.0031 | +0.0273 [+0.0213, +0.0331] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1392 | 0.4146 | +0.0811 [+0.0110, +0.1858] |
| scarcity_state | 3 | 473 | 117 | 0.248 | 0.453 | 0.3162 | 0.2474 | -0.0100 [-0.0517, +0.0290] |
| day_type | month_end | 150 | 17 | 0.412 | 0.875 | 0.1083 | 0.1133 | +0.0380 [+0.0172, +0.0604] |
| day_type | ordinary | 1603 | 101 | 0.188 | 0.365 | 0.0941 | 0.0630 | +0.0016 [-0.0109, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1692 | 0.2903 | +0.1263 [+0.0343, +0.2181] |
| day_type | tax_date | 89 | 13 | 0.077 | 0.500 | 0.0926 | 0.1461 | +0.0503 [+0.0322, +0.0691] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.000 | – | 0.4124 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1941 | 0.2213 |

## rare_gbm_balanced_bootstrap_policy+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.636] | 0.231 | 2.92 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.545] | 0.231 | 2.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.52 (126 of 1873 days never flag) | 74 | 0.179 | 0.338 | 0.0638 | +0.0076 [-0.0037, +0.0175] | -0.0075 [-0.0174, +0.0005] | 0.835 | 0.150 | no |
| 2 | 0.458 (147 of 1872 days never flag) | 42 | 0.108 | 0.357 | 0.0707 | +0.0003 [-0.0118, +0.0113] | -0.0097 [-0.0208, +0.0006] | 0.784 | 0.092 | no |
| 3 | 0.352 (147 of 1871 days never flag) | 64 | 0.225 | 0.484 | 0.0647 | +0.0059 [-0.0042, +0.0152] | -0.0004 [-0.0098, +0.0080] | 0.860 | 0.206 | no |
| 4 | 0.545 (147 of 1870 days never flag) | 58 | 0.167 | 0.397 | 0.0684 | +0.0024 [-0.0062, +0.0114] | -0.0061 [-0.0147, +0.0025] | 0.799 | 0.146 | no |
| 5 | 0.388 (126 of 1869 days never flag) | 103 | 0.196 | 0.262 | 0.0696 | +0.0013 [-0.0089, +0.0103] | -0.0062 [-0.0153, +0.0020] | 0.810 | 0.152 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.529 (climatology 0.457, difference +0.0723 [-0.0922, +0.1864]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0874, ΔBrier vs climatology +0.0421 [+0.0266, +0.0617], realised minus predicted +0.0031 [-0.0277, +0.0368]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.206 | 0.318 | 0.3281 | 0.2720 | -0.0304 [-0.0795, +0.0140] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0980 | 0.0159 | +0.0307 [+0.0221, +0.0382] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0134 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0144 | 0.0200 | +0.0039 [+0.0002, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.500 | 0.0796 | 0.1165 | +0.0274 [+0.0042, +0.0555] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0139 | 0.0048 | +0.0091 [+0.0075, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0457 | 0.0031 | +0.0269 [+0.0206, +0.0325] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1418 | 0.4146 | 0.0952 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.205 | 0.329 | 0.3088 | 0.2474 | -0.0165 [-0.0571, +0.0206] |
| day_type | month_end | 150 | 17 | 0.294 | 0.625 | 0.1130 | 0.1133 | +0.0349 [+0.0153, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.274 | 0.0943 | 0.0630 | +0.0016 [-0.0112, +0.0127] |
| day_type | quarter_end | 31 | 9 | 0.222 | 1.000 | 0.1767 | 0.2903 | +0.1161 [+0.0356, +0.1923] |
| day_type | tax_date | 89 | 13 | 0.077 | 0.500 | 0.0843 | 0.1461 | +0.0320 [+0.0099, +0.0524] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.000 | – | 0.4745 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2032 | 0.2213 |

## rare_gbm_class_weight+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.650] | 0.269 | 5.12 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.607] | 0.269 | 5.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.373 (147 of 1873 days never flag) | 109 | 0.393 | 0.505 | 0.0615 | +0.0099 [-0.0003, +0.0196] | -0.0052 [-0.0137, +0.0022] | 0.807 | 0.362 | no |
| 2 | 0.67 (189 of 1872 days never flag) | 10 | 0.050 | 0.700 | 0.0723 | -0.0013 [-0.0160, +0.0113] | -0.0113 [-0.0251, +0.0005] | 0.796 | 0.049 | no |
| 3 | 0.763 (147 of 1871 days never flag) | 16 | 0.058 | 0.500 | 0.0712 | -0.0005 [-0.0132, +0.0108] | -0.0068 [-0.0190, +0.0037] | 0.800 | 0.053 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 84 | 0.268 | 0.440 | 0.0705 | +0.0004 [-0.0094, +0.0090] | -0.0081 [-0.0171, -0.0002] | 0.706 | 0.241 | no |
| 5 | 0.385 (126 of 1869 days never flag) | 205 | 0.522 | 0.351 | 0.0678 | +0.0031 [-0.0053, +0.0118] | -0.0045 [-0.0119, +0.0031] | 0.741 | 0.445 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.549 (climatology 0.457, difference +0.0923 [+0.0006, +0.1708]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0925, ΔBrier vs climatology +0.0370 [+0.0180, +0.0565], realised minus predicted +0.0030 [-0.0299, +0.0370]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.500 | 0.2909 | 0.2720 | -0.0121 [-0.0611, +0.0361] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1065 | 0.0159 | +0.0299 [+0.0212, +0.0385] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0172 | 0.0000 | +0.0134 [+0.0117, +0.0153] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0138 | 0.0200 | +0.0017 [-0.0026, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.625 | 0.0596 | 0.1165 | +0.0205 [+0.0059, +0.0387] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0160 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0507 | 0.0031 | +0.0270 [+0.0214, +0.0327] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0771 | 0.4146 | 0.0320 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.462 | 0.500 | 0.2765 | 0.2474 | -0.0011 [-0.0405, +0.0379] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.0998 | 0.1133 | +0.0359 [+0.0153, +0.0561] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.437 | 0.0864 | 0.0630 | +0.0040 [-0.0074, +0.0146] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.1425 | 0.2903 | +0.1071 [+0.0197, +0.1934] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.1012 | 0.1461 | +0.0382 [+0.0138, +0.0582] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.3424 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1912 | 0.2213 |

## rare_gbm_focal+recalibrated (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.682] | 0.231 | 4.15 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.207, 0.571] | 0.231 | 4.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.358 (147 of 1873 days never flag) | 126 | 0.443 | 0.492 | 0.0561 | +0.0153 [+0.0079, +0.0232] | +0.0002 [-0.0065, +0.0066] | 0.867 | 0.406 | no |
| 2 | 0.437 (168 of 1872 days never flag) | 49 | 0.129 | 0.367 | 0.0618 | +0.0092 [+0.0006, +0.0173] | -0.0008 [-0.0084, +0.0068] | 0.833 | 0.112 | no |
| 3 | 0.42 (147 of 1871 days never flag) | 39 | 0.080 | 0.282 | 0.0586 | +0.0121 [+0.0049, +0.0198] | +0.0058 [-0.0012, +0.0134] | 0.845 | 0.064 | no |
| 4 | 0.409 (126 of 1870 days never flag) | 148 | 0.391 | 0.365 | 0.0624 | +0.0085 [+0.0024, +0.0150] | +0.0000 [-0.0060, +0.0060] | 0.834 | 0.337 | no |
| 5 | 0.433 (126 of 1869 days never flag) | 178 | 0.507 | 0.393 | 0.0634 | +0.0075 [+0.0008, +0.0150] | -0.0000 [-0.0066, +0.0071] | 0.777 | 0.445 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.556 (climatology 0.457, difference +0.0992 [-0.0150, +0.1823]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0447 [+0.0293, +0.0618], realised minus predicted +0.0148 [-0.0156, +0.0494]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.487 | 0.3092 | 0.2720 | +0.0199 [-0.0172, +0.0584] |
| regime | 2020 | 251 | 4 | 0.500 | 0.400 | 0.1049 | 0.0159 | +0.0306 [+0.0221, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0153 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0111 | 0.0200 | +0.0015 [-0.0033, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.667 | 0.0439 | 0.1165 | +0.0122 [+0.0011, +0.0279] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0136 | 0.0048 | +0.0087 [+0.0069, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0473 | 0.0031 | +0.0272 [+0.0216, +0.0325] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0479 | 0.4146 | -0.0024 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.530 | 0.492 | 0.2877 | 0.2474 | +0.0232 [-0.0064, +0.0540] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.0986 | 0.1133 | +0.0378 [+0.0208, +0.0558] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.436 | 0.0866 | 0.0630 | +0.0093 [+0.0009, +0.0179] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1359 | 0.2903 | +0.1064 [+0.0236, +0.1946] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.1085 | 0.1461 | +0.0541 [+0.0390, +0.0702] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.3026 | 0.4822 |
| mar-2020 | 10 | 3 | 0.667 | 0.667 | 0.1842 | 0.2213 |

## rare_logistic_balanced_bootstrap+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 4 | 0.154 [0.043, 0.273] | 0.115 | 0.96 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.029, 0.226] | 0.115 | 0.96 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.8 (147 of 1873 days never flag) | 32 | 0.171 | 0.750 | 0.0663 | +0.0051 [-0.0122, +0.0202] | -0.0100 [-0.0260, +0.0036] | 0.915 | 0.167 | no |
| 2 | 0.828 (147 of 1872 days never flag) | 23 | 0.086 | 0.522 | 0.0774 | -0.0063 [-0.0262, +0.0104] | -0.0163 [-0.0352, -0.0000] | 0.886 | 0.080 | no |
| 3 | 0.831 (147 of 1871 days never flag) | 28 | 0.116 | 0.571 | 0.0755 | -0.0048 [-0.0237, +0.0125] | -0.0111 [-0.0292, +0.0051] | 0.895 | 0.109 | no |
| 4 | 0.823 (147 of 1870 days never flag) | 25 | 0.101 | 0.560 | 0.0733 | -0.0025 [-0.0202, +0.0143] | -0.0110 [-0.0281, +0.0058] | 0.893 | 0.095 | no |
| 5 | 0.69 (147 of 1869 days never flag) | 44 | 0.138 | 0.432 | 0.0702 | +0.0008 [-0.0164, +0.0158] | -0.0068 [-0.0225, +0.0076] | 0.871 | 0.123 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.640 (climatology 0.457, difference +0.1830 [+0.0070, +0.3314]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0855, ΔBrier vs climatology +0.0440 [+0.0196, +0.0688], realised minus predicted -0.0040 [-0.0357, +0.0292]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.176 | 0.720 | 0.4681 | 0.2720 | -0.0497 [-0.1269, +0.0227] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0460 | 0.0159 | +0.0359 [+0.0276, +0.0442] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0022 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0086 | 0.0200 | +0.0049 [+0.0005, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0905 | 0.1165 | +0.0306 [+0.0067, +0.0598] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0072 | 0.0048 | +0.0094 [+0.0076, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0119 | 0.0031 | +0.0298 [+0.0225, +0.0366] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1940 | 0.4146 | +0.1258 [+0.0478, +0.2170] |
| scarcity_state | 3 | 473 | 117 | 0.188 | 0.733 | 0.4105 | 0.2474 | -0.0317 [-0.0939, +0.0285] |
| day_type | month_end | 150 | 17 | 0.235 | 0.800 | 0.1340 | 0.1133 | +0.0322 [-0.0009, +0.0619] |
| day_type | ordinary | 1603 | 101 | 0.109 | 0.688 | 0.1080 | 0.0630 | -0.0038 [-0.0222, +0.0121] |
| day_type | quarter_end | 31 | 9 | 0.556 | 1.000 | 0.3141 | 0.2903 | +0.1638 [+0.0993, +0.2249] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.667 | 0.1173 | 0.1461 | +0.0639 [+0.0252, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.0675 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2515 | 0.2213 |

## rare_logistic_class_weight+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 5 | 0.192 [0.065, 0.323] | 0.115 | 0.96 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.000, 0.229] | 0.115 | 0.96 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.82 (147 of 1873 days never flag) | 27 | 0.150 | 0.778 | 0.0674 | +0.0040 [-0.0128, +0.0200] | -0.0110 [-0.0265, +0.0029] | 0.910 | 0.147 | no |
| 2 | 0.836 (147 of 1872 days never flag) | 29 | 0.115 | 0.552 | 0.0778 | -0.0067 [-0.0270, +0.0104] | -0.0167 [-0.0367, -0.0001] | 0.885 | 0.108 | no |
| 3 | 0.838 (147 of 1871 days never flag) | 30 | 0.123 | 0.567 | 0.0771 | -0.0064 [-0.0261, +0.0122] | -0.0127 [-0.0320, +0.0048] | 0.893 | 0.116 | no |
| 4 | 0.823 (147 of 1870 days never flag) | 29 | 0.123 | 0.586 | 0.0727 | -0.0019 [-0.0201, +0.0146] | -0.0103 [-0.0281, +0.0060] | 0.895 | 0.116 | no |
| 5 | 0.735 (147 of 1869 days never flag) | 42 | 0.123 | 0.405 | 0.0703 | +0.0006 [-0.0165, +0.0149] | -0.0069 [-0.0233, +0.0070] | 0.865 | 0.109 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.645 (climatology 0.457, difference +0.1880 [+0.0160, +0.3435]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0205, +0.0695], realised minus predicted -0.0038 [-0.0350, +0.0268]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.147 | 0.750 | 0.4624 | 0.2720 | -0.0539 [-0.1350, +0.0214] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0526 | 0.0159 | +0.0350 [+0.0264, +0.0432] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0030 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0096 | 0.0200 | +0.0049 [+0.0008, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0883 | 0.1165 | +0.0298 [+0.0076, +0.0579] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0080 | 0.0048 | +0.0094 [+0.0078, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0144 | 0.0031 | +0.0297 [+0.0230, +0.0365] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1804 | 0.4146 | 0.1211 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.154 | 0.750 | 0.4079 | 0.2474 | -0.0355 [-0.1011, +0.0265] |
| day_type | month_end | 150 | 17 | 0.176 | 0.750 | 0.1328 | 0.1133 | +0.0313 [+0.0016, +0.0604] |
| day_type | ordinary | 1603 | 101 | 0.099 | 0.769 | 0.1083 | 0.0630 | -0.0046 [-0.0225, +0.0121] |
| day_type | quarter_end | 31 | 9 | 0.556 | 1.000 | 0.3122 | 0.2903 | +0.1613 [+0.0959, +0.2286] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.600 | 0.1120 | 0.1461 | +0.0583 [+0.0220, +0.0983] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1170 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2522 | 0.2213 |

## recal_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.700] | 0.269 | 5.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.318, 0.686] | 0.269 | 5.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.267 (126 of 1873 days never flag) | 242 | 0.671 | 0.388 | 0.0502 | +0.0213 [+0.0131, +0.0299] | +0.0062 [+0.0013, +0.0117] | 0.906 | 0.586 | no |
| 2 | 0.319 (126 of 1872 days never flag) | 207 | 0.583 | 0.391 | 0.0532 | +0.0178 [+0.0107, +0.0254] | +0.0078 [+0.0027, +0.0135] | 0.891 | 0.510 | no |
| 3 | 0.333 (126 of 1871 days never flag) | 174 | 0.435 | 0.345 | 0.0541 | +0.0166 [+0.0100, +0.0239] | +0.0103 [+0.0048, +0.0164] | 0.894 | 0.369 | no |
| 4 | 0.343 (126 of 1870 days never flag) | 212 | 0.507 | 0.330 | 0.0566 | +0.0142 [+0.0076, +0.0213] | +0.0058 [+0.0005, +0.0112] | 0.877 | 0.425 | no |
| 5 | 0.354 (126 of 1869 days never flag) | 228 | 0.594 | 0.360 | 0.0556 | +0.0153 [+0.0085, +0.0232] | +0.0077 [+0.0023, +0.0139] | 0.886 | 0.510 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.674 (climatology 0.457, difference +0.2165 [+0.0626, +0.3431]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0331, +0.0647], realised minus predicted +0.0421 [+0.0134, +0.0725]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.385 | 0.2868 | 0.2720 | +0.0384 [+0.0038, +0.0765] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0656 | 0.0159 | +0.0353 [+0.0280, +0.0418] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0110 | 0.0000 | +0.0136 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0123 | 0.0200 | +0.0016 [-0.0042, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.419 | 0.1114 | 0.1165 | +0.0239 [-0.0043, +0.0571] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0122 | 0.0048 | +0.0085 [+0.0065, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0429 | 0.0031 | +0.0266 [+0.0202, +0.0323] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.562 | 0.2118 | 0.4146 | 0.0840 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.718 | 0.382 | 0.2704 | 0.2474 | +0.0400 [+0.0109, +0.0716] |
| day_type | month_end | 150 | 17 | 0.824 | 0.609 | 0.0900 | 0.1133 | +0.0356 [+0.0154, +0.0587] |
| day_type | ordinary | 1603 | 101 | 0.693 | 0.341 | 0.0844 | 0.0630 | +0.0166 [+0.0083, +0.0259] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.1244 | 0.2903 | +0.0894 [-0.0015, +0.1762] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.1166 | 0.1461 | +0.0569 [+0.0331, +0.0829] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0433 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2542 | 0.2213 |

## recal_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.719] | 0.269 | 5.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.304, 0.684] | 0.269 | 5.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.246 (126 of 1873 days never flag) | 242 | 0.671 | 0.388 | 0.0496 | +0.0219 [+0.0135, +0.0311] | +0.0068 [+0.0020, +0.0122] | 0.898 | 0.586 | no |
| 2 | 0.269 (126 of 1872 days never flag) | 233 | 0.626 | 0.373 | 0.0530 | +0.0180 [+0.0114, +0.0251] | +0.0080 [+0.0031, +0.0136] | 0.881 | 0.542 | no |
| 3 | 0.277 (126 of 1871 days never flag) | 188 | 0.507 | 0.372 | 0.0541 | +0.0166 [+0.0101, +0.0239] | +0.0103 [+0.0051, +0.0162] | 0.887 | 0.439 | no |
| 4 | 0.283 (126 of 1870 days never flag) | 229 | 0.580 | 0.349 | 0.0567 | +0.0141 [+0.0078, +0.0210] | +0.0057 [+0.0010, +0.0110] | 0.871 | 0.494 | no |
| 5 | 0.284 (126 of 1869 days never flag) | 227 | 0.601 | 0.366 | 0.0574 | +0.0136 [+0.0069, +0.0213] | +0.0060 [+0.0012, +0.0122] | 0.876 | 0.518 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.697 (climatology 0.457, difference +0.2403 [+0.0918, +0.3391]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0301, +0.0594], realised minus predicted +0.0422 [+0.0121, +0.0751]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.735 | 0.385 | 0.2612 | 0.2720 | +0.0460 [+0.0128, +0.0813] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0935 | 0.0159 | +0.0328 [+0.0267, +0.0393] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0320 | 0.0000 | +0.0127 [+0.0110, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0255 | 0.0200 | +0.0010 [-0.0045, +0.0049] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.436 | 0.1116 | 0.1165 | +0.0229 [-0.0054, +0.0569] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0287 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0638 | 0.0031 | +0.0250 [+0.0189, +0.0306] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.667 | 0.1980 | 0.4146 | 0.0840 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.379 | 0.2559 | 0.2474 | +0.0446 [+0.0156, +0.0747] |
| day_type | month_end | 150 | 17 | 0.824 | 0.609 | 0.1021 | 0.1133 | +0.0421 [+0.0199, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.683 | 0.342 | 0.0934 | 0.0630 | +0.0169 [+0.0083, +0.0262] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1348 | 0.2903 | +0.0922 [+0.0064, +0.1789] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1164 | 0.1461 | +0.0534 [+0.0279, +0.0784] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1018 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2480 | 0.2213 |

## recal_platt_group (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.269 | 5.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.750] | 0.269 | 5.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.237 (126 of 1873 days never flag) | 223 | 0.664 | 0.417 | 0.0479 | +0.0235 [+0.0159, +0.0323] | +0.0084 [+0.0039, +0.0137] | 0.908 | 0.589 | no |
| 2 | 0.279 (126 of 1872 days never flag) | 204 | 0.590 | 0.402 | 0.0509 | +0.0201 [+0.0135, +0.0273] | +0.0101 [+0.0050, +0.0160] | 0.895 | 0.520 | no |
| 3 | 0.277 (126 of 1871 days never flag) | 181 | 0.536 | 0.409 | 0.0508 | +0.0199 [+0.0127, +0.0278] | +0.0136 [+0.0079, +0.0196] | 0.903 | 0.474 | no |
| 4 | 0.25 (126 of 1870 days never flag) | 227 | 0.587 | 0.357 | 0.0533 | +0.0176 [+0.0110, +0.0247] | +0.0091 [+0.0042, +0.0147] | 0.890 | 0.503 | no |
| 5 | 0.247 (126 of 1869 days never flag) | 222 | 0.616 | 0.383 | 0.0538 | +0.0171 [+0.0103, +0.0244] | +0.0096 [+0.0044, +0.0155] | 0.892 | 0.537 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.457, difference +0.2209 [+0.0708, +0.3391]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0818, ΔBrier vs climatology +0.0477 [+0.0334, +0.0646], realised minus predicted +0.0427 [+0.0135, +0.0746]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.415 | 0.2524 | 0.2720 | +0.0478 [+0.0153, +0.0845] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0820 | 0.0159 | +0.0339 [+0.0266, +0.0406] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0320 | 0.0000 | +0.0127 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0255 | 0.0200 | +0.0010 [-0.0042, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.444 | 0.1001 | 0.1165 | +0.0316 [+0.0037, +0.0717] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0260 | 0.0048 | +0.0082 [+0.0064, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0602 | 0.0031 | +0.0251 [+0.0191, +0.0308] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.588 | 0.2268 | 0.4146 | 0.1088 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.410 | 0.2425 | 0.2474 | +0.0486 [+0.0218, +0.0794] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1033 | 0.1133 | +0.0406 [+0.0193, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.367 | 0.0871 | 0.0630 | +0.0184 [+0.0103, +0.0275] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.1432 | 0.2903 | +0.1084 [+0.0225, +0.1946] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1223 | 0.1461 | +0.0578 [+0.0362, +0.0829] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0935 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2608 | 0.2213 |

## recal_platt_weighted (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.722] | 0.276 | 5.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.345, 0.727] | 0.276 | 5.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.246 (126 of 1873 days never flag) | 231 | 0.650 | 0.394 | 0.0481 | +0.0233 [+0.0153, +0.0320] | +0.0082 [+0.0036, +0.0135] | 0.912 | 0.569 | no |
| 2 | 0.359 (126 of 1872 days never flag) | 178 | 0.518 | 0.404 | 0.0513 | +0.0198 [+0.0132, +0.0271] | +0.0098 [+0.0049, +0.0156] | 0.899 | 0.457 | no |
| 3 | 0.374 (126 of 1871 days never flag) | 145 | 0.420 | 0.400 | 0.0518 | +0.0189 [+0.0123, +0.0267] | +0.0125 [+0.0072, +0.0186] | 0.903 | 0.370 | no |
| 4 | 0.269 (126 of 1870 days never flag) | 237 | 0.601 | 0.350 | 0.0541 | +0.0168 [+0.0103, +0.0236] | +0.0083 [+0.0035, +0.0136] | 0.894 | 0.513 | no |
| 5 | 0.269 (126 of 1869 days never flag) | 236 | 0.616 | 0.360 | 0.0547 | +0.0162 [+0.0097, +0.0233] | +0.0087 [+0.0035, +0.0141] | 0.895 | 0.529 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.659 (climatology 0.457, difference +0.2015 [+0.0748, +0.2925]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0831, ΔBrier vs climatology +0.0464 [+0.0325, +0.0612], realised minus predicted +0.0520 [+0.0230, +0.0825]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.706 | 0.391 | 0.2574 | 0.2720 | +0.0479 [+0.0166, +0.0831] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0751 | 0.0159 | +0.0343 [+0.0272, +0.0409] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0135 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0144 | 0.0200 | +0.0009 [-0.0048, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.436 | 0.1029 | 0.1165 | +0.0270 [-0.0023, +0.0624] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0145 | 0.0048 | +0.0085 [+0.0065, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0461 | 0.0031 | +0.0267 [+0.0205, +0.0325] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.667 | 0.2015 | 0.4146 | 0.0928 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.701 | 0.385 | 0.2497 | 0.2474 | +0.0471 [+0.0210, +0.0759] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1058 | 0.1133 | +0.0436 [+0.0208, +0.0719] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.349 | 0.0786 | 0.0630 | +0.0183 [+0.0101, +0.0270] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1389 | 0.2903 | +0.0937 [+0.0121, +0.1763] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.583 | 0.1149 | 0.1461 | +0.0536 [+0.0295, +0.0788] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1070 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2570 | 0.2213 |

## recency_decay_126+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 4 | 0.154 [0.043, 0.276] | 0.115 | 0.88 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.029, 0.222] | 0.115 | 0.88 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.775 (147 of 1873 days never flag) | 32 | 0.164 | 0.719 | 0.0673 | +0.0041 [-0.0119, +0.0185] | -0.0110 [-0.0254, +0.0018] | 0.899 | 0.159 | no |
| 2 | 0.792 (147 of 1872 days never flag) | 25 | 0.086 | 0.480 | 0.0759 | -0.0049 [-0.0235, +0.0111] | -0.0149 [-0.0328, +0.0001] | 0.872 | 0.079 | no |
| 3 | 0.795 (147 of 1871 days never flag) | 22 | 0.109 | 0.682 | 0.0747 | -0.0041 [-0.0222, +0.0119] | -0.0104 [-0.0279, +0.0051] | 0.881 | 0.105 | no |
| 4 | 0.777 (147 of 1870 days never flag) | 26 | 0.101 | 0.538 | 0.0714 | -0.0006 [-0.0183, +0.0164] | -0.0090 [-0.0262, +0.0070] | 0.880 | 0.095 | no |
| 5 | 0.633 (147 of 1869 days never flag) | 42 | 0.138 | 0.452 | 0.0686 | +0.0023 [-0.0140, +0.0169] | -0.0052 [-0.0209, +0.0084] | 0.871 | 0.124 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.668 (climatology 0.457, difference +0.2112 [+0.0140, +0.3689]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0828, ΔBrier vs climatology +0.0467 [+0.0210, +0.0721], realised minus predicted -0.0294 [-0.0583, +0.0001]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.137 | 0.778 | 0.4319 | 0.2720 | -0.0400 [-0.1133, +0.0247] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0573 | 0.0159 | +0.0358 [+0.0278, +0.0440] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0128 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0323 | 0.0200 | +0.0024 [-0.0039, +0.0097] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.615 | 0.1816 | 0.1165 | +0.0116 [-0.0190, +0.0485] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0304 | 0.0048 | +0.0055 [+0.0020, +0.0086] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0373 | 0.0031 | +0.0244 [+0.0139, +0.0336] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.600 | 0.2773 | 0.4146 | 0.1403 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.162 | 0.731 | 0.3895 | 0.2474 | -0.0248 [-0.0868, +0.0279] |
| day_type | month_end | 150 | 17 | 0.235 | 1.000 | 0.1312 | 0.1133 | +0.0300 [+0.0006, +0.0568] |
| day_type | ordinary | 1603 | 101 | 0.109 | 0.647 | 0.1236 | 0.0630 | -0.0039 [-0.0204, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.556 | 1.000 | 0.3375 | 0.2903 | +0.1384 [+0.0553, +0.2187] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.500 | 0.1229 | 0.1461 | +0.0569 [+0.0190, +0.0973] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1282 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2436 | 0.2213 |

## recency_decay_252+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 4 | 0.154 [0.045, 0.276] | 0.115 | 1.08 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 4 | 0.154 [0.043, 0.269] | 0.115 | 1.08 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.799 (147 of 1873 days never flag) | 32 | 0.164 | 0.719 | 0.0678 | +0.0036 [-0.0123, +0.0191] | -0.0115 [-0.0262, +0.0021] | 0.907 | 0.159 | no |
| 2 | 0.815 (147 of 1872 days never flag) | 27 | 0.101 | 0.519 | 0.0765 | -0.0055 [-0.0232, +0.0112] | -0.0155 [-0.0330, +0.0001] | 0.883 | 0.093 | no |
| 3 | 0.818 (147 of 1871 days never flag) | 22 | 0.101 | 0.636 | 0.0757 | -0.0050 [-0.0243, +0.0124] | -0.0113 [-0.0294, +0.0054] | 0.890 | 0.097 | no |
| 4 | 0.801 (147 of 1870 days never flag) | 31 | 0.116 | 0.516 | 0.0720 | -0.0012 [-0.0183, +0.0153] | -0.0096 [-0.0263, +0.0066] | 0.891 | 0.107 | no |
| 5 | 0.684 (147 of 1869 days never flag) | 49 | 0.152 | 0.429 | 0.0693 | +0.0016 [-0.0151, +0.0160] | -0.0059 [-0.0217, +0.0080] | 0.874 | 0.136 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.670 (climatology 0.457, difference +0.2125 [+0.0231, +0.3768]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0807, ΔBrier vs climatology +0.0488 [+0.0230, +0.0762], realised minus predicted -0.0266 [-0.0569, +0.0016]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.137 | 0.737 | 0.4465 | 0.2720 | -0.0465 [-0.1213, +0.0282] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0541 | 0.0159 | +0.0356 [+0.0270, +0.0442] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0073 | 0.0000 | +0.0137 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0266 | 0.0200 | +0.0035 [-0.0020, +0.0097] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.667 | 0.1841 | 0.1165 | +0.0164 [-0.0157, +0.0565] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0237 | 0.0048 | +0.0064 [+0.0032, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0323 | 0.0031 | +0.0254 [+0.0150, +0.0346] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.600 | 0.3297 | 0.4146 | 0.1522 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.162 | 0.731 | 0.4026 | 0.2474 | -0.0304 [-0.0914, +0.0299] |
| day_type | month_end | 150 | 17 | 0.235 | 0.800 | 0.1359 | 0.1133 | +0.0326 [+0.0014, +0.0631] |
| day_type | ordinary | 1603 | 101 | 0.109 | 0.647 | 0.1228 | 0.0630 | -0.0048 [-0.0218, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.556 | 1.000 | 0.3447 | 0.2903 | +0.1438 [+0.0615, +0.2197] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.600 | 0.1234 | 0.1461 | +0.0568 [+0.0182, +0.0974] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1237 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2494 | 0.2213 |

## recency_decay_63+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 4 | 0.154 [0.048, 0.273] | 0.077 | 0.58 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.031, 0.220] | 0.077 | 0.58 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.715 (147 of 1873 days never flag) | 24 | 0.121 | 0.708 | 0.0658 | +0.0056 [-0.0083, +0.0203] | -0.0094 [-0.0222, +0.0029] | 0.887 | 0.117 | no |
| 2 | 0.738 (147 of 1872 days never flag) | 21 | 0.079 | 0.524 | 0.0745 | -0.0035 [-0.0207, +0.0120] | -0.0135 [-0.0300, +0.0018] | 0.857 | 0.073 | no |
| 3 | 0.74 (147 of 1871 days never flag) | 14 | 0.058 | 0.571 | 0.0729 | -0.0023 [-0.0189, +0.0129] | -0.0086 [-0.0243, +0.0059] | 0.867 | 0.055 | no |
| 4 | 0.618 (147 of 1870 days never flag) | 25 | 0.087 | 0.480 | 0.0700 | +0.0008 [-0.0153, +0.0157] | -0.0077 [-0.0234, +0.0071] | 0.864 | 0.079 | no |
| 5 | 0.536 (147 of 1869 days never flag) | 31 | 0.116 | 0.516 | 0.0677 | +0.0032 [-0.0106, +0.0169] | -0.0043 [-0.0174, +0.0093] | 0.862 | 0.107 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.670 (climatology 0.457, difference +0.2131 [+0.0179, +0.3681]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0864, ΔBrier vs climatology +0.0431 [+0.0206, +0.0684], realised minus predicted -0.0263 [-0.0580, +0.0050]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.118 | 0.800 | 0.4071 | 0.2720 | -0.0295 [-0.0961, +0.0373] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0654 | 0.0159 | +0.0356 [+0.0270, +0.0442] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0216 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0322 | 0.0200 | +0.0035 [-0.0024, +0.0101] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.500 | 0.1645 | 0.1165 | +0.0079 [-0.0187, +0.0434] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0368 | 0.0048 | +0.0055 [+0.0021, +0.0086] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0458 | 0.0031 | +0.0236 [+0.0124, +0.0328] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.500 | 0.1949 | 0.4146 | 0.1161 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.128 | 0.789 | 0.3663 | 0.2474 | -0.0158 [-0.0694, +0.0378] |
| day_type | month_end | 150 | 17 | 0.235 | 1.000 | 0.1286 | 0.1133 | +0.0291 [+0.0039, +0.0537] |
| day_type | ordinary | 1603 | 101 | 0.050 | 0.625 | 0.1210 | 0.0630 | -0.0018 [-0.0166, +0.0135] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3202 | 0.2903 | +0.1300 [+0.0451, +0.2048] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.600 | 0.1237 | 0.1461 | +0.0572 [+0.0207, +0.0975] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1323 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2292 | 0.2213 |

## recency_window_252+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 6 | 0.231 [0.095, 0.385] | 0.115 | 1.35 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 5 | 0.192 [0.061, 0.333] | 0.115 | 1.35 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.806 (147 of 1873 days never flag) | 28 | 0.150 | 0.750 | 0.0675 | +0.0039 [-0.0129, +0.0191] | -0.0112 [-0.0262, +0.0023] | 0.910 | 0.146 | no |
| 2 | 0.826 (147 of 1872 days never flag) | 26 | 0.108 | 0.577 | 0.0776 | -0.0065 [-0.0261, +0.0116] | -0.0165 [-0.0348, +0.0004] | 0.887 | 0.102 | no |
| 3 | 0.83 (147 of 1871 days never flag) | 23 | 0.116 | 0.696 | 0.0769 | -0.0062 [-0.0258, +0.0114] | -0.0125 [-0.0314, +0.0047] | 0.895 | 0.112 | no |
| 4 | 0.818 (147 of 1870 days never flag) | 30 | 0.130 | 0.600 | 0.0728 | -0.0020 [-0.0187, +0.0150] | -0.0104 [-0.0271, +0.0062] | 0.896 | 0.124 | no |
| 5 | 0.735 (147 of 1869 days never flag) | 56 | 0.152 | 0.375 | 0.0713 | -0.0004 [-0.0167, +0.0152] | -0.0079 [-0.0243, +0.0071] | 0.866 | 0.132 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.457, difference +0.1799 [+0.0064, +0.3229]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0450 [+0.0211, +0.0697], realised minus predicted -0.0073 [-0.0399, +0.0251]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.147 | 0.789 | 0.4538 | 0.2720 | -0.0522 [-0.1298, +0.0205] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0474 | 0.0159 | +0.0362 [+0.0276, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0034 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0102 | 0.0200 | +0.0050 [+0.0010, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.667 | 0.1114 | 0.1165 | +0.0253 [-0.0015, +0.0558] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0087 | 0.0048 | +0.0094 [+0.0078, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0143 | 0.0031 | +0.0297 [+0.0222, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.1868 | 0.4146 | 0.1257 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.162 | 0.731 | 0.4094 | 0.2474 | -0.0363 [-0.0982, +0.0223] |
| day_type | month_end | 150 | 17 | 0.235 | 1.000 | 0.1332 | 0.1133 | +0.0345 [+0.0023, +0.0662] |
| day_type | ordinary | 1603 | 101 | 0.099 | 0.714 | 0.1090 | 0.0630 | -0.0048 [-0.0235, +0.0111] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2970 | 0.2903 | +0.1605 [+0.1014, +0.2238] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.500 | 0.1233 | 0.1461 | +0.0557 [+0.0167, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1285 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2621 | 0.2213 |

## recency_window_504+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 6 | 0.231 [0.097, 0.375] | 0.154 | 1.62 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 4 | 0.154 [0.045, 0.273] | 0.154 | 1.62 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.82 (147 of 1873 days never flag) | 41 | 0.193 | 0.659 | 0.0680 | +0.0034 [-0.0139, +0.0184] | -0.0117 [-0.0280, +0.0017] | 0.913 | 0.185 | no |
| 2 | 0.836 (147 of 1872 days never flag) | 30 | 0.122 | 0.567 | 0.0772 | -0.0062 [-0.0256, +0.0114] | -0.0162 [-0.0343, +0.0003] | 0.891 | 0.115 | no |
| 3 | 0.838 (147 of 1871 days never flag) | 31 | 0.130 | 0.581 | 0.0762 | -0.0055 [-0.0259, +0.0126] | -0.0118 [-0.0315, +0.0055] | 0.901 | 0.123 | no |
| 4 | 0.823 (147 of 1870 days never flag) | 38 | 0.167 | 0.605 | 0.0722 | -0.0014 [-0.0195, +0.0159] | -0.0099 [-0.0276, +0.0066] | 0.902 | 0.158 | no |
| 5 | 0.735 (147 of 1869 days never flag) | 69 | 0.196 | 0.391 | 0.0705 | +0.0004 [-0.0170, +0.0154] | -0.0071 [-0.0234, +0.0076] | 0.870 | 0.171 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.669 (climatology 0.457, difference +0.2118 [+0.0150, +0.3771]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0787, ΔBrier vs climatology +0.0508 [+0.0241, +0.0781], realised minus predicted -0.0127 [-0.0427, +0.0167]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.147 | 0.750 | 0.4624 | 0.2720 | -0.0539 [-0.1330, +0.0192] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0526 | 0.0159 | +0.0351 [+0.0268, +0.0434] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0031 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0095 | 0.0200 | +0.0049 [+0.0007, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.550 | 0.1437 | 0.1165 | +0.0248 [-0.0044, +0.0591] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0079 | 0.0048 | +0.0094 [+0.0077, +0.0112] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0146 | 0.0031 | +0.0297 [+0.0229, +0.0362] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.714 | 0.2829 | 0.4146 | 0.1462 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.179 | 0.636 | 0.4282 | 0.2474 | -0.0403 [-0.1066, +0.0177] |
| day_type | month_end | 150 | 17 | 0.235 | 0.800 | 0.1358 | 0.1133 | +0.0354 [+0.0024, +0.0682] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.600 | 0.1161 | 0.0630 | -0.0056 [-0.0241, +0.0102] |
| day_type | quarter_end | 31 | 9 | 0.556 | 1.000 | 0.3084 | 0.2903 | +0.1620 [+0.0994, +0.2274] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.500 | 0.1242 | 0.1461 | +0.0560 [+0.0164, +0.0948] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1170 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2522 | 0.2213 |

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

## scarcity_gbm (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.682] | 0.269 | 5.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.235, 0.619] | 0.269 | 5.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.3 (147 of 1873 days never flag) | 223 | 0.686 | 0.430 | 0.0526 | +0.0188 [+0.0125, +0.0260] | +0.0037 [+0.0001, +0.0076] | 0.832 | 0.612 | no |
| 2 | 0.319 (126 of 1872 days never flag) | 191 | 0.518 | 0.377 | 0.0591 | +0.0120 [+0.0074, +0.0169] | +0.0020 [-0.0015, +0.0056] | 0.797 | 0.449 | no |
| 3 | 0.336 (147 of 1871 days never flag) | 169 | 0.507 | 0.414 | 0.0585 | +0.0121 [+0.0083, +0.0164] | +0.0058 [+0.0030, +0.0090] | 0.825 | 0.450 | no |
| 4 | 0.285 (147 of 1870 days never flag) | 206 | 0.536 | 0.359 | 0.0613 | +0.0096 [+0.0050, +0.0142] | +0.0011 [-0.0023, +0.0048] | 0.721 | 0.460 | no |
| 5 | 0.33 (147 of 1869 days never flag) | 149 | 0.399 | 0.369 | 0.0610 | +0.0099 [+0.0052, +0.0146] | +0.0024 [-0.0012, +0.0060] | 0.778 | 0.344 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.504 (climatology 0.457, difference +0.0472 [-0.0797, +0.1678]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0896, ΔBrier vs climatology +0.0399 [+0.0271, +0.0535], realised minus predicted +0.0387 [+0.0057, +0.0753]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.443 | 0.2021 | 0.2720 | +0.0253 [+0.0036, +0.0493] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.1016 | 0.0159 | +0.0277 [+0.0171, +0.0376] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0078 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0119 | 0.0200 | +0.0003 [-0.0052, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.562 | 0.1285 | 0.1165 | +0.0336 [+0.0038, +0.0708] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0130 | 0.0048 | +0.0080 [+0.0059, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0481 | 0.0031 | +0.0265 [+0.0199, +0.0326] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.778 | 0.1986 | 0.4146 | 0.1212 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.761 | 0.416 | 0.2219 | 0.2474 | +0.0281 [+0.0079, +0.0500] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.0913 | 0.1133 | +0.0366 [+0.0184, +0.0581] |
| day_type | ordinary | 1603 | 101 | 0.703 | 0.390 | 0.0739 | 0.0630 | +0.0146 [+0.0083, +0.0218] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.0978 | 0.2903 | +0.0734 [-0.0270, +0.1663] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.0779 | 0.1461 | +0.0449 [+0.0297, +0.0610] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.3511 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2036 | 0.2213 |

## scarcity_gbm_interactions (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.680] | 0.269 | 5.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.231, 0.625] | 0.269 | 5.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.3 (147 of 1873 days never flag) | 223 | 0.693 | 0.435 | 0.0526 | +0.0188 [+0.0121, +0.0259] | +0.0037 [-0.0001, +0.0075] | 0.833 | 0.620 | no |
| 2 | 0.319 (126 of 1872 days never flag) | 191 | 0.518 | 0.377 | 0.0591 | +0.0120 [+0.0074, +0.0169] | +0.0020 [-0.0015, +0.0055] | 0.797 | 0.449 | no |
| 3 | 0.336 (147 of 1871 days never flag) | 169 | 0.507 | 0.414 | 0.0585 | +0.0121 [+0.0080, +0.0165] | +0.0058 [+0.0028, +0.0089] | 0.825 | 0.450 | no |
| 4 | 0.285 (147 of 1870 days never flag) | 206 | 0.536 | 0.359 | 0.0613 | +0.0096 [+0.0052, +0.0143] | +0.0011 [-0.0024, +0.0046] | 0.721 | 0.460 | no |
| 5 | 0.33 (147 of 1869 days never flag) | 149 | 0.399 | 0.369 | 0.0610 | +0.0099 [+0.0051, +0.0149] | +0.0024 [-0.0012, +0.0064] | 0.778 | 0.344 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.504 (climatology 0.457, difference +0.0472 [-0.0732, +0.1787]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0896, ΔBrier vs climatology +0.0398 [+0.0260, +0.0542], realised minus predicted +0.0388 [+0.0045, +0.0738]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.443 | 0.2021 | 0.2720 | +0.0253 [+0.0021, +0.0488] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.1016 | 0.0159 | +0.0277 [+0.0164, +0.0380] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0137 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0002 [-0.0052, +0.0044] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.594 | 0.1260 | 0.1165 | +0.0338 [+0.0039, +0.0714] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0125 | 0.0048 | +0.0080 [+0.0060, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0470 | 0.0031 | +0.0263 [+0.0195, +0.0323] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.889 | 0.1984 | 0.4146 | 0.1233 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.761 | 0.416 | 0.2221 | 0.2474 | +0.0280 [+0.0068, +0.0498] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.0900 | 0.1133 | +0.0365 [+0.0187, +0.0584] |
| day_type | ordinary | 1603 | 101 | 0.713 | 0.396 | 0.0735 | 0.0630 | +0.0146 [+0.0079, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.0970 | 0.2903 | +0.0729 [-0.0284, +0.1636] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.0790 | 0.1461 | +0.0447 [+0.0299, +0.0613] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.3511 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2036 | 0.2213 |

## scarcity_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.696] | 0.269 | 4.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.611] | 0.269 | 4.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.404 (147 of 1873 days never flag) | 210 | 0.621 | 0.414 | 0.0528 | +0.0186 [+0.0117, +0.0260] | +0.0035 [-0.0006, +0.0074] | 0.872 | 0.550 | no |
| 2 | 0.372 (147 of 1872 days never flag) | 201 | 0.626 | 0.433 | 0.0590 | +0.0121 [+0.0070, +0.0172] | +0.0020 [-0.0018, +0.0060] | 0.844 | 0.560 | no |
| 3 | 0.381 (147 of 1871 days never flag) | 185 | 0.580 | 0.432 | 0.0609 | +0.0097 [+0.0054, +0.0142] | +0.0034 [-0.0005, +0.0072] | 0.832 | 0.519 | no |
| 4 | 0.404 (147 of 1870 days never flag) | 185 | 0.493 | 0.368 | 0.0604 | +0.0105 [+0.0059, +0.0151] | +0.0020 [-0.0025, +0.0066] | 0.830 | 0.425 | no |
| 5 | 0.409 (147 of 1869 days never flag) | 198 | 0.558 | 0.389 | 0.0610 | +0.0099 [+0.0054, +0.0143] | +0.0024 [-0.0018, +0.0064] | 0.807 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0501, +0.1189]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0911, ΔBrier vs climatology +0.0384 [+0.0266, +0.0521], realised minus predicted +0.0452 [+0.0134, +0.0804]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.408 | 0.2174 | 0.2720 | +0.0280 [+0.0063, +0.0536] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1424 | 0.0159 | +0.0171 [+0.0033, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0091 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0068 | 0.0200 | +0.0013 [-0.0040, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.560 | 0.1177 | 0.1165 | +0.0380 [+0.0067, +0.0757] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0648 | 0.0031 | +0.0254 [+0.0194, +0.0309] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.2300 | 0.4146 | 0.1230 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.709 | 0.405 | 0.2468 | 0.2474 | +0.0262 [+0.0050, +0.0506] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1027 | 0.1133 | +0.0443 [+0.0233, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.604 | 0.363 | 0.0755 | 0.0630 | +0.0126 [+0.0064, +0.0198] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2460 | 0.2903 | +0.0957 [+0.0480, +0.1406] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1246 | 0.1461 | +0.0563 [+0.0325, +0.0826] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2396 | 0.2213 |

## scarcity_logistic_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.316, 0.692] | 0.192 | 1.85 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.625] | 0.192 | 1.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.404 (147 of 1873 days never flag) | 86 | 0.293 | 0.477 | 0.0528 | +0.0186 [+0.0122, +0.0263] | +0.0035 [-0.0004, +0.0074] | 0.872 | 0.267 | no |
| 2 | 0.372 (147 of 1872 days never flag) | 64 | 0.165 | 0.359 | 0.0590 | +0.0121 [+0.0069, +0.0177] | +0.0020 [-0.0018, +0.0059] | 0.844 | 0.142 | no |
| 3 | 0.381 (147 of 1871 days never flag) | 59 | 0.152 | 0.356 | 0.0609 | +0.0097 [+0.0054, +0.0141] | +0.0034 [-0.0004, +0.0072] | 0.832 | 0.130 | no |
| 4 | 0.404 (147 of 1870 days never flag) | 68 | 0.246 | 0.500 | 0.0604 | +0.0105 [+0.0061, +0.0151] | +0.0020 [-0.0021, +0.0064] | 0.830 | 0.227 | no |
| 5 | 0.409 (147 of 1869 days never flag) | 81 | 0.239 | 0.407 | 0.0610 | +0.0099 [+0.0055, +0.0141] | +0.0024 [-0.0019, +0.0065] | 0.807 | 0.211 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0480, +0.1124]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0911, ΔBrier vs climatology +0.0384 [+0.0265, +0.0514], realised minus predicted +0.0452 [+0.0117, +0.0795]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.324 | 0.452 | 0.2174 | 0.2720 | +0.0280 [+0.0052, +0.0542] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1424 | 0.0159 | +0.0171 [+0.0036, +0.0292] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0091 | 0.0000 | +0.0137 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0068 | 0.0200 | +0.0013 [-0.0039, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.1177 | 0.1165 | +0.0380 [+0.0082, +0.0746] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0648 | 0.0031 | +0.0254 [+0.0194, +0.0306] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.2300 | 0.4146 | 0.1230 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.464 | 0.2468 | 0.2474 | +0.0262 [+0.0048, +0.0508] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1027 | 0.1133 | +0.0443 [+0.0235, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.238 | 0.407 | 0.0755 | 0.0630 | +0.0126 [+0.0065, +0.0197] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2460 | 0.2903 | +0.0957 [+0.0446, +0.1424] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.556 | 0.1246 | 0.1461 | +0.0563 [+0.0326, +0.0821] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2396 | 0.2213 |

## scarcity_logistic_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.217, 0.556] | 0.115 | 0.92 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.500] | 0.115 | 0.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.404 (147 of 1873 days never flag) | 43 | 0.136 | 0.442 | 0.0528 | +0.0186 [+0.0121, +0.0260] | +0.0035 [-0.0003, +0.0077] | 0.872 | 0.122 | no |
| 2 | 0.372 (147 of 1872 days never flag) | 41 | 0.129 | 0.439 | 0.0590 | +0.0121 [+0.0065, +0.0174] | +0.0020 [-0.0019, +0.0059] | 0.844 | 0.116 | no |
| 3 | 0.381 (147 of 1871 days never flag) | 37 | 0.116 | 0.432 | 0.0609 | +0.0097 [+0.0054, +0.0140] | +0.0034 [-0.0003, +0.0070] | 0.832 | 0.104 | no |
| 4 | 0.404 (147 of 1870 days never flag) | 38 | 0.123 | 0.447 | 0.0604 | +0.0105 [+0.0059, +0.0149] | +0.0020 [-0.0021, +0.0062] | 0.830 | 0.111 | no |
| 5 | 0.409 (147 of 1869 days never flag) | 37 | 0.109 | 0.405 | 0.0610 | +0.0099 [+0.0056, +0.0143] | +0.0024 [-0.0016, +0.0063] | 0.807 | 0.096 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0518, +0.1163]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0911, ΔBrier vs climatology +0.0384 [+0.0267, +0.0520], realised minus predicted +0.0452 [+0.0113, +0.0802]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.137 | 0.424 | 0.2174 | 0.2720 | +0.0280 [+0.0058, +0.0520] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1424 | 0.0159 | +0.0171 [+0.0034, +0.0291] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0091 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0068 | 0.0200 | +0.0013 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.714 | 0.1177 | 0.1165 | +0.0380 [+0.0077, +0.0760] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0648 | 0.0031 | +0.0254 [+0.0196, +0.0308] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.2300 | 0.4146 | +0.1230 [+0.0023, +0.2254] |
| scarcity_state | 3 | 473 | 117 | 0.145 | 0.415 | 0.2468 | 0.2474 | +0.0262 [+0.0053, +0.0493] |
| day_type | month_end | 150 | 17 | 0.176 | 0.750 | 0.1027 | 0.1133 | +0.0443 [+0.0236, +0.0703] |
| day_type | ordinary | 1603 | 101 | 0.099 | 0.323 | 0.0755 | 0.0630 | +0.0126 [+0.0067, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.2460 | 0.2903 | +0.0957 [+0.0474, +0.1400] |
| day_type | tax_date | 89 | 13 | 0.231 | 1.000 | 0.1246 | 0.1461 | +0.0563 [+0.0322, +0.0823] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2396 | 0.2213 |

## scarcity_logistic_interactions (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.346, 0.731] | 0.269 | 5.50 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.619] | 0.269 | 4.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.384 (126 of 1873 days never flag) | 233 | 0.643 | 0.386 | 0.0540 | +0.0174 [+0.0112, +0.0246] | +0.0024 [-0.0014, +0.0060] | 0.859 | 0.560 | no |
| 2 | 0.372 (147 of 1872 days never flag) | 201 | 0.626 | 0.433 | 0.0590 | +0.0121 [+0.0069, +0.0173] | +0.0020 [-0.0019, +0.0060] | 0.844 | 0.560 | no |
| 3 | 0.381 (147 of 1871 days never flag) | 185 | 0.580 | 0.432 | 0.0609 | +0.0097 [+0.0052, +0.0142] | +0.0034 [-0.0004, +0.0073] | 0.832 | 0.519 | no |
| 4 | 0.404 (147 of 1870 days never flag) | 185 | 0.493 | 0.368 | 0.0604 | +0.0105 [+0.0059, +0.0149] | +0.0020 [-0.0022, +0.0060] | 0.830 | 0.425 | no |
| 5 | 0.409 (147 of 1869 days never flag) | 198 | 0.558 | 0.389 | 0.0610 | +0.0099 [+0.0056, +0.0144] | +0.0024 [-0.0017, +0.0064] | 0.807 | 0.488 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0460, +0.1162]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0253, +0.0491], realised minus predicted +0.0474 [+0.0144, +0.0844]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.376 | 0.2070 | 0.2720 | +0.0243 [+0.0022, +0.0477] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1466 | 0.0159 | +0.0179 [+0.0050, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0115 | 0.0000 | +0.0136 [+0.0117, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0082 | 0.0200 | +0.0013 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.1169 | 0.1165 | +0.0346 [+0.0037, +0.0735] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0095 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0725 | 0.0031 | +0.0243 [+0.0186, +0.0296] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.667 | 0.2169 | 0.4146 | 0.1034 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.735 | 0.379 | 0.2368 | 0.2474 | +0.0242 [+0.0039, +0.0462] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1020 | 0.1133 | +0.0438 [+0.0240, +0.0678] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.333 | 0.0760 | 0.0630 | +0.0123 [+0.0065, +0.0189] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1814 | 0.2903 | +0.0462 [-0.0256, +0.1140] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1291 | 0.1461 | +0.0556 [+0.0324, +0.0801] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0570 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2325 | 0.2213 |

## scarcity_logistic_interactions_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.722] | 0.192 | 2.04 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.611] | 0.192 | 1.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.384 (126 of 1873 days never flag) | 96 | 0.307 | 0.448 | 0.0540 | +0.0174 [+0.0109, +0.0245] | +0.0024 [-0.0013, +0.0062] | 0.859 | 0.277 | no |
| 2 | 0.372 (147 of 1872 days never flag) | 64 | 0.165 | 0.359 | 0.0590 | +0.0121 [+0.0070, +0.0173] | +0.0020 [-0.0018, +0.0058] | 0.844 | 0.142 | no |
| 3 | 0.381 (147 of 1871 days never flag) | 59 | 0.152 | 0.356 | 0.0609 | +0.0097 [+0.0054, +0.0141] | +0.0034 [-0.0002, +0.0073] | 0.832 | 0.130 | no |
| 4 | 0.404 (147 of 1870 days never flag) | 68 | 0.246 | 0.500 | 0.0604 | +0.0105 [+0.0059, +0.0153] | +0.0020 [-0.0026, +0.0064] | 0.830 | 0.227 | no |
| 5 | 0.409 (147 of 1869 days never flag) | 81 | 0.239 | 0.407 | 0.0610 | +0.0099 [+0.0055, +0.0142] | +0.0024 [-0.0017, +0.0068] | 0.807 | 0.211 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0511, +0.1139]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0254, +0.0502], realised minus predicted +0.0474 [+0.0134, +0.0817]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.434 | 0.2070 | 0.2720 | +0.0243 [+0.0026, +0.0474] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1466 | 0.0159 | +0.0179 [+0.0051, +0.0298] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0115 | 0.0000 | +0.0136 [+0.0119, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0082 | 0.0200 | +0.0013 [-0.0037, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.636 | 0.1169 | 0.1165 | +0.0346 [+0.0034, +0.0723] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0095 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0725 | 0.0031 | +0.0243 [+0.0186, +0.0297] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.333 | 0.2169 | 0.4146 | 0.1034 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.359 | 0.452 | 0.2368 | 0.2474 | +0.0242 [+0.0044, +0.0473] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1020 | 0.1133 | +0.0438 [+0.0232, +0.0676] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.380 | 0.0760 | 0.0630 | +0.0123 [+0.0063, +0.0191] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.750 | 0.1814 | 0.2903 | +0.0462 [-0.0267, +0.1156] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.556 | 0.1291 | 0.1461 | +0.0556 [+0.0313, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0570 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2325 | 0.2213 |

## scarcity_logistic_interactions_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 9 | 0.346 [0.185, 0.524] | 0.115 | 1.15 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.483] | 0.115 | 0.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.384 (126 of 1873 days never flag) | 49 | 0.136 | 0.388 | 0.0540 | +0.0174 [+0.0114, +0.0249] | +0.0024 [-0.0012, +0.0061] | 0.859 | 0.118 | no |
| 2 | 0.372 (147 of 1872 days never flag) | 41 | 0.129 | 0.439 | 0.0590 | +0.0121 [+0.0069, +0.0176] | +0.0020 [-0.0019, +0.0060] | 0.844 | 0.116 | no |
| 3 | 0.381 (147 of 1871 days never flag) | 37 | 0.116 | 0.432 | 0.0609 | +0.0097 [+0.0052, +0.0142] | +0.0034 [-0.0003, +0.0072] | 0.832 | 0.104 | no |
| 4 | 0.404 (147 of 1870 days never flag) | 38 | 0.123 | 0.447 | 0.0604 | +0.0105 [+0.0060, +0.0147] | +0.0020 [-0.0022, +0.0060] | 0.830 | 0.111 | no |
| 5 | 0.409 (147 of 1869 days never flag) | 37 | 0.109 | 0.405 | 0.0610 | +0.0099 [+0.0057, +0.0142] | +0.0024 [-0.0016, +0.0066] | 0.807 | 0.096 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0522, +0.1165]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0251, +0.0500], realised minus predicted +0.0474 [+0.0134, +0.0833]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.147 | 0.385 | 0.2070 | 0.2720 | +0.0243 [+0.0027, +0.0472] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1466 | 0.0159 | +0.0179 [+0.0051, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0115 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0082 | 0.0200 | +0.0013 [-0.0040, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.500 | 0.1169 | 0.1165 | +0.0346 [+0.0041, +0.0739] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0095 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0725 | 0.0031 | +0.0243 [+0.0187, +0.0298] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.333 | 0.2169 | 0.4146 | 0.1034 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.154 | 0.391 | 0.2368 | 0.2474 | +0.0242 [+0.0045, +0.0482] |
| day_type | month_end | 150 | 17 | 0.118 | 0.667 | 0.1020 | 0.1133 | +0.0438 [+0.0246, +0.0700] |
| day_type | ordinary | 1603 | 101 | 0.119 | 0.300 | 0.0760 | 0.0630 | +0.0123 [+0.0067, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.222 | 0.667 | 0.1814 | 0.2903 | +0.0462 [-0.0262, +0.1137] |
| day_type | tax_date | 89 | 13 | 0.231 | 1.000 | 0.1291 | 0.1461 | +0.0556 [+0.0320, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0570 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2325 | 0.2213 |

## scarcity_logistic_regime_pooled (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.692] | 0.269 | 5.19 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.640] | 0.269 | 5.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.367 (147 of 1873 days never flag) | 218 | 0.650 | 0.417 | 0.0523 | +0.0191 [+0.0124, +0.0273] | +0.0040 [+0.0005, +0.0078] | 0.881 | 0.577 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 197 | 0.619 | 0.437 | 0.0583 | +0.0127 [+0.0070, +0.0186] | +0.0027 [-0.0011, +0.0068] | 0.851 | 0.555 | no |
| 3 | 0.38 (147 of 1871 days never flag) | 177 | 0.543 | 0.424 | 0.0601 | +0.0106 [+0.0054, +0.0155] | +0.0043 [+0.0004, +0.0083] | 0.840 | 0.485 | no |
| 4 | 0.406 (147 of 1870 days never flag) | 189 | 0.500 | 0.365 | 0.0600 | +0.0109 [+0.0058, +0.0158] | +0.0024 [-0.0020, +0.0069] | 0.838 | 0.431 | no |
| 5 | 0.409 (147 of 1869 days never flag) | 203 | 0.493 | 0.335 | 0.0608 | +0.0102 [+0.0049, +0.0153] | +0.0026 [-0.0018, +0.0075] | 0.822 | 0.415 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.519 (climatology 0.457, difference +0.0620 [-0.0393, +0.1796]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0405 [+0.0283, +0.0548], realised minus predicted +0.0470 [+0.0161, +0.0818]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.411 | 0.2178 | 0.2720 | +0.0267 [+0.0044, +0.0531] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1316 | 0.0159 | +0.0191 [+0.0048, +0.0319] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0092 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0085 | 0.0200 | +0.0037 [+0.0002, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.556 | 0.1162 | 0.1165 | +0.0394 [+0.0081, +0.0797] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0091 | 0.0048 | +0.0092 [+0.0077, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0512 | 0.0031 | +0.0270 [+0.0210, +0.0327] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.714 | 0.2459 | 0.4146 | 0.1326 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.405 | 0.2462 | 0.2474 | +0.0254 [+0.0036, +0.0495] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.0985 | 0.1133 | +0.0450 [+0.0229, +0.0707] |
| day_type | ordinary | 1603 | 101 | 0.634 | 0.368 | 0.0742 | 0.0630 | +0.0129 [+0.0066, +0.0205] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.2505 | 0.2903 | +0.0997 [+0.0463, +0.1541] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1255 | 0.1461 | +0.0585 [+0.0325, +0.0886] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0281 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2430 | 0.2213 |

## settlement_probit_scarcity (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 3.42 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.500] | 0.231 | 3.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.385 (126 of 1873 days never flag) | 147 | 0.529 | 0.503 | 0.0535 | +0.0179 [+0.0089, +0.0281] | +0.0028 [-0.0047, +0.0106] | 0.923 | 0.486 | no |
| 2 | 0.471 (126 of 1872 days never flag) | 99 | 0.295 | 0.414 | 0.0622 | +0.0089 [-0.0014, +0.0186] | -0.0011 [-0.0107, +0.0080] | 0.905 | 0.261 | no |
| 3 | 0.488 (126 of 1871 days never flag) | 136 | 0.341 | 0.346 | 0.0640 | +0.0067 [-0.0038, +0.0165] | +0.0004 [-0.0095, +0.0100] | 0.899 | 0.289 | no |
| 4 | 0.481 (126 of 1870 days never flag) | 116 | 0.304 | 0.362 | 0.0646 | +0.0063 [-0.0047, +0.0165] | -0.0022 [-0.0128, +0.0077] | 0.900 | 0.262 | no |
| 5 | 0.48 (147 of 1869 days never flag) | 74 | 0.239 | 0.446 | 0.0655 | +0.0054 [-0.0053, +0.0154] | -0.0021 [-0.0124, +0.0074] | 0.885 | 0.215 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.636 (climatology 0.457, difference +0.1787 [+0.0535, +0.2779]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0324, +0.0645], realised minus predicted +0.0380 [+0.0089, +0.0683]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.500 | 0.3490 | 0.2720 | +0.0285 [-0.0131, +0.0771] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0427 | 0.0159 | +0.0301 [+0.0185, +0.0415] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0000 | 0.0000 | +0.0138 [+0.0121, +0.0158] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0042 [-0.0001, +0.0076] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.778 | 0.0378 | 0.1165 | +0.0156 [+0.0008, +0.0359] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0013 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0233, +0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0341 | 0.4146 | 0.0031 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.497 | 0.3144 | 0.2474 | +0.0290 [-0.0056, +0.0683] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.0967 | 0.1133 | +0.0419 [+0.0201, +0.0654] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.447 | 0.0736 | 0.0630 | +0.0114 [+0.0018, +0.0224] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2752 | 0.2903 | +0.1034 [+0.0496, +0.1529] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1210 | 0.1461 | +0.0650 [+0.0296, +0.1032] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0015 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2291 | 0.2213 |

## settlement_probit_tga (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 2.81 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.151, 0.483] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.439 (126 of 1873 days never flag) | 137 | 0.457 | 0.467 | 0.0544 | +0.0171 [+0.0079, +0.0271] | +0.0020 [-0.0059, +0.0101] | 0.922 | 0.415 | no |
| 2 | 0.497 (147 of 1872 days never flag) | 82 | 0.281 | 0.476 | 0.0635 | +0.0076 [-0.0037, +0.0177] | -0.0024 [-0.0126, +0.0073] | 0.904 | 0.256 | no |
| 3 | 0.468 (147 of 1871 days never flag) | 96 | 0.297 | 0.427 | 0.0647 | +0.0060 [-0.0050, +0.0163] | -0.0004 [-0.0107, +0.0096] | 0.899 | 0.265 | no |
| 4 | 0.454 (147 of 1870 days never flag) | 101 | 0.333 | 0.455 | 0.0656 | +0.0052 [-0.0062, +0.0159] | -0.0032 [-0.0147, +0.0072] | 0.898 | 0.302 | no |
| 5 | 0.474 (147 of 1869 days never flag) | 107 | 0.333 | 0.430 | 0.0667 | +0.0043 [-0.0075, +0.0150] | -0.0033 [-0.0150, +0.0070] | 0.887 | 0.298 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.640 (climatology 0.457, difference +0.1830 [+0.0459, +0.2979]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0825, ΔBrier vs climatology +0.0470 [+0.0318, +0.0634], realised minus predicted +0.0364 [+0.0071, +0.0664]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.468 | 0.3571 | 0.2720 | +0.0233 [-0.0225, +0.0717] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0354 | 0.0159 | +0.0309 [+0.0201, +0.0412] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0034 | 0.0200 | +0.0046 [+0.0006, +0.0087] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0403 | 0.1165 | +0.0160 [+0.0007, +0.0369] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0002 | 0.0031 | +0.0302 [+0.0230, +0.0373] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0338 | 0.4146 | 0.0020 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.538 | 0.463 | 0.3175 | 0.2474 | +0.0258 [-0.0092, +0.0650] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1000 | 0.1133 | +0.0435 [+0.0208, +0.0656] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.404 | 0.0742 | 0.0630 | +0.0099 [-0.0001, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2874 | 0.2903 | +0.1101 [+0.0557, +0.1601] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1231 | 0.1461 | +0.0689 [+0.0346, +0.1082] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0013 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2648 | 0.2213 |

## settlement_probit_timing (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.783] | 0.269 | 5.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.314, 0.680] | 0.269 | 5.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.386 (126 of 1873 days never flag) | 214 | 0.586 | 0.383 | 0.0562 | +0.0153 [+0.0100, +0.0216] | +0.0002 [-0.0042, +0.0043] | 0.865 | 0.510 | no |
| 2 | 0.288 (147 of 1872 days never flag) | 232 | 0.662 | 0.397 | 0.0606 | +0.0104 [+0.0069, +0.0140] | +0.0004 [-0.0016, +0.0025] | 0.819 | 0.581 | no |
| 3 | 0.265 (147 of 1871 days never flag) | 225 | 0.609 | 0.373 | 0.0643 | +0.0064 [+0.0032, +0.0095] | +0.0001 [-0.0021, +0.0022] | 0.781 | 0.527 | no |
| 4 | 0.271 (147 of 1870 days never flag) | 198 | 0.507 | 0.354 | 0.0614 | +0.0095 [+0.0069, +0.0124] | +0.0010 [-0.0011, +0.0032] | 0.806 | 0.433 | no |
| 5 | 0.256 (147 of 1869 days never flag) | 188 | 0.507 | 0.372 | 0.0620 | +0.0089 [+0.0063, +0.0119] | +0.0014 [-0.0007, +0.0036] | 0.790 | 0.439 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 2.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.476 (climatology 0.457, difference +0.0188 [-0.0490, +0.0882]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1085, ΔBrier vs climatology +0.0209 [+0.0130, +0.0300], realised minus predicted +0.0095 [-0.0290, +0.0508]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.479 | 0.1678 | 0.2720 | +0.0381 [+0.0209, +0.0559] |
| regime | 2020 | 251 | 4 | 0.250 | 0.023 | 0.1515 | 0.0159 | -0.0066 [-0.0152, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0292 | 0.0000 | +0.0100 [+0.0088, +0.0113] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0353 | 0.0200 | +0.0035 [+0.0012, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.591 | 0.0915 | 0.1165 | +0.0304 [+0.0059, +0.0624] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0278 | 0.0048 | +0.0073 [+0.0060, +0.0086] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1096 | 0.0031 | -0.0018 [-0.0076, +0.0041] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.1910 | 0.4146 | 0.1008 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.441 | 0.1740 | 0.2474 | +0.0369 [+0.0213, +0.0539] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1376 | 0.1133 | +0.0236 [-0.0011, +0.0520] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.364 | 0.0641 | 0.0630 | +0.0133 [+0.0087, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.400 | 0.4897 | 0.2903 | -0.0068 [-0.0726, +0.0583] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.333 | 0.1783 | 0.1461 | +0.0444 [+0.0274, +0.0639] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0499 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2673 | 0.2213 |

## settlement_quantile_scarcity (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.630] | 0.262 | 4.54 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.591] | 0.235 | 4.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.399 (105 of 1873 days never flag) | 196 | 0.650 | 0.464 | 0.0478 | +0.0236 [+0.0148, +0.0337] | +0.0085 [+0.0025, +0.0152] | 0.931 | 0.589 | no |
| 2 | 0.388 (126 of 1872 days never flag) | 185 | 0.482 | 0.362 | 0.0588 | +0.0122 [+0.0045, +0.0199] | +0.0022 [-0.0044, +0.0087] | 0.893 | 0.414 | no |
| 3 | 0.419 (126 of 1871 days never flag) | 168 | 0.413 | 0.339 | 0.0594 | +0.0112 [+0.0029, +0.0192] | +0.0049 [-0.0030, +0.0123] | 0.905 | 0.349 | no |
| 4 | 0.369 (126 of 1870 days never flag) | 131 | 0.406 | 0.427 | 0.0586 | +0.0123 [+0.0047, +0.0203] | +0.0038 [-0.0034, +0.0115] | 0.894 | 0.362 | no |
| 5 | 0.356 (126 of 1869 days never flag) | 124 | 0.362 | 0.403 | 0.0575 | +0.0134 [+0.0061, +0.0207] | +0.0059 [-0.0014, +0.0132] | 0.892 | 0.320 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.603 (climatology 0.457, difference +0.1461 [-0.0273, +0.2957]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0773, ΔBrier vs climatology +0.0521 [+0.0361, +0.0692], realised minus predicted +0.0170 [-0.0082, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.706 | 0.474 | 0.3012 | 0.2720 | +0.0504 [+0.0145, +0.0914] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.0629 | 0.0159 | +0.0237 [+0.0104, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0119 | 0.0200 | +0.0019 [-0.0032, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.567 | 0.0961 | 0.1165 | +0.0350 [+0.0060, +0.0722] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0060 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0216 | 0.0031 | +0.0280 [+0.0219, +0.0343] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2780 | 0.4146 | +0.1264 [+0.0034, +0.2642] |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.463 | 0.2813 | 0.2474 | +0.0442 [+0.0138, +0.0788] |
| day_type | month_end | 150 | 17 | 0.824 | 0.636 | 0.1283 | 0.1133 | +0.0513 [+0.0192, +0.0837] |
| day_type | ordinary | 1603 | 101 | 0.624 | 0.417 | 0.0705 | 0.0630 | +0.0174 [+0.0089, +0.0271] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3063 | 0.2903 | +0.0652 [-0.0038, +0.1266] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1794 | 0.1461 | +0.0753 [+0.0330, +0.1188] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0127 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2641 | 0.2213 |

## settlement_quantile_tga (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.643] | 0.269 | 4.88 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.210, 0.571] | 0.231 | 3.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (105 of 1873 days never flag) | 191 | 0.600 | 0.440 | 0.0514 | +0.0200 [+0.0113, +0.0300] | +0.0049 [-0.0011, +0.0118] | 0.919 | 0.538 | no |
| 2 | 0.585 (126 of 1872 days never flag) | 186 | 0.424 | 0.317 | 0.0653 | +0.0058 [-0.0040, +0.0152] | -0.0042 [-0.0138, +0.0044] | 0.884 | 0.351 | no |
| 3 | 0.591 (126 of 1871 days never flag) | 126 | 0.297 | 0.325 | 0.0670 | +0.0037 [-0.0074, +0.0133] | -0.0026 [-0.0130, +0.0066] | 0.888 | 0.248 | no |
| 4 | 0.543 (126 of 1870 days never flag) | 128 | 0.341 | 0.367 | 0.0645 | +0.0064 [-0.0037, +0.0160] | -0.0021 [-0.0121, +0.0071] | 0.895 | 0.294 | no |
| 5 | 0.502 (126 of 1869 days never flag) | 129 | 0.348 | 0.372 | 0.0636 | +0.0073 [-0.0044, +0.0177] | -0.0002 [-0.0114, +0.0100] | 0.886 | 0.301 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.619 (climatology 0.457, difference +0.1618 [-0.0236, +0.3351]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0450 [+0.0248, +0.0667], realised minus predicted +0.0064 [-0.0228, +0.0363]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.466 | 0.3001 | 0.2720 | +0.0405 [+0.0038, +0.0837] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.0866 | 0.0159 | +0.0107 [-0.0133, +0.0304] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0112 | 0.0200 | +0.0024 [-0.0024, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.591 | 0.0956 | 0.1165 | +0.0352 [+0.0072, +0.0689] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0061 | 0.0048 | +0.0089 [+0.0071, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0438 | 0.0031 | +0.0169 [-0.0012, +0.0302] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.2645 | 0.4146 | 0.1292 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.650 | 0.461 | 0.2782 | 0.2474 | +0.0370 [+0.0070, +0.0725] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1375 | 0.1133 | +0.0425 [+0.0081, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.383 | 0.0732 | 0.0630 | +0.0141 [+0.0056, +0.0238] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3041 | 0.2903 | +0.0629 [-0.0058, +0.1227] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1746 | 0.1461 | +0.0726 [+0.0320, +0.1167] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0086 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2670 | 0.2213 |

## settlement_quantile_timing (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.778] | 0.337 | 6.38 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.336 | 6.38 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.298 (105 of 1873 days never flag) | 242 | 0.686 | 0.397 | 0.0524 | +0.0190 [+0.0117, +0.0277] | +0.0039 [-0.0008, +0.0091] | 0.914 | 0.601 | no |
| 2 | 0.296 (147 of 1872 days never flag) | 263 | 0.719 | 0.380 | 0.0583 | +0.0128 [+0.0074, +0.0188] | +0.0028 [-0.0001, +0.0063] | 0.887 | 0.625 | no |
| 3 | 0.302 (147 of 1871 days never flag) | 257 | 0.710 | 0.381 | 0.0602 | +0.0105 [+0.0059, +0.0160] | +0.0042 [+0.0009, +0.0079] | 0.874 | 0.618 | no |
| 4 | 0.319 (147 of 1870 days never flag) | 257 | 0.659 | 0.354 | 0.0619 | +0.0089 [+0.0047, +0.0137] | +0.0005 [-0.0024, +0.0033] | 0.854 | 0.564 | no |
| 5 | 0.302 (147 of 1869 days never flag) | 244 | 0.580 | 0.328 | 0.0622 | +0.0087 [+0.0043, +0.0136] | +0.0012 [-0.0017, +0.0041] | 0.840 | 0.485 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 4.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1214 [+0.0387, +0.2067]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1015, ΔBrier vs climatology +0.0280 [+0.0163, +0.0425], realised minus predicted +0.0144 [-0.0178, +0.0483]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.755 | 0.464 | 0.1923 | 0.2720 | +0.0522 [+0.0263, +0.0803] |
| regime | 2020 | 251 | 4 | 0.250 | 0.032 | 0.1024 | 0.0159 | +0.0049 [-0.0050, +0.0149] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0197 | 0.0000 | +0.0093 [+0.0083, +0.0105] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0289 | 0.0200 | -0.0011 [-0.0082, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.586 | 0.1179 | 0.1165 | +0.0320 [+0.0001, +0.0721] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.083 | 0.0209 | 0.0048 | +0.0056 [+0.0034, +0.0073] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0726 | 0.0031 | +0.0068 [+0.0010, +0.0130] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.667 | 0.3122 | 0.4146 | 0.1245 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.455 | 0.1927 | 0.2474 | +0.0475 [+0.0250, +0.0713] |
| day_type | month_end | 150 | 17 | 0.882 | 0.577 | 0.1291 | 0.1133 | +0.0337 [+0.0033, +0.0676] |
| day_type | ordinary | 1603 | 101 | 0.653 | 0.375 | 0.0600 | 0.0630 | +0.0165 [+0.0096, +0.0247] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.333 | 0.5501 | 0.2903 | -0.0228 [-0.0831, +0.0330] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.421 | 0.1846 | 0.1461 | +0.0523 [+0.0344, +0.0732] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2841 | 0.2213 |

## settlement_quantile_timing_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.448, 0.778] | 0.231 | 2.85 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.639] | 0.231 | 2.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.298 (105 of 1873 days never flag) | 104 | 0.286 | 0.385 | 0.0524 | +0.0190 [+0.0113, +0.0273] | +0.0039 [-0.0008, +0.0088] | 0.914 | 0.249 | no |
| 2 | 0.296 (147 of 1872 days never flag) | 89 | 0.187 | 0.292 | 0.0583 | +0.0128 [+0.0075, +0.0188] | +0.0028 [-0.0004, +0.0065] | 0.887 | 0.151 | no |
| 3 | 0.302 (147 of 1871 days never flag) | 90 | 0.203 | 0.311 | 0.0602 | +0.0105 [+0.0057, +0.0159] | +0.0042 [+0.0008, +0.0079] | 0.874 | 0.167 | no |
| 4 | 0.319 (147 of 1870 days never flag) | 107 | 0.239 | 0.308 | 0.0619 | +0.0089 [+0.0046, +0.0139] | +0.0005 [-0.0023, +0.0035] | 0.854 | 0.196 | no |
| 5 | 0.302 (147 of 1869 days never flag) | 109 | 0.283 | 0.358 | 0.0622 | +0.0087 [+0.0043, +0.0136] | +0.0012 [-0.0017, +0.0040] | 0.840 | 0.242 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1214 [+0.0403, +0.2055]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1015, ΔBrier vs climatology +0.0280 [+0.0161, +0.0419], realised minus predicted +0.0144 [-0.0186, +0.0499]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.607 | 0.1923 | 0.2720 | +0.0522 [+0.0263, +0.0816] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.1024 | 0.0159 | +0.0049 [-0.0049, +0.0149] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0197 | 0.0000 | +0.0093 [+0.0082, +0.0105] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0289 | 0.0200 | -0.0011 [-0.0075, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.556 | 0.1179 | 0.1165 | +0.0320 [+0.0010, +0.0717] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0209 | 0.0048 | +0.0056 [+0.0036, +0.0073] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0726 | 0.0031 | +0.0068 [+0.0011, +0.0126] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.3122 | 0.4146 | 0.1245 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.316 | 0.552 | 0.1927 | 0.2474 | +0.0475 [+0.0245, +0.0733] |
| day_type | month_end | 150 | 17 | 0.588 | 0.526 | 0.1291 | 0.1133 | +0.0337 [+0.0038, +0.0676] |
| day_type | ordinary | 1603 | 101 | 0.228 | 0.377 | 0.0600 | 0.0630 | +0.0165 [+0.0094, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.176 | 0.5501 | 0.2903 | -0.0228 [-0.0776, +0.0348] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.571 | 0.1846 | 0.1461 | +0.0523 [+0.0342, +0.0708] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2841 | 0.2213 |

## settlement_quantile_timing_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.217, 0.548] | 0.192 | 2.19 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 6 | 0.231 [0.091, 0.393] | 0.192 | 1.81 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.298 (105 of 1873 days never flag) | 84 | 0.193 | 0.321 | 0.0524 | +0.0190 [+0.0112, +0.0276] | +0.0039 [-0.0006, +0.0088] | 0.914 | 0.160 | no |
| 2 | 0.296 (147 of 1872 days never flag) | 64 | 0.151 | 0.328 | 0.0583 | +0.0128 [+0.0073, +0.0187] | +0.0028 [-0.0004, +0.0062] | 0.887 | 0.126 | no |
| 3 | 0.302 (147 of 1871 days never flag) | 64 | 0.152 | 0.328 | 0.0602 | +0.0105 [+0.0057, +0.0154] | +0.0042 [+0.0009, +0.0076] | 0.874 | 0.127 | no |
| 4 | 0.319 (147 of 1870 days never flag) | 67 | 0.152 | 0.313 | 0.0619 | +0.0089 [+0.0046, +0.0135] | +0.0005 [-0.0022, +0.0032] | 0.854 | 0.126 | no |
| 5 | 0.302 (147 of 1869 days never flag) | 63 | 0.116 | 0.254 | 0.0622 | +0.0087 [+0.0043, +0.0132] | +0.0012 [-0.0018, +0.0041] | 0.840 | 0.089 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1214 [+0.0419, +0.2076]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1015, ΔBrier vs climatology +0.0280 [+0.0159, +0.0415], realised minus predicted +0.0144 [-0.0186, +0.0480]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.206 | 0.553 | 0.1923 | 0.2720 | +0.0522 [+0.0262, +0.0805] |
| regime | 2020 | 251 | 4 | 0.250 | 0.043 | 0.1024 | 0.0159 | +0.0049 [-0.0055, +0.0149] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0197 | 0.0000 | +0.0093 [+0.0082, +0.0105] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0289 | 0.0200 | -0.0011 [-0.0076, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.556 | 0.1179 | 0.1165 | +0.0320 [-0.0001, +0.0717] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0209 | 0.0048 | +0.0056 [+0.0035, +0.0073] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0726 | 0.0031 | +0.0068 [+0.0006, +0.0128] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.3122 | 0.4146 | 0.1245 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.205 | 0.511 | 0.1927 | 0.2474 | +0.0475 [+0.0247, +0.0724] |
| day_type | month_end | 150 | 17 | 0.471 | 0.471 | 0.1291 | 0.1133 | +0.0337 [+0.0018, +0.0669] |
| day_type | ordinary | 1603 | 101 | 0.119 | 0.279 | 0.0600 | 0.0630 | +0.0165 [+0.0092, +0.0248] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.176 | 0.5501 | 0.2903 | -0.0228 [-0.0796, +0.0327] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.571 | 0.1846 | 0.1461 | +0.0523 [+0.0339, +0.0714] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2841 | 0.2213 |

## stack_equal_average (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.433, 0.790] | 0.269 | 5.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.629] | 0.238 | 4.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.286 (126 of 1873 days never flag) | 215 | 0.600 | 0.391 | 0.0476 | +0.0238 [+0.0175, +0.0311] | +0.0088 [+0.0043, +0.0136] | 0.927 | 0.524 | no |
| 2 | 0.334 (147 of 1872 days never flag) | 159 | 0.468 | 0.409 | 0.0545 | +0.0166 [+0.0116, +0.0223] | +0.0066 [+0.0018, +0.0118] | 0.900 | 0.413 | no |
| 3 | 0.324 (147 of 1871 days never flag) | 168 | 0.493 | 0.405 | 0.0558 | +0.0149 [+0.0099, +0.0196] | +0.0086 [+0.0043, +0.0132] | 0.894 | 0.435 | no |
| 4 | 0.308 (147 of 1870 days never flag) | 168 | 0.478 | 0.393 | 0.0566 | +0.0143 [+0.0096, +0.0191] | +0.0058 [+0.0012, +0.0105] | 0.891 | 0.419 | no |
| 5 | 0.32 (147 of 1869 days never flag) | 178 | 0.478 | 0.371 | 0.0573 | +0.0137 [+0.0092, +0.0185] | +0.0061 [+0.0014, +0.0111] | 0.879 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.457, difference +0.1392 [+0.0354, +0.2298]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0843, ΔBrier vs climatology +0.0451 [+0.0335, +0.0576], realised minus predicted +0.0649 [+0.0338, +0.0993]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.706 | 0.373 | 0.2538 | 0.2720 | +0.0496 [+0.0218, +0.0802] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0659 | 0.0159 | +0.0349 [+0.0269, +0.0431] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0020 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0032 | 0.0200 | +0.0027 [-0.0012, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0500 | 0.1165 | +0.0254 [+0.0089, +0.0454] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0025 | 0.0048 | +0.0092 [+0.0075, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0220 | 0.0031 | +0.0299 [+0.0239, +0.0359] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0876 | 0.4146 | 0.0485 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.382 | 0.2393 | 0.2474 | +0.0497 [+0.0275, +0.0757] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.0891 | 0.1133 | +0.0407 [+0.0258, +0.0569] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.335 | 0.0611 | 0.0630 | +0.0180 [+0.0118, +0.0254] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.1957 | 0.2903 | +0.1165 [+0.0613, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1023 | 0.1461 | +0.0676 [+0.0472, +0.0907] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0656 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2254 | 0.2213 |

## stacked_ensemble (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.786] | 0.269 | 5.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.195, 0.576] | 0.269 | 4.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.36 (126 of 1873 days never flag) | 226 | 0.607 | 0.376 | 0.0508 | +0.0207 [+0.0136, +0.0286] | +0.0056 [+0.0008, +0.0102] | 0.926 | 0.526 | no |
| 2 | 0.335 (147 of 1872 days never flag) | 180 | 0.532 | 0.411 | 0.0569 | +0.0142 [+0.0087, +0.0199] | +0.0042 [-0.0009, +0.0093] | 0.906 | 0.471 | no |
| 3 | 0.352 (147 of 1871 days never flag) | 165 | 0.449 | 0.376 | 0.0578 | +0.0129 [+0.0081, +0.0183] | +0.0066 [+0.0020, +0.0113] | 0.903 | 0.390 | no |
| 4 | 0.307 (147 of 1870 days never flag) | 150 | 0.420 | 0.387 | 0.0593 | +0.0116 [+0.0065, +0.0165] | +0.0031 [-0.0017, +0.0078] | 0.897 | 0.367 | no |
| 5 | 0.499 (147 of 1869 days never flag) | 204 | 0.587 | 0.397 | 0.0605 | +0.0104 [+0.0039, +0.0165] | +0.0029 [-0.0034, +0.0090] | 0.881 | 0.516 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.457, difference +0.1561 [+0.0650, +0.2699]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0834, ΔBrier vs climatology +0.0461 [+0.0327, +0.0612], realised minus predicted +0.0532 [+0.0230, +0.0862]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.359 | 0.2945 | 0.2720 | +0.0292 [-0.0012, +0.0634] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0539 | 0.0159 | +0.0330 [+0.0230, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0004 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0024 | 0.0200 | +0.0036 [-0.0003, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.619 | 0.0680 | 0.1165 | +0.0331 [+0.0101, +0.0622] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0015 | 0.0048 | +0.0093 [+0.0077, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0136 | 0.0031 | +0.0300 [+0.0238, +0.0356] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.0999 | 0.4146 | 0.0677 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.367 | 0.2785 | 0.2474 | +0.0350 [+0.0082, +0.0644] |
| day_type | month_end | 150 | 17 | 0.765 | 0.619 | 0.1004 | 0.1133 | +0.0509 [+0.0295, +0.0763] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.324 | 0.0703 | 0.0630 | +0.0144 [+0.0074, +0.0227] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.1924 | 0.2903 | +0.1053 [+0.0220, +0.1853] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.538 | 0.0902 | 0.1461 | +0.0520 [+0.0354, +0.0690] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3616 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.2167 | 0.2213 |

## time_to_pressure_hazard (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 9 | 0.346 [0.185, 0.526] | 0.231 | 3.77 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.176, 0.526] | 0.231 | 3.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.372 (147 of 1873 days never flag) | 162 | 0.521 | 0.451 | 0.0553 | +0.0161 [+0.0088, +0.0243] | +0.0010 [-0.0058, +0.0079] | 0.915 | 0.470 | no |
| 2 | 0.372 (147 of 1872 days never flag) | 146 | 0.460 | 0.438 | 0.0576 | +0.0135 [+0.0066, +0.0206] | +0.0035 [-0.0036, +0.0103] | 0.907 | 0.413 | no |
| 3 | 0.394 (147 of 1871 days never flag) | 158 | 0.435 | 0.380 | 0.0595 | +0.0112 [+0.0043, +0.0179] | +0.0049 [-0.0023, +0.0115] | 0.902 | 0.378 | no |
| 4 | 0.396 (147 of 1870 days never flag) | 158 | 0.442 | 0.386 | 0.0594 | +0.0114 [+0.0049, +0.0187] | +0.0030 [-0.0041, +0.0100] | 0.899 | 0.386 | no |
| 5 | 0.383 (147 of 1869 days never flag) | 138 | 0.399 | 0.399 | 0.0599 | +0.0110 [+0.0050, +0.0172] | +0.0035 [-0.0033, +0.0098] | 0.895 | 0.351 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.584 (climatology 0.457, difference +0.1267 [-0.0172, +0.2577]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0896, ΔBrier vs climatology +0.0398 [+0.0261, +0.0552], realised minus predicted +0.0608 [+0.0310, +0.0944]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.461 | 0.3017 | 0.2720 | +0.0265 [-0.0081, +0.0667] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0437 | 0.0159 | +0.0338 [+0.0237, +0.0442] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0019 [-0.0027, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.069 | 0.667 | 0.0194 | 0.1165 | +0.0036 [-0.0037, +0.0115] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0009 | 0.0048 | +0.0090 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0009 | 0.0031 | +0.0302 [+0.0229, +0.0368] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0238 | 0.4146 | -0.0167 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.451 | 0.2690 | 0.2474 | +0.0248 [-0.0027, +0.0571] |
| day_type | month_end | 150 | 17 | 0.529 | 0.500 | 0.0899 | 0.1133 | +0.0209 [+0.0056, +0.0349] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.413 | 0.0620 | 0.0630 | +0.0119 [+0.0047, +0.0203] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2200 | 0.2903 | +0.0928 [+0.0465, +0.1330] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1093 | 0.1461 | +0.0565 [+0.0216, +0.0945] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2811 | 0.2213 |

## two_part_gbm (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.762] | 0.269 | 4.81 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.364, 0.720] | 0.269 | 4.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.281 (147 of 1873 days never flag) | 121 | 0.486 | 0.562 | 0.0495 | +0.0219 [+0.0146, +0.0303] | +0.0068 [+0.0017, +0.0125] | 0.911 | 0.455 | yes |
| 2 | 0.363 (126 of 1872 days never flag) | 169 | 0.482 | 0.396 | 0.0591 | +0.0119 [+0.0044, +0.0193] | +0.0019 [-0.0049, +0.0086] | 0.881 | 0.423 | no |
| 3 | 0.358 (126 of 1871 days never flag) | 184 | 0.529 | 0.397 | 0.0602 | +0.0105 [+0.0025, +0.0178] | +0.0042 [-0.0031, +0.0109] | 0.883 | 0.465 | no |
| 4 | 0.393 (147 of 1870 days never flag) | 90 | 0.261 | 0.400 | 0.0635 | +0.0073 [-0.0004, +0.0163] | -0.0011 [-0.0085, +0.0067] | 0.874 | 0.230 | no |
| 5 | 0.504 (126 of 1869 days never flag) | 178 | 0.384 | 0.298 | 0.0685 | +0.0024 [-0.0059, +0.0108] | -0.0051 [-0.0132, +0.0029] | 0.844 | 0.312 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.540 (climatology 0.457, difference +0.0829 [-0.0632, +0.1874]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0331, +0.0638], realised minus predicted +0.0425 [+0.0124, +0.0750]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.529 | 0.574 | 0.2651 | 0.2720 | +0.0459 [+0.0147, +0.0821] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0232 | 0.0159 | +0.0338 [+0.0187, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0016 [-0.0029, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.591 | 0.0659 | 0.1165 | +0.0185 [-0.0013, +0.0446] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0089 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0232, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0476 | 0.4146 | +0.0277 [-0.0127, +0.0727] |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.555 | 0.2521 | 0.2474 | +0.0441 [+0.0167, +0.0753] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.0938 | 0.1133 | +0.0499 [+0.0247, +0.0784] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.511 | 0.0587 | 0.0630 | +0.0149 [+0.0077, +0.0231] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1546 | 0.2903 | +0.1213 [+0.0296, +0.2096] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1012 | 0.1461 | +0.0672 [+0.0447, +0.0923] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0436 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2258 | 0.2213 |

## two_part_gbm_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.387, 0.759] | 0.192 | 2.00 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 14 | 0.538 [0.357, 0.720] | 0.192 | 2.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.281 (147 of 1873 days never flag) | 54 | 0.243 | 0.630 | 0.0495 | +0.0219 [+0.0145, +0.0305] | +0.0068 [+0.0015, +0.0120] | 0.911 | 0.231 | yes |
| 2 | 0.363 (126 of 1872 days never flag) | 68 | 0.187 | 0.382 | 0.0591 | +0.0119 [+0.0041, +0.0192] | +0.0019 [-0.0048, +0.0082] | 0.881 | 0.163 | no |
| 3 | 0.358 (126 of 1871 days never flag) | 80 | 0.275 | 0.475 | 0.0602 | +0.0105 [+0.0023, +0.0183] | +0.0042 [-0.0033, +0.0112] | 0.883 | 0.251 | no |
| 4 | 0.393 (147 of 1870 days never flag) | 42 | 0.138 | 0.452 | 0.0635 | +0.0073 [-0.0012, +0.0161] | -0.0011 [-0.0087, +0.0070] | 0.874 | 0.124 | no |
| 5 | 0.504 (126 of 1869 days never flag) | 75 | 0.167 | 0.307 | 0.0685 | +0.0024 [-0.0060, +0.0104] | -0.0051 [-0.0135, +0.0027] | 0.844 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.540 (climatology 0.457, difference +0.0829 [-0.0657, +0.1850]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0324, +0.0635], realised minus predicted +0.0425 [+0.0131, +0.0739]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.245 | 0.641 | 0.2651 | 0.2720 | +0.0459 [+0.0138, +0.0815] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0232 | 0.0159 | +0.0338 [+0.0192, +0.0458] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0016 [-0.0032, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0659 | 0.1165 | +0.0185 [-0.0033, +0.0459] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0089 [+0.0072, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0231, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0476 | 0.4146 | +0.0277 [-0.0117, +0.0722] |
| scarcity_state | 3 | 473 | 117 | 0.282 | 0.623 | 0.2521 | 0.2474 | +0.0441 [+0.0170, +0.0748] |
| day_type | month_end | 150 | 17 | 0.235 | 0.571 | 0.0938 | 0.1133 | +0.0499 [+0.0244, +0.0793] |
| day_type | ordinary | 1603 | 101 | 0.228 | 0.622 | 0.0587 | 0.0630 | +0.0149 [+0.0075, +0.0234] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.750 | 0.1546 | 0.2903 | +0.1213 [+0.0289, +0.2029] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.667 | 0.1012 | 0.1461 | +0.0672 [+0.0441, +0.0921] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0436 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2258 | 0.2213 |

## two_part_gbm_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.235, 0.600] | 0.115 | 1.12 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 6 | 0.231 [0.105, 0.375] | 0.115 | 1.12 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.281 (147 of 1873 days never flag) | 35 | 0.143 | 0.571 | 0.0495 | +0.0219 [+0.0143, +0.0298] | +0.0068 [+0.0014, +0.0124] | 0.911 | 0.134 | yes |
| 2 | 0.363 (126 of 1872 days never flag) | 40 | 0.137 | 0.475 | 0.0591 | +0.0119 [+0.0042, +0.0195] | +0.0019 [-0.0051, +0.0084] | 0.881 | 0.125 | no |
| 3 | 0.358 (126 of 1871 days never flag) | 40 | 0.130 | 0.450 | 0.0602 | +0.0105 [+0.0025, +0.0183] | +0.0042 [-0.0034, +0.0113] | 0.883 | 0.118 | no |
| 4 | 0.393 (147 of 1870 days never flag) | 25 | 0.058 | 0.320 | 0.0635 | +0.0073 [-0.0012, +0.0162] | -0.0011 [-0.0090, +0.0067] | 0.874 | 0.048 | no |
| 5 | 0.504 (126 of 1869 days never flag) | 37 | 0.058 | 0.216 | 0.0685 | +0.0024 [-0.0059, +0.0109] | -0.0051 [-0.0134, +0.0030] | 0.844 | 0.041 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.540 (climatology 0.457, difference +0.0829 [-0.0641, +0.1877]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0321, +0.0645], realised minus predicted +0.0425 [+0.0134, +0.0754]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.147 | 0.577 | 0.2651 | 0.2720 | +0.0459 [+0.0125, +0.0792] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0232 | 0.0159 | +0.0338 [+0.0187, +0.0464] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0016 [-0.0030, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.667 | 0.0659 | 0.1165 | +0.0185 [-0.0020, +0.0447] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0089 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0232, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0476 | 0.4146 | +0.0277 [-0.0122, +0.0760] |
| scarcity_state | 3 | 473 | 117 | 0.162 | 0.559 | 0.2521 | 0.2474 | +0.0441 [+0.0154, +0.0734] |
| day_type | month_end | 150 | 17 | 0.118 | 0.400 | 0.0938 | 0.1133 | +0.0499 [+0.0226, +0.0773] |
| day_type | ordinary | 1603 | 101 | 0.129 | 0.542 | 0.0587 | 0.0630 | +0.0149 [+0.0073, +0.0229] |
| day_type | quarter_end | 31 | 9 | 0.222 | 0.667 | 0.1546 | 0.2903 | +0.1213 [+0.0315, +0.2074] |
| day_type | tax_date | 89 | 13 | 0.231 | 1.000 | 0.1012 | 0.1461 | +0.0672 [+0.0436, +0.0920] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0436 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2258 | 0.2213 |

## two_part_logistic (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.727] | 0.231 | 3.96 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.150, 0.486] | 0.231 | 2.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.332 (126 of 1873 days never flag) | 185 | 0.586 | 0.443 | 0.0511 | +0.0203 [+0.0128, +0.0280] | +0.0052 [-0.0017, +0.0115] | 0.924 | 0.526 | no |
| 2 | 0.423 (147 of 1872 days never flag) | 129 | 0.432 | 0.465 | 0.0579 | +0.0131 [+0.0066, +0.0206] | +0.0031 [-0.0034, +0.0103] | 0.904 | 0.392 | no |
| 3 | 0.434 (147 of 1871 days never flag) | 128 | 0.406 | 0.438 | 0.0598 | +0.0108 [+0.0039, +0.0183] | +0.0045 [-0.0020, +0.0114] | 0.899 | 0.364 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 126 | 0.391 | 0.429 | 0.0597 | +0.0112 [+0.0042, +0.0183] | +0.0027 [-0.0037, +0.0101] | 0.899 | 0.350 | no |
| 5 | 0.446 (147 of 1869 days never flag) | 113 | 0.355 | 0.434 | 0.0605 | +0.0104 [+0.0039, +0.0177] | +0.0029 [-0.0037, +0.0101] | 0.890 | 0.318 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.457, difference +0.1361 [+0.0049, +0.2488]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0863, ΔBrier vs climatology +0.0431 [+0.0290, +0.0597], realised minus predicted +0.0508 [+0.0219, +0.0853]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.442 | 0.2998 | 0.2720 | +0.0463 [+0.0111, +0.0810] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0459 | 0.0159 | +0.0297 [+0.0176, +0.0403] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0015 | 0.0200 | +0.0027 [-0.0007, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0238 | 0.1165 | +0.0090 [+0.0010, +0.0201] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0010 | 0.0048 | +0.0092 [+0.0075, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0018 | 0.0031 | +0.0302 [+0.0233, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0409 | 0.4146 | 0.0118 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.684 | 0.437 | 0.2687 | 0.2474 | +0.0387 [+0.0106, +0.0671] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.0869 | 0.1133 | +0.0301 [+0.0096, +0.0506] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.391 | 0.0617 | 0.0630 | +0.0155 [+0.0080, +0.0234] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2820 | 0.2903 | +0.0930 [+0.0431, +0.1368] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1101 | 0.1461 | +0.0648 [+0.0325, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0068 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2345 | 0.2213 |

## window_onset_gbm+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.348, 0.731] | 0.269 | 4.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.269, 0.650] | 0.269 | 4.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.656 (126 of 1873 days never flag) | 171 | 0.364 | 0.298 | 0.0908 | -0.0194 [-0.0328, -0.0067] | -0.0345 [-0.0486, -0.0218] | 0.737 | 0.295 | no |
| 2 | 0.656 (126 of 1872 days never flag) | 167 | 0.367 | 0.305 | 0.0896 | -0.0186 [-0.0331, -0.0055] | -0.0286 [-0.0431, -0.0152] | 0.750 | 0.300 | no |
| 3 | 0.641 (126 of 1871 days never flag) | 183 | 0.406 | 0.306 | 0.0879 | -0.0172 [-0.0316, -0.0040] | -0.0235 [-0.0379, -0.0101] | 0.753 | 0.333 | no |
| 4 | 0.641 (147 of 1870 days never flag) | 138 | 0.333 | 0.333 | 0.0892 | -0.0184 [-0.0329, -0.0057] | -0.0268 [-0.0418, -0.0136] | 0.744 | 0.280 | no |
| 5 | 0.697 (147 of 1869 days never flag) | 149 | 0.333 | 0.309 | 0.0912 | -0.0203 [-0.0346, -0.0077] | -0.0279 [-0.0425, -0.0147] | 0.723 | 0.274 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.527 (climatology 0.457, difference +0.0701 [-0.0229, +0.1552]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1148, ΔBrier vs climatology +0.0147 [+0.0022, +0.0273], realised minus predicted -0.0046 [-0.0466, +0.0403]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.312 | 0.3290 | 0.2720 | -0.0556 [-0.1009, -0.0109] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.3543 | 0.0159 | -0.0970 [-0.1486, -0.0532] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0694 | 0.0000 | +0.0071 [+0.0059, +0.0085] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0262 | 0.0200 | +0.0011 [-0.0034, +0.0044] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0952 | 0.1165 | +0.0130 [-0.0067, +0.0379] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0521 | 0.0048 | +0.0046 [+0.0026, +0.0063] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.2067 | 0.0031 | -0.0270 [-0.0452, -0.0107] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1786 | 0.4146 | 0.0530 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.436 | 0.298 | 0.3514 | 0.2474 | -0.0731 [-0.1182, -0.0301] |
| day_type | month_end | 150 | 17 | 0.471 | 0.421 | 0.1886 | 0.1133 | +0.0015 [-0.0214, +0.0264] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.250 | 0.1558 | 0.0630 | -0.0268 [-0.0414, -0.0135] |
| day_type | quarter_end | 31 | 9 | 0.222 | 1.000 | 0.1319 | 0.2903 | +0.0473 [-0.0445, +0.1372] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.1384 | 0.1461 | +0.0555 [+0.0250, +0.0975] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.3650 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2651 | 0.2213 |

## window_onset_hierarchical_logistic+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.731] | 0.301 | 6.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.310, 0.688] | 0.301 | 6.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (105 of 1873 days never flag) | 215 | 0.521 | 0.340 | 0.0843 | -0.0129 [-0.0284, +0.0014] | -0.0280 [-0.0429, -0.0147] | 0.800 | 0.439 | no |
| 2 | 0.675 (126 of 1872 days never flag) | 213 | 0.511 | 0.333 | 0.0848 | -0.0137 [-0.0294, +0.0003] | -0.0237 [-0.0400, -0.0109] | 0.804 | 0.429 | no |
| 3 | 0.677 (147 of 1871 days never flag) | 193 | 0.507 | 0.363 | 0.0846 | -0.0139 [-0.0295, +0.0001] | -0.0202 [-0.0356, -0.0070] | 0.816 | 0.436 | no |
| 4 | 0.676 (147 of 1870 days never flag) | 200 | 0.493 | 0.340 | 0.0869 | -0.0161 [-0.0317, -0.0022] | -0.0245 [-0.0401, -0.0108] | 0.801 | 0.417 | no |
| 5 | 0.675 (147 of 1869 days never flag) | 224 | 0.478 | 0.295 | 0.0879 | -0.0170 [-0.0325, -0.0035] | -0.0245 [-0.0398, -0.0114] | 0.798 | 0.387 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.502 (climatology 0.457, difference +0.0444 [-0.0660, +0.1591]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1095, ΔBrier vs climatology +0.0199 [+0.0032, +0.0383], realised minus predicted +0.0082 [-0.0337, +0.0509]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.328 | 0.2795 | 0.2720 | -0.0386 [-0.0820, -0.0006] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.3637 | 0.0159 | -0.1095 [-0.1679, -0.0550] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0353 | 0.0000 | +0.0116 [+0.0101, +0.0132] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0169 | 0.0200 | +0.0023 [-0.0013, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.1787 | 0.1165 | +0.0344 [-0.0038, +0.0824] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0269 | 0.0048 | +0.0082 [+0.0066, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1922 | 0.0031 | -0.0191 [-0.0375, -0.0036] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.3989 | 0.4146 | 0.1203 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.590 | 0.329 | 0.3483 | 0.2474 | -0.0663 [-0.1159, -0.0200] |
| day_type | month_end | 150 | 17 | 0.824 | 0.500 | 0.1865 | 0.1133 | +0.0136 [-0.0190, +0.0512] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.294 | 0.1407 | 0.0630 | -0.0189 [-0.0350, -0.0046] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.750 | 0.2063 | 0.2903 | +0.0519 [-0.0215, +0.1225] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.667 | 0.1268 | 0.1461 | +0.0282 [+0.0077, +0.0475] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3760 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2537 | 0.2213 |

