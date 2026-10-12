Table 1. +5 bp onsets flagged at some lead 1 to 5, by cell: the parent `risk_gbm+every_day+gate+settle+h41+iorb` and each variant.

| cell | onsets | parent | state_platt (recall difference, 90% interval) | state_shrunk (recall difference, 90% interval) |
|---|---|---|---|---|
| all | 26 | 19 | 18 (-0.0385 [-0.1111, +0.0000]) | 18 (-0.0385 [-0.1154, +0.0000]) |
| year 2018 | 4 | 0 | 0 (+0.0000 (no interval)) | 0 (+0.0000 (no interval)) |
| year 2019 | 13 | 13 | 13 (+0.0000 [+0.0000, +0.0000]) | 13 (+0.0000 (no interval)) |
| year 2020 | 2 | 2 | 2 (+0.0000 (no interval)) | 2 (+0.0000 (no interval)) |
| year 2021 | 0 | 0 | 0 (-) | 0 (-) |
| year 2022 | 0 | 0 | 0 (-) | 0 (-) |
| year 2023 | 0 | 0 | 0 (-) | 0 (-) |
| year 2024 | 2 | 0 | 0 (+0.0000 (no interval)) | 0 (+0.0000 (no interval)) |
| year 2025 | 5 | 4 | 3 (-0.2000 (no interval)) | 3 (-0.2000 (no interval)) |
| regime 2018-19 | 17 | 13 | 13 (+0.0000 [+0.0000, +0.0000]) | 13 (+0.0000 [+0.0000, +0.0000]) |
| regime 2020 | 2 | 2 | 2 (+0.0000 (no interval)) | 2 (+0.0000 (no interval)) |
| regime 2021-23 | 0 | 0 | 0 (-) | 0 (-) |
| regime 2024 | 2 | 0 | 0 (+0.0000 (no interval)) | 0 (+0.0000 (no interval)) |
| regime 2025-26 | 5 | 4 | 3 (-0.2000 (no interval)) | 3 (-0.2000 (no interval)) |
| day type month_end | 6 | 4 | 4 (+0.0000 (no interval)) | 4 (+0.0000 (no interval)) |
| day type ordinary | 12 | 9 | 9 (+0.0000 [+0.0000, +0.0000]) | 9 (+0.0000 [+0.0000, +0.0000]) |
| day type quarter_end | 3 | 2 | 2 (+0.0000 (no interval)) | 2 (+0.0000 (no interval)) |
| day type tax_date | 5 | 4 | 3 (-0.2000 (no interval)) | 3 (-0.2000 (no interval)) |

Table 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | 177(95); 14/27; 3.52 | 164(86); 12/26; 3.31 | 165(90); 11/26; 3.46 | 165(90); 12/26; 3.46 | 165(91); 15/26; 3.50 |
| risk_gbm+every_day+gate+settle+h41+iorb+state_platt | 169(89); 12/27; 3.30 | 193(113); 12/26; 4.35 | 173(100); 11/26; 3.85 | 177(103); 12/26; 3.96 | 160(93); 14/26; 3.58 |
| risk_gbm+every_day+gate+settle+h41+iorb+state_shrunk | 171(88); 12/27; 3.26 | 176(98); 12/26; 3.77 | 167(92); 11/26; 3.54 | 182(101); 12/26; 3.88 | 169(93); 14/26; 3.58 |

Table 3 (state_platt). Paired Brier difference against the parent, +5 bp (positive favours the variant: the parent's squared error minus the variant's), 90% interval, h = 1: all days, by regime and by pressure-day type.

| cell | days | difference |
|---|---|---|
| all | 1873 | -0.0029 [-0.0062, +0.0008] |
| regime 2018-19 | 375 | +0.0050 [-0.0056, +0.0174] |
| regime 2020 | 251 | -0.0157 [-0.0235, -0.0060] |
| regime 2021-23 | 748 | -0.0084 [-0.0102, -0.0067] |
| regime 2024 | 250 | +0.0007 [-0.0046, +0.0073] |
| regime 2025-26 | 249 | +0.0112 [+0.0019, +0.0220] |
| day_type month_end | 150 | -0.0160 [-0.0269, -0.0052] |
| day_type ordinary | 1603 | -0.0011 [-0.0039, +0.0022] |
| day_type quarter_end | 31 | -0.0167 [-0.0444, +0.0106] |
| day_type tax_date | 89 | -0.0085 [-0.0275, +0.0122] |

Table 3 (state_shrunk). Paired Brier difference against the parent, +5 bp (positive favours the variant: the parent's squared error minus the variant's), 90% interval, h = 1: all days, by regime and by pressure-day type.

| cell | days | difference |
|---|---|---|
| all | 1873 | +0.0029 [-0.0001, +0.0062] |
| regime 2018-19 | 375 | +0.0050 [-0.0056, +0.0180] |
| regime 2020 | 251 | -0.0043 [-0.0128, +0.0043] |
| regime 2021-23 | 748 | -0.0002 [-0.0006, +0.0001] |
| regime 2024 | 250 | +0.0066 [+0.0003, +0.0157] |
| regime 2025-26 | 249 | +0.0128 [+0.0033, +0.0247] |
| day_type month_end | 150 | -0.0042 [-0.0155, +0.0076] |
| day_type ordinary | 1603 | +0.0040 [+0.0012, +0.0068] |
| day_type quarter_end | 31 | -0.0131 [-0.0431, +0.0145] |
| day_type tax_date | 89 | +0.0018 [-0.0159, +0.0222] |
