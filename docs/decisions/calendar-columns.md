# Decision: the calendar columns

**Status: decided and declared; the columns build. The panel rebuild that puts them into published
records has not run.**

## What was decided

Three columns, each a function of the scored date alone and contributing no source:

- `days_to_month_end` — calendar days remaining until the last day of the month. Zero on the last
  day; 27 to 30 on the first, depending on month length. Unclipped and unsigned.
- `quarter_end` — the last calendar day of March, June, September or December.
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
feature here is that it does not help. The rebuild and the re-score decide it; nothing above should
be read as anticipating them.
