"""Derived features, interactions' inputs and lagged pressure, built from panel rows without a look-ahead (#631).

A measurement module, not a published declaration: every column here is **off** in every published declaration. Each column on
a row is a function of the panel rows up to and including that row and of nothing else. A reader sees the series only through
`Causal`, a view that refuses (`LookAheadError`) any index after its own row, so a reader cannot read a later row by mistake;
`check_columns_causal` rebuilds a column on the panel cut at a row and refuses a column that differs. Whether the value on a
row is *public* at a decision instant is the as-of rule's: the column is declared on the source fields of the series it reads
(`COLUMN_FIELDS` is built by the script from the constituents), so a read at a decision instant takes the latest row on which
every one of those fields was public. A pressure outcome enters a column only on the row whose spread it is, hence only once
that spread is public.

Calendar features (`dow`, `bday_of_month`, `maint_period_day`) are functions of the date and the market holiday table. They are
known in advance, and are declared in `contract.CALENDAR_FEATURES` for a run.

The definitions are in `metadata/derived_features_631.json`, committed before any number was computed. Standard library only.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Callable, Dict, List, Mapping, Optional, Sequence

from .data import DailyObservation, exceeds_bp, market_holidays
from .splits import LookAheadError

__all__ = [
    "Causal",
    "MAINTENANCE_ANCHOR",
    "above_median_run",
    "change",
    "bday_of_month",
    "build_columns",
    "check_columns_causal",
    "days_since_pressure",
    "lagged",
    "maint_period_day",
    "range_stats",
    "realised_vol",
]

#: The first day of a reserve maintenance period: Thursday 2019-04-25, which began the period 2019-04-25 to 2019-05-08
#: (Federal Reserve Bank of Philadelphia, weekly maintenance calendar). Periods run 14 days, Thursday to Wednesday.
MAINTENANCE_ANCHOR = date(2019, 4, 25)
MAINTENANCE_LENGTH = 14


class Causal:
    """A series seen from row `end`: indices up to and including `end` only."""

    def __init__(self, values: Sequence[Optional[float]], end: int) -> None:
        if end < 0 or end >= len(values):
            raise ValueError(f"row {end} is outside the series of {len(values)}")
        self._values = values
        self.end = end

    def __getitem__(self, index: int) -> Optional[float]:
        if index > self.end:
            raise LookAheadError(
                f"a derived feature on row {self.end} read row {index}, which is later: the feature would use what was not public"
            )
        if index < 0:
            raise ValueError("an index before the first row is not a row")
        return self._values[index]

    def last(self, count: int) -> Optional[List[float]]:
        """The last `count` values ending at `end`, or `None` if fewer rows exist or any value is missing."""

        start = self.end - count + 1
        if start < 0:
            return None
        window = [self[i] for i in range(start, self.end + 1)]
        if any(v is None for v in window):
            return None
        return window  # type: ignore[return-value]


def realised_vol(view: Causal, days: int) -> Optional[float]:
    """The sample standard deviation of the last `days` one-day changes of the series."""

    window = view.last(days + 1)
    if window is None:
        return None
    changes = [b - a for a, b in zip(window, window[1:])]
    mean = sum(changes) / len(changes)
    return math.sqrt(sum((c - mean) ** 2 for c in changes) / (len(changes) - 1))


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0


def above_median_run(view: Causal, window: int, minimum: int) -> Optional[float]:
    """How many consecutive rows, ending at this one, have the series strictly above the median of its last `window` values.

    The median is taken once, at this row, over the last `window` values that exist (at least `minimum`, else `None`);
    a row on which the series is not above it has a run of 0.
    """

    start = max(0, view.end - window + 1)
    recent = [view[i] for i in range(start, view.end + 1)]
    if any(v is None for v in recent) or len(recent) < minimum:
        return None
    cut = _median(recent)  # type: ignore[arg-type]
    run = 0
    for i in range(view.end, start - 1, -1):
        if view[i] > cut:  # type: ignore[operator]
            run += 1
        else:
            break
    return float(run)


def days_since_pressure(view: Causal, threshold_bp: float) -> Optional[float]:
    """Panel rows from this row back to the latest row, at or before it, whose spread is strictly above `threshold_bp`.

    0 when this row's spread is itself a pressure day. `None` until a pressure day has been seen, and when this row's spread is
    missing. A pressure outcome counts only from its own row on, the row on which its spread is public.
    """

    if view[view.end] is None:
        return None
    for i in range(view.end, -1, -1):
        value = view[i]
        if value is not None and exceeds_bp(value, threshold_bp):
            return float(view.end - i)
    return None


def lagged(view: Causal, lag: int) -> Optional[float]:
    """The value `lag` rows before this one."""

    if lag < 0:
        raise ValueError("a lag is not negative")
    index = view.end - lag
    return None if index < 0 else view[index]


def change(view: Causal, days: int) -> Optional[float]:
    """The value less its value `days` rows earlier."""

    now, before = lagged(view, 0), lagged(view, days)
    return None if now is None or before is None else now - before


def range_stats(view: Causal, window: int, scale: float = 1.0) -> Optional[Dict[str, float]]:
    """The series against its own trailing `window` values, this row's included.

    `min_dist` is the value less the window's minimum, `max_dist` the window's maximum less the value (both times `scale`,
    100 to turn a rate in percent into basis points), `z` the value less the window's mean over its sample standard deviation (`None` for a constant window).
    """

    values = view.last(window)
    if values is None:
        return None
    now = values[-1]
    mean = sum(values) / window
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / (window - 1))
    return {
        "min_dist": (now - min(values)) * scale,
        "max_dist": (max(values) - now) * scale,
        "z": (now - mean) / sd if sd > 0.0 else None,  # type: ignore[dict-item]
    }


# -- the calendar -------------------------------------------------------------------------------------------


def bday_of_month(day: date) -> float:
    """The market day of the month: 1 for the first weekday that is not in the market holiday table."""

    closed = market_holidays().closed
    count = 0
    current = day.replace(day=1)
    while current <= day:
        if current.weekday() < 5 and current not in closed:
            count += 1
        current += timedelta(days=1)
    return float(count)


def maint_period_day(day: date) -> float:
    """The calendar day within the 14-day Thursday-to-Wednesday maintenance period: 0 on the Thursday, 13 on the Wednesday."""

    return float((day - MAINTENANCE_ANCHOR).days % MAINTENANCE_LENGTH)


# -- the columns --------------------------------------------------------------------------------------------

#: Column readers: name -> (input column, reader of one `Causal` view). Built by `columns_for`.
Reader = Callable[[Causal], Optional[float]]


def columns_for(
    *,
    rates: Sequence[str],
    windows: Sequence[int],
    median_window: int,
    median_minimum: int,
    vol_days: Sequence[int],
    lags: Sequence[int],
    threshold_bp: float,
    bp_scale: float = 100.0,
    changes: Mapping[str, "tuple[str, int]"] = {},
) -> Dict[str, "tuple[str, Reader]"]:
    """Every causal column: name -> (the panel column it reads, its reader)."""

    out: Dict[str, "tuple[str, Reader]"] = {}
    for k in vol_days:
        out[f"spread_rv{k}"] = ("spread_bps", lambda v, k=k: realised_vol(v, k))
    out["above_median_run"] = ("spread_bps", lambda v: above_median_run(v, median_window, median_minimum))
    out["days_since_pressure"] = ("spread_bps", lambda v: days_since_pressure(v, threshold_bp))
    for rate in rates:
        for w in windows:
            for stat in ("min_dist", "max_dist", "z"):
                out[f"{rate}_{stat}_{w}"] = (
                    rate,
                    lambda v, w=w, stat=stat: (lambda r: None if r is None else r[stat])(range_stats(v, w, bp_scale)),
                )
    for name, (source, days) in changes.items():
        out[name] = (source, lambda v, days=days: change(v, days))
    out["pressure_last"] = (
        "spread_bps",
        lambda v: None if v[v.end] is None else float(exceeds_bp(v[v.end], threshold_bp)),
    )
    for k in lags:
        out[f"pressure_lag{k}"] = (
            "spread_bps",
            lambda v, k=k: (lambda x: None if x is None else float(exceeds_bp(x, threshold_bp)))(lagged(v, k)),
        )
        out[f"spread_lag{k}"] = ("spread_bps", lambda v, k=k: lagged(v, k))
    return out


def build_columns(
    rows: Sequence[DailyObservation],
    spec: Mapping[str, "tuple[str, Reader]"],
) -> Dict[str, List[Optional[float]]]:
    """Each column of `spec` on each row, from the rows up to and including it."""

    sources = sorted({source for source, _reader in spec.values()})
    series: Dict[str, List[Optional[float]]] = {}
    for source in sources:
        if source == "spread_bps":
            series[source] = [row.spread_bps for row in rows]
        else:
            series[source] = [row.values.get(source) for row in rows]
    out: Dict[str, List[Optional[float]]] = {name: [] for name in spec}
    for i in range(len(rows)):
        views = {source: Causal(values, i) for source, values in series.items()}
        for name, (source, reader) in spec.items():
            value = reader(views[source])
            out[name].append(value)
    return out


def check_columns_causal(
    rows: Sequence[DailyObservation],
    spec: Mapping[str, "tuple[str, Reader]"],
    built: Mapping[str, Sequence[Optional[float]]],
    *,
    indices: Sequence[int],
) -> None:
    """Refuse a built column that is not what the panel cut at its own row gives.

    Raises:
        LookAheadError: a checked row's value differs from the same row rebuilt from the rows up to and including it, so the
            column depended on a later row.
    """

    for i in indices:
        again = build_columns(rows[: i + 1], spec)
        for name in spec:
            have, want = built[name][i], again[name][i]
            if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):
                raise LookAheadError(
                    f"{name} on {rows[i].date.isoformat()} is {have}, but the panel cut at that row gives {want}; "
                    "the column depended on a later row"
                )
