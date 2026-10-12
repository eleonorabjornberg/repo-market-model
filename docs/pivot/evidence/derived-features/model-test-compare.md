Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the parent `risk_gbm+settle+h41+dist_roll+every_day` and the row `risk_gbm+settle+h41+dist_roll+every_day+lagpress`.

| cell | onsets | parent | row | recall difference (90% interval) |
|---|---|---|---|---|
| all | 26 | 19 | 17 | -0.0769 [-0.1714, +0.0000] |
| year 2018 | 4 | 0 | 0 | +0.0000 (no interval) |
| year 2019 | 13 | 13 | 12 | -0.0769 [-0.2000, +0.0000] |
| year 2020 | 2 | 1 | 0 | -0.5000 (no interval) |
| year 2021 | 0 | 0 | 0 | - |
| year 2022 | 0 | 0 | 0 | - |
| year 2023 | 0 | 0 | 0 | - |
| year 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| year 2025 | 5 | 5 | 5 | +0.0000 (no interval) |
| regime 2018-19 | 17 | 13 | 12 | -0.0588 [-0.1667, +0.0000] |
| regime 2020 | 2 | 1 | 0 | -0.5000 (no interval) |
| regime 2021-23 | 0 | 0 | 0 | - |
| regime 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 5 | 5 | +0.0000 (no interval) |
| day type month_end | 6 | 4 | 4 | +0.0000 (no interval) |
| day type ordinary | 12 | 9 | 7 | -0.1667 [-0.3333, +0.0000] |
| day type quarter_end | 3 | 2 | 2 | +0.0000 (no interval) |
| day type tax_date | 5 | 4 | 4 | +0.0000 (no interval) |

Table 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm+settle+h41+dist_roll+every_day | 235(139); 16/27; 5.15 | 206(113); 15/26; 4.35 | 197(114); 10/26; 4.38 | 188(107); 12/26; 4.12 | 184(105); 14/26; 4.04 |
| risk_gbm+settle+h41+dist_roll+every_day+lagpress | 195(100); 15/27; 3.70 | 167(88); 14/26; 3.38 | 174(100); 9/26; 3.85 | 159(86); 10/26; 3.31 | 161(87); 13/26; 3.35 |

Table 3. Paired Brier difference against the parent, +5 bp (the parent's squared error minus the row's, so positive favours the row), 90% interval, h = 1: all days, by regime and by pressure-day type.

| cell | days | difference |
|---|---|---|
| all | 1873 | +0.0015 [-0.0007, +0.0039] |
| regime 2018-19 | 375 | +0.0006 [-0.0097, +0.0117] |
| regime 2020 | 251 | +0.0064 [+0.0037, +0.0093] |
| regime 2021-23 | 748 | -0.0002 [-0.0003, -0.0000] |
| regime 2024 | 250 | +0.0015 [+0.0004, +0.0031] |
| regime 2025-26 | 249 | +0.0029 [-0.0024, +0.0087] |
| day_type month_end | 150 | +0.0023 [+0.0002, +0.0056] |
| day_type ordinary | 1603 | +0.0015 [-0.0010, +0.0043] |
| day_type quarter_end | 31 | +0.0000 [+0.0000, +0.0000] |
| day_type tax_date | 89 | +0.0000 [+0.0000, +0.0000] |
