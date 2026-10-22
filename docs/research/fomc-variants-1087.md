# The FOMC meeting columns on the calendar-aware variants (#1087, H5 step 3, calendar first): design

**Status: design and declaration. Nothing is scored here.** The direct arm's walks take hours and run on Eleonora's Mac (`needs-mac`, #46); the result page replaces this section when they have been scored. **Development data, never a verdict.** The declaration is `metadata/fomc_variants_1087.json`, committed before any number was computed; the script is `scripts/fomc_variants_1087.py` (commands in its docstring); the test is `tests/test_fomc_variants_1087.py`.

## What is asked

Eleonora's ruling of 21 October 2026 on #1046: "calendar first". FOMC meeting days are calendar days, so `fomc_meeting_day` and `fomc_days_to_next_meeting` (#1038) are tested on the two calendar-aware variants of #1027, not left off. Whether they join a published declaration is her question and comes back to her with the result; no published declaration, record or figure changes here.

## The two arms

| arm | adds the columns to | pairing | status |
|---|---|---|---|
| `gbm_funding_cal_direct_fomc` | `gbm_funding_cal_direct` | direct pairs (`training_pairs="direct"`) | passes the #947 guard; walked on the Mac |
| `gbm_funding_cal_aligned_fomc` | `gbm_funding_cal_aligned` | one-step pairs on the aligned frame | **not run unless she admits it** (below) |

An arm is its variant plus the two columns at every lead h = 1 to 5; its other inputs, leaf, seed, quantile grid, refit cadence and pairing are the variant's. The meeting calendar is known well ahead, so unlike the Treasury settlement columns (public at 15:00 the business day before the target, lead 1 only) the FOMC columns are read at every lead.

## Read at the target day

The columns are written about the target day, so `asof` rule 2 serves them from the target row, and a meeting counts only from the instant its schedule was public:

* **The column.** `with_fomc(rows, h)` gives row T the values read at the 16:00 decision instant of the panel day h rows before T (`fomc_calendar.add_columns(horizon=h)`). A scheduled meeting counts from the earliest Board release that lists it, an unscheduled one from its own release, a cancelled one stops counting from its cancellation's; each meeting a value uses passes `fomc_calendar.require_public`, which raises `LookAheadError`.
* **The declaration.** The source is declared to `InformationRule` for the study as a scheduled field available h panel days ahead at 16:00 (`fomc_registry(h)`), so the rule serves the columns from the target row and `check` raises `LookAheadError` for a read that was not public. The registries on disk are unchanged; `metadata/sources_measurement.json` still has the source off every published declaration.
* **The fit.** The direct arm trains each pair's columns from the pair's target row by construction. The aligned arm's one-step pairs train them from the frame whose row p carries row p + 1's (`align_columns`, then `require_aligned` before every fit).

## The aligned arm and the #947 guard

`one_step_guard` refuses a calendar or scheduled regressor on any one-step fit, and the FOMC columns are in `target_day_columns.TARGET_DAY_COLUMNS`. #1027's two allow-list entries match that variant's regressors exactly, so the aligned arm, which has two more, is refused. A new entry is her decision (`CLAUDE.md`); none is added here. `walk` refuses the aligned arm before any work and writes nothing, and `score` reports it as not run. If she admits it, the same script walks it: the entry's regressors are `arm_features(ALIGNED_FOMC, h)` less the target at each lead (leads 2 to 5 share one set), and the tests run the arm with a stand-in entry.

## What is scored

Paired, on development days to 2025-12-31 only, the studentized stationary bootstrap (seed 1087), grid CRPS and upper-tail twCRPS, pooled, by regime, and by target-day type:

* each arm over its #1027 variant without the columns, and each arm over `gbm_funding`;
* the five #1027 types (quarter-end, month-end, tax date, settlement, ordinary) plus the union of the calendar types, and FOMC days as their own type: `fomc_day` (every meeting day, both days of a two-day meeting), `fomc_ordinary` (a meeting day with no other type) and `ordinary_non_fomc`. These three overlap the five exclusive types and are labelled after the fact, for scoring only, never as an input.
* The declared reading: an arm **helps** over its variant when the lower end of its grid-CRPS skill interval on `fomc_day` is above 0, and **loses** on ordinary non-FOMC days when that interval is wholly below 0. Against `gbm_funding` the rule is #1027's. Lens C's caveat on the lag-10 standard error applies to every interval.

The walks of `gbm_funding` and of the #1027 variants are #1027's and are reused from the Mac (`~/rmm-1027`); every walk records the panel and the FOMC calendar digests, and `score` refuses a walk from another calendar.

## What the result page will say

Whether the columns help on the days they describe, whether they cost anything on ordinary days, and what that means for #1046's question. It will not decide the publish question.
