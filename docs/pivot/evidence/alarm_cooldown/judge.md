# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `e7f04634b557…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## hierarchical_logistic_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.192 | 1.81 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 13 | 0.500 [0.321, 0.683] | 0.192 | 1.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (147 of 1873 days never flag) | 68 | 0.214 | 0.441 | 0.0530 | +0.0184 [+0.0118, +0.0257] | +0.0034 [-0.0007, +0.0071] | 0.880 | 0.192 | no |
| 2 | 0.417 (147 of 1872 days never flag) | 42 | 0.151 | 0.500 | 0.0589 | +0.0121 [+0.0068, +0.0180] | +0.0021 [-0.0016, +0.0063] | 0.847 | 0.139 | no |
| 3 | 0.419 (147 of 1871 days never flag) | 43 | 0.159 | 0.512 | 0.0607 | +0.0100 [+0.0050, +0.0147] | +0.0037 [-0.0000, +0.0075] | 0.834 | 0.147 | no |
| 4 | 0.419 (147 of 1870 days never flag) | 56 | 0.217 | 0.536 | 0.0603 | +0.0105 [+0.0056, +0.0153] | +0.0020 [-0.0024, +0.0063] | 0.833 | 0.202 | no |
| 5 | 0.477 (126 of 1869 days never flag) | 73 | 0.188 | 0.356 | 0.0608 | +0.0101 [+0.0050, +0.0151] | +0.0026 [-0.0021, +0.0070] | 0.827 | 0.161 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.552 (climatology 0.457, difference +0.0945 [+0.0003, +0.1840]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0390 [+0.0269, +0.0525], realised minus predicted +0.0465 [+0.0130, +0.0809]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.216 | 0.400 | 0.2190 | 0.2720 | +0.0265 [+0.0034, +0.0525] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1363 | 0.0159 | +0.0181 [+0.0030, +0.0306] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0085 | 0.0000 | +0.0137 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0065 | 0.0200 | +0.0013 [-0.0038, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.727 | 0.1189 | 0.1165 | +0.0382 [+0.0081, +0.0733] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0590 | 0.0031 | +0.0263 [+0.0204, +0.0318] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2358 | 0.4146 | +0.1250 [+0.0041, +0.2202] |
| scarcity_state | 3 | 473 | 117 | 0.239 | 0.431 | 0.2484 | 0.2474 | +0.0249 [+0.0028, +0.0497] |
| day_type | month_end | 150 | 17 | 0.294 | 0.625 | 0.1016 | 0.1133 | +0.0440 [+0.0226, +0.0691] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.354 | 0.0752 | 0.0630 | +0.0128 [+0.0066, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2214 | 0.2903 | +0.0754 [+0.0165, +0.1327] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.667 | 0.1263 | 0.1461 | +0.0569 [+0.0326, +0.0844] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0273 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2425 | 0.2213 |

## hierarchical_logistic_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.290, 0.647] | 0.115 | 0.96 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.151, 0.474] | 0.115 | 0.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.448 (147 of 1873 days never flag) | 39 | 0.129 | 0.462 | 0.0530 | +0.0184 [+0.0115, +0.0263] | +0.0034 [-0.0004, +0.0072] | 0.880 | 0.116 | no |
| 2 | 0.417 (147 of 1872 days never flag) | 25 | 0.108 | 0.600 | 0.0589 | +0.0121 [+0.0064, +0.0176] | +0.0021 [-0.0018, +0.0060] | 0.847 | 0.102 | no |
| 3 | 0.419 (147 of 1871 days never flag) | 31 | 0.130 | 0.581 | 0.0607 | +0.0100 [+0.0054, +0.0146] | +0.0037 [+0.0001, +0.0077] | 0.834 | 0.123 | no |
| 4 | 0.419 (147 of 1870 days never flag) | 33 | 0.123 | 0.515 | 0.0603 | +0.0105 [+0.0059, +0.0152] | +0.0020 [-0.0021, +0.0066] | 0.833 | 0.114 | no |
| 5 | 0.477 (126 of 1869 days never flag) | 36 | 0.080 | 0.306 | 0.0608 | +0.0101 [+0.0051, +0.0154] | +0.0026 [-0.0020, +0.0073] | 0.827 | 0.065 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.552 (climatology 0.457, difference +0.0945 [-0.0038, +0.1754]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0904, ΔBrier vs climatology +0.0390 [+0.0264, +0.0540], realised minus predicted +0.0465 [+0.0139, +0.0820]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.127 | 0.448 | 0.2190 | 0.2720 | +0.0265 [+0.0035, +0.0518] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1363 | 0.0159 | +0.0181 [+0.0038, +0.0307] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0085 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0065 | 0.0200 | +0.0013 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.625 | 0.1189 | 0.1165 | +0.0382 [+0.0081, +0.0767] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0074 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0590 | 0.0031 | +0.0263 [+0.0202, +0.0321] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.667 | 0.2358 | 0.4146 | 0.1250 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.137 | 0.444 | 0.2484 | 0.2474 | +0.0249 [+0.0030, +0.0487] |
| day_type | month_end | 150 | 17 | 0.059 | 0.500 | 0.1016 | 0.1133 | +0.0440 [+0.0235, +0.0684] |
| day_type | ordinary | 1603 | 101 | 0.109 | 0.379 | 0.0752 | 0.0630 | +0.0128 [+0.0064, +0.0201] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.2214 | 0.2903 | +0.0754 [+0.0169, +0.1300] |
| day_type | tax_date | 89 | 13 | 0.231 | 1.000 | 0.1263 | 0.1461 | +0.0569 [+0.0316, +0.0859] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0273 | 0.4822 |
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

## ngboost_laplace_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.393, 0.750] | 0.115 | 1.27 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.178, 0.524] | 0.115 | 1.27 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.438 (147 of 1873 days never flag) | 38 | 0.200 | 0.737 | 0.0462 | +0.0252 [+0.0185, +0.0328] | +0.0101 [+0.0052, +0.0151] | 0.928 | 0.194 | no |
| 2 | 0.526 (168 of 1872 days never flag) | 26 | 0.065 | 0.346 | 0.0568 | +0.0143 [+0.0090, +0.0196] | +0.0043 [-0.0009, +0.0089] | 0.899 | 0.055 | no |
| 3 | 0.531 (147 of 1871 days never flag) | 23 | 0.065 | 0.391 | 0.0595 | +0.0112 [+0.0050, +0.0173] | +0.0049 [-0.0007, +0.0102] | 0.892 | 0.057 | no |
| 4 | 0.54 (147 of 1870 days never flag) | 49 | 0.116 | 0.327 | 0.0615 | +0.0093 [+0.0032, +0.0160] | +0.0008 [-0.0048, +0.0064] | 0.873 | 0.097 | no |
| 5 | 0.627 (147 of 1869 days never flag) | 23 | 0.051 | 0.304 | 0.0637 | +0.0072 [+0.0002, +0.0144] | -0.0003 [-0.0072, +0.0062] | 0.862 | 0.041 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.556 (climatology 0.457, difference +0.0986 [-0.0509, +0.1901]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0303, +0.0558], realised minus predicted +0.0654 [+0.0341, +0.0987]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.186 | 0.704 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0853] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0503 | 0.0159 | +0.0329 [+0.0231, +0.0420] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0005, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0443 | 0.1165 | +0.0287 [+0.0116, +0.0512] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0080, +0.0111] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0268 | 0.0031 | +0.0285 [+0.0230, +0.0338] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | +0.0409 [+0.0046, +0.0673] |
| scarcity_state | 3 | 473 | 117 | 0.205 | 0.706 | 0.2024 | 0.2474 | +0.0558 [+0.0323, +0.0822] |
| day_type | month_end | 150 | 17 | 0.412 | 0.778 | 0.0819 | 0.1133 | +0.0481 [+0.0294, +0.0681] |
| day_type | ordinary | 1603 | 101 | 0.139 | 0.636 | 0.0518 | 0.0630 | +0.0187 [+0.0122, +0.0259] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1699 | 0.2903 | +0.1308 [+0.0516, +0.2165] |
| day_type | tax_date | 89 | 13 | 0.308 | 1.000 | 0.0904 | 0.1461 | +0.0670 [+0.0496, +0.0853] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## ngboost_laplace_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.217, 0.565] | 0.077 | 0.58 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 2 | 0.077 [0.000, 0.167] | 0.077 | 0.58 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.438 (147 of 1873 days never flag) | 35 | 0.186 | 0.743 | 0.0462 | +0.0252 [+0.0184, +0.0329] | +0.0101 [+0.0051, +0.0151] | 0.928 | 0.181 | no |
| 2 | 0.526 (168 of 1872 days never flag) | 18 | 0.043 | 0.333 | 0.0568 | +0.0143 [+0.0089, +0.0198] | +0.0043 [-0.0010, +0.0090] | 0.899 | 0.036 | no |
| 3 | 0.531 (147 of 1871 days never flag) | 14 | 0.036 | 0.357 | 0.0595 | +0.0112 [+0.0048, +0.0174] | +0.0049 [-0.0005, +0.0103] | 0.892 | 0.031 | no |
| 4 | 0.54 (147 of 1870 days never flag) | 20 | 0.036 | 0.250 | 0.0615 | +0.0093 [+0.0030, +0.0154] | +0.0008 [-0.0050, +0.0062] | 0.873 | 0.028 | no |
| 5 | 0.627 (147 of 1869 days never flag) | 13 | 0.022 | 0.231 | 0.0637 | +0.0072 [+0.0001, +0.0138] | -0.0003 [-0.0070, +0.0058] | 0.862 | 0.016 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.556 (climatology 0.457, difference +0.0986 [-0.0574, +0.1872]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0875, ΔBrier vs climatology +0.0420 [+0.0304, +0.0550], realised minus predicted +0.0654 [+0.0339, +0.0998]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.167 | 0.708 | 0.2236 | 0.2720 | +0.0543 [+0.0260, +0.0848] |
| regime | 2020 | 251 | 4 | 0.250 | 0.333 | 0.0503 | 0.0159 | +0.0329 [+0.0236, +0.0420] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0071] |
| regime | 2025-26 | 249 | 29 | 0.241 | 1.000 | 0.0443 | 0.1165 | +0.0287 [+0.0111, +0.0525] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0080, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0268 | 0.0031 | +0.0285 [+0.0229, +0.0344] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | 0.0409 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.188 | 0.710 | 0.2024 | 0.2474 | +0.0558 [+0.0326, +0.0810] |
| day_type | month_end | 150 | 17 | 0.412 | 0.778 | 0.0819 | 0.1133 | +0.0481 [+0.0300, +0.0686] |
| day_type | ordinary | 1603 | 101 | 0.129 | 0.650 | 0.0518 | 0.0630 | +0.0187 [+0.0121, +0.0266] |
| day_type | quarter_end | 31 | 9 | 0.222 | 1.000 | 0.1699 | 0.2903 | +0.1308 [+0.0497, +0.2105] |
| day_type | tax_date | 89 | 13 | 0.308 | 1.000 | 0.0904 | 0.1461 | +0.0670 [+0.0483, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## scarcity_logistic (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.320, 0.696] | 0.231 | 3.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.238, 0.611] | 0.231 | 3.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.44 (147 of 1873 days never flag) | 152 | 0.557 | 0.513 | 0.0528 | +0.0186 [+0.0117, +0.0260] | +0.0035 [-0.0006, +0.0074] | 0.872 | 0.514 | no |
| 2 | 0.414 (147 of 1872 days never flag) | 111 | 0.424 | 0.532 | 0.0590 | +0.0121 [+0.0070, +0.0172] | +0.0020 [-0.0018, +0.0060] | 0.844 | 0.394 | no |
| 3 | 0.42 (147 of 1871 days never flag) | 150 | 0.493 | 0.453 | 0.0609 | +0.0097 [+0.0054, +0.0142] | +0.0034 [-0.0005, +0.0072] | 0.832 | 0.445 | no |
| 4 | 0.417 (147 of 1870 days never flag) | 144 | 0.478 | 0.458 | 0.0604 | +0.0105 [+0.0059, +0.0151] | +0.0020 [-0.0025, +0.0066] | 0.830 | 0.433 | no |
| 5 | 0.432 (147 of 1869 days never flag) | 145 | 0.442 | 0.421 | 0.0610 | +0.0099 [+0.0054, +0.0143] | +0.0024 [-0.0018, +0.0064] | 0.807 | 0.394 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0501, +0.1189]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0911, ΔBrier vs climatology +0.0384 [+0.0266, +0.0521], realised minus predicted +0.0452 [+0.0134, +0.0804]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.512 | 0.2174 | 0.2720 | +0.0280 [+0.0063, +0.0536] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1424 | 0.0159 | +0.0171 [+0.0033, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0091 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0068 | 0.0200 | +0.0013 [-0.0040, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.560 | 0.1177 | 0.1165 | +0.0380 [+0.0067, +0.0757] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0648 | 0.0031 | +0.0254 [+0.0194, +0.0309] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.800 | 0.2300 | 0.4146 | 0.1230 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.632 | 0.503 | 0.2468 | 0.2474 | +0.0262 [+0.0050, +0.0506] |
| day_type | month_end | 150 | 17 | 0.706 | 0.750 | 0.1027 | 0.1133 | +0.0443 [+0.0233, +0.0694] |
| day_type | ordinary | 1603 | 101 | 0.515 | 0.456 | 0.0755 | 0.0630 | +0.0126 [+0.0064, +0.0198] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.714 | 0.2460 | 0.2903 | +0.0957 [+0.0480, +0.1406] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1246 | 0.1461 | +0.0563 [+0.0325, +0.0826] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2396 | 0.2213 |

## scarcity_logistic_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.316, 0.692] | 0.154 | 1.42 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.258, 0.625] | 0.154 | 1.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.44 (147 of 1873 days never flag) | 65 | 0.207 | 0.446 | 0.0528 | +0.0186 [+0.0122, +0.0263] | +0.0035 [-0.0004, +0.0074] | 0.872 | 0.186 | no |
| 2 | 0.414 (147 of 1872 days never flag) | 45 | 0.180 | 0.556 | 0.0590 | +0.0121 [+0.0069, +0.0177] | +0.0020 [-0.0018, +0.0059] | 0.844 | 0.168 | no |
| 3 | 0.42 (147 of 1871 days never flag) | 43 | 0.159 | 0.512 | 0.0609 | +0.0097 [+0.0054, +0.0141] | +0.0034 [-0.0004, +0.0072] | 0.832 | 0.147 | no |
| 4 | 0.417 (147 of 1870 days never flag) | 56 | 0.217 | 0.536 | 0.0604 | +0.0105 [+0.0061, +0.0151] | +0.0020 [-0.0021, +0.0064] | 0.830 | 0.202 | no |
| 5 | 0.432 (147 of 1869 days never flag) | 63 | 0.188 | 0.413 | 0.0610 | +0.0099 [+0.0055, +0.0141] | +0.0024 [-0.0019, +0.0065] | 0.807 | 0.167 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0480, +0.1124]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0911, ΔBrier vs climatology +0.0384 [+0.0265, +0.0514], realised minus predicted +0.0452 [+0.0117, +0.0795]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.206 | 0.396 | 0.2174 | 0.2720 | +0.0280 [+0.0052, +0.0542] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1424 | 0.0159 | +0.0171 [+0.0036, +0.0292] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0091 | 0.0000 | +0.0137 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0068 | 0.0200 | +0.0013 [-0.0039, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.276 | 0.800 | 0.1177 | 0.1165 | +0.0380 [+0.0082, +0.0746] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0648 | 0.0031 | +0.0254 [+0.0194, +0.0306] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.2300 | 0.4146 | 0.1230 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.231 | 0.429 | 0.2468 | 0.2474 | +0.0262 [+0.0048, +0.0508] |
| day_type | month_end | 150 | 17 | 0.353 | 0.667 | 0.1027 | 0.1133 | +0.0443 [+0.0235, +0.0701] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.341 | 0.0755 | 0.0630 | +0.0126 [+0.0065, +0.0197] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.667 | 0.2460 | 0.2903 | +0.0957 [+0.0446, +0.1424] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.667 | 0.1246 | 0.1461 | +0.0563 [+0.0326, +0.0821] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2396 | 0.2213 |

## scarcity_logistic_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.281, 0.640] | 0.115 | 0.81 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.182, 0.526] | 0.115 | 0.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.44 (147 of 1873 days never flag) | 38 | 0.129 | 0.474 | 0.0528 | +0.0186 [+0.0121, +0.0260] | +0.0035 [-0.0003, +0.0077] | 0.872 | 0.117 | no |
| 2 | 0.414 (147 of 1872 days never flag) | 28 | 0.137 | 0.679 | 0.0590 | +0.0121 [+0.0065, +0.0174] | +0.0020 [-0.0019, +0.0059] | 0.844 | 0.131 | no |
| 3 | 0.42 (147 of 1871 days never flag) | 31 | 0.130 | 0.581 | 0.0609 | +0.0097 [+0.0054, +0.0140] | +0.0034 [-0.0003, +0.0070] | 0.832 | 0.123 | no |
| 4 | 0.417 (147 of 1870 days never flag) | 33 | 0.123 | 0.515 | 0.0604 | +0.0105 [+0.0059, +0.0149] | +0.0020 [-0.0021, +0.0062] | 0.830 | 0.114 | no |
| 5 | 0.432 (147 of 1869 days never flag) | 33 | 0.087 | 0.364 | 0.0610 | +0.0099 [+0.0056, +0.0143] | +0.0024 [-0.0016, +0.0063] | 0.807 | 0.075 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0518, +0.1163]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0911, ΔBrier vs climatology +0.0384 [+0.0267, +0.0520], realised minus predicted +0.0452 [+0.0113, +0.0802]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.127 | 0.448 | 0.2174 | 0.2720 | +0.0280 [+0.0058, +0.0520] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1424 | 0.0159 | +0.0171 [+0.0034, +0.0291] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0091 | 0.0000 | +0.0137 [+0.0120, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0068 | 0.0200 | +0.0013 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.714 | 0.1177 | 0.1165 | +0.0380 [+0.0077, +0.0760] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0077 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0648 | 0.0031 | +0.0254 [+0.0196, +0.0308] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.2300 | 0.4146 | +0.1230 [+0.0023, +0.2254] |
| scarcity_state | 3 | 473 | 117 | 0.137 | 0.444 | 0.2468 | 0.2474 | +0.0262 [+0.0053, +0.0493] |
| day_type | month_end | 150 | 17 | 0.118 | 0.667 | 0.1027 | 0.1133 | +0.0443 [+0.0236, +0.0703] |
| day_type | ordinary | 1603 | 101 | 0.099 | 0.370 | 0.0755 | 0.0630 | +0.0126 [+0.0067, +0.0195] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.600 | 0.2460 | 0.2903 | +0.0957 [+0.0474, +0.1400] |
| day_type | tax_date | 89 | 13 | 0.231 | 1.000 | 0.1246 | 0.1461 | +0.0563 [+0.0322, +0.0823] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0368 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2396 | 0.2213 |

## scarcity_logistic_interactions (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.346, 0.731] | 0.231 | 3.23 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.241, 0.619] | 0.231 | 3.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.407 (126 of 1873 days never flag) | 164 | 0.579 | 0.494 | 0.0540 | +0.0174 [+0.0112, +0.0246] | +0.0024 [-0.0014, +0.0060] | 0.859 | 0.531 | no |
| 2 | 0.414 (147 of 1872 days never flag) | 111 | 0.424 | 0.532 | 0.0590 | +0.0121 [+0.0069, +0.0173] | +0.0020 [-0.0019, +0.0060] | 0.844 | 0.394 | no |
| 3 | 0.42 (147 of 1871 days never flag) | 150 | 0.493 | 0.453 | 0.0609 | +0.0097 [+0.0052, +0.0142] | +0.0034 [-0.0004, +0.0073] | 0.832 | 0.445 | no |
| 4 | 0.417 (147 of 1870 days never flag) | 144 | 0.478 | 0.458 | 0.0604 | +0.0105 [+0.0059, +0.0149] | +0.0020 [-0.0022, +0.0060] | 0.830 | 0.433 | no |
| 5 | 0.432 (147 of 1869 days never flag) | 145 | 0.442 | 0.421 | 0.0610 | +0.0099 [+0.0056, +0.0144] | +0.0024 [-0.0017, +0.0064] | 0.807 | 0.394 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0460, +0.1162]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0253, +0.0491], realised minus predicted +0.0474 [+0.0144, +0.0844]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.657 | 0.489 | 0.2070 | 0.2720 | +0.0243 [+0.0022, +0.0477] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1466 | 0.0159 | +0.0179 [+0.0050, +0.0296] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0115 | 0.0000 | +0.0136 [+0.0117, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0082 | 0.0200 | +0.0013 [-0.0038, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.538 | 0.1169 | 0.1165 | +0.0346 [+0.0037, +0.0735] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0095 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0725 | 0.0031 | +0.0243 [+0.0186, +0.0296] |
| scarcity_state | 2 | 41 | 17 | 0.235 | 0.667 | 0.2169 | 0.4146 | 0.1034 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.658 | 0.487 | 0.2368 | 0.2474 | +0.0242 [+0.0039, +0.0462] |
| day_type | month_end | 150 | 17 | 0.765 | 0.765 | 0.1020 | 0.1133 | +0.0438 [+0.0240, +0.0678] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.433 | 0.0760 | 0.0630 | +0.0123 [+0.0065, +0.0189] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.1814 | 0.2903 | +0.0462 [-0.0256, +0.1140] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1291 | 0.1461 | +0.0556 [+0.0324, +0.0801] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0570 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2325 | 0.2213 |

## scarcity_logistic_interactions_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.353, 0.722] | 0.154 | 1.54 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.611] | 0.154 | 1.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.407 (126 of 1873 days never flag) | 71 | 0.221 | 0.437 | 0.0540 | +0.0174 [+0.0109, +0.0245] | +0.0024 [-0.0013, +0.0062] | 0.859 | 0.198 | no |
| 2 | 0.414 (147 of 1872 days never flag) | 45 | 0.180 | 0.556 | 0.0590 | +0.0121 [+0.0070, +0.0173] | +0.0020 [-0.0018, +0.0058] | 0.844 | 0.168 | no |
| 3 | 0.42 (147 of 1871 days never flag) | 43 | 0.159 | 0.512 | 0.0609 | +0.0097 [+0.0054, +0.0141] | +0.0034 [-0.0002, +0.0073] | 0.832 | 0.147 | no |
| 4 | 0.417 (147 of 1870 days never flag) | 56 | 0.217 | 0.536 | 0.0604 | +0.0105 [+0.0059, +0.0153] | +0.0020 [-0.0026, +0.0064] | 0.830 | 0.202 | no |
| 5 | 0.432 (147 of 1869 days never flag) | 63 | 0.188 | 0.413 | 0.0610 | +0.0099 [+0.0055, +0.0142] | +0.0024 [-0.0017, +0.0068] | 0.807 | 0.167 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0511, +0.1139]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0254, +0.0502], realised minus predicted +0.0474 [+0.0134, +0.0817]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.235 | 0.407 | 0.2070 | 0.2720 | +0.0243 [+0.0026, +0.0474] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1466 | 0.0159 | +0.0179 [+0.0051, +0.0298] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0115 | 0.0000 | +0.0136 [+0.0119, +0.0152] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0082 | 0.0200 | +0.0013 [-0.0037, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.636 | 0.1169 | 0.1165 | +0.0346 [+0.0034, +0.0723] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0095 | 0.0048 | +0.0088 [+0.0069, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0725 | 0.0031 | +0.0243 [+0.0186, +0.0297] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.333 | 0.2169 | 0.4146 | 0.1034 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.256 | 0.441 | 0.2368 | 0.2474 | +0.0242 [+0.0044, +0.0473] |
| day_type | month_end | 150 | 17 | 0.353 | 0.667 | 0.1020 | 0.1133 | +0.0438 [+0.0232, +0.0676] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.346 | 0.0760 | 0.0630 | +0.0123 [+0.0063, +0.0191] |
| day_type | quarter_end | 31 | 9 | 0.333 | 0.750 | 0.1814 | 0.2903 | +0.0462 [-0.0267, +0.1156] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.667 | 0.1291 | 0.1461 | +0.0556 [+0.0313, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0570 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2325 | 0.2213 |

## scarcity_logistic_interactions_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.280, 0.652] | 0.115 | 0.88 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.174, 0.524] | 0.115 | 0.81 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.407 (126 of 1873 days never flag) | 42 | 0.136 | 0.452 | 0.0540 | +0.0174 [+0.0114, +0.0249] | +0.0024 [-0.0012, +0.0061] | 0.859 | 0.122 | no |
| 2 | 0.414 (147 of 1872 days never flag) | 28 | 0.137 | 0.679 | 0.0590 | +0.0121 [+0.0069, +0.0176] | +0.0020 [-0.0019, +0.0060] | 0.844 | 0.131 | no |
| 3 | 0.42 (147 of 1871 days never flag) | 31 | 0.130 | 0.581 | 0.0609 | +0.0097 [+0.0052, +0.0142] | +0.0034 [-0.0003, +0.0072] | 0.832 | 0.123 | no |
| 4 | 0.417 (147 of 1870 days never flag) | 33 | 0.123 | 0.515 | 0.0604 | +0.0105 [+0.0060, +0.0147] | +0.0020 [-0.0022, +0.0060] | 0.830 | 0.114 | no |
| 5 | 0.432 (147 of 1869 days never flag) | 33 | 0.087 | 0.364 | 0.0610 | +0.0099 [+0.0057, +0.0142] | +0.0024 [-0.0016, +0.0066] | 0.807 | 0.075 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.493 (climatology 0.457, difference +0.0363 [-0.0522, +0.1165]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0926, ΔBrier vs climatology +0.0369 [+0.0251, +0.0500], realised minus predicted +0.0474 [+0.0134, +0.0833]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.147 | 0.455 | 0.2070 | 0.2720 | +0.0243 [+0.0027, +0.0472] |
| regime | 2020 | 251 | 4 | 0.000 | 0.000 | 0.1466 | 0.0159 | +0.0179 [+0.0051, +0.0293] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0115 | 0.0000 | +0.0136 [+0.0119, +0.0154] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0082 | 0.0200 | +0.0013 [-0.0040, +0.0053] |
| regime | 2025-26 | 249 | 29 | 0.138 | 0.500 | 0.1169 | 0.1165 | +0.0346 [+0.0041, +0.0739] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0095 | 0.0048 | +0.0088 [+0.0069, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0725 | 0.0031 | +0.0243 [+0.0187, +0.0298] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 0.333 | 0.2169 | 0.4146 | 0.1034 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.154 | 0.462 | 0.2368 | 0.2474 | +0.0242 [+0.0045, +0.0482] |
| day_type | month_end | 150 | 17 | 0.118 | 0.667 | 0.1020 | 0.1133 | +0.0438 [+0.0246, +0.0700] |
| day_type | ordinary | 1603 | 101 | 0.119 | 0.364 | 0.0760 | 0.0630 | +0.0123 [+0.0067, +0.0190] |
| day_type | quarter_end | 31 | 9 | 0.222 | 0.667 | 0.1814 | 0.2903 | +0.0462 [-0.0262, +0.1137] |
| day_type | tax_date | 89 | 13 | 0.231 | 1.000 | 0.1291 | 0.1461 | +0.0556 [+0.0320, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0570 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | 0.000 | 0.2325 | 0.2213 |

## settlement_quantile_timing (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.231 | 3.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.250, 0.619] | 0.231 | 3.65 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.437 (105 of 1873 days never flag) | 153 | 0.550 | 0.503 | 0.0524 | +0.0190 [+0.0117, +0.0277] | +0.0039 [-0.0008, +0.0091] | 0.914 | 0.506 | no |
| 2 | 0.35 (147 of 1872 days never flag) | 141 | 0.511 | 0.504 | 0.0583 | +0.0128 [+0.0074, +0.0188] | +0.0028 [-0.0001, +0.0063] | 0.887 | 0.470 | no |
| 3 | 0.302 (147 of 1871 days never flag) | 159 | 0.493 | 0.428 | 0.0602 | +0.0105 [+0.0059, +0.0160] | +0.0042 [+0.0009, +0.0079] | 0.874 | 0.440 | no |
| 4 | 0.319 (147 of 1870 days never flag) | 163 | 0.514 | 0.436 | 0.0619 | +0.0089 [+0.0047, +0.0137] | +0.0005 [-0.0024, +0.0033] | 0.854 | 0.461 | no |
| 5 | 0.329 (147 of 1869 days never flag) | 161 | 0.478 | 0.410 | 0.0622 | +0.0087 [+0.0043, +0.0136] | +0.0012 [-0.0017, +0.0041] | 0.840 | 0.423 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1214 [+0.0387, +0.2067]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1015, ΔBrier vs climatology +0.0280 [+0.0163, +0.0425], realised minus predicted +0.0144 [-0.0178, +0.0483]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.625 | 0.1923 | 0.2720 | +0.0522 [+0.0263, +0.0803] |
| regime | 2020 | 251 | 4 | 0.250 | 0.043 | 0.1024 | 0.0159 | +0.0049 [-0.0050, +0.0149] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0197 | 0.0000 | +0.0093 [+0.0083, +0.0105] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0289 | 0.0200 | -0.0011 [-0.0082, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.517 | 0.577 | 0.1179 | 0.1165 | +0.0320 [+0.0001, +0.0721] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.143 | 0.0209 | 0.0048 | +0.0056 [+0.0034, +0.0073] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0726 | 0.0031 | +0.0068 [+0.0010, +0.0130] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.3122 | 0.4146 | 0.1245 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.573 | 0.583 | 0.1927 | 0.2474 | +0.0475 [+0.0250, +0.0713] |
| day_type | month_end | 150 | 17 | 0.647 | 0.579 | 0.1291 | 0.1133 | +0.0337 [+0.0033, +0.0676] |
| day_type | ordinary | 1603 | 101 | 0.505 | 0.477 | 0.0600 | 0.0630 | +0.0165 [+0.0096, +0.0247] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.412 | 0.5501 | 0.2903 | -0.0228 [-0.0831, +0.0330] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.800 | 0.1846 | 0.1461 | +0.0523 [+0.0344, +0.0732] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2841 | 0.2213 |

## settlement_quantile_timing_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.750] | 0.192 | 1.73 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 11 | 0.423 [0.242, 0.609] | 0.192 | 1.73 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.437 (105 of 1873 days never flag) | 70 | 0.236 | 0.471 | 0.0524 | +0.0190 [+0.0113, +0.0273] | +0.0039 [-0.0008, +0.0088] | 0.914 | 0.214 | no |
| 2 | 0.35 (147 of 1872 days never flag) | 51 | 0.151 | 0.412 | 0.0583 | +0.0128 [+0.0075, +0.0188] | +0.0028 [-0.0004, +0.0065] | 0.887 | 0.134 | no |
| 3 | 0.302 (147 of 1871 days never flag) | 71 | 0.196 | 0.380 | 0.0602 | +0.0105 [+0.0057, +0.0159] | +0.0042 [+0.0008, +0.0079] | 0.874 | 0.170 | no |
| 4 | 0.319 (147 of 1870 days never flag) | 68 | 0.188 | 0.382 | 0.0619 | +0.0089 [+0.0046, +0.0139] | +0.0005 [-0.0023, +0.0035] | 0.854 | 0.164 | no |
| 5 | 0.329 (147 of 1869 days never flag) | 70 | 0.181 | 0.357 | 0.0622 | +0.0087 [+0.0043, +0.0136] | +0.0012 [-0.0017, +0.0040] | 0.840 | 0.155 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1214 [+0.0403, +0.2055]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1015, ΔBrier vs climatology +0.0280 [+0.0161, +0.0419], realised minus predicted +0.0144 [-0.0186, +0.0499]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.265 | 0.794 | 0.1923 | 0.2720 | +0.0522 [+0.0263, +0.0816] |
| regime | 2020 | 251 | 4 | 0.250 | 0.048 | 0.1024 | 0.0159 | +0.0049 [-0.0049, +0.0149] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0197 | 0.0000 | +0.0093 [+0.0082, +0.0105] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0289 | 0.0200 | -0.0011 [-0.0075, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.625 | 0.1179 | 0.1165 | +0.0320 [+0.0010, +0.0717] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0209 | 0.0048 | +0.0056 [+0.0036, +0.0073] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0726 | 0.0031 | +0.0068 [+0.0011, +0.0126] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.3122 | 0.4146 | 0.1245 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.256 | 0.682 | 0.1927 | 0.2474 | +0.0475 [+0.0245, +0.0733] |
| day_type | month_end | 150 | 17 | 0.471 | 0.533 | 0.1291 | 0.1133 | +0.0337 [+0.0038, +0.0676] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.472 | 0.0600 | 0.0630 | +0.0165 [+0.0094, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.286 | 0.5501 | 0.2903 | -0.0228 [-0.0776, +0.0348] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.800 | 0.1846 | 0.1461 | +0.0523 [+0.0342, +0.0708] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2841 | 0.2213 |

## settlement_quantile_timing_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.333, 0.667] | 0.154 | 1.38 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 6 | 0.231 [0.105, 0.375] | 0.115 | 1.27 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.437 (105 of 1873 days never flag) | 66 | 0.214 | 0.455 | 0.0524 | +0.0190 [+0.0112, +0.0276] | +0.0039 [-0.0006, +0.0088] | 0.914 | 0.194 | no |
| 2 | 0.35 (147 of 1872 days never flag) | 46 | 0.144 | 0.435 | 0.0583 | +0.0128 [+0.0073, +0.0187] | +0.0028 [-0.0004, +0.0062] | 0.887 | 0.129 | no |
| 3 | 0.302 (147 of 1871 days never flag) | 52 | 0.152 | 0.404 | 0.0602 | +0.0105 [+0.0057, +0.0154] | +0.0042 [+0.0009, +0.0076] | 0.874 | 0.134 | no |
| 4 | 0.319 (147 of 1870 days never flag) | 52 | 0.138 | 0.365 | 0.0619 | +0.0089 [+0.0046, +0.0135] | +0.0005 [-0.0022, +0.0032] | 0.854 | 0.119 | no |
| 5 | 0.329 (147 of 1869 days never flag) | 49 | 0.123 | 0.347 | 0.0622 | +0.0087 [+0.0043, +0.0132] | +0.0012 [-0.0018, +0.0041] | 0.840 | 0.105 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 2.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1214 [+0.0419, +0.2076]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1015, ΔBrier vs climatology +0.0280 [+0.0159, +0.0415], realised minus predicted +0.0144 [-0.0186, +0.0480]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.235 | 0.774 | 0.1923 | 0.2720 | +0.0522 [+0.0262, +0.0805] |
| regime | 2020 | 251 | 4 | 0.250 | 0.050 | 0.1024 | 0.0159 | +0.0049 [-0.0055, +0.0149] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0197 | 0.0000 | +0.0093 [+0.0082, +0.0105] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0289 | 0.0200 | -0.0011 [-0.0076, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.625 | 0.1179 | 0.1165 | +0.0320 [-0.0001, +0.0717] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0209 | 0.0048 | +0.0056 [+0.0035, +0.0073] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0726 | 0.0031 | +0.0068 [+0.0006, +0.0128] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.750 | 0.3122 | 0.4146 | 0.1245 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.231 | 0.675 | 0.1927 | 0.2474 | +0.0475 [+0.0247, +0.0724] |
| day_type | month_end | 150 | 17 | 0.471 | 0.533 | 0.1291 | 0.1133 | +0.0337 [+0.0018, +0.0669] |
| day_type | ordinary | 1603 | 101 | 0.139 | 0.438 | 0.0600 | 0.0630 | +0.0165 [+0.0092, +0.0248] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.286 | 0.5501 | 0.2903 | -0.0228 [-0.0796, +0.0327] |
| day_type | tax_date | 89 | 13 | 0.308 | 0.800 | 0.1846 | 0.1461 | +0.0523 [+0.0339, +0.0714] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2841 | 0.2213 |

## two_part_gbm (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.400, 0.762] | 0.192 | 2.46 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.178, 0.520] | 0.192 | 2.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.835 (147 of 1873 days never flag) | 39 | 0.236 | 0.846 | 0.0495 | +0.0219 [+0.0146, +0.0303] | +0.0068 [+0.0017, +0.0125] | 0.911 | 0.232 | yes |
| 2 | 0.665 (210 of 1872 days never flag) | 44 | 0.101 | 0.318 | 0.0591 | +0.0119 [+0.0044, +0.0193] | +0.0019 [-0.0049, +0.0086] | 0.881 | 0.083 | no |
| 3 | 0.729 (126 of 1871 days never flag) | 57 | 0.116 | 0.281 | 0.0602 | +0.0105 [+0.0025, +0.0178] | +0.0042 [-0.0031, +0.0109] | 0.883 | 0.092 | no |
| 4 | 0.703 (147 of 1870 days never flag) | 69 | 0.246 | 0.493 | 0.0635 | +0.0073 [-0.0004, +0.0163] | -0.0011 [-0.0085, +0.0067] | 0.874 | 0.226 | no |
| 5 | 0.767 (126 of 1869 days never flag) | 95 | 0.225 | 0.326 | 0.0685 | +0.0024 [-0.0059, +0.0108] | -0.0051 [-0.0132, +0.0029] | 0.844 | 0.188 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.540 (climatology 0.457, difference +0.0829 [-0.0632, +0.1874]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0331, +0.0638], realised minus predicted +0.0425 [+0.0124, +0.0750]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.255 | 0.929 | 0.2651 | 0.2720 | +0.0459 [+0.0147, +0.0821] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.0232 | 0.0159 | +0.0338 [+0.0187, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0016 [-0.0029, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.207 | 0.667 | 0.0659 | 0.1165 | +0.0185 [-0.0013, +0.0446] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0089 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0232, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0476 | 0.4146 | +0.0277 [-0.0127, +0.0727] |
| scarcity_state | 3 | 473 | 117 | 0.282 | 0.846 | 0.2521 | 0.2474 | +0.0441 [+0.0167, +0.0753] |
| day_type | month_end | 150 | 17 | 0.471 | 0.800 | 0.0938 | 0.1133 | +0.0499 [+0.0247, +0.0784] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.800 | 0.0587 | 0.0630 | +0.0149 [+0.0077, +0.0231] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.1546 | 0.2903 | +0.1213 [+0.0296, +0.2096] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.1012 | 0.1461 | +0.0672 [+0.0447, +0.0923] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0436 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2258 | 0.2213 |

## two_part_gbm_cooldown5 (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.387, 0.759] | 0.115 | 1.15 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 9 | 0.346 [0.179, 0.517] | 0.115 | 1.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.835 (147 of 1873 days never flag) | 27 | 0.164 | 0.852 | 0.0495 | +0.0219 [+0.0145, +0.0305] | +0.0068 [+0.0015, +0.0120] | 0.911 | 0.162 | yes |
| 2 | 0.665 (210 of 1872 days never flag) | 28 | 0.058 | 0.286 | 0.0591 | +0.0119 [+0.0041, +0.0192] | +0.0019 [-0.0048, +0.0082] | 0.881 | 0.046 | no |
| 3 | 0.729 (126 of 1871 days never flag) | 31 | 0.072 | 0.323 | 0.0602 | +0.0105 [+0.0023, +0.0183] | +0.0042 [-0.0033, +0.0112] | 0.883 | 0.060 | no |
| 4 | 0.703 (147 of 1870 days never flag) | 32 | 0.116 | 0.500 | 0.0635 | +0.0073 [-0.0012, +0.0161] | -0.0011 [-0.0087, +0.0070] | 0.874 | 0.107 | no |
| 5 | 0.767 (126 of 1869 days never flag) | 41 | 0.080 | 0.268 | 0.0685 | +0.0024 [-0.0060, +0.0104] | -0.0051 [-0.0135, +0.0027] | 0.844 | 0.062 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.540 (climatology 0.457, difference +0.0829 [-0.0657, +0.1850]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0324, +0.0635], realised minus predicted +0.0425 [+0.0131, +0.0739]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.167 | 0.895 | 0.2651 | 0.2720 | +0.0459 [+0.0138, +0.0815] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.0232 | 0.0159 | +0.0338 [+0.0192, +0.0458] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0016 [-0.0032, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.172 | 0.833 | 0.0659 | 0.1165 | +0.0185 [-0.0033, +0.0459] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0089 [+0.0072, +0.0107] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0231, +0.0370] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0476 | 0.4146 | +0.0277 [-0.0117, +0.0722] |
| scarcity_state | 3 | 473 | 117 | 0.197 | 0.852 | 0.2521 | 0.2474 | +0.0441 [+0.0170, +0.0748] |
| day_type | month_end | 150 | 17 | 0.471 | 0.800 | 0.0938 | 0.1133 | +0.0499 [+0.0244, +0.0793] |
| day_type | ordinary | 1603 | 101 | 0.069 | 0.778 | 0.0587 | 0.0630 | +0.0149 [+0.0075, +0.0234] |
| day_type | quarter_end | 31 | 9 | 0.333 | 1.000 | 0.1546 | 0.2903 | +0.1213 [+0.0289, +0.2029] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.1012 | 0.1461 | +0.0672 [+0.0441, +0.0921] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0436 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2258 | 0.2213 |

## two_part_gbm_cooldown5_strict (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.278, 0.640] | 0.077 | 0.62 | recall no, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 6 | 0.231 [0.100, 0.375] | 0.077 | 0.62 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.835 (147 of 1873 days never flag) | 24 | 0.143 | 0.833 | 0.0495 | +0.0219 [+0.0143, +0.0298] | +0.0068 [+0.0014, +0.0124] | 0.911 | 0.141 | yes |
| 2 | 0.665 (210 of 1872 days never flag) | 17 | 0.043 | 0.353 | 0.0591 | +0.0119 [+0.0042, +0.0195] | +0.0019 [-0.0051, +0.0084] | 0.881 | 0.037 | no |
| 3 | 0.729 (126 of 1871 days never flag) | 18 | 0.043 | 0.333 | 0.0602 | +0.0105 [+0.0025, +0.0183] | +0.0042 [-0.0034, +0.0113] | 0.883 | 0.037 | no |
| 4 | 0.703 (147 of 1870 days never flag) | 20 | 0.065 | 0.450 | 0.0635 | +0.0073 [-0.0012, +0.0162] | -0.0011 [-0.0090, +0.0067] | 0.874 | 0.059 | no |
| 5 | 0.767 (126 of 1869 days never flag) | 23 | 0.051 | 0.304 | 0.0685 | +0.0024 [-0.0059, +0.0109] | -0.0051 [-0.0134, +0.0030] | 0.844 | 0.041 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.540 (climatology 0.457, difference +0.0829 [-0.0641, +0.1877]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0321, +0.0645], realised minus predicted +0.0425 [+0.0134, +0.0754]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.167 | 0.895 | 0.2651 | 0.2720 | +0.0459 [+0.0125, +0.0792] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.0232 | 0.0159 | +0.0338 [+0.0187, +0.0464] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0156] |
| regime | 2024 | 250 | 5 | 0.000 | – | 0.0008 | 0.0200 | +0.0016 [-0.0030, +0.0054] |
| regime | 2025-26 | 249 | 29 | 0.069 | 0.667 | 0.0659 | 0.1165 | +0.0185 [-0.0020, +0.0447] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | – | 0.0005 | 0.0048 | +0.0089 [+0.0072, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0232, +0.0369] |
| scarcity_state | 2 | 41 | 17 | 0.000 | – | 0.0476 | 0.4146 | +0.0277 [-0.0122, +0.0760] |
| scarcity_state | 3 | 473 | 117 | 0.171 | 0.833 | 0.2521 | 0.2474 | +0.0441 [+0.0154, +0.0734] |
| day_type | month_end | 150 | 17 | 0.412 | 0.778 | 0.0938 | 0.1133 | +0.0499 [+0.0226, +0.0773] |
| day_type | ordinary | 1603 | 101 | 0.059 | 0.750 | 0.0587 | 0.0630 | +0.0149 [+0.0073, +0.0229] |
| day_type | quarter_end | 31 | 9 | 0.222 | 1.000 | 0.1546 | 0.2903 | +0.1213 [+0.0315, +0.2074] |
| day_type | tax_date | 89 | 13 | 0.385 | 1.000 | 0.1012 | 0.1461 | +0.0672 [+0.0436, +0.0920] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.200 | 1.000 | 0.0436 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2258 | 0.2213 |

