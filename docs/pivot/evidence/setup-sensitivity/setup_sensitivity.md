
Table 1. Tier 1 at lead >= 1, +5 bp, h = 1 to 5, whole window: the declared reading, and the cut-off chosen with the period 2018-2019 down-weighted to its share of all days (0.200). Onsets flagged, worst false alarms per onset (limit 2).

| row | declared: onsets flagged | declared: worst FA per onset | down-weighted: onsets flagged | down-weighted: worst FA per onset |
|---|---|---|---|---|
| two_part_gbm | 15 of 26 | 2.46 | 15 of 26 | 2.42 |
| ngboost_laplace | 15 of 26 | 2.54 | 15 of 26 | 2.54 |
| hierarchical_logistic | 15 of 26 | 3.65 | 15 of 26 | 3.69 |
| settlement_quantile_timing | 15 of 26 | 3.65 | 15 of 26 | 3.65 |
| scarcity_logistic_interactions | 14 of 26 | 3.23 | 14 of 26 | 3.23 |
| calendar_climatology | 10 of 26 | 5.00 | 10 of 26 | 4.19 |
| persistence_logistic | 7 of 26 | 3.42 | 7 of 26 | 3.42 |

Table 2a. Tier 1 by calendar year of the flagged day, declared reading: onsets flagged of onsets (worst false alarms at one horizon). Onsets by year: 2018: 4, 2019: 13, 2020: 2, 2021: 0, 2022: 0, 2023: 0, 2024: 2, 2025: 5.

| row | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 0 of 4 (0) | 12 of 13 (60) | 1 of 2 (4) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 2 of 5 (3) |
| ngboost_laplace | 0 of 4 (0) | 11 of 13 (66) | 0 of 2 (2) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 4 of 5 (1) |
| hierarchical_logistic | 0 of 4 (0) | 12 of 13 (91) | 0 of 2 (2) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 3 of 5 (11) |
| settlement_quantile_timing | 1 of 4 (1) | 13 of 13 (63) | 0 of 2 (22) | 0 of 0 (5) | 0 of 0 (1) | 0 of 0 (1) | 0 of 2 (2) | 1 of 5 (17) |
| scarcity_logistic_interactions | 0 of 4 (0) | 12 of 13 (80) | 0 of 2 (2) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 2 of 5 (12) |
| calendar_climatology | 0 of 4 (4) | 10 of 13 (96) | 0 of 2 (21) | 0 of 0 (10) | 0 of 0 (3) | 0 of 0 (0) | 0 of 2 (0) | 0 of 5 (0) |
| persistence_logistic | 0 of 4 (0) | 7 of 13 (72) | 0 of 2 (4) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (2) | 0 of 5 (15) |

Table 3a. Tier 3 by calendar year, declared reading: flags per 252 business days over all days (worst horizon); in brackets over the days in scarcity state 0 (limit 21), where the year has any.

| row | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 0 | 89 | 6 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 9 (0) |
| ngboost_laplace | 0 | 103 | 3 | 0 (0) | 0 (0) | 0 (0) | 1 (1) | 11 (0) |
| hierarchical_logistic | 0 | 153 | 2 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 26 (0) |
| settlement_quantile_timing | 6 | 118 | 23 | 5 (5) | 1 (1) | 1 (1) | 3 (3) | 29 (4) |
| scarcity_logistic_interactions | 0 | 147 | 2 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 26 (0) |
| calendar_climatology | 8 | 162 | 21 | 10 (12) | 3 (3) | 0 (0) | 0 (0) | 1 (0) |
| persistence_logistic | 0 | 142 | 4 | 0 (0) | 0 (0) | 0 (0) | 2 (2) | 26 (2) |

Table 2b. Tier 1 by calendar year of the flagged day, downweighted reading: onsets flagged of onsets (worst false alarms at one horizon). Onsets by year: 2018: 4, 2019: 13, 2020: 2, 2021: 0, 2022: 0, 2023: 0, 2024: 2, 2025: 5.

| row | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 0 of 4 (0) | 12 of 13 (60) | 1 of 2 (3) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 2 of 5 (3) |
| ngboost_laplace | 0 of 4 (0) | 11 of 13 (66) | 0 of 2 (2) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 4 of 5 (1) |
| hierarchical_logistic | 0 of 4 (0) | 12 of 13 (91) | 0 of 2 (2) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 3 of 5 (11) |
| settlement_quantile_timing | 1 of 4 (1) | 13 of 13 (63) | 0 of 2 (10) | 0 of 0 (4) | 0 of 0 (1) | 0 of 0 (1) | 0 of 2 (2) | 1 of 5 (17) |
| scarcity_logistic_interactions | 0 of 4 (0) | 12 of 13 (80) | 0 of 2 (2) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 2 of 5 (12) |
| calendar_climatology | 0 of 4 (4) | 10 of 13 (96) | 0 of 2 (13) | 0 of 0 (1) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (0) | 0 of 5 (0) |
| persistence_logistic | 0 of 4 (0) | 7 of 13 (72) | 0 of 2 (5) | 0 of 0 (0) | 0 of 0 (0) | 0 of 0 (0) | 0 of 2 (2) | 0 of 5 (15) |

Table 3b. Tier 3 by calendar year, downweighted reading: flags per 252 business days over all days (worst horizon); in brackets over the days in scarcity state 0 (limit 21), where the year has any.

| row | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 0 | 89 | 6 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 9 (0) |
| ngboost_laplace | 0 | 103 | 3 | 0 (0) | 0 (0) | 0 (0) | 1 (1) | 11 (0) |
| hierarchical_logistic | 0 | 153 | 2 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 26 (0) |
| settlement_quantile_timing | 6 | 118 | 11 | 4 (5) | 1 (1) | 1 (1) | 3 (3) | 29 (4) |
| scarcity_logistic_interactions | 0 | 147 | 2 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 26 (0) |
| calendar_climatology | 8 | 162 | 13 | 1 (2) | 0 (0) | 0 (0) | 0 (0) | 1 (0) |
| persistence_logistic | 0 | 142 | 5 | 0 (0) | 0 (0) | 0 (0) | 2 (2) | 26 (2) |

Table 4. Pooled calibration at h = 1, +5 bp: realised minus mean predicted, over all scored days, inside and outside 2018-19 (weighting 2018-19 to its share of all days leaves the pooled mean unchanged, so the outside reading is the one that can differ).

| row | all days | inside 2018-19 | outside 2018-19 |
|---|---|---|---|
| two_part_gbm | +0.0096 | +0.0069 | +0.0103 |
| ngboost_laplace | +0.0167 | +0.0484 | +0.0088 |
| hierarchical_logistic | -0.0074 | +0.0530 | -0.0226 |
| settlement_quantile_timing | -0.0049 | +0.0797 | -0.0260 |
| scarcity_logistic_interactions | -0.0076 | +0.0650 | -0.0257 |
| calendar_climatology | -0.0398 | +0.1393 | -0.0847 |
| persistence_logistic | -0.0030 | +0.1041 | -0.0299 |

Table 5. How the stretches differ (scored days; spread SOFR - IORB in basis points; panel medians of the inputs).

|  | 2018-19 | 2020 | 2021-23 | 2024 | 2025 |
|---|---|---|---|---|---|
| scored days | 371 | 251 | 748 | 250 | 249 |
| pressure days (> +5 bp) | 102 (27.2%) | 4 (1.6%) | 0 (0.0%) | 5 (2.0%) | 29 (11.6%) |
| onsets / episodes | 17 / 32 | 2 / 3 | 0 / 0 | 2 / 3 | 5 / 9 |
| longest episodes (days) | 12, 10, 8, 7 | 2, 1, 1 | – | 2, 2, 1 | 11, 6, 4, 2 |
| spread median / p90 / max | 2 / 11 / 315 | -1 / 0 / 44 | -10 / -8 / 1 | -8 / -4 / 15 | -5 / 8 / 32 |
| scarcity state shares | 3: 100% | 1: 71%, 2: 2%, 3: 27% | 0: 88%, 1: 12% | 0: 100% | 0: 51%, 1: 22%, 2: 14%, 3: 13% |
| reserve_balances | 1,622.3 | 2,851.9 | 3,339.4 | 3,331.4 | 3,254.7 |
| tga | 330.2 | 1,531.1 | 581.3 | 774.7 | 597.5 |
| sofr_volume | 982.0 | 1,000.0 | 970.0 | 2,007.5 | 2,740.0 |
| dealer_treasury_position | 224.5 | 241.2 | 159.8 | 300.0 | 393.7 |
| treasury_settlement | 0.0 | 45.0 | 22.0 | 14.0 | 28.0 |
| tbill_13w | 2.2 | 0.1 | 1.8 | 5.4 | 4.3 |

Table 6. Refit cadence of the flag cut-off, tier 1 at lead >= 1: onsets flagged of 26 and worst false alarms per onset, for a cut-off refitted every 21 (declared), 10 and 5 scored days.

| row | every 21 | every 10 | every 5 |
|---|---|---|---|
| two_part_gbm | 15 (2.46) | 13 (1.65) | 13 (1.65) |
| ngboost_laplace | 15 (2.54) | 15 (2.35) | 14 (2.19) |
| hierarchical_logistic | 15 (3.65) | 15 (3.42) | 15 (3.46) |
| settlement_quantile_timing | 15 (3.65) | 15 (3.62) | 15 (3.42) |
| scarcity_logistic_interactions | 14 (3.23) | 13 (3.31) | 13 (3.27) |
| calendar_climatology | 10 (5.00) | 11 (4.65) | 11 (4.65) |
| persistence_logistic | 7 (3.42) | 6 (2.85) | 6 (3.04) |

Table 7. Tier 1 by calendar year, cut-off refitted every 10 and every 5 scored days: onsets flagged of onsets, worst false alarms at one horizon (the declared reading is Table 2a).

| row | refit | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| two_part_gbm | 10 | 0 of 4 (9) | 10 of 13 (39) | 1 of 2 (4) | 0 of 2 (0) | 2 of 5 (3) |
| two_part_gbm | 5 | 0 of 4 (7) | 10 of 13 (39) | 1 of 2 (4) | 0 of 2 (0) | 2 of 5 (3) |
| ngboost_laplace | 10 | 1 of 4 (7) | 10 of 13 (61) | 0 of 2 (2) | 0 of 2 (0) | 4 of 5 (1) |
| ngboost_laplace | 5 | 0 of 4 (9) | 10 of 13 (57) | 0 of 2 (2) | 0 of 2 (0) | 4 of 5 (1) |
| hierarchical_logistic | 10 | 0 of 4 (3) | 12 of 13 (85) | 0 of 2 (2) | 0 of 2 (0) | 3 of 5 (11) |
| hierarchical_logistic | 5 | 0 of 4 (3) | 12 of 13 (86) | 0 of 2 (2) | 0 of 2 (0) | 3 of 5 (11) |
| settlement_quantile_timing | 10 | 1 of 4 (1) | 13 of 13 (62) | 0 of 2 (22) | 0 of 2 (2) | 1 of 5 (17) |
| settlement_quantile_timing | 5 | 1 of 4 (5) | 13 of 13 (57) | 0 of 2 (22) | 0 of 2 (2) | 1 of 5 (17) |
| scarcity_logistic_interactions | 10 | 0 of 4 (3) | 11 of 13 (82) | 0 of 2 (2) | 0 of 2 (0) | 2 of 5 (12) |
| scarcity_logistic_interactions | 5 | 0 of 4 (3) | 11 of 13 (81) | 0 of 2 (2) | 0 of 2 (0) | 2 of 5 (12) |
| calendar_climatology | 10 | 0 of 4 (5) | 11 of 13 (83) | 0 of 2 (21) | 0 of 2 (0) | 0 of 5 (0) |
| calendar_climatology | 5 | 0 of 4 (5) | 11 of 13 (82) | 0 of 2 (21) | 0 of 2 (0) | 0 of 5 (0) |
| persistence_logistic | 10 | 0 of 4 (8) | 6 of 13 (55) | 0 of 2 (4) | 0 of 2 (2) | 0 of 5 (14) |
| persistence_logistic | 5 | 0 of 4 (6) | 6 of 13 (60) | 0 of 2 (4) | 0 of 2 (2) | 0 of 5 (14) |

Table 8. Onsets whose warning changes when the cut-off is refitted more often.

| row | refit every | onset day | declared (21) | this cadence |
|---|---|---|---|---|
| two_part_gbm | 10 | 2019-01-15 | flagged | not flagged |
| two_part_gbm | 10 | 2019-02-28 | flagged | not flagged |
| two_part_gbm | 5 | 2019-01-15 | flagged | not flagged |
| two_part_gbm | 5 | 2019-02-28 | flagged | not flagged |
| ngboost_laplace | 10 | 2018-12-17 | not flagged | flagged |
| ngboost_laplace | 10 | 2019-02-28 | flagged | not flagged |
| ngboost_laplace | 5 | 2019-02-28 | flagged | not flagged |
| scarcity_logistic_interactions | 10 | 2019-01-15 | flagged | not flagged |
| scarcity_logistic_interactions | 5 | 2019-01-15 | flagged | not flagged |
| calendar_climatology | 10 | 2019-01-31 | not flagged | flagged |
| calendar_climatology | 5 | 2019-01-31 | not flagged | flagged |
| persistence_logistic | 10 | 2019-11-29 | flagged | not flagged |
| persistence_logistic | 5 | 2019-11-29 | flagged | not flagged |

Table 9. Tier 5 (week-ahead window, +5 bp) under the declared combiner (the maximum) and under independence. Realised minus predicted, and Brier difference against calendar climatology (positive: better), 90% intervals; calibrated = interval covers zero, beats = interval above zero.

| row | combiner | base rate | mean predicted | realised - predicted | Brier diff vs climatology | calibrated | beats clim. | tier 5 |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | max | 0.152 | 0.109 | +0.0425 [+0.0124, +0.0750] | +0.0476 [+0.0331, +0.0638] | no | yes | fail |
| two_part_gbm | independence | 0.152 | 0.152 | +0.0003 [-0.0307, +0.0327] | +0.1362 [+0.1090, +0.1620] | yes | yes | pass |
| ngboost_laplace | max | 0.152 | 0.087 | +0.0654 [+0.0350, +0.0998] | +0.0420 [+0.0303, +0.0551] | no | yes | fail |
| ngboost_laplace | independence | 0.152 | 0.149 | +0.0032 [-0.0271, +0.0356] | +0.1400 [+0.1135, +0.1646] | yes | yes | pass |
| hierarchical_logistic | max | 0.152 | 0.105 | +0.0465 [+0.0139, +0.0831] | +0.0390 [+0.0269, +0.0533] | no | yes | fail |
| hierarchical_logistic | independence | 0.152 | 0.236 | -0.0845 [-0.1229, -0.0466] | +0.1173 [+0.0959, +0.1385] | no | yes | fail |
| settlement_quantile_timing | max | 0.152 | 0.138 | +0.0144 [-0.0178, +0.0483] | +0.0280 [+0.0163, +0.0425] | yes | yes | pass |
| settlement_quantile_timing | independence | 0.152 | 0.240 | -0.0883 [-0.1169, -0.0587] | +0.1210 [+0.1050, +0.1383] | no | yes | fail |
| scarcity_logistic_interactions | max | 0.152 | 0.105 | +0.0474 [+0.0144, +0.0844] | +0.0369 [+0.0253, +0.0491] | no | yes | fail |
| scarcity_logistic_interactions | independence | 0.152 | 0.245 | -0.0928 [-0.1310, -0.0528] | +0.1123 [+0.0910, +0.1337] | no | yes | fail |
| calendar_climatology | max | 0.152 | 0.300 | -0.0470 [-0.1017, +0.0117] | +0.0000 [+0.0000, +0.0000] | yes | no | fail |
| calendar_climatology | independence | 0.152 | 0.869 | -0.3808 [-0.4458, -0.3060] | +0.0000 [+0.0000, +0.0000] | no | no | fail |
| persistence_logistic | max | 0.152 | 0.212 | +0.0011 [-0.0528, +0.0600] | -0.0348 [-0.0510, -0.0203] | yes | no | fail |
| persistence_logistic | independence | 0.152 | 0.607 | -0.2702 [-0.3400, -0.1949] | -0.0854 [-0.1119, -0.0608] | no | no | fail |

Table 10. Tier 3 calibration in every regime (+5 bp): realised minus predicted frequency; a star marks an interval that misses zero. Pressure days in the regime: 2018-19: 102 of 375 days, 2020: 4 of 251 days, 2021-23: 0 of 748 days, 2024: 5 of 250 days, 2025-26: 29 of 249 days.

| row | h | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|---|
| two_part_gbm | 1 | +0.0069 | -0.0073 | -0.0001 * | +0.0192 | +0.0505 |
| two_part_gbm | 2 | -0.0120 | -0.0224 * | -0.0002 * | +0.0195 | +0.0803 * |
| two_part_gbm | 3 | -0.0091 | -0.0195 * | -0.0000 * | +0.0195 | +0.0797 * |
| two_part_gbm | 4 | +0.0118 | -0.0343 * | -0.0001 * | +0.0197 | +0.0863 * |
| two_part_gbm | 5 | +0.0334 | -0.0776 * | -0.0006 * | +0.0196 | +0.0969 * |
| ngboost_laplace | 1 | +0.0484 | -0.0343 * | -0.0003 * | +0.0163 | +0.0721 * |
| ngboost_laplace | 2 | +0.0452 | -0.0139 | -0.0005 * | +0.0163 | +0.0938 * |
| ngboost_laplace | 3 | +0.0505 | -0.0205 * | -0.0009 * | +0.0178 | +0.0996 * |
| ngboost_laplace | 4 | +0.0528 | -0.0331 * | -0.0004 * | +0.0194 | +0.1004 * |
| ngboost_laplace | 5 | +0.0434 | -0.0463 * | -0.0005 * | +0.0195 | +0.1018 * |
| hierarchical_logistic | 1 | +0.0530 | -0.1203 * | -0.0085 * | +0.0135 | -0.0024 |
| hierarchical_logistic | 2 | +0.0679 | -0.1302 * | -0.0112 * | +0.0131 | +0.0279 |
| hierarchical_logistic | 3 | +0.0750 | -0.1427 * | -0.0157 * | +0.0120 | +0.0365 |
| hierarchical_logistic | 4 | +0.0740 | -0.1353 * | -0.0113 * | +0.0134 | +0.0323 |
| hierarchical_logistic | 5 | +0.0736 | -0.1465 * | -0.0125 * | +0.0131 | +0.0317 |
| settlement_quantile_timing | 1 | +0.0797 * | -0.0864 * | -0.0197 * | -0.0089 | -0.0014 |
| settlement_quantile_timing | 2 | +0.1061 * | -0.0852 * | -0.0142 * | -0.0047 | -0.0008 |
| settlement_quantile_timing | 3 | +0.1122 * | -0.0896 * | -0.0156 * | -0.0030 | -0.0001 |
| settlement_quantile_timing | 4 | +0.1241 * | -0.0963 * | -0.0175 * | -0.0060 | +0.0024 |
| settlement_quantile_timing | 5 | +0.1243 * | -0.1084 * | -0.0208 * | -0.0059 | +0.0061 |
| scarcity_logistic_interactions | 1 | +0.0650 | -0.1306 * | -0.0115 * | +0.0118 | -0.0004 |
| scarcity_logistic_interactions | 2 | +0.0694 | -0.1363 * | -0.0121 * | +0.0128 | +0.0284 |
| scarcity_logistic_interactions | 3 | +0.0756 | -0.1474 * | -0.0166 * | +0.0117 | +0.0390 |
| scarcity_logistic_interactions | 4 | +0.0750 | -0.1418 * | -0.0121 * | +0.0133 | +0.0332 |
| scarcity_logistic_interactions | 5 | +0.0828 | -0.1589 * | -0.0167 * | +0.0113 | +0.0337 |
| calendar_climatology | 1 | +0.1393 * | -0.1832 * | -0.1084 * | -0.0507 * | +0.0519 |
| calendar_climatology | 2 | +0.1372 * | -0.1835 * | -0.1085 * | -0.0508 * | +0.0519 |
| calendar_climatology | 3 | +0.1354 * | -0.1838 * | -0.1086 * | -0.0508 * | +0.0520 |
| calendar_climatology | 4 | +0.1362 * | -0.1841 * | -0.1087 * | -0.0509 * | +0.0521 |
| calendar_climatology | 5 | +0.1372 * | -0.1844 * | -0.1088 * | -0.0509 * | +0.0521 |
| persistence_logistic | 1 | +0.1041 * | -0.1154 * | -0.0237 * | -0.0109 | +0.0187 |
| persistence_logistic | 2 | +0.1182 * | -0.1349 * | -0.0342 * | -0.0155 | +0.0245 |
| persistence_logistic | 3 | +0.1198 * | -0.1668 * | -0.0595 * | -0.0256 * | +0.0339 |
| persistence_logistic | 4 | +0.1255 * | -0.1440 * | -0.0401 * | -0.0165 | +0.0270 |
| persistence_logistic | 5 | +0.1273 * | -0.1474 * | -0.0420 * | -0.0174 | +0.0275 |

Table 11. Where tier 3 fails, counted over the five leads: regimes whose calibration interval misses zero, and abundant stretches over the 21-flags limit.

| row | tier 3 | calibration misses zero (leads) | alarm rate over limit (leads) |
|---|---|---|---|
| two_part_gbm | fail | 2021-23: 5, 2020: 4, 2025-26: 4 | none |
| ngboost_laplace | fail | 2020: 4, 2021-23: 5, 2025-26: 5 | none |
| hierarchical_logistic | fail | 2020: 5, 2021-23: 5 | none |
| settlement_quantile_timing | fail | 2018-19: 5, 2020: 5, 2021-23: 5 | none |
| scarcity_logistic_interactions | fail | 2020: 5, 2021-23: 5 | none |
| calendar_climatology | fail | 2018-19: 5, 2020: 5, 2021-23: 5, 2024: 5 | none |
| persistence_logistic | fail | 2018-19: 5, 2020: 5, 2021-23: 5, 2024: 1 | none |
