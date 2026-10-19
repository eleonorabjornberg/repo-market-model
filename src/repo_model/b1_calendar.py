"""B1', the calendar-aware persistence of #960 (H5 step 5, H1 step 3; development tier).

A reference row, not a benchmark of the protocol: B1 stays as ruled (`docs/decisions/scoring-protocol.md`, section 4),
and whether B1' replaces it is a section-13 decision that is Eleonora's. B1' has no parameter beyond B1's own window and
the pool floor of the context-pooled variants (`spread_mr_variants.POOL_MIN`). It is declared in
`metadata/b1_calendar_960.json`.

- **The anchor** is the spread of the last *ordinary* day at or before the as-of anchor (the last public row), where
  ordinary is `SplitDeclaration.reporting_day_type == "ordinary"`, so the day after a month-end or a tax date no longer
  anchors on the spike.
- **The changes** are, for every row `e` in the trailing two years up to the anchor, `spread[e] - last_ordinary[e - h]`,
  the change from the last ordinary spread at or before `e - h`. They are pooled by the reporting day type of the
  *target* day, a type known in advance from the calendar, and a pool of fewer than `POOL_MIN` changes falls back to the
  changes of every type.
- The forecast at lead h is the anchor plus the 23 empirical quantiles of the pooled changes.

Every row read is at or before the anchor, and `protocol_benchmarks._require_public` restates it for the rows read. Stdlib
only.
"""

from __future__ import annotations

from datetime import time
from typing import Dict, List, Mapping, Optional, Sequence

from . import protocol_benchmarks as pb
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import HORIZONS, ProtocolError
from .spread_mr_variants import POOL_MIN


def last_ordinary_rows(panel: Sequence[DailyObservation], splits: SplitDeclaration, upto: int) -> List[Optional[int]]:
    """For each row `s` up to `upto`, the index of the last ordinary row at or before `s`, or None before the first one."""

    out: List[Optional[int]] = []
    latest: Optional[int] = None
    for s in range(upto + 1):
        if splits.reporting_day_type(panel[s].date, panel[s].values) == "ordinary":
            latest = s
        out.append(latest)
    return out


def b1_calendar_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> Dict[int, List[float]]:
    """B1' for the decision on row `decision_index`: the 23 quantiles at each lead h = 1..5.

    Raises:
        ProtocolError: no ordinary day at or before the anchor, or a lead with no change in the window.
        LookAheadError: a row read after the anchor (`protocol_benchmarks._require_public`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    dates = [row.date for row in panel]
    ordinary = last_ordinary_rows(panel, splits, anchor)
    if ordinary[anchor] is None:
        raise ProtocolError(f"no ordinary day at or before {dates[anchor]}")
    centre = panel[ordinary[anchor]].spread_bps
    first = pb._window_start(panel, decision_index, pb.B1_YEARS)

    def kind_of(s: int) -> str:
        return splits.reporting_day_type(panel[s].date, panel[s].values)

    out = {}
    for h in HORIZONS:
        kind = kind_of(decision_index + h)
        ends = [s for s in range(max(first, h), anchor + 1) if ordinary[s - h] is not None]
        if not ends:
            raise ProtocolError(f"B1' has no {h}-day change before {dates[anchor]}")
        same = [s for s in ends if kind_of(s) == kind]
        rows = same if len(same) >= POOL_MIN else ends
        pb._require_public(rows + [ordinary[s - h] for s in rows], anchor, dates,
                           f"B1' for {dates[decision_index]}, lead {h}")
        changes = sorted(panel[s].spread_bps - panel[ordinary[s - h]].spread_bps for s in rows)
        out[h] = pb.empirical_quantiles(changes, centre)
    return out
