# B2's thin-pool fallback, development reading (#1155): development data, not a verdict

H5 step 2 (benchmarks; calendar first). Panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`. Declaration `metadata/b2_pool_fallback_1155.json`. Seed 1155, 10,000 draws, the studentized stationary bootstrap (block 10). Decision days 2019-04-03 to 2025-12-23 (last target 2025-12-31): 1,680 days, every arm on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model; intervals are two-sided 90% (the lower end is the one-sided 95% lower bound).

The turn labels are the draft of #1135 (`turn_days.TurnLabels`), not in force; the fallback is the draft of #1155 (`b2_pool`), not in force. Nothing here is a verdict, and B2 is a benchmark: no candidate's result chose a number. The hit rule is Eleonora's open question (#993): both are reported. A rate is pooled over the five leads of the scored days, so its cells overlap and Kupiec's p-value (in brackets, for 20 or more cells) is read as a guide.

Decision days on which B2 without a minimum cannot forecast (an empty pool: the first year-end of the panel) are not scored in any arm: none.

## The pool each target type reads

Cells (day, lead) by target type; for each, the pool read (own type or the step of the chain) and the range of rows.

### B2 + fallback, min 4

| target type | cells | pools read (cells) | rows in the pool |
|---|---|---|---|
| year_end | 61 | quarter_end_turn 61 | 6 to 6 |
| quarter_end_turn | 200 | quarter_end_turn 200 | 5 to 6 |
| turn | 540 | turn 540 | 15 to 16 |
| tax_date | 415 | tax_date 415 | 10 to 13 |
| ordinary | 7,184 | ordinary 7184 | 211 to 215 |

### B2 + fallback, min 10

| target type | cells | pools read (cells) | rows in the pool |
|---|---|---|---|
| year_end | 61 | turn 61 | 16 to 16 |
| quarter_end_turn | 200 | turn 200 | 16 to 16 |
| turn | 540 | turn 540 | 15 to 16 |
| tax_date | 415 | tax_date 415 | 10 to 13 |
| ordinary | 7,184 | ordinary 7184 | 211 to 215 |

### B2 + fallback, min 20

| target type | cells | pools read (cells) | rows in the pool |
|---|---|---|---|
| year_end | 61 | all_days 61 | 248 to 250 |
| quarter_end_turn | 200 | all_days 200 | 248 to 250 |
| turn | 540 | all_days 540 | 248 to 251 |
| tax_date | 415 | all_days 415 | 247 to 251 |
| ordinary | 7,184 | ordinary 7184 | 211 to 215 |

### B2 + fallback, min 30

| target type | cells | pools read (cells) | rows in the pool |
|---|---|---|---|
| year_end | 61 | all_days 61 | 248 to 250 |
| quarter_end_turn | 200 | all_days 200 | 248 to 250 |
| turn | 540 | all_days 540 | 248 to 251 |
| tax_date | 415 | all_days 415 | 247 to 251 |
| ordinary | 7,184 | ordinary 7184 | 211 to 215 |

## Coverage and exceedance, under both hit rules

### 50% band miss (nominal 0.500), hit rule `y > q`

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| pooled | 0.467 (0.000) n=8400 | 0.467 (0.000) n=8400 | 0.541 (0.000) n=8400 | 0.544 (0.000) n=8400 | 0.542 (0.000) n=8400 | 0.548 (0.000) n=8400 | 0.544 (0.000) n=8400 | 0.544 (0.000) n=8400 |

**regime (target day)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 0.524 (0.147) n=920 | 0.518 (0.262) n=920 | 0.557 (0.001) n=920 | 0.560 (0.000) n=920 | 0.560 (0.000) n=920 | 0.565 (0.000) n=920 | 0.602 (0.000) n=920 | 0.602 (0.000) n=920 |
| 2020 | 0.202 (0.000) n=1255 | 0.245 (0.000) n=1255 | 0.407 (0.000) n=1255 | 0.410 (0.000) n=1255 | 0.406 (0.000) n=1255 | 0.418 (0.000) n=1255 | 0.395 (0.000) n=1255 | 0.395 (0.000) n=1255 |
| 2021-23 | 0.409 (0.000) n=3740 | 0.391 (0.000) n=3740 | 0.551 (0.000) n=3740 | 0.556 (0.000) n=3740 | 0.553 (0.000) n=3740 | 0.552 (0.000) n=3740 | 0.536 (0.000) n=3740 | 0.536 (0.000) n=3740 |
| 2024 | 0.567 (0.000) n=1250 | 0.581 (0.000) n=1250 | 0.462 (0.008) n=1250 | 0.465 (0.013) n=1250 | 0.465 (0.013) n=1250 | 0.469 (0.027) n=1250 | 0.486 (0.309) n=1250 | 0.486 (0.309) n=1250 |
| 2025-26 | 0.766 (0.000) n=1235 | 0.772 (0.000) n=1235 | 0.718 (0.000) n=1235 | 0.715 (0.000) n=1235 | 0.713 (0.000) n=1235 | 0.733 (0.000) n=1235 | 0.737 (0.000) n=1235 | 0.737 (0.000) n=1235 |

**pressure-day type (target day, turn labels)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| year_end | 0.508 (0.898) n=61 | 0.443 (0.370) n=61 | 0.672 (0.007) n=61 | 0.967 (0.000) n=61 | 0.672 (0.007) n=61 | 0.672 (0.007) n=61 | 0.590 (0.158) n=61 | 0.590 (0.158) n=61 |
| quarter_end_turn | 0.640 (0.000) n=200 | 0.645 (0.000) n=200 | 0.750 (0.000) n=200 | 0.595 (0.007) n=200 | 0.595 (0.007) n=200 | 0.825 (0.000) n=200 | 0.825 (0.000) n=200 | 0.825 (0.000) n=200 |
| turn | 0.609 (0.000) n=540 | 0.535 (0.102) n=540 | 0.667 (0.000) n=540 | 0.628 (0.000) n=540 | 0.628 (0.000) n=540 | 0.628 (0.000) n=540 | 0.648 (0.000) n=540 | 0.648 (0.000) n=540 |
| tax_date | 0.475 (0.303) n=415 | 0.472 (0.259) n=415 | 0.670 (0.000) n=415 | 0.670 (0.000) n=415 | 0.670 (0.000) n=415 | 0.670 (0.000) n=415 | 0.588 (0.000) n=415 | 0.588 (0.000) n=415 |
| ordinary | 0.450 (0.000) n=7184 | 0.457 (0.000) n=7184 | 0.518 (0.003) n=7184 | 0.526 (0.000) n=7184 | 0.526 (0.000) n=7184 | 0.526 (0.000) n=7184 | 0.526 (0.000) n=7184 | 0.526 (0.000) n=7184 |

### 90% band miss (nominal 0.100), hit rule `y > q`

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| pooled | 0.157 (0.000) n=8400 | 0.170 (0.000) n=8400 | 0.181 (0.000) n=8400 | 0.197 (0.000) n=8400 | 0.193 (0.000) n=8400 | 0.198 (0.000) n=8400 | 0.185 (0.000) n=8400 | 0.185 (0.000) n=8400 |

**regime (target day)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 0.184 (0.000) n=920 | 0.186 (0.000) n=920 | 0.201 (0.000) n=920 | 0.207 (0.000) n=920 | 0.207 (0.000) n=920 | 0.207 (0.000) n=920 | 0.230 (0.000) n=920 | 0.230 (0.000) n=920 |
| 2020 | 0.025 (0.000) n=1255 | 0.035 (0.000) n=1255 | 0.123 (0.009) n=1255 | 0.135 (0.000) n=1255 | 0.131 (0.001) n=1255 | 0.131 (0.001) n=1255 | 0.100 (0.962) n=1255 | 0.100 (0.962) n=1255 |
| 2021-23 | 0.115 (0.002) n=3740 | 0.110 (0.036) n=3740 | 0.172 (0.000) n=3740 | 0.191 (0.000) n=3740 | 0.187 (0.000) n=3740 | 0.188 (0.000) n=3740 | 0.161 (0.000) n=3740 | 0.161 (0.000) n=3740 |
| 2024 | 0.230 (0.000) n=1250 | 0.250 (0.000) n=1250 | 0.142 (0.000) n=1250 | 0.185 (0.000) n=1250 | 0.181 (0.000) n=1250 | 0.185 (0.000) n=1250 | 0.197 (0.000) n=1250 | 0.197 (0.000) n=1250 |
| 2025-26 | 0.321 (0.000) n=1235 | 0.398 (0.000) n=1235 | 0.294 (0.000) n=1235 | 0.280 (0.000) n=1235 | 0.278 (0.000) n=1235 | 0.301 (0.000) n=1235 | 0.299 (0.000) n=1235 | 0.299 (0.000) n=1235 |

**pressure-day type (target day, turn labels)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| year_end | 0.279 (0.000) n=61 | 0.279 (0.000) n=61 | 0.590 (0.000) n=61 | 0.967 (0.000) n=61 | 0.508 (0.000) n=61 | 0.492 (0.000) n=61 | 0.426 (0.000) n=61 | 0.426 (0.000) n=61 |
| quarter_end_turn | 0.425 (0.000) n=200 | 0.410 (0.000) n=200 | 0.525 (0.000) n=200 | 0.405 (0.000) n=200 | 0.405 (0.000) n=200 | 0.600 (0.000) n=200 | 0.550 (0.000) n=200 | 0.550 (0.000) n=200 |
| turn | 0.254 (0.000) n=540 | 0.226 (0.000) n=540 | 0.222 (0.000) n=540 | 0.250 (0.000) n=540 | 0.250 (0.000) n=540 | 0.250 (0.000) n=540 | 0.206 (0.000) n=540 | 0.206 (0.000) n=540 |
| tax_date | 0.190 (0.000) n=415 | 0.164 (0.000) n=415 | 0.386 (0.000) n=415 | 0.386 (0.000) n=415 | 0.386 (0.000) n=415 | 0.386 (0.000) n=415 | 0.227 (0.000) n=415 | 0.227 (0.000) n=415 |
| ordinary | 0.139 (0.000) n=7184 | 0.159 (0.000) n=7184 | 0.154 (0.000) n=7184 | 0.169 (0.000) n=7184 | 0.169 (0.000) n=7184 | 0.169 (0.000) n=7184 | 0.169 (0.000) n=7184 | 0.169 (0.000) n=7184 |

### q95 exceedance (nominal 0.050), hit rule `y > q`

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| pooled | 0.082 (0.000) n=8400 | 0.095 (0.000) n=8400 | 0.093 (0.000) n=8400 | 0.100 (0.000) n=8400 | 0.099 (0.000) n=8400 | 0.102 (0.000) n=8400 | 0.110 (0.000) n=8400 | 0.110 (0.000) n=8400 |

**regime (target day)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 0.088 (0.000) n=920 | 0.120 (0.000) n=920 | 0.168 (0.000) n=920 | 0.174 (0.000) n=920 | 0.174 (0.000) n=920 | 0.174 (0.000) n=920 | 0.212 (0.000) n=920 | 0.212 (0.000) n=920 |
| 2020 | 0.014 (0.000) n=1255 | 0.017 (0.000) n=1255 | 0.008 (0.000) n=1255 | 0.008 (0.000) n=1255 | 0.008 (0.000) n=1255 | 0.008 (0.000) n=1255 | 0.008 (0.000) n=1255 | 0.008 (0.000) n=1255 |
| 2021-23 | 0.065 (0.000) n=3740 | 0.065 (0.000) n=3740 | 0.056 (0.077) n=3740 | 0.060 (0.005) n=3740 | 0.060 (0.005) n=3740 | 0.059 (0.013) n=3740 | 0.061 (0.002) n=3740 | 0.061 (0.002) n=3740 |
| 2024 | 0.110 (0.000) n=1250 | 0.137 (0.000) n=1250 | 0.134 (0.000) n=1250 | 0.177 (0.000) n=1250 | 0.173 (0.000) n=1250 | 0.177 (0.000) n=1250 | 0.189 (0.000) n=1250 | 0.189 (0.000) n=1250 |
| 2025-26 | 0.172 (0.000) n=1235 | 0.206 (0.000) n=1235 | 0.194 (0.000) n=1235 | 0.181 (0.000) n=1235 | 0.178 (0.000) n=1235 | 0.202 (0.000) n=1235 | 0.206 (0.000) n=1235 | 0.206 (0.000) n=1235 |

**pressure-day type (target day, turn labels)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| year_end | 0.230 (0.000) n=61 | 0.230 (0.000) n=61 | 0.508 (0.000) n=61 | 0.475 (0.000) n=61 | 0.344 (0.000) n=61 | 0.328 (0.000) n=61 | 0.426 (0.000) n=61 | 0.426 (0.000) n=61 |
| quarter_end_turn | 0.410 (0.000) n=200 | 0.390 (0.000) n=200 | 0.300 (0.000) n=200 | 0.150 (0.000) n=200 | 0.150 (0.000) n=200 | 0.300 (0.000) n=200 | 0.375 (0.000) n=200 | 0.375 (0.000) n=200 |
| turn | 0.248 (0.000) n=540 | 0.172 (0.000) n=540 | 0.194 (0.000) n=540 | 0.111 (0.000) n=540 | 0.111 (0.000) n=540 | 0.111 (0.000) n=540 | 0.204 (0.000) n=540 | 0.204 (0.000) n=540 |
| tax_date | 0.118 (0.000) n=415 | 0.101 (0.000) n=415 | 0.147 (0.000) n=415 | 0.147 (0.000) n=415 | 0.147 (0.000) n=415 | 0.147 (0.000) n=415 | 0.133 (0.000) n=415 | 0.133 (0.000) n=415 |
| ordinary | 0.057 (0.007) n=7184 | 0.079 (0.000) n=7184 | 0.073 (0.000) n=7184 | 0.092 (0.000) n=7184 | 0.092 (0.000) n=7184 | 0.092 (0.000) n=7184 | 0.092 (0.000) n=7184 | 0.092 (0.000) n=7184 |

### 50% band miss (nominal 0.500), hit rule `y >= q`

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| pooled | 0.688 (0.000) n=8400 | 0.730 (0.000) n=8400 | 0.755 (0.000) n=8400 | 0.761 (0.000) n=8400 | 0.760 (0.000) n=8400 | 0.765 (0.000) n=8400 | 0.773 (0.000) n=8400 | 0.773 (0.000) n=8400 |

**regime (target day)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 0.574 (0.000) n=920 | 0.643 (0.000) n=920 | 0.621 (0.000) n=920 | 0.597 (0.000) n=920 | 0.597 (0.000) n=920 | 0.602 (0.000) n=920 | 0.650 (0.000) n=920 | 0.650 (0.000) n=920 |
| 2020 | 0.235 (0.000) n=1255 | 0.312 (0.000) n=1255 | 0.535 (0.014) n=1255 | 0.548 (0.001) n=1255 | 0.544 (0.002) n=1255 | 0.556 (0.000) n=1255 | 0.545 (0.001) n=1255 | 0.545 (0.001) n=1255 |
| 2021-23 | 0.764 (0.000) n=3740 | 0.784 (0.000) n=3740 | 0.794 (0.000) n=3740 | 0.806 (0.000) n=3740 | 0.806 (0.000) n=3740 | 0.806 (0.000) n=3740 | 0.807 (0.000) n=3740 | 0.807 (0.000) n=3740 |
| 2024 | 0.814 (0.000) n=1250 | 0.894 (0.000) n=1250 | 0.906 (0.000) n=1250 | 0.909 (0.000) n=1250 | 0.909 (0.000) n=1250 | 0.909 (0.000) n=1250 | 0.934 (0.000) n=1250 | 0.934 (0.000) n=1250 |
| 2025-26 | 0.877 (0.000) n=1235 | 0.887 (0.000) n=1235 | 0.811 (0.000) n=1235 | 0.812 (0.000) n=1235 | 0.808 (0.000) n=1235 | 0.828 (0.000) n=1235 | 0.832 (0.000) n=1235 | 0.832 (0.000) n=1235 |

**pressure-day type (target day, turn labels)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| year_end | 0.770 (0.000) n=61 | 0.787 (0.000) n=61 | 0.918 (0.000) n=61 | 1.000 (0.000) n=61 | 0.836 (0.000) n=61 | 0.918 (0.000) n=61 | 0.918 (0.000) n=61 | 0.918 (0.000) n=61 |
| quarter_end_turn | 0.735 (0.000) n=200 | 0.710 (0.000) n=200 | 0.775 (0.000) n=200 | 0.630 (0.000) n=200 | 0.630 (0.000) n=200 | 0.825 (0.000) n=200 | 0.900 (0.000) n=200 | 0.900 (0.000) n=200 |
| turn | 0.750 (0.000) n=540 | 0.761 (0.000) n=540 | 0.798 (0.000) n=540 | 0.730 (0.000) n=540 | 0.730 (0.000) n=540 | 0.730 (0.000) n=540 | 0.828 (0.000) n=540 | 0.828 (0.000) n=540 |
| tax_date | 0.641 (0.000) n=415 | 0.653 (0.000) n=415 | 0.783 (0.000) n=415 | 0.783 (0.000) n=415 | 0.783 (0.000) n=415 | 0.783 (0.000) n=415 | 0.783 (0.000) n=415 | 0.783 (0.000) n=415 |
| ordinary | 0.684 (0.000) n=7184 | 0.732 (0.000) n=7184 | 0.749 (0.000) n=7184 | 0.764 (0.000) n=7184 | 0.764 (0.000) n=7184 | 0.764 (0.000) n=7184 | 0.764 (0.000) n=7184 | 0.764 (0.000) n=7184 |

### 90% band miss (nominal 0.100), hit rule `y >= q`

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| pooled | 0.180 (0.000) n=8400 | 0.203 (0.000) n=8400 | 0.386 (0.000) n=8400 | 0.406 (0.000) n=8400 | 0.403 (0.000) n=8400 | 0.407 (0.000) n=8400 | 0.405 (0.000) n=8400 | 0.405 (0.000) n=8400 |

**regime (target day)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 0.192 (0.000) n=920 | 0.198 (0.000) n=920 | 0.241 (0.000) n=920 | 0.259 (0.000) n=920 | 0.259 (0.000) n=920 | 0.259 (0.000) n=920 | 0.286 (0.000) n=920 | 0.286 (0.000) n=920 |
| 2020 | 0.025 (0.000) n=1255 | 0.048 (0.000) n=1255 | 0.175 (0.000) n=1255 | 0.202 (0.000) n=1255 | 0.198 (0.000) n=1255 | 0.198 (0.000) n=1255 | 0.168 (0.000) n=1255 | 0.168 (0.000) n=1255 |
| 2021-23 | 0.133 (0.000) n=3740 | 0.139 (0.000) n=3740 | 0.532 (0.000) n=3740 | 0.545 (0.000) n=3740 | 0.544 (0.000) n=3740 | 0.542 (0.000) n=3740 | 0.537 (0.000) n=3740 | 0.537 (0.000) n=3740 |
| 2024 | 0.278 (0.000) n=1250 | 0.306 (0.000) n=1250 | 0.290 (0.000) n=1250 | 0.336 (0.000) n=1250 | 0.332 (0.000) n=1250 | 0.336 (0.000) n=1250 | 0.346 (0.000) n=1250 | 0.346 (0.000) n=1250 |
| 2025-26 | 0.372 (0.000) n=1235 | 0.455 (0.000) n=1235 | 0.364 (0.000) n=1235 | 0.370 (0.000) n=1235 | 0.366 (0.000) n=1235 | 0.389 (0.000) n=1235 | 0.394 (0.000) n=1235 | 0.394 (0.000) n=1235 |

**pressure-day type (target day, turn labels)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| year_end | 0.279 (0.000) n=61 | 0.279 (0.000) n=61 | 0.754 (0.000) n=61 | 1.000 (0.000) n=61 | 0.672 (0.000) n=61 | 0.656 (0.000) n=61 | 0.590 (0.000) n=61 | 0.590 (0.000) n=61 |
| quarter_end_turn | 0.445 (0.000) n=200 | 0.430 (0.000) n=200 | 0.580 (0.000) n=200 | 0.500 (0.000) n=200 | 0.500 (0.000) n=200 | 0.650 (0.000) n=200 | 0.700 (0.000) n=200 | 0.700 (0.000) n=200 |
| turn | 0.287 (0.000) n=540 | 0.331 (0.000) n=540 | 0.420 (0.000) n=540 | 0.361 (0.000) n=540 | 0.361 (0.000) n=540 | 0.361 (0.000) n=540 | 0.428 (0.000) n=540 | 0.428 (0.000) n=540 |
| tax_date | 0.212 (0.000) n=415 | 0.183 (0.000) n=415 | 0.525 (0.000) n=415 | 0.525 (0.000) n=415 | 0.525 (0.000) n=415 | 0.525 (0.000) n=415 | 0.390 (0.000) n=415 | 0.390 (0.000) n=415 |
| ordinary | 0.162 (0.000) n=7184 | 0.188 (0.000) n=7184 | 0.367 (0.000) n=7184 | 0.394 (0.000) n=7184 | 0.394 (0.000) n=7184 | 0.394 (0.000) n=7184 | 0.394 (0.000) n=7184 | 0.394 (0.000) n=7184 |

### q95 exceedance (nominal 0.050), hit rule `y >= q`

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| pooled | 0.092 (0.000) n=8400 | 0.107 (0.000) n=8400 | 0.135 (0.000) n=8400 | 0.145 (0.000) n=8400 | 0.144 (0.000) n=8400 | 0.147 (0.000) n=8400 | 0.158 (0.000) n=8400 | 0.158 (0.000) n=8400 |

**regime (target day)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 0.091 (0.000) n=920 | 0.127 (0.000) n=920 | 0.187 (0.000) n=920 | 0.204 (0.000) n=920 | 0.204 (0.000) n=920 | 0.204 (0.000) n=920 | 0.242 (0.000) n=920 | 0.242 (0.000) n=920 |
| 2020 | 0.014 (0.000) n=1255 | 0.017 (0.000) n=1255 | 0.008 (0.000) n=1255 | 0.012 (0.000) n=1255 | 0.012 (0.000) n=1255 | 0.012 (0.000) n=1255 | 0.012 (0.000) n=1255 | 0.012 (0.000) n=1255 |
| 2021-23 | 0.073 (0.000) n=3740 | 0.074 (0.000) n=3740 | 0.107 (0.000) n=3740 | 0.107 (0.000) n=3740 | 0.107 (0.000) n=3740 | 0.106 (0.000) n=3740 | 0.111 (0.000) n=3740 | 0.111 (0.000) n=3740 |
| 2024 | 0.137 (0.000) n=1250 | 0.164 (0.000) n=1250 | 0.242 (0.000) n=1250 | 0.288 (0.000) n=1250 | 0.284 (0.000) n=1250 | 0.288 (0.000) n=1250 | 0.298 (0.000) n=1250 | 0.298 (0.000) n=1250 |
| 2025-26 | 0.188 (0.000) n=1235 | 0.227 (0.000) n=1235 | 0.202 (0.000) n=1235 | 0.208 (0.000) n=1235 | 0.204 (0.000) n=1235 | 0.228 (0.000) n=1235 | 0.240 (0.000) n=1235 | 0.240 (0.000) n=1235 |

**pressure-day type (target day, turn labels)**

| group | B1 | B1' | B2 legacy month-end | B2 turn labels, no minimum | B2 + fallback, min 4 | B2 + fallback, min 10 | B2 + fallback, min 20 | B2 + fallback, min 30 |
|---|---|---|---|---|---|---|---|---|
| year_end | 0.230 (0.000) n=61 | 0.230 (0.000) n=61 | 0.508 (0.000) n=61 | 0.508 (0.000) n=61 | 0.344 (0.000) n=61 | 0.328 (0.000) n=61 | 0.426 (0.000) n=61 | 0.426 (0.000) n=61 |
| quarter_end_turn | 0.430 (0.000) n=200 | 0.410 (0.000) n=200 | 0.300 (0.000) n=200 | 0.150 (0.000) n=200 | 0.150 (0.000) n=200 | 0.300 (0.000) n=200 | 0.425 (0.000) n=200 | 0.425 (0.000) n=200 |
| turn | 0.280 (0.000) n=540 | 0.176 (0.000) n=540 | 0.244 (0.000) n=540 | 0.111 (0.000) n=540 | 0.111 (0.000) n=540 | 0.111 (0.000) n=540 | 0.261 (0.000) n=540 | 0.261 (0.000) n=540 |
| tax_date | 0.133 (0.000) n=415 | 0.118 (0.000) n=415 | 0.200 (0.000) n=415 | 0.200 (0.000) n=415 | 0.200 (0.000) n=415 | 0.200 (0.000) n=415 | 0.133 (0.000) n=415 | 0.133 (0.000) n=415 |
| ordinary | 0.066 (0.000) n=7184 | 0.092 (0.000) n=7184 | 0.115 (0.000) n=7184 | 0.141 (0.000) n=7184 | 0.141 (0.000) n=7184 | 0.141 (0.000) n=7184 | 0.141 (0.000) n=7184 | 0.141 (0.000) n=7184 |

## Scores, paired

Mean grid CRPS and upper-tail twCRPS by arm, pooled: B1 2.0904 / 1.1685; B1' 1.7154 / 0.8571; B2 legacy month-end 2.4517 / 1.0231; B2 turn labels, no minimum 2.5311 / 1.0983; B2 + fallback, min 4 2.4522 / 1.0300; B2 + fallback, min 10 2.4524 / 1.0266; B2 + fallback, min 20 2.4176 / 0.9882; B2 + fallback, min 30 2.4176 / 0.9882.

### grid CRPS (23 levels)

**pooled (decision days)**

| group | days | B2 + fallback, min 4 over B2 turn labels, no minimum | B2 + fallback, min 10 over B2 turn labels, no minimum | B2 + fallback, min 20 over B2 turn labels, no minimum | B2 + fallback, min 30 over B2 turn labels, no minimum | B2 turn labels, no minimum over B2 legacy month-end | B2 + fallback, min 10 over B1 | B2 + fallback, min 10 over B1' |
|---|---|---|---|---|---|---|---|---|
| all decision days | 1,680 | undefined | +3.1% [-0.1%, +19.1%] | +4.5% [+0.4%, +17.5%] | +4.5% [+0.4%, +17.5%] | -3.2% [-16.1%, -0.5%] | -17.3% [-43.8%, +26.3%] | -43.0% [-66.8%, -22.7%] |

**regime (target day)**

| group | days | B2 + fallback, min 4 over B2 turn labels, no minimum | B2 + fallback, min 10 over B2 turn labels, no minimum | B2 + fallback, min 20 over B2 turn labels, no minimum | B2 + fallback, min 30 over B2 turn labels, no minimum | B2 turn labels, no minimum over B2 legacy month-end | B2 + fallback, min 10 over B1 | B2 + fallback, min 10 over B1' |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 186 | undefined | undefined | +4.1% [-4.2%, +40.5%] | +4.1% [-4.2%, +40.5%] | -4.6% [-26.4%, -0.2%] | +22.3% [-3.9%, +81.4%] | -15.8% [-49.4%, +5.8%] |
| 2020 | 251 | undefined | undefined | +20.7% [+10.7%, +46.5%] | +20.7% [+10.7%, +46.5%] | -12.3% [-92.9%, -1.3%] | -71.3% [-178.7%, +5.1%] | -74.8% [-184.3%, +18.2%] |
| 2021-23 | 748 | undefined | +2.3% [+0.3%, +9.1%] | +4.6% [+2.6%, +9.0%] | +4.6% [+2.6%, +9.0%] | -1.7% [-7.6%, +0.2%] | -108.8% [-170.5%, -63.8%] | -119.4% [-182.7%, -70.2%] |
| 2024 | 250 | undefined | undefined | -5.2% [-8.2%, -2.2%] | -5.2% [-8.2%, -2.2%] | +0.9% [-1.6%, +3.4%] | +13.6% [-2.8%, +30.2%] | -1.3% [-20.8%, +16.9%] |
| 2025-26 | 249 | undefined | undefined | -5.7% [-11.1%, -2.2%] | -5.7% [-11.1%, -2.2%] | +1.6% [-0.3%, +3.8%] | -13.6% [-52.0%, +13.0%] | -27.4% [-75.3%, +4.9%] |

**pressure-day type (target day, turn labels)**

| group | days | B2 + fallback, min 4 over B2 turn labels, no minimum | B2 + fallback, min 10 over B2 turn labels, no minimum | B2 + fallback, min 20 over B2 turn labels, no minimum | B2 + fallback, min 30 over B2 turn labels, no minimum | B2 turn labels, no minimum over B2 legacy month-end | B2 + fallback, min 10 over B1 | B2 + fallback, min 10 over B1' |
|---|---|---|---|---|---|---|---|---|
| quarter_end_turn | 40 | undefined | -0.3% [-55.6%, +20.9%] | -7.8% [-106.9%, +27.2%] | -7.8% [-106.9%, +27.2%] | -4.0% [-39.7%, +25.3%] | -25.8% [-87.1%, +11.4%] | -29.1% [-93.6%, +9.4%] |
| turn | 108 | undefined | undefined | -3.2% [-25.7%, +30.7%] | -3.2% [-25.7%, +30.7%] | +0.9% [-37.6%, +16.9%] | -32.5% [-82.0%, +0.1%] | -44.7% [-80.5%, -14.5%] |
| tax_date | 83 | undefined | undefined | +12.8% [-9.4%, +29.3%] | +12.8% [-9.4%, +29.3%] | undefined | -40.2% [-102.2%, +55.5%] | -42.5% [-109.5%, +68.2%] |
| ordinary | 1,440 | undefined | undefined | undefined | undefined | -0.5% [-1.5%, +0.6%] | -11.2% [-40.3%, +39.4%] | -44.2% [-68.1%, -23.5%] |

### upper-tail twCRPS (weight 1{z > 0 bp})

**pooled (decision days)**

| group | days | B2 + fallback, min 4 over B2 turn labels, no minimum | B2 + fallback, min 10 over B2 turn labels, no minimum | B2 + fallback, min 20 over B2 turn labels, no minimum | B2 + fallback, min 30 over B2 turn labels, no minimum | B2 turn labels, no minimum over B2 legacy month-end | B2 + fallback, min 10 over B1 | B2 + fallback, min 10 over B1' |
|---|---|---|---|---|---|---|---|---|
| all decision days | 1,680 | undefined | +6.5% [-1.0%, +66.9%] | +10.0% [+0.2%, +48.2%] | +10.0% [+0.2%, +48.2%] | -7.3% [-50.4%, -0.8%] | +12.1% [-12.6%, +59.5%] | -19.8% [-42.3%, -2.3%] |

**regime (target day)**

| group | days | B2 + fallback, min 4 over B2 turn labels, no minimum | B2 + fallback, min 10 over B2 turn labels, no minimum | B2 + fallback, min 20 over B2 turn labels, no minimum | B2 + fallback, min 30 over B2 turn labels, no minimum | B2 turn labels, no minimum over B2 legacy month-end | B2 + fallback, min 10 over B1 | B2 + fallback, min 10 over B1' |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 186 | undefined | undefined | +4.5% [-4.1%, +45.1%] | +4.5% [-4.1%, +45.1%] | -4.7% [-29.1%, +0.0%] | +24.7% [+0.9%, +82.2%] | -12.4% [-38.0%, +4.6%] |
| 2020 | 251 | undefined | undefined | +38.0% [+17.2%, +73.5%] | +38.0% [+17.2%, +73.5%] | -26.9% [-224.2%, -2.1%] | -67.8% [-229.0%, +102.9%] | -62.5% [-236.0%, +102.7%] |
| 2021-23 | 748 | undefined | undefined | -3.3% [-7.4%, -0.2%] | -3.3% [-7.4%, -0.2%] | +4.2% [+0.5%, +8.2%] | +67.7% [+47.9%, +77.8%] | +59.0% [+40.0%, +73.0%] |
| 2024 | 250 | undefined | undefined | undefined | undefined | undefined | undefined | undefined |
| 2025-26 | 249 | undefined | undefined | -2.8% [-11.0%, +2.2%] | -2.8% [-11.0%, +2.2%] | +0.8% [-1.2%, +3.8%] | +2.1% [-37.0%, +22.5%] | -19.8% [-66.1%, +2.8%] |

**pressure-day type (target day, turn labels)**

| group | days | B2 + fallback, min 4 over B2 turn labels, no minimum | B2 + fallback, min 10 over B2 turn labels, no minimum | B2 + fallback, min 20 over B2 turn labels, no minimum | B2 + fallback, min 30 over B2 turn labels, no minimum | B2 turn labels, no minimum over B2 legacy month-end | B2 + fallback, min 10 over B1 | B2 + fallback, min 10 over B1' |
|---|---|---|---|---|---|---|---|---|
| quarter_end_turn | 40 | undefined | undefined | undefined | undefined | undefined | undefined | undefined |
| turn | 108 | undefined | undefined | undefined | undefined | undefined | undefined | undefined |
| tax_date | 83 | undefined | undefined | undefined | undefined | undefined | undefined | undefined |
| ordinary | 1,440 | undefined | undefined | undefined | undefined | +0.9% [-1.2%, +3.4%] | +29.7% [-3.9%, +91.3%] | -15.4% [-38.7%, +6.9%] |

`undefined` is a pair that has no studentized interval: the two arms forecast alike on every day of the group (no variance of the difference), or the benchmark scores zero on a resample (the upper-tail score of a group in which no forecast and no outcome is above 0 bp).

## What it shows and does not show

- The chain replaces a thin type's pool by the next step's rows; it does not add them. A thin type's own few rows are dropped, so a target type that runs hotter than the type it falls to is forecast from the cooler one.
- A pool minimum of 20 and one of 30 are the same rule here: no type but ordinary has as many as 20 rows in a year, so every other type reads every day. Their arms are identical.
- Where a type keeps its own pool the fallback arm is B2 without a minimum, exactly (the paired test of those groups is `undefined`).

- q95 exceedance (nominal 0.050), hit rule `y > q`, B2 without a minimum / min 4 / min 10 / min 20: year_end 0.475 / 0.344 / 0.328 / 0.426; quarter_end_turn 0.150 / 0.150 / 0.300 / 0.375.
- 90% band miss (nominal 0.100), hit rule `y > q`, B2 without a minimum / min 4 / min 10 / min 20: year_end 0.967 / 0.508 / 0.492 / 0.426; quarter_end_turn 0.405 / 0.405 / 0.600 / 0.550.
- q95 exceedance (nominal 0.050), hit rule `y >= q`, B2 without a minimum / min 4 / min 10 / min 20: year_end 0.508 / 0.344 / 0.328 / 0.426; quarter_end_turn 0.150 / 0.150 / 0.300 / 0.425.
- 90% band miss (nominal 0.100), hit rule `y >= q`, B2 without a minimum / min 4 / min 10 / min 20: year_end 1.000 / 0.672 / 0.656 / 0.590; quarter_end_turn 0.500 / 0.500 / 0.650 / 0.700.
- A minimum of 4 (added by the ruling of 23 October 2026) is at or below the smallest quarter_end_turn pool of the scored days (5 rows), so on these days the target types that change pool are: year_end; year_end reads quarter_end_turn.
- Against a minimum of 10 (hit rule `y > q`): the quarter-end turn keeps B2's own rates at 4 (90% band miss 0.405, q95 exceedance 0.150) where 10 raises them (0.600, 0.300); the year-end is a little worse at 4 (0.508, 0.344) than at 10 (0.492, 0.328), and both are far better than without a minimum (0.967, 0.475).
- Mean grid CRPS, pooled: B2 without a minimum 2.5311, min 4 2.4522, min 10 2.4524, min 20 and 30 2.4176, B1' 1.7154. The paired test of min 4 against B2 without a minimum is `undefined` whenever the two differ on year-end targets only: a resample of blocks can hold none of those days, and its difference then has no long-run variance. The means above are the point reading; the year_end group (13 target days) is below the floor and is not tested.
- Every arm is far from nominal on the thin types and on the 90% band of ordinary days: the fallback does not bring them near it. Development data on 2019-2025, never a verdict; B2 is a benchmark.

Groups of fewer than 20 target days, listed and not tested: pressure_day_type/year_end (13).

