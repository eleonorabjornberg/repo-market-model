# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `43315a29cfd7…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## risk_gbm+every_day+gate+settle+h41+iorb (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 19 | 0.731 [0.560, 0.889] | 0.231 | 3.69 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 15 | 0.577 [0.385, 0.762] | 0.231 | 3.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.107 (105 of 1873 days never flag) | 178 | 0.586 | 0.461 | 0.0497 | +0.0217 [+0.0145, +0.0298] | +0.0066 [+0.0013, +0.0125] | 0.805 | 0.530 | no |
| 2 | 0.164 (147 of 1872 days never flag) | 163 | 0.561 | 0.479 | 0.0544 | +0.0166 [+0.0116, +0.0220] | +0.0066 [+0.0018, +0.0120] | 0.800 | 0.512 | no |
| 3 | 0.263 (147 of 1871 days never flag) | 163 | 0.536 | 0.454 | 0.0570 | +0.0137 [+0.0085, +0.0190] | +0.0074 [+0.0028, +0.0122] | 0.776 | 0.485 | no |
| 4 | 0.194 (147 of 1870 days never flag) | 165 | 0.543 | 0.455 | 0.0532 | +0.0176 [+0.0122, +0.0232] | +0.0092 [+0.0049, +0.0139] | 0.807 | 0.492 | no |
| 5 | 0.218 (147 of 1869 days never flag) | 165 | 0.536 | 0.448 | 0.0539 | +0.0170 [+0.0117, +0.0225] | +0.0095 [+0.0050, +0.0139] | 0.804 | 0.484 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.715 (climatology 0.457, difference +0.2581 [+0.0630, +0.4287]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0718, ΔBrier vs climatology +0.0577 [+0.0397, +0.0765], realised minus predicted +0.0295 [+0.0055, +0.0555]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.588 | 0.531 | 0.1724 | 0.2720 | +0.0442 [+0.0158, +0.0733] |
| regime | 2020 | 251 | 4 | 0.500 | 0.182 | 0.0283 | 0.0159 | +0.0350 [+0.0212, +0.0466] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0040 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.0179 | 0.0200 | -0.0058 [-0.0174, +0.0034] |
| regime | 2025-26 | 249 | 29 | 0.690 | 0.444 | 0.0904 | 0.1165 | +0.0264 [+0.0024, +0.0563] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.0088 | 0.0048 | +0.0064 [+0.0030, +0.0093] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0095 | 0.0031 | +0.0275 [+0.0183, +0.0351] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.526 | 0.1962 | 0.4146 | 0.0665 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.615 | 0.514 | 0.1722 | 0.2474 | +0.0473 [+0.0228, +0.0731] |
| day_type | month_end | 150 | 17 | 0.824 | 0.583 | 0.1010 | 0.1133 | +0.0595 [+0.0347, +0.0862] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.420 | 0.0445 | 0.0630 | +0.0136 [+0.0073, +0.0208] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2074 | 0.2903 | +0.1247 [+0.0432, +0.2095] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.533 | 0.0989 | 0.1461 | +0.0689 [+0.0395, +0.0976] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.800 | 1.000 | 0.3022 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.3803 | 0.2213 |

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

