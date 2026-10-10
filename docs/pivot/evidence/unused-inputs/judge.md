# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `20a3ed4c9a34…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## risk_gbm_base_dealer (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.394, 0.757] | 0.115 | 1.19 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.500] | 0.115 | 1.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 73 | 0.300 | 0.575 | 0.0594 | +0.0120 [+0.0069, +0.0169] | -0.0030 [-0.0110, +0.0045] | 0.642 | 0.282 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 55 | 0.194 | 0.491 | 0.0683 | +0.0028 [-0.0040, +0.0089] | -0.0072 [-0.0159, +0.0002] | 0.578 | 0.178 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 56 | 0.210 | 0.518 | 0.0662 | +0.0045 [-0.0024, +0.0104] | -0.0018 [-0.0097, +0.0050] | 0.580 | 0.195 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 52 | 0.167 | 0.442 | 0.0678 | +0.0030 [-0.0036, +0.0089] | -0.0054 [-0.0132, +0.0013] | 0.579 | 0.150 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 50 | 0.159 | 0.440 | 0.0687 | +0.0022 [-0.0042, +0.0081] | -0.0053 [-0.0130, +0.0011] | 0.576 | 0.143 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.505 (climatology 0.457, difference +0.0479 [-0.0998, +0.1745]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1046, ΔBrier vs climatology +0.0249 [+0.0155, +0.0345], realised minus predicted +0.0904 [+0.0538, +0.1292]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.612 | 0.1002 | 0.2720 | -0.0050 [-0.0243, +0.0151] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0161 | 0.0159 | +0.0351 [+0.0250, +0.0449] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0016 | 0.0200 | +0.0033 [-0.0005, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0316 | 0.1165 | +0.0179 [+0.0030, +0.0377] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0012 | 0.0048 | +0.0090 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.250 | 0.0064 | 0.0031 | +0.0317 [+0.0254, +0.0378] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0374 | 0.4146 | 0.0088 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.316 | 0.578 | 0.0957 | 0.2474 | +0.0055 [-0.0130, +0.0233] |
| day_type | month_end | 150 | 17 | 0.647 | 0.524 | 0.0981 | 0.1133 | +0.0314 [+0.0104, +0.0522] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.556 | 0.0121 | 0.0630 | +0.0048 [-0.0002, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.1952 | 0.2903 | +0.0928 [+0.0080, +0.1818] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.625 | 0.1118 | 0.1461 | +0.0818 [+0.0550, +0.1089] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4373 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2557 | 0.2213 |

## risk_gbm_base_policy (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.714] | 0.115 | 1.19 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.115 | 1.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 73 | 0.300 | 0.575 | 0.0587 | +0.0127 [+0.0074, +0.0181] | -0.0024 [-0.0106, +0.0050] | 0.643 | 0.282 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 44 | 0.165 | 0.523 | 0.0684 | +0.0027 [-0.0039, +0.0087] | -0.0073 [-0.0154, +0.0002] | 0.578 | 0.153 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 51 | 0.181 | 0.490 | 0.0672 | +0.0035 [-0.0033, +0.0094] | -0.0028 [-0.0105, +0.0038] | 0.580 | 0.166 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 47 | 0.181 | 0.532 | 0.0670 | +0.0038 [-0.0024, +0.0100] | -0.0046 [-0.0121, +0.0021] | 0.580 | 0.168 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 48 | 0.152 | 0.438 | 0.0684 | +0.0025 [-0.0040, +0.0085] | -0.0050 [-0.0127, +0.0016] | 0.577 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.520 (climatology 0.457, difference +0.0629 [-0.0857, +0.1972]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1034, ΔBrier vs climatology +0.0261 [+0.0171, +0.0351], realised minus predicted +0.0943 [+0.0590, +0.1308]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.612 | 0.0868 | 0.2720 | -0.0044 [-0.0269, +0.0165] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.0152 | 0.0159 | +0.0368 [+0.0276, +0.0455] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0019 | 0.0200 | +0.0035 [-0.0004, +0.0063] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0320 | 0.1165 | +0.0199 [+0.0050, +0.0391] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0011 | 0.0048 | +0.0093 [+0.0077, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0042 | 0.0031 | +0.0298 [+0.0228, +0.0363] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0430 | 0.4146 | 0.0132 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.325 | 0.603 | 0.0862 | 0.2474 | +0.0083 [-0.0120, +0.0281] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0895 | 0.1133 | +0.0391 [+0.0177, +0.0601] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.571 | 0.0118 | 0.0630 | +0.0051 [+0.0000, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2037 | 0.2903 | +0.1293 [+0.0579, +0.2050] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.0718 | 0.1461 | +0.0647 [+0.0378, +0.0910] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.7478 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2478 | 0.2213 |

## risk_gbm_base_settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.714] | 0.115 | 1.35 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.161, 0.462] | 0.115 | 1.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 77 | 0.300 | 0.545 | 0.0596 | +0.0118 [+0.0066, +0.0168] | -0.0032 [-0.0113, +0.0041] | 0.642 | 0.280 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 52 | 0.173 | 0.462 | 0.0693 | +0.0017 [-0.0050, +0.0076] | -0.0083 [-0.0167, -0.0008] | 0.577 | 0.157 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 54 | 0.174 | 0.444 | 0.0686 | +0.0021 [-0.0045, +0.0081] | -0.0042 [-0.0122, +0.0029] | 0.579 | 0.157 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 54 | 0.174 | 0.444 | 0.0676 | +0.0032 [-0.0034, +0.0089] | -0.0053 [-0.0130, +0.0014] | 0.579 | 0.157 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 53 | 0.167 | 0.434 | 0.0678 | +0.0032 [-0.0035, +0.0086] | -0.0044 [-0.0123, +0.0019] | 0.577 | 0.149 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.532 (climatology 0.457, difference +0.0748 [-0.0537, +0.1995]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0221 [+0.0129, +0.0321], realised minus predicted +0.0891 [+0.0546, +0.1272]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0990 | 0.2720 | -0.0009 [-0.0205, +0.0168] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.0275 | 0.0159 | +0.0316 [+0.0192, +0.0426] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0002 | 0.0200 | +0.0010 [-0.0044, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0323 | 0.1165 | +0.0161 [+0.0005, +0.0366] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0008 | 0.0048 | +0.0085 [+0.0064, +0.0103] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0077 | 0.0031 | +0.0286 [+0.0226, +0.0348] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0270 | 0.4146 | -0.0026 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.565 | 0.1012 | 0.2474 | +0.0090 [-0.0100, +0.0263] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.1012 | 0.1133 | +0.0335 [+0.0100, +0.0567] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.533 | 0.0123 | 0.0630 | +0.0050 [-0.0001, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2158 | 0.2903 | +0.0833 [+0.0020, +0.1634] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1205 | 0.1461 | +0.0731 [+0.0516, +0.0962] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4656 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2008 | 0.2213 |

## risk_gbm_dealer (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.115 | 1.12 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.435] | 0.115 | 1.00 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 71 | 0.300 | 0.592 | 0.0585 | +0.0130 [+0.0075, +0.0182] | -0.0021 [-0.0107, +0.0054] | 0.642 | 0.283 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 53 | 0.173 | 0.453 | 0.0681 | +0.0030 [-0.0034, +0.0086] | -0.0070 [-0.0151, +0.0003] | 0.578 | 0.156 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 51 | 0.188 | 0.510 | 0.0670 | +0.0037 [-0.0032, +0.0096] | -0.0026 [-0.0105, +0.0040] | 0.579 | 0.174 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 46 | 0.174 | 0.522 | 0.0672 | +0.0037 [-0.0032, +0.0097] | -0.0048 [-0.0128, +0.0019] | 0.579 | 0.161 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 48 | 0.159 | 0.458 | 0.0695 | +0.0015 [-0.0053, +0.0077] | -0.0061 [-0.0138, +0.0011] | 0.577 | 0.144 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.501 (climatology 0.457, difference +0.0435 [-0.1107, +0.1696]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1037, ΔBrier vs climatology +0.0257 [+0.0162, +0.0353], realised minus predicted +0.0947 [+0.0587, +0.1339]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.620 | 0.0938 | 0.2720 | -0.0024 [-0.0244, +0.0181] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0146 | 0.0159 | +0.0398 [+0.0317, +0.0483] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0031 | 0.0200 | +0.0045 [+0.0005, +0.0087] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0319 | 0.1165 | +0.0151 [+0.0003, +0.0365] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0017 | 0.0048 | +0.0094 [+0.0076, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0036 | 0.0031 | +0.0300 [+0.0230, +0.0366] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0358 | 0.4146 | +0.0017 [-0.0253, +0.0384] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.609 | 0.0921 | 0.2474 | +0.0101 [-0.0102, +0.0299] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0978 | 0.1133 | +0.0446 [+0.0239, +0.0657] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.577 | 0.0117 | 0.0630 | +0.0045 [-0.0011, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2129 | 0.2903 | +0.1286 [+0.0517, +0.2108] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.0898 | 0.1461 | +0.0710 [+0.0471, +0.0949] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6765 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2041 | 0.2213 |

## risk_gbm_policy (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.677] | 0.115 | 1.12 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.130, 0.423] | 0.115 | 1.00 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 68 | 0.286 | 0.588 | 0.0578 | +0.0136 [+0.0076, +0.0191] | -0.0014 [-0.0101, +0.0062] | 0.642 | 0.270 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 54 | 0.180 | 0.463 | 0.0683 | +0.0028 [-0.0042, +0.0085] | -0.0072 [-0.0161, -0.0000] | 0.578 | 0.163 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 52 | 0.203 | 0.538 | 0.0670 | +0.0037 [-0.0033, +0.0097] | -0.0026 [-0.0107, +0.0037] | 0.580 | 0.189 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 46 | 0.188 | 0.565 | 0.0671 | +0.0038 [-0.0029, +0.0099] | -0.0047 [-0.0121, +0.0022] | 0.579 | 0.177 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 47 | 0.152 | 0.447 | 0.0693 | +0.0016 [-0.0050, +0.0078] | -0.0059 [-0.0136, +0.0011] | 0.578 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.504 (climatology 0.457, difference +0.0472 [-0.0950, +0.1776]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1036, ΔBrier vs climatology +0.0259 [+0.0165, +0.0357], realised minus predicted +0.0944 [+0.0588, +0.1313]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.275 | 0.609 | 0.0915 | 0.2720 | -0.0001 [-0.0239, +0.0219] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0127 | 0.0159 | +0.0405 [+0.0328, +0.0486] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.400 | 1.000 | 0.0044 | 0.0200 | +0.0062 [+0.0011, +0.0126] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0317 | 0.1165 | +0.0143 [-0.0000, +0.0337] |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.500 | 0.0023 | 0.0048 | +0.0096 [+0.0077, +0.0115] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0022 | 0.0031 | +0.0301 [+0.0230, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0359 | 0.4146 | -0.0003 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.308 | 0.600 | 0.0895 | 0.2474 | +0.0125 [-0.0090, +0.0323] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0940 | 0.1133 | +0.0509 [+0.0277, +0.0732] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.577 | 0.0119 | 0.0630 | +0.0046 [-0.0008, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2256 | 0.2903 | +0.1304 [+0.0517, +0.2167] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.0760 | 0.1461 | +0.0726 [+0.0421, +0.1023] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.7523 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2014 | 0.2213 |

## risk_gbm_settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.154 | 1.54 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.161, 0.458] | 0.115 | 1.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 81 | 0.293 | 0.506 | 0.0585 | +0.0129 [+0.0075, +0.0181] | -0.0021 [-0.0107, +0.0051] | 0.642 | 0.270 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 55 | 0.173 | 0.436 | 0.0687 | +0.0024 [-0.0042, +0.0084] | -0.0076 [-0.0158, -0.0003] | 0.578 | 0.155 | no |
| 3 | 0.105 (147 of 1871 days never flag) | 54 | 0.203 | 0.519 | 0.0667 | +0.0040 [-0.0026, +0.0099] | -0.0023 [-0.0096, +0.0043] | 0.580 | 0.188 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 49 | 0.174 | 0.490 | 0.0671 | +0.0037 [-0.0025, +0.0092] | -0.0048 [-0.0122, +0.0016] | 0.579 | 0.159 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 52 | 0.152 | 0.404 | 0.0692 | +0.0017 [-0.0050, +0.0079] | -0.0058 [-0.0133, +0.0009] | 0.577 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.487 (climatology 0.457, difference +0.0304 [-0.1179, +0.1506]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1049, ΔBrier vs climatology +0.0245 [+0.0153, +0.0342], realised minus predicted +0.0906 [+0.0548, +0.1263]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.574 | 0.0991 | 0.2720 | +0.0016 [-0.0211, +0.0217] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0188 | 0.0159 | +0.0373 [+0.0277, +0.0464] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0011 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0009 | 0.0200 | +0.0012 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0432 | 0.1165 | +0.0153 [-0.0019, +0.0391] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0023 | 0.0048 | +0.0077 [+0.0055, +0.0098] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0043 | 0.0031 | +0.0294 [+0.0219, +0.0364] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0408 | 0.4146 | 0.0055 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.549 | 0.1019 | 0.2474 | +0.0137 [-0.0063, +0.0325] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.1033 | 0.1133 | +0.0542 [+0.0308, +0.0796] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0131 | 0.0630 | +0.0047 [-0.0003, +0.0093] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.455 | 0.2441 | 0.2903 | +0.0866 [+0.0015, +0.1758] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1080 | 0.1461 | +0.0661 [+0.0432, +0.0917] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.6499 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2001 | 0.2213 |

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

## risk_logistic_base_dealer (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.192 | 2.00 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.13 (105 of 1873 days never flag) | 96 | 0.314 | 0.458 | 0.0623 | +0.0091 [+0.0039, +0.0138] | -0.0060 [-0.0147, +0.0015] | 0.643 | 0.284 | no |
| 2 | 0.302 (147 of 1872 days never flag) | 65 | 0.187 | 0.400 | 0.0699 | +0.0012 [-0.0054, +0.0071] | -0.0088 [-0.0168, -0.0016] | 0.578 | 0.165 | no |
| 3 | 0.162 (147 of 1871 days never flag) | 59 | 0.210 | 0.492 | 0.0697 | +0.0010 [-0.0064, +0.0076] | -0.0053 [-0.0131, +0.0021] | 0.579 | 0.193 | no |
| 4 | 0.0493 (147 of 1870 days never flag) | 70 | 0.196 | 0.386 | 0.0702 | +0.0006 [-0.0061, +0.0067] | -0.0078 [-0.0158, -0.0008] | 0.578 | 0.171 | no |
| 5 | 0.352 (147 of 1869 days never flag) | 62 | 0.174 | 0.387 | 0.0701 | +0.0009 [-0.0063, +0.0074] | -0.0067 [-0.0148, +0.0005] | 0.578 | 0.152 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.576 (climatology 0.457, difference +0.1186 [-0.0325, +0.2563]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1086, ΔBrier vs climatology +0.0209 [+0.0101, +0.0317], realised minus predicted +0.0728 [+0.0382, +0.1093]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.577 | 0.1073 | 0.2720 | -0.0065 [-0.0269, +0.0111] |
| regime | 2020 | 251 | 4 | 0.250 | 0.040 | 0.0461 | 0.0159 | +0.0170 [+0.0046, +0.0279] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0002 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0038 | 0.0200 | +0.0046 [+0.0004, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.667 | 0.0487 | 0.1165 | +0.0149 [-0.0006, +0.0345] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0029 | 0.0048 | +0.0086 [+0.0065, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0239 | 0.0031 | +0.0172 [+0.0086, +0.0245] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0569 | 0.4146 | 0.0312 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.549 | 0.1098 | 0.2474 | +0.0025 [-0.0155, +0.0196] |
| day_type | month_end | 150 | 17 | 0.647 | 0.407 | 0.1101 | 0.1133 | +0.0210 [-0.0058, +0.0489] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.500 | 0.0134 | 0.0630 | +0.0045 [-0.0006, +0.0090] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3725 | 0.2903 | +0.0835 [+0.0076, +0.1591] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.450 | 0.1744 | 0.1461 | +0.0448 [+0.0010, +0.0870] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4003 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_logistic_base_policy (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.719] | 0.192 | 1.77 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.464] | 0.115 | 1.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0429 (105 of 1873 days never flag) | 91 | 0.321 | 0.495 | 0.0606 | +0.0108 [+0.0052, +0.0161] | -0.0043 [-0.0122, +0.0026] | 0.643 | 0.295 | no |
| 2 | 0.029 (147 of 1872 days never flag) | 59 | 0.201 | 0.475 | 0.0662 | +0.0048 [-0.0026, +0.0110] | -0.0052 [-0.0138, +0.0018] | 0.579 | 0.184 | no |
| 3 | 0.169 (147 of 1871 days never flag) | 60 | 0.203 | 0.467 | 0.0659 | +0.0048 [-0.0019, +0.0111] | -0.0015 [-0.0090, +0.0053] | 0.580 | 0.184 | no |
| 4 | 0.155 (147 of 1870 days never flag) | 58 | 0.196 | 0.466 | 0.0685 | +0.0024 [-0.0047, +0.0088] | -0.0061 [-0.0142, +0.0014] | 0.579 | 0.178 | no |
| 5 | 0.263 (147 of 1869 days never flag) | 62 | 0.203 | 0.452 | 0.0687 | +0.0022 [-0.0045, +0.0086] | -0.0053 [-0.0133, +0.0021] | 0.578 | 0.183 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.585 (climatology 0.457, difference +0.1280 [-0.0271, +0.2791]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1022, ΔBrier vs climatology +0.0273 [+0.0160, +0.0391], realised minus predicted +0.0782 [+0.0448, +0.1143]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1124 | 0.2720 | -0.0110 [-0.0312, +0.0085] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0150 | 0.0159 | +0.0348 [+0.0252, +0.0439] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0004 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0048 | 0.0200 | +0.0049 [+0.0008, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.0412 | 0.1165 | +0.0163 [+0.0004, +0.0353] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.125 | 0.0031 | 0.0048 | +0.0088 [+0.0067, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0038 | 0.0031 | +0.0297 [+0.0230, +0.0362] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0658 | 0.4146 | 0.0332 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.534 | 0.1070 | 0.2474 | +0.0004 [-0.0181, +0.0183] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1082 | 0.1133 | +0.0281 [-0.0009, +0.0596] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.486 | 0.0122 | 0.0630 | +0.0036 [-0.0016, +0.0084] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3443 | 0.2903 | +0.1098 [+0.0358, +0.1816] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1267 | 0.1461 | +0.0763 [+0.0436, +0.1151] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2664 | 0.2213 |

## risk_logistic_base_settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.192 | 1.92 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.200, 0.500] | 0.154 | 1.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.205 (105 of 1873 days never flag) | 93 | 0.307 | 0.462 | 0.0597 | +0.0117 [+0.0064, +0.0164] | -0.0033 [-0.0115, +0.0036] | 0.643 | 0.278 | no |
| 2 | 0.226 (147 of 1872 days never flag) | 58 | 0.194 | 0.466 | 0.0677 | +0.0034 [-0.0029, +0.0092] | -0.0066 [-0.0146, +0.0009] | 0.579 | 0.176 | no |
| 3 | 0.294 (147 of 1871 days never flag) | 53 | 0.181 | 0.472 | 0.0696 | +0.0011 [-0.0063, +0.0077] | -0.0052 [-0.0139, +0.0021] | 0.579 | 0.165 | no |
| 4 | 0.188 (147 of 1870 days never flag) | 58 | 0.181 | 0.431 | 0.0703 | +0.0005 [-0.0066, +0.0069] | -0.0080 [-0.0163, -0.0004] | 0.578 | 0.162 | no |
| 5 | 0.283 (126 of 1869 days never flag) | 64 | 0.196 | 0.422 | 0.0710 | -0.0001 [-0.0069, +0.0062] | -0.0076 [-0.0160, -0.0004] | 0.577 | 0.174 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.557 (climatology 0.457, difference +0.0998 [-0.0391, +0.2225]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1073, ΔBrier vs climatology +0.0221 [+0.0113, +0.0327], realised minus predicted +0.0765 [+0.0424, +0.1146]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1098 | 0.2720 | -0.0009 [-0.0219, +0.0178] |
| regime | 2020 | 251 | 4 | 0.250 | 0.045 | 0.0314 | 0.0159 | +0.0283 [+0.0177, +0.0380] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0024 | 0.0200 | +0.0036 [-0.0000, +0.0063] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0310 | 0.1165 | +0.0159 [+0.0031, +0.0333] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0093 [+0.0076, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0099 | 0.0031 | +0.0280 [+0.0218, +0.0339] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0394 | 0.4146 | 0.0115 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.513 | 0.1085 | 0.2474 | +0.0060 [-0.0127, +0.0237] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1056 | 0.1133 | +0.0358 [+0.0097, +0.0606] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.441 | 0.0123 | 0.0630 | +0.0051 [-0.0003, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3282 | 0.2903 | +0.0791 [+0.0218, +0.1316] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.1326 | 0.1461 | +0.0676 [+0.0372, +0.1016] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2021 | 0.2213 |

## risk_logistic_dealer (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.192 | 2.00 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.192 | 1.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0922 (105 of 1873 days never flag) | 94 | 0.300 | 0.447 | 0.0641 | +0.0073 [+0.0019, +0.0125] | -0.0078 [-0.0165, +0.0003] | 0.641 | 0.270 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 63 | 0.187 | 0.413 | 0.0708 | +0.0003 [-0.0069, +0.0064] | -0.0097 [-0.0188, -0.0019] | 0.577 | 0.166 | no |
| 3 | 0.152 (147 of 1871 days never flag) | 65 | 0.210 | 0.446 | 0.0700 | +0.0007 [-0.0068, +0.0073] | -0.0056 [-0.0146, +0.0018] | 0.578 | 0.189 | no |
| 4 | 0.595 (147 of 1870 days never flag) | 55 | 0.145 | 0.364 | 0.0707 | +0.0001 [-0.0066, +0.0065] | -0.0083 [-0.0165, -0.0009] | 0.577 | 0.125 | no |
| 5 | 0.0802 (147 of 1869 days never flag) | 72 | 0.188 | 0.361 | 0.0711 | -0.0002 [-0.0072, +0.0066] | -0.0077 [-0.0160, -0.0000] | 0.576 | 0.162 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.566 (climatology 0.457, difference +0.1086 [-0.0303, +0.2334]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1135, ΔBrier vs climatology +0.0159 [+0.0043, +0.0271], realised minus predicted +0.0675 [+0.0316, +0.1050]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.284 | 0.569 | 0.1076 | 0.2720 | -0.0057 [-0.0257, +0.0139] |
| regime | 2020 | 251 | 4 | 0.250 | 0.050 | 0.0496 | 0.0159 | +0.0087 [-0.0108, +0.0267] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0007 | 0.0000 | +0.0138 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0066 | 0.0200 | +0.0050 [+0.0009, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.550 | 0.0504 | 0.1165 | +0.0082 [-0.0070, +0.0261] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.125 | 0.0047 | 0.0048 | +0.0083 [+0.0059, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0246 | 0.0031 | +0.0131 [-0.0016, +0.0245] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0438 | 0.4146 | 0.0159 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.316 | 0.529 | 0.1119 | 0.2474 | +0.0004 [-0.0176, +0.0179] |
| day_type | month_end | 150 | 17 | 0.588 | 0.400 | 0.1151 | 0.1133 | +0.0127 [-0.0158, +0.0395] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.500 | 0.0132 | 0.0630 | +0.0039 [-0.0010, +0.0086] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.4067 | 0.2903 | +0.0572 [-0.0405, +0.1490] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.429 | 0.1849 | 0.1461 | +0.0410 [-0.0076, +0.0913] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_logistic_policy (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.679] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.161, 0.462] | 0.154 | 1.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.054 (105 of 1873 days never flag) | 90 | 0.307 | 0.478 | 0.0611 | +0.0103 [+0.0047, +0.0156] | -0.0048 [-0.0129, +0.0027] | 0.642 | 0.280 | no |
| 2 | 0.0282 (147 of 1872 days never flag) | 65 | 0.209 | 0.446 | 0.0678 | +0.0032 [-0.0041, +0.0095] | -0.0068 [-0.0154, +0.0007] | 0.579 | 0.188 | no |
| 3 | 0.0571 (147 of 1871 days never flag) | 59 | 0.203 | 0.475 | 0.0667 | +0.0040 [-0.0032, +0.0104] | -0.0023 [-0.0103, +0.0049] | 0.580 | 0.185 | no |
| 4 | 0.0192 (147 of 1870 days never flag) | 72 | 0.210 | 0.403 | 0.0676 | +0.0032 [-0.0037, +0.0094] | -0.0053 [-0.0131, +0.0019] | 0.580 | 0.185 | no |
| 5 | 0.118 (147 of 1869 days never flag) | 65 | 0.210 | 0.446 | 0.0691 | +0.0019 [-0.0051, +0.0080] | -0.0057 [-0.0136, +0.0017] | 0.577 | 0.189 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.568 (climatology 0.457, difference +0.1111 [-0.0351, +0.2465]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0240 [+0.0127, +0.0356], realised minus predicted +0.0747 [+0.0400, +0.1109]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.545 | 0.1094 | 0.2720 | -0.0087 [-0.0307, +0.0124] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.0225 | 0.0159 | +0.0286 [+0.0152, +0.0400] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0056 | 0.0200 | +0.0050 [+0.0006, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.579 | 0.0439 | 0.1165 | +0.0152 [-0.0005, +0.0335] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.125 | 0.0034 | 0.0048 | +0.0086 [+0.0064, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0042 | 0.0031 | +0.0291 [+0.0228, +0.0352] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0635 | 0.4146 | +0.0297 [-0.0260, +0.0766] |
| scarcity_state | 3 | 473 | 117 | 0.325 | 0.514 | 0.1094 | 0.2474 | -0.0007 [-0.0195, +0.0178] |
| day_type | month_end | 150 | 17 | 0.706 | 0.444 | 0.1139 | 0.1133 | +0.0232 [-0.0056, +0.0548] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.457 | 0.0123 | 0.0630 | +0.0036 [-0.0018, +0.0085] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3666 | 0.2903 | +0.0824 [-0.0069, +0.1672] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1242 | 0.1461 | +0.0834 [+0.0516, +0.1189] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2340 | 0.2213 |

## risk_logistic_settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.714] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.545] | 0.154 | 1.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.262 (105 of 1873 days never flag) | 90 | 0.307 | 0.478 | 0.0609 | +0.0105 [+0.0052, +0.0153] | -0.0046 [-0.0132, +0.0030] | 0.642 | 0.280 | no |
| 2 | 0.193 (147 of 1872 days never flag) | 58 | 0.194 | 0.466 | 0.0685 | +0.0026 [-0.0039, +0.0086] | -0.0074 [-0.0155, -0.0000] | 0.579 | 0.176 | no |
| 3 | 0.245 (147 of 1871 days never flag) | 57 | 0.203 | 0.491 | 0.0691 | +0.0016 [-0.0054, +0.0079] | -0.0048 [-0.0131, +0.0024] | 0.579 | 0.186 | no |
| 4 | 0.129 (147 of 1870 days never flag) | 69 | 0.181 | 0.362 | 0.0701 | +0.0007 [-0.0062, +0.0067] | -0.0078 [-0.0156, -0.0007] | 0.578 | 0.156 | no |
| 5 | 0.221 (126 of 1869 days never flag) | 61 | 0.167 | 0.377 | 0.0717 | -0.0008 [-0.0086, +0.0057] | -0.0083 [-0.0170, -0.0009] | 0.575 | 0.145 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.544 (climatology 0.457, difference +0.0867 [-0.0568, +0.2046]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1087, ΔBrier vs climatology +0.0207 [+0.0100, +0.0310], realised minus predicted +0.0744 [+0.0403, +0.1113]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.564 | 0.1088 | 0.2720 | +0.0002 [-0.0214, +0.0197] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.0358 | 0.0159 | +0.0209 [+0.0028, +0.0358] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0158] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0008, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.625 | 0.0340 | 0.1165 | +0.0113 [-0.0009, +0.0280] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0032 | 0.0048 | +0.0091 [+0.0072, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0102 | 0.0031 | +0.0257 [+0.0189, +0.0315] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0317 | 0.4146 | -0.0009 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.513 | 0.1102 | 0.2474 | +0.0043 [-0.0150, +0.0227] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1082 | 0.1133 | +0.0286 [+0.0021, +0.0552] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0127 | 0.0630 | +0.0042 [-0.0012, +0.0090] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3658 | 0.2903 | +0.0759 [+0.0066, +0.1419] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.500 | 0.1368 | 0.1461 | +0.0705 [+0.0395, +0.1075] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2008 | 0.2213 |

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

## risk_quantile_skewt_base_policy (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.682] | 0.192 | 1.96 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.160, 0.467] | 0.115 | 1.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.243 (84 of 1873 days never flag) | 95 | 0.314 | 0.463 | 0.0647 | +0.0067 [+0.0003, +0.0131] | -0.0084 [-0.0170, -0.0000] | 0.644 | 0.285 | no |
| 2 | 0.14 (147 of 1872 days never flag) | 52 | 0.158 | 0.423 | 0.0735 | -0.0025 [-0.0114, +0.0055] | -0.0125 [-0.0218, -0.0039] | 0.566 | 0.141 | no |
| 3 | 0.203 (126 of 1871 days never flag) | 44 | 0.159 | 0.500 | 0.0686 | +0.0021 [-0.0058, +0.0094] | -0.0042 [-0.0127, +0.0036] | 0.586 | 0.147 | no |
| 4 | 0.302 (126 of 1870 days never flag) | 42 | 0.145 | 0.476 | 0.0727 | -0.0019 [-0.0102, +0.0055] | -0.0103 [-0.0191, -0.0023] | 0.578 | 0.132 | no |
| 5 | 0.225 (126 of 1869 days never flag) | 42 | 0.109 | 0.357 | 0.0710 | -0.0000 [-0.0083, +0.0074] | -0.0076 [-0.0166, +0.0004] | 0.580 | 0.093 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.629 (climatology 0.457, difference +0.1718 [+0.0316, +0.2921]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1169, ΔBrier vs climatology +0.0126 [-0.0008, +0.0255], realised minus predicted +0.0626 [+0.0284, +0.0998]; calibrated no, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.556 | 0.1277 | 0.2720 | -0.0230 [-0.0492, +0.0033] |
| regime | 2020 | 251 | 4 | 0.250 | 0.045 | 0.0372 | 0.0159 | +0.0212 [+0.0097, +0.0319] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0020 | 0.0000 | +0.0137 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0079 | 0.0200 | +0.0017 [-0.0037, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.706 | 0.0453 | 0.1165 | +0.0207 [+0.0023, +0.0441] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0037 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0222 | 0.0031 | +0.0160 [+0.0053, +0.0254] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.0840 | 0.4146 | +0.0462 [-0.0207, +0.1189] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.520 | 0.1217 | 0.2474 | -0.0078 [-0.0296, +0.0144] |
| day_type | month_end | 150 | 17 | 0.706 | 0.387 | 0.1440 | 0.1133 | +0.0065 [-0.0296, +0.0462] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.486 | 0.0146 | 0.0630 | +0.0021 [-0.0036, +0.0071] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2920 | 0.2903 | +0.0806 [+0.0118, +0.1446] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.474 | 0.2013 | 0.1461 | +0.0647 [+0.0023, +0.1360] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4287 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2058 | 0.2213 |

## risk_quantile_skewt_base_settle (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.361, 0.720] | 0.154 | 1.69 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.193, 0.500] | 0.154 | 1.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.411 (126 of 1873 days never flag) | 86 | 0.300 | 0.488 | 0.0635 | +0.0079 [+0.0014, +0.0142] | -0.0072 [-0.0163, +0.0012] | 0.638 | 0.275 | no |
| 2 | 0.0921 (126 of 1872 days never flag) | 69 | 0.209 | 0.420 | 0.0690 | +0.0021 [-0.0058, +0.0085] | -0.0079 [-0.0170, -0.0003] | 0.579 | 0.186 | no |
| 3 | 0.266 (126 of 1871 days never flag) | 54 | 0.196 | 0.500 | 0.0683 | +0.0023 [-0.0060, +0.0094] | -0.0040 [-0.0130, +0.0039] | 0.586 | 0.180 | no |
| 4 | 0.461 (126 of 1870 days never flag) | 72 | 0.210 | 0.403 | 0.0680 | +0.0028 [-0.0045, +0.0096] | -0.0056 [-0.0140, +0.0019] | 0.586 | 0.185 | no |
| 5 | 0.606 (126 of 1869 days never flag) | 63 | 0.203 | 0.444 | 0.0670 | +0.0040 [-0.0030, +0.0108] | -0.0036 [-0.0118, +0.0045] | 0.584 | 0.183 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.578 (climatology 0.457, difference +0.1208 [-0.0608, +0.2797]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1064, ΔBrier vs climatology +0.0230 [+0.0093, +0.0359], realised minus predicted +0.0505 [+0.0179, +0.0840]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.652 | 0.1224 | 0.2720 | -0.0163 [-0.0427, +0.0102] |
| regime | 2020 | 251 | 4 | 0.250 | 0.038 | 0.0545 | 0.0159 | +0.0174 [+0.0072, +0.0275] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0032 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0014 [-0.0047, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.833 | 0.0509 | 0.1165 | +0.0242 [+0.0052, +0.0480] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0059 | 0.0048 | +0.0086 [+0.0065, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0327 | 0.0031 | +0.0171 [+0.0097, +0.0238] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 1.000 | 0.0963 | 0.4146 | 0.0526 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.316 | 0.607 | 0.1205 | 0.2474 | -0.0038 [-0.0269, +0.0191] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1533 | 0.1133 | +0.0087 [-0.0313, +0.0491] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.484 | 0.0149 | 0.0630 | +0.0034 [-0.0023, +0.0085] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3293 | 0.2903 | +0.0804 [+0.0234, +0.1370] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.381 | 0.2302 | 0.1461 | +0.0626 [+0.0112, +0.1238] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4128 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

