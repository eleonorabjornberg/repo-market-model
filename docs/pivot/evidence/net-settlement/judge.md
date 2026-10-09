# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `f6588fd80cd7…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## hierarchical_logistic_net (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.722] | 0.231 | 3.38 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 5 | 0.192 [0.064, 0.333] | 0.115 | 1.27 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.4 (126 of 1873 days never flag) | 174 | 0.614 | 0.494 | 0.0540 | +0.0175 [+0.0113, +0.0242] | +0.0024 [-0.0016, +0.0061] | 0.850 | 0.564 | no |
| 2 | 0.425 (147 of 1872 days never flag) | 112 | 0.367 | 0.455 | 0.0597 | +0.0114 [+0.0062, +0.0166] | +0.0014 [-0.0028, +0.0053] | 0.837 | 0.332 | no |
| 3 | 0.414 (189 of 1871 days never flag) | 57 | 0.174 | 0.421 | 0.0619 | +0.0088 [+0.0042, +0.0133] | +0.0024 [-0.0014, +0.0063] | 0.824 | 0.155 | no |
| 4 | 0.426 (189 of 1870 days never flag) | 51 | 0.174 | 0.471 | 0.0619 | +0.0089 [+0.0042, +0.0135] | +0.0005 [-0.0041, +0.0048] | 0.807 | 0.158 | no |
| 5 | 0.425 (189 of 1869 days never flag) | 49 | 0.167 | 0.469 | 0.0622 | +0.0087 [+0.0037, +0.0138] | +0.0012 [-0.0036, +0.0062] | 0.794 | 0.152 | no |

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
| regime | 2018-19 | 375 | 102 | 0.696 | 0.486 | 0.2122 | 0.2720 | +0.0250 [+0.0039, +0.0472] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1535 | 0.0159 | +0.0150 [+0.0019, +0.0268] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0133 | 0.0000 | +0.0135 [+0.0118, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0092 | 0.0200 | +0.0015 [-0.0029, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.600 | 0.1082 | 0.1165 | +0.0365 [+0.0080, +0.0740] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0109 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0712 | 0.0031 | +0.0239 [+0.0183, +0.0293] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.2176 | 0.4146 | 0.1085 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.692 | 0.479 | 0.2411 | 0.2474 | +0.0241 [+0.0032, +0.0459] |
| day_type | month_end | 150 | 17 | 0.765 | 0.722 | 0.1018 | 0.1133 | +0.0425 [+0.0218, +0.0667] |
| day_type | ordinary | 1603 | 101 | 0.584 | 0.440 | 0.0774 | 0.0630 | +0.0118 [+0.0059, +0.0180] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2435 | 0.2903 | +0.1078 [+0.0596, +0.1528] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1173 | 0.1461 | +0.0463 [+0.0247, +0.0688] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0681 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2254 | 0.2213 |

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

## onset_logistic_net+recalibrated (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 11 | 0.423 [0.250, 0.591] | 0.231 | 2.81 | recall no, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 8 | 0.308 [0.154, 0.483] | 0.231 | 2.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.357 (126 of 1873 days never flag) | 128 | 0.393 | 0.430 | 0.0635 | +0.0079 [+0.0045, +0.0112] | -0.0072 [-0.0134, -0.0012] | 0.679 | 0.351 | no |
| 2 | 0.359 (147 of 1872 days never flag) | 113 | 0.324 | 0.398 | 0.0649 | +0.0062 [+0.0034, +0.0089] | -0.0038 [-0.0088, +0.0008] | 0.691 | 0.285 | no |
| 3 | 0.388 (147 of 1871 days never flag) | 101 | 0.239 | 0.327 | 0.0654 | +0.0053 [+0.0011, +0.0091] | -0.0010 [-0.0070, +0.0043] | 0.737 | 0.200 | no |
| 4 | 0.37 (147 of 1870 days never flag) | 64 | 0.159 | 0.344 | 0.0682 | +0.0026 [-0.0019, +0.0066] | -0.0058 [-0.0114, -0.0008] | 0.637 | 0.135 | no |
| 5 | 0.333 (147 of 1869 days never flag) | 57 | 0.167 | 0.404 | 0.0622 | +0.0088 [+0.0051, +0.0121] | +0.0012 [-0.0039, +0.0060] | 0.792 | 0.147 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.603 (climatology 0.457, difference +0.1461 [+0.0899, +0.2311]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0220 [+0.0159, +0.0284], realised minus predicted +0.0339 [-0.0057, +0.0747]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.510 | 0.481 | 0.1417 | 0.2720 | +0.0042 [-0.0072, +0.0156] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1559 | 0.0159 | +0.0107 [-0.0056, +0.0255] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0515 | 0.0000 | +0.0100 [+0.0085, +0.0117] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0230 | 0.0200 | +0.0036 [+0.0009, +0.0057] |
| regime | 2025-26 | 249 | 29 | 0.069 | 1.000 | 0.0582 | 0.1165 | +0.0085 [+0.0024, +0.0160] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0421 | 0.0048 | +0.0069 [+0.0056, +0.0082] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0813 | 0.0031 | +0.0211 [+0.0156, +0.0270] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.500 | 0.0745 | 0.4146 | 0.0049 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.453 | 0.431 | 0.1651 | 0.2474 | +0.0013 [-0.0106, +0.0130] |
| day_type | month_end | 150 | 17 | 0.471 | 0.400 | 0.1323 | 0.1133 | +0.0245 [+0.0110, +0.0390] |
| day_type | ordinary | 1603 | 101 | 0.337 | 0.378 | 0.0698 | 0.0630 | +0.0035 [+0.0003, +0.0065] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2939 | 0.2903 | +0.0575 [+0.0055, +0.1067] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.778 | 0.1141 | 0.1461 | +0.0425 [+0.0278, +0.0578] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.5799 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.1682 | 0.2213 |

