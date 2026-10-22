"""15 October as a declared alternative tax date, and its control (#965; H5 step 2, H6 step 1).

`metadata/tax_date_october_965.json` is the declaration; this module is its arithmetic. A label is a function of the date
and the market holiday table (`data.market_holidays`) alone, like `data.quarter_end`: no source, publication time or
revision is read, so nothing here can look ahead.

- `october_window`: the 15th of October rolled forward off weekends and District of Columbia holidays (the rule of
  `data.corporate_tax_deadline`, 26 U.S.C. 7503) and the two market days after it (the count of
  `data.tax_date_market_days`). Columbus Day falls on 8-14 October, so the DC rule and the market rule roll the 15th alike.
- `control_window`: the control for the coupon effect. The 15th of the months the published column and the alternative
  leave alone (`CONTROL_MONTHS`), rolled and counted on the market calendar, the same shape as the October window.
- `AlternativeLabels`: a drop-in for `SplitDeclaration.reporting_day_type` that returns `tax_date` for a day of the chosen
  window that the declared types call `ordinary`. The published types keep their precedence and the published column is not
  changed.

- `add_columns` (#1095, finding #1004): the `tax_date_october` scratch-panel column, `october_tax_date` on each row's own date. A function of
  the date and the table alone, written about the target day, so it is declared in `target_day_columns` (`asof` rule 2 serves it from the
  scored row; a one-step fit on it is refused by `one_step_guard`). It is off in every published declaration.

Not the published column: `data.tax_date` is, until a publish pull request rebuilds the panel. Stdlib only.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List, Mapping, Optional, Sequence

from . import data
from .data import DailyObservation

__all__ = [
    "AlternativeLabels",
    "COLUMN",
    "CONTROL_MONTHS",
    "WINDOW_MARKET_DAYS",
    "add_columns",
    "control_deadline",
    "control_window",
    "extra_risk_flag",
    "october_deadline",
    "october_tax_date",
    "october_window",
]

#: The scratch-panel column of `add_columns` (#1095): 1.0 in the October window, 0.0 on every other day.
COLUMN = "tax_date_october"

#: The months whose 15th is the control: the ones neither `data.TAX_DEADLINE_MONTHS` nor October holds.
CONTROL_MONTHS = tuple(m for m in range(1, 13) if m not in data.TAX_DEADLINE_MONTHS + (10,))
#: The deadline and this many market days after it are in the window.
WINDOW_MARKET_DAYS = data.TAX_WINDOW_BUSINESS_DAYS


def _forward(start: date, ok) -> date:
    day = start
    while not ok(day):
        day += timedelta(days=1)
    return day


def _window_after(deadline: date) -> tuple:
    out = [deadline]
    current = deadline
    while len(out) <= WINDOW_MARKET_DAYS:
        current += timedelta(days=1)
        if data._is_market_business_day(current):
            out.append(current)
    return tuple(out)


def october_deadline(year: int) -> date:
    """15 October, rolled forward off weekends and DC holidays.

    Raises:
        ValueError: if the market holiday table does not cover the window.
    """

    deadline = _forward(date(year, 10, 15), data._is_tax_business_day)
    data._is_market_business_day(deadline)  # refuses a year the table does not cover
    return deadline


def october_window(day: date) -> bool:
    """Whether `day` is the October deadline or one of the two market days after it.

    Raises:
        ValueError: if `day` is in October and the market holiday table does not cover the window.
    """

    if day.month != 10:
        return False
    return day in _window_after(october_deadline(day.year))


def october_tax_date(day: date) -> float:
    """1.0 in the October window, else 0.0: the added part of the alternative `tax_date`."""

    return float(october_window(day))


def control_deadline(year: int, month: int) -> date:
    """The 15th of a control month rolled forward to a market business day.

    Raises:
        ValueError: if `month` is not a control month, or the table does not cover the day.
    """

    if month not in CONTROL_MONTHS:
        raise ValueError(f"month {month} is not a control month {CONTROL_MONTHS}")
    return _forward(date(year, month, 15), data._is_market_business_day)


def control_window(day: date) -> bool:
    """Whether `day` is a control deadline or one of the two market days after it.

    Raises:
        ValueError: if `day` is in a control month and the market holiday table does not cover the window.
    """

    if day.month not in CONTROL_MONTHS:
        return False
    return day in _window_after(control_deadline(day.year, day.month))


_WINDOWS = {"october": october_window, "control": control_window}


def extra_risk_flag(day: date, which: str) -> bool:
    """Whether the chosen alternative adds `day` to a calendar of scheduled risk dates."""

    try:
        return _WINDOWS[which](day)
    except KeyError:
        raise ValueError(f"unknown alternative {which!r}; expected one of {sorted(_WINDOWS)}") from None


class AlternativeLabels:
    """The `reporting_day_type` of a `SplitDeclaration`, with the chosen window added to the `tax_date` type.

    `base` is the declared `SplitDeclaration`; a day it calls `quarter_end`, `month_end` or `tax_date` keeps that type and
    a day it calls `ordinary` becomes `tax_date` inside the window.
    """

    def __init__(self, base, *, which: str):
        if which not in _WINDOWS:
            raise ValueError(f"unknown alternative {which!r}; expected one of {sorted(_WINDOWS)}")
        self._base = base
        self.which = which

    def reporting_day_type(self, when: date, values: Mapping[str, Optional[float]]) -> str:
        kind = self._base.reporting_day_type(when, values)
        if kind == "ordinary" and _WINDOWS[self.which](when):
            return "tax_date"
        return kind


def add_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with the `tax_date_october` column, each from its own row's date and no other.

    The column is written about the row's day, so a forecast of that day reads it from its row (`asof` rule 2, `target_day_columns`). Every other
    value of every row is the frame's own, and a row that already carries the column is refused rather than overwritten.

    Raises:
        ValueError: a row already has the column, or a row in October is outside the market holiday table.
    """

    out = []
    for row in rows:
        if COLUMN in row.values:
            raise ValueError(f"{row.date} already carries {COLUMN!r}; the column is written once")
        out.append(DailyObservation(date=row.date, values={**row.values, COLUMN: october_tax_date(row.date)}))
    return out
