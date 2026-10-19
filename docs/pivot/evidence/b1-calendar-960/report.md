# B1' (a calendar-aware persistence) and gbm_funding, paired (#960): development data, not a verdict

Panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`. Declaration `metadata/b1_calendar_960.json`. Seed 960, 10000 draws, the studentized stationary bootstrap (block 10). Decision days 2018-07-19 to 2025-12-23 (last target 2025-12-31): 1855 days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound).

**The gbm_funding arms are not scored here:** its per-day forecasts are #634's walks, which are run on the Mac (#46's rule on long runs; #905 has not committed them). Only the arms that need no walks are scored.

## Mean scores, pooled

| model | grid CRPS (23 levels) | upper-tail twCRPS (weight 1{z > 0 bp}) |
|---|---|---|
| B1 | 2.2889 | 1.3750 |
| B2 | 2.5184 | 1.1315 |
| B1' (#960) | 1.9281 | 1.0648 |
| spread_mr_ctx (#761) | 1.7504 | 0.9077 |

Reproduction: mean grid CRPS of B1, B2 and spread_mr_ctx equals #761's page (B1 2.2889, B2 2.5184, spread_mr_ctx 1.7504).

## Reading rules (declared)

- gbm_funding against spread_mr_ctx on ordinary targets: not scored (the gbm walks are absent).
- gbm_funding against B1': not scored (the gbm walks are absent).

## grid CRPS (23 levels)

### pooled (decision days)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| all decision days | 1,855 | +9.2% [+4.9%, +15.3%] | +23.5% [+16.5%, +40.8%] | +30.5% [+20.6%, +39.4%] | +15.8% [+8.1%, +49.2%] | +23.4% [+12.1%, +33.7%] |

### regime (target day)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| 2018-19 | 361 | +14.4% [+3.7%, +27.3%] | +36.2% [+27.0%, +54.2%] | +17.2% [+2.9%, +32.2%] | +25.5% [+13.4%, +70.7%] | +3.3% [-11.7%, +15.4%] |
| 2020 | 251 | -2.8% [-17.5%, +29.0%] | -0.4% [-10.9%, +15.9%] | +40.9% [+15.8%, +66.5%] | +2.3% [-7.8%, +8.5%] | +42.5% [-1.0%, +68.5%] |
| 2021-23 | 748 | -7.8% [-13.6%, -2.4%] | -2.9% [-8.6%, +2.1%] | +51.0% [+38.7%, +61.0%] | +4.5% [+2.6%, +6.7%] | +54.6% [+42.2%, +65.3%] |
| 2024 | 250 | +15.5% [+6.3%, +24.4%] | +22.2% [+12.8%, +31.5%] | +9.9% [-4.7%, +23.0%] | +7.9% [+4.2%, +12.6%] | -6.6% [-31.4%, +10.9%] |
| 2025-26 | 249 | +13.1% [+4.5%, +21.6%] | +20.6% [+12.0%, +29.2%] | +29.4% [+4.3%, +48.5%] | +8.6% [+4.7%, +13.2%] | +18.7% [-7.4%, +40.3%] |

### reporting day type (target day)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| ordinary | 1,590 | +12.3% [+7.0%, +19.0%] | +29.6% [+18.9%, +57.1%] | +32.0% [+23.1%, +40.5%] | +19.7% [+7.6%, +75.9%] | +22.4% [+9.6%, +33.2%] |
| month_end | 150 | -1.0% [-24.4%, +12.1%] | +5.7% [-25.7%, +19.3%] | +27.6% [+15.4%, +39.7%] | +6.7% [-0.0%, +13.5%] | +28.3% [+9.9%, +44.5%] |
| quarter_end | 30 | +5.3% [-5.2%, +9.4%] | +6.7% [-1.2%, +10.8%] | +14.2% [-37.5%, +45.9%] | +1.6% [+0.3%, +4.1%] | +9.4% [-46.9%, +52.1%] |
| tax_date | 89 | +1.0% [-7.8%, +7.8%] | +2.3% [-3.2%, +6.9%] | +30.6% [-58.6%, +51.2%] | +1.4% [-5.5%, +5.5%] | +30.0% [-61.2%, +55.5%] |

### anchor day type (decision)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| ordinary | 1,588 | +11.8% [+7.7%, +17.8%] | +12.8% [+8.8%, +18.5%] | +31.2% [+21.0%, +40.5%] | +1.1% [+0.2%, +1.8%] | +21.9% [+9.3%, +33.3%] |
| month_end | 149 | -2.2% [-10.2%, +5.7%] | +35.6% [+24.3%, +53.5%] | +27.2% [+16.0%, +38.9%] | +37.0% [+24.0%, +53.4%] | +28.7% [+14.7%, +41.0%] |
| quarter_end | 29 | +0.4% [-27.2%, +39.3%] | +65.2% [+36.9%, +104.8%] | +8.7% [-52.7%, +55.0%] | +65.0% [+35.1%, +151.2%] | +8.4% [-101.5%, +74.7%] |
| tax_date | 89 | -30.7% [-95.1%, -11.4%] | +67.2% [+29.7%, +212.4%] | +30.3% [-16.6%, +53.4%] | +74.9% [+42.0%, +204.7%] | +46.7% [+19.6%, +65.2%] |

## upper-tail twCRPS (weight 1{z > 0 bp})

### pooled (decision days)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| all decision days | 1,855 | +14.8% [+6.6%, +25.9%] | +34.0% [+25.8%, +50.2%] | +19.8% [+7.1%, +32.4%] | +22.6% [+11.4%, +65.2%] | +5.9% [-9.4%, +17.7%] |

### regime (target day)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| 2018-19 | 361 | +13.6% [+2.0%, +29.0%] | +37.3% [+27.2%, +55.0%] | +13.1% [-0.0%, +28.6%] | +27.3% [+14.8%, +72.2%] | -0.6% [-18.8%, +11.9%] |
| 2020 | 251 | +11.8% [-22.7%, +97.2%] | +10.4% [-19.7%, +77.2%] | +45.6% [-4.8%, +71.8%] | -1.6% [-9.2%, +5.8%] | +38.3% [-127.3%, +79.2%] |
| 2021-23 | 748 | -155.3% [-327.3%, +144.1%] | -92.2% [-194.2%, +40.7%] | -461.4% [-808.2%, -23.9%] | +24.7% [+3.6%, +37.2%] | -119.9% [-269.8%, -59.3%] |
| 2024 | 250 | +22.8% [-10.5%, +197.6%] | +27.4% [-66.5%, +273.8%] | undefined | +6.0% [-8.2%, +58.3%] | undefined |
| 2025-26 | 249 | +21.5% [+7.8%, +34.5%] | +31.7% [+18.5%, +42.6%] | +28.9% [+18.9%, +42.2%] | +12.9% [+7.4%, +18.7%] | +9.4% [-13.6%, +37.7%] |

### reporting day type (target day)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| ordinary | 1,590 | +22.3% [+12.9%, +32.9%] | +46.8% [+33.0%, +72.4%] | +20.8% [+10.2%, +31.5%] | +31.6% [+10.9%, +109.6%] | -1.9% [-24.9%, +13.9%] |
| month_end | 150 | -0.1% [-28.4%, +14.3%] | -0.8% [-59.5%, +15.9%] | undefined | -0.8% [-15.3%, +6.2%] | undefined |
| quarter_end | 30 | undefined | undefined | undefined | undefined | undefined |
| tax_date | 89 | +1.9% [-6.0%, +5.2%] | +2.1% [-5.1%, +5.1%] | undefined | +0.2% [-2.3%, +2.3%] | undefined |

### anchor day type (decision)

| group | days | spread_mr_ctx (#761) over B1' (#960) | spread_mr_ctx (#761) over B1 | spread_mr_ctx (#761) over B2 | B1' (#960) over B1 | B1' (#960) over B2 |
|---|---|---|---|---|---|---|
| ordinary | 1,588 | +17.9% [+10.7%, +28.4%] | +17.8% [+10.6%, +28.1%] | +20.8% [+8.4%, +34.0%] | -0.2% [-1.3%, +0.6%] | +3.4% [-13.3%, +16.9%] |
| month_end | 149 | -5.3% [-25.9%, +12.3%] | +46.8% [+34.3%, +60.5%] | +15.6% [+5.1%, +31.8%] | +49.5% [+31.4%, +61.4%] | +19.8% [-0.7%, +39.5%] |
| quarter_end | 29 | +11.5% [-273.4%, +96.3%] | +84.5% [+42.9%, +90.2%] | +30.8% [+2.2%, +39.7%] | +82.4% [+76.7%, +95.7%] | +21.8% [-94.7%, +61.4%] |
| tax_date | 89 | -61.2% [-462.8%, -2.8%] | +81.8% [+70.5%, +105.0%] | -2.2% [-78.7%, +25.8%] | +88.7% [+75.5%, +120.8%] | +36.6% [+15.9%, +67.6%] |

