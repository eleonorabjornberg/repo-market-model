"""The turn-day labels of #959 (H5 step 2): the month and quarter turns, and the year-end, as functions of the date.

`metadata/turn_day_labels_959.json` is the declaration; this module is its arithmetic. A label is a function of the date
and the market holiday table (`data.market_holidays`) alone, like `data.quarter_end`: no source, publication time or
revision is read, so nothing here can look ahead. A business day is a weekday not in the table.

- `turn`: the last business day of a month and the first business day of the next, in a month that is not a quarter's
  last (the month's penultimate and run-up days are *not* turn days).
- `quarter_end_turn`: the last business day of March, June or September and the first business day after it.
- `year_end`: the last business day of December and the first business day of January.
- `tax_date`: as the calendar column reads it, on a day that is none of the above.
- `ordinary`: every other day. 26 December is `december_26`, its own flag; the labels pool it as ordinary.

`TurnLabels` is a drop-in for the `reporting_day_type` of `evaluation_splits.SplitDeclaration`, so the unchanged B2
(`protocol_benchmarks.b2_forecast`) and the mean-reversion level (`spread_mean_reversion.ordinary_levels`) can be read on
it. Stdlib only.
"""

from __future__ import annotations

from datetime import date
from typing import Mapping, Optional, Tuple

from . import data
from .evaluation_splits import SplitDeclaration

#: Whether the month-end turn record (#1135) is in force. It is a draft, `docs/decisions/drafts/month-end-turn.md`, until
#: Eleonora merges it into `docs/decisions/month-end-turn.md`; the PR that moves it there flips this to `True`
#: (`tests/test_month_end_turn_1135.py` fails if the two disagree). While `False`, `SplitDeclaration.reporting_day_type`
#: (B2's pools, the mean-reversion level, the day-type splits, `risk_dates`) is exactly what it was.
IN_FORCE = False

TURN = "turn"
QUARTER_END_TURN = "quarter_end_turn"
YEAR_END = "year_end"
TAX_DATE = "tax_date"
ORDINARY = "ordinary"
#: The labels, in precedence order.
LABELS: Tuple[str, ...] = (YEAR_END, QUARTER_END_TURN, TURN, TAX_DATE, ORDINARY)
#: The labels that are turn days.
TURN_LABELS = frozenset({TURN, QUARTER_END_TURN, YEAR_END})


def in_force() -> bool:
    """Whether `reporting_day_type` reads the turn labels (the record of #1135 is merged)."""

    return IN_FORCE


def reporting_day_type(splits, when: date, values: Mapping[str, Optional[float]]) -> str:
    """The pressure-day type a result is reported by and B2 pools by: the one definition of #1135.

    While `IN_FORCE` is `False` this is `splits.reporting_day_type(when, values)` exactly. Once the record is in force it is
    `turn_day_type` on the day's date and its `tax_date` column, for a `SplitDeclaration` (which still checks the row's calendar
    columns, so a hole is a `ValueError`). Any other object with a `reporting_day_type` (`TurnLabels`, `tax_date_october`'s
    labels) keeps its own reading. `evaluation_splits.SplitDeclaration` is part of the frozen live declaration
    (`scripts/live_score.py`, `LIVE_SOURCE`) and is not edited: every reader calls this function instead.

    Raises:
        ValueError: as `SplitDeclaration.reporting_day_type`, and if the market holiday table does not cover the day.
    """

    if IN_FORCE and isinstance(splits, SplitDeclaration):
        splits.day_type(values)
        return turn_day_type(when, tax_date=float(values["tax_date"]) == 1.0)
    return splits.reporting_day_type(when, values)


def turn_days_of_month(year: int, month: int) -> Tuple[date, date]:
    """The month's last business day and the first business day after it, which falls in the next month.

    Raises:
        ValueError: if the market holiday table does not cover the month or the day after it.
    """

    last = data.last_business_days_of_month(year, month, count=1)[0]
    return last, data.next_business_day(last, 1)


def _month_label(month: int) -> str:
    if month == 12:
        return YEAR_END
    return QUARTER_END_TURN if month % 3 == 0 else TURN


def turn_label(day: date) -> Optional[str]:
    """`turn`, `quarter_end_turn` or `year_end` when `day` is a turn day, else `None`.

    Raises:
        ValueError: if the market holiday table does not cover the day's month and the month before.
    """

    previous = (day.year, day.month - 1) if day.month > 1 else (day.year - 1, 12)
    for year, month in (previous, (day.year, day.month)):
        if day in turn_days_of_month(year, month):
            return _month_label(month)
    return None


def turn_day_type(day: date, *, tax_date: bool) -> str:
    """The label of `day`; `tax_date` is the day's calendar column (`tax_date == 1.0`).

    Raises:
        ValueError: as `turn_label`.
    """

    label = turn_label(day)
    if label is not None:
        return label
    return TAX_DATE if tax_date else ORDINARY


def december_26(day: date) -> bool:
    """26 December, the day Lens A found prints apart from the year-end turn."""

    return day.month == 12 and day.day == 26


def penultimate_day(day: date) -> bool:
    """The month's second-last business day: the day the repo's month-end label has counted and the turn label does not.

    Raises:
        ValueError: if the market holiday table does not cover the month.
    """

    return day == data.last_business_days_of_month(day.year, day.month, count=2)[0]


class TurnLabels:
    """The `reporting_day_type` of a `SplitDeclaration`, with the turn labels in place of month-end.

    `base` is the declared `SplitDeclaration`; its `day_type` still reads the calendar columns, so a hole in one is a
    `ValueError` as it is there. `keep_tax_date=False` returns tax dates to `ordinary`, which reads the mean-reversion
    level's set as excluding only turn days.
    """

    def __init__(self, base, *, keep_tax_date: bool = True):
        self._base = base
        self._keep_tax_date = keep_tax_date

    def reporting_day_type(self, when: date, values: Mapping[str, Optional[float]]) -> str:
        self._base.day_type(values)
        label = turn_day_type(when, tax_date=float(values["tax_date"]) == 1.0)
        if label == TAX_DATE and not self._keep_tax_date:
            return ORDINARY
        return label





def day_set_changes(first: date, last: date, *, splits) -> dict:
    """The business days from `first` to `last` whose reporting day type the turn record changes, from the calendar alone.

    Reads no panel and no score: the legacy type is `splits.reporting_day_type` (the declared `SplitDeclaration`, unedited) on the day's own calendar columns
    (`data.CALENDAR_COLUMN_RULES`), the new one `turn_day_type`. A business day is a weekday not in the holiday table.

    Returns `relabelled` ((legacy, new) -> days), `leave_month_end` (legacy `month_end`, now `ordinary` or `tax_date`) and
    `join_turn` (legacy `ordinary` or `tax_date`, now a turn type), each day list ascending.

    Raises:
        ValueError: if the holiday table does not cover the range and the month before and after it.
    """

    from datetime import timedelta

    holidays = data.market_holidays()
    rules = data.CALENDAR_COLUMN_RULES
    relabelled: dict = {}
    day = first
    while day <= last:
        if day.weekday() < 5 and day not in holidays.closed:
            row = {name: float(rules[name](day)) for name in ("days_to_month_end", "quarter_end", "tax_date")}
            old = splits.reporting_day_type(day, row)
            new = turn_day_type(day, tax_date=row["tax_date"] == 1.0)
            if old != new:
                relabelled.setdefault((old, new), []).append(day)
        day += timedelta(days=1)
    leave = sorted(d for (old, new), days in relabelled.items() if old == "month_end" and new in (ORDINARY, TAX_DATE) for d in days)
    join = sorted(d for (old, new), days in relabelled.items() if old in (ORDINARY, TAX_DATE) and new in TURN_LABELS for d in days)
    return {"relabelled": relabelled, "leave_month_end": leave, "join_turn": join}
