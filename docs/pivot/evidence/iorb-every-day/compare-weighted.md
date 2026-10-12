Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the parent `risk_gbm+every_day+gate+settle+h41` and the row `risk_gbm+every_day+gate+settle+h41+iorb`.

| cell | onsets | parent | row | recall difference (90% interval) |
|---|---|---|---|---|
| all | 26 | 18 | 19 | +0.0385 [+0.0000, +0.1111] |
| year 2018 | 4 | 0 | 0 | +0.0000 (no interval) |
| year 2019 | 13 | 13 | 13 | +0.0000 [+0.0000, +0.0000] |
| year 2020 | 2 | 1 | 2 | +0.5000 (no interval) |
| year 2021 | 0 | 0 | 0 | - |
| year 2022 | 0 | 0 | 0 | - |
| year 2023 | 0 | 0 | 0 | - |
| year 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| year 2025 | 5 | 4 | 4 | +0.0000 (no interval) |
| regime 2018-19 | 17 | 13 | 13 | +0.0000 [+0.0000, +0.0000] |
| regime 2020 | 2 | 1 | 2 | +0.5000 (no interval) |
| regime 2021-23 | 0 | 0 | 0 | - |
| regime 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 4 | 4 | +0.0000 (no interval) |
| day type month_end | 6 | 4 | 4 | +0.0000 (no interval) |
| day type ordinary | 12 | 8 | 9 | +0.0833 [+0.0000, +0.2222] |
| day type quarter_end | 3 | 2 | 2 | +0.0000 (no interval) |
| day type tax_date | 5 | 4 | 4 | +0.0000 (no interval) |

Table 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41 | 172(92); 13/27; 3.41 | 163(85); 12/26; 3.27 | 163(89); 11/26; 3.42 | 165(90); 12/26; 3.46 | 165(91); 15/26; 3.50 |
| risk_gbm+every_day+gate+settle+h41+iorb | 178(96); 14/27; 3.56 | 163(85); 12/26; 3.27 | 163(89); 11/26; 3.42 | 165(90); 12/26; 3.46 | 165(91); 15/26; 3.50 |

Table 3. Paired Brier difference against the parent, +5 bp (the parent's squared error minus the row's, so positive favours the row), 90% interval, h = 1: all days, by regime and by pressure-day type.

| cell | days | difference |
|---|---|---|
| all | 1873 | +0.0001 [-0.0014, +0.0017] |
| regime 2018-19 | 375 | +0.0022 [-0.0011, +0.0073] |
| regime 2020 | 251 | +0.0041 [+0.0000, +0.0111] |
| regime 2021-23 | 748 | +0.0000 [+0.0000, +0.0000] |
| regime 2024 | 250 | -0.0043 [-0.0113, +0.0000] |
| regime 2025-26 | 249 | -0.0021 [-0.0045, +0.0000] |
| day_type month_end | 150 | -0.0000 [-0.0001, +0.0000] |
| day_type ordinary | 1603 | +0.0002 [-0.0017, +0.0020] |
| day_type quarter_end | 31 | +0.0000 [+0.0000, +0.0000] |
| day_type tax_date | 89 | +0.0000 [+0.0000, +0.0000] |
