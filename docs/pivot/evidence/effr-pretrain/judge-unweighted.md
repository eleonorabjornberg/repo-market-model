# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `4691be07ea1b…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## effr_pooled (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 5 | 0.192 [0.062, 0.333] | 0.154 | 1.50 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 4 | 0.154 [0.040, 0.292] | 0.154 | 1.50 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (189 of 1873 days never flag) | 69 | 0.300 | 0.609 | 0.0535 | +0.0179 [+0.0105, +0.0264] | +0.0029 [-0.0044, +0.0098] | 0.919 | 0.284 | no |
| 2 | 0.524 (189 of 1872 days never flag) | 69 | 0.237 | 0.478 | 0.0574 | +0.0136 [+0.0066, +0.0212] | +0.0036 [-0.0027, +0.0103] | 0.905 | 0.217 | no |
| 3 | 0.638 (189 of 1871 days never flag) | 64 | 0.232 | 0.500 | 0.0597 | +0.0110 [+0.0038, +0.0181] | +0.0046 [-0.0019, +0.0109] | 0.895 | 0.213 | no |
| 4 | 0.62 (189 of 1870 days never flag) | 80 | 0.297 | 0.512 | 0.0592 | +0.0117 [+0.0051, +0.0187] | +0.0032 [-0.0032, +0.0101] | 0.896 | 0.275 | no |
| 5 | 0.527 (126 of 1869 days never flag) | 70 | 0.239 | 0.471 | 0.0594 | +0.0115 [+0.0051, +0.0184] | +0.0040 [-0.0025, +0.0105] | 0.894 | 0.218 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.626 (climatology 0.457, difference +0.1686 [+0.0293, +0.2689]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0883, ΔBrier vs climatology +0.0412 [+0.0280, +0.0550], realised minus predicted +0.0644 [+0.0342, +0.0974]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.402 | 0.612 | 0.2942 | 0.2720 | +0.0363 [+0.0004, +0.0763] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0415 | 0.0159 | +0.0339 [+0.0217, +0.0443] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0012 | 0.0200 | +0.0025 [-0.0015, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0169 | 0.1165 | +0.0023 [-0.0048, +0.0094] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0009 | 0.0048 | +0.0091 [+0.0074, +0.0108] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0019 | 0.0031 | +0.0302 [+0.0229, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0461 | 0.4146 | -0.0427 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.359 | 0.609 | 0.2581 | 0.2474 | +0.0342 [+0.0061, +0.0653] |
| day_type | month_end | 150 | 17 | 0.176 | 0.429 | 0.0744 | 0.1133 | +0.0222 [+0.0076, +0.0358] |
| day_type | ordinary | 1603 | 101 | 0.287 | 0.592 | 0.0616 | 0.0630 | +0.0123 [+0.0042, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1869 | 0.2903 | +0.1299 [+0.0707, +0.1957] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1100 | 0.1461 | +0.0733 [+0.0381, +0.1121] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0070 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.3224 | 0.2213 |

## effr_pretrain_finetune (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 7 | 0.269 [0.129, 0.433] | 0.192 | 1.96 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.120, 0.412] | 0.192 | 1.96 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.518 (147 of 1873 days never flag) | 106 | 0.414 | 0.547 | 0.0536 | +0.0178 [+0.0107, +0.0261] | +0.0028 [-0.0034, +0.0094] | 0.919 | 0.387 | no |
| 2 | 0.617 (147 of 1872 days never flag) | 90 | 0.331 | 0.511 | 0.0580 | +0.0131 [+0.0060, +0.0207] | +0.0031 [-0.0038, +0.0102] | 0.906 | 0.306 | no |
| 3 | 0.598 (147 of 1871 days never flag) | 84 | 0.290 | 0.476 | 0.0616 | +0.0090 [+0.0013, +0.0173] | +0.0027 [-0.0047, +0.0100] | 0.896 | 0.264 | no |
| 4 | 0.562 (147 of 1870 days never flag) | 98 | 0.341 | 0.480 | 0.0592 | +0.0117 [+0.0046, +0.0189] | +0.0032 [-0.0039, +0.0106] | 0.900 | 0.311 | no |
| 5 | 0.537 (147 of 1869 days never flag) | 94 | 0.312 | 0.457 | 0.0597 | +0.0112 [+0.0047, +0.0179] | +0.0037 [-0.0029, +0.0102] | 0.896 | 0.282 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.590 (climatology 0.457, difference +0.1330 [-0.0028, +0.2575]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0877, ΔBrier vs climatology +0.0418 [+0.0278, +0.0573], realised minus predicted +0.0546 [+0.0242, +0.0879]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.560 | 0.2886 | 0.2720 | +0.0334 [-0.0007, +0.0724] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0348 | 0.0159 | +0.0341 [+0.0202, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0006 | 0.0200 | +0.0015 [-0.0031, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.069 | 0.667 | 0.0227 | 0.1165 | +0.0066 [-0.0007, +0.0152] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0006 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0011 | 0.0031 | +0.0302 [+0.0228, +0.0368] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0554 | 0.4146 | -0.0225 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.496 | 0.547 | 0.2530 | 0.2474 | +0.0324 [+0.0063, +0.0632] |
| day_type | month_end | 150 | 17 | 0.412 | 0.538 | 0.0837 | 0.1133 | +0.0237 [+0.0101, +0.0387] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.513 | 0.0584 | 0.0630 | +0.0136 [+0.0065, +0.0223] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2199 | 0.2903 | +0.1007 [+0.0569, +0.1471] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1112 | 0.1461 | +0.0566 [+0.0176, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0020 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.3433 | 0.2213 |

## effr_sofr_only (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 7 | 0.269 [0.128, 0.429] | 0.192 | 1.96 | recall no, recall_above_climatology no, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.424] | 0.192 | 1.96 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.562 (147 of 1873 days never flag) | 111 | 0.450 | 0.568 | 0.0554 | +0.0160 [+0.0084, +0.0240] | +0.0009 [-0.0060, +0.0077] | 0.915 | 0.422 | no |
| 2 | 0.586 (147 of 1872 days never flag) | 91 | 0.317 | 0.484 | 0.0587 | +0.0124 [+0.0049, +0.0202] | +0.0024 [-0.0051, +0.0098] | 0.904 | 0.289 | no |
| 3 | 0.582 (147 of 1871 days never flag) | 94 | 0.312 | 0.457 | 0.0606 | +0.0101 [+0.0024, +0.0182] | +0.0038 [-0.0037, +0.0116] | 0.899 | 0.282 | no |
| 4 | 0.556 (147 of 1870 days never flag) | 81 | 0.297 | 0.506 | 0.0604 | +0.0104 [+0.0026, +0.0184] | +0.0019 [-0.0060, +0.0098] | 0.899 | 0.274 | no |
| 5 | 0.544 (147 of 1869 days never flag) | 82 | 0.290 | 0.488 | 0.0612 | +0.0098 [+0.0033, +0.0172] | +0.0022 [-0.0041, +0.0096] | 0.887 | 0.266 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [+0.0003, +0.2335]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0409 [+0.0267, +0.0564], realised minus predicted +0.0580 [+0.0261, +0.0913]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.569 | 0.3018 | 0.2720 | +0.0263 [-0.0103, +0.0663] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.0439 | 0.0159 | +0.0339 [+0.0239, +0.0436] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0158] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0019 [-0.0026, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0190 | 0.1165 | +0.0033 [-0.0041, +0.0118] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0009 | 0.0048 | +0.0090 [+0.0072, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0009 | 0.0031 | +0.0302 [+0.0232, +0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0232 | 0.4146 | -0.0175 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.538 | 0.568 | 0.2691 | 0.2474 | +0.0246 [-0.0045, +0.0562] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.0899 | 0.1133 | +0.0208 [+0.0065, +0.0342] |
| day_type | ordinary | 1603 | 101 | 0.426 | 0.537 | 0.0620 | 0.0630 | +0.0118 [+0.0043, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2197 | 0.2903 | +0.0923 [+0.0488, +0.1360] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1092 | 0.1461 | +0.0565 [+0.0214, +0.0945] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0049 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2780 | 0.2213 |

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

## risk_gbm+effr_pooled (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.618] | 0.192 | 2.08 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.118, 0.433] | 0.192 | 2.08 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (147 of 1873 days never flag) | 58 | 0.321 | 0.776 | 0.0477 | +0.0237 [+0.0150, +0.0339] | +0.0087 [+0.0019, +0.0163] | 0.924 | 0.314 | no |
| 2 | 0.605 (294 of 1872 days never flag) | 16 | 0.050 | 0.438 | 0.0594 | +0.0116 [+0.0047, +0.0191] | +0.0016 [-0.0047, +0.0074] | 0.899 | 0.045 | no |
| 3 | 0.56 (210 of 1871 days never flag) | 43 | 0.159 | 0.512 | 0.0593 | +0.0114 [+0.0047, +0.0184] | +0.0051 [-0.0008, +0.0110] | 0.893 | 0.147 | no |
| 4 | 0.655 (252 of 1870 days never flag) | 21 | 0.087 | 0.571 | 0.0593 | +0.0115 [+0.0048, +0.0185] | +0.0030 [-0.0031, +0.0093] | 0.892 | 0.082 | no |
| 5 | 0.534 (126 of 1869 days never flag) | 99 | 0.326 | 0.455 | 0.0618 | +0.0091 [+0.0024, +0.0158] | +0.0016 [-0.0046, +0.0076] | 0.884 | 0.295 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.482 (climatology 0.457, difference +0.0253 [-0.1094, +0.1283]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0824, ΔBrier vs climatology +0.0471 [+0.0330, +0.0629], realised minus predicted +0.0490 [+0.0206, +0.0799]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.766 | 0.3133 | 0.2720 | +0.0519 [+0.0126, +0.0983] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.0461 | 0.0159 | +0.0345 [+0.0234, +0.0448] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0008 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [-0.0000, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0465 | 0.1165 | +0.0205 [+0.0003, +0.0484] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0024 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0041 | 0.0031 | +0.0296 [+0.0221, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0656 | 0.4146 | -0.0169 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.376 | 0.786 | 0.2863 | 0.2474 | +0.0561 [+0.0233, +0.0934] |
| day_type | month_end | 150 | 17 | 0.588 | 0.909 | 0.1039 | 0.1133 | +0.0582 [+0.0353, +0.0833] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.722 | 0.0692 | 0.0630 | +0.0162 [+0.0073, +0.0265] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0286, +0.1946] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0434, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2684 | 0.2213 |

## risk_gbm+effr_pretrain_finetune (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.238, 0.607] | 0.192 | 2.12 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.150, 0.474] | 0.192 | 2.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (147 of 1873 days never flag) | 89 | 0.443 | 0.697 | 0.0466 | +0.0248 [+0.0163, +0.0340] | +0.0097 [+0.0032, +0.0161] | 0.926 | 0.427 | no |
| 2 | 0.605 (147 of 1872 days never flag) | 96 | 0.360 | 0.521 | 0.0586 | +0.0125 [+0.0057, +0.0198] | +0.0025 [-0.0037, +0.0085] | 0.902 | 0.333 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 91 | 0.297 | 0.451 | 0.0598 | +0.0109 [+0.0032, +0.0183] | +0.0046 [-0.0019, +0.0110] | 0.897 | 0.268 | no |
| 4 | 0.521 (147 of 1870 days never flag) | 92 | 0.319 | 0.478 | 0.0578 | +0.0131 [+0.0064, +0.0200] | +0.0046 [-0.0018, +0.0107] | 0.897 | 0.291 | no |
| 5 | 0.537 (147 of 1869 days never flag) | 104 | 0.355 | 0.471 | 0.0606 | +0.0103 [+0.0043, +0.0165] | +0.0028 [-0.0032, +0.0087] | 0.885 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.477 (climatology 0.457, difference +0.0197 [-0.1270, +0.1311]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0828, ΔBrier vs climatology +0.0467 [+0.0325, +0.0629], realised minus predicted +0.0487 [+0.0210, +0.0808]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.684 | 0.2974 | 0.2720 | +0.0560 [+0.0204, +0.0954] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.0413 | 0.0159 | +0.0338 [+0.0216, +0.0447] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0007 | 0.0000 | +0.0138 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [-0.0001, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0515 | 0.1165 | +0.0229 [+0.0014, +0.0509] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0024 | 0.0048 | +0.0087 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0042 | 0.0031 | +0.0296 [+0.0221, +0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0734 | 0.4146 | 0.0010 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.701 | 0.2730 | 0.2474 | +0.0586 [+0.0272, +0.0920] |
| day_type | month_end | 150 | 17 | 0.588 | 0.909 | 0.1039 | 0.1133 | +0.0589 [+0.0345, +0.0853] |
| day_type | ordinary | 1603 | 101 | 0.426 | 0.642 | 0.0655 | 0.0630 | +0.0174 [+0.0090, +0.0266] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0334, +0.1964] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0418, +0.0965] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3081 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2985 | 0.2213 |

## risk_gbm+effr_sofr_only (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.240, 0.619] | 0.192 | 2.27 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.166, 0.478] | 0.192 | 2.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (147 of 1873 days never flag) | 84 | 0.407 | 0.679 | 0.0482 | +0.0232 [+0.0145, +0.0326] | +0.0081 [+0.0010, +0.0156] | 0.920 | 0.392 | no |
| 2 | 0.586 (147 of 1872 days never flag) | 88 | 0.273 | 0.432 | 0.0589 | +0.0121 [+0.0048, +0.0199] | +0.0021 [-0.0051, +0.0090] | 0.897 | 0.245 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 93 | 0.304 | 0.452 | 0.0588 | +0.0119 [+0.0043, +0.0191] | +0.0056 [-0.0016, +0.0123] | 0.897 | 0.275 | no |
| 4 | 0.619 (147 of 1870 days never flag) | 86 | 0.283 | 0.453 | 0.0591 | +0.0117 [+0.0042, +0.0189] | +0.0032 [-0.0039, +0.0101] | 0.896 | 0.255 | no |
| 5 | 0.537 (147 of 1869 days never flag) | 95 | 0.261 | 0.379 | 0.0624 | +0.0085 [+0.0015, +0.0151] | +0.0010 [-0.0057, +0.0071] | 0.880 | 0.227 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.467 (climatology 0.457, difference +0.0097 [-0.1434, +0.1232]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0821, ΔBrier vs climatology +0.0473 [+0.0337, +0.0627], realised minus predicted +0.0504 [+0.0219, +0.0836]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.649 | 0.3087 | 0.2720 | +0.0479 [+0.0084, +0.0900] |
| regime | 2020 | 251 | 4 | 0.250 | 1.000 | 0.0478 | 0.0159 | +0.0360 [+0.0268, +0.0450] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0008 | 0.0000 | +0.0138 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0030 | 0.0200 | +0.0037 [-0.0001, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0480 | 0.1165 | +0.0207 [-0.0001, +0.0469] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0025 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0041 | 0.0031 | +0.0296 [+0.0220, +0.0366] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0417 | 0.4146 | 0.0066 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.479 | 0.683 | 0.2863 | 0.2474 | +0.0518 [+0.0196, +0.0850] |
| day_type | month_end | 150 | 17 | 0.588 | 0.909 | 0.1052 | 0.1133 | +0.0582 [+0.0327, +0.0835] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.613 | 0.0686 | 0.0630 | +0.0156 [+0.0070, +0.0247] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0357, +0.1943] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0958 | 0.1461 | +0.0686 [+0.0426, +0.0946] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3090 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2103 | 0.2213 |

