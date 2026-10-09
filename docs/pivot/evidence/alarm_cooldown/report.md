# Alarm cool-down (#459): base rows and their cooled forms

Tier 1 at lead >= 1, +5 bp, days to 2025-12-31, under the unweighted rule (every false alarm counts 1; the weighted count is shown beside it). `with exception` keeps repeats when a pressure day starts in the window (reads the days after the flag); `strict` drops every repeat.

| row | form | onsets warned | recall [90%] | worst false alarms per onset, flat (weighted) | tier 1 | tier 3 | tier 5 | pass |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | base | 15 of 26 | 0.577 [0.400, 0.762] | 2.46 (1.07) | no | no | no | no |
| two_part_gbm | with exception | 15 of 26 | 0.577 [0.387, 0.759] | 1.15 (0.42) | yes | no | no | no |
| two_part_gbm | strict | 12 of 26 | 0.462 [0.278, 0.640] | 0.62 (0.26) | no | no | no | no |
| ngboost_laplace | base | 15 of 26 | 0.577 [0.400, 0.759] | 2.54 (1.03) | no | no | no | no |
| ngboost_laplace | with exception | 15 of 26 | 0.577 [0.393, 0.750] | 1.27 (0.44) | yes | no | no | no |
| ngboost_laplace | strict | 10 of 26 | 0.385 [0.217, 0.565] | 0.58 (0.21) | no | no | no | no |
| hierarchical_logistic | base | 15 of 26 | 0.577 [0.400, 0.750] | 3.65 (1.31) | no | no | no | no |
| hierarchical_logistic | with exception | 15 of 26 | 0.577 [0.400, 0.750] | 1.81 (0.65) | yes | no | no | no |
| hierarchical_logistic | strict | 12 of 26 | 0.462 [0.290, 0.647] | 0.96 (0.38) | no | no | no | no |
| settlement_quantile_timing | base | 15 of 26 | 0.577 [0.391, 0.750] | 3.65 (1.68) | no | no | yes | no |
| settlement_quantile_timing | with exception | 15 of 26 | 0.577 [0.400, 0.750] | 1.73 (1.13) | yes | no | yes | no |
| settlement_quantile_timing | strict | 13 of 26 | 0.500 [0.333, 0.667] | 1.38 (1.12) | yes | no | yes | no |
| scarcity_logistic_interactions | base | 14 of 26 | 0.538 [0.346, 0.731] | 3.23 (1.23) | no | no | no | no |
| scarcity_logistic_interactions | with exception | 14 of 26 | 0.538 [0.353, 0.722] | 1.54 (0.54) | yes | no | no | no |
| scarcity_logistic_interactions | strict | 12 of 26 | 0.462 [0.280, 0.652] | 0.88 (0.33) | no | no | no | no |
| scarcity_logistic | base | 13 of 26 | 0.500 [0.320, 0.696] | 3.23 (1.23) | no | no | no | no |
| scarcity_logistic | with exception | 13 of 26 | 0.500 [0.316, 0.692] | 1.42 (0.54) | yes | no | no | no |
| scarcity_logistic | strict | 12 of 26 | 0.462 [0.281, 0.640] | 0.81 (0.33) | no | no | no | no |

False alarms per onset by horizon:

| row | form | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| two_part_gbm | base | 0.23 | 1.15 | 1.58 | 1.35 | 2.46 |
| two_part_gbm | with exception | 0.15 | 0.77 | 0.81 | 0.62 | 1.15 |
| two_part_gbm | strict | 0.15 | 0.42 | 0.46 | 0.42 | 0.62 |
| ngboost_laplace | base | 1.69 | 1.73 | 1.42 | 2.54 | 1.58 |
| ngboost_laplace | with exception | 0.38 | 0.65 | 0.54 | 1.27 | 0.62 |
| ngboost_laplace | strict | 0.35 | 0.46 | 0.35 | 0.58 | 0.38 |
| hierarchical_logistic | base | 3.08 | 1.81 | 3.15 | 3.00 | 3.65 |
| hierarchical_logistic | with exception | 1.46 | 0.81 | 0.81 | 1.00 | 1.81 |
| hierarchical_logistic | strict | 0.81 | 0.38 | 0.50 | 0.62 | 0.96 |
| settlement_quantile_timing | base | 2.92 | 2.69 | 3.50 | 3.54 | 3.65 |
| settlement_quantile_timing | with exception | 1.42 | 1.15 | 1.69 | 1.62 | 1.73 |
| settlement_quantile_timing | strict | 1.38 | 1.00 | 1.19 | 1.27 | 1.23 |
| scarcity_logistic_interactions | base | 3.19 | 2.00 | 3.15 | 3.00 | 3.23 |
| scarcity_logistic_interactions | with exception | 1.54 | 0.77 | 0.81 | 1.00 | 1.42 |
| scarcity_logistic_interactions | strict | 0.88 | 0.35 | 0.50 | 0.62 | 0.81 |
| scarcity_logistic | base | 2.85 | 2.00 | 3.15 | 3.00 | 3.23 |
| scarcity_logistic | with exception | 1.38 | 0.77 | 0.81 | 1.00 | 1.42 |
| scarcity_logistic | strict | 0.77 | 0.35 | 0.50 | 0.62 | 0.81 |

Alarms at h = 1 (flags; of them false alarms) by regime:

| row | form | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|---|
| two_part_gbm | base | 28 (2) | 2 (1) | 0 (0) | 0 (0) | 9 (3) |
| two_part_gbm | with exception | 19 (2) | 2 (1) | 0 (0) | 0 (0) | 6 (1) |
| two_part_gbm | strict | 19 (2) | 2 (1) | 0 (0) | 0 (0) | 3 (1) |
| ngboost_laplace | base | 97 (41) | 3 (2) | 0 (0) | 1 (0) | 11 (1) |
| ngboost_laplace | with exception | 27 (8) | 3 (2) | 0 (0) | 1 (0) | 7 (0) |
| ngboost_laplace | strict | 24 (7) | 3 (2) | 0 (0) | 1 (0) | 7 (0) |
| hierarchical_logistic | base | 136 (67) | 2 (2) | 0 (0) | 0 (0) | 26 (11) |
| hierarchical_logistic | with exception | 55 (33) | 2 (2) | 0 (0) | 0 (0) | 11 (3) |
| hierarchical_logistic | strict | 29 (16) | 2 (2) | 0 (0) | 0 (0) | 8 (3) |
| settlement_quantile_timing | base | 96 (36) | 23 (22) | 5 (5) | 3 (2) | 26 (11) |
| settlement_quantile_timing | with exception | 34 (7) | 21 (20) | 5 (5) | 2 (2) | 8 (3) |
| settlement_quantile_timing | strict | 31 (7) | 20 (19) | 5 (5) | 2 (2) | 8 (3) |
| scarcity_logistic_interactions | base | 137 (70) | 1 (1) | 0 (0) | 0 (0) | 26 (12) |
| scarcity_logistic_interactions | with exception | 59 (35) | 1 (1) | 0 (0) | 0 (0) | 11 (4) |
| scarcity_logistic_interactions | strict | 33 (18) | 1 (1) | 0 (0) | 0 (0) | 8 (4) |
| scarcity_logistic | base | 125 (61) | 2 (2) | 0 (0) | 0 (0) | 25 (11) |
| scarcity_logistic | with exception | 53 (32) | 2 (2) | 0 (0) | 0 (0) | 10 (2) |
| scarcity_logistic | strict | 29 (16) | 2 (2) | 0 (0) | 0 (0) | 7 (2) |

Alarms at h = 1 (flags; of them false alarms) by pressure-day type:

| row | form | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|---|
| two_part_gbm | base | 10 (2) | 20 (4) | 4 (0) | 5 (0) |
| two_part_gbm | with exception | 10 (2) | 9 (2) | 3 (0) | 5 (0) |
| two_part_gbm | strict | 9 (2) | 8 (2) | 2 (0) | 5 (0) |
| ngboost_laplace | base | 15 (5) | 83 (37) | 6 (0) | 8 (2) |
| ngboost_laplace | with exception | 9 (2) | 22 (8) | 3 (0) | 4 (0) |
| ngboost_laplace | strict | 9 (2) | 20 (7) | 2 (0) | 4 (0) |
| hierarchical_logistic | base | 17 (5) | 125 (67) | 7 (2) | 15 (6) |
| hierarchical_logistic | with exception | 8 (3) | 48 (31) | 6 (2) | 6 (2) |
| hierarchical_logistic | strict | 2 (1) | 29 (18) | 5 (2) | 3 (0) |
| settlement_quantile_timing | base | 19 (8) | 107 (56) | 17 (10) | 10 (2) |
| settlement_quantile_timing | with exception | 15 (7) | 36 (19) | 14 (10) | 5 (1) |
| settlement_quantile_timing | strict | 15 (7) | 32 (18) | 14 (10) | 5 (1) |
| scarcity_logistic_interactions | base | 17 (4) | 127 (72) | 5 (1) | 15 (6) |
| scarcity_logistic_interactions | with exception | 9 (3) | 52 (34) | 4 (1) | 6 (2) |
| scarcity_logistic_interactions | strict | 3 (1) | 33 (21) | 3 (1) | 3 (0) |
| scarcity_logistic | base | 16 (4) | 114 (62) | 7 (2) | 15 (6) |
| scarcity_logistic | with exception | 9 (3) | 44 (29) | 6 (2) | 6 (2) |
| scarcity_logistic | strict | 3 (1) | 27 (17) | 5 (2) | 3 (0) |
