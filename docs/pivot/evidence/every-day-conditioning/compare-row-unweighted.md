Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the reference `risk_gbm+every_day+gate+settle+h41+iorb` and `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`.

| cell | onsets | reference | row | recall difference (90% interval) |
|---|---|---|---|---|
| all | 26 | 16 | 17 | +0.0385 [-0.0667, +0.1540] |
| year 2018 | 4 | 0 | 0 | +0.0000 (no interval) |
| year 2019 | 13 | 11 | 12 | +0.0769 [+0.0000, +0.2105] |
| year 2020 | 2 | 2 | 1 | -0.5000 (no interval) |
| year 2021 | 0 | 0 | 0 | - |
| year 2022 | 0 | 0 | 0 | - |
| year 2023 | 0 | 0 | 0 | - |
| year 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| year 2025 | 5 | 3 | 4 | +0.2000 (no interval) |
| regime 2018-19 | 17 | 11 | 12 | +0.0588 [+0.0000, +0.1667] |
| regime 2020 | 2 | 2 | 1 | -0.5000 (no interval) |
| regime 2021-23 | 0 | 0 | 0 | - |
| regime 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 3 | 4 | +0.2000 (no interval) |
| day type month_end | 6 | 4 | 4 | +0.0000 (no interval) |
| day type ordinary | 12 | 7 | 7 | +0.0000 [-0.1818, +0.2143] |
| day type quarter_end | 3 | 2 | 2 | +0.0000 (no interval) |
| day type tax_date | 5 | 3 | 4 | +0.2000 (no interval) |

Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the reference `risk_gbm+every_day+gate+settle+h41+iorb` and `risk_gbm+every_day+gate+settle+h41+iorb+tailcap50`.

| cell | onsets | reference | row | recall difference (90% interval) |
|---|---|---|---|---|
| all | 26 | 16 | 14 | -0.0769 [-0.2222, +0.0556] |
| year 2018 | 4 | 0 | 0 | +0.0000 (no interval) |
| year 2019 | 13 | 11 | 10 | -0.0769 [-0.2147, +0.0000] |
| year 2020 | 2 | 2 | 0 | -1.0000 (no interval) |
| year 2021 | 0 | 0 | 0 | - |
| year 2022 | 0 | 0 | 0 | - |
| year 2023 | 0 | 0 | 0 | - |
| year 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| year 2025 | 5 | 3 | 4 | +0.2000 (no interval) |
| regime 2018-19 | 17 | 11 | 10 | -0.0588 [-0.1670, +0.0000] |
| regime 2020 | 2 | 2 | 0 | -1.0000 (no interval) |
| regime 2021-23 | 0 | 0 | 0 | - |
| regime 2024 | 2 | 0 | 0 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 3 | 4 | +0.2000 (no interval) |
| day type month_end | 6 | 4 | 4 | +0.0000 (no interval) |
| day type ordinary | 12 | 7 | 4 | -0.2500 [-0.5000, +0.0000] |
| day type quarter_end | 3 | 2 | 2 | +0.0000 (no interval) |
| day type tax_date | 5 | 3 | 4 | +0.2000 (no interval) |

Table 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| calendar_climatology | 198(126); 9/27; 4.67 | 196(127); 10/26; 4.88 | 196(128); 10/26; 4.92 | 196(129); 10/26; 4.96 | 196(130); 10/26; 5.00 |
| persistence_logistic | 133(72); 4/27; 2.67 | 170(89); 6/26; 3.42 | 120(73); 6/26; 2.81 | 141(82); 6/26; 3.15 | 127(73); 5/26; 2.81 |
| risk_gbm+every_day+gate+settle+h41+iorb | 68(22); 13/27; 0.81 | 96(43); 10/26; 1.65 | 93(47); 9/26; 1.81 | 93(41); 10/26; 1.58 | 123(61); 12/26; 2.35 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap50 | 76(35); 13/27; 1.30 | 63(25); 11/26; 0.96 | 63(28); 10/26; 1.08 | 64(27); 10/26; 1.04 | 62(26); 11/26; 1.00 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 68(27); 13/27; 1.00 | 57(20); 11/26; 0.77 | 70(35); 10/26; 1.35 | 73(34); 11/26; 1.31 | 77(35); 13/26; 1.35 |

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
