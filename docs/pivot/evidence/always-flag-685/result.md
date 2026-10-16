# Tier 1 with and without the always-flag reading, option B: a dropped flag is not a warning but still a false alarm (#685)

## Weighted rule in force

### Tier 1, leads 1 to 5 (pooled)

| row | option | onsets warned, recall [90%] | pooled false alarms per onset (limit 2) | criteria met | tier 1 |
|---|---|---|---|---|---|
| ngboost_laplace | off | 17 of 26, 0.654 [0.467, 0.826] | 2.34 | y y n | fail |
| ngboost_laplace | on | 13 of 26, 0.500 [0.316, 0.696] | 2.34 | y y n | fail |
| calendar_climatology | off | 12 of 26, 0.462 [0.286, 0.667] | 3.90 | n n n | fail |
| calendar_climatology | on | 2 of 26, 0.077 [0.000, 0.176] | 3.90 | n n n | fail |
| persistence_logistic | off | 12 of 26, 0.462 [0.273, 0.650] | 4.09 | n n n | fail |
| persistence_logistic | on | 4 of 26, 0.154 [0.042, 0.278] | 4.09 | n n n | fail |
| published_v1 | off | 14 of 26, 0.538 [0.350, 0.720] | 3.06 | y n n | fail |
| published_v1 | on | 8 of 26, 0.308 [0.136, 0.500] | 3.06 | n n n | fail |

### Onsets warned at lead of at least 1 to 5, off → on

| row | ≥ 1 | ≥ 2 | ≥ 3 | ≥ 4 | ≥ 5 |
|---|---|---|---|---|---|
| ngboost_laplace | 17 → 13 | 12 → 7 | 12 → 7 | 10 → 5 | 10 → 5 |
| calendar_climatology | 12 → 2 | 10 → 2 | 10 → 2 | 10 → 2 | 10 → 2 |
| persistence_logistic | 12 → 4 | 11 → 2 | 11 → 2 | 9 → 1 | 8 → 1 |
| published_v1 | 14 → 8 | 13 → 7 | 13 → 7 | 13 → 6 | 13 → 6 |

### Always-flag blocks per row and horizon (leads 1 to 5 reading), and what they carried

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | flags dropped (h = 1 … 5) | onsets lost |
|---|---|---|---|---|---|---|---|
| ngboost_laplace | 3 | 3 | 4 | 5 | 5 | 63 / 63 / 84 / 105 / 105 | 4: 2019-01-15, 2019-01-31, 2019-06-25, 2019-10-15 |
| calendar_climatology | 10 | 8 | 8 | 9 | 8 | 210 / 168 / 168 / 169 / 168 | 10: 2019-01-15, 2019-01-31, 2019-05-28, 2019-06-17, 2019-06-25, 2019-08-13, 2019-08-30, 2019-10-15, 2019-11-29, 2019-12-16 |
| persistence_logistic | 9 | 8 | 10 | 8 | 7 | 189 / 168 / 210 / 168 / 147 | 8: 2019-03-15, 2019-05-28, 2019-06-17, 2019-06-25, 2019-08-13, 2019-08-30, 2019-10-15, 2019-11-29 |
| published_v1 | 7 | 7 | 4 | 6 | 6 | 147 / 147 / 84 / 126 / 126 | 6: 2019-01-15, 2019-01-31, 2019-02-28, 2019-08-13, 2019-08-30, 2019-10-15 |

## Flat count

### Tier 1, leads 1 to 5 (pooled)

| row | option | onsets warned, recall [90%] | pooled false alarms per onset (limit 2) | criteria met | tier 1 |
|---|---|---|---|---|---|
| ngboost_laplace | off | 15 of 26, 0.577 [0.400, 0.759] | 4.38 | y y n | fail |
| ngboost_laplace | on | 12 of 26, 0.462 [0.281, 0.652] | 4.38 | n y n | fail |
| calendar_climatology | off | 10 of 26, 0.385 [0.208, 0.588] | 5.38 | n n n | fail |
| calendar_climatology | on | 3 of 26, 0.115 [0.000, 0.238] | 5.38 | n n n | fail |
| persistence_logistic | off | 7 of 26, 0.269 [0.111, 0.444] | 5.73 | n n n | fail |
| persistence_logistic | on | 6 of 26, 0.231 [0.083, 0.400] | 5.73 | n n n | fail |
| published_v1 | off | 2 of 26, 0.077 [0.000, 0.185] | 3.92 | n n n | fail |
| published_v1 | on | 0 of 26, 0.000 [0.000, 0.000] | 3.92 | n n n | fail |

### Onsets warned at lead of at least 1 to 5, off → on

| row | ≥ 1 | ≥ 2 | ≥ 3 | ≥ 4 | ≥ 5 |
|---|---|---|---|---|---|
| ngboost_laplace | 15 → 12 | 10 → 6 | 9 → 5 | 7 → 3 | 2 → 1 |
| calendar_climatology | 10 → 3 | 10 → 3 | 10 → 3 | 10 → 3 | 10 → 3 |
| persistence_logistic | 7 → 6 | 7 → 6 | 7 → 6 | 6 → 6 | 5 → 5 |
| published_v1 | 2 → 0 | 2 → 0 | 2 → 0 | 2 → 0 | 2 → 0 |

### Always-flag blocks per row and horizon (leads 1 to 5 reading), and what they carried

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | flags dropped (h = 1 … 5) | onsets lost |
|---|---|---|---|---|---|---|---|
| ngboost_laplace | 1 | 0 | 1 | 3 | 1 | 21 / 0 / 21 / 63 / 21 | 3: 2019-01-15, 2019-01-31, 2019-06-25 |
| calendar_climatology | 7 | 7 | 7 | 8 | 7 | 147 / 147 / 147 / 148 / 147 | 7: 2019-05-28, 2019-06-17, 2019-06-25, 2019-08-13, 2019-08-30, 2019-10-15, 2019-11-29 |
| persistence_logistic | 0 | 5 | 3 | 4 | 1 | 0 / 105 / 63 / 84 / 21 | 1: 2019-05-28 |
| published_v1 | 1 | 0 | 0 | 1 | 1 | 21 / 0 / 0 / 21 / 21 | 2: 2019-01-15, 2019-01-31 |

