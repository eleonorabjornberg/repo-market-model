# Decision: the calendar columns

**Status: decided and declared; the columns build. The panel rebuild that puts them into published
records has not run.**

## What was decided

Three columns, each a function of the scored date alone and contributing no source:

- `days_to_month_end` — calendar days remaining until the last day of the month. Zero on the last
  day; 27 to 30 on the first, depending on month length. Unclipped and unsigned.
- `quarter_end` — the last business day of March, June, September or December: the last weekday of
  the quarter not in the market holiday table. Until 1 October 2026 it was the last calendar day; see
  below.
- `tax_date` — the statutory corporate estimated-tax date, rolled forward off Saturdays, Sundays and
  the legal holidays of the District of Columbia, **and the two business days that follow it**.

`fomc_scheduled` was considered and deliberately not declared. It is not a function of the scored
date; it draws on an announced schedule with a publication date and an availability bound, so it
needs a source declaration rather than a calendar-feature entry. Declaring it in `CALENDAR_FEATURES`
would smuggle a source past the classifier, which is the one thing that classifier exists to prevent.

## Why a countdown and not a signed distance

The first design measured a signed distance to the *nearer* month boundary, clipped at five days. It
was wrong twice over, and both faults are worth recording because they are easy to repeat.

Measured from zero, it gave the last day of a month and the first day of the next the same value —
destroying precisely the asymmetry that justified signing the column at all. And the clip collapsed
every mid-month day to the bound, so the column carried no information on the September 2019 and
March 2020 days: most of the days in the panel that move the spread twenty basis points or more sit
at a month boundary, but the ones that do not are exactly those two episodes, and they are what a
calendar was wanted for.

A plain countdown has neither fault. The month is one monotone ramp, the two boundaries sit at
opposite ends of it, and the middle stays resolved. The cost is that a tree spends two splits to
express "either end of the month" where a signed column spends one. That is the trade, and it buys
back the middle.

## Amended 1 October 2026: `quarter_end` on business days

Eleonora's decisions on #44: 30 September 2026, that `quarter_end` marks the last business day of
the quarter, and 1 October 2026, ruling on the review of that change, that business days come from
a published holiday schedule, not from the panel's grid.

`quarter_end` is 1.0 on the last weekday of the quarter that is not in
`metadata/market_holidays.json`, and 0.0 otherwise. It is computed from the date and the table
alone, so it stays a function of the scored date. The table lists the days with no scheduled SOFR
publication, each with its date, reason and source, and its checksum is pinned in
`data.MARKET_HOLIDAYS_SHA256`. The panel's target is SOFR − IORB, so a business day for the
calendar columns is a day the New York Fed publishes SOFR (#59, decided under Eleonora's
delegation, 1 October 2026). Where SIFMA recommended only an early close and SOFR was not
published, as on Good Friday 2021, 2023 and 2026, the day stays in the table, and its row records
SIFMA's actual recommendation and cites the New York Fed's publication schedule. An unscheduled closure is a new table entry, added by a reviewed pull request.

The table carries no announcement date for now (Eleonora, 1 October 2026, deferring the question).
That is a known limit: a closure announced after a decision date can land on a quarter's last
weekday, and then the weekday before it would read 1.0 on a rebuilt panel although nobody knew at
that day's decision instant. If one does, the pull request that adds it must add announcement dates
to the table and make `quarter_end` respect them.

`days_to_month_end` and `tax_date` are unchanged, and neither reads the table.

## A quarter-end window

Decided by Eleonora, 2 October 2026 (#140; ruling on PR #186), in force once PR #186 merges.
[`quarter-end-window.md`](quarter-end-window.md) adds a column `quarter_end_window` covering the quarter's last
business day and the two business days either side, a split reported alongside the day types on every new record,
and a per-quarter peak of SOFR − IORB. It leaves `quarter_end` as decided above.

## Why calendar days and not business days

Three reasons, in the order they bind.

`data.py` refuses to invent a holiday calendar, and says so in four places — the coverage grid
construction, the refusal of `ref_date` with `business_days`, rule 8, and `splits.py` on why a
leakage guard must not depend on one. A business-day month boundary needs exactly that calendar.

Regulatory balance-sheet reporting falls on calendar month and quarter ends, so the calendar
boundary is also the economically correct one.

And the evidence that motivated the column was measured in calendar days.

## The one place a holiday rule is unavoidable, and how it is bounded

`tax_date` cannot be computed without one: the statutory date rolls forward off weekends *and legal
holidays*, and over the declared span weekend-only rolling gets several of the deadlines wrong —
every one of them DC Emancipation Day, which moves federal filing deadlines. The same holidays also
move the two window days that follow the deadline, on further dates.

What is added is therefore **not a holiday calendar and must not be used as one**. It is the
statutory rolling rule for a single deadline, limited to the four deadline months, and it is pinned
by a test that names both sides of each moved date. If that set ever changes, the test goes red and
a human looks. The refusal in `data.py` stands.

## What the evidence was, and what it was not

The design was argued from the days in `data/processed/funding_panel.csv` that move the SOFR–IORB
spread most, and from the FOMC and statutory calendars around them. Two premises the project had
been carrying did not survive that check and are corrected here: the September 2019 corporate tax
date is the Monday, not the Tuesday, so a same-day flag fires on the smallest of the three moves and
misses both larger ones — which is why `tax_date` is a window; and the March 2020 pair is a
*cancelled* scheduled meeting, which is why a schedule feature must read the schedule as published
before the decision date rather than the realised record.

This is coverage of the days that motivated the feature. **It is not evidence that the model scores
better.** Every feature this repository had previously built made the exceedance metric worse at
every declared threshold — see the single-feature records in `docs/runs/`. The prior for a new
feature here is that it does not help. The rebuild and the re-score have since decided it, and they decided it against that prior.
Scored like for like against the control -- same panel, same purge, same fold count, because
these columns are computed from the scored date and declare no source -- the calendar set is the
first this repository has built that improves the threshold-weighted metric rather than degrading
it. It improves the skill at the two widest declared thresholds and costs the narrower one, and it
makes the log score unavailable at one threshold, which is the same trade the fitted tail makes.
The comparison is `docs/runs/exceedance_gbm_conformal_calendar_mh61.json` against
`docs/runs/exceedance_gbm_conformal_mh61.json`; the records carry the numbers.

The prior stated above was the right prior to hold and it was wrong here. Both halves of that are
worth keeping: the sentence about every previously built feature is still true of every feature
*derived from the target* -- the lags, the GARCH variance, the ARX forecast -- and the funding and
market columns remain unscored, because they were declared and empty. Three cases, three answers.
