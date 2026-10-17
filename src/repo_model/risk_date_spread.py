"""The spread on announced risk dates: the day set, the calendar benchmark and the type x state model (#693; H6, development tier).

`metadata/risk_date_spread_693.json` is the declaration; this module is its arithmetic. The target is the SOFR - IORB spread
in bp on a day that is known in advance to be a risk date, h business days after a decision day, as the 23 quantiles of
`scoring_protocol.GRID`.

* A **risk date** has one of four types, in this precedence (`risk_day_type`): `quarter_end`, `month_end` (one of the month's last
  two business days) and `tax_date`, which are `SplitDeclaration.reporting_day_type`, then `settlement`, a day with a coupon
  settlement (`treasury_settlement_coupons > 0`, the reading of `pressure_judge._scheduled_risk_date`). Every other day is not a
  risk date and is not scored here. The type is read from the target row's own calendar columns, as protocol B2 reads them,
  except the coupon settlement, which counts at a lead only where the registry makes it public by the decision instant
  (`target_risk_type`; Eleonora's ruling on #720, 13 October 2026, point 2; #849). A day already public (a sample day) is typed
  in hindsight.
* The **risk-date calendar benchmark** (`calendar_forecast`) is the empirical distribution of the spreads on days of the target's
  risk type in the trailing year, rows at or before the anchor; its median is its point forecast.
* The **type x state model** (`type_state_forecast`) is the empirical distribution of the spreads on days of the target's risk type
  *and* scarcity-state group in the trailing two years, rows at or before the anchor, when that cell holds at least `MIN_CELL`
  days; otherwise the type alone over the same two years (`basis` says which). The state group (`state_group`) is `low` for
  states 0 and 1, `high` for 2 and 3, `unknown` for none; a target whose state is unknown is forecast from the type alone. A
  sample day's state, and the target's, are each read as of the decision instant at the lead being forecast
  (`states[h][day]`, `scarcity.own_leg_states` at horizon h), so the target's state was public when the decision was made.

The anchor is the latest row public at the decision instant (`protocol_benchmarks._anchor`, which runs both guards of
`InformationRule` at every lead); `protocol_benchmarks._require_public` raises `LookAheadError` for any sampled row after it.
Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Dict, List, Mapping, Optional, Sequence

from . import protocol_benchmarks as pb
from . import risk_dates
from . import spread_mr_variants as smv
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import GRID, HORIZONS, ProtocolError
from .splits import LookAheadError

#: The risk types, in the order of their precedence after the three of `reporting_day_type`.
RISK_TYPES = ("quarter_end", "month_end", "tax_date", "settlement")
#: The calendar benchmark's window, in years: B2's.
CALENDAR_YEARS = pb.B2_YEARS
#: The type x state model's window, in years: B1's.
CELL_YEARS = pb.B1_YEARS
#: A (type, state group) cell with fewer sample days than this falls back to the type alone.
MIN_CELL = 10
#: The index of the median on the grid.
MEDIAN_AT = GRID.index(0.5)


def risk_day_type(
    when: date, values: Mapping[str, Optional[float]], splits: SplitDeclaration, *, coupon_clause: bool = True
) -> Optional[str]:
    """The risk type of a day, or `None` when it is not a risk date.

    `coupon_clause=False` drops the coupon settlement. The default reads it, which is right for a day already public (a sample
    day, a report); a target at a lead goes through `target_risk_type`.
    """

    if not risk_dates.is_risk_date(
        values, risk_dates.NON_ORDINARY, splits=splits, coupon_clause=coupon_clause, reporting_on=when
    ):
        return None
    kind = splits.reporting_day_type(when, values)
    return kind if kind in ("quarter_end", "month_end", "tax_date") else "settlement"


def require_settlement_public(
    panel: Sequence[DailyObservation],
    row: int,
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> None:
    """Refuse to read row `row`'s coupon settlement at the decision on row `decision_index` unless it was public then.

    Mutation record: see `tests/test_risk_date_spread.py` (`target_risk_type` reads the coupon clause as always true).

    Raises:
        LookAheadError: the settlement flag was not public at the decision instant.
    """

    if not smv.coupon_public(panel, row, decision_index, registry=registry, decision_time=decision_time):
        raise LookAheadError(
            f"the coupon settlement of {panel[row].date} was not public at the decision instant of {panel[decision_index].date}"
        )


def target_risk_type(
    panel: Sequence[DailyObservation],
    decision_index: int,
    h: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> Optional[str]:
    """The risk type of the target `h` rows after the decision, as that decision could read it (#849).

    A quarter-end, month-end or tax date is a calendar fact. A coupon settlement makes the day a risk date only where its
    flag was public at the decision instant (`spread_mr_variants.coupon_public`); otherwise the day is not a risk date at
    this lead.

    Raises:
        LookAheadError: a settlement is read that was not public (`require_settlement_public`).
    """

    scored = decision_index + h
    public = smv.coupon_public(panel, scored, decision_index, registry=registry, decision_time=decision_time)
    kind = risk_day_type(panel[scored].date, panel[scored].values, splits, coupon_clause=public)
    if kind == "settlement":
        require_settlement_public(panel, scored, decision_index, registry=registry, decision_time=decision_time)
    return kind


def state_group(state: Optional[float]) -> str:
    """`low` for the scarcity states 0 and 1, `high` for 2 and 3, `unknown` for none.

    Raises:
        ValueError: a state that is not 0, 1, 2, 3 or `None`.
    """

    if state is None:
        return "unknown"
    if state not in (0, 1, 2, 3):
        raise ValueError(f"reserve-scarcity state {state!r} is not 0 to 3")
    return "low" if state <= 1 else "high"


def median(quantiles: Sequence[float]) -> float:
    """The median of a forecast on the grid: its 0.5 quantile."""

    return quantiles[MEDIAN_AT]


def sample_rows(panel: Sequence[DailyObservation], decision_index: int, anchor: int, *, years: int) -> List[int]:
    """The rows of the trailing `years` years at or before the anchor, each required public.

    Mutation record: see `tests/test_risk_date_spread.py` (the upper bound of the range).

    Raises:
        LookAheadError: a row after the anchor is among them.
    """

    first = pb._window_start(panel, decision_index, years)
    rows = list(range(first, anchor + 1))
    pb._require_public(rows, anchor, [row.date for row in panel], f"the risk-date sample for {panel[decision_index].date}")
    return rows


def require_sample(rows: Sequence[object], kind: str, decision_day: date) -> None:
    """Refuse an empty sample, as protocol B2 does.

    Raises:
        ProtocolError: no day of the type in the window.
    """

    if not rows:
        raise ProtocolError(f"no {kind} day in the window before {decision_day} to forecast from")


def _target_types(
    panel: Sequence[DailyObservation],
    decision_index: int,
    splits: SplitDeclaration,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> Dict[int, str]:
    """Lead -> risk type of its target, for the leads whose target is a risk date as the decision could read it.

    Raises:
        ProtocolError: a lead has no row in the panel.
        LookAheadError: a settlement is read that was not public.
    """

    out = {}
    for h in HORIZONS:
        if decision_index + h >= len(panel):
            raise ProtocolError(f"lead {h} from {panel[decision_index].date} has no row in the panel")
        kind = target_risk_type(panel, decision_index, h, registry=registry, decision_time=decision_time, splits=splits)
        if kind is not None:
            out[h] = kind
    return out


def calendar_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> Dict[int, List[float]]:
    """The risk-date calendar benchmark: per lead whose target is a risk date, the trailing year's spreads of its type.

    Raises:
        ProtocolError: a lead has no row, or no day of the target's type in the window.
        LookAheadError, StaleReadError: the information-set guards of the decision.
    """

    targets = _target_types(panel, decision_index, splits, registry=registry, decision_time=decision_time)
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    rows = sample_rows(panel, decision_index, anchor, years=CALENDAR_YEARS)
    out = {}
    for h, kind in targets.items():
        same = [s for s in rows if risk_day_type(panel[s].date, panel[s].values, splits) == kind]
        require_sample(same, kind, panel[decision_index].date)
        out[h] = pb.empirical_quantiles(sorted(panel[s].spread_bps for s in same))
    return out


@dataclass(frozen=True)
class TypeStateForecast:
    """Per lead whose target is a risk date: the quantiles, and the sample they came from (`cell` or `type`)."""

    quantiles: Dict[int, List[float]]
    basis: Dict[int, str]
    sizes: Dict[int, int]


def type_state_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    states: Mapping[int, Mapping[date, Optional[float]]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    min_cell: int = MIN_CELL,
) -> TypeStateForecast:
    """The type x state model's forecast for the decision on row `decision_index`.

    `states[h][day]` is the scarcity state of `day` as read at the decision instant at lead h (absent or `None` is unknown).

    Raises:
        ProtocolError: a lead has no row, or no day of the target's type in the window.
        LookAheadError, StaleReadError: the information-set guards of the decision.
        ValueError: a state outside 0 to 3.
    """

    targets = _target_types(panel, decision_index, splits, registry=registry, decision_time=decision_time)
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    rows = sample_rows(panel, decision_index, anchor, years=CELL_YEARS)
    quantiles, basis, sizes = {}, {}, {}
    for h, kind in targets.items():
        same = [s for s in rows if risk_day_type(panel[s].date, panel[s].values, splits) == kind]
        require_sample(same, kind, panel[decision_index].date)
        group = state_group(states[h].get(panel[decision_index + h].date))
        chosen, how = same, "type"
        if group != "unknown":
            cell = [s for s in same if state_group(states[h].get(panel[s].date)) == group]
            if len(cell) >= min_cell:
                chosen, how = cell, "cell"
        quantiles[h] = pb.empirical_quantiles(sorted(panel[s].spread_bps for s in chosen))
        basis[h], sizes[h] = how, len(chosen)
    return TypeStateForecast(quantiles, basis, sizes)
