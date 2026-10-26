"""The day type of a decision day's anchor, the split of #741 (H1 step 3, read by the H5 result pages).

B1 (scoring protocol v1, §4) centres every lead on the anchor, the last public row. When the anchor is a
quarter-end, tax-date or month-end spike, B1 carries it forward. A result against B1 is therefore also
reported by the type of the anchor, beside the pooled figure. The type is `SplitDeclaration.reporting_day_type`
of the anchor row, read from that row's own calendar columns; the anchor is `protocol_benchmarks`' own, found
under both guards of the decision-instant rule. This module changes no benchmark and no rule.

Stdlib only.
"""

from __future__ import annotations

from datetime import date, time
from typing import Dict, Iterable, Mapping, Sequence

from . import turn_days
from . import protocol_benchmarks as pb
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration


def anchor_day_type(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> str:
    """The reporting day type of the anchor of the decision on row `decision_index`."""

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    row = panel[anchor]
    return turn_days.reporting_day_type(splits, row.date, row.values)


def anchor_day_types(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    **settings,
) -> Dict[date, str]:
    """`anchor_day_type` for each of `decision_days`, keyed by decision day.

    Raises:
        ValueError: a decision day that is not a panel day.
    """

    position = {row.date: index for index, row in enumerate(panel)}
    out = {}
    for day in decision_days:
        if day not in position:
            raise ValueError(f"decision day {day} is not a panel day")
        out[day] = anchor_day_type(panel, position[day], **settings)
    return out
