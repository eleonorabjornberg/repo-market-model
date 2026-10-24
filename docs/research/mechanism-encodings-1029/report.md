# gbm_funding with its raw levels re-encoded as the mechanism acts on them, on #1027's direct calendar design (#1029): development data, not a verdict

Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, scratch panel `f9fae9dce43341f2816d19c76d9562f9773f0bff5891bd051f52eac0ffecb8f3`. Declaration `metadata/mechanism_encodings_1029.json`. Seed 1029, 10000 draws, the studentized stationary bootstrap. 1855 decision days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days.

## Mean scores, pooled

| model | grid CRPS (23 levels) | upper-tail twCRPS (weight 1{z > 0 bp}) |
|---|---|---|
| B1 | 2.2889 | 1.3750 |
| B1_prime | 1.9281 | 1.0648 |
| B2 | 2.5184 | 1.1315 |
| spread_mr_ctx | 1.7504 | 0.9077 |
| gbm_funding | 1.8223 | 0.9515 |
| gbm_funding_cal_direct | 1.8683 | 0.9549 |
| gbm_funding_cal_direct_enc | 1.8747 | 0.9341 |

## Reading (declared rules)

- gbm_funding_cal_direct_enc, against gbm_funding: on all decision days is not shown to differ from it (skill -2.9%, interval -8.5% to +2.1%); on calendar days is not shown to differ from it (skill -0.5%, interval -6.0% to +4.7%); on ordinary days is not shown to differ from it (skill -7.6%, interval -16.4% to +0.1%).
- gbm_funding_cal_direct_enc, against gbm_funding_cal_direct: on all decision days is not shown to differ from it (skill -0.3%, interval -4.0% to +3.1%); on calendar days is not shown to differ from it (skill -0.4%, interval -3.6% to +2.9%); on ordinary days is not shown to differ from it (skill -0.7%, interval -6.3% to +4.7%).

Replacing the candidate is a marked question for Eleonora; this page does not decide it.

## grid CRPS (23 levels)

### pooled (decision days)

| group | days | gbm_funding_cal_direct_enc over gbm_funding | gbm_funding_cal_direct_enc over gbm_funding_cal_direct | gbm_funding_cal_direct_enc over B1 | gbm_funding_cal_direct_enc over B1_prime | gbm_funding_cal_direct_enc over B2 | gbm_funding_cal_direct_enc over spread_mr_ctx |
|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | -2.9% [-8.5%, +2.1%] | -0.3% [-4.0%, +3.1%] | +18.1% [+8.6%, +36.0%] | +2.8% [-4.7%, +10.4%] | +25.6% [+15.5%, +34.8%] | -7.1% [-14.7%, -0.8%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_enc over gbm_funding | gbm_funding_cal_direct_enc over gbm_funding_cal_direct | gbm_funding_cal_direct_enc over B1 | gbm_funding_cal_direct_enc over B1_prime | gbm_funding_cal_direct_enc over B2 | gbm_funding_cal_direct_enc over spread_mr_ctx |
|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | -4.9% [-12.6%, +1.5%] | -1.0% [-5.9%, +3.2%] | +26.3% [+12.5%, +57.4%] | +1.2% [-8.2%, +13.7%] | +4.4% [-4.4%, +14.7%] | -15.5% [-32.0%, -2.8%] |
| 2020 | 251 | -1.9% [-23.6%, +12.7%] | +5.8% [+2.3%, +9.1%] | +13.0% [-25.6%, +27.3%] | +10.9% [-24.8%, +27.7%] | +48.7% [+27.9%, +68.0%] | +13.3% [-12.7%, +25.2%] |
| 2021-23 | 748 | -37.9% [-55.1%, -23.6%] | -7.9% [-18.5%, +2.3%] | -39.8% [-70.7%, -18.6%] | -46.4% [-76.7%, -24.8%] | +33.5% [+14.3%, +52.4%] | -35.8% [-62.5%, -15.8%] |
| 2024 | 250 | +13.3% [+7.1%, +19.8%] | -5.2% [-13.1%, +2.2%] | +25.9% [+17.5%, +36.9%] | +19.5% [+11.6%, +29.0%] | +14.2% [-0.7%, +25.2%] | +4.8% [-2.4%, +12.0%] |
| 2025-26 | 249 | +19.9% [+11.5%, +27.5%] | +7.4% [-2.1%, +19.5%] | +32.4% [+22.9%, +40.4%] | +26.0% [+15.3%, +35.2%] | +39.9% [+25.6%, +52.5%] | +14.9% [+4.2%, +24.5%] |

### target day type

| group | days | gbm_funding_cal_direct_enc over gbm_funding | gbm_funding_cal_direct_enc over gbm_funding_cal_direct | gbm_funding_cal_direct_enc over B1 | gbm_funding_cal_direct_enc over B1_prime | gbm_funding_cal_direct_enc over B2 | gbm_funding_cal_direct_enc over spread_mr_ctx |
|---|---|---|---|---|---|---|---|
| ordinary | 848 | -7.6% [-16.4%, +0.1%] | -0.7% [-6.3%, +4.7%] | +30.1% [+14.3%, +64.2%] | +8.7% [-2.8%, +20.8%] | +25.3% [+12.7%, +38.0%] | -7.8% [-19.9%, +2.6%] |
| settlement | 742 | -6.6% [-14.7%, +0.2%] | -0.3% [-4.7%, +4.0%] | +15.4% [+2.0%, +37.3%] | -0.5% [-11.2%, +8.1%] | +25.8% [+14.7%, +37.6%] | -11.0% [-22.0%, -2.4%] |
| month_end | 150 | +13.8% [-0.2%, +26.6%] | -5.1% [-12.7%, +2.0%] | +16.4% [+3.8%, +28.7%] | +10.4% [-2.0%, +22.6%] | +35.8% [+25.8%, +47.0%] | +11.3% [-3.2%, +24.9%] |
| tax_date | 89 | -3.0% [-10.6%, +4.5%] | +0.1% [-2.7%, +3.2%] | -8.1% [-24.4%, +2.3%] | -9.6% [-31.6%, +3.8%] | +23.2% [-26.0%, +49.9%] | -10.7% [-23.8%, -0.7%] |
| quarter_end | 30 | +17.7% [-4.5%, +39.2%] | +4.1% [-3.4%, +11.1%] | +7.3% [-21.8%, +34.5%] | +5.8% [-25.1%, +34.5%] | +14.7% [-46.3%, +35.1%] | +0.6% [-23.9%, +39.2%] |
| calendar_days | 1,011 | -0.5% [-6.0%, +4.7%] | -0.4% [-3.6%, +2.9%] | +10.4% [+1.8%, +20.9%] | -0.4% [-8.0%, +5.9%] | +25.8% [+12.1%, +37.9%] | -6.6% [-14.8%, -0.3%] |

## upper-tail twCRPS (weight 1{z > 0 bp})

### pooled (decision days)

| group | days | gbm_funding_cal_direct_enc over gbm_funding | gbm_funding_cal_direct_enc over gbm_funding_cal_direct | gbm_funding_cal_direct_enc over B1 | gbm_funding_cal_direct_enc over B1_prime | gbm_funding_cal_direct_enc over B2 | gbm_funding_cal_direct_enc over spread_mr_ctx |
|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | +1.8% [-3.0%, +6.9%] | +2.2% [-1.1%, +5.9%] | +32.1% [+21.8%, +50.4%] | +12.3% [+2.7%, +24.0%] | +17.4% [+3.8%, +31.1%] | -2.9% [-11.3%, +4.3%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_enc over gbm_funding | gbm_funding_cal_direct_enc over gbm_funding_cal_direct | gbm_funding_cal_direct_enc over B1 | gbm_funding_cal_direct_enc over B1_prime | gbm_funding_cal_direct_enc over B2 | gbm_funding_cal_direct_enc over spread_mr_ctx |
|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | -1.3% [-7.0%, +4.1%] | +1.1% [-2.3%, +4.7%] | +30.1% [+16.5%, +59.3%] | +3.7% [-6.1%, +18.4%] | +3.2% [-5.6%, +13.9%] | -11.5% [-26.9%, -0.6%] |
| 2020 | 251 | +3.1% [-25.1%, +29.5%] | +7.6% [+0.8%, +14.8%] | +43.1% [+21.1%, +62.8%] | +44.0% [+26.3%, +66.0%] | +65.4% [-34.0%, +88.4%] | +36.4% [-15.8%, +66.3%] |
| 2021-23 | 748 | -73.0% [-385.6%, +40.0%] | -44.0% [-190.8%, +36.0%] | +6.6% [-136.4%, +71.3%] | -24.1% [-233.7%, +72.4%] | -172.8% [-672.0%, +7.2%] | +51.4% [-9.5%, +78.0%] |
| 2024 | 250 | +5.5% [-3.4%, +12.5%] | -6.5% [-19.5%, +4.2%] | +29.1% [+3.6%, +105.1%] | +24.6% [+4.0%, +75.6%] | undefined | +2.2% [-9.0%, +10.7%] |
| 2025-26 | 249 | +17.9% [+0.4%, +31.5%] | +7.5% [-4.7%, +28.2%] | +38.0% [+17.4%, +51.5%] | +28.8% [+8.0%, +43.5%] | +35.5% [+29.5%, +43.6%] | +9.3% [-3.1%, +18.5%] |

### target day type

| group | days | gbm_funding_cal_direct_enc over gbm_funding | gbm_funding_cal_direct_enc over gbm_funding_cal_direct | gbm_funding_cal_direct_enc over B1 | gbm_funding_cal_direct_enc over B1_prime | gbm_funding_cal_direct_enc over B2 | gbm_funding_cal_direct_enc over spread_mr_ctx |
|---|---|---|---|---|---|---|---|
| ordinary | 848 | +0.5% [-10.4%, +9.8%] | +5.6% [-0.5%, +11.8%] | +57.9% [+40.5%, +84.4%] | +31.2% [+13.1%, +50.3%] | +19.4% [+0.7%, +34.0%] | +2.4% [-19.9%, +16.9%] |
| settlement | 742 | -3.4% [-14.0%, +4.4%] | +1.5% [-3.0%, +6.3%] | +31.0% [+12.8%, +61.2%] | +8.7% [-5.1%, +19.0%] | +15.8% [-0.3%, +28.9%] | -9.2% [-29.1%, +2.0%] |
| month_end | 150 | +19.6% [+10.7%, +34.2%] | -1.5% [-17.2%, +13.2%] | +19.0% [+5.9%, +32.6%] | +19.6% [-1.3%, +37.3%] | undefined | +19.7% [-8.7%, +51.2%] |
| tax_date | 89 | undefined | +0.3% [-1.3%, +2.4%] | -6.4% [-19.2%, +0.3%] | -6.6% [-22.6%, +1.7%] | undefined | -8.6% [-23.3%, -1.1%] |
| quarter_end | 30 | +16.2% [+1.2%, +29.7%] | +4.1% [-4.1%, +21.7%] | +7.0% [-12.0%, +28.1%] | +5.9% [-14.1%, +28.4%] | undefined | +0.2% [-34.2%, +30.7%] |
| calendar_days | 1,011 | +2.7% [-1.4%, +7.3%] | +1.1% [-1.6%, +4.2%] | +18.0% [+10.4%, +29.4%] | +5.3% [-1.8%, +12.4%] | +17.2% [-0.7%, +34.2%] | -4.1% [-12.4%, +2.9%] |

