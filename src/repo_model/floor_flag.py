"""The floor flag and the residual pools it splits (#966; H5 step 3, 2021-23 and the residual pools).

`metadata/floor_flag_966.json` is the declaration; this module is its arithmetic. The flag says that SOFR sits on the
ON RRP offering rate, the floor of the corridor, so the spread to IORB barely moves:

- the spread to the floor at row `i` is SOFR less the ON RRP offering rate in force on that row, in bp. The rate is read
  from `metadata/policy_events.json` by announcement, never by effective date alone: an entry counts on a row only if it
  was public at that row's decision instant and effective on or before the row's date (`policy_events.known_entries`).
  A row before the first ON RRP entry has no spread to the floor.
- the flag at row `i` is on when the median of the spreads to the floor of the last `WINDOW` rows at or before `i` is at
  most `THRESHOLD_BP`, with at least `MIN_ROWS` of those rows defined; off when it is above; `None` when fewer than
  `MIN_ROWS` rows are defined. A row's flag reads that row and the rows before it, so a flag read at the anchor is as-of
  (`check_no_future` refuses one that is not).

Two arms use it as a pool selector, a third wraps a model:

- (i) `flag_b1_forecast`: B1's change pool restricted to the origins whose flag is the anchor's.
- (ii) `flag_fit` and `flag_forecast`: the mean-reversion candidate's `eps_h` pool (`spread_mean_reversion`) restricted to
  the training pairs whose origin flag is the anchor's. `phi` is the base fit's.
- (iii) `two_part`: a model's law off the flag, B1's law on it.
- (iv) `flag_scaled_fit` and `flag_scaled_forecast`: the volatility-scaled mean reversion of #941
  (`spread_mr_fhs`, variant `FHS_NAME`) with its standardised residual pool restricted to the training pairs whose origin
  flag is the anchor's; (v) `two_part` on that model (B1's law on the flag, the scaled model's off it). Added on Eleonora's
  ruling of 22 October 2026: the flag and the two-part rule go on the best model as well as on B1.

A restricted pool of fewer than `MIN_POOL` changes (or residuals) at a lead, or an anchor with no flag, gives the full
pool. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_fhs as fhs
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .policy_events import PolicyEntry, known_entries
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: The trailing rows the flag's median is taken over, and the fewest defined ones it needs.
WINDOW = 60
MIN_ROWS = 40
#: On when the median spread to the floor is at most this, in bp.
THRESHOLD_BP = 1.0
#: A restricted pool with fewer values at a lead falls back to the full pool.
MIN_POOL = 60
#: Rounding applied to the median before the comparison, so 1.0000000000000004 bp is 1 bp.
ROUND = 9


def rrp_rate_percent(register: Sequence[PolicyEntry], day: date, decision_time: time) -> Optional[float]:
    """The ON RRP offering rate in force on `day` as public at `day`'s decision instant, in percent; `None` before any.

    The entries that count are announced at or before `datetime.combine(day, decision_time)` and effective on or before
    `day`; of those, the latest by effective date and announcement. An entry that is effective by `day` but was announced
    after the instant (a retroactive one) is not read. An entry without an offering rate (a limit-only change) does not
    set the rate: the latest entry that carries one does.
    """

    public = known_entries(register, datetime.combine(day, decision_time))
    pool = [
        e for e in public
        if e.kind == "on_rrp" and e.effective is not None and e.effective <= day
        and e.details.get("offering_rate_percent") is not None
    ]
    if not pool:
        return None
    return float(max(pool, key=lambda e: (e.effective, e.announced_at)).details["offering_rate_percent"])


def spread_to_floor_bp(
    panel: Sequence[DailyObservation], register: Sequence[PolicyEntry], decision_time: time
) -> List[Optional[float]]:
    """SOFR less the ON RRP offering rate in force on each row, in bp; `None` where no rate is in force."""

    out: List[Optional[float]] = []
    for row in panel:
        rate = rrp_rate_percent(register, row.date, decision_time)
        out.append(None if rate is None else 100.0 * (float(row.values["sofr"]) - rate))
    return out


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0


def _decide(window: Sequence[float]) -> Optional[bool]:
    """The flag from the defined spreads to the floor of a row's trailing window: `None` under `MIN_ROWS` of them."""

    if len(window) < MIN_ROWS:
        return None
    return round(_median(window), ROUND) <= THRESHOLD_BP


def flags(
    panel: Sequence[DailyObservation], register: Sequence[PolicyEntry], decision_time: time
) -> List[Optional[bool]]:
    """The floor flag at every row: True, False, or None where fewer than `MIN_ROWS` of the last `WINDOW` rows are defined.

    Row `i` reads rows `i - WINDOW + 1` to `i`, and no later row.

    Mutation record: see `tests/test_floor_flag.py` (`flags`).
    """

    spreads = spread_to_floor_bp(panel, register, decision_time)
    return [
        _decide([v for v in spreads[max(0, i - WINDOW + 1): i + 1] if v is not None]) for i in range(len(panel))
    ]


def flag_at(
    panel: Sequence[DailyObservation], register: Sequence[PolicyEntry], decision_time: time
) -> Optional[bool]:
    """The flag of the last row of `panel`, from that row and the rows before it: the panel is the cut at the row."""

    tail = panel[-WINDOW:]
    return _decide([v for v in spread_to_floor_bp(tail, register, decision_time) if v is not None])


def check_no_future(
    panel: Sequence[DailyObservation],
    built: Sequence[Optional[bool]],
    register: Sequence[PolicyEntry],
    decision_time: time,
    *,
    indices: Sequence[int],
) -> None:
    """Refuse a built flag that is not what the panel cut at its own row gives.

    Raises:
        LookAheadError: a checked row's flag differs from the same row rebuilt from `panel` up to and including it, so
            it depended on a later row.
    """

    for i in indices:
        again = flag_at(panel[: i + 1], register, decision_time)
        if built[i] != again:
            raise LookAheadError(
                f"the floor flag on {panel[i].date.isoformat()} is {built[i]}, but the panel cut at that row gives "
                f"{again}; the flag depended on a later row"
            )


def _pool(values: Sequence[float], full: Sequence[float]) -> Sequence[float]:
    return values if len(values) >= MIN_POOL else full


def flag_b1_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    row_flags: Sequence[Optional[bool]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> Dict[int, List[float]]:
    """Arm (i): B1 with its change pool restricted to origins whose flag is the anchor's.

    The changes are B1's own, `spread[s] - spread[s - h]` for the rows `s` of its window up to the anchor; a change joins
    the restricted pool when the flag at its origin row `s - h` equals the flag at the anchor. A lead whose restricted
    pool holds fewer than `MIN_POOL` changes, and an anchor without a flag, use B1's full pool. Every row read is at or
    before the anchor.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    dates = [row.date for row in panel]
    first = pb._window_start(panel, decision_index, pb.B1_YEARS)
    last = panel[anchor].spread_bps
    state = row_flags[anchor]
    out = {}
    for h in HORIZONS:
        ends = list(range(max(first, h), anchor + 1))
        if not ends:
            raise ProtocolError(f"B1 has no {h}-day change before {dates[anchor]}")
        pb._require_public(ends, anchor, dates, f"the floor-flag B1 for {dates[decision_index]}, lead {h}")
        full = sorted(panel[s].spread_bps - panel[s - h].spread_bps for s in ends)
        if state is None:
            changes = full
        else:
            changes = sorted(
                panel[s].spread_bps - panel[s - h].spread_bps for s in ends if row_flags[s - h] == state
            )
            changes = list(_pool(changes, full))
        out[h] = pb.empirical_quantiles(changes, last)
    return out


@dataclass(frozen=True)
class FlagFit:
    """The base fit and, per lead and flag state, the residual quantiles and the number of pairs behind them."""

    base: smr.Fit
    #: lead -> state (True, False) -> 23 residual quantiles (the base's full pool where the state's pool is short).
    residuals: Mapping[int, Mapping[bool, Sequence[float]]]
    sizes: Mapping[int, Mapping[bool, int]]
    #: Per lead, the states whose own pool was used (not the fallback).
    own_pool: Mapping[int, Tuple[bool, ...]]


def flag_fit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    row_flags: Sequence[Optional[bool]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    base: Optional[smr.Fit] = None,
) -> FlagFit:
    """Arm (ii): the residual pools split by the flag at the training pair's origin, as of the decision on `decision_index`.

    `phi` and the training pairs are the base fit's (`spread_mean_reversion.fit` runs the information-set guards and
    refuses a training row after the anchor); a pair whose origin has no flag joins neither pool.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    base = (
        smr.fit(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits, levels=levels)
        if base is None else base
    )
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    residuals: Dict[int, Dict[bool, Sequence[float]]] = {}
    sizes: Dict[int, Dict[bool, int]] = {}
    own: Dict[int, Tuple[bool, ...]] = {}
    for h in HORIZONS:
        k = h + lag
        pools: Dict[bool, List[float]] = {True: [], False: []}
        for origin, target in rows[h]:
            state = row_flags[origin]
            if state is None:
                continue
            deviation = panel[origin].spread_bps - levels[origin]
            pools[state].append((panel[target].spread_bps - levels[origin]) - base.phi**k * deviation)
        sizes[h] = {state: len(pool) for state, pool in pools.items()}
        residuals[h] = {
            state: (pb.empirical_quantiles(sorted(pool)) if len(pool) >= MIN_POOL else list(base.residuals[h]))
            for state, pool in pools.items()
        }
        own[h] = tuple(state for state in (True, False) if len(pools[state]) >= MIN_POOL)
    return FlagFit(base, residuals, sizes, own)


def flag_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: FlagFit,
    row_flags: Sequence[Optional[bool]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
) -> Dict[int, List[float]]:
    """Arm (ii)'s forecast from `fit_` (possibly an older fit): `last`, `level`, `k` and the anchor's flag read afresh.

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
    state = row_flags[anchor]
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    out = {}
    for h in HORIZONS:
        centre = level + fit_.base.phi ** (h + lag) * (last - level)
        pool = fit_.base.residuals[h] if state is None else fit_.residuals[h][state]
        out[h] = [centre + value for value in pool]
    return out


#: The #941 variant ("mad window 20 floor 0.5") the scaled arms are built on, and the arms' names in a walk.
FHS_NAME = "spread_mr_fhs_mad20_f0.5"
ARM_FHS = "flag_fhs"
ARM_TWO_FHS = "two_part_fhs"


@dataclass(frozen=True)
class FlagScaledFit:
    """The base fit, the scaled fit's whole-lead pools and, per lead and flag state, the standardised residual quantiles."""

    base: smr.Fit
    scaled: fhs.ScaledFit
    #: lead -> state (True, False) -> 23 standardised quantiles (the whole-lead pool where the state's pool is short).
    standardised: Mapping[int, Mapping[bool, Sequence[float]]]
    sizes: Mapping[int, Mapping[bool, int]]
    #: Per lead, the states whose own pool was used (not the fallback).
    own_pool: Mapping[int, Tuple[bool, ...]]


def flag_scaled_fit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    row_flags: Sequence[Optional[bool]],
    variant: fhs.Variant,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    base: Optional[smr.Fit] = None,
    scaled: Optional[fhs.ScaledFit] = None,
) -> FlagScaledFit:
    """Arm (iv): the standardised residual pools of `variant` split by the flag at the training pair's origin.

    `phi`, the training pairs, the scale and the whole-lead pools are `spread_mr_fhs.fit`'s (it runs the information-set
    guards, requires every row the scale reads to be public, and refuses a training row after the anchor); a pair whose
    origin has no flag or no scale joins neither pool. A state's pool of fewer than `MIN_POOL` pairs falls back to the
    whole-lead pool.

    Mutation record: see `tests/test_floor_flag.py` (`flag_scaled_fit`).
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    base = smr.fit(panel, decision_index, **settings) if base is None else base
    scaled = fhs.fit(panel, decision_index, [variant], base=base, **settings)[variant.name] if scaled is None else scaled
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    reader = fhs.ScaleReader([row.spread_bps for row in panel[: anchor + 1]], variant)
    standardised: Dict[int, Dict[bool, Sequence[float]]] = {}
    sizes: Dict[int, Dict[bool, int]] = {}
    own: Dict[int, Tuple[bool, ...]] = {}
    for h in HORIZONS:
        k = h + lag
        pools: Dict[bool, List[float]] = {True: [], False: []}
        for origin, target in rows[h]:
            state = row_flags[origin]
            scale = reader.at(origin)
            if state is None or scale is None:
                continue
            raw = (panel[target].spread_bps - levels[origin]) - base.phi**k * (panel[origin].spread_bps - levels[origin])
            pools[state].append(raw / scale)
        sizes[h] = {state: len(pool) for state, pool in pools.items()}
        standardised[h] = {
            state: (pb.empirical_quantiles(sorted(pool)) if len(pool) >= MIN_POOL else list(scaled.standardised[h]))
            for state, pool in pools.items()
        }
        own[h] = tuple(state for state in (True, False) if len(pools[state]) >= MIN_POOL)
    return FlagScaledFit(base, scaled, standardised, sizes, own)


def flag_scaled_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: FlagScaledFit,
    row_flags: Sequence[Optional[bool]],
    variant: fhs.Variant,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
) -> Dict[int, List[float]]:
    """Arm (iv)'s forecast from `fit_` (possibly an older fit): the scaled model's forecast with the anchor's state's pool.

    The anchor's flag is read afresh; with no flag the whole-lead pool is used, which is the scaled model itself.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    state = row_flags[anchor]
    chosen = fit_.scaled.standardised if state is None else {h: fit_.standardised[h][state] for h in HORIZONS}
    pool = fhs.ScaledFit(chosen, fit_.scaled.pairs, fit_.scaled.left_out)
    return fhs.forecast(
        panel, decision_index, pool, fit_.base, variant,
        registry=registry, decision_time=decision_time, splits=splits, levels=levels,
    )


def two_part(
    law: Mapping[int, Sequence[float]], b1: Mapping[int, Sequence[float]], flag: Optional[bool]
) -> Dict[int, List[float]]:
    """Arm (iii): `law` off the flag, B1's law on it. An anchor without a flag keeps `law`."""

    chosen = b1 if flag else law
    return {h: list(chosen[h]) for h in HORIZONS}


@dataclass(frozen=True)
class FlagWalk:
    #: Name -> decision day -> lead -> 23 quantiles. `smr.REFERENCE`-style names are the caller's.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    fit_used: Dict[date, date]
    fits: Dict[date, FlagFit]
    skipped: Tuple[date, ...]
    #: Decision day -> the flag at its anchor.
    anchor_flag: Dict[date, Optional[bool]]
    #: Refit day -> the scaled arm's fit (empty when the walk was run without a variant).
    scaled_fits: Dict[date, FlagScaledFit] = field(default_factory=dict)


ARM_B1 = "flag_b1"
ARM_MR = "flag_mr"
BASE_MR = "spread_mr_level10"


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Sequence[date],
    row_flags: Sequence[Optional[bool]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    variant: Optional[fhs.Variant] = None,
) -> FlagWalk:
    """The base mean reversion and arms (i) and (ii) on `decision_days`, refitting as `spread_mean_reversion.walk` does.

    With a `variant` (#941's, `FHS_NAME`), the series `variant.name`, `ARM_FHS` (iv) and `ARM_TWO_FHS` (v) are added, on
    the same refits and the same days; a day on which any of them has no forecast is skipped for all.

    Arm (i) has no fit and is forecast on every day it can be; the days without a mean-reversion forecast (too little
    history) are skipped for every series, so all series cover the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    names = [BASE_MR, ARM_B1, ARM_MR] + ([variant.name, ARM_FHS, ARM_TWO_FHS] if variant is not None else [])
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {name: {} for name in names}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, FlagFit] = {}
    scaled_fits: Dict[date, FlagScaledFit] = {}
    current_scaled: Optional[FlagScaledFit] = None
    anchor_flag: Dict[date, Optional[bool]] = {}
    skipped: List[date] = []
    current: Optional[FlagFit] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                refit = smr.fit(panel, index, **settings)
                refit_flag = flag_fit(panel, index, row_flags, base=refit, **settings)
                if variant is not None:
                    current_scaled = flag_scaled_fit(panel, index, row_flags, variant, base=refit, **settings)
                    scaled_fits[day] = current_scaled
                current = refit_flag
                fits[day] = current
                since = 0
            reference = smr.forecast(panel, index, current.base, **settings)
            arm_mr = flag_forecast(panel, index, current, row_flags, **settings)
            arm_b1 = flag_b1_forecast(panel, index, row_flags, registry=registry, decision_time=decision_time)
            if variant is not None:
                scaled = fhs.forecast(
                    panel, index, current_scaled.scaled, current.base, variant, **settings
                )
                arm_fhs = flag_scaled_forecast(panel, index, current_scaled, row_flags, variant, **settings)
                full_b1 = pb.b1_forecast(panel, index, registry=registry, decision_time=decision_time)
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
        forecasts[BASE_MR][day], forecasts[ARM_MR][day], forecasts[ARM_B1][day] = reference, arm_mr, arm_b1
        anchor_flag[day] = row_flags[pb._anchor(panel, index, registry, decision_time)]
        if variant is not None:
            forecasts[variant.name][day], forecasts[ARM_FHS][day] = scaled, arm_fhs
            forecasts[ARM_TWO_FHS][day] = two_part(scaled, full_b1, anchor_flag[day])
    return FlagWalk(forecasts, fit_used, fits, tuple(skipped), anchor_flag, scaled_fits)
