# Does the settlement driver pick up the 15th, month-end and the bill days? (#339)

Status: a check, and a scored candidate, by the pull request that closes #339. It changes no feature, panel column, published record or
declaration. The code is `scripts/settlement_check.py`, the lists are in
`docs/pivot/evidence/settlement-check/settlement_check.json`, and `tests/test_settlement_check.py` pins the
finding. Every date is on or before 2025-12-31 (`docs/decisions/lockbox.md`); the panel is the published one,
rebuilt from the tracked fixtures (`docs/pivot/next-session.md`), and the auctions are the tracked Treasury
snapshot.

## The pattern checked

Eleonora's ruling on #339:

- 3-, 10- and 30-year notes and bonds are auctioned in the second week of the month and settle on the 15th, or
  the next business day.
- 2-, 5- and 7-year notes settle on the last day of the month.
- Bills mostly settle on Thursdays, some on Tuesdays.

For each month from April 2018 to December 2025 the script takes the 15th and the last calendar day, moves each
to the next business day in the panel, and asks whether `treasury_settlement_coupons` is above zero on it. That
column is what the day-type tag `coupon_settlement` and the `settlement_day` features read.

## Result

1. **Every date of the pattern is flagged.** The 15th (or next business day) and the month-end (or next business
   day) are above zero in `treasury_settlement_coupons` in every month of the window. `pattern_dates` in the JSON
   lists them with their kind, `pattern_dates_not_flagged` is empty, and `by_year` gives the same per year. Nothing
   is missed, so no fix is needed for the feature to "pick up" the two coupon settlement dates.
2. **Every flagged day is a settlement the snapshot carries.** `flagged_without_a_coupon_issue_in_snapshot` is
   empty. No issue is announced on or after the day it settles (`issue_dates_announced_on_or_after_the_issue_date`
   is empty), so the amounts are known before the day they settle.
3. **The flag is wider than the pattern.** `flagged_outside_pattern` lists the other coupon days, with what the
   snapshot says settled on each. They are floating-rate notes (the 2-year FRN and its reopenings), inflation-
   protected securities, and 20-year bonds, which settle on other days, mostly in the last week of the month, for
   example 2018-05-25 and 2018-06-29. The column sums every `Note` and `Bond` record by Treasury's own bill and
   coupon split (`TREASURY_COUPON_SECURITY_TYPES` in `src/repo_model/contract.py`), so these are coupon
   settlements by that definition, and the flag marks them too. They are not the "2-, 5- and 7-year" or
   "3-, 10- and 30-year" settlements the ruling names, so "coupon settlement day" is the pattern's two dates plus
   these.
4. **One nominal settlement sits off the pattern's dates.** `snapshot_mid_month_or_month_end_issues_off_pattern_dates`
   lists it: a 10-year reopening that settled on 2019-06-26, not on the 15th or at month-end. The flag picks it
   up, since the column reads the issue date.
5. **Bills.** Bills settle on Thursdays and Tuesdays: `bills.flagged_by_weekday` is dominated by the two days.
   Tuesday settlements begin in December 2018 (`first_tuesday_bill_issue`, the 4- and 8-week bills moved), and
   from then every Tuesday and every Thursday of the panel carries bills
   (`thursdays_and_tuesdays_since_the_first_without_bills` is empty). The other weekdays carry cash-management bills
   and holiday shifts.

## What was not checked

- The as-of availability of the settlement columns at a decision instant is covered by the existing
  `scheduled_availability` tests; this check reads announcement dates against issue dates only.
- Whether `settlement_day` (the calendar of the scored day) is the right input is not examined: the check asks
  only what the existing columns flag.
- The snapshot carries no `TIPS` or `FRN` security type: Fiscal Data records them as `Note` and `Bond` with the
  `floating_rate` and `inflation_index_security` flags, which is how the script names them.

## The narrowed flag, scored (Eleonora's ruling on #339 and on this pull request)

The published declaration reads the coupon-settlement day only through its scorecaster's fourth indicator
(`treasury_settlement_coupons > 0`, at h = 1). The candidate narrows that indicator to the ruled settlements (3-, 10-
and 30-year on the 15th or next business day; 2-, 5- and 7-year at month-end or next business day; FRN, TIPS,
20-year and off-date settlements not marked) and changes nothing else. The test was declared in
[`settlement-flag-test.md`](settlement-flag-test.md) in a commit before any scoring, and is run by
`scripts/settlement_flag_candidate.py`; the figures are in
`docs/pivot/evidence/settlement-flag/settlement_flag_candidate.json`. Days: 2018-06-29 to 2025-12-31, no later row
loaded. The published side reproduces the CRPS record's per-day losses and the pressure record's Brier at +5 and
+10 bp exactly.

The narrowed flag marks 186 of the 251 days the published flag marks. The paired figures (published minus
candidate, so a positive mean favours the candidate), with 90% stationary-bootstrap intervals:

| Figure | Mean difference | 90% interval | Cells worse beyond their interval |
|---|---|---|---|
| Five-quantile score (CRPS, bp) | -0.0036 | -0.0091 to 0.0013 | quarter-end |
| Brier at +5 bp | -0.00056 | -0.00094 to -0.00024 | month-end, quarter-end, tax date, 2018-19, 2020, 2021-23 |
| Brier at +10 bp | -0.00046 | -0.00070 to -0.00025 | month-end, ordinary, quarter-end, 2018-19, 2020, 2021-23 |

**It does not improve the model by the declared test**: no figure's lower bound is above zero, and the pressure
probability is worse at both thresholds with its whole interval below zero. So the narrowed flag **stays off** in
the published declaration and this pull request only reports it. No published figure, panel column or declaration
moves, and the live record and its pin are untouched.
