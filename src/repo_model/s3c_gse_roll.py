"""(s3c-gse-roll): the GSE ramp with the payment-day roll when the 25th is not a business day (#1287; H5 step 3, development tier).

Eleonora, 28 October 2026 (chat, relayed; ledger item 70 on #1116; finding #1285): test the GSE-cycle ramp of (s3c-gse) (#1274) with the payment
day rolled. The agencies pay on the 25th, or on the next business day when the 25th is not one. In (s3c-gse) the ramp is tied to the calendar 25th,
so in the months where the 25th is a weekend or a holiday (37 of 98 months) the payment day reads 0 and the ramp peaks on the day before.

**The term.** `roll_ramp(day)` is `s3c_gse.ramp(day)` with one change: the value of the 25th (7/7, i.e. 1) is read on the *payment day*, the first
business day on or after the 25th (`data.market_holidays()` and weekends), and the 25th itself reads nothing when it is not a business day (it has no
panel row). The other days keep their own date's value: `(d - 18) / 7` from the 19th to the 24th, 0 before the 19th, 0 after the payment day. When
the 25th is a business day the payment day is the 25th and the term is (s3c-gse)'s. The rule is declared before any score and is not tuned. It is
a function of the calendar date and the holiday table alone (both public in advance), read from the target row's own date.

**Where it sits.** `RollTermTable` is `spread_mr_calendar.TermTable` with the slot of `dom_19_23` holding `roll_ramp` at every lead, as
`s3c_gse.GseTermTable` holds `ramp`; the arm (s3) and the direct pairs are unchanged, so `asof` rule 2 and the one-step guard hold as they do for
`dom_19_23` and no allow-list entry is added. Stdlib only.
"""

from __future__ import annotations

from datetime import date, time, timedelta
from typing import List, Optional, Sequence

from .decision_instant import DECISION_TIME
from . import announced_iorb, data, fomc_calendar
from . import spread_mr_calendar as cal
from .data import DailyObservation
from .s3c_gse import FIRST_DAY, LAST_DAY, REPLACED_TERM, ramp
from .scoring_protocol import HORIZONS

__all__ = ["FIRST_DAY", "LAST_DAY", "REPLACED_TERM", "RollTermTable", "moved_days", "payment_day", "roll_ramp"]


def payment_day(year: int, month: int) -> date:
    """The day the agencies pay for `year`-`month`: the 25th, or the next business day when the 25th is a weekend or in the market holiday table.

    Raises:
        ValueError: the market holiday table does not cover the day (`data.next_business_day`).

    Mutation record: see `tests/test_s3c_gse_roll.py` (`payment_day`).
    """

    return data.next_business_day(date(year, month, LAST_DAY) - timedelta(days=1), 1)


def roll_ramp(day: date) -> float:
    """The ramp of the calendar date `day` with the payment-day roll: `ramp(day)`, except that the payment day reads the 25th's value and the
    25th, when it is not the payment day, reads 0."""

    if day == payment_day(day.year, day.month):
        return ramp(date(day.year, day.month, LAST_DAY))
    if day.day == LAST_DAY:
        return 0.0
    return ramp(day) if day.day < LAST_DAY else 0.0


def moved_days(dates: Sequence[date]) -> List[date]:
    """The days among `dates` on which the roll changes the term: the payment days of the months whose 25th is not a business day."""

    return [d for d in dates if roll_ramp(d) != ramp(d)]


class RollTermTable(cal.TermTable):
    """`spread_mr_calendar.TermTable` with `roll_ramp` in the slot of `dom_19_23`; every other term is the base class's.

    The value at a row is `roll_ramp` of that row's own date, the same at every lead, served from the target row as `TermTable.read` serves
    every calendar column.
    """

    def __init__(
        self,
        panel: Sequence[DailyObservation],
        announcements: Sequence[announced_iorb.IorbAnnouncement],
        calendar: Optional[Sequence[fomc_calendar.Meeting]] = None,
        *,
        decision_time: time = DECISION_TIME,
    ):
        super().__init__(panel, announcements, calendar, decision_time=decision_time)
        column = [roll_ramp(day) for day in self.dates]
        for lead in HORIZONS:
            self._flags[(REPLACED_TERM, lead)] = list(column)
