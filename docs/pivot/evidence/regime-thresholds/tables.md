Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic+scarce_cutoff | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace+scarce_cutoff | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 2.54 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 0.231 | 3.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_logistic+scarce_cutoff | 13 of 26 | 0.500 [0.320, 0.684] | 0.231 | 3.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 0.231 | 3.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_logistic_interactions+scarce_cutoff | 14 of 26 | 0.538 [0.343, 0.727] | 0.231 | 3.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| settlement_quantile_timing | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 3.65 | 2.2 / 2.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| settlement_quantile_timing+scarce_cutoff | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 2.2 / 2.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 2.46 | 0.0 / 0.0 | 4 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| two_part_gbm+scarce_cutoff | 15 of 26 | 0.577 [0.391, 0.765] | 0.192 | 2.46 | 0.0 / 0.0 | 4 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic+scarce_cutoff | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| ngboost_laplace+scarce_cutoff | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| scarcity_logistic | 0.63 (102) | 0.00 (4) | – | 0.00 (5) | 0.48 (29) | 0.71 (17) | 0.51 (101) | 0.56 (9) | 0.69 (13) |
| scarcity_logistic+scarce_cutoff | 0.63 (102) | 0.00 (4) | – | 0.00 (5) | 0.48 (29) | 0.71 (17) | 0.51 (101) | 0.56 (9) | 0.69 (13) |
| scarcity_logistic_interactions | 0.66 (102) | 0.00 (4) | – | 0.00 (5) | 0.48 (29) | 0.76 (17) | 0.54 (101) | 0.44 (9) | 0.69 (13) |
| scarcity_logistic_interactions+scarce_cutoff | 0.66 (102) | 0.00 (4) | – | 0.00 (5) | 0.48 (29) | 0.76 (17) | 0.54 (101) | 0.44 (9) | 0.69 (13) |
| settlement_quantile_timing | 0.59 (102) | 0.25 (4) | – | 0.20 (5) | 0.52 (29) | 0.65 (17) | 0.50 (101) | 0.78 (9) | 0.62 (13) |
| settlement_quantile_timing+scarce_cutoff | 0.59 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.71 (17) | 0.52 (101) | 0.78 (9) | 0.62 (13) |
| two_part_gbm | 0.25 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.47 (17) | 0.16 (101) | 0.44 (9) | 0.38 (13) |
| two_part_gbm+scarce_cutoff | 0.25 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.47 (17) | 0.16 (101) | 0.44 (9) | 0.38 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| hierarchical_logistic+scarce_cutoff | +0.0265 [+0.0034, +0.0521] | +0.0181 [+0.0041, +0.0304] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0039, +0.0052] | +0.0382 [+0.0070, +0.0769] | +0.0440 [+0.0220, +0.0707] | +0.0128 [+0.0067, +0.0200] | +0.0754 [+0.0181, +0.1293] | +0.0569 [+0.0325, +0.0850] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| ngboost_laplace+scarce_cutoff | +0.0543 [+0.0271, +0.0840] | +0.0329 [+0.0235, +0.0416] | +0.0138 [+0.0122, +0.0157] | +0.0041 [+0.0006, +0.0071] | +0.0287 [+0.0112, +0.0508] | +0.0481 [+0.0302, +0.0684] | +0.0187 [+0.0124, +0.0259] | +0.1308 [+0.0506, +0.2077] | +0.0670 [+0.0484, +0.0862] |
| scarcity_logistic | +0.0280 [+0.0063, +0.0536] | +0.0171 [+0.0033, +0.0296] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0040, +0.0053] | +0.0380 [+0.0067, +0.0757] | +0.0443 [+0.0233, +0.0694] | +0.0126 [+0.0064, +0.0198] | +0.0957 [+0.0480, +0.1406] | +0.0563 [+0.0325, +0.0826] |
| scarcity_logistic+scarce_cutoff | +0.0280 [+0.0051, +0.0528] | +0.0171 [+0.0030, +0.0294] | +0.0137 [+0.0119, +0.0155] | +0.0013 [-0.0040, +0.0053] | +0.0380 [+0.0067, +0.0750] | +0.0443 [+0.0229, +0.0693] | +0.0126 [+0.0062, +0.0193] | +0.0957 [+0.0470, +0.1404] | +0.0563 [+0.0319, +0.0824] |
| scarcity_logistic_interactions | +0.0243 [+0.0022, +0.0477] | +0.0179 [+0.0050, +0.0296] | +0.0136 [+0.0117, +0.0154] | +0.0013 [-0.0038, +0.0053] | +0.0346 [+0.0037, +0.0735] | +0.0438 [+0.0240, +0.0678] | +0.0123 [+0.0065, +0.0189] | +0.0462 [-0.0256, +0.1140] | +0.0556 [+0.0324, +0.0801] |
| scarcity_logistic_interactions+scarce_cutoff | +0.0243 [+0.0019, +0.0478] | +0.0179 [+0.0052, +0.0295] | +0.0136 [+0.0119, +0.0153] | +0.0013 [-0.0039, +0.0052] | +0.0346 [+0.0042, +0.0737] | +0.0438 [+0.0237, +0.0694] | +0.0123 [+0.0063, +0.0188] | +0.0462 [-0.0278, +0.1128] | +0.0556 [+0.0319, +0.0828] |
| settlement_quantile_timing | +0.0522 [+0.0263, +0.0803] | +0.0049 [-0.0050, +0.0149] | +0.0093 [+0.0083, +0.0105] | -0.0011 [-0.0082, +0.0038] | +0.0320 [+0.0001, +0.0721] | +0.0337 [+0.0033, +0.0676] | +0.0165 [+0.0096, +0.0247] | -0.0228 [-0.0831, +0.0330] | +0.0523 [+0.0344, +0.0732] |
| settlement_quantile_timing+scarce_cutoff | +0.0522 [+0.0263, +0.0804] | +0.0049 [-0.0054, +0.0147] | +0.0093 [+0.0082, +0.0105] | -0.0011 [-0.0077, +0.0037] | +0.0320 [+0.0002, +0.0714] | +0.0337 [+0.0026, +0.0681] | +0.0165 [+0.0093, +0.0243] | -0.0228 [-0.0818, +0.0307] | +0.0523 [+0.0353, +0.0724] |
| two_part_gbm | +0.0459 [+0.0147, +0.0821] | +0.0338 [+0.0187, +0.0466] | +0.0138 [+0.0121, +0.0157] | +0.0016 [-0.0029, +0.0052] | +0.0185 [-0.0013, +0.0446] | +0.0499 [+0.0247, +0.0784] | +0.0149 [+0.0077, +0.0231] | +0.1213 [+0.0296, +0.2096] | +0.0672 [+0.0447, +0.0923] |
| two_part_gbm+scarce_cutoff | +0.0459 [+0.0138, +0.0808] | +0.0338 [+0.0190, +0.0465] | +0.0138 [+0.0121, +0.0157] | +0.0016 [-0.0029, +0.0054] | +0.0185 [-0.0008, +0.0449] | +0.0499 [+0.0232, +0.0791] | +0.0149 [+0.0074, +0.0234] | +0.1213 [+0.0269, +0.2105] | +0.0672 [+0.0435, +0.0937] |


Table 4. Onsets flagged at lead of at least 1 (a flag on the onset day at any horizon 1 to 5), by calendar year, under the pooled cut-off and under the scarce-state cut-off (pooled / scarce); the number of onsets in the year in the header.

| model | 2018 (4) | 2019 (13) | 2020 (2) | 2024 (2) | 2025 (5) | all (26) |
|---|---|---|---|---|---|---|
| two_part_gbm | 0 / 0 | 12 / 12 | 1 / 1 | 0 / 0 | 2 / 2 | 15 / 15 |
| ngboost_laplace | 0 / 0 | 11 / 11 | 0 / 0 | 0 / 0 | 4 / 4 | 15 / 15 |
| hierarchical_logistic | 0 / 0 | 12 / 12 | 0 / 0 | 0 / 0 | 3 / 3 | 15 / 15 |
| settlement_quantile_timing | 1 / 1 | 13 / 13 | 0 / 0 | 0 / 0 | 1 / 1 | 15 / 15 |
| scarcity_logistic_interactions | 0 / 0 | 12 / 12 | 0 / 0 | 0 / 0 | 2 / 2 | 14 / 14 |
| scarcity_logistic | 0 / 0 | 10 / 10 | 0 / 0 | 0 / 0 | 3 / 3 | 13 / 13 |

Table 5. The scarce-state cut-off (as-of state at least 2), h = 1 to 5: scored days in the state, its pressure days and onsets, refit blocks with a day in the state whose cut-off flags nothing, and the flags on those days under the pooled and the scarce-state cut-off.

| model | h | scored days | scarce days | scarce pressure days | scarce onsets | blocks with a scarce day | of them, flag nothing | flags: pooled | flags: scarce cut-off |
|---|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 1 | 1873 | 514 | 134 | 24 | 26 | 7 | 39 | 39 |
| two_part_gbm | 2 | 1872 | 513 | 133 | 23 | 26 | 10 | 44 | 44 |
| two_part_gbm | 3 | 1871 | 512 | 132 | 23 | 26 | 6 | 57 | 55 |
| two_part_gbm | 4 | 1870 | 511 | 132 | 23 | 26 | 7 | 69 | 68 |
| two_part_gbm | 5 | 1869 | 510 | 132 | 23 | 25 | 6 | 95 | 95 |
| ngboost_laplace | 1 | 1873 | 514 | 134 | 24 | 26 | 7 | 111 | 110 |
| ngboost_laplace | 2 | 1872 | 513 | 133 | 23 | 26 | 8 | 63 | 63 |
| ngboost_laplace | 3 | 1871 | 512 | 132 | 23 | 26 | 7 | 59 | 59 |
| ngboost_laplace | 4 | 1870 | 511 | 132 | 23 | 26 | 7 | 102 | 102 |
| ngboost_laplace | 5 | 1869 | 510 | 132 | 23 | 25 | 7 | 59 | 59 |
| hierarchical_logistic | 1 | 1873 | 514 | 134 | 24 | 26 | 7 | 164 | 164 |
| hierarchical_logistic | 2 | 1872 | 513 | 133 | 23 | 26 | 7 | 91 | 91 |
| hierarchical_logistic | 3 | 1871 | 512 | 132 | 23 | 26 | 7 | 150 | 150 |
| hierarchical_logistic | 4 | 1870 | 511 | 132 | 23 | 26 | 7 | 144 | 144 |
| hierarchical_logistic | 5 | 1869 | 510 | 132 | 23 | 25 | 6 | 158 | 158 |
| settlement_quantile_timing | 1 | 1873 | 514 | 134 | 24 | 26 | 5 | 129 | 135 |
| settlement_quantile_timing | 2 | 1872 | 513 | 133 | 23 | 26 | 7 | 130 | 131 |
| settlement_quantile_timing | 3 | 1871 | 512 | 132 | 23 | 26 | 7 | 144 | 147 |
| settlement_quantile_timing | 4 | 1870 | 511 | 132 | 23 | 26 | 7 | 148 | 149 |
| settlement_quantile_timing | 5 | 1869 | 510 | 132 | 23 | 25 | 7 | 148 | 148 |
| scarcity_logistic_interactions | 1 | 1873 | 514 | 134 | 24 | 26 | 6 | 164 | 163 |
| scarcity_logistic_interactions | 2 | 1872 | 513 | 133 | 23 | 26 | 7 | 111 | 111 |
| scarcity_logistic_interactions | 3 | 1871 | 512 | 132 | 23 | 26 | 7 | 150 | 150 |
| scarcity_logistic_interactions | 4 | 1870 | 511 | 132 | 23 | 26 | 7 | 144 | 144 |
| scarcity_logistic_interactions | 5 | 1869 | 510 | 132 | 23 | 25 | 7 | 145 | 145 |
| scarcity_logistic | 1 | 1873 | 514 | 134 | 24 | 26 | 7 | 152 | 152 |
| scarcity_logistic | 2 | 1872 | 513 | 133 | 23 | 26 | 7 | 111 | 111 |
| scarcity_logistic | 3 | 1871 | 512 | 132 | 23 | 26 | 7 | 150 | 150 |
| scarcity_logistic | 4 | 1870 | 511 | 132 | 23 | 26 | 7 | 144 | 144 |
| scarcity_logistic | 5 | 1869 | 510 | 132 | 23 | 25 | 7 | 145 | 145 |
