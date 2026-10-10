Table 1. The judge row, with and without the back-filled history (tiers 1, 3 and 5, under the rule in force)

| model | history | onsets flagged | recall [90%] | worst false alarms per onset (weighted; flat) | tier 1 | tier 3 | tier 5 | pass |
|---|---|---|---|---|---|---|---|---|
| risk_gbm | without | 13 of 26 | 0.500 [0.310, 0.667] | 0.80; 1.38 | yes | no | no | no |
| risk_gbm | with | 13 of 26 | 0.500 [0.320, 0.667] | 0.84; 1.42 | yes | no | no | no |
| risk_gbm_base | without | 14 of 26 | 0.538 [0.360, 0.719] | 0.97; 1.50 | yes | no | no | no |
| risk_gbm_base | with | 16 of 26 | 0.615 [0.444, 0.786] | 1.68; 2.31 | yes | no | no | no |
| risk_logistic | without | 16 of 26 | 0.615 [0.435, 0.800] | 1.74; 2.42 | yes | no | no | no |
| risk_logistic | with | 15 of 26 | 0.577 [0.400, 0.750] | 1.74; 2.42 | yes | no | no | no |
| risk_logistic_base | without | 15 of 26 | 0.577 [0.391, 0.762] | 1.65; 2.31 | yes | no | no | no |
| risk_logistic_base | with | 13 of 26 | 0.500 [0.318, 0.667] | 1.41; 2.04 | yes | no | no | no |
| risk_quantile_skewt_base | without | 15 of 26 | 0.577 [0.391, 0.750] | 1.62; 2.31 | yes | no | no | no |
| risk_quantile_skewt_base | with | 15 of 26 | 0.577 [0.409, 0.750] | 1.36; 1.96 | yes | no | no | no |

Table 2. Paired, with against without (recall: onsets flagged at some lead 1 to 5; Brier difference on all scored days at +5 bp, positive: the history helps), 90% stationary-bootstrap intervals

| model | recall with | recall without | recall difference (with − without) | Brier difference h = 1 | Brier difference h = 2 | Brier difference h = 3 | Brier difference h = 4 | Brier difference h = 5 |
|---|---|---|---|---|---|---|---|---|
| risk_gbm | 0.500 [0.323, 0.682] | 0.500 [0.323, 0.682] | +0.000 [+0.000, +0.000] | -0.00003 [-0.00041, +0.00032] | +0.00009 [-0.00033, +0.00064] | -0.00027 [-0.00106, +0.00033] | -0.00071 [-0.00162, -0.00000] | -0.00039 [-0.00106, +0.00021] |
| risk_gbm_base | 0.615 [0.455, 0.789] | 0.538 [0.364, 0.731] | +0.077 [+0.000, +0.167] | -0.00216 [-0.00397, -0.00043] | +0.00038 [-0.00143, +0.00244] | -0.00066 [-0.00330, +0.00201] | -0.00111 [-0.00361, +0.00152] | -0.00073 [-0.00278, +0.00138] |
| risk_logistic | 0.577 [0.391, 0.750] | 0.615 [0.435, 0.792] | -0.038 [-0.111, +0.000] | -0.00002 [-0.00011, +0.00004] | +0.00002 [-0.00006, +0.00010] | +0.00017 [-0.00021, +0.00061] | +0.00045 [-0.00010, +0.00116] | -0.00016 [-0.00050, +0.00016] |
| risk_logistic_base | 0.500 [0.333, 0.667] | 0.577 [0.381, 0.750] | -0.077 [-0.167, +0.000] | +0.00019 [-0.00143, +0.00173] | +0.00052 [-0.00106, +0.00209] | +0.00212 [+0.00010, +0.00477] | +0.00208 [-0.00063, +0.00585] | +0.00074 [-0.00123, +0.00314] |
| risk_quantile_skewt_base | 0.577 [0.400, 0.750] | 0.577 [0.393, 0.758] | +0.000 [-0.087, +0.087] | +0.00599 [+0.00257, +0.00983] | +0.00464 [+0.00162, +0.00802] | +0.00284 [+0.00013, +0.00589] | +0.00306 [+0.00046, +0.00597] | +0.00175 [-0.00106, +0.00491] |

Table 3. +5 bp onsets flagged at some lead 1 to 5, by calendar year of the onset

| model | history | **2018** | 2019 | **2020** | **2024** | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm | without | 0/4 | 10/13 | 0/2 | 0/2 | 3/5 | 13/26 |
| risk_gbm | with | 0/4 | 10/13 | 0/2 | 0/2 | 3/5 | 13/26 |
| risk_gbm_base | without | 0/4 | 10/13 | 0/2 | 0/2 | 4/5 | 14/26 |
| risk_gbm_base | with | 1/4 | 10/13 | 0/2 | 0/2 | 5/5 | 16/26 |
| risk_logistic | without | 0/4 | 10/13 | 0/2 | 1/2 | 5/5 | 16/26 |
| risk_logistic | with | 0/4 | 10/13 | 0/2 | 0/2 | 5/5 | 15/26 |
| risk_logistic_base | without | 0/4 | 10/13 | 0/2 | 0/2 | 5/5 | 15/26 |
| risk_logistic_base | with | 0/4 | 9/13 | 0/2 | 0/2 | 4/5 | 13/26 |
| risk_quantile_skewt_base | without | 0/4 | 10/13 | 0/2 | 0/2 | 5/5 | 15/26 |
| risk_quantile_skewt_base | with | 1/4 | 9/13 | 0/2 | 0/2 | 5/5 | 15/26 |

Table 4. False alarms per onset by calendar year, at the worst horizon, under the weighted miss rule in force

| model | history | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|---|
| risk_gbm | without | 0.50 | 0.56 | 6.00 | 0.50 | 0.55 |
| risk_gbm | with | 0.50 | 0.56 | 6.50 | 0.50 | 0.55 |
| risk_gbm_base | without | 0.50 | 0.62 | 8.50 | 0.00 | 0.30 |
| risk_gbm_base | with | 0.75 | 0.75 | 13.62 | 1.25 | 0.75 |
| risk_logistic | without | 0.50 | 0.77 | 14.50 | 1.62 | 1.75 |
| risk_logistic | with | 0.50 | 0.77 | 13.50 | 1.62 | 1.75 |
| risk_logistic_base | without | 0.50 | 0.77 | 14.12 | 0.75 | 0.70 |
| risk_logistic_base | with | 1.00 | 0.75 | 12.50 | 0.00 | 0.55 |
| risk_quantile_skewt_base | without | 0.00 | 0.60 | 15.38 | 0.12 | 0.65 |
| risk_quantile_skewt_base | with | 0.25 | 0.50 | 12.62 | 1.25 | 0.65 |

Table 5. The same, flat count

| model | history | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|---|
| risk_gbm | without | 0.50 | 1.46 | 6.50 | 0.50 | 1.00 |
| risk_gbm | with | 0.50 | 1.46 | 7.00 | 0.50 | 1.00 |
| risk_gbm_base | without | 0.50 | 1.46 | 9.00 | 0.00 | 0.60 |
| risk_gbm_base | with | 0.75 | 1.69 | 14.50 | 1.50 | 1.20 |
| risk_logistic | without | 0.50 | 1.77 | 15.00 | 2.00 | 2.20 |
| risk_logistic | with | 0.50 | 1.77 | 14.00 | 2.00 | 2.20 |
| risk_logistic_base | without | 0.50 | 1.77 | 15.00 | 1.00 | 1.20 |
| risk_logistic_base | with | 1.00 | 1.69 | 13.00 | 0.00 | 1.00 |
| risk_quantile_skewt_base | without | 0.00 | 1.54 | 16.00 | 0.50 | 1.40 |
| risk_quantile_skewt_base | with | 0.25 | 1.31 | 13.50 | 1.50 | 1.40 |

Table 6. Training history at each 2018 onset (refit in force, window, what it holds), without and with the back-fill

| 2018 onset | h | refit window with → end | rows without / with | pressure days without / with | onsets without / with | pressure days on risk dates without / with |
|---|---|---|---|---|---|---|
| 2018-06-29 | 1 | 2014-08-22 → 2018-06-27 | 61 / 960 | 3 / 8 | 1 / 4 | 1 / 5 |
| 2018-11-15 | 1 | 2014-08-22 → 2018-10-26 | 145 / 1044 | 5 / 10 | 2 / 5 | 3 / 7 |
| 2018-11-15 | 5 | 2014-08-22 → 2018-10-26 | 145 / 1044 | 5 / 10 | 2 / 5 | 2 / 6 |
| 2018-11-30 | 1 | 2014-08-22 → 2018-11-28 | 166 / 1065 | 7 / 12 | 3 / 6 | 4 / 8 |
| 2018-11-30 | 5 | 2014-08-22 → 2018-10-26 | 145 / 1044 | 5 / 10 | 2 / 5 | 2 / 6 |
| 2018-12-17 | 1 | 2014-08-22 → 2018-11-28 | 166 / 1065 | 7 / 12 | 3 / 6 | 4 / 8 |
| 2018-12-17 | 5 | 2014-08-22 → 2018-11-28 | 166 / 1065 | 7 / 12 | 3 / 6 | 2 / 6 |
| 2018-12-28 | 1 | 2014-08-22 → 2018-11-28 | 166 / 1065 | 7 / 12 | 3 / 6 | 4 / 8 |
| 2018-12-28 | 5 | 2014-08-22 → 2018-11-28 | 166 / 1065 | 7 / 12 | 3 / 6 | 2 / 6 |

Table 7. Back-filled rows each model actually used (last fit)

| model | h | back-filled rows in the training frame | back-filled label days that trained a pair | of them risk dates (what the fit uses) | all pairs in the last fit |
|---|---|---|---|---|---|
| risk_gbm | 1 | 899 | 696 | 0 | 2626 |
| risk_gbm | 2 | 899 | 757 | 0 | 2687 |
| risk_gbm | 3 | 899 | 756 | 0 | 2686 |
| risk_gbm | 4 | 899 | 755 | 0 | 2685 |
| risk_gbm | 5 | 899 | 754 | 0 | 2663 |
| risk_gbm_base | 1 | 899 | 890 | 194 | 2820 |
| risk_gbm_base | 2 | 899 | 889 | 132 | 2819 |
| risk_gbm_base | 3 | 899 | 888 | 132 | 2818 |
| risk_gbm_base | 4 | 899 | 887 | 132 | 2817 |
| risk_gbm_base | 5 | 899 | 886 | 132 | 2795 |
| risk_logistic | 1 | 899 | 696 | 0 | 2626 |
| risk_logistic | 2 | 899 | 757 | 0 | 2687 |
| risk_logistic | 3 | 899 | 756 | 0 | 2686 |
| risk_logistic | 4 | 899 | 755 | 0 | 2685 |
| risk_logistic | 5 | 899 | 754 | 0 | 2663 |
| risk_logistic_base | 1 | 899 | 890 | 194 | 2820 |
| risk_logistic_base | 2 | 899 | 889 | 132 | 2819 |
| risk_logistic_base | 3 | 899 | 888 | 132 | 2818 |
| risk_logistic_base | 4 | 899 | 887 | 132 | 2817 |
| risk_logistic_base | 5 | 899 | 886 | 132 | 2795 |
| risk_quantile_skewt_base | 1 | 899 | 890 | 194 | 2820 |
| risk_quantile_skewt_base | 2 | 899 | 889 | 132 | 2819 |
| risk_quantile_skewt_base | 3 | 899 | 888 | 132 | 2818 |
| risk_quantile_skewt_base | 4 | 899 | 887 | 132 | 2817 |
| risk_quantile_skewt_base | 5 | 899 | 886 | 132 | 2795 |
