"""(s3c-t): (s3c) with the cap off on turn days (#1265; H5 step 3, her ruling of 27 October 2026 on #1261 and #1264).

At full allotment (s3c) clips every quantile at the Standing Repo Facility line, so P(SOFR - IORB > +10 bp) read as 1 - F(10.5) is at most
about 1% and exactly 0 when the upper quantiles sit on the line. SOFR closed above the line on turn days (26, 29 and 31 December 2025;
#1252). (s3c-t) is (s3c) with the cap off on a turn day: on a target day whose reporting type is `year_end`, `quarter_end_turn` or `turn`
(`turn_days.TURN_LABELS`, the day types in force) the quantiles are (s3)'s, unclipped; on every other day it is (s3c), cap and all.

The type is a function of the target date and the market holiday table, like the calendar columns, so it is known at the decision instant
and no outcome is read. The caller passes the type of the target day (`turn_days.reporting_day_type`). A label that is not one of
`turn_days.LABELS` (the legacy `month_end` and `quarter_end` among them) raises `ValueError`: it is never read as "not a turn". The cap, the
line and the full-allotment flag are (s3c)'s (`repo_model.s3c_candidate`) and are not touched. It fits nothing. Stdlib only.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Sequence

from . import turn_days
from .policy_events import PolicyEntry
from .s3c_candidate import MARGIN_BP, capped_quantiles as s3c_capped_quantiles

__all__ = ["MARGIN_BP", "TURN_LABELS", "capped_quantiles", "is_turn"]

#: The reporting types that are turn days.
TURN_LABELS = turn_days.TURN_LABELS


def is_turn(day_type: str) -> bool:
    """Whether a reporting day type is a turn day.

    Raises:
        ValueError: `day_type` is not one of `turn_days.LABELS`.
    """

    if day_type not in turn_days.LABELS:
        raise ValueError(f"day type {day_type!r} is not one of the labels in force {turn_days.LABELS}: a turn day cannot be read")
    return day_type in turn_days.TURN_LABELS


def capped_quantiles(
    quantiles: Sequence[float], register: Sequence[PolicyEntry], as_of: datetime, target: date, day_type: str
) -> List[float]:
    """(s3)'s quantiles for `target` as (s3c-t) forecasts them: (s3c)'s on a day that is not a turn, a copy of (s3)'s on a turn day."""

    if is_turn(day_type):
        return [float(q) for q in quantiles]
    return s3c_capped_quantiles(quantiles, register, as_of, target)
