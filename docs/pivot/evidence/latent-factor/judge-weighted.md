# Pressure-day judge (#375)

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `4144a17e3cb2…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

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

## latent_factor (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.357, 0.727] | 0.395 | 6.96 | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.296, 0.714] | 0.318 | 6.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.416 (126 of 1873 days never flag) | 276 | 0.679 | 0.344 | 0.0840 | -0.0126 [-0.0235, -0.0009] | -0.0277 [-0.0369, -0.0184] | 0.796 | 0.574 | no |
| 2 | 0.442 (147 of 1872 days never flag) | 231 | 0.604 | 0.364 | 0.1019 | -0.0309 [-0.0414, -0.0197] | -0.0409 [-0.0509, -0.0303] | 0.686 | 0.519 | no |
| 3 | 0.454 (147 of 1871 days never flag) | 223 | 0.601 | 0.372 | 0.1091 | -0.0384 [-0.0498, -0.0269] | -0.0447 [-0.0560, -0.0338] | 0.618 | 0.521 | no |
| 4 | 0.457 (126 of 1870 days never flag) | 243 | 0.609 | 0.346 | 0.1129 | -0.0421 [-0.0526, -0.0312] | -0.0505 [-0.0609, -0.0397] | 0.571 | 0.517 | no |
| 5 | 0.457 (126 of 1869 days never flag) | 247 | 0.630 | 0.352 | 0.1145 | -0.0436 [-0.0540, -0.0330] | -0.0511 [-0.0619, -0.0401] | 0.541 | 0.538 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.467 (climatology 0.457, difference +0.0103 [-0.1235, +0.1593]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1381, ΔBrier vs climatology -0.0086 [-0.0256, +0.0104], realised minus predicted -0.1285 [-0.1701, -0.0822]; calibrated no, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.843 | 0.379 | 0.3026 | 0.2720 | +0.0242 [-0.0170, +0.0667] |
| regime | 2020 | 251 | 4 | 0.500 | 0.056 | 0.3770 | 0.0159 | -0.0906 [-0.1007, -0.0801] |
| regime | 2021-23 | 748 | 0 | – | – | 0.1683 | 0.0000 | -0.0189 [-0.0244, -0.0138] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.1199 | 0.0200 | -0.0076 [-0.0097, -0.0049] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.583 | 0.1589 | 0.1165 | +0.0245 [-0.0043, +0.0610] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.1377 | 0.0048 | -0.0109 [-0.0133, -0.0086] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.3042 | 0.0031 | -0.0694 [-0.0794, -0.0574] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.500 | 0.2983 | 0.4146 | 0.0746 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.786 | 0.343 | 0.3176 | 0.2474 | +0.0150 [-0.0199, +0.0513] |
| day_type | month_end | 150 | 17 | 0.647 | 0.478 | 0.2130 | 0.1133 | -0.0007 [-0.0221, +0.0235] |
| day_type | ordinary | 1603 | 101 | 0.713 | 0.306 | 0.2153 | 0.0630 | -0.0178 [-0.0293, -0.0057] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2196 | 0.2903 | +0.0693 [-0.0111, +0.1547] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.2215 | 0.1461 | +0.0331 [+0.0133, +0.0572] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0386 | 0.4822 |
| mar-2020 | 10 | 3 | 0.667 | 0.286 | 0.2749 | 0.2213 |

## latent_factor_logit (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 12 | 0.462 [0.267, 0.654] | 0.404 | 6.85 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.276, 0.667] | 0.404 | 6.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.171 (126 of 1873 days never flag) | 227 | 0.693 | 0.427 | 0.0529 | +0.0185 [+0.0111, +0.0275] | +0.0034 [+0.0003, +0.0072] | 0.916 | 0.618 | no |
| 2 | 0.188 (147 of 1872 days never flag) | 248 | 0.719 | 0.403 | 0.0590 | +0.0120 [+0.0066, +0.0173] | +0.0020 [+0.0005, +0.0037] | 0.855 | 0.634 | no |
| 3 | 0.198 (147 of 1871 days never flag) | 263 | 0.681 | 0.357 | 0.0617 | +0.0089 [+0.0046, +0.0134] | +0.0026 [+0.0011, +0.0041] | 0.820 | 0.584 | no |
| 4 | 0.238 (147 of 1870 days never flag) | 226 | 0.623 | 0.381 | 0.0647 | +0.0062 [+0.0023, +0.0097] | -0.0023 [-0.0045, -0.0004] | 0.767 | 0.542 | no |
| 5 | 0.211 (147 of 1869 days never flag) | 272 | 0.681 | 0.346 | 0.0626 | +0.0083 [+0.0046, +0.0120] | +0.0008 [-0.0004, +0.0020] | 0.786 | 0.578 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.529 (climatology 0.457, difference +0.0723 [-0.0363, +0.1945]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1011, ΔBrier vs climatology +0.0284 [+0.0162, +0.0412], realised minus predicted +0.0324 [-0.0021, +0.0670]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.745 | 0.432 | 0.2177 | 0.2720 | +0.0275 [-0.0032, +0.0629] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0903 | 0.0159 | +0.0292 [+0.0141, +0.0413] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0089 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0186 | 0.0200 | +0.0017 [-0.0029, +0.0052] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.487 | 0.1014 | 0.1165 | +0.0258 [-0.0030, +0.0636] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0105 | 0.0048 | +0.0089 [+0.0071, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0554 | 0.0031 | +0.0247 [+0.0164, +0.0325] |
| scarcity_state | 2 | 41 | 17 | 0.647 | 0.550 | 0.2834 | 0.4146 | 0.0761 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.726 | 0.423 | 0.2121 | 0.2474 | +0.0304 [+0.0051, +0.0589] |
| day_type | month_end | 150 | 17 | 0.706 | 0.600 | 0.0762 | 0.1133 | +0.0256 [+0.0008, +0.0535] |
| day_type | ordinary | 1603 | 101 | 0.743 | 0.389 | 0.0742 | 0.0630 | +0.0153 [+0.0079, +0.0245] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.0939 | 0.2903 | +0.0903 [-0.0026, +0.1922] |
| day_type | tax_date | 89 | 13 | 0.462 | 0.600 | 0.0840 | 0.1461 | +0.0390 [+0.0073, +0.0712] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0452 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3522 | 0.2213 |

## latent_factor_resid (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.346, 0.720] | 0.388 | 6.85 | recall yes, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.308, 0.700] | 0.310 | 6.15 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.416 (126 of 1873 days never flag) | 272 | 0.671 | 0.346 | 0.0841 | -0.0126 [-0.0236, -0.0008] | -0.0277 [-0.0370, -0.0183] | 0.801 | 0.569 | no |
| 2 | 0.442 (147 of 1872 days never flag) | 231 | 0.604 | 0.364 | 0.1020 | -0.0310 [-0.0416, -0.0197] | -0.0410 [-0.0516, -0.0302] | 0.689 | 0.519 | no |
| 3 | 0.454 (147 of 1871 days never flag) | 222 | 0.601 | 0.374 | 0.1092 | -0.0385 [-0.0499, -0.0275] | -0.0448 [-0.0560, -0.0342] | 0.620 | 0.521 | no |
| 4 | 0.457 (126 of 1870 days never flag) | 227 | 0.601 | 0.366 | 0.1130 | -0.0422 [-0.0527, -0.0313] | -0.0507 [-0.0619, -0.0394] | 0.572 | 0.518 | no |
| 5 | 0.457 (126 of 1869 days never flag) | 247 | 0.630 | 0.352 | 0.1146 | -0.0437 [-0.0540, -0.0334] | -0.0512 [-0.0621, -0.0401] | 0.543 | 0.538 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.469 (climatology 0.457, difference +0.0116 [-0.1218, +0.1656]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1378, ΔBrier vs climatology -0.0083 [-0.0237, +0.0092], realised minus predicted -0.1301 [-0.1720, -0.0881]; calibrated no, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.833 | 0.381 | 0.3072 | 0.2720 | +0.0252 [-0.0160, +0.0713] |
| regime | 2020 | 251 | 4 | 0.500 | 0.056 | 0.3774 | 0.0159 | -0.0909 [-0.1007, -0.0804] |
| regime | 2021-23 | 748 | 0 | – | – | 0.1696 | 0.0000 | -0.0193 [-0.0252, -0.0143] |
| regime | 2024 | 250 | 5 | 0.000 | 0.000 | 0.1218 | 0.0200 | -0.0080 [-0.0101, -0.0052] |
| regime | 2025-26 | 249 | 29 | 0.241 | 0.583 | 0.1609 | 0.1165 | +0.0243 [-0.0054, +0.0650] |
| scarcity_state | 0 | 1035 | 5 | 0.000 | 0.000 | 0.1393 | 0.0048 | -0.0113 [-0.0138, -0.0090] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.3050 | 0.0031 | -0.0698 [-0.0796, -0.0580] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 0.500 | 0.2993 | 0.4146 | 0.0762 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.778 | 0.345 | 0.3213 | 0.2474 | +0.0157 [-0.0209, +0.0537] |
| day_type | month_end | 150 | 17 | 0.647 | 0.478 | 0.2151 | 0.1133 | -0.0003 [-0.0231, +0.0248] |
| day_type | ordinary | 1603 | 101 | 0.703 | 0.307 | 0.2172 | 0.0630 | -0.0180 [-0.0296, -0.0051] |
| day_type | quarter_end | 31 | 9 | 0.444 | 0.800 | 0.2219 | 0.2903 | +0.0712 [-0.0058, +0.1510] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.615 | 0.2236 | 0.1461 | +0.0335 [+0.0112, +0.0590] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0398 | 0.4822 |
| mar-2020 | 10 | 3 | 0.667 | 0.286 | 0.2748 | 0.2213 |

## ngboost_laplace (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.467, 0.826] | 0.231 | 4.08 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 12 | 0.462 [0.273, 0.650] | 0.231 | 4.08 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.334 (126 of 1873 days never flag) | 161 | 0.536 | 0.466 | 0.0462 | +0.0252 [+0.0186, +0.0323] | +0.0101 [+0.0050, +0.0152] | 0.928 | 0.486 | no |
| 2 | 0.297 (147 of 1872 days never flag) | 150 | 0.432 | 0.400 | 0.0568 | +0.0143 [+0.0086, +0.0201] | +0.0043 [-0.0009, +0.0092] | 0.899 | 0.380 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 144 | 0.428 | 0.410 | 0.0595 | +0.0112 [+0.0046, +0.0169] | +0.0049 [-0.0008, +0.0100] | 0.892 | 0.378 | no |
| 4 | 0.302 (126 of 1870 days never flag) | 133 | 0.290 | 0.301 | 0.0615 | +0.0093 [+0.0028, +0.0154] | +0.0008 [-0.0050, +0.0062] | 0.873 | 0.236 | no |
| 5 | 0.32 (126 of 1869 days never flag) | 163 | 0.413 | 0.350 | 0.0637 | +0.0072 [-0.0004, +0.0140] | -0.0003 [-0.0076, +0.0060] | 0.862 | 0.352 | no |

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
| regime | 2018-19 | 375 | 102 | 0.608 | 0.437 | 0.2236 | 0.2720 | +0.0543 [+0.0271, +0.0844] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.0503 | 0.0159 | +0.0329 [+0.0235, +0.0419] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0037 | 0.0200 | +0.0041 [+0.0006, +0.0072] |
| regime | 2025-26 | 249 | 29 | 0.379 | 0.917 | 0.0443 | 0.1165 | +0.0287 [+0.0113, +0.0503] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0014 | 0.0048 | +0.0095 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.333 | 0.0268 | 0.0031 | +0.0285 [+0.0229, +0.0343] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0687 | 0.4146 | 0.0409 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.598 | 0.455 | 0.2024 | 0.2474 | +0.0558 [+0.0323, +0.0805] |
| day_type | month_end | 150 | 17 | 0.706 | 0.632 | 0.0819 | 0.1133 | +0.0481 [+0.0291, +0.0671] |
| day_type | ordinary | 1603 | 101 | 0.485 | 0.395 | 0.0518 | 0.0630 | +0.0187 [+0.0123, +0.0262] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.857 | 0.1699 | 0.2903 | +0.1308 [+0.0495, +0.2125] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.727 | 0.0904 | 0.1461 | +0.0670 [+0.0493, +0.0861] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1286 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2328 | 0.2213 |

## risk_gbm (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.310, 0.667] | 0.154 | 1.38 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.421] | 0.115 | 1.23 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 78 | 0.300 | 0.538 | 0.0577 | +0.0137 [+0.0082, +0.0193] | -0.0014 [-0.0097, +0.0063] | 0.642 | 0.279 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 55 | 0.180 | 0.455 | 0.0687 | +0.0024 [-0.0040, +0.0080] | -0.0076 [-0.0161, -0.0005] | 0.578 | 0.163 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 53 | 0.188 | 0.491 | 0.0667 | +0.0040 [-0.0025, +0.0098] | -0.0023 [-0.0102, +0.0044] | 0.579 | 0.173 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 49 | 0.181 | 0.510 | 0.0668 | +0.0040 [-0.0028, +0.0099] | -0.0045 [-0.0121, +0.0023] | 0.579 | 0.167 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0053, +0.0074] | -0.0062 [-0.0136, +0.0007] | 0.577 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

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
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.167 | 0.0022 | 0.0048 | +0.0087 [+0.0068, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0035 | 0.0031 | +0.0296 [+0.0218, +0.0367] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0274 | 0.4146 | -0.0074 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.574 | 0.0971 | 0.2474 | +0.0155 [-0.0047, +0.0366] |
| day_type | month_end | 150 | 17 | 0.706 | 0.522 | 0.0985 | 0.1133 | +0.0543 [+0.0303, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.149 | 0.517 | 0.0127 | 0.0630 | +0.0049 [-0.0002, +0.0099] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2204 | 0.2903 | +0.1155 [+0.0314, +0.2020] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.0958 | 0.1461 | +0.0686 [+0.0412, +0.0953] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.7080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2003 | 0.2213 |

## risk_gbm+latent_factor (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.305, 0.704] | 0.283 | 5.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.621] | 0.283 | 5.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.43 (126 of 1873 days never flag) | 157 | 0.543 | 0.484 | 0.0731 | -0.0017 [-0.0135, +0.0109] | -0.0168 [-0.0261, -0.0067] | 0.825 | 0.496 | no |
| 2 | 0.459 (147 of 1872 days never flag) | 217 | 0.612 | 0.392 | 0.0972 | -0.0261 [-0.0365, -0.0153] | -0.0361 [-0.0463, -0.0256] | 0.702 | 0.535 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 215 | 0.623 | 0.400 | 0.1010 | -0.0303 [-0.0404, -0.0196] | -0.0366 [-0.0464, -0.0262] | 0.677 | 0.549 | no |
| 4 | 0.457 (147 of 1870 days never flag) | 208 | 0.601 | 0.399 | 0.1041 | -0.0333 [-0.0431, -0.0228] | -0.0418 [-0.0516, -0.0309] | 0.642 | 0.529 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 234 | 0.580 | 0.342 | 0.1081 | -0.0372 [-0.0466, -0.0273] | -0.0447 [-0.0549, -0.0342] | 0.599 | 0.491 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.461 (climatology 0.457, difference +0.0034 [-0.0843, +0.0848]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1265, ΔBrier vs climatology +0.0029 [-0.0170, +0.0247], realised minus predicted -0.1500 [-0.1884, -0.1082]; calibrated no, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.464 | 0.3398 | 0.2720 | +0.0442 [-0.0026, +0.0927] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.3092 | 0.0159 | -0.0634 [-0.0769, -0.0495] |
| regime | 2021-23 | 748 | 0 | – | – | 0.1335 | 0.0000 | -0.0123 [-0.0172, -0.0080] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0947 | 0.0200 | -0.0057 [-0.0091, -0.0023] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.625 | 0.1584 | 0.1165 | +0.0274 [-0.0038, +0.0636] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.1100 | 0.0048 | -0.0074 [-0.0096, -0.0053] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.2378 | 0.0031 | -0.0479 [-0.0575, -0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.400 | 0.2740 | 0.4146 | 0.0505 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.490 | 0.3507 | 0.2474 | +0.0379 [-0.0034, +0.0818] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1257 | 0.1133 | +0.0573 [+0.0303, +0.0849] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.433 | 0.2082 | 0.0630 | -0.0134 [-0.0259, +0.0001] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2204 | 0.2903 | +0.1155 [+0.0352, +0.1937] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0958 | 0.1461 | +0.0686 [+0.0400, +0.0954] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2516 | 0.2213 |

## risk_gbm+latent_factor_logit (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.393, 0.762] | 0.269 | 5.04 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 12 | 0.462 [0.285, 0.640] | 0.269 | 5.04 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.638 (147 of 1873 days never flag) | 158 | 0.550 | 0.487 | 0.0465 | +0.0249 [+0.0162, +0.0342] | +0.0098 [+0.0040, +0.0161] | 0.914 | 0.503 | no |
| 2 | 0.233 (147 of 1872 days never flag) | 222 | 0.662 | 0.414 | 0.0596 | +0.0115 [+0.0061, +0.0169] | +0.0015 [-0.0020, +0.0048] | 0.854 | 0.587 | no |
| 3 | 0.241 (147 of 1871 days never flag) | 221 | 0.652 | 0.407 | 0.0593 | +0.0114 [+0.0069, +0.0158] | +0.0051 [+0.0022, +0.0082] | 0.834 | 0.577 | no |
| 4 | 0.244 (147 of 1870 days never flag) | 190 | 0.536 | 0.389 | 0.0613 | +0.0095 [+0.0058, +0.0135] | +0.0011 [-0.0019, +0.0042] | 0.802 | 0.469 | no |
| 5 | 0.229 (147 of 1869 days never flag) | 204 | 0.558 | 0.377 | 0.0623 | +0.0086 [+0.0046, +0.0126] | +0.0011 [-0.0019, +0.0041] | 0.793 | 0.485 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.464 (climatology 0.457, difference +0.0072 [-0.1005, +0.1006]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0817, ΔBrier vs climatology +0.0478 [+0.0333, +0.0644], realised minus predicted +0.0025 [-0.0283, +0.0353]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.559 | 0.533 | 0.2752 | 0.2720 | +0.0589 [+0.0223, +0.0985] |
| regime | 2020 | 251 | 4 | 0.250 | 0.071 | 0.0873 | 0.0159 | +0.0275 [+0.0122, +0.0413] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0078 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0135 | 0.0200 | +0.0034 [-0.0006, +0.0064] |
| regime | 2025-26 | 249 | 29 | 0.621 | 0.500 | 0.1065 | 0.1165 | +0.0268 [+0.0002, +0.0595] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0096 | 0.0048 | +0.0086 [+0.0067, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0454 | 0.0031 | +0.0261 [+0.0185, +0.0331] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.571 | 0.2469 | 0.4146 | 0.0415 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.581 | 0.493 | 0.2665 | 0.2474 | +0.0584 [+0.0273, +0.0920] |
| day_type | month_end | 150 | 17 | 0.647 | 0.647 | 0.1063 | 0.1133 | +0.0613 [+0.0359, +0.0893] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.451 | 0.0808 | 0.0630 | +0.0173 [+0.0089, +0.0266] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2204 | 0.2903 | +0.1155 [+0.0285, +0.1939] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.500 | 0.0958 | 0.1461 | +0.0686 [+0.0429, +0.0951] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.200 | 0.3389 | 0.2213 |

## risk_gbm+latent_factor_resid (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 no, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 13 | 0.500 [0.304, 0.704] | 0.283 | 5.92 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 11 | 0.423 [0.240, 0.609] | 0.283 | 5.92 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.43 (126 of 1873 days never flag) | 157 | 0.543 | 0.484 | 0.0733 | -0.0018 [-0.0134, +0.0105] | -0.0169 [-0.0264, -0.0071] | 0.827 | 0.496 | no |
| 2 | 0.459 (147 of 1872 days never flag) | 217 | 0.612 | 0.392 | 0.0974 | -0.0263 [-0.0369, -0.0145] | -0.0363 [-0.0466, -0.0253] | 0.704 | 0.535 | no |
| 3 | 0.458 (147 of 1871 days never flag) | 218 | 0.630 | 0.399 | 0.1012 | -0.0305 [-0.0406, -0.0197] | -0.0368 [-0.0469, -0.0268] | 0.678 | 0.555 | no |
| 4 | 0.457 (147 of 1870 days never flag) | 209 | 0.601 | 0.397 | 0.1043 | -0.0335 [-0.0434, -0.0236] | -0.0419 [-0.0525, -0.0312] | 0.643 | 0.529 | no |
| 5 | 0.457 (147 of 1869 days never flag) | 234 | 0.580 | 0.342 | 0.1083 | -0.0374 [-0.0468, -0.0276] | -0.0449 [-0.0550, -0.0346] | 0.600 | 0.491 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 yes, 2020 no, 2024 no, 2025-26 yes. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.461 (climatology 0.457, difference +0.0041 [-0.0840, +0.0964]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1265, ΔBrier vs climatology +0.0029 [-0.0169, +0.0240], realised minus predicted -0.1512 [-0.1886, -0.1103]; calibrated no, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.627 | 0.464 | 0.3433 | 0.2720 | +0.0445 [-0.0010, +0.0921] |
| regime | 2020 | 251 | 4 | 0.250 | 0.500 | 0.3095 | 0.0159 | -0.0636 [-0.0776, -0.0496] |
| regime | 2021-23 | 748 | 0 | – | – | 0.1345 | 0.0000 | -0.0126 [-0.0173, -0.0084] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0962 | 0.0200 | -0.0060 [-0.0094, -0.0024] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.625 | 0.1600 | 0.1165 | +0.0271 [-0.0057, +0.0674] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.1112 | 0.0048 | -0.0077 [-0.0100, -0.0056] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.2384 | 0.0031 | -0.0482 [-0.0583, -0.0374] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 0.400 | 0.2746 | 0.4146 | 0.0517 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.624 | 0.490 | 0.3537 | 0.2474 | +0.0380 [-0.0027, +0.0791] |
| day_type | month_end | 150 | 17 | 0.647 | 0.688 | 0.1260 | 0.1133 | +0.0572 [+0.0297, +0.0859] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.433 | 0.2100 | 0.0630 | -0.0136 [-0.0253, -0.0010] |
| day_type | quarter_end | 31 | 9 | 0.556 | 0.625 | 0.2204 | 0.2903 | +0.1155 [+0.0353, +0.1963] |
| day_type | tax_date | 89 | 13 | 0.385 | 0.833 | 0.0958 | 0.1461 | +0.0686 [+0.0405, +0.0934] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.3080 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2515 | 0.2213 |

## risk_gbm_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 7 | 0.269 [0.125, 0.419] | 0.154 | 1.38 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0833 (105 of 1873 days never flag) | 82 | 0.307 | 0.524 | 0.0592 | +0.0122 [+0.0075, +0.0168] | -0.0029 [-0.0106, +0.0039] | 0.643 | 0.285 | no |
| 2 | 0.0833 (147 of 1872 days never flag) | 53 | 0.173 | 0.453 | 0.0691 | +0.0020 [-0.0047, +0.0081] | -0.0080 [-0.0168, -0.0003] | 0.578 | 0.156 | no |
| 3 | 0.087 (147 of 1871 days never flag) | 61 | 0.181 | 0.410 | 0.0677 | +0.0029 [-0.0038, +0.0089] | -0.0034 [-0.0115, +0.0034] | 0.579 | 0.160 | no |
| 4 | 0.0909 (147 of 1870 days never flag) | 56 | 0.196 | 0.482 | 0.0668 | +0.0040 [-0.0023, +0.0100] | -0.0044 [-0.0120, +0.0023] | 0.579 | 0.179 | no |
| 5 | 0.0909 (147 of 1869 days never flag) | 53 | 0.152 | 0.396 | 0.0696 | +0.0013 [-0.0055, +0.0072] | -0.0062 [-0.0140, +0.0005] | 0.576 | 0.134 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
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
| regime | 2025-26 | 249 | 29 | 0.345 | 0.769 | 0.0354 | 0.1165 | +0.0158 [+0.0016, +0.0330] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.500 | 0.0009 | 0.0048 | +0.0094 [+0.0079, +0.0110] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0072 | 0.0031 | +0.0290 [+0.0225, +0.0354] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0352 | 0.4146 | -0.0002 [-0.0278, +0.0371] |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.565 | 0.1006 | 0.2474 | +0.0080 [-0.0097, +0.0247] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0983 | 0.1133 | +0.0339 [+0.0115, +0.0566] |
| day_type | ordinary | 1603 | 101 | 0.158 | 0.500 | 0.0128 | 0.0630 | +0.0052 [+0.0001, +0.0097] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.600 | 0.2030 | 0.2903 | +0.1101 [+0.0294, +0.1928] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.562 | 0.1197 | 0.1461 | +0.0681 [+0.0463, +0.0927] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4699 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2084 | 0.2213 |

## risk_logistic (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.435, 0.800] | 0.192 | 2.42 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.552] | 0.192 | 2.23 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.043 (105 of 1873 days never flag) | 109 | 0.329 | 0.422 | 0.0606 | +0.0108 [+0.0056, +0.0158] | -0.0043 [-0.0128, +0.0035] | 0.642 | 0.292 | no |
| 2 | 0.0176 (147 of 1872 days never flag) | 72 | 0.201 | 0.389 | 0.0676 | +0.0035 [-0.0030, +0.0092] | -0.0065 [-0.0146, +0.0005] | 0.579 | 0.176 | no |
| 3 | 0.0841 (147 of 1871 days never flag) | 76 | 0.210 | 0.382 | 0.0689 | +0.0018 [-0.0055, +0.0085] | -0.0045 [-0.0134, +0.0031] | 0.579 | 0.183 | no |
| 4 | 0.0243 (147 of 1870 days never flag) | 89 | 0.225 | 0.348 | 0.0688 | +0.0020 [-0.0047, +0.0081] | -0.0065 [-0.0150, +0.0012] | 0.578 | 0.191 | no |
| 5 | 0.12 (147 of 1869 days never flag) | 86 | 0.217 | 0.349 | 0.0690 | +0.0019 [-0.0052, +0.0083] | -0.0056 [-0.0140, +0.0017] | 0.577 | 0.185 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 3.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 2.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.9 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.573 (climatology 0.457, difference +0.1155 [-0.0282, +0.2340]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1074, ΔBrier vs climatology +0.0220 [+0.0108, +0.0330], realised minus predicted +0.0748 [+0.0408, +0.1112]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1074 | 0.2720 | -0.0026 [-0.0240, +0.0179] |
| regime | 2020 | 251 | 4 | 0.250 | 0.043 | 0.0308 | 0.0159 | +0.0252 [+0.0095, +0.0381] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0005 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 0.200 | 0.0059 | 0.0200 | +0.0050 [+0.0008, +0.0096] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.542 | 0.0332 | 0.1165 | +0.0133 [+0.0003, +0.0294] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.077 | 0.0032 | 0.0048 | +0.0091 [+0.0073, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0069 | 0.0031 | +0.0280 [+0.0221, +0.0336] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0360 | 0.4146 | 0.0046 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.513 | 0.1081 | 0.2474 | +0.0032 [-0.0160, +0.0217] |
| day_type | month_end | 150 | 17 | 0.765 | 0.394 | 0.1022 | 0.1133 | +0.0282 [+0.0011, +0.0563] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.450 | 0.0126 | 0.0630 | +0.0040 [-0.0012, +0.0088] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3561 | 0.2903 | +0.0892 [+0.0158, +0.1596] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1296 | 0.1461 | +0.0774 [+0.0463, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4000 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2020 | 0.2213 |

## risk_logistic_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.762] | 0.192 | 2.31 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 8 | 0.308 [0.167, 0.455] | 0.192 | 1.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.068 (105 of 1873 days never flag) | 106 | 0.329 | 0.434 | 0.0596 | +0.0118 [+0.0070, +0.0164] | -0.0033 [-0.0115, +0.0041] | 0.643 | 0.294 | no |
| 2 | 0.33 (147 of 1872 days never flag) | 73 | 0.209 | 0.397 | 0.0672 | +0.0039 [-0.0026, +0.0099] | -0.0061 [-0.0146, +0.0009] | 0.579 | 0.183 | no |
| 3 | 0.374 (147 of 1871 days never flag) | 68 | 0.196 | 0.397 | 0.0689 | +0.0018 [-0.0060, +0.0080] | -0.0045 [-0.0131, +0.0025] | 0.579 | 0.172 | no |
| 4 | 0.361 (147 of 1870 days never flag) | 64 | 0.196 | 0.422 | 0.0689 | +0.0019 [-0.0048, +0.0080] | -0.0065 [-0.0146, +0.0010] | 0.578 | 0.174 | no |
| 5 | 0.433 (147 of 1869 days never flag) | 80 | 0.210 | 0.362 | 0.0687 | +0.0023 [-0.0045, +0.0084] | -0.0053 [-0.0131, +0.0019] | 0.577 | 0.181 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.583 (climatology 0.457, difference +0.1255 [-0.0214, +0.2463]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1055, ΔBrier vs climatology +0.0239 [+0.0136, +0.0345], realised minus predicted +0.0775 [+0.0426, +0.1148]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.554 | 0.1080 | 0.2720 | -0.0024 [-0.0224, +0.0166] |
| regime | 2020 | 251 | 4 | 0.250 | 0.032 | 0.0294 | 0.0159 | +0.0298 [+0.0202, +0.0383] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0003 | 0.0000 | +0.0138 [+0.0120, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0040 [+0.0003, +0.0070] |
| regime | 2025-26 | 249 | 29 | 0.448 | 0.722 | 0.0311 | 0.1165 | +0.0168 [+0.0040, +0.0338] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0014 | 0.0048 | +0.0094 [+0.0078, +0.0109] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0092 | 0.0031 | +0.0279 [+0.0218, +0.0337] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 1.000 | 0.0421 | 0.4146 | 0.0149 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.519 | 0.1063 | 0.2474 | +0.0057 [-0.0113, +0.0230] |
| day_type | month_end | 150 | 17 | 0.765 | 0.433 | 0.0996 | 0.1133 | +0.0352 [+0.0096, +0.0600] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.439 | 0.0123 | 0.0630 | +0.0047 [-0.0004, +0.0092] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.462 | 0.3198 | 0.2903 | +0.0954 [+0.0396, +0.1520] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.409 | 0.1332 | 0.1461 | +0.0711 [+0.0381, +0.1107] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2040 | 0.2213 |

## risk_quantile_skewt (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 14 | 0.538 [0.360, 0.719] | 0.231 | 3.42 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 9 | 0.346 [0.192, 0.500] | 0.231 | 3.42 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.148 (42 of 1873 days never flag) | 116 | 0.329 | 0.397 | 0.0632 | +0.0082 [+0.0025, +0.0141] | -0.0069 [-0.0152, +0.0007] | 0.645 | 0.288 | no |
| 2 | 0.283 (126 of 1872 days never flag) | 94 | 0.216 | 0.319 | 0.0676 | +0.0034 [-0.0039, +0.0105] | -0.0066 [-0.0149, +0.0014] | 0.578 | 0.179 | no |
| 3 | 0.092 (126 of 1871 days never flag) | 90 | 0.196 | 0.300 | 0.0669 | +0.0038 [-0.0032, +0.0106] | -0.0025 [-0.0103, +0.0048] | 0.581 | 0.159 | no |
| 4 | 0.0391 (126 of 1870 days never flag) | 118 | 0.210 | 0.246 | 0.0672 | +0.0037 [-0.0026, +0.0097] | -0.0048 [-0.0124, +0.0018] | 0.580 | 0.159 | no |
| 5 | 0.0988 (126 of 1869 days never flag) | 92 | 0.196 | 0.293 | 0.0669 | +0.0040 [-0.0026, +0.0101] | -0.0035 [-0.0110, +0.0034] | 0.581 | 0.158 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 2.2 over 1035 days; regime_2021-23: 0.3 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 2.9 over 1035 days; regime_2021-23: 3.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 8.3 over 1035 days; regime_2021-23: 12.1 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 4.1 over 1035 days; regime_2021-23: 5.4 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.641 (climatology 0.457, difference +0.1837 [+0.0710, +0.2966]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1101, ΔBrier vs climatology +0.0193 [+0.0086, +0.0311], realised minus predicted +0.0574 [+0.0238, +0.0943]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.294 | 0.588 | 0.1014 | 0.2720 | -0.0090 [-0.0307, +0.0131] |
| regime | 2020 | 251 | 4 | 0.250 | 0.025 | 0.0608 | 0.0159 | +0.0085 [-0.0055, +0.0225] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0155] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0110 | 0.0200 | +0.0019 [-0.0033, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0481 | 0.1165 | +0.0239 [+0.0054, +0.0480] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.167 | 0.0056 | 0.0048 | +0.0087 [+0.0068, +0.0104] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.031 | 0.0339 | 0.0031 | +0.0134 [+0.0040, +0.0223] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.1154 | 0.4146 | 0.0760 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.333 | 0.542 | 0.1028 | 0.2474 | -0.0022 [-0.0208, +0.0174] |
| day_type | month_end | 150 | 17 | 0.765 | 0.382 | 0.1226 | 0.1133 | +0.0234 [-0.0109, +0.0571] |
| day_type | ordinary | 1603 | 101 | 0.168 | 0.425 | 0.0150 | 0.0630 | +0.0014 [-0.0042, +0.0066] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.429 | 0.3534 | 0.2903 | +0.1102 [+0.0260, +0.1974] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.357 | 0.1886 | 0.1461 | +0.0706 [+0.0331, +0.1124] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4001 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

## risk_quantile_skewt_base (candidate): FAIL at +5 bp

Tier 1 yes, tier 3 no, tier 5 no. Scarce regime alone (state >= 2, reported only): fail (tier 1 yes, tier 3 no, tier 5 no; 23 onsets).

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 15 | 0.577 [0.391, 0.750] | 0.192 | 2.31 | recall yes, recall_above_climatology yes, false_alarms yes |
| lead_at_least_3 | 26 | 10 | 0.385 [0.227, 0.542] | 0.154 | 1.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.154 (105 of 1873 days never flag) | 107 | 0.336 | 0.439 | 0.0630 | +0.0084 [+0.0021, +0.0147] | -0.0067 [-0.0153, +0.0016] | 0.635 | 0.301 | no |
| 2 | 0.11 (147 of 1872 days never flag) | 82 | 0.216 | 0.366 | 0.0687 | +0.0024 [-0.0054, +0.0093] | -0.0076 [-0.0168, -0.0001] | 0.582 | 0.186 | no |
| 3 | 0.142 (126 of 1871 days never flag) | 69 | 0.217 | 0.435 | 0.0670 | +0.0037 [-0.0037, +0.0105] | -0.0026 [-0.0108, +0.0047] | 0.585 | 0.195 | no |
| 4 | 0.261 (126 of 1870 days never flag) | 58 | 0.210 | 0.500 | 0.0669 | +0.0039 [-0.0034, +0.0110] | -0.0045 [-0.0128, +0.0033] | 0.586 | 0.193 | no |
| 5 | 0.325 (126 of 1869 days never flag) | 53 | 0.188 | 0.491 | 0.0670 | +0.0039 [-0.0030, +0.0107] | -0.0036 [-0.0120, +0.0040] | 0.585 | 0.173 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 no, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.7 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated (regimes with a pressure day): 2018-19 no, 2020 yes, 2024 yes, 2025-26 no. Reported, no pressure day: 2021-23 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.594 (climatology 0.457, difference +0.1367 [-0.0372, +0.2817]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1051, ΔBrier vs climatology +0.0244 [+0.0124, +0.0374], realised minus predicted +0.0555 [+0.0217, +0.0899]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.304 | 0.608 | 0.1199 | 0.2720 | -0.0169 [-0.0413, +0.0085] |
| regime | 2020 | 251 | 4 | 0.250 | 0.030 | 0.0469 | 0.0159 | +0.0220 [+0.0121, +0.0313] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0029 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.500 | 0.0118 | 0.0200 | +0.0015 [-0.0048, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.483 | 0.667 | 0.0509 | 0.1165 | +0.0242 [+0.0051, +0.0465] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0059 | 0.0048 | +0.0086 [+0.0067, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.036 | 0.0271 | 0.0031 | +0.0196 [+0.0120, +0.0263] |
| scarcity_state | 2 | 41 | 17 | 0.294 | 0.833 | 0.0959 | 0.4146 | 0.0536 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.342 | 0.580 | 0.1179 | 0.2474 | -0.0036 [-0.0259, +0.0196] |
| day_type | month_end | 150 | 17 | 0.765 | 0.448 | 0.1397 | 0.1133 | +0.0244 [-0.0130, +0.0627] |
| day_type | ordinary | 1603 | 101 | 0.178 | 0.462 | 0.0159 | 0.0630 | +0.0028 [-0.0028, +0.0082] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.500 | 0.3234 | 0.2903 | +0.0724 [-0.0002, +0.1368] |
| day_type | tax_date | 89 | 13 | 0.769 | 0.370 | 0.2039 | 0.1461 | +0.0602 [+0.0207, +0.1034] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4054 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 1.000 | 0.2000 | 0.2213 |

