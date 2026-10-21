# gbm_funding with calendar and scheduled columns read from the target row (#1027): development data, not a verdict

Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, scratch panel `f9fae9dce43341f2816d19c76d9562f9773f0bff5891bd051f52eac0ffecb8f3`. Declaration `metadata/aligned_calendar_1027.json`. Seed 1027, 10000 draws, the studentized stationary bootstrap. 1855 decision days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days.

## Mean scores, pooled

| model | grid CRPS (23 levels) | upper-tail twCRPS (weight 1{z > 0 bp}) |
|---|---|---|
| B1 | 2.2889 | 1.3750 |
| B1_prime | 1.9281 | 1.0648 |
| B2 | 2.5184 | 1.1315 |
| spread_mr_ctx | 1.7504 | 0.9077 |
| gbm_funding | 1.8223 | 0.9515 |
| gbm_funding_cal_direct | 1.8683 | 0.9549 |

## Reading (declared rules)

- gbm_funding_cal_direct is not shown to beat gbm_funding on calendar days (skill -0.1%, one-sided 95% lower bound -5.4%) and does not lose on ordinary days (skill -6.9%, interval -16.4% to +1.5%).
- gbm_funding_cal_aligned: not run: refused by repo_model.one_step_guard (#947) until Eleonora admits it by an allow-list entry per lead.

Replacing the candidate is a marked question for Eleonora; this page does not decide it.

## grid CRPS (23 levels)

### pooled (decision days)

| group | days | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx |
|---|---|---|---|---|---|---|
| all decision days | 1,855 | -2.5% [-8.1%, +2.6%] | +18.4% [+8.7%, +35.9%] | +3.1% [-4.5%, +11.1%] | +25.8% [+16.1%, +34.6%] | -6.7% [-14.3%, -0.2%] |

### regime (target day)

| group | days | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx |
|---|---|---|---|---|---|---|
| 2018-19 | 361 | -3.9% [-11.2%, +1.6%] | +27.1% [+13.8%, +55.5%] | +2.1% [-8.0%, +15.8%] | +5.3% [-5.2%, +15.0%] | -14.3% [-31.1%, -3.0%] |
| 2020 | 251 | -8.2% [-34.6%, +7.8%] | +7.6% [-34.8%, +23.2%] | +5.4% [-36.3%, +24.0%] | +45.6% [+24.0%, +66.9%] | +7.9% [-20.0%, +21.1%] |
| 2021-23 | 748 | -27.8% [-41.5%, -17.0%] | -29.6% [-54.0%, -11.7%] | -35.7% [-60.0%, -17.6%] | +38.3% [+20.6%, +56.0%] | -25.9% [-46.6%, -9.1%] |
| 2024 | 250 | +17.6% [+9.2%, +25.5%] | +29.6% [+18.7%, +41.5%] | +23.5% [+12.6%, +35.8%] | +18.5% [+5.8%, +28.5%] | +9.5% [-1.3%, +18.1%] |
| 2025-26 | 249 | +13.6% [-7.1%, +27.9%] | +27.0% [+6.3%, +40.0%] | +20.2% [-3.6%, +35.2%] | +35.1% [+23.2%, +48.2%] | +8.1% [-14.5%, +24.9%] |

### target day type

| group | days | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx |
|---|---|---|---|---|---|---|
| ordinary | 848 | -6.9% [-16.4%, +1.5%] | +30.6% [+14.5%, +62.8%] | +9.3% [-2.7%, +21.3%] | +25.8% [+13.6%, +37.2%] | -7.1% [-20.3%, +3.6%] |
| settlement | 742 | -6.3% [-14.4%, +0.2%] | +15.6% [+0.8%, +38.7%] | -0.2% [-11.6%, +8.7%] | +26.0% [+15.1%, +36.5%] | -10.7% [-22.7%, -1.8%] |
| month_end | 150 | +18.0% [+5.0%, +33.8%] | +20.5% [+6.7%, +35.8%] | +14.8% [-0.2%, +30.5%] | +38.9% [+29.0%, +48.9%] | +15.6% [-3.7%, +31.2%] |
| tax_date | 89 | -3.1% [-7.9%, +1.7%] | -8.2% [-20.4%, +0.1%] | -9.8% [-26.2%, +1.8%] | +23.1% [-29.2%, +48.8%] | -10.8% [-19.7%, -2.4%] |
| quarter_end | 30 | +14.1% [-13.7%, +39.5%] | +3.3% [-34.5%, +35.2%] | +1.8% [-38.1%, +35.3%] | +11.0% [-40.9%, +29.1%] | -3.7% [-34.5%, +41.3%] |
| calendar_days | 1,011 | -0.1% [-5.4%, +4.9%] | +10.8% [+2.2%, +20.8%] | +0.0% [-7.1%, +6.3%] | +26.1% [+12.3%, +37.1%] | -6.3% [-13.4%, -0.1%] |

## upper-tail twCRPS (weight 1{z > 0 bp})

### pooled (decision days)

| group | days | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx |
|---|---|---|---|---|---|---|
| all decision days | 1,855 | -0.4% [-6.3%, +4.8%] | +30.6% [+19.9%, +49.3%] | +10.3% [+0.3%, +22.3%] | +15.6% [+2.5%, +27.7%] | -5.2% [-14.1%, +1.9%] |

### regime (target day)

| group | days | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx |
|---|---|---|---|---|---|---|
| 2018-19 | 361 | -2.4% [-9.2%, +2.8%] | +29.3% [+15.9%, +57.4%] | +2.7% [-8.0%, +17.9%] | +2.1% [-8.3%, +11.8%] | -12.7% [-30.0%, -1.9%] |
| 2020 | 251 | -4.8% [-43.8%, +27.7%] | +38.4% [+18.8%, +61.2%] | +39.4% [+22.4%, +65.4%] | +62.6% [-35.5%, +86.3%] | +31.2% [-13.3%, +61.6%] |
| 2021-23 | 748 | -20.2% [-115.2%, +21.7%] | +35.1% [-48.7%, +76.6%] | +13.8% [-110.1%, +75.6%] | -89.5% [-402.0%, +15.6%] | +66.2% [+25.4%, +85.7%] |
| 2024 | 250 | +11.2% [+2.8%, +24.1%] | +33.4% [+3.8%, +157.8%] | +29.1% [+6.1%, +114.2%] | undefined | +8.2% [+4.5%, +14.9%] |
| 2025-26 | 249 | +11.3% [-28.4%, +34.8%] | +33.0% [-5.8%, +51.9%] | +23.1% [-17.7%, +44.6%] | +30.3% [+16.3%, +39.7%] | +2.0% [-28.5%, +20.3%] |

### target day type

| group | days | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx |
|---|---|---|---|---|---|---|
| ordinary | 848 | -5.5% [-19.6%, +5.8%] | +55.4% [+35.7%, +83.2%] | +27.1% [+7.4%, +46.6%] | +14.6% [-9.5%, +29.6%] | -3.4% [-28.0%, +12.9%] |
| settlement | 742 | -5.0% [-17.8%, +3.1%] | +30.0% [+9.6%, +62.4%] | +7.3% [-7.7%, +18.1%] | +14.5% [-3.6%, +26.4%] | -10.9% [-33.5%, +1.8%] |
| month_end | 150 | +20.8% [-0.1%, +53.2%] | +20.2% [-11.2%, +45.9%] | +20.8% [-25.1%, +47.1%] | undefined | +20.9% [-23.9%, +55.4%] |
| tax_date | 89 | undefined | -6.7% [-15.4%, -1.5%] | -6.9% [-16.5%, -0.5%] | undefined | -9.0% [-19.0%, -2.3%] |
| quarter_end | 30 | +12.6% [-9.2%, +27.8%] | +3.0% [-27.2%, +26.1%] | +1.8% [-30.5%, +26.4%] | undefined | -4.1% [-69.1%, +32.6%] |
| calendar_days | 1,011 | +1.6% [-2.8%, +6.2%] | +17.1% [+9.5%, +28.4%] | +4.3% [-2.6%, +11.3%] | +16.3% [-1.3%, +31.5%] | -5.2% [-12.8%, +1.3%] |

