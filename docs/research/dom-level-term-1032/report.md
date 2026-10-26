# gbm_funding_cal_direct with a day-of-month level term (#1032): development data, not a verdict

Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, scratch panel `f9fae9dce43341f2816d19c76d9562f9773f0bff5891bd051f52eac0ffecb8f3`. Declaration `metadata/dom_level_term_1032.json`. Seed 1032, 10000 draws, the studentized stationary bootstrap. 1855 decision days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days.

## Mean scores, pooled

| model | grid CRPS (23 levels) | upper-tail twCRPS (weight 1{z > 0 bp}) |
|---|---|---|
| B1 | 2.2889 | 1.3750 |
| B1_prime | 1.9281 | 1.0648 |
| B2 | 2.5184 | 1.1315 |
| spread_mr_ctx | 1.7504 | 0.9077 |
| gbm_funding | 1.8223 | 0.9515 |
| gbm_funding_cal_direct | 1.8683 | 0.9549 |
| gbm_funding_cal_aligned | 1.8019 | 0.9360 |
| gbm_funding_cal_direct_dom | 1.8611 | 0.9516 |

## Reading (declared rules)

- The day-of-month term helps over gbm_funding_cal_direct on all decision days (skill +0.4%, interval +0.2% to +0.6%).
- The day-of-month term helps over gbm_funding_cal_direct on target days of the 19th to 23rd (skill +0.7%, interval +0.3% to +1.0%).
- It does not lose on ordinary target days (skill +0.3%, interval +0.0% to +0.6%).

Against gbm_funding (calendar days and ordinary days, #1027's reading): gbm_funding_cal_direct_dom is not shown to beat gbm_funding on calendar days (skill +0.3%, one-sided 95% lower bound -4.9%) and does not lose on ordinary days (skill -6.6%, interval -15.7% to +1.7%).

Adopting the term, or naming it with a variant of #1027 as the candidate, is a marked question for Eleonora; this page does not decide it.

## grid CRPS (23 levels)

### pooled (decision days)

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | +0.4% [+0.2%, +0.6%] | -3.3% [-7.3%, +0.5%] | -2.1% [-7.7%, +3.0%] | +18.7% [+9.2%, +35.8%] | +3.5% [-4.2%, +11.4%] | +26.1% [+16.6%, +34.8%] | -6.3% [-13.6%, +0.1%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | +0.3% [+0.1%, +0.7%] | -5.6% [-11.4%, -1.2%] | -3.6% [-10.4%, +1.9%] | +27.3% [+13.9%, +56.1%] | +2.5% [-7.7%, +15.9%] | +5.7% [-4.7%, +15.4%] | -14.0% [-29.9%, -3.0%] |
| 2020 | 251 | +0.8% [+0.2%, +1.4%] | -4.0% [-20.4%, +8.8%] | -7.3% [-33.4%, +9.5%] | +8.4% [-33.3%, +24.5%] | +6.2% [-34.0%, +25.1%] | +46.0% [+24.6%, +66.4%] | +8.7% [-20.3%, +22.0%] |
| 2021-23 | 748 | -0.0% [-0.5%, +0.4%] | -18.5% [-26.3%, -12.1%] | -27.8% [-41.7%, -17.0%] | -29.6% [-53.9%, -11.6%] | -35.7% [-59.7%, -17.7%] | +38.3% [+21.1%, +56.5%] | -25.9% [-46.7%, -9.2%] |
| 2024 | 250 | +0.2% [-0.3%, +0.8%] | +12.8% [+4.3%, +22.1%] | +17.8% [+9.8%, +25.6%] | +29.7% [+19.3%, +41.9%] | +23.7% [+13.3%, +36.2%] | +18.7% [+5.8%, +28.5%] | +9.7% [-0.6%, +18.2%] |
| 2025-26 | 249 | +0.7% [+0.3%, +1.1%] | +7.6% [-9.6%, +19.8%] | +14.2% [-6.9%, +28.1%] | +27.6% [+6.4%, +40.2%] | +20.7% [-3.2%, +35.4%] | +35.6% [+23.2%, +48.6%] | +8.8% [-13.4%, +24.7%] |

### target day type

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| ordinary | 848 | +0.3% [+0.0%, +0.6%] | -3.8% [-10.1%, +2.5%] | -6.6% [-15.7%, +1.7%] | +30.8% [+14.5%, +63.4%] | +9.6% [-2.2%, +21.6%] | +26.0% [+13.8%, +37.7%] | -6.8% [-19.7%, +3.9%] |
| settlement | 742 | +0.6% [+0.3%, +0.9%] | -5.2% [-11.0%, -0.2%] | -5.7% [-13.6%, +0.8%] | +16.1% [+1.8%, +38.9%] | +0.4% [-10.6%, +9.2%] | +26.4% [+15.8%, +37.0%] | -10.0% [-21.5%, -1.2%] |
| month_end | 150 | +0.1% [-0.4%, +0.6%] | +2.0% [-4.8%, +12.8%] | +18.1% [+5.3%, +34.4%] | +20.5% [+6.5%, +36.5%] | +14.8% [-0.3%, +31.1%] | +39.0% [+29.0%, +49.4%] | +15.7% [-3.5%, +31.4%] |
| tax_date | 89 | +0.1% [-0.2%, +0.4%] | -2.6% [-6.0%, +1.0%] | -2.9% [-7.6%, +1.7%] | -8.1% [-19.6%, -0.2%] | -9.6% [-25.1%, +1.3%] | +23.2% [-29.8%, +49.3%] | -10.7% [-19.1%, -2.7%] |
| quarter_end | 30 | +0.3% [+0.1%, +0.5%] | +2.7% [-2.0%, +8.9%] | +14.4% [-11.9%, +39.5%] | +3.6% [-32.9%, +35.0%] | +2.0% [-36.5%, +35.0%] | +11.3% [-39.2%, +29.3%] | -3.4% [-33.4%, +40.7%] |
| calendar_days | 1,011 | +0.4% [+0.2%, +0.7%] | -3.0% [-6.5%, +0.3%] | +0.3% [-4.9%, +5.4%] | +11.1% [+2.7%, +21.1%] | +0.4% [-6.9%, +6.9%] | +26.4% [+12.3%, +37.7%] | -5.8% [-12.8%, +0.3%] |

### day of month of the target day (bucket)

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| 19-23 | 305 | +0.7% [+0.3%, +1.0%] | -6.1% [-15.5%, +2.1%] | -9.9% [-22.1%, +0.8%] | +37.8% [-2.5%, +115.4%] | +0.9% [-27.8%, +25.3%] | +32.0% [+15.2%, +50.8%] | +0.5% [-24.9%, +20.6%] |
| 24-31 | 459 | +0.1% [-0.2%, +0.4%] | -4.3% [-10.2%, +3.6%] | +4.6% [-5.9%, +16.0%] | +15.5% [-2.9%, +49.5%] | +1.5% [-11.6%, +13.3%] | +27.0% [+13.1%, +39.0%] | -3.9% [-15.4%, +8.1%] |
| 1-5 | 297 | +0.3% [-0.1%, +0.7%] | +5.5% [-2.7%, +12.8%] | +4.8% [-5.5%, +13.3%] | +21.3% [+9.2%, +33.1%] | +8.2% [-4.9%, +19.4%] | +28.4% [+12.8%, +40.8%] | +1.2% [-12.9%, +11.1%] |
| 6-14 | 553 | +0.3% [-0.1%, +0.7%] | -8.7% [-17.7%, +0.7%] | -13.7% [-26.9%, -2.2%] | +26.0% [+10.6%, +48.0%] | +11.6% [-7.2%, +34.2%] | +21.5% [+3.8%, +36.6%] | -16.7% [-36.4%, -2.4%] |
| 15-18 | 245 | +0.7% [+0.1%, +1.2%] | -3.2% [-9.0%, +5.2%] | -2.2% [-7.2%, +2.6%] | -4.1% [-12.6%, +1.7%] | -4.5% [-14.2%, +2.7%] | +24.5% [-10.0%, +43.4%] | -9.9% [-21.1%, -2.4%] |

## upper-tail twCRPS (weight 1{z > 0 bp})

### pooled (decision days)

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | +0.3% [+0.1%, +0.6%] | -1.7% [-5.8%, +1.8%] | -0.0% [-5.8%, +5.3%] | +30.8% [+20.0%, +49.6%] | +10.6% [+0.4%, +22.8%] | +15.9% [+2.6%, +28.2%] | -4.8% [-13.6%, +2.4%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | +0.3% [+0.0%, +0.6%] | -4.0% [-9.5%, -0.2%] | -2.1% [-8.6%, +3.0%] | +29.5% [+15.9%, +58.3%] | +3.0% [-7.8%, +17.9%] | +2.4% [-7.7%, +12.1%] | -12.4% [-28.7%, -1.8%] |
| 2020 | 251 | +0.7% [-0.3%, +2.0%] | +5.5% [-8.1%, +24.3%] | -4.0% [-40.6%, +29.2%] | +38.8% [+19.6%, +62.6%] | +39.8% [+23.1%, +67.0%] | +62.9% [-32.7%, +86.3%] | +31.7% [-11.5%, +61.9%] |
| 2021-23 | 748 | -0.2% [-2.7%, +3.6%] | -164.5% [-555.2%, +204.2%] | -20.5% [-118.5%, +20.6%] | +35.0% [-49.3%, +76.8%] | +13.6% [-111.0%, +75.8%] | -89.9% [-414.2%, +15.7%] | +66.2% [+25.1%, +86.0%] |
| 2024 | 250 | -0.3% [-0.7%, -0.1%] | +8.4% [+2.1%, +58.5%] | +10.9% [+2.2%, +24.5%] | +33.1% [+3.5%, +160.0%] | +28.9% [+6.1%, +116.8%] | undefined | +7.8% [+4.2%, +14.7%] |
| 2025-26 | 249 | +0.6% [+0.1%, +1.0%] | +5.6% [-26.4%, +20.7%] | +11.8% [-27.3%, +35.0%] | +33.4% [-5.0%, +52.0%] | +23.5% [-16.9%, +44.3%] | +30.7% [+16.5%, +39.9%] | +2.5% [-27.2%, +20.2%] |

### target day type

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| ordinary | 848 | -0.1% [-0.5%, +0.4%] | -2.2% [-9.7%, +4.5%] | -5.6% [-19.1%, +5.6%] | +55.3% [+35.6%, +83.1%] | +27.0% [+8.0%, +46.6%] | +14.5% [-8.2%, +29.4%] | -3.5% [-28.2%, +12.7%] |
| settlement | 742 | +0.8% [+0.4%, +1.2%] | -4.0% [-13.0%, +1.7%] | -4.1% [-16.6%, +3.6%] | +30.5% [+10.6%, +62.4%] | +8.1% [-6.9%, +18.5%] | +15.2% [-2.9%, +27.1%] | -10.0% [-32.3%, +2.4%] |
| month_end | 150 | +0.4% [-0.3%, +1.3%] | +3.3% [-0.3%, +7.8%] | +21.1% [+0.5%, +54.5%] | +20.6% [-11.0%, +46.3%] | +21.2% [-26.8%, +47.7%] | undefined | +21.2% [-27.8%, +55.5%] |
| tax_date | 89 | +0.0% [-0.2%, +0.2%] | -1.3% [-3.7%, +0.9%] | undefined | -6.7% [-15.1%, -1.5%] | -6.9% [-16.1%, -0.6%] | undefined | -8.9% [-19.2%, -2.8%] |
| quarter_end | 30 | +0.2% [+0.1%, +0.5%] | +3.6% [+0.5%, +6.2%] | +12.8% [-7.9%, +27.9%] | +3.3% [-26.5%, +26.3%] | +2.1% [-29.4%, +26.5%] | undefined | -3.9% [-66.2%, +33.3%] |
| calendar_days | 1,011 | +0.5% [+0.1%, +0.8%] | -1.4% [-4.5%, +1.1%] | +2.1% [-2.3%, +6.8%] | +17.5% [+9.9%, +28.3%] | +4.7% [-2.4%, +11.7%] | +16.7% [-1.0%, +32.0%] | -4.7% [-12.1%, +1.9%] |

### day of month of the target day (bucket)

| group | days | gbm_funding_cal_direct_dom over gbm_funding_cal_direct | gbm_funding_cal_direct_dom over gbm_funding_cal_aligned | gbm_funding_cal_direct_dom over gbm_funding | gbm_funding_cal_direct_dom over B1 | gbm_funding_cal_direct_dom over B1_prime | gbm_funding_cal_direct_dom over B2 | gbm_funding_cal_direct_dom over spread_mr_ctx |
|---|---|---|---|---|---|---|---|---|
| 19-23 | 305 | +0.8% [+0.4%, +1.2%] | -11.9% [-29.0%, +4.7%] | -14.0% [-34.4%, +0.9%] | +69.6% [+31.3%, +115.6%] | +30.9% [-8.2%, +64.5%] | +14.3% [-33.0%, +49.2%] | +18.4% [-24.4%, +46.0%] |
| 24-31 | 459 | -0.0% [-0.4%, +0.4%] | -3.7% [-9.0%, +1.8%] | +6.3% [-3.6%, +15.8%] | +26.5% [-2.0%, +80.3%] | +6.2% [-9.8%, +17.8%] | +21.9% [-3.1%, +40.9%] | -1.6% [-13.5%, +10.0%] |
| 1-5 | 297 | +0.4% [-0.0%, +0.9%] | +6.0% [-4.4%, +14.4%] | +4.6% [-8.8%, +14.0%] | +25.9% [+6.1%, +44.9%] | +6.6% [-9.5%, +22.5%] | +18.4% [-9.7%, +36.2%] | -0.4% [-23.0%, +11.7%] |
| 6-14 | 553 | +0.0% [-0.8%, +1.0%] | -9.9% [-28.9%, +4.8%] | -12.0% [-46.6%, +7.0%] | +51.6% [+30.4%, +78.5%] | +35.0% [+1.3%, +67.9%] | +6.9% [-36.6%, +31.1%] | -22.6% [-93.2%, +3.8%] |
| 15-18 | 245 | +0.6% [-0.0%, +1.0%] | +0.3% [-2.2%, +3.8%] | +0.2% [-3.2%, +3.2%] | -4.0% [-13.1%, +1.9%] | -3.4% [-13.2%, +3.7%] | +14.0% [-8.3%, +30.4%] | -8.8% [-23.7%, -1.1%] |

