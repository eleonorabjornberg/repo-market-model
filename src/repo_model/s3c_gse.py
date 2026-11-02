"""(s3c-gse): (s3c) with the GSE cash cycle as a ramp from the 19th to the 25th in place of the flat 19th-23rd term (#1274; H5 step 3).

Eleonora, 27 October 2026 (chat, relayed; ledger item 66 on #1116): queue four arms on (s3c), one directive each, independent of each other.
This is the second: (s3) has one flat 0/1 term for the 19th to the 23rd of the month (`dom_19_23`). The cash cycle of the housing
agencies (Fannie Mae and Freddie Mac) runs longer: their cash comes into the market around the 19th and leaves around the 25th, and its effect
may build through those days rather than stay flat.

**The term.** `ramp(day)` is 0 before the 19th and after the 25th of the month, and `(d - 18) / 7` on day `d` from 19 to 25, a function of the
calendar date alone: 1/7 on the 19th, 4/7 on the 22nd, 1 on the 25th. The shape is declared before any score and is not tuned. Where the 25th or
the days before it fall on a weekend or a holiday there is no panel row for them and the term is read on the business days that remain; the
value of a row is the value of its own date, not renumbered.

**Where it sits.** `GseTermTable` is `spread_mr_calendar.TermTable` with one column replaced: the slot of `dom_19_23` holds the ramp, at every
lead, and every other term is the base class's, untouched. (s3) is the arm `spread_mr_state_calendar.ARMS[2]` on this table: its terms, its
Huber fit, its ridge of 5 and its direct pairs are unchanged, so the only difference from (s3) is the one column. The column is read from the
target row's own date (`TermTable.read` takes the row `decision_index + lead`), exactly as the flag it replaces, and it needs no input but the
date, so `asof` rule 2 and the one-step guard hold as they do for `dom_19_23`: `fit_state_terms` is decorated with
`one_step_guard.guard_one_step_fit`, which refuses a one-step fit of the arm's calendar columns, and no allow-list entry is added.

**Count of a term.** A term enters a lead's fit when `MIN_FLAGGED` training pairs carry it; for a 0/1 flag that is a count of days, for the ramp
the base class counts the sum of the values (the 19th to the 25th of a month add 4 to it). Both pass that minimum after the first month of
history, far before the first refit, so the entry of the term is the same; the page states the sums it reports as sums of ramp values.

(s3c-gse) is the quantiles of that walk clipped at the line where `repo_model.s3c_candidate` clips them; the cap is not touched here.
Stdlib only.
"""

from __future__ import annotations

from datetime import date, time
from typing import Optional, Sequence

from .decision_instant import DECISION_TIME
from . import announced_iorb, fomc_calendar
from . import spread_mr_calendar as cal
from .data import DailyObservation
from .scoring_protocol import HORIZONS

__all__ = ["FIRST_DAY", "LAST_DAY", "REPLACED_TERM", "GseTermTable", "ramp"]

#: The first and the last day of the month on which the ramp is non-zero. The shape is declared, not tuned.
FIRST_DAY = 19
LAST_DAY = 25
#: The term the ramp replaces: its slot in `spread_mr_calendar.TERMS`, and so in the arms' `location` and in `StateEstimate.effect`.
REPLACED_TERM = "dom_19_23"
_STEPS = LAST_DAY - FIRST_DAY + 1


def ramp(day: date) -> float:
    """The GSE cash-cycle ramp of the calendar date `day`: 0 before the 19th and after the 25th, `(d - 18) / 7` from the 19th to the 25th.

    Mutation record: see `tests/test_s3c_gse.py` (`ramp`).
    """

    d = day.day
    if d < FIRST_DAY or d > LAST_DAY:
        return 0.0
    return (d - (FIRST_DAY - 1)) / _STEPS


class GseTermTable(cal.TermTable):
    """`spread_mr_calendar.TermTable` with the ramp in the slot of `dom_19_23`; every other term is the base class's.

    The value at a row is `ramp` of that row's own date, the same at every lead (a function of the date is known whenever it is read), and
    it is served from the target row: `TermTable.read` and `flags_at` index the row they are given, the target row.
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
        column = [ramp(day) for day in self.dates]
        for lead in HORIZONS:
            self._flags[(REPLACED_TERM, lead)] = list(column)
