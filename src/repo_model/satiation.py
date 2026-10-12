"""A time-varying satiation level for the reserve-demand terms (#587, ruling on #569).

The structural model (#542) and the projected-reserves model (#545) place reserves on a demand curve whose
kink, the satiation level, is the fixed 0.12 of the published scarcity indicator's band
(`scarcity.SATIATION_BAND`). 2025's pressure came at reserve ratios of 0.117 to 0.129, so a fixed 0.12 leaves
both models blind to it (#569). This module is the measurement of two ways to set the level from past data only.
The published indicator and its band are unchanged; nothing here is published.

**Forms** (`FORMS`; declared in `metadata/satiation_587.json` before any score):

* `fixed`: the level is `scarcity.SATIATION_BAND[0]`. The control; every model is unchanged.
* `fixed_kink`: the level is 0.12 too, but the projected model keeps its kink (a hinge, below). Separates what
  the kink's shape adds from what a moving level adds. A control, not one of the two forms.
* `rolling` (form a): the level at a decision is the `ROLLING_QUANTILE` quantile of the reserves-to-assets ratios
  that were public at each of the last `ROLLING_WINDOW` panel rows' own decisions, up to and including the
  decision's. Until `ROLLING_MINIMUM` ratios exist the level is the fixed 0.12. It is a panel column
  (`ROLLING_COLUMN`, source `SOURCE_ID`, zero lag) built from as-of reads, so a model reads it through the
  as-of rule like any input.
* `fitted` (form b): at each refit the level is the kink of a hinge regression of the spread on the ratio, fitted
  on that refit's training pairs only (`fit_level`): `spread = a + b * max(0, k - ratio)`, `b >= 0`, `k` on a
  declared grid, least squares. The refit's one level serves its training pairs and the days it forecasts.

**The kink after standardisation.** `proj_dist_h` is linear in the projected ratio, so a ridge logistic on
standardised columns cannot see where the level is. The projected model under any form but `fixed` reads
`hinge(ratio, level) = max(0, 100 * level - 100 * ratio)`, percentage points below the level, which is zero
above it and so keeps the kink in the forecast (the second half of #569).

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta  # noqa: F401
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .asof import InformationRule
from .data import DailyObservation, next_business_day
from .scarcity import SATIATION_BAND, reserves_ratio
from .splits import LookAheadError, SplitError

__all__ = [
    "COLUMN_FIELDS",
    "DISTANCE_COLUMN",
    "DISTANCE_COLUMN_FIELDS",
    "DISTANCE_SOURCE_ID",
    "HINGE_COLUMN",
    "FIXED",
    "FORMS",
    "KINK_GRID",
    "KINK_MINIMUM_PAIRS",
    "READ_FEATURES",
    "ROLLING_COLUMN",
    "ROLLING_MINIMUM",
    "ROLLING_QUANTILE",
    "ROLLING_WINDOW",
    "SOURCE_ID",
    "asof_ratios",
    "build_columns",
    "build_distance_columns",
    "check_distance_no_future",
    "check_no_future",
    "distance",
    "fit_level",
    "hinge",
    "hinge_value",
    "quantile",
    "rolling_level",
]

#: The source the as-of rule reads the column through (`metadata/sources_measurement.json`). Zero lag: each row's
#: level is built from what was public at that row's own decision.
SOURCE_ID = "satiation_columns"
#: The rolling level, a panel column. **Off** in every published declaration.
ROLLING_COLUMN = "satiation_roll"
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {ROLLING_COLUMN: ((SOURCE_ID, ROLLING_COLUMN),)}
#: The rolling distance (#598): two more panel columns built from the same as-of ratio and the same rolling level, read by
#: the risk-date passers as one extra input each. Zero lag, like `ROLLING_COLUMN`; **off** in every published declaration.
DISTANCE_SOURCE_ID = "satiation_distance_columns"
DISTANCE_COLUMN = "satiation_dist_roll"
HINGE_COLUMN = "satiation_hinge_roll"
DISTANCE_COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    DISTANCE_COLUMN: ((DISTANCE_SOURCE_ID, DISTANCE_COLUMN),),
    HINGE_COLUMN: ((DISTANCE_SOURCE_ID, HINGE_COLUMN),),
}
#: The two legs of the ratio, each read at its own latest public row (as the structural model reads them).
READ_FEATURES = ("reserve_balances", "bank_total_assets")
#: The fixed level: the lower end of the published band. Never changed here.
FIXED = SATIATION_BAND[0]
FORMS = ("fixed", "fixed_kink", "rolling", "fitted")

#: Form a. A low quantile of the as-of ratios of the last two years of panel rows (504 business days), once at
#: least a quarter (63 rows) of them exist. Chosen before any score, not tuned.
ROLLING_QUANTILE = 0.10
ROLLING_WINDOW = 504
ROLLING_MINIMUM = 63
#: Form b. The kink is searched on a grid of ratios, 0.080 to 0.200 in steps of 0.0025, and needs a year of pairs.
KINK_GRID = tuple(round(0.08 + 0.0025 * k, 4) for k in range(49))
KINK_MINIMUM_PAIRS = 250
#: Business days appended to the dates handed to the rule, so a lag at the last real row is dated the same
#: whatever follows it.
_EXTRA_DATES = 15


def hinge(ratio: float, level: float) -> float:
    """Percentage points by which `ratio` is below `level`; 0 at or above it."""

    return max(0.0, 100.0 * (float(level) - float(ratio)))


def quantile(values: Sequence[float], q: float) -> float:
    """The `q` quantile by linear interpolation between order statistics (Hyndman and Fan's type 7)."""

    if not values:
        raise ValueError("a quantile needs at least one value")
    if not 0.0 <= q <= 1.0:
        raise ValueError(f"a quantile level is in [0, 1], got {q}")
    ordered = sorted(float(v) for v in values)
    position = q * (len(ordered) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def rolling_level(
    ratios: Sequence[Optional[float]],
    i: int,
    *,
    q: float = ROLLING_QUANTILE,
    window: int = ROLLING_WINDOW,
    minimum: int = ROLLING_MINIMUM,
) -> Optional[float]:
    """The rolling level at row `i`: the `q` quantile of the as-of ratios of rows `i - window + 1 .. i`.

    `ratios[j]` is the ratio the as-of rule reads at row `j`'s own decision. Only rows up to `i` are read. The
    fixed level while fewer than `minimum` ratios exist; `None` when row `i` itself has no ratio (an unobserved
    input is never served a level).
    """

    if ratios[i] is None:
        return None
    seen = [r for r in ratios[max(0, i - window + 1): i + 1] if r is not None]
    if len(seen) < minimum:
        return FIXED
    return quantile(seen, q)


def fit_level(
    ratios: Sequence[float],
    spreads: Sequence[float],
    *,
    grid: Sequence[float] = KINK_GRID,
    minimum_pairs: int = KINK_MINIMUM_PAIRS,
) -> Tuple[float, Dict[str, object]]:
    """The fitted kink: `k` on `grid` minimising the squared error of `spread = a + b * hinge(ratio, k)`, `b >= 0`.

    Reads only the pairs handed in, which are one refit's training pairs: each ratio was public at its pair's
    own decision and each spread is the label of a day the training frame covers. With fewer than
    `minimum_pairs` pairs, or no candidate with a non-negative slope, the level is the fixed 0.12.

    Returns:
        `(level, record)`; the record says whether the level was fitted, from how many pairs, and the winner's
        slope.
    """

    if len(ratios) != len(spreads):
        raise ValueError("fit_level needs one spread per ratio")
    n = len(ratios)
    if n < minimum_pairs:
        return FIXED, {"fitted": False, "reason": "too few pairs", "pairs": n}
    y_mean = sum(spreads) / n
    best: Optional[Tuple[float, float, float]] = None
    for k in grid:
        x = [hinge(r, k) for r in ratios]
        x_mean = sum(x) / n
        sxx = sum((v - x_mean) ** 2 for v in x)
        if sxx <= 0.0:
            continue
        slope = sum((v - x_mean) * (s - y_mean) for v, s in zip(x, spreads)) / sxx
        if slope < 0.0:
            continue
        intercept = y_mean - slope * x_mean
        sse = sum((s - intercept - slope * v) ** 2 for v, s in zip(x, spreads))
        if best is None or sse < best[0] - 1e-12:
            best = (sse, float(k), slope)
    if best is None:
        return FIXED, {"fitted": False, "reason": "no candidate with a non-negative slope", "pairs": n}
    return best[1], {"fitted": True, "pairs": n, "slope": best[2], "sse": best[0]}


def asof_ratios(
    rows: Sequence[DailyObservation], rule: InformationRule, *, last_day: date
) -> List[Optional[float]]:
    """The reserves-to-assets ratio the rule reads at each row's own 16:00 decision; `None` if a leg has no read.

    Each leg is read at its own latest public row. Row `i` reads rows `0..i` only, through `rule` with the scored
    row `i + 1`, exactly as a forecast made at `i` would. Rows after `last_day` are `None`.
    """

    dates = [row.date for row in rows]
    out: List[Optional[float]] = []
    for i, row in enumerate(rows):
        if row.date > last_day:
            out.append(None)
            continue
        out.append(_ratio_at(rows, dates, i, rule))
    return out


def _extended(dates: Sequence[date], i: int) -> List[date]:
    out = list(dates[: i + 1])
    day = out[-1]
    for _ in range(_EXTRA_DATES):
        day = next_business_day(day, 1)
        out.append(day)
    return out


def _ratio_at(
    rows: Sequence[DailyObservation], dates: Sequence[date], i: int, rule: InformationRule
) -> Optional[float]:
    try:
        info = rule.information_set(_extended(dates, i), i + 1)
    except SplitError:
        return None
    read = {r.feature: r.row for r in info.reads}
    if any(feature not in read for feature in READ_FEATURES):
        return None
    reserves = rows[read["reserve_balances"]].values.get("reserve_balances")
    assets = rows[read["bank_total_assets"]].values.get("bank_total_assets")
    if reserves is None or assets is None:
        return None
    return reserves_ratio(float(reserves), float(assets))


def build_columns(
    rows: Sequence[DailyObservation],
    rule: InformationRule,
    *,
    last_day: date,
    q: float = ROLLING_QUANTILE,
    window: int = ROLLING_WINDOW,
    minimum: int = ROLLING_MINIMUM,
) -> List[DailyObservation]:
    """`rows` with the rolling level as a column, for rows to `last_day`; a later row's value is `None`.

    The caller holds the measurement declaration in force (`scarcity.measurement_declaration` and a feature map
    with the measurement fields), so `rule` can read the two legs.
    """

    ratios = asof_ratios(rows, rule, last_day=last_day)
    out = []
    for i, row in enumerate(rows):
        values = dict(row.values)
        values[ROLLING_COLUMN] = (
            rolling_level(ratios, i, q=q, window=window, minimum=minimum) if row.date <= last_day else None
        )
        out.append(DailyObservation(row.date, values))
    return out


def check_no_future(
    rows: Sequence[DailyObservation],
    built: Sequence[DailyObservation],
    rule: InformationRule,
    *,
    last_day: date,
    indices: Sequence[int],
    q: float = ROLLING_QUANTILE,
    window: int = ROLLING_WINDOW,
    minimum: int = ROLLING_MINIMUM,
) -> None:
    """Refuse a built level that is not what the panel cut at its own row gives.

    Raises:
        LookAheadError: a checked row's level differs from the same row rebuilt from `rows` up to and including
            it, so it depended on a later row.
    """

    for i in indices:
        if rows[i].date > last_day:
            continue
        cut = rows[: i + 1]
        again = build_columns(cut, rule, last_day=last_day, q=q, window=window, minimum=minimum)[i]
        have, want = built[i].values.get(ROLLING_COLUMN), again.values.get(ROLLING_COLUMN)
        if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):
            raise LookAheadError(
                f"{ROLLING_COLUMN} on {rows[i].date.isoformat()} is {have}, but the panel cut at that row gives "
                f"{want}; the level depended on a later row"
            )


def distance(ratio: Optional[float], level: Optional[float]) -> Optional[float]:
    """The reserves ratio minus the satiation level (#598); `None` when either is unobserved."""

    if ratio is None or level is None:
        return None
    return float(ratio) - float(level)


def hinge_value(ratio: Optional[float], level: Optional[float]) -> Optional[float]:
    """`hinge(ratio, level)`, or `None` when either is unobserved: the distance that enters only below the level (#598)."""

    if ratio is None or level is None:
        return None
    return hinge(ratio, level)


def build_distance_columns(
    rows: Sequence[DailyObservation],
    rule: InformationRule,
    *,
    last_day: date,
    q: float = ROLLING_QUANTILE,
    window: int = ROLLING_WINDOW,
    minimum: int = ROLLING_MINIMUM,
) -> List[DailyObservation]:
    """`rows` with the rolling distance as two columns, for rows to `last_day`; a later row's values are `None`.

    Row `i` carries the ratio the rule reads at its own decision minus the rolling level at `i` (`DISTANCE_COLUMN`), and the
    percentage points by which that ratio is below the level (`HINGE_COLUMN`). The level is `rolling_level`, with the
    constants of #587 passed in by the caller; nothing here re-tunes them. Only rows up to `i` are read.
    """

    ratios = asof_ratios(rows, rule, last_day=last_day)
    out = []
    for i, row in enumerate(rows):
        values = dict(row.values)
        if row.date <= last_day:
            ratio = ratios[i]
            level = rolling_level(ratios, i, q=q, window=window, minimum=minimum)
            values[DISTANCE_COLUMN] = distance(ratio, level)
            values[HINGE_COLUMN] = hinge_value(ratio, level)
        else:
            values[DISTANCE_COLUMN] = values[HINGE_COLUMN] = None
        out.append(DailyObservation(row.date, values))
    return out


def check_distance_no_future(
    rows: Sequence[DailyObservation],
    built: Sequence[DailyObservation],
    rule: InformationRule,
    *,
    last_day: date,
    indices: Sequence[int],
    q: float = ROLLING_QUANTILE,
    window: int = ROLLING_WINDOW,
    minimum: int = ROLLING_MINIMUM,
) -> None:
    """Refuse a built distance column that is not what the panel cut at its own row gives.

    Raises:
        LookAheadError: a checked row's distance or hinge differs from the same row rebuilt from `rows` up to and including
            it, so it depended on a later row.
    """

    for i in indices:
        if rows[i].date > last_day:
            continue
        cut = rows[: i + 1]
        again = build_distance_columns(cut, rule, last_day=last_day, q=q, window=window, minimum=minimum)[i]
        for column in (DISTANCE_COLUMN, HINGE_COLUMN):
            have, want = built[i].values.get(column), again.values.get(column)
            if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):
                raise LookAheadError(
                    f"{column} on {rows[i].date.isoformat()} is {have}, but the panel cut at that row gives "
                    f"{want}; the column depended on a later row"
                )
