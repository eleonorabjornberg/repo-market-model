# Decision: a quarter-end window and per-quarter peak pressure

**Status: decided by Eleonora, 2 October 2026 (#140; ruling on PR #186). In force once PR #186 merges.** A session
drafted it at her request of 2 October 2026, and she approved the draft with the two choices below. No published
panel or declaration reads the column, and no record already published changes.

## The question

`quarter_end` (`calendar-columns.md`) marks one day: the quarter's last business day. Quarter-end pressure does not
always peak on that day. When the peak lands a day before or after it, that day counts under another day type
(`month_end` or `ordinary`), so the `quarter_end` split misses it. Eleonora asked for a window around the day, and
for one peak per quarter, to match how the New York Fed measures this pressure.

## The decision

1. **A calendar column `quarter_end_window`.** It is 1.0 on the quarter's last business day (the day `quarter_end`
   marks) and on the two business days either side of it. It is 0.0 on every other day. Business days come from
   `metadata/market_holidays.json`, the same table `quarter_end` uses. So the window skips weekends and days with no
   SOFR publication, and the two days after quarter end fall in the next quarter. Like the other calendar columns it
   is a function of the date alone: it reads no observation and no panel row. Code: `data.quarter_end_window` and
   `data.quarter_end_window_days`.
2. **A `quarter_end_window` split, reported alongside the day types.** Every scored day is either
   `quarter_end_window` or `outside_quarter_end_window`, read from its date. It is a separate grouping, reported
   beside `by_regime` and `by_day_type` as `by_quarter_end_window`. It is not a new entry in the day-type precedence.
   `metadata/evaluation_splits.json`, its precedence and the `quarter_end` type do not change, so no published split
   table moves. Code: `evaluation_splits.quarter_end_window_label` and `baseline.split_document`.
3. **Per-quarter peak pressure.** For each quarter, the peak is the maximum of SOFR − IORB over the quarter's window:
   one value per quarter. For each model, the forecast for that peak is the highest P(> +5 bp) and the highest
   P(> +10 bp) the model gave on any day of the window. Each of those probabilities is the forecast made for that day
   at that day's own as-of decision instant. A peak is above τ when its spread, read on whole basis points, is
   strictly above τ (`pressure-probability.md`, ruling of 2 October 2026 on #155). Code:
   `quarter_peaks.quarter_peak_table`. The table honours `lockbox.md`: it reads no window day after its end date, and
   it raises `LookAheadError` on a day in a locked tier.

## Her two choices

1. **The measure: keep ours, cite theirs.** The window measures SOFR − IORB, the panel's target, on the project's own
   labels. The New York Fed's published measure, month-end SOFR − ON RRP (below), is cited as related work, and the
   departures from it are recorded below. No label and no past record changes.
2. **`by_quarter_end_window` on new records.** Every record published from now on carries the window split beside
   `by_regime` and `by_day_type`. Records already published stay as they are, under the rule that a published record
   is never edited in place. The split is written by `baseline.split_document`, which every record's split path
   calls (`tests/test_benchmarks.py`, `test_a_new_record_carries_the_quarter_end_window_split`).

## The New York Fed source

The window follows the New York Fed's measure of **month-end** repo pressure. Roberto Perli, System Open Market
Account Manager, used it in two speeches:

- *Facing Quarter-End Pressures: Understanding the Repo Market and Federal Reserve Tools*, New York University,
  12 November 2024. Slide 2, "Month-end Repo Spread (SOFR Spread to ON RRP)", under the heading "Quarter-end spreads
  wider than recent reporting dates, similar to 2015-2017". The chart note reads: "Month-end spread calculated as the
  maximum SOFR-ON RRP in the 5-day period centered on the last business day of the month." Slides:
  https://www.newyorkfed.org/medialibrary/media/newsevents/speeches/2024/Understanding-the-Repo-Market-and-Federal-Reserve-Tools-Slides.pdf;
  speech: https://www.newyorkfed.org/newsevents/speeches/2024/per241112.
- *Money Market Conditions and the Federal Reserve's Balance Sheet*, 2025 U.S. Treasury Market Conference,
  12 November 2025. Chart 5, "Month End SOFR-ON RRP Spread". The chart note reads: "Month end spread calculated as the
  maximum SOFR-ON RRP spread in the 5 day period centered on the last business day of the month." Slides:
  https://www.newyorkfed.org/medialibrary/media/newsevents/speeches/2025/Roberto-Perli-Nov-12-2025-slides.pdf.

**Where the decision departs from the source.** Eleonora kept these departures (choice 1 above).

- **The spread.** The source measures SOFR minus the ON RRP rate. This decision measures SOFR − IORB, the panel's
  target. The ON RRP rate sits at the bottom of the target range and IORB sits above it, so the two spreads differ by
  a constant set by policy within any one setting. The peak day is the same under either spread. Its level is not.
- **The period.** The source window is centred on each month's last business day. Here it is centred on each
  quarter's last business day, as the directive asked. Every quarter end is also a month end, so this is the source's
  window at the subset of month ends that are quarter ends.
- **Not verified.** The directive describes the New York Fed's measure as "the maximum SOFR − IORB over a
  5-business-day window centred on the quarter's last business day". The drafting session did not find that wording on a
  New York Fed page it could read. A web search attributed it to the New York Fed Teller Window post "Monitoring
  Money Market Dynamics Around Year-end" (16 January 2025,
  https://tellerwindow.newyorkfed.org/2025/01/16/monitoring-money-market-dynamics-around-year-end/). This
  environment's egress proxy blocks that host, so the post was not read and is not cited as the source here.
- **"5-day period".** The source does not say business days, but a window centred on a business day and counted in
  SOFR publication days is the natural reading, and is what this decision uses.

## What it does not change

- `quarter_end` still marks only the last business day of the quarter (`tests/test_quarter_end_window.py`,
  `test_quarter_end_is_unchanged`).
- `quarter_end_window` is an opt-in panel column (`data.OPT_IN_COLUMNS`). The published panel's documented build
  names no columns, so it does not build this one, and the panel digest does not move.
- The day-type precedence, `metadata/evaluation_splits.json` and every record in `docs/runs/` are unchanged.
- No declaration reads the column as a model input. Making it a feature is a separate scored question.
