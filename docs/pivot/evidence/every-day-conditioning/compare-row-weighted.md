Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the reference `risk_gbm+every_day+gate+settle+h41+iorb` and `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`.

| cell | onsets | reference | row | recall difference (90% interval) |
|---|---|---|---|---|
| all | 26 | 19 | 18 | -0.0385 [-0.1111, +0.0000] |
| year 2018 | 4 | 0 | 0 | +0.0000 (no interval) |
| year 2019 | 13 | 13 | 13 | +0.0000 [+0.0000, +0.0000] |
| year 2020 | 2 | 2 | 1 | -0.5000 (no interval) |
| year 2021 | 0 | 0 | 0 | - |
| year 2022 | 0 | 0 | 0 | - |
| year 2023 | 0 | 0 | 0 | - |
| year 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| year 2025 | 5 | 4 | 4 | +0.0000 (no interval) |
| regime 2018-19 | 17 | 13 | 13 | +0.0000 [+0.0000, +0.0000] |
| regime 2020 | 2 | 2 | 1 | -0.5000 (no interval) |
| regime 2021-23 | 0 | 0 | 0 | - |
| regime 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 4 | 4 | +0.0000 (no interval) |
| day type month_end | 6 | 4 | 4 | +0.0000 (no interval) |
| day type ordinary | 12 | 9 | 8 | -0.0833 [-0.2222, +0.0000] |
| day type quarter_end | 3 | 2 | 2 | +0.0000 (no interval) |
| day type tax_date | 5 | 4 | 4 | +0.0000 (no interval) |

Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the reference `risk_gbm+every_day+gate+settle+h41+iorb` and `risk_gbm+every_day+gate+settle+h41+iorb+tailcap50`.

| cell | onsets | reference | row | recall difference (90% interval) |
|---|---|---|---|---|
| all | 26 | 19 | 14 | -0.1923 [-0.3478, -0.0500] |
| year 2018 | 4 | 0 | 0 | +0.0000 (no interval) |
| year 2019 | 13 | 13 | 10 | -0.2308 [-0.4444, +0.0000] |
| year 2020 | 2 | 2 | 0 | -1.0000 (no interval) |
| year 2021 | 0 | 0 | 0 | - |
| year 2022 | 0 | 0 | 0 | - |
| year 2023 | 0 | 0 | 0 | - |
| year 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| year 2025 | 5 | 4 | 4 | +0.0000 (no interval) |
| regime 2018-19 | 17 | 13 | 10 | -0.1765 [-0.3333, +0.0000] |
| regime 2020 | 2 | 2 | 0 | -1.0000 (no interval) |
| regime 2021-23 | 0 | 0 | 0 | - |
| regime 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 4 | 4 | +0.0000 (no interval) |
| day type month_end | 6 | 4 | 4 | +0.0000 (no interval) |
| day type ordinary | 12 | 9 | 4 | -0.4167 [-0.6667, -0.1429] |
| day type quarter_end | 3 | 2 | 2 | +0.0000 (no interval) |
| day type tax_date | 5 | 4 | 4 | +0.0000 (no interval) |

Table 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| calendar_climatology | 258(174); 12/27; 6.44 | 213(144); 10/26; 5.54 | 213(145); 10/26; 5.58 | 213(146); 10/26; 5.62 | 213(147); 10/26; 5.65 |
| persistence_logistic | 286(183); 11/27; 6.78 | 215(124); 7/26; 4.77 | 243(154); 10/26; 5.92 | 222(140); 8/26; 5.38 | 199(118); 8/26; 4.54 |
| risk_gbm+every_day+gate+settle+h41+iorb | 178(96); 14/27; 3.56 | 163(85); 12/26; 3.27 | 163(89); 11/26; 3.42 | 165(90); 12/26; 3.46 | 165(91); 15/26; 3.50 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap50 | 78(37); 13/27; 1.37 | 63(25); 11/26; 0.96 | 75(36); 10/26; 1.38 | 68(30); 10/26; 1.15 | 67(30); 11/26; 1.15 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 92(48); 14/27; 1.78 | 84(39); 12/26; 1.50 | 95(51); 11/26; 1.96 | 89(46); 12/26; 1.77 | 93(48); 14/26; 1.85 |

Table 3. Paired Brier difference of `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75` against `risk_gbm+every_day+gate+settle+h41+iorb`, +5 bp (negative favours the row), 90% interval, h = 1: all days, by regime and by pressure-day type.

| cell | days | difference |
|---|---|---|
| all | 1873 | -0.0073 [-0.0150, -0.0005] |
| regime 2018-19 | 375 | -0.0400 [-0.0716, -0.0116] |
| regime 2020 | 251 | +0.0072 [+0.0000, +0.0204] |
| regime 2021-23 | 748 | +0.0001 [+0.0000, +0.0002] |
| regime 2024 | 250 | +0.0072 [+0.0009, +0.0162] |
| regime 2025-26 | 249 | -0.0090 [-0.0285, +0.0053] |
| day_type month_end | 150 | -0.0057 [-0.0123, +0.0000] |
| day_type ordinary | 1603 | -0.0080 [-0.0167, -0.0004] |
| day_type quarter_end | 31 | +0.0000 [+0.0000, +0.0000] |
| day_type tax_date | 89 | +0.0000 [+0.0000, +0.0000] |

Table 3. Paired Brier difference of `risk_gbm+every_day+gate+settle+h41+iorb+tailcap50` against `risk_gbm+every_day+gate+settle+h41+iorb`, +5 bp (negative favours the row), 90% interval, h = 1: all days, by regime and by pressure-day type.

| cell | days | difference |
|---|---|---|
| all | 1873 | -0.0082 [-0.0165, -0.0017] |
| regime 2018-19 | 375 | -0.0423 [-0.0757, -0.0144] |
| regime 2020 | 251 | +0.0032 [-0.0064, +0.0165] |
| regime 2021-23 | 748 | +0.0001 [+0.0000, +0.0002] |
| regime 2024 | 250 | +0.0072 [+0.0009, +0.0163] |
| regime 2025-26 | 249 | -0.0090 [-0.0298, +0.0054] |
| day_type month_end | 150 | -0.0057 [-0.0129, +0.0000] |
| day_type ordinary | 1603 | -0.0091 [-0.0184, -0.0015] |
| day_type quarter_end | 31 | +0.0000 [+0.0000, +0.0000] |
| day_type tax_date | 89 | +0.0000 [+0.0000, +0.0000] |
