# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `70b26e00e643…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

## calendar_climatology (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.212, 0.576] | 0.269 | 5.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.286 (105 of 1873 days never flag) | 198 | 0.514 | 0.364 | 0.0714 | +0.0000 [+0.0000, +0.0000] | -0.0151 [-0.0211, -0.0097] | 0.586 | 0.442 | no |
| 2 | 0.286 (147 of 1872 days never flag) | 196 | 0.496 | 0.352 | 0.0711 | +0.0000 [+0.0000, +0.0000] | -0.0100 [-0.0146, -0.0054] | 0.586 | 0.423 | no |
| 3 | 0.286 (147 of 1871 days never flag) | 196 | 0.493 | 0.347 | 0.0707 | +0.0000 [+0.0000, +0.0000] | -0.0063 [-0.0098, -0.0028] | 0.585 | 0.419 | no |
| 4 | 0.286 (147 of 1870 days never flag) | 196 | 0.486 | 0.342 | 0.0708 | +0.0000 [+0.0000, +0.0000] | -0.0085 [-0.0120, -0.0048] | 0.580 | 0.411 | no |
| 5 | 0.286 (147 of 1869 days never flag) | 196 | 0.478 | 0.337 | 0.0709 | +0.0000 [+0.0000, +0.0000] | -0.0075 [-0.0114, -0.0036] | 0.578 | 0.403 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.457 (climatology 0.457, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1757, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0470 [-0.1017, +0.0117]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.436 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0645 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0907 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1572 | 0.0031 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0728 | 0.4146 | 0.0000 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.424 | 0.1413 | 0.2474 | +0.0000 [+0.0000, +0.0000] |
| day_type | month_end | 150 | 17 | 0.529 | 0.375 | 0.1364 | 0.1133 | +0.0000 [+0.0000, +0.0000] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.398 | 0.1006 | 0.0630 | +0.0000 [+0.0000, +0.0000] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.250 | 0.4089 | 0.2903 | +0.0000 [+0.0000, +0.0000] |
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
| lead_at_least_1 | 26 | 7 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.107, 0.448] | 0.231 | 3.15 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.285 (210 of 1873 days never flag) | 133 | 0.436 | 0.459 | 0.0563 | +0.0151 [+0.0094, +0.0214] | +0.0000 [+0.0000, +0.0000] | 0.876 | 0.394 | no |
| 2 | 0.258 (147 of 1872 days never flag) | 170 | 0.583 | 0.476 | 0.0611 | +0.0100 [+0.0056, +0.0146] | +0.0000 [+0.0000, +0.0000] | 0.817 | 0.531 | no |
| 3 | 0.255 (189 of 1871 days never flag) | 120 | 0.341 | 0.392 | 0.0644 | +0.0063 [+0.0030, +0.0098] | +0.0000 [+0.0000, +0.0000] | 0.765 | 0.298 | no |
| 4 | 0.251 (232 of 1870 days never flag) | 141 | 0.428 | 0.418 | 0.0624 | +0.0085 [+0.0047, +0.0121] | +0.0000 [+0.0000, +0.0000] | 0.788 | 0.380 | no |
| 5 | 0.323 (315 of 1869 days never flag) | 127 | 0.391 | 0.425 | 0.0634 | +0.0075 [+0.0036, +0.0114] | +0.0000 [+0.0000, +0.0000] | 0.772 | 0.349 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.477 (climatology 0.457, difference +0.0203 [-0.0817, +0.1399]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0510, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.451 | 0.455 | 0.1679 | 0.2720 | +0.0168 [-0.0027, +0.0376] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.0978 | 0.1165 | +0.0256 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0233 | 0.0048 | +0.0080 [+0.0059, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0891 | 0.0031 | +0.0206 [+0.0144, +0.0267] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2311 | 0.4146 | 0.0897 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.453 | 0.457 | 0.1759 | 0.2474 | +0.0203 [+0.0030, +0.0386] |
| day_type | month_end | 150 | 17 | 0.412 | 0.583 | 0.0778 | 0.1133 | +0.0212 [+0.0029, +0.0434] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.432 | 0.0774 | 0.0630 | +0.0125 [+0.0072, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.0845 | 0.2903 | +0.0604 [-0.0440, +0.1631] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.429 | 0.0819 | 0.1461 | +0.0355 [+0.0130, +0.0568] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1364 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3171 | 0.2213 |

## extreme_value_tail (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 9 | 0.346 [0.174, 0.530] | 0.192 | 2.31 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.154, 0.481] | 0.192 | 2.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.458 (147 of 1873 days never flag) | 129 | 0.493 | 0.535 | 0.0520 | +0.0194 [+0.0134, +0.0262] | +0.0043 [-0.0017, +0.0101] | 0.921 | 0.458 | no |
| 2 | 0.447 (147 of 1872 days never flag) | 101 | 0.324 | 0.446 | 0.0554 | +0.0157 [+0.0101, +0.0222] | +0.0057 [-0.0004, +0.0121] | 0.909 | 0.291 | no |
| 3 | 0.46 (147 of 1871 days never flag) | 101 | 0.355 | 0.485 | 0.0564 | +0.0142 [+0.0085, +0.0205] | +0.0079 [+0.0019, +0.0142] | 0.904 | 0.325 | no |
| 4 | 0.459 (147 of 1870 days never flag) | 84 | 0.326 | 0.536 | 0.0558 | +0.0150 [+0.0092, +0.0210] | +0.0066 [+0.0003, +0.0130] | 0.906 | 0.304 | no |
| 5 | 0.526 (147 of 1869 days never flag) | 81 | 0.275 | 0.469 | 0.0564 | +0.0145 [+0.0092, +0.0203] | +0.0070 [+0.0010, +0.0132] | 0.905 | 0.251 | no |

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
| regime | 2018-19 | 375 | 102 | 0.667 | 0.535 | 0.2680 | 0.2720 | +0.0378 [+0.0106, +0.0698] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0397 | 0.0159 | +0.0354 [+0.0268, +0.0441] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0000 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0022 [-0.0016, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0259 | 0.1165 | +0.0094 [+0.0013, +0.0191] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0091 [+0.0074, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0005 | 0.0031 | +0.0302 [+0.0229, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0509 | 0.4146 | +0.0066 [-0.0153, +0.0368] |
| scarcity_state | 3 | 473 | 117 | 0.590 | 0.535 | 0.2417 | 0.2474 | +0.0357 [+0.0140, +0.0604] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.0800 | 0.1133 | +0.0290 [+0.0188, +0.0400] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.505 | 0.0564 | 0.0630 | +0.0142 [+0.0082, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2083 | 0.2903 | +0.1148 [+0.0604, +0.1722] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.0927 | 0.1461 | +0.0629 [+0.0363, +0.0926] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1546 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2533 | 0.2213 |

## gbm_reference (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 7 | 0.269 [0.130, 0.423] | 0.192 | 2.19 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 4 | 0.154 [0.043, 0.273] | 0.192 | 2.19 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.457 (1617 of 1873 days never flag) | 119 | 0.479 | 0.563 | 0.0519 | +0.0196 [+0.0105, +0.0296] | +0.0045 [-0.0009, +0.0105] | 0.888 | 0.449 | no |
| 2 | 0.633 (168 of 1872 days never flag) | 108 | 0.403 | 0.519 | 0.0548 | +0.0162 [+0.0081, +0.0256] | +0.0062 [+0.0002, +0.0134] | 0.888 | 0.373 | no |
| 3 | 0.612 (147 of 1871 days never flag) | 86 | 0.290 | 0.465 | 0.0595 | +0.0112 [+0.0031, +0.0202] | +0.0048 [-0.0015, +0.0121] | 0.878 | 0.263 | no |
| 4 | 0.6 (1491 of 1870 days never flag) | 34 | 0.087 | 0.353 | 0.0612 | +0.0096 [+0.0020, +0.0173] | +0.0011 [-0.0050, +0.0074] | 0.865 | 0.074 | no |
| 5 | 0.591 (147 of 1869 days never flag) | 104 | 0.341 | 0.452 | 0.0601 | +0.0108 [+0.0023, +0.0194] | +0.0033 [-0.0036, +0.0106] | 0.852 | 0.308 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2356 [+0.0901, +0.4060]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0798, ΔBrier vs climatology +0.0496 [+0.0336, +0.0674], realised minus predicted +0.0222 [-0.0049, +0.0513]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.549 | 0.3041 | 0.2720 | +0.0327 [-0.0044, +0.0758] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0766 | 0.0159 | +0.0295 [+0.0159, +0.0410] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0478 | 0.0000 | +0.0115 [+0.0098, +0.0133] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0522 | 0.0200 | +0.0008 [-0.0027, +0.0032] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.647 | 0.1131 | 0.1165 | +0.0327 [+0.0009, +0.0728] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0489 | 0.0048 | +0.0070 [+0.0055, +0.0086] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0531 | 0.0031 | +0.0271 [+0.0201, +0.0339] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.714 | 0.1979 | 0.4146 | +0.0952 [-0.0379, +0.2365] |
| scarcity_state | 3 | 473 | 117 | 0.530 | 0.554 | 0.2840 | 0.2474 | +0.0353 [+0.0040, +0.0700] |
| day_type | month_end | 150 | 17 | 0.706 | 0.750 | 0.1545 | 0.1133 | +0.0353 [+0.0062, +0.0674] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.500 | 0.1077 | 0.0630 | +0.0148 [+0.0059, +0.0250] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1572 | 0.2903 | +0.1113 [+0.0291, +0.1974] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.1067 | 0.1461 | +0.0473 [+0.0209, +0.0769] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0037 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.3159 | 0.2213 |

## hierarchical_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.682] | 0.231 | 3.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (147 of 1873 days never flag) | 164 | 0.600 | 0.512 | 0.0530 | +0.0184 [+0.0114, +0.0260] | +0.0034 [-0.0007, +0.0073] | 0.880 | 0.554 | no |
| 2 | 0.417 (147 of 1872 days never flag) | 91 | 0.317 | 0.484 | 0.0589 | +0.0121 [+0.0066, +0.0178] | +0.0021 [-0.0016, +0.0061] | 0.847 | 0.289 | no |
| 3 | 0.419 (147 of 1871 days never flag) | 150 | 0.493 | 0.453 | 0.0607 | +0.0100 [+0.0053, +0.0146] | +0.0037 [-0.0001, +0.0076] | 0.834 | 0.445 | no |
| 4 | 0.419 (147 of 1870 days never flag) | 144 | 0.478 | 0.458 | 0.0603 | +0.0105 [+0.0057, +0.0154] | +0.0020 [-0.0023, +0.0062] | 0.833 | 0.433 | no |
| 5 | 0.477 (126 of 1869 days never flag) | 158 | 0.457 | 0.399 | 0.0608 | +0.0101 [+0.0050, +0.0151] | +0.0026 [-0.0020, +0.0071] | 0.827 | 0.402 | no |

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
| regime | 2018-19 | 375 | 102 | 0.676 | 0.507 | 0.2190 | 0.2720 | +0.0265 [+0.0024, +0.0512] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1363 | 0.0159 | +0.0181 [+0.0037, +0.0311] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0085 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0065 | 0.0200 | +0.0013 [-0.0036, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.577 | 0.1189 | 0.1165 | +0.0382 [+0.0069, +0.0750] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0590 | 0.0031 | +0.0263 [+0.0203, +0.0319] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.2358 | 0.4146 | 0.1250 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.500 | 0.2484 | 0.2474 | +0.0249 [+0.0018, +0.0497] |
| day_type | month_end | 150 | 17 | 0.706 | 0.706 | 0.1016 | 0.1133 | +0.0440 [+0.0227, +0.0682] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.464 | 0.0752 | 0.0630 | +0.0128 [+0.0065, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2214 | 0.2903 | +0.0754 [+0.0169, +0.1274] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1263 | 0.1461 | +0.0569 [+0.0308, +0.0829] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2425 | 0.2213 |

## ngboost_laplace (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.174, 0.536] | 0.231 | 2.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.438 (147 of 1873 days never flag) | 112 | 0.486 | 0.607 | 0.0462 | +0.0252 [+0.0186, +0.0323] | +0.0101 [+0.0050, +0.0152] | 0.928 | 0.460 | no |
| 2 | 0.526 (168 of 1872 days never flag) | 63 | 0.129 | 0.286 | 0.0568 | +0.0143 [+0.0086, +0.0201] | +0.0043 [-0.0009, +0.0092] | 0.899 | 0.104 | no |
| 3 | 0.531 (147 of 1871 days never flag) | 59 | 0.159 | 0.373 | 0.0595 | +0.0112 [+0.0046, +0.0169] | +0.0049 [-0.0008, +0.0100] | 0.892 | 0.138 | no |
| 4 | 0.54 (147 of 1870 days never flag) | 102 | 0.261 | 0.353 | 0.0615 | +0.0093 [+0.0028, +0.0154] | +0.0008 [-0.0050, +0.0062] | 0.873 | 0.223 | no |
| 5 | 0.627 (147 of 1869 days never flag) | 59 | 0.130 | 0.305 | 0.0637 | +0.0072 [-0.0004, +0.0140] | -0.0003 [-0.0076, +0.0060] | 0.862 | 0.107 | no |

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
| regime | 2018-19 | 375 | 102 | 0.549 | 0.577 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0503 | 0.0159 | +0.0329 [+0.0235, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.909 | 0.0443 | 0.1165 | +0.0287 [+0.0113, +0.0503] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0268 | 0.0031 | +0.0285 [+0.0229, +0.0343] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | 0.0409 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.547 | 0.593 | 0.2024 | 0.2474 | +0.0558 [+0.0323, +0.0805] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.0819 | 0.1133 | +0.0481 [+0.0291, +0.0671] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.554 | 0.0518 | 0.0630 | +0.0187 [+0.0123, +0.0262] |
| day_type | quarter_end | 31 | 9 | 0.667 | 1.000 | 0.1699 | 0.2903 | +0.1308 [+0.0495, +0.2125] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.750 | 0.0904 | 0.1461 | +0.0670 [+0.0493, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## ngboost_normal (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.545] | 0.192 | 1.96 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 5 | 0.192 [0.071, 0.344] | 0.154 | 1.58 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (147 of 1873 days never flag) | 116 | 0.464 | 0.560 | 0.0526 | +0.0188 [+0.0098, +0.0291] | +0.0038 [-0.0029, +0.0114] | 0.923 | 0.435 | no |
| 2 | 0.621 (231 of 1872 days never flag) | 36 | 0.072 | 0.278 | 0.0634 | +0.0077 [-0.0012, +0.0167] | -0.0023 [-0.0106, +0.0060] | 0.885 | 0.057 | no |
| 3 | 0.696 (168 of 1871 days never flag) | 49 | 0.058 | 0.163 | 0.0691 | +0.0016 [-0.0092, +0.0115] | -0.0047 [-0.0144, +0.0041] | 0.872 | 0.034 | no |
| 4 | 0.633 (147 of 1870 days never flag) | 35 | 0.036 | 0.143 | 0.0707 | +0.0002 [-0.0099, +0.0096] | -0.0083 [-0.0177, +0.0006] | 0.856 | 0.019 | no |
| 5 | 0.576 (231 of 1869 days never flag) | 29 | 0.058 | 0.276 | 0.0726 | -0.0016 [-0.0129, +0.0083] | -0.0092 [-0.0204, +0.0005] | 0.845 | 0.046 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.482 (climatology 0.457, difference +0.0247 [-0.1022, +0.1027]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0280, +0.0622], realised minus predicted +0.0307 [+0.0002, +0.0631]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.542 | 0.3131 | 0.2720 | +0.0378 [-0.0037, +0.0819] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1139 | 0.0159 | +0.0051 [-0.0111, +0.0179] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0012 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0052 | 0.0200 | +0.0045 [+0.0008, +0.0082] |
| regime | 2025-26 | 249 | 29 | 0.207 | 1.000 | 0.0670 | 0.1165 | +0.0345 [+0.0113, +0.0636] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0019 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0350 | 0.0031 | +0.0165 [+0.0105, +0.0224] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1266 | 0.4146 | 0.0862 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.547 | 0.566 | 0.3094 | 0.2474 | +0.0351 [+0.0010, +0.0712] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1138 | 0.1133 | +0.0433 [+0.0215, +0.0677] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.516 | 0.0788 | 0.0630 | +0.0130 [+0.0035, +0.0233] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.2509 | 0.2903 | +0.0828 [+0.0025, +0.1649] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1529 | 0.1461 | +0.0610 [+0.0408, +0.0844] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0805 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2117 | 0.2213 |

## published_v1 (baseline): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 2 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 2 | 0.077 [0.000, 0.185] | 0.154 | 1.46 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.445 (147 of 1873 days never flag) | 123 | 0.443 | 0.504 | 0.0496 | +0.0219 [+0.0139, +0.0309] | +0.0068 [+0.0022, +0.0122] | 0.898 | 0.408 | no |
| 2 | 0.41 (231 of 1872 days never flag) | 85 | 0.324 | 0.529 | 0.0530 | +0.0180 [+0.0112, +0.0255] | +0.0080 [+0.0029, +0.0135] | 0.881 | 0.301 | no |
| 3 | 0.539 (147 of 1871 days never flag) | 62 | 0.225 | 0.500 | 0.0541 | +0.0166 [+0.0099, +0.0244] | +0.0103 [+0.0052, +0.0164] | 0.887 | 0.207 | no |
| 4 | 0.25 (1785 of 1870 days never flag) | 48 | 0.109 | 0.312 | 0.0567 | +0.0141 [+0.0078, +0.0213] | +0.0057 [+0.0011, +0.0112] | 0.871 | 0.090 | no |
| 5 | 0.387 (1764 of 1869 days never flag) | 57 | 0.138 | 0.333 | 0.0574 | +0.0136 [+0.0066, +0.0208] | +0.0060 [+0.0007, +0.0117] | 0.876 | 0.116 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.697 (climatology 0.457, difference +0.2403 [+0.0957, +0.3431]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0302, +0.0598], realised minus predicted +0.0422 [+0.0127, +0.0756]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.515 | 0.2612 | 0.2720 | +0.0460 [+0.0127, +0.0833] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0935 | 0.0159 | +0.0328 [+0.0266, +0.0391] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0320 | 0.0000 | +0.0127 [+0.0111, +0.0144] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0255 | 0.0200 | +0.0010 [-0.0043, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.526 | 0.1116 | 0.1165 | +0.0229 [-0.0053, +0.0574] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0287 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0638 | 0.0031 | +0.0250 [+0.0189, +0.0303] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1980 | 0.4146 | +0.0840 [-0.0308, +0.2028] |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.504 | 0.2559 | 0.2474 | +0.0446 [+0.0172, +0.0763] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1021 | 0.1133 | +0.0421 [+0.0202, +0.0713] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.452 | 0.0934 | 0.0630 | +0.0169 [+0.0088, +0.0259] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1348 | 0.2903 | +0.0922 [+0.0137, +0.1746] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.1164 | 0.1461 | +0.0534 [+0.0285, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1018 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2480 | 0.2213 |

## qrf (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.273, 0.652] | 0.231 | 2.85 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.200, 0.579] | 0.231 | 2.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.677 (126 of 1873 days never flag) | 123 | 0.429 | 0.488 | 0.0494 | +0.0220 [+0.0156, +0.0293] | +0.0069 [+0.0020, +0.0116] | 0.921 | 0.392 | no |
| 2 | 0.48 (168 of 1872 days never flag) | 74 | 0.230 | 0.432 | 0.0567 | +0.0143 [+0.0088, +0.0201] | +0.0043 [-0.0005, +0.0088] | 0.892 | 0.206 | no |
| 3 | 0.537 (231 of 1871 days never flag) | 68 | 0.152 | 0.309 | 0.0569 | +0.0138 [+0.0089, +0.0190] | +0.0075 [+0.0032, +0.0116] | 0.886 | 0.125 | no |
| 4 | 0.449 (147 of 1870 days never flag) | 96 | 0.246 | 0.354 | 0.0592 | +0.0116 [+0.0064, +0.0169] | +0.0032 [-0.0015, +0.0076] | 0.879 | 0.211 | no |
| 5 | 0.439 (168 of 1869 days never flag) | 123 | 0.355 | 0.398 | 0.0594 | +0.0115 [+0.0071, +0.0163] | +0.0040 [-0.0006, +0.0082] | 0.848 | 0.312 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.611 (climatology 0.457, difference +0.1536 [+0.0546, +0.2448]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0877, ΔBrier vs climatology +0.0418 [+0.0301, +0.0542], realised minus predicted +0.0623 [+0.0303, +0.0980]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.479 | 0.2566 | 0.2720 | +0.0471 [+0.0197, +0.0797] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.0597 | 0.0159 | +0.0315 [+0.0202, +0.0416] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0010 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0040 | 0.0200 | +0.0035 [-0.0002, +0.0061] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0412 | 0.1165 | +0.0177 [+0.0057, +0.0338] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0021 | 0.0048 | +0.0093 [+0.0076, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0230 | 0.0031 | +0.0284 [+0.0225, +0.0342] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0588 | 0.4146 | +0.0265 [-0.0005, +0.0549] |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.488 | 0.2352 | 0.2474 | +0.0449 [+0.0217, +0.0699] |
| day_type | month_end | 150 | 17 | 0.353 | 0.500 | 0.0922 | 0.1133 | +0.0373 [+0.0208, +0.0551] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.461 | 0.0600 | 0.0630 | +0.0169 [+0.0103, +0.0247] |
| day_type | quarter_end | 31 | 9 | 0.222 | 1.000 | 0.1591 | 0.2903 | +0.0947 [+0.0240, +0.1682] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.0927 | 0.1461 | +0.0613 [+0.0412, +0.0823] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1316 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.1899 | 0.2213 |

## stack_equal_average (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.278, 0.655] | 0.231 | 3.23 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.182, 0.536] | 0.231 | 3.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.554 (126 of 1873 days never flag) | 135 | 0.507 | 0.526 | 0.0476 | +0.0238 [+0.0175, +0.0311] | +0.0088 [+0.0043, +0.0136] | 0.927 | 0.470 | no |
| 2 | 0.507 (147 of 1872 days never flag) | 90 | 0.331 | 0.511 | 0.0545 | +0.0166 [+0.0116, +0.0223] | +0.0066 [+0.0018, +0.0118] | 0.900 | 0.306 | no |
| 3 | 0.491 (147 of 1871 days never flag) | 103 | 0.290 | 0.388 | 0.0558 | +0.0149 [+0.0099, +0.0196] | +0.0086 [+0.0043, +0.0132] | 0.894 | 0.254 | no |
| 4 | 0.431 (147 of 1870 days never flag) | 132 | 0.391 | 0.409 | 0.0566 | +0.0143 [+0.0096, +0.0191] | +0.0058 [+0.0012, +0.0105] | 0.891 | 0.346 | no |
| 5 | 0.432 (147 of 1869 days never flag) | 145 | 0.442 | 0.421 | 0.0573 | +0.0137 [+0.0092, +0.0185] | +0.0061 [+0.0014, +0.0111] | 0.879 | 0.394 | no |

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
| regime | 2018-19 | 375 | 102 | 0.657 | 0.515 | 0.2538 | 0.2720 | +0.0496 [+0.0218, +0.0802] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0659 | 0.0159 | +0.0349 [+0.0269, +0.0431] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0020 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0032 | 0.0200 | +0.0027 [-0.0012, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.800 | 0.0500 | 0.1165 | +0.0254 [+0.0089, +0.0454] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0025 | 0.0048 | +0.0092 [+0.0075, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0220 | 0.0031 | +0.0299 [+0.0239, +0.0359] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0876 | 0.4146 | 0.0485 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.526 | 0.2393 | 0.2474 | +0.0497 [+0.0275, +0.0757] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.0891 | 0.1133 | +0.0407 [+0.0258, +0.0569] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.476 | 0.0611 | 0.0630 | +0.0180 [+0.0118, +0.0254] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1957 | 0.2903 | +0.1165 [+0.0613, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1023 | 0.1461 | +0.0676 [+0.0472, +0.0907] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0656 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2254 | 0.2213 |

## stacked_ensemble (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.393, 0.750] | 0.231 | 3.27 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.161, 0.529] | 0.231 | 3.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.607 (126 of 1873 days never flag) | 158 | 0.521 | 0.462 | 0.0508 | +0.0207 [+0.0136, +0.0286] | +0.0056 [+0.0008, +0.0102] | 0.926 | 0.472 | no |
| 2 | 0.511 (147 of 1872 days never flag) | 133 | 0.439 | 0.459 | 0.0569 | +0.0142 [+0.0087, +0.0199] | +0.0042 [-0.0009, +0.0093] | 0.906 | 0.397 | no |
| 3 | 0.501 (147 of 1871 days never flag) | 137 | 0.413 | 0.416 | 0.0578 | +0.0129 [+0.0081, +0.0183] | +0.0066 [+0.0020, +0.0113] | 0.903 | 0.367 | no |
| 4 | 0.491 (147 of 1870 days never flag) | 114 | 0.377 | 0.456 | 0.0593 | +0.0116 [+0.0065, +0.0165] | +0.0031 [-0.0017, +0.0078] | 0.897 | 0.341 | no |
| 5 | 0.569 (147 of 1869 days never flag) | 141 | 0.420 | 0.411 | 0.0605 | +0.0104 [+0.0039, +0.0165] | +0.0029 [-0.0034, +0.0090] | 0.881 | 0.372 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.457, difference +0.1561 [+0.0650, +0.2699]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0834, ΔBrier vs climatology +0.0461 [+0.0327, +0.0612], realised minus predicted +0.0532 [+0.0230, +0.0862]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.444 | 0.2945 | 0.2720 | +0.0292 [-0.0012, +0.0634] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0539 | 0.0159 | +0.0330 [+0.0230, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0004 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0024 | 0.0200 | +0.0036 [-0.0003, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0680 | 0.1165 | +0.0331 [+0.0101, +0.0622] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0015 | 0.0048 | +0.0093 [+0.0077, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0136 | 0.0031 | +0.0300 [+0.0238, +0.0356] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0999 | 0.4146 | 0.0677 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.455 | 0.2785 | 0.2474 | +0.0350 [+0.0082, +0.0644] |
| day_type | month_end | 150 | 17 | 0.706 | 0.667 | 0.1004 | 0.1133 | +0.0509 [+0.0295, +0.0763] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.406 | 0.0703 | 0.0630 | +0.0144 [+0.0074, +0.0227] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1924 | 0.2903 | +0.1053 [+0.0220, +0.1853] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.0902 | 0.1461 | +0.0520 [+0.0354, +0.0690] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3616 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2167 | 0.2213 |

## time_to_pressure_hazard (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 7 | 0.269 [0.129, 0.423] | 0.192 | 2.19 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.423] | 0.192 | 2.19 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.559 (147 of 1873 days never flag) | 111 | 0.450 | 0.568 | 0.0553 | +0.0161 [+0.0088, +0.0243] | +0.0010 [-0.0058, +0.0079] | 0.915 | 0.422 | no |
| 2 | 0.524 (147 of 1872 days never flag) | 102 | 0.367 | 0.500 | 0.0576 | +0.0135 [+0.0066, +0.0206] | +0.0035 [-0.0036, +0.0103] | 0.907 | 0.337 | no |
| 3 | 0.535 (147 of 1871 days never flag) | 102 | 0.348 | 0.471 | 0.0595 | +0.0112 [+0.0043, +0.0179] | +0.0049 [-0.0023, +0.0115] | 0.902 | 0.317 | no |
| 4 | 0.507 (147 of 1870 days never flag) | 104 | 0.341 | 0.452 | 0.0594 | +0.0114 [+0.0049, +0.0187] | +0.0030 [-0.0041, +0.0100] | 0.899 | 0.308 | no |
| 5 | 0.491 (147 of 1869 days never flag) | 74 | 0.246 | 0.459 | 0.0599 | +0.0110 [+0.0050, +0.0172] | +0.0035 [-0.0033, +0.0098] | 0.895 | 0.223 | no |

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
| regime | 2018-19 | 375 | 102 | 0.608 | 0.569 | 0.3017 | 0.2720 | +0.0265 [-0.0081, +0.0667] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0437 | 0.0159 | +0.0338 [+0.0237, +0.0442] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0019 [-0.0027, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0194 | 0.1165 | +0.0036 [-0.0037, +0.0115] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0009 | 0.0048 | +0.0090 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0009 | 0.0031 | +0.0302 [+0.0229, +0.0368] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0238 | 0.4146 | -0.0167 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.538 | 0.568 | 0.2690 | 0.2474 | +0.0248 [-0.0027, +0.0571] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.0899 | 0.1133 | +0.0209 [+0.0056, +0.0349] |
| day_type | ordinary | 1603 | 101 | 0.426 | 0.537 | 0.0620 | 0.0630 | +0.0119 [+0.0047, +0.0203] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2200 | 0.2903 | +0.0928 [+0.0465, +0.1330] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1093 | 0.1461 | +0.0565 [+0.0216, +0.0945] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2811 | 0.2213 |

