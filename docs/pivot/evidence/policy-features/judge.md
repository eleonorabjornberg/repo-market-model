# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `be340666b9f9…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## onset_logistic_policy+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.406, 0.742] | 0.231 | 3.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.550] | 0.192 | 1.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.305 (126 of 1873 days never flag) | 145 | 0.436 | 0.421 | 0.0573 | +0.0141 [+0.0108, +0.0179] | -0.0010 [-0.0063, +0.0038] | 0.776 | 0.387 | no |
| 2 | 0.303 (126 of 1872 days never flag) | 120 | 0.345 | 0.400 | 0.0604 | +0.0106 [+0.0077, +0.0138] | +0.0006 [-0.0035, +0.0049] | 0.765 | 0.304 | no |
| 3 | 0.285 (147 of 1871 days never flag) | 79 | 0.203 | 0.354 | 0.0607 | +0.0100 [+0.0055, +0.0139] | +0.0036 [-0.0019, +0.0084] | 0.789 | 0.173 | no |
| 4 | 0.328 (147 of 1870 days never flag) | 81 | 0.232 | 0.395 | 0.0603 | +0.0105 [+0.0067, +0.0144] | +0.0021 [-0.0028, +0.0069] | 0.791 | 0.204 | no |
| 5 | 0.327 (147 of 1869 days never flag) | 63 | 0.188 | 0.413 | 0.0608 | +0.0101 [+0.0061, +0.0139] | +0.0026 [-0.0019, +0.0070] | 0.798 | 0.167 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.457, difference +0.1799 [+0.0695, +0.3101]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0928, ΔBrier vs climatology +0.0367 [+0.0270, +0.0473], realised minus predicted +0.0362 [+0.0026, +0.0726]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.438 | 0.1424 | 0.2720 | +0.0145 [+0.0049, +0.0246] |
| regime | 2020 | 251 | 4 | 0.750 | 0.214 | 0.1036 | 0.0159 | +0.0280 [+0.0186, +0.0371] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0405 | 0.0000 | +0.0100 [+0.0080, +0.0120] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0207 | 0.0200 | +0.0046 [+0.0013, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.533 | 0.0723 | 0.1165 | +0.0214 [+0.0059, +0.0411] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0320 | 0.0048 | +0.0078 [+0.0064, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0569 | 0.0031 | +0.0232 [+0.0150, +0.0312] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0988 | 0.4146 | 0.0482 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.426 | 0.1632 | 0.2474 | +0.0187 [+0.0088, +0.0297] |
| day_type | month_end | 150 | 17 | 0.588 | 0.455 | 0.1263 | 0.1133 | +0.0343 [+0.0174, +0.0539] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.386 | 0.0588 | 0.0630 | +0.0093 [+0.0066, +0.0123] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.455 | 0.3191 | 0.2903 | +0.0695 [+0.0099, +0.1262] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.1089 | 0.1461 | +0.0475 [+0.0329, +0.0648] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.5832 | 0.4822 |
| mar-2020 | 10 | 3 | 1.000 | 1.000 | 0.1666 | 0.2213 |

## rare_gbm_balanced_bootstrap+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 7 | 0.269 [0.105, 0.438] | 0.115 | 1.19 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 3 | 0.115 [0.000, 0.217] | 0.115 | 1.19 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.644 (126 of 1873 days never flag) | 53 | 0.171 | 0.453 | 0.0625 | +0.0089 [-0.0020, +0.0189] | -0.0062 [-0.0156, +0.0020] | 0.853 | 0.155 | no |
| 2 | 0.764 (168 of 1872 days never flag) | 25 | 0.065 | 0.360 | 0.0727 | -0.0016 [-0.0147, +0.0095] | -0.0116 [-0.0233, -0.0016] | 0.800 | 0.056 | no |
| 3 | 0.927 (147 of 1871 days never flag) | 15 | 0.065 | 0.600 | 0.0676 | +0.0031 [-0.0110, +0.0154] | -0.0032 [-0.0169, +0.0084] | 0.866 | 0.062 | no |
| 4 | 0.807 (147 of 1870 days never flag) | 32 | 0.051 | 0.219 | 0.0723 | -0.0015 [-0.0126, +0.0088] | -0.0099 [-0.0203, -0.0004] | 0.823 | 0.036 | no |
| 5 | 0.668 (126 of 1869 days never flag) | 38 | 0.051 | 0.184 | 0.0724 | -0.0015 [-0.0129, +0.0091] | -0.0090 [-0.0200, +0.0004] | 0.807 | 0.033 | no |

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
| regime | 2018-19 | 375 | 102 | 0.216 | 0.431 | 0.3483 | 0.2720 | -0.0221 [-0.0739, +0.0258] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0961 | 0.0159 | +0.0314 [+0.0235, +0.0393] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0117 | 0.0000 | +0.0136 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0098 | 0.0200 | +0.0018 [-0.0023, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0584 | 0.1165 | +0.0255 [+0.0079, +0.0479] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0113 | 0.0048 | +0.0088 [+0.0071, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0417 | 0.0031 | +0.0273 [+0.0213, +0.0331] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1392 | 0.4146 | +0.0811 [+0.0110, +0.1858] |
| scarcity_state | 3 | 473 | 117 | 0.197 | 0.442 | 0.3162 | 0.2474 | -0.0100 [-0.0517, +0.0290] |
| day_type | month_end | 150 | 17 | 0.235 | 0.800 | 0.1083 | 0.1133 | +0.0380 [+0.0172, +0.0604] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.372 | 0.0941 | 0.0630 | +0.0016 [-0.0109, +0.0124] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1692 | 0.2903 | +0.1263 [+0.0343, +0.2181] |
| day_type | tax_date | 89 | 13 | 0.077 | 0.500 | 0.0926 | 0.1461 | +0.0503 [+0.0322, +0.0691] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.000 | – | 0.4124 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1941 | 0.2213 |

## rare_gbm_balanced_bootstrap_policy+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 6 | 0.231 [0.087, 0.375] | 0.154 | 1.65 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 5 | 0.192 [0.062, 0.342] | 0.115 | 1.23 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.715 (126 of 1873 days never flag) | 61 | 0.129 | 0.295 | 0.0638 | +0.0076 [-0.0037, +0.0175] | -0.0075 [-0.0174, +0.0005] | 0.835 | 0.104 | no |
| 2 | 0.691 (147 of 1872 days never flag) | 21 | 0.058 | 0.381 | 0.0707 | +0.0003 [-0.0118, +0.0113] | -0.0097 [-0.0208, +0.0006] | 0.784 | 0.050 | no |
| 3 | 0.786 (147 of 1871 days never flag) | 31 | 0.101 | 0.452 | 0.0647 | +0.0059 [-0.0042, +0.0152] | -0.0004 [-0.0098, +0.0080] | 0.860 | 0.092 | no |
| 4 | 0.868 (147 of 1870 days never flag) | 26 | 0.058 | 0.308 | 0.0684 | +0.0024 [-0.0062, +0.0114] | -0.0061 [-0.0147, +0.0025] | 0.799 | 0.048 | no |
| 5 | 0.733 (126 of 1869 days never flag) | 39 | 0.051 | 0.179 | 0.0696 | +0.0013 [-0.0089, +0.0103] | -0.0062 [-0.0153, +0.0020] | 0.810 | 0.032 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.529 (climatology 0.457, difference +0.0723 [-0.0922, +0.1864]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0874, ΔBrier vs climatology +0.0421 [+0.0266, +0.0617], realised minus predicted +0.0031 [-0.0277, +0.0368]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.137 | 0.264 | 0.3281 | 0.2720 | -0.0304 [-0.0795, +0.0140] |
| regime | 2020 | 251 | 4 | 0.000 | – | 0.0980 | 0.0159 | +0.0307 [+0.0221, +0.0382] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0134 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0144 | 0.0200 | +0.0039 [+0.0002, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.500 | 0.0796 | 0.1165 | +0.0274 [+0.0042, +0.0555] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0139 | 0.0048 | +0.0091 [+0.0075, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0457 | 0.0031 | +0.0269 [+0.0206, +0.0325] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1418 | 0.4146 | 0.0952 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.145 | 0.283 | 0.3088 | 0.2474 | -0.0165 [-0.0571, +0.0206] |
| day_type | month_end | 150 | 17 | 0.294 | 0.625 | 0.1130 | 0.1133 | +0.0349 [+0.0153, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.099 | 0.200 | 0.0943 | 0.0630 | +0.0016 [-0.0112, +0.0127] |
| day_type | quarter_end | 31 | 9 | 0.222 | 1.000 | 0.1767 | 0.2903 | +0.1161 [+0.0356, +0.1923] |
| day_type | tax_date | 89 | 13 | 0.077 | 1.000 | 0.0843 | 0.1461 | +0.0320 [+0.0099, +0.0524] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.000 | – | 0.4745 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2032 | 0.2213 |

