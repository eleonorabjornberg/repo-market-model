# A day-of-month level term on the direct-pairs variant (#1032, H5 step 2)

**Development data, not a verdict.** No locked day and no day after 2025-12-31 is scored; nothing published, registered or declared for the candidate moves. Declaration `metadata/dom_level_term_1032.json`, committed before any number. Every figure is read from `docs/research/dom-level-term-1032/score.json` (the Mac run, commit `397f262a`) and is collected in `result.json` beside it; the full tables are in `report.md`.

## What was run

One declared variant, `gbm_funding_cal_direct_dom`: #1027's direct-pairs variant `gbm_funding_cal_direct` plus one input, `dom_bucket` (1-5, 6-14, 15-18, 19-23, 24-31), the bucket of the **target** day's day of the month, read from the target row at every lead h = 1 to 5. It differs from `gbm_funding_cal_direct` by that term alone. Published panel `4ddc3882cd6d`, scratch panel (#1027's AUG3 with the term written at load) `f9fae9dce433`. 1,855 decision days, 2018-07-19 to 2025-12-23 (last target 2025-12-31), every pair on the same days, 89 refits. Grid CRPS (23 levels) and upper-tail twCRPS (weight 1{z > 0 bp}) in bp, lower is better. A skill cell is the skill of `gbm_funding_cal_direct_dom` over the named reference (positive favours the term), with the two-sided 90% interval of the studentized stationary bootstrap (seed 1032, 10,000 draws); the lower end is the one-sided 95% lower bound. Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days.

Mean scores, pooled (grid CRPS / upper-tail twCRPS): `gbm_funding` 1.8223 / 0.9515, `gbm_funding_cal_direct` 1.8683 / 0.9549, `gbm_funding_cal_aligned` 1.8019 / 0.9360, `gbm_funding_cal_direct_dom` 1.8611 / 0.9516, `spread_mr_ctx` 1.7504 / 0.9077, B1 2.2889 / 1.3750, B1' 1.9281 / 1.0648, B2 2.5184 / 1.1315.

## Reading, under the declared rules

- The term helps over `gbm_funding_cal_direct` on all decision days: skill +0.4%, interval +0.2% to +0.6%.
- It helps on the trough: on target days of the 19th to 23rd, skill +0.7%, interval +0.3% to +1.0%.
- It does not lose on ordinary target days: skill +0.3%, interval +0.0% to +0.6%.
- Against `gbm_funding` (#1027's reading): not shown to beat it on calendar days (skill +0.3%, one-sided 95% lower bound -4.9%), and does not lose on ordinary days (skill -6.6%, interval -15.7% to +1.7%).

## What the numbers say, and what they do not

The term does what it was declared to do and the gain is small. Over its own control it is +0.4% pooled with an interval clear of zero, +0.7% on the 19-23 bucket (the trough Lens A pointed at), and the interval is above zero in 2018-19, 2020 and 2025-26 and straddles zero in 2021-23 and 2024. On upper-tail twCRPS the pooled gain is +0.3% (+0.1% to +0.6%), but 2024 is slightly negative (-0.3%, -0.7% to -0.1%).

It does not close the gap to the other references. Against `gbm_funding_cal_aligned` the term variant is -3.3% pooled (-7.3% to +0.5%) and -18.5% in 2021-23; against `gbm_funding` it is -2.1% pooled (-7.7% to +3.0%) and -9.9% on the 19-23 bucket (-22.1% to +0.8%). The term moves the direct-pairs variant by about 0.007 bp of mean grid CRPS (1.8683 to 1.8611); in 2021-23 the term variant is still -27.8% (-41.7% to -17.0%) against `gbm_funding`. Nothing here shows the term is the missing piece for the trough.

## grid CRPS (23 levels), skill of `gbm_funding_cal_direct_dom` over each reference
### Pooled
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| all decision days | 1,855 | +0.4% [+0.2%, +0.6%] | -3.3% [-7.3%, +0.5%] | -2.1% [-7.7%, +3.0%] |

### By regime (target day)
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| 2018-19 | 361 | +0.3% [+0.1%, +0.7%] | -5.6% [-11.4%, -1.2%] | -3.6% [-10.4%, +1.9%] |
| 2020 | 251 | +0.8% [+0.2%, +1.4%] | -4.0% [-20.4%, +8.8%] | -7.3% [-33.4%, +9.5%] |
| 2021-23 | 748 | -0.0% [-0.5%, +0.4%] | -18.5% [-26.3%, -12.1%] | -27.8% [-41.7%, -17.0%] |
| 2024 | 250 | +0.2% [-0.3%, +0.8%] | +12.8% [+4.3%, +22.1%] | +17.8% [+9.8%, +25.6%] |
| 2025-26 | 249 | +0.7% [+0.3%, +1.1%] | +7.6% [-9.6%, +19.8%] | +14.2% [-6.9%, +28.1%] |

### By target day type
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| ordinary | 848 | +0.3% [+0.0%, +0.6%] | -3.8% [-10.1%, +2.5%] | -6.6% [-15.7%, +1.7%] |
| calendar_days | 1,011 | +0.4% [+0.2%, +0.7%] | -3.0% [-6.5%, +0.3%] | +0.3% [-4.9%, +5.4%] |
| settlement | 742 | +0.6% [+0.3%, +0.9%] | -5.2% [-11.0%, -0.2%] | -5.7% [-13.6%, +0.8%] |
| month_end | 150 | +0.1% [-0.4%, +0.6%] | +2.0% [-4.8%, +12.8%] | +18.1% [+5.3%, +34.4%] |
| tax_date | 89 | +0.1% [-0.2%, +0.4%] | -2.6% [-6.0%, +1.0%] | -2.9% [-7.6%, +1.7%] |
| quarter_end | 30 | +0.3% [+0.1%, +0.5%] | +2.7% [-2.0%, +8.9%] | +14.4% [-11.9%, +39.5%] |

### By day-of-month bucket of the target day
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| 19-23 | 305 | +0.7% [+0.3%, +1.0%] | -6.1% [-15.5%, +2.1%] | -9.9% [-22.1%, +0.8%] |
| 24-31 | 459 | +0.1% [-0.2%, +0.4%] | -4.3% [-10.2%, +3.6%] | +4.6% [-5.9%, +16.0%] |
| 1-5 | 297 | +0.3% [-0.1%, +0.7%] | +5.5% [-2.7%, +12.8%] | +4.8% [-5.5%, +13.3%] |
| 6-14 | 553 | +0.3% [-0.1%, +0.7%] | -8.7% [-17.7%, +0.7%] | -13.7% [-26.9%, -2.2%] |
| 15-18 | 245 | +0.7% [+0.1%, +1.2%] | -3.2% [-9.0%, +5.2%] | -2.2% [-7.2%, +2.6%] |

## Upper-tail twCRPS (weight 1{z > 0 bp}), same layout
### Pooled
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| all decision days | 1,855 | +0.3% [+0.1%, +0.6%] | -1.7% [-5.8%, +1.8%] | -0.0% [-5.8%, +5.3%] |

### By regime (target day)
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| 2018-19 | 361 | +0.3% [+0.0%, +0.6%] | -4.0% [-9.5%, -0.2%] | -2.1% [-8.6%, +3.0%] |
| 2020 | 251 | +0.7% [-0.3%, +2.0%] | +5.5% [-8.1%, +24.3%] | -4.0% [-40.6%, +29.2%] |
| 2021-23 | 748 | -0.2% [-2.7%, +3.6%] | -164.5% [-555.2%, +204.2%] | -20.5% [-118.5%, +20.6%] |
| 2024 | 250 | -0.3% [-0.7%, -0.1%] | +8.4% [+2.1%, +58.5%] | +10.9% [+2.2%, +24.5%] |
| 2025-26 | 249 | +0.6% [+0.1%, +1.0%] | +5.6% [-26.4%, +20.7%] | +11.8% [-27.3%, +35.0%] |

### By target day type
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| ordinary | 848 | -0.1% [-0.5%, +0.4%] | -2.2% [-9.7%, +4.5%] | -5.6% [-19.1%, +5.6%] |
| calendar_days | 1,011 | +0.5% [+0.1%, +0.8%] | -1.4% [-4.5%, +1.1%] | +2.1% [-2.3%, +6.8%] |
| settlement | 742 | +0.8% [+0.4%, +1.2%] | -4.0% [-13.0%, +1.7%] | -4.1% [-16.6%, +3.6%] |
| month_end | 150 | +0.4% [-0.3%, +1.3%] | +3.3% [-0.3%, +7.8%] | +21.1% [+0.5%, +54.5%] |
| tax_date | 89 | +0.0% [-0.2%, +0.2%] | -1.3% [-3.7%, +0.9%] | undefined |
| quarter_end | 30 | +0.2% [+0.1%, +0.5%] | +3.6% [+0.5%, +6.2%] | +12.8% [-7.9%, +27.9%] |

### By day-of-month bucket of the target day
| group | days | over direct | over aligned | over gbm_funding |
|---|---|---|---|---|
| 19-23 | 305 | +0.8% [+0.4%, +1.2%] | -11.9% [-29.0%, +4.7%] | -14.0% [-34.4%, +0.9%] |
| 24-31 | 459 | -0.0% [-0.4%, +0.4%] | -3.7% [-9.0%, +1.8%] | +6.3% [-3.6%, +15.8%] |
| 1-5 | 297 | +0.4% [-0.0%, +0.9%] | +6.0% [-4.4%, +14.4%] | +4.6% [-8.8%, +14.0%] |
| 6-14 | 553 | +0.0% [-0.8%, +1.0%] | -9.9% [-28.9%, +4.8%] | -12.0% [-46.6%, +7.0%] |
| 15-18 | 245 | +0.6% [-0.0%, +1.0%] | +0.3% [-2.2%, +3.8%] | +0.2% [-3.2%, +3.2%] |

## Marked questions for Eleonora (nothing settled in code)

1. **Adopt the term, or name it with a variant of #1027 as the candidate?** Evidence: the gain over the direct-pairs control is small and positive (+0.4% pooled, +0.7% on 19-23); against `gbm_funding` and `gbm_funding_cal_aligned` it is not shown to help. Default if unanswered by the next 5 pm batch: no change to the candidate or to any declaration; the variant stays a development result.
2. **Add the term to the aligned variant too?** That needs her `ONE_STEP_ALLOW_LIST` entry first (PR body, question 1). Default: not asked for; the aligned variant is untouched.
3. Bucket edges (1-5, 6-14, 15-18, 19-23, 24-31) were declared before any score; a different cut is a new declaration. Default: keep as declared.

## Checked, and not checked

Checked: the scores of the five new walks (leads 1 to 5) and of #1027's reference walks are read as they came from the Mac (`score.json`, `report.md`); this page, `result.json` and the research-log entry quote them without recomputation, and `result.json` is extracted from `score.json` mechanically. Not checked: the walks were not re-run in the cloud (they take hours, `needs-mac`); the 20 control walks are #1027's, on her Mac, not committed. The environment of the walks is recorded in `result.json` (Python 3.11.17 on the Mac; the numpy and scikit-learn versions went to `~/1032.log` there and are not in the tree). The full suite runs in the PR's CI.
