# gbm_funding with every calendar and scheduled column read from the target row (#1027, H5 step 3/4 re-run): design

**Status: design and declaration. Nothing is scored here.** The walks take hours and run on Eleonora's Mac (`needs-mac`, #46); the result page replaces this section when they have been scored. Development data, never a verdict. The declaration is `metadata/aligned_calendar_1027.json`, committed before any number was computed; the script is `scripts/aligned_calendar_1027.py` (commands in its docstring); the test is `tests/test_aligned_calendar_1027.py`.

## The rule

Rule 2 of `src/repo_model/asof.py` serves a calendar column, and every column of a field a source lists under `scheduled_availability`, from the **target** row of a forecast. A model must be trained on what it is served: in the training pair whose target is row t, those columns are row t's. `gbm_funding` trains on one-step pairs `(p, p + 1)` with row p's design, so it trains each such column one day off (#914). It also has no calendar day-type input at all, and its one scheduled input, `treasury_settlement`, is read only at lead 1.

## The two variants

Both read `gbm_funding`'s published inputs at the lead (as of the decision instant), plus the target-row columns, plus the observed `net_settlement` and `net_settlement_due_5d` (dated at their own day, so read as of the decision instant, not from the target). They differ in the pairing only.

| variant | pairing | what makes the columns aligned |
|---|---|---|
| `gbm_funding_cal_aligned` (i) | `gbm_funding`'s one-step pairs, at every lead | `align_columns`: row p carries row p + 1's value of each target-row column, so the pair `(p, p + 1)` trains them from its target row; the observed columns of row p are untouched |
| `gbm_funding_cal_direct` (ii) | #951's direct pairs (`training_pairs="direct"`) | each target is paired with its own as-of read, so every column is trained from the row it is served from |

Settings are `gbm_funding`'s (seed, quantile grid, refit every 21 scored days, 61 days of minimum history) except `min_samples_leaf`, declared at 5: #951 section 2 shows that a leaf of 20 can isolate quarter-ends in only about a third of the refits and a leaf of 5 in most. #951 tested 5 and 20 only; 10 is untested.

## The #947 guard

`repo_model.one_step_guard` (merged under #947) refuses a calendar or scheduled regressor on any one-step fit, aligned or not, and says to train on direct pairs. Its allow-list is pinned and is Eleonora's. Variant (ii) passes. Variant (i) is refused as the code stands; it runs only once she adds an allow-list entry for the fitter and each lead's regressors. The tests run (i) with a stand-in entry and show the refusal without it. **Marked question:** admit (i), or drop it and run (ii) alone.

## Which columns at which lead

| lead | target-row columns |
|---|---|
| 1 | `quarter_end`, `days_to_month_end`, `tax_date`, `treasury_settlement`, `treasury_settlement_coupons`, `treasury_settlement_bills` |
| 2 to 5 | `quarter_end`, `days_to_month_end`, `tax_date` |

**A finding against the directive's wording, marked for Eleonora.** Criterion 1 reads every calendar and scheduled column at each lead h = 1 to 5. The settlement columns are scheduled fields declared public at 15:00 the business day before the target (`metadata/sources.json`, `treasury_auctions`), so a decision at lead 2 or more cannot read them: `InformationRule.check` raises `LookAheadError`, and `gbm_funding` already drops `treasury_settlement` beyond lead 1. The calendar columns are known in advance and are read at every lead. This design reads every column the information set allows and no more. `LeadAvailabilityTests` shows both halves.

## What is tested

`tests/test_aligned_calendar_1027.py` fits both variants for real at all five leads on a synthetic panel whose every column value is unique to its row, records the design the estimators receive, and requires each target-row column of every training pair to be the value of that pair's target row (the target is identified by its unique spread). The observed columns must stay row p's. The control case, `gbm_funding`'s fit as it stands on main, is shown to train every such cell one day off. The mutation that makes the aligned variant read row p again fails the test; the record is in the test's docstring.

## What the result page will report (criterion 3 and 4)

Paired grid CRPS and upper-tail twCRPS of each variant against `gbm_funding`, B1, B1', B2 and `spread_mr_ctx`, pooled, by regime and by target day type (quarter-end, month-end, tax date, settlement, ordinary), on development days to 2025-12-31 only, on the studentized one-sided bound (ruling 1) with Lens C's caveat on the lag-10 standard error. It says which variant, if either, beats `gbm_funding` on calendar days without losing on ordinary days, under the rule declared in the declaration. Replacing the candidate is Eleonora's decision.
