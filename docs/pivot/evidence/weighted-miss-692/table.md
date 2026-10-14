Scored days 2018-06-29 to 2025-12-31; tier 1 at lead >= 1, +5 bp, limit 2 per onset; h = 1 to 5.

Table 1. Each candidate under the unweighted rule (the current bar) and the weighted rule (the draft). False alarms per onset are the worst horizon's. 'flat' counts every false alarm as 1, 'weighted' by its distance to a pressure day. Each rule chooses its own flag cut-offs.

| candidate | onsets | warned, unweighted rule | warned, weighted rule | FA/onset, unweighted rule (flat / weighted) | FA/onset, weighted rule (flat / weighted) | tier 1, unweighted | tier 1, weighted | tier 3 (unw. / w.) | tier 5 (unw. / w.) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 26 | 10 | 12 | 5.00 / 2.80 | 6.69 / 3.75 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic | 26 | 15 | 15 | 3.65 / 1.31 | 6.23 / 2.91 | fail | fail | pass / pass | fail / fail |
| hierarchical_logistic_fed_repo | 26 | 15 | 15 | 4.23 / 1.71 | 6.38 / 2.94 | fail | fail | pass / pass | fail / fail |
| hierarchical_logistic_fed_repo_sameday | 26 | 14 | 16 | 4.38 / 1.68 | 6.50 / 2.99 | fail | fail | pass / pass | fail / fail |
| hierarchical_logistic_srf | 26 | 15 | 15 | 4.08 / 1.48 | 6.38 / 2.94 | fail | fail | pass / pass | fail / fail |
| hierarchical_logistic_srf_sameday | 26 | 15 | 15 | 4.19 / 1.65 | 6.27 / 2.89 | fail | fail | pass / pass | fail / fail |
| persistence_logistic | 26 | 7 | 12 | 3.42 / 1.17 | 7.04 / 3.25 | fail | fail | fail / fail | fail / fail |
| published_v1 | 26 | 2 | 14 | 2.35 / 0.79 | 5.73 / 2.38 | fail | fail | pass / pass | fail / fail |

Table 2. The same split by regime: onsets, onsets warned, and the worst horizon's false alarms (flat / weighted count), per candidate under each rule.

| candidate | rule | regime | onsets | warned | false alarms (flat / weighted) |
|---|---|---|---|---|---|
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
| hierarchical_logistic_fed_repo | unweighted | 2018-19 | 17 | 12 | 102 / 39.00 |
| hierarchical_logistic_fed_repo | unweighted | 2020 | 2 | 0 | 4 / 4.00 |
| hierarchical_logistic_fed_repo | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | unweighted | 2025-26 | 5 | 3 | 11 / 3.50 |
| hierarchical_logistic_fed_repo | weighted | 2018-19 | 17 | 12 | 146 / 64.75 |
| hierarchical_logistic_fed_repo | weighted | 2020 | 2 | 0 | 8 / 7.50 |
| hierarchical_logistic_fed_repo | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | weighted | 2025-26 | 5 | 3 | 12 / 4.25 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2018-19 | 17 | 12 | 102 / 38.50 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2020 | 2 | 0 | 5 / 3.25 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2025-26 | 5 | 2 | 11 / 3.75 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2018-19 | 17 | 12 | 146 / 64.75 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2020 | 2 | 1 | 10 / 8.25 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2025-26 | 5 | 3 | 13 / 4.75 |
| hierarchical_logistic_srf | unweighted | 2018-19 | 17 | 12 | 96 / 34.75 |
| hierarchical_logistic_srf | unweighted | 2020 | 2 | 0 | 2 / 2.00 |
| hierarchical_logistic_srf | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | unweighted | 2025-26 | 5 | 3 | 10 / 3.75 |
| hierarchical_logistic_srf | weighted | 2018-19 | 17 | 12 | 146 / 64.75 |
| hierarchical_logistic_srf | weighted | 2020 | 2 | 0 | 10 / 7.25 |
| hierarchical_logistic_srf | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | weighted | 2025-26 | 5 | 3 | 15 / 5.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2018-19 | 17 | 12 | 97 / 37.50 |
| hierarchical_logistic_srf_sameday | unweighted | 2020 | 2 | 0 | 2 / 2.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2025-26 | 5 | 3 | 10 / 3.50 |
| hierarchical_logistic_srf_sameday | weighted | 2018-19 | 17 | 12 | 146 / 64.75 |
| hierarchical_logistic_srf_sameday | weighted | 2020 | 2 | 0 | 7 / 7.00 |
| hierarchical_logistic_srf_sameday | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | weighted | 2025-26 | 5 | 3 | 14 / 5.00 |
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
