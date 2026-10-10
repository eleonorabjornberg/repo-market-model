Table 1. +5 bp onsets flagged at some lead 1 to 5 / onsets, recall, and the recall difference against risk_gbm (90% interval).

| cell | onsets | risk_gbm | all_inputs_logistic+recalibrated | difference vs risk_gbm | all_inputs_gbm+recalibrated | difference vs risk_gbm |
|---|---|---|---|---|---|---|
| all | 26 | 13/26 | 0.500 | +0.0000 [-0.0882, +0.0952] | 0.577 | +0.0769 [-0.0456, +0.2105] |
| year 2018 | 4 | 0/4 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| year 2019 | 13 | 10/13 | 0.846 | +0.0769 [+0.0000, +0.2308] | 1.000 | +0.2308 [+0.0000, +0.4444] |
| year 2020 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| year 2021 | 0 | 0/0 | - | - | - | - |
| year 2022 | 0 | 0/0 | - | - | - | - |
| year 2023 | 0 | 0/0 | - | - | - | - |
| year 2024 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| year 2025 | 5 | 3/5 | 0.400 | -0.2000 (no interval) | 0.400 | -0.2000 (no interval) |
| regime 2018-19 | 17 | 10/17 | 0.647 | +0.0588 [+0.0000, +0.1765] | 0.765 | +0.1765 [+0.0000, +0.3449] |
| regime 2020 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| regime 2021-23 | 0 | 0/0 | - | - | - | - |
| regime 2024 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 3/5 | 0.400 | -0.2000 (no interval) | 0.400 | -0.2000 (no interval) |
| day type month_end | 6 | 4/6 | 0.667 | +0.0000 (no interval) | 0.667 | +0.0000 (no interval) |
| day type ordinary | 12 | 4/12 | 0.333 | +0.0000 [-0.2000, +0.2000] | 0.583 | +0.2500 [+0.0000, +0.5000] |
| day type quarter_end | 3 | 2/3 | 0.667 | +0.0000 (no interval) | 0.333 | -0.3333 (no interval) |
| day type tax_date | 5 | 3/5 | 0.600 | +0.0000 (no interval) | 0.600 | +0.0000 (no interval) |

Table 2 (h = 1). Brier score the comparison loses to the candidate (positive favours the candidate), +5 bp, 90% interval.

| model | cell | days | vs climatology | vs persistence-logistic | vs risk_gbm |
|---|---|---|---|---|---|
| all_inputs_logistic+recalibrated | all | 1873 | +0.0034 [+0.0005, +0.0061] | -0.0117 [-0.0175, -0.0061] | -0.0103 [-0.0167, -0.0035] |
| all_inputs_logistic+recalibrated | regime 2018-19 | 375 | +0.0066 [-0.0055, +0.0181] | -0.0102 [-0.0311, +0.0095] | +0.0049 [-0.0203, +0.0330] |
| all_inputs_logistic+recalibrated | regime 2020 | 251 | -0.0103 [-0.0186, -0.0024] | -0.0338 [-0.0470, -0.0191] | -0.0499 [-0.0618, -0.0383] |
| all_inputs_logistic+recalibrated | regime 2021-23 | 748 | +0.0049 [+0.0035, +0.0062] | -0.0081 [-0.0096, -0.0066] | -0.0088 [-0.0106, -0.0072] |
| all_inputs_logistic+recalibrated | regime 2024 | 250 | +0.0029 [+0.0007, +0.0047] | +0.0031 [-0.0002, +0.0078] | -0.0008 [-0.0041, +0.0024] |
| all_inputs_logistic+recalibrated | regime 2025-26 | 249 | +0.0080 [+0.0039, +0.0129] | -0.0176 [-0.0456, +0.0045] | -0.0075 [-0.0283, +0.0092] |
| all_inputs_logistic+recalibrated | day_type month_end | 150 | +0.0109 [-0.0029, +0.0251] | -0.0103 [-0.0353, +0.0150] | -0.0435 [-0.0650, -0.0224] |
| all_inputs_logistic+recalibrated | day_type ordinary | 1603 | +0.0010 [-0.0015, +0.0034] | -0.0115 [-0.0171, -0.0063] | -0.0039 [-0.0098, +0.0028] |
| all_inputs_logistic+recalibrated | day_type quarter_end | 31 | +0.0275 [-0.0288, +0.0762] | -0.0329 [-0.1071, +0.0381] | -0.0880 [-0.1737, -0.0066] |
| all_inputs_logistic+recalibrated | day_type tax_date | 89 | +0.0251 [+0.0030, +0.0441] | -0.0105 [-0.0278, +0.0059] | -0.0435 [-0.0818, -0.0127] |
| all_inputs_gbm+recalibrated | all | 1873 | +0.0064 [+0.0030, +0.0098] | -0.0087 [-0.0150, -0.0030] | -0.0073 [-0.0127, -0.0015] |
| all_inputs_gbm+recalibrated | regime 2018-19 | 375 | +0.0013 [-0.0119, +0.0141] | -0.0155 [-0.0409, +0.0085] | -0.0003 [-0.0228, +0.0234] |
| all_inputs_gbm+recalibrated | regime 2020 | 251 | +0.0033 [-0.0070, +0.0131] | -0.0202 [-0.0335, -0.0073] | -0.0363 [-0.0460, -0.0269] |
| all_inputs_gbm+recalibrated | regime 2021-23 | 748 | +0.0095 [+0.0082, +0.0110] | -0.0035 [-0.0045, -0.0026] | -0.0042 [-0.0055, -0.0032] |
| all_inputs_gbm+recalibrated | regime 2024 | 250 | +0.0017 [-0.0023, +0.0048] | +0.0019 [-0.0002, +0.0052] | -0.0020 [-0.0058, +0.0002] |
| all_inputs_gbm+recalibrated | regime 2025-26 | 249 | +0.0124 [+0.0007, +0.0266] | -0.0132 [-0.0401, +0.0061] | -0.0031 [-0.0192, +0.0105] |
| all_inputs_gbm+recalibrated | day_type month_end | 150 | +0.0248 [+0.0107, +0.0400] | +0.0035 [-0.0186, +0.0265] | -0.0296 [-0.0462, -0.0137] |
| all_inputs_gbm+recalibrated | day_type ordinary | 1603 | +0.0014 [-0.0017, +0.0043] | -0.0111 [-0.0181, -0.0052] | -0.0035 [-0.0086, +0.0022] |
| all_inputs_gbm+recalibrated | day_type quarter_end | 31 | +0.0667 [-0.0039, +0.1483] | +0.0063 [-0.0511, +0.0659] | -0.0488 [-0.1193, +0.0129] |
| all_inputs_gbm+recalibrated | day_type tax_date | 89 | +0.0446 [+0.0194, +0.0693] | +0.0091 [-0.0212, +0.0389] | -0.0240 [-0.0498, -0.0026] |

Table 2 (h = 5). Brier score the comparison loses to the candidate (positive favours the candidate), +5 bp, 90% interval.

| model | cell | days | vs climatology | vs persistence-logistic | vs risk_gbm |
|---|---|---|---|---|---|
| all_inputs_logistic+recalibrated | all | 1869 | +0.0054 [+0.0012, +0.0097] | -0.0021 [-0.0074, +0.0028] | +0.0041 [-0.0019, +0.0101] |
| all_inputs_logistic+recalibrated | regime 2018-19 | 371 | -0.0157 [-0.0288, -0.0035] | -0.0131 [-0.0319, +0.0029] | +0.0214 [+0.0025, +0.0416] |
| all_inputs_logistic+recalibrated | regime 2020 | 251 | +0.0084 [+0.0001, +0.0160] | -0.0093 [-0.0174, -0.0013] | -0.0279 [-0.0392, -0.0170] |
| all_inputs_logistic+recalibrated | regime 2021-23 | 748 | +0.0107 [+0.0092, +0.0122] | -0.0010 [-0.0018, -0.0002] | -0.0031 [-0.0038, -0.0025] |
| all_inputs_logistic+recalibrated | regime 2024 | 250 | +0.0024 [-0.0007, +0.0049] | +0.0026 [+0.0008, +0.0052] | +0.0010 [-0.0005, +0.0030] |
| all_inputs_logistic+recalibrated | regime 2025-26 | 249 | +0.0208 [+0.0036, +0.0415] | +0.0131 [-0.0089, +0.0368] | +0.0351 [+0.0088, +0.0659] |
| all_inputs_logistic+recalibrated | day_type month_end | 150 | +0.0194 [+0.0022, +0.0408] | +0.0100 [-0.0046, +0.0277] | +0.0058 [-0.0158, +0.0313] |
| all_inputs_logistic+recalibrated | day_type ordinary | 1600 | +0.0024 [-0.0008, +0.0053] | -0.0036 [-0.0091, +0.0013] | +0.0048 [-0.0013, +0.0113] |
| all_inputs_logistic+recalibrated | day_type quarter_end | 30 | +0.0795 [-0.0000, +0.1628] | +0.0542 [-0.0147, +0.1308] | +0.0164 [-0.0434, +0.0880] |
| all_inputs_logistic+recalibrated | day_type tax_date | 89 | +0.0105 [-0.0201, +0.0375] | -0.0152 [-0.0383, +0.0044] | -0.0153 [-0.0485, +0.0150] |
| all_inputs_gbm+recalibrated | all | 1869 | +0.0018 [-0.0040, +0.0071] | -0.0057 [-0.0122, -0.0004] | +0.0005 [-0.0054, +0.0073] |
| all_inputs_gbm+recalibrated | regime 2018-19 | 371 | -0.0307 [-0.0514, -0.0119] | -0.0281 [-0.0550, -0.0073] | +0.0065 [-0.0126, +0.0287] |
| all_inputs_gbm+recalibrated | regime 2020 | 251 | +0.0046 [-0.0075, +0.0152] | -0.0131 [-0.0239, -0.0035] | -0.0316 [-0.0449, -0.0195] |
| all_inputs_gbm+recalibrated | regime 2021-23 | 748 | +0.0106 [+0.0091, +0.0121] | -0.0011 [-0.0019, -0.0005] | -0.0033 [-0.0043, -0.0024] |
| all_inputs_gbm+recalibrated | regime 2024 | 250 | +0.0038 [+0.0004, +0.0068] | +0.0040 [+0.0006, +0.0091] | +0.0023 [-0.0004, +0.0073] |
| all_inputs_gbm+recalibrated | regime 2025-26 | 249 | +0.0191 [+0.0037, +0.0373] | +0.0114 [-0.0021, +0.0300] | +0.0334 [+0.0077, +0.0639] |
| all_inputs_gbm+recalibrated | day_type month_end | 150 | +0.0088 [-0.0054, +0.0244] | -0.0006 [-0.0126, +0.0119] | -0.0048 [-0.0231, +0.0155] |
| all_inputs_gbm+recalibrated | day_type ordinary | 1600 | -0.0009 [-0.0056, +0.0032] | -0.0069 [-0.0136, -0.0016] | +0.0015 [-0.0050, +0.0083] |
| all_inputs_gbm+recalibrated | day_type quarter_end | 30 | +0.0522 [-0.0665, +0.1603] | +0.0268 [-0.0189, +0.0802] | -0.0109 [-0.0823, +0.0580] |
| all_inputs_gbm+recalibrated | day_type tax_date | 89 | +0.0212 [-0.0095, +0.0455] | -0.0045 [-0.0183, +0.0100] | -0.0047 [-0.0437, +0.0330] |

Table 3. The 26 episodes of the post-mortem (#474): who warns at some lead 1 to 5.

| start | type | regime | post-mortem | risk_gbm | all_inputs_logistic+recalibrated | all_inputs_gbm+recalibrated |
|---|---|---|---|---|---|---|
| 2018-11-15 | ordinary | 2018-19 | no signal in the panel | no | no | no |
| 2018-11-30 | month_end | 2018-19 | signal present, under the cut-off | no | no | no |
| 2018-12-17 | tax_date | 2018-19 | no signal in the panel | no | no | no |
| 2018-12-28 | month_end | 2018-19 | no signal in the panel | no | no | no |
| 2019-01-15 | ordinary | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-01-31 | month_end | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-02-28 | month_end | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-03-15 | ordinary | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-03-29 | quarter_end | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-05-28 | ordinary | 2018-19 | signal too late for the lead rule | no | no | yes |
| 2019-06-17 | tax_date | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-06-25 | ordinary | 2018-19 | signal too late for the lead rule | no | no | yes |
| 2019-08-13 | ordinary | 2018-19 | signal too late for the lead rule | no | yes | yes |
| 2019-08-30 | month_end | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-10-15 | ordinary | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-11-29 | month_end | 2018-19 | warned by at least one | yes | yes | yes |
| 2019-12-16 | tax_date | 2018-19 | warned by at least one | yes | yes | yes |
| 2020-03-04 | ordinary | 2020 | no signal in the panel | no | no | no |
| 2020-03-12 | ordinary | 2020 | signal too late for the lead rule | no | no | no |
| 2024-09-30 | quarter_end | 2024 | no signal in the panel | no | no | no |
| 2024-12-26 | ordinary | 2024 | signal too late for the lead rule | no | no | no |
| 2025-09-15 | tax_date | 2025-26 | warned by at least one | no | no | no |
| 2025-09-30 | quarter_end | 2025-26 | warned by at least one | yes | yes | no |
| 2025-10-15 | ordinary | 2025-26 | warned by at least one | no | no | no |
| 2025-12-15 | tax_date | 2025-26 | warned by at least one | yes | yes | yes |
| 2025-12-26 | ordinary | 2025-26 | warned by at least one | yes | no | yes |

Table 4. What each refit chose (fits per setting, per horizon).

* all_inputs_gbm, h = 1: 179 fits, {'[2]': 63, '[3]': 33, '[4]': 83}, default used 0
* all_inputs_gbm, h = 2: 179 fits, {'[2]': 64, '[3]': 39, '[4]': 76}, default used 0
* all_inputs_gbm, h = 3: 179 fits, {'[2]': 78, '[3]': 35, '[4]': 66}, default used 0
* all_inputs_gbm, h = 4: 179 fits, {'[2]': 103, '[3]': 32, '[4]': 44}, default used 0
* all_inputs_gbm, h = 5: 177 fits, {'[2]': 72, '[3]': 23, '[4]': 82}, default used 0
* all_inputs_logistic, h = 1: 179 fits, {'["l2", 1.0]': 2, '["l1", 1.0]': 19, '["l1", 0.3]': 53, '["l1", 0.1]': 103, '["l2", 0.3]': 2}, default used 0
* all_inputs_logistic, h = 2: 179 fits, {'["l2", 1.0]': 7, '["l1", 1.0]': 22, '["l1", 0.3]': 102, '["l1", 0.1]': 42, '["l2", 0.3]': 6}, default used 0
* all_inputs_logistic, h = 3: 179 fits, {'["l2", 1.0]': 1, '["l1", 1.0]': 36, '["l1", 0.3]': 73, '["l1", 0.1]': 64, '["l2", 0.3]': 5}, default used 0
* all_inputs_logistic, h = 4: 179 fits, {'["l1", 1.0]': 17, '["l1", 0.3]': 71, '["l2", 1.0]': 1, '["l1", 0.1]': 87, '["l2", 0.3]': 3}, default used 0
* all_inputs_logistic, h = 5: 177 fits, {'["l1", 1.0]': 29, '["l1", 0.3]': 80, '["l1", 0.1]': 68}, default used 0
