Paired Brier difference, candidate minus its passer, +5 bp, all scored days (negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero).

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0029 [+0.0002, +0.0058] * | +0.0022 [+0.0004, +0.0042] * | +0.0003 [-0.0006, +0.0013] | +0.0010 [-0.0004, +0.0025] | +0.0006 [-0.0004, +0.0020] |

By regime, h = 1:

| candidate | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0042 [-0.0044, +0.0140] | +0.0128 [+0.0030, +0.0247] * | -0.0000 [-0.0000, +0.0000] | -0.0009 [-0.0024, +0.0000] | +0.0032 [-0.0055, +0.0132] |

By day_type, h = 1:

| candidate | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|
| risk_logistic_base_dealer | +0.0164 [-0.0007, +0.0364] | +0.0007 [-0.0011, +0.0026] | -0.0069 [-0.0320, +0.0147] | +0.0228 [-0.0023, +0.0568] |

+5 bp onsets flagged / onsets at some lead 1 to 5, by year, under the judge's cut-offs:

| model | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| risk_logistic_base | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer | 3/5 | 10/13 | 0/2 | 0/2 | 5/5 | 18/27 |

+5 bp onsets flagged / onsets at lead 1, false alarms per onset (all days):

| model | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| risk_logistic_base | 13/27, 1.70 | 6/26, 1.00 | 6/26, 1.00 | 7/26, 1.12 | 8/26, 1.15 |
| risk_logistic_base_dealer | 16/27, 1.81 | 7/26, 1.50 | 7/26, 1.12 | 8/26, 1.62 | 8/26, 1.35 |
