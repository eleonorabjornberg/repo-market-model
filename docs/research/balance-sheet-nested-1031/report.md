# The balance-sheet days on the turn days, nested into the calendar-aware candidate (#1031): development data, not a verdict

Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, scratch panel `f9fae9dce43341f2816d19c76d9562f9773f0bff5891bd051f52eac0ffecb8f3`. Declaration `metadata/balance_sheet_nested_1031.json`. Seed 1031, 10000 draws, the studentized stationary bootstrap. 1855 decision days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days. The relabel is not adopted here; the page reads with it (`bs_turn`) and without it (`bs_coded`).

## Mean scores, pooled

| model | grid CRPS (23 levels) | upper-tail twCRPS (weight 1{z > 0 bp}) |
|---|---|---|
| B1 | 2.2889 | 1.3750 |
| B2 | 2.5184 | 1.1315 |
| gbm_funding | 1.8223 | 0.9515 |
| gbm_funding_cal_direct | 1.8683 | 0.9549 |
| gbm_funding_cal_direct_bs_coded | 1.8600 | 0.9511 |
| gbm_funding_cal_direct_bs_turn | 1.8635 | 0.9511 |

## Reading (declared rules)

**over gbm_funding_cal_direct**

- gbm_funding_cal_direct_bs_coded beats the reference on its flagged days (skill +0.8%, one-sided 95% lower bound +0.1%) and does not lose on days neither set flags (skill +0.4%, interval +0.0% to +0.9%).
- gbm_funding_cal_direct_bs_turn is not shown to beat the reference on its flagged days (skill +0.9%, one-sided 95% lower bound -1.0%) and does not lose on days neither set flags (skill +0.1%, interval -0.2% to +0.5%).

**over B2**

- gbm_funding_cal_direct_bs_coded beats the reference on its flagged days (skill +27.1%, one-sided 95% lower bound +14.0%) and does not lose on days neither set flags (skill +25.8%, interval +13.6% to +36.2%).
- gbm_funding_cal_direct_bs_turn beats the reference on its flagged days (skill +29.6%, one-sided 95% lower bound +9.6%) and does not lose on days neither set flags (skill +25.6%, interval +13.5% to +36.0%).

**the relabel alone (turn arm over coded arm)**

- gbm_funding_cal_direct_bs_turn is not shown to beat the reference on its flagged days (skill +0.9%, one-sided 95% lower bound -1.3%) and does not lose on days neither set flags (skill -0.3%, interval -0.8% to +0.2%).

Adopting the relabel is a marked question for Eleonora; this page does not decide it.

## grid CRPS (23 levels)

### pooled (decision days)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | +0.4% [+0.1%, +0.9%] | +26.1% [+16.3%, +34.9%] | +18.7% [+9.1%, +36.0%] | -2.1% [-7.7%, +3.1%] | +0.3% [-0.3%, +0.9%] | +26.0% [+16.1%, +34.8%] | +18.6% [+9.1%, +35.6%] | -2.3% [-7.7%, +2.8%] | -0.2% [-0.7%, +0.5%] | +25.8% [+16.1%, +34.6%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | +0.2% [-0.3%, +0.9%] | +5.5% [-5.4%, +15.3%] | +27.2% [+14.1%, +55.3%] | -3.7% [-11.2%, +1.8%] | +0.4% [-0.7%, +1.9%] | +5.7% [-4.9%, +15.4%] | +27.4% [+14.4%, +54.2%] | -3.5% [-10.2%, +1.7%] | +0.2% [-0.8%, +1.6%] | +5.3% [-5.2%, +15.0%] |
| 2020 | 251 | -0.2% [-1.1%, +0.5%] | +45.4% [+23.5%, +67.0%] | +7.4% [-35.0%, +23.1%] | -8.5% [-35.1%, +7.9%] | -0.9% [-2.3%, +0.1%] | +45.1% [+23.2%, +66.2%] | +6.8% [-34.8%, +22.4%] | -9.2% [-35.0%, +6.7%] | -0.6% [-2.1%, +0.4%] | +45.6% [+24.0%, +66.9%] |
| 2021-23 | 748 | +0.0% [-0.5%, +0.6%] | +38.3% [+20.7%, +56.1%] | -29.6% [-54.1%, -11.7%] | -27.8% [-41.4%, -17.0%] | -0.1% [-0.6%, +0.3%] | +38.2% [+20.6%, +56.0%] | -29.7% [-54.3%, -11.7%] | -28.0% [-41.6%, -17.1%] | -0.1% [-0.7%, +0.4%] | +38.3% [+20.6%, +56.0%] |
| 2024 | 250 | +2.1% [+0.0%, +4.8%] | +20.3% [+10.0%, +29.1%] | +31.1% [+21.4%, +42.2%] | +19.4% [+12.5%, +26.2%] | +0.8% [-0.0%, +1.7%] | +19.2% [+6.5%, +29.1%] | +30.1% [+19.3%, +42.2%] | +18.3% [+9.9%, +26.3%] | -1.4% [-4.2%, +0.8%] | +18.5% [+5.8%, +28.5%] |
| 2025-26 | 249 | +1.1% [-0.0%, +2.3%] | +35.8% [+23.8%, +48.5%] | +27.8% [+7.6%, +40.5%] | +14.5% [-5.6%, +28.5%] | +0.8% [-0.1%, +1.5%] | +35.6% [+23.4%, +48.8%] | +27.6% [+7.7%, +40.3%] | +14.2% [-5.4%, +28.1%] | -0.3% [-1.5%, +0.6%] | +35.1% [+23.2%, +48.2%] |

### target day type (turn labels)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ordinary | 1,591 | +0.6% [+0.1%, +1.2%] | +26.3% [+16.8%, +35.6%] | +24.3% [+9.4%, +51.5%] | -7.2% [-15.0%, -0.4%] | +0.2% [-0.2%, +0.6%] | +26.0% [+16.6%, +35.2%] | +24.0% [+9.0%, +51.4%] | -7.7% [-15.1%, -1.0%] | -0.4% [-1.1%, +0.2%] | +25.8% [+16.4%, +35.1%] |
| turn | 120 | -1.4% [-2.6%, -0.5%] | +41.7% [+35.9%, +49.4%] | +24.7% [+8.6%, +35.7%] | +22.3% [+11.1%, +34.6%] | -0.4% [-4.3%, +1.5%] | +42.3% [+36.6%, +49.8%] | +25.4% [+11.7%, +35.7%] | +23.0% [+13.4%, +34.2%] | +1.0% [-1.0%, +2.6%] | +42.5% [+36.9%, +49.9%] |
| tax_date | 89 | +0.2% [-0.0%, +0.5%] | +23.3% [-29.6%, +49.0%] | -8.0% [-20.0%, +0.1%] | -2.9% [-7.5%, +1.8%] | -0.2% [-0.3%, +0.0%] | +23.0% [-30.0%, +48.7%] | -8.4% [-20.6%, -0.1%] | -3.2% [-8.1%, +1.5%] | -0.3% [-0.5%, -0.1%] | +23.1% [-29.2%, +48.8%] |
| quarter_end_turn | 44 | +1.4% [-0.8%, +10.0%] | +18.0% [-6.1%, +29.9%] | +6.4% [-34.2%, +31.5%] | +18.2% [-9.3%, +36.9%] | +4.4% [+0.4%, +13.6%] | +20.5% [-5.9%, +31.8%] | +9.2% [-31.5%, +41.0%] | +20.7% [-7.7%, +45.2%] | +3.0% [-1.7%, +9.1%] | +16.8% [-14.0%, +30.0%] |

### day groups (target day)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| turn days (all three relabelled labels: the relabelled flags' days) | 179 | -0.0% [-0.7%, +0.8%] | +29.0% [+9.4%, +40.0%] | +13.1% [+1.7%, +23.6%] | +16.1% [+5.0%, +27.5%] | +0.9% [-1.0%, +3.0%] | +29.6% [+9.6%, +40.6%] | +13.9% [+2.2%, +24.3%] | +16.8% [+5.6%, +28.0%] | +0.9% [-1.3%, +2.8%] | +29.0% [+8.6%, +40.3%] |
| as-coded flag days (the run-up windows) | 166 | +0.8% [+0.1%, +1.6%] | +27.1% [+14.0%, +38.6%] | +16.1% [-0.0%, +27.6%] | +16.5% [+2.0%, +28.5%] | +0.8% [-0.9%, +3.9%] | +27.1% [+14.3%, +38.4%] | +16.1% [+0.5%, +28.0%] | +16.5% [+2.4%, +29.2%] | +0.0% [-1.8%, +2.5%] | +26.5% [+13.0%, +38.2%] |
| days neither set flags | 1,604 | +0.4% [+0.0%, +0.9%] | +25.8% [+13.6%, +36.2%] | +20.6% [+9.2%, +39.8%] | -6.8% [-13.7%, -1.2%] | +0.1% [-0.2%, +0.5%] | +25.6% [+13.5%, +36.0%] | +20.3% [+8.9%, +39.9%] | -7.2% [-13.9%, -1.6%] | -0.3% [-0.8%, +0.2%] | +25.5% [+13.4%, +35.9%] |
| penultimate days (second-last business day of a month) | 90 | +0.0% [-0.8%, +0.8%] | +32.1% [+10.3%, +50.8%] | -4.7% [-32.2%, +24.6%] | -5.5% [-22.5%, +22.4%] | -0.2% [-0.7%, +0.6%] | +32.0% [+10.7%, +51.1%] | -4.9% [-31.5%, +24.5%] | -5.7% [-22.2%, +21.8%] | -0.2% [-1.2%, +1.2%] | +32.1% [+10.4%, +51.1%] |

## upper-tail twCRPS (weight 1{z > 0 bp})

### pooled (decision days)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all decision days | 1,855 | +0.4% [-0.1%, +1.1%] | +15.9% [+2.4%, +28.1%] | +30.8% [+20.3%, +49.2%] | +0.0% [-5.9%, +5.1%] | +0.4% [-0.6%, +1.7%] | +15.9% [+2.4%, +28.2%] | +30.8% [+20.5%, +48.7%] | +0.0% [-5.6%, +5.1%] | +0.0% [-0.9%, +1.2%] | +15.6% [+2.5%, +27.7%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | +0.3% [-0.3%, +1.0%] | +2.4% [-8.4%, +12.1%] | +29.5% [+16.2%, +57.3%] | -2.2% [-9.2%, +3.1%] | +0.5% [-0.8%, +2.2%] | +2.6% [-7.7%, +12.3%] | +29.7% [+16.7%, +56.3%] | -1.9% [-8.0%, +3.1%] | +0.2% [-0.9%, +1.9%] | +2.1% [-8.3%, +11.8%] |
| 2020 | 251 | -0.2% [-1.1%, +0.9%] | +62.5% [-34.8%, +86.4%] | +38.3% [+18.5%, +60.8%] | -5.0% [-42.5%, +27.4%] | -2.6% [-6.8%, -0.6%] | +61.6% [-34.7%, +85.9%] | +36.8% [+16.6%, +60.1%] | -7.6% [-47.7%, +24.4%] | -2.5% [-6.3%, -0.6%] | +62.6% [-35.5%, +86.3%] |
| 2021-23 | 748 | -1.1% [-5.2%, +3.5%] | -91.6% [-424.6%, +16.0%] | +34.4% [-53.8%, +77.5%] | -21.5% [-113.7%, +19.7%] | -3.7% [-44.1%, +13.0%] | -96.4% [-346.6%, +6.5%] | +32.8% [-39.4%, +75.7%] | -24.6% [-128.1%, +27.4%] | -2.5% [-45.3%, +15.2%] | -89.5% [-402.0%, +15.6%] |
| 2024 | 250 | -0.0% [-1.1%, +1.2%] | undefined | +33.3% [+3.7%, +155.1%] | +11.2% [+1.9%, +23.4%] | -0.9% [-10.1%, +2.9%] | undefined | +32.8% [-81.2%, +176.3%] | +10.5% [-8.1%, +28.2%] | -0.8% [-12.7%, +5.0%] | undefined |
| 2025-26 | 249 | +1.4% [-0.2%, +3.7%] | +31.2% [+19.5%, +39.6%] | +34.0% [-2.4%, +51.9%] | +12.5% [-24.7%, +34.9%] | +1.6% [+0.7%, +2.4%] | +31.4% [+18.4%, +40.2%] | +34.1% [-3.2%, +52.3%] | +12.7% [-25.9%, +35.2%] | +0.2% [-1.0%, +1.4%] | +30.3% [+16.3%, +39.7%] |

### target day type (turn labels)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ordinary | 1,591 | +0.7% [-0.2%, +1.6%] | +15.5% [-1.9%, +27.1%] | +45.5% [+25.6%, +76.4%] | -6.0% [-19.3%, +3.8%] | +0.6% [-0.4%, +1.6%] | +15.5% [-0.9%, +27.0%] | +45.5% [+25.4%, +76.5%] | -6.0% [-18.3%, +3.5%] | -0.0% [-1.4%, +1.3%] | +15.0% [-2.0%, +26.5%] |
| turn | 120 | -2.1% [-5.6%, -0.0%] | +38.0% [+34.1%, +42.6%] | +18.0% [-18.5%, +64.2%] | +20.8% [-1.2%, +56.1%] | -0.4% [-11.1%, +2.8%] | +39.1% [+35.2%, +43.1%] | +19.3% [-10.9%, +60.0%] | +22.1% [+3.5%, +52.4%] | +1.7% [-2.6%, +3.6%] | +39.3% [+35.0%, +44.5%] |
| tax_date | 89 | +0.0% [-0.1%, +0.3%] | undefined | -6.7% [-15.1%, -1.5%] | undefined | -0.1% [-0.3%, +0.1%] | undefined | -6.8% [-15.7%, -1.7%] | undefined | -0.2% [-0.5%, +0.1%] | undefined |
| quarter_end_turn | 44 | +2.8% [+0.5%, +19.2%] | +3.5% [-15.5%, +17.6%] | +12.0% [+3.7%, +19.8%] | +21.1% [+12.3%, +31.4%] | +5.6% [-2.8%, +27.1%] | +6.2% [-17.4%, +21.6%] | +14.4% [+2.8%, +35.8%] | +23.4% [+13.6%, +40.1%] | +2.8% [-6.2%, +14.8%] | +0.7% [-23.1%, +15.4%] |

### day groups (target day)

| group | days | gbm_funding_cal_direct_bs_coded over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_coded over B2 | gbm_funding_cal_direct_bs_coded over B1 | gbm_funding_cal_direct_bs_coded over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct | gbm_funding_cal_direct_bs_turn over B2 | gbm_funding_cal_direct_bs_turn over B1 | gbm_funding_cal_direct_bs_turn over gbm_funding | gbm_funding_cal_direct_bs_turn over gbm_funding_cal_direct_bs_coded | gbm_funding_cal_direct over B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| turn days (all three relabelled labels: the relabelled flags' days) | 179 | +0.2% [-0.4%, +1.1%] | +21.9% [-1.2%, +37.8%] | +9.6% [-0.1%, +19.0%] | +14.5% [+3.9%, +26.8%] | +0.5% [-2.2%, +3.7%] | +22.2% [-1.1%, +37.7%] | +9.9% [+0.4%, +18.8%] | +14.8% [+4.2%, +25.6%] | +0.3% [-2.6%, +3.5%] | +21.8% [-2.1%, +38.0%] |
| as-coded flag days (the run-up windows) | 166 | +0.6% [-0.0%, +1.5%] | +24.2% [+1.2%, +44.7%] | +19.2% [+9.0%, +29.2%] | +19.0% [+6.7%, +29.0%] | +1.5% [-1.4%, +5.8%] | +24.9% [+2.0%, +44.0%] | +20.0% [+9.9%, +29.8%] | +19.8% [+7.8%, +29.7%] | +0.9% [-1.8%, +4.4%] | +23.8% [-0.3%, +44.4%] |
| days neither set flags | 1,604 | +0.4% [-0.2%, +1.2%] | +14.0% [-4.1%, +27.9%] | +35.6% [+22.6%, +54.5%] | -5.0% [-14.5%, +1.3%] | +0.4% [-0.3%, +1.2%] | +13.9% [-3.6%, +27.6%] | +35.6% [+22.5%, +54.6%] | -5.1% [-13.9%, +1.1%] | -0.1% [-0.8%, +0.8%] | +13.6% [-3.8%, +27.2%] |
| penultimate days (second-last business day of a month) | 90 | -0.3% [-1.7%, +0.9%] | undefined | -16.8% [-128.1%, +17.1%] | -13.3% [-33.6%, -1.9%] | +0.8% [-0.9%, +1.9%] | undefined | -15.6% [-122.2%, +18.5%] | -12.1% [-32.9%, -0.7%] | +1.1% [-0.9%, +2.8%] | undefined |

Groups of fewer than 20 days, listed and not tested: cut/december_26 (5), target_type/year_end (15).

