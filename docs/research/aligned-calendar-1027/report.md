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
| gbm_funding_cal_aligned | 1.8019 | 0.9360 |
| gbm_funding_cal_direct | 1.8683 | 0.9549 |

## Reading (declared rules)

- gbm_funding_cal_aligned beats gbm_funding on calendar days (skill +3.2%, one-sided 95% lower bound +0.7%) and does not lose on ordinary days (skill -2.6%, interval -6.4% to +0.7%).
- gbm_funding_cal_direct is not shown to beat gbm_funding on calendar days (skill -0.1%, one-sided 95% lower bound -5.4%) and does not lose on ordinary days (skill -6.9%, interval -16.4% to +1.5%).

Replacing the candidate is a marked question for Eleonora; this page does not decide it.

## grid CRPS (23 levels)

### pooled (decision days)

| group | days | gbm_funding_cal_aligned over gbm_funding | gbm_funding_cal_aligned over B1 | gbm_funding_cal_aligned over B1_prime | gbm_funding_cal_aligned over B2 | gbm_funding_cal_aligned over spread_mr_ctx | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx | gbm_funding_cal_aligned over gbm_funding_cal_direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | +1.1% [-1.1%, +3.5%] | +21.3% [+13.4%, +40.0%] | +6.5% [+1.5%, +12.6%] | +28.5% [+18.4%, +37.3%] | -2.9% [-7.7%, +1.4%] | -2.5% [-8.1%, +2.6%] | +18.4% [+8.7%, +35.9%] | +3.1% [-4.5%, +11.1%] | +25.8% [+16.1%, +34.6%] | -6.7% [-14.3%, -0.2%] | +3.6% [-0.1%, +7.3%] |

### regime (target day)

| group | days | gbm_funding_cal_aligned over gbm_funding | gbm_funding_cal_aligned over B1 | gbm_funding_cal_aligned over B1_prime | gbm_funding_cal_aligned over B2 | gbm_funding_cal_aligned over spread_mr_ctx | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx | gbm_funding_cal_aligned over gbm_funding_cal_direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | +2.0% [-1.5%, +6.3%] | +31.2% [+19.8%, +56.7%] | +7.7% [-1.3%, +21.7%] | +10.7% [-0.2%, +22.1%] | -7.9% [-17.8%, -0.3%] | -3.9% [-11.2%, +1.6%] | +27.1% [+13.8%, +55.5%] | +2.1% [-8.0%, +15.8%] | +5.3% [-5.2%, +15.0%] | -14.3% [-31.1%, -3.0%] | +5.6% [+1.3%, +10.8%] |
| 2020 | 251 | -3.2% [-11.7%, +2.5%] | +11.9% [-12.3%, +21.6%] | +9.8% [-13.8%, +20.1%] | +48.1% [+20.2%, +67.5%] | +12.2% [-8.3%, +25.5%] | -8.2% [-34.6%, +7.8%] | +7.6% [-34.8%, +23.2%] | +5.4% [-36.3%, +24.0%] | +45.6% [+24.0%, +66.9%] | +7.9% [-20.0%, +21.1%] | +4.6% [-8.0%, +18.4%] |
| 2021-23 | 748 | -7.9% [-14.3%, -2.1%] | -9.4% [-30.9%, +4.6%] | -14.6% [-35.8%, -0.4%] | +47.9% [+32.7%, +63.3%] | -6.3% [-24.1%, +7.6%] | -27.8% [-41.5%, -17.0%] | -29.6% [-54.0%, -11.7%] | -35.7% [-60.0%, -17.6%] | +38.3% [+20.6%, +56.0%] | -25.9% [-46.6%, -9.1%] | +15.6% [+10.9%, +20.7%] |
| 2024 | 250 | +5.7% [+2.8%, +8.5%] | +19.3% [+13.9%, +26.0%] | +12.5% [+8.0%, +17.5%] | +6.7% [-8.9%, +18.8%] | -3.6% [-10.4%, +4.4%] | +17.6% [+9.2%, +25.5%] | +29.6% [+18.7%, +41.5%] | +23.5% [+12.6%, +35.8%] | +18.5% [+5.8%, +28.5%] | +9.5% [-1.3%, +18.1%] | -14.5% [-28.1%, -3.8%] |
| 2025-26 | 249 | +7.1% [+2.0%, +12.4%] | +21.6% [+14.0%, +29.0%] | +14.2% [+5.9%, +21.5%] | +30.3% [+10.2%, +46.5%] | +1.2% [-8.5%, +11.2%] | +13.6% [-7.1%, +27.9%] | +27.0% [+6.3%, +40.0%] | +20.2% [-3.6%, +35.2%] | +35.1% [+23.2%, +48.2%] | +8.1% [-14.5%, +24.9%] | -7.5% [-23.8%, +9.8%] |

### target day type

| group | days | gbm_funding_cal_aligned over gbm_funding | gbm_funding_cal_aligned over B1 | gbm_funding_cal_aligned over B1_prime | gbm_funding_cal_aligned over B2 | gbm_funding_cal_aligned over spread_mr_ctx | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx | gbm_funding_cal_aligned over gbm_funding_cal_direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ordinary | 848 | -2.6% [-6.4%, +0.7%] | +33.3% [+19.0%, +76.0%] | +12.9% [+5.3%, +22.8%] | +28.7% [+17.1%, +40.2%] | -2.8% [-11.0%, +4.1%] | -6.9% [-16.4%, +1.5%] | +30.6% [+14.5%, +62.8%] | +9.3% [-2.7%, +21.3%] | +25.8% [+13.6%, +37.2%] | -7.1% [-20.3%, +3.6%] | +4.0% [-2.3%, +9.6%] |
| settlement | 742 | -0.5% [-2.7%, +1.5%] | +20.2% [+8.3%, +47.1%] | +5.3% [-0.9%, +10.8%] | +30.0% [+20.2%, +40.5%] | -4.6% [-10.8%, +1.1%] | -6.3% [-14.4%, +0.2%] | +15.6% [+0.8%, +38.7%] | -0.2% [-11.6%, +8.7%] | +26.0% [+15.1%, +36.5%] | -10.7% [-22.7%, -1.8%] | +5.5% [+0.8%, +10.6%] |
| month_end | 150 | +16.4% [+7.3%, +29.4%] | +18.9% [+8.3%, +31.8%] | +13.1% [-0.7%, +29.4%] | +37.7% [+24.5%, +50.0%] | +13.9% [-7.3%, +35.9%] | +18.0% [+5.0%, +33.8%] | +20.5% [+6.7%, +35.8%] | +14.8% [-0.2%, +30.5%] | +38.9% [+29.0%, +48.9%] | +15.6% [-3.7%, +31.2%] | -2.0% [-14.0%, +4.7%] |
| tax_date | 89 | -0.3% [-2.4%, +1.5%] | -5.4% [-14.7%, +0.8%] | -6.9% [-19.8%, +1.3%] | +25.1% [-33.2%, +51.9%] | -7.9% [-16.2%, -1.0%] | -3.1% [-7.9%, +1.7%] | -8.2% [-20.4%, +0.1%] | -9.8% [-26.2%, +1.8%] | +23.1% [-29.2%, +48.8%] | -10.8% [-19.7%, -2.4%] | +2.6% [-1.5%, +6.1%] |
| quarter_end | 30 | +12.0% [-12.7%, +32.8%] | +0.9% [-32.8%, +28.2%] | -0.7% [-36.6%, +28.2%] | +8.8% [-45.0%, +29.4%] | -6.3% [-33.1%, +35.3%] | +14.1% [-13.7%, +39.5%] | +3.3% [-34.5%, +35.2%] | +1.8% [-38.1%, +35.3%] | +11.0% [-40.9%, +29.1%] | -3.7% [-34.5%, +41.3%] | -2.5% [-9.6%, +2.3%] |
| calendar_days | 1,011 | +3.2% [+0.7%, +6.1%] | +13.7% [+7.5%, +22.7%] | +3.3% [-1.5%, +7.6%] | +28.5% [+14.6%, +39.6%] | -2.8% [-7.6%, +1.8%] | -0.1% [-5.4%, +4.9%] | +10.8% [+2.2%, +20.8%] | +0.0% [-7.1%, +6.3%] | +26.1% [+12.3%, +37.1%] | -6.3% [-13.4%, -0.1%] | +3.3% [+0.2%, +6.6%] |

## upper-tail twCRPS (weight 1{z > 0 bp})

### pooled (decision days)

| group | days | gbm_funding_cal_aligned over gbm_funding | gbm_funding_cal_aligned over B1 | gbm_funding_cal_aligned over B1_prime | gbm_funding_cal_aligned over B2 | gbm_funding_cal_aligned over spread_mr_ctx | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx | gbm_funding_cal_aligned over gbm_funding_cal_direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | +1.6% [-1.3%, +5.1%] | +31.9% [+22.4%, +51.4%] | +12.1% [+3.9%, +22.7%] | +17.3% [+4.9%, +29.6%] | -3.1% [-9.2%, +2.8%] | -0.4% [-6.3%, +4.8%] | +30.6% [+19.9%, +49.3%] | +10.3% [+0.3%, +22.3%] | +15.6% [+2.5%, +27.7%] | -5.2% [-14.1%, +1.9%] | +2.0% [-1.5%, +6.1%] |

### regime (target day)

| group | days | gbm_funding_cal_aligned over gbm_funding | gbm_funding_cal_aligned over B1 | gbm_funding_cal_aligned over B1_prime | gbm_funding_cal_aligned over B2 | gbm_funding_cal_aligned over spread_mr_ctx | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx | gbm_funding_cal_aligned over gbm_funding_cal_direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | +1.8% [-1.8%, +6.4%] | +32.2% [+20.0%, +58.5%] | +6.7% [-2.9%, +23.0%] | +6.2% [-3.6%, +17.6%] | -8.0% [-18.9%, +0.2%] | -2.4% [-9.2%, +2.8%] | +29.3% [+15.9%, +57.4%] | +2.7% [-8.0%, +17.9%] | +2.1% [-8.3%, +11.8%] | -12.7% [-30.0%, -1.9%] | +4.1% [+0.4%, +9.3%] |
| 2020 | 251 | -10.1% [-33.2%, +9.7%] | +35.3% [+1.0%, +52.1%] | +36.3% [+10.9%, +53.0%] | +60.7% [-70.1%, +90.2%] | +27.8% [-60.4%, +66.8%] | -4.8% [-43.8%, +27.7%] | +38.4% [+18.8%, +61.2%] | +39.4% [+22.4%, +65.4%] | +62.6% [-35.5%, +86.3%] | +31.2% [-13.3%, +61.6%] | -5.0% [-31.3%, +8.2%] |
| 2021-23 | 748 | +54.5% [-154.2%, +123.1%] | +75.4% [+6.1%, +89.2%] | +67.3% [-9.4%, +85.6%] | +28.2% [-90.0%, +79.5%] | +87.2% [+23.9%, +96.4%] | -20.2% [-115.2%, +21.7%] | +35.1% [-48.7%, +76.6%] | +13.8% [-110.1%, +75.6%] | -89.5% [-402.0%, +15.6%] | +66.2% [+25.4%, +85.7%] | +62.1% [-95.2%, +93.4%] |
| 2024 | 250 | +2.8% [-1.5%, +9.5%] | +27.0% [-14.6%, +124.9%] | +22.4% [+2.1%, +81.5%] | undefined | -0.6% [-19.7%, +6.9%] | +11.2% [+2.8%, +24.1%] | +33.4% [+3.8%, +157.8%] | +29.1% [+6.1%, +114.2%] | undefined | +8.2% [+4.5%, +14.9%] | -9.5% [-69.0%, -3.5%] |
| 2025-26 | 249 | +6.5% [-4.4%, +20.9%] | +29.5% [+12.5%, +42.1%] | +19.0% [+2.1%, +32.7%] | +26.6% [+16.1%, +37.6%] | -3.3% [-12.7%, +6.6%] | +11.3% [-28.4%, +34.8%] | +33.0% [-5.8%, +51.9%] | +23.1% [-17.7%, +44.6%] | +30.3% [+16.3%, +39.7%] | +2.0% [-28.5%, +20.3%] | -5.3% [-24.3%, +26.0%] |

### target day type

| group | days | gbm_funding_cal_aligned over gbm_funding | gbm_funding_cal_aligned over B1 | gbm_funding_cal_aligned over B1_prime | gbm_funding_cal_aligned over B2 | gbm_funding_cal_aligned over spread_mr_ctx | gbm_funding_cal_direct over gbm_funding | gbm_funding_cal_direct over B1 | gbm_funding_cal_direct over B1_prime | gbm_funding_cal_direct over B2 | gbm_funding_cal_direct over spread_mr_ctx | gbm_funding_cal_aligned over gbm_funding_cal_direct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ordinary | 848 | -3.3% [-10.5%, +3.7%] | +56.3% [+38.9%, +87.8%] | +28.6% [+13.8%, +45.9%] | +16.4% [-0.5%, +30.1%] | -1.2% [-20.2%, +12.1%] | -5.5% [-19.6%, +5.8%] | +55.4% [+35.7%, +83.2%] | +27.1% [+7.4%, +46.6%] | +14.6% [-9.5%, +29.6%] | -3.4% [-28.0%, +12.9%] | +2.1% [-5.0%, +8.9%] |
| settlement | 742 | -0.1% [-3.1%, +2.5%] | +33.2% [+16.2%, +71.9%] | +11.6% [+4.9%, +18.4%] | +18.5% [+6.3%, +29.6%] | -5.8% [-16.0%, +3.6%] | -5.0% [-17.8%, +3.1%] | +30.0% [+9.6%, +62.4%] | +7.3% [-7.7%, +18.1%] | +14.5% [-3.6%, +26.4%] | -10.9% [-33.5%, +1.8%] | +4.6% [-1.2%, +12.7%] |
| month_end | 150 | +18.5% [-1.2%, +55.1%] | +17.9% [-9.7%, +54.4%] | +18.5% [-25.6%, +49.7%] | undefined | +18.6% [-32.5%, +59.7%] | +20.8% [-0.1%, +53.2%] | +20.2% [-11.2%, +45.9%] | +20.8% [-25.1%, +47.1%] | undefined | +20.9% [-23.9%, +55.4%] | -2.9% [-8.7%, +0.7%] |
| tax_date | 89 | undefined | -5.3% [-18.9%, -1.1%] | -5.6% [-20.4%, -0.2%] | undefined | -7.6% [-20.3%, -0.9%] | undefined | -6.7% [-15.4%, -1.5%] | -6.9% [-16.5%, -0.5%] | undefined | -9.0% [-19.0%, -2.3%] | +1.3% [-1.2%, +3.4%] |
| quarter_end | 30 | +9.6% [-10.3%, +23.6%] | -0.3% [-29.0%, +21.6%] | -1.5% [-32.1%, +21.9%] | undefined | -7.7% [-64.2%, +29.1%] | +12.6% [-9.2%, +27.8%] | +3.0% [-27.2%, +26.1%] | +1.8% [-30.5%, +26.4%] | undefined | -4.1% [-69.1%, +32.6%] | -3.4% [-6.2%, -0.2%] |
| calendar_days | 1,011 | +3.5% [+0.6%, +7.4%] | +18.7% [+12.1%, +29.8%] | +6.0% [+0.2%, +11.9%] | +17.9% [+0.9%, +32.9%] | -3.3% [-9.1%, +2.5%] | +1.6% [-2.8%, +6.2%] | +17.1% [+9.5%, +28.4%] | +4.3% [-2.6%, +11.3%] | +16.3% [-1.3%, +31.5%] | -5.2% [-12.8%, +1.3%] | +1.9% [-0.6%, +4.9%] |

