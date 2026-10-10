# What the forecast reads: the age of the weekly observations (#517)

Age = calendar days from the observation's Wednesday to the decision day, read through the as-of rule. Threshold: 7 days.

| h | scored days | feature | min / median / max (days) | reads older than the threshold | scored days with any weekly read older | spread read, panel days before the scored day | copied row read |
|---|---|---|---|---|---|---|---|
| 1 | 1873 | reserve_balances | 6 / 8 / 13 | 1110 of 1873 | 1873 | 2: 1873 | 6 |
|  |  | tga | 6 / 8 / 13 | 1110 of 1873 |  |  |  |
|  |  | dealer_treasury_position | 9 / 13 / 19 | 1873 of 1873 |  |  |  |
| 2 | 1872 | reserve_balances | 6 / 8 / 13 | 1110 of 1872 | 1872 | 3: 1872 | 6 |
|  |  | tga | 6 / 8 / 13 | 1110 of 1872 |  |  |  |
|  |  | dealer_treasury_position | 9 / 13 / 19 | 1872 of 1872 |  |  |  |
| 3 | 1871 | reserve_balances | 6 / 8 / 13 | 1109 of 1871 | 1871 | 4: 1871 | 6 |
|  |  | tga | 6 / 8 / 13 | 1109 of 1871 |  |  |  |
|  |  | dealer_treasury_position | 9 / 13 / 19 | 1871 of 1871 |  |  |  |
| 4 | 1870 | reserve_balances | 6 / 8 / 13 | 1108 of 1870 | 1870 | 5: 1870 | 6 |
|  |  | tga | 6 / 8 / 13 | 1108 of 1870 |  |  |  |
|  |  | dealer_treasury_position | 9 / 13 / 19 | 1870 of 1870 |  |  |  |
| 5 | 1869 | reserve_balances | 6 / 8 / 13 | 1108 of 1869 | 1869 | 6: 1869 | 6 |
|  |  | tga | 6 / 8 / 13 | 1108 of 1869 |  |  |  |
|  |  | dealer_treasury_position | 9 / 13 / 19 | 1869 of 1869 |  |  |  |

Distribution of ages (days: reads), h = 1:

* reserve_balances: 6: 380, 7: 383, 8: 379, 9: 379, 12: 344, 13: 8
* tga: 6: 380, 7: 383, 8: 379, 9: 379, 12: 344, 13: 8
* dealer_treasury_position: 9: 276, 12: 341, 13: 388, 14: 383, 15: 379, 16: 103, 19: 3

Around each of the 26 episodes, the 10 panel days before it that the judge scores, at h = 1 (stale = a weekly read older than the threshold):

| episode | decision days | days with a stale read | features | copied rows read |
|---|---|---|---|---|
| 2018-11-15 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2018-11-30 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2018-12-17 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2018-12-28 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-01-15 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-01-31 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-02-28 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-03-15 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-03-29 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-05-28 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-06-17 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-06-25 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-08-13 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-08-30 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-10-15 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-11-29 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2019-12-16 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 1 |
| 2020-03-04 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2020-03-12 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2024-09-30 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2024-12-26 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2025-09-15 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2025-09-30 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2025-10-15 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2025-12-15 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
| 2025-12-26 | 10 | 10 | dealer_treasury_position, reserve_balances, tga | 0 |
