# Draft: the month-end turn is the one month-end definition (#1135)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1135, from her ruling of 22 October
2026 (relayed by the orchestrating session; five-lens review item 1, Lens A, #958; the label is the one #959 and PR #975
measured). It binds nothing until she merges it into `docs/decisions/month-end-turn.md` with her own `GO #1135`. Until then
the implementation below is inert: `repo_model.turn_days.IN_FORCE` is `False`, and every reader gives what it gave before.
This is a §13 change to `scoring-protocol.md` (ruling 6 and the implementation ruling on B2's day type), and the definition
is a data meaning: both are hers.

## The question

The repo's month-end day type is the month's last two business days (`data.MONTH_END_BUSINESS_DAYS = 2`;
`SplitDeclaration.reporting_day_type`). On the published panel the penultimate day is ordinary and the pressure sits on the
last business day and the first of the next month (#959, Lens A). B2 pools by that type, so its month-end pool mixes cold
penultimate days with hot last days, and the same label feeds the mean-reversion level, H6's risk dates and H8's calendar.
#800 left open which reading is the shared one.

## The decision

1. **One definition for H2, H5, H6 and H8, B2 included.** A business day is a weekday not in
   `metadata/market_holidays.json`. The day types, in this precedence:
   - `year_end`: the last business day of December and the first business day of January;
   - `quarter_end_turn`: the last business day of March, June and September and the first business day after it;
   - `turn`: the last business day of any other month and the first business day of the next;
   - `tax_date`: the calendar column's tax date, on a day that is none of the above;
   - `ordinary`: every other day. The penultimate day and the run-up days are ordinary.
2. **26 December is its own flag**, `turn_days.december_26`, which the pools read as ordinary, as #959 declared.
3. **The definition is a function of the date and the holiday table alone.** No source, publication time or revision is
   read, so no leakage or staleness guard is involved.
4. **It replaces `month_end` (two business days) as the type a result is reported by and B2 pools by.** One place in `src/`
   holds it, `repo_model.turn_days.turn_day_type`. `SplitDeclaration.reporting_day_type` delegates to it, and so do all its
   readers: `protocol_benchmarks.b2_forecast`, `spread_mean_reversion.ordinary_levels`, `b1_calendar`, `ranking_daytype`,
   `anchor_day_type`, `risk_dates.is_risk_date(..., reporting_on=...)` (and so H6's `risk_date_spread` and
   `spread_mr_variants.is_risk_day`), and the day-type splits of the scoring pages.
5. **Not changed.** The calendar columns (`days_to_month_end`, `quarter_end`, `tax_date`), `SplitDeclaration.day_type` (the
   frozen scorecaster's window counts calendar days), the panel, `metadata/evaluation_splits.json`, every published record in
   `docs/runs/` and every published figure. Published records are not re-scored. New pages use the definition once it is in
   force. As §13 says, a change applies only to confirmation days logged after it.

## Which day sets change

From the calendar alone (`python3 scripts/turn_definition_day_sets_1135.py`; business days 2018-02-01 to 2025-12-31, no panel
and no score read, nothing after 2025-12-31; January 2018 is refused because its turn needs December 2017, outside the holiday
table):

| legacy type | type under this record | days |
|---|---|---|
| month_end | ordinary (the penultimate day) | 95 |
| month_end | turn (the last day, renamed) | 63 |
| ordinary | turn (the first day after) | 64 |
| ordinary | quarter_end_turn (the first day after a quarter's end) | 24 |
| ordinary | year_end (the first business day of January) | 7 |
| quarter_end | quarter_end_turn | 24 |
| quarter_end | year_end (31 December or its last business day) | 8 |

By regime, 95 days leave the month-end pool and 95 join a turn type: 23 in 2018-19, 12 in 2020, 36 in 2021-23, 12 in 2024
and 12 in 2025-26. The risk-date set (`NON_ORDINARY`) loses the 95 penultimate days and gains the 95 first days after the
turn, so its size is unchanged and its membership is not. Coupon settlements keep their own clause.

## What this means for B2, which needs her call

B2 pools the trailing year by day type, with no minimum sample (`scoring-protocol.md`, implementation rulings). Under this
record `year_end` has about two days a year and `quarter_end_turn` about eight, and the first `year_end` target of a panel has
no earlier year-end to pool from, so `b2_forecast` raises `ProtocolError`, as it does for any empty pool today. A minimum
sample or a fallback to a wider pool would be a rule, which is hers; this draft adds none.

## Marked questions for Eleonora

1. **Adopt as drafted, with a minimum-sample rule for B2's thin pools?** Default: adopt the definition as drafted and ask
   for a separate directive that drafts the pool fallback (for example `year_end` falls back to `quarter_end_turn`).
2. **The year-end as its own type in B2 (about two days a year), or pooled with `quarter_end_turn`?** Default: its own type,
   as ruled.
3. **Which §13 kind does this change carry?** It is a definition, not a demonstration (a) or a reproduced error (b); the
   ruling of 22 October 2026 is the authority. Default: record it as her decision, applying only to days logged after it.

## Putting it in force

The pull request that moves this file to `docs/decisions/month-end-turn.md` also sets `turn_days.IN_FORCE = True`
(`tests/test_month_end_turn_1135.py` fails if the record and the switch disagree) and carries her `GO #1135` in
`metadata/owner_attestations.json`. Scripts that hard-code the legacy vocabulary (`month_end`, `quarter_end`; for example
`risk_date_spread.RISK_TYPES` and the study scripts that count by it) are read on the new types by new studies; none of them
re-scores a published record.
