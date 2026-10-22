# The 15 October tax-date column on the calendar-aware variants (#1095, finding #1004; H5 step 3, calendar first): design

**Status: design and declaration; nothing is scored yet.** The walks go to Eleonora's Mac (`needs-mac`, #46). **Development data, never a verdict, and nothing is published.** The declaration is `metadata/october_tax_1004.json`, committed before any number was computed; the script is `scripts/october_tax_1004.py` (commands in its docstring); the test is `tests/test_october_tax_1004.py`. The result page, `docs/research/october-tax-1004-result.md`, comes with the walks.

## What is asked

Eleonora's ruling on #1004 (20 October 2026, corrected): the 15 October `tax_date` label is **deferred, not rejected**. #979 tested it only in B2 and in H8's calendar ranker, on the days that prompted it (2019-10-15, 16 and 17; 2025-10-15 and 16), and no learned model ever read it, because the H5 candidate read no calendar input at all. It is tested again with a candidate that reads calendar days at the target day (#1027), and only on a reading that leaves out the 2019 and 2025 October days, or on 2026 development days. `tax_date`, B2 and every existing declaration stay as they are; adopting the label is hers.

## The column

`tax_date_october` (`repo_model.tax_date_october.add_columns`) is 1.0 on the 15th of October rolled forward off weekends and DC holidays (the rule of `data.corporate_tax_deadline`, 26 U.S.C. 7503) and on the two market days after it, and 0.0 on every other day. It is a function of the row's own date and `metadata/market_holidays.json`: nothing is read from a source, so there is nothing to look ahead into. It is written about the target day, so it is declared in `repo_model.target_day_columns`; `asof` rule 2 serves it from the scored row, and `one_step_guard` refuses it on any one-step fit that the allow-list does not admit. It is in no published declaration and not in `contract.CALENDAR_FEATURES`: the study serves it as a calendar column for the run only (`switched`).

## The two arms

| arm | adds the column to | pairing | status |
|---|---|---|---|
| `gbm_funding_cal_direct_october` | `gbm_funding_cal_direct` | direct pairs (`training_pairs="direct"`) | passes the #947 guard; walked on the Mac |
| `gbm_funding_cal_aligned_october` | `gbm_funding_cal_aligned` | one-step pairs on the aligned frame | **not run unless she admits it** (below) |

An arm is its variant plus the one column at every lead h = 1 to 5; its other inputs, leaf, seed, quantile grid, refit cadence and pairing are the variant's. The deadline rule is public law and the calendar is known years ahead, so unlike the Treasury settlement columns the column is read at every lead.

## The aligned arm and the #947 guard

`one_step_guard` refuses a calendar or scheduled regressor on any one-step fit, and the new column is in `target_day_columns.TARGET_DAY_COLUMNS`. #1027's two allow-list entries match that variant's regressors exactly, so the aligned arm, which has one more, is refused. A new entry is her decision (`CLAUDE.md`); none is added here. `walk` refuses the aligned arm before any work and writes nothing, and `score` reports it as not run. If she admits it, the same script walks it: the entry's regressors are `arm_features(ALIGNED_OCTOBER, h)` less the target at each lead, and the tests run the arm with a stand-in entry.

## What is scored

Paired, on development days to 2025-12-31 only, the studentized stationary bootstrap (seed 1095), grid CRPS and upper-tail twCRPS, with the interval of the mean difference beside the skill:

* each arm over its #1027 variant without the column, over B1, over B2 and over `gbm_funding`; each variant over B1 and B2 beside them;
* each arm and variant over **B3**, the published distribution, on its five levels (the protocol's secondary comparison), on the decision days with all five published leads;
* pooled, by regime, by the target day's reporting day type (quarter-end, month-end, tax date, settlement, ordinary), and on the October cuts, which overlap the types: the window in every year (`october_window`), the window with 2019 and 2025 left out (`october_without_2019_2025`), and ordinary days outside the window (`ordinary_outside_october`, where the column is 0, so a loss there is the cost of carrying it). The October window by year is listed with the realised spread and each model's mean score.

**The two readings the ruling asks for.** (1) With the 2019 and 2025 windows left out: scored. (2) On the 2026 development days the lockbox leaves open (2026-01-01 to 2026-09-03): **not scoreable on this panel.** The panel ends on 2026-09-03, so the October 2026 window (15, 16 and 19 October) is in the blind tier, which no comparison may score; the open 2026 days hold no October window; and the study window is #1027's 2025-12-31, because the control's and the variants' walks end there. `reading_2026` reports this in the result. Extending the window to the open 2026 days would need new walks of the control and of the variant, and would only show that the column costs nothing where it is 0: a marked question for Eleonora, default no.

**The declared reading.** An arm **helps** over its variant when the lower end of the studentized interval of its mean grid-CRPS difference on `october_without_2019_2025` is above 0 (finding #1004 read the mean difference, whose interval covered zero), and **loses** outside October when the upper end on `ordinary_outside_october` is below 0. The window in every year is context, to show what the two motivating years add. The October cuts hold few target days, so their intervals are weak; the cuts are scored from a floor lower than the other groups' (declared), and Lens C's caveat on the lag-10 standard error applies to every interval.

The walks of `gbm_funding` and of `gbm_funding_cal_direct` are #1027's and are reused from the Mac (`~/rmm-1027`); `score` refuses an arm walk made from another scratch panel or on other inputs than the declared ones.

## What the result page will say

Whether the column helps in the October window once the days that prompted it are out, whether it costs anything elsewhere, and what that means for adopting the label. It will not decide the adoption.
