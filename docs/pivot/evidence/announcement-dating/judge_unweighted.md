# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `41c1a1ca772b…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## risk_gbm (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.667] | 0.115 | 1.35 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.115 | 1.04 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 77 | 0.300 | 0.545 | 0.0577 | +0.0137 [+0.0082, +0.0193] | -0.0014 [-0.0097, +0.0063] | 0.642 | 0.280 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 53 | 0.180 | 0.472 | 0.0687 | +0.0024 [-0.0040, +0.0080] | -0.0076 [-0.0161, -0.0005] | 0.578 | 0.164 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0667 | +0.0040 [-0.0025, +0.0098] | -0.0023 [-0.0102, +0.0044] | 0.579 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 46 | 0.167 | 0.500 | 0.0668 | +0.0040 [-0.0028, +0.0099] | -0.0045 [-0.0121, +0.0023] | 0.579 | 0.153 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 48 | 0.152 | 0.438 | 0.0696 | +0.0013 [-0.0053, +0.0074] | -0.0062 [-0.0136, +0.0007] | 0.577 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0022 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0035 | 0.0031 | +0.0296 [+0.0218, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0274 | 0.4146 | -0.0074 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0971 | 0.2474 | +0.0155 [-0.0047, +0.0366] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0985 | 0.1133 | +0.0543 [+0.0303, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0314, +0.2020] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0958 | 0.1461 | +0.0686 [+0.0412, +0.0953] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2003 | 0.2213 |

## risk_gbm+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.778] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.545] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 67 | 0.321 | 0.672 | 0.0497 | +0.0218 [+0.0145, +0.0293] | +0.0067 [+0.0016, +0.0119] | 0.804 | 0.309 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 120 | 0.388 | 0.450 | 0.0624 | +0.0087 [+0.0038, +0.0133] | -0.0013 [-0.0055, +0.0024] | 0.749 | 0.350 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 134 | 0.413 | 0.425 | 0.0606 | +0.0101 [+0.0050, +0.0146] | +0.0038 [-0.0008, +0.0076] | 0.747 | 0.369 | no |
| 4 | 0.258 (147 of 1870 days never flag) | 109 | 0.384 | 0.486 | 0.0603 | +0.0106 [+0.0055, +0.0156] | +0.0021 [-0.0014, +0.0056] | 0.760 | 0.352 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 111 | 0.348 | 0.432 | 0.0636 | +0.0073 [+0.0018, +0.0125] | -0.0002 [-0.0042, +0.0037] | 0.742 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.487 (climatology 0.457, difference +0.0300 [-0.0960, +0.1429]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0862, ΔBrier vs climatology +0.0433 [+0.0303, +0.0579], realised minus predicted +0.0618 [+0.0331, +0.0951]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.1676 | 0.2720 | +0.0417 [+0.0143, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0224 | 0.0159 | +0.0323 [+0.0157, +0.0454] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0152 | 0.0200 | +0.0007 [-0.0068, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0899 | 0.1165 | +0.0266 [+0.0009, +0.0587] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0090 | 0.0048 | +0.0078 [+0.0053, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0085 | 0.0031 | +0.0282 [+0.0200, +0.0355] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1827 | 0.4146 | 0.0599 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.368 | 0.694 | 0.1657 | 0.2474 | +0.0446 [+0.0203, +0.0703] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1023 | 0.1133 | +0.0600 [+0.0346, +0.0873] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0419 | 0.0630 | +0.0138 [+0.0076, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0326, +0.1953] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0419, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3822 | 0.2213 |

## risk_gbm+every_day+gate+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.231 | 2.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.226, 0.560] | 0.231 | 2.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 65 | 0.314 | 0.677 | 0.0498 | +0.0216 [+0.0147, +0.0294] | +0.0065 [+0.0014, +0.0119] | 0.804 | 0.302 | no |
| 2 | 0.316 (147 of 1872 days never flag) | 119 | 0.367 | 0.429 | 0.0627 | +0.0084 [+0.0035, +0.0128] | -0.0016 [-0.0060, +0.0022] | 0.748 | 0.328 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 133 | 0.413 | 0.429 | 0.0609 | +0.0098 [+0.0047, +0.0144] | +0.0035 [-0.0007, +0.0073] | 0.747 | 0.369 | no |
| 4 | 0.338 (147 of 1870 days never flag) | 110 | 0.377 | 0.473 | 0.0610 | +0.0099 [+0.0051, +0.0149] | +0.0014 [-0.0018, +0.0046] | 0.760 | 0.343 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 114 | 0.355 | 0.430 | 0.0636 | +0.0073 [+0.0020, +0.0124] | -0.0002 [-0.0043, +0.0037] | 0.742 | 0.318 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.457, difference +0.0394 [-0.0965, +0.1539]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0850, ΔBrier vs climatology +0.0444 [+0.0311, +0.0584], realised minus predicted +0.0598 [+0.0318, +0.0888]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.694 | 0.1692 | 0.2720 | +0.0420 [+0.0147, +0.0717] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0244 | 0.0159 | +0.0309 [+0.0160, +0.0445] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0129 | 0.0200 | -0.0015 [-0.0093, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0907 | 0.1165 | +0.0286 [+0.0030, +0.0600] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0079 | 0.0048 | +0.0074 [+0.0048, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0096 | 0.0031 | +0.0277 [+0.0190, +0.0354] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2003 | 0.4146 | +0.0733 [+0.0021, +0.1487] |
| scarcity_state | 3 | 473 | 117 | 0.359 | 0.700 | 0.1671 | 0.2474 | +0.0438 [+0.0198, +0.0701] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1010 | 0.1133 | +0.0595 [+0.0347, +0.0863] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0425 | 0.0630 | +0.0134 [+0.0071, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0409, +0.2067] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0989 | 0.1461 | +0.0689 [+0.0399, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3821 | 0.2213 |

## risk_gbm+every_day+gate+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.719] | 0.192 | 2.27 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.619] | 0.192 | 2.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 67 | 0.321 | 0.672 | 0.0497 | +0.0218 [+0.0147, +0.0294] | +0.0067 [+0.0015, +0.0120] | 0.804 | 0.309 | no |
| 2 | 0.716 (147 of 1872 days never flag) | 97 | 0.396 | 0.567 | 0.0541 | +0.0170 [+0.0112, +0.0228] | +0.0070 [+0.0020, +0.0122] | 0.801 | 0.371 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 85 | 0.319 | 0.518 | 0.0561 | +0.0145 [+0.0092, +0.0200] | +0.0082 [+0.0037, +0.0130] | 0.779 | 0.295 | no |
| 4 | 0.396 (147 of 1870 days never flag) | 104 | 0.384 | 0.510 | 0.0538 | +0.0171 [+0.0122, +0.0221] | +0.0086 [+0.0047, +0.0128] | 0.807 | 0.355 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 120 | 0.442 | 0.508 | 0.0547 | +0.0162 [+0.0107, +0.0221] | +0.0087 [+0.0045, +0.0132] | 0.805 | 0.408 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.664 (climatology 0.457, difference +0.2071 [+0.0378, +0.3580]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0719, ΔBrier vs climatology +0.0575 [+0.0405, +0.0777], realised minus predicted +0.0323 [+0.0077, +0.0580]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.1676 | 0.2720 | +0.0417 [+0.0146, +0.0694] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0224 | 0.0159 | +0.0323 [+0.0166, +0.0452] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0152 | 0.0200 | +0.0007 [-0.0063, +0.0058] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0899 | 0.1165 | +0.0266 [-0.0000, +0.0579] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0090 | 0.0048 | +0.0078 [+0.0053, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0085 | 0.0031 | +0.0282 [+0.0200, +0.0360] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1827 | 0.4146 | 0.0599 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.368 | 0.694 | 0.1657 | 0.2474 | +0.0446 [+0.0200, +0.0698] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1023 | 0.1133 | +0.0600 [+0.0349, +0.0873] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0419 | 0.0630 | +0.0138 [+0.0075, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0332, +0.1954] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0415, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3822 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.417, 0.741] | 0.192 | 2.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.650] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 65 | 0.314 | 0.677 | 0.0498 | +0.0216 [+0.0142, +0.0289] | +0.0065 [+0.0011, +0.0118] | 0.804 | 0.302 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 96 | 0.381 | 0.552 | 0.0544 | +0.0166 [+0.0116, +0.0221] | +0.0066 [+0.0019, +0.0117] | 0.800 | 0.356 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 93 | 0.333 | 0.495 | 0.0570 | +0.0137 [+0.0083, +0.0189] | +0.0074 [+0.0025, +0.0124] | 0.776 | 0.306 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 93 | 0.377 | 0.559 | 0.0532 | +0.0176 [+0.0122, +0.0229] | +0.0092 [+0.0049, +0.0138] | 0.807 | 0.353 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 123 | 0.449 | 0.504 | 0.0539 | +0.0170 [+0.0115, +0.0226] | +0.0095 [+0.0051, +0.0144] | 0.804 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.457, difference +0.2581 [+0.0710, +0.4127]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0726, ΔBrier vs climatology +0.0569 [+0.0394, +0.0760], realised minus predicted +0.0315 [+0.0067, +0.0570]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.694 | 0.1692 | 0.2720 | +0.0420 [+0.0131, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0244 | 0.0159 | +0.0309 [+0.0152, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0129 | 0.0200 | -0.0015 [-0.0087, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0907 | 0.1165 | +0.0286 [+0.0022, +0.0591] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0079 | 0.0048 | +0.0074 [+0.0050, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0096 | 0.0031 | +0.0277 [+0.0187, +0.0358] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2003 | 0.4146 | +0.0733 [-0.0010, +0.1500] |
| scarcity_state | 3 | 473 | 117 | 0.359 | 0.700 | 0.1671 | 0.2474 | +0.0438 [+0.0178, +0.0695] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1010 | 0.1133 | +0.0595 [+0.0350, +0.0859] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0425 | 0.0630 | +0.0134 [+0.0067, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2074 | 0.2903 | +0.1247 [+0.0406, +0.2112] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0989 | 0.1461 | +0.0689 [+0.0406, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3821 | 0.2213 |

## risk_gbm+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.323, 0.667] | 0.115 | 1.35 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.129, 0.423] | 0.115 | 1.12 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 76 | 0.293 | 0.539 | 0.0579 | +0.0135 [+0.0079, +0.0190] | -0.0016 [-0.0101, +0.0060] | 0.642 | 0.273 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 52 | 0.158 | 0.423 | 0.0690 | +0.0021 [-0.0047, +0.0079] | -0.0079 [-0.0164, -0.0006] | 0.578 | 0.141 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 52 | 0.188 | 0.500 | 0.0670 | +0.0037 [-0.0031, +0.0096] | -0.0026 [-0.0101, +0.0039] | 0.580 | 0.173 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 52 | 0.188 | 0.500 | 0.0675 | +0.0033 [-0.0035, +0.0093] | -0.0052 [-0.0130, +0.0015] | 0.579 | 0.173 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 51 | 0.159 | 0.431 | 0.0696 | +0.0013 [-0.0050, +0.0073] | -0.0062 [-0.0137, +0.0005] | 0.577 | 0.143 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.496 (climatology 0.457, difference +0.0385 [-0.1046, +0.1645]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1037, ΔBrier vs climatology +0.0258 [+0.0163, +0.0353], realised minus predicted +0.0912 [+0.0561, +0.1275]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0220, +0.0229] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0168 | 0.0159 | +0.0382 [+0.0296, +0.0469] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0005 | 0.0200 | +0.0014 [-0.0034, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0395 | 0.1165 | +0.0174 [+0.0002, +0.0394] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0012 | 0.0048 | +0.0084 [+0.0063, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0046 | 0.0031 | +0.0291 [+0.0212, +0.0364] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0449 | 0.4146 | 0.0060 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0984 | 0.2474 | +0.0146 [-0.0062, +0.0352] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0972 | 0.1133 | +0.0538 [+0.0313, +0.0774] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.500 | 0.0133 | 0.0630 | +0.0045 [-0.0007, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0394, +0.2069] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0989 | 0.1461 | +0.0689 [+0.0404, +0.0985] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2001 | 0.2213 |

## risk_gbm+settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.708] | 0.115 | 1.35 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.600] | 0.115 | 1.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 77 | 0.300 | 0.545 | 0.0577 | +0.0137 [+0.0077, +0.0192] | -0.0014 [-0.0100, +0.0063] | 0.642 | 0.280 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 64 | 0.273 | 0.594 | 0.0589 | +0.0121 [+0.0070, +0.0167] | +0.0021 [-0.0049, +0.0089] | 0.639 | 0.258 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 65 | 0.283 | 0.600 | 0.0603 | +0.0104 [+0.0049, +0.0154] | +0.0040 [-0.0026, +0.0102] | 0.637 | 0.268 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 55 | 0.239 | 0.600 | 0.0595 | +0.0114 [+0.0061, +0.0161] | +0.0029 [-0.0036, +0.0086] | 0.633 | 0.226 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 61 | 0.261 | 0.590 | 0.0601 | +0.0108 [+0.0059, +0.0154] | +0.0033 [-0.0030, +0.0089] | 0.633 | 0.246 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.666 (climatology 0.457, difference +0.2093 [+0.0434, +0.3629]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0855, ΔBrier vs climatology +0.0440 [+0.0311, +0.0571], realised minus predicted +0.0600 [+0.0320, +0.0917]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0959 | 0.2720 | +0.0016 [-0.0229, +0.0224] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0148 | 0.0159 | +0.0396 [+0.0312, +0.0486] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0028 | 0.0200 | +0.0037 [-0.0003, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0386 | 0.1165 | +0.0155 [-0.0031, +0.0393] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0022 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0035 | 0.0031 | +0.0296 [+0.0220, +0.0366] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0274 | 0.4146 | -0.0074 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0971 | 0.2474 | +0.0155 [-0.0069, +0.0358] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0985 | 0.1133 | +0.0543 [+0.0303, +0.0790] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0007, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0341, +0.1996] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0958 | 0.1461 | +0.0686 [+0.0400, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2003 | 0.2213 |

## risk_gbm+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.710] | 0.115 | 1.35 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.607] | 0.115 | 1.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 76 | 0.293 | 0.539 | 0.0579 | +0.0135 [+0.0081, +0.0193] | -0.0016 [-0.0095, +0.0062] | 0.642 | 0.273 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0593 | +0.0117 [+0.0069, +0.0165] | +0.0017 [-0.0052, +0.0083] | 0.639 | 0.259 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 63 | 0.254 | 0.556 | 0.0612 | +0.0095 [+0.0041, +0.0147] | +0.0032 [-0.0037, +0.0092] | 0.636 | 0.237 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 64 | 0.268 | 0.578 | 0.0589 | +0.0119 [+0.0070, +0.0167] | +0.0034 [-0.0027, +0.0094] | 0.633 | 0.253 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 63 | 0.261 | 0.571 | 0.0593 | +0.0116 [+0.0067, +0.0163] | +0.0041 [-0.0020, +0.0098] | 0.632 | 0.245 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.714 (climatology 0.457, difference +0.2566 [+0.0629, +0.4146]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0429 [+0.0308, +0.0563], realised minus predicted +0.0594 [+0.0304, +0.0911]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0211, +0.0239] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0168 | 0.0159 | +0.0382 [+0.0294, +0.0470] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0005 | 0.0200 | +0.0014 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0395 | 0.1165 | +0.0174 [+0.0002, +0.0403] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0012 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0046 | 0.0031 | +0.0291 [+0.0209, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.0449 | 0.4146 | 0.0060 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0984 | 0.2474 | +0.0146 [-0.0055, +0.0359] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0972 | 0.1133 | +0.0538 [+0.0302, +0.0783] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.500 | 0.0133 | 0.0630 | +0.0045 [-0.0005, +0.0095] |
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
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.419] | 0.115 | 1.27 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 81 | 0.300 | 0.519 | 0.0592 | +0.0122 [+0.0075, +0.0168] | -0.0029 [-0.0106, +0.0039] | 0.643 | 0.277 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 49 | 0.173 | 0.490 | 0.0691 | +0.0020 [-0.0047, +0.0081] | -0.0080 [-0.0168, -0.0003] | 0.578 | 0.158 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 55 | 0.159 | 0.400 | 0.0677 | +0.0029 [-0.0038, +0.0089] | -0.0034 [-0.0115, +0.0034] | 0.579 | 0.140 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0668 | +0.0040 [-0.0023, +0.0100] | -0.0044 [-0.0120, +0.0023] | 0.579 | 0.179 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 49 | 0.152 | 0.429 | 0.0696 | +0.0013 [-0.0055, +0.0072] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.136 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
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
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0354 | 0.1165 | +0.0158 [+0.0016, +0.0330] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0072 | 0.0031 | +0.0290 [+0.0225, +0.0354] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0352 | 0.4146 | -0.0002 [-0.0278, +0.0371] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.565 | 0.1006 | 0.2474 | +0.0080 [-0.0097, +0.0247] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0983 | 0.1133 | +0.0339 [+0.0115, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0128 | 0.0630 | +0.0052 [+0.0001, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1101 [+0.0294, +0.1928] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1197 | 0.1461 | +0.0681 [+0.0463, +0.0927] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2084 | 0.2213 |

## risk_gbm_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.231 | 2.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.520] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 136 | 0.507 | 0.522 | 0.0511 | +0.0203 [+0.0135, +0.0272] | +0.0052 [+0.0007, +0.0098] | 0.805 | 0.470 | no |
| 2 | 0.315 (147 of 1872 days never flag) | 122 | 0.388 | 0.443 | 0.0628 | +0.0083 [+0.0035, +0.0129] | -0.0017 [-0.0059, +0.0021] | 0.748 | 0.349 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 130 | 0.399 | 0.423 | 0.0617 | +0.0090 [+0.0040, +0.0138] | +0.0027 [-0.0017, +0.0065] | 0.745 | 0.355 | no |
| 4 | 0.265 (147 of 1870 days never flag) | 109 | 0.384 | 0.486 | 0.0602 | +0.0106 [+0.0055, +0.0155] | +0.0021 [-0.0015, +0.0055] | 0.761 | 0.352 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 107 | 0.333 | 0.430 | 0.0636 | +0.0073 [+0.0021, +0.0122] | -0.0002 [-0.0043, +0.0036] | 0.740 | 0.298 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.457, difference +0.0407 [-0.0963, +0.1618]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0878, ΔBrier vs climatology +0.0417 [+0.0289, +0.0553], realised minus predicted +0.0592 [+0.0303, +0.0907]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.559 | 0.1689 | 0.2720 | +0.0386 [+0.0127, +0.0658] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0329 | 0.0159 | +0.0256 [+0.0080, +0.0396] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0145 | 0.0200 | +0.0009 [-0.0065, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.522 | 0.0867 | 0.1165 | +0.0269 [+0.0031, +0.0546] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0076 | 0.0048 | +0.0084 [+0.0062, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0121 | 0.0031 | +0.0276 [+0.0203, +0.0338] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.500 | 0.1906 | 0.4146 | 0.0671 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.533 | 0.1693 | 0.2474 | +0.0372 [+0.0134, +0.0612] |
| day_type | month_end | 150 | 17 | 0.588 | 0.526 | 0.1021 | 0.1133 | +0.0395 [+0.0145, +0.0650] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.480 | 0.0421 | 0.0630 | +0.0141 [+0.0076, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0304, +0.1894] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0458, +0.0933] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3903 | 0.2213 |

## risk_gbm_base+every_day+gate+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.348, 0.731] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.519] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.308 (105 of 1873 days never flag) | 136 | 0.507 | 0.522 | 0.0514 | +0.0200 [+0.0132, +0.0271] | +0.0049 [+0.0002, +0.0098] | 0.805 | 0.470 | no |
| 2 | 0.25 (147 of 1872 days never flag) | 111 | 0.353 | 0.441 | 0.0631 | +0.0080 [+0.0031, +0.0125] | -0.0020 [-0.0061, +0.0018] | 0.748 | 0.317 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 133 | 0.406 | 0.421 | 0.0610 | +0.0097 [+0.0048, +0.0142] | +0.0034 [-0.0007, +0.0072] | 0.746 | 0.361 | no |
| 4 | 0.527 (147 of 1870 days never flag) | 105 | 0.377 | 0.495 | 0.0613 | +0.0095 [+0.0048, +0.0140] | +0.0010 [-0.0027, +0.0046] | 0.759 | 0.346 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 111 | 0.348 | 0.432 | 0.0636 | +0.0073 [+0.0020, +0.0121] | -0.0002 [-0.0045, +0.0035] | 0.740 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.504 (climatology 0.457, difference +0.0472 [-0.0864, +0.1635]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0860, ΔBrier vs climatology +0.0434 [+0.0302, +0.0574], realised minus predicted +0.0593 [+0.0304, +0.0919]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.552 | 0.1717 | 0.2720 | +0.0380 [+0.0114, +0.0670] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0291 | 0.0159 | +0.0271 [+0.0075, +0.0430] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0127 | 0.0200 | -0.0018 [-0.0098, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.0812 | 0.1165 | +0.0264 [+0.0036, +0.0536] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0070 | 0.0048 | +0.0079 [+0.0054, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0091 | 0.0031 | +0.0285 [+0.0209, +0.0354] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.500 | 0.1841 | 0.4146 | 0.0637 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.532 | 0.1697 | 0.2474 | +0.0368 [+0.0133, +0.0616] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.0993 | 0.1133 | +0.0436 [+0.0215, +0.0663] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.480 | 0.0424 | 0.0630 | +0.0134 [+0.0070, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0189, +0.1788] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0484, +0.0951] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3835 | 0.2213 |

## risk_gbm_base+every_day+gate+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.690] | 0.231 | 2.50 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.611] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 136 | 0.507 | 0.522 | 0.0511 | +0.0203 [+0.0137, +0.0272] | +0.0052 [+0.0008, +0.0099] | 0.805 | 0.470 | no |
| 2 | 0.435 (147 of 1872 days never flag) | 104 | 0.410 | 0.548 | 0.0548 | +0.0163 [+0.0108, +0.0223] | +0.0063 [+0.0016, +0.0116] | 0.800 | 0.383 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 98 | 0.362 | 0.510 | 0.0551 | +0.0156 [+0.0103, +0.0211] | +0.0092 [+0.0045, +0.0141] | 0.779 | 0.335 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 101 | 0.413 | 0.564 | 0.0539 | +0.0169 [+0.0112, +0.0229] | +0.0085 [+0.0040, +0.0133] | 0.806 | 0.388 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 121 | 0.435 | 0.496 | 0.0559 | +0.0150 [+0.0098, +0.0204] | +0.0075 [+0.0030, +0.0120] | 0.803 | 0.400 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.683 (climatology 0.457, difference +0.2259 [+0.0609, +0.3747]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0751, ΔBrier vs climatology +0.0543 [+0.0350, +0.0746], realised minus predicted +0.0247 [-0.0006, +0.0535]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.559 | 0.1689 | 0.2720 | +0.0386 [+0.0128, +0.0656] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0329 | 0.0159 | +0.0256 [+0.0092, +0.0400] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0145 | 0.0200 | +0.0009 [-0.0066, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.522 | 0.0867 | 0.1165 | +0.0269 [+0.0029, +0.0560] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0076 | 0.0048 | +0.0084 [+0.0061, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0121 | 0.0031 | +0.0276 [+0.0204, +0.0345] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.500 | 0.1906 | 0.4146 | 0.0671 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.556 | 0.533 | 0.1693 | 0.2474 | +0.0372 [+0.0140, +0.0607] |
| day_type | month_end | 150 | 17 | 0.588 | 0.526 | 0.1021 | 0.1133 | +0.0395 [+0.0158, +0.0639] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.480 | 0.0421 | 0.0630 | +0.0141 [+0.0076, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1101 [+0.0286, +0.1901] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1197 | 0.1461 | +0.0681 [+0.0462, +0.0937] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3903 | 0.2213 |

## risk_gbm_base+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.316, 0.684] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 2.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.308 (105 of 1873 days never flag) | 136 | 0.507 | 0.522 | 0.0514 | +0.0200 [+0.0130, +0.0277] | +0.0049 [+0.0002, +0.0099] | 0.805 | 0.470 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 102 | 0.396 | 0.539 | 0.0548 | +0.0163 [+0.0108, +0.0219] | +0.0063 [+0.0016, +0.0115] | 0.800 | 0.369 | no |
| 3 | 0.363 (147 of 1871 days never flag) | 100 | 0.370 | 0.510 | 0.0551 | +0.0156 [+0.0106, +0.0209] | +0.0093 [+0.0049, +0.0136] | 0.777 | 0.341 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 91 | 0.377 | 0.571 | 0.0542 | +0.0166 [+0.0112, +0.0224] | +0.0082 [+0.0037, +0.0133] | 0.805 | 0.354 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 127 | 0.442 | 0.480 | 0.0547 | +0.0163 [+0.0106, +0.0221] | +0.0087 [+0.0040, +0.0139] | 0.802 | 0.404 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.722 (climatology 0.457, difference +0.2644 [+0.0784, +0.4292]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0734, ΔBrier vs climatology +0.0561 [+0.0373, +0.0754], realised minus predicted +0.0261 [+0.0006, +0.0526]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.552 | 0.1717 | 0.2720 | +0.0380 [+0.0117, +0.0675] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0291 | 0.0159 | +0.0271 [+0.0077, +0.0427] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0127 | 0.0200 | -0.0018 [-0.0094, +0.0044] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.0812 | 0.1165 | +0.0264 [+0.0031, +0.0546] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0070 | 0.0048 | +0.0079 [+0.0053, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0091 | 0.0031 | +0.0285 [+0.0208, +0.0355] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.500 | 0.1841 | 0.4146 | 0.0637 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.532 | 0.1697 | 0.2474 | +0.0368 [+0.0130, +0.0628] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.0993 | 0.1133 | +0.0436 [+0.0220, +0.0677] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.480 | 0.0424 | 0.0630 | +0.0134 [+0.0069, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1739 | 0.2903 | +0.0993 [+0.0164, +0.1817] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1094 | 0.1461 | +0.0713 [+0.0493, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3835 | 0.2213 |

## risk_gbm_base+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.720] | 0.115 | 1.19 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.115 | 1.15 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 73 | 0.300 | 0.575 | 0.0595 | +0.0119 [+0.0067, +0.0168] | -0.0032 [-0.0114, +0.0040] | 0.643 | 0.282 | no |
| 2 | 0.211 (147 of 1872 days never flag) | 50 | 0.180 | 0.500 | 0.0694 | +0.0017 [-0.0045, +0.0076] | -0.0083 [-0.0169, -0.0010] | 0.578 | 0.165 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 55 | 0.181 | 0.455 | 0.0671 | +0.0036 [-0.0031, +0.0096] | -0.0027 [-0.0104, +0.0039] | 0.579 | 0.164 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 56 | 0.188 | 0.464 | 0.0679 | +0.0029 [-0.0039, +0.0089] | -0.0056 [-0.0133, +0.0012] | 0.579 | 0.171 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 49 | 0.145 | 0.408 | 0.0696 | +0.0013 [-0.0053, +0.0070] | -0.0062 [-0.0142, +0.0001] | 0.576 | 0.128 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.503 (climatology 0.457, difference +0.0463 [-0.0998, +0.1739]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1046, ΔBrier vs climatology +0.0248 [+0.0157, +0.0347], realised minus predicted +0.0910 [+0.0556, +0.1285]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1000 | 0.2720 | -0.0021 [-0.0225, +0.0166] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0215 | 0.0159 | +0.0344 [+0.0205, +0.0461] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0012 [-0.0039, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0299 | 0.1165 | +0.0153 [+0.0018, +0.0317] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0003 | 0.0048 | +0.0088 [+0.0070, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0042 | 0.0031 | +0.0299 [+0.0230, +0.0364] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0287 | 0.4146 | -0.0036 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.591 | 0.1010 | 0.2474 | +0.0076 [-0.0107, +0.0248] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0955 | 0.1133 | +0.0379 [+0.0169, +0.0587] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.552 | 0.0132 | 0.0630 | +0.0045 [-0.0007, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.1739 | 0.2903 | +0.0993 [+0.0206, +0.1796] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1094 | 0.1461 | +0.0713 [+0.0478, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2015 | 0.2213 |

## risk_gbm_base+settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.677] | 0.154 | 1.50 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.571] | 0.115 | 1.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 81 | 0.300 | 0.519 | 0.0592 | +0.0122 [+0.0074, +0.0168] | -0.0029 [-0.0108, +0.0038] | 0.643 | 0.277 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 68 | 0.273 | 0.559 | 0.0596 | +0.0114 [+0.0064, +0.0162] | +0.0014 [-0.0054, +0.0079] | 0.639 | 0.256 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 66 | 0.268 | 0.561 | 0.0593 | +0.0114 [+0.0063, +0.0166] | +0.0051 [-0.0010, +0.0112] | 0.637 | 0.251 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 67 | 0.283 | 0.582 | 0.0596 | +0.0112 [+0.0059, +0.0166] | +0.0028 [-0.0040, +0.0090] | 0.632 | 0.266 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 66 | 0.261 | 0.545 | 0.0613 | +0.0096 [+0.0044, +0.0143] | +0.0021 [-0.0044, +0.0082] | 0.632 | 0.244 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.683 (climatology 0.457, difference +0.2262 [+0.0742, +0.3710]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0878, ΔBrier vs climatology +0.0417 [+0.0270, +0.0573], realised minus predicted +0.0521 [+0.0210, +0.0848]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0972 | 0.2720 | -0.0015 [-0.0206, +0.0151] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0253 | 0.0159 | +0.0329 [+0.0219, +0.0435] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [+0.0002, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0354 | 0.1165 | +0.0158 [+0.0021, +0.0337] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0072 | 0.0031 | +0.0290 [+0.0228, +0.0347] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0352 | 0.4146 | -0.0002 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.565 | 0.1006 | 0.2474 | +0.0080 [-0.0095, +0.0247] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0983 | 0.1133 | +0.0339 [+0.0105, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0128 | 0.0630 | +0.0052 [+0.0001, +0.0098] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1101 [+0.0311, +0.1880] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1197 | 0.1461 | +0.0681 [+0.0450, +0.0926] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2084 | 0.2213 |

## risk_gbm_base+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.720] | 0.115 | 1.23 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.211, 0.571] | 0.115 | 1.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 73 | 0.300 | 0.575 | 0.0595 | +0.0119 [+0.0068, +0.0166] | -0.0032 [-0.0114, +0.0038] | 0.643 | 0.282 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 68 | 0.281 | 0.574 | 0.0596 | +0.0114 [+0.0064, +0.0167] | +0.0014 [-0.0053, +0.0083] | 0.639 | 0.264 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 64 | 0.268 | 0.578 | 0.0592 | +0.0114 [+0.0069, +0.0161] | +0.0051 [-0.0004, +0.0108] | 0.637 | 0.253 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 67 | 0.268 | 0.552 | 0.0599 | +0.0109 [+0.0059, +0.0161] | +0.0025 [-0.0038, +0.0090] | 0.631 | 0.251 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 67 | 0.254 | 0.522 | 0.0601 | +0.0109 [+0.0058, +0.0156] | +0.0033 [-0.0032, +0.0093] | 0.631 | 0.235 | no |

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
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0215 | 0.0159 | +0.0344 [+0.0215, +0.0463] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0012 [-0.0040, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0299 | 0.1165 | +0.0153 [+0.0018, +0.0321] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0003 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0042 | 0.0031 | +0.0299 [+0.0227, +0.0368] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0287 | 0.4146 | -0.0036 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.591 | 0.1010 | 0.2474 | +0.0076 [-0.0114, +0.0247] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0955 | 0.1133 | +0.0379 [+0.0174, +0.0602] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.552 | 0.0132 | 0.0630 | +0.0045 [-0.0010, +0.0091] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.1739 | 0.2903 | +0.0993 [+0.0197, +0.1799] |
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
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.724] | 0.192 | 1.85 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.105 (105 of 1873 days never flag) | 91 | 0.307 | 0.473 | 0.0606 | +0.0108 [+0.0056, +0.0158] | -0.0043 [-0.0128, +0.0035] | 0.642 | 0.279 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 54 | 0.201 | 0.519 | 0.0676 | +0.0035 [-0.0030, +0.0092] | -0.0065 [-0.0146, +0.0005] | 0.579 | 0.186 | no |
| 3 | 0.0841 (147 of 1871 days never flag) | 59 | 0.203 | 0.475 | 0.0689 | +0.0018 [-0.0055, +0.0085] | -0.0045 [-0.0134, +0.0031] | 0.579 | 0.185 | no |
| 4 | 0.107 (147 of 1870 days never flag) | 66 | 0.188 | 0.394 | 0.0688 | +0.0020 [-0.0047, +0.0081] | -0.0065 [-0.0150, +0.0012] | 0.578 | 0.165 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 59 | 0.159 | 0.373 | 0.0690 | +0.0019 [-0.0052, +0.0083] | -0.0056 [-0.0140, +0.0017] | 0.577 | 0.138 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.457, difference +0.1155 [-0.0282, +0.2340]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0220 [+0.0108, +0.0330], realised minus predicted +0.0748 [+0.0408, +0.1112]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1074 | 0.2720 | -0.0026 [-0.0240, +0.0179] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0308 | 0.0159 | +0.0252 [+0.0095, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0059 | 0.0200 | +0.0050 [+0.0008, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0332 | 0.1165 | +0.0133 [+0.0003, +0.0294] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0069 | 0.0031 | +0.0280 [+0.0221, +0.0336] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0360 | 0.4146 | 0.0046 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.506 | 0.1081 | 0.2474 | +0.0032 [-0.0160, +0.0217] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1022 | 0.1133 | +0.0282 [+0.0011, +0.0563] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.455 | 0.0126 | 0.0630 | +0.0040 [-0.0012, +0.0088] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3561 | 0.2903 | +0.0892 [+0.0158, +0.1596] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1296 | 0.1461 | +0.0774 [+0.0463, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2020 | 0.2213 |

## risk_logistic+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.720] | 0.231 | 3.00 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.219, 0.548] | 0.231 | 3.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (105 of 1873 days never flag) | 123 | 0.443 | 0.504 | 0.0525 | +0.0189 [+0.0122, +0.0264] | +0.0038 [-0.0018, +0.0096] | 0.801 | 0.408 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 75 | 0.252 | 0.467 | 0.0613 | +0.0098 [+0.0039, +0.0157] | -0.0002 [-0.0051, +0.0047] | 0.752 | 0.229 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 78 | 0.268 | 0.474 | 0.0628 | +0.0079 [+0.0011, +0.0144] | +0.0015 [-0.0048, +0.0076] | 0.746 | 0.244 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 65 | 0.246 | 0.523 | 0.0623 | +0.0086 [+0.0029, +0.0143] | +0.0001 [-0.0053, +0.0056] | 0.758 | 0.228 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 141 | 0.457 | 0.447 | 0.0630 | +0.0079 [+0.0025, +0.0134] | +0.0004 [-0.0044, +0.0050] | 0.743 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.457, difference +0.1358 [+0.0033, +0.2420]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0908, ΔBrier vs climatology +0.0386 [+0.0219, +0.0543], realised minus predicted +0.0450 [+0.0160, +0.0733]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.562 | 0.1791 | 0.2720 | +0.0375 [+0.0124, +0.0643] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0384 | 0.0159 | +0.0179 [-0.0056, +0.0369] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0183 | 0.0200 | +0.0020 [-0.0055, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0845 | 0.1165 | +0.0244 [+0.0024, +0.0530] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0099 | 0.0048 | +0.0082 [+0.0057, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0119 | 0.0031 | +0.0266 [+0.0198, +0.0330] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1914 | 0.4146 | 0.0719 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.487 | 0.528 | 0.1768 | 0.2474 | +0.0324 [+0.0082, +0.0578] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.1060 | 0.1133 | +0.0339 [+0.0051, +0.0632] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.474 | 0.0419 | 0.0630 | +0.0129 [+0.0068, +0.0197] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0134, +0.1635] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0481, +0.1152] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3840 | 0.2213 |

## risk_logistic+every_day+gate+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.182, 0.520] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (105 of 1873 days never flag) | 130 | 0.464 | 0.500 | 0.0523 | +0.0191 [+0.0123, +0.0263] | +0.0040 [-0.0013, +0.0096] | 0.801 | 0.427 | no |
| 2 | 0.402 (147 of 1872 days never flag) | 65 | 0.245 | 0.523 | 0.0601 | +0.0109 [+0.0053, +0.0168] | +0.0009 [-0.0035, +0.0056] | 0.752 | 0.227 | no |
| 3 | 0.756 (147 of 1871 days never flag) | 66 | 0.246 | 0.515 | 0.0603 | +0.0103 [+0.0045, +0.0165] | +0.0040 [-0.0012, +0.0094] | 0.747 | 0.228 | no |
| 4 | 0.649 (147 of 1870 days never flag) | 51 | 0.188 | 0.510 | 0.0606 | +0.0103 [+0.0045, +0.0157] | +0.0018 [-0.0026, +0.0065] | 0.759 | 0.174 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 140 | 0.457 | 0.450 | 0.0632 | +0.0077 [+0.0021, +0.0133] | +0.0002 [-0.0049, +0.0052] | 0.744 | 0.412 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.567 (climatology 0.457, difference +0.1101 [-0.0101, +0.2107]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0409 [+0.0257, +0.0569], realised minus predicted +0.0449 [+0.0162, +0.0735]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.541 | 0.1820 | 0.2720 | +0.0382 [+0.0119, +0.0662] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0359 | 0.0159 | +0.0193 [-0.0051, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0182 | 0.0200 | +0.0021 [-0.0048, +0.0082] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0821 | 0.1165 | +0.0236 [+0.0016, +0.0514] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0098 | 0.0048 | +0.0083 [+0.0059, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0102 | 0.0031 | +0.0271 [+0.0199, +0.0333] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1902 | 0.4146 | 0.0703 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.517 | 0.1779 | 0.2474 | +0.0329 [+0.0083, +0.0592] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1046 | 0.1133 | +0.0362 [+0.0097, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.455 | 0.0422 | 0.0630 | +0.0129 [+0.0065, +0.0198] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0174, +0.1659] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0439, +0.1141] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic+every_day+gate+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.708] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.667] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.39 (105 of 1873 days never flag) | 123 | 0.443 | 0.504 | 0.0525 | +0.0189 [+0.0120, +0.0258] | +0.0038 [-0.0017, +0.0093] | 0.801 | 0.408 | no |
| 2 | 0.864 (126 of 1872 days never flag) | 70 | 0.230 | 0.457 | 0.0557 | +0.0153 [+0.0099, +0.0212] | +0.0053 [+0.0001, +0.0107] | 0.799 | 0.208 | no |
| 3 | 0.415 (126 of 1871 days never flag) | 65 | 0.239 | 0.508 | 0.0555 | +0.0152 [+0.0099, +0.0211] | +0.0088 [+0.0038, +0.0143] | 0.778 | 0.221 | no |
| 4 | 0.683 (126 of 1870 days never flag) | 89 | 0.348 | 0.539 | 0.0546 | +0.0162 [+0.0113, +0.0215] | +0.0078 [+0.0036, +0.0128] | 0.805 | 0.324 | no |
| 5 | 0.334 (126 of 1869 days never flag) | 143 | 0.478 | 0.462 | 0.0547 | +0.0162 [+0.0109, +0.0218] | +0.0087 [+0.0044, +0.0132] | 0.805 | 0.434 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.704 (climatology 0.457, difference +0.2469 [+0.0758, +0.3996]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0728, ΔBrier vs climatology +0.0567 [+0.0392, +0.0754], realised minus predicted +0.0193 [-0.0050, +0.0436]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.562 | 0.1791 | 0.2720 | +0.0375 [+0.0110, +0.0642] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0384 | 0.0159 | +0.0179 [-0.0062, +0.0362] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0118, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0183 | 0.0200 | +0.0020 [-0.0051, +0.0078] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0845 | 0.1165 | +0.0244 [+0.0018, +0.0521] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0099 | 0.0048 | +0.0082 [+0.0058, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0119 | 0.0031 | +0.0266 [+0.0195, +0.0326] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1914 | 0.4146 | 0.0719 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.487 | 0.528 | 0.1768 | 0.2474 | +0.0324 [+0.0067, +0.0565] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.1060 | 0.1133 | +0.0339 [+0.0052, +0.0614] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.474 | 0.0419 | 0.0630 | +0.0129 [+0.0067, +0.0192] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3561 | 0.2903 | +0.0892 [+0.0187, +0.1595] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.1296 | 0.1461 | +0.0774 [+0.0464, +0.1139] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3840 | 0.2213 |

## risk_logistic+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.351, 0.708] | 0.231 | 2.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.625] | 0.231 | 2.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.388 (105 of 1873 days never flag) | 130 | 0.464 | 0.500 | 0.0523 | +0.0191 [+0.0123, +0.0264] | +0.0040 [-0.0014, +0.0097] | 0.801 | 0.427 | no |
| 2 | 0.875 (126 of 1872 days never flag) | 82 | 0.295 | 0.500 | 0.0557 | +0.0154 [+0.0098, +0.0216] | +0.0054 [+0.0004, +0.0108] | 0.800 | 0.271 | no |
| 3 | 0.421 (147 of 1871 days never flag) | 52 | 0.217 | 0.577 | 0.0551 | +0.0156 [+0.0100, +0.0211] | +0.0093 [+0.0042, +0.0146] | 0.779 | 0.205 | no |
| 4 | 0.786 (126 of 1870 days never flag) | 89 | 0.377 | 0.584 | 0.0544 | +0.0164 [+0.0113, +0.0217] | +0.0079 [+0.0035, +0.0127] | 0.805 | 0.355 | no |
| 5 | 0.334 (126 of 1869 days never flag) | 130 | 0.435 | 0.462 | 0.0548 | +0.0161 [+0.0109, +0.0217] | +0.0086 [+0.0041, +0.0134] | 0.804 | 0.394 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.708 (climatology 0.457, difference +0.2513 [+0.0892, +0.3945]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0722, ΔBrier vs climatology +0.0573 [+0.0396, +0.0772], realised minus predicted +0.0195 [-0.0043, +0.0462]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.541 | 0.1820 | 0.2720 | +0.0382 [+0.0132, +0.0653] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0359 | 0.0159 | +0.0193 [-0.0049, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0182 | 0.0200 | +0.0021 [-0.0046, +0.0081] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0821 | 0.1165 | +0.0236 [+0.0017, +0.0507] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0098 | 0.0048 | +0.0083 [+0.0059, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0102 | 0.0031 | +0.0271 [+0.0200, +0.0339] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1902 | 0.4146 | 0.0703 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.513 | 0.517 | 0.1779 | 0.2474 | +0.0329 [+0.0093, +0.0578] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1046 | 0.1133 | +0.0362 [+0.0093, +0.0647] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.455 | 0.0422 | 0.0630 | +0.0129 [+0.0066, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3546 | 0.2903 | +0.0906 [+0.0222, +0.1607] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1246 | 0.1461 | +0.0764 [+0.0442, +0.1149] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.682] | 0.192 | 1.73 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.205, 0.500] | 0.154 | 1.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 88 | 0.307 | 0.489 | 0.0604 | +0.0110 [+0.0057, +0.0161] | -0.0041 [-0.0124, +0.0041] | 0.641 | 0.281 | no |
| 2 | 0.402 (147 of 1872 days never flag) | 55 | 0.201 | 0.509 | 0.0664 | +0.0046 [-0.0020, +0.0105] | -0.0054 [-0.0136, +0.0019] | 0.579 | 0.186 | no |
| 3 | 0.296 (147 of 1871 days never flag) | 59 | 0.203 | 0.475 | 0.0664 | +0.0043 [-0.0024, +0.0103] | -0.0021 [-0.0093, +0.0048] | 0.579 | 0.185 | no |
| 4 | 0.0798 (147 of 1870 days never flag) | 68 | 0.203 | 0.412 | 0.0672 | +0.0037 [-0.0029, +0.0097] | -0.0048 [-0.0125, +0.0021] | 0.579 | 0.180 | no |
| 5 | 0.179 (126 of 1869 days never flag) | 67 | 0.203 | 0.418 | 0.0692 | +0.0017 [-0.0054, +0.0076] | -0.0058 [-0.0139, +0.0015] | 0.577 | 0.180 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.552 (climatology 0.457, difference +0.0948 [-0.0312, +0.2063]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1051, ΔBrier vs climatology +0.0243 [+0.0142, +0.0347], realised minus predicted +0.0748 [+0.0419, +0.1115]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.574 | 0.1103 | 0.2720 | -0.0019 [-0.0231, +0.0185] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0283 | 0.0159 | +0.0266 [+0.0120, +0.0388] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0058 | 0.0200 | +0.0050 [+0.0013, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0309 | 0.1165 | +0.0125 [+0.0011, +0.0275] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0030 | 0.0048 | +0.0092 [+0.0076, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0053 | 0.0031 | +0.0285 [+0.0219, +0.0350] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0348 | 0.4146 | +0.0030 [-0.0320, +0.0353] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1092 | 0.2474 | +0.0037 [-0.0157, +0.0218] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1008 | 0.1133 | +0.0305 [+0.0048, +0.0573] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0129 | 0.0630 | +0.0040 [-0.0010, +0.0089] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3546 | 0.2903 | +0.0906 [+0.0193, +0.1630] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1246 | 0.1461 | +0.0764 [+0.0437, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

## risk_logistic+settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.433, 0.808] | 0.192 | 1.88 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 16 | 0.615 [0.435, 0.800] | 0.192 | 1.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.105 (105 of 1873 days never flag) | 91 | 0.307 | 0.473 | 0.0606 | +0.0108 [+0.0052, +0.0157] | -0.0043 [-0.0131, +0.0033] | 0.642 | 0.279 | no |
| 2 | 0.0864 (126 of 1872 days never flag) | 89 | 0.324 | 0.506 | 0.0606 | +0.0105 [+0.0052, +0.0154] | +0.0005 [-0.0069, +0.0073] | 0.638 | 0.298 | no |
| 3 | 0.0922 (126 of 1871 days never flag) | 82 | 0.326 | 0.549 | 0.0597 | +0.0110 [+0.0058, +0.0161] | +0.0047 [-0.0017, +0.0108] | 0.637 | 0.305 | no |
| 4 | 0.112 (126 of 1870 days never flag) | 82 | 0.290 | 0.488 | 0.0603 | +0.0105 [+0.0059, +0.0154] | +0.0021 [-0.0045, +0.0086] | 0.632 | 0.266 | no |
| 5 | 0.0346 (126 of 1869 days never flag) | 91 | 0.304 | 0.462 | 0.0601 | +0.0108 [+0.0057, +0.0155] | +0.0033 [-0.0032, +0.0092] | 0.633 | 0.276 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 3.7 over 1035 days; regime_2021-23: 1.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.457, difference +0.2447 [+0.0757, +0.3924]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0852, ΔBrier vs climatology +0.0443 [+0.0318, +0.0581], realised minus predicted +0.0455 [+0.0171, +0.0761]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1074 | 0.2720 | -0.0026 [-0.0241, +0.0173] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0308 | 0.0159 | +0.0252 [+0.0090, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0121, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0059 | 0.0200 | +0.0050 [+0.0009, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0332 | 0.1165 | +0.0133 [+0.0013, +0.0280] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0069 | 0.0031 | +0.0280 [+0.0221, +0.0339] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0360 | 0.4146 | 0.0046 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.506 | 0.1081 | 0.2474 | +0.0032 [-0.0164, +0.0219] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1022 | 0.1133 | +0.0282 [+0.0001, +0.0539] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.455 | 0.0126 | 0.0630 | +0.0040 [-0.0016, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3561 | 0.2903 | +0.0892 [+0.0151, +0.1641] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1296 | 0.1461 | +0.0774 [+0.0474, +0.1148] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2020 | 0.2213 |

## risk_logistic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.760] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 14 | 0.538 [0.361, 0.714] | 0.192 | 1.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 88 | 0.307 | 0.489 | 0.0604 | +0.0110 [+0.0058, +0.0158] | -0.0041 [-0.0125, +0.0039] | 0.641 | 0.281 | no |
| 2 | 0.131 (126 of 1872 days never flag) | 86 | 0.331 | 0.535 | 0.0606 | +0.0105 [+0.0053, +0.0154] | +0.0005 [-0.0068, +0.0073] | 0.639 | 0.308 | no |
| 3 | 0.421 (147 of 1871 days never flag) | 72 | 0.297 | 0.569 | 0.0593 | +0.0114 [+0.0062, +0.0163] | +0.0051 [-0.0016, +0.0110] | 0.638 | 0.279 | no |
| 4 | 0.092 (126 of 1870 days never flag) | 82 | 0.297 | 0.500 | 0.0601 | +0.0107 [+0.0055, +0.0154] | +0.0022 [-0.0044, +0.0083] | 0.632 | 0.273 | no |
| 5 | 0.0786 (126 of 1869 days never flag) | 89 | 0.304 | 0.472 | 0.0602 | +0.0107 [+0.0058, +0.0156] | +0.0032 [-0.0032, +0.0094] | 0.633 | 0.277 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.708 (climatology 0.457, difference +0.2509 [+0.0893, +0.4002]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0846, ΔBrier vs climatology +0.0449 [+0.0325, +0.0588], realised minus predicted +0.0458 [+0.0174, +0.0765]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.574 | 0.1103 | 0.2720 | -0.0019 [-0.0231, +0.0187] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0283 | 0.0159 | +0.0266 [+0.0117, +0.0388] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0058 | 0.0200 | +0.0050 [+0.0011, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.588 | 0.0309 | 0.1165 | +0.0125 [+0.0008, +0.0272] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0030 | 0.0048 | +0.0092 [+0.0074, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0053 | 0.0031 | +0.0285 [+0.0222, +0.0350] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0348 | 0.4146 | 0.0030 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1092 | 0.2474 | +0.0037 [-0.0151, +0.0222] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1008 | 0.1133 | +0.0305 [+0.0038, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0129 | 0.0630 | +0.0040 [-0.0012, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3546 | 0.2903 | +0.0906 [+0.0189, +0.1627] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1246 | 0.1461 | +0.0764 [+0.0461, +0.1173] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.192 | 1.77 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.115 | 1.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (105 of 1873 days never flag) | 90 | 0.314 | 0.489 | 0.0596 | +0.0118 [+0.0070, +0.0164] | -0.0033 [-0.0115, +0.0041] | 0.643 | 0.288 | no |
| 2 | 0.33 (147 of 1872 days never flag) | 50 | 0.173 | 0.480 | 0.0672 | +0.0039 [-0.0026, +0.0099] | -0.0061 [-0.0146, +0.0009] | 0.579 | 0.158 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 49 | 0.167 | 0.469 | 0.0689 | +0.0018 [-0.0060, +0.0080] | -0.0045 [-0.0131, +0.0025] | 0.579 | 0.152 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0689 | +0.0019 [-0.0048, +0.0080] | -0.0065 [-0.0146, +0.0010] | 0.578 | 0.179 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 57 | 0.196 | 0.474 | 0.0687 | +0.0023 [-0.0045, +0.0084] | -0.0053 [-0.0131, +0.0019] | 0.577 | 0.178 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [-0.0214, +0.2463]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0239 [+0.0136, +0.0345], realised minus predicted +0.0775 [+0.0426, +0.1148]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1080 | 0.2720 | -0.0024 [-0.0224, +0.0166] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.0294 | 0.0159 | +0.0298 [+0.0202, +0.0383] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0311 | 0.1165 | +0.0168 [+0.0040, +0.0338] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0092 | 0.0031 | +0.0279 [+0.0218, +0.0337] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0421 | 0.4146 | 0.0149 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1063 | 0.2474 | +0.0057 [-0.0113, +0.0230] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.0996 | 0.1133 | +0.0352 [+0.0096, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.471 | 0.0123 | 0.0630 | +0.0047 [-0.0004, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1520] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1332 | 0.1461 | +0.0711 [+0.0381, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2040 | 0.2213 |

## risk_logistic_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.714] | 0.231 | 2.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 94 | 0.350 | 0.521 | 0.0516 | +0.0199 [+0.0132, +0.0270] | +0.0048 [+0.0004, +0.0093] | 0.804 | 0.324 | no |
| 2 | 0.381 (147 of 1872 days never flag) | 73 | 0.266 | 0.507 | 0.0609 | +0.0102 [+0.0048, +0.0160] | +0.0002 [-0.0045, +0.0051] | 0.752 | 0.245 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 80 | 0.275 | 0.475 | 0.0628 | +0.0079 [+0.0013, +0.0142] | +0.0015 [-0.0045, +0.0075] | 0.748 | 0.251 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0623 | +0.0085 [+0.0026, +0.0144] | +0.0000 [-0.0054, +0.0056] | 0.758 | 0.217 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 138 | 0.457 | 0.457 | 0.0627 | +0.0083 [+0.0027, +0.0136] | +0.0007 [-0.0038, +0.0055] | 0.744 | 0.413 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.457, difference +0.1421 [+0.0012, +0.2594]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0406 [+0.0256, +0.0566], realised minus predicted +0.0472 [+0.0192, +0.0765]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.581 | 0.1797 | 0.2720 | +0.0377 [+0.0125, +0.0659] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0370 | 0.0159 | +0.0225 [+0.0051, +0.0368] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0151 | 0.0200 | +0.0010 [-0.0058, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0823 | 0.1165 | +0.0279 [+0.0032, +0.0559] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0082 | 0.0048 | +0.0084 [+0.0062, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0142 | 0.0031 | +0.0265 [+0.0196, +0.0327] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.1975 | 0.4146 | +0.0822 [-0.0034, +0.1683] |
| scarcity_state | 3 | 473 | 117 | 0.376 | 0.543 | 0.1750 | 0.2474 | +0.0349 [+0.0125, +0.0594] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1034 | 0.1133 | +0.0409 [+0.0150, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.424 | 0.0416 | 0.0630 | +0.0136 [+0.0073, +0.0205] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0427, +0.1489] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1332 | 0.1461 | +0.0711 [+0.0394, +0.1092] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3860 | 0.2213 |

## risk_logistic_base+every_day+gate+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.375, 0.714] | 0.231 | 2.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.600] | 0.231 | 2.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.331 (84 of 1873 days never flag) | 118 | 0.443 | 0.525 | 0.0511 | +0.0203 [+0.0140, +0.0272] | +0.0052 [+0.0005, +0.0102] | 0.804 | 0.411 | no |
| 2 | 0.361 (147 of 1872 days never flag) | 66 | 0.252 | 0.530 | 0.0600 | +0.0110 [+0.0059, +0.0169] | +0.0010 [-0.0037, +0.0058] | 0.753 | 0.234 | no |
| 3 | 0.348 (147 of 1871 days never flag) | 81 | 0.283 | 0.481 | 0.0604 | +0.0102 [+0.0041, +0.0162] | +0.0039 [-0.0013, +0.0092] | 0.749 | 0.258 | no |
| 4 | 0.333 (147 of 1870 days never flag) | 76 | 0.246 | 0.447 | 0.0610 | +0.0098 [+0.0044, +0.0154] | +0.0014 [-0.0032, +0.0060] | 0.759 | 0.222 | no |
| 5 | 0.499 (147 of 1869 days never flag) | 133 | 0.457 | 0.474 | 0.0632 | +0.0077 [+0.0020, +0.0130] | +0.0002 [-0.0052, +0.0050] | 0.744 | 0.416 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.568 (climatology 0.457, difference +0.1111 [-0.0083, +0.2211]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0866, ΔBrier vs climatology +0.0428 [+0.0288, +0.0585], realised minus predicted +0.0483 [+0.0208, +0.0787]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.575 | 0.1825 | 0.2720 | +0.0394 [+0.0149, +0.0660] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0331 | 0.0159 | +0.0238 [+0.0062, +0.0379] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0151 | 0.0200 | +0.0011 [-0.0057, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0805 | 0.1165 | +0.0273 [+0.0042, +0.0562] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0081 | 0.0048 | +0.0084 [+0.0062, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0120 | 0.0031 | +0.0268 [+0.0196, +0.0328] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.1958 | 0.4146 | 0.0790 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.487 | 0.543 | 0.1760 | 0.2474 | +0.0367 [+0.0146, +0.0600] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1014 | 0.1133 | +0.0435 [+0.0169, +0.0727] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.468 | 0.0419 | 0.0630 | +0.0137 [+0.0076, +0.0207] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3205 | 0.2903 | +0.0964 [+0.0455, +0.1428] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0401, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3919 | 0.2213 |

## risk_logistic_base+every_day+gate+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.715] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.360, 0.722] | 0.231 | 2.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 94 | 0.350 | 0.521 | 0.0516 | +0.0199 [+0.0134, +0.0270] | +0.0048 [+0.0001, +0.0095] | 0.804 | 0.324 | no |
| 2 | 0.394 (126 of 1872 days never flag) | 84 | 0.281 | 0.464 | 0.0546 | +0.0165 [+0.0111, +0.0219] | +0.0065 [+0.0018, +0.0119] | 0.801 | 0.255 | no |
| 3 | 0.443 (126 of 1871 days never flag) | 92 | 0.362 | 0.543 | 0.0561 | +0.0146 [+0.0095, +0.0202] | +0.0083 [+0.0036, +0.0135] | 0.778 | 0.338 | no |
| 4 | 0.53 (126 of 1870 days never flag) | 118 | 0.449 | 0.525 | 0.0554 | +0.0155 [+0.0108, +0.0207] | +0.0070 [+0.0029, +0.0119] | 0.805 | 0.417 | no |
| 5 | 0.334 (126 of 1869 days never flag) | 128 | 0.449 | 0.484 | 0.0561 | +0.0148 [+0.0097, +0.0198] | +0.0073 [+0.0031, +0.0116] | 0.802 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.457, difference +0.2344 [+0.1116, +0.3581]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0744, ΔBrier vs climatology +0.0550 [+0.0367, +0.0748], realised minus predicted +0.0166 [-0.0082, +0.0438]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.581 | 0.1797 | 0.2720 | +0.0377 [+0.0132, +0.0635] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0370 | 0.0159 | +0.0225 [+0.0051, +0.0370] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0151 | 0.0200 | +0.0010 [-0.0062, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0823 | 0.1165 | +0.0279 [+0.0040, +0.0555] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0082 | 0.0048 | +0.0084 [+0.0062, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0142 | 0.0031 | +0.0265 [+0.0193, +0.0329] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.1975 | 0.4146 | 0.0822 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.376 | 0.543 | 0.1750 | 0.2474 | +0.0349 [+0.0119, +0.0589] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1034 | 0.1133 | +0.0409 [+0.0155, +0.0696] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.424 | 0.0416 | 0.0630 | +0.0136 [+0.0073, +0.0204] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3198 | 0.2903 | +0.0954 [+0.0386, +0.1490] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1332 | 0.1461 | +0.0711 [+0.0384, +0.1050] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3860 | 0.2213 |

## risk_logistic_base+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.714] | 0.192 | 2.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.192 | 2.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.331 (84 of 1873 days never flag) | 118 | 0.443 | 0.525 | 0.0511 | +0.0203 [+0.0136, +0.0273] | +0.0052 [+0.0006, +0.0104] | 0.804 | 0.411 | no |
| 2 | 0.386 (126 of 1872 days never flag) | 108 | 0.367 | 0.472 | 0.0542 | +0.0169 [+0.0113, +0.0231] | +0.0069 [+0.0020, +0.0124] | 0.802 | 0.334 | no |
| 3 | 0.446 (126 of 1871 days never flag) | 60 | 0.217 | 0.500 | 0.0555 | +0.0152 [+0.0099, +0.0204] | +0.0089 [+0.0042, +0.0138] | 0.778 | 0.200 | no |
| 4 | 0.492 (126 of 1870 days never flag) | 110 | 0.420 | 0.527 | 0.0552 | +0.0156 [+0.0107, +0.0207] | +0.0072 [+0.0028, +0.0120] | 0.805 | 0.390 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 115 | 0.413 | 0.496 | 0.0562 | +0.0147 [+0.0096, +0.0200] | +0.0072 [+0.0029, +0.0121] | 0.802 | 0.380 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.457, difference +0.2350 [+0.1088, +0.3609]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0735, ΔBrier vs climatology +0.0560 [+0.0382, +0.0746], realised minus predicted +0.0170 [-0.0075, +0.0428]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.575 | 0.1825 | 0.2720 | +0.0394 [+0.0143, +0.0681] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0331 | 0.0159 | +0.0238 [+0.0063, +0.0380] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0151 | 0.0200 | +0.0011 [-0.0060, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.500 | 0.0805 | 0.1165 | +0.0273 [+0.0044, +0.0556] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0081 | 0.0048 | +0.0084 [+0.0062, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0120 | 0.0031 | +0.0268 [+0.0198, +0.0332] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.1958 | 0.4146 | 0.0790 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.487 | 0.543 | 0.1760 | 0.2474 | +0.0367 [+0.0133, +0.0617] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1014 | 0.1133 | +0.0435 [+0.0162, +0.0734] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.468 | 0.0419 | 0.0630 | +0.0137 [+0.0074, +0.0205] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.700 | 0.3205 | 0.2903 | +0.0964 [+0.0448, +0.1452] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.1254 | 0.1461 | +0.0736 [+0.0406, +0.1103] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3919 | 0.2213 |

## risk_logistic_base+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.680] | 0.154 | 1.69 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.200, 0.500] | 0.154 | 1.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.134 (84 of 1873 days never flag) | 89 | 0.321 | 0.506 | 0.0592 | +0.0122 [+0.0074, +0.0168] | -0.0029 [-0.0111, +0.0043] | 0.643 | 0.296 | no |
| 2 | 0.361 (147 of 1872 days never flag) | 47 | 0.173 | 0.511 | 0.0663 | +0.0047 [-0.0015, +0.0107] | -0.0053 [-0.0131, +0.0021] | 0.579 | 0.159 | no |
| 3 | 0.348 (147 of 1871 days never flag) | 50 | 0.167 | 0.460 | 0.0665 | +0.0042 [-0.0029, +0.0100] | -0.0022 [-0.0103, +0.0044] | 0.580 | 0.151 | no |
| 4 | 0.333 (147 of 1870 days never flag) | 51 | 0.167 | 0.451 | 0.0676 | +0.0032 [-0.0037, +0.0092] | -0.0052 [-0.0133, +0.0014] | 0.579 | 0.151 | no |
| 5 | 0.499 (126 of 1869 days never flag) | 66 | 0.210 | 0.439 | 0.0692 | +0.0017 [-0.0050, +0.0080] | -0.0058 [-0.0140, +0.0014] | 0.578 | 0.189 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.552 (climatology 0.457, difference +0.0945 [-0.0323, +0.2088]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1033, ΔBrier vs climatology +0.0262 [+0.0162, +0.0367], realised minus predicted +0.0786 [+0.0456, +0.1162]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.561 | 0.1108 | 0.2720 | -0.0007 [-0.0211, +0.0184] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0255 | 0.0159 | +0.0310 [+0.0217, +0.0397] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0293 | 0.1165 | +0.0162 [+0.0044, +0.0316] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0013 | 0.0048 | +0.0094 [+0.0078, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0071 | 0.0031 | +0.0282 [+0.0220, +0.0341] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0404 | 0.4146 | 0.0117 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.533 | 0.1073 | 0.2474 | +0.0075 [-0.0108, +0.0244] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.0976 | 0.1133 | +0.0378 [+0.0116, +0.0655] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.485 | 0.0127 | 0.0630 | +0.0048 [-0.0001, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.500 | 0.3205 | 0.2903 | +0.0964 [+0.0467, +0.1441] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1254 | 0.1461 | +0.0736 [+0.0411, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2099 | 0.2213 |

## risk_logistic_base+settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.677] | 0.192 | 1.77 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.154 | 1.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (105 of 1873 days never flag) | 90 | 0.314 | 0.489 | 0.0596 | +0.0118 [+0.0068, +0.0161] | -0.0033 [-0.0115, +0.0039] | 0.643 | 0.288 | no |
| 2 | 0.394 (126 of 1872 days never flag) | 75 | 0.281 | 0.520 | 0.0594 | +0.0116 [+0.0066, +0.0164] | +0.0016 [-0.0056, +0.0089] | 0.640 | 0.260 | no |
| 3 | 0.222 (126 of 1871 days never flag) | 82 | 0.297 | 0.500 | 0.0603 | +0.0104 [+0.0055, +0.0153] | +0.0041 [-0.0023, +0.0104] | 0.637 | 0.273 | no |
| 4 | 0.215 (126 of 1870 days never flag) | 84 | 0.290 | 0.476 | 0.0611 | +0.0098 [+0.0048, +0.0144] | +0.0013 [-0.0051, +0.0075] | 0.633 | 0.264 | no |
| 5 | 0.41 (126 of 1869 days never flag) | 80 | 0.290 | 0.500 | 0.0615 | +0.0094 [+0.0045, +0.0140] | +0.0019 [-0.0047, +0.0078] | 0.633 | 0.267 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.689 (climatology 0.457, difference +0.2322 [+0.1035, +0.3644]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0427 [+0.0299, +0.0563], realised minus predicted +0.0436 [+0.0154, +0.0745]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1080 | 0.2720 | -0.0024 [-0.0227, +0.0164] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.0294 | 0.0159 | +0.0298 [+0.0200, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0311 | 0.1165 | +0.0168 [+0.0042, +0.0327] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0092 | 0.0031 | +0.0279 [+0.0220, +0.0336] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0421 | 0.4146 | +0.0149 [-0.0146, +0.0505] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1063 | 0.2474 | +0.0057 [-0.0121, +0.0225] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.0996 | 0.1133 | +0.0352 [+0.0107, +0.0625] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.471 | 0.0123 | 0.0630 | +0.0047 [-0.0004, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0370, +0.1535] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1332 | 0.1461 | +0.0711 [+0.0391, +0.1102] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2040 | 0.2213 |

## risk_logistic_base+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.684] | 0.154 | 1.69 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 13 | 0.500 [0.322, 0.680] | 0.154 | 1.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.134 (84 of 1873 days never flag) | 89 | 0.321 | 0.506 | 0.0592 | +0.0122 [+0.0071, +0.0170] | -0.0029 [-0.0110, +0.0041] | 0.643 | 0.296 | no |
| 2 | 0.135 (126 of 1872 days never flag) | 84 | 0.317 | 0.524 | 0.0591 | +0.0120 [+0.0068, +0.0169] | +0.0020 [-0.0048, +0.0086] | 0.640 | 0.293 | no |
| 3 | 0.446 (126 of 1871 days never flag) | 84 | 0.297 | 0.488 | 0.0597 | +0.0110 [+0.0057, +0.0156] | +0.0047 [-0.0018, +0.0106] | 0.638 | 0.272 | no |
| 4 | 0.324 (126 of 1870 days never flag) | 75 | 0.268 | 0.493 | 0.0609 | +0.0099 [+0.0046, +0.0145] | +0.0015 [-0.0052, +0.0076] | 0.633 | 0.246 | no |
| 5 | 0.161 (147 of 1869 days never flag) | 71 | 0.254 | 0.493 | 0.0616 | +0.0093 [+0.0043, +0.0138] | +0.0018 [-0.0049, +0.0077] | 0.633 | 0.233 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.457, difference +0.2340 [+0.1076, +0.3619]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0859, ΔBrier vs climatology +0.0436 [+0.0303, +0.0588], realised minus predicted +0.0440 [+0.0139, +0.0747]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.561 | 0.1108 | 0.2720 | -0.0007 [-0.0216, +0.0182] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0255 | 0.0159 | +0.0310 [+0.0218, +0.0401] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0293 | 0.1165 | +0.0162 [+0.0036, +0.0324] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0013 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0071 | 0.0031 | +0.0282 [+0.0219, +0.0344] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0404 | 0.4146 | +0.0117 [-0.0223, +0.0433] |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.533 | 0.1073 | 0.2474 | +0.0075 [-0.0111, +0.0245] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.0976 | 0.1133 | +0.0378 [+0.0124, +0.0646] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.485 | 0.0127 | 0.0630 | +0.0048 [-0.0004, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.500 | 0.3205 | 0.2903 | +0.0964 [+0.0455, +0.1424] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1254 | 0.1461 | +0.0736 [+0.0422, +0.1116] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2099 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.192 | 1.88 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.542] | 0.154 | 1.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 93 | 0.314 | 0.473 | 0.0630 | +0.0084 [+0.0021, +0.0147] | -0.0067 [-0.0153, +0.0016] | 0.635 | 0.286 | no |
| 2 | 0.431 (147 of 1872 days never flag) | 73 | 0.216 | 0.411 | 0.0687 | +0.0024 [-0.0054, +0.0093] | -0.0076 [-0.0168, -0.0001] | 0.582 | 0.191 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 69 | 0.217 | 0.435 | 0.0670 | +0.0037 [-0.0037, +0.0105] | -0.0026 [-0.0108, +0.0047] | 0.585 | 0.195 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0669 | +0.0039 [-0.0034, +0.0110] | -0.0045 [-0.0128, +0.0033] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 53 | 0.188 | 0.491 | 0.0670 | +0.0039 [-0.0030, +0.0107] | -0.0036 [-0.0120, +0.0040] | 0.585 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.457, difference +0.1367 [-0.0372, +0.2817]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1051, ΔBrier vs climatology +0.0244 [+0.0124, +0.0374], realised minus predicted +0.0555 [+0.0217, +0.0899]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1199 | 0.2720 | -0.0169 [-0.0413, +0.0085] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.0469 | 0.0159 | +0.0220 [+0.0121, +0.0313] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0048, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0509 | 0.1165 | +0.0242 [+0.0051, +0.0465] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0271 | 0.0031 | +0.0196 [+0.0120, +0.0263] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0959 | 0.4146 | 0.0536 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.1179 | 0.2474 | -0.0036 [-0.0259, +0.0196] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1397 | 0.1133 | +0.0244 [-0.0130, +0.0627] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.471 | 0.0159 | 0.0630 | +0.0028 [-0.0028, +0.0082] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3234 | 0.2903 | +0.0724 [-0.0002, +0.1368] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1034] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.741] | 0.231 | 3.15 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.231 | 3.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 119 | 0.421 | 0.496 | 0.0549 | +0.0165 [+0.0089, +0.0248] | +0.0014 [-0.0045, +0.0074] | 0.793 | 0.387 | no |
| 2 | 0.431 (189 of 1872 days never flag) | 63 | 0.223 | 0.492 | 0.0624 | +0.0087 [+0.0021, +0.0154] | -0.0013 [-0.0065, +0.0039] | 0.753 | 0.205 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 92 | 0.319 | 0.478 | 0.0609 | +0.0098 [+0.0034, +0.0159] | +0.0035 [-0.0022, +0.0089] | 0.755 | 0.291 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 110 | 0.391 | 0.491 | 0.0603 | +0.0105 [+0.0042, +0.0168] | +0.0021 [-0.0032, +0.0074] | 0.767 | 0.359 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 152 | 0.507 | 0.461 | 0.0610 | +0.0099 [+0.0038, +0.0166] | +0.0024 [-0.0032, +0.0079] | 0.754 | 0.460 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.611 (climatology 0.457, difference +0.1539 [-0.0041, +0.3022]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0888, ΔBrier vs climatology +0.0407 [+0.0240, +0.0588], realised minus predicted +0.0265 [-0.0007, +0.0545]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.529 | 0.1916 | 0.2720 | +0.0232 [-0.0055, +0.0539] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0545 | 0.0159 | +0.0147 [-0.0015, +0.0294] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0067 | 0.0000 | +0.0134 [+0.0115, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0243 | 0.0200 | -0.0014 [-0.0092, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1021 | 0.1165 | +0.0353 [+0.0043, +0.0720] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0126 | 0.0048 | +0.0076 [+0.0051, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0321 | 0.0031 | +0.0182 [+0.0098, +0.0252] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2513 | 0.4146 | +0.1209 [-0.0095, +0.2456] |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.525 | 0.1866 | 0.2474 | +0.0256 [+0.0006, +0.0513] |
| day_type | month_end | 150 | 17 | 0.706 | 0.667 | 0.1435 | 0.1133 | +0.0301 [-0.0079, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.434 | 0.0451 | 0.0630 | +0.0117 [+0.0052, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0022, +0.1388] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2039 | 0.1461 | +0.0602 [+0.0201, +0.1035] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.679] | 0.231 | 3.19 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.632] | 0.231 | 3.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (63 of 1873 days never flag) | 112 | 0.393 | 0.491 | 0.0538 | +0.0177 [+0.0107, +0.0246] | +0.0026 [-0.0026, +0.0078] | 0.799 | 0.360 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 87 | 0.281 | 0.448 | 0.0611 | +0.0100 [+0.0039, +0.0167] | -0.0000 [-0.0056, +0.0059] | 0.758 | 0.253 | no |
| 3 | 0.49 (126 of 1871 days never flag) | 84 | 0.283 | 0.464 | 0.0607 | +0.0099 [+0.0029, +0.0171] | +0.0036 [-0.0028, +0.0101] | 0.753 | 0.257 | no |
| 4 | 0.463 (126 of 1870 days never flag) | 95 | 0.333 | 0.484 | 0.0624 | +0.0085 [+0.0022, +0.0146] | +0.0000 [-0.0051, +0.0052] | 0.760 | 0.305 | no |
| 5 | 0.458 (126 of 1869 days never flag) | 148 | 0.471 | 0.439 | 0.0638 | +0.0072 [+0.0009, +0.0139] | -0.0004 [-0.0060, +0.0054] | 0.752 | 0.423 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.602 (climatology 0.457, difference +0.1452 [+0.0218, +0.2506]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0907, ΔBrier vs climatology +0.0388 [+0.0226, +0.0572], realised minus predicted +0.0244 [-0.0022, +0.0514]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.402 | 0.532 | 0.1794 | 0.2720 | +0.0264 [+0.0015, +0.0524] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0474 | 0.0159 | +0.0195 [+0.0031, +0.0341] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0065 | 0.0000 | +0.0134 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0238 | 0.0200 | -0.0012 [-0.0088, +0.0044] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1022 | 0.1165 | +0.0343 [+0.0036, +0.0720] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0123 | 0.0048 | +0.0077 [+0.0054, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0277 | 0.0031 | +0.0204 [+0.0122, +0.0277] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2517 | 0.4146 | 0.1211 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.410 | 0.516 | 0.1762 | 0.2474 | +0.0286 [+0.0062, +0.0519] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1303 | 0.1133 | +0.0283 [-0.0071, +0.0642] |
| day_type | ordinary | 1603 | 101 | 0.307 | 0.437 | 0.0429 | 0.0630 | +0.0124 [+0.0063, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2995 | 0.2903 | +0.1011 [+0.0271, +0.1653] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.500 | 0.2003 | 0.1461 | +0.0655 [+0.0221, +0.1113] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.300, 0.632] | 0.192 | 2.31 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.192 | 1.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.481 (105 of 1873 days never flag) | 119 | 0.421 | 0.496 | 0.0549 | +0.0165 [+0.0086, +0.0247] | +0.0014 [-0.0046, +0.0071] | 0.793 | 0.387 | no |
| 2 | 0.608 (126 of 1872 days never flag) | 113 | 0.410 | 0.504 | 0.0551 | +0.0160 [+0.0096, +0.0229] | +0.0060 [+0.0000, +0.0126] | 0.794 | 0.378 | no |
| 3 | 0.462 (126 of 1871 days never flag) | 91 | 0.312 | 0.473 | 0.0579 | +0.0128 [+0.0057, +0.0203] | +0.0064 [-0.0004, +0.0140] | 0.781 | 0.284 | no |
| 4 | 0.472 (126 of 1870 days never flag) | 103 | 0.377 | 0.505 | 0.0549 | +0.0160 [+0.0099, +0.0228] | +0.0075 [+0.0013, +0.0139] | 0.809 | 0.347 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 73 | 0.290 | 0.548 | 0.0591 | +0.0118 [+0.0039, +0.0192] | +0.0043 [-0.0029, +0.0110] | 0.808 | 0.271 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.642 (climatology 0.457, difference +0.1852 [-0.0280, +0.3932]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0836, ΔBrier vs climatology +0.0458 [+0.0249, +0.0685], realised minus predicted -0.0070 [-0.0324, +0.0182]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.529 | 0.1916 | 0.2720 | +0.0232 [-0.0063, +0.0532] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0545 | 0.0159 | +0.0147 [-0.0019, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0067 | 0.0000 | +0.0134 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0243 | 0.0200 | -0.0014 [-0.0089, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1021 | 0.1165 | +0.0353 [+0.0049, +0.0760] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0126 | 0.0048 | +0.0076 [+0.0052, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0321 | 0.0031 | +0.0182 [+0.0096, +0.0252] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2513 | 0.4146 | 0.1209 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.525 | 0.1866 | 0.2474 | +0.0256 [-0.0004, +0.0516] |
| day_type | month_end | 150 | 17 | 0.706 | 0.667 | 0.1435 | 0.1133 | +0.0301 [-0.0110, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.434 | 0.0451 | 0.0630 | +0.0117 [+0.0051, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3234 | 0.2903 | +0.0724 [+0.0024, +0.1380] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2039 | 0.1461 | +0.0602 [+0.0194, +0.1031] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.405, 0.743] | 0.231 | 2.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.393, 0.750] | 0.231 | 2.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (63 of 1873 days never flag) | 112 | 0.393 | 0.491 | 0.0538 | +0.0177 [+0.0104, +0.0257] | +0.0026 [-0.0025, +0.0077] | 0.799 | 0.360 | no |
| 2 | 0.399 (126 of 1872 days never flag) | 121 | 0.432 | 0.496 | 0.0549 | +0.0162 [+0.0100, +0.0228] | +0.0062 [+0.0005, +0.0125] | 0.800 | 0.396 | no |
| 3 | 0.38 (126 of 1871 days never flag) | 130 | 0.471 | 0.500 | 0.0581 | +0.0125 [+0.0053, +0.0198] | +0.0062 [-0.0011, +0.0133] | 0.779 | 0.434 | no |
| 4 | 0.67 (126 of 1870 days never flag) | 134 | 0.464 | 0.478 | 0.0544 | +0.0164 [+0.0102, +0.0228] | +0.0080 [+0.0023, +0.0141] | 0.807 | 0.423 | no |
| 5 | 0.494 (126 of 1869 days never flag) | 123 | 0.464 | 0.520 | 0.0573 | +0.0136 [+0.0069, +0.0200] | +0.0061 [-0.0003, +0.0120] | 0.805 | 0.430 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.457, difference +0.2206 [+0.0574, +0.3919]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0258, +0.0678], realised minus predicted -0.0017 [-0.0258, +0.0235]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.402 | 0.532 | 0.1794 | 0.2720 | +0.0264 [-0.0007, +0.0546] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0474 | 0.0159 | +0.0195 [+0.0030, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0065 | 0.0000 | +0.0134 [+0.0116, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0238 | 0.0200 | -0.0012 [-0.0083, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1022 | 0.1165 | +0.0343 [+0.0031, +0.0744] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0123 | 0.0048 | +0.0077 [+0.0053, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0277 | 0.0031 | +0.0204 [+0.0119, +0.0278] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2517 | 0.4146 | 0.1211 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.410 | 0.516 | 0.1762 | 0.2474 | +0.0286 [+0.0050, +0.0525] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1303 | 0.1133 | +0.0283 [-0.0077, +0.0667] |
| day_type | ordinary | 1603 | 101 | 0.307 | 0.437 | 0.0429 | 0.0630 | +0.0124 [+0.0061, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2995 | 0.2903 | +0.1011 [+0.0326, +0.1630] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.500 | 0.2003 | 0.1461 | +0.0655 [+0.0219, +0.1132] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.731] | 0.192 | 2.27 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.58 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.231 (63 of 1873 days never flag) | 104 | 0.321 | 0.433 | 0.0618 | +0.0096 [+0.0036, +0.0154] | -0.0055 [-0.0142, +0.0021] | 0.642 | 0.287 | no |
| 2 | 0.331 (126 of 1872 days never flag) | 65 | 0.209 | 0.446 | 0.0674 | +0.0037 [-0.0034, +0.0104] | -0.0063 [-0.0145, +0.0014] | 0.586 | 0.188 | no |
| 3 | 0.166 (126 of 1871 days never flag) | 70 | 0.217 | 0.429 | 0.0668 | +0.0039 [-0.0042, +0.0108] | -0.0025 [-0.0111, +0.0057] | 0.585 | 0.194 | no |
| 4 | 0.463 (126 of 1870 days never flag) | 68 | 0.196 | 0.397 | 0.0689 | +0.0019 [-0.0057, +0.0080] | -0.0066 [-0.0150, +0.0005] | 0.581 | 0.172 | no |
| 5 | 0.458 (126 of 1869 days never flag) | 61 | 0.188 | 0.426 | 0.0698 | +0.0011 [-0.0069, +0.0085] | -0.0064 [-0.0152, +0.0020] | 0.583 | 0.168 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.587 (climatology 0.457, difference +0.1302 [-0.0040, +0.2610]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1070, ΔBrier vs climatology +0.0225 [+0.0105, +0.0347], realised minus predicted +0.0534 [+0.0205, +0.0880]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.544 | 0.1077 | 0.2720 | -0.0137 [-0.0364, +0.0083] |
| regime | 2020 | 251 | 4 | 0.250 | 0.036 | 0.0398 | 0.0159 | +0.0267 [+0.0159, +0.0374] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0114 | 0.0200 | +0.0018 [-0.0046, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.706 | 0.0510 | 0.1165 | +0.0232 [+0.0042, +0.0467] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0056 | 0.0048 | +0.0087 [+0.0067, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0227 | 0.0031 | +0.0218 [+0.0138, +0.0288] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.0964 | 0.4146 | 0.0537 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1075 | 0.2474 | -0.0006 [-0.0207, +0.0197] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1265 | 0.1133 | +0.0226 [-0.0136, +0.0575] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.447 | 0.0136 | 0.0630 | +0.0035 [-0.0021, +0.0085] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.2995 | 0.2903 | +0.1011 [+0.0304, +0.1646] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2003 | 0.1461 | +0.0655 [+0.0210, +0.1146] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.667] | 0.192 | 1.88 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 13 | 0.500 [0.321, 0.680] | 0.154 | 1.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.274 (105 of 1873 days never flag) | 93 | 0.314 | 0.473 | 0.0630 | +0.0084 [+0.0022, +0.0144] | -0.0067 [-0.0158, +0.0012] | 0.635 | 0.286 | no |
| 2 | 0.304 (126 of 1872 days never flag) | 73 | 0.295 | 0.562 | 0.0599 | +0.0111 [+0.0051, +0.0171] | +0.0011 [-0.0067, +0.0084] | 0.634 | 0.276 | no |
| 3 | 0.38 (126 of 1871 days never flag) | 87 | 0.326 | 0.517 | 0.0621 | +0.0086 [+0.0023, +0.0154] | +0.0023 [-0.0053, +0.0100] | 0.642 | 0.302 | no |
| 4 | 0.367 (126 of 1870 days never flag) | 74 | 0.290 | 0.541 | 0.0606 | +0.0102 [+0.0042, +0.0164] | +0.0018 [-0.0055, +0.0091] | 0.636 | 0.270 | no |
| 5 | 0.355 (126 of 1869 days never flag) | 77 | 0.297 | 0.532 | 0.0645 | +0.0064 [-0.0011, +0.0133] | -0.0011 [-0.0096, +0.0070] | 0.637 | 0.276 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.640 (climatology 0.457, difference +0.1830 [-0.0223, +0.3753]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0962, ΔBrier vs climatology +0.0332 [+0.0158, +0.0515], realised minus predicted +0.0191 [-0.0108, +0.0517]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1199 | 0.2720 | -0.0169 [-0.0425, +0.0072] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.0469 | 0.0159 | +0.0220 [+0.0121, +0.0308] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0045, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0509 | 0.1165 | +0.0242 [+0.0057, +0.0472] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0271 | 0.0031 | +0.0196 [+0.0114, +0.0261] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0959 | 0.4146 | 0.0536 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.1179 | 0.2474 | -0.0036 [-0.0261, +0.0181] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1397 | 0.1133 | +0.0244 [-0.0140, +0.0641] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.471 | 0.0159 | 0.0630 | +0.0028 [-0.0029, +0.0080] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3234 | 0.2903 | +0.0724 [+0.0018, +0.1392] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2039 | 0.1461 | +0.0602 [+0.0202, +0.1010] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.393, 0.750] | 0.192 | 2.27 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 14 | 0.538 [0.361, 0.715] | 0.192 | 1.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.231 (63 of 1873 days never flag) | 104 | 0.321 | 0.433 | 0.0618 | +0.0096 [+0.0036, +0.0151] | -0.0055 [-0.0141, +0.0021] | 0.642 | 0.287 | no |
| 2 | 0.253 (126 of 1872 days never flag) | 77 | 0.302 | 0.545 | 0.0597 | +0.0113 [+0.0052, +0.0172] | +0.0013 [-0.0064, +0.0088] | 0.640 | 0.282 | no |
| 3 | 0.38 (126 of 1871 days never flag) | 93 | 0.319 | 0.473 | 0.0623 | +0.0084 [+0.0014, +0.0152] | +0.0020 [-0.0062, +0.0100] | 0.641 | 0.291 | no |
| 4 | 0.295 (126 of 1870 days never flag) | 92 | 0.312 | 0.467 | 0.0601 | +0.0107 [+0.0049, +0.0163] | +0.0023 [-0.0050, +0.0091] | 0.635 | 0.283 | no |
| 5 | 0.494 (126 of 1869 days never flag) | 81 | 0.297 | 0.506 | 0.0627 | +0.0082 [+0.0022, +0.0144] | +0.0007 [-0.0067, +0.0078] | 0.634 | 0.274 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.457, difference +0.2212 [+0.0566, +0.3954]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0187, +0.0500], realised minus predicted +0.0244 [-0.0049, +0.0534]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.544 | 0.1077 | 0.2720 | -0.0137 [-0.0364, +0.0081] |
| regime | 2020 | 251 | 4 | 0.250 | 0.036 | 0.0398 | 0.0159 | +0.0267 [+0.0162, +0.0369] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0114 | 0.0200 | +0.0018 [-0.0044, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.706 | 0.0510 | 0.1165 | +0.0232 [+0.0038, +0.0453] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0056 | 0.0048 | +0.0087 [+0.0068, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0227 | 0.0031 | +0.0218 [+0.0140, +0.0286] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.0964 | 0.4146 | +0.0537 [-0.0225, +0.1205] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.527 | 0.1075 | 0.2474 | -0.0006 [-0.0217, +0.0190] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1265 | 0.1133 | +0.0226 [-0.0118, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.447 | 0.0136 | 0.0630 | +0.0035 [-0.0020, +0.0084] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.2995 | 0.2903 | +0.1011 [+0.0256, +0.1610] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2003 | 0.1461 | +0.0655 [+0.0214, +0.1136] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4014 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

