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

TURN = "turn"
QUARTER_END_TURN = "quarter_end_turn"
YEAR_END = "year_end"
TAX_DATE = "tax_date"
ORDINARY = "ordinary"
#: The labels, in precedence order.
LABELS: Tuple[str, ...] = (YEAR_END, QUARTER_END_TURN, TURN, TAX_DATE, ORDINARY)
#: The labels that are turn days.
TURN_LABELS = frozenset({TURN, QUARTER_END_TURN, YEAR_END})


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
