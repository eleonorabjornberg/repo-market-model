# The #1027 calendar-aware variants with the FOMC meeting columns (#1087): development data, not a verdict

Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, scratch panel `f9fae9dce43341f2816d19c76d9562f9773f0bff5891bd051f52eac0ffecb8f3`, FOMC calendar `cddbadfa2bb37fbc536b2be29a985d6594a9d9e62320263e007975417b4da403`. Declaration `metadata/fomc_variants_1087.json`. Seed 1087, 10000 draws, the studentized stationary bootstrap. 1855 decision days, every pair on the same days. Skill = mean(d) / mean(S(benchmark)); positive favours the first model. Intervals: two-sided 90% (the lower end is the one-sided 95% lower bound). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days. The cuts `fomc_day`, `fomc_ordinary` and `ordinary_non_fomc` overlap the five exclusive target day types.

## Mean scores, pooled

| model | grid CRPS (23 levels) | upper-tail twCRPS (weight 1{z > 0 bp}) |
|---|---|---|
| gbm_funding | 1.8223 | 0.9515 |
| gbm_funding_cal_direct | 1.8683 | 0.9549 |
| gbm_funding_cal_direct_fomc | 1.8807 | 0.9553 |

## Reading (declared rules)

Over the arm's #1027 variant:

- gbm_funding_cal_direct_fomc is not shown to help over gbm_funding_cal_direct on FOMC days (skill -1.2%, one-sided 95% lower bound -3.0%) and does not lose on ordinary non-FOMC days (skill -0.7%, interval -1.7% to +0.3%).

Over gbm_funding:

- gbm_funding_cal_direct_fomc is not shown to beat gbm_funding on calendar days (skill -0.7%, one-sided 95% lower bound -6.3%) and does not lose on ordinary days (skill -7.8%, interval -17.3% to +0.8%).
- gbm_funding_cal_aligned_fomc: not run: repo_model.one_step_guard (#947) refuses it until Eleonora admits it by an allow-list entry per lead; walk refuses and writes nothing.

Whether the columns join a published declaration is Eleonora's question (#1046); this page does not decide it.

## grid CRPS (23 levels)

### pooled (decision days)

| group | days | gbm_funding_cal_direct_fomc over gbm_funding_cal_direct | gbm_funding_cal_direct_fomc over gbm_funding |
|---|---|---|---|
| all decision days | 1,855 | -0.7% [-1.5%, +0.1%] | -3.2% [-8.8%, +2.1%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_fomc over gbm_funding_cal_direct | gbm_funding_cal_direct_fomc over gbm_funding |
|---|---|---|---|
| 2018-19 | 361 | -0.1% [-1.4%, +1.0%] | -4.0% [-11.1%, +1.5%] |
| 2020 | 251 | -2.4% [-8.4%, +1.9%] | -10.8% [-37.6%, +10.0%] |
| 2021-23 | 748 | -2.2% [-3.5%, -1.0%] | -30.6% [-44.9%, -19.7%] |
| 2024 | 250 | +0.4% [-0.6%, +1.6%] | +17.9% [+9.7%, +25.7%] |
| 2025-26 | 249 | +0.1% [-1.9%, +1.5%] | +13.6% [-6.9%, +28.3%] |

### target day type

| group | days | gbm_funding_cal_direct_fomc over gbm_funding_cal_direct | gbm_funding_cal_direct_fomc over gbm_funding |
|---|---|---|---|
| ordinary | 848 | -0.9% [-1.9%, +0.1%] | -7.8% [-17.3%, +0.8%] |
| settlement | 742 | -0.5% [-1.5%, +0.4%] | -6.8% [-15.3%, -0.2%] |
| month_end | 150 | -2.0% [-4.3%, -0.3%] | +16.3% [+3.7%, +31.9%] |
| tax_date | 89 | -0.6% [-2.0%, +0.5%] | -3.7% [-9.9%, +2.5%] |
| quarter_end | 30 | +0.8% [-0.4%, +3.2%] | +14.8% [-12.0%, +39.3%] |
| calendar_days | 1,011 | -0.6% [-1.5%, +0.1%] | -0.7% [-6.3%, +4.4%] |
| fomc_day | 120 | -1.2% [-3.0%, -0.2%] | -1.3% [-5.8%, +3.5%] |
| fomc_ordinary | 42 | -4.3% [-12.0%, +0.2%] | -3.5% [-16.7%, +9.9%] |
| ordinary_non_fomc | 806 | -0.7% [-1.7%, +0.3%] | -8.1% [-17.8%, +0.7%] |

## upper-tail twCRPS (weight 1{z > 0 bp})

### pooled (decision days)

| group | days | gbm_funding_cal_direct_fomc over gbm_funding_cal_direct | gbm_funding_cal_direct_fomc over gbm_funding |
|---|---|---|---|
| all decision days | 1,855 | -0.0% [-1.2%, +1.0%] | -0.4% [-6.4%, +5.0%] |

### regime (target day)

| group | days | gbm_funding_cal_direct_fomc over gbm_funding_cal_direct | gbm_funding_cal_direct_fomc over gbm_funding |
|---|---|---|---|
| 2018-19 | 361 | -0.2% [-1.6%, +0.9%] | -2.6% [-9.4%, +2.7%] |
| 2020 | 251 | +3.0% [-0.7%, +6.4%] | -1.7% [-38.7%, +33.7%] |
| 2021-23 | 748 | +4.8% [-13.2%, +24.7%] | -14.4% [-76.2%, +22.0%] |
| 2024 | 250 | +0.1% [-0.5%, +0.7%] | +11.3% [+3.6%, +24.0%] |
| 2025-26 | 249 | -0.8% [-5.3%, +2.2%] | +10.6% [-30.1%, +35.5%] |

### target day type

| group | days | gbm_funding_cal_direct_fomc over gbm_funding_cal_direct | gbm_funding_cal_direct_fomc over gbm_funding |
|---|---|---|---|
| ordinary | 848 | -0.2% [-2.6%, +1.4%] | -5.7% [-19.8%, +5.4%] |
| settlement | 742 | +0.4% [-0.8%, +1.5%] | -4.5% [-17.4%, +3.7%] |
| month_end | 150 | -3.3% [-8.0%, -0.5%] | +18.1% [-3.0%, +44.4%] |
| tax_date | 89 | +0.0% [-0.3%, +0.6%] | undefined |
| quarter_end | 30 | +1.5% [+1.0%, +2.8%] | +14.0% [-7.0%, +29.0%] |
| calendar_days | 1,011 | +0.0% [-1.0%, +0.9%] | +1.7% [-2.9%, +6.3%] |
| fomc_day | 120 | -1.4% [-2.9%, +0.1%] | -0.5% [-3.1%, +3.2%] |
| fomc_ordinary | 42 | -10.5% [-22.0%, -6.5%] | +3.6% [-31.0%, +23.7%] |
| ordinary_non_fomc | 806 | +0.3% [-2.0%, +1.9%] | -6.3% [-22.0%, +4.9%] |

