Paired Brier difference, candidate minus its passer, +5 bp, all scored days (negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero).

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0014 [-0.0011, +0.0043] | +0.0012 [-0.0005, +0.0033] | +0.0003 [-0.0006, +0.0013] | +0.0007 [-0.0004, +0.0020] | +0.0006 [-0.0004, +0.0018] |

By regime, h = 1:

| candidate | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| risk_logistic_base_dealer | -0.0009 [-0.0056, +0.0045] | +0.0162 [+0.0027, +0.0352] * | +0.0000 [+0.0000, +0.0000] * | -0.0005 [-0.0015, +0.0000] | -0.0042 [-0.0092, +0.0001] |

By day_type, h = 1:

| candidate | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0010 [-0.0105, +0.0141] | +0.0001 [-0.0010, +0.0013] | +0.0106 [-0.0050, +0.0270] | +0.0215 [-0.0056, +0.0618] |

+5 bp onsets flagged / onsets at some lead 1 to 5, by year, under the judge's cut-offs:

| model | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| risk_logistic_base | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer | 3/5 | 10/13 | 0/2 | 0/2 | 4/5 | 17/27 |

+5 bp onsets flagged / onsets at lead 1, false alarms per onset (all days):

| model | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| risk_logistic_base | 13/27, 1.70 | 6/26, 1.00 | 6/26, 1.00 | 7/26, 1.12 | 8/26, 1.15 |
| risk_logistic_base_dealer | 17/27, 1.78 | 7/26, 1.12 | 7/26, 1.12 | 7/26, 1.15 | 8/26, 1.15 |
