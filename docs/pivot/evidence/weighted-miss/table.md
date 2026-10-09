Scored days 2018-06-29 to 2025-12-31; tier 1 at lead >= 1, +5 bp, limit 2 per onset; h = 1 to 5.

Table 1. Each candidate under the unweighted rule (the current bar) and the weighted rule (the draft). False alarms per onset are the worst horizon's. 'flat' counts every false alarm as 1, 'weighted' by its distance to a pressure day. Each rule chooses its own flag cut-offs.

| candidate | onsets | warned, unweighted rule | warned, weighted rule | FA/onset, unweighted rule (flat / weighted) | FA/onset, weighted rule (flat / weighted) | tier 1, unweighted | tier 1, weighted | tier 3 (unw. / w.) | tier 5 (unw. / w.) |
|---|---|---|---|---|---|---|---|---|---|
| balance_sheet_hierarchical_logistic | 26 | 12 | 15 | 2.15 / 0.84 | 5.08 / 2.24 | fail | fail | fail / fail | pass / pass |
| balance_sheet_scarcity_gbm | 26 | 10 | 13 | 2.15 / 0.77 | 5.27 / 2.35 | fail | fail | fail / fail | pass / pass |
| base_adaptive_offset | 26 | 4 | 5 | 0.85 / 0.41 | 1.19 / 0.56 | fail | fail | fail / fail | pass / pass |
| base_online_platt | 26 | 3 | 4 | 0.77 / 0.38 | 0.85 / 0.39 | fail | fail | fail / fail | pass / pass |
| calendar_climatology | 26 | 10 | 12 | 5.00 / 2.80 | 6.69 / 3.75 | fail | fail | fail / fail | fail / fail |
| extreme_value_tail | 26 | 9 | 11 | 2.31 / 0.75 | 5.04 / 2.23 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic | 26 | 15 | 15 | 3.65 / 1.31 | 6.23 / 2.91 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_fed_repo | 26 | 14 | 15 | 3.73 / 1.56 | 5.65 / 2.68 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_fed_repo_sameday | 26 | 15 | 15 | 3.85 / 1.58 | 5.92 / 2.81 | fail | fail | fail / fail | pass / pass |
| hierarchical_logistic_net | 26 | 14 | 15 | 3.38 / 1.27 | 5.46 / 2.51 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_srf | 26 | 15 | 15 | 3.81 / 1.54 | 5.65 / 2.69 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_srf_sameday | 26 | 15 | 15 | 4.08 / 1.75 | 5.69 / 2.72 | fail | fail | fail / fail | fail / fail |
| onset_gbm_class_weight+recalibrated | 26 | 8 | 9 | 3.42 / 1.82 | 4.65 / 2.74 | fail | fail | fail / fail | pass / pass |
| onset_gbm_class_weight_funding+recalibrated | 26 | 8 | 9 | 3.38 / 1.78 | 4.62 / 2.73 | fail | fail | fail / fail | pass / pass |
| onset_gbm_focal+recalibrated | 26 | 10 | 13 | 2.85 / 1.68 | 4.58 / 2.56 | fail | fail | fail / fail | pass / pass |
| onset_logistic+recalibrated | 26 | 11 | 14 | 3.54 / 1.80 | 5.77 / 3.28 | fail | fail | fail / fail | fail / fail |
| onset_logistic_class_weight+recalibrated | 26 | 6 | 10 | 0.81 / 0.30 | 2.92 / 1.58 | fail | fail | fail / fail | pass / pass |
| onset_logistic_class_weight_funding+recalibrated | 26 | 5 | 11 | 0.77 / 0.29 | 2.85 / 1.57 | fail | fail | fail / fail | pass / pass |
| onset_logistic_net+recalibrated | 26 | 11 | 13 | 2.81 / 1.40 | 5.27 / 2.84 | fail | fail | fail / fail | pass / pass |
| onset_logistic_policy+recalibrated | 26 | 15 | 17 | 3.23 / 1.53 | 6.12 / 3.21 | fail | fail | fail / fail | fail / fail |
| persistence_logistic | 26 | 7 | 12 | 3.42 / 1.17 | 7.04 / 3.25 | fail | fail | fail / fail | fail / fail |
| published_v1 | 26 | 2 | 14 | 2.35 / 0.79 | 5.73 / 2.38 | fail | fail | fail / fail | fail / fail |
| published_v1_blend_equal | 26 | 3 | 13 | 2.27 / 0.89 | 5.73 / 2.38 | fail | fail | fail / fail | fail / fail |
| published_v1_calendar_switch | 26 | 8 | 15 | 2.92 / 1.01 | 5.73 / 2.38 | fail | fail | fail / fail | fail / fail |
| published_v1_nowcast | 26 | 4 | 13 | 2.38 / 0.83 | 5.46 / 2.28 | fail | fail | fail / fail | fail / fail |
| published_v1_nowcast_substituted | 26 | 6 | 10 | 2.96 / 1.24 | 5.96 / 2.90 | fail | fail | fail / fail | fail / fail |
| published_v1_predicted_turn_switch | 26 | 5 | 15 | 2.88 / 1.00 | 5.73 / 2.38 | fail | fail | fail / fail | fail / fail |
| rare_gbm_balanced_bootstrap+recalibrated | 26 | 7 | 7 | 1.19 / 0.53 | 2.19 / 0.85 | fail | fail | fail / fail | pass / pass |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 26 | 6 | 12 | 1.65 / 0.72 | 2.92 / 1.37 | fail | fail | fail / fail | pass / pass |
| rare_gbm_class_weight+recalibrated | 26 | 6 | 12 | 1.46 / 0.63 | 5.12 / 2.16 | fail | fail | fail / fail | pass / pass |
| rare_gbm_focal+recalibrated | 26 | 7 | 13 | 1.58 / 0.64 | 4.15 / 1.66 | fail | pass | fail / fail | pass / pass |
| rare_logistic_balanced_bootstrap+recalibrated | 26 | 3 | 4 | 0.65 / 0.35 | 0.96 / 0.42 | fail | fail | fail / fail | pass / pass |
| rare_logistic_class_weight+recalibrated | 26 | 3 | 5 | 0.77 / 0.38 | 0.96 / 0.42 | fail | fail | fail / fail | pass / pass |
| recal_isotonic | 26 | 3 | 13 | 2.42 / 0.85 | 5.69 / 2.42 | fail | fail | fail / fail | fail / fail |
| recal_platt | 26 | 2 | 14 | 2.35 / 0.79 | 5.73 / 2.38 | fail | fail | fail / fail | fail / fail |
| recal_platt_group | 26 | 5 | 15 | 2.77 / 0.93 | 5.62 / 2.35 | fail | fail | fail / fail | fail / fail |
| recal_platt_weighted | 26 | 5 | 14 | 2.77 / 0.93 | 5.92 / 2.61 | fail | fail | fail / fail | fail / fail |
| recency_decay_126+recalibrated | 26 | 4 | 4 | 0.35 / 0.09 | 0.88 / 0.29 | fail | fail | fail / fail | pass / pass |
| recency_decay_252+recalibrated | 26 | 4 | 4 | 0.54 / 0.19 | 1.08 / 0.38 | fail | fail | fail / fail | pass / pass |
| recency_decay_63+recalibrated | 26 | 3 | 4 | 0.38 / 0.12 | 0.58 / 0.22 | fail | fail | fail / fail | pass / pass |
| recency_window_252+recalibrated | 26 | 3 | 6 | 0.77 / 0.38 | 1.35 / 0.56 | fail | fail | fail / fail | pass / pass |
| recency_window_504+recalibrated | 26 | 3 | 6 | 0.81 / 0.38 | 1.62 / 0.62 | fail | fail | fail / fail | pass / pass |
| risk_gbm | 26 | 13 | 13 | 1.35 / 0.76 | 1.38 / 0.80 | pass | pass | fail / fail | fail / fail |
| risk_gbm_base | 26 | 14 | 14 | 1.50 / 0.97 | 1.50 / 0.97 | pass | pass | fail / fail | fail / fail |
| risk_logistic | 26 | 14 | 16 | 1.85 / 1.19 | 2.42 / 1.74 | pass | pass | fail / fail | fail / fail |
| risk_logistic_base | 26 | 13 | 15 | 1.77 / 1.16 | 2.31 / 1.65 | pass | pass | fail / fail | fail / fail |
| risk_quantile_skewt | 26 | 13 | 14 | 2.54 / 1.96 | 3.42 / 2.85 | fail | fail | fail / fail | fail / fail |
| risk_quantile_skewt_base | 26 | 14 | 15 | 1.88 / 1.25 | 2.31 / 1.62 | pass | pass | fail / fail | fail / fail |
| scarcity_gbm | 26 | 10 | 13 | 2.65 / 1.20 | 5.08 / 2.36 | fail | fail | fail / fail | fail / fail |
| scarcity_gbm_interactions | 26 | 10 | 13 | 2.65 / 1.20 | 5.08 / 2.36 | fail | fail | fail / fail | fail / fail |
| scarcity_logistic | 26 | 13 | 13 | 3.23 / 1.23 | 4.73 / 2.09 | fail | fail | fail / fail | fail / fail |
| scarcity_logistic_interactions | 26 | 14 | 14 | 3.23 / 1.23 | 5.50 / 2.39 | fail | fail | fail / fail | fail / fail |
| scarcity_logistic_regime_pooled | 26 | 13 | 13 | 3.23 / 1.22 | 5.19 / 2.54 | fail | fail | fail / fail | fail / fail |
| settlement_probit_scarcity | 26 | 8 | 11 | 1.58 / 0.57 | 3.42 / 1.48 | fail | fail | fail / fail | fail / fail |
| settlement_probit_tga | 26 | 9 | 11 | 1.73 / 0.70 | 2.81 / 1.19 | fail | fail | fail / fail | fail / fail |
| settlement_probit_timing | 26 | 13 | 16 | 3.46 / 1.97 | 5.42 / 3.11 | fail | fail | fail / fail | pass / pass |
| settlement_quantile_scarcity | 26 | 10 | 12 | 2.38 / 0.87 | 4.54 / 2.04 | fail | fail | fail / fail | pass / pass |
| settlement_quantile_tga | 26 | 9 | 12 | 2.27 / 1.09 | 4.88 / 2.57 | fail | fail | fail / fail | pass / pass |
| settlement_quantile_timing | 26 | 15 | 16 | 3.65 / 1.68 | 6.38 / 3.41 | fail | fail | fail / fail | pass / pass |
| stack_equal_average | 26 | 12 | 16 | 3.23 / 1.32 | 5.04 / 2.21 | fail | fail | fail / fail | fail / fail |
| stacked_ensemble | 26 | 15 | 16 | 3.27 / 1.23 | 5.42 / 2.31 | fail | fail | fail / fail | fail / fail |
| time_to_pressure_hazard | 26 | 7 | 9 | 2.19 / 0.75 | 3.77 / 1.58 | fail | fail | fail / fail | fail / fail |
| two_part_gbm | 26 | 15 | 15 | 2.46 / 1.07 | 4.81 / 2.55 | fail | fail | fail / fail | fail / fail |
| two_part_logistic | 26 | 10 | 14 | 2.00 / 0.73 | 3.96 / 1.68 | fail | pass | fail / fail | fail / fail |

Table 2. The same split by regime: onsets, onsets warned, and the worst horizon's false alarms (flat / weighted count), per candidate under each rule.

| candidate | rule | regime | onsets | warned | false alarms (flat / weighted) |
|---|---|---|---|---|---|
| balance_sheet_hierarchical_logistic | unweighted | 2018-19 | 17 | 9 | 39 / 15.25 |
| balance_sheet_hierarchical_logistic | unweighted | 2020 | 2 | 0 | 3 / 2.25 |
| balance_sheet_hierarchical_logistic | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| balance_sheet_hierarchical_logistic | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| balance_sheet_hierarchical_logistic | unweighted | 2025-26 | 5 | 3 | 19 / 6.50 |
| balance_sheet_hierarchical_logistic | weighted | 2018-19 | 17 | 12 | 102 / 45.75 |
| balance_sheet_hierarchical_logistic | weighted | 2020 | 2 | 0 | 7 / 5.00 |
| balance_sheet_hierarchical_logistic | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| balance_sheet_hierarchical_logistic | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| balance_sheet_hierarchical_logistic | weighted | 2025-26 | 5 | 3 | 23 / 7.50 |
| balance_sheet_scarcity_gbm | unweighted | 2018-19 | 17 | 7 | 49 / 17.75 |
| balance_sheet_scarcity_gbm | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| balance_sheet_scarcity_gbm | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| balance_sheet_scarcity_gbm | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| balance_sheet_scarcity_gbm | unweighted | 2025-26 | 5 | 3 | 10 / 5.00 |
| balance_sheet_scarcity_gbm | weighted | 2018-19 | 17 | 10 | 115 / 49.25 |
| balance_sheet_scarcity_gbm | weighted | 2020 | 2 | 0 | 8 / 6.00 |
| balance_sheet_scarcity_gbm | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| balance_sheet_scarcity_gbm | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| balance_sheet_scarcity_gbm | weighted | 2025-26 | 5 | 3 | 14 / 5.75 |
| base_adaptive_offset | unweighted | 2018-19 | 17 | 3 | 20 / 9.75 |
| base_adaptive_offset | unweighted | 2020 | 2 | 0 | 1 / 0.25 |
| base_adaptive_offset | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| base_adaptive_offset | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| base_adaptive_offset | unweighted | 2025-26 | 5 | 1 | 3 / 1.00 |
| base_adaptive_offset | weighted | 2018-19 | 17 | 4 | 27 / 12.75 |
| base_adaptive_offset | weighted | 2020 | 2 | 0 | 2 / 1.25 |
| base_adaptive_offset | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| base_adaptive_offset | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| base_adaptive_offset | weighted | 2025-26 | 5 | 1 | 4 / 1.75 |
| base_online_platt | unweighted | 2018-19 | 17 | 3 | 20 / 9.75 |
| base_online_platt | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| base_online_platt | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| base_online_platt | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| base_online_platt | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| base_online_platt | weighted | 2018-19 | 17 | 4 | 22 / 10.25 |
| base_online_platt | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| base_online_platt | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| base_online_platt | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| base_online_platt | weighted | 2025-26 | 5 | 0 | 2 / 0.50 |
| calendar_climatology | unweighted | 2018-19 | 17 | 10 | 96 / 39.75 |
| calendar_climatology | unweighted | 2020 | 2 | 0 | 21 / 20.00 |
| calendar_climatology | unweighted | 2021-23 | 0 | 0 | 13 / 13.00 |
| calendar_climatology | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| calendar_climatology | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| calendar_climatology | weighted | 2018-19 | 17 | 12 | 132 / 56.50 |
| calendar_climatology | weighted | 2020 | 2 | 0 | 28 / 27.00 |
| calendar_climatology | weighted | 2021-23 | 0 | 0 | 14 / 14.00 |
| calendar_climatology | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| calendar_climatology | weighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| extreme_value_tail | unweighted | 2018-19 | 17 | 9 | 59 / 18.50 |
| extreme_value_tail | unweighted | 2020 | 2 | 0 | 1 / 1.00 |
| extreme_value_tail | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| extreme_value_tail | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| extreme_value_tail | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| extreme_value_tail | weighted | 2018-19 | 17 | 11 | 123 / 53.00 |
| extreme_value_tail | weighted | 2020 | 2 | 0 | 6 / 4.50 |
| extreme_value_tail | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| extreme_value_tail | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| extreme_value_tail | weighted | 2025-26 | 5 | 0 | 2 / 1.00 |
| hierarchical_logistic | unweighted | 2018-19 | 17 | 12 | 91 / 32.50 |
| hierarchical_logistic | unweighted | 2020 | 2 | 0 | 2 / 1.25 |
| hierarchical_logistic | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic | unweighted | 2025-26 | 5 | 3 | 11 / 3.25 |
| hierarchical_logistic | weighted | 2018-19 | 17 | 12 | 146 / 64.75 |
| hierarchical_logistic | weighted | 2020 | 2 | 0 | 15 / 11.50 |
| hierarchical_logistic | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic | weighted | 2025-26 | 5 | 3 | 13 / 3.75 |
| hierarchical_logistic_fed_repo | unweighted | 2018-19 | 17 | 11 | 93 / 38.50 |
| hierarchical_logistic_fed_repo | unweighted | 2020 | 2 | 0 | 2 / 1.25 |
| hierarchical_logistic_fed_repo | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | unweighted | 2025-26 | 5 | 3 | 11 / 3.50 |
| hierarchical_logistic_fed_repo | weighted | 2018-19 | 17 | 12 | 131 / 59.75 |
| hierarchical_logistic_fed_repo | weighted | 2020 | 2 | 0 | 7 / 7.00 |
| hierarchical_logistic_fed_repo | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | weighted | 2025-26 | 5 | 3 | 14 / 4.50 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2018-19 | 17 | 12 | 92 / 38.50 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2020 | 2 | 0 | 2 / 0.50 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2025-26 | 5 | 3 | 14 / 4.50 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2018-19 | 17 | 12 | 131 / 60.00 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2020 | 2 | 0 | 9 / 7.75 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2025-26 | 5 | 3 | 16 / 5.25 |
| hierarchical_logistic_net | unweighted | 2018-19 | 17 | 11 | 75 / 27.75 |
| hierarchical_logistic_net | unweighted | 2020 | 2 | 0 | 4 / 4.00 |
| hierarchical_logistic_net | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_net | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_net | unweighted | 2025-26 | 5 | 3 | 10 / 3.00 |
| hierarchical_logistic_net | weighted | 2018-19 | 17 | 12 | 126 / 54.00 |
| hierarchical_logistic_net | weighted | 2020 | 2 | 0 | 10 / 9.50 |
| hierarchical_logistic_net | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_net | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_net | weighted | 2025-26 | 5 | 3 | 10 / 3.00 |
| hierarchical_logistic_srf | unweighted | 2018-19 | 17 | 12 | 97 / 39.50 |
| hierarchical_logistic_srf | unweighted | 2020 | 2 | 0 | 1 / 0.25 |
| hierarchical_logistic_srf | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | unweighted | 2025-26 | 5 | 3 | 11 / 3.25 |
| hierarchical_logistic_srf | weighted | 2018-19 | 17 | 12 | 131 / 59.75 |
| hierarchical_logistic_srf | weighted | 2020 | 2 | 0 | 7 / 7.00 |
| hierarchical_logistic_srf | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | weighted | 2025-26 | 5 | 3 | 11 / 3.25 |
| hierarchical_logistic_srf_sameday | unweighted | 2018-19 | 17 | 12 | 97 / 40.50 |
| hierarchical_logistic_srf_sameday | unweighted | 2020 | 2 | 0 | 3 / 3.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2025-26 | 5 | 3 | 7 / 2.00 |
| hierarchical_logistic_srf_sameday | weighted | 2018-19 | 17 | 12 | 132 / 60.50 |
| hierarchical_logistic_srf_sameday | weighted | 2020 | 2 | 0 | 7 / 7.00 |
| hierarchical_logistic_srf_sameday | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | weighted | 2025-26 | 5 | 3 | 9 / 3.25 |
| onset_gbm_class_weight+recalibrated | unweighted | 2018-19 | 17 | 8 | 73 / 33.25 |
| onset_gbm_class_weight+recalibrated | unweighted | 2020 | 2 | 0 | 15 / 14.50 |
| onset_gbm_class_weight+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| onset_gbm_class_weight+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_gbm_class_weight+recalibrated | unweighted | 2025-26 | 5 | 0 | 4 / 2.50 |
| onset_gbm_class_weight+recalibrated | weighted | 2018-19 | 17 | 9 | 92 / 42.00 |
| onset_gbm_class_weight+recalibrated | weighted | 2020 | 2 | 0 | 30 / 28.75 |
| onset_gbm_class_weight+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| onset_gbm_class_weight+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_gbm_class_weight+recalibrated | weighted | 2025-26 | 5 | 0 | 4 / 2.50 |
| onset_gbm_class_weight_funding+recalibrated | unweighted | 2018-19 | 17 | 8 | 73 / 33.25 |
| onset_gbm_class_weight_funding+recalibrated | unweighted | 2020 | 2 | 0 | 15 / 14.50 |
| onset_gbm_class_weight_funding+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| onset_gbm_class_weight_funding+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_gbm_class_weight_funding+recalibrated | unweighted | 2025-26 | 5 | 0 | 3 / 1.50 |
| onset_gbm_class_weight_funding+recalibrated | weighted | 2018-19 | 17 | 9 | 92 / 42.00 |
| onset_gbm_class_weight_funding+recalibrated | weighted | 2020 | 2 | 0 | 30 / 28.75 |
| onset_gbm_class_weight_funding+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| onset_gbm_class_weight_funding+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_gbm_class_weight_funding+recalibrated | weighted | 2025-26 | 5 | 0 | 3 / 1.50 |
| onset_gbm_focal+recalibrated | unweighted | 2018-19 | 17 | 9 | 51 / 24.75 |
| onset_gbm_focal+recalibrated | unweighted | 2020 | 2 | 0 | 22 / 20.75 |
| onset_gbm_focal+recalibrated | unweighted | 2021-23 | 0 | 0 | 1 / 1.00 |
| onset_gbm_focal+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_gbm_focal+recalibrated | unweighted | 2025-26 | 5 | 1 | 1 / 1.00 |
| onset_gbm_focal+recalibrated | weighted | 2018-19 | 17 | 11 | 90 / 40.75 |
| onset_gbm_focal+recalibrated | weighted | 2020 | 2 | 1 | 27 / 25.25 |
| onset_gbm_focal+recalibrated | weighted | 2021-23 | 0 | 0 | 1 / 1.00 |
| onset_gbm_focal+recalibrated | weighted | 2024 | 2 | 0 | 1 / 1.00 |
| onset_gbm_focal+recalibrated | weighted | 2025-26 | 5 | 1 | 1 / 1.00 |
| onset_logistic+recalibrated | unweighted | 2018-19 | 17 | 10 | 85 / 40.50 |
| onset_logistic+recalibrated | unweighted | 2020 | 2 | 0 | 9 / 8.00 |
| onset_logistic+recalibrated | unweighted | 2021-23 | 0 | 0 | 1 / 1.00 |
| onset_logistic+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic+recalibrated | unweighted | 2025-26 | 5 | 1 | 1 / 1.00 |
| onset_logistic+recalibrated | weighted | 2018-19 | 17 | 12 | 114 / 51.75 |
| onset_logistic+recalibrated | weighted | 2020 | 2 | 0 | 33 / 31.25 |
| onset_logistic+recalibrated | weighted | 2021-23 | 0 | 0 | 1 / 1.00 |
| onset_logistic+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic+recalibrated | weighted | 2025-26 | 5 | 2 | 2 / 1.25 |
| onset_logistic_class_weight+recalibrated | unweighted | 2018-19 | 17 | 4 | 17 / 6.50 |
| onset_logistic_class_weight+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| onset_logistic_class_weight+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| onset_logistic_class_weight+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_class_weight+recalibrated | unweighted | 2025-26 | 5 | 2 | 4 / 1.25 |
| onset_logistic_class_weight+recalibrated | weighted | 2018-19 | 17 | 8 | 65 / 34.25 |
| onset_logistic_class_weight+recalibrated | weighted | 2020 | 2 | 0 | 2 / 2.00 |
| onset_logistic_class_weight+recalibrated | weighted | 2021-23 | 0 | 0 | 1 / 1.00 |
| onset_logistic_class_weight+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_class_weight+recalibrated | weighted | 2025-26 | 5 | 2 | 8 / 3.75 |
| onset_logistic_class_weight_funding+recalibrated | unweighted | 2018-19 | 17 | 4 | 17 / 6.50 |
| onset_logistic_class_weight_funding+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| onset_logistic_class_weight_funding+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| onset_logistic_class_weight_funding+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_class_weight_funding+recalibrated | unweighted | 2025-26 | 5 | 1 | 3 / 1.00 |
| onset_logistic_class_weight_funding+recalibrated | weighted | 2018-19 | 17 | 8 | 65 / 34.25 |
| onset_logistic_class_weight_funding+recalibrated | weighted | 2020 | 2 | 0 | 2 / 2.00 |
| onset_logistic_class_weight_funding+recalibrated | weighted | 2021-23 | 0 | 0 | 1 / 1.00 |
| onset_logistic_class_weight_funding+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_class_weight_funding+recalibrated | weighted | 2025-26 | 5 | 3 | 12 / 3.75 |
| onset_logistic_net+recalibrated | unweighted | 2018-19 | 17 | 10 | 62 / 27.75 |
| onset_logistic_net+recalibrated | unweighted | 2020 | 2 | 0 | 16 / 14.75 |
| onset_logistic_net+recalibrated | unweighted | 2021-23 | 0 | 0 | 2 / 2.00 |
| onset_logistic_net+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_net+recalibrated | unweighted | 2025-26 | 5 | 1 | 1 / 1.00 |
| onset_logistic_net+recalibrated | weighted | 2018-19 | 17 | 12 | 115 / 54.00 |
| onset_logistic_net+recalibrated | weighted | 2020 | 2 | 0 | 30 / 28.75 |
| onset_logistic_net+recalibrated | weighted | 2021-23 | 0 | 0 | 3 / 3.00 |
| onset_logistic_net+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_net+recalibrated | weighted | 2025-26 | 5 | 1 | 2 / 1.00 |
| onset_logistic_policy+recalibrated | unweighted | 2018-19 | 17 | 12 | 63 / 24.25 |
| onset_logistic_policy+recalibrated | unweighted | 2020 | 2 | 1 | 11 / 9.75 |
| onset_logistic_policy+recalibrated | unweighted | 2021-23 | 0 | 0 | 3 / 3.00 |
| onset_logistic_policy+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_policy+recalibrated | unweighted | 2025-26 | 5 | 2 | 7 / 2.75 |
| onset_logistic_policy+recalibrated | weighted | 2018-19 | 17 | 13 | 131 / 59.50 |
| onset_logistic_policy+recalibrated | weighted | 2020 | 2 | 1 | 24 / 22.25 |
| onset_logistic_policy+recalibrated | weighted | 2021-23 | 0 | 0 | 4 / 4.00 |
| onset_logistic_policy+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| onset_logistic_policy+recalibrated | weighted | 2025-26 | 5 | 3 | 8 / 3.00 |
| persistence_logistic | unweighted | 2018-19 | 17 | 7 | 72 / 24.75 |
| persistence_logistic | unweighted | 2020 | 2 | 0 | 4 / 1.50 |
| persistence_logistic | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| persistence_logistic | unweighted | 2024 | 2 | 0 | 2 / 1.00 |
| persistence_logistic | unweighted | 2025-26 | 5 | 0 | 15 / 5.50 |
| persistence_logistic | weighted | 2018-19 | 17 | 11 | 139 / 60.25 |
| persistence_logistic | weighted | 2020 | 2 | 1 | 23 / 18.75 |
| persistence_logistic | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| persistence_logistic | weighted | 2024 | 2 | 0 | 3 / 1.00 |
| persistence_logistic | weighted | 2025-26 | 5 | 0 | 18 / 6.50 |
| published_v1 | unweighted | 2018-19 | 17 | 2 | 49 / 17.00 |
| published_v1 | unweighted | 2020 | 2 | 0 | 2 / 0.50 |
| published_v1 | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1 | unweighted | 2024 | 2 | 0 | 1 / 0.50 |
| published_v1 | unweighted | 2025-26 | 5 | 0 | 13 / 4.25 |
| published_v1 | weighted | 2018-19 | 17 | 12 | 125 / 53.75 |
| published_v1 | weighted | 2020 | 2 | 0 | 3 / 2.00 |
| published_v1 | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1 | weighted | 2024 | 2 | 0 | 3 / 1.00 |
| published_v1 | weighted | 2025-26 | 5 | 2 | 22 / 7.00 |
| published_v1_blend_equal | unweighted | 2018-19 | 17 | 3 | 55 / 22.00 |
| published_v1_blend_equal | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| published_v1_blend_equal | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_blend_equal | unweighted | 2024 | 2 | 0 | 1 / 0.50 |
| published_v1_blend_equal | unweighted | 2025-26 | 5 | 0 | 13 / 4.25 |
| published_v1_blend_equal | weighted | 2018-19 | 17 | 11 | 125 / 53.75 |
| published_v1_blend_equal | weighted | 2020 | 2 | 0 | 3 / 2.00 |
| published_v1_blend_equal | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_blend_equal | weighted | 2024 | 2 | 0 | 1 / 1.00 |
| published_v1_blend_equal | weighted | 2025-26 | 5 | 2 | 21 / 7.00 |
| published_v1_calendar_switch | unweighted | 2018-19 | 17 | 7 | 63 / 22.50 |
| published_v1_calendar_switch | unweighted | 2020 | 2 | 0 | 2 / 0.50 |
| published_v1_calendar_switch | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_calendar_switch | unweighted | 2024 | 2 | 0 | 1 / 0.50 |
| published_v1_calendar_switch | unweighted | 2025-26 | 5 | 1 | 13 / 4.25 |
| published_v1_calendar_switch | weighted | 2018-19 | 17 | 13 | 125 / 53.75 |
| published_v1_calendar_switch | weighted | 2020 | 2 | 0 | 4 / 2.50 |
| published_v1_calendar_switch | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_calendar_switch | weighted | 2024 | 2 | 0 | 2 / 1.00 |
| published_v1_calendar_switch | weighted | 2025-26 | 5 | 2 | 21 / 7.00 |
| published_v1_nowcast | unweighted | 2018-19 | 17 | 4 | 54 / 18.75 |
| published_v1_nowcast | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| published_v1_nowcast | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_nowcast | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| published_v1_nowcast | unweighted | 2025-26 | 5 | 0 | 13 / 4.25 |
| published_v1_nowcast | weighted | 2018-19 | 17 | 10 | 117 / 50.75 |
| published_v1_nowcast | weighted | 2020 | 2 | 1 | 3 / 1.50 |
| published_v1_nowcast | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_nowcast | weighted | 2024 | 2 | 0 | 3 / 1.00 |
| published_v1_nowcast | weighted | 2025-26 | 5 | 2 | 21 / 6.75 |
| published_v1_nowcast_substituted | unweighted | 2018-19 | 17 | 6 | 68 / 29.00 |
| published_v1_nowcast_substituted | unweighted | 2020 | 2 | 0 | 5 / 5.00 |
| published_v1_nowcast_substituted | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_nowcast_substituted | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| published_v1_nowcast_substituted | unweighted | 2025-26 | 5 | 0 | 9 / 3.25 |
| published_v1_nowcast_substituted | weighted | 2018-19 | 17 | 10 | 129 / 57.00 |
| published_v1_nowcast_substituted | weighted | 2020 | 2 | 0 | 16 / 14.50 |
| published_v1_nowcast_substituted | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_nowcast_substituted | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| published_v1_nowcast_substituted | weighted | 2025-26 | 5 | 0 | 11 / 4.00 |
| published_v1_predicted_turn_switch | unweighted | 2018-19 | 17 | 5 | 63 / 22.50 |
| published_v1_predicted_turn_switch | unweighted | 2020 | 2 | 0 | 2 / 0.50 |
| published_v1_predicted_turn_switch | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_predicted_turn_switch | unweighted | 2024 | 2 | 0 | 1 / 0.50 |
| published_v1_predicted_turn_switch | unweighted | 2025-26 | 5 | 0 | 13 / 4.25 |
| published_v1_predicted_turn_switch | weighted | 2018-19 | 17 | 13 | 125 / 53.75 |
| published_v1_predicted_turn_switch | weighted | 2020 | 2 | 0 | 4 / 2.00 |
| published_v1_predicted_turn_switch | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| published_v1_predicted_turn_switch | weighted | 2024 | 2 | 0 | 3 / 1.00 |
| published_v1_predicted_turn_switch | weighted | 2025-26 | 5 | 2 | 22 / 7.00 |
| rare_gbm_balanced_bootstrap+recalibrated | unweighted | 2018-19 | 17 | 7 | 31 / 13.75 |
| rare_gbm_balanced_bootstrap+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap+recalibrated | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap+recalibrated | weighted | 2018-19 | 17 | 7 | 57 / 22.00 |
| rare_gbm_balanced_bootstrap+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap+recalibrated | weighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | unweighted | 2018-19 | 17 | 6 | 39 / 17.25 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | unweighted | 2025-26 | 5 | 0 | 4 / 1.50 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | weighted | 2018-19 | 17 | 10 | 70 / 33.50 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | weighted | 2025-26 | 5 | 2 | 10 / 4.00 |
| rare_gbm_class_weight+recalibrated | unweighted | 2018-19 | 17 | 6 | 38 / 16.50 |
| rare_gbm_class_weight+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_gbm_class_weight+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_class_weight+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_class_weight+recalibrated | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| rare_gbm_class_weight+recalibrated | weighted | 2018-19 | 17 | 12 | 133 / 56.25 |
| rare_gbm_class_weight+recalibrated | weighted | 2020 | 2 | 0 | 1 / 0.25 |
| rare_gbm_class_weight+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_class_weight+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_class_weight+recalibrated | weighted | 2025-26 | 5 | 0 | 3 / 1.25 |
| rare_gbm_focal+recalibrated | unweighted | 2018-19 | 17 | 7 | 41 / 16.75 |
| rare_gbm_focal+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | weighted | 2018-19 | 17 | 12 | 108 / 43.25 |
| rare_gbm_focal+recalibrated | weighted | 2020 | 2 | 1 | 3 / 1.00 |
| rare_gbm_focal+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | weighted | 2025-26 | 5 | 0 | 2 / 0.75 |
| rare_logistic_balanced_bootstrap+recalibrated | unweighted | 2018-19 | 17 | 3 | 17 / 9.00 |
| rare_logistic_balanced_bootstrap+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_logistic_balanced_bootstrap+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_logistic_balanced_bootstrap+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_logistic_balanced_bootstrap+recalibrated | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| rare_logistic_balanced_bootstrap+recalibrated | weighted | 2018-19 | 17 | 3 | 25 / 11.00 |
| rare_logistic_balanced_bootstrap+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_logistic_balanced_bootstrap+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_logistic_balanced_bootstrap+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_logistic_balanced_bootstrap+recalibrated | weighted | 2025-26 | 5 | 1 | 1 / 0.25 |
| rare_logistic_class_weight+recalibrated | unweighted | 2018-19 | 17 | 3 | 20 / 9.75 |
| rare_logistic_class_weight+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_logistic_class_weight+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_logistic_class_weight+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_logistic_class_weight+recalibrated | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| rare_logistic_class_weight+recalibrated | weighted | 2018-19 | 17 | 4 | 25 / 11.00 |
| rare_logistic_class_weight+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| rare_logistic_class_weight+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| rare_logistic_class_weight+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| rare_logistic_class_weight+recalibrated | weighted | 2025-26 | 5 | 1 | 1 / 0.25 |
| recal_isotonic | unweighted | 2018-19 | 17 | 3 | 57 / 20.00 |
| recal_isotonic | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| recal_isotonic | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_isotonic | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| recal_isotonic | unweighted | 2025-26 | 5 | 0 | 14 / 4.25 |
| recal_isotonic | weighted | 2018-19 | 17 | 11 | 125 / 53.75 |
| recal_isotonic | weighted | 2020 | 2 | 0 | 3 / 2.00 |
| recal_isotonic | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_isotonic | weighted | 2024 | 2 | 0 | 3 / 1.50 |
| recal_isotonic | weighted | 2025-26 | 5 | 2 | 25 / 8.25 |
| recal_platt | unweighted | 2018-19 | 17 | 2 | 49 / 17.00 |
| recal_platt | unweighted | 2020 | 2 | 0 | 2 / 0.50 |
| recal_platt | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_platt | unweighted | 2024 | 2 | 0 | 1 / 0.50 |
| recal_platt | unweighted | 2025-26 | 5 | 0 | 13 / 4.25 |
| recal_platt | weighted | 2018-19 | 17 | 12 | 125 / 53.75 |
| recal_platt | weighted | 2020 | 2 | 0 | 3 / 2.00 |
| recal_platt | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_platt | weighted | 2024 | 2 | 0 | 3 / 1.00 |
| recal_platt | weighted | 2025-26 | 5 | 2 | 22 / 7.00 |
| recal_platt_group | unweighted | 2018-19 | 17 | 3 | 58 / 20.25 |
| recal_platt_group | unweighted | 2020 | 2 | 0 | 2 / 1.00 |
| recal_platt_group | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_platt_group | unweighted | 2024 | 2 | 0 | 1 / 0.50 |
| recal_platt_group | unweighted | 2025-26 | 5 | 2 | 11 / 3.25 |
| recal_platt_group | weighted | 2018-19 | 17 | 12 | 116 / 49.50 |
| recal_platt_group | weighted | 2020 | 2 | 0 | 6 / 5.00 |
| recal_platt_group | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_platt_group | weighted | 2024 | 2 | 0 | 3 / 1.00 |
| recal_platt_group | weighted | 2025-26 | 5 | 3 | 25 / 8.25 |
| recal_platt_weighted | unweighted | 2018-19 | 17 | 4 | 60 / 20.75 |
| recal_platt_weighted | unweighted | 2020 | 2 | 0 | 2 / 0.50 |
| recal_platt_weighted | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_platt_weighted | unweighted | 2024 | 2 | 0 | 1 / 0.50 |
| recal_platt_weighted | unweighted | 2025-26 | 5 | 1 | 13 / 4.25 |
| recal_platt_weighted | weighted | 2018-19 | 17 | 12 | 129 / 56.25 |
| recal_platt_weighted | weighted | 2020 | 2 | 0 | 8 / 6.00 |
| recal_platt_weighted | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recal_platt_weighted | weighted | 2024 | 2 | 0 | 3 / 1.00 |
| recal_platt_weighted | weighted | 2025-26 | 5 | 2 | 22 / 7.00 |
| recency_decay_126+recalibrated | unweighted | 2018-19 | 17 | 3 | 8 / 2.00 |
| recency_decay_126+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_decay_126+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_decay_126+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_decay_126+recalibrated | unweighted | 2025-26 | 5 | 1 | 2 / 1.00 |
| recency_decay_126+recalibrated | weighted | 2018-19 | 17 | 3 | 8 / 2.00 |
| recency_decay_126+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_decay_126+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_decay_126+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_decay_126+recalibrated | weighted | 2025-26 | 5 | 1 | 15 / 5.50 |
| recency_decay_252+recalibrated | unweighted | 2018-19 | 17 | 3 | 11 / 3.75 |
| recency_decay_252+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_decay_252+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_decay_252+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_decay_252+recalibrated | unweighted | 2025-26 | 5 | 1 | 3 / 1.25 |
| recency_decay_252+recalibrated | weighted | 2018-19 | 17 | 3 | 15 / 4.75 |
| recency_decay_252+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_decay_252+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_decay_252+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_decay_252+recalibrated | weighted | 2025-26 | 5 | 1 | 13 / 5.00 |
| recency_decay_63+recalibrated | unweighted | 2018-19 | 17 | 3 | 8 / 2.00 |
| recency_decay_63+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_decay_63+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_decay_63+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_decay_63+recalibrated | unweighted | 2025-26 | 5 | 0 | 3 / 2.25 |
| recency_decay_63+recalibrated | weighted | 2018-19 | 17 | 3 | 8 / 2.00 |
| recency_decay_63+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_decay_63+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_decay_63+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_decay_63+recalibrated | weighted | 2025-26 | 5 | 1 | 7 / 3.75 |
| recency_window_252+recalibrated | unweighted | 2018-19 | 17 | 3 | 20 / 9.75 |
| recency_window_252+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_window_252+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_window_252+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_window_252+recalibrated | unweighted | 2025-26 | 5 | 0 | 1 / 0.25 |
| recency_window_252+recalibrated | weighted | 2018-19 | 17 | 3 | 24 / 10.75 |
| recency_window_252+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_window_252+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_window_252+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_window_252+recalibrated | weighted | 2025-26 | 5 | 3 | 11 / 3.75 |
| recency_window_504+recalibrated | unweighted | 2018-19 | 17 | 3 | 20 / 9.75 |
| recency_window_504+recalibrated | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_window_504+recalibrated | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_window_504+recalibrated | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_window_504+recalibrated | unweighted | 2025-26 | 5 | 0 | 4 / 1.00 |
| recency_window_504+recalibrated | weighted | 2018-19 | 17 | 4 | 25 / 11.00 |
| recency_window_504+recalibrated | weighted | 2020 | 2 | 0 | 0 / 0.00 |
| recency_window_504+recalibrated | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| recency_window_504+recalibrated | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| recency_window_504+recalibrated | weighted | 2025-26 | 5 | 2 | 17 / 5.25 |
| risk_gbm | unweighted | 2018-19 | 17 | 10 | 21 / 9.25 |
| risk_gbm | unweighted | 2020 | 2 | 0 | 11 / 10.00 |
| risk_gbm | unweighted | 2021-23 | 0 | 0 | 1 / 1.00 |
| risk_gbm | unweighted | 2024 | 2 | 0 | 1 / 1.00 |
| risk_gbm | unweighted | 2025-26 | 5 | 3 | 5 / 2.75 |
| risk_gbm | weighted | 2018-19 | 17 | 10 | 21 / 9.25 |
| risk_gbm | weighted | 2020 | 2 | 0 | 13 / 12.00 |
| risk_gbm | weighted | 2021-23 | 0 | 0 | 2 / 2.00 |
| risk_gbm | weighted | 2024 | 2 | 0 | 1 / 1.00 |
| risk_gbm | weighted | 2025-26 | 5 | 3 | 5 / 2.75 |
| risk_gbm_base | unweighted | 2018-19 | 17 | 10 | 21 / 10.00 |
| risk_gbm_base | unweighted | 2020 | 2 | 0 | 15 / 14.00 |
| risk_gbm_base | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_gbm_base | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| risk_gbm_base | unweighted | 2025-26 | 5 | 4 | 3 / 1.50 |
| risk_gbm_base | weighted | 2018-19 | 17 | 10 | 21 / 10.00 |
| risk_gbm_base | weighted | 2020 | 2 | 0 | 18 / 17.00 |
| risk_gbm_base | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_gbm_base | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| risk_gbm_base | weighted | 2025-26 | 5 | 4 | 3 / 1.50 |
| risk_logistic | unweighted | 2018-19 | 17 | 10 | 25 / 12.00 |
| risk_logistic | unweighted | 2020 | 2 | 0 | 19 / 18.00 |
| risk_logistic | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_logistic | unweighted | 2024 | 2 | 0 | 3 / 2.50 |
| risk_logistic | unweighted | 2025-26 | 5 | 4 | 7 / 4.75 |
| risk_logistic | weighted | 2018-19 | 17 | 10 | 25 / 12.00 |
| risk_logistic | weighted | 2020 | 2 | 0 | 30 / 29.00 |
| risk_logistic | weighted | 2021-23 | 0 | 0 | 2 / 2.00 |
| risk_logistic | weighted | 2024 | 2 | 1 | 4 / 3.25 |
| risk_logistic | weighted | 2025-26 | 5 | 5 | 11 / 8.75 |
| risk_logistic_base | unweighted | 2018-19 | 17 | 10 | 25 / 12.00 |
| risk_logistic_base | unweighted | 2020 | 2 | 0 | 17 / 15.75 |
| risk_logistic_base | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_logistic_base | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| risk_logistic_base | unweighted | 2025-26 | 5 | 3 | 4 / 2.50 |
| risk_logistic_base | weighted | 2018-19 | 17 | 10 | 25 / 12.00 |
| risk_logistic_base | weighted | 2020 | 2 | 0 | 30 / 28.25 |
| risk_logistic_base | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_logistic_base | weighted | 2024 | 2 | 0 | 2 / 1.50 |
| risk_logistic_base | weighted | 2025-26 | 5 | 5 | 6 / 3.50 |
| risk_quantile_skewt | unweighted | 2018-19 | 17 | 9 | 21 / 10.50 |
| risk_quantile_skewt | unweighted | 2020 | 2 | 0 | 33 / 31.75 |
| risk_quantile_skewt | unweighted | 2021-23 | 0 | 0 | 14 / 14.00 |
| risk_quantile_skewt | unweighted | 2024 | 2 | 0 | 3 / 2.50 |
| risk_quantile_skewt | unweighted | 2025-26 | 5 | 4 | 9 / 5.25 |
| risk_quantile_skewt | weighted | 2018-19 | 17 | 9 | 21 / 10.50 |
| risk_quantile_skewt | weighted | 2020 | 2 | 0 | 39 / 37.75 |
| risk_quantile_skewt | weighted | 2021-23 | 0 | 0 | 36 / 36.00 |
| risk_quantile_skewt | weighted | 2024 | 2 | 0 | 3 / 2.50 |
| risk_quantile_skewt | weighted | 2025-26 | 5 | 5 | 11 / 7.25 |
| risk_quantile_skewt_base | unweighted | 2018-19 | 17 | 10 | 20 / 7.75 |
| risk_quantile_skewt_base | unweighted | 2020 | 2 | 0 | 24 / 22.75 |
| risk_quantile_skewt_base | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_quantile_skewt_base | unweighted | 2024 | 2 | 0 | 1 / 0.25 |
| risk_quantile_skewt_base | unweighted | 2025-26 | 5 | 4 | 5 / 1.75 |
| risk_quantile_skewt_base | weighted | 2018-19 | 17 | 10 | 20 / 7.75 |
| risk_quantile_skewt_base | weighted | 2020 | 2 | 0 | 32 / 30.75 |
| risk_quantile_skewt_base | weighted | 2021-23 | 0 | 0 | 2 / 2.00 |
| risk_quantile_skewt_base | weighted | 2024 | 2 | 0 | 1 / 0.25 |
| risk_quantile_skewt_base | weighted | 2025-26 | 5 | 5 | 7 / 3.25 |
| scarcity_gbm | unweighted | 2018-19 | 17 | 8 | 61 / 28.75 |
| scarcity_gbm | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| scarcity_gbm | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_gbm | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_gbm | unweighted | 2025-26 | 5 | 2 | 11 / 3.25 |
| scarcity_gbm | weighted | 2018-19 | 17 | 10 | 109 / 44.50 |
| scarcity_gbm | weighted | 2020 | 2 | 0 | 16 / 13.00 |
| scarcity_gbm | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_gbm | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_gbm | weighted | 2025-26 | 5 | 3 | 17 / 5.75 |
| scarcity_gbm_interactions | unweighted | 2018-19 | 17 | 8 | 61 / 28.75 |
| scarcity_gbm_interactions | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| scarcity_gbm_interactions | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_gbm_interactions | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_gbm_interactions | unweighted | 2025-26 | 5 | 2 | 10 / 3.00 |
| scarcity_gbm_interactions | weighted | 2018-19 | 17 | 10 | 109 / 44.50 |
| scarcity_gbm_interactions | weighted | 2020 | 2 | 0 | 16 / 13.00 |
| scarcity_gbm_interactions | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_gbm_interactions | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_gbm_interactions | weighted | 2025-26 | 5 | 3 | 17 / 5.75 |
| scarcity_logistic | unweighted | 2018-19 | 17 | 10 | 80 / 31.50 |
| scarcity_logistic | unweighted | 2020 | 2 | 0 | 2 / 1.50 |
| scarcity_logistic | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_logistic | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_logistic | unweighted | 2025-26 | 5 | 3 | 11 / 3.25 |
| scarcity_logistic | weighted | 2018-19 | 17 | 10 | 111 / 50.00 |
| scarcity_logistic | weighted | 2020 | 2 | 0 | 7 / 7.00 |
| scarcity_logistic | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_logistic | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_logistic | weighted | 2025-26 | 5 | 3 | 11 / 3.25 |
| scarcity_logistic_interactions | unweighted | 2018-19 | 17 | 12 | 80 / 31.50 |
| scarcity_logistic_interactions | unweighted | 2020 | 2 | 0 | 2 / 1.50 |
| scarcity_logistic_interactions | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_logistic_interactions | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_logistic_interactions | unweighted | 2025-26 | 5 | 2 | 12 / 3.50 |
| scarcity_logistic_interactions | weighted | 2018-19 | 17 | 12 | 126 / 54.50 |
| scarcity_logistic_interactions | weighted | 2020 | 2 | 0 | 7 / 7.00 |
| scarcity_logistic_interactions | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_logistic_interactions | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_logistic_interactions | weighted | 2025-26 | 5 | 2 | 12 / 3.50 |
| scarcity_logistic_regime_pooled | unweighted | 2018-19 | 17 | 10 | 80 / 31.00 |
| scarcity_logistic_regime_pooled | unweighted | 2020 | 2 | 0 | 2 / 1.25 |
| scarcity_logistic_regime_pooled | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_logistic_regime_pooled | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_logistic_regime_pooled | unweighted | 2025-26 | 5 | 3 | 12 / 3.50 |
| scarcity_logistic_regime_pooled | weighted | 2018-19 | 17 | 10 | 123 / 56.50 |
| scarcity_logistic_regime_pooled | weighted | 2020 | 2 | 0 | 9 / 8.00 |
| scarcity_logistic_regime_pooled | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| scarcity_logistic_regime_pooled | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| scarcity_logistic_regime_pooled | weighted | 2025-26 | 5 | 3 | 12 / 3.50 |
| settlement_probit_scarcity | unweighted | 2018-19 | 17 | 8 | 41 / 13.75 |
| settlement_probit_scarcity | unweighted | 2020 | 2 | 0 | 2 / 2.00 |
| settlement_probit_scarcity | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_probit_scarcity | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| settlement_probit_scarcity | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| settlement_probit_scarcity | weighted | 2018-19 | 17 | 10 | 89 / 38.50 |
| settlement_probit_scarcity | weighted | 2020 | 2 | 0 | 6 / 4.50 |
| settlement_probit_scarcity | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_probit_scarcity | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| settlement_probit_scarcity | weighted | 2025-26 | 5 | 1 | 2 / 0.50 |
| settlement_probit_tga | unweighted | 2018-19 | 17 | 9 | 42 / 16.00 |
| settlement_probit_tga | unweighted | 2020 | 2 | 0 | 3 / 2.25 |
| settlement_probit_tga | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_probit_tga | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| settlement_probit_tga | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| settlement_probit_tga | weighted | 2018-19 | 17 | 11 | 66 / 26.25 |
| settlement_probit_tga | weighted | 2020 | 2 | 0 | 6 / 4.50 |
| settlement_probit_tga | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_probit_tga | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| settlement_probit_tga | weighted | 2025-26 | 5 | 0 | 1 / 0.25 |
| settlement_probit_timing | unweighted | 2018-19 | 17 | 12 | 57 / 20.75 |
| settlement_probit_timing | unweighted | 2020 | 2 | 0 | 26 / 23.00 |
| settlement_probit_timing | unweighted | 2021-23 | 0 | 0 | 5 / 5.00 |
| settlement_probit_timing | unweighted | 2024 | 2 | 0 | 1 / 1.00 |
| settlement_probit_timing | unweighted | 2025-26 | 5 | 1 | 7 / 3.25 |
| settlement_probit_timing | weighted | 2018-19 | 17 | 13 | 103 / 40.75 |
| settlement_probit_timing | weighted | 2020 | 2 | 1 | 42 / 37.50 |
| settlement_probit_timing | weighted | 2021-23 | 0 | 0 | 7 / 7.00 |
| settlement_probit_timing | weighted | 2024 | 2 | 0 | 1 / 1.00 |
| settlement_probit_timing | weighted | 2025-26 | 5 | 2 | 9 / 3.75 |
| settlement_quantile_scarcity | unweighted | 2018-19 | 17 | 9 | 56 / 19.00 |
| settlement_quantile_scarcity | unweighted | 2020 | 2 | 0 | 5 / 3.50 |
| settlement_quantile_scarcity | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_quantile_scarcity | unweighted | 2024 | 2 | 0 | 1 / 0.25 |
| settlement_quantile_scarcity | unweighted | 2025-26 | 5 | 1 | 6 / 1.75 |
| settlement_quantile_scarcity | weighted | 2018-19 | 17 | 11 | 104 / 47.00 |
| settlement_quantile_scarcity | weighted | 2020 | 2 | 0 | 10 / 7.00 |
| settlement_quantile_scarcity | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_quantile_scarcity | weighted | 2024 | 2 | 0 | 2 / 0.50 |
| settlement_quantile_scarcity | weighted | 2025-26 | 5 | 1 | 13 / 4.00 |
| settlement_quantile_tga | unweighted | 2018-19 | 17 | 9 | 43 / 15.25 |
| settlement_quantile_tga | unweighted | 2020 | 2 | 0 | 13 / 13.00 |
| settlement_quantile_tga | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_quantile_tga | unweighted | 2024 | 2 | 0 | 1 / 0.25 |
| settlement_quantile_tga | unweighted | 2025-26 | 5 | 0 | 5 / 1.50 |
| settlement_quantile_tga | weighted | 2018-19 | 17 | 11 | 103 / 46.25 |
| settlement_quantile_tga | weighted | 2020 | 2 | 0 | 19 / 19.00 |
| settlement_quantile_tga | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| settlement_quantile_tga | weighted | 2024 | 2 | 0 | 2 / 0.50 |
| settlement_quantile_tga | weighted | 2025-26 | 5 | 1 | 9 / 2.25 |
| settlement_quantile_timing | unweighted | 2018-19 | 17 | 14 | 63 / 21.75 |
| settlement_quantile_timing | unweighted | 2020 | 2 | 0 | 22 / 19.00 |
| settlement_quantile_timing | unweighted | 2021-23 | 0 | 0 | 6 / 6.00 |
| settlement_quantile_timing | unweighted | 2024 | 2 | 0 | 2 / 1.00 |
| settlement_quantile_timing | unweighted | 2025-26 | 5 | 1 | 17 / 6.50 |
| settlement_quantile_timing | weighted | 2018-19 | 17 | 14 | 113 / 45.50 |
| settlement_quantile_timing | weighted | 2020 | 2 | 1 | 36 / 31.00 |
| settlement_quantile_timing | weighted | 2021-23 | 0 | 0 | 12 / 12.00 |
| settlement_quantile_timing | weighted | 2024 | 2 | 0 | 3 / 1.50 |
| settlement_quantile_timing | weighted | 2025-26 | 5 | 1 | 18 / 7.25 |
| stack_equal_average | unweighted | 2018-19 | 17 | 12 | 84 / 34.25 |
| stack_equal_average | unweighted | 2020 | 2 | 0 | 0 / 0.00 |
| stack_equal_average | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| stack_equal_average | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| stack_equal_average | unweighted | 2025-26 | 5 | 0 | 1 / 0.25 |
| stack_equal_average | weighted | 2018-19 | 17 | 13 | 121 / 52.75 |
| stack_equal_average | weighted | 2020 | 2 | 0 | 7 / 4.00 |
| stack_equal_average | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| stack_equal_average | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| stack_equal_average | weighted | 2025-26 | 5 | 3 | 3 / 0.75 |
| stacked_ensemble | unweighted | 2018-19 | 17 | 13 | 83 / 32.00 |
| stacked_ensemble | unweighted | 2020 | 2 | 0 | 2 / 1.25 |
| stacked_ensemble | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| stacked_ensemble | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| stacked_ensemble | unweighted | 2025-26 | 5 | 2 | 3 / 0.75 |
| stacked_ensemble | weighted | 2018-19 | 17 | 13 | 125 / 53.00 |
| stacked_ensemble | weighted | 2020 | 2 | 0 | 8 / 8.00 |
| stacked_ensemble | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| stacked_ensemble | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| stacked_ensemble | weighted | 2025-26 | 5 | 3 | 8 / 2.75 |
| time_to_pressure_hazard | unweighted | 2018-19 | 17 | 7 | 56 / 18.50 |
| time_to_pressure_hazard | unweighted | 2020 | 2 | 0 | 1 / 1.00 |
| time_to_pressure_hazard | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| time_to_pressure_hazard | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| time_to_pressure_hazard | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| time_to_pressure_hazard | weighted | 2018-19 | 17 | 9 | 95 / 38.25 |
| time_to_pressure_hazard | weighted | 2020 | 2 | 0 | 5 / 4.25 |
| time_to_pressure_hazard | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| time_to_pressure_hazard | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| time_to_pressure_hazard | weighted | 2025-26 | 5 | 0 | 1 / 0.25 |
| two_part_gbm | unweighted | 2018-19 | 17 | 12 | 60 / 24.50 |
| two_part_gbm | unweighted | 2020 | 2 | 1 | 4 / 3.25 |
| two_part_gbm | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| two_part_gbm | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| two_part_gbm | unweighted | 2025-26 | 5 | 2 | 3 / 1.25 |
| two_part_gbm | weighted | 2018-19 | 17 | 12 | 97 / 40.25 |
| two_part_gbm | weighted | 2020 | 2 | 1 | 28 / 26.00 |
| two_part_gbm | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| two_part_gbm | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| two_part_gbm | weighted | 2025-26 | 5 | 2 | 9 / 3.50 |
| two_part_logistic | unweighted | 2018-19 | 17 | 10 | 49 / 16.75 |
| two_part_logistic | unweighted | 2020 | 2 | 0 | 3 / 2.25 |
| two_part_logistic | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| two_part_logistic | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| two_part_logistic | unweighted | 2025-26 | 5 | 0 | 0 / 0.00 |
| two_part_logistic | weighted | 2018-19 | 17 | 13 | 96 / 39.00 |
| two_part_logistic | weighted | 2020 | 2 | 0 | 6 / 4.50 |
| two_part_logistic | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| two_part_logistic | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| two_part_logistic | weighted | 2025-26 | 5 | 1 | 1 / 0.25 |
