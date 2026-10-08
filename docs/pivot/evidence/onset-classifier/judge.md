# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `eacead154f9b…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## onset_gbm_class_weight+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.143, 0.482] | 0.231 | 3.42 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.107, 0.441] | 0.231 | 3.00 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.296 (126 of 1873 days never flag) | 136 | 0.336 | 0.346 | 0.0706 | +0.0008 [-0.0028, +0.0040] | -0.0143 [-0.0212, -0.0085] | 0.525 | 0.284 | no |
| 2 | 0.313 (210 of 1872 days never flag) | 76 | 0.223 | 0.408 | 0.0751 | -0.0040 [-0.0095, +0.0008] | -0.0140 [-0.0202, -0.0085] | 0.485 | 0.197 | no |
| 3 | 0.317 (147 of 1871 days never flag) | 89 | 0.217 | 0.337 | 0.0739 | -0.0032 [-0.0085, +0.0013] | -0.0096 [-0.0160, -0.0044] | 0.421 | 0.183 | no |
| 4 | 0.347 (147 of 1870 days never flag) | 59 | 0.123 | 0.288 | 0.0757 | -0.0048 [-0.0112, +0.0003] | -0.0133 [-0.0202, -0.0075] | 0.419 | 0.099 | no |
| 5 | 0.413 (126 of 1869 days never flag) | 110 | 0.232 | 0.291 | 0.0720 | -0.0011 [-0.0056, +0.0030] | -0.0086 [-0.0135, -0.0044] | 0.552 | 0.187 | no |

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
| regime | 2018-19 | 375 | 102 | 0.461 | 0.392 | 0.1185 | 0.2720 | -0.0106 [-0.0256, +0.0041] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2041 | 0.0159 | +0.0026 [-0.0048, +0.0097] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0713 | 0.0000 | +0.0078 [+0.0066, +0.0090] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0399 | 0.0200 | +0.0012 [-0.0020, +0.0037] |
| regime | 2025-26 | 249 | 29 | 0.000 | 0.000 | 0.0514 | 0.1165 | -0.0052 [-0.0112, -0.0006] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0567 | 0.0048 | +0.0052 [+0.0039, +0.0065] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1410 | 0.0031 | +0.0071 [+0.0027, +0.0114] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0669 | 0.4146 | -0.0126 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.402 | 0.351 | 0.1366 | 0.2474 | -0.0120 [-0.0241, -0.0006] |
| day_type | month_end | 150 | 17 | 0.412 | 0.467 | 0.1136 | 0.1133 | +0.0091 [-0.0017, +0.0196] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.312 | 0.0876 | 0.0630 | -0.0017 [-0.0045, +0.0007] |
| day_type | quarter_end | 31 | 9 | 0.111 | 0.250 | 0.1115 | 0.2903 | +0.0060 [-0.1023, +0.1222] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.625 | 0.1213 | 0.1461 | +0.0297 [+0.0063, +0.0508] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.6209 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2044 | 0.2213 |

## onset_gbm_class_weight_funding+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.143, 0.500] | 0.231 | 3.38 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.111, 0.450] | 0.231 | 3.00 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.296 (126 of 1873 days never flag) | 135 | 0.336 | 0.348 | 0.0706 | +0.0009 [-0.0026, +0.0040] | -0.0142 [-0.0209, -0.0083] | 0.531 | 0.285 | no |
| 2 | 0.313 (210 of 1872 days never flag) | 76 | 0.223 | 0.408 | 0.0751 | -0.0040 [-0.0096, +0.0006] | -0.0140 [-0.0203, -0.0088] | 0.485 | 0.197 | no |
| 3 | 0.317 (147 of 1871 days never flag) | 89 | 0.217 | 0.337 | 0.0740 | -0.0033 [-0.0086, +0.0010] | -0.0096 [-0.0157, -0.0045] | 0.414 | 0.183 | no |
| 4 | 0.347 (147 of 1870 days never flag) | 59 | 0.123 | 0.288 | 0.0759 | -0.0050 [-0.0112, +0.0004] | -0.0135 [-0.0202, -0.0078] | 0.413 | 0.099 | no |
| 5 | 0.413 (126 of 1869 days never flag) | 111 | 0.239 | 0.297 | 0.0720 | -0.0010 [-0.0053, +0.0029] | -0.0086 [-0.0135, -0.0042] | 0.548 | 0.194 | no |

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
| regime | 2018-19 | 375 | 102 | 0.461 | 0.392 | 0.1185 | 0.2720 | -0.0106 [-0.0248, +0.0034] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2041 | 0.0159 | +0.0026 [-0.0049, +0.0099] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0712 | 0.0000 | +0.0078 [+0.0066, +0.0090] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0398 | 0.0200 | +0.0011 [-0.0022, +0.0037] |
| regime | 2025-26 | 249 | 29 | 0.000 | 0.000 | 0.0545 | 0.1165 | -0.0047 [-0.0111, +0.0001] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0570 | 0.0048 | +0.0052 [+0.0039, +0.0064] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.1412 | 0.0031 | +0.0071 [+0.0029, +0.0116] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0762 | 0.4146 | -0.0071 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.402 | 0.351 | 0.1366 | 0.2474 | -0.0122 [-0.0238, -0.0010] |
| day_type | month_end | 150 | 17 | 0.412 | 0.467 | 0.1145 | 0.1133 | +0.0090 [-0.0010, +0.0214] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.315 | 0.0880 | 0.0630 | -0.0015 [-0.0043, +0.0009] |
| day_type | quarter_end | 31 | 9 | 0.111 | 0.250 | 0.1094 | 0.2903 | +0.0012 [-0.1133, +0.1156] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.625 | 0.1215 | 0.1461 | +0.0294 [+0.0061, +0.0502] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.6209 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2044 | 0.2213 |

## onset_gbm_focal+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.208, 0.565] | 0.231 | 2.85 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.500] | 0.192 | 2.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.3 (126 of 1873 days never flag) | 106 | 0.229 | 0.302 | 0.0681 | +0.0033 [+0.0006, +0.0060] | -0.0118 [-0.0178, -0.0061] | 0.650 | 0.186 | no |
| 2 | 0.317 (147 of 1872 days never flag) | 51 | 0.079 | 0.216 | 0.0699 | +0.0011 [-0.0024, +0.0043] | -0.0089 [-0.0137, -0.0044] | 0.659 | 0.056 | no |
| 3 | 0.452 (147 of 1871 days never flag) | 78 | 0.210 | 0.372 | 0.0683 | +0.0023 [-0.0012, +0.0055] | -0.0040 [-0.0087, -0.0001] | 0.617 | 0.182 | no |
| 4 | 0.343 (210 of 1870 days never flag) | 70 | 0.145 | 0.286 | 0.0698 | +0.0010 [-0.0028, +0.0044] | -0.0074 [-0.0128, -0.0029] | 0.617 | 0.116 | no |
| 5 | 0.358 (126 of 1869 days never flag) | 78 | 0.159 | 0.282 | 0.0660 | +0.0049 [+0.0013, +0.0085] | -0.0026 [-0.0067, +0.0015] | 0.736 | 0.127 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.542 (climatology 0.457, difference +0.0848 [-0.0023, +0.1843]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1090, ΔBrier vs climatology +0.0204 [+0.0127, +0.0284], realised minus predicted +0.0103 [-0.0309, +0.0558]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.386 | 0.1505 | 0.2720 | -0.0000 [-0.0109, +0.0112] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2061 | 0.0159 | +0.0009 [-0.0076, +0.0091] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0680 | 0.0000 | +0.0081 [+0.0068, +0.0094] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0377 | 0.0200 | +0.0010 [-0.0020, +0.0035] |
| regime | 2025-26 | 249 | 29 | 0.000 | 0.000 | 0.0517 | 0.1165 | -0.0011 [-0.0046, +0.0023] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0542 | 0.0048 | +0.0053 [+0.0040, +0.0066] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1400 | 0.0031 | +0.0068 [+0.0020, +0.0116] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0752 | 0.4146 | -0.0046 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.274 | 0.308 | 0.1625 | 0.2474 | -0.0027 [-0.0119, +0.0066] |
| day_type | month_end | 150 | 17 | 0.412 | 0.636 | 0.1259 | 0.1133 | +0.0141 [+0.0049, +0.0244] |
| day_type | ordinary | 1603 | 101 | 0.198 | 0.233 | 0.0920 | 0.0630 | +0.0001 [-0.0021, +0.0022] |
| day_type | quarter_end | 31 | 9 | 0.000 | 0.000 | 0.1367 | 0.2903 | +0.0303 [-0.0714, +0.1348] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.714 | 0.1203 | 0.1461 | +0.0340 [+0.0098, +0.0543] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.6458 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2158 | 0.2213 |

## onset_logistic+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.586] | 0.231 | 3.54 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.519] | 0.231 | 2.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.377 (126 of 1873 days never flag) | 148 | 0.400 | 0.378 | 0.0623 | +0.0092 [+0.0060, +0.0120] | -0.0059 [-0.0121, -0.0004] | 0.686 | 0.347 | no |
| 2 | 0.332 (147 of 1872 days never flag) | 94 | 0.237 | 0.351 | 0.0636 | +0.0075 [+0.0048, +0.0103] | -0.0025 [-0.0074, +0.0019] | 0.707 | 0.202 | no |
| 3 | 0.362 (147 of 1871 days never flag) | 106 | 0.239 | 0.311 | 0.0646 | +0.0061 [+0.0018, +0.0096] | -0.0003 [-0.0062, +0.0044] | 0.723 | 0.197 | no |
| 4 | 0.355 (147 of 1870 days never flag) | 93 | 0.232 | 0.344 | 0.0638 | +0.0070 [+0.0034, +0.0104] | -0.0015 [-0.0069, +0.0033] | 0.748 | 0.197 | no |
| 5 | 0.314 (147 of 1869 days never flag) | 57 | 0.159 | 0.386 | 0.0629 | +0.0081 [+0.0043, +0.0114] | +0.0005 [-0.0047, +0.0053] | 0.781 | 0.139 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.457, difference +0.1386 [+0.0775, +0.2307]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1047, ΔBrier vs climatology +0.0247 [+0.0182, +0.0316], realised minus predicted +0.0395 [+0.0006, +0.0804]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.384 | 0.1406 | 0.2720 | +0.0046 [-0.0073, +0.0158] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1413 | 0.0159 | +0.0189 [+0.0073, +0.0292] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0492 | 0.0000 | +0.0100 [+0.0085, +0.0116] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0213 | 0.0200 | +0.0041 [+0.0015, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.069 | 0.667 | 0.0578 | 0.1165 | +0.0087 [+0.0018, +0.0174] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0398 | 0.0048 | +0.0070 [+0.0057, +0.0084] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0766 | 0.0031 | +0.0217 [+0.0155, +0.0274] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0669 | 0.4146 | +0.0063 [-0.0148, +0.0237] |
| scarcity_state | 3 | 473 | 117 | 0.462 | 0.375 | 0.1604 | 0.2474 | +0.0056 [-0.0045, +0.0157] |
| day_type | month_end | 150 | 17 | 0.471 | 0.444 | 0.1290 | 0.1133 | +0.0242 [+0.0110, +0.0400] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.324 | 0.0660 | 0.0630 | +0.0048 [+0.0019, +0.0077] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3017 | 0.2903 | +0.0670 [+0.0163, +0.1153] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.1152 | 0.1461 | +0.0413 [+0.0262, +0.0582] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.6460 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1735 | 0.2213 |

## onset_logistic_class_weight+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 6 | 0.231 [0.091, 0.381] | 0.115 | 0.81 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 2 | 0.077 [0.000, 0.174] | 0.038 | 0.23 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.722 (126 of 1873 days never flag) | 34 | 0.093 | 0.382 | 0.0658 | +0.0056 [-0.0073, +0.0166] | -0.0094 [-0.0209, +0.0006] | 0.826 | 0.081 | no |
| 2 | 0.885 (147 of 1872 days never flag) | 14 | 0.036 | 0.357 | 0.0776 | -0.0065 [-0.0236, +0.0071] | -0.0165 [-0.0331, -0.0029] | 0.803 | 0.031 | no |
| 3 | 0.969 (147 of 1871 days never flag) | 10 | 0.029 | 0.400 | 0.0760 | -0.0053 [-0.0239, +0.0100] | -0.0116 [-0.0295, +0.0039] | 0.866 | 0.026 | no |
| 4 | 0.902 (147 of 1870 days never flag) | 5 | 0.022 | 0.600 | 0.0721 | -0.0013 [-0.0190, +0.0137] | -0.0098 [-0.0276, +0.0049] | 0.859 | 0.021 | no |
| 5 | 0.9 (147 of 1869 days never flag) | 8 | 0.029 | 0.500 | 0.0712 | -0.0003 [-0.0198, +0.0154] | -0.0078 [-0.0270, +0.0076] | 0.859 | 0.027 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.669 (climatology 0.457, difference +0.2118 [+0.0766, +0.3508]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0235, +0.0676], realised minus predicted -0.0271 [-0.0578, +0.0038]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.078 | 0.320 | 0.2986 | 0.2720 | -0.0222 [-0.0825, +0.0282] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.1368 | 0.0159 | +0.0194 [+0.0074, +0.0300] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0374 | 0.0000 | +0.0116 [+0.0100, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0211 | 0.0200 | +0.0051 [+0.0027, +0.0080] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.556 | 0.1206 | 0.1165 | +0.0162 [-0.0038, +0.0409] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0373 | 0.0048 | +0.0069 [+0.0051, +0.0088] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0719 | 0.0031 | +0.0218 [+0.0152, +0.0283] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1363 | 0.4146 | 0.0620 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.103 | 0.364 | 0.3004 | 0.2474 | -0.0131 [-0.0616, +0.0284] |
| day_type | month_end | 150 | 17 | 0.176 | 0.750 | 0.1462 | 0.1133 | +0.0251 [+0.0073, +0.0457] |
| day_type | ordinary | 1603 | 101 | 0.050 | 0.208 | 0.1024 | 0.0630 | -0.0007 [-0.0143, +0.0102] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.3764 | 0.2903 | +0.0954 [+0.0558, +0.1377] |
| day_type | tax_date | 89 | 13 | 0.154 | 0.667 | 0.1333 | 0.1461 | +0.0562 [+0.0270, +0.0916] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.000 | – | 0.6076 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1780 | 0.2213 |

## onset_logistic_class_weight_funding+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 5 | 0.192 [0.062, 0.333] | 0.115 | 0.77 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 2 | 0.077 [0.000, 0.179] | 0.038 | 0.23 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.722 (126 of 1873 days never flag) | 33 | 0.093 | 0.394 | 0.0649 | +0.0065 [-0.0066, +0.0171] | -0.0086 [-0.0206, +0.0013] | 0.832 | 0.081 | no |
| 2 | 0.885 (147 of 1872 days never flag) | 14 | 0.036 | 0.357 | 0.0761 | -0.0051 [-0.0225, +0.0096] | -0.0151 [-0.0312, -0.0009] | 0.822 | 0.031 | no |
| 3 | 0.969 (147 of 1871 days never flag) | 10 | 0.029 | 0.400 | 0.0751 | -0.0044 [-0.0232, +0.0111] | -0.0107 [-0.0286, +0.0038] | 0.873 | 0.026 | no |
| 4 | 0.902 (147 of 1870 days never flag) | 5 | 0.022 | 0.600 | 0.0709 | -0.0000 [-0.0174, +0.0147] | -0.0085 [-0.0259, +0.0065] | 0.871 | 0.021 | no |
| 5 | 0.9 (147 of 1869 days never flag) | 8 | 0.029 | 0.500 | 0.0688 | +0.0022 [-0.0175, +0.0199] | -0.0054 [-0.0235, +0.0115] | 0.879 | 0.027 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.707 (climatology 0.457, difference +0.2494 [+0.0838, +0.4137]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0800, ΔBrier vs climatology +0.0494 [+0.0290, +0.0736], realised minus predicted -0.0208 [-0.0493, +0.0106]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.078 | 0.320 | 0.2986 | 0.2720 | -0.0222 [-0.0818, +0.0297] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.1310 | 0.0159 | +0.0202 [+0.0080, +0.0316] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0226 | 0.0000 | +0.0128 [+0.0112, +0.0145] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0193 | 0.0200 | +0.0051 [+0.0022, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.625 | 0.1182 | 0.1165 | +0.0182 [-0.0047, +0.0468] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0271 | 0.0048 | +0.0078 [+0.0058, +0.0096] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0639 | 0.0031 | +0.0229 [+0.0157, +0.0295] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.1314 | 0.4146 | 0.0614 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.111 | 0.394 | 0.2999 | 0.2474 | -0.0123 [-0.0620, +0.0294] |
| day_type | month_end | 150 | 17 | 0.235 | 0.800 | 0.1428 | 0.1133 | +0.0310 [+0.0103, +0.0558] |
| day_type | ordinary | 1603 | 101 | 0.059 | 0.250 | 0.0952 | 0.0630 | -0.0002 [-0.0147, +0.0108] |
| day_type | quarter_end | 31 | 9 | 0.222 | 1.000 | 0.3529 | 0.2903 | +0.0936 [+0.0541, +0.1289] |
| day_type | tax_date | 89 | 13 | 0.077 | 0.500 | 0.1232 | 0.1461 | +0.0560 [+0.0283, +0.0916] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.000 | – | 0.6076 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1780 | 0.2213 |

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

