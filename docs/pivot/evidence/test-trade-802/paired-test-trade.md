Paired Brier difference, candidate minus its passer, +5 bp, all scored days (negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero).

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0021 [-0.0002, +0.0046] | +0.0022 [+0.0006, +0.0041] * | +0.0008 [-0.0000, +0.0018] | +0.0009 [-0.0005, +0.0024] | +0.0009 [-0.0001, +0.0021] |

By regime, h = 1:

| candidate | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0040 [-0.0046, +0.0135] | +0.0061 [-0.0014, +0.0155] | +0.0000 [-0.0000, +0.0000] | -0.0009 [-0.0027, +0.0000] | +0.0044 [-0.0021, +0.0117] |

By day_type, h = 1:

| candidate | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0060 [-0.0049, +0.0192] | +0.0008 [-0.0008, +0.0026] | -0.0047 [-0.0300, +0.0189] | +0.0205 [-0.0019, +0.0511] |

+5 bp onsets flagged / onsets at some lead 1 to 5, by year, under the judge's cut-offs:

| model | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| risk_logistic_base | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer | 3/5 | 10/13 | 0/2 | 1/2 | 4/5 | 18/27 |

+5 bp onsets flagged / onsets at lead 1, false alarms per onset (all days):

| model | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| risk_logistic_base | 13/27, 1.70 | 6/26, 1.00 | 6/26, 1.00 | 7/26, 1.12 | 8/26, 1.15 |
| risk_logistic_base_dealer | 16/27, 1.63 | 7/26, 1.54 | 7/26, 1.15 | 8/26, 1.54 | 8/26, 1.35 |
