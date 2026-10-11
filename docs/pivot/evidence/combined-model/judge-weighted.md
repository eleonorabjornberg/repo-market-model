# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `709c5db2e57a…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## risk_gbm+combined (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.212, 0.571] | 0.154 | 1.69 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.208, 0.576] | 0.154 | 1.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 71 | 0.329 | 0.648 | 0.0599 | +0.0116 [+0.0063, +0.0165] | -0.0035 [-0.0113, +0.0037] | 0.723 | 0.314 | no |
| 2 | 0.037 (147 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0641 | +0.0069 [+0.0003, +0.0138] | -0.0031 [-0.0110, +0.0048] | 0.698 | 0.230 | no |
| 3 | 0.104 (147 of 1871 days never flag) | 73 | 0.275 | 0.521 | 0.0656 | +0.0051 [-0.0031, +0.0122] | -0.0012 [-0.0095, +0.0063] | 0.702 | 0.255 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 75 | 0.225 | 0.413 | 0.0683 | +0.0026 [-0.0046, +0.0100] | -0.0059 [-0.0137, +0.0020] | 0.675 | 0.199 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 69 | 0.225 | 0.449 | 0.0672 | +0.0038 [-0.0048, +0.0113] | -0.0038 [-0.0125, +0.0040] | 0.676 | 0.203 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0522, +0.3886]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1028, ΔBrier vs climatology +0.0267 [+0.0151, +0.0389], realised minus predicted +0.0976 [+0.0620, +0.1357]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.655 | 0.0653 | 0.2720 | -0.0020 [-0.0236, +0.0186] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0346, +0.0500] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0013 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0047, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0165 | 0.1165 | +0.0049 [-0.0043, +0.0151] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0010 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0014 | 0.0031 | +0.0302 [+0.0231, +0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0130 | 0.4146 | -0.0298 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.385 | 0.652 | 0.0609 | 0.2474 | +0.0084 [-0.0102, +0.0257] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.0401 | 0.1133 | +0.0298 [+0.0161, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.692 | 0.0117 | 0.0630 | +0.0071 [+0.0020, +0.0116] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0102, +0.1953] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.0269 | 0.1461 | +0.0292 [-0.0010, +0.0578] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6331 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_no_factor (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.212, 0.571] | 0.154 | 1.65 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.207, 0.577] | 0.154 | 1.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 74 | 0.336 | 0.635 | 0.0599 | +0.0115 [+0.0062, +0.0162] | -0.0036 [-0.0116, +0.0031] | 0.723 | 0.320 | no |
| 2 | 0.037 (147 of 1872 days never flag) | 71 | 0.252 | 0.493 | 0.0634 | +0.0076 [+0.0006, +0.0139] | -0.0024 [-0.0101, +0.0046] | 0.696 | 0.231 | no |
| 3 | 0.0385 (147 of 1871 days never flag) | 73 | 0.275 | 0.521 | 0.0647 | +0.0060 [-0.0018, +0.0128] | -0.0003 [-0.0084, +0.0068] | 0.714 | 0.255 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 74 | 0.225 | 0.419 | 0.0676 | +0.0032 [-0.0046, +0.0099] | -0.0052 [-0.0134, +0.0021] | 0.679 | 0.200 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 68 | 0.225 | 0.456 | 0.0666 | +0.0044 [-0.0037, +0.0116] | -0.0032 [-0.0118, +0.0043] | 0.673 | 0.203 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0553, +0.4045]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1030, ΔBrier vs climatology +0.0264 [+0.0150, +0.0387], realised minus predicted +0.0985 [+0.0622, +0.1379]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.644 | 0.0639 | 0.2720 | -0.0025 [-0.0234, +0.0174] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0348, +0.0500] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0014 | 0.0000 | +0.0138 [+0.0121, +0.0158] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0047, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0165 | 0.1165 | +0.0050 [-0.0044, +0.0151] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0011 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0013 | 0.0031 | +0.0302 [+0.0231, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0143 | 0.4146 | -0.0291 [-0.0461, -0.0006] |
| scarcity_state | 3 | 473 | 117 | 0.385 | 0.634 | 0.0599 | 0.2474 | +0.0081 [-0.0103, +0.0254] |
| day_type | month_end | 150 | 17 | 0.529 | 0.562 | 0.0401 | 0.1133 | +0.0298 [+0.0165, +0.0444] |
| day_type | ordinary | 1603 | 101 | 0.277 | 0.667 | 0.0115 | 0.0630 | +0.0070 [+0.0023, +0.0112] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0121, +0.1925] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.0269 | 0.1461 | +0.0292 [-0.0021, +0.0572] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6355 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_no_projected (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.200, 0.571] | 0.154 | 1.65 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.208, 0.571] | 0.154 | 1.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 97 | 0.414 | 0.598 | 0.0594 | +0.0120 [+0.0070, +0.0167] | -0.0031 [-0.0111, +0.0037] | 0.736 | 0.392 | no |
| 2 | 0.0312 (147 of 1872 days never flag) | 76 | 0.252 | 0.461 | 0.0646 | +0.0065 [-0.0009, +0.0130] | -0.0035 [-0.0120, +0.0033] | 0.661 | 0.228 | no |
| 3 | 0.0323 (147 of 1871 days never flag) | 72 | 0.275 | 0.528 | 0.0659 | +0.0048 [-0.0036, +0.0119] | -0.0015 [-0.0100, +0.0057] | 0.694 | 0.256 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 74 | 0.225 | 0.419 | 0.0682 | +0.0026 [-0.0057, +0.0099] | -0.0059 [-0.0146, +0.0019] | 0.666 | 0.200 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 74 | 0.246 | 0.459 | 0.0663 | +0.0046 [-0.0038, +0.0115] | -0.0029 [-0.0117, +0.0044] | 0.676 | 0.223 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0523, +0.4019]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1030, ΔBrier vs climatology +0.0264 [+0.0144, +0.0386], realised minus predicted +0.0979 [+0.0647, +0.1336]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.412 | 0.667 | 0.0657 | 0.2720 | +0.0005 [-0.0202, +0.0202] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0345, +0.0498] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0047, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.517 | 0.0144 | 0.1165 | +0.0044 [-0.0051, +0.0146] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0001 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0012 | 0.0031 | +0.0302 [+0.0231, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.600 | 0.0105 | 0.4146 | -0.0319 [-0.0515, -0.0033] |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.605 | 0.0608 | 0.2474 | +0.0103 [-0.0078, +0.0268] |
| day_type | month_end | 150 | 17 | 0.588 | 0.556 | 0.0405 | 0.1133 | +0.0296 [+0.0172, +0.0431] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.597 | 0.0110 | 0.0630 | +0.0076 [+0.0028, +0.0118] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0156, +0.1989] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.0269 | 0.1461 | +0.0292 [-0.0021, +0.0579] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.5705 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_no_structural (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.217, 0.562] | 0.192 | 1.73 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.577] | 0.154 | 1.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0284 (147 of 1873 days never flag) | 104 | 0.421 | 0.567 | 0.0606 | +0.0108 [+0.0054, +0.0161] | -0.0042 [-0.0120, +0.0027] | 0.719 | 0.395 | no |
| 2 | 0.0312 (147 of 1872 days never flag) | 69 | 0.245 | 0.493 | 0.0647 | +0.0064 [-0.0001, +0.0121] | -0.0036 [-0.0110, +0.0028] | 0.685 | 0.224 | no |
| 3 | 0.0323 (147 of 1871 days never flag) | 61 | 0.246 | 0.557 | 0.0646 | +0.0061 [+0.0003, +0.0118] | -0.0003 [-0.0066, +0.0061] | 0.673 | 0.231 | no |
| 4 | 0.108 (147 of 1870 days never flag) | 64 | 0.232 | 0.500 | 0.0648 | +0.0060 [+0.0002, +0.0115] | -0.0025 [-0.0093, +0.0038] | 0.668 | 0.213 | no |
| 5 | 0.108 (147 of 1869 days never flag) | 71 | 0.232 | 0.451 | 0.0642 | +0.0068 [+0.0006, +0.0127] | -0.0008 [-0.0076, +0.0055] | 0.668 | 0.209 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.693 (climatology 0.457, difference +0.2359 [+0.0634, +0.3968]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1011, ΔBrier vs climatology +0.0284 [+0.0177, +0.0394], realised minus predicted +0.1033 [+0.0688, +0.1416]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.382 | 0.736 | 0.0659 | 0.2720 | -0.0058 [-0.0284, +0.0163] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0053 | 0.0159 | +0.0422 [+0.0349, +0.0497] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0005 | 0.0200 | +0.0010 [-0.0049, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.413 | 0.0174 | 0.1165 | +0.0052 [-0.0036, +0.0153] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0004 | 0.0048 | +0.0088 [+0.0069, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0015 | 0.0031 | +0.0302 [+0.0235, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.526 | 0.0152 | 0.4146 | -0.0287 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.583 | 0.0617 | 0.2474 | +0.0055 [-0.0140, +0.0244] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.0399 | 0.1133 | +0.0299 [+0.0166, +0.0442] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.549 | 0.0116 | 0.0630 | +0.0062 [+0.0010, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1190 | 0.2903 | +0.1049 [+0.0149, +0.1995] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.0269 | 0.1461 | +0.0292 [-0.0007, +0.0589] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6469 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2128 | 0.2213 |

## risk_gbm+combined_nogate (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.308, 0.684] | 0.231 | 3.23 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.227, 0.621] | 0.231 | 3.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.352 (147 of 1873 days never flag) | 158 | 0.529 | 0.468 | 0.0501 | +0.0213 [+0.0128, +0.0310] | +0.0063 [-0.0006, +0.0139] | 0.858 | 0.480 | no |
| 2 | 0.488 (147 of 1872 days never flag) | 72 | 0.302 | 0.583 | 0.0568 | +0.0143 [+0.0027, +0.0255] | +0.0043 [-0.0066, +0.0150] | 0.822 | 0.285 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 144 | 0.464 | 0.444 | 0.0591 | +0.0116 [+0.0011, +0.0218] | +0.0052 [-0.0051, +0.0152] | 0.825 | 0.418 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 120 | 0.406 | 0.467 | 0.0601 | +0.0108 [-0.0001, +0.0208] | +0.0023 [-0.0085, +0.0126] | 0.806 | 0.369 | no |
| 5 | 0.723 (168 of 1869 days never flag) | 33 | 0.188 | 0.788 | 0.0651 | +0.0058 [-0.0049, +0.0163] | -0.0017 [-0.0121, +0.0082] | 0.793 | 0.184 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.719 (climatology 0.457, difference +0.2619 [+0.0646, +0.4327]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0820, ΔBrier vs climatology +0.0475 [+0.0280, +0.0688], realised minus predicted -0.0245 [-0.0553, +0.0085]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.454 | 0.2869 | 0.2720 | +0.0486 [+0.0100, +0.0920] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1287 | 0.0159 | +0.0248 [+0.0141, +0.0346] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0230 | 0.0000 | +0.0127 [+0.0110, +0.0144] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0057 | 0.0200 | +0.0015 [-0.0035, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0536 | 0.1165 | +0.0228 [+0.0030, +0.0491] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0142 | 0.0048 | +0.0081 [+0.0061, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0714 | 0.0031 | +0.0220 [+0.0145, +0.0288] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0832 | 0.4146 | 0.0221 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.468 | 0.2763 | 0.2474 | +0.0498 [+0.0174, +0.0844] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1082 | 0.1133 | +0.0566 [+0.0330, +0.0822] |
| day_type | ordinary | 1603 | 101 | 0.525 | 0.417 | 0.0876 | 0.0630 | +0.0134 [+0.0046, +0.0234] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2074 | 0.2903 | +0.1247 [+0.0394, +0.2037] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.556 | 0.0989 | 0.1461 | +0.0689 [+0.0407, +0.0977] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3603 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.1688 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.524, 0.857] | 0.231 | 3.54 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 15 | 0.577 [0.393, 0.767] | 0.231 | 3.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 172 | 0.571 | 0.465 | 0.0498 | +0.0216 [+0.0142, +0.0289] | +0.0065 [+0.0011, +0.0118] | 0.804 | 0.518 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 163 | 0.561 | 0.479 | 0.0544 | +0.0166 [+0.0116, +0.0221] | +0.0066 [+0.0019, +0.0117] | 0.800 | 0.512 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 163 | 0.536 | 0.454 | 0.0570 | +0.0137 [+0.0083, +0.0189] | +0.0074 [+0.0025, +0.0124] | 0.776 | 0.485 | no |
| 4 | 0.194 (147 of 1870 days never flag) | 165 | 0.543 | 0.455 | 0.0532 | +0.0176 [+0.0122, +0.0229] | +0.0092 [+0.0049, +0.0138] | 0.807 | 0.492 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 165 | 0.536 | 0.448 | 0.0539 | +0.0170 [+0.0115, +0.0226] | +0.0095 [+0.0051, +0.0144] | 0.804 | 0.484 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

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

## risk_gbm+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.710] | 0.154 | 1.38 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.154 | 1.38 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 77 | 0.293 | 0.532 | 0.0579 | +0.0135 [+0.0081, +0.0193] | -0.0016 [-0.0095, +0.0062] | 0.642 | 0.272 | no |
| 2 | 0.111 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0593 | +0.0117 [+0.0069, +0.0165] | +0.0017 [-0.0052, +0.0083] | 0.639 | 0.259 | no |
| 3 | 0.115 (147 of 1871 days never flag) | 76 | 0.290 | 0.526 | 0.0612 | +0.0095 [+0.0041, +0.0147] | +0.0032 [-0.0037, +0.0092] | 0.636 | 0.269 | no |
| 4 | 0.12 (147 of 1870 days never flag) | 67 | 0.268 | 0.552 | 0.0589 | +0.0119 [+0.0070, +0.0167] | +0.0034 [-0.0027, +0.0094] | 0.633 | 0.251 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 65 | 0.261 | 0.554 | 0.0593 | +0.0116 [+0.0067, +0.0163] | +0.0041 [-0.0020, +0.0098] | 0.632 | 0.244 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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

## risk_gbm_base+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.474, 0.826] | 0.231 | 3.65 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 14 | 0.538 [0.350, 0.722] | 0.231 | 3.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 172 | 0.593 | 0.483 | 0.0514 | +0.0200 [+0.0130, +0.0277] | +0.0049 [+0.0002, +0.0099] | 0.805 | 0.542 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 166 | 0.561 | 0.470 | 0.0548 | +0.0163 [+0.0108, +0.0219] | +0.0063 [+0.0016, +0.0115] | 0.800 | 0.510 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 167 | 0.543 | 0.449 | 0.0551 | +0.0156 [+0.0106, +0.0209] | +0.0093 [+0.0049, +0.0136] | 0.777 | 0.490 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 170 | 0.543 | 0.441 | 0.0542 | +0.0166 [+0.0112, +0.0224] | +0.0082 [+0.0037, +0.0133] | 0.805 | 0.489 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 170 | 0.543 | 0.441 | 0.0547 | +0.0163 [+0.0106, +0.0221] | +0.0087 [+0.0040, +0.0139] | 0.802 | 0.489 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.722 (climatology 0.457, difference +0.2644 [+0.0784, +0.4292]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0734, ΔBrier vs climatology +0.0561 [+0.0373, +0.0754], realised minus predicted +0.0261 [+0.0006, +0.0526]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.549 | 0.1717 | 0.2720 | +0.0380 [+0.0117, +0.0675] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0291 | 0.0159 | +0.0271 [+0.0077, +0.0427] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0127 | 0.0200 | -0.0018 [-0.0094, +0.0044] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.500 | 0.0812 | 0.1165 | +0.0264 [+0.0031, +0.0546] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0070 | 0.0048 | +0.0079 [+0.0053, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0091 | 0.0031 | +0.0285 [+0.0208, +0.0355] |
| scarcity_state | 2 | 41 | 17 | 0.647 | 0.579 | 0.1841 | 0.4146 | 0.0637 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.522 | 0.1697 | 0.2474 | +0.0368 [+0.0130, +0.0628] |
| day_type | month_end | 150 | 17 | 0.765 | 0.542 | 0.0993 | 0.1133 | +0.0436 [+0.0220, +0.0677] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.445 | 0.0424 | 0.0630 | +0.0134 [+0.0069, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.1739 | 0.2903 | +0.0993 [+0.0164, +0.1817] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1094 | 0.1461 | +0.0713 [+0.0493, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3835 | 0.2213 |

## risk_gbm_base+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.720] | 0.154 | 1.50 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.211, 0.571] | 0.154 | 1.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 77 | 0.307 | 0.558 | 0.0595 | +0.0119 [+0.0068, +0.0166] | -0.0032 [-0.0114, +0.0038] | 0.643 | 0.288 | no |
| 2 | 0.111 (147 of 1872 days never flag) | 71 | 0.281 | 0.549 | 0.0596 | +0.0114 [+0.0064, +0.0167] | +0.0014 [-0.0053, +0.0083] | 0.639 | 0.262 | no |
| 3 | 0.115 (147 of 1871 days never flag) | 75 | 0.283 | 0.520 | 0.0592 | +0.0114 [+0.0069, +0.0161] | +0.0051 [-0.0004, +0.0108] | 0.637 | 0.262 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 76 | 0.268 | 0.487 | 0.0599 | +0.0109 [+0.0059, +0.0161] | +0.0025 [-0.0038, +0.0090] | 0.631 | 0.246 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 76 | 0.268 | 0.487 | 0.0601 | +0.0109 [+0.0058, +0.0156] | +0.0033 [-0.0032, +0.0093] | 0.631 | 0.246 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.721 (climatology 0.457, difference +0.2635 [+0.0792, +0.4430]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0863, ΔBrier vs climatology +0.0431 [+0.0291, +0.0582], realised minus predicted +0.0537 [+0.0239, +0.0861]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1000 | 0.2720 | -0.0021 [-0.0226, +0.0166] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0215 | 0.0159 | +0.0344 [+0.0215, +0.0463] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0012 [-0.0040, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.846 | 0.0299 | 0.1165 | +0.0153 [+0.0018, +0.0321] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0003 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0042 | 0.0031 | +0.0299 [+0.0227, +0.0368] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0287 | 0.4146 | -0.0036 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.582 | 0.1010 | 0.2474 | +0.0076 [-0.0114, +0.0247] |
| day_type | month_end | 150 | 17 | 0.765 | 0.542 | 0.0955 | 0.1133 | +0.0379 [+0.0174, +0.0602] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.516 | 0.0132 | 0.0630 | +0.0045 [-0.0010, +0.0091] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.1739 | 0.2903 | +0.0993 [+0.0197, +0.1799] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1094 | 0.1461 | +0.0713 [+0.0487, +0.0967] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2015 | 0.2213 |

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

## risk_logistic+combined (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.258, 0.606] | 0.192 | 2.35 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.259, 0.600] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0339 (147 of 1873 days never flag) | 107 | 0.379 | 0.495 | 0.0606 | +0.0108 [+0.0061, +0.0153] | -0.0043 [-0.0123, +0.0025] | 0.720 | 0.347 | no |
| 2 | 0.0334 (147 of 1872 days never flag) | 89 | 0.317 | 0.494 | 0.0633 | +0.0077 [+0.0011, +0.0140] | -0.0023 [-0.0101, +0.0049] | 0.700 | 0.291 | no |
| 3 | 0.0177 (147 of 1871 days never flag) | 99 | 0.275 | 0.384 | 0.0656 | +0.0051 [-0.0028, +0.0123] | -0.0012 [-0.0093, +0.0064] | 0.702 | 0.240 | no |
| 4 | 0.0342 (147 of 1870 days never flag) | 97 | 0.290 | 0.412 | 0.0684 | +0.0025 [-0.0055, +0.0099] | -0.0060 [-0.0144, +0.0020] | 0.677 | 0.257 | no |
| 5 | 0.0431 (147 of 1869 days never flag) | 82 | 0.232 | 0.390 | 0.0696 | +0.0013 [-0.0072, +0.0087] | -0.0062 [-0.0148, +0.0018] | 0.675 | 0.203 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 3.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 3.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.673 (climatology 0.457, difference +0.2159 [+0.0593, +0.3640]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1063, ΔBrier vs climatology +0.0232 [+0.0120, +0.0341], realised minus predicted +0.0924 [+0.0564, +0.1302]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.382 | 0.661 | 0.0674 | 0.2720 | -0.0055 [-0.0246, +0.0131] |
| regime | 2020 | 251 | 4 | 0.250 | 0.050 | 0.0152 | 0.0159 | +0.0333 [+0.0240, +0.0412] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0013 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0036 | 0.0200 | +0.0048 [+0.0011, +0.0084] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.750 | 0.0200 | 0.1165 | +0.0096 [+0.0012, +0.0205] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.077 | 0.0020 | 0.0048 | +0.0097 [+0.0081, +0.0113] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0040 | 0.0031 | +0.0285 [+0.0221, +0.0349] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0297 | 0.4146 | -0.0051 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.410 | 0.585 | 0.0663 | 0.2474 | +0.0024 [-0.0136, +0.0184] |
| day_type | month_end | 150 | 17 | 0.647 | 0.440 | 0.0404 | 0.1133 | +0.0265 [+0.0131, +0.0413] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.529 | 0.0106 | 0.0630 | +0.0062 [+0.0016, +0.0105] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.2700 | 0.2903 | +0.0668 [-0.0140, +0.1429] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.0519 | 0.1461 | +0.0484 [+0.0290, +0.0675] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.5353 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2516 | 0.2213 |

## risk_logistic+combined_nogate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.273, 0.583] | 0.231 | 3.65 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.135, 0.421] | 0.192 | 2.08 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.352 (126 of 1873 days never flag) | 168 | 0.521 | 0.435 | 0.0525 | +0.0189 [+0.0106, +0.0285] | +0.0038 [-0.0035, +0.0116] | 0.851 | 0.467 | no |
| 2 | 0.488 (147 of 1872 days never flag) | 54 | 0.273 | 0.704 | 0.0580 | +0.0130 [+0.0018, +0.0238] | +0.0030 [-0.0079, +0.0136] | 0.826 | 0.264 | no |
| 3 | 0.414 (147 of 1871 days never flag) | 84 | 0.370 | 0.607 | 0.0572 | +0.0134 [+0.0032, +0.0236] | +0.0071 [-0.0032, +0.0173] | 0.825 | 0.351 | no |
| 4 | 0.786 (147 of 1870 days never flag) | 88 | 0.246 | 0.386 | 0.0613 | +0.0096 [-0.0011, +0.0201] | +0.0011 [-0.0097, +0.0117] | 0.797 | 0.215 | no |
| 5 | 0.773 (147 of 1869 days never flag) | 28 | 0.101 | 0.500 | 0.0660 | +0.0049 [-0.0060, +0.0152] | -0.0026 [-0.0130, +0.0080] | 0.792 | 0.093 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.711 (climatology 0.457, difference +0.2538 [+0.0943, +0.3944]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0812, ΔBrier vs climatology +0.0483 [+0.0281, +0.0697], realised minus predicted -0.0358 [-0.0643, -0.0039]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.435 | 0.2997 | 0.2720 | +0.0448 [+0.0063, +0.0879] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1402 | 0.0159 | +0.0131 [-0.0023, +0.0258] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0230 | 0.0000 | +0.0127 [+0.0111, +0.0145] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0110 | 0.0200 | +0.0051 [+0.0012, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.700 | 0.0449 | 0.1165 | +0.0178 [+0.0037, +0.0369] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0160 | 0.0048 | +0.0089 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0720 | 0.0031 | +0.0214 [+0.0160, +0.0273] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0731 | 0.4146 | 0.0192 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.598 | 0.432 | 0.2872 | 0.2474 | +0.0388 [+0.0060, +0.0750] |
| day_type | month_end | 150 | 17 | 0.588 | 0.556 | 0.1118 | 0.1133 | +0.0333 [+0.0073, +0.0610] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.389 | 0.0873 | 0.0630 | +0.0129 [+0.0045, +0.0223] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0168, +0.1610] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0457, +0.1128] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0581 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.1723 | 0.2213 |

## risk_logistic+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.519, 0.857] | 0.250 | 4.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.444, 0.783] | 0.250 | 4.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 186 | 0.593 | 0.446 | 0.0523 | +0.0191 [+0.0123, +0.0264] | +0.0040 [-0.0014, +0.0097] | 0.801 | 0.533 | no |
| 2 | 0.131 (126 of 1872 days never flag) | 184 | 0.547 | 0.413 | 0.0557 | +0.0154 [+0.0098, +0.0216] | +0.0054 [+0.0004, +0.0108] | 0.800 | 0.484 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 128 | 0.442 | 0.477 | 0.0551 | +0.0156 [+0.0100, +0.0211] | +0.0093 [+0.0042, +0.0146] | 0.779 | 0.403 | no |
| 4 | 0.163 (126 of 1870 days never flag) | 161 | 0.529 | 0.453 | 0.0544 | +0.0164 [+0.0113, +0.0217] | +0.0079 [+0.0035, +0.0127] | 0.805 | 0.478 | no |
| 5 | 0.132 (126 of 1869 days never flag) | 199 | 0.609 | 0.422 | 0.0548 | +0.0161 [+0.0109, +0.0217] | +0.0086 [+0.0041, +0.0134] | 0.804 | 0.542 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.708 (climatology 0.457, difference +0.2513 [+0.0892, +0.3945]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0722, ΔBrier vs climatology +0.0573 [+0.0396, +0.0772], realised minus predicted +0.0195 [-0.0043, +0.0462]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.521 | 0.1820 | 0.2720 | +0.0382 [+0.0132, +0.0653] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0359 | 0.0159 | +0.0193 [-0.0049, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.100 | 0.0182 | 0.0200 | +0.0021 [-0.0046, +0.0081] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.475 | 0.0821 | 0.1165 | +0.0236 [+0.0017, +0.0507] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.067 | 0.0098 | 0.0048 | +0.0083 [+0.0059, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0102 | 0.0031 | +0.0271 [+0.0200, +0.0339] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.562 | 0.1902 | 0.4146 | 0.0703 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.490 | 0.1779 | 0.2474 | +0.0329 [+0.0093, +0.0578] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1046 | 0.1133 | +0.0362 [+0.0093, +0.0647] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.420 | 0.0422 | 0.0630 | +0.0129 [+0.0066, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3546 | 0.2903 | +0.0906 [+0.0222, +0.1607] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1246 | 0.1461 | +0.0764 [+0.0442, +0.1149] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.800] | 0.231 | 2.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.429, 0.793] | 0.231 | 2.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0483 (105 of 1873 days never flag) | 107 | 0.321 | 0.421 | 0.0604 | +0.0110 [+0.0058, +0.0158] | -0.0041 [-0.0125, +0.0039] | 0.641 | 0.286 | no |
| 2 | 0.0436 (126 of 1872 days never flag) | 106 | 0.345 | 0.453 | 0.0606 | +0.0105 [+0.0053, +0.0154] | +0.0005 [-0.0068, +0.0073] | 0.639 | 0.312 | no |
| 3 | 0.025 (147 of 1871 days never flag) | 109 | 0.326 | 0.413 | 0.0593 | +0.0114 [+0.0062, +0.0163] | +0.0051 [-0.0016, +0.0110] | 0.638 | 0.289 | no |
| 4 | 0.092 (126 of 1870 days never flag) | 101 | 0.304 | 0.416 | 0.0601 | +0.0107 [+0.0055, +0.0154] | +0.0022 [-0.0044, +0.0083] | 0.632 | 0.270 | no |
| 5 | 0.0254 (126 of 1869 days never flag) | 115 | 0.319 | 0.383 | 0.0602 | +0.0107 [+0.0058, +0.0156] | +0.0032 [-0.0032, +0.0094] | 0.633 | 0.278 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 4.9 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 5.1 over 1035 days; regime_2021-23: 2.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.708 (climatology 0.457, difference +0.2509 [+0.0893, +0.4002]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0846, ΔBrier vs climatology +0.0449 [+0.0325, +0.0588], realised minus predicted +0.0458 [+0.0174, +0.0765]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1103 | 0.2720 | -0.0019 [-0.0231, +0.0187] |
| regime | 2020 | 251 | 4 | 0.250 | 0.038 | 0.0283 | 0.0159 | +0.0266 [+0.0117, +0.0388] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0058 | 0.0200 | +0.0050 [+0.0011, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0309 | 0.1165 | +0.0125 [+0.0008, +0.0272] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.111 | 0.0030 | 0.0048 | +0.0092 [+0.0074, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0053 | 0.0031 | +0.0285 [+0.0222, +0.0350] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0348 | 0.4146 | 0.0030 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.506 | 0.1092 | 0.2474 | +0.0037 [-0.0151, +0.0222] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1008 | 0.1133 | +0.0305 [+0.0038, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.405 | 0.0129 | 0.0630 | +0.0040 [-0.0012, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3546 | 0.2903 | +0.0906 [+0.0189, +0.1627] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.474 | 0.1246 | 0.1461 | +0.0764 [+0.0461, +0.1173] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

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

## risk_logistic_base+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.474, 0.815] | 0.231 | 4.15 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.737] | 0.231 | 3.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.134 (84 of 1873 days never flag) | 193 | 0.636 | 0.461 | 0.0511 | +0.0203 [+0.0136, +0.0273] | +0.0052 [+0.0006, +0.0104] | 0.804 | 0.576 | no |
| 2 | 0.135 (126 of 1872 days never flag) | 184 | 0.547 | 0.413 | 0.0542 | +0.0169 [+0.0113, +0.0231] | +0.0069 [+0.0020, +0.0124] | 0.802 | 0.484 | no |
| 3 | 0.446 (126 of 1871 days never flag) | 138 | 0.406 | 0.406 | 0.0555 | +0.0152 [+0.0099, +0.0204] | +0.0089 [+0.0042, +0.0138] | 0.778 | 0.358 | no |
| 4 | 0.324 (126 of 1870 days never flag) | 162 | 0.522 | 0.444 | 0.0552 | +0.0156 [+0.0107, +0.0207] | +0.0072 [+0.0028, +0.0120] | 0.805 | 0.470 | no |
| 5 | 0.172 (147 of 1869 days never flag) | 158 | 0.500 | 0.437 | 0.0562 | +0.0147 [+0.0096, +0.0200] | +0.0072 [+0.0029, +0.0121] | 0.802 | 0.449 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.457, difference +0.2350 [+0.1088, +0.3609]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0735, ΔBrier vs climatology +0.0560 [+0.0382, +0.0746], realised minus predicted +0.0170 [-0.0075, +0.0428]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.516 | 0.1825 | 0.2720 | +0.0394 [+0.0143, +0.0681] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0331 | 0.0159 | +0.0238 [+0.0063, +0.0380] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.167 | 0.0151 | 0.0200 | +0.0011 [-0.0060, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.759 | 0.500 | 0.0805 | 0.1165 | +0.0273 [+0.0044, +0.0556] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.091 | 0.0081 | 0.0048 | +0.0084 [+0.0062, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0120 | 0.0031 | +0.0268 [+0.0198, +0.0332] |
| scarcity_state | 2 | 41 | 17 | 0.706 | 0.600 | 0.1958 | 0.4146 | 0.0790 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.650 | 0.490 | 0.1760 | 0.2474 | +0.0367 [+0.0133, +0.0617] |
| day_type | month_end | 150 | 17 | 0.882 | 0.556 | 0.1014 | 0.1133 | +0.0435 [+0.0162, +0.0734] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.423 | 0.0419 | 0.0630 | +0.0137 [+0.0074, +0.0205] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.538 | 0.3205 | 0.2903 | +0.0964 [+0.0448, +0.1452] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1254 | 0.1461 | +0.0736 [+0.0406, +0.1103] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3919 | 0.2213 |

## risk_logistic_base+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.192 | 2.27 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.750] | 0.192 | 2.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0842 (84 of 1873 days never flag) | 104 | 0.336 | 0.452 | 0.0592 | +0.0122 [+0.0071, +0.0170] | -0.0029 [-0.0110, +0.0041] | 0.643 | 0.303 | no |
| 2 | 0.0769 (126 of 1872 days never flag) | 101 | 0.331 | 0.455 | 0.0591 | +0.0120 [+0.0068, +0.0169] | +0.0020 [-0.0048, +0.0086] | 0.640 | 0.299 | no |
| 3 | 0.0715 (126 of 1871 days never flag) | 99 | 0.326 | 0.455 | 0.0597 | +0.0110 [+0.0057, +0.0156] | +0.0047 [-0.0018, +0.0106] | 0.638 | 0.295 | no |
| 4 | 0.116 (126 of 1870 days never flag) | 100 | 0.297 | 0.410 | 0.0609 | +0.0099 [+0.0046, +0.0145] | +0.0015 [-0.0052, +0.0076] | 0.633 | 0.263 | no |
| 5 | 0.0569 (147 of 1869 days never flag) | 94 | 0.297 | 0.436 | 0.0616 | +0.0093 [+0.0043, +0.0138] | +0.0018 [-0.0049, +0.0077] | 0.633 | 0.266 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.457, difference +0.2340 [+0.1076, +0.3619]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0859, ΔBrier vs climatology +0.0436 [+0.0303, +0.0588], realised minus predicted +0.0440 [+0.0139, +0.0747]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.561 | 0.1108 | 0.2720 | -0.0007 [-0.0216, +0.0182] |
| regime | 2020 | 251 | 4 | 0.250 | 0.034 | 0.0255 | 0.0159 | +0.0310 [+0.0218, +0.0401] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.765 | 0.0293 | 0.1165 | +0.0162 [+0.0036, +0.0324] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0013 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0071 | 0.0031 | +0.0282 [+0.0219, +0.0344] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0404 | 0.4146 | +0.0117 [-0.0223, +0.0433] |
| scarcity_state | 3 | 473 | 117 | 0.350 | 0.526 | 0.1073 | 0.2474 | +0.0075 [-0.0111, +0.0245] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.0976 | 0.1133 | +0.0378 [+0.0124, +0.0646] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.439 | 0.0127 | 0.0630 | +0.0048 [-0.0004, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.500 | 0.3205 | 0.2903 | +0.0964 [+0.0455, +0.1424] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.450 | 0.1254 | 0.1461 | +0.0736 [+0.0422, +0.1116] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2099 | 0.2213 |

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

## risk_quantile_skewt_base+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.520, 0.848] | 0.269 | 5.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 17 | 0.654 [0.478, 0.812] | 0.269 | 5.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.231 (63 of 1873 days never flag) | 201 | 0.621 | 0.433 | 0.0538 | +0.0177 [+0.0104, +0.0257] | +0.0026 [-0.0025, +0.0077] | 0.799 | 0.556 | no |
| 2 | 0.253 (126 of 1872 days never flag) | 148 | 0.489 | 0.459 | 0.0549 | +0.0162 [+0.0100, +0.0228] | +0.0062 [+0.0005, +0.0125] | 0.800 | 0.443 | no |
| 3 | 0.219 (126 of 1871 days never flag) | 195 | 0.580 | 0.410 | 0.0581 | +0.0125 [+0.0053, +0.0198] | +0.0062 [-0.0011, +0.0133] | 0.779 | 0.513 | no |
| 4 | 0.295 (126 of 1870 days never flag) | 216 | 0.616 | 0.394 | 0.0544 | +0.0164 [+0.0102, +0.0228] | +0.0080 [+0.0023, +0.0141] | 0.807 | 0.540 | no |
| 5 | 0.334 (126 of 1869 days never flag) | 172 | 0.536 | 0.430 | 0.0573 | +0.0136 [+0.0069, +0.0200] | +0.0061 [-0.0003, +0.0120] | 0.805 | 0.480 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.457, difference +0.2206 [+0.0574, +0.3919]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0258, +0.0678], realised minus predicted -0.0017 [-0.0258, +0.0235]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.500 | 0.1794 | 0.2720 | +0.0264 [-0.0007, +0.0546] |
| regime | 2020 | 251 | 4 | 0.250 | 0.034 | 0.0474 | 0.0159 | +0.0195 [+0.0030, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0065 | 0.0000 | +0.0134 [+0.0116, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0238 | 0.0200 | -0.0012 [-0.0083, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.759 | 0.512 | 0.1022 | 0.1165 | +0.0343 [+0.0031, +0.0744] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.167 | 0.0123 | 0.0048 | +0.0077 [+0.0053, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0277 | 0.0031 | +0.0204 [+0.0119, +0.0278] |
| scarcity_state | 2 | 41 | 17 | 0.706 | 0.600 | 0.2517 | 0.4146 | 0.1211 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.632 | 0.481 | 0.1762 | 0.2474 | +0.0286 [+0.0050, +0.0525] |
| day_type | month_end | 150 | 17 | 0.882 | 0.441 | 0.1303 | 0.1133 | +0.0283 [-0.0077, +0.0667] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.425 | 0.0429 | 0.0630 | +0.0124 [+0.0061, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.2995 | 0.2903 | +0.1011 [+0.0326, +0.1630] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2003 | 0.1461 | +0.0655 [+0.0219, +0.1132] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.781] | 0.231 | 2.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.435, 0.800] | 0.231 | 2.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0577 (63 of 1873 days never flag) | 123 | 0.336 | 0.382 | 0.0618 | +0.0096 [+0.0036, +0.0151] | -0.0055 [-0.0141, +0.0021] | 0.642 | 0.292 | no |
| 2 | 0.253 (126 of 1872 days never flag) | 82 | 0.317 | 0.537 | 0.0597 | +0.0113 [+0.0052, +0.0172] | +0.0013 [-0.0064, +0.0088] | 0.640 | 0.295 | no |
| 3 | 0.109 (126 of 1871 days never flag) | 109 | 0.333 | 0.422 | 0.0623 | +0.0084 [+0.0014, +0.0152] | +0.0020 [-0.0062, +0.0100] | 0.641 | 0.297 | no |
| 4 | 0.126 (126 of 1870 days never flag) | 113 | 0.341 | 0.416 | 0.0601 | +0.0107 [+0.0049, +0.0163] | +0.0023 [-0.0050, +0.0091] | 0.635 | 0.302 | no |
| 5 | 0.184 (126 of 1869 days never flag) | 99 | 0.312 | 0.434 | 0.0627 | +0.0082 [+0.0022, +0.0144] | +0.0007 [-0.0067, +0.0078] | 0.634 | 0.279 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.457, difference +0.2212 [+0.0566, +0.3954]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0187, +0.0500], realised minus predicted +0.0244 [-0.0049, +0.0534]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.544 | 0.1077 | 0.2720 | -0.0137 [-0.0364, +0.0081] |
| regime | 2020 | 251 | 4 | 0.250 | 0.027 | 0.0398 | 0.0159 | +0.0267 [+0.0162, +0.0369] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0027 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.400 | 0.500 | 0.0114 | 0.0200 | +0.0018 [-0.0044, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.650 | 0.0510 | 0.1165 | +0.0232 [+0.0038, +0.0453] |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.182 | 0.0056 | 0.0048 | +0.0087 [+0.0068, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.031 | 0.0227 | 0.0031 | +0.0218 [+0.0140, +0.0286] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.0964 | 0.4146 | +0.0537 [-0.0225, +0.1205] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1075 | 0.2474 | -0.0006 [-0.0217, +0.0190] |
| day_type | month_end | 150 | 17 | 0.765 | 0.371 | 0.1265 | 0.1133 | +0.0226 [-0.0118, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.405 | 0.0136 | 0.0630 | +0.0035 [-0.0020, +0.0084] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.412 | 0.2995 | 0.2903 | +0.1011 [+0.0256, +0.1610] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.345 | 0.2003 | 0.1461 | +0.0655 [+0.0214, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

