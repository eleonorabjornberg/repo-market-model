
### Tier 1, 3 and 5, weighted rule

| row | start-up rule | onsets flagged at leads 1 to 5, recall [90%], false alarms per onset pooled over the leads (limit 2) | tier 1 | leads 3 to 5: flagged, recall [90%] | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | 19 of 26, 0.731 [0.560, 0.889], 3.46 | no | 15 of 26, 0.577 [0.385, 0.762] | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 21 of 26, 0.808 [0.667, 0.933], 3.94 | no | 15 of 26, 0.577 [0.385, 0.762] | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 19 of 26, 0.731 [0.560, 0.889], 3.58 | no | 15 of 26, 0.577 [0.385, 0.762] | no | no | no |
| risk_gbm+settle+h41 | declared | 14 of 26, 0.538 [0.353, 0.710], 1.44 | yes | 11 of 26, 0.423 [0.250, 0.607] | no | no | no |
| risk_gbm+settle+h41 | a: climatology rate | 16 of 26, 0.615 [0.435, 0.774], 1.92 | yes | 11 of 26, 0.423 [0.250, 0.607] | no | no | no |
| risk_gbm+settle+h41 | b: fixed 0.2 | 14 of 26, 0.538 [0.353, 0.710], 1.56 | yes | 11 of 26, 0.423 [0.250, 0.607] | no | no | no |
| ngboost_laplace | declared | 17 of 26, 0.654 [0.467, 0.826], 2.34 | no | 12 of 26, 0.462 [0.273, 0.650] | no | no | no |
| ngboost_laplace | a: climatology rate | 17 of 26, 0.654 [0.467, 0.826], 2.91 | no | 12 of 26, 0.462 [0.273, 0.650] | no | no | no |
| ngboost_laplace | b: fixed 0.2 | 17 of 26, 0.654 [0.467, 0.826], 2.34 | no | 12 of 26, 0.462 [0.273, 0.650] | no | no | no |
| calendar_climatology | declared | 12 of 26, 0.462 [0.286, 0.667], 3.90 | no | 10 of 26, 0.385 [0.212, 0.576] | no | no | no |
| calendar_climatology | a: climatology rate | 14 of 26, 0.538 [0.360, 0.727], 5.71 | no | 10 of 26, 0.385 [0.212, 0.576] | no | no | no |
| calendar_climatology | b: fixed 0.2 | 12 of 26, 0.462 [0.286, 0.667], 3.98 | no | 10 of 26, 0.385 [0.212, 0.576] | no | no | no |
| persistence_logistic | declared | 12 of 26, 0.462 [0.273, 0.650], 4.09 | no | 11 of 26, 0.423 [0.256, 0.600] | no | no | no |
| persistence_logistic | a: climatology rate | 14 of 26, 0.538 [0.346, 0.720], 6.50 | no | 11 of 26, 0.423 [0.256, 0.600] | no | no | no |
| persistence_logistic | b: fixed 0.2 | 12 of 26, 0.462 [0.273, 0.650], 4.43 | no | 11 of 26, 0.423 [0.256, 0.600] | no | no | no |

### Tier 1 per lead, +5 bp, weighted rule: onsets flagged of the 26 and recall [90%]; 2018 onsets flagged of 4; weighted false alarms per onset (limit 2)

| row | start-up rule | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | 14/26 0.538 [0.370, 0.708]; 2018 0/4; 1.63 | 12/26 0.462 [0.276, 0.640]; 2018 0/4; 1.39 | 11/26 0.423 [0.241, 0.607]; 2018 0/4; 1.44 | 12/26 0.462 [0.261, 0.667]; 2018 0/4; 1.50 | 15/26 0.577 [0.393, 0.769]; 2018 0/4; 1.64 |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 14/26 0.538 [0.375, 0.704]; 2018 0/4; 1.63 | 14/26 0.538 [0.361, 0.704]; 2018 2/4; 1.91 | 11/26 0.423 [0.241, 0.611]; 2018 0/4; 1.44 | 12/26 0.462 [0.273, 0.650]; 2018 0/4; 1.50 | 15/26 0.577 [0.389, 0.760]; 2018 0/4; 1.64 |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 14/26 0.538 [0.368, 0.706]; 2018 0/4; 1.63 | 12/26 0.462 [0.292, 0.640]; 2018 0/4; 1.47 | 11/26 0.423 [0.250, 0.613]; 2018 0/4; 1.56 | 12/26 0.462 [0.261, 0.667]; 2018 0/4; 1.65 | 15/26 0.577 [0.385, 0.762]; 2018 0/4; 1.80 |
| risk_gbm+settle+h41 | declared | 13/26 0.500 [0.320, 0.667]; 2018 0/4; 0.75 | 11/26 0.423 [0.250, 0.600]; 2018 0/4; 0.58 | 10/26 0.385 [0.212, 0.576]; 2018 0/4; 0.88 | 10/26 0.385 [0.207, 0.571]; 2018 0/4; 0.68 | 11/26 0.423 [0.250, 0.615]; 2018 0/4; 0.76 |
| risk_gbm+settle+h41 | a: climatology rate | 13/26 0.500 [0.320, 0.676]; 2018 0/4; 0.75 | 13/26 0.500 [0.333, 0.679]; 2018 2/4; 1.10 | 10/26 0.385 [0.200, 0.571]; 2018 0/4; 0.88 | 10/26 0.385 [0.210, 0.565]; 2018 0/4; 0.68 | 11/26 0.423 [0.242, 0.600]; 2018 0/4; 0.76 |
| risk_gbm+settle+h41 | b: fixed 0.2 | 13/26 0.500 [0.320, 0.682]; 2018 0/4; 0.75 | 11/26 0.423 [0.250, 0.607]; 2018 0/4; 0.65 | 10/26 0.385 [0.208, 0.565]; 2018 0/4; 1.00 | 10/26 0.385 [0.211, 0.565]; 2018 0/4; 0.84 | 11/26 0.423 [0.242, 0.607]; 2018 0/4; 0.91 |
| ngboost_laplace | declared | 15/26 0.577 [0.375, 0.758]; 2018 0/4; 1.41 | 7/26 0.269 [0.129, 0.429]; 2018 0/4; 1.42 | 9/26 0.346 [0.184, 0.517]; 2018 0/4; 1.29 | 9/26 0.346 [0.182, 0.500]; 2018 0/4; 1.60 | 10/26 0.385 [0.214, 0.556]; 2018 0/4; 1.73 |
| ngboost_laplace | a: climatology rate | 15/26 0.577 [0.400, 0.750]; 2018 0/4; 1.41 | 7/26 0.269 [0.130, 0.423]; 2018 0/4; 2.00 | 9/26 0.346 [0.182, 0.520]; 2018 0/4; 1.29 | 9/26 0.346 [0.182, 0.501]; 2018 0/4; 1.60 | 10/26 0.385 [0.217, 0.550]; 2018 0/4; 1.73 |
| ngboost_laplace | b: fixed 0.2 | 15/26 0.577 [0.385, 0.750]; 2018 0/4; 1.41 | 7/26 0.269 [0.120, 0.423]; 2018 0/4; 1.42 | 9/26 0.346 [0.182, 0.529]; 2018 0/4; 1.29 | 9/26 0.346 [0.190, 0.500]; 2018 0/4; 1.60 | 10/26 0.385 [0.217, 0.571]; 2018 0/4; 1.73 |

### The rows against the benchmarks under the same start-up rule, weighted rule: onsets flagged at some lead, difference in recall (90% interval); all and 2018

| row | start-up rule | vs calendar_climatology: all | 2018 | vs persistence_logistic: all | 2018 |
|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | +0.269 [+0.107, +0.440] | 0.000 (no interval) | +0.269 [+0.115, +0.433] | 0.000 (no interval) |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | +0.269 [+0.115, +0.440] | 0.000 (no interval) | +0.269 [+0.115, +0.435] | 0.000 (no interval) |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | +0.269 [+0.111, +0.441] | 0.000 (no interval) | +0.269 [+0.115, +0.438] | 0.000 (no interval) |
| risk_gbm+settle+h41 | declared | +0.077 [-0.129, +0.269] | 0.000 (no interval) | +0.077 [-0.139, +0.300] | 0.000 (no interval) |
| risk_gbm+settle+h41 | a: climatology rate | +0.077 [-0.133, +0.286] | 0.000 (no interval) | +0.077 [-0.143, +0.296] | 0.000 (no interval) |
| risk_gbm+settle+h41 | b: fixed 0.2 | +0.077 [-0.118, +0.265] | 0.000 (no interval) | +0.077 [-0.150, +0.300] | 0.000 (no interval) |
| ngboost_laplace | declared | +0.192 [+0.000, +0.367] | 0.000 (no interval) | +0.192 [+0.000, +0.406] | 0.000 (no interval) |
| ngboost_laplace | a: climatology rate | +0.115 [-0.107, +0.346] | -0.500 (no interval) | +0.115 [-0.120, +0.333] | -0.500 (no interval) |
| ngboost_laplace | b: fixed 0.2 | +0.192 [+0.000, +0.381] | 0.000 (no interval) | +0.192 [+0.000, +0.400] | 0.000 (no interval) |

### Onsets flagged at some lead, by year (of the onsets of the year), weighted rule; difference from the declared judge with its 90% interval

| row | start-up rule | all | year 2018 | year 2019 | year 2020 | year 2021 | year 2022 | year 2023 | year 2024 | year 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | 19/26 | 0/4 | 13/13 | 2/2 | 0/0 | 0/0 | 0/0 | 0/2 | 4/5 |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 21/26 (+0.077 [+0.000, +0.185]) | 2/4 (0.500 (no interval)) | 13/13 (+0.000 [+0.000, +0.000]) | 2/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 19/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 13/13 (+0.000 [+0.000, +0.000]) | 2/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| risk_gbm+settle+h41 | declared | 14/26 | 0/4 | 10/13 | 0/2 | 0/0 | 0/0 | 0/0 | 0/2 | 4/5 |
| risk_gbm+settle+h41 | a: climatology rate | 16/26 (+0.077 [+0.000, +0.185]) | 2/4 (0.500 (no interval)) | 10/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| risk_gbm+settle+h41 | b: fixed 0.2 | 14/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 10/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| ngboost_laplace | declared | 17/26 | 0/4 | 12/13 | 0/2 | 0/0 | 0/0 | 0/0 | 0/2 | 5/5 |
| ngboost_laplace | a: climatology rate | 17/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 12/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 5/5 (0.000 (no interval)) |
| ngboost_laplace | b: fixed 0.2 | 17/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 12/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 5/5 (0.000 (no interval)) |
| calendar_climatology | declared | 12/26 | 0/4 | 12/13 | 0/2 | 0/0 | 0/0 | 0/0 | 0/2 | 0/5 |
| calendar_climatology | a: climatology rate | 14/26 (+0.077 [+0.000, +0.188]) | 2/4 (0.500 (no interval)) | 12/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |
| calendar_climatology | b: fixed 0.2 | 12/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 12/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |
| persistence_logistic | declared | 12/26 | 0/4 | 11/13 | 1/2 | 0/0 | 0/0 | 0/0 | 0/2 | 0/5 |
| persistence_logistic | a: climatology rate | 14/26 (+0.077 [+0.000, +0.192]) | 2/4 (0.500 (no interval)) | 11/13 (+0.000 [+0.000, +0.000]) | 1/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |
| persistence_logistic | b: fixed 0.2 | 12/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 11/13 (+0.000 [+0.000, +0.000]) | 1/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |

### Recall difference from the declared judge, by regime and day type, weighted rule

| row | start-up rule | day type month_end (6) | day type ordinary (12) | day type quarter_end (3) | day type tax_date (5) | regime 2018-19 (17) | regime 2020 (2) | regime 2021-23 (0) | regime 2024 (2) | regime 2025-26 (5) |
|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.278] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| risk_gbm+settle+h41 | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.286] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| risk_gbm+settle+h41 | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| ngboost_laplace | a: climatology rate | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| ngboost_laplace | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| calendar_climatology | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.286] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| calendar_climatology | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| persistence_logistic | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.278] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| persistence_logistic | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |

### Flags the start-up rule adds against the declared judge, by year, weighted rule: flags (of which not pressure days; onsets), over h = 1 to 5

| row | start-up rule | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | none | 2018: 17 (15; 2) | none | none | none |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | none | 2018: 2 (2; 0) | 2018: 3 (3; 0) | 2018: 4 (4; 0) | 2018: 4 (4; 0) |
| risk_gbm+settle+h41 | a: climatology rate | none | 2018: 17 (15; 2) | none | none | none |
| risk_gbm+settle+h41 | b: fixed 0.2 | none | 2018: 2 (2; 0) | 2018: 3 (3; 0) | 2018: 4 (4; 0) | 2018: 4 (4; 0) |
| ngboost_laplace | a: climatology rate | none | 2018: 15 (15; 0) | none | none | none |
| ngboost_laplace | b: fixed 0.2 | none | none | none | none | none |
| calendar_climatology | a: climatology rate | none | 2018: 61 (58; 2) | none | none | none |
| calendar_climatology | b: fixed 0.2 | 2018: 1 (1; 0) | 2018: 4 (4; 0) | 2018: 5 (5; 0) | 2018: 6 (6; 0) | 2018: 6 (6; 0) |
| persistence_logistic | a: climatology rate | none | 2018: 71 (68; 2) | none | none | none |
| persistence_logistic | b: fixed 0.2 | none | none | none | none | 2018: 9 (9; 0) |

### Tier 1, 3 and 5, flat rule

| row | start-up rule | onsets flagged at leads 1 to 5, recall [90%], false alarms per onset pooled over the leads (limit 2) | tier 1 | leads 3 to 5: flagged, recall [90%] | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | 16 of 26, 0.615 [0.440, 0.786], 4.35 | no | 12 of 26, 0.462 [0.280, 0.652] | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 18 of 26, 0.692 [0.533, 0.846], 4.88 | no | 12 of 26, 0.462 [0.280, 0.652] | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 16 of 26, 0.615 [0.440, 0.786], 4.46 | no | 12 of 26, 0.462 [0.280, 0.652] | no | no | no |
| risk_gbm+settle+h41 | declared | 14 of 26, 0.538 [0.353, 0.710], 2.00 | yes | 11 of 26, 0.423 [0.250, 0.607] | no | no | no |
| risk_gbm+settle+h41 | a: climatology rate | 16 of 26, 0.615 [0.435, 0.774], 2.54 | no | 11 of 26, 0.423 [0.250, 0.607] | no | no | no |
| risk_gbm+settle+h41 | b: fixed 0.2 | 14 of 26, 0.538 [0.353, 0.710], 2.12 | no | 11 of 26, 0.423 [0.250, 0.607] | no | no | no |
| ngboost_laplace | declared | 15 of 26, 0.577 [0.400, 0.759], 4.38 | no | 9 of 26, 0.346 [0.174, 0.536] | no | no | no |
| ngboost_laplace | a: climatology rate | 15 of 26, 0.577 [0.400, 0.759], 4.96 | no | 9 of 26, 0.346 [0.174, 0.536] | no | no | no |
| ngboost_laplace | b: fixed 0.2 | 15 of 26, 0.577 [0.400, 0.759], 4.38 | no | 9 of 26, 0.346 [0.174, 0.536] | no | no | no |
| calendar_climatology | declared | 10 of 26, 0.385 [0.208, 0.588], 5.38 | no | 10 of 26, 0.385 [0.212, 0.576] | no | no | no |
| calendar_climatology | a: climatology rate | 12 of 26, 0.462 [0.286, 0.656], 7.50 | no | 10 of 26, 0.385 [0.212, 0.576] | no | no | no |
| calendar_climatology | b: fixed 0.2 | 10 of 26, 0.385 [0.208, 0.588], 5.46 | no | 10 of 26, 0.385 [0.212, 0.576] | no | no | no |
| persistence_logistic | declared | 7 of 26, 0.269 [0.111, 0.444], 5.73 | no | 7 of 26, 0.269 [0.107, 0.448] | no | no | no |
| persistence_logistic | a: climatology rate | 9 of 26, 0.346 [0.167, 0.535], 8.35 | no | 7 of 26, 0.269 [0.107, 0.448] | no | no | no |
| persistence_logistic | b: fixed 0.2 | 7 of 26, 0.269 [0.111, 0.444], 6.08 | no | 7 of 26, 0.269 [0.107, 0.448] | no | no | no |

### Tier 1 per lead, +5 bp, flat rule: onsets flagged of the 26 and recall [90%]; 2018 onsets flagged of 4; flat false alarms per onset (limit 2)

| row | start-up rule | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | 13/26 0.500 [0.320, 0.679]; 2018 0/4; 0.85 | 10/26 0.385 [0.211, 0.552]; 2018 0/4; 1.65 | 9/26 0.346 [0.176, 0.524]; 2018 0/4; 1.81 | 10/26 0.385 [0.207, 0.571]; 2018 0/4; 1.58 | 12/26 0.462 [0.280, 0.652]; 2018 0/4; 2.35 |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 13/26 0.500 [0.333, 0.679]; 2018 0/4; 0.85 | 12/26 0.462 [0.294, 0.630]; 2018 2/4; 2.23 | 9/26 0.346 [0.179, 0.520]; 2018 0/4; 1.81 | 10/26 0.385 [0.208, 0.567]; 2018 0/4; 1.58 | 12/26 0.462 [0.278, 0.652]; 2018 0/4; 2.35 |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 13/26 0.500 [0.320, 0.680]; 2018 0/4; 0.85 | 10/26 0.385 [0.222, 0.560]; 2018 0/4; 1.73 | 9/26 0.346 [0.179, 0.526]; 2018 0/4; 1.92 | 10/26 0.385 [0.200, 0.563]; 2018 0/4; 1.73 | 12/26 0.462 [0.276, 0.654]; 2018 0/4; 2.50 |
| risk_gbm+settle+h41 | declared | 13/26 0.500 [0.320, 0.667]; 2018 0/4; 1.35 | 11/26 0.423 [0.250, 0.600]; 2018 0/4; 0.96 | 10/26 0.385 [0.212, 0.576]; 2018 0/4; 1.08 | 10/26 0.385 [0.207, 0.571]; 2018 0/4; 1.04 | 11/26 0.423 [0.250, 0.615]; 2018 0/4; 1.04 |
| risk_gbm+settle+h41 | a: climatology rate | 13/26 0.500 [0.320, 0.676]; 2018 0/4; 1.35 | 13/26 0.500 [0.333, 0.679]; 2018 2/4; 1.54 | 10/26 0.385 [0.200, 0.571]; 2018 0/4; 1.08 | 10/26 0.385 [0.210, 0.565]; 2018 0/4; 1.04 | 11/26 0.423 [0.242, 0.600]; 2018 0/4; 1.04 |
| risk_gbm+settle+h41 | b: fixed 0.2 | 13/26 0.500 [0.320, 0.682]; 2018 0/4; 1.35 | 11/26 0.423 [0.250, 0.607]; 2018 0/4; 1.04 | 10/26 0.385 [0.208, 0.565]; 2018 0/4; 1.19 | 10/26 0.385 [0.211, 0.565]; 2018 0/4; 1.19 | 11/26 0.423 [0.242, 0.607]; 2018 0/4; 1.19 |
| ngboost_laplace | declared | 10/26 0.385 [0.212, 0.552]; 2018 0/4; 1.69 | 3/26 0.115 [0.000, 0.229]; 2018 0/4; 1.73 | 3/26 0.115 [0.000, 0.227]; 2018 0/4; 1.42 | 6/26 0.231 [0.087, 0.389]; 2018 0/4; 2.54 | 2/26 0.077 [0.000, 0.171]; 2018 0/4; 1.58 |
| ngboost_laplace | a: climatology rate | 10/26 0.385 [0.214, 0.552]; 2018 0/4; 1.69 | 3/26 0.115 [0.026, 0.231]; 2018 0/4; 2.31 | 3/26 0.115 [0.027, 0.227]; 2018 0/4; 1.42 | 6/26 0.231 [0.086, 0.391]; 2018 0/4; 2.54 | 2/26 0.077 [0.000, 0.167]; 2018 0/4; 1.58 |
| ngboost_laplace | b: fixed 0.2 | 10/26 0.385 [0.219, 0.556]; 2018 0/4; 1.69 | 3/26 0.115 [0.000, 0.238]; 2018 0/4; 1.73 | 3/26 0.115 [0.031, 0.231]; 2018 0/4; 1.42 | 6/26 0.231 [0.083, 0.375]; 2018 0/4; 2.54 | 2/26 0.077 [0.000, 0.179]; 2018 0/4; 1.58 |

### The rows against the benchmarks under the same start-up rule, flat rule: onsets flagged at some lead, difference in recall (90% interval); all and 2018

| row | start-up rule | vs calendar_climatology: all | 2018 | vs persistence_logistic: all | 2018 |
|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | +0.231 [+0.000, +0.423] | 0.000 (no interval) | +0.346 [+0.111, +0.571] | 0.000 (no interval) |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | +0.231 [+0.000, +0.429] | 0.000 (no interval) | +0.346 [+0.111, +0.577] | 0.000 (no interval) |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | +0.231 [+0.000, +0.448] | 0.000 (no interval) | +0.346 [+0.120, +0.579] | 0.000 (no interval) |
| risk_gbm+settle+h41 | declared | +0.154 [-0.067, +0.360] | 0.000 (no interval) | +0.269 [+0.034, +0.500] | 0.000 (no interval) |
| risk_gbm+settle+h41 | a: climatology rate | +0.154 [-0.080, +0.369] | 0.000 (no interval) | +0.269 [+0.000, +0.520] | 0.000 (no interval) |
| risk_gbm+settle+h41 | b: fixed 0.2 | +0.154 [-0.065, +0.353] | 0.000 (no interval) | +0.269 [+0.000, +0.517] | 0.000 (no interval) |
| ngboost_laplace | declared | +0.192 [+0.000, +0.393] | 0.000 (no interval) | +0.308 [+0.077, +0.526] | 0.000 (no interval) |
| ngboost_laplace | a: climatology rate | +0.115 [-0.120, +0.350] | -0.500 (no interval) | +0.231 [-0.033, +0.476] | -0.500 (no interval) |
| ngboost_laplace | b: fixed 0.2 | +0.192 [+0.000, +0.387] | 0.000 (no interval) | +0.308 [+0.080, +0.524] | 0.000 (no interval) |

### Onsets flagged at some lead, by year (of the onsets of the year), flat rule; difference from the declared judge with its 90% interval

| row | start-up rule | all | year 2018 | year 2019 | year 2020 | year 2021 | year 2022 | year 2023 | year 2024 | year 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | declared | 16/26 | 0/4 | 11/13 | 2/2 | 0/0 | 0/0 | 0/0 | 0/2 | 3/5 |
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 18/26 (+0.077 [+0.000, +0.185]) | 2/4 (0.500 (no interval)) | 11/13 (+0.000 [+0.000, +0.000]) | 2/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 3/5 (0.000 (no interval)) |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 16/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 11/13 (+0.000 [+0.000, +0.000]) | 2/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 3/5 (0.000 (no interval)) |
| risk_gbm+settle+h41 | declared | 14/26 | 0/4 | 10/13 | 0/2 | 0/0 | 0/0 | 0/0 | 0/2 | 4/5 |
| risk_gbm+settle+h41 | a: climatology rate | 16/26 (+0.077 [+0.000, +0.185]) | 2/4 (0.500 (no interval)) | 10/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| risk_gbm+settle+h41 | b: fixed 0.2 | 14/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 10/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| ngboost_laplace | declared | 15/26 | 0/4 | 11/13 | 0/2 | 0/0 | 0/0 | 0/0 | 0/2 | 4/5 |
| ngboost_laplace | a: climatology rate | 15/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 11/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| ngboost_laplace | b: fixed 0.2 | 15/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 11/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 4/5 (0.000 (no interval)) |
| calendar_climatology | declared | 10/26 | 0/4 | 10/13 | 0/2 | 0/0 | 0/0 | 0/0 | 0/2 | 0/5 |
| calendar_climatology | a: climatology rate | 12/26 (+0.077 [+0.000, +0.188]) | 2/4 (0.500 (no interval)) | 10/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |
| calendar_climatology | b: fixed 0.2 | 10/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 10/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |
| persistence_logistic | declared | 7/26 | 0/4 | 7/13 | 0/2 | 0/0 | 0/0 | 0/0 | 0/2 | 0/5 |
| persistence_logistic | a: climatology rate | 9/26 (+0.077 [+0.000, +0.192]) | 2/4 (0.500 (no interval)) | 7/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |
| persistence_logistic | b: fixed 0.2 | 7/26 (+0.000 [+0.000, +0.000]) | 0/4 (0.000 (no interval)) | 7/13 (+0.000 [+0.000, +0.000]) | 0/2 (0.000 (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/0 (– (no interval)) | 0/2 (0.000 (no interval)) | 0/5 (0.000 (no interval)) |

### Recall difference from the declared judge, by regime and day type, flat rule

| row | start-up rule | day type month_end (6) | day type ordinary (12) | day type quarter_end (3) | day type tax_date (5) | regime 2018-19 (17) | regime 2020 (2) | regime 2021-23 (0) | regime 2024 (2) | regime 2025-26 (5) |
|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.278] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| risk_gbm+settle+h41 | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.286] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| risk_gbm+settle+h41 | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| ngboost_laplace | a: climatology rate | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| ngboost_laplace | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| calendar_climatology | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.286] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| calendar_climatology | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| persistence_logistic | a: climatology rate | 0.167 (no interval) | +0.083 [+0.000, +0.250] | 0.000 (no interval) | 0.000 (no interval) | +0.118 [+0.000, +0.278] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |
| persistence_logistic | b: fixed 0.2 | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | 0.000 (no interval) | +0.000 [+0.000, +0.000] | 0.000 (no interval) | – (no interval) | 0.000 (no interval) | 0.000 (no interval) |

### Flags the start-up rule adds against the declared judge, by year, flat rule: flags (of which not pressure days; onsets), over h = 1 to 5

| row | start-up rule | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| risk_gbm+every_day+gate+settle+h41+iorb | a: climatology rate | none | 2018: 17 (15; 2) | none | none | none |
| risk_gbm+every_day+gate+settle+h41+iorb | b: fixed 0.2 | none | 2018: 2 (2; 0) | 2018: 3 (3; 0) | 2018: 4 (4; 0) | 2018: 4 (4; 0) |
| risk_gbm+settle+h41 | a: climatology rate | none | 2018: 17 (15; 2) | none | none | none |
| risk_gbm+settle+h41 | b: fixed 0.2 | none | 2018: 2 (2; 0) | 2018: 3 (3; 0) | 2018: 4 (4; 0) | 2018: 4 (4; 0) |
| ngboost_laplace | a: climatology rate | none | 2018: 15 (15; 0) | none | none | none |
| ngboost_laplace | b: fixed 0.2 | none | none | none | none | none |
| calendar_climatology | a: climatology rate | none | 2018: 61 (58; 2) | none | none | none |
| calendar_climatology | b: fixed 0.2 | 2018: 1 (1; 0) | 2018: 4 (4; 0) | 2018: 5 (5; 0) | 2018: 6 (6; 0) | 2018: 6 (6; 0) |
| persistence_logistic | a: climatology rate | none | 2018: 71 (68; 2) | none | none | none |
| persistence_logistic | b: fixed 0.2 | none | none | none | none | 2018: 9 (9; 0) |

### Blocks whose cut-off came from the start-up rule (+5 bp, weighted run): first day, last day, cut-off

* `risk_gbm+every_day+gate+settle+h41+iorb`, a: climatology rate: h = 1: 0 blocks; h = 2: 4 blocks (2018-08-01 to 2018-11-30; first cut-off 0.05263); h = 3: 0 blocks; h = 4: 0 blocks; h = 5: 0 blocks
* `risk_gbm+every_day+gate+settle+h41+iorb`, b: fixed 0.2: h = 1: 1 blocks (2018-06-29 to 2018-07-30; first cut-off 0.2); h = 2: 1 blocks (2018-07-02 to 2018-11-30; first cut-off 0.2); h = 3: 1 blocks (2018-07-03 to 2018-12-03; first cut-off 0.2); h = 4: 1 blocks (2018-07-05 to 2018-12-04; first cut-off 0.2); h = 5: 1 blocks (2018-07-06 to 2018-12-06; first cut-off 0.2)
* `risk_gbm+settle+h41`, a: climatology rate: h = 1: 0 blocks; h = 2: 4 blocks (2018-08-01 to 2018-11-30; first cut-off 0.05263); h = 3: 0 blocks; h = 4: 0 blocks; h = 5: 0 blocks
* `risk_gbm+settle+h41`, b: fixed 0.2: h = 1: 1 blocks (2018-06-29 to 2018-07-30; first cut-off 0.2); h = 2: 1 blocks (2018-07-02 to 2018-11-30; first cut-off 0.2); h = 3: 1 blocks (2018-07-03 to 2018-12-03; first cut-off 0.2); h = 4: 1 blocks (2018-07-05 to 2018-12-04; first cut-off 0.2); h = 5: 1 blocks (2018-07-06 to 2018-12-06; first cut-off 0.2)
* `ngboost_laplace`, a: climatology rate: h = 1: 0 blocks; h = 2: 4 blocks (2018-08-01 to 2018-11-30; first cut-off 0.05263); h = 3: 0 blocks; h = 4: 0 blocks; h = 5: 0 blocks
* `ngboost_laplace`, b: fixed 0.2: h = 1: 1 blocks (2018-06-29 to 2018-07-30; first cut-off 0.2); h = 2: 1 blocks (2018-07-02 to 2018-11-30; first cut-off 0.2); h = 3: 1 blocks (2018-07-03 to 2018-12-03; first cut-off 0.2); h = 4: 1 blocks (2018-07-05 to 2018-12-04; first cut-off 0.2); h = 5: 1 blocks (2018-07-06 to 2018-12-06; first cut-off 0.2)
* `calendar_climatology`, a: climatology rate: h = 1: 0 blocks; h = 2: 4 blocks (2018-08-01 to 2018-11-30; first cut-off 0.05263); h = 3: 0 blocks; h = 4: 0 blocks; h = 5: 0 blocks
* `calendar_climatology`, b: fixed 0.2: h = 1: 1 blocks (2018-06-29 to 2018-07-30; first cut-off 0.2); h = 2: 1 blocks (2018-07-02 to 2018-11-30; first cut-off 0.2); h = 3: 1 blocks (2018-07-03 to 2018-12-03; first cut-off 0.2); h = 4: 1 blocks (2018-07-05 to 2018-12-04; first cut-off 0.2); h = 5: 1 blocks (2018-07-06 to 2018-12-06; first cut-off 0.2)
* `persistence_logistic`, a: climatology rate: h = 1: 0 blocks; h = 2: 4 blocks (2018-08-01 to 2018-11-30; first cut-off 0.05263); h = 3: 0 blocks; h = 4: 0 blocks; h = 5: 0 blocks
* `persistence_logistic`, b: fixed 0.2: h = 1: 1 blocks (2018-06-29 to 2018-07-30; first cut-off 0.2); h = 2: 1 blocks (2018-07-02 to 2018-11-30; first cut-off 0.2); h = 3: 1 blocks (2018-07-03 to 2018-12-03; first cut-off 0.2); h = 4: 1 blocks (2018-07-05 to 2018-12-04; first cut-off 0.2); h = 5: 1 blocks (2018-07-06 to 2018-12-06; first cut-off 0.2)
