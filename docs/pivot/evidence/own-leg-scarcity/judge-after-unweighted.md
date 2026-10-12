# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `062fba17b6e3…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

- h = 1: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.2 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 2.4 over 1041 days; regime_2021-23: 4.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.512 (climatology 0.512, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1757, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0470 [-0.1017, +0.0117]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.436 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.034 | 1.000 | 0.0645 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0913 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1596 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1021 | 0.2439 | 0.0000 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.426 | 0.1369 | 0.2615 | +0.0000 [+0.0000, +0.0000] |
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

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.506 (climatology 0.512, difference -0.0059 [-0.0893, +0.0823]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0510, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.451 | 0.455 | 0.1679 | 0.2720 | +0.0168 [-0.0027, +0.0376] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.0978 | 0.1165 | +0.0256 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0240 | 0.0048 | +0.0080 [+0.0058, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0873 | 0.0000 | +0.0224 [+0.0166, +0.0283] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1445 | 0.2439 | 0.0333 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.464 | 0.472 | 0.1830 | 0.2615 | +0.0241 [+0.0043, +0.0450] |
| day_type | month_end | 150 | 17 | 0.412 | 0.583 | 0.0778 | 0.1133 | +0.0212 [+0.0029, +0.0434] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.432 | 0.0774 | 0.0630 | +0.0125 [+0.0072, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.0845 | 0.2903 | +0.0604 [-0.0440, +0.1631] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.429 | 0.0819 | 0.1461 | +0.0355 [+0.0130, +0.0568] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1364 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3171 | 0.2213 |

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

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.603 (climatology 0.512, difference +0.0911 [-0.0509, +0.1787]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0303, +0.0551], realised minus predicted +0.0654 [+0.0350, +0.0998]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.577 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0503 | 0.0159 | +0.0329 [+0.0235, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.909 | 0.0443 | 0.1165 | +0.0287 [+0.0113, +0.0503] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0096 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0260 | 0.0000 | +0.0283 [+0.0221, +0.0343] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 1.000 | 0.0561 | 0.2439 | +0.0463 [+0.0179, +0.0828] |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.596 | 0.2024 | 0.2615 | +0.0552 [+0.0317, +0.0794] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.0819 | 0.1133 | +0.0481 [+0.0291, +0.0671] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.554 | 0.0518 | 0.0630 | +0.0187 [+0.0123, +0.0262] |
| day_type | quarter_end | 31 | 9 | 0.667 | 1.000 | 0.1699 | 0.2903 | +0.1308 [+0.0495, +0.2125] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.750 | 0.0904 | 0.1461 | +0.0670 [+0.0493, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## risk_gbm (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.667] | 0.115 | 1.35 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.115 | 1.04 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 77 | 0.300 | 0.545 | 0.0575 | +0.0139 [+0.0085, +0.0196] | -0.0012 [-0.0094, +0.0065] | 0.643 | 0.280 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 54 | 0.187 | 0.481 | 0.0686 | +0.0025 [-0.0039, +0.0081] | -0.0075 [-0.0160, -0.0005] | 0.578 | 0.171 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0665 | +0.0042 [-0.0024, +0.0101] | -0.0021 [-0.0100, +0.0048] | 0.580 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 46 | 0.167 | 0.500 | 0.0669 | +0.0039 [-0.0029, +0.0099] | -0.0045 [-0.0124, +0.0024] | 0.579 | 0.153 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 48 | 0.152 | 0.438 | 0.0697 | +0.0012 [-0.0054, +0.0074] | -0.0063 [-0.0137, +0.0006] | 0.577 | 0.137 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.523 (climatology 0.512, difference +0.0110 [-0.1321, +0.1313]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1044, ΔBrier vs climatology +0.0250 [+0.0161, +0.0339], realised minus predicted +0.0931 [+0.0564, +0.1322]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0959 | 0.2720 | +0.0016 [-0.0200, +0.0242] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0148 | 0.0159 | +0.0396 [+0.0307, +0.0483] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0028 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0390 | 0.1165 | +0.0173 [-0.0006, +0.0406] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0021 | 0.0048 | +0.0090 [+0.0071, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0021 | 0.0000 | +0.0317 [+0.0250, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0240 | 0.2439 | -0.0030 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.0979 | 0.2615 | +0.0145 [-0.0059, +0.0355] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0987 | 0.1133 | +0.0545 [+0.0304, +0.0791] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0435, +0.2143] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0950] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2003 | 0.2213 |

## risk_gbm+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.760] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 2.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 102 | 0.464 | 0.637 | 0.0476 | +0.0238 [+0.0166, +0.0321] | +0.0087 [+0.0039, +0.0140] | 0.897 | 0.443 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 139 | 0.446 | 0.446 | 0.0601 | +0.0110 [+0.0065, +0.0153] | +0.0010 [-0.0020, +0.0040] | 0.845 | 0.402 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 132 | 0.428 | 0.447 | 0.0603 | +0.0103 [+0.0066, +0.0145] | +0.0040 [+0.0011, +0.0073] | 0.814 | 0.385 | no |
| 4 | 0.335 (147 of 1870 days never flag) | 118 | 0.420 | 0.492 | 0.0595 | +0.0114 [+0.0070, +0.0160] | +0.0029 [+0.0003, +0.0058] | 0.820 | 0.386 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 117 | 0.370 | 0.436 | 0.0630 | +0.0079 [+0.0035, +0.0123] | +0.0004 [-0.0027, +0.0032] | 0.789 | 0.331 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0116 [-0.1004, +0.1004]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0841, ΔBrier vs climatology +0.0454 [+0.0318, +0.0607], realised minus predicted +0.0117 [-0.0184, +0.0444]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2373 | 0.2720 | +0.0573 [+0.0304, +0.0862] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1174 | 0.0159 | +0.0233 [+0.0097, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0192 | 0.0000 | +0.0131 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0328 | 0.0200 | +0.0006 [-0.0060, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.1153 | 0.1165 | +0.0293 [+0.0021, +0.0606] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0236 | 0.0048 | +0.0074 [+0.0049, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0654 | 0.0000 | +0.0253 [+0.0194, +0.0316] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1446 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.650 | 0.2483 | 0.2615 | +0.0573 [+0.0324, +0.0837] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1080 | 0.1133 | +0.0597 [+0.0358, +0.0874] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.592 | 0.0861 | 0.0630 | +0.0160 [+0.0093, +0.0240] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0510, +0.2060] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0421, +0.0961] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3382 | 0.2213 |

## risk_gbm+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.444, 0.778] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.545] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 70 | 0.329 | 0.657 | 0.0494 | +0.0220 [+0.0148, +0.0296] | +0.0069 [+0.0018, +0.0121] | 0.805 | 0.315 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 120 | 0.388 | 0.450 | 0.0623 | +0.0087 [+0.0037, +0.0134] | -0.0013 [-0.0053, +0.0024] | 0.750 | 0.350 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 134 | 0.413 | 0.425 | 0.0604 | +0.0103 [+0.0051, +0.0149] | +0.0040 [-0.0006, +0.0079] | 0.747 | 0.369 | no |
| 4 | 0.258 (147 of 1870 days never flag) | 109 | 0.384 | 0.486 | 0.0603 | +0.0105 [+0.0055, +0.0154] | +0.0020 [-0.0015, +0.0056] | 0.759 | 0.352 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 111 | 0.348 | 0.432 | 0.0637 | +0.0072 [+0.0017, +0.0125] | -0.0003 [-0.0043, +0.0037] | 0.742 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.530 (climatology 0.512, difference +0.0178 [-0.1007, +0.1301]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0860, ΔBrier vs climatology +0.0435 [+0.0306, +0.0581], realised minus predicted +0.0619 [+0.0330, +0.0947]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.680 | 0.1676 | 0.2720 | +0.0417 [+0.0143, +0.0703] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0224 | 0.0159 | +0.0323 [+0.0157, +0.0454] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0152 | 0.0200 | +0.0007 [-0.0068, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0902 | 0.1165 | +0.0284 [+0.0031, +0.0604] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0098 | 0.0048 | +0.0076 [+0.0052, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0033 | 0.0000 | +0.0316 [+0.0249, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1135 | 0.2439 | 0.0371 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.676 | 0.1718 | 0.2615 | +0.0457 [+0.0214, +0.0719] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1025 | 0.1133 | +0.0602 [+0.0346, +0.0877] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.578 | 0.0419 | 0.0630 | +0.0138 [+0.0076, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0438, +0.2071] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0418, +0.0955] |

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
| 1 | 0.65 (105 of 1873 days never flag) | 64 | 0.314 | 0.688 | 0.0499 | +0.0215 [+0.0142, +0.0286] | +0.0064 [+0.0011, +0.0117] | 0.804 | 0.303 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 100 | 0.396 | 0.550 | 0.0543 | +0.0168 [+0.0118, +0.0223] | +0.0068 [+0.0021, +0.0119] | 0.801 | 0.370 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 94 | 0.348 | 0.511 | 0.0563 | +0.0144 [+0.0089, +0.0198] | +0.0081 [+0.0032, +0.0130] | 0.778 | 0.321 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 94 | 0.384 | 0.564 | 0.0530 | +0.0178 [+0.0124, +0.0232] | +0.0094 [+0.0051, +0.0141] | 0.808 | 0.360 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 123 | 0.449 | 0.504 | 0.0542 | +0.0168 [+0.0113, +0.0224] | +0.0092 [+0.0048, +0.0141] | 0.804 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.704 (climatology 0.512, difference +0.1918 [+0.0419, +0.3200]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0719, ΔBrier vs climatology +0.0576 [+0.0400, +0.0768], realised minus predicted +0.0312 [+0.0067, +0.0565]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.333 | 0.694 | 0.1692 | 0.2720 | +0.0420 [+0.0131, +0.0705] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0243 | 0.0159 | +0.0310 [+0.0152, +0.0451] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0135 [+0.0117, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0131 | 0.0200 | -0.0013 [-0.0085, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0898 | 0.1165 | +0.0279 [+0.0027, +0.0580] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0091 | 0.0048 | +0.0074 [+0.0047, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0030 | 0.0000 | +0.0316 [+0.0251, +0.0386] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1374 | 0.2439 | 0.0348 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.352 | 0.698 | 0.1724 | 0.2615 | +0.0445 [+0.0181, +0.0702] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.0999 | 0.1133 | +0.0579 [+0.0340, +0.0836] |
| day_type | ordinary | 1603 | 101 | 0.248 | 0.595 | 0.0425 | 0.0630 | +0.0134 [+0.0067, +0.0199] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0507, +0.2140] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0392, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3821 | 0.2213 |

## risk_gbm+every_day+gate+settle+h41+iorb (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.440, 0.786] | 0.192 | 2.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.652] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 67 | 0.329 | 0.687 | 0.0498 | +0.0216 [+0.0144, +0.0296] | +0.0065 [+0.0012, +0.0125] | 0.804 | 0.316 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 100 | 0.396 | 0.550 | 0.0543 | +0.0168 [+0.0118, +0.0222] | +0.0068 [+0.0020, +0.0122] | 0.801 | 0.370 | no |
| 3 | 0.402 (147 of 1871 days never flag) | 94 | 0.348 | 0.511 | 0.0563 | +0.0144 [+0.0090, +0.0199] | +0.0081 [+0.0035, +0.0129] | 0.778 | 0.321 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 94 | 0.384 | 0.564 | 0.0530 | +0.0178 [+0.0124, +0.0234] | +0.0094 [+0.0050, +0.0142] | 0.808 | 0.360 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 123 | 0.449 | 0.504 | 0.0542 | +0.0168 [+0.0115, +0.0223] | +0.0092 [+0.0047, +0.0136] | 0.804 | 0.414 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.704 (climatology 0.512, difference +0.1918 [+0.0357, +0.3321]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0711, ΔBrier vs climatology +0.0584 [+0.0404, +0.0773], realised minus predicted +0.0293 [+0.0056, +0.0553]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.343 | 0.700 | 0.1724 | 0.2720 | +0.0442 [+0.0158, +0.0733] |
| regime | 2020 | 251 | 4 | 0.500 | 0.500 | 0.0282 | 0.0159 | +0.0350 [+0.0212, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0042 | 0.0000 | +0.0136 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0181 | 0.0200 | -0.0056 [-0.0171, +0.0035] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.818 | 0.0895 | 0.1165 | +0.0258 [+0.0024, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0098 | 0.0048 | +0.0064 [+0.0029, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0027 | 0.0000 | +0.0316 [+0.0246, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1425 | 0.2439 | 0.0321 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.708 | 0.1772 | 0.2615 | +0.0474 [+0.0224, +0.0736] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.0999 | 0.1133 | +0.0579 [+0.0339, +0.0839] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.600 | 0.0445 | 0.0630 | +0.0135 [+0.0073, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0525, +0.2116] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0375, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3803 | 0.2213 |

## risk_gbm+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.406, 0.750] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.226, 0.565] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 84 | 0.357 | 0.595 | 0.0481 | +0.0233 [+0.0166, +0.0308] | +0.0082 [+0.0034, +0.0134] | 0.888 | 0.338 | no |
| 2 | 0.257 (147 of 1872 days never flag) | 133 | 0.439 | 0.459 | 0.0593 | +0.0118 [+0.0082, +0.0152] | +0.0018 [-0.0015, +0.0051] | 0.831 | 0.397 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 135 | 0.420 | 0.430 | 0.0590 | +0.0117 [+0.0083, +0.0156] | +0.0054 [+0.0016, +0.0093] | 0.803 | 0.376 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 117 | 0.399 | 0.470 | 0.0581 | +0.0127 [+0.0092, +0.0162] | +0.0043 [+0.0016, +0.0072] | 0.809 | 0.363 | no |
| 5 | 0.258 (147 of 1869 days never flag) | 107 | 0.370 | 0.477 | 0.0613 | +0.0096 [+0.0060, +0.0132] | +0.0021 [-0.0009, +0.0050] | 0.780 | 0.337 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0122 [-0.1051, +0.1055]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0856, ΔBrier vs climatology +0.0439 [+0.0310, +0.0576], realised minus predicted +0.0219 [-0.0100, +0.0582]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.576 | 0.2177 | 0.2720 | +0.0498 [+0.0240, +0.0771] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.1033 | 0.0159 | +0.0291 [+0.0201, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0160 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0240 | 0.0200 | +0.0027 [-0.0017, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0986 | 0.1165 | +0.0283 [+0.0050, +0.0582] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0184 | 0.0048 | +0.0084 [+0.0065, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0557 | 0.0000 | +0.0265 [+0.0204, +0.0326] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1148 | 0.2439 | 0.0329 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.602 | 0.2277 | 0.2615 | +0.0528 [+0.0291, +0.0779] |
| day_type | month_end | 150 | 17 | 0.706 | 0.706 | 0.1066 | 0.1133 | +0.0588 [+0.0341, +0.0842] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.500 | 0.0741 | 0.0630 | +0.0154 [+0.0094, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0488, +0.2053] |
| day_type | tax_date | 89 | 13 | 0.538 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0420, +0.0959] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.400 | 1.000 | 0.4541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2486 | 0.2213 |

## risk_gbm+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.433, 0.792] | 0.231 | 2.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.600] | 0.231 | 2.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 101 | 0.464 | 0.644 | 0.0467 | +0.0247 [+0.0175, +0.0325] | +0.0096 [+0.0047, +0.0148] | 0.913 | 0.444 | no |
| 2 | 0.398 (147 of 1872 days never flag) | 140 | 0.460 | 0.457 | 0.0591 | +0.0119 [+0.0074, +0.0163] | +0.0019 [-0.0012, +0.0048] | 0.877 | 0.417 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 137 | 0.442 | 0.445 | 0.0584 | +0.0123 [+0.0086, +0.0161] | +0.0059 [+0.0030, +0.0089] | 0.865 | 0.398 | no |
| 4 | 0.335 (147 of 1870 days never flag) | 117 | 0.428 | 0.504 | 0.0580 | +0.0128 [+0.0089, +0.0172] | +0.0044 [+0.0020, +0.0072] | 0.865 | 0.394 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 114 | 0.370 | 0.447 | 0.0619 | +0.0090 [+0.0046, +0.0133] | +0.0015 [-0.0015, +0.0046] | 0.849 | 0.333 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.524 (climatology 0.512, difference +0.0116 [-0.1013, +0.1034]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0328, +0.0605], realised minus predicted +0.0387 [+0.0087, +0.0716]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.646 | 0.2373 | 0.2720 | +0.0573 [+0.0292, +0.0859] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1171 | 0.0159 | +0.0233 [+0.0105, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0047 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0037 [-0.0003, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.688 | 0.0987 | 0.1165 | +0.0318 [+0.0046, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0021 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0654 | 0.0000 | +0.0253 [+0.0194, +0.0314] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1446 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.650 | 0.2483 | 0.2615 | +0.0573 [+0.0318, +0.0820] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1060 | 0.1133 | +0.0598 [+0.0356, +0.0871] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.600 | 0.0723 | 0.0630 | +0.0170 [+0.0102, +0.0242] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0472, +0.2084] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0413, +0.0938] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3382 | 0.2213 |

## risk_gbm+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.324, 0.682] | 0.115 | 1.31 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.423] | 0.115 | 1.23 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 88 | 0.400 | 0.636 | 0.0481 | +0.0233 [+0.0177, +0.0293] | +0.0082 [+0.0032, +0.0134] | 0.905 | 0.382 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 66 | 0.230 | 0.485 | 0.0603 | +0.0107 [+0.0075, +0.0139] | +0.0007 [-0.0031, +0.0044] | 0.852 | 0.211 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 56 | 0.203 | 0.500 | 0.0595 | +0.0111 [+0.0077, +0.0150] | +0.0048 [+0.0008, +0.0089] | 0.820 | 0.187 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 54 | 0.203 | 0.519 | 0.0593 | +0.0115 [+0.0079, +0.0153] | +0.0031 [-0.0004, +0.0065] | 0.832 | 0.188 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 56 | 0.174 | 0.429 | 0.0624 | +0.0085 [+0.0048, +0.0120] | +0.0010 [-0.0030, +0.0045] | 0.796 | 0.155 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.518 (climatology 0.512, difference +0.0053 [-0.1142, +0.1111]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0297, +0.0515], realised minus predicted +0.0535 [+0.0202, +0.0884]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.441 | 0.608 | 0.1666 | 0.2720 | +0.0429 [+0.0257, +0.0603] |
| regime | 2020 | 251 | 4 | 0.250 | 1.000 | 0.0661 | 0.0159 | +0.0366 [+0.0281, +0.0449] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0099 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0178 | 0.0200 | +0.0030 [-0.0012, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0771 | 0.1165 | +0.0299 [+0.0055, +0.0612] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0128 | 0.0048 | +0.0086 [+0.0066, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0337 | 0.0000 | +0.0301 [+0.0237, +0.0363] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0843 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.448 | 0.644 | 0.1731 | 0.2615 | +0.0505 [+0.0329, +0.0687] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.1034 | 0.1133 | +0.0575 [+0.0328, +0.0848] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.600 | 0.0494 | 0.0630 | +0.0156 [+0.0111, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0496, +0.2077] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.875 | 0.0961 | 0.1461 | +0.0685 [+0.0414, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.4080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2173 | 0.2213 |

## risk_gbm+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.389, 0.783] | 0.231 | 2.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.618] | 0.231 | 2.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 87 | 0.336 | 0.540 | 0.0604 | +0.0110 [+0.0011, +0.0208] | -0.0041 [-0.0123, +0.0042] | 0.873 | 0.313 | no |
| 2 | 0.605 (147 of 1872 days never flag) | 125 | 0.410 | 0.456 | 0.0716 | -0.0005 [-0.0089, +0.0076] | -0.0105 [-0.0182, -0.0033] | 0.816 | 0.371 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 122 | 0.413 | 0.467 | 0.0723 | -0.0017 [-0.0111, +0.0062] | -0.0080 [-0.0169, -0.0004] | 0.798 | 0.376 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 104 | 0.384 | 0.510 | 0.0703 | +0.0005 [-0.0068, +0.0069] | -0.0079 [-0.0145, -0.0022] | 0.814 | 0.355 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 106 | 0.355 | 0.462 | 0.0729 | -0.0019 [-0.0084, +0.0038] | -0.0095 [-0.0154, -0.0042] | 0.775 | 0.322 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.480 (climatology 0.512, difference -0.0322 [-0.1362, +0.0556]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0227, +0.0506], realised minus predicted +0.0060 [-0.0286, +0.0431]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.507 | 0.3118 | 0.2720 | +0.0131 [-0.0304, +0.0570] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0240, +0.0127] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0688 | 0.1165 | +0.0286 [+0.0036, +0.0581] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0084 | 0.0048 | +0.0080 [+0.0061, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1098 | 0.0000 | +0.0120 [+0.0062, +0.0178] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1009 | 0.2439 | 0.0281 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.376 | 0.547 | 0.3114 | 0.2615 | +0.0154 [-0.0232, +0.0525] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1094 | 0.1133 | +0.0570 [+0.0317, +0.0837] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1025 | 0.0630 | +0.0012 [-0.0092, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0503, +0.2063] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0947] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.778] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.567] | 0.231 | 2.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 84 | 0.329 | 0.548 | 0.0609 | +0.0105 [+0.0004, +0.0200] | -0.0046 [-0.0129, +0.0032] | 0.870 | 0.307 | no |
| 2 | 0.668 (147 of 1872 days never flag) | 109 | 0.374 | 0.477 | 0.0718 | -0.0007 [-0.0093, +0.0071] | -0.0107 [-0.0191, -0.0034] | 0.814 | 0.341 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 123 | 0.413 | 0.463 | 0.0723 | -0.0016 [-0.0115, +0.0067] | -0.0079 [-0.0174, -0.0001] | 0.801 | 0.375 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 106 | 0.391 | 0.509 | 0.0704 | +0.0004 [-0.0070, +0.0074] | -0.0081 [-0.0149, -0.0018] | 0.818 | 0.361 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 101 | 0.355 | 0.485 | 0.0727 | -0.0017 [-0.0081, +0.0042] | -0.0093 [-0.0155, -0.0038] | 0.779 | 0.325 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.504 (climatology 0.512, difference -0.0078 [-0.1152, +0.0856]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0913, ΔBrier vs climatology +0.0381 [+0.0238, +0.0540], realised minus predicted +0.0028 [-0.0323, +0.0386]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.514 | 0.3133 | 0.2720 | +0.0133 [-0.0301, +0.0543] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1939 | 0.0159 | -0.0054 [-0.0268, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0119 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0050 | 0.0200 | +0.0005 [-0.0055, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0684 | 0.1165 | +0.0281 [+0.0054, +0.0560] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0077 [+0.0056, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1096 | 0.0000 | +0.0121 [+0.0066, +0.0181] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1248 | 0.2439 | 0.0259 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.548 | 0.3121 | 0.2615 | +0.0142 [-0.0235, +0.0495] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1068 | 0.1133 | +0.0547 [+0.0325, +0.0782] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1031 | 0.0630 | +0.0008 [-0.0095, +0.0108] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0470, +0.2071] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.714] | 0.192 | 2.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.615] | 0.192 | 2.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (105 of 1873 days never flag) | 87 | 0.336 | 0.540 | 0.0604 | +0.0110 [+0.0017, +0.0209] | -0.0041 [-0.0122, +0.0039] | 0.873 | 0.313 | no |
| 2 | 0.716 (147 of 1872 days never flag) | 111 | 0.432 | 0.541 | 0.0649 | +0.0062 [-0.0032, +0.0150] | -0.0038 [-0.0127, +0.0044] | 0.839 | 0.402 | no |
| 3 | 0.615 (147 of 1871 days never flag) | 108 | 0.399 | 0.509 | 0.0687 | +0.0020 [-0.0082, +0.0112] | -0.0043 [-0.0139, +0.0044] | 0.827 | 0.368 | no |
| 4 | 0.754 (147 of 1870 days never flag) | 99 | 0.370 | 0.515 | 0.0650 | +0.0059 [-0.0015, +0.0131] | -0.0026 [-0.0097, +0.0041] | 0.843 | 0.342 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 112 | 0.435 | 0.536 | 0.0652 | +0.0057 [-0.0010, +0.0121] | -0.0018 [-0.0081, +0.0043] | 0.828 | 0.405 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0145, +0.2668]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0818, ΔBrier vs climatology +0.0477 [+0.0295, +0.0684], realised minus predicted -0.0171 [-0.0463, +0.0160]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.507 | 0.3118 | 0.2720 | +0.0131 [-0.0284, +0.0549] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1920 | 0.0159 | -0.0040 [-0.0226, +0.0126] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0120 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0071 | 0.0200 | +0.0025 [-0.0025, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0688 | 0.1165 | +0.0286 [+0.0048, +0.0604] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0084 | 0.0048 | +0.0080 [+0.0060, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1098 | 0.0000 | +0.0120 [+0.0065, +0.0174] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1009 | 0.2439 | 0.0281 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.376 | 0.547 | 0.3114 | 0.2615 | +0.0154 [-0.0210, +0.0532] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1094 | 0.1133 | +0.0570 [+0.0330, +0.0845] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1025 | 0.0630 | +0.0012 [-0.0087, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0471, +0.2088] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0961 | 0.1461 | +0.0685 [+0.0416, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2881 | 0.2213 |

## risk_gbm+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.719] | 0.192 | 2.15 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.192 | 2.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (105 of 1873 days never flag) | 84 | 0.329 | 0.548 | 0.0609 | +0.0105 [+0.0011, +0.0201] | -0.0046 [-0.0128, +0.0035] | 0.870 | 0.307 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 116 | 0.432 | 0.517 | 0.0652 | +0.0059 [-0.0035, +0.0144] | -0.0041 [-0.0129, +0.0041] | 0.838 | 0.399 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 112 | 0.413 | 0.509 | 0.0688 | +0.0018 [-0.0087, +0.0106] | -0.0045 [-0.0145, +0.0041] | 0.823 | 0.381 | no |
| 4 | 0.641 (147 of 1870 days never flag) | 106 | 0.399 | 0.519 | 0.0643 | +0.0066 [-0.0014, +0.0139] | -0.0019 [-0.0096, +0.0054] | 0.844 | 0.369 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 109 | 0.435 | 0.550 | 0.0647 | +0.0062 [-0.0005, +0.0128] | -0.0013 [-0.0080, +0.0051] | 0.827 | 0.406 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1893 [+0.0390, +0.3183]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0475 [+0.0293, +0.0674], realised minus predicted -0.0179 [-0.0488, +0.0162]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.373 | 0.514 | 0.3133 | 0.2720 | +0.0133 [-0.0292, +0.0558] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1939 | 0.0159 | -0.0054 [-0.0262, +0.0109] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0162 | 0.0000 | +0.0119 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0050 | 0.0200 | +0.0005 [-0.0050, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0684 | 0.1165 | +0.0281 [+0.0049, +0.0583] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0077 [+0.0056, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1096 | 0.0000 | +0.0121 [+0.0063, +0.0176] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1248 | 0.2439 | 0.0259 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.548 | 0.3121 | 0.2615 | +0.0142 [-0.0216, +0.0515] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1068 | 0.1133 | +0.0547 [+0.0307, +0.0797] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.435 | 0.1031 | 0.0630 | +0.0008 [-0.0095, +0.0112] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0496, +0.2096] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0979] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_gbm+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.760] | 0.231 | 3.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 93 | 0.386 | 0.581 | 0.0559 | +0.0155 [+0.0082, +0.0238] | +0.0005 [-0.0059, +0.0070] | 0.849 | 0.363 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 133 | 0.388 | 0.406 | 0.0697 | +0.0013 [-0.0044, +0.0070] | -0.0087 [-0.0144, -0.0031] | 0.775 | 0.343 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 126 | 0.428 | 0.468 | 0.0697 | +0.0010 [-0.0038, +0.0057] | -0.0053 [-0.0103, -0.0005] | 0.728 | 0.389 | no |
| 4 | 0.452 (147 of 1870 days never flag) | 119 | 0.413 | 0.479 | 0.0692 | +0.0016 [-0.0031, +0.0061] | -0.0069 [-0.0115, -0.0025] | 0.752 | 0.377 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 131 | 0.370 | 0.389 | 0.0729 | -0.0020 [-0.0072, +0.0029] | -0.0095 [-0.0151, -0.0043] | 0.717 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.479 (climatology 0.512, difference -0.0329 [-0.1329, +0.0587]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0962, ΔBrier vs climatology +0.0333 [+0.0203, +0.0469], realised minus predicted -0.0114 [-0.0467, +0.0268]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.566 | 0.2828 | 0.2720 | +0.0391 [+0.0075, +0.0714] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0137, +0.0099] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0086, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0022, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0675 | 0.1165 | +0.0265 [+0.0030, +0.0554] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0218 | 0.0048 | +0.0076 [+0.0058, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1294 | 0.0000 | +0.0062 [+0.0011, +0.0119] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0781 | 0.2439 | 0.0070 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.432 | 0.587 | 0.2860 | 0.2615 | +0.0397 [+0.0114, +0.0682] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1101 | 0.1133 | +0.0563 [+0.0319, +0.0831] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.507 | 0.1068 | 0.0630 | +0.0066 [-0.0009, +0.0146] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0462, +0.2080] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0402, +0.0966] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2839 | 0.2213 |

## risk_gbm+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.424, 0.794] | 0.231 | 3.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 3.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 94 | 0.386 | 0.574 | 0.0564 | +0.0150 [+0.0075, +0.0232] | -0.0000 [-0.0057, +0.0060] | 0.842 | 0.363 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 139 | 0.424 | 0.424 | 0.0699 | +0.0012 [-0.0047, +0.0065] | -0.0088 [-0.0146, -0.0033] | 0.768 | 0.378 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 123 | 0.413 | 0.463 | 0.0696 | +0.0011 [-0.0040, +0.0060] | -0.0052 [-0.0103, -0.0004] | 0.732 | 0.375 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 121 | 0.420 | 0.479 | 0.0694 | +0.0014 [-0.0034, +0.0066] | -0.0070 [-0.0115, -0.0024] | 0.760 | 0.384 | no |
| 5 | 0.491 (147 of 1869 days never flag) | 133 | 0.377 | 0.391 | 0.0727 | -0.0018 [-0.0071, +0.0032] | -0.0093 [-0.0150, -0.0038] | 0.719 | 0.330 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.500 (climatology 0.512, difference -0.0122 [-0.1225, +0.0832]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0944, ΔBrier vs climatology +0.0351 [+0.0216, +0.0503], realised minus predicted -0.0146 [-0.0480, +0.0223]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.573 | 0.2844 | 0.2720 | +0.0393 [+0.0063, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2020 | 0.0159 | -0.0034 [-0.0161, +0.0083] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0363 | 0.0000 | +0.0103 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0095 | 0.0200 | +0.0005 [-0.0052, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0671 | 0.1165 | +0.0259 [+0.0045, +0.0515] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0211 | 0.0048 | +0.0073 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1291 | 0.0000 | +0.0063 [+0.0010, +0.0120] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1019 | 0.2439 | 0.0047 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.424 | 0.582 | 0.2866 | 0.2615 | +0.0385 [+0.0083, +0.0682] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1076 | 0.1133 | +0.0540 [+0.0316, +0.0791] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.500 | 0.1074 | 0.0630 | +0.0062 [-0.0014, +0.0143] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0518, +0.2102] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0379, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.363, 0.719] | 0.231 | 2.81 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.606] | 0.231 | 2.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 93 | 0.386 | 0.581 | 0.0559 | +0.0155 [+0.0082, +0.0237] | +0.0005 [-0.0056, +0.0068] | 0.849 | 0.363 | no |
| 2 | 0.716 (147 of 1872 days never flag) | 106 | 0.403 | 0.528 | 0.0622 | +0.0088 [+0.0023, +0.0156] | -0.0012 [-0.0077, +0.0056] | 0.805 | 0.374 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 90 | 0.333 | 0.511 | 0.0655 | +0.0052 [-0.0004, +0.0112] | -0.0011 [-0.0068, +0.0049] | 0.773 | 0.308 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 112 | 0.391 | 0.482 | 0.0636 | +0.0073 [+0.0014, +0.0130] | -0.0012 [-0.0070, +0.0047] | 0.794 | 0.358 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 133 | 0.435 | 0.451 | 0.0649 | +0.0060 [+0.0000, +0.0119] | -0.0015 [-0.0079, +0.0049] | 0.783 | 0.393 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0192, +0.2720]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0837, ΔBrier vs climatology +0.0458 [+0.0278, +0.0657], realised minus predicted -0.0358 [-0.0675, -0.0024]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.566 | 0.2828 | 0.2720 | +0.0391 [+0.0085, +0.0728] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2001 | 0.0159 | -0.0020 [-0.0133, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0362 | 0.0000 | +0.0103 [+0.0087, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0116 | 0.0200 | +0.0026 [-0.0025, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0675 | 0.1165 | +0.0265 [+0.0041, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0218 | 0.0048 | +0.0076 [+0.0057, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1294 | 0.0000 | +0.0062 [+0.0009, +0.0119] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0781 | 0.2439 | 0.0070 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.432 | 0.587 | 0.2860 | 0.2615 | +0.0397 [+0.0117, +0.0686] |
| day_type | month_end | 150 | 17 | 0.647 | 0.786 | 0.1101 | 0.1133 | +0.0563 [+0.0325, +0.0810] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.507 | 0.1068 | 0.0630 | +0.0066 [-0.0006, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0469, +0.2050] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0412, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2839 | 0.2213 |

## risk_gbm+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.351, 0.722] | 0.231 | 2.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.619] | 0.231 | 2.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 94 | 0.386 | 0.574 | 0.0564 | +0.0150 [+0.0080, +0.0231] | -0.0000 [-0.0060, +0.0060] | 0.842 | 0.363 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 112 | 0.403 | 0.500 | 0.0626 | +0.0085 [+0.0022, +0.0151] | -0.0015 [-0.0081, +0.0052] | 0.805 | 0.371 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 103 | 0.377 | 0.505 | 0.0656 | +0.0050 [-0.0009, +0.0111] | -0.0013 [-0.0073, +0.0050] | 0.769 | 0.347 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 108 | 0.399 | 0.509 | 0.0629 | +0.0080 [+0.0021, +0.0145] | -0.0005 [-0.0065, +0.0060] | 0.794 | 0.368 | no |
| 5 | 0.723 (147 of 1869 days never flag) | 129 | 0.428 | 0.457 | 0.0644 | +0.0065 [+0.0004, +0.0125] | -0.0010 [-0.0074, +0.0054] | 0.779 | 0.387 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1893 [+0.0398, +0.3290]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0839, ΔBrier vs climatology +0.0456 [+0.0277, +0.0660], realised minus predicted -0.0365 [-0.0667, -0.0047]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.573 | 0.2844 | 0.2720 | +0.0393 [+0.0072, +0.0745] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2020 | 0.0159 | -0.0034 [-0.0161, +0.0077] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0363 | 0.0000 | +0.0103 [+0.0086, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0095 | 0.0200 | +0.0005 [-0.0054, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0671 | 0.1165 | +0.0259 [+0.0048, +0.0531] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0211 | 0.0048 | +0.0073 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1291 | 0.0000 | +0.0063 [+0.0009, +0.0118] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1019 | 0.2439 | 0.0047 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.424 | 0.582 | 0.2866 | 0.2615 | +0.0385 [+0.0114, +0.0677] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1076 | 0.1133 | +0.0540 [+0.0323, +0.0775] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.500 | 0.1074 | 0.0630 | +0.0062 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2099 | 0.2903 | +0.1309 [+0.0513, +0.2113] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0387, +0.0972] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2837 | 0.2213 |

## risk_gbm+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.308, 0.704] | 0.231 | 2.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.192 | 2.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 120 | 0.436 | 0.508 | 0.0560 | +0.0154 [+0.0061, +0.0247] | +0.0003 [-0.0079, +0.0078] | 0.919 | 0.402 | no |
| 2 | 0.605 (147 of 1872 days never flag) | 129 | 0.432 | 0.465 | 0.0663 | +0.0047 [-0.0044, +0.0130] | -0.0053 [-0.0139, +0.0020] | 0.880 | 0.392 | no |
| 3 | 0.621 (147 of 1871 days never flag) | 126 | 0.449 | 0.492 | 0.0659 | +0.0048 [-0.0055, +0.0137] | -0.0015 [-0.0115, +0.0072] | 0.892 | 0.412 | no |
| 4 | 0.655 (147 of 1870 days never flag) | 119 | 0.428 | 0.496 | 0.0656 | +0.0052 [-0.0021, +0.0113] | -0.0033 [-0.0099, +0.0027] | 0.847 | 0.393 | no |
| 5 | 0.667 (147 of 1869 days never flag) | 115 | 0.406 | 0.487 | 0.0728 | -0.0019 [-0.0108, +0.0062] | -0.0094 [-0.0182, -0.0017] | 0.817 | 0.372 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.491 (climatology 0.512, difference -0.0213 [-0.1189, +0.0586]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0877, ΔBrier vs climatology +0.0417 [+0.0281, +0.0571], realised minus predicted +0.0232 [-0.0094, +0.0588]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.481 | 0.3126 | 0.2720 | +0.0169 [-0.0246, +0.0564] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0837 | 0.0159 | +0.0174 [-0.0067, +0.0366] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0006 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0000, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0778 | 0.1165 | +0.0277 [+0.0050, +0.0578] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0030 | 0.0048 | +0.0090 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0031 | 0.0000 | +0.0317 [+0.0253, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0494 | 0.2439 | 0.0189 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.513 | 0.3198 | 0.2615 | +0.0183 [-0.0178, +0.0529] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1059 | 0.1133 | +0.0577 [+0.0326, +0.0840] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.441 | 0.0796 | 0.0630 | +0.0063 [-0.0035, +0.0156] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0490, +0.2079] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0410, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.692] | 0.192 | 2.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.562] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0569 | +0.0145 [+0.0051, +0.0240] | -0.0006 [-0.0089, +0.0072] | 0.917 | 0.399 | no |
| 2 | 0.625 (147 of 1872 days never flag) | 117 | 0.403 | 0.479 | 0.0667 | +0.0044 [-0.0045, +0.0123] | -0.0057 [-0.0144, +0.0019] | 0.877 | 0.368 | no |
| 3 | 0.618 (147 of 1871 days never flag) | 119 | 0.428 | 0.496 | 0.0658 | +0.0049 [-0.0053, +0.0135] | -0.0014 [-0.0115, +0.0068] | 0.896 | 0.393 | no |
| 4 | 0.624 (147 of 1870 days never flag) | 121 | 0.435 | 0.496 | 0.0631 | +0.0078 [+0.0010, +0.0140] | -0.0007 [-0.0068, +0.0048] | 0.884 | 0.400 | no |
| 5 | 0.591 (147 of 1869 days never flag) | 108 | 0.370 | 0.472 | 0.0669 | +0.0040 [-0.0019, +0.0095] | -0.0035 [-0.0096, +0.0020] | 0.819 | 0.337 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.499 (climatology 0.512, difference -0.0135 [-0.1307, +0.0836]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0861, ΔBrier vs climatology +0.0434 [+0.0291, +0.0589], realised minus predicted +0.0215 [-0.0098, +0.0565]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.515 | 0.3148 | 0.2720 | +0.0153 [-0.0252, +0.0560] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0864 | 0.0159 | +0.0156 [-0.0099, +0.0360] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0007 | 0.0000 | +0.0137 [+0.0120, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0014 | 0.0200 | +0.0016 [-0.0034, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0775 | 0.1165 | +0.0273 [+0.0067, +0.0557] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0087 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0028 | 0.0000 | +0.0317 [+0.0247, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0732 | 0.2439 | 0.0166 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.541 | 0.3213 | 0.2615 | +0.0156 [-0.0205, +0.0507] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1035 | 0.1133 | +0.0558 [+0.0329, +0.0823] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.466 | 0.0805 | 0.0630 | +0.0054 [-0.0048, +0.0149] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0542, +0.2064] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0383, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.696] | 0.192 | 2.27 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.263, 0.667] | 0.192 | 2.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 120 | 0.436 | 0.508 | 0.0560 | +0.0154 [+0.0059, +0.0245] | +0.0003 [-0.0079, +0.0078] | 0.919 | 0.402 | no |
| 2 | 0.716 (147 of 1872 days never flag) | 111 | 0.446 | 0.559 | 0.0603 | +0.0108 [+0.0015, +0.0189] | +0.0008 [-0.0086, +0.0089] | 0.892 | 0.418 | no |
| 3 | 0.731 (147 of 1871 days never flag) | 117 | 0.420 | 0.496 | 0.0631 | +0.0076 [-0.0034, +0.0166] | +0.0013 [-0.0096, +0.0102] | 0.899 | 0.386 | no |
| 4 | 0.754 (147 of 1870 days never flag) | 108 | 0.406 | 0.519 | 0.0609 | +0.0099 [+0.0027, +0.0165] | +0.0014 [-0.0054, +0.0082] | 0.868 | 0.376 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 97 | 0.384 | 0.546 | 0.0658 | +0.0052 [-0.0041, +0.0131] | -0.0024 [-0.0106, +0.0053] | 0.856 | 0.359 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0210, +0.2697]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0768, ΔBrier vs climatology +0.0527 [+0.0344, +0.0728], realised minus predicted +0.0019 [-0.0281, +0.0322]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.481 | 0.3126 | 0.2720 | +0.0169 [-0.0237, +0.0566] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0837 | 0.0159 | +0.0174 [-0.0071, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0006 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0035 | 0.0200 | +0.0037 [-0.0003, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0778 | 0.1165 | +0.0277 [+0.0047, +0.0555] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0030 | 0.0048 | +0.0090 [+0.0072, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0031 | 0.0000 | +0.0317 [+0.0252, +0.0385] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0494 | 0.2439 | 0.0189 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.513 | 0.3198 | 0.2615 | +0.0183 [-0.0183, +0.0531] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1059 | 0.1133 | +0.0577 [+0.0329, +0.0831] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.441 | 0.0796 | 0.0630 | +0.0063 [-0.0039, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0483, +0.2074] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0427, +0.0968] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.682] | 0.192 | 2.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.192 | 2.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0569 | +0.0145 [+0.0051, +0.0242] | -0.0006 [-0.0089, +0.0074] | 0.917 | 0.399 | no |
| 2 | 0.625 (147 of 1872 days never flag) | 104 | 0.396 | 0.529 | 0.0608 | +0.0103 [+0.0013, +0.0185] | +0.0003 [-0.0086, +0.0084] | 0.893 | 0.367 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 111 | 0.420 | 0.523 | 0.0634 | +0.0073 [-0.0035, +0.0171] | +0.0010 [-0.0095, +0.0107] | 0.898 | 0.390 | no |
| 4 | 0.641 (147 of 1870 days never flag) | 109 | 0.420 | 0.532 | 0.0577 | +0.0131 [+0.0060, +0.0197] | +0.0047 [-0.0026, +0.0112] | 0.895 | 0.391 | no |
| 5 | 0.723 (147 of 1869 days never flag) | 111 | 0.435 | 0.541 | 0.0595 | +0.0114 [+0.0053, +0.0182] | +0.0039 [-0.0025, +0.0106] | 0.856 | 0.405 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1899 [+0.0427, +0.3224]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0774, ΔBrier vs climatology +0.0521 [+0.0340, +0.0716], realised minus predicted +0.0022 [-0.0268, +0.0317]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.515 | 0.3148 | 0.2720 | +0.0153 [-0.0263, +0.0564] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0864 | 0.0159 | +0.0156 [-0.0107, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0007 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0014 | 0.0200 | +0.0016 [-0.0033, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0775 | 0.1165 | +0.0273 [+0.0054, +0.0563] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0023 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0028 | 0.0000 | +0.0317 [+0.0248, +0.0383] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0732 | 0.2439 | 0.0166 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.541 | 0.3213 | 0.2615 | +0.0156 [-0.0213, +0.0519] |
| day_type | month_end | 150 | 17 | 0.588 | 0.769 | 0.1035 | 0.1133 | +0.0558 [+0.0323, +0.0818] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.466 | 0.0805 | 0.0630 | +0.0054 [-0.0047, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0543, +0.2097] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0390, +0.0977] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_gbm+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.696] | 0.231 | 3.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 3.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 156 | 0.486 | 0.436 | 0.0496 | +0.0218 [+0.0143, +0.0297] | +0.0067 [+0.0010, +0.0127] | 0.903 | 0.435 | no |
| 2 | 0.605 (147 of 1872 days never flag) | 135 | 0.396 | 0.407 | 0.0613 | +0.0097 [+0.0041, +0.0154] | -0.0003 [-0.0056, +0.0045] | 0.854 | 0.350 | no |
| 3 | 0.56 (147 of 1871 days never flag) | 169 | 0.529 | 0.432 | 0.0599 | +0.0108 [+0.0060, +0.0154] | +0.0045 [-0.0001, +0.0091] | 0.856 | 0.474 | no |
| 4 | 0.48 (147 of 1870 days never flag) | 124 | 0.442 | 0.492 | 0.0618 | +0.0091 [+0.0045, +0.0135] | +0.0006 [-0.0038, +0.0048] | 0.829 | 0.406 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 140 | 0.428 | 0.421 | 0.0692 | +0.0017 [-0.0037, +0.0067] | -0.0058 [-0.0117, -0.0003] | 0.782 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.492 (climatology 0.512, difference -0.0197 [-0.1117, +0.0624]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0898, ΔBrier vs climatology +0.0397 [+0.0271, +0.0539], realised minus predicted +0.0212 [-0.0113, +0.0580]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.410 | 0.2736 | 0.2720 | +0.0457 [+0.0147, +0.0775] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1223 | 0.0159 | +0.0209 [+0.0043, +0.0353] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0079 | 0.0000 | +0.0134 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0039 | 0.0200 | +0.0037 [-0.0000, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0755 | 0.1165 | +0.0300 [+0.0055, +0.0612] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0051 | 0.0048 | +0.0090 [+0.0072, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0504 | 0.0000 | +0.0282 [+0.0218, +0.0345] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0778 | 0.2439 | 0.0175 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.544 | 0.439 | 0.2818 | 0.2615 | +0.0459 [+0.0179, +0.0739] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1072 | 0.1133 | +0.0584 [+0.0347, +0.0842] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.375 | 0.0795 | 0.0630 | +0.0137 [+0.0063, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0485, +0.2109] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0409, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2722 | 0.2213 |

## risk_gbm+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.700] | 0.231 | 3.50 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 147 | 0.479 | 0.456 | 0.0504 | +0.0210 [+0.0137, +0.0295] | +0.0059 [-0.0001, +0.0122] | 0.897 | 0.432 | no |
| 2 | 0.452 (147 of 1872 days never flag) | 132 | 0.388 | 0.409 | 0.0617 | +0.0094 [+0.0036, +0.0151] | -0.0006 [-0.0063, +0.0046] | 0.849 | 0.343 | no |
| 3 | 0.726 (147 of 1871 days never flag) | 163 | 0.522 | 0.442 | 0.0600 | +0.0107 [+0.0055, +0.0155] | +0.0044 [-0.0003, +0.0092] | 0.857 | 0.469 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 126 | 0.449 | 0.492 | 0.0604 | +0.0105 [+0.0055, +0.0150] | +0.0020 [-0.0024, +0.0062] | 0.845 | 0.412 | no |
| 5 | 0.489 (147 of 1869 days never flag) | 129 | 0.384 | 0.411 | 0.0670 | +0.0039 [-0.0012, +0.0088] | -0.0036 [-0.0091, +0.0019] | 0.792 | 0.340 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.512, difference -0.0147 [-0.1229, +0.0768]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0872, ΔBrier vs climatology +0.0423 [+0.0285, +0.0569], realised minus predicted +0.0221 [-0.0105, +0.0568]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.431 | 0.2769 | 0.2720 | +0.0447 [+0.0131, +0.0776] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1254 | 0.0159 | +0.0193 [+0.0030, +0.0347] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0081 | 0.0000 | +0.0134 [+0.0117, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0018 | 0.0200 | +0.0016 [-0.0030, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0296 [+0.0063, +0.0590] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0044 | 0.0048 | +0.0087 [+0.0069, +0.0104] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0518 | 0.0000 | +0.0280 [+0.0216, +0.0343] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0976 | 0.2439 | 0.0158 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.456 | 0.2836 | 0.2615 | +0.0437 [+0.0161, +0.0738] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1047 | 0.1133 | +0.0561 [+0.0322, +0.0814] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.390 | 0.0807 | 0.0630 | +0.0130 [+0.0058, +0.0216] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0526, +0.2114] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0373, +0.0988] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2718 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.312, 0.690] | 0.231 | 3.38 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.654] | 0.231 | 2.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (126 of 1873 days never flag) | 156 | 0.486 | 0.436 | 0.0496 | +0.0218 [+0.0140, +0.0297] | +0.0067 [+0.0009, +0.0126] | 0.903 | 0.435 | no |
| 2 | 0.716 (147 of 1872 days never flag) | 95 | 0.403 | 0.589 | 0.0545 | +0.0165 [+0.0098, +0.0230] | +0.0065 [+0.0001, +0.0130] | 0.871 | 0.380 | no |
| 3 | 0.53 (147 of 1871 days never flag) | 108 | 0.391 | 0.500 | 0.0566 | +0.0141 [+0.0082, +0.0203] | +0.0078 [+0.0020, +0.0139] | 0.871 | 0.360 | no |
| 4 | 0.468 (147 of 1870 days never flag) | 120 | 0.391 | 0.450 | 0.0567 | +0.0141 [+0.0086, +0.0196] | +0.0056 [-0.0001, +0.0112] | 0.851 | 0.353 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 132 | 0.435 | 0.455 | 0.0618 | +0.0092 [+0.0032, +0.0154] | +0.0016 [-0.0048, +0.0078] | 0.829 | 0.393 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.661 (climatology 0.512, difference +0.1483 [+0.0178, +0.2693]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0776, ΔBrier vs climatology +0.0519 [+0.0344, +0.0709], realised minus predicted -0.0023 [-0.0330, +0.0273]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.410 | 0.2736 | 0.2720 | +0.0457 [+0.0136, +0.0778] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1223 | 0.0159 | +0.0209 [+0.0043, +0.0354] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0079 | 0.0000 | +0.0134 [+0.0118, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0039 | 0.0200 | +0.0037 [-0.0002, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0755 | 0.1165 | +0.0300 [+0.0052, +0.0623] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0051 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0504 | 0.0000 | +0.0282 [+0.0220, +0.0345] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0778 | 0.2439 | 0.0175 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.544 | 0.439 | 0.2818 | 0.2615 | +0.0459 [+0.0173, +0.0746] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1072 | 0.1133 | +0.0584 [+0.0337, +0.0833] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.375 | 0.0795 | 0.0630 | +0.0137 [+0.0064, +0.0215] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2213 | 0.2903 | +0.1280 [+0.0491, +0.2110] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0961 | 0.1461 | +0.0685 [+0.0424, +0.0948] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2722 | 0.2213 |

## risk_gbm+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.314, 0.692] | 0.231 | 3.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.611] | 0.231 | 2.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.65 (126 of 1873 days never flag) | 147 | 0.479 | 0.456 | 0.0504 | +0.0210 [+0.0132, +0.0291] | +0.0059 [+0.0001, +0.0120] | 0.897 | 0.432 | no |
| 2 | 0.653 (147 of 1872 days never flag) | 112 | 0.432 | 0.536 | 0.0550 | +0.0161 [+0.0094, +0.0227] | +0.0061 [-0.0005, +0.0123] | 0.871 | 0.402 | no |
| 3 | 0.599 (147 of 1871 days never flag) | 125 | 0.413 | 0.456 | 0.0569 | +0.0138 [+0.0077, +0.0201] | +0.0075 [+0.0016, +0.0135] | 0.866 | 0.374 | no |
| 4 | 0.537 (147 of 1870 days never flag) | 108 | 0.428 | 0.546 | 0.0546 | +0.0163 [+0.0100, +0.0226] | +0.0078 [+0.0015, +0.0143] | 0.863 | 0.399 | no |
| 5 | 0.723 (147 of 1869 days never flag) | 128 | 0.428 | 0.461 | 0.0594 | +0.0116 [+0.0054, +0.0178] | +0.0040 [-0.0024, +0.0106] | 0.832 | 0.388 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1899 [+0.0366, +0.3187]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0771, ΔBrier vs climatology +0.0524 [+0.0346, +0.0715], realised minus predicted +0.0003 [-0.0289, +0.0299]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.578 | 0.431 | 0.2769 | 0.2720 | +0.0447 [+0.0133, +0.0778] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1254 | 0.0159 | +0.0193 [+0.0024, +0.0338] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0081 | 0.0000 | +0.0134 [+0.0117, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0018 | 0.0200 | +0.0016 [-0.0031, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0296 [+0.0065, +0.0605] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0044 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0518 | 0.0000 | +0.0280 [+0.0218, +0.0342] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0976 | 0.2439 | 0.0158 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.456 | 0.2836 | 0.2615 | +0.0437 [+0.0145, +0.0740] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1047 | 0.1133 | +0.0561 [+0.0309, +0.0812] |
| day_type | ordinary | 1603 | 101 | 0.475 | 0.390 | 0.0807 | 0.0630 | +0.0130 [+0.0055, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.2099 | 0.2903 | +0.1309 [+0.0542, +0.2103] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0988 | 0.1461 | +0.0683 [+0.0380, +0.0994] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2718 | 0.2213 |

## risk_gbm+settle+h41 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.115 | 1.35 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.568] | 0.115 | 1.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.121 (105 of 1873 days never flag) | 76 | 0.293 | 0.539 | 0.0580 | +0.0134 [+0.0080, +0.0191] | -0.0017 [-0.0097, +0.0061] | 0.642 | 0.273 | no |
| 2 | 0.256 (147 of 1872 days never flag) | 63 | 0.273 | 0.603 | 0.0591 | +0.0119 [+0.0070, +0.0168] | +0.0019 [-0.0050, +0.0085] | 0.639 | 0.259 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 65 | 0.261 | 0.554 | 0.0605 | +0.0102 [+0.0048, +0.0154] | +0.0039 [-0.0027, +0.0099] | 0.636 | 0.244 | no |
| 4 | 0.27 (147 of 1870 days never flag) | 64 | 0.268 | 0.578 | 0.0587 | +0.0121 [+0.0071, +0.0170] | +0.0037 [-0.0025, +0.0096] | 0.633 | 0.253 | no |
| 5 | 0.27 (147 of 1869 days never flag) | 62 | 0.254 | 0.565 | 0.0596 | +0.0114 [+0.0065, +0.0160] | +0.0038 [-0.0022, +0.0095] | 0.632 | 0.238 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.702 (climatology 0.512, difference +0.1902 [+0.0363, +0.3262]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0855, ΔBrier vs climatology +0.0439 [+0.0317, +0.0572], realised minus predicted +0.0590 [+0.0302, +0.0902]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.585 | 0.0975 | 0.2720 | +0.0019 [-0.0211, +0.0239] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0167 | 0.0159 | +0.0382 [+0.0294, +0.0470] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0007 | 0.0000 | +0.0137 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0007 | 0.0200 | +0.0016 [-0.0030, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.643 | 0.0386 | 0.1165 | +0.0168 [+0.0005, +0.0385] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0014 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0018 | 0.0000 | +0.0317 [+0.0251, +0.0382] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0479 | 0.2439 | -0.0053 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.588 | 0.0985 | 0.2615 | +0.0133 [-0.0073, +0.0339] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.0961 | 0.1133 | +0.0522 [+0.0290, +0.0759] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.500 | 0.0133 | 0.0630 | +0.0045 [-0.0005, +0.0095] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2099 | 0.2903 | +0.1309 [+0.0527, +0.2129] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.0988 | 0.1461 | +0.0683 [+0.0393, +0.0972] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2001 | 0.2213 |

## risk_gbm_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.154 | 1.46 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.158, 0.460] | 0.115 | 1.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.187 (105 of 1873 days never flag) | 80 | 0.300 | 0.525 | 0.0586 | +0.0129 [+0.0079, +0.0176] | -0.0022 [-0.0100, +0.0046] | 0.643 | 0.278 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 49 | 0.173 | 0.490 | 0.0686 | +0.0024 [-0.0042, +0.0085] | -0.0076 [-0.0164, +0.0001] | 0.578 | 0.158 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 57 | 0.174 | 0.421 | 0.0674 | +0.0033 [-0.0034, +0.0093] | -0.0030 [-0.0113, +0.0038] | 0.580 | 0.155 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 57 | 0.203 | 0.491 | 0.0660 | +0.0048 [-0.0017, +0.0111] | -0.0036 [-0.0111, +0.0031] | 0.580 | 0.186 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 49 | 0.152 | 0.429 | 0.0696 | +0.0013 [-0.0055, +0.0071] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.136 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.539 (climatology 0.512, difference +0.0266 [-0.1146, +0.1515]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1041, ΔBrier vs climatology +0.0253 [+0.0163, +0.0348], realised minus predicted +0.0899 [+0.0555, +0.1265]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.596 | 0.0972 | 0.2720 | -0.0015 [-0.0206, +0.0159] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0237 | 0.0159 | +0.0335 [+0.0228, +0.0443] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0038 [+0.0001, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0377 | 0.1165 | +0.0199 [+0.0032, +0.0405] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0058 | 0.0000 | +0.0309 [+0.0245, +0.0370] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0203 | 0.2439 | 0.0057 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.580 | 0.1021 | 0.2615 | +0.0089 [-0.0095, +0.0255] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.1003 | 0.1133 | +0.0379 [+0.0140, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0129 | 0.0630 | +0.0054 [+0.0003, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.556 | 0.2030 | 0.2903 | +0.1126 [+0.0332, +0.1946] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1168 | 0.1461 | +0.0706 [+0.0489, +0.0946] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2084 | 0.2213 |

## risk_gbm_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.476, 0.824] | 0.231 | 2.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.619] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 155 | 0.579 | 0.523 | 0.0486 | +0.0228 [+0.0155, +0.0309] | +0.0077 [+0.0030, +0.0129] | 0.899 | 0.536 | no |
| 2 | 0.315 (147 of 1872 days never flag) | 137 | 0.439 | 0.445 | 0.0601 | +0.0110 [+0.0069, +0.0151] | +0.0010 [-0.0021, +0.0039] | 0.836 | 0.395 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 134 | 0.428 | 0.440 | 0.0613 | +0.0094 [+0.0056, +0.0132] | +0.0031 [+0.0001, +0.0061] | 0.812 | 0.384 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 110 | 0.420 | 0.527 | 0.0585 | +0.0123 [+0.0074, +0.0173] | +0.0038 [+0.0007, +0.0072] | 0.838 | 0.390 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 119 | 0.362 | 0.420 | 0.0630 | +0.0080 [+0.0035, +0.0120] | +0.0004 [-0.0026, +0.0034] | 0.782 | 0.322 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.534 (climatology 0.512, difference +0.0222 [-0.1006, +0.1277]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0847, ΔBrier vs climatology +0.0448 [+0.0306, +0.0605], realised minus predicted +0.0098 [-0.0214, +0.0442]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0542 [+0.0257, +0.0845] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1263 | 0.0159 | +0.0173 [+0.0016, +0.0307] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0321 | 0.0200 | +0.0008 [-0.0060, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.1139 | 0.1165 | +0.0318 [+0.0048, +0.0663] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0225 | 0.0048 | +0.0080 [+0.0057, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0691 | 0.0000 | +0.0246 [+0.0189, +0.0302] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1409 | 0.2439 | 0.0481 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.632 | 0.534 | 0.2526 | 0.2615 | +0.0517 [+0.0258, +0.0791] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1097 | 0.1133 | +0.0430 [+0.0192, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.479 | 0.0863 | 0.0630 | +0.0165 [+0.0094, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0371, +0.1936] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0951] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.231 | 2.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.556] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 134 | 0.507 | 0.530 | 0.0505 | +0.0209 [+0.0140, +0.0279] | +0.0058 [+0.0012, +0.0105] | 0.805 | 0.471 | no |
| 2 | 0.315 (147 of 1872 days never flag) | 122 | 0.388 | 0.443 | 0.0623 | +0.0087 [+0.0040, +0.0133] | -0.0013 [-0.0054, +0.0025] | 0.749 | 0.349 | no |
| 3 | 0.25 (147 of 1871 days never flag) | 130 | 0.399 | 0.423 | 0.0613 | +0.0094 [+0.0044, +0.0142] | +0.0030 [-0.0014, +0.0070] | 0.746 | 0.355 | no |
| 4 | 0.265 (147 of 1870 days never flag) | 116 | 0.420 | 0.500 | 0.0594 | +0.0114 [+0.0060, +0.0167] | +0.0030 [-0.0008, +0.0067] | 0.763 | 0.387 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 107 | 0.333 | 0.430 | 0.0636 | +0.0073 [+0.0021, +0.0121] | -0.0002 [-0.0043, +0.0036] | 0.740 | 0.298 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.544 (climatology 0.512, difference +0.0322 [-0.0976, +0.1388]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0429 [+0.0300, +0.0571], realised minus predicted +0.0588 [+0.0304, +0.0903]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.559 | 0.1689 | 0.2720 | +0.0386 [+0.0127, +0.0658] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.0313 | 0.0159 | +0.0263 [+0.0081, +0.0404] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0145 | 0.0200 | +0.0009 [-0.0065, +0.0059] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.0889 | 0.1165 | +0.0310 [+0.0055, +0.0607] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0086 | 0.0048 | +0.0082 [+0.0059, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0070 | 0.0000 | +0.0308 [+0.0244, +0.0366] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1098 | 0.2439 | 0.0458 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.543 | 0.1761 | 0.2615 | +0.0401 [+0.0146, +0.0649] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1041 | 0.1133 | +0.0436 [+0.0174, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.479 | 0.0421 | 0.0630 | +0.0143 [+0.0078, +0.0210] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0341, +0.1908] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0952] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3903 | 0.2213 |

## risk_gbm_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.800] | 0.231 | 2.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.600] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 135 | 0.507 | 0.526 | 0.0487 | +0.0227 [+0.0162, +0.0302] | +0.0076 [+0.0030, +0.0127] | 0.893 | 0.470 | no |
| 2 | 0.276 (147 of 1872 days never flag) | 134 | 0.439 | 0.455 | 0.0594 | +0.0116 [+0.0085, +0.0151] | +0.0016 [-0.0017, +0.0051] | 0.820 | 0.397 | no |
| 3 | 0.257 (147 of 1871 days never flag) | 131 | 0.406 | 0.427 | 0.0598 | +0.0109 [+0.0075, +0.0145] | +0.0045 [+0.0011, +0.0085] | 0.802 | 0.363 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 126 | 0.442 | 0.484 | 0.0567 | +0.0141 [+0.0099, +0.0183] | +0.0056 [+0.0026, +0.0089] | 0.835 | 0.405 | no |
| 5 | 0.265 (147 of 1869 days never flag) | 113 | 0.370 | 0.451 | 0.0613 | +0.0096 [+0.0062, +0.0130] | +0.0021 [-0.0010, +0.0050] | 0.772 | 0.334 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.535 (climatology 0.512, difference +0.0228 [-0.0941, +0.1215]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0857, ΔBrier vs climatology +0.0437 [+0.0300, +0.0589], realised minus predicted +0.0197 [-0.0113, +0.0551]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.523 | 0.2205 | 0.2720 | +0.0484 [+0.0229, +0.0773] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1138 | 0.0159 | +0.0229 [+0.0100, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0155 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0227 | 0.0200 | +0.0029 [-0.0014, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.667 | 0.0976 | 0.1165 | +0.0320 [+0.0078, +0.0614] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0170 | 0.0048 | +0.0090 [+0.0071, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0607 | 0.0000 | +0.0257 [+0.0200, +0.0314] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1137 | 0.2439 | 0.0482 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.523 | 0.2331 | 0.2615 | +0.0486 [+0.0250, +0.0746] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1082 | 0.1133 | +0.0422 [+0.0179, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.474 | 0.0748 | 0.0630 | +0.0165 [+0.0103, +0.0237] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0372, +0.1918] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1168 | 0.1461 | +0.0706 [+0.0489, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0837 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2566 | 0.2213 |

## risk_gbm_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.833] | 0.231 | 3.00 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.609] | 0.231 | 3.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 153 | 0.579 | 0.529 | 0.0478 | +0.0237 [+0.0164, +0.0313] | +0.0086 [+0.0041, +0.0137] | 0.914 | 0.537 | no |
| 2 | 0.315 (147 of 1872 days never flag) | 139 | 0.446 | 0.446 | 0.0592 | +0.0119 [+0.0075, +0.0160] | +0.0019 [-0.0012, +0.0049] | 0.875 | 0.402 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 138 | 0.435 | 0.435 | 0.0594 | +0.0113 [+0.0077, +0.0153] | +0.0050 [+0.0020, +0.0081] | 0.862 | 0.390 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 110 | 0.435 | 0.545 | 0.0571 | +0.0138 [+0.0093, +0.0187] | +0.0053 [+0.0024, +0.0087] | 0.874 | 0.406 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 116 | 0.362 | 0.431 | 0.0618 | +0.0091 [+0.0049, +0.0132] | +0.0016 [-0.0015, +0.0046] | 0.846 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.534 (climatology 0.512, difference +0.0222 [-0.0983, +0.1196]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0831, ΔBrier vs climatology +0.0463 [+0.0324, +0.0618], realised minus predicted +0.0369 [+0.0061, +0.0695]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.549 | 0.2386 | 0.2720 | +0.0542 [+0.0277, +0.0836] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1260 | 0.0159 | +0.0173 [+0.0018, +0.0320] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0043 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0022 | 0.0200 | +0.0038 [-0.0002, +0.0069] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.571 | 0.0974 | 0.1165 | +0.0343 [+0.0077, +0.0644] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0009 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0691 | 0.0000 | +0.0246 [+0.0191, +0.0303] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1409 | 0.2439 | 0.0481 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.632 | 0.534 | 0.2526 | 0.2615 | +0.0517 [+0.0265, +0.0789] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1076 | 0.1133 | +0.0431 [+0.0173, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.487 | 0.0725 | 0.0630 | +0.0175 [+0.0106, +0.0249] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0335, +0.1904] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0931] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3463 | 0.2213 |

## risk_gbm_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.718] | 0.192 | 2.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.462] | 0.154 | 1.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.329 (105 of 1873 days never flag) | 128 | 0.479 | 0.523 | 0.0492 | +0.0222 [+0.0169, +0.0277] | +0.0071 [+0.0023, +0.0116] | 0.908 | 0.443 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 65 | 0.230 | 0.492 | 0.0603 | +0.0107 [+0.0074, +0.0138] | +0.0007 [-0.0037, +0.0045] | 0.845 | 0.211 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 52 | 0.188 | 0.500 | 0.0605 | +0.0102 [+0.0067, +0.0135] | +0.0039 [-0.0003, +0.0077] | 0.824 | 0.173 | no |
| 4 | 0.25 (147 of 1870 days never flag) | 62 | 0.239 | 0.532 | 0.0584 | +0.0125 [+0.0085, +0.0165] | +0.0040 [+0.0001, +0.0077] | 0.841 | 0.222 | no |
| 5 | 0.25 (147 of 1869 days never flag) | 62 | 0.181 | 0.403 | 0.0624 | +0.0085 [+0.0051, +0.0118] | +0.0010 [-0.0028, +0.0044] | 0.791 | 0.160 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.526 (climatology 0.512, difference +0.0141 [-0.1025, +0.1244]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0897, ΔBrier vs climatology +0.0398 [+0.0288, +0.0513], realised minus predicted +0.0507 [+0.0176, +0.0856]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.576 | 0.1679 | 0.2720 | +0.0397 [+0.0236, +0.0565] |
| regime | 2020 | 251 | 4 | 0.250 | 0.083 | 0.0750 | 0.0159 | +0.0305 [+0.0195, +0.0408] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0032 [-0.0013, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.545 | 0.0758 | 0.1165 | +0.0324 [+0.0085, +0.0609] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0117 | 0.0048 | +0.0092 [+0.0073, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0375 | 0.0000 | +0.0293 [+0.0233, +0.0352] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0806 | 0.2439 | 0.0353 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.551 | 0.1774 | 0.2615 | +0.0449 [+0.0275, +0.0625] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1050 | 0.1133 | +0.0408 [+0.0165, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.494 | 0.0496 | 0.0630 | +0.0161 [+0.0117, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2030 | 0.2903 | +0.1126 [+0.0374, +0.1919] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2254 | 0.2213 |

## risk_gbm_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.385, 0.767] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.567] | 0.231 | 2.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (105 of 1873 days never flag) | 135 | 0.514 | 0.533 | 0.0615 | +0.0099 [+0.0001, +0.0193] | -0.0051 [-0.0140, +0.0029] | 0.874 | 0.478 | no |
| 2 | 0.603 (147 of 1872 days never flag) | 109 | 0.374 | 0.477 | 0.0716 | -0.0006 [-0.0096, +0.0072] | -0.0106 [-0.0192, -0.0031] | 0.817 | 0.341 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 121 | 0.399 | 0.455 | 0.0733 | -0.0026 [-0.0115, +0.0051] | -0.0089 [-0.0175, -0.0013] | 0.796 | 0.360 | no |
| 4 | 0.643 (147 of 1870 days never flag) | 96 | 0.362 | 0.521 | 0.0694 | +0.0015 [-0.0058, +0.0085] | -0.0070 [-0.0137, -0.0006] | 0.823 | 0.336 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 102 | 0.355 | 0.480 | 0.0728 | -0.0019 [-0.0084, +0.0035] | -0.0094 [-0.0158, -0.0040] | 0.770 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.501 (climatology 0.512, difference -0.0110 [-0.1232, +0.0940]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0224, +0.0512], realised minus predicted +0.0046 [-0.0308, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.3131 | 0.2720 | +0.0099 [-0.0341, +0.0495] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2009 | 0.0159 | -0.0101 [-0.0343, +0.0089] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0027 [-0.0027, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0674 | 0.1165 | +0.0312 [+0.0072, +0.0606] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0072 | 0.0048 | +0.0086 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1136 | 0.0000 | +0.0113 [+0.0058, +0.0169] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0972 | 0.2439 | 0.0369 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.533 | 0.3157 | 0.2615 | +0.0098 [-0.0291, +0.0446] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1110 | 0.1133 | +0.0404 [+0.0156, +0.0675] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.490 | 0.1027 | 0.0630 | +0.0017 [-0.0087, +0.0113] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0339, +0.1905] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0492, +0.0923] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2962 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.368, 0.778] | 0.231 | 3.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.182, 0.517] | 0.192 | 2.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 161 | 0.579 | 0.503 | 0.0617 | +0.0097 [-0.0002, +0.0192] | -0.0054 [-0.0137, +0.0022] | 0.874 | 0.532 | no |
| 2 | 0.607 (147 of 1872 days never flag) | 110 | 0.367 | 0.464 | 0.0721 | -0.0011 [-0.0095, +0.0068] | -0.0111 [-0.0191, -0.0036] | 0.814 | 0.333 | no |
| 3 | 0.6 (147 of 1871 days never flag) | 118 | 0.391 | 0.458 | 0.0728 | -0.0021 [-0.0122, +0.0057] | -0.0084 [-0.0180, -0.0009] | 0.797 | 0.354 | no |
| 4 | 0.588 (147 of 1870 days never flag) | 99 | 0.370 | 0.515 | 0.0705 | +0.0003 [-0.0075, +0.0073] | -0.0082 [-0.0152, -0.0014] | 0.819 | 0.342 | no |
| 5 | 0.575 (147 of 1869 days never flag) | 105 | 0.355 | 0.467 | 0.0729 | -0.0020 [-0.0083, +0.0037] | -0.0095 [-0.0156, -0.0038] | 0.771 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.498 (climatology 0.512, difference -0.0138 [-0.1284, +0.0885]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0918, ΔBrier vs climatology +0.0377 [+0.0232, +0.0544], realised minus predicted +0.0039 [-0.0299, +0.0400]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.487 | 0.3159 | 0.2720 | +0.0093 [-0.0342, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1988 | 0.0159 | -0.0092 [-0.0323, +0.0093] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0045 | 0.0200 | -0.0001 [-0.0066, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0654 | 0.1165 | +0.0318 [+0.0097, +0.0597] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0080 [+0.0058, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1120 | 0.0000 | +0.0117 [+0.0061, +0.0177] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1019 | 0.2439 | 0.0494 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.648 | 0.503 | 0.3169 | 0.2615 | +0.0086 [-0.0288, +0.0447] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1089 | 0.1133 | +0.0435 [+0.0219, +0.0664] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.450 | 0.1032 | 0.0630 | +0.0011 [-0.0098, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0365, +0.1928] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0943] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.308, 0.682] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.619] | 0.192 | 2.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (105 of 1873 days never flag) | 135 | 0.514 | 0.533 | 0.0615 | +0.0099 [+0.0001, +0.0193] | -0.0051 [-0.0137, +0.0026] | 0.874 | 0.478 | no |
| 2 | 0.599 (147 of 1872 days never flag) | 104 | 0.424 | 0.567 | 0.0650 | +0.0060 [-0.0035, +0.0153] | -0.0040 [-0.0134, +0.0044] | 0.846 | 0.398 | no |
| 3 | 0.593 (147 of 1871 days never flag) | 115 | 0.435 | 0.522 | 0.0673 | +0.0034 [-0.0061, +0.0122] | -0.0029 [-0.0123, +0.0059] | 0.830 | 0.403 | no |
| 4 | 0.765 (147 of 1870 days never flag) | 115 | 0.442 | 0.530 | 0.0650 | +0.0059 [-0.0023, +0.0133] | -0.0026 [-0.0109, +0.0049] | 0.843 | 0.411 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 104 | 0.384 | 0.510 | 0.0665 | +0.0044 [-0.0025, +0.0109] | -0.0031 [-0.0102, +0.0032] | 0.819 | 0.355 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1658 [+0.0518, +0.2840]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0450 [+0.0244, +0.0673], realised minus predicted -0.0207 [-0.0524, +0.0120]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.3131 | 0.2720 | +0.0099 [-0.0329, +0.0526] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2009 | 0.0159 | -0.0101 [-0.0344, +0.0092] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0027 [-0.0021, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0674 | 0.1165 | +0.0312 [+0.0066, +0.0611] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0072 | 0.0048 | +0.0086 [+0.0068, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1136 | 0.0000 | +0.0113 [+0.0059, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0972 | 0.2439 | 0.0369 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.533 | 0.3157 | 0.2615 | +0.0098 [-0.0290, +0.0465] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1110 | 0.1133 | +0.0404 [+0.0156, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.490 | 0.1027 | 0.0630 | +0.0017 [-0.0088, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0359, +0.1919] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0945] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2962 | 0.2213 |

## risk_gbm_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.345, 0.727] | 0.231 | 3.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.231, 0.611] | 0.192 | 2.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (105 of 1873 days never flag) | 161 | 0.579 | 0.503 | 0.0617 | +0.0097 [-0.0000, +0.0195] | -0.0054 [-0.0136, +0.0025] | 0.874 | 0.532 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 119 | 0.432 | 0.504 | 0.0658 | +0.0053 [-0.0035, +0.0138] | -0.0047 [-0.0135, +0.0034] | 0.839 | 0.398 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 92 | 0.377 | 0.565 | 0.0669 | +0.0038 [-0.0052, +0.0127] | -0.0025 [-0.0116, +0.0060] | 0.825 | 0.354 | no |
| 4 | 0.713 (147 of 1870 days never flag) | 107 | 0.420 | 0.542 | 0.0649 | +0.0060 [-0.0025, +0.0146] | -0.0025 [-0.0106, +0.0061] | 0.845 | 0.392 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 116 | 0.442 | 0.526 | 0.0662 | +0.0047 [-0.0020, +0.0114] | -0.0028 [-0.0094, +0.0041] | 0.821 | 0.410 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.718 (climatology 0.512, difference +0.2062 [+0.0614, +0.3424]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0831, ΔBrier vs climatology +0.0464 [+0.0271, +0.0663], realised minus predicted -0.0194 [-0.0506, +0.0131]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.716 | 0.487 | 0.3159 | 0.2720 | +0.0093 [-0.0343, +0.0511] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1988 | 0.0159 | -0.0092 [-0.0313, +0.0102] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0105, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0045 | 0.0200 | -0.0001 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0654 | 0.1165 | +0.0318 [+0.0096, +0.0601] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0066 | 0.0048 | +0.0080 [+0.0058, +0.0099] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1120 | 0.0000 | +0.0117 [+0.0058, +0.0179] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.1019 | 0.2439 | 0.0494 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.648 | 0.503 | 0.3169 | 0.2615 | +0.0086 [-0.0288, +0.0458] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1089 | 0.1133 | +0.0435 [+0.0210, +0.0666] |
| day_type | ordinary | 1603 | 101 | 0.574 | 0.450 | 0.1032 | 0.0630 | +0.0011 [-0.0096, +0.0114] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0325, +0.1916] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0970] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2893 | 0.2213 |

## risk_gbm_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.423, 0.800] | 0.231 | 3.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.231 | 3.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 151 | 0.571 | 0.530 | 0.0569 | +0.0145 [+0.0069, +0.0226] | -0.0006 [-0.0069, +0.0054] | 0.852 | 0.530 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 117 | 0.353 | 0.419 | 0.0698 | +0.0013 [-0.0041, +0.0065] | -0.0087 [-0.0146, -0.0032] | 0.773 | 0.313 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 122 | 0.406 | 0.459 | 0.0706 | +0.0000 [-0.0047, +0.0044] | -0.0063 [-0.0112, -0.0017] | 0.726 | 0.368 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 118 | 0.406 | 0.475 | 0.0683 | +0.0025 [-0.0028, +0.0075] | -0.0059 [-0.0110, -0.0011] | 0.768 | 0.370 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 130 | 0.370 | 0.392 | 0.0728 | -0.0019 [-0.0073, +0.0032] | -0.0094 [-0.0153, -0.0038] | 0.709 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.497 (climatology 0.512, difference -0.0153 [-0.1294, +0.0940]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0960, ΔBrier vs climatology +0.0335 [+0.0199, +0.0483], realised minus predicted -0.0133 [-0.0493, +0.0253]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.519 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0687] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2090 | 0.0159 | -0.0081 [-0.0241, +0.0060] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0027 [-0.0030, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0662 | 0.1165 | +0.0290 [+0.0078, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0206 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1332 | 0.0000 | +0.0055 [+0.0001, +0.0108] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0744 | 0.2439 | 0.0157 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.530 | 0.2903 | 0.2615 | +0.0341 [+0.0043, +0.0649] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1118 | 0.1133 | +0.0396 [+0.0167, +0.0640] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.491 | 0.1070 | 0.0630 | +0.0071 [-0.0005, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0356, +0.1888] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1168 | 0.1461 | +0.0706 [+0.0484, +0.0944] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2920 | 0.2213 |

## risk_gbm_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.375, 0.774] | 0.231 | 3.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.618] | 0.231 | 3.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 173 | 0.600 | 0.486 | 0.0572 | +0.0142 [+0.0066, +0.0228] | -0.0009 [-0.0066, +0.0054] | 0.850 | 0.549 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 115 | 0.345 | 0.417 | 0.0703 | +0.0008 [-0.0050, +0.0063] | -0.0092 [-0.0151, -0.0033] | 0.770 | 0.307 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 122 | 0.413 | 0.467 | 0.0701 | +0.0006 [-0.0040, +0.0050] | -0.0058 [-0.0108, -0.0009] | 0.728 | 0.376 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 116 | 0.406 | 0.483 | 0.0695 | +0.0013 [-0.0038, +0.0063] | -0.0071 [-0.0122, -0.0021] | 0.762 | 0.371 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 133 | 0.377 | 0.391 | 0.0729 | -0.0020 [-0.0078, +0.0030] | -0.0095 [-0.0155, -0.0039] | 0.709 | 0.330 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.495 (climatology 0.512, difference -0.0169 [-0.1304, +0.0848]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0950, ΔBrier vs climatology +0.0345 [+0.0206, +0.0496], realised minus predicted -0.0138 [-0.0497, +0.0250]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.481 | 0.2869 | 0.2720 | +0.0353 [+0.0025, +0.0716] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2069 | 0.0159 | -0.0072 [-0.0222, +0.0072] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0087, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0090 | 0.0200 | -0.0000 [-0.0064, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0642 | 0.1165 | +0.0297 [+0.0090, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0200 | 0.0048 | +0.0076 [+0.0055, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1316 | 0.0000 | +0.0059 [+0.0008, +0.0116] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0790 | 0.2439 | 0.0282 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.486 | 0.2915 | 0.2615 | +0.0329 [+0.0033, +0.0651] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1096 | 0.1133 | +0.0427 [+0.0224, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.441 | 0.1075 | 0.0630 | +0.0065 [-0.0011, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0307, +0.1935] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0475, +0.0966] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2851 | 0.2213 |

## risk_gbm_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.318, 0.680] | 0.231 | 2.77 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.611] | 0.231 | 2.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 151 | 0.571 | 0.530 | 0.0569 | +0.0145 [+0.0068, +0.0228] | -0.0006 [-0.0065, +0.0058] | 0.852 | 0.530 | no |
| 2 | 0.599 (147 of 1872 days never flag) | 117 | 0.432 | 0.513 | 0.0624 | +0.0087 [+0.0018, +0.0158] | -0.0013 [-0.0085, +0.0056] | 0.815 | 0.399 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 112 | 0.442 | 0.545 | 0.0641 | +0.0066 [+0.0004, +0.0131] | +0.0003 [-0.0061, +0.0067] | 0.774 | 0.413 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 112 | 0.413 | 0.509 | 0.0636 | +0.0073 [+0.0010, +0.0133] | -0.0012 [-0.0076, +0.0051] | 0.795 | 0.381 | no |
| 5 | 0.655 (147 of 1869 days never flag) | 129 | 0.413 | 0.442 | 0.0662 | +0.0047 [-0.0018, +0.0110] | -0.0029 [-0.0094, +0.0040] | 0.772 | 0.371 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1665 [+0.0511, +0.2853]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0860, ΔBrier vs climatology +0.0435 [+0.0244, +0.0650], realised minus predicted -0.0400 [-0.0718, -0.0060]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.676 | 0.519 | 0.2841 | 0.2720 | +0.0360 [+0.0036, +0.0706] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.2090 | 0.0159 | -0.0081 [-0.0243, +0.0055] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0027 [-0.0022, +0.0067] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0662 | 0.1165 | +0.0290 [+0.0070, +0.0552] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0206 | 0.0048 | +0.0082 [+0.0065, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1332 | 0.0000 | +0.0055 [+0.0003, +0.0109] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0744 | 0.2439 | 0.0157 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.530 | 0.2903 | 0.2615 | +0.0341 [+0.0033, +0.0648] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1118 | 0.1133 | +0.0396 [+0.0164, +0.0653] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.491 | 0.1070 | 0.0630 | +0.0071 [-0.0006, +0.0155] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0339, +0.1887] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1168 | 0.1461 | +0.0706 [+0.0478, +0.0937] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2920 | 0.2213 |

## risk_gbm_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.727] | 0.231 | 3.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.233, 0.616] | 0.231 | 3.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (105 of 1873 days never flag) | 173 | 0.600 | 0.486 | 0.0572 | +0.0142 [+0.0067, +0.0222] | -0.0009 [-0.0067, +0.0050] | 0.850 | 0.549 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 104 | 0.374 | 0.500 | 0.0631 | +0.0079 [+0.0013, +0.0143] | -0.0021 [-0.0088, +0.0044] | 0.805 | 0.344 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 98 | 0.391 | 0.551 | 0.0637 | +0.0070 [+0.0011, +0.0134] | +0.0007 [-0.0054, +0.0074] | 0.768 | 0.366 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 106 | 0.399 | 0.519 | 0.0635 | +0.0074 [+0.0008, +0.0140] | -0.0011 [-0.0079, +0.0061] | 0.798 | 0.369 | no |
| 5 | 0.528 (147 of 1869 days never flag) | 142 | 0.442 | 0.430 | 0.0659 | +0.0050 [-0.0014, +0.0111] | -0.0025 [-0.0093, +0.0042] | 0.773 | 0.395 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.512, difference +0.2074 [+0.0600, +0.3396]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0849, ΔBrier vs climatology +0.0446 [+0.0268, +0.0642], realised minus predicted -0.0386 [-0.0698, -0.0044]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.725 | 0.481 | 0.2869 | 0.2720 | +0.0353 [+0.0035, +0.0676] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2069 | 0.0159 | -0.0072 [-0.0222, +0.0062] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0090 | 0.0200 | -0.0000 [-0.0062, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0642 | 0.1165 | +0.0297 [+0.0093, +0.0557] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0200 | 0.0048 | +0.0076 [+0.0056, +0.0093] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1316 | 0.0000 | +0.0059 [+0.0008, +0.0116] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0790 | 0.2439 | 0.0282 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.672 | 0.486 | 0.2915 | 0.2615 | +0.0329 [+0.0040, +0.0629] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1096 | 0.1133 | +0.0427 [+0.0207, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.594 | 0.441 | 0.1075 | 0.0630 | +0.0065 [-0.0010, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0329, +0.1885] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1136 | 0.1461 | +0.0711 [+0.0481, +0.0952] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2851 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.235, 0.625] | 0.231 | 3.08 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.485] | 0.231 | 2.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (126 of 1873 days never flag) | 155 | 0.536 | 0.484 | 0.0571 | +0.0143 [+0.0046, +0.0237] | -0.0008 [-0.0089, +0.0068] | 0.920 | 0.490 | no |
| 2 | 0.603 (147 of 1872 days never flag) | 114 | 0.403 | 0.491 | 0.0664 | +0.0047 [-0.0048, +0.0124] | -0.0053 [-0.0141, +0.0022] | 0.879 | 0.369 | no |
| 3 | 0.621 (147 of 1871 days never flag) | 124 | 0.428 | 0.476 | 0.0668 | +0.0039 [-0.0060, +0.0125] | -0.0024 [-0.0117, +0.0057] | 0.891 | 0.390 | no |
| 4 | 0.643 (147 of 1870 days never flag) | 102 | 0.362 | 0.490 | 0.0647 | +0.0061 [-0.0011, +0.0126] | -0.0023 [-0.0090, +0.0037] | 0.855 | 0.332 | no |
| 5 | 0.683 (147 of 1869 days never flag) | 96 | 0.348 | 0.500 | 0.0727 | -0.0018 [-0.0108, +0.0060] | -0.0093 [-0.0181, -0.0018] | 0.814 | 0.320 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.513 (climatology 0.512, difference +0.0013 [-0.0974, +0.1058]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0873, ΔBrier vs climatology +0.0422 [+0.0274, +0.0587], realised minus predicted +0.0217 [-0.0109, +0.0567]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.465 | 0.3139 | 0.2720 | +0.0138 [-0.0278, +0.0533] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0927 | 0.0159 | +0.0113 [-0.0168, +0.0345] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0038 [+0.0002, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0764 | 0.1165 | +0.0302 [+0.0088, +0.0588] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0018 | 0.0048 | +0.0095 [+0.0080, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0069 | 0.0000 | +0.0309 [+0.0243, +0.0373] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0457 | 0.2439 | 0.0276 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.484 | 0.3240 | 0.2615 | +0.0127 [-0.0242, +0.0488] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1075 | 0.1133 | +0.0411 [+0.0185, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.435 | 0.0799 | 0.0630 | +0.0068 [-0.0033, +0.0166] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0383, +0.1920] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0481, +0.0937] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2894 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.300, 0.700] | 0.231 | 2.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.565] | 0.192 | 2.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 154 | 0.557 | 0.506 | 0.0578 | +0.0136 [+0.0042, +0.0233] | -0.0014 [-0.0095, +0.0063] | 0.920 | 0.513 | no |
| 2 | 0.607 (147 of 1872 days never flag) | 102 | 0.345 | 0.471 | 0.0671 | +0.0040 [-0.0050, +0.0118] | -0.0060 [-0.0147, +0.0016] | 0.878 | 0.314 | no |
| 3 | 0.618 (147 of 1871 days never flag) | 122 | 0.428 | 0.484 | 0.0663 | +0.0044 [-0.0059, +0.0132] | -0.0019 [-0.0117, +0.0065] | 0.893 | 0.391 | no |
| 4 | 0.588 (147 of 1870 days never flag) | 120 | 0.435 | 0.500 | 0.0632 | +0.0076 [+0.0007, +0.0138] | -0.0008 [-0.0074, +0.0055] | 0.883 | 0.400 | no |
| 5 | 0.575 (147 of 1869 days never flag) | 110 | 0.370 | 0.464 | 0.0672 | +0.0037 [-0.0026, +0.0097] | -0.0038 [-0.0098, +0.0020] | 0.814 | 0.335 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.492 (climatology 0.512, difference -0.0200 [-0.1284, +0.0824]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0865, ΔBrier vs climatology +0.0430 [+0.0288, +0.0593], realised minus predicted +0.0225 [-0.0099, +0.0558]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.490 | 0.3174 | 0.2720 | +0.0113 [-0.0310, +0.0525] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0912 | 0.0159 | +0.0118 [-0.0144, +0.0351] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0011 [-0.0041, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0311 [+0.0100, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0313 [+0.0247, +0.0381] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0503 | 0.2439 | 0.0401 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.506 | 0.3262 | 0.2615 | +0.0100 [-0.0267, +0.0460] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1056 | 0.1133 | +0.0446 [+0.0230, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.452 | 0.0806 | 0.0630 | +0.0056 [-0.0046, +0.0156] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0331, +0.1941] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0477, +0.0955] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2827 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.273, 0.655] | 0.231 | 3.08 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.615] | 0.192 | 2.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.681 (126 of 1873 days never flag) | 155 | 0.536 | 0.484 | 0.0571 | +0.0143 [+0.0049, +0.0236] | -0.0008 [-0.0089, +0.0074] | 0.920 | 0.490 | no |
| 2 | 0.599 (147 of 1872 days never flag) | 136 | 0.504 | 0.515 | 0.0605 | +0.0106 [+0.0011, +0.0196] | +0.0006 [-0.0085, +0.0089] | 0.897 | 0.466 | no |
| 3 | 0.593 (147 of 1871 days never flag) | 114 | 0.442 | 0.535 | 0.0617 | +0.0090 [-0.0014, +0.0185] | +0.0027 [-0.0074, +0.0121] | 0.902 | 0.411 | no |
| 4 | 0.765 (147 of 1870 days never flag) | 115 | 0.435 | 0.522 | 0.0609 | +0.0099 [+0.0024, +0.0175] | +0.0014 [-0.0063, +0.0088] | 0.868 | 0.403 | no |
| 5 | 0.69 (147 of 1869 days never flag) | 112 | 0.420 | 0.518 | 0.0671 | +0.0038 [-0.0055, +0.0123] | -0.0037 [-0.0128, +0.0044] | 0.849 | 0.389 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1658 [+0.0511, +0.2833]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0798, ΔBrier vs climatology +0.0497 [+0.0304, +0.0710], realised minus predicted -0.0023 [-0.0328, +0.0309]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.647 | 0.465 | 0.3139 | 0.2720 | +0.0138 [-0.0264, +0.0547] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0927 | 0.0159 | +0.0113 [-0.0177, +0.0349] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0158] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0038 [+0.0000, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0764 | 0.1165 | +0.0302 [+0.0089, +0.0569] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0018 | 0.0048 | +0.0095 [+0.0078, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0069 | 0.0000 | +0.0309 [+0.0245, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0457 | 0.2439 | 0.0276 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.600 | 0.484 | 0.3240 | 0.2615 | +0.0127 [-0.0222, +0.0491] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1075 | 0.1133 | +0.0411 [+0.0176, +0.0659] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.435 | 0.0799 | 0.0630 | +0.0068 [-0.0030, +0.0163] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2030 | 0.2903 | +0.1126 [+0.0335, +0.1895] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1168 | 0.1461 | +0.0706 [+0.0493, +0.0935] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2894 | 0.2213 |

## risk_gbm_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.667] | 0.231 | 2.92 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.636] | 0.192 | 2.38 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 154 | 0.557 | 0.506 | 0.0578 | +0.0136 [+0.0042, +0.0229] | -0.0014 [-0.0098, +0.0062] | 0.920 | 0.513 | no |
| 2 | 0.578 (147 of 1872 days never flag) | 136 | 0.475 | 0.485 | 0.0613 | +0.0097 [+0.0007, +0.0186] | -0.0003 [-0.0089, +0.0081] | 0.893 | 0.434 | no |
| 3 | 0.652 (147 of 1871 days never flag) | 91 | 0.384 | 0.582 | 0.0614 | +0.0093 [-0.0014, +0.0186] | +0.0030 [-0.0074, +0.0120] | 0.900 | 0.362 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 98 | 0.384 | 0.541 | 0.0583 | +0.0125 [+0.0049, +0.0201] | +0.0041 [-0.0035, +0.0116] | 0.895 | 0.358 | no |
| 5 | 0.528 (147 of 1869 days never flag) | 123 | 0.442 | 0.496 | 0.0610 | +0.0099 [+0.0031, +0.0164] | +0.0024 [-0.0044, +0.0091] | 0.852 | 0.406 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.718 (climatology 0.512, difference +0.2062 [+0.0596, +0.3414]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0786, ΔBrier vs climatology +0.0508 [+0.0319, +0.0721], realised minus predicted -0.0001 [-0.0311, +0.0312]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.490 | 0.3174 | 0.2720 | +0.0113 [-0.0297, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0912 | 0.0159 | +0.0118 [-0.0167, +0.0348] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0009 | 0.0200 | +0.0011 [-0.0043, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0745 | 0.1165 | +0.0311 [+0.0103, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0012 | 0.0048 | +0.0089 [+0.0071, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0313 [+0.0246, +0.0378] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0503 | 0.2439 | 0.0401 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.506 | 0.3262 | 0.2615 | +0.0100 [-0.0269, +0.0462] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1056 | 0.1133 | +0.0446 [+0.0225, +0.0699] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.452 | 0.0806 | 0.0630 | +0.0056 [-0.0047, +0.0155] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0355, +0.1932] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1136 | 0.1461 | +0.0711 [+0.0488, +0.0956] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2827 | 0.2213 |

## risk_gbm_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.333, 0.731] | 0.231 | 3.77 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.231 | 3.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (126 of 1873 days never flag) | 164 | 0.557 | 0.476 | 0.0507 | +0.0207 [+0.0130, +0.0294] | +0.0056 [-0.0003, +0.0117] | 0.905 | 0.508 | no |
| 2 | 0.603 (147 of 1872 days never flag) | 130 | 0.396 | 0.423 | 0.0614 | +0.0097 [+0.0043, +0.0152] | -0.0003 [-0.0057, +0.0047] | 0.852 | 0.352 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 169 | 0.514 | 0.420 | 0.0608 | +0.0099 [+0.0055, +0.0145] | +0.0035 [-0.0007, +0.0078] | 0.857 | 0.458 | no |
| 4 | 0.451 (147 of 1870 days never flag) | 125 | 0.435 | 0.480 | 0.0608 | +0.0100 [+0.0048, +0.0151] | +0.0015 [-0.0034, +0.0064] | 0.839 | 0.397 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 140 | 0.428 | 0.421 | 0.0692 | +0.0018 [-0.0037, +0.0070] | -0.0058 [-0.0118, -0.0000] | 0.777 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.508 (climatology 0.512, difference -0.0047 [-0.1012, +0.0944]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0895, ΔBrier vs climatology +0.0400 [+0.0260, +0.0553], realised minus predicted +0.0193 [-0.0152, +0.0546]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.459 | 0.2748 | 0.2720 | +0.0425 [+0.0112, +0.0777] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1312 | 0.0159 | +0.0148 [-0.0056, +0.0328] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0038 [+0.0003, +0.0068] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0741 | 0.1165 | +0.0325 [+0.0094, +0.0629] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0039 | 0.0048 | +0.0095 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0541 | 0.0000 | +0.0275 [+0.0216, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0740 | 0.2439 | 0.0262 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.472 | 0.2861 | 0.2615 | +0.0402 [+0.0106, +0.0725] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1088 | 0.1133 | +0.0418 [+0.0186, +0.0685] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.422 | 0.0797 | 0.0630 | +0.0142 [+0.0067, +0.0227] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0390, +0.1911] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0478, +0.0949] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2803 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.286, 0.714] | 0.231 | 3.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.621] | 0.231 | 3.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 162 | 0.557 | 0.481 | 0.0512 | +0.0202 [+0.0127, +0.0282] | +0.0051 [-0.0008, +0.0110] | 0.904 | 0.509 | no |
| 2 | 0.607 (147 of 1872 days never flag) | 128 | 0.374 | 0.406 | 0.0620 | +0.0090 [+0.0034, +0.0147] | -0.0010 [-0.0067, +0.0043] | 0.850 | 0.330 | no |
| 3 | 0.534 (147 of 1871 days never flag) | 161 | 0.500 | 0.429 | 0.0605 | +0.0102 [+0.0054, +0.0150] | +0.0038 [-0.0009, +0.0083] | 0.855 | 0.447 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 125 | 0.442 | 0.488 | 0.0605 | +0.0103 [+0.0054, +0.0151] | +0.0019 [-0.0032, +0.0068] | 0.845 | 0.405 | no |
| 5 | 0.489 (147 of 1869 days never flag) | 119 | 0.384 | 0.445 | 0.0672 | +0.0037 [-0.0011, +0.0090] | -0.0038 [-0.0091, +0.0017] | 0.784 | 0.346 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.491 (climatology 0.512, difference -0.0213 [-0.1310, +0.0810]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0876, ΔBrier vs climatology +0.0419 [+0.0284, +0.0573], realised minus predicted +0.0228 [-0.0103, +0.0591]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.467 | 0.2794 | 0.2720 | +0.0407 [+0.0093, +0.0725] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1302 | 0.0159 | +0.0155 [-0.0048, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0013 | 0.0200 | +0.0011 [-0.0042, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0716 | 0.1165 | +0.0333 [+0.0106, +0.0610] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0034 | 0.0048 | +0.0089 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0542 | 0.0000 | +0.0276 [+0.0213, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0747 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.481 | 0.2885 | 0.2615 | +0.0382 [+0.0100, +0.0682] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1068 | 0.1133 | +0.0449 [+0.0232, +0.0695] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.427 | 0.0808 | 0.0630 | +0.0132 [+0.0059, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0320, +0.1895] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1136 | 0.1461 | +0.0711 [+0.0481, +0.0958] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2732 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.275, 0.667] | 0.231 | 3.31 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.235, 0.607] | 0.231 | 2.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.482 (126 of 1873 days never flag) | 164 | 0.557 | 0.476 | 0.0507 | +0.0207 [+0.0129, +0.0295] | +0.0056 [-0.0004, +0.0116] | 0.905 | 0.508 | no |
| 2 | 0.599 (147 of 1872 days never flag) | 148 | 0.504 | 0.473 | 0.0547 | +0.0164 [+0.0092, +0.0237] | +0.0064 [-0.0006, +0.0133] | 0.877 | 0.459 | no |
| 3 | 0.428 (147 of 1871 days never flag) | 131 | 0.457 | 0.481 | 0.0551 | +0.0155 [+0.0093, +0.0220] | +0.0092 [+0.0030, +0.0157] | 0.872 | 0.417 | no |
| 4 | 0.522 (147 of 1870 days never flag) | 111 | 0.413 | 0.514 | 0.0567 | +0.0141 [+0.0080, +0.0206] | +0.0056 [-0.0009, +0.0126] | 0.848 | 0.382 | no |
| 5 | 0.655 (147 of 1869 days never flag) | 125 | 0.391 | 0.432 | 0.0631 | +0.0078 [+0.0012, +0.0140] | +0.0003 [-0.0065, +0.0070] | 0.821 | 0.350 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1665 [+0.0547, +0.2791]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0798, ΔBrier vs climatology +0.0496 [+0.0303, +0.0699], realised minus predicted -0.0067 [-0.0377, +0.0258]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.667 | 0.459 | 0.2748 | 0.2720 | +0.0425 [+0.0109, +0.0762] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1312 | 0.0159 | +0.0148 [-0.0050, +0.0317] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0032 | 0.0200 | +0.0038 [+0.0001, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.889 | 0.0741 | 0.1165 | +0.0325 [+0.0098, +0.0625] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0039 | 0.0048 | +0.0095 [+0.0080, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0541 | 0.0000 | +0.0275 [+0.0215, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0740 | 0.2439 | 0.0262 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.616 | 0.472 | 0.2861 | 0.2615 | +0.0402 [+0.0102, +0.0720] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1088 | 0.1133 | +0.0418 [+0.0172, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.535 | 0.422 | 0.0797 | 0.0630 | +0.0142 [+0.0068, +0.0228] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.2030 | 0.2903 | +0.1126 [+0.0328, +0.1876] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.692 | 0.1168 | 0.1461 | +0.0706 [+0.0483, +0.0931] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2803 | 0.2213 |

## risk_gbm_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.278, 0.667] | 0.231 | 3.23 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.611] | 0.192 | 2.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.698 (126 of 1873 days never flag) | 162 | 0.557 | 0.481 | 0.0512 | +0.0202 [+0.0125, +0.0280] | +0.0051 [-0.0009, +0.0109] | 0.904 | 0.509 | no |
| 2 | 0.526 (147 of 1872 days never flag) | 120 | 0.439 | 0.508 | 0.0556 | +0.0155 [+0.0089, +0.0228] | +0.0055 [-0.0008, +0.0123] | 0.871 | 0.405 | no |
| 3 | 0.652 (147 of 1871 days never flag) | 106 | 0.428 | 0.557 | 0.0549 | +0.0158 [+0.0100, +0.0219] | +0.0095 [+0.0038, +0.0153] | 0.867 | 0.400 | no |
| 4 | 0.615 (147 of 1870 days never flag) | 110 | 0.428 | 0.536 | 0.0551 | +0.0157 [+0.0095, +0.0225] | +0.0072 [+0.0007, +0.0142] | 0.863 | 0.398 | no |
| 5 | 0.528 (147 of 1869 days never flag) | 120 | 0.442 | 0.508 | 0.0608 | +0.0101 [+0.0037, +0.0166] | +0.0026 [-0.0041, +0.0092] | 0.826 | 0.408 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.720 (climatology 0.512, difference +0.2074 [+0.0613, +0.3406]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0781, ΔBrier vs climatology +0.0514 [+0.0325, +0.0715], realised minus predicted -0.0023 [-0.0322, +0.0283]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.686 | 0.467 | 0.2794 | 0.2720 | +0.0407 [+0.0091, +0.0712] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.1302 | 0.0159 | +0.0155 [-0.0040, +0.0334] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0013 | 0.0200 | +0.0011 [-0.0050, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0716 | 0.1165 | +0.0333 [+0.0108, +0.0615] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0034 | 0.0048 | +0.0089 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0542 | 0.0000 | +0.0276 [+0.0213, +0.0337] |
| scarcity_state | 2 | 41 | 10 | 0.000 | – | 0.0747 | 0.2439 | 0.0393 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.624 | 0.481 | 0.2885 | 0.2615 | +0.0382 [+0.0087, +0.0667] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1068 | 0.1133 | +0.0449 [+0.0227, +0.0693] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.427 | 0.0808 | 0.0630 | +0.0132 [+0.0058, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1847 | 0.2903 | +0.1129 [+0.0286, +0.1963] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1136 | 0.1461 | +0.0711 [+0.0478, +0.0962] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0542 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2732 | 0.2213 |

## risk_logistic (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.769] | 0.154 | 1.65 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0864 (105 of 1873 days never flag) | 88 | 0.321 | 0.511 | 0.0600 | +0.0114 [+0.0062, +0.0165] | -0.0037 [-0.0121, +0.0040] | 0.642 | 0.297 | no |
| 2 | 0.318 (147 of 1872 days never flag) | 53 | 0.201 | 0.528 | 0.0678 | +0.0032 [-0.0033, +0.0091] | -0.0068 [-0.0148, +0.0004] | 0.579 | 0.187 | no |
| 3 | 0.118 (147 of 1871 days never flag) | 58 | 0.203 | 0.483 | 0.0687 | +0.0019 [-0.0054, +0.0087] | -0.0044 [-0.0133, +0.0033] | 0.578 | 0.186 | no |
| 4 | 0.107 (147 of 1870 days never flag) | 66 | 0.188 | 0.394 | 0.0689 | +0.0019 [-0.0049, +0.0081] | -0.0065 [-0.0151, +0.0011] | 0.578 | 0.165 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 58 | 0.159 | 0.379 | 0.0693 | +0.0016 [-0.0056, +0.0080] | -0.0059 [-0.0144, +0.0015] | 0.577 | 0.139 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.588 (climatology 0.512, difference +0.0754 [-0.0491, +0.1806]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1079, ΔBrier vs climatology +0.0216 [+0.0098, +0.0329], realised minus predicted +0.0742 [+0.0405, +0.1110]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.564 | 0.1071 | 0.2720 | -0.0038 [-0.0245, +0.0163] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0283 | 0.0159 | +0.0266 [+0.0104, +0.0402] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0048 | 0.0200 | +0.0049 [+0.0006, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.706 | 0.0382 | 0.1165 | +0.0183 [+0.0033, +0.0374] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0025 | 0.0048 | +0.0094 [+0.0077, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0041 | 0.0000 | +0.0308 [+0.0245, +0.0367] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.400 | 0.0741 | 0.2439 | -0.0329 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.336 | 0.553 | 0.1072 | 0.2615 | +0.0069 [-0.0120, +0.0248] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1048 | 0.1133 | +0.0284 [+0.0008, +0.0576] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.515 | 0.0125 | 0.0630 | +0.0043 [-0.0009, +0.0090] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3499 | 0.2903 | +0.1030 [+0.0321, +0.1692] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1308 | 0.1461 | +0.0798 [+0.0478, +0.1161] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2023 | 0.2213 |

## risk_logistic+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.259, 0.600] | 0.231 | 2.73 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.517] | 0.231 | 2.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 127 | 0.507 | 0.559 | 0.0501 | +0.0213 [+0.0138, +0.0290] | +0.0062 [+0.0006, +0.0117] | 0.879 | 0.475 | no |
| 2 | 0.473 (147 of 1872 days never flag) | 77 | 0.273 | 0.494 | 0.0593 | +0.0118 [+0.0060, +0.0178] | +0.0018 [-0.0029, +0.0064] | 0.841 | 0.251 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 66 | 0.254 | 0.530 | 0.0626 | +0.0080 [+0.0014, +0.0146] | +0.0017 [-0.0046, +0.0076] | 0.812 | 0.236 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 67 | 0.246 | 0.507 | 0.0614 | +0.0094 [+0.0033, +0.0152] | +0.0009 [-0.0048, +0.0065] | 0.820 | 0.227 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 133 | 0.449 | 0.466 | 0.0627 | +0.0083 [+0.0031, +0.0136] | +0.0007 [-0.0039, +0.0051] | 0.797 | 0.408 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.621 (climatology 0.512, difference +0.1086 [+0.0223, +0.1877]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0889, ΔBrier vs climatology +0.0406 [+0.0244, +0.0581], realised minus predicted -0.0058 [-0.0354, +0.0263]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.630 | 0.2485 | 0.2720 | +0.0519 [+0.0244, +0.0802] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1310 | 0.0159 | +0.0103 [-0.0136, +0.0275] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0188 | 0.0000 | +0.0132 [+0.0114, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0349 | 0.0200 | +0.0019 [-0.0051, +0.0080] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.500 | 0.1145 | 0.1165 | +0.0303 [+0.0036, +0.0614] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0241 | 0.0048 | +0.0078 [+0.0056, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0674 | 0.0000 | +0.0244 [+0.0187, +0.0299] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1946 | 0.2439 | 0.0094 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.595 | 0.2576 | 0.2615 | +0.0497 [+0.0238, +0.0757] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1142 | 0.1133 | +0.0335 [+0.0050, +0.0634] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.534 | 0.0859 | 0.0630 | +0.0153 [+0.0084, +0.0225] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0288, +0.1764] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0482, +0.1158] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3403 | 0.2213 |

## risk_logistic+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.370, 0.720] | 0.231 | 3.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.219, 0.548] | 0.231 | 3.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (105 of 1873 days never flag) | 120 | 0.443 | 0.517 | 0.0519 | +0.0195 [+0.0127, +0.0271] | +0.0044 [-0.0011, +0.0101] | 0.802 | 0.409 | no |
| 2 | 0.473 (147 of 1872 days never flag) | 75 | 0.266 | 0.493 | 0.0615 | +0.0095 [+0.0036, +0.0156] | -0.0005 [-0.0054, +0.0045] | 0.752 | 0.244 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 83 | 0.297 | 0.494 | 0.0627 | +0.0080 [+0.0011, +0.0146] | +0.0017 [-0.0047, +0.0079] | 0.746 | 0.273 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 66 | 0.246 | 0.515 | 0.0623 | +0.0085 [+0.0028, +0.0143] | +0.0001 [-0.0054, +0.0056] | 0.758 | 0.228 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 142 | 0.457 | 0.444 | 0.0633 | +0.0076 [+0.0020, +0.0131] | +0.0001 [-0.0049, +0.0048] | 0.743 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0979 [-0.0161, +0.1873]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0913, ΔBrier vs climatology +0.0382 [+0.0211, +0.0539], realised minus predicted +0.0444 [+0.0151, +0.0726]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.480 | 0.570 | 0.1788 | 0.2720 | +0.0363 [+0.0110, +0.0633] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0359 | 0.0159 | +0.0193 [-0.0051, +0.0387] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0173 | 0.0200 | +0.0020 [-0.0056, +0.0083] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.500 | 0.0894 | 0.1165 | +0.0294 [+0.0050, +0.0613] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.200 | 0.0102 | 0.0048 | +0.0081 [+0.0057, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0053 | 0.0000 | +0.0307 [+0.0244, +0.0370] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1636 | 0.2439 | 0.0072 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.550 | 0.1811 | 0.2615 | +0.0381 [+0.0154, +0.0633] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1087 | 0.1133 | +0.0340 [+0.0044, +0.0651] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.474 | 0.0417 | 0.0630 | +0.0131 [+0.0069, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0283, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0501, +0.1180] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3843 | 0.2213 |

## risk_logistic+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.708] | 0.192 | 2.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.192 | 2.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (126 of 1873 days never flag) | 116 | 0.450 | 0.543 | 0.0502 | +0.0212 [+0.0143, +0.0282] | +0.0062 [+0.0011, +0.0115] | 0.876 | 0.419 | no |
| 2 | 0.318 (147 of 1872 days never flag) | 94 | 0.338 | 0.500 | 0.0583 | +0.0128 [+0.0078, +0.0180] | +0.0028 [-0.0021, +0.0078] | 0.830 | 0.311 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 72 | 0.283 | 0.542 | 0.0611 | +0.0096 [+0.0028, +0.0157] | +0.0032 [-0.0034, +0.0097] | 0.805 | 0.264 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 85 | 0.283 | 0.459 | 0.0602 | +0.0106 [+0.0058, +0.0156] | +0.0021 [-0.0031, +0.0077] | 0.812 | 0.256 | no |
| 5 | 0.388 (147 of 1869 days never flag) | 111 | 0.428 | 0.532 | 0.0610 | +0.0100 [+0.0053, +0.0142] | +0.0024 [-0.0023, +0.0069] | 0.792 | 0.397 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1023 [+0.0175, +0.1786]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0899, ΔBrier vs climatology +0.0395 [+0.0240, +0.0564], realised minus predicted +0.0037 [-0.0282, +0.0364]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.575 | 0.2314 | 0.2720 | +0.0463 [+0.0212, +0.0731] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.1169 | 0.0159 | +0.0160 [-0.0038, +0.0306] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0133 [+0.0115, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0263 | 0.0200 | +0.0041 [-0.0004, +0.0087] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.579 | 0.0994 | 0.1165 | +0.0299 [+0.0064, +0.0589] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0192 | 0.0048 | +0.0088 [+0.0070, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0583 | 0.0000 | +0.0256 [+0.0200, +0.0310] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1671 | 0.2439 | 0.0068 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.565 | 0.2389 | 0.2615 | +0.0467 [+0.0235, +0.0698] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1128 | 0.1133 | +0.0326 [+0.0030, +0.0610] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.507 | 0.0748 | 0.0630 | +0.0153 [+0.0092, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0303, +0.1713] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0477, +0.1164] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2506 | 0.2213 |

## risk_logistic+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.259, 0.600] | 0.231 | 2.62 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.515] | 0.231 | 2.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (147 of 1873 days never flag) | 125 | 0.507 | 0.568 | 0.0492 | +0.0222 [+0.0147, +0.0304] | +0.0071 [+0.0017, +0.0130] | 0.907 | 0.476 | no |
| 2 | 0.473 (147 of 1872 days never flag) | 83 | 0.302 | 0.506 | 0.0584 | +0.0127 [+0.0069, +0.0183] | +0.0027 [-0.0018, +0.0076] | 0.882 | 0.278 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 63 | 0.254 | 0.556 | 0.0607 | +0.0100 [+0.0036, +0.0165] | +0.0036 [-0.0028, +0.0098] | 0.866 | 0.237 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 64 | 0.246 | 0.531 | 0.0600 | +0.0109 [+0.0051, +0.0166] | +0.0024 [-0.0033, +0.0078] | 0.863 | 0.229 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 130 | 0.449 | 0.477 | 0.0615 | +0.0094 [+0.0043, +0.0144] | +0.0019 [-0.0028, +0.0063] | 0.851 | 0.410 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.621 (climatology 0.512, difference +0.1086 [+0.0217, +0.1862]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0872, ΔBrier vs climatology +0.0423 [+0.0261, +0.0597], realised minus predicted +0.0203 [-0.0110, +0.0514]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.630 | 0.2485 | 0.2720 | +0.0519 [+0.0251, +0.0810] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.1307 | 0.0159 | +0.0103 [-0.0121, +0.0280] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0044 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0049 | 0.0200 | +0.0049 [+0.0006, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.524 | 0.0979 | 0.1165 | +0.0327 [+0.0063, +0.0644] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0025 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0674 | 0.0000 | +0.0244 [+0.0188, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1946 | 0.2439 | 0.0094 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.552 | 0.595 | 0.2576 | 0.2615 | +0.0497 [+0.0238, +0.0758] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1121 | 0.1133 | +0.0336 [+0.0051, +0.0659] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.547 | 0.0721 | 0.0630 | +0.0164 [+0.0097, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0305, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0490, +0.1171] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3403 | 0.2213 |

## risk_logistic+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.367, 0.708] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.195, 0.500] | 0.192 | 2.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.361 (126 of 1873 days never flag) | 131 | 0.464 | 0.496 | 0.0506 | +0.0208 [+0.0154, +0.0264] | +0.0057 [+0.0003, +0.0110] | 0.887 | 0.426 | no |
| 2 | 0.318 (147 of 1872 days never flag) | 53 | 0.187 | 0.491 | 0.0595 | +0.0115 [+0.0070, +0.0161] | +0.0015 [-0.0033, +0.0064] | 0.843 | 0.171 | no |
| 3 | 0.382 (147 of 1871 days never flag) | 48 | 0.196 | 0.562 | 0.0618 | +0.0088 [+0.0032, +0.0145] | +0.0025 [-0.0036, +0.0084] | 0.814 | 0.184 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 34 | 0.138 | 0.559 | 0.0613 | +0.0096 [+0.0052, +0.0138] | +0.0011 [-0.0040, +0.0063] | 0.827 | 0.129 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 95 | 0.268 | 0.389 | 0.0621 | +0.0088 [+0.0045, +0.0129] | +0.0013 [-0.0039, +0.0059] | 0.808 | 0.235 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.512, difference +0.1011 [+0.0140, +0.1706]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0938, ΔBrier vs climatology +0.0356 [+0.0224, +0.0489], realised minus predicted +0.0355 [+0.0035, +0.0702]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.505 | 0.1778 | 0.2720 | +0.0375 [+0.0206, +0.0547] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.0797 | 0.0159 | +0.0235 [+0.0056, +0.0375] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0095 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0198 | 0.0200 | +0.0043 [-0.0005, +0.0090] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.667 | 0.0763 | 0.1165 | +0.0309 [+0.0077, +0.0603] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0133 | 0.0048 | +0.0090 [+0.0071, +0.0108] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0358 | 0.0000 | +0.0292 [+0.0230, +0.0351] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1344 | 0.2439 | -0.0033 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.504 | 0.508 | 0.1824 | 0.2615 | +0.0429 [+0.0260, +0.0610] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.1095 | 0.1133 | +0.0313 [+0.0035, +0.0611] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.442 | 0.0492 | 0.0630 | +0.0149 [+0.0107, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3499 | 0.2903 | +0.1030 [+0.0272, +0.1714] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.643 | 0.1308 | 0.1461 | +0.0798 [+0.0487, +0.1176] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2194 | 0.2213 |

## risk_logistic+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.594] | 0.192 | 2.38 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.560] | 0.192 | 2.38 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 101 | 0.443 | 0.614 | 0.0629 | +0.0085 [-0.0016, +0.0187] | -0.0066 [-0.0158, +0.0021] | 0.870 | 0.420 | no |
| 2 | 0.676 (147 of 1872 days never flag) | 67 | 0.237 | 0.493 | 0.0708 | +0.0002 [-0.0096, +0.0091] | -0.0098 [-0.0193, -0.0015] | 0.824 | 0.218 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 65 | 0.232 | 0.492 | 0.0746 | -0.0040 [-0.0143, +0.0057] | -0.0103 [-0.0203, -0.0008] | 0.796 | 0.213 | no |
| 4 | 0.703 (147 of 1870 days never flag) | 78 | 0.268 | 0.474 | 0.0723 | -0.0014 [-0.0102, +0.0064] | -0.0099 [-0.0188, -0.0018] | 0.814 | 0.244 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 127 | 0.471 | 0.512 | 0.0725 | -0.0016 [-0.0088, +0.0052] | -0.0091 [-0.0161, -0.0022] | 0.779 | 0.435 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.598 (climatology 0.512, difference +0.0860 [+0.0076, +0.1469]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0339 [+0.0168, +0.0518], realised minus predicted -0.0138 [-0.0478, +0.0233]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.618 | 0.3229 | 0.2720 | +0.0077 [-0.0373, +0.0503] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2056 | 0.0159 | -0.0171 [-0.0410, +0.0042] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0017, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0680 | 0.1165 | +0.0296 [+0.0061, +0.0580] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0089 | 0.0048 | +0.0084 [+0.0065, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1119 | 0.0000 | +0.0111 [+0.0059, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1510 | 0.2439 | -0.0018 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.622 | 0.3208 | 0.2615 | +0.0078 [-0.0312, +0.0454] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1156 | 0.1133 | +0.0309 [+0.0033, +0.0610] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.575 | 0.1023 | 0.0630 | +0.0006 [-0.0096, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0319, +0.1731] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0493, +0.1168] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2902 | 0.2213 |

## risk_logistic+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.714] | 0.192 | 2.38 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.226, 0.560] | 0.192 | 2.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 133 | 0.507 | 0.534 | 0.0629 | +0.0085 [-0.0018, +0.0187] | -0.0065 [-0.0156, +0.0020] | 0.870 | 0.471 | no |
| 2 | 0.604 (147 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0694 | +0.0016 [-0.0078, +0.0100] | -0.0084 [-0.0166, -0.0009] | 0.824 | 0.230 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 66 | 0.246 | 0.515 | 0.0725 | -0.0018 [-0.0119, +0.0071] | -0.0081 [-0.0180, +0.0004] | 0.797 | 0.228 | no |
| 4 | 0.726 (147 of 1870 days never flag) | 75 | 0.261 | 0.480 | 0.0713 | -0.0005 [-0.0086, +0.0071] | -0.0090 [-0.0174, -0.0011] | 0.816 | 0.238 | no |
| 5 | 0.647 (147 of 1869 days never flag) | 114 | 0.391 | 0.474 | 0.0726 | -0.0017 [-0.0092, +0.0056] | -0.0092 [-0.0170, -0.0020] | 0.785 | 0.357 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.512, difference +0.0610 [-0.0127, +0.1206]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0931, ΔBrier vs climatology +0.0364 [+0.0205, +0.0534], realised minus predicted -0.0136 [-0.0454, +0.0211]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.533 | 0.3266 | 0.2720 | +0.0083 [-0.0374, +0.0521] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2046 | 0.0159 | -0.0171 [-0.0421, +0.0044] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0014, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0659 | 0.1165 | +0.0291 [+0.0061, +0.0562] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0088 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1110 | 0.0000 | +0.0114 [+0.0061, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1496 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.538 | 0.3229 | 0.2615 | +0.0078 [-0.0318, +0.0467] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1161 | 0.1133 | +0.0317 [+0.0021, +0.0620] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.481 | 0.1027 | 0.0630 | +0.0007 [-0.0099, +0.0107] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0330, +0.1761] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1173] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2900 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.296, 0.625] | 0.192 | 2.15 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.289, 0.630] | 0.192 | 2.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 101 | 0.443 | 0.614 | 0.0629 | +0.0085 [-0.0021, +0.0182] | -0.0066 [-0.0161, +0.0019] | 0.870 | 0.420 | no |
| 2 | 0.856 (147 of 1872 days never flag) | 70 | 0.273 | 0.543 | 0.0660 | +0.0050 [-0.0042, +0.0143] | -0.0050 [-0.0141, +0.0035] | 0.840 | 0.255 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 53 | 0.232 | 0.604 | 0.0675 | +0.0032 [-0.0072, +0.0125] | -0.0031 [-0.0130, +0.0061] | 0.827 | 0.220 | no |
| 4 | 0.721 (126 of 1870 days never flag) | 81 | 0.290 | 0.494 | 0.0656 | +0.0052 [-0.0027, +0.0129] | -0.0032 [-0.0110, +0.0044] | 0.841 | 0.266 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 112 | 0.406 | 0.500 | 0.0651 | +0.0058 [-0.0015, +0.0125] | -0.0018 [-0.0085, +0.0051] | 0.827 | 0.373 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.512, difference +0.1793 [+0.0513, +0.2797]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0809, ΔBrier vs climatology +0.0485 [+0.0303, +0.0678], realised minus predicted -0.0312 [-0.0603, -0.0031]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.618 | 0.3229 | 0.2720 | +0.0077 [-0.0387, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2056 | 0.0159 | -0.0171 [-0.0424, +0.0041] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0019, +0.0089] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0680 | 0.1165 | +0.0296 [+0.0061, +0.0595] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0089 | 0.0048 | +0.0084 [+0.0066, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1119 | 0.0000 | +0.0111 [+0.0056, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1510 | 0.2439 | -0.0018 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.622 | 0.3208 | 0.2615 | +0.0078 [-0.0320, +0.0450] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1156 | 0.1133 | +0.0309 [+0.0025, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.575 | 0.1023 | 0.0630 | +0.0006 [-0.0105, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0291, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0483, +0.1183] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2902 | 0.2213 |

## risk_logistic+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.350, 0.731] | 0.192 | 2.38 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.625] | 0.192 | 1.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 133 | 0.507 | 0.534 | 0.0629 | +0.0085 [-0.0012, +0.0190] | -0.0065 [-0.0154, +0.0022] | 0.870 | 0.471 | no |
| 2 | 0.866 (147 of 1872 days never flag) | 77 | 0.317 | 0.571 | 0.0661 | +0.0050 [-0.0047, +0.0140] | -0.0050 [-0.0144, +0.0039] | 0.843 | 0.298 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 54 | 0.239 | 0.611 | 0.0671 | +0.0036 [-0.0065, +0.0126] | -0.0027 [-0.0124, +0.0062] | 0.829 | 0.227 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 79 | 0.312 | 0.544 | 0.0651 | +0.0057 [-0.0027, +0.0138] | -0.0027 [-0.0112, +0.0052] | 0.842 | 0.291 | no |
| 5 | 0.6 (147 of 1869 days never flag) | 99 | 0.384 | 0.535 | 0.0651 | +0.0058 [-0.0017, +0.0130] | -0.0017 [-0.0085, +0.0054] | 0.828 | 0.357 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1874 [+0.0633, +0.2930]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0799, ΔBrier vs climatology +0.0495 [+0.0307, +0.0693], realised minus predicted -0.0310 [-0.0595, -0.0007]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.637 | 0.533 | 0.3266 | 0.2720 | +0.0083 [-0.0344, +0.0524] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2046 | 0.0159 | -0.0171 [-0.0419, +0.0042] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0158 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0091 | 0.0200 | +0.0038 [-0.0017, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0659 | 0.1165 | +0.0291 [+0.0060, +0.0568] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0088 | 0.0048 | +0.0085 [+0.0065, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1110 | 0.0000 | +0.0114 [+0.0057, +0.0172] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1496 | 0.2439 | -0.0032 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.538 | 0.3229 | 0.2615 | +0.0078 [-0.0292, +0.0471] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1161 | 0.1133 | +0.0317 [+0.0025, +0.0617] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.481 | 0.1027 | 0.0630 | +0.0007 [-0.0092, +0.0110] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0318, +0.1744] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0436, +0.1153] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2900 | 0.2213 |

## risk_logistic+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.607] | 0.231 | 3.23 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.556] | 0.231 | 3.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (147 of 1873 days never flag) | 122 | 0.521 | 0.598 | 0.0584 | +0.0130 [+0.0051, +0.0217] | -0.0021 [-0.0088, +0.0048] | 0.841 | 0.493 | no |
| 2 | 0.546 (147 of 1872 days never flag) | 81 | 0.237 | 0.407 | 0.0690 | +0.0021 [-0.0044, +0.0086] | -0.0079 [-0.0143, -0.0014] | 0.781 | 0.210 | no |
| 3 | 0.643 (147 of 1871 days never flag) | 74 | 0.261 | 0.486 | 0.0720 | -0.0013 [-0.0080, +0.0054] | -0.0076 [-0.0149, -0.0007] | 0.730 | 0.239 | no |
| 4 | 0.498 (147 of 1870 days never flag) | 63 | 0.217 | 0.476 | 0.0712 | -0.0004 [-0.0069, +0.0060] | -0.0089 [-0.0159, -0.0019] | 0.752 | 0.198 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 148 | 0.464 | 0.432 | 0.0725 | -0.0016 [-0.0080, +0.0046] | -0.0091 [-0.0160, -0.0027] | 0.722 | 0.415 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.598 (climatology 0.512, difference +0.0854 [+0.0048, +0.1499]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0986, ΔBrier vs climatology +0.0309 [+0.0154, +0.0483], realised minus predicted -0.0308 [-0.0641, +0.0072]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.614 | 0.2940 | 0.2720 | +0.0337 [+0.0011, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2137 | 0.0159 | -0.0150 [-0.0358, +0.0017] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0089, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0137 | 0.0200 | +0.0038 [-0.0017, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0667 | 0.1165 | +0.0275 [+0.0065, +0.0547] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0222 | 0.0048 | +0.0080 [+0.0063, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1315 | 0.0000 | +0.0053 [+0.0006, +0.0107] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1281 | 0.2439 | -0.0229 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.607 | 0.2953 | 0.2615 | +0.0321 [+0.0027, +0.0631] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1163 | 0.1133 | +0.0301 [+0.0016, +0.0583] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.568 | 0.1065 | 0.0630 | +0.0060 [-0.0012, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3499 | 0.2903 | +0.1030 [+0.0303, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1308 | 0.1461 | +0.0798 [+0.0478, +0.1178] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2859 | 0.2213 |

## risk_logistic+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.720] | 0.231 | 3.15 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 3.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (126 of 1873 days never flag) | 158 | 0.586 | 0.519 | 0.0583 | +0.0131 [+0.0052, +0.0217] | -0.0020 [-0.0088, +0.0051] | 0.841 | 0.542 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 76 | 0.237 | 0.434 | 0.0676 | +0.0035 [-0.0029, +0.0096] | -0.0065 [-0.0125, -0.0006] | 0.781 | 0.213 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 59 | 0.232 | 0.542 | 0.0698 | +0.0008 [-0.0050, +0.0067] | -0.0055 [-0.0112, +0.0005] | 0.731 | 0.216 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 62 | 0.217 | 0.484 | 0.0703 | +0.0005 [-0.0057, +0.0069] | -0.0079 [-0.0145, -0.0010] | 0.754 | 0.199 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 136 | 0.391 | 0.397 | 0.0726 | -0.0017 [-0.0087, +0.0049] | -0.0092 [-0.0167, -0.0022] | 0.728 | 0.344 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.512, difference +0.0604 [-0.0172, +0.1240]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0961, ΔBrier vs climatology +0.0334 [+0.0182, +0.0498], realised minus predicted -0.0307 [-0.0645, +0.0052]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.518 | 0.2976 | 0.2720 | +0.0343 [+0.0014, +0.0700] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2127 | 0.0159 | -0.0150 [-0.0373, +0.0023] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0136 | 0.0200 | +0.0039 [-0.0016, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0646 | 0.1165 | +0.0269 [+0.0062, +0.0515] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0221 | 0.0048 | +0.0081 [+0.0062, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1305 | 0.0000 | +0.0056 [+0.0006, +0.0112] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1268 | 0.2439 | -0.0244 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.523 | 0.2975 | 0.2615 | +0.0321 [+0.0030, +0.0628] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1168 | 0.1133 | +0.0309 [+0.0029, +0.0603] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.467 | 0.1070 | 0.0630 | +0.0061 [-0.0015, +0.0144] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3465 | 0.2903 | +0.1049 [+0.0345, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1295 | 0.1461 | +0.0774 [+0.0452, +0.1168] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2858 | 0.2213 |

## risk_logistic+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.632] | 0.231 | 2.85 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.625] | 0.231 | 2.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (147 of 1873 days never flag) | 122 | 0.521 | 0.598 | 0.0584 | +0.0130 [+0.0055, +0.0217] | -0.0021 [-0.0085, +0.0049] | 0.841 | 0.493 | no |
| 2 | 0.856 (147 of 1872 days never flag) | 54 | 0.223 | 0.574 | 0.0634 | +0.0076 [+0.0008, +0.0146] | -0.0024 [-0.0093, +0.0047] | 0.804 | 0.210 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 49 | 0.232 | 0.653 | 0.0643 | +0.0064 [+0.0002, +0.0126] | +0.0001 [-0.0064, +0.0068] | 0.769 | 0.222 | no |
| 4 | 0.721 (126 of 1870 days never flag) | 81 | 0.304 | 0.519 | 0.0642 | +0.0066 [+0.0003, +0.0128] | -0.0018 [-0.0087, +0.0049] | 0.788 | 0.282 | no |
| 5 | 0.767 (147 of 1869 days never flag) | 132 | 0.420 | 0.439 | 0.0649 | +0.0061 [+0.0001, +0.0121] | -0.0015 [-0.0075, +0.0053] | 0.781 | 0.378 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.512, difference +0.1799 [+0.0515, +0.2860]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0827, ΔBrier vs climatology +0.0467 [+0.0275, +0.0661], realised minus predicted -0.0498 [-0.0806, -0.0194]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.614 | 0.2940 | 0.2720 | +0.0337 [+0.0025, +0.0666] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2137 | 0.0159 | -0.0150 [-0.0345, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0137 | 0.0200 | +0.0038 [-0.0016, +0.0088] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0667 | 0.1165 | +0.0275 [+0.0061, +0.0541] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0222 | 0.0048 | +0.0080 [+0.0062, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1315 | 0.0000 | +0.0053 [+0.0004, +0.0106] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1281 | 0.2439 | -0.0229 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.607 | 0.2953 | 0.2615 | +0.0321 [+0.0040, +0.0631] |
| day_type | month_end | 150 | 17 | 0.471 | 0.615 | 0.1163 | 0.1133 | +0.0301 [+0.0021, +0.0589] |
| day_type | ordinary | 1603 | 101 | 0.495 | 0.568 | 0.1065 | 0.0630 | +0.0060 [-0.0011, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3499 | 0.2903 | +0.1030 [+0.0314, +0.1735] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1308 | 0.1461 | +0.0798 [+0.0495, +0.1160] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2859 | 0.2213 |

## risk_logistic+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.679] | 0.231 | 2.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.267, 0.581] | 0.231 | 2.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.517 (126 of 1873 days never flag) | 158 | 0.586 | 0.519 | 0.0583 | +0.0131 [+0.0049, +0.0212] | -0.0020 [-0.0092, +0.0046] | 0.841 | 0.542 | no |
| 2 | 0.866 (147 of 1872 days never flag) | 61 | 0.266 | 0.607 | 0.0634 | +0.0076 [+0.0007, +0.0144] | -0.0024 [-0.0093, +0.0046] | 0.807 | 0.252 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 50 | 0.239 | 0.660 | 0.0639 | +0.0068 [+0.0012, +0.0127] | +0.0005 [-0.0055, +0.0067] | 0.771 | 0.229 | no |
| 4 | 0.807 (126 of 1870 days never flag) | 97 | 0.355 | 0.505 | 0.0637 | +0.0072 [+0.0009, +0.0135] | -0.0013 [-0.0079, +0.0054] | 0.789 | 0.327 | no |
| 5 | 0.767 (147 of 1869 days never flag) | 118 | 0.384 | 0.449 | 0.0648 | +0.0061 [-0.0005, +0.0128] | -0.0014 [-0.0081, +0.0057] | 0.779 | 0.347 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.700 (climatology 0.512, difference +0.1880 [+0.0729, +0.2941]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0817, ΔBrier vs climatology +0.0478 [+0.0289, +0.0673], realised minus predicted -0.0496 [-0.0813, -0.0187]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.696 | 0.518 | 0.2976 | 0.2720 | +0.0343 [+0.0003, +0.0670] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.2127 | 0.0159 | -0.0150 [-0.0355, +0.0019] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0359 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0136 | 0.0200 | +0.0039 [-0.0017, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.692 | 0.0646 | 0.1165 | +0.0269 [+0.0062, +0.0510] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0221 | 0.0048 | +0.0081 [+0.0063, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1305 | 0.0000 | +0.0056 [+0.0005, +0.0110] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1268 | 0.2439 | -0.0244 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.640 | 0.523 | 0.2975 | 0.2615 | +0.0321 [+0.0013, +0.0630] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1168 | 0.1133 | +0.0309 [+0.0031, +0.0602] |
| day_type | ordinary | 1603 | 101 | 0.564 | 0.467 | 0.1070 | 0.0630 | +0.0061 [-0.0015, +0.0142] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3465 | 0.2903 | +0.1049 [+0.0307, +0.1769] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1295 | 0.1461 | +0.0774 [+0.0445, +0.1144] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2858 | 0.2213 |

## risk_logistic+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.650] | 0.231 | 2.88 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.231 | 2.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 89 | 0.364 | 0.573 | 0.0586 | +0.0129 [+0.0034, +0.0227] | -0.0022 [-0.0107, +0.0061] | 0.915 | 0.342 | no |
| 2 | 0.676 (147 of 1872 days never flag) | 80 | 0.295 | 0.512 | 0.0656 | +0.0055 [-0.0039, +0.0142] | -0.0045 [-0.0130, +0.0037] | 0.884 | 0.272 | no |
| 3 | 0.643 (147 of 1871 days never flag) | 65 | 0.232 | 0.492 | 0.0682 | +0.0025 [-0.0085, +0.0123] | -0.0038 [-0.0145, +0.0056] | 0.890 | 0.213 | no |
| 4 | 0.677 (147 of 1870 days never flag) | 89 | 0.312 | 0.483 | 0.0676 | +0.0032 [-0.0051, +0.0108] | -0.0052 [-0.0135, +0.0029] | 0.846 | 0.285 | no |
| 5 | 0.701 (147 of 1869 days never flag) | 145 | 0.507 | 0.483 | 0.0724 | -0.0015 [-0.0106, +0.0068] | -0.0090 [-0.0180, -0.0005] | 0.820 | 0.464 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.609 (climatology 0.512, difference +0.0964 [+0.0156, +0.1551]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0898, ΔBrier vs climatology +0.0397 [+0.0231, +0.0578], realised minus predicted +0.0039 [-0.0272, +0.0355]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.579 | 0.3238 | 0.2720 | +0.0115 [-0.0306, +0.0550] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0973 | 0.0159 | +0.0043 [-0.0257, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0056 | 0.0200 | +0.0049 [+0.0004, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0770 | 0.1165 | +0.0286 [+0.0068, +0.0559] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0035 | 0.0048 | +0.0094 [+0.0077, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0308 [+0.0245, +0.0369] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0994 | 0.2439 | -0.0110 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.581 | 0.3291 | 0.2615 | +0.0107 [-0.0264, +0.0478] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1120 | 0.1133 | +0.0315 [+0.0031, +0.0597] |
| day_type | ordinary | 1603 | 101 | 0.297 | 0.500 | 0.0794 | 0.0630 | +0.0057 [-0.0036, +0.0153] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0311, +0.1756] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0798 [+0.0496, +0.1176] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.192 | 2.31 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.445] | 0.192 | 2.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (126 of 1873 days never flag) | 120 | 0.443 | 0.517 | 0.0589 | +0.0125 [+0.0023, +0.0225] | -0.0026 [-0.0120, +0.0061] | 0.915 | 0.409 | no |
| 2 | 0.604 (147 of 1872 days never flag) | 75 | 0.266 | 0.493 | 0.0644 | +0.0067 [-0.0022, +0.0152] | -0.0033 [-0.0116, +0.0045] | 0.886 | 0.244 | no |
| 3 | 0.71 (147 of 1871 days never flag) | 63 | 0.225 | 0.492 | 0.0660 | +0.0047 [-0.0061, +0.0143] | -0.0016 [-0.0120, +0.0076] | 0.893 | 0.206 | no |
| 4 | 0.631 (147 of 1870 days never flag) | 66 | 0.217 | 0.455 | 0.0640 | +0.0068 [-0.0005, +0.0140] | -0.0016 [-0.0091, +0.0060] | 0.880 | 0.197 | no |
| 5 | 0.535 (147 of 1869 days never flag) | 106 | 0.333 | 0.434 | 0.0669 | +0.0041 [-0.0030, +0.0107] | -0.0035 [-0.0110, +0.0035] | 0.826 | 0.299 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.576 (climatology 0.512, difference +0.0635 [-0.0138, +0.1244]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0873, ΔBrier vs climatology +0.0422 [+0.0266, +0.0599], realised minus predicted +0.0051 [-0.0246, +0.0370]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.514 | 0.3281 | 0.2720 | +0.0103 [-0.0327, +0.0542] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0970 | 0.0159 | +0.0040 [-0.0266, +0.0295] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0055 | 0.0200 | +0.0050 [+0.0006, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0750 | 0.1165 | +0.0283 [+0.0066, +0.0550] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0034 | 0.0048 | +0.0095 [+0.0076, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0042 | 0.0000 | +0.0311 [+0.0247, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0981 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.521 | 0.3322 | 0.2615 | +0.0092 [-0.0282, +0.0481] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1127 | 0.1133 | +0.0327 [+0.0036, +0.0638] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.444 | 0.0801 | 0.0630 | +0.0053 [-0.0047, +0.0150] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0309, +0.1746] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1295 | 0.1461 | +0.0774 [+0.0437, +0.1152] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.633] | 0.231 | 2.65 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.639] | 0.231 | 2.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 89 | 0.364 | 0.573 | 0.0586 | +0.0129 [+0.0026, +0.0226] | -0.0022 [-0.0114, +0.0061] | 0.915 | 0.342 | no |
| 2 | 0.856 (147 of 1872 days never flag) | 72 | 0.288 | 0.556 | 0.0615 | +0.0096 [-0.0002, +0.0190] | -0.0004 [-0.0102, +0.0087] | 0.892 | 0.269 | no |
| 3 | 0.706 (147 of 1871 days never flag) | 55 | 0.239 | 0.600 | 0.0619 | +0.0088 [-0.0020, +0.0190] | +0.0025 [-0.0079, +0.0125] | 0.900 | 0.226 | no |
| 4 | 0.721 (126 of 1870 days never flag) | 95 | 0.341 | 0.495 | 0.0616 | +0.0093 [+0.0017, +0.0167] | +0.0008 [-0.0068, +0.0084] | 0.865 | 0.313 | no |
| 5 | 0.767 (126 of 1869 days never flag) | 118 | 0.355 | 0.415 | 0.0657 | +0.0052 [-0.0045, +0.0139] | -0.0023 [-0.0113, +0.0060] | 0.853 | 0.315 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.691 (climatology 0.512, difference +0.1793 [+0.0452, +0.2843]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0759, ΔBrier vs climatology +0.0536 [+0.0347, +0.0743], realised minus predicted -0.0120 [-0.0408, +0.0167]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.579 | 0.3238 | 0.2720 | +0.0115 [-0.0324, +0.0533] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.0973 | 0.0159 | +0.0043 [-0.0261, +0.0292] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0056 | 0.0200 | +0.0049 [+0.0006, +0.0091] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0770 | 0.1165 | +0.0286 [+0.0067, +0.0547] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0035 | 0.0048 | +0.0094 [+0.0075, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0052 | 0.0000 | +0.0308 [+0.0244, +0.0368] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0994 | 0.2439 | -0.0110 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.581 | 0.3291 | 0.2615 | +0.0107 [-0.0271, +0.0484] |
| day_type | month_end | 150 | 17 | 0.471 | 0.667 | 0.1120 | 0.1133 | +0.0315 [+0.0027, +0.0605] |
| day_type | ordinary | 1603 | 101 | 0.297 | 0.500 | 0.0794 | 0.0630 | +0.0057 [-0.0045, +0.0157] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0298, +0.1679] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0798 [+0.0494, +0.1163] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.667] | 0.192 | 2.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.526] | 0.192 | 1.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (126 of 1873 days never flag) | 120 | 0.443 | 0.517 | 0.0589 | +0.0125 [+0.0026, +0.0221] | -0.0026 [-0.0115, +0.0059] | 0.915 | 0.409 | no |
| 2 | 0.625 (147 of 1872 days never flag) | 79 | 0.331 | 0.582 | 0.0616 | +0.0094 [-0.0004, +0.0186] | -0.0006 [-0.0100, +0.0083] | 0.895 | 0.312 | no |
| 3 | 0.707 (147 of 1871 days never flag) | 53 | 0.239 | 0.623 | 0.0616 | +0.0091 [-0.0012, +0.0189] | +0.0027 [-0.0073, +0.0124] | 0.903 | 0.228 | no |
| 4 | 0.7 (126 of 1870 days never flag) | 104 | 0.413 | 0.548 | 0.0585 | +0.0123 [+0.0046, +0.0193] | +0.0038 [-0.0043, +0.0109] | 0.892 | 0.386 | no |
| 5 | 0.767 (147 of 1869 days never flag) | 88 | 0.319 | 0.500 | 0.0599 | +0.0110 [+0.0040, +0.0181] | +0.0035 [-0.0035, +0.0109] | 0.855 | 0.293 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1887 [+0.0745, +0.2903]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0746, ΔBrier vs climatology +0.0548 [+0.0358, +0.0748], realised minus predicted -0.0101 [-0.0386, +0.0179]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.514 | 0.3281 | 0.2720 | +0.0103 [-0.0349, +0.0517] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0970 | 0.0159 | +0.0040 [-0.0254, +0.0300] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0055 | 0.0200 | +0.0050 [+0.0006, +0.0094] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0750 | 0.1165 | +0.0283 [+0.0072, +0.0540] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0034 | 0.0048 | +0.0095 [+0.0077, +0.0113] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0042 | 0.0000 | +0.0311 [+0.0245, +0.0373] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0981 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.521 | 0.3322 | 0.2615 | +0.0092 [-0.0293, +0.0462] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1127 | 0.1133 | +0.0327 [+0.0042, +0.0614] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.444 | 0.0801 | 0.0630 | +0.0053 [-0.0049, +0.0149] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0341, +0.1752] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1141] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2834 | 0.2213 |

## risk_logistic+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.285, 0.647] | 0.231 | 3.81 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.588] | 0.231 | 3.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 102 | 0.407 | 0.559 | 0.0521 | +0.0193 [+0.0115, +0.0276] | +0.0042 [-0.0020, +0.0105] | 0.894 | 0.381 | no |
| 2 | 0.546 (147 of 1872 days never flag) | 88 | 0.252 | 0.398 | 0.0606 | +0.0105 [+0.0039, +0.0168] | +0.0005 [-0.0059, +0.0063] | 0.861 | 0.221 | no |
| 3 | 0.643 (147 of 1871 days never flag) | 92 | 0.268 | 0.402 | 0.0622 | +0.0085 [+0.0016, +0.0151] | +0.0022 [-0.0047, +0.0087] | 0.854 | 0.236 | no |
| 4 | 0.48 (147 of 1870 days never flag) | 84 | 0.304 | 0.500 | 0.0638 | +0.0071 [+0.0008, +0.0133] | -0.0014 [-0.0084, +0.0055] | 0.827 | 0.280 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 171 | 0.522 | 0.421 | 0.0689 | +0.0021 [-0.0044, +0.0081] | -0.0055 [-0.0126, +0.0010] | 0.783 | 0.465 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.608 (climatology 0.512, difference +0.0954 [+0.0158, +0.1584]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0921, ΔBrier vs climatology +0.0374 [+0.0204, +0.0538], realised minus predicted +0.0018 [-0.0321, +0.0378]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.2847 | 0.2720 | +0.0403 [+0.0081, +0.0735] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1359 | 0.0159 | +0.0078 [-0.0154, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0075 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0008, +0.0092] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0747 | 0.1165 | +0.0309 [+0.0084, +0.0595] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0056 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0524 | 0.0000 | +0.0274 [+0.0216, +0.0335] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1278 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.448 | 0.566 | 0.2911 | 0.2615 | +0.0382 [+0.0081, +0.0693] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1134 | 0.1133 | +0.0322 [+0.0053, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.493 | 0.0793 | 0.0630 | +0.0131 [+0.0055, +0.0212] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0304, +0.1708] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0479, +0.1161] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2743 | 0.2213 |

## risk_logistic+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.714] | 0.231 | 2.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.192 | 2.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 135 | 0.479 | 0.496 | 0.0524 | +0.0191 [+0.0116, +0.0273] | +0.0040 [-0.0022, +0.0107] | 0.893 | 0.439 | no |
| 2 | 0.543 (147 of 1872 days never flag) | 80 | 0.237 | 0.412 | 0.0593 | +0.0117 [+0.0055, +0.0182] | +0.0017 [-0.0040, +0.0077] | 0.862 | 0.210 | no |
| 3 | 0.71 (147 of 1871 days never flag) | 62 | 0.181 | 0.403 | 0.0602 | +0.0104 [+0.0045, +0.0165] | +0.0041 [-0.0014, +0.0103] | 0.854 | 0.160 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 64 | 0.239 | 0.516 | 0.0613 | +0.0095 [+0.0035, +0.0158] | +0.0011 [-0.0050, +0.0078] | 0.841 | 0.221 | no |
| 5 | 0.489 (147 of 1869 days never flag) | 111 | 0.341 | 0.423 | 0.0669 | +0.0040 [-0.0027, +0.0103] | -0.0035 [-0.0104, +0.0033] | 0.797 | 0.304 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0629 [-0.0130, +0.1259]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0887, ΔBrier vs climatology +0.0408 [+0.0262, +0.0571], realised minus predicted +0.0058 [-0.0255, +0.0403]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.492 | 0.2902 | 0.2720 | +0.0396 [+0.0091, +0.0730] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1360 | 0.0159 | +0.0076 [-0.0164, +0.0283] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0005, +0.0095] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0720 | 0.1165 | +0.0305 [+0.0086, +0.0572] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0055 | 0.0048 | +0.0094 [+0.0076, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0532 | 0.0000 | +0.0274 [+0.0213, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1224 | 0.2439 | -0.0133 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.500 | 0.2945 | 0.2615 | +0.0374 [+0.0090, +0.0674] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1139 | 0.1133 | +0.0330 [+0.0037, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.434 | 0.0804 | 0.0630 | +0.0129 [+0.0059, +0.0209] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0345, +0.1711] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0451, +0.1169] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.632] | 0.231 | 3.77 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.633] | 0.231 | 3.77 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.765 (147 of 1873 days never flag) | 102 | 0.407 | 0.559 | 0.0521 | +0.0193 [+0.0113, +0.0280] | +0.0042 [-0.0020, +0.0107] | 0.894 | 0.381 | no |
| 2 | 0.856 (147 of 1872 days never flag) | 45 | 0.209 | 0.644 | 0.0557 | +0.0154 [+0.0085, +0.0226] | +0.0054 [-0.0010, +0.0122] | 0.871 | 0.199 | no |
| 3 | 0.706 (147 of 1871 days never flag) | 50 | 0.254 | 0.700 | 0.0554 | +0.0153 [+0.0094, +0.0217] | +0.0090 [+0.0027, +0.0157] | 0.867 | 0.245 | no |
| 4 | 0.721 (126 of 1870 days never flag) | 105 | 0.399 | 0.524 | 0.0574 | +0.0135 [+0.0071, +0.0196] | +0.0050 [-0.0018, +0.0116] | 0.849 | 0.370 | no |
| 5 | 0.767 (126 of 1869 days never flag) | 157 | 0.428 | 0.376 | 0.0617 | +0.0092 [+0.0022, +0.0153] | +0.0017 [-0.0053, +0.0084] | 0.830 | 0.371 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.692 (climatology 0.512, difference +0.1799 [+0.0506, +0.2860]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0765, ΔBrier vs climatology +0.0529 [+0.0345, +0.0718], realised minus predicted -0.0167 [-0.0456, +0.0127]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.2847 | 0.2720 | +0.0403 [+0.0089, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.1359 | 0.0159 | +0.0078 [-0.0158, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0075 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0060 | 0.0200 | +0.0049 [+0.0007, +0.0093] |
| regime | 2025-26 | 249 | 29 | 0.172 | 1.000 | 0.0747 | 0.1165 | +0.0309 [+0.0072, +0.0586] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0056 | 0.0048 | +0.0094 [+0.0075, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0524 | 0.0000 | +0.0274 [+0.0215, +0.0331] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1278 | 0.2439 | -0.0124 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.448 | 0.566 | 0.2911 | 0.2615 | +0.0382 [+0.0086, +0.0699] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1134 | 0.1133 | +0.0322 [+0.0038, +0.0616] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.493 | 0.0793 | 0.0630 | +0.0131 [+0.0057, +0.0213] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3499 | 0.2903 | +0.1030 [+0.0309, +0.1698] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1308 | 0.1461 | +0.0798 [+0.0477, +0.1165] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2743 | 0.2213 |

## risk_logistic+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.323, 0.680] | 0.231 | 2.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.238, 0.542] | 0.192 | 1.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.742 (126 of 1873 days never flag) | 135 | 0.479 | 0.496 | 0.0524 | +0.0191 [+0.0108, +0.0274] | +0.0040 [-0.0026, +0.0104] | 0.893 | 0.439 | no |
| 2 | 0.866 (147 of 1872 days never flag) | 55 | 0.266 | 0.673 | 0.0559 | +0.0152 [+0.0081, +0.0222] | +0.0052 [-0.0017, +0.0119] | 0.874 | 0.256 | no |
| 3 | 0.707 (147 of 1871 days never flag) | 45 | 0.246 | 0.756 | 0.0551 | +0.0155 [+0.0098, +0.0216] | +0.0092 [+0.0034, +0.0154] | 0.870 | 0.240 | no |
| 4 | 0.807 (126 of 1870 days never flag) | 107 | 0.406 | 0.523 | 0.0554 | +0.0155 [+0.0094, +0.0217] | +0.0070 [+0.0005, +0.0136] | 0.857 | 0.376 | no |
| 5 | 0.767 (147 of 1869 days never flag) | 88 | 0.319 | 0.500 | 0.0597 | +0.0112 [+0.0046, +0.0182] | +0.0037 [-0.0035, +0.0109] | 0.836 | 0.293 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.701 (climatology 0.512, difference +0.1887 [+0.0694, +0.2888]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0743, ΔBrier vs climatology +0.0552 [+0.0364, +0.0756], realised minus predicted -0.0127 [-0.0420, +0.0168]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.492 | 0.2902 | 0.2720 | +0.0396 [+0.0073, +0.0736] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1360 | 0.0159 | +0.0076 [-0.0161, +0.0291] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0077 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0059 | 0.0200 | +0.0050 [+0.0006, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.138 | 1.000 | 0.0720 | 0.1165 | +0.0305 [+0.0076, +0.0585] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0055 | 0.0048 | +0.0094 [+0.0077, +0.0112] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0532 | 0.0000 | +0.0274 [+0.0217, +0.0333] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1224 | 0.2439 | -0.0133 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.500 | 0.2945 | 0.2615 | +0.0374 [+0.0068, +0.0681] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1139 | 0.1133 | +0.0330 [+0.0045, +0.0626] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.434 | 0.0804 | 0.0630 | +0.0129 [+0.0053, +0.0210] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3465 | 0.2903 | +0.1049 [+0.0348, +0.1781] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1295 | 0.1461 | +0.0774 [+0.0446, +0.1156] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2739 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.154 | 1.69 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.115 | 1.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.144 (105 of 1873 days never flag) | 90 | 0.329 | 0.511 | 0.0590 | +0.0124 [+0.0075, +0.0171] | -0.0027 [-0.0108, +0.0045] | 0.643 | 0.303 | no |
| 2 | 0.326 (147 of 1872 days never flag) | 51 | 0.173 | 0.471 | 0.0671 | +0.0040 [-0.0025, +0.0100] | -0.0060 [-0.0144, +0.0010] | 0.579 | 0.157 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 55 | 0.196 | 0.491 | 0.0688 | +0.0019 [-0.0060, +0.0083] | -0.0045 [-0.0132, +0.0027] | 0.579 | 0.179 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0694 | +0.0014 [-0.0053, +0.0078] | -0.0070 [-0.0150, +0.0007] | 0.578 | 0.179 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 58 | 0.203 | 0.483 | 0.0695 | +0.0015 [-0.0054, +0.0077] | -0.0061 [-0.0143, +0.0012] | 0.577 | 0.186 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.596 (climatology 0.512, difference +0.0835 [-0.0393, +0.1951]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1070, ΔBrier vs climatology +0.0225 [+0.0109, +0.0339], realised minus predicted +0.0762 [+0.0414, +0.1136]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1064 | 0.2720 | -0.0032 [-0.0226, +0.0153] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0254 | 0.0159 | +0.0308 [+0.0204, +0.0398] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0021 | 0.0200 | +0.0036 [+0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.722 | 0.0369 | 0.1165 | +0.0218 [+0.0063, +0.0409] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0011 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0055 | 0.0000 | +0.0304 [+0.0241, +0.0362] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.0450 | 0.2439 | -0.0046 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.551 | 0.1075 | 0.2615 | +0.0084 [-0.0095, +0.0265] |
| day_type | month_end | 150 | 17 | 0.765 | 0.500 | 0.1021 | 0.1133 | +0.0357 [+0.0082, +0.0629] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.529 | 0.0120 | 0.0630 | +0.0051 [+0.0001, +0.0096] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3212 | 0.2903 | +0.0996 [+0.0457, +0.1509] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.529 | 0.1308 | 0.1461 | +0.0731 [+0.0406, +0.1119] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2036 | 0.2213 |

## risk_logistic_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.219, 0.559] | 0.192 | 2.42 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.188, 0.500] | 0.192 | 2.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 75 | 0.329 | 0.613 | 0.0491 | +0.0223 [+0.0148, +0.0305] | +0.0072 [+0.0025, +0.0126] | 0.888 | 0.312 | no |
| 2 | 0.579 (147 of 1872 days never flag) | 67 | 0.252 | 0.522 | 0.0585 | +0.0125 [+0.0074, +0.0184] | +0.0025 [-0.0014, +0.0072] | 0.842 | 0.233 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 77 | 0.261 | 0.468 | 0.0627 | +0.0080 [+0.0016, +0.0143] | +0.0017 [-0.0046, +0.0077] | 0.812 | 0.237 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0619 | +0.0089 [+0.0027, +0.0153] | +0.0004 [-0.0056, +0.0065] | 0.821 | 0.217 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 108 | 0.326 | 0.417 | 0.0628 | +0.0081 [+0.0027, +0.0132] | +0.0006 [-0.0044, +0.0055] | 0.799 | 0.290 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0100, +0.1941]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0409 [+0.0244, +0.0588], realised minus predicted -0.0037 [-0.0341, +0.0293]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.727 | 0.2477 | 0.2720 | +0.0525 [+0.0247, +0.0816] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1281 | 0.0159 | +0.0146 [-0.0007, +0.0280] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0321 | 0.0200 | +0.0006 [-0.0058, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.619 | 0.1132 | 0.1165 | +0.0338 [+0.0068, +0.0687] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0227 | 0.0048 | +0.0079 [+0.0057, +0.0100] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0688 | 0.0000 | +0.0240 [+0.0184, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1655 | 0.2439 | 0.0378 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.344 | 0.632 | 0.2580 | 0.2615 | +0.0513 [+0.0245, +0.0801] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1114 | 0.1133 | +0.0408 [+0.0128, +0.0719] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.553 | 0.0854 | 0.0630 | +0.0162 [+0.0093, +0.0239] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3212 | 0.2903 | +0.0996 [+0.0482, +0.1478] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1308 | 0.1461 | +0.0731 [+0.0408, +0.1102] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3416 | 0.2213 |

## risk_logistic_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.677] | 0.231 | 3.00 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.211, 0.567] | 0.231 | 3.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.314 (105 of 1873 days never flag) | 82 | 0.314 | 0.537 | 0.0510 | +0.0205 [+0.0136, +0.0279] | +0.0054 [+0.0010, +0.0100] | 0.805 | 0.292 | no |
| 2 | 0.579 (147 of 1872 days never flag) | 66 | 0.245 | 0.515 | 0.0608 | +0.0103 [+0.0048, +0.0162] | +0.0003 [-0.0044, +0.0051] | 0.752 | 0.226 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 77 | 0.261 | 0.468 | 0.0627 | +0.0079 [+0.0013, +0.0145] | +0.0016 [-0.0047, +0.0078] | 0.747 | 0.237 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 72 | 0.239 | 0.458 | 0.0628 | +0.0080 [+0.0018, +0.0143] | -0.0004 [-0.0065, +0.0053] | 0.759 | 0.217 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 141 | 0.457 | 0.447 | 0.0634 | +0.0075 [+0.0015, +0.0132] | -0.0000 [-0.0053, +0.0050] | 0.743 | 0.411 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.512, difference +0.1036 [-0.0114, +0.1993]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0391 [+0.0231, +0.0559], realised minus predicted +0.0459 [+0.0178, +0.0760]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.275 | 0.596 | 0.1781 | 0.2720 | +0.0369 [+0.0121, +0.0653] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0330 | 0.0159 | +0.0236 [+0.0057, +0.0384] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0039 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0145 | 0.0200 | +0.0007 [-0.0062, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.583 | 0.0882 | 0.1165 | +0.0329 [+0.0055, +0.0636] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0088 | 0.0048 | +0.0081 [+0.0057, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0067 | 0.0000 | +0.0303 [+0.0242, +0.0364] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1345 | 0.2439 | 0.0355 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.563 | 0.1815 | 0.2615 | +0.0396 [+0.0158, +0.0655] |
| day_type | month_end | 150 | 17 | 0.529 | 0.643 | 0.1059 | 0.1133 | +0.0414 [+0.0138, +0.0709] |
| day_type | ordinary | 1603 | 101 | 0.208 | 0.438 | 0.0412 | 0.0630 | +0.0140 [+0.0077, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0498, +0.1498] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1308 | 0.1461 | +0.0731 [+0.0420, +0.1104] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3856 | 0.2213 |

## risk_logistic_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.679] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.562] | 0.192 | 1.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.314 (126 of 1873 days never flag) | 78 | 0.307 | 0.551 | 0.0492 | +0.0222 [+0.0158, +0.0294] | +0.0071 [+0.0027, +0.0122] | 0.884 | 0.287 | no |
| 2 | 0.326 (147 of 1872 days never flag) | 92 | 0.331 | 0.500 | 0.0575 | +0.0136 [+0.0090, +0.0185] | +0.0036 [-0.0007, +0.0080] | 0.832 | 0.304 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 70 | 0.261 | 0.514 | 0.0609 | +0.0097 [+0.0041, +0.0158] | +0.0034 [-0.0024, +0.0100] | 0.807 | 0.241 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 89 | 0.304 | 0.472 | 0.0603 | +0.0105 [+0.0051, +0.0158] | +0.0021 [-0.0038, +0.0077] | 0.817 | 0.277 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 79 | 0.290 | 0.506 | 0.0609 | +0.0100 [+0.0054, +0.0145] | +0.0025 [-0.0025, +0.0072] | 0.798 | 0.267 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.622 (climatology 0.512, difference +0.1098 [+0.0160, +0.1912]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0894, ΔBrier vs climatology +0.0401 [+0.0239, +0.0568], realised minus predicted +0.0060 [-0.0246, +0.0398]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.275 | 0.560 | 0.2307 | 0.2720 | +0.0468 [+0.0227, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1153 | 0.0159 | +0.0202 [+0.0089, +0.0305] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0156 | 0.0000 | +0.0133 [+0.0116, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0230 | 0.0200 | +0.0027 [-0.0012, +0.0058] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.684 | 0.0974 | 0.1165 | +0.0335 [+0.0081, +0.0657] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 1.000 | 0.0174 | 0.0048 | +0.0089 [+0.0072, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0607 | 0.0000 | +0.0251 [+0.0196, +0.0310] |
| scarcity_state | 2 | 41 | 10 | 0.200 | 0.500 | 0.1383 | 0.2439 | 0.0357 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.320 | 0.556 | 0.2394 | 0.2615 | +0.0482 [+0.0249, +0.0726] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1100 | 0.1133 | +0.0400 [+0.0130, +0.0693] |
| day_type | ordinary | 1603 | 101 | 0.198 | 0.444 | 0.0743 | 0.0630 | +0.0162 [+0.0102, +0.0229] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0446, +0.1511] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1308 | 0.1461 | +0.0731 [+0.0406, +0.1074] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2519 | 0.2213 |

## risk_logistic_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.216, 0.560] | 0.192 | 2.31 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.516] | 0.192 | 2.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 77 | 0.336 | 0.610 | 0.0482 | +0.0232 [+0.0162, +0.0311] | +0.0081 [+0.0032, +0.0133] | 0.911 | 0.318 | no |
| 2 | 0.579 (147 of 1872 days never flag) | 73 | 0.281 | 0.534 | 0.0576 | +0.0134 [+0.0083, +0.0190] | +0.0034 [-0.0007, +0.0079] | 0.883 | 0.261 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 74 | 0.261 | 0.486 | 0.0608 | +0.0099 [+0.0038, +0.0162] | +0.0036 [-0.0025, +0.0097] | 0.867 | 0.239 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 68 | 0.239 | 0.485 | 0.0605 | +0.0104 [+0.0042, +0.0163] | +0.0019 [-0.0042, +0.0076] | 0.865 | 0.219 | no |
| 5 | 0.334 (147 of 1869 days never flag) | 105 | 0.326 | 0.429 | 0.0617 | +0.0093 [+0.0039, +0.0144] | +0.0017 [-0.0032, +0.0069] | 0.852 | 0.291 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0138, +0.1940]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0869, ΔBrier vs climatology +0.0426 [+0.0265, +0.0601], realised minus predicted +0.0232 [-0.0090, +0.0562]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.727 | 0.2477 | 0.2720 | +0.0525 [+0.0258, +0.0815] |
| regime | 2020 | 251 | 4 | 0.250 | 0.100 | 0.1278 | 0.0159 | +0.0146 [-0.0009, +0.0276] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0043 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0022 | 0.0200 | +0.0036 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.609 | 0.0966 | 0.1165 | +0.0362 [+0.0088, +0.0721] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0011 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0688 | 0.0000 | +0.0240 [+0.0184, +0.0298] |
| scarcity_state | 2 | 41 | 10 | 0.300 | 0.429 | 0.1655 | 0.2439 | 0.0378 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.352 | 0.629 | 0.2580 | 0.2615 | +0.0513 [+0.0275, +0.0789] |
| day_type | month_end | 150 | 17 | 0.471 | 0.727 | 0.1094 | 0.1133 | +0.0409 [+0.0132, +0.0708] |
| day_type | ordinary | 1603 | 101 | 0.257 | 0.542 | 0.0716 | 0.0630 | +0.0173 [+0.0107, +0.0251] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3212 | 0.2903 | +0.0996 [+0.0428, +0.1521] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1308 | 0.1461 | +0.0731 [+0.0417, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3416 | 0.2213 |

## risk_logistic_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.154 | 1.62 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.476] | 0.154 | 1.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.314 (126 of 1873 days never flag) | 98 | 0.400 | 0.571 | 0.0497 | +0.0218 [+0.0168, +0.0272] | +0.0067 [+0.0021, +0.0112] | 0.897 | 0.376 | no |
| 2 | 0.326 (147 of 1872 days never flag) | 51 | 0.173 | 0.471 | 0.0588 | +0.0123 [+0.0082, +0.0168] | +0.0023 [-0.0024, +0.0068] | 0.846 | 0.157 | no |
| 3 | 0.373 (147 of 1871 days never flag) | 48 | 0.188 | 0.542 | 0.0619 | +0.0088 [+0.0034, +0.0140] | +0.0025 [-0.0038, +0.0084] | 0.814 | 0.176 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 47 | 0.159 | 0.468 | 0.0618 | +0.0091 [+0.0038, +0.0139] | +0.0006 [-0.0056, +0.0062] | 0.826 | 0.145 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 71 | 0.232 | 0.451 | 0.0622 | +0.0087 [+0.0042, +0.0130] | +0.0012 [-0.0040, +0.0058] | 0.807 | 0.209 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.613 (climatology 0.512, difference +0.1011 [+0.0066, +0.1784]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0362 [+0.0226, +0.0502], realised minus predicted +0.0375 [+0.0058, +0.0711]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.422 | 0.589 | 0.1771 | 0.2720 | +0.0380 [+0.0234, +0.0555] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0767 | 0.0159 | +0.0278 [+0.0179, +0.0372] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0094 | 0.0000 | +0.0137 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0171 | 0.0200 | +0.0029 [-0.0015, +0.0061] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.786 | 0.0751 | 0.1165 | +0.0344 [+0.0106, +0.0651] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0119 | 0.0048 | +0.0091 [+0.0073, +0.0107] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0371 | 0.0000 | +0.0288 [+0.0228, +0.0347] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.1053 | 0.2439 | 0.0250 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.432 | 0.581 | 0.1828 | 0.2615 | +0.0444 [+0.0278, +0.0633] |
| day_type | month_end | 150 | 17 | 0.647 | 0.733 | 0.1067 | 0.1133 | +0.0386 [+0.0114, +0.0690] |
| day_type | ordinary | 1603 | 101 | 0.297 | 0.484 | 0.0487 | 0.0630 | +0.0158 [+0.0118, +0.0207] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0478, +0.1514] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.750 | 0.1308 | 0.1461 | +0.0731 [+0.0413, +0.1099] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2207 | 0.2213 |

## risk_logistic_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.154, 0.472] | 0.192 | 2.31 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.440] | 0.192 | 2.31 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 51 | 0.250 | 0.686 | 0.0619 | +0.0095 [-0.0005, +0.0194] | -0.0056 [-0.0146, +0.0027] | 0.873 | 0.241 | no |
| 2 | 0.638 (147 of 1872 days never flag) | 71 | 0.245 | 0.479 | 0.0700 | +0.0010 [-0.0078, +0.0098] | -0.0090 [-0.0172, -0.0010] | 0.826 | 0.223 | no |
| 3 | 0.623 (147 of 1871 days never flag) | 106 | 0.333 | 0.434 | 0.0747 | -0.0040 [-0.0148, +0.0054] | -0.0104 [-0.0210, -0.0008] | 0.801 | 0.299 | no |
| 4 | 0.8 (147 of 1870 days never flag) | 81 | 0.261 | 0.444 | 0.0728 | -0.0019 [-0.0103, +0.0065] | -0.0104 [-0.0187, -0.0021] | 0.816 | 0.235 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 101 | 0.333 | 0.455 | 0.0726 | -0.0017 [-0.0088, +0.0050] | -0.0092 [-0.0166, -0.0022] | 0.785 | 0.302 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.612 (climatology 0.512, difference +0.0998 [-0.0011, +0.1827]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0958, ΔBrier vs climatology +0.0337 [+0.0168, +0.0512], realised minus predicted -0.0105 [-0.0446, +0.0227]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.284 | 0.707 | 0.3222 | 0.2720 | +0.0082 [-0.0350, +0.0508] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2026 | 0.0159 | -0.0128 [-0.0340, +0.0052] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0026, +0.0060] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0667 | 0.1165 | +0.0331 [+0.0092, +0.0656] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0101] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1132 | 0.0000 | +0.0107 [+0.0050, +0.0168] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1219 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.280 | 0.700 | 0.3211 | 0.2615 | +0.0093 [-0.0280, +0.0472] |
| day_type | month_end | 150 | 17 | 0.353 | 0.750 | 0.1128 | 0.1133 | +0.0382 [+0.0115, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.188 | 0.633 | 0.1018 | 0.0630 | +0.0015 [-0.0086, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1489] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0411, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.263, 0.600] | 0.192 | 2.31 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.190, 0.501] | 0.192 | 2.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.78 (105 of 1873 days never flag) | 109 | 0.436 | 0.560 | 0.0618 | +0.0097 [-0.0004, +0.0194] | -0.0054 [-0.0145, +0.0029] | 0.876 | 0.408 | no |
| 2 | 0.593 (147 of 1872 days never flag) | 65 | 0.223 | 0.477 | 0.0690 | +0.0021 [-0.0074, +0.0104] | -0.0080 [-0.0169, -0.0003] | 0.828 | 0.203 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 80 | 0.268 | 0.463 | 0.0724 | -0.0017 [-0.0113, +0.0070] | -0.0080 [-0.0175, +0.0004] | 0.803 | 0.243 | no |
| 4 | 0.767 (147 of 1870 days never flag) | 70 | 0.275 | 0.543 | 0.0718 | -0.0010 [-0.0087, +0.0066] | -0.0094 [-0.0175, -0.0020] | 0.818 | 0.257 | no |
| 5 | 0.714 (147 of 1869 days never flag) | 107 | 0.341 | 0.439 | 0.0731 | -0.0022 [-0.0099, +0.0048] | -0.0097 [-0.0177, -0.0025] | 0.789 | 0.306 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.572 (climatology 0.512, difference +0.0594 [-0.0274, +0.1402]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0932, ΔBrier vs climatology +0.0363 [+0.0206, +0.0539], realised minus predicted -0.0102 [-0.0441, +0.0236]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.560 | 0.3272 | 0.2720 | +0.0089 [-0.0381, +0.0531] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2005 | 0.0159 | -0.0120 [-0.0332, +0.0064] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0136] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0031, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0652 | 0.1165 | +0.0325 [+0.0081, +0.0629] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1118 | 0.0000 | +0.0113 [+0.0059, +0.0171] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1208 | 0.2439 | 0.0255 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.565 | 0.3242 | 0.2615 | +0.0097 [-0.0311, +0.0483] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1135 | 0.1133 | +0.0383 [+0.0101, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.506 | 0.1025 | 0.0630 | +0.0017 [-0.0088, +0.0115] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0469, +0.1465] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1283 | 0.1461 | +0.0745 [+0.0438, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2938 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.560] | 0.192 | 2.12 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.560] | 0.192 | 2.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 51 | 0.250 | 0.686 | 0.0619 | +0.0095 [-0.0006, +0.0198] | -0.0056 [-0.0143, +0.0026] | 0.873 | 0.241 | no |
| 2 | 0.849 (147 of 1872 days never flag) | 55 | 0.252 | 0.636 | 0.0646 | +0.0065 [-0.0027, +0.0155] | -0.0035 [-0.0124, +0.0050] | 0.846 | 0.240 | no |
| 3 | 0.625 (126 of 1871 days never flag) | 81 | 0.304 | 0.519 | 0.0676 | +0.0031 [-0.0071, +0.0124] | -0.0033 [-0.0131, +0.0062] | 0.825 | 0.282 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 74 | 0.297 | 0.554 | 0.0667 | +0.0041 [-0.0044, +0.0120] | -0.0043 [-0.0128, +0.0034] | 0.842 | 0.278 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 112 | 0.413 | 0.509 | 0.0666 | +0.0043 [-0.0022, +0.0111] | -0.0032 [-0.0098, +0.0035] | 0.826 | 0.381 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.694 (climatology 0.512, difference +0.1818 [+0.0967, +0.2766]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0830, ΔBrier vs climatology +0.0465 [+0.0284, +0.0667], realised minus predicted -0.0298 [-0.0609, +0.0006]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.284 | 0.707 | 0.3222 | 0.2720 | +0.0082 [-0.0367, +0.0517] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.2026 | 0.0159 | -0.0128 [-0.0357, +0.0061] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0107, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0027, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0667 | 0.1165 | +0.0331 [+0.0079, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0067, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1132 | 0.0000 | +0.0107 [+0.0051, +0.0165] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1219 | 0.2439 | 0.0266 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.280 | 0.700 | 0.3211 | 0.2615 | +0.0093 [-0.0296, +0.0486] |
| day_type | month_end | 150 | 17 | 0.353 | 0.750 | 0.1128 | 0.1133 | +0.0382 [+0.0104, +0.0702] |
| day_type | ordinary | 1603 | 101 | 0.188 | 0.633 | 0.1018 | 0.0630 | +0.0015 [-0.0086, +0.0117] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1508] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0412, +0.1083] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2915 | 0.2213 |

## risk_logistic_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.556] | 0.192 | 1.85 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.225, 0.550] | 0.154 | 1.58 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.78 (105 of 1873 days never flag) | 109 | 0.436 | 0.560 | 0.0618 | +0.0097 [-0.0011, +0.0202] | -0.0054 [-0.0148, +0.0032] | 0.876 | 0.408 | no |
| 2 | 0.772 (147 of 1872 days never flag) | 58 | 0.273 | 0.655 | 0.0645 | +0.0065 [-0.0030, +0.0152] | -0.0035 [-0.0126, +0.0048] | 0.848 | 0.262 | no |
| 3 | 0.625 (147 of 1871 days never flag) | 51 | 0.217 | 0.588 | 0.0673 | +0.0034 [-0.0068, +0.0122] | -0.0030 [-0.0128, +0.0057] | 0.826 | 0.205 | no |
| 4 | 0.8 (105 of 1870 days never flag) | 77 | 0.304 | 0.545 | 0.0660 | +0.0048 [-0.0032, +0.0128] | -0.0037 [-0.0121, +0.0044] | 0.842 | 0.284 | no |
| 5 | 0.846 (147 of 1869 days never flag) | 89 | 0.348 | 0.539 | 0.0665 | +0.0044 [-0.0029, +0.0116] | -0.0031 [-0.0102, +0.0042] | 0.826 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1655 [+0.0644, +0.2701]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0826, ΔBrier vs climatology +0.0469 [+0.0274, +0.0694], realised minus predicted -0.0294 [-0.0594, +0.0036]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.549 | 0.560 | 0.3272 | 0.2720 | +0.0089 [-0.0382, +0.0539] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.2005 | 0.0159 | -0.0120 [-0.0344, +0.0058] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0157 | 0.0000 | +0.0120 [+0.0106, +0.0135] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0064 | 0.0200 | +0.0025 [-0.0027, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0652 | 0.1165 | +0.0325 [+0.0076, +0.0626] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0085 [+0.0068, +0.0102] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1118 | 0.0000 | +0.0113 [+0.0057, +0.0170] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1208 | 0.2439 | 0.0255 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.488 | 0.565 | 0.3242 | 0.2615 | +0.0097 [-0.0311, +0.0495] |
| day_type | month_end | 150 | 17 | 0.529 | 0.692 | 0.1135 | 0.1133 | +0.0383 [+0.0102, +0.0683] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.506 | 0.1025 | 0.0630 | +0.0017 [-0.0091, +0.0123] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0474, +0.1469] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.700 | 0.1283 | 0.1461 | +0.0745 [+0.0424, +0.1142] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2938 | 0.2213 |

## risk_logistic_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.214, 0.562] | 0.231 | 2.96 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.550] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 76 | 0.336 | 0.618 | 0.0574 | +0.0140 [+0.0066, +0.0226] | -0.0011 [-0.0069, +0.0054] | 0.847 | 0.319 | no |
| 2 | 0.579 (147 of 1872 days never flag) | 80 | 0.237 | 0.412 | 0.0682 | +0.0029 [-0.0032, +0.0090] | -0.0071 [-0.0133, -0.0006] | 0.784 | 0.210 | no |
| 3 | 0.483 (147 of 1871 days never flag) | 81 | 0.268 | 0.457 | 0.0721 | -0.0014 [-0.0082, +0.0052] | -0.0077 [-0.0148, -0.0009] | 0.732 | 0.243 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 87 | 0.268 | 0.425 | 0.0717 | -0.0009 [-0.0080, +0.0059] | -0.0093 [-0.0172, -0.0018] | 0.755 | 0.239 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 124 | 0.341 | 0.379 | 0.0727 | -0.0017 [-0.0083, +0.0043] | -0.0093 [-0.0166, -0.0026] | 0.726 | 0.296 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0979 [-0.0034, +0.1793]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0988, ΔBrier vs climatology +0.0307 [+0.0146, +0.0474], realised minus predicted -0.0277 [-0.0630, +0.0092]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.667 | 0.2932 | 0.2720 | +0.0342 [+0.0043, +0.0702] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2108 | 0.0159 | -0.0108 [-0.0251, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0025 [-0.0025, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0654 | 0.1165 | +0.0310 [+0.0087, +0.0577] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0064, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1328 | 0.0000 | +0.0049 [-0.0002, +0.0105] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0990 | 0.2439 | 0.0054 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.630 | 0.2957 | 0.2615 | +0.0336 [+0.0056, +0.0664] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1135 | 0.1133 | +0.0374 [+0.0114, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.562 | 0.1060 | 0.0630 | +0.0069 [-0.0002, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3212 | 0.2903 | +0.0996 [+0.0501, +0.1483] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0731 [+0.0420, +0.1101] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 2.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.565] | 0.231 | 2.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 121 | 0.486 | 0.562 | 0.0572 | +0.0142 [+0.0065, +0.0226] | -0.0009 [-0.0072, +0.0056] | 0.850 | 0.455 | no |
| 2 | 0.489 (147 of 1872 days never flag) | 76 | 0.237 | 0.434 | 0.0672 | +0.0039 [-0.0022, +0.0102] | -0.0061 [-0.0116, -0.0002] | 0.785 | 0.213 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 88 | 0.290 | 0.455 | 0.0697 | +0.0010 [-0.0044, +0.0063] | -0.0053 [-0.0105, +0.0006] | 0.735 | 0.262 | no |
| 4 | 0.513 (147 of 1870 days never flag) | 97 | 0.326 | 0.464 | 0.0708 | +0.0001 [-0.0062, +0.0060] | -0.0084 [-0.0149, -0.0025] | 0.755 | 0.296 | no |
| 5 | 0.498 (147 of 1869 days never flag) | 124 | 0.341 | 0.379 | 0.0732 | -0.0022 [-0.0088, +0.0043] | -0.0098 [-0.0176, -0.0025] | 0.732 | 0.296 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0632 [-0.0255, +0.1421]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0963, ΔBrier vs climatology +0.0332 [+0.0177, +0.0499], realised minus predicted -0.0274 [-0.0626, +0.0096]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.574 | 0.2982 | 0.2720 | +0.0350 [+0.0016, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2086 | 0.0159 | -0.0099 [-0.0240, +0.0027] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0119] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0110 | 0.0200 | +0.0026 [-0.0024, +0.0061] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0640 | 0.1165 | +0.0304 [+0.0082, +0.0563] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0065, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1314 | 0.0000 | +0.0055 [+0.0005, +0.0109] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0980 | 0.2439 | 0.0044 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.563 | 0.2988 | 0.2615 | +0.0340 [+0.0041, +0.0652] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1142 | 0.1133 | +0.0375 [+0.0103, +0.0658] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.512 | 0.1068 | 0.0630 | +0.0070 [-0.0007, +0.0154] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0466, +0.1439] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1283 | 0.1461 | +0.0745 [+0.0446, +0.1114] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2896 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.300, 0.630] | 0.231 | 2.69 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.629] | 0.231 | 2.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 76 | 0.336 | 0.618 | 0.0574 | +0.0140 [+0.0062, +0.0223] | -0.0011 [-0.0072, +0.0053] | 0.847 | 0.319 | no |
| 2 | 0.849 (147 of 1872 days never flag) | 39 | 0.201 | 0.718 | 0.0620 | +0.0091 [+0.0024, +0.0158] | -0.0009 [-0.0074, +0.0057] | 0.812 | 0.195 | no |
| 3 | 0.848 (126 of 1871 days never flag) | 95 | 0.348 | 0.505 | 0.0644 | +0.0063 [+0.0003, +0.0127] | -0.0001 [-0.0061, +0.0066] | 0.770 | 0.321 | no |
| 4 | 0.528 (126 of 1870 days never flag) | 109 | 0.377 | 0.477 | 0.0653 | +0.0055 [-0.0009, +0.0119] | -0.0029 [-0.0098, +0.0037] | 0.791 | 0.344 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 125 | 0.399 | 0.440 | 0.0663 | +0.0046 [-0.0017, +0.0108] | -0.0029 [-0.0095, +0.0041] | 0.778 | 0.358 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.695 (climatology 0.512, difference +0.1830 [+0.0978, +0.2723]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0848, ΔBrier vs climatology +0.0447 [+0.0266, +0.0651], realised minus predicted -0.0487 [-0.0806, -0.0151]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.353 | 0.667 | 0.2932 | 0.2720 | +0.0342 [+0.0036, +0.0693] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.2108 | 0.0159 | -0.0108 [-0.0252, +0.0015] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0118] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0109 | 0.0200 | +0.0025 [-0.0025, +0.0063] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0654 | 0.1165 | +0.0310 [+0.0081, +0.0583] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0064, +0.0095] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1328 | 0.0000 | +0.0049 [-0.0003, +0.0102] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0990 | 0.2439 | 0.0054 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.368 | 0.630 | 0.2957 | 0.2615 | +0.0336 [+0.0033, +0.0648] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1135 | 0.1133 | +0.0374 [+0.0101, +0.0665] |
| day_type | ordinary | 1603 | 101 | 0.267 | 0.562 | 0.1060 | 0.0630 | +0.0069 [-0.0005, +0.0148] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.3212 | 0.2903 | +0.0996 [+0.0466, +0.1500] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1308 | 0.1461 | +0.0731 [+0.0407, +0.1105] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.292, 0.640] | 0.192 | 2.42 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.625] | 0.192 | 2.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 121 | 0.486 | 0.562 | 0.0572 | +0.0142 [+0.0064, +0.0223] | -0.0009 [-0.0072, +0.0059] | 0.850 | 0.455 | no |
| 2 | 0.772 (147 of 1872 days never flag) | 44 | 0.230 | 0.727 | 0.0619 | +0.0092 [+0.0026, +0.0157] | -0.0008 [-0.0072, +0.0061] | 0.815 | 0.223 | no |
| 3 | 0.466 (147 of 1871 days never flag) | 50 | 0.232 | 0.640 | 0.0641 | +0.0066 [+0.0006, +0.0128] | +0.0002 [-0.0062, +0.0067] | 0.769 | 0.221 | no |
| 4 | 0.866 (105 of 1870 days never flag) | 105 | 0.370 | 0.486 | 0.0646 | +0.0062 [+0.0000, +0.0124] | -0.0023 [-0.0088, +0.0043] | 0.789 | 0.338 | no |
| 5 | 0.846 (147 of 1869 days never flag) | 115 | 0.377 | 0.452 | 0.0663 | +0.0047 [-0.0018, +0.0108] | -0.0029 [-0.0093, +0.0041] | 0.777 | 0.340 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1661 [+0.0643, +0.2681]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0844, ΔBrier vs climatology +0.0451 [+0.0263, +0.0662], realised minus predicted -0.0484 [-0.0790, -0.0161]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.574 | 0.2982 | 0.2720 | +0.0350 [+0.0007, +0.0689] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2086 | 0.0159 | -0.0099 [-0.0234, +0.0031] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0357 | 0.0000 | +0.0104 [+0.0088, +0.0120] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0110 | 0.0200 | +0.0026 [-0.0024, +0.0062] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.750 | 0.0640 | 0.1165 | +0.0304 [+0.0085, +0.0558] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0208 | 0.0048 | +0.0081 [+0.0065, +0.0096] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.1314 | 0.0000 | +0.0055 [+0.0005, +0.0112] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0980 | 0.2439 | 0.0044 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.563 | 0.2988 | 0.2615 | +0.0340 [+0.0036, +0.0657] |
| day_type | month_end | 150 | 17 | 0.588 | 0.667 | 0.1142 | 0.1133 | +0.0375 [+0.0089, +0.0673] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.512 | 0.1068 | 0.0630 | +0.0070 [-0.0006, +0.0151] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0459, +0.1466] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.667 | 0.1283 | 0.1461 | +0.0745 [+0.0436, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2896 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 9 | 0.346 [0.176, 0.531] | 0.231 | 3.00 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.143, 0.500] | 0.231 | 3.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 72 | 0.357 | 0.694 | 0.0576 | +0.0138 [+0.0036, +0.0238] | -0.0012 [-0.0102, +0.0072] | 0.919 | 0.344 | no |
| 2 | 0.638 (147 of 1872 days never flag) | 82 | 0.295 | 0.500 | 0.0648 | +0.0063 [-0.0029, +0.0149] | -0.0037 [-0.0122, +0.0039] | 0.886 | 0.271 | no |
| 3 | 0.623 (147 of 1871 days never flag) | 86 | 0.275 | 0.442 | 0.0682 | +0.0025 [-0.0080, +0.0125] | -0.0039 [-0.0147, +0.0059] | 0.891 | 0.248 | no |
| 4 | 0.677 (147 of 1870 days never flag) | 69 | 0.210 | 0.420 | 0.0681 | +0.0027 [-0.0054, +0.0104] | -0.0057 [-0.0138, +0.0023] | 0.849 | 0.187 | no |
| 5 | 0.698 (147 of 1869 days never flag) | 147 | 0.500 | 0.469 | 0.0726 | -0.0016 [-0.0114, +0.0068] | -0.0092 [-0.0188, -0.0007] | 0.824 | 0.455 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.625 (climatology 0.512, difference +0.1133 [+0.0190, +0.1877]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0902, ΔBrier vs climatology +0.0393 [+0.0224, +0.0586], realised minus predicted +0.0071 [-0.0262, +0.0417]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.721 | 0.3231 | 0.2720 | +0.0120 [-0.0311, +0.0540] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0944 | 0.0159 | +0.0086 [-0.0194, +0.0308] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0036 [-0.0002, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0757 | 0.1165 | +0.0321 [+0.0093, +0.0610] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0078, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0065 | 0.0000 | +0.0304 [+0.0245, +0.0364] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0703 | 0.2439 | 0.0173 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.704 | 0.3294 | 0.2615 | +0.0123 [-0.0276, +0.0516] |
| day_type | month_end | 150 | 17 | 0.353 | 0.600 | 0.1092 | 0.1133 | +0.0389 [+0.0110, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.688 | 0.0789 | 0.0630 | +0.0065 [-0.0039, +0.0165] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0463, +0.1499] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.875 | 0.1308 | 0.1461 | +0.0731 [+0.0408, +0.1101] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2847 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.682] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.560] | 0.192 | 2.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (105 of 1873 days never flag) | 127 | 0.479 | 0.528 | 0.0578 | +0.0136 [+0.0034, +0.0232] | -0.0015 [-0.0106, +0.0068] | 0.920 | 0.444 | no |
| 2 | 0.593 (147 of 1872 days never flag) | 66 | 0.230 | 0.485 | 0.0640 | +0.0071 [-0.0026, +0.0158] | -0.0029 [-0.0121, +0.0050] | 0.888 | 0.211 | no |
| 3 | 0.639 (147 of 1871 days never flag) | 83 | 0.275 | 0.458 | 0.0659 | +0.0048 [-0.0066, +0.0144] | -0.0015 [-0.0121, +0.0079] | 0.894 | 0.249 | no |
| 4 | 0.662 (147 of 1870 days never flag) | 82 | 0.319 | 0.537 | 0.0644 | +0.0064 [-0.0012, +0.0134] | -0.0021 [-0.0096, +0.0049] | 0.881 | 0.297 | no |
| 5 | 0.557 (147 of 1869 days never flag) | 111 | 0.348 | 0.432 | 0.0674 | +0.0035 [-0.0037, +0.0105] | -0.0040 [-0.0117, +0.0033] | 0.829 | 0.311 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.575 (climatology 0.512, difference +0.0632 [-0.0322, +0.1440]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0255, +0.0601], realised minus predicted +0.0088 [-0.0222, +0.0416]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.521 | 0.3287 | 0.2720 | +0.0109 [-0.0337, +0.0521] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0929 | 0.0159 | +0.0091 [-0.0177, +0.0319] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0743 | 0.1165 | +0.0318 [+0.0094, +0.0586] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0051 | 0.0000 | +0.0310 [+0.0241, +0.0371] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0693 | 0.2439 | 0.0163 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.532 | 0.3334 | 0.2615 | +0.0111 [-0.0278, +0.0487] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1101 | 0.1133 | +0.0393 [+0.0095, +0.0699] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.463 | 0.0799 | 0.0630 | +0.0062 [-0.0042, +0.0159] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0475, +0.1473] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0425, +0.1110] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.550] | 0.154 | 1.65 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.545] | 0.154 | 1.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.688 (147 of 1873 days never flag) | 72 | 0.357 | 0.694 | 0.0576 | +0.0138 [+0.0040, +0.0236] | -0.0012 [-0.0095, +0.0064] | 0.919 | 0.344 | no |
| 2 | 0.849 (147 of 1872 days never flag) | 69 | 0.288 | 0.580 | 0.0600 | +0.0110 [+0.0013, +0.0200] | +0.0010 [-0.0082, +0.0098] | 0.896 | 0.271 | no |
| 3 | 0.848 (126 of 1871 days never flag) | 72 | 0.283 | 0.542 | 0.0620 | +0.0086 [-0.0024, +0.0179] | +0.0023 [-0.0085, +0.0119] | 0.898 | 0.264 | no |
| 4 | 0.778 (126 of 1870 days never flag) | 80 | 0.319 | 0.550 | 0.0627 | +0.0082 [+0.0004, +0.0157] | -0.0003 [-0.0082, +0.0073] | 0.864 | 0.298 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 91 | 0.348 | 0.527 | 0.0672 | +0.0037 [-0.0054, +0.0121] | -0.0038 [-0.0127, +0.0047] | 0.850 | 0.323 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.694 (climatology 0.512, difference +0.1818 [+0.0954, +0.2710]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0785, ΔBrier vs climatology +0.0510 [+0.0324, +0.0713], realised minus predicted -0.0118 [-0.0420, +0.0190]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.431 | 0.721 | 0.3231 | 0.2720 | +0.0120 [-0.0302, +0.0532] |
| regime | 2020 | 251 | 4 | 0.250 | 0.200 | 0.0944 | 0.0159 | +0.0086 [-0.0190, +0.0310] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0028 | 0.0200 | +0.0036 [-0.0000, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0757 | 0.1165 | +0.0321 [+0.0099, +0.0596] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0065 | 0.0000 | +0.0304 [+0.0240, +0.0361] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0703 | 0.2439 | 0.0173 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.400 | 0.704 | 0.3294 | 0.2615 | +0.0123 [-0.0245, +0.0493] |
| day_type | month_end | 150 | 17 | 0.353 | 0.600 | 0.1092 | 0.1133 | +0.0389 [+0.0117, +0.0689] |
| day_type | ordinary | 1603 | 101 | 0.327 | 0.688 | 0.0789 | 0.0630 | +0.0065 [-0.0034, +0.0165] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0466, +0.1495] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.875 | 0.1308 | 0.1461 | +0.0731 [+0.0398, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2847 | 0.2213 |

## risk_logistic_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.296, 0.636] | 0.192 | 2.31 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.219, 0.556] | 0.192 | 1.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.727 (105 of 1873 days never flag) | 127 | 0.479 | 0.528 | 0.0578 | +0.0136 [+0.0035, +0.0235] | -0.0015 [-0.0104, +0.0069] | 0.920 | 0.444 | no |
| 2 | 0.625 (147 of 1872 days never flag) | 67 | 0.295 | 0.612 | 0.0601 | +0.0110 [+0.0017, +0.0197] | +0.0010 [-0.0078, +0.0093] | 0.898 | 0.280 | no |
| 3 | 0.836 (147 of 1871 days never flag) | 47 | 0.210 | 0.617 | 0.0619 | +0.0088 [-0.0019, +0.0182] | +0.0025 [-0.0084, +0.0116] | 0.900 | 0.200 | no |
| 4 | 0.7 (105 of 1870 days never flag) | 105 | 0.413 | 0.543 | 0.0595 | +0.0114 [+0.0042, +0.0185] | +0.0029 [-0.0043, +0.0103] | 0.891 | 0.385 | no |
| 5 | 0.846 (147 of 1869 days never flag) | 99 | 0.384 | 0.535 | 0.0613 | +0.0096 [+0.0026, +0.0161] | +0.0021 [-0.0050, +0.0090] | 0.853 | 0.357 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.678 (climatology 0.512, difference +0.1661 [+0.0682, +0.2659]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0776, ΔBrier vs climatology +0.0518 [+0.0332, +0.0735], realised minus predicted -0.0096 [-0.0383, +0.0214]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.598 | 0.521 | 0.3287 | 0.2720 | +0.0109 [-0.0334, +0.0545] |
| regime | 2020 | 251 | 4 | 0.250 | 0.250 | 0.0929 | 0.0159 | +0.0091 [-0.0188, +0.0316] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0029 | 0.0200 | +0.0037 [+0.0002, +0.0066] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0743 | 0.1165 | +0.0318 [+0.0089, +0.0605] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0111] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0051 | 0.0000 | +0.0310 [+0.0246, +0.0368] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0693 | 0.2439 | 0.0163 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.536 | 0.532 | 0.3334 | 0.2615 | +0.0111 [-0.0284, +0.0494] |
| day_type | month_end | 150 | 17 | 0.588 | 0.714 | 0.1101 | 0.1133 | +0.0393 [+0.0106, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.463 | 0.0799 | 0.0630 | +0.0062 [-0.0044, +0.0163] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3184 | 0.2903 | +0.0979 [+0.0480, +0.1453] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0429, +0.1115] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2872 | 0.2213 |

## risk_logistic_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.606] | 0.231 | 3.65 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.606] | 0.231 | 3.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 85 | 0.407 | 0.671 | 0.0512 | +0.0203 [+0.0124, +0.0285] | +0.0052 [-0.0007, +0.0111] | 0.901 | 0.391 | no |
| 2 | 0.579 (147 of 1872 days never flag) | 79 | 0.223 | 0.392 | 0.0598 | +0.0113 [+0.0050, +0.0178] | +0.0013 [-0.0045, +0.0073] | 0.863 | 0.195 | no |
| 3 | 0.483 (147 of 1871 days never flag) | 106 | 0.312 | 0.406 | 0.0623 | +0.0084 [+0.0020, +0.0148] | +0.0021 [-0.0043, +0.0088] | 0.858 | 0.275 | no |
| 4 | 0.48 (147 of 1870 days never flag) | 87 | 0.239 | 0.379 | 0.0642 | +0.0066 [+0.0000, +0.0130] | -0.0019 [-0.0089, +0.0055] | 0.830 | 0.208 | no |
| 5 | 0.552 (147 of 1869 days never flag) | 161 | 0.478 | 0.410 | 0.0690 | +0.0019 [-0.0046, +0.0079] | -0.0056 [-0.0128, +0.0011] | 0.789 | 0.423 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.623 (climatology 0.512, difference +0.1111 [+0.0204, +0.1948]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0924, ΔBrier vs climatology +0.0371 [+0.0212, +0.0547], realised minus predicted +0.0051 [-0.0271, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.667 | 0.2840 | 0.2720 | +0.0408 [+0.0093, +0.0724] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1330 | 0.0159 | +0.0121 [-0.0077, +0.0283] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0032 | 0.0200 | +0.0036 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0734 | 0.1165 | +0.0345 [+0.0094, +0.0662] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0538 | 0.0000 | +0.0269 [+0.0214, +0.0328] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0987 | 0.2439 | 0.0159 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.679 | 0.2915 | 0.2615 | +0.0398 [+0.0095, +0.0713] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1106 | 0.1133 | +0.0395 [+0.0109, +0.0692] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.645 | 0.0788 | 0.0630 | +0.0140 [+0.0065, +0.0222] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0458, +0.1491] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0418, +0.1090] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2756 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.364, 0.714] | 0.231 | 3.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.214, 0.560] | 0.231 | 3.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 137 | 0.507 | 0.518 | 0.0512 | +0.0202 [+0.0123, +0.0288] | +0.0051 [-0.0009, +0.0112] | 0.901 | 0.469 | no |
| 2 | 0.593 (147 of 1872 days never flag) | 85 | 0.259 | 0.424 | 0.0589 | +0.0121 [+0.0060, +0.0187] | +0.0021 [-0.0035, +0.0079] | 0.865 | 0.231 | no |
| 3 | 0.442 (147 of 1871 days never flag) | 120 | 0.348 | 0.400 | 0.0601 | +0.0106 [+0.0054, +0.0163] | +0.0043 [-0.0009, +0.0100] | 0.860 | 0.306 | no |
| 4 | 0.474 (147 of 1870 days never flag) | 87 | 0.312 | 0.494 | 0.0618 | +0.0091 [+0.0035, +0.0147] | +0.0006 [-0.0053, +0.0068] | 0.841 | 0.286 | no |
| 5 | 0.489 (147 of 1869 days never flag) | 129 | 0.362 | 0.388 | 0.0675 | +0.0035 [-0.0036, +0.0100] | -0.0041 [-0.0116, +0.0029] | 0.801 | 0.317 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.577 (climatology 0.512, difference +0.0651 [-0.0283, +0.1509]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0888, ΔBrier vs climatology +0.0407 [+0.0254, +0.0568], realised minus predicted +0.0093 [-0.0226, +0.0439]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.2907 | 0.2720 | +0.0403 [+0.0075, +0.0741] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1319 | 0.0159 | +0.0127 [-0.0058, +0.0301] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0076 | 0.0000 | +0.0135 [+0.0118, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0033 | 0.0200 | +0.0037 [-0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0714 | 0.1165 | +0.0340 [+0.0099, +0.0637] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0540 | 0.0000 | +0.0273 [+0.0217, +0.0334] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0937 | 0.2439 | 0.0154 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.519 | 0.2958 | 0.2615 | +0.0392 [+0.0088, +0.0721] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1113 | 0.1133 | +0.0396 [+0.0110, +0.0709] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.451 | 0.0801 | 0.0630 | +0.0138 [+0.0064, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0430, +0.1462] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0431, +0.1134] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2776 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.294, 0.630] | 0.231 | 2.65 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.300, 0.622] | 0.231 | 2.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.797 (147 of 1873 days never flag) | 85 | 0.407 | 0.671 | 0.0512 | +0.0203 [+0.0122, +0.0287] | +0.0052 [-0.0006, +0.0112] | 0.901 | 0.391 | no |
| 2 | 0.849 (147 of 1872 days never flag) | 66 | 0.230 | 0.485 | 0.0542 | +0.0168 [+0.0100, +0.0241] | +0.0068 [+0.0003, +0.0135] | 0.877 | 0.211 | no |
| 3 | 0.438 (126 of 1871 days never flag) | 98 | 0.362 | 0.510 | 0.0555 | +0.0152 [+0.0089, +0.0217] | +0.0089 [+0.0025, +0.0157] | 0.867 | 0.335 | no |
| 4 | 0.528 (126 of 1870 days never flag) | 115 | 0.406 | 0.487 | 0.0585 | +0.0124 [+0.0060, +0.0187] | +0.0039 [-0.0031, +0.0109] | 0.848 | 0.372 | no |
| 5 | 0.855 (147 of 1869 days never flag) | 121 | 0.377 | 0.430 | 0.0632 | +0.0077 [+0.0015, +0.0139] | +0.0002 [-0.0062, +0.0070] | 0.827 | 0.337 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.695 (climatology 0.512, difference +0.1824 [+0.0988, +0.2706]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0788, ΔBrier vs climatology +0.0507 [+0.0319, +0.0706], realised minus predicted -0.0157 [-0.0465, +0.0164]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.667 | 0.2840 | 0.2720 | +0.0408 [+0.0099, +0.0756] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.1330 | 0.0159 | +0.0121 [-0.0068, +0.0290] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0074 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0032 | 0.0200 | +0.0036 [+0.0001, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.857 | 0.0734 | 0.1165 | +0.0345 [+0.0094, +0.0650] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0538 | 0.0000 | +0.0269 [+0.0213, +0.0329] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0987 | 0.2439 | 0.0159 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.679 | 0.2915 | 0.2615 | +0.0398 [+0.0092, +0.0714] |
| day_type | month_end | 150 | 17 | 0.412 | 0.700 | 0.1106 | 0.1133 | +0.0395 [+0.0122, +0.0696] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.645 | 0.0788 | 0.0630 | +0.0140 [+0.0064, +0.0221] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3212 | 0.2903 | +0.0996 [+0.0460, +0.1502] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.857 | 0.1308 | 0.1461 | +0.0731 [+0.0428, +0.1100] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2756 | 0.2213 |

## risk_logistic_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 2.54 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.292, 0.633] | 0.192 | 2.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.586 (105 of 1873 days never flag) | 137 | 0.507 | 0.518 | 0.0512 | +0.0202 [+0.0123, +0.0285] | +0.0051 [-0.0011, +0.0112] | 0.901 | 0.469 | no |
| 2 | 0.772 (147 of 1872 days never flag) | 70 | 0.252 | 0.500 | 0.0543 | +0.0168 [+0.0096, +0.0235] | +0.0068 [+0.0002, +0.0135] | 0.879 | 0.232 | no |
| 3 | 0.836 (147 of 1871 days never flag) | 44 | 0.246 | 0.773 | 0.0554 | +0.0153 [+0.0094, +0.0217] | +0.0090 [+0.0032, +0.0154] | 0.868 | 0.241 | no |
| 4 | 0.476 (105 of 1870 days never flag) | 115 | 0.406 | 0.487 | 0.0563 | +0.0145 [+0.0086, +0.0206] | +0.0061 [-0.0002, +0.0128] | 0.856 | 0.372 | no |
| 5 | 0.846 (147 of 1869 days never flag) | 100 | 0.384 | 0.530 | 0.0612 | +0.0097 [+0.0034, +0.0159] | +0.0022 [-0.0046, +0.0089] | 0.835 | 0.357 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.679 (climatology 0.512, difference +0.1668 [+0.0734, +0.2681]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0771, ΔBrier vs climatology +0.0524 [+0.0333, +0.0719], realised minus predicted -0.0116 [-0.0411, +0.0184]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.516 | 0.2907 | 0.2720 | +0.0403 [+0.0076, +0.0757] |
| regime | 2020 | 251 | 4 | 0.250 | 0.143 | 0.1319 | 0.0159 | +0.0127 [-0.0078, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0076 | 0.0000 | +0.0135 [+0.0118, +0.0153] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0033 | 0.0200 | +0.0037 [+0.0002, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.875 | 0.0714 | 0.1165 | +0.0340 [+0.0093, +0.0646] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | – | 0.0041 | 0.0048 | +0.0095 [+0.0078, +0.0110] |
| scarcity_state | 1 | 313 | 0 | – | – | 0.0540 | 0.0000 | +0.0273 [+0.0212, +0.0330] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.500 | 0.0937 | 0.2439 | 0.0154 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.519 | 0.2958 | 0.2615 | +0.0392 [+0.0091, +0.0706] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1113 | 0.1133 | +0.0396 [+0.0112, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.455 | 0.451 | 0.0801 | 0.0630 | +0.0138 [+0.0061, +0.0220] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3184 | 0.2903 | +0.0979 [+0.0456, +0.1459] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.1283 | 0.1461 | +0.0745 [+0.0425, +0.1129] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2776 | 0.2213 |

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.450, 0.773] | 0.231 | 2.50 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.545] | 0.231 | 2.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.355 (21 of 1873 days never flag) | 101 | 0.329 | 0.455 | 0.0643 | +0.0071 [+0.0015, +0.0131] | -0.0080 [-0.0162, -0.0004] | 0.645 | 0.297 | no |
| 2 | 0.475 (126 of 1872 days never flag) | 64 | 0.194 | 0.422 | 0.0676 | +0.0034 [-0.0037, +0.0106] | -0.0066 [-0.0150, +0.0013] | 0.575 | 0.173 | no |
| 3 | 0.184 (126 of 1871 days never flag) | 72 | 0.188 | 0.361 | 0.0670 | +0.0037 [-0.0035, +0.0104] | -0.0027 [-0.0104, +0.0047] | 0.582 | 0.162 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 94 | 0.210 | 0.309 | 0.0671 | +0.0037 [-0.0026, +0.0096] | -0.0048 [-0.0123, +0.0018] | 0.579 | 0.173 | no |
| 5 | 0.0988 (126 of 1869 days never flag) | 80 | 0.203 | 0.350 | 0.0663 | +0.0047 [-0.0022, +0.0109] | -0.0029 [-0.0104, +0.0041] | 0.581 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 3.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 3.6 over 1041 days; regime_2021-23: 4.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.9 over 1041 days; regime_2021-23: 1.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.642 (climatology 0.512, difference +0.1298 [+0.0281, +0.2339]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1113, ΔBrier vs climatology +0.0182 [+0.0076, +0.0297], realised minus predicted +0.0591 [+0.0253, +0.0967]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.314 | 0.627 | 0.0990 | 0.2720 | -0.0111 [-0.0320, +0.0100] |
| regime | 2020 | 251 | 4 | 0.250 | 0.031 | 0.0630 | 0.0159 | +0.0047 [-0.0118, +0.0203] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0109 | 0.0200 | +0.0018 [-0.0033, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.750 | 0.0489 | 0.1165 | +0.0227 [+0.0039, +0.0475] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0056 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0333 | 0.0000 | +0.0121 [-0.0003, +0.0227] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.0819 | 0.2439 | -0.0305 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.352 | 0.603 | 0.1054 | 0.2615 | +0.0034 [-0.0176, +0.0257] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1188 | 0.1133 | +0.0214 [-0.0122, +0.0556] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.444 | 0.0146 | 0.0630 | +0.0008 [-0.0048, +0.0059] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3544 | 0.2903 | +0.0945 [+0.0001, +0.1888] |
| day_type | tax_date | 89 | 13 | 0.846 | 0.458 | 0.2000 | 0.1461 | +0.0663 [+0.0181, +0.1187] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.325, 0.667] | 0.192 | 1.96 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.194, 0.500] | 0.154 | 1.54 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.26 (126 of 1873 days never flag) | 94 | 0.307 | 0.457 | 0.0648 | +0.0066 [-0.0000, +0.0132] | -0.0084 [-0.0172, +0.0000] | 0.638 | 0.278 | no |
| 2 | 0.171 (126 of 1872 days never flag) | 68 | 0.209 | 0.426 | 0.0687 | +0.0024 [-0.0055, +0.0094] | -0.0076 [-0.0167, -0.0000] | 0.579 | 0.186 | no |
| 3 | 0.294 (126 of 1871 days never flag) | 70 | 0.217 | 0.429 | 0.0679 | +0.0028 [-0.0046, +0.0098] | -0.0035 [-0.0116, +0.0039] | 0.584 | 0.194 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0666 | +0.0042 [-0.0031, +0.0111] | -0.0042 [-0.0124, +0.0035] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 55 | 0.203 | 0.509 | 0.0665 | +0.0044 [-0.0025, +0.0111] | -0.0031 [-0.0114, +0.0046] | 0.584 | 0.187 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.599 (climatology 0.512, difference +0.0867 [-0.0682, +0.2247]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1069, ΔBrier vs climatology +0.0226 [+0.0098, +0.0359], realised minus predicted +0.0552 [+0.0212, +0.0901]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.625 | 0.1190 | 0.2720 | -0.0214 [-0.0472, +0.0047] |
| regime | 2020 | 251 | 4 | 0.250 | 0.034 | 0.0535 | 0.0159 | +0.0165 [+0.0051, +0.0274] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0116 | 0.0200 | +0.0014 [-0.0050, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0522 | 0.1165 | +0.0232 [+0.0036, +0.0459] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.333 | 0.0055 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0303 | 0.0000 | +0.0173 [+0.0085, +0.0247] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.0788 | 0.2439 | -0.0198 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.328 | 0.612 | 0.1206 | 0.2615 | -0.0027 [-0.0269, +0.0225] |
| day_type | month_end | 150 | 17 | 0.765 | 0.464 | 0.1438 | 0.1133 | +0.0138 [-0.0251, +0.0536] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.441 | 0.0161 | 0.0630 | +0.0022 [-0.0035, +0.0076] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.3214 | 0.2903 | +0.0712 [-0.0019, +0.1363] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.2112 | 0.1461 | +0.0525 [+0.0089, +0.0978] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base+every_day (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.409, 0.750] | 0.231 | 2.58 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.667] | 0.231 | 2.58 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 135 | 0.514 | 0.533 | 0.0549 | +0.0166 [+0.0078, +0.0256] | +0.0015 [-0.0051, +0.0076] | 0.879 | 0.478 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0601 | +0.0109 [+0.0049, +0.0173] | +0.0009 [-0.0039, +0.0056] | 0.846 | 0.230 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 116 | 0.355 | 0.422 | 0.0617 | +0.0089 [+0.0030, +0.0153] | +0.0026 [-0.0027, +0.0081] | 0.834 | 0.316 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 112 | 0.399 | 0.491 | 0.0591 | +0.0117 [+0.0055, +0.0184] | +0.0032 [-0.0022, +0.0090] | 0.847 | 0.366 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 113 | 0.355 | 0.434 | 0.0599 | +0.0110 [+0.0051, +0.0174] | +0.0035 [-0.0016, +0.0093] | 0.842 | 0.318 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.512, difference +0.1248 [+0.0086, +0.2320]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0885, ΔBrier vs climatology +0.0410 [+0.0234, +0.0604], realised minus predicted -0.0190 [-0.0489, +0.0130]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.580 | 0.2604 | 0.2720 | +0.0343 [+0.0002, +0.0683] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1562 | 0.0159 | +0.0002 [-0.0148, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0214 | 0.0000 | +0.0130 [+0.0112, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0417 | 0.0200 | -0.0016 [-0.0088, +0.0039] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1284 | 0.1165 | +0.0351 [+0.0021, +0.0751] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0271 | 0.0048 | +0.0072 [+0.0045, +0.0094] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0936 | 0.0000 | +0.0109 [+0.0019, +0.0189] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1994 | 0.2439 | 0.0225 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.583 | 0.2710 | 0.2615 | +0.0401 [+0.0092, +0.0724] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1531 | 0.1133 | +0.0189 [-0.0231, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.511 | 0.0895 | 0.0630 | +0.0133 [+0.0059, +0.0211] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0034, +0.1375] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0098, +0.1012] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+gate (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.407, 0.741] | 0.231 | 3.15 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.333, 0.679] | 0.231 | 3.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 117 | 0.443 | 0.530 | 0.0567 | +0.0147 [+0.0068, +0.0231] | -0.0004 [-0.0068, +0.0059] | 0.795 | 0.411 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 72 | 0.252 | 0.486 | 0.0624 | +0.0087 [+0.0021, +0.0155] | -0.0013 [-0.0065, +0.0039] | 0.751 | 0.230 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 114 | 0.341 | 0.412 | 0.0618 | +0.0089 [+0.0023, +0.0153] | +0.0026 [-0.0034, +0.0084] | 0.753 | 0.302 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 110 | 0.391 | 0.491 | 0.0600 | +0.0108 [+0.0045, +0.0170] | +0.0024 [-0.0029, +0.0076] | 0.767 | 0.359 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 152 | 0.507 | 0.461 | 0.0605 | +0.0104 [+0.0042, +0.0170] | +0.0029 [-0.0026, +0.0083] | 0.754 | 0.460 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1023 [-0.0332, +0.2353]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0906, ΔBrier vs climatology +0.0389 [+0.0218, +0.0573], realised minus predicted +0.0262 [-0.0015, +0.0547]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.600 | 0.1907 | 0.2720 | +0.0187 [-0.0118, +0.0504] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0611 | 0.0159 | +0.0093 [-0.0083, +0.0254] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0066 | 0.0000 | +0.0135 [+0.0116, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0241 | 0.0200 | -0.0015 [-0.0094, +0.0043] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.600 | 0.1034 | 0.1165 | +0.0343 [+0.0031, +0.0715] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.250 | 0.0132 | 0.0048 | +0.0074 [+0.0046, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0315 | 0.0000 | +0.0172 [+0.0085, +0.0248] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1683 | 0.2439 | 0.0203 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.588 | 0.1945 | 0.2615 | +0.0285 [+0.0001, +0.0585] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1476 | 0.1133 | +0.0195 [-0.0207, +0.0625] |
| day_type | ordinary | 1603 | 101 | 0.366 | 0.507 | 0.0453 | 0.0630 | +0.0111 [+0.0044, +0.0185] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0011, +0.1382] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0092, +0.0984] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3820 | 0.2213 |

## risk_quantile_skewt_base+every_day+persist (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.368, 0.706] | 0.231 | 2.81 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.231 | 2.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.382 (126 of 1873 days never flag) | 127 | 0.479 | 0.528 | 0.0551 | +0.0163 [+0.0089, +0.0244] | +0.0012 [-0.0049, +0.0074] | 0.865 | 0.444 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 88 | 0.302 | 0.477 | 0.0592 | +0.0119 [+0.0064, +0.0181] | +0.0019 [-0.0027, +0.0068] | 0.825 | 0.276 | no |
| 3 | 0.294 (126 of 1871 days never flag) | 126 | 0.406 | 0.444 | 0.0601 | +0.0106 [+0.0051, +0.0172] | +0.0043 [-0.0014, +0.0107] | 0.825 | 0.365 | no |
| 4 | 0.3 (126 of 1870 days never flag) | 141 | 0.493 | 0.482 | 0.0573 | +0.0135 [+0.0080, +0.0197] | +0.0050 [+0.0000, +0.0109] | 0.843 | 0.451 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 101 | 0.348 | 0.475 | 0.0578 | +0.0131 [+0.0074, +0.0190] | +0.0056 [-0.0001, +0.0113] | 0.844 | 0.317 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1286 [+0.0083, +0.2335]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0893, ΔBrier vs climatology +0.0402 [+0.0228, +0.0569], realised minus predicted -0.0103 [-0.0410, +0.0204]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.576 | 0.2415 | 0.2720 | +0.0275 [-0.0047, +0.0596] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.1471 | 0.0159 | +0.0054 [-0.0058, +0.0168] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0187 | 0.0000 | +0.0132 [+0.0115, +0.0149] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0336 | 0.0200 | +0.0007 [-0.0050, +0.0046] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1128 | 0.1165 | +0.0352 [+0.0057, +0.0727] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0223 | 0.0048 | +0.0082 [+0.0063, +0.0100] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0884 | 0.0000 | +0.0116 [+0.0025, +0.0196] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.250 | 0.1734 | 0.2439 | 0.0226 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.520 | 0.580 | 0.2508 | 0.2615 | +0.0363 [+0.0083, +0.0660] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1501 | 0.1133 | +0.0153 [-0.0248, +0.0562] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.506 | 0.0790 | 0.0630 | +0.0133 [+0.0068, +0.0204] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0019, +0.1378] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0096, +0.1022] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2483 | 0.2213 |

## risk_quantile_skewt_base+every_day+scarce (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.739] | 0.231 | 2.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.323, 0.667] | 0.231 | 2.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.49 (126 of 1873 days never flag) | 134 | 0.514 | 0.537 | 0.0540 | +0.0174 [+0.0090, +0.0264] | +0.0023 [-0.0042, +0.0089] | 0.900 | 0.479 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 70 | 0.252 | 0.500 | 0.0592 | +0.0118 [+0.0058, +0.0186] | +0.0018 [-0.0027, +0.0067] | 0.880 | 0.232 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 126 | 0.413 | 0.452 | 0.0598 | +0.0109 [+0.0049, +0.0171] | +0.0045 [-0.0009, +0.0102] | 0.875 | 0.373 | no |
| 4 | 0.407 (126 of 1870 days never flag) | 108 | 0.399 | 0.509 | 0.0577 | +0.0132 [+0.0069, +0.0197] | +0.0047 [-0.0009, +0.0101] | 0.878 | 0.368 | no |
| 5 | 0.465 (126 of 1869 days never flag) | 111 | 0.355 | 0.441 | 0.0587 | +0.0122 [+0.0063, +0.0184] | +0.0046 [-0.0007, +0.0105] | 0.874 | 0.319 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.637 (climatology 0.512, difference +0.1248 [+0.0105, +0.2321]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0868, ΔBrier vs climatology +0.0427 [+0.0244, +0.0614], realised minus predicted +0.0051 [-0.0239, +0.0351]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.569 | 0.580 | 0.2604 | 0.2720 | +0.0343 [-0.0011, +0.0666] |
| regime | 2020 | 251 | 4 | 0.250 | 0.077 | 0.1559 | 0.0159 | +0.0002 [-0.0144, +0.0143] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0070 | 0.0000 | +0.0134 [+0.0117, +0.0153] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0117 | 0.0200 | +0.0014 [-0.0049, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.414 | 0.632 | 0.1119 | 0.1165 | +0.0376 [+0.0057, +0.0784] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0055 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0936 | 0.0000 | +0.0109 [+0.0026, +0.0188] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.200 | 0.1994 | 0.2439 | 0.0225 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.560 | 0.579 | 0.2710 | 0.2615 | +0.0401 [+0.0090, +0.0728] |
| day_type | month_end | 150 | 17 | 0.647 | 0.611 | 0.1511 | 0.1133 | +0.0190 [-0.0252, +0.0599] |
| day_type | ordinary | 1603 | 101 | 0.465 | 0.516 | 0.0757 | 0.0630 | +0.0143 [+0.0069, +0.0223] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [-0.0002, +0.1350] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0102, +0.0997] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3379 | 0.2213 |

## risk_quantile_skewt_base+every_day+shrunk (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.375, 0.722] | 0.231 | 2.50 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.280, 0.636] | 0.231 | 2.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.382 (126 of 1873 days never flag) | 120 | 0.471 | 0.550 | 0.0554 | +0.0160 [+0.0095, +0.0226] | +0.0009 [-0.0056, +0.0073] | 0.879 | 0.440 | no |
| 2 | 0.409 (126 of 1872 days never flag) | 75 | 0.266 | 0.493 | 0.0604 | +0.0107 [+0.0052, +0.0161] | +0.0007 [-0.0047, +0.0057] | 0.848 | 0.244 | no |
| 3 | 0.294 (126 of 1871 days never flag) | 115 | 0.362 | 0.435 | 0.0609 | +0.0097 [+0.0044, +0.0153] | +0.0034 [-0.0023, +0.0090] | 0.833 | 0.325 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 72 | 0.246 | 0.472 | 0.0590 | +0.0118 [+0.0065, +0.0173] | +0.0034 [-0.0020, +0.0087] | 0.844 | 0.224 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 89 | 0.275 | 0.427 | 0.0593 | +0.0116 [+0.0061, +0.0172] | +0.0041 [-0.0017, +0.0098] | 0.840 | 0.246 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.631 (climatology 0.512, difference +0.1192 [+0.0054, +0.2273]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0930, ΔBrier vs climatology +0.0365 [+0.0212, +0.0518], realised minus predicted +0.0189 [-0.0120, +0.0500]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.624 | 0.1897 | 0.2720 | +0.0198 [-0.0072, +0.0437] |
| regime | 2020 | 251 | 4 | 0.250 | 0.056 | 0.1048 | 0.0159 | +0.0135 [+0.0019, +0.0245] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0121 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0267 | 0.0200 | +0.0008 [-0.0057, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.733 | 0.0903 | 0.1165 | +0.0357 [+0.0066, +0.0714] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0163 | 0.0048 | +0.0084 [+0.0064, +0.0103] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0620 | 0.0000 | +0.0157 [+0.0063, +0.0235] |
| scarcity_state | 2 | 41 | 10 | 0.100 | 0.333 | 0.1391 | 0.2439 | 0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.512 | 0.610 | 0.1958 | 0.2615 | +0.0333 [+0.0089, +0.0576] |
| day_type | month_end | 150 | 17 | 0.706 | 0.545 | 0.1484 | 0.1133 | +0.0167 [-0.0255, +0.0558] |
| day_type | ordinary | 1603 | 101 | 0.396 | 0.548 | 0.0528 | 0.0630 | +0.0129 [+0.0080, +0.0179] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.750 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1362] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.471 | 0.2112 | 0.1461 | +0.0525 [+0.0086, +0.1013] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2171 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.286, 0.667] | 0.231 | 3.08 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.613] | 0.231 | 3.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 112 | 0.407 | 0.509 | 0.0677 | +0.0037 [-0.0070, +0.0141] | -0.0114 [-0.0211, -0.0021] | 0.862 | 0.375 | no |
| 2 | 0.652 (126 of 1872 days never flag) | 68 | 0.237 | 0.485 | 0.0717 | -0.0006 [-0.0105, +0.0085] | -0.0106 [-0.0193, -0.0023] | 0.823 | 0.217 | no |
| 3 | 0.625 (126 of 1871 days never flag) | 143 | 0.457 | 0.441 | 0.0738 | -0.0031 [-0.0141, +0.0060] | -0.0094 [-0.0201, -0.0008] | 0.812 | 0.410 | no |
| 4 | 0.8 (126 of 1870 days never flag) | 111 | 0.399 | 0.495 | 0.0700 | +0.0009 [-0.0077, +0.0092] | -0.0076 [-0.0158, +0.0007] | 0.829 | 0.366 | no |
| 5 | 0.7 (126 of 1869 days never flag) | 100 | 0.355 | 0.490 | 0.0697 | +0.0012 [-0.0066, +0.0084] | -0.0063 [-0.0142, +0.0007] | 0.811 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.512, difference +0.1061 [+0.0031, +0.2035]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0155, +0.0527], realised minus predicted -0.0269 [-0.0589, +0.0055]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.516 | 0.3348 | 0.2720 | -0.0100 [-0.0551, +0.0358] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2307 | 0.0159 | -0.0271 [-0.0463, -0.0094] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0184 | 0.0000 | +0.0119 [+0.0105, +0.0133] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0160 | 0.0200 | +0.0003 [-0.0063, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0820 | 0.1165 | +0.0344 [+0.0052, +0.0718] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0118 | 0.0048 | +0.0078 [+0.0055, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1381 | 0.0000 | -0.0024 [-0.0130, +0.0074] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1557 | 0.2439 | 0.0113 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.538 | 0.3342 | 0.2615 | -0.0018 [-0.0415, +0.0393] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1545 | 0.1133 | +0.0163 [-0.0259, +0.0584] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.462 | 0.1059 | 0.0630 | -0.0015 [-0.0118, +0.0085] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3214 | 0.2903 | +0.0712 [+0.0005, +0.1352] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0098, +0.0993] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.680] | 0.192 | 2.31 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.176, 0.533] | 0.192 | 2.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 118 | 0.457 | 0.542 | 0.0644 | +0.0070 [-0.0030, +0.0175] | -0.0081 [-0.0171, +0.0005] | 0.860 | 0.426 | no |
| 2 | 0.626 (126 of 1872 days never flag) | 114 | 0.388 | 0.474 | 0.0699 | +0.0012 [-0.0088, +0.0103] | -0.0088 [-0.0183, -0.0003] | 0.830 | 0.354 | no |
| 3 | 0.625 (126 of 1871 days never flag) | 96 | 0.333 | 0.479 | 0.0732 | -0.0025 [-0.0130, +0.0071] | -0.0088 [-0.0190, +0.0002] | 0.806 | 0.304 | no |
| 4 | 0.703 (126 of 1870 days never flag) | 110 | 0.362 | 0.455 | 0.0732 | -0.0023 [-0.0113, +0.0067] | -0.0108 [-0.0194, -0.0017] | 0.821 | 0.328 | no |
| 5 | 0.63 (126 of 1869 days never flag) | 72 | 0.254 | 0.486 | 0.0743 | -0.0034 [-0.0115, +0.0047] | -0.0109 [-0.0191, -0.0028] | 0.809 | 0.232 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.616 (climatology 0.512, difference +0.1039 [+0.0245, +0.1829]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0981, ΔBrier vs climatology +0.0314 [+0.0137, +0.0504], realised minus predicted -0.0289 [-0.0613, +0.0043]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.529 | 0.540 | 0.3200 | 0.2720 | +0.0012 [-0.0435, +0.0435] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2229 | 0.0159 | -0.0200 [-0.0404, -0.0017] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0155 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0814 | 0.1165 | +0.0345 [+0.0051, +0.0705] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0117 | 0.0048 | +0.0079 [+0.0058, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1314 | 0.0000 | +0.0030 [-0.0051, +0.0107] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1475 | 0.2439 | 0.0271 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.504 | 0.558 | 0.3230 | 0.2615 | +0.0059 [-0.0336, +0.0464] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1365 | 0.1133 | +0.0304 [-0.0017, +0.0652] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.488 | 0.1035 | 0.0630 | +0.0001 [-0.0101, +0.0102] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0303, +0.1580] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0163, +0.1065] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.600] | 0.192 | 2.00 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 112 | 0.407 | 0.509 | 0.0677 | +0.0037 [-0.0072, +0.0144] | -0.0114 [-0.0210, -0.0021] | 0.862 | 0.375 | no |
| 2 | 0.729 (126 of 1872 days never flag) | 126 | 0.453 | 0.500 | 0.0659 | +0.0052 [-0.0049, +0.0150] | -0.0048 [-0.0150, +0.0047] | 0.844 | 0.417 | no |
| 3 | 0.667 (126 of 1871 days never flag) | 80 | 0.290 | 0.500 | 0.0703 | +0.0004 [-0.0105, +0.0101] | -0.0059 [-0.0171, +0.0039] | 0.820 | 0.267 | no |
| 4 | 0.701 (126 of 1870 days never flag) | 109 | 0.413 | 0.523 | 0.0653 | +0.0055 [-0.0035, +0.0146] | -0.0030 [-0.0122, +0.0059] | 0.844 | 0.383 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 72 | 0.268 | 0.514 | 0.0694 | +0.0016 [-0.0079, +0.0112] | -0.0060 [-0.0152, +0.0032] | 0.837 | 0.248 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1289 [-0.0295, +0.3063]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0943, ΔBrier vs climatology +0.0352 [+0.0134, +0.0597], realised minus predicted -0.0509 [-0.0820, -0.0191]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.471 | 0.516 | 0.3348 | 0.2720 | -0.0100 [-0.0553, +0.0370] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2307 | 0.0159 | -0.0271 [-0.0472, -0.0088] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0184 | 0.0000 | +0.0119 [+0.0104, +0.0134] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0160 | 0.0200 | +0.0003 [-0.0061, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0820 | 0.1165 | +0.0344 [+0.0052, +0.0733] |
| scarcity_state | 0 | 1041 | 5 | 0.000 | 0.000 | 0.0118 | 0.0048 | +0.0078 [+0.0057, +0.0098] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1381 | 0.0000 | -0.0024 [-0.0138, +0.0073] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1557 | 0.2439 | 0.0113 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.456 | 0.538 | 0.3342 | 0.2615 | -0.0018 [-0.0419, +0.0403] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1545 | 0.1133 | +0.0163 [-0.0234, +0.0572] |
| day_type | ordinary | 1603 | 101 | 0.356 | 0.462 | 0.1059 | 0.0630 | -0.0015 [-0.0117, +0.0086] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.3214 | 0.2903 | +0.0712 [+0.0010, +0.1361] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0103, +0.0964] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2878 | 0.2213 |

## risk_quantile_skewt_base+hurdle_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.355, 0.708] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.649] | 0.192 | 2.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 118 | 0.457 | 0.542 | 0.0644 | +0.0070 [-0.0026, +0.0165] | -0.0081 [-0.0164, -0.0000] | 0.860 | 0.426 | no |
| 2 | 0.591 (126 of 1872 days never flag) | 123 | 0.460 | 0.520 | 0.0660 | +0.0050 [-0.0049, +0.0145] | -0.0050 [-0.0143, +0.0042] | 0.842 | 0.426 | no |
| 3 | 0.604 (126 of 1871 days never flag) | 118 | 0.399 | 0.466 | 0.0693 | +0.0014 [-0.0092, +0.0115] | -0.0050 [-0.0154, +0.0052] | 0.828 | 0.362 | no |
| 4 | 0.757 (126 of 1870 days never flag) | 101 | 0.406 | 0.554 | 0.0660 | +0.0048 [-0.0042, +0.0136] | -0.0036 [-0.0123, +0.0054] | 0.845 | 0.380 | no |
| 5 | 0.663 (126 of 1869 days never flag) | 96 | 0.355 | 0.510 | 0.0686 | +0.0023 [-0.0058, +0.0105] | -0.0052 [-0.0139, +0.0030] | 0.821 | 0.328 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.682 (climatology 0.512, difference +0.1696 [+0.0447, +0.3185]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0910, ΔBrier vs climatology +0.0385 [+0.0168, +0.0610], realised minus predicted -0.0458 [-0.0762, -0.0162]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.529 | 0.540 | 0.3200 | 0.2720 | +0.0012 [-0.0405, +0.0420] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2229 | 0.0159 | -0.0200 [-0.0414, -0.0020] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0183 | 0.0000 | +0.0118 [+0.0105, +0.0134] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0155 | 0.0200 | +0.0006 [-0.0056, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0814 | 0.1165 | +0.0345 [+0.0052, +0.0721] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0117 | 0.0048 | +0.0079 [+0.0057, +0.0097] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1314 | 0.0000 | +0.0030 [-0.0055, +0.0103] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1475 | 0.2439 | 0.0271 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.504 | 0.558 | 0.3230 | 0.2615 | +0.0059 [-0.0306, +0.0429] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1365 | 0.1133 | +0.0304 [-0.0015, +0.0625] |
| day_type | ordinary | 1603 | 101 | 0.406 | 0.488 | 0.1035 | 0.0630 | +0.0001 [-0.0097, +0.0100] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0221, +0.1551] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0176, +0.1040] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2879 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.321, 0.682] | 0.231 | 3.15 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.290, 0.647] | 0.231 | 3.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 130 | 0.479 | 0.515 | 0.0631 | +0.0083 [-0.0002, +0.0176] | -0.0068 [-0.0144, +0.0005] | 0.832 | 0.442 | no |
| 2 | 0.652 (126 of 1872 days never flag) | 64 | 0.209 | 0.453 | 0.0698 | +0.0013 [-0.0057, +0.0078] | -0.0087 [-0.0150, -0.0026] | 0.780 | 0.188 | no |
| 3 | 0.567 (126 of 1871 days never flag) | 122 | 0.391 | 0.443 | 0.0711 | -0.0004 [-0.0067, +0.0060] | -0.0067 [-0.0131, +0.0001] | 0.750 | 0.352 | no |
| 4 | 0.513 (126 of 1870 days never flag) | 127 | 0.420 | 0.457 | 0.0689 | +0.0019 [-0.0045, +0.0087] | -0.0066 [-0.0129, +0.0002] | 0.775 | 0.380 | no |
| 5 | 0.498 (126 of 1869 days never flag) | 134 | 0.377 | 0.388 | 0.0697 | +0.0012 [-0.0057, +0.0079] | -0.0063 [-0.0135, +0.0008] | 0.764 | 0.329 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.618 (climatology 0.512, difference +0.1061 [+0.0022, +0.2035]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0980, ΔBrier vs climatology +0.0315 [+0.0130, +0.0495], realised minus predicted -0.0433 [-0.0765, -0.0106]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.514 | 0.3059 | 0.2720 | +0.0161 [-0.0193, +0.0531] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2388 | 0.0159 | -0.0251 [-0.0390, -0.0110] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0384 | 0.0000 | +0.0102 [+0.0086, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0205 | 0.0200 | +0.0003 [-0.0059, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0807 | 0.1165 | +0.0323 [+0.0068, +0.0663] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0252 | 0.0048 | +0.0074 [+0.0054, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1577 | 0.0000 | -0.0082 [-0.0188, +0.0012] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1329 | 0.2439 | -0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.537 | 0.3087 | 0.2615 | +0.0225 [-0.0087, +0.0583] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1552 | 0.1133 | +0.0155 [-0.0248, +0.0562] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.474 | 0.1102 | 0.0630 | +0.0039 [-0.0037, +0.0121] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0005, +0.1381] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0074, +0.0991] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.680] | 0.231 | 3.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.613] | 0.231 | 3.12 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 138 | 0.514 | 0.522 | 0.0599 | +0.0115 [+0.0032, +0.0198] | -0.0036 [-0.0101, +0.0030] | 0.829 | 0.476 | no |
| 2 | 0.551 (126 of 1872 days never flag) | 105 | 0.345 | 0.457 | 0.0680 | +0.0031 [-0.0038, +0.0098] | -0.0069 [-0.0135, +0.0003] | 0.790 | 0.312 | no |
| 3 | 0.504 (126 of 1871 days never flag) | 89 | 0.304 | 0.472 | 0.0705 | +0.0002 [-0.0070, +0.0069] | -0.0062 [-0.0136, +0.0011] | 0.743 | 0.277 | no |
| 4 | 0.513 (126 of 1870 days never flag) | 136 | 0.399 | 0.404 | 0.0721 | -0.0013 [-0.0085, +0.0052] | -0.0097 [-0.0172, -0.0027] | 0.765 | 0.352 | no |
| 5 | 0.517 (126 of 1869 days never flag) | 73 | 0.261 | 0.493 | 0.0744 | -0.0034 [-0.0110, +0.0037] | -0.0110 [-0.0188, -0.0034] | 0.760 | 0.239 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.615 (climatology 0.512, difference +0.1026 [+0.0223, +0.1873]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1007, ΔBrier vs climatology +0.0288 [+0.0111, +0.0476], realised minus predicted -0.0454 [-0.0756, -0.0110]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.517 | 0.2910 | 0.2720 | +0.0272 [-0.0050, +0.0612] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2310 | 0.0159 | -0.0180 [-0.0316, -0.0051] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0201 | 0.0200 | +0.0007 [-0.0057, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0801 | 0.1165 | +0.0324 [+0.0057, +0.0639] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0251 | 0.0048 | +0.0074 [+0.0055, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1510 | 0.0000 | -0.0028 [-0.0104, +0.0044] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1246 | 0.2439 | 0.0060 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.534 | 0.2976 | 0.2615 | +0.0302 [-0.0017, +0.0627] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1372 | 0.1133 | +0.0296 [-0.0022, +0.0624] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.1077 | 0.0630 | +0.0055 [-0.0025, +0.0131] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0261, +0.1579] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0192, +0.1066] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.759] | 0.231 | 3.31 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.303, 0.625] | 0.192 | 2.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 130 | 0.479 | 0.515 | 0.0631 | +0.0083 [-0.0001, +0.0170] | -0.0068 [-0.0144, +0.0007] | 0.832 | 0.442 | no |
| 2 | 0.543 (126 of 1872 days never flag) | 158 | 0.518 | 0.456 | 0.0632 | +0.0078 [+0.0006, +0.0160] | -0.0022 [-0.0095, +0.0061] | 0.815 | 0.468 | no |
| 3 | 0.667 (126 of 1871 days never flag) | 75 | 0.304 | 0.560 | 0.0671 | +0.0036 [-0.0044, +0.0114] | -0.0027 [-0.0113, +0.0055] | 0.768 | 0.285 | no |
| 4 | 0.497 (126 of 1870 days never flag) | 110 | 0.406 | 0.509 | 0.0639 | +0.0069 [-0.0003, +0.0144] | -0.0016 [-0.0090, +0.0063] | 0.797 | 0.375 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 99 | 0.355 | 0.495 | 0.0691 | +0.0018 [-0.0071, +0.0103] | -0.0057 [-0.0147, +0.0031] | 0.798 | 0.326 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.7 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.643 (climatology 0.512, difference +0.1308 [-0.0403, +0.3013]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0955, ΔBrier vs climatology +0.0340 [+0.0119, +0.0573], realised minus predicted -0.0686 [-0.0998, -0.0357]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.514 | 0.3059 | 0.2720 | +0.0161 [-0.0203, +0.0557] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.2388 | 0.0159 | -0.0251 [-0.0392, -0.0111] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0384 | 0.0000 | +0.0102 [+0.0087, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0205 | 0.0200 | +0.0003 [-0.0060, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0807 | 0.1165 | +0.0323 [+0.0053, +0.0657] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0252 | 0.0048 | +0.0074 [+0.0054, +0.0092] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1577 | 0.0000 | -0.0082 [-0.0189, +0.0016] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1329 | 0.2439 | -0.0098 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.528 | 0.537 | 0.3087 | 0.2615 | +0.0225 [-0.0092, +0.0577] |
| day_type | month_end | 150 | 17 | 0.588 | 0.588 | 0.1552 | 0.1133 | +0.0155 [-0.0251, +0.0532] |
| day_type | ordinary | 1603 | 101 | 0.446 | 0.474 | 0.1102 | 0.0630 | +0.0039 [-0.0036, +0.0122] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0039, +0.1379] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0111, +0.0986] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.793] | 0.231 | 2.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.389, 0.765] | 0.231 | 2.58 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 138 | 0.514 | 0.522 | 0.0599 | +0.0115 [+0.0039, +0.0198] | -0.0036 [-0.0098, +0.0029] | 0.829 | 0.476 | no |
| 2 | 0.571 (126 of 1872 days never flag) | 133 | 0.460 | 0.481 | 0.0634 | +0.0077 [+0.0003, +0.0152] | -0.0023 [-0.0095, +0.0055] | 0.813 | 0.421 | no |
| 3 | 0.604 (126 of 1871 days never flag) | 125 | 0.420 | 0.464 | 0.0661 | +0.0046 [-0.0026, +0.0119] | -0.0018 [-0.0093, +0.0063] | 0.777 | 0.382 | no |
| 4 | 0.659 (126 of 1870 days never flag) | 127 | 0.471 | 0.512 | 0.0646 | +0.0062 [-0.0014, +0.0139] | -0.0022 [-0.0102, +0.0058] | 0.797 | 0.435 | no |
| 5 | 0.527 (126 of 1869 days never flag) | 93 | 0.377 | 0.559 | 0.0683 | +0.0026 [-0.0053, +0.0109] | -0.0049 [-0.0133, +0.0038] | 0.781 | 0.353 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.684 (climatology 0.512, difference +0.1715 [+0.0411, +0.3196]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0922, ΔBrier vs climatology +0.0373 [+0.0163, +0.0596], realised minus predicted -0.0634 [-0.0956, -0.0313]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.517 | 0.2910 | 0.2720 | +0.0272 [-0.0041, +0.0590] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.2310 | 0.0159 | -0.0180 [-0.0321, -0.0043] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0383 | 0.0000 | +0.0102 [+0.0085, +0.0118] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0201 | 0.0200 | +0.0007 [-0.0054, +0.0051] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.714 | 0.0801 | 0.1165 | +0.0324 [+0.0055, +0.0642] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0251 | 0.0048 | +0.0074 [+0.0056, +0.0091] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.1510 | 0.0000 | -0.0028 [-0.0102, +0.0040] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1246 | 0.2439 | 0.0060 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.568 | 0.534 | 0.2976 | 0.2615 | +0.0302 [-0.0001, +0.0615] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1372 | 0.1133 | +0.0296 [-0.0031, +0.0637] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.1077 | 0.0630 | +0.0055 [-0.0015, +0.0138] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0252, +0.1564] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0173, +0.1059] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2836 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.276, 0.643] | 0.231 | 2.62 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.235, 0.600] | 0.231 | 2.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0633 | +0.0081 [-0.0028, +0.0182] | -0.0070 [-0.0167, +0.0018] | 0.904 | 0.399 | no |
| 2 | 0.652 (126 of 1872 days never flag) | 72 | 0.266 | 0.514 | 0.0664 | +0.0046 [-0.0049, +0.0141] | -0.0054 [-0.0140, +0.0030] | 0.881 | 0.246 | no |
| 3 | 0.659 (126 of 1871 days never flag) | 124 | 0.406 | 0.452 | 0.0673 | +0.0034 [-0.0073, +0.0130] | -0.0029 [-0.0141, +0.0062] | 0.897 | 0.367 | no |
| 4 | 0.664 (126 of 1870 days never flag) | 113 | 0.384 | 0.469 | 0.0653 | +0.0055 [-0.0032, +0.0136] | -0.0029 [-0.0117, +0.0051] | 0.860 | 0.349 | no |
| 5 | 0.7 (126 of 1869 days never flag) | 134 | 0.478 | 0.493 | 0.0697 | +0.0013 [-0.0087, +0.0100] | -0.0063 [-0.0159, +0.0022] | 0.846 | 0.439 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.632 (climatology 0.512, difference +0.1195 [+0.0148, +0.2186]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0903, ΔBrier vs climatology +0.0392 [+0.0214, +0.0585], realised minus predicted -0.0114 [-0.0430, +0.0192]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.3357 | 0.2720 | -0.0061 [-0.0513, +0.0369] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1225 | 0.0159 | -0.0057 [-0.0299, +0.0142] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0014 [-0.0045, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0910 | 0.1165 | +0.0335 [+0.0066, +0.0689] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0314 | 0.0000 | +0.0173 [+0.0083, +0.0248] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1042 | 0.2439 | 0.0021 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.472 | 0.567 | 0.3425 | 0.2615 | +0.0011 [-0.0391, +0.0416] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1509 | 0.1133 | +0.0170 [-0.0236, +0.0575] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.494 | 0.0830 | 0.0630 | +0.0036 [-0.0067, +0.0134] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1339] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0085, +0.0969] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2810 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.679] | 0.231 | 2.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.200, 0.588] | 0.231 | 2.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 119 | 0.464 | 0.546 | 0.0605 | +0.0109 [+0.0012, +0.0208] | -0.0041 [-0.0126, +0.0040] | 0.904 | 0.433 | no |
| 2 | 0.625 (126 of 1872 days never flag) | 113 | 0.403 | 0.496 | 0.0648 | +0.0063 [-0.0036, +0.0153] | -0.0037 [-0.0132, +0.0049] | 0.888 | 0.370 | no |
| 3 | 0.685 (126 of 1871 days never flag) | 98 | 0.348 | 0.490 | 0.0667 | +0.0040 [-0.0082, +0.0143] | -0.0023 [-0.0141, +0.0076] | 0.894 | 0.319 | no |
| 4 | 0.7 (126 of 1870 days never flag) | 127 | 0.413 | 0.449 | 0.0658 | +0.0050 [-0.0032, +0.0129] | -0.0034 [-0.0115, +0.0045] | 0.881 | 0.373 | no |
| 5 | 0.574 (126 of 1869 days never flag) | 84 | 0.312 | 0.512 | 0.0686 | +0.0023 [-0.0058, +0.0103] | -0.0052 [-0.0131, +0.0029] | 0.843 | 0.288 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.612 (climatology 0.512, difference +0.1001 [+0.0216, +0.1839]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0930, ΔBrier vs climatology +0.0364 [+0.0186, +0.0551], realised minus predicted -0.0134 [-0.0435, +0.0190]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.545 | 0.3215 | 0.2720 | +0.0032 [-0.0371, +0.0429] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1153 | 0.0159 | +0.0010 [-0.0252, +0.0228] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0120 | 0.0200 | +0.0018 [-0.0039, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0905 | 0.1165 | +0.0338 [+0.0072, +0.0668] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0063 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0247 | 0.0000 | +0.0226 [+0.0162, +0.0282] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0959 | 0.2439 | 0.0179 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.512 | 0.561 | 0.3322 | 0.2615 | +0.0073 [-0.0289, +0.0459] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1331 | 0.1133 | +0.0314 [+0.0002, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.494 | 0.0809 | 0.0630 | +0.0047 [-0.0051, +0.0140] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0272, +0.1583] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0190, +0.1068] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.316, 0.667] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.550] | 0.192 | 2.31 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.745 (126 of 1873 days never flag) | 111 | 0.429 | 0.541 | 0.0633 | +0.0081 [-0.0025, +0.0186] | -0.0070 [-0.0160, +0.0019] | 0.904 | 0.399 | no |
| 2 | 0.613 (126 of 1872 days never flag) | 129 | 0.475 | 0.512 | 0.0613 | +0.0098 [-0.0000, +0.0195] | -0.0002 [-0.0102, +0.0093] | 0.892 | 0.438 | no |
| 3 | 0.667 (126 of 1871 days never flag) | 87 | 0.319 | 0.506 | 0.0647 | +0.0060 [-0.0053, +0.0160] | -0.0003 [-0.0114, +0.0096] | 0.891 | 0.294 | no |
| 4 | 0.701 (126 of 1870 days never flag) | 123 | 0.457 | 0.512 | 0.0613 | +0.0095 [+0.0004, +0.0179] | +0.0011 [-0.0082, +0.0098] | 0.867 | 0.422 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 72 | 0.268 | 0.514 | 0.0699 | +0.0010 [-0.0103, +0.0114] | -0.0065 [-0.0176, +0.0034] | 0.862 | 0.248 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.512, difference +0.1289 [-0.0351, +0.3087]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0901, ΔBrier vs climatology +0.0393 [+0.0161, +0.0630], realised minus predicted -0.0354 [-0.0658, -0.0056]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.490 | 0.549 | 0.3357 | 0.2720 | -0.0061 [-0.0496, +0.0402] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1225 | 0.0159 | -0.0057 [-0.0294, +0.0155] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0014 [-0.0046, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0910 | 0.1165 | +0.0335 [+0.0058, +0.0684] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0065 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0314 | 0.0000 | +0.0173 [+0.0088, +0.0251] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1042 | 0.2439 | 0.0021 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.472 | 0.567 | 0.3425 | 0.2615 | +0.0011 [-0.0395, +0.0421] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1509 | 0.1133 | +0.0170 [-0.0234, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.376 | 0.494 | 0.0830 | 0.0630 | +0.0036 [-0.0067, +0.0135] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [+0.0003, +0.1381] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0086, +0.0978] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2810 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.192 | 2.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.391, 0.767] | 0.192 | 2.19 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 119 | 0.464 | 0.546 | 0.0605 | +0.0109 [+0.0007, +0.0206] | -0.0041 [-0.0132, +0.0037] | 0.904 | 0.433 | no |
| 2 | 0.591 (126 of 1872 days never flag) | 129 | 0.489 | 0.527 | 0.0616 | +0.0095 [-0.0004, +0.0187] | -0.0005 [-0.0099, +0.0088] | 0.891 | 0.454 | no |
| 3 | 0.747 (126 of 1871 days never flag) | 108 | 0.384 | 0.491 | 0.0638 | +0.0068 [-0.0044, +0.0176] | +0.0005 [-0.0104, +0.0109] | 0.899 | 0.352 | no |
| 4 | 0.659 (126 of 1870 days never flag) | 121 | 0.464 | 0.529 | 0.0595 | +0.0114 [+0.0032, +0.0199] | +0.0029 [-0.0055, +0.0117] | 0.891 | 0.431 | no |
| 5 | 0.579 (126 of 1869 days never flag) | 114 | 0.413 | 0.500 | 0.0634 | +0.0075 [-0.0007, +0.0156] | -0.0000 [-0.0082, +0.0084] | 0.851 | 0.380 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.682 (climatology 0.512, difference +0.1702 [+0.0476, +0.3173]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0867, ΔBrier vs climatology +0.0427 [+0.0208, +0.0658], realised minus predicted -0.0294 [-0.0598, +0.0013]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.539 | 0.545 | 0.3215 | 0.2720 | +0.0032 [-0.0382, +0.0447] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1153 | 0.0159 | +0.0010 [-0.0244, +0.0221] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0118, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0120 | 0.0200 | +0.0018 [-0.0041, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0905 | 0.1165 | +0.0338 [+0.0065, +0.0691] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0063 | 0.0048 | +0.0088 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0247 | 0.0000 | +0.0226 [+0.0164, +0.0284] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.0959 | 0.2439 | 0.0179 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.512 | 0.561 | 0.3322 | 0.2615 | +0.0073 [-0.0321, +0.0462] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1331 | 0.1133 | +0.0314 [-0.0009, +0.0656] |
| day_type | ordinary | 1603 | 101 | 0.416 | 0.494 | 0.0809 | 0.0630 | +0.0047 [-0.0056, +0.0141] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0249, +0.1560] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2028 | 0.1461 | +0.0603 [+0.0188, +0.1050] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2813 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.688] | 0.231 | 3.69 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.285, 0.650] | 0.231 | 3.69 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 107 | 0.436 | 0.570 | 0.0569 | +0.0145 [+0.0061, +0.0235] | -0.0006 [-0.0078, +0.0066] | 0.880 | 0.409 | no |
| 2 | 0.652 (126 of 1872 days never flag) | 75 | 0.230 | 0.427 | 0.0614 | +0.0096 [+0.0025, +0.0171] | -0.0004 [-0.0066, +0.0058] | 0.861 | 0.205 | no |
| 3 | 0.47 (126 of 1871 days never flag) | 153 | 0.442 | 0.399 | 0.0613 | +0.0094 [+0.0031, +0.0157] | +0.0031 [-0.0032, +0.0094] | 0.872 | 0.389 | no |
| 4 | 0.47 (126 of 1870 days never flag) | 134 | 0.399 | 0.410 | 0.0615 | +0.0094 [+0.0027, +0.0163] | +0.0009 [-0.0057, +0.0076] | 0.844 | 0.353 | no |
| 5 | 0.597 (126 of 1869 days never flag) | 167 | 0.514 | 0.425 | 0.0661 | +0.0048 [-0.0020, +0.0115] | -0.0027 [-0.0095, +0.0043] | 0.818 | 0.459 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.626 (climatology 0.512, difference +0.1136 [+0.0104, +0.2100]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0919, ΔBrier vs climatology +0.0375 [+0.0206, +0.0557], realised minus predicted -0.0125 [-0.0435, +0.0201]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.500 | 0.586 | 0.2966 | 0.2720 | +0.0226 [-0.0131, +0.0612] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1611 | 0.0159 | -0.0022 [-0.0195, +0.0139] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0115, +0.0151] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0014 [-0.0047, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0886 | 0.1165 | +0.0358 [+0.0065, +0.0715] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0085 | 0.0048 | +0.0087 [+0.0068, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0786 | 0.0000 | +0.0139 [+0.0054, +0.0215] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1326 | 0.2439 | 0.0007 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.600 | 0.3045 | 0.2615 | +0.0287 [-0.0039, +0.0622] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1523 | 0.1133 | +0.0176 [-0.0254, +0.0569] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.534 | 0.0829 | 0.0630 | +0.0110 [+0.0038, +0.0191] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [-0.0026, +0.1398] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0087, +0.0981] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2719 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.714] | 0.231 | 3.08 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.286, 0.647] | 0.231 | 3.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 141 | 0.521 | 0.518 | 0.0539 | +0.0175 [+0.0093, +0.0261] | +0.0024 [-0.0035, +0.0085] | 0.875 | 0.482 | no |
| 2 | 0.551 (126 of 1872 days never flag) | 98 | 0.309 | 0.439 | 0.0598 | +0.0113 [+0.0041, +0.0179] | +0.0013 [-0.0054, +0.0078] | 0.866 | 0.278 | no |
| 3 | 0.504 (126 of 1871 days never flag) | 113 | 0.348 | 0.425 | 0.0609 | +0.0098 [+0.0032, +0.0169] | +0.0035 [-0.0032, +0.0104] | 0.864 | 0.310 | no |
| 4 | 0.471 (126 of 1870 days never flag) | 139 | 0.428 | 0.424 | 0.0631 | +0.0077 [+0.0011, +0.0144] | -0.0007 [-0.0077, +0.0062] | 0.846 | 0.381 | no |
| 5 | 0.517 (126 of 1869 days never flag) | 73 | 0.254 | 0.479 | 0.0686 | +0.0023 [-0.0057, +0.0099] | -0.0053 [-0.0134, +0.0024] | 0.823 | 0.232 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.610 (climatology 0.512, difference +0.0976 [+0.0183, +0.1842]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0939, ΔBrier vs climatology +0.0356 [+0.0183, +0.0550], realised minus predicted -0.0117 [-0.0425, +0.0217]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.512 | 0.2836 | 0.2720 | +0.0326 [+0.0009, +0.0651] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1543 | 0.0159 | +0.0047 [-0.0129, +0.0210] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0102 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0875 | 0.1165 | +0.0360 [+0.0065, +0.0723] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0084 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0736 | 0.0000 | +0.0190 [+0.0122, +0.0247] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1203 | 0.2439 | 0.0170 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.529 | 0.2945 | 0.2615 | +0.0355 [+0.0053, +0.0687] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1343 | 0.1133 | +0.0317 [-0.0013, +0.0663] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.0811 | 0.0630 | +0.0123 [+0.0050, +0.0202] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0243, +0.1554] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2028 | 0.1461 | +0.0603 [+0.0193, +0.1048] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2717 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.231 | 3.12 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.294, 0.632] | 0.192 | 2.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.682 (126 of 1873 days never flag) | 107 | 0.436 | 0.570 | 0.0569 | +0.0145 [+0.0061, +0.0237] | -0.0006 [-0.0071, +0.0064] | 0.880 | 0.409 | no |
| 2 | 0.477 (126 of 1872 days never flag) | 149 | 0.489 | 0.456 | 0.0555 | +0.0155 [+0.0074, +0.0233] | +0.0055 [-0.0024, +0.0132] | 0.871 | 0.442 | no |
| 3 | 0.667 (126 of 1871 days never flag) | 111 | 0.370 | 0.459 | 0.0582 | +0.0125 [+0.0046, +0.0201] | +0.0062 [-0.0020, +0.0142] | 0.859 | 0.335 | no |
| 4 | 0.497 (126 of 1870 days never flag) | 124 | 0.435 | 0.484 | 0.0571 | +0.0137 [+0.0067, +0.0212] | +0.0053 [-0.0020, +0.0129] | 0.848 | 0.398 | no |
| 5 | 0.743 (126 of 1869 days never flag) | 95 | 0.333 | 0.484 | 0.0659 | +0.0050 [-0.0037, +0.0140] | -0.0026 [-0.0121, +0.0065] | 0.837 | 0.305 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.643 (climatology 0.512, difference +0.1308 [-0.0350, +0.3052]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0900, ΔBrier vs climatology +0.0395 [+0.0174, +0.0626], realised minus predicted -0.0379 [-0.0693, -0.0071]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.500 | 0.586 | 0.2966 | 0.2720 | +0.0226 [-0.0129, +0.0600] |
| regime | 2020 | 251 | 4 | 0.250 | 0.125 | 0.1611 | 0.0159 | -0.0022 [-0.0189, +0.0130] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0101 | 0.0000 | +0.0133 [+0.0116, +0.0152] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0128 | 0.0200 | +0.0014 [-0.0044, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0886 | 0.1165 | +0.0358 [+0.0072, +0.0730] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0085 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0786 | 0.0000 | +0.0139 [+0.0052, +0.0216] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1326 | 0.2439 | 0.0007 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.480 | 0.600 | 0.3045 | 0.2615 | +0.0287 [-0.0026, +0.0631] |
| day_type | month_end | 150 | 17 | 0.588 | 0.625 | 0.1523 | 0.1133 | +0.0176 [-0.0239, +0.0571] |
| day_type | ordinary | 1603 | 101 | 0.386 | 0.534 | 0.0829 | 0.0630 | +0.0110 [+0.0036, +0.0193] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.3214 | 0.2903 | +0.0712 [-0.0006, +0.1383] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.636 | 0.2112 | 0.1461 | +0.0525 [+0.0119, +0.1001] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0057 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2719 | 0.2213 |

## risk_quantile_skewt_base+hurdle_state_platt+settle+h41 (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 yes; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.429, 0.792] | 0.231 | 2.62 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.400, 0.759] | 0.192 | 2.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.672 (126 of 1873 days never flag) | 141 | 0.521 | 0.518 | 0.0539 | +0.0175 [+0.0101, +0.0263] | +0.0024 [-0.0035, +0.0087] | 0.875 | 0.482 | no |
| 2 | 0.49 (126 of 1872 days never flag) | 127 | 0.468 | 0.512 | 0.0558 | +0.0152 [+0.0075, +0.0229] | +0.0052 [-0.0022, +0.0124] | 0.868 | 0.432 | no |
| 3 | 0.604 (126 of 1871 days never flag) | 115 | 0.391 | 0.470 | 0.0574 | +0.0133 [+0.0057, +0.0208] | +0.0070 [-0.0008, +0.0146] | 0.870 | 0.356 | no |
| 4 | 0.659 (126 of 1870 days never flag) | 123 | 0.457 | 0.512 | 0.0563 | +0.0145 [+0.0076, +0.0221] | +0.0061 [-0.0016, +0.0139] | 0.859 | 0.422 | no |
| 5 | 0.527 (126 of 1869 days never flag) | 99 | 0.377 | 0.525 | 0.0632 | +0.0077 [-0.0003, +0.0152] | +0.0002 [-0.0081, +0.0079] | 0.826 | 0.350 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1041 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.684 (climatology 0.512, difference +0.1715 [+0.0430, +0.3172]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0858, ΔBrier vs climatology +0.0437 [+0.0237, +0.0650], realised minus predicted -0.0298 [-0.0582, +0.0010]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.618 | 0.512 | 0.2836 | 0.2720 | +0.0326 [+0.0023, +0.0655] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1543 | 0.0159 | +0.0047 [-0.0130, +0.0195] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0102 | 0.0000 | +0.0133 [+0.0116, +0.0150] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0124 | 0.0200 | +0.0018 [-0.0043, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.0875 | 0.1165 | +0.0360 [+0.0071, +0.0710] |
| scarcity_state | 0 | 1041 | 5 | 0.200 | 0.500 | 0.0084 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 313 | 0 | – | 0.000 | 0.0736 | 0.0000 | +0.0190 [+0.0131, +0.0246] |
| scarcity_state | 2 | 41 | 10 | 0.000 | 0.000 | 0.1203 | 0.2439 | 0.0170 (no interval) |
| scarcity_state | 3 | 478 | 125 | 0.576 | 0.529 | 0.2945 | 0.2615 | +0.0355 [+0.0071, +0.0671] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1343 | 0.1133 | +0.0317 [-0.0015, +0.0670] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.471 | 0.0811 | 0.0630 | +0.0123 [+0.0052, +0.0200] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.833 | 0.3025 | 0.2903 | +0.0954 [+0.0260, +0.1590] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.571 | 0.2028 | 0.1461 | +0.0603 [+0.0197, +0.1058] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0017 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2717 | 0.2213 |

