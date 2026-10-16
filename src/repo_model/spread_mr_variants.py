"""Variants of the mean-reverting spread distribution: context-pooled residuals and the B2 average (#761; H5 step 2).

`metadata/spread_distribution_761.json` is the declaration; this module is its arithmetic. The base is
`repo_model.spread_mean_reversion` (#686), unchanged: `level + phi^k * (last - level) + eps_h`. Three variants:

- `spread_mr_ctx`: `eps_h` is pooled by the target day's context, one of a risk day, an ordinary day after a risk day
  and an ordinary day after an ordinary day (`CONTEXTS`). The context is read from the calendar columns of the target
  row and the row before it, through `calendar_view`, which raises `LookAheadError` on any other column; a row's coupon
  settlement counts only where the registry makes it public at the decision instant (#799: the day before at 15:00, so
  not for the target at leads 2 to 5), in the pools and in the forecast alike. A pool of
  fewer than `POOL_MIN` values falls back to the lead's pooled residuals. `phi` is the base fit's.
- `spread_mr_b2`: `w * q_MR + (1 - w) * q_B2`, level by level. `w` is chosen on `WEIGHT_GRID` at each refit, by the mean
  grid CRPS over the last `TRAIL_DAYS` decision days with a forecast of both legs whose five targets were public at the
  refit's decision instant (`choose_weight`); fewer than `MIN_TRAIL` such days give `DEFAULT_WEIGHT`.
- `spread_mr_ctx_b2`: the same average with `spread_mr_ctx` as the first leg.

`b1_recentred_forecast` is the reference row of #741, not a variant: B1 centred on the last ordinary spread at or before
the anchor. Stdlib only.
"""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from .asof import declared_availability
from . import spread_mean_reversion as smr
from .data import DailyObservation
from .evaluation_splits import DAY_TYPE_COLUMNS, SplitDeclaration
from .scoring_protocol import GRID, HORIZONS, ProtocolError, grid_crps
from .splits import LookAheadError, SplitError

#: The coupon-settlement column that makes an ordinary day a scheduled-pressure day (`onset.COUPON_SETTLEMENT_COLUMN`).
COUPON_COLUMN = "treasury_settlement_coupons"
#: The registry source and field that date `COUPON_COLUMN` (`metadata/sources.json`, `scheduled_availability`).
COUPON_SOURCE, COUPON_FIELD = "treasury_auctions", "treasury_settlement_coupon"
#: The only columns a context may read: the calendar, known in advance.
CALENDAR_COLUMNS: Tuple[str, ...] = tuple(DAY_TYPE_COLUMNS) + (COUPON_COLUMN,)
CONTEXTS: Tuple[str, ...] = ("risk_day", "ordinary_after_risk", "ordinary_after_ordinary")
#: A context pool with fewer values falls back to the lead's pooled residuals.
POOL_MIN = 30
#: The weight on mean reversion is searched on this grid.
WEIGHT_GRID: Tuple[float, ...] = tuple(step / 10.0 for step in range(11))
#: The weight is chosen on this many trailing scored decision days, and not on fewer than `MIN_TRAIL`.
TRAIL_DAYS = 250
MIN_TRAIL = 60
DEFAULT_WEIGHT = 0.5
#: Mean CRPS (bp) within which two weights tie; a tie takes the larger weight.
TIE = 1e-9

REFERENCE = "spread_mr_level10"
NAMES: Tuple[str, ...] = ("spread_mr_ctx", "spread_mr_b2", "spread_mr_ctx_b2")
BLENDS: Tuple[str, ...] = ("spread_mr_b2", "spread_mr_ctx_b2")


class CalendarView(MappingABC):
    """A row's calendar columns and nothing else.

    Mutation record: see `tests/test_spread_mr_variants.py` (`CalendarView.__getitem__`).

    Raises:
        LookAheadError: on a read of any column that is not a calendar column.
    """

    def __init__(self, values: Mapping[str, Optional[float]]):
        self._values = values

    def __getitem__(self, column: str) -> Optional[float]:
        if column not in CALENDAR_COLUMNS:
            raise LookAheadError(
                f"a context reads {column!r}, which is not a calendar column; only {', '.join(CALENDAR_COLUMNS)} "
                f"are known in advance"
            )
        return self._values.get(column)

    def __iter__(self) -> Iterator[str]:
        return iter(CALENDAR_COLUMNS)

    def __len__(self) -> int:
        return len(CALENDAR_COLUMNS)


def calendar_view(row: DailyObservation) -> CalendarView:
    return CalendarView(row.values)


def is_risk_day(row: DailyObservation, splits: SplitDeclaration, *, coupon_clause: bool = True) -> bool:
    """A quarter-end, month-end or tax date, or (`coupon_clause`) a day that settles a coupon: read from the calendar
    columns alone. The coupon settlement is dated by the registry, not known in advance (#799); `coupon_clause=False`
    drops it, as the model does at the leads where it is not yet public."""

    view = calendar_view(row)
    if splits.reporting_day_type(row.date, view) != "ordinary":
        return True
    coupons = view.get(COUPON_COLUMN)
    return coupon_clause and coupons is not None and float(coupons) > 0.0


def coupon_public(
    panel: Sequence[DailyObservation],
    row: int,
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> bool:
    """Whether row `row`'s coupon settlement is public at the decision instant on row `decision_index`.

    Read through the registry's declared availability (`asof.declared_availability`), not assumed.
    """

    dates = [panel_row.date for panel_row in panel]
    available = declared_availability(registry, COUPON_SOURCE, COUPON_FIELD, dates, row)
    return available is not None and available <= datetime.combine(dates[decision_index], decision_time)


def target_context(
    panel: Sequence[DailyObservation],
    index: int,
    splits: SplitDeclaration,
    *,
    h: Optional[int] = None,
    registry: Optional[Mapping[str, Mapping[str, object]]] = None,
    decision_time: Optional[time] = None,
) -> str:
    """The context of row `index` as a target: one of `CONTEXTS`, from its calendar columns and the row before's.

    With `h` (and `registry`, `decision_time`) the context is the one a forecast made `h` rows before `index` can
    read: a row's coupon settlement counts only if it is public at that decision instant (`coupon_public`). Without
    `h` it is the hindsight label of the day, for splits and reports only, never an input to a forecast.

    Raises:
        ValueError: the first row, which has no row before it; or `h` without `registry` and `decision_time`.
        LookAheadError: never from here; a coupon not yet public is left out, not read.
    """

    if index < 1:
        raise ValueError("the first row has no day before it, so no context")
    if h is None:
        clause = {index: True, index - 1: True}
    else:
        if registry is None or decision_time is None:
            raise ValueError("a context at a lead needs the registry and the decision time")
        clause = {
            row: coupon_public(panel, row, index - h, registry=registry, decision_time=decision_time)
            for row in (index, index - 1)
        }
    if is_risk_day(panel[index], splits, coupon_clause=clause[index]):
        return "risk_day"
    return (
        "ordinary_after_risk"
        if is_risk_day(panel[index - 1], splits, coupon_clause=clause[index - 1])
        else "ordinary_after_ordinary"
    )


def context_quantiles(
    pools: Mapping[str, Sequence[float]], context: str, *, fallback: Sequence[float]
) -> List[float]:
    """The 23 residual quantiles of `context`'s pool, or `fallback` where it holds fewer than `POOL_MIN` values."""

    pool = pools.get(context, ())
    if len(pool) < POOL_MIN:
        return list(fallback)
    return pb.empirical_quantiles(sorted(pool))


@dataclass(frozen=True)
class ContextFit:
    """The base fit and, per lead and context, the residual quantiles and the number of pairs behind them."""

    base: smr.Fit
    residuals: Mapping[int, Mapping[str, Sequence[float]]]
    sizes: Mapping[int, Mapping[str, int]]
    #: Per lead, the contexts whose own pool was used (not the fallback).
    own_pool: Mapping[int, Tuple[str, ...]]


def context_fit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    base: Optional[smr.Fit] = None,
) -> ContextFit:
    """The context-pooled residuals as of the decision on row `decision_index`.

    `phi` and the training pairs are the base fit's (`spread_mean_reversion.fit`, which runs the information-set guards
    and refuses a training row after the anchor); each pair joins the pool of its target row's context.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    base = smr.fit(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits, levels=levels) if base is None else base
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    residuals: Dict[int, Dict[str, List[float]]] = {}
    sizes: Dict[int, Dict[str, int]] = {}
    own: Dict[int, Tuple[str, ...]] = {}
    for h in HORIZONS:
        k = h + lag
        pools: Dict[str, List[float]] = {context: [] for context in CONTEXTS}
        for origin, target in rows[h]:
            deviation = panel[origin].spread_bps - levels[origin]
            pools[target_context(panel, target, splits, h=h, registry=registry, decision_time=decision_time)].append(
                (panel[target].spread_bps - levels[origin]) - base.phi**k * deviation
            )
        sizes[h] = {context: len(pool) for context, pool in pools.items()}
        residuals[h] = {
            context: context_quantiles(pools, context, fallback=base.residuals[h]) for context in CONTEXTS
        }
        own[h] = tuple(context for context in CONTEXTS if len(pools[context]) >= POOL_MIN)
    return ContextFit(base, residuals, sizes, own)


def context_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: ContextFit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
) -> Dict[int, List[float]]:
    """The decision day's forecast from `fit_` (possibly an older fit): `last`, `level`, `k` and the contexts read afresh.

    Raises:
        InsufficientHistory: the anchor has no level.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level = levels[anchor]
    if level is None:
        raise smr.InsufficientHistory(
            f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor"
        )
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    out = {}
    for h in HORIZONS:
        centre = level + fit_.base.phi ** (h + lag) * (last - level)
        context = target_context(
            panel, decision_index + h, splits, h=h, registry=registry, decision_time=decision_time
        )
        out[h] = [centre + value for value in fit_.residuals[h][context]]
    return out


def blend(
    first: Mapping[int, Sequence[float]], second: Mapping[int, Sequence[float]], weight: float
) -> Dict[int, List[float]]:
    """`weight * first + (1 - weight) * second`, level by level, per lead.

    Raises:
        ValueError: a weight that is not on `WEIGHT_GRID`.
    """

    if weight not in WEIGHT_GRID:
        raise ValueError(f"the weight {weight} is not on the declared grid {WEIGHT_GRID}")
    return {
        h: [weight * a + (1.0 - weight) * b for a, b in zip(first[h], second[h])] for h in HORIZONS
    }


def choose_weight(
    panel: Sequence[DailyObservation],
    anchor: int,
    leg: Mapping[int, Mapping[int, Sequence[float]]],
    b2: Mapping[int, Mapping[int, Sequence[float]]],
) -> float:
    """The weight on `leg` that scored best on the trailing days public at the anchor.

    `leg` and `b2` map a decision row to the forecast made on it. The scored days are the last `TRAIL_DAYS` decision rows
    in both whose five targets are at or before `anchor`, the last row public at the refit's decision instant; every
    target row read is required public. The criterion is the mean grid CRPS over those days and the five leads; a tie
    (within `TIE`) takes the larger weight. Fewer than `MIN_TRAIL` days give `DEFAULT_WEIGHT`.

    Mutation record: see `tests/test_spread_mr_variants.py` (`choose_weight`).

    Raises:
        LookAheadError: a scored target row after the anchor.
    """

    lead = max(HORIZONS)
    eligible = sorted(index for index in leg if index in b2 and index + lead <= anchor)
    recent = eligible[-TRAIL_DAYS:]
    if len(recent) < MIN_TRAIL:
        return DEFAULT_WEIGHT
    dates = [row.date for row in panel]
    pb._require_public(
        {index + h for index in recent for h in HORIZONS}, anchor, dates,
        f"the weight chosen at the refit whose anchor is {dates[anchor]}",
    )
    best, best_loss = DEFAULT_WEIGHT, float("inf")
    for weight in reversed(WEIGHT_GRID):
        loss = 0.0
        for index in recent:
            mixed = blend(leg[index], b2[index], weight)
            loss += sum(grid_crps(mixed[h], panel[index + h].spread_bps) for h in HORIZONS)
        loss /= len(recent) * len(HORIZONS)
        if loss < best_loss - TIE:
            best, best_loss = weight, loss
    return best


@dataclass(frozen=True)
class VariantWalk:
    #: Name -> decision day -> lead -> 23 quantiles; `REFERENCE` is the base model's own walk.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    #: Decision day -> the day of the fit it was forecast with.
    fit_used: Dict[date, date]
    #: Refit day -> the context fit.
    fits: Dict[date, ContextFit]
    #: Refit day -> blend name -> the weight on mean reversion chosen there.
    weights: Dict[date, Dict[str, float]]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Sequence[date],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    b2: Mapping[date, Mapping[int, Sequence[float]]],
    refit_every: int = smr.REFIT_EVERY,
) -> VariantWalk:
    """The base model and the three variants on `decision_days`, refitting as `spread_mean_reversion.walk` does.

    `b2` is B2's forecast on each decision day (`protocol_benchmarks.b2_forecast`); a day without one has no blend, and
    is not scored in a weight choice. The base model's forecasts are `spread_mean_reversion.walk`'s exactly.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    b2_rows = {position[day]: forecast for day, forecast in b2.items() if day in position}
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {REFERENCE: {}, **{name: {} for name in NAMES}}
    history: Dict[str, Dict[int, Dict[int, List[float]]]] = {REFERENCE: {}, "spread_mr_ctx": {}}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, ContextFit] = {}
    weights: Dict[date, Dict[str, float]] = {}
    skipped: List[date] = []
    current: Optional[ContextFit] = None
    current_weights: Dict[str, float] = {}
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                current = context_fit(panel, index, base=base, **settings)
                anchor = pb._anchor(panel, index, registry, decision_time)
                current_weights = {
                    "spread_mr_b2": choose_weight(panel, anchor, history[REFERENCE], b2_rows),
                    "spread_mr_ctx_b2": choose_weight(panel, anchor, history["spread_mr_ctx"], b2_rows),
                }
                fits[day], weights[day] = current, dict(current_weights)
                since = 0
            reference = smr.forecast(panel, index, current.base, **settings)
            contextual = context_forecast(panel, index, current, **settings)
        except smr.InsufficientHistory:
            skipped.append(day)
            continue
        except SplitError:
            if current is not None:
                raise
            skipped.append(day)
            continue
        fit_used[day] = current.base.fitted_on
        since += 1
        forecasts[REFERENCE][day], forecasts["spread_mr_ctx"][day] = reference, contextual
        history[REFERENCE][index], history["spread_mr_ctx"][index] = reference, contextual
        if index in b2_rows:
            forecasts["spread_mr_b2"][day] = blend(reference, b2_rows[index], current_weights["spread_mr_b2"])
            forecasts["spread_mr_ctx_b2"][day] = blend(contextual, b2_rows[index], current_weights["spread_mr_ctx_b2"])
    return VariantWalk(forecasts, fit_used, fits, weights, tuple(skipped))


def b1_recentred_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> Dict[int, List[float]]:
    """B1 with its centre moved from the anchor's spread to the last ordinary spread at or before the anchor (#741).

    A reference row, not a benchmark of the protocol. The changes are B1's own; every row read is at or before the
    anchor.

    Raises:
        ProtocolError: no ordinary day at or before the anchor.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    ordinary = next(
        (
            s for s in range(anchor, -1, -1)
            if splits.reporting_day_type(panel[s].date, panel[s].values) == "ordinary"
        ),
        None,
    )
    if ordinary is None:
        raise ProtocolError(f"no ordinary day at or before {panel[anchor].date}")
    dates = [row.date for row in panel]
    pb._require_public([ordinary], anchor, dates, f"the recentred B1 for {dates[decision_index]}")
    b1 = pb.b1_forecast(panel, decision_index, registry=registry, decision_time=decision_time)
    shift = panel[ordinary].spread_bps - panel[anchor].spread_bps
    return {h: [value + shift for value in b1[h]] for h in HORIZONS}
