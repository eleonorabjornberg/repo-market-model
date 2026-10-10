# Alarm cool-down (#459): base rows and their cooled forms

Tier 1 at lead >= 1, +5 bp, days to 2025-12-31, under the weighted-miss rule of #454 forced on (a scratch run; the flag cut-offs are chosen on the weighted count, tier 1's limit is on it). `with exception` keeps repeats when a pressure day starts in the window (reads the days after the flag); `strict` drops every repeat.

| row | form | onsets warned | recall [90%] | worst false alarms per onset, flat (weighted) | tier 1 | tier 3 | tier 5 | pass |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | base | 15 of 26 | 0.577 [0.400, 0.762] | 4.81 (2.55) | no | no | no | no |
| two_part_gbm | with exception | 15 of 26 | 0.577 [0.387, 0.759] | 2.00 (0.83) | yes | no | no | no |
| two_part_gbm | strict | 11 of 26 | 0.423 [0.235, 0.600] | 1.12 (0.56) | no | no | no | no |
| ngboost_laplace | base | 17 of 26 | 0.654 [0.467, 0.826] | 4.08 (1.73) | yes | no | no | no |
| ngboost_laplace | with exception | 17 of 26 | 0.654 [0.474, 0.828] | 1.73 (0.61) | yes | no | no | no |
| ngboost_laplace | strict | 11 of 26 | 0.423 [0.250, 0.609] | 0.85 (0.42) | no | no | no | no |
| hierarchical_logistic | base | 15 of 26 | 0.577 [0.400, 0.750] | 6.23 (2.91) | no | no | no | no |
| hierarchical_logistic | with exception | 15 of 26 | 0.577 [0.400, 0.750] | 2.46 (0.90) | yes | no | no | no |
| hierarchical_logistic | strict | 10 of 26 | 0.385 [0.217, 0.560] | 1.12 (0.52) | no | no | no | no |
| settlement_quantile_timing | base | 16 of 26 | 0.615 [0.444, 0.778] | 6.38 (3.41) | no | no | yes | no |
| settlement_quantile_timing | with exception | 16 of 26 | 0.615 [0.448, 0.778] | 2.85 (1.80) | yes | no | yes | no |
| settlement_quantile_timing | strict | 10 of 26 | 0.385 [0.217, 0.548] | 2.19 (1.72) | no | no | yes | no |
| scarcity_logistic_interactions | base | 14 of 26 | 0.538 [0.346, 0.731] | 5.50 (2.39) | no | no | no | no |
| scarcity_logistic_interactions | with exception | 14 of 26 | 0.538 [0.353, 0.722] | 2.04 (0.71) | yes | no | no | no |
| scarcity_logistic_interactions | strict | 9 of 26 | 0.346 [0.185, 0.524] | 1.15 (0.48) | no | no | no | no |
| scarcity_logistic | base | 13 of 26 | 0.500 [0.320, 0.696] | 4.73 (2.09) | no | no | no | no |
| scarcity_logistic | with exception | 13 of 26 | 0.500 [0.316, 0.692] | 1.85 (0.66) | yes | no | no | no |
| scarcity_logistic | strict | 10 of 26 | 0.385 [0.217, 0.556] | 0.92 (0.40) | no | no | no | no |

False alarms per onset by horizon:

| row | form | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| two_part_gbm | base | 2.04 | 3.92 | 4.27 | 2.08 | 4.81 |
| two_part_gbm | with exception | 0.77 | 1.62 | 1.62 | 0.88 | 2.00 |
| two_part_gbm | strict | 0.58 | 0.81 | 0.85 | 0.65 | 1.12 |
| ngboost_laplace | base | 3.31 | 3.46 | 3.27 | 3.58 | 4.08 |
| ngboost_laplace | with exception | 1.19 | 1.12 | 1.04 | 1.58 | 1.73 |
| ngboost_laplace | strict | 0.73 | 0.69 | 0.62 | 0.73 | 0.85 |
| hierarchical_logistic | base | 5.15 | 4.38 | 4.04 | 4.58 | 6.23 |
| hierarchical_logistic | with exception | 1.88 | 1.58 | 1.46 | 1.31 | 2.46 |
| hierarchical_logistic | strict | 1.04 | 0.88 | 0.81 | 0.81 | 1.12 |
| settlement_quantile_timing | base | 5.62 | 6.27 | 6.12 | 6.38 | 6.31 |
| settlement_quantile_timing | with exception | 2.46 | 2.42 | 2.38 | 2.85 | 2.69 |
| settlement_quantile_timing | strict | 2.19 | 1.65 | 1.65 | 1.77 | 1.81 |
| scarcity_logistic_interactions | base | 5.50 | 4.38 | 4.04 | 4.50 | 4.65 |
| scarcity_logistic_interactions | with exception | 2.04 | 1.58 | 1.46 | 1.31 | 1.85 |
| scarcity_logistic_interactions | strict | 1.15 | 0.88 | 0.81 | 0.81 | 0.85 |
| scarcity_logistic | base | 4.73 | 4.38 | 4.04 | 4.50 | 4.65 |
| scarcity_logistic | with exception | 1.73 | 1.58 | 1.46 | 1.31 | 1.85 |
| scarcity_logistic | strict | 0.92 | 0.88 | 0.81 | 0.81 | 0.85 |

Alarms at h = 1 (flags; of them false alarms) by regime:

| row | form | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|---|
| two_part_gbm | base | 94 (40) | 5 (4) | 0 (0) | 0 (0) | 22 (9) |
| two_part_gbm | with exception | 39 (14) | 5 (4) | 0 (0) | 0 (0) | 10 (2) |
| two_part_gbm | strict | 26 (11) | 3 (2) | 0 (0) | 0 (0) | 6 (2) |
| ngboost_laplace | base | 142 (80) | 6 (5) | 0 (0) | 1 (0) | 12 (1) |
| ngboost_laplace | with exception | 51 (26) | 6 (5) | 0 (0) | 1 (0) | 8 (0) |
| ngboost_laplace | strict | 33 (14) | 6 (5) | 0 (0) | 1 (0) | 8 (0) |
| hierarchical_logistic | base | 180 (106) | 16 (15) | 0 (0) | 0 (0) | 29 (13) |
| hierarchical_logistic | with exception | 73 (40) | 8 (7) | 0 (0) | 0 (0) | 11 (2) |
| hierarchical_logistic | strict | 33 (19) | 7 (6) | 0 (0) | 0 (0) | 8 (2) |
| settlement_quantile_timing | base | 166 (89) | 31 (30) | 12 (12) | 4 (3) | 29 (12) |
| settlement_quantile_timing | with exception | 56 (22) | 25 (24) | 12 (12) | 2 (2) | 9 (4) |
| settlement_quantile_timing | strict | 38 (17) | 23 (22) | 12 (12) | 2 (2) | 9 (4) |
| scarcity_logistic_interactions | base | 202 (126) | 5 (5) | 0 (0) | 0 (0) | 26 (12) |
| scarcity_logistic_interactions | with exception | 83 (47) | 2 (2) | 0 (0) | 0 (0) | 11 (4) |
| scarcity_logistic_interactions | strict | 39 (24) | 2 (2) | 0 (0) | 0 (0) | 8 (4) |
| scarcity_logistic | base | 179 (106) | 6 (6) | 0 (0) | 0 (0) | 25 (11) |
| scarcity_logistic | with exception | 73 (40) | 3 (3) | 0 (0) | 0 (0) | 10 (2) |
| scarcity_logistic | strict | 33 (19) | 3 (3) | 0 (0) | 0 (0) | 7 (2) |

Alarms at h = 1 (flags; of them false alarms) by pressure-day type:

| row | form | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|---|
| two_part_gbm | base | 14 (4) | 92 (45) | 5 (1) | 10 (3) |
| two_part_gbm | with exception | 7 (3) | 37 (14) | 4 (1) | 6 (2) |
| two_part_gbm | strict | 5 (3) | 24 (11) | 3 (1) | 3 (0) |
| ngboost_laplace | base | 19 (7) | 124 (75) | 7 (1) | 11 (3) |
| ngboost_laplace | with exception | 13 (4) | 43 (26) | 4 (1) | 6 (0) |
| ngboost_laplace | strict | 10 (3) | 29 (15) | 3 (1) | 6 (0) |
| hierarchical_logistic | base | 22 (10) | 181 (116) | 7 (2) | 15 (6) |
| hierarchical_logistic | with exception | 13 (5) | 64 (38) | 6 (2) | 9 (4) |
| hierarchical_logistic | strict | 5 (2) | 35 (23) | 5 (2) | 3 (0) |
| settlement_quantile_timing | base | 26 (11) | 176 (110) | 21 (14) | 19 (11) |
| settlement_quantile_timing | with exception | 19 (9) | 61 (38) | 17 (14) | 7 (3) |
| settlement_quantile_timing | strict | 17 (9) | 43 (31) | 17 (14) | 7 (3) |
| scarcity_logistic_interactions | base | 21 (8) | 192 (128) | 5 (1) | 15 (6) |
| scarcity_logistic_interactions | with exception | 12 (4) | 71 (44) | 4 (1) | 9 (4) |
| scarcity_logistic_interactions | strict | 3 (1) | 40 (28) | 3 (1) | 3 (0) |
| scarcity_logistic | base | 20 (8) | 168 (107) | 7 (2) | 15 (6) |
| scarcity_logistic | with exception | 12 (4) | 59 (35) | 6 (2) | 9 (4) |
| scarcity_logistic | strict | 4 (1) | 31 (21) | 5 (2) | 3 (0) |
