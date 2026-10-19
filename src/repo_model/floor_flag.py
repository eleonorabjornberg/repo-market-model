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

A restricted pool of fewer than `MIN_POOL` changes (or residuals) at a lead, or an anchor with no flag, gives the full
pool. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
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


def flags(
    panel: Sequence[DailyObservation], register: Sequence[PolicyEntry], decision_time: time
) -> List[Optional[bool]]:
    """The floor flag at every row: True, False, or None where fewer than `MIN_ROWS` of the last `WINDOW` rows are defined.

    Row `i` reads rows `i - WINDOW + 1` to `i`, and no later row.

    Mutation record: see `tests/test_floor_flag.py` (`flags`).
    """

    spreads = spread_to_floor_bp(panel, register, decision_time)
    out: List[Optional[bool]] = []
    for i in range(len(panel)):
        window = [v for v in spreads[max(0, i - WINDOW + 1): i + 1] if v is not None]
        if len(window) < MIN_ROWS:
            out.append(None)
        else:
            out.append(round(_median(window), ROUND) <= THRESHOLD_BP)
    return out


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
        again = flags(panel[: i + 1], register, decision_time)[i]
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
) -> FlagWalk:
    """The base mean reversion and arms (i) and (ii) on `decision_days`, refitting as `spread_mean_reversion.walk` does.

    Arm (i) has no fit and is forecast on every day it can be; the days without a mean-reversion forecast (too little
    history) are skipped for every series, so all series cover the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {BASE_MR: {}, ARM_B1: {}, ARM_MR: {}}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, FlagFit] = {}
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
                current = flag_fit(panel, index, row_flags, base=smr.fit(panel, index, **settings), **settings)
                fits[day] = current
                since = 0
            reference = smr.forecast(panel, index, current.base, **settings)
            arm_mr = flag_forecast(panel, index, current, row_flags, **settings)
            arm_b1 = flag_b1_forecast(panel, index, row_flags, registry=registry, decision_time=decision_time)
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
    return FlagWalk(forecasts, fit_used, fits, tuple(skipped), anchor_flag)
