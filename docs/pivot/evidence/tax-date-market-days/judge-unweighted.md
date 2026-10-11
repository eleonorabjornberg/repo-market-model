# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `2ae089a08621…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

## calendar_climatology (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.212, 0.576] | 0.269 | 5.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.286 (105 of 1873 days never flag) | 198 | 0.514 | 0.364 | 0.0714 | +0.0000 [+0.0000, +0.0000] | -0.0151 [-0.0211, -0.0097] | 0.585 | 0.442 | no |
| 2 | 0.286 (147 of 1872 days never flag) | 196 | 0.496 | 0.352 | 0.0711 | +0.0000 [+0.0000, +0.0000] | -0.0100 [-0.0146, -0.0054] | 0.586 | 0.423 | no |
| 3 | 0.286 (147 of 1871 days never flag) | 196 | 0.493 | 0.347 | 0.0707 | +0.0000 [+0.0000, +0.0000] | -0.0063 [-0.0099, -0.0028] | 0.585 | 0.419 | no |
| 4 | 0.286 (147 of 1870 days never flag) | 196 | 0.486 | 0.342 | 0.0708 | +0.0000 [+0.0000, +0.0000] | -0.0085 [-0.0120, -0.0047] | 0.580 | 0.411 | no |
| 5 | 0.286 (147 of 1869 days never flag) | 196 | 0.478 | 0.337 | 0.0709 | +0.0000 [+0.0000, +0.0000] | -0.0075 [-0.0115, -0.0036] | 0.577 | 0.403 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.4 over 1035 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.457 (climatology 0.457, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1754, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0463 [-0.1010, +0.0124]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.436 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0648 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0907 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1572 | 0.0031 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0729 | 0.4146 | 0.0000 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.424 | 0.1413 | 0.2474 | +0.0000 [+0.0000, +0.0000] |
| day_type | month_end | 150 | 17 | 0.529 | 0.375 | 0.1364 | 0.1133 | +0.0000 [+0.0000, +0.0000] |
| day_type | ordinary | 1602 | 101 | 0.505 | 0.398 | 0.1006 | 0.0630 | +0.0000 [+0.0000, +0.0000] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.250 | 0.4089 | 0.2903 | +0.0000 [+0.0000, +0.0000] |
| day_type | tax_date | 90 | 13 | 0.615 | 0.267 | 0.2262 | 0.1444 | +0.0000 [+0.0000, +0.0000] |

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
| 2 | 0.258 (147 of 1872 days never flag) | 170 | 0.583 | 0.476 | 0.0611 | +0.0100 [+0.0056, +0.0147] | +0.0000 [+0.0000, +0.0000] | 0.817 | 0.531 | no |
| 3 | 0.255 (189 of 1871 days never flag) | 120 | 0.341 | 0.392 | 0.0644 | +0.0063 [+0.0030, +0.0099] | +0.0000 [+0.0000, +0.0000] | 0.765 | 0.298 | no |
| 4 | 0.251 (232 of 1870 days never flag) | 141 | 0.428 | 0.418 | 0.0624 | +0.0085 [+0.0047, +0.0121] | +0.0000 [+0.0000, +0.0000] | 0.788 | 0.380 | no |
| 5 | 0.323 (315 of 1869 days never flag) | 127 | 0.391 | 0.425 | 0.0634 | +0.0075 [+0.0036, +0.0114] | +0.0000 [+0.0000, +0.0000] | 0.772 | 0.349 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.477 (climatology 0.457, difference +0.0203 [-0.0817, +0.1399]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0508, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.451 | 0.455 | 0.1679 | 0.2720 | +0.0168 [-0.0029, +0.0375] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0113, +0.0148] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.0978 | 0.1165 | +0.0257 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0233 | 0.0048 | +0.0081 [+0.0059, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0891 | 0.0031 | +0.0206 [+0.0143, +0.0267] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.615 | 0.2311 | 0.4146 | 0.0897 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.453 | 0.457 | 0.1759 | 0.2474 | +0.0203 [+0.0031, +0.0386] |
| day_type | month_end | 150 | 17 | 0.412 | 0.583 | 0.0778 | 0.1133 | +0.0212 [+0.0029, +0.0434] |
| day_type | ordinary | 1602 | 101 | 0.475 | 0.432 | 0.0774 | 0.0630 | +0.0125 [+0.0072, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.0845 | 0.2903 | +0.0604 [-0.0440, +0.1631] |
| day_type | tax_date | 90 | 13 | 0.231 | 0.429 | 0.0813 | 0.1444 | +0.0350 [+0.0121, +0.0559] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1364 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3171 | 0.2213 |

## risk_gbm (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.667] | 0.154 | 1.38 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.115 | 1.08 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 78 | 0.300 | 0.538 | 0.0578 | +0.0136 [+0.0081, +0.0191] | -0.0015 [-0.0097, +0.0062] | 0.642 | 0.279 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 53 | 0.180 | 0.472 | 0.0687 | +0.0023 [-0.0040, +0.0080] | -0.0077 [-0.0162, -0.0007] | 0.578 | 0.164 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 53 | 0.181 | 0.472 | 0.0669 | +0.0038 [-0.0027, +0.0097] | -0.0025 [-0.0103, +0.0041] | 0.579 | 0.165 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 48 | 0.174 | 0.500 | 0.0669 | +0.0039 [-0.0029, +0.0100] | -0.0046 [-0.0123, +0.0023] | 0.579 | 0.160 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 49 | 0.159 | 0.449 | 0.0696 | +0.0014 [-0.0053, +0.0074] | -0.0062 [-0.0133, +0.0007] | 0.577 | 0.144 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.491 (climatology 0.457, difference +0.0335 [-0.1279, +0.1613]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1051, ΔBrier vs climatology +0.0244 [+0.0155, +0.0332], realised minus predicted +0.0938 [+0.0571, +0.1325]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0951 | 0.2720 | +0.0020 [-0.0195, +0.0249] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0145 | 0.0159 | +0.0398 [+0.0309, +0.0486] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0007 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0023 | 0.0200 | +0.0026 [-0.0012, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.600 | 0.0373 | 0.1165 | +0.0151 [-0.0019, +0.0375] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.167 | 0.0020 | 0.0048 | +0.0085 [+0.0065, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0037 | 0.0031 | +0.0298 [+0.0224, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0314 | 0.4146 | -0.0075 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.582 | 0.0954 | 0.2474 | +0.0153 [-0.0048, +0.0361] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0968 | 0.1133 | +0.0527 [+0.0295, +0.0765] |
| day_type | ordinary | 1602 | 101 | 0.149 | 0.536 | 0.0127 | 0.0630 | +0.0048 [-0.0003, +0.0098] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2112 | 0.2903 | +0.1035 [+0.0201, +0.1919] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.529 | 0.0921 | 0.1444 | +0.0733 [+0.0455, +0.1010] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7102 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2007 | 0.2213 |

## risk_gbm+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.760] | 0.231 | 3.00 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 98 | 0.450 | 0.643 | 0.0479 | +0.0235 [+0.0162, +0.0317] | +0.0084 [+0.0037, +0.0137] | 0.891 | 0.430 | no |
| 2 | 0.367 (147 of 1872 days never flag) | 138 | 0.446 | 0.449 | 0.0602 | +0.0109 [+0.0064, +0.0151] | +0.0009 [-0.0023, +0.0040] | 0.832 | 0.402 | no |
| 3 | 0.422 (147 of 1871 days never flag) | 137 | 0.428 | 0.431 | 0.0607 | +0.0099 [+0.0063, +0.0138] | +0.0036 [+0.0011, +0.0065] | 0.811 | 0.383 | no |
| 4 | 0.426 (147 of 1870 days never flag) | 110 | 0.413 | 0.518 | 0.0595 | +0.0114 [+0.0070, +0.0160] | +0.0029 [+0.0003, +0.0058] | 0.822 | 0.382 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 117 | 0.370 | 0.436 | 0.0629 | +0.0080 [+0.0035, +0.0126] | +0.0005 [-0.0026, +0.0034] | 0.792 | 0.331 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.476 (climatology 0.457, difference +0.0185 [-0.1080, +0.1260]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0448 [+0.0312, +0.0599], realised minus predicted +0.0122 [-0.0180, +0.0447]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2365 | 0.2720 | +0.0579 [+0.0311, +0.0865] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1171 | 0.0159 | +0.0236 [+0.0102, +0.0351] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0192 | 0.0000 | +0.0131 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0323 | 0.0200 | -0.0005 [-0.0074, +0.0041] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.1134 | 0.1165 | +0.0271 [-0.0001, +0.0590] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0227 | 0.0048 | +0.0073 [+0.0048, +0.0095] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0682 | 0.0031 | +0.0224 [+0.0151, +0.0292] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2156 | 0.4146 | 0.0618 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.656 | 0.2417 | 0.2474 | +0.0564 [+0.0318, +0.0825] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1062 | 0.1133 | +0.0579 [+0.0346, +0.0841] |
| day_type | ordinary | 1602 | 101 | 0.436 | 0.603 | 0.0862 | 0.0630 | +0.0160 [+0.0093, +0.0238] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2112 | 0.2903 | +0.1035 [+0.0266, +0.1828] |
| day_type | tax_date | 90 | 13 | 0.385 | 1.000 | 0.0921 | 0.1444 | +0.0733 [+0.0458, +0.1025] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3102 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3386 | 0.2213 |

## risk_gbm+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.231 | 2.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.545] | 0.231 | 2.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 66 | 0.314 | 0.667 | 0.0498 | +0.0217 [+0.0144, +0.0291] | +0.0066 [+0.0015, +0.0118] | 0.804 | 0.302 | no |
| 2 | 0.367 (147 of 1872 days never flag) | 121 | 0.388 | 0.446 | 0.0624 | +0.0086 [+0.0037, +0.0132] | -0.0014 [-0.0056, +0.0024] | 0.749 | 0.350 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 133 | 0.413 | 0.429 | 0.0608 | +0.0099 [+0.0048, +0.0145] | +0.0036 [-0.0008, +0.0073] | 0.746 | 0.369 | no |
| 4 | 0.258 (147 of 1870 days never flag) | 107 | 0.384 | 0.495 | 0.0603 | +0.0105 [+0.0056, +0.0155] | +0.0020 [-0.0015, +0.0055] | 0.760 | 0.353 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 112 | 0.348 | 0.429 | 0.0635 | +0.0074 [+0.0018, +0.0127] | -0.0002 [-0.0041, +0.0038] | 0.743 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.494 (climatology 0.457, difference +0.0369 [-0.1008, +0.1577]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0866, ΔBrier vs climatology +0.0429 [+0.0298, +0.0575], realised minus predicted +0.0624 [+0.0339, +0.0961]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.1668 | 0.2720 | +0.0422 [+0.0145, +0.0708] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0221 | 0.0159 | +0.0326 [+0.0163, +0.0454] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0147 | 0.0200 | -0.0004 [-0.0079, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0885 | 0.1165 | +0.0262 [+0.0009, +0.0571] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0087 | 0.0048 | +0.0076 [+0.0051, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0087 | 0.0031 | +0.0284 [+0.0206, +0.0356] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.1868 | 0.4146 | 0.0598 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.359 | 0.689 | 0.1641 | 0.2474 | +0.0446 [+0.0209, +0.0700] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1007 | 0.1133 | +0.0584 [+0.0341, +0.0851] |
| day_type | ordinary | 1602 | 101 | 0.248 | 0.595 | 0.0419 | 0.0630 | +0.0137 [+0.0075, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2112 | 0.2903 | +0.1035 [+0.0208, +0.1845] |
| day_type | tax_date | 90 | 13 | 0.385 | 1.000 | 0.0921 | 0.1444 | +0.0733 [+0.0456, +0.1018] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3102 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3827 | 0.2213 |

## risk_gbm+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.715] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.226, 0.565] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 80 | 0.343 | 0.600 | 0.0484 | +0.0230 [+0.0162, +0.0305] | +0.0079 [+0.0031, +0.0132] | 0.881 | 0.324 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 132 | 0.439 | 0.462 | 0.0595 | +0.0116 [+0.0082, +0.0150] | +0.0016 [-0.0020, +0.0051] | 0.816 | 0.398 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 135 | 0.420 | 0.430 | 0.0593 | +0.0114 [+0.0081, +0.0150] | +0.0050 [+0.0016, +0.0086] | 0.800 | 0.376 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 116 | 0.399 | 0.474 | 0.0581 | +0.0127 [+0.0092, +0.0163] | +0.0043 [+0.0016, +0.0071] | 0.811 | 0.363 | no |
| 5 | 0.258 (147 of 1869 days never flag) | 106 | 0.370 | 0.481 | 0.0612 | +0.0097 [+0.0061, +0.0135] | +0.0022 [-0.0008, +0.0052] | 0.784 | 0.338 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.474 (climatology 0.457, difference +0.0172 [-0.1176, +0.1340]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0863, ΔBrier vs climatology +0.0432 [+0.0304, +0.0571], realised minus predicted +0.0225 [-0.0094, +0.0587]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.382 | 0.582 | 0.2169 | 0.2720 | +0.0503 [+0.0244, +0.0777] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.1031 | 0.0159 | +0.0293 [+0.0205, +0.0388] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0161 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0236 | 0.0200 | +0.0016 [-0.0027, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.727 | 0.0968 | 0.1165 | +0.0260 [+0.0028, +0.0550] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0181 | 0.0048 | +0.0080 [+0.0060, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0569 | 0.0031 | +0.0247 [+0.0180, +0.0311] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.500 | 0.1743 | 0.4146 | 0.0487 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.402 | 0.610 | 0.2219 | 0.2474 | +0.0524 [+0.0296, +0.0772] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1048 | 0.1133 | +0.0570 [+0.0331, +0.0818] |
| day_type | ordinary | 1602 | 101 | 0.257 | 0.510 | 0.0741 | 0.0630 | +0.0154 [+0.0093, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2112 | 0.2903 | +0.1035 [+0.0232, +0.1832] |
| day_type | tax_date | 90 | 13 | 0.538 | 1.000 | 0.0921 | 0.1444 | +0.0733 [+0.0464, +0.1027] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.4598 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2490 | 0.2213 |

## risk_gbm+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.760] | 0.231 | 3.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.600] | 0.231 | 3.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 97 | 0.450 | 0.649 | 0.0472 | +0.0242 [+0.0169, +0.0320] | +0.0091 [+0.0042, +0.0143] | 0.911 | 0.430 | no |
| 2 | 0.367 (147 of 1872 days never flag) | 139 | 0.453 | 0.453 | 0.0595 | +0.0116 [+0.0071, +0.0160] | +0.0016 [-0.0018, +0.0047] | 0.871 | 0.409 | no |
| 3 | 0.422 (147 of 1871 days never flag) | 141 | 0.435 | 0.426 | 0.0590 | +0.0117 [+0.0081, +0.0152] | +0.0053 [+0.0027, +0.0081] | 0.859 | 0.388 | no |
| 4 | 0.426 (147 of 1870 days never flag) | 110 | 0.420 | 0.527 | 0.0582 | +0.0127 [+0.0086, +0.0171] | +0.0042 [+0.0017, +0.0071] | 0.865 | 0.390 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 115 | 0.370 | 0.443 | 0.0619 | +0.0090 [+0.0045, +0.0135] | +0.0015 [-0.0016, +0.0046] | 0.850 | 0.333 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.476 (climatology 0.457, difference +0.0185 [-0.1081, +0.1280]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0839, ΔBrier vs climatology +0.0456 [+0.0319, +0.0599], realised minus predicted +0.0385 [+0.0086, +0.0714]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2365 | 0.2720 | +0.0579 [+0.0298, +0.0863] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1171 | 0.0159 | +0.0236 [+0.0110, +0.0360] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0051 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0023 | 0.0200 | +0.0026 [-0.0012, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0999 | 0.1165 | +0.0279 [+0.0005, +0.0609] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0020 | 0.0048 | +0.0085 [+0.0066, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0682 | 0.0031 | +0.0224 [+0.0155, +0.0292] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2156 | 0.4146 | 0.0618 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.656 | 0.2417 | 0.2474 | +0.0564 [+0.0314, +0.0808] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1041 | 0.1133 | +0.0579 [+0.0346, +0.0845] |
| day_type | ordinary | 1602 | 101 | 0.436 | 0.611 | 0.0730 | 0.0630 | +0.0167 [+0.0099, +0.0240] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2112 | 0.2903 | +0.1035 [+0.0251, +0.1843] |
| day_type | tax_date | 90 | 13 | 0.385 | 1.000 | 0.0921 | 0.1444 | +0.0733 [+0.0450, +0.1011] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3102 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3386 | 0.2213 |

## risk_gbm+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.650] | 0.115 | 1.27 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.423] | 0.115 | 1.15 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 83 | 0.379 | 0.639 | 0.0485 | +0.0230 [+0.0173, +0.0289] | +0.0079 [+0.0029, +0.0131] | 0.898 | 0.361 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 65 | 0.230 | 0.492 | 0.0604 | +0.0106 [+0.0073, +0.0137] | +0.0006 [-0.0033, +0.0044] | 0.842 | 0.211 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 55 | 0.203 | 0.509 | 0.0599 | +0.0107 [+0.0075, +0.0143] | +0.0044 [+0.0006, +0.0082] | 0.819 | 0.187 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 53 | 0.203 | 0.528 | 0.0593 | +0.0115 [+0.0079, +0.0153] | +0.0031 [-0.0004, +0.0064] | 0.830 | 0.188 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 54 | 0.174 | 0.444 | 0.0623 | +0.0086 [+0.0049, +0.0122] | +0.0011 [-0.0028, +0.0045] | 0.803 | 0.157 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.470 (climatology 0.457, difference +0.0128 [-0.1260, +0.1367]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0901, ΔBrier vs climatology +0.0394 [+0.0290, +0.0509], realised minus predicted +0.0541 [+0.0210, +0.0889]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.608 | 0.1658 | 0.2720 | +0.0433 [+0.0261, +0.0606] |
| regime | 2020 | 251 | 4 | 0.250 | 1.000 | 0.0658 | 0.0159 | +0.0368 [+0.0284, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0100 | 0.0000 | +0.0136 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0173 | 0.0200 | +0.0019 [-0.0022, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0754 | 0.1165 | +0.0276 [+0.0035, +0.0589] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0123 | 0.0048 | +0.0083 [+0.0062, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0360 | 0.0031 | +0.0280 [+0.0209, +0.0345] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.1235 | 0.4146 | 0.0485 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.642 | 0.1686 | 0.2474 | +0.0495 [+0.0326, +0.0671] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1015 | 0.1133 | +0.0556 [+0.0319, +0.0828] |
| day_type | ordinary | 1602 | 101 | 0.307 | 0.608 | 0.0494 | 0.0630 | +0.0155 [+0.0111, +0.0201] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2112 | 0.2903 | +0.1035 [+0.0226, +0.1868] |
| day_type | tax_date | 90 | 13 | 0.538 | 0.875 | 0.0921 | 0.1444 | +0.0733 [+0.0453, +0.1041] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.4102 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2178 | 0.2213 |

## risk_gbm_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.419] | 0.115 | 1.23 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 81 | 0.300 | 0.519 | 0.0586 | +0.0128 [+0.0079, +0.0173] | -0.0023 [-0.0102, +0.0045] | 0.643 | 0.277 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 50 | 0.173 | 0.480 | 0.0691 | +0.0020 [-0.0047, +0.0082] | -0.0080 [-0.0167, -0.0003] | 0.577 | 0.158 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 55 | 0.167 | 0.418 | 0.0676 | +0.0031 [-0.0036, +0.0091] | -0.0032 [-0.0114, +0.0035] | 0.579 | 0.148 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0668 | +0.0040 [-0.0023, +0.0101] | -0.0044 [-0.0120, +0.0024] | 0.579 | 0.179 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 49 | 0.152 | 0.429 | 0.0697 | +0.0013 [-0.0055, +0.0072] | -0.0063 [-0.0141, +0.0004] | 0.576 | 0.136 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.457, difference +0.0410 [-0.1117, +0.1732]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1061, ΔBrier vs climatology +0.0234 [+0.0144, +0.0327], realised minus predicted +0.0913 [+0.0563, +0.1287]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0972 | 0.2720 | -0.0000 [-0.0193, +0.0167] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0253 | 0.0159 | +0.0338 [+0.0241, +0.0436] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0016 | 0.0200 | +0.0033 [-0.0002, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0343 | 0.1165 | +0.0173 [+0.0019, +0.0356] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0008 | 0.0048 | +0.0093 [+0.0077, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0077 | 0.0031 | +0.0289 [+0.0224, +0.0351] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0345 | 0.4146 | -0.0008 [-0.0280, +0.0369] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.565 | 0.0996 | 0.2474 | +0.0105 [-0.0071, +0.0274] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0970 | 0.1133 | +0.0339 [+0.0115, +0.0566] |
| day_type | ordinary | 1602 | 101 | 0.158 | 0.500 | 0.0128 | 0.0630 | +0.0053 [+0.0003, +0.0098] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.1993 | 0.2903 | +0.1062 [+0.0282, +0.1858] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.562 | 0.1173 | 0.1444 | +0.0783 [+0.0544, +0.1051] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4167 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2061 | 0.2213 |

## risk_gbm_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.769] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.619] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 150 | 0.571 | 0.533 | 0.0487 | +0.0227 [+0.0154, +0.0309] | +0.0076 [+0.0030, +0.0128] | 0.898 | 0.531 | no |
| 2 | 0.306 (147 of 1872 days never flag) | 137 | 0.432 | 0.438 | 0.0605 | +0.0105 [+0.0064, +0.0147] | +0.0005 [-0.0026, +0.0036] | 0.828 | 0.387 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 134 | 0.428 | 0.440 | 0.0615 | +0.0092 [+0.0054, +0.0130] | +0.0029 [-0.0001, +0.0059] | 0.810 | 0.384 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 101 | 0.391 | 0.535 | 0.0593 | +0.0115 [+0.0069, +0.0161] | +0.0030 [+0.0000, +0.0064] | 0.832 | 0.364 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 118 | 0.362 | 0.424 | 0.0630 | +0.0080 [+0.0035, +0.0121] | +0.0004 [-0.0026, +0.0034] | 0.784 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.467 (climatology 0.457, difference +0.0103 [-0.1217, +0.1345]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0861, ΔBrier vs climatology +0.0434 [+0.0296, +0.0590], realised minus predicted +0.0108 [-0.0207, +0.0458]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0558 [+0.0275, +0.0864] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1279 | 0.0159 | +0.0175 [+0.0026, +0.0303] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0317 | 0.0200 | +0.0003 [-0.0065, +0.0048] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.1104 | 0.1165 | +0.0292 [+0.0033, +0.0622] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0215 | 0.0048 | +0.0081 [+0.0059, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0722 | 0.0031 | +0.0215 [+0.0149, +0.0273] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.556 | 0.2187 | 0.4146 | 0.0685 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.540 | 0.2460 | 0.2474 | +0.0516 [+0.0263, +0.0781] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1064 | 0.1133 | +0.0390 [+0.0156, +0.0637] |
| day_type | ordinary | 1602 | 101 | 0.564 | 0.496 | 0.0863 | 0.0630 | +0.0165 [+0.0094, +0.0244] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1993 | 0.2903 | +0.1062 [+0.0315, +0.1856] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.692 | 0.1173 | 0.1444 | +0.0783 [+0.0549, +0.1063] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0167 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3441 | 0.2213 |

## risk_gbm_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.393, 0.750] | 0.231 | 2.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.520] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 146 | 0.536 | 0.514 | 0.0506 | +0.0209 [+0.0140, +0.0279] | +0.0058 [+0.0012, +0.0105] | 0.805 | 0.495 | no |
| 2 | 0.306 (147 of 1872 days never flag) | 121 | 0.381 | 0.438 | 0.0628 | +0.0083 [+0.0035, +0.0130] | -0.0017 [-0.0059, +0.0022] | 0.748 | 0.342 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 130 | 0.399 | 0.423 | 0.0615 | +0.0092 [+0.0042, +0.0139] | +0.0029 [-0.0015, +0.0068] | 0.746 | 0.355 | no |
| 4 | 0.265 (147 of 1870 days never flag) | 109 | 0.384 | 0.486 | 0.0602 | +0.0106 [+0.0055, +0.0156] | +0.0022 [-0.0016, +0.0056] | 0.761 | 0.352 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 106 | 0.333 | 0.434 | 0.0636 | +0.0073 [+0.0021, +0.0121] | -0.0002 [-0.0043, +0.0035] | 0.740 | 0.299 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.457, difference +0.0401 [-0.0986, +0.1618]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0880, ΔBrier vs climatology +0.0415 [+0.0287, +0.0551], realised minus predicted +0.0599 [+0.0308, +0.0916]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.563 | 0.1689 | 0.2720 | +0.0401 [+0.0141, +0.0670] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0329 | 0.0159 | +0.0265 [+0.0096, +0.0400] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0141 | 0.0200 | +0.0004 [-0.0069, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.556 | 0.0855 | 0.1165 | +0.0284 [+0.0043, +0.0568] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0075 | 0.0048 | +0.0083 [+0.0061, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0126 | 0.0031 | +0.0275 [+0.0201, +0.0336] |
| scarcity_state | 2 | 41 | 17 | 0.412 | 0.583 | 0.1899 | 0.4146 | 0.0665 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.540 | 0.1683 | 0.2474 | +0.0398 [+0.0158, +0.0639] |
| day_type | month_end | 150 | 17 | 0.647 | 0.524 | 0.1008 | 0.1133 | +0.0396 [+0.0144, +0.0648] |
| day_type | ordinary | 1602 | 101 | 0.495 | 0.485 | 0.0421 | 0.0630 | +0.0142 [+0.0077, +0.0210] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.1993 | 0.2903 | +0.1062 [+0.0269, +0.1840] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.643 | 0.1173 | 0.1444 | +0.0783 [+0.0549, +0.1054] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0167 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3881 | 0.2213 |

## risk_gbm_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.737] | 0.231 | 2.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.565] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 134 | 0.514 | 0.537 | 0.0487 | +0.0227 [+0.0162, +0.0304] | +0.0076 [+0.0030, +0.0127] | 0.892 | 0.479 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 133 | 0.432 | 0.451 | 0.0599 | +0.0112 [+0.0080, +0.0146] | +0.0012 [-0.0022, +0.0046] | 0.812 | 0.390 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 131 | 0.406 | 0.427 | 0.0600 | +0.0107 [+0.0074, +0.0142] | +0.0043 [+0.0008, +0.0082] | 0.799 | 0.363 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 120 | 0.399 | 0.458 | 0.0577 | +0.0131 [+0.0093, +0.0168] | +0.0046 [+0.0016, +0.0078] | 0.828 | 0.361 | no |
| 5 | 0.265 (147 of 1869 days never flag) | 113 | 0.370 | 0.451 | 0.0613 | +0.0096 [+0.0062, +0.0130] | +0.0021 [-0.0010, +0.0049] | 0.774 | 0.334 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.467 (climatology 0.457, difference +0.0103 [-0.1193, +0.1280]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0873, ΔBrier vs climatology +0.0422 [+0.0288, +0.0570], realised minus predicted +0.0207 [-0.0105, +0.0563]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.532 | 0.2209 | 0.2720 | +0.0502 [+0.0238, +0.0800] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1156 | 0.0159 | +0.0231 [+0.0115, +0.0339] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0155 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0223 | 0.0200 | +0.0024 [-0.0017, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.667 | 0.0941 | 0.1165 | +0.0294 [+0.0069, +0.0573] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0167 | 0.0048 | +0.0088 [+0.0070, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0620 | 0.0031 | +0.0237 [+0.0179, +0.0292] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1804 | 0.4146 | 0.0622 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.581 | 0.535 | 0.2276 | 0.2474 | +0.0491 [+0.0258, +0.0755] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1050 | 0.1133 | +0.0382 [+0.0153, +0.0627] |
| day_type | ordinary | 1602 | 101 | 0.465 | 0.485 | 0.0749 | 0.0630 | +0.0165 [+0.0104, +0.0237] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1993 | 0.2903 | +0.1062 [+0.0318, +0.1849] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.692 | 0.1173 | 0.1444 | +0.0783 [+0.0547, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0208 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2544 | 0.2213 |

## risk_gbm_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.769] | 0.231 | 3.00 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.231 | 3.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (105 of 1873 days never flag) | 149 | 0.571 | 0.537 | 0.0480 | +0.0234 [+0.0162, +0.0311] | +0.0083 [+0.0036, +0.0134] | 0.913 | 0.532 | no |
| 2 | 0.306 (147 of 1872 days never flag) | 139 | 0.439 | 0.439 | 0.0598 | +0.0113 [+0.0069, +0.0155] | +0.0013 [-0.0017, +0.0044] | 0.868 | 0.394 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 138 | 0.435 | 0.435 | 0.0598 | +0.0109 [+0.0074, +0.0148] | +0.0046 [+0.0017, +0.0076] | 0.857 | 0.390 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 105 | 0.406 | 0.533 | 0.0581 | +0.0128 [+0.0086, +0.0173] | +0.0043 [+0.0015, +0.0076] | 0.868 | 0.378 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 116 | 0.362 | 0.431 | 0.0620 | +0.0090 [+0.0047, +0.0131] | +0.0014 [-0.0017, +0.0045] | 0.844 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.467 (climatology 0.457, difference +0.0103 [-0.1184, +0.1260]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0447 [+0.0310, +0.0600], realised minus predicted +0.0372 [+0.0064, +0.0703]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0558 [+0.0290, +0.0860] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1279 | 0.0159 | +0.0175 [+0.0031, +0.0313] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0045 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0016 | 0.0200 | +0.0033 [-0.0005, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0969 | 0.1165 | +0.0301 [+0.0044, +0.0594] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0008 | 0.0048 | +0.0093 [+0.0077, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0722 | 0.0031 | +0.0215 [+0.0153, +0.0273] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.556 | 0.2187 | 0.4146 | 0.0685 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.641 | 0.540 | 0.2460 | 0.2474 | +0.0516 [+0.0266, +0.0787] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1043 | 0.1133 | +0.0391 [+0.0143, +0.0644] |
| day_type | ordinary | 1602 | 101 | 0.564 | 0.500 | 0.0731 | 0.0630 | +0.0172 [+0.0104, +0.0246] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1993 | 0.2903 | +0.1062 [+0.0261, +0.1843] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.692 | 0.1173 | 0.1444 | +0.0783 [+0.0549, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0167 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3441 | 0.2213 |

## risk_gbm_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.684] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.130, 0.424] | 0.154 | 1.42 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.223 (105 of 1873 days never flag) | 130 | 0.479 | 0.515 | 0.0493 | +0.0222 [+0.0168, +0.0277] | +0.0071 [+0.0023, +0.0116] | 0.908 | 0.442 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 65 | 0.223 | 0.477 | 0.0608 | +0.0103 [+0.0069, +0.0134] | +0.0003 [-0.0041, +0.0040] | 0.838 | 0.203 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0607 | +0.0100 [+0.0065, +0.0133] | +0.0037 [-0.0004, +0.0075] | 0.815 | 0.173 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 57 | 0.203 | 0.491 | 0.0592 | +0.0117 [+0.0081, +0.0152] | +0.0032 [-0.0008, +0.0068] | 0.838 | 0.186 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 61 | 0.174 | 0.393 | 0.0624 | +0.0085 [+0.0051, +0.0118] | +0.0010 [-0.0028, +0.0044] | 0.793 | 0.153 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.461 (climatology 0.457, difference +0.0041 [-0.1150, +0.1287]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0915, ΔBrier vs climatology +0.0380 [+0.0272, +0.0491], realised minus predicted +0.0520 [+0.0189, +0.0874]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.576 | 0.1679 | 0.2720 | +0.0413 [+0.0250, +0.0585] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0766 | 0.0159 | +0.0307 [+0.0209, +0.0401] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0166 | 0.0200 | +0.0026 [-0.0017, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0723 | 0.1165 | +0.0298 [+0.0070, +0.0568] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0111 | 0.0048 | +0.0090 [+0.0073, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0399 | 0.0031 | +0.0270 [+0.0209, +0.0327] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1266 | 0.4146 | +0.0552 [-0.0073, +0.1165] |
| scarcity_state | 3 | 473 | 117 | 0.530 | 0.554 | 0.1728 | 0.2474 | +0.0447 [+0.0279, +0.0616] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.1017 | 0.1133 | +0.0368 [+0.0143, +0.0592] |
| day_type | ordinary | 1602 | 101 | 0.406 | 0.488 | 0.0496 | 0.0630 | +0.0160 [+0.0116, +0.0207] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.1993 | 0.2903 | +0.1062 [+0.0306, +0.1842] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.643 | 0.1173 | 0.1444 | +0.0783 [+0.0544, +0.1038] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1167 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2232 | 0.2213 |

## risk_logistic (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.724] | 0.192 | 1.85 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.105 (105 of 1873 days never flag) | 91 | 0.307 | 0.473 | 0.0607 | +0.0108 [+0.0055, +0.0159] | -0.0043 [-0.0130, +0.0036] | 0.641 | 0.279 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 54 | 0.201 | 0.519 | 0.0676 | +0.0034 [-0.0032, +0.0092] | -0.0066 [-0.0146, +0.0006] | 0.578 | 0.186 | no |
| 3 | 0.0777 (147 of 1871 days never flag) | 60 | 0.210 | 0.483 | 0.0684 | +0.0023 [-0.0049, +0.0089] | -0.0040 [-0.0124, +0.0033] | 0.578 | 0.192 | no |
| 4 | 0.103 (147 of 1870 days never flag) | 68 | 0.188 | 0.382 | 0.0685 | +0.0023 [-0.0045, +0.0085] | -0.0061 [-0.0146, +0.0014] | 0.578 | 0.164 | no |
| 5 | 0.115 (147 of 1869 days never flag) | 60 | 0.159 | 0.367 | 0.0688 | +0.0022 [-0.0049, +0.0086] | -0.0054 [-0.0137, +0.0020] | 0.576 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1223 [-0.0239, +0.2474]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1073, ΔBrier vs climatology +0.0222 [+0.0116, +0.0326], realised minus predicted +0.0758 [+0.0424, +0.1119]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1083 | 0.2720 | -0.0033 [-0.0253, +0.0173] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0306 | 0.0159 | +0.0259 [+0.0113, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0060 | 0.0200 | +0.0049 [+0.0008, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.625 | 0.0337 | 0.1165 | +0.0134 [+0.0003, +0.0300] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0033 | 0.0048 | +0.0091 [+0.0073, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0066 | 0.0031 | +0.0286 [+0.0226, +0.0342] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0364 | 0.4146 | 0.0053 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.506 | 0.1090 | 0.2474 | +0.0027 [-0.0166, +0.0215] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1022 | 0.1133 | +0.0283 [+0.0018, +0.0567] |
| day_type | ordinary | 1602 | 101 | 0.149 | 0.469 | 0.0128 | 0.0630 | +0.0039 [-0.0013, +0.0087] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3539 | 0.2903 | +0.0936 [+0.0194, +0.1637] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.500 | 0.1313 | 0.1444 | +0.0758 [+0.0443, +0.1121] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2026 | 0.2213 |

## risk_logistic+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.375, 0.707] | 0.231 | 2.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.238, 0.546] | 0.231 | 2.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.373 (126 of 1873 days never flag) | 131 | 0.493 | 0.527 | 0.0507 | +0.0207 [+0.0133, +0.0282] | +0.0056 [-0.0001, +0.0111] | 0.879 | 0.457 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 75 | 0.252 | 0.467 | 0.0591 | +0.0120 [+0.0064, +0.0178] | +0.0020 [-0.0027, +0.0065] | 0.841 | 0.229 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 60 | 0.225 | 0.517 | 0.0623 | +0.0084 [+0.0022, +0.0144] | +0.0021 [-0.0037, +0.0076] | 0.811 | 0.208 | no |
| 4 | 0.501 (147 of 1870 days never flag) | 63 | 0.239 | 0.524 | 0.0610 | +0.0098 [+0.0041, +0.0153] | +0.0013 [-0.0038, +0.0068] | 0.818 | 0.222 | no |
| 5 | 0.329 (147 of 1869 days never flag) | 131 | 0.457 | 0.481 | 0.0621 | +0.0088 [+0.0038, +0.0139] | +0.0013 [-0.0029, +0.0056] | 0.796 | 0.417 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.457, difference +0.1605 [+0.0331, +0.2905]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0880, ΔBrier vs climatology +0.0415 [+0.0264, +0.0581], realised minus predicted -0.0039 [-0.0334, +0.0281]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.589 | 0.2497 | 0.2720 | +0.0525 [+0.0249, +0.0804] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1332 | 0.0159 | +0.0097 [-0.0124, +0.0260] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0190 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0360 | 0.0200 | +0.0019 [-0.0049, +0.0080] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.1098 | 0.1165 | +0.0254 [+0.0012, +0.0537] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0240 | 0.0048 | +0.0079 [+0.0056, +0.0101] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0711 | 0.0031 | +0.0212 [+0.0151, +0.0267] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.2206 | 0.4146 | 0.0746 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.547 | 0.552 | 0.2553 | 0.2474 | +0.0437 [+0.0162, +0.0683] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1115 | 0.1133 | +0.0335 [+0.0064, +0.0618] |
| day_type | ordinary | 1602 | 101 | 0.436 | 0.500 | 0.0862 | 0.0630 | +0.0150 [+0.0083, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3539 | 0.2903 | +0.0936 [+0.0174, +0.1713] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.600 | 0.1313 | 0.1444 | +0.0758 [+0.0450, +0.1108] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3405 | 0.2213 |

## risk_logistic+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.414, 0.742] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.259, 0.586] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.373 (105 of 1873 days never flag) | 124 | 0.450 | 0.508 | 0.0526 | +0.0189 [+0.0122, +0.0263] | +0.0038 [-0.0019, +0.0095] | 0.801 | 0.415 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 75 | 0.252 | 0.467 | 0.0613 | +0.0097 [+0.0039, +0.0157] | -0.0003 [-0.0051, +0.0048] | 0.752 | 0.229 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 77 | 0.268 | 0.481 | 0.0623 | +0.0084 [+0.0019, +0.0147] | +0.0020 [-0.0040, +0.0079] | 0.746 | 0.245 | no |
| 4 | 0.501 (147 of 1870 days never flag) | 62 | 0.239 | 0.532 | 0.0619 | +0.0089 [+0.0035, +0.0146] | +0.0005 [-0.0046, +0.0057] | 0.758 | 0.222 | no |
| 5 | 0.329 (147 of 1869 days never flag) | 141 | 0.464 | 0.454 | 0.0627 | +0.0082 [+0.0027, +0.0137] | +0.0007 [-0.0040, +0.0052] | 0.743 | 0.419 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.602 (climatology 0.457, difference +0.1452 [+0.0058, +0.2582]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0906, ΔBrier vs climatology +0.0389 [+0.0230, +0.0542], realised minus predicted +0.0459 [+0.0166, +0.0737]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.562 | 0.1800 | 0.2720 | +0.0368 [+0.0114, +0.0636] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0382 | 0.0159 | +0.0187 [-0.0042, +0.0371] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0184 | 0.0200 | +0.0020 [-0.0056, +0.0082] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0849 | 0.1165 | +0.0245 [+0.0024, +0.0533] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0100 | 0.0048 | +0.0081 [+0.0057, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0116 | 0.0031 | +0.0272 [+0.0203, +0.0338] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.1918 | 0.4146 | 0.0726 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.532 | 0.1777 | 0.2474 | +0.0319 [+0.0079, +0.0577] |
| day_type | month_end | 150 | 17 | 0.647 | 0.550 | 0.1060 | 0.1133 | +0.0340 [+0.0051, +0.0630] |
| day_type | ordinary | 1602 | 101 | 0.366 | 0.474 | 0.0420 | 0.0630 | +0.0128 [+0.0067, +0.0197] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3539 | 0.2903 | +0.0936 [+0.0149, +0.1680] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.600 | 0.1313 | 0.1444 | +0.0758 [+0.0461, +0.1127] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3846 | 0.2213 |

## risk_logistic+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.231 | 3.50 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.192 | 2.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.373 (126 of 1873 days never flag) | 175 | 0.600 | 0.480 | 0.0508 | +0.0206 [+0.0139, +0.0274] | +0.0055 [+0.0005, +0.0109] | 0.877 | 0.547 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 84 | 0.317 | 0.524 | 0.0581 | +0.0130 [+0.0082, +0.0181] | +0.0030 [-0.0017, +0.0080] | 0.830 | 0.293 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 72 | 0.283 | 0.542 | 0.0608 | +0.0099 [+0.0036, +0.0156] | +0.0035 [-0.0025, +0.0096] | 0.803 | 0.264 | no |
| 4 | 0.501 (147 of 1870 days never flag) | 81 | 0.275 | 0.469 | 0.0599 | +0.0109 [+0.0065, +0.0158] | +0.0025 [-0.0025, +0.0079] | 0.809 | 0.251 | no |
| 5 | 0.329 (147 of 1869 days never flag) | 112 | 0.435 | 0.536 | 0.0604 | +0.0105 [+0.0061, +0.0147] | +0.0030 [-0.0014, +0.0072] | 0.790 | 0.405 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.611 (climatology 0.457, difference +0.1536 [+0.0302, +0.2711]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0891, ΔBrier vs climatology +0.0404 [+0.0260, +0.0567], realised minus predicted +0.0056 [-0.0259, +0.0385]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.493 | 0.2326 | 0.2720 | +0.0469 [+0.0214, +0.0737] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1197 | 0.0159 | +0.0153 [-0.0027, +0.0288] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0163 | 0.0000 | +0.0133 [+0.0115, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0282 | 0.0200 | +0.0041 [-0.0000, +0.0087] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.579 | 0.0947 | 0.1165 | +0.0248 [+0.0037, +0.0505] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0200 | 0.0048 | +0.0086 [+0.0066, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0608 | 0.0031 | +0.0234 [+0.0176, +0.0288] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1797 | 0.4146 | 0.0640 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.675 | 0.485 | 0.2375 | 0.2474 | +0.0412 [+0.0177, +0.0640] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1101 | 0.1133 | +0.0326 [+0.0039, +0.0601] |
| day_type | ordinary | 1602 | 101 | 0.574 | 0.446 | 0.0754 | 0.0630 | +0.0150 [+0.0090, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3539 | 0.2903 | +0.0936 [+0.0187, +0.1672] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.600 | 0.1313 | 0.1444 | +0.0758 [+0.0445, +0.1122] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2509 | 0.2213 |

## risk_logistic+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.375, 0.700] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.231, 0.545] | 0.231 | 2.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.373 (126 of 1873 days never flag) | 130 | 0.493 | 0.531 | 0.0500 | +0.0214 [+0.0141, +0.0292] | +0.0063 [+0.0009, +0.0121] | 0.905 | 0.458 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 74 | 0.252 | 0.473 | 0.0583 | +0.0127 [+0.0070, +0.0183] | +0.0027 [-0.0017, +0.0077] | 0.878 | 0.229 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 58 | 0.225 | 0.534 | 0.0606 | +0.0101 [+0.0042, +0.0164] | +0.0038 [-0.0020, +0.0095] | 0.861 | 0.209 | no |
| 4 | 0.501 (147 of 1870 days never flag) | 61 | 0.239 | 0.541 | 0.0598 | +0.0111 [+0.0055, +0.0166] | +0.0026 [-0.0024, +0.0076] | 0.861 | 0.223 | no |
| 5 | 0.329 (147 of 1869 days never flag) | 129 | 0.457 | 0.488 | 0.0611 | +0.0099 [+0.0050, +0.0147] | +0.0023 [-0.0019, +0.0066] | 0.849 | 0.418 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.457, difference +0.1605 [+0.0305, +0.2775]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0430 [+0.0277, +0.0595], realised minus predicted +0.0211 [-0.0095, +0.0524]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.589 | 0.2497 | 0.2720 | +0.0525 [+0.0251, +0.0813] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1332 | 0.0159 | +0.0097 [-0.0113, +0.0264] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0049 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0008, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0963 | 0.1165 | +0.0263 [+0.0026, +0.0547] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0033 | 0.0048 | +0.0091 [+0.0073, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0711 | 0.0031 | +0.0212 [+0.0150, +0.0267] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.500 | 0.2206 | 0.4146 | 0.0746 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.547 | 0.552 | 0.2553 | 0.2474 | +0.0437 [+0.0180, +0.0706] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1095 | 0.1133 | +0.0336 [+0.0065, +0.0642] |
| day_type | ordinary | 1602 | 101 | 0.436 | 0.506 | 0.0730 | 0.0630 | +0.0158 [+0.0092, +0.0232] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3539 | 0.2903 | +0.0936 [+0.0182, +0.1674] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.600 | 0.1313 | 0.1444 | +0.0758 [+0.0451, +0.1129] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3405 | 0.2213 |

## risk_logistic+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.750] | 0.231 | 2.85 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.195, 0.500] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (126 of 1873 days never flag) | 150 | 0.543 | 0.507 | 0.0513 | +0.0202 [+0.0150, +0.0255] | +0.0051 [-0.0004, +0.0104] | 0.890 | 0.500 | no |
| 2 | 0.366 (147 of 1872 days never flag) | 47 | 0.165 | 0.489 | 0.0593 | +0.0117 [+0.0074, +0.0162] | +0.0017 [-0.0031, +0.0067] | 0.845 | 0.152 | no |
| 3 | 0.366 (147 of 1871 days never flag) | 48 | 0.188 | 0.542 | 0.0615 | +0.0092 [+0.0039, +0.0144] | +0.0029 [-0.0028, +0.0085] | 0.815 | 0.176 | no |
| 4 | 0.501 (147 of 1870 days never flag) | 47 | 0.174 | 0.511 | 0.0609 | +0.0100 [+0.0058, +0.0141] | +0.0015 [-0.0034, +0.0065] | 0.825 | 0.161 | no |
| 5 | 0.167 (147 of 1869 days never flag) | 98 | 0.268 | 0.378 | 0.0615 | +0.0094 [+0.0051, +0.0134] | +0.0019 [-0.0031, +0.0064] | 0.808 | 0.233 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.609 (climatology 0.457, difference +0.1518 [+0.0254, +0.2581]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0239, +0.0487], realised minus predicted +0.0373 [+0.0055, +0.0727]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.539 | 0.1790 | 0.2720 | +0.0380 [+0.0208, +0.0552] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0819 | 0.0159 | +0.0229 [+0.0066, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0098 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0210 | 0.0200 | +0.0043 [-0.0003, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0718 | 0.1165 | +0.0260 [+0.0051, +0.0527] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0136 | 0.0048 | +0.0088 [+0.0068, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0389 | 0.0031 | +0.0267 [+0.0206, +0.0323] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1285 | 0.4146 | 0.0613 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.526 | 0.1822 | 0.2474 | +0.0368 [+0.0200, +0.0542] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1069 | 0.1133 | +0.0313 [+0.0047, +0.0594] |
| day_type | ordinary | 1602 | 101 | 0.485 | 0.476 | 0.0495 | 0.0630 | +0.0146 [+0.0105, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3539 | 0.2903 | +0.0936 [+0.0187, +0.1676] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.600 | 0.1313 | 0.1444 | +0.0758 [+0.0450, +0.1129] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2197 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.115 | 1.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.136 (105 of 1873 days never flag) | 91 | 0.314 | 0.484 | 0.0597 | +0.0117 [+0.0069, +0.0163] | -0.0034 [-0.0117, +0.0041] | 0.643 | 0.287 | no |
| 2 | 0.327 (147 of 1872 days never flag) | 50 | 0.173 | 0.480 | 0.0672 | +0.0038 [-0.0027, +0.0097] | -0.0062 [-0.0146, +0.0009] | 0.579 | 0.158 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 49 | 0.167 | 0.469 | 0.0684 | +0.0023 [-0.0050, +0.0084] | -0.0040 [-0.0124, +0.0027] | 0.579 | 0.152 | no |
| 4 | 0.359 (147 of 1870 days never flag) | 55 | 0.188 | 0.473 | 0.0687 | +0.0021 [-0.0045, +0.0081] | -0.0063 [-0.0142, +0.0010] | 0.578 | 0.172 | no |
| 5 | 0.429 (147 of 1869 days never flag) | 58 | 0.203 | 0.483 | 0.0687 | +0.0023 [-0.0046, +0.0085] | -0.0053 [-0.0131, +0.0019] | 0.577 | 0.186 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [-0.0214, +0.2463]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1058, ΔBrier vs climatology +0.0237 [+0.0138, +0.0338], realised minus predicted +0.0782 [+0.0437, +0.1154]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1082 | 0.2720 | -0.0025 [-0.0225, +0.0168] |
| regime | 2020 | 251 | 4 | 0.250 | 0.053 | 0.0304 | 0.0159 | +0.0292 [+0.0195, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0026 | 0.0200 | +0.0039 [+0.0002, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0310 | 0.1165 | +0.0169 [+0.0042, +0.0339] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0099 | 0.0031 | +0.0277 [+0.0215, +0.0331] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0421 | 0.4146 | 0.0149 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.520 | 0.1065 | 0.2474 | +0.0055 [-0.0116, +0.0228] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1001 | 0.1133 | +0.0348 [+0.0091, +0.0598] |
| day_type | ordinary | 1602 | 101 | 0.158 | 0.471 | 0.0123 | 0.0630 | +0.0046 [-0.0005, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3178 | 0.2903 | +0.0970 [+0.0420, +0.1529] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.529 | 0.1350 | 0.1444 | +0.0688 [+0.0365, +0.1084] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2052 | 0.2213 |

## risk_logistic_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.259, 0.593] | 0.192 | 2.31 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.548] | 0.192 | 2.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.337 (147 of 1873 days never flag) | 97 | 0.386 | 0.557 | 0.0498 | +0.0216 [+0.0143, +0.0296] | +0.0065 [+0.0017, +0.0119] | 0.887 | 0.361 | no |
| 2 | 0.381 (147 of 1872 days never flag) | 73 | 0.252 | 0.479 | 0.0587 | +0.0124 [+0.0072, +0.0182] | +0.0023 [-0.0016, +0.0071] | 0.841 | 0.230 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 79 | 0.268 | 0.468 | 0.0623 | +0.0084 [+0.0026, +0.0143] | +0.0021 [-0.0032, +0.0076] | 0.812 | 0.244 | no |
| 4 | 0.359 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0612 | +0.0096 [+0.0039, +0.0157] | +0.0011 [-0.0042, +0.0067] | 0.818 | 0.217 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 105 | 0.326 | 0.429 | 0.0620 | +0.0089 [+0.0039, +0.0138] | +0.0014 [-0.0028, +0.0058] | 0.797 | 0.291 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0169, +0.2528]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0871, ΔBrier vs climatology +0.0424 [+0.0269, +0.0592], realised minus predicted -0.0014 [-0.0318, +0.0313]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.402 | 0.651 | 0.2496 | 0.2720 | +0.0533 [+0.0255, +0.0823] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1330 | 0.0159 | +0.0129 [-0.0019, +0.0259] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0188 | 0.0000 | +0.0132 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0327 | 0.0200 | +0.0009 [-0.0055, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.1071 | 0.1165 | +0.0288 [+0.0042, +0.0593] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0221 | 0.0048 | +0.0082 [+0.0061, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0744 | 0.0031 | +0.0203 [+0.0141, +0.0259] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.2264 | 0.4146 | +0.0843 [-0.0048, +0.1738] |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.590 | 0.2528 | 0.2474 | +0.0465 [+0.0213, +0.0735] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1094 | 0.1133 | +0.0400 [+0.0139, +0.0689] |
| day_type | ordinary | 1602 | 101 | 0.307 | 0.484 | 0.0858 | 0.0630 | +0.0158 [+0.0089, +0.0234] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3178 | 0.2903 | +0.0970 [+0.0455, +0.1510] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.692 | 0.1350 | 0.1444 | +0.0688 [+0.0363, +0.1057] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3431 | 0.2213 |

## risk_logistic_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.714] | 0.231 | 2.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.337 (105 of 1873 days never flag) | 95 | 0.350 | 0.516 | 0.0517 | +0.0198 [+0.0131, +0.0269] | +0.0047 [+0.0003, +0.0094] | 0.803 | 0.323 | no |
| 2 | 0.381 (147 of 1872 days never flag) | 73 | 0.252 | 0.479 | 0.0610 | +0.0101 [+0.0047, +0.0160] | +0.0001 [-0.0046, +0.0051] | 0.752 | 0.230 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 79 | 0.268 | 0.468 | 0.0623 | +0.0084 [+0.0021, +0.0147] | +0.0021 [-0.0036, +0.0078] | 0.748 | 0.244 | no |
| 4 | 0.359 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0621 | +0.0087 [+0.0030, +0.0146] | +0.0003 [-0.0050, +0.0056] | 0.758 | 0.217 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 138 | 0.457 | 0.457 | 0.0626 | +0.0083 [+0.0027, +0.0136] | +0.0008 [-0.0038, +0.0054] | 0.744 | 0.413 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.457, difference +0.1421 [+0.0012, +0.2594]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0890, ΔBrier vs climatology +0.0405 [+0.0257, +0.0564], realised minus predicted +0.0478 [+0.0201, +0.0776]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.581 | 0.1799 | 0.2720 | +0.0376 [+0.0122, +0.0659] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0380 | 0.0159 | +0.0219 [+0.0044, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0150 | 0.0200 | +0.0010 [-0.0059, +0.0058] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0822 | 0.1165 | +0.0280 [+0.0033, +0.0559] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0081 | 0.0048 | +0.0084 [+0.0062, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0149 | 0.0031 | +0.0263 [+0.0196, +0.0322] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.1975 | 0.4146 | +0.0822 [-0.0031, +0.1681] |
| scarcity_state | 3 | 473 | 117 | 0.376 | 0.543 | 0.1752 | 0.2474 | +0.0347 [+0.0121, +0.0592] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1039 | 0.1133 | +0.0405 [+0.0144, +0.0668] |
| day_type | ordinary | 1602 | 101 | 0.248 | 0.424 | 0.0416 | 0.0630 | +0.0136 [+0.0073, +0.0204] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3178 | 0.2903 | +0.0970 [+0.0450, +0.1503] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.692 | 0.1350 | 0.1444 | +0.0688 [+0.0376, +0.1072] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3872 | 0.2213 |

## risk_logistic_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.679] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.562] | 0.192 | 1.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.337 (126 of 1873 days never flag) | 94 | 0.343 | 0.511 | 0.0499 | +0.0215 [+0.0152, +0.0284] | +0.0064 [+0.0019, +0.0115] | 0.882 | 0.316 | no |
| 2 | 0.327 (147 of 1872 days never flag) | 82 | 0.295 | 0.500 | 0.0576 | +0.0134 [+0.0089, +0.0183] | +0.0034 [-0.0007, +0.0079] | 0.831 | 0.271 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 67 | 0.254 | 0.522 | 0.0605 | +0.0102 [+0.0051, +0.0158] | +0.0038 [-0.0013, +0.0099] | 0.806 | 0.235 | no |
| 4 | 0.359 (147 of 1870 days never flag) | 89 | 0.304 | 0.472 | 0.0597 | +0.0111 [+0.0065, +0.0160] | +0.0027 [-0.0023, +0.0078] | 0.814 | 0.277 | no |
| 5 | 0.429 (147 of 1869 days never flag) | 75 | 0.290 | 0.533 | 0.0602 | +0.0108 [+0.0065, +0.0149] | +0.0032 [-0.0011, +0.0074] | 0.795 | 0.270 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.457, difference +0.1424 [+0.0193, +0.2505]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0880, ΔBrier vs climatology +0.0415 [+0.0268, +0.0573], realised minus predicted +0.0083 [-0.0225, +0.0424]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.343 | 0.522 | 0.2326 | 0.2720 | +0.0476 [+0.0230, +0.0730] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1221 | 0.0159 | +0.0184 [+0.0080, +0.0282] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0133 [+0.0116, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0238 | 0.0200 | +0.0031 [-0.0009, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.647 | 0.0913 | 0.1165 | +0.0283 [+0.0058, +0.0562] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0176 | 0.0048 | +0.0089 [+0.0072, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0659 | 0.0031 | +0.0223 [+0.0170, +0.0279] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.571 | 0.1865 | 0.4146 | 0.0739 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.368 | 0.512 | 0.2351 | 0.2474 | +0.0440 [+0.0224, +0.0666] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1080 | 0.1133 | +0.0391 [+0.0141, +0.0669] |
| day_type | ordinary | 1602 | 101 | 0.238 | 0.407 | 0.0750 | 0.0630 | +0.0157 [+0.0098, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3178 | 0.2903 | +0.0970 [+0.0403, +0.1507] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.692 | 0.1350 | 0.1444 | +0.0688 [+0.0361, +0.1048] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2535 | 0.2213 |

## risk_logistic_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.600] | 0.192 | 2.23 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.546] | 0.192 | 2.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.337 (147 of 1873 days never flag) | 96 | 0.386 | 0.562 | 0.0491 | +0.0223 [+0.0155, +0.0301] | +0.0072 [+0.0023, +0.0124] | 0.909 | 0.361 | no |
| 2 | 0.381 (147 of 1872 days never flag) | 74 | 0.266 | 0.500 | 0.0580 | +0.0131 [+0.0080, +0.0185] | +0.0031 [-0.0010, +0.0077] | 0.879 | 0.245 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 77 | 0.268 | 0.481 | 0.0605 | +0.0101 [+0.0047, +0.0161] | +0.0038 [-0.0015, +0.0093] | 0.863 | 0.245 | no |
| 4 | 0.359 (147 of 1870 days never flag) | 69 | 0.239 | 0.478 | 0.0600 | +0.0109 [+0.0054, +0.0165] | +0.0024 [-0.0027, +0.0077] | 0.862 | 0.218 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 103 | 0.326 | 0.437 | 0.0610 | +0.0099 [+0.0048, +0.0148] | +0.0024 [-0.0018, +0.0070] | 0.851 | 0.293 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.601 (climatology 0.457, difference +0.1442 [+0.0195, +0.2564]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0288, +0.0607], realised minus predicted +0.0248 [-0.0063, +0.0581]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.402 | 0.651 | 0.2496 | 0.2720 | +0.0533 [+0.0264, +0.0821] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1330 | 0.0159 | +0.0129 [-0.0025, +0.0255] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0046 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0026 | 0.0200 | +0.0039 [+0.0001, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0936 | 0.1165 | +0.0297 [+0.0051, +0.0624] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0744 | 0.0031 | +0.0203 [+0.0141, +0.0260] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.444 | 0.2264 | 0.4146 | 0.0843 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.419 | 0.590 | 0.2528 | 0.2474 | +0.0465 [+0.0234, +0.0733] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1074 | 0.1133 | +0.0401 [+0.0144, +0.0670] |
| day_type | ordinary | 1602 | 101 | 0.307 | 0.492 | 0.0726 | 0.0630 | +0.0166 [+0.0101, +0.0243] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3178 | 0.2903 | +0.0970 [+0.0396, +0.1527] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.692 | 0.1350 | 0.1444 | +0.0688 [+0.0366, +0.1061] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3431 | 0.2213 |

## risk_logistic_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 2.50 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.524] | 0.115 | 1.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.337 (126 of 1873 days never flag) | 141 | 0.543 | 0.539 | 0.0504 | +0.0211 [+0.0163, +0.0264] | +0.0060 [+0.0014, +0.0107] | 0.899 | 0.505 | no |
| 2 | 0.327 (147 of 1872 days never flag) | 49 | 0.173 | 0.490 | 0.0590 | +0.0121 [+0.0081, +0.0165] | +0.0021 [-0.0025, +0.0067] | 0.846 | 0.158 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 63 | 0.225 | 0.492 | 0.0615 | +0.0092 [+0.0043, +0.0141] | +0.0029 [-0.0028, +0.0085] | 0.815 | 0.206 | no |
| 4 | 0.359 (147 of 1870 days never flag) | 47 | 0.159 | 0.468 | 0.0611 | +0.0098 [+0.0053, +0.0141] | +0.0013 [-0.0041, +0.0064] | 0.825 | 0.145 | no |
| 5 | 0.429 (147 of 1869 days never flag) | 67 | 0.232 | 0.478 | 0.0614 | +0.0095 [+0.0053, +0.0135] | +0.0020 [-0.0027, +0.0063] | 0.806 | 0.212 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.589 (climatology 0.457, difference +0.1317 [+0.0089, +0.2280]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0919, ΔBrier vs climatology +0.0376 [+0.0251, +0.0505], realised minus predicted +0.0397 [+0.0079, +0.0734]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.552 | 0.1789 | 0.2720 | +0.0387 [+0.0238, +0.0560] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0817 | 0.0159 | +0.0261 [+0.0169, +0.0351] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0095 | 0.0000 | +0.0137 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0176 | 0.0200 | +0.0032 [-0.0012, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0690 | 0.1165 | +0.0294 [+0.0087, +0.0566] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0118 | 0.0048 | +0.0091 [+0.0073, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0422 | 0.0031 | +0.0258 [+0.0202, +0.0312] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.1343 | 0.4146 | +0.0709 [+0.0126, +0.1381] |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.541 | 0.1797 | 0.2474 | +0.0396 [+0.0248, +0.0559] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1048 | 0.1133 | +0.0378 [+0.0117, +0.0654] |
| day_type | ordinary | 1602 | 101 | 0.485 | 0.500 | 0.0491 | 0.0630 | +0.0153 [+0.0114, +0.0201] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3178 | 0.2903 | +0.0970 [+0.0419, +0.1523] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.600 | 0.1350 | 0.1444 | +0.0688 [+0.0361, +0.1064] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2223 | 0.2213 |

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.231 | 2.73 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 2.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.148 (42 of 1873 days never flag) | 107 | 0.321 | 0.421 | 0.0631 | +0.0083 [+0.0027, +0.0142] | -0.0068 [-0.0151, +0.0009] | 0.646 | 0.286 | no |
| 2 | 0.283 (126 of 1872 days never flag) | 68 | 0.209 | 0.426 | 0.0674 | +0.0036 [-0.0036, +0.0107] | -0.0064 [-0.0148, +0.0015] | 0.578 | 0.186 | no |
| 3 | 0.184 (126 of 1871 days never flag) | 73 | 0.203 | 0.384 | 0.0663 | +0.0044 [-0.0027, +0.0110] | -0.0020 [-0.0096, +0.0052] | 0.581 | 0.177 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 99 | 0.203 | 0.283 | 0.0670 | +0.0038 [-0.0025, +0.0097] | -0.0047 [-0.0121, +0.0018] | 0.579 | 0.162 | no |
| 5 | 0.302 (126 of 1869 days never flag) | 77 | 0.188 | 0.338 | 0.0672 | +0.0037 [-0.0030, +0.0098] | -0.0038 [-0.0114, +0.0032] | 0.580 | 0.159 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 4.6 over 1035 days; regime_2021-23: 5.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 2.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.457, difference +0.1837 [+0.0683, +0.2976]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1118, ΔBrier vs climatology +0.0177 [+0.0072, +0.0290], realised minus predicted +0.0586 [+0.0246, +0.0958]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.588 | 0.0990 | 0.2720 | -0.0069 [-0.0287, +0.0153] |
| regime | 2020 | 251 | 4 | 0.250 | 0.030 | 0.0628 | 0.0159 | +0.0061 [-0.0087, +0.0206] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0110 | 0.0200 | +0.0019 [-0.0032, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.650 | 0.0482 | 0.1165 | +0.0240 [+0.0055, +0.0480] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.200 | 0.0056 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.040 | 0.0345 | 0.0031 | +0.0128 [+0.0032, +0.0220] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.1151 | 0.4146 | 0.0759 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.542 | 0.1015 | 0.2474 | -0.0014 [-0.0200, +0.0182] |
| day_type | month_end | 150 | 17 | 0.765 | 0.419 | 0.1213 | 0.1133 | +0.0267 [-0.0077, +0.0602] |
| day_type | ordinary | 1602 | 101 | 0.158 | 0.410 | 0.0148 | 0.0630 | +0.0013 [-0.0042, +0.0064] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3576 | 0.2903 | +0.1032 [+0.0177, +0.1911] |
| day_type | tax_date | 90 | 13 | 0.769 | 0.417 | 0.1854 | 0.1444 | +0.0708 [+0.0331, +0.1131] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4005 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.542] | 0.154 | 1.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.304 (105 of 1873 days never flag) | 92 | 0.321 | 0.489 | 0.0630 | +0.0084 [+0.0020, +0.0146] | -0.0067 [-0.0154, +0.0017] | 0.635 | 0.294 | no |
| 2 | 0.402 (147 of 1872 days never flag) | 72 | 0.216 | 0.417 | 0.0689 | +0.0021 [-0.0058, +0.0092] | -0.0079 [-0.0171, -0.0004] | 0.582 | 0.192 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 68 | 0.217 | 0.441 | 0.0672 | +0.0035 [-0.0039, +0.0103] | -0.0028 [-0.0110, +0.0045] | 0.585 | 0.195 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0668 | +0.0040 [-0.0034, +0.0111] | -0.0044 [-0.0127, +0.0034] | 0.584 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 53 | 0.188 | 0.491 | 0.0670 | +0.0039 [-0.0029, +0.0107] | -0.0036 [-0.0121, +0.0040] | 0.584 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.593 (climatology 0.457, difference +0.1355 [-0.0383, +0.2815]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1059, ΔBrier vs climatology +0.0236 [+0.0116, +0.0364], realised minus predicted +0.0564 [+0.0222, +0.0911]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.620 | 0.1198 | 0.2720 | -0.0165 [-0.0411, +0.0093] |
| regime | 2020 | 251 | 4 | 0.250 | 0.042 | 0.0472 | 0.0159 | +0.0211 [+0.0107, +0.0308] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0119 | 0.0200 | +0.0015 [-0.0049, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.750 | 0.0510 | 0.1165 | +0.0245 [+0.0053, +0.0468] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0272 | 0.0031 | +0.0192 [+0.0114, +0.0261] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0956 | 0.4146 | 0.0535 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.588 | 0.1179 | 0.2474 | -0.0033 [-0.0258, +0.0197] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1402 | 0.1133 | +0.0244 [-0.0128, +0.0624] |
| day_type | ordinary | 1602 | 101 | 0.168 | 0.500 | 0.0159 | 0.0630 | +0.0027 [-0.0029, +0.0082] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3243 | 0.2903 | +0.0714 [-0.0019, +0.1359] |
| day_type | tax_date | 90 | 13 | 0.692 | 0.409 | 0.2008 | 0.1444 | +0.0609 [+0.0219, +0.1025] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.409, 0.750] | 0.192 | 2.46 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.192 | 2.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.477 (105 of 1873 days never flag) | 110 | 0.450 | 0.573 | 0.0531 | +0.0183 [+0.0098, +0.0273] | +0.0033 [-0.0028, +0.0092] | 0.881 | 0.423 | no |
| 2 | 0.402 (189 of 1872 days never flag) | 66 | 0.223 | 0.470 | 0.0604 | +0.0107 [+0.0045, +0.0171] | +0.0006 [-0.0042, +0.0055] | 0.845 | 0.203 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 98 | 0.333 | 0.469 | 0.0611 | +0.0096 [+0.0040, +0.0158] | +0.0033 [-0.0019, +0.0086] | 0.839 | 0.303 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 112 | 0.399 | 0.491 | 0.0594 | +0.0115 [+0.0052, +0.0182] | +0.0030 [-0.0023, +0.0090] | 0.849 | 0.366 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 113 | 0.355 | 0.434 | 0.0603 | +0.0106 [+0.0046, +0.0168] | +0.0031 [-0.0021, +0.0087] | 0.839 | 0.318 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.457, difference +0.1799 [+0.0322, +0.3287]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0876, ΔBrier vs climatology +0.0419 [+0.0250, +0.0609], realised minus predicted -0.0182 [-0.0483, +0.0136]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.620 | 0.2613 | 0.2720 | +0.0393 [+0.0081, +0.0717] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1498 | 0.0159 | +0.0048 [-0.0090, +0.0172] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0215 | 0.0000 | +0.0130 [+0.0112, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0419 | 0.0200 | -0.0015 [-0.0086, +0.0039] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1271 | 0.1165 | +0.0364 [+0.0037, +0.0762] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0267 | 0.0048 | +0.0074 [+0.0051, +0.0095] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0917 | 0.0031 | +0.0118 [+0.0034, +0.0189] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2798 | 0.4146 | +0.1228 [-0.0069, +0.2478] |
| scarcity_state | 3 | 473 | 117 | 0.479 | 0.602 | 0.2642 | 0.2474 | +0.0377 [+0.0095, +0.0659] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1495 | 0.1133 | +0.0295 [-0.0090, +0.0689] |
| day_type | ordinary | 1602 | 101 | 0.376 | 0.521 | 0.0894 | 0.0630 | +0.0139 [+0.0065, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3243 | 0.2903 | +0.0714 [-0.0031, +0.1375] |
| day_type | tax_date | 90 | 13 | 0.615 | 0.615 | 0.2008 | 0.1444 | +0.0609 [+0.0220, +0.1068] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.741] | 0.231 | 3.15 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.231 | 3.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.477 (105 of 1873 days never flag) | 119 | 0.421 | 0.496 | 0.0549 | +0.0165 [+0.0089, +0.0247] | +0.0014 [-0.0046, +0.0075] | 0.793 | 0.387 | no |
| 2 | 0.402 (189 of 1872 days never flag) | 66 | 0.223 | 0.470 | 0.0627 | +0.0084 [+0.0019, +0.0152] | -0.0016 [-0.0068, +0.0037] | 0.753 | 0.203 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 95 | 0.319 | 0.463 | 0.0611 | +0.0096 [+0.0031, +0.0157] | +0.0032 [-0.0025, +0.0088] | 0.755 | 0.289 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 110 | 0.391 | 0.491 | 0.0602 | +0.0106 [+0.0043, +0.0169] | +0.0022 [-0.0031, +0.0074] | 0.767 | 0.359 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 152 | 0.507 | 0.461 | 0.0610 | +0.0100 [+0.0038, +0.0165] | +0.0024 [-0.0030, +0.0078] | 0.753 | 0.460 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.457, difference +0.1527 [-0.0067, +0.3022]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0235, +0.0578], realised minus predicted +0.0273 [-0.0000, +0.0555]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.529 | 0.1916 | 0.2720 | +0.0236 [-0.0053, +0.0536] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0548 | 0.0159 | +0.0139 [-0.0024, +0.0287] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0067 | 0.0000 | +0.0134 [+0.0116, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0243 | 0.0200 | -0.0014 [-0.0092, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1022 | 0.1165 | +0.0356 [+0.0045, +0.0722] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0127 | 0.0048 | +0.0076 [+0.0052, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0322 | 0.0031 | +0.0178 [+0.0094, +0.0249] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2509 | 0.4146 | +0.1208 [-0.0095, +0.2455] |
| scarcity_state | 3 | 473 | 117 | 0.444 | 0.525 | 0.1866 | 0.2474 | +0.0259 [+0.0008, +0.0519] |
| day_type | month_end | 150 | 17 | 0.706 | 0.667 | 0.1440 | 0.1133 | +0.0301 [-0.0077, +0.0702] |
| day_type | ordinary | 1602 | 101 | 0.327 | 0.434 | 0.0452 | 0.0630 | +0.0117 [+0.0051, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3243 | 0.2903 | +0.0714 [+0.0014, +0.1383] |
| day_type | tax_date | 90 | 13 | 0.615 | 0.471 | 0.2008 | 0.1444 | +0.0609 [+0.0212, +0.1030] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.706] | 0.231 | 2.85 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.231 | 2.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.477 (105 of 1873 days never flag) | 118 | 0.414 | 0.492 | 0.0534 | +0.0181 [+0.0110, +0.0259] | +0.0030 [-0.0027, +0.0089] | 0.866 | 0.380 | no |
| 2 | 0.402 (168 of 1872 days never flag) | 71 | 0.273 | 0.535 | 0.0594 | +0.0116 [+0.0060, +0.0180] | +0.0016 [-0.0031, +0.0066] | 0.825 | 0.254 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 120 | 0.420 | 0.483 | 0.0594 | +0.0113 [+0.0057, +0.0177] | +0.0049 [-0.0006, +0.0111] | 0.831 | 0.385 | no |
| 4 | 0.3 (126 of 1870 days never flag) | 141 | 0.486 | 0.475 | 0.0575 | +0.0133 [+0.0078, +0.0196] | +0.0049 [-0.0003, +0.0108] | 0.846 | 0.443 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 100 | 0.348 | 0.480 | 0.0583 | +0.0127 [+0.0070, +0.0186] | +0.0051 [-0.0005, +0.0108] | 0.841 | 0.318 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.640 (climatology 0.457, difference +0.1824 [+0.0246, +0.3155]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0884, ΔBrier vs climatology +0.0411 [+0.0245, +0.0577], realised minus predicted -0.0095 [-0.0402, +0.0210]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.500 | 0.2424 | 0.2720 | +0.0325 [+0.0030, +0.0629] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1403 | 0.0159 | +0.0101 [-0.0005, +0.0200] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0131 [+0.0115, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0339 | 0.0200 | +0.0008 [-0.0048, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.706 | 0.1117 | 0.1165 | +0.0365 [+0.0076, +0.0733] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0226 | 0.0048 | +0.0081 [+0.0063, +0.0099] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0842 | 0.0031 | +0.0136 [+0.0057, +0.0203] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.750 | 0.2412 | 0.4146 | +0.1165 [-0.0026, +0.2256] |
| scarcity_state | 3 | 473 | 117 | 0.436 | 0.505 | 0.2449 | 0.2474 | +0.0344 [+0.0090, +0.0606] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1465 | 0.1133 | +0.0259 [-0.0110, +0.0646] |
| day_type | ordinary | 1602 | 101 | 0.327 | 0.429 | 0.0788 | 0.0630 | +0.0139 [+0.0074, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3243 | 0.2903 | +0.0714 [-0.0013, +0.1376] |
| day_type | tax_date | 90 | 13 | 0.615 | 0.500 | 0.2008 | 0.1444 | +0.0609 [+0.0218, +0.1081] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2483 | 0.2213 |

## risk_quantile_skewt_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.739] | 0.192 | 2.38 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.323, 0.667] | 0.192 | 2.38 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.477 (105 of 1873 days never flag) | 109 | 0.450 | 0.578 | 0.0524 | +0.0190 [+0.0109, +0.0281] | +0.0039 [-0.0020, +0.0102] | 0.900 | 0.423 | no |
| 2 | 0.402 (189 of 1872 days never flag) | 65 | 0.223 | 0.477 | 0.0597 | +0.0114 [+0.0053, +0.0183] | +0.0014 [-0.0031, +0.0063] | 0.876 | 0.203 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 97 | 0.333 | 0.474 | 0.0594 | +0.0113 [+0.0054, +0.0173] | +0.0050 [-0.0002, +0.0106] | 0.873 | 0.304 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 109 | 0.399 | 0.505 | 0.0581 | +0.0128 [+0.0064, +0.0193] | +0.0043 [-0.0013, +0.0097] | 0.878 | 0.367 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 111 | 0.355 | 0.441 | 0.0593 | +0.0116 [+0.0057, +0.0179] | +0.0041 [-0.0014, +0.0101] | 0.870 | 0.319 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.457, difference +0.1799 [+0.0268, +0.3191]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0861, ΔBrier vs climatology +0.0434 [+0.0259, +0.0617], realised minus predicted +0.0051 [-0.0235, +0.0353]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.620 | 0.2613 | 0.2720 | +0.0393 [+0.0071, +0.0702] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1498 | 0.0159 | +0.0048 [-0.0097, +0.0179] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0073 | 0.0000 | +0.0134 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0119 | 0.0200 | +0.0015 [-0.0048, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1136 | 0.1165 | +0.0373 [+0.0058, +0.0782] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0917 | 0.0031 | +0.0118 [+0.0034, +0.0188] |
| scarcity_state | 2 | 41 | 17 | 0.353 | 0.667 | 0.2798 | 0.4146 | 0.1228 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.479 | 0.602 | 0.2642 | 0.2474 | +0.0377 [+0.0106, +0.0663] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1475 | 0.1133 | +0.0296 [-0.0094, +0.0691] |
| day_type | ordinary | 1602 | 101 | 0.376 | 0.528 | 0.0762 | 0.0630 | +0.0147 [+0.0074, +0.0226] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3243 | 0.2903 | +0.0714 [+0.0005, +0.1346] |
| day_type | tax_date | 90 | 13 | 0.615 | 0.615 | 0.2008 | 0.1444 | +0.0609 [+0.0225, +0.1050] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.375, 0.722] | 0.231 | 2.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.231 | 2.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.477 (105 of 1873 days never flag) | 139 | 0.514 | 0.518 | 0.0536 | +0.0178 [+0.0118, +0.0241] | +0.0027 [-0.0032, +0.0089] | 0.880 | 0.476 | no |
| 2 | 0.402 (189 of 1872 days never flag) | 83 | 0.338 | 0.566 | 0.0607 | +0.0104 [+0.0049, +0.0157] | +0.0004 [-0.0050, +0.0056] | 0.847 | 0.317 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 120 | 0.377 | 0.433 | 0.0603 | +0.0104 [+0.0052, +0.0157] | +0.0041 [-0.0016, +0.0096] | 0.840 | 0.338 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 72 | 0.246 | 0.472 | 0.0592 | +0.0116 [+0.0063, +0.0172] | +0.0032 [-0.0024, +0.0086] | 0.846 | 0.224 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 88 | 0.275 | 0.432 | 0.0597 | +0.0112 [+0.0058, +0.0169] | +0.0037 [-0.0020, +0.0094] | 0.838 | 0.246 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.630 (climatology 0.457, difference +0.1724 [+0.0266, +0.2958]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0920, ΔBrier vs climatology +0.0375 [+0.0229, +0.0522], realised minus predicted +0.0199 [-0.0108, +0.0511]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.567 | 0.1906 | 0.2720 | +0.0248 [+0.0009, +0.0465] |
| regime | 2020 | 251 | 4 | 0.250 | 0.062 | 0.0985 | 0.0159 | +0.0181 [+0.0078, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0122 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0269 | 0.0200 | +0.0008 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.647 | 0.0891 | 0.1165 | +0.0370 [+0.0083, +0.0725] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0163 | 0.0048 | +0.0083 [+0.0064, +0.0102] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0595 | 0.0031 | +0.0173 [+0.0089, +0.0244] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.714 | 0.1877 | 0.4146 | 0.1095 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.564 | 0.559 | 0.1911 | 0.2474 | +0.0308 [+0.0108, +0.0508] |
| day_type | month_end | 150 | 17 | 0.706 | 0.571 | 0.1449 | 0.1133 | +0.0273 [-0.0109, +0.0650] |
| day_type | ordinary | 1602 | 101 | 0.455 | 0.505 | 0.0527 | 0.0630 | +0.0134 [+0.0088, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3243 | 0.2903 | +0.0714 [+0.0001, +0.1353] |
| day_type | tax_date | 90 | 13 | 0.615 | 0.471 | 0.2008 | 0.1444 | +0.0609 [+0.0209, +0.1053] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1048 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2171 | 0.2213 |

