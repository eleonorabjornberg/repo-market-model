Table 1. +5 bp onsets flagged at some lead 1 to 5 / onsets, recall, and the recall difference against risk_gbm (90% interval).

| cell | onsets | risk_gbm | all_inputs_logistic+recalibrated | difference vs risk_gbm | all_inputs_gbm+recalibrated | difference vs risk_gbm |
|---|---|---|---|---|---|---|
| all | 26 | 13/26 | 0.500 | +0.0000 [-0.0882, +0.0952] | 0.615 | +0.1154 [+0.0000, +0.2609] |
| year 2018 | 4 | 0/4 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| year 2019 | 13 | 10/13 | 0.846 | +0.0769 [+0.0000, +0.2308] | 1.000 | +0.2308 [+0.0000, +0.4444] |
| year 2020 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| year 2021 | 0 | 0/0 | - | - | - | - |
| year 2022 | 0 | 0/0 | - | - | - | - |
| year 2023 | 0 | 0/0 | - | - | - | - |
| year 2024 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| year 2025 | 5 | 3/5 | 0.400 | -0.2000 (no interval) | 0.600 | +0.0000 (no interval) |
| regime 2018-19 | 17 | 10/17 | 0.647 | +0.0588 [+0.0000, +0.1765] | 0.765 | +0.1765 [+0.0000, +0.3449] |
| regime 2020 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| regime 2021-23 | 0 | 0/0 | - | - | - | - |
| regime 2024 | 2 | 0/2 | 0.000 | +0.0000 (no interval) | 0.000 | +0.0000 (no interval) |
| regime 2025-26 | 5 | 3/5 | 0.400 | -0.2000 (no interval) | 0.600 | +0.0000 (no interval) |
| day type month_end | 6 | 4/6 | 0.667 | +0.0000 (no interval) | 0.667 | +0.0000 (no interval) |
| day type ordinary | 12 | 4/12 | 0.333 | +0.0000 [-0.2000, +0.2000] | 0.667 | +0.3333 [+0.1000, +0.6000] |
| day type quarter_end | 3 | 2/3 | 0.667 | +0.0000 (no interval) | 0.333 | -0.3333 (no interval) |
| day type tax_date | 5 | 3/5 | 0.600 | +0.0000 (no interval) | 0.600 | +0.0000 (no interval) |

Table 2 (h = 1). Brier score the comparison loses to the candidate (positive favours the candidate), +5 bp, 90% interval.

| model | cell | days | vs climatology | vs persistence-logistic | vs risk_gbm |
|---|---|---|---|---|---|
| all_inputs_logistic+recalibrated | all | 1873 | +0.0040 [+0.0009, +0.0069] | -0.0111 [-0.0169, -0.0057] | -0.0097 [-0.0163, -0.0026] |
| all_inputs_logistic+recalibrated | regime 2018-19 | 375 | +0.0072 [-0.0050, +0.0192] | -0.0096 [-0.0307, +0.0100] | +0.0056 [-0.0205, +0.0344] |
| all_inputs_logistic+recalibrated | regime 2020 | 251 | -0.0098 [-0.0196, -0.0002] | -0.0333 [-0.0475, -0.0181] | -0.0494 [-0.0625, -0.0365] |
| all_inputs_logistic+recalibrated | regime 2021-23 | 748 | +0.0058 [+0.0044, +0.0071] | -0.0072 [-0.0089, -0.0057] | -0.0080 [-0.0099, -0.0063] |
| all_inputs_logistic+recalibrated | regime 2024 | 250 | +0.0030 [+0.0010, +0.0046] | +0.0032 [-0.0003, +0.0082] | -0.0007 [-0.0041, +0.0028] |
| all_inputs_logistic+recalibrated | regime 2025-26 | 249 | +0.0089 [+0.0033, +0.0160] | -0.0167 [-0.0428, +0.0038] | -0.0066 [-0.0271, +0.0106] |
| all_inputs_logistic+recalibrated | day_type month_end | 150 | +0.0127 [-0.0022, +0.0277] | -0.0085 [-0.0322, +0.0153] | -0.0417 [-0.0621, -0.0210] |
| all_inputs_logistic+recalibrated | day_type ordinary | 1603 | +0.0016 [-0.0010, +0.0042] | -0.0109 [-0.0164, -0.0059] | -0.0033 [-0.0091, +0.0034] |
| all_inputs_logistic+recalibrated | day_type quarter_end | 31 | +0.0204 [-0.0385, +0.0706] | -0.0400 [-0.1174, +0.0362] | -0.0951 [-0.1822, -0.0102] |
| all_inputs_logistic+recalibrated | day_type tax_date | 89 | +0.0272 [+0.0066, +0.0446] | -0.0083 [-0.0246, +0.0080] | -0.0414 [-0.0784, -0.0105] |
| all_inputs_gbm+recalibrated | all | 1873 | +0.0061 [+0.0026, +0.0097] | -0.0089 [-0.0154, -0.0032] | -0.0075 [-0.0129, -0.0017] |
| all_inputs_gbm+recalibrated | regime 2018-19 | 375 | +0.0017 [-0.0115, +0.0149] | -0.0152 [-0.0409, +0.0093] | +0.0000 [-0.0218, +0.0234] |
| all_inputs_gbm+recalibrated | regime 2020 | 251 | -0.0001 [-0.0102, +0.0099] | -0.0235 [-0.0365, -0.0100] | -0.0397 [-0.0491, -0.0308] |
| all_inputs_gbm+recalibrated | regime 2021-23 | 748 | +0.0095 [+0.0082, +0.0109] | -0.0035 [-0.0046, -0.0026] | -0.0042 [-0.0055, -0.0032] |
| all_inputs_gbm+recalibrated | regime 2024 | 250 | +0.0019 [-0.0019, +0.0049] | +0.0021 [+0.0000, +0.0054] | -0.0018 [-0.0053, +0.0003] |
| all_inputs_gbm+recalibrated | regime 2025-26 | 249 | +0.0133 [+0.0007, +0.0286] | -0.0123 [-0.0383, +0.0063] | -0.0022 [-0.0181, +0.0119] |
| all_inputs_gbm+recalibrated | day_type month_end | 150 | +0.0248 [+0.0102, +0.0411] | +0.0036 [-0.0187, +0.0267] | -0.0295 [-0.0458, -0.0136] |
| all_inputs_gbm+recalibrated | day_type ordinary | 1603 | +0.0010 [-0.0021, +0.0039] | -0.0115 [-0.0184, -0.0054] | -0.0038 [-0.0090, +0.0019] |
| all_inputs_gbm+recalibrated | day_type quarter_end | 31 | +0.0656 [-0.0041, +0.1477] | +0.0051 [-0.0516, +0.0665] | -0.0500 [-0.1199, +0.0111] |
| all_inputs_gbm+recalibrated | day_type tax_date | 89 | +0.0464 [+0.0219, +0.0705] | +0.0109 [-0.0202, +0.0409] | -0.0222 [-0.0481, -0.0009] |

Table 2 (h = 5). Brier score the comparison loses to the candidate (positive favours the candidate), +5 bp, 90% interval.

| model | cell | days | vs climatology | vs persistence-logistic | vs risk_gbm |
|---|---|---|---|---|---|
| all_inputs_logistic+recalibrated | all | 1869 | +0.0055 [+0.0013, +0.0098] | -0.0020 [-0.0073, +0.0030] | +0.0042 [-0.0017, +0.0103] |
| all_inputs_logistic+recalibrated | regime 2018-19 | 371 | -0.0157 [-0.0288, -0.0035] | -0.0131 [-0.0319, +0.0029] | +0.0215 [+0.0025, +0.0416] |
| all_inputs_logistic+recalibrated | regime 2020 | 251 | +0.0084 [-0.0001, +0.0162] | -0.0092 [-0.0176, -0.0010] | -0.0278 [-0.0394, -0.0168] |
| all_inputs_logistic+recalibrated | regime 2021-23 | 748 | +0.0117 [+0.0102, +0.0132] | -0.0000 [-0.0006, +0.0006] | -0.0022 [-0.0027, -0.0017] |
| all_inputs_logistic+recalibrated | regime 2024 | 250 | +0.0025 [-0.0005, +0.0048] | +0.0027 [+0.0006, +0.0054] | +0.0010 [-0.0007, +0.0033] |
| all_inputs_logistic+recalibrated | regime 2025-26 | 249 | +0.0187 [+0.0019, +0.0398] | +0.0110 [-0.0125, +0.0348] | +0.0330 [+0.0074, +0.0634] |
| all_inputs_logistic+recalibrated | day_type month_end | 150 | +0.0186 [+0.0027, +0.0381] | +0.0092 [-0.0043, +0.0249] | +0.0050 [-0.0150, +0.0282] |
| all_inputs_logistic+recalibrated | day_type ordinary | 1600 | +0.0028 [-0.0006, +0.0059] | -0.0032 [-0.0088, +0.0018] | +0.0051 [-0.0009, +0.0118] |
| all_inputs_logistic+recalibrated | day_type quarter_end | 30 | +0.0707 [-0.0038, +0.1493] | +0.0454 [-0.0141, +0.1078] | +0.0076 [-0.0397, +0.0592] |
| all_inputs_logistic+recalibrated | day_type tax_date | 89 | +0.0106 [-0.0207, +0.0381] | -0.0151 [-0.0391, +0.0046] | -0.0152 [-0.0484, +0.0147] |
| all_inputs_gbm+recalibrated | all | 1869 | +0.0013 [-0.0041, +0.0063] | -0.0062 [-0.0124, -0.0011] | +0.0000 [-0.0059, +0.0066] |
| all_inputs_gbm+recalibrated | regime 2018-19 | 371 | -0.0299 [-0.0496, -0.0119] | -0.0272 [-0.0528, -0.0073] | +0.0073 [-0.0123, +0.0295] |
| all_inputs_gbm+recalibrated | regime 2020 | 251 | +0.0008 [-0.0111, +0.0115] | -0.0169 [-0.0285, -0.0069] | -0.0354 [-0.0496, -0.0226] |
| all_inputs_gbm+recalibrated | regime 2021-23 | 748 | +0.0111 [+0.0098, +0.0124] | -0.0006 [-0.0011, -0.0002] | -0.0027 [-0.0037, -0.0019] |
| all_inputs_gbm+recalibrated | regime 2024 | 250 | +0.0038 [+0.0005, +0.0069] | +0.0040 [+0.0006, +0.0092] | +0.0024 [-0.0004, +0.0074] |
| all_inputs_gbm+recalibrated | regime 2025-26 | 249 | +0.0165 [+0.0034, +0.0322] | +0.0088 [-0.0047, +0.0269] | +0.0308 [+0.0066, +0.0595] |
| all_inputs_gbm+recalibrated | day_type month_end | 150 | +0.0078 [-0.0059, +0.0227] | -0.0016 [-0.0131, +0.0104] | -0.0058 [-0.0231, +0.0132] |
| all_inputs_gbm+recalibrated | day_type ordinary | 1600 | -0.0012 [-0.0057, +0.0026] | -0.0072 [-0.0136, -0.0020] | +0.0011 [-0.0053, +0.0080] |
| all_inputs_gbm+recalibrated | day_type quarter_end | 30 | +0.0464 [-0.0718, +0.1546] | +0.0210 [-0.0229, +0.0719] | -0.0167 [-0.0876, +0.0497] |
| all_inputs_gbm+recalibrated | day_type tax_date | 89 | +0.0216 [-0.0079, +0.0450] | -0.0041 [-0.0169, +0.0094] | -0.0042 [-0.0445, +0.0361] |

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
| 2025-10-15 | ordinary | 2025-26 | warned by at least one | no | no | yes |
| 2025-12-15 | tax_date | 2025-26 | warned by at least one | yes | yes | yes |
| 2025-12-26 | ordinary | 2025-26 | warned by at least one | yes | no | yes |

Table 4. What each refit chose (fits per setting, per horizon).

* all_inputs_gbm, h = 1: 179 fits, {'[2]': 74, '[3]': 29, '[4]': 76}, default used 0
* all_inputs_gbm, h = 2: 179 fits, {'[2]': 84, '[4]': 67, '[3]': 28}, default used 0
* all_inputs_gbm, h = 3: 179 fits, {'[2]': 60, '[3]': 32, '[4]': 87}, default used 0
* all_inputs_gbm, h = 4: 179 fits, {'[2]': 99, '[3]': 42, '[4]': 38}, default used 0
* all_inputs_gbm, h = 5: 177 fits, {'[2]': 74, '[3]': 16, '[4]': 87}, default used 0
* all_inputs_logistic, h = 1: 179 fits, {'["l2", 1.0]': 4, '["l1", 1.0]': 32, '["l1", 0.3]': 47, '["l1", 0.1]': 91, '["l2", 0.3]': 5}, default used 0
* all_inputs_logistic, h = 2: 179 fits, {'["l2", 1.0]': 5, '["l1", 1.0]': 29, '["l1", 0.3]': 94, '["l1", 0.1]': 42, '["l2", 0.3]': 9}, default used 0
* all_inputs_logistic, h = 3: 179 fits, {'["l2", 1.0]': 1, '["l1", 1.0]': 38, '["l1", 0.3]': 73, '["l1", 0.1]': 63, '["l2", 0.3]': 4}, default used 0
* all_inputs_logistic, h = 4: 179 fits, {'["l1", 1.0]': 15, '["l1", 0.3]': 76, '["l2", 1.0]': 1, '["l1", 0.1]': 84, '["l2", 0.3]': 3}, default used 0
* all_inputs_logistic, h = 5: 177 fits, {'["l1", 1.0]': 38, '["l1", 0.3]': 71, '["l1", 0.1]': 68}, default used 0
