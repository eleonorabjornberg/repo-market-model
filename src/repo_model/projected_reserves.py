"""Reserves projected to the scored day (#545, track S2 of #374).

A funding desk does not forecast pressure from today's reserves: it rolls them forward to the day in
question through every flow it already knows about, and asks where that leaves the market on the demand
curve. This module does the roll-forward and writes it as panel columns; the forecast is the direct
logistic (`ml.pressure_logistic_exceedance`) on them. `metadata/projected_reserves.json` declares all of
it before any score.

**The roll-forward** for the scored day `T = d + h` (decision row `d`, 16:00):

* the start is the reserve level the as-of rule reads at `d`, the H.4.1 Wednesday level observed on
  the Wednesday `O` on or before its read row;
* to `d`: the Treasury General Account and the overnight reverse repo facility gain what reserves lose
  (the Fed liability identity), so `R_d = R_O - (TGA_read - TGA_O) - (RRP_read - RRP_O)`, less the net
  settlement announced for the rows after the TGA's read row up to `d`;
* after `d`: the net Treasury settlement announced for the next `h` business days, plus the expected
  tax receipts on tax dates (the previous year's rise on the same position of the same month's window,
  less that day's settlement). The ON RRP balance absorbs a net drain before reserves do.

The Treasury leg of the Federal Reserve's runoff is not added: the Treasury finances what the Federal
Reserve redeems with a larger public offering, which the announced net settlement already counts. No
announced TGA path is tracked, so the persistence rule applies: no flow beyond those above.

**The columns** (`COLUMNS`), one set per horizon: `proj_reserves_h{h}` in USD billions, `proj_dist_h{h}`
the projected level over bank assets above the satiation level (`scarcity.SATIATION_BAND`, the lower
end), and `proj_change_h{h}` the projected change from the start, both in percentage points of bank
assets. They are built for scored days to the last scored day only, and are off in every published
declaration (`COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`).

**Availability.** Every column of row `d` is a function of the as-of reads at `d`'s own decision and of
rows up to `d`. `build_row` reads through `asof.InformationRule` with the scored row `d + 1` at horizon
1, so the reads are exactly those a forecast of `d + 1` made at `d` would take, and `check_no_future`
rebuilds a row from the panel cut at `d` and refuses (`LookAheadError`) a column that differs.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta  # noqa: F401 (datetime: the announcement instant)
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from . import net_settlement as ns
from .asof import WEEKLY_OBSERVATION_WEEKDAY, InformationRule
from .data import (
    TAX_WINDOW_BUSINESS_DAYS,
    DailyObservation,
    _is_tax_business_day,
    corporate_tax_deadline,
    next_business_day,
    tax_date,
)
from .scarcity import SATIATION_BAND
from .splits import LookAheadError, SplitError

__all__ = [
    "AHEAD_COLUMNS",
    "COLUMNS",
    "COLUMNS_BUILT",
    "COLUMN_FIELDS",
    "HORIZONS",
    "READ_FEATURES",
    "SATIATION",
    "SOURCE_ID",
    "ahead_columns",
    "build_columns",
    "build_row",
    "check_no_future",
    "distance_and_change",
    "expected_tax",
    "extended_dates",
    "features_at_horizon",
    "reserve_change",
    "roll_forward",
    "tax_window",
    "window_tax",
]

#: The source the as-of rule reads the columns through (`metadata/sources_measurement.json`). Zero lag:
#: each row's columns are built from what was public at that row's own decision.
SOURCE_ID = "projected_reserves_columns"
#: The scored days' horizons, in panel rows after the decision row.
HORIZONS = (1, 2, 3, 4, 5)
#: The satiation level, as a share of bank assets: the lower end of the scarcity band, not fitted.
SATIATION = SATIATION_BAND[0]
#: The announced net settlement of the next k business days, summed, k = 1 to 5.
AHEAD_COLUMNS = tuple(f"net_settlement_ahead_{k}d" for k in range(1, 6))
COLUMNS_BUILT = tuple(
    f"proj_{kind}_h{h}" for h in HORIZONS for kind in ("reserves", "dist", "change")
)
COLUMNS = AHEAD_COLUMNS + COLUMNS_BUILT
#: Every column's source field, for the as-of rule. **Off**: a track switches them on.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {name: ((SOURCE_ID, name),) for name in COLUMNS}
#: The features the roll-forward reads through the as-of rule.
READ_FEATURES = ("reserve_balances", "bank_total_assets", "tga_daily", "on_rrp")
#: Business days appended to the dates handed to the rule, so a business-day lag at the last real row is
#: dated the same whatever follows it.
_EXTRA_DATES = 15


def reserve_change(flow: float, rrp_level: float) -> float:
    """The change in reserves from a net `flow` of cash into the Treasury account, USD billions.

    A net drain is absorbed by the ON RRP balance first, one for one, up to the balance; a net paydown
    raises reserves by its size.
    """

    return -(flow - min(max(flow, 0.0), max(rrp_level, 0.0)))


def roll_forward(
    start: float,
    *,
    tga_change: float,
    rrp_change: float,
    gap_settlement: float,
    flow_ahead: float,
    rrp_level: float,
) -> float:
    """The reserve level projected to the scored day, USD billions."""

    return start - tga_change - rrp_change - gap_settlement + reserve_change(flow_ahead, rrp_level)


def distance_and_change(projected: float, start: float, bank_assets: float) -> Tuple[float, float]:
    """`(projected level over bank assets above satiation, projected change from the start)`, in points."""

    if bank_assets <= 0:
        raise ValueError(f"bank assets must be positive, got {bank_assets}")
    return 100.0 * (projected / bank_assets - SATIATION), 100.0 * (projected - start) / bank_assets


def features_at_horizon(horizon: int) -> Tuple[str, ...]:
    """The declared features of the model at `horizon`."""

    if horizon not in HORIZONS:
        raise ValueError(f"horizon must be one of {list(HORIZONS)}, got {horizon}")
    return ("spread_bps", "days_to_month_end", "quarter_end", "tax_date", f"proj_dist_h{horizon}", f"proj_change_h{horizon}")


def tax_window(year: int, month: int) -> List[date]:
    """The days `data.tax_date` flags in `month` of `year`: the deadline and the two business days after it."""

    current = corporate_tax_deadline(year, month)
    window = [current]
    while len(window) <= TAX_WINDOW_BUSINESS_DAYS:
        current += timedelta(days=1)
        if _is_tax_business_day(current):
            window.append(current)
    return window


def expected_tax(day: date, by_date: Mapping[date, DailyObservation]) -> float:
    """The expected tax receipt of `day`, USD billions, from the previous year's same window position.

    On a tax date, the TGA's rise on the same position of the same month's window a year earlier, less
    that day's net settlement, floored at zero; scale 1. Zero off a tax date, and when the earlier row is
    absent or carries no TGA change.
    """

    if tax_date(day) != 1.0:
        return 0.0
    position = tax_window(day.year, day.month).index(day)
    earlier = by_date.get(tax_window(day.year - 1, day.month)[position])
    if earlier is None:
        return 0.0
    change = earlier.values.get("tga_daily_change")
    settled = earlier.values.get("net_settlement")
    if change is None or settled is None:
        return 0.0
    return max(0.0, float(change) - float(settled))


def window_tax(
    rows: Sequence[DailyObservation],
    i: int,
    horizon: int,
    by_date: Optional[Mapping[date, DailyObservation]] = None,
) -> float:
    """The expected tax receipts of the `horizon` business days after row `i`."""

    if by_date is None:
        by_date = {row.date: row for row in rows[: i + 1]}
    total = 0.0
    day = rows[i].date
    for _ in range(horizon):
        day = next_business_day(day, 1)
        total += expected_tax(day, by_date)
    return total


def ahead_columns(
    rows: Sequence[DailyObservation], auctions: Sequence[ns.Auction], declaration: Mapping[str, object]
) -> List[DailyObservation]:
    """`rows` with the announced net settlement of the next k business days, k = 1 to 5, cumulative.

    Each auction counts only from its announcement, as at the declared instant on the row's own day
    (`net_settlement`'s rule), so the value is what was public at the row's decision.
    """

    by_day = ns._by_day(auctions)
    out = []
    for row in rows:
        instant = ns._instant(row.date, declaration)
        values = dict(row.values)
        total = 0.0
        day = row.date
        for k, name in enumerate(AHEAD_COLUMNS, start=1):
            day = next_business_day(day, 1)
            total += ns.net_for_day(by_day.get(day, ()), instant)[0]
            values[name] = total
        out.append(DailyObservation(row.date, values))
    return out


def extended_dates(dates: Sequence[date], i: int) -> List[date]:
    """The panel dates through row `i`, then the next business days: all the rule may know of the calendar."""

    out = list(dates[: i + 1])
    day = out[-1]
    for _ in range(_EXTRA_DATES):
        day = next_business_day(day, 1)
        out.append(day)
    return out


def _value(rows: Sequence[DailyObservation], position: int, column: str) -> Optional[float]:
    value = rows[position].values.get(column)
    return None if value is None else float(value)


def build_row(
    rows: Sequence[DailyObservation],
    i: int,
    rule: InformationRule,
    by_date: Optional[Mapping[date, DailyObservation]] = None,
) -> Dict[str, Optional[float]]:
    """The projected columns of row `i`, from what the rule says was public at its 16:00 decision.

    Every column is `None` when a read or an input is missing. Nothing after row `i` is read.
    """

    empty: Dict[str, Optional[float]] = {name: None for name in COLUMNS_BUILT}
    dates = extended_dates([row.date for row in rows[: i + 1]], i)
    try:
        info = rule.information_set(dates, i + 1)
    except SplitError:
        return empty
    read = {r.feature: r.row for r in info.reads}
    if any(feature not in read for feature in READ_FEATURES):
        return empty
    start = _value(rows, read["reserve_balances"], "reserve_balances")
    assets = _value(rows, read["bank_total_assets"], "bank_total_assets")
    tga_read = _value(rows, read["tga_daily"], "tga_daily")
    rrp_read = _value(rows, read["on_rrp"], "on_rrp")
    if None in (start, assets, tga_read, rrp_read):
        return empty
    reserve_row = read["reserve_balances"]
    observed = rows[reserve_row].date - timedelta(
        days=(rows[reserve_row].date.weekday() - WEEKLY_OBSERVATION_WEEKDAY) % 7
    )
    then = reserve_row
    while then >= 0 and rows[then].date > observed:
        then -= 1
    if then < 0 or then > min(read["tga_daily"], read["on_rrp"]):
        # the level on the Wednesday was not public when the TGA and the facility were read
        return empty
    tga_then = _value(rows, then, "tga_daily")
    rrp_then = _value(rows, then, "on_rrp")
    gap_rows = [_value(rows, q, "net_settlement") for q in range(read["tga_daily"] + 1, i + 1)]
    if None in (tga_then, rrp_then) or None in gap_rows:
        return empty
    gap = sum(gap_rows)
    out = dict(empty)
    for h in HORIZONS:
        ahead = rows[i].values.get(f"net_settlement_ahead_{h}d")
        if ahead is None:
            continue
        projected = roll_forward(
            start,
            tga_change=tga_read - tga_then,
            rrp_change=rrp_read - rrp_then,
            gap_settlement=gap,
            flow_ahead=float(ahead) + window_tax(rows, i, h, by_date),
            rrp_level=rrp_read,
        )
        dist, change = distance_and_change(projected, start, assets)
        out[f"proj_reserves_h{h}"] = projected
        out[f"proj_dist_h{h}"] = dist
        out[f"proj_change_h{h}"] = change
    return out


def build_columns(
    rows: Sequence[DailyObservation], rule: InformationRule, *, last_day: date
) -> List[DailyObservation]:
    """`rows` with the projected columns, for rows to `last_day`; a later row's columns are `None`.

    The caller holds the measurement declaration in force (`scarcity.measurement_declaration` and the
    feature map with `COLUMN_FIELDS` and the measurement fields), so `rule` can read the features.
    """

    by_date = {row.date: row for row in rows}
    out = []
    for i, row in enumerate(rows):
        values = dict(row.values)
        if row.date <= last_day:
            values.update(build_row(rows, i, rule, by_date))
        else:
            values.update({name: None for name in COLUMNS_BUILT})
        out.append(DailyObservation(row.date, values))
    return out


def check_no_future(
    rows: Sequence[DailyObservation],
    built: Sequence[DailyObservation],
    rule: InformationRule,
    *,
    last_day: date,
    indices: Sequence[int],
) -> None:
    """Refuse a built column that is not what the panel cut at its own row gives.

    Raises:
        LookAheadError: a column of a checked row differs from the same row rebuilt from `rows` up to
            and including it, so it depended on a later row.
    """

    for i in indices:
        if rows[i].date > last_day:
            continue
        again = build_row(rows[: i + 1], i, rule)
        for name in COLUMNS_BUILT:
            have, want = built[i].values.get(name), again[name]
            if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-9):
                raise LookAheadError(
                    f"{name} on {rows[i].date.isoformat()} is {have}, but the panel cut at that row gives "
                    f"{want}; the column depended on a later row"
                )
