"""The benchmarks of scoring protocol v1, section 4 (#655).

`docs/decisions/scoring-protocol.md` §4 fixes three benchmarks, each forecasting the 23
quantiles of `scoring_protocol.GRID` at leads h = 1..5, made at the decision instant of
`docs/decisions/information-set.md`:

- **B1, as-of persistence.** The last public spread, plus the empirical distribution of
  that horizon's own h-day changes over the trailing two years.
- **B2, calendar climatology.** The empirical distribution of the spread over the trailing
  year, on days of the same type as the target (quarter-end, month-end, tax date, ordinary).
- **B4, a plain quantile regression (#1360)** on the last spread, the as-of reserve balances and the calendar terms at the target day: `b4_forecast`.
  Added at Eleonora's ruling of 2 November 2026 beside the benchmarks of §4; whether it joins the decision rule is hers (a marked question), and until
  she rules it is reported beside them.
- **B3, the incumbent.** The best registered model; initially the published v1 funding
  declaration. Scored on its own five levels against the candidate's same five, as a
  secondary comparison (`b3_forecast`; ruling of 13 October 2026, PR #660).

**B1* (#1388, development tier, not a benchmark of the protocol).** `b1_anchor_forecast` counts the change from the last public
anchor to the target, `h + lag` rows (`anchor_lag`), where B1 counts `h`; `b1_calendar.b1_calendar_anchor_forecast` is B1'*. Whether
they replace B1 and B1' is Eleonora's.

**B1'*-cap and B2*-cap (#1421, development tier; her ruling of 3 November 2026).** The candidate is capped at the Standing Repo Facility line on
target days at full allotment, so the confirmatory baselines carry the same cap: `capped_forecast` clips each quantile of a baseline at the line the
candidate reads (`s3c_candidate.cap_line`: the register entries public at the decision instant, margin 0 bp) and reads the probabilities under the same
rule (b) (`capped_exceedance`, `capped_law` rule `open_tail`). `b1_calendar_anchor_capped_forecast` is B1'*-cap and `b2_star_capped_forecast` is
B2*-cap (#1440, the finding of #1434): `b2_star_forecast` clipped at the same line. #1422 had capped plain B2 in B2*'s place before B2* was on main; that
stand-in is gone, and the re-run is `docs/research/capped-baselines-b2star-1434-result.md`. The uncapped versions are reported beside the capped ones;
nothing here changes B1, B2 or B3.

**What is read, and when.** The decision for lead h on decision row `t` is the forecast of row
`t + h` under `InformationRule(horizon=h)`, so every lead of one decision day shares one
decision instant and one anchor: the latest row whose spread was public at it. Both guards of
that rule run (`InformationRule.check`): nothing newer than the decision instant
(`LookAheadError`), nothing older than the latest public value (`StaleReadError`). B1 reads
the anchor's spread. Every row B1 and B2 draw their distribution from is at or before the
anchor, which `_require_public` restates for the rows actually read.

**Reading choices this module makes** are listed, with the alternatives, as questions in the
pull request that closes #655; none is a decision. They are: the trailing windows are counted
in calendar years back from the decision day, and clipped at the start of the panel; B1's
changes span h rows, as §4 says, although its last public value is one row older than the
decision day; B2's day type is `SplitDeclaration.reporting_day_type` (month-end on the market
calendar), read from each row's own calendar columns; empirical quantiles are linearly
interpolated (`empirical_quantiles`).

Stdlib only.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import turn_days
from .asof import InformationRule
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import GRID, HORIZONS, ProtocolError
from .splits import LookAheadError

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "_anchor": (
        "not_entry",
        "reads the last public row for a benchmark forecast of protocol v1 (#655); makes a "
        "forecast, scores nothing: the forecast is scored only through scoring_protocol.day_scores, "
        "which calls require_unlocked on every scored day",
    ),
}

#: §4: B1's trailing window and B2's, in years before the decision day.
B1_YEARS = 2
B2_YEARS = 1

#: B2* (#1420, development tier; `metadata/b2_star_1420.json`): B2's day types and fallback chain with a two-year lookback and a minimum pool of 10.
B2STAR_YEARS = 2
B2STAR_POOL_MIN = 10

ROOT = Path(__file__).resolve().parents[2]
#: §4: "initially, the published v1 funding declaration". Its record, and the daily
#: forecasts of it that `docs/runs/published_distribution_daily_h*.json` reproduce.
INCUMBENT_RECORD = "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
INCUMBENT_DAILY = "docs/runs/published_distribution_daily_h1.json"


def years_before(day: date, years: int) -> date:
    """`day` less `years` calendar years; 29 February falls back to the 28th."""

    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day.replace(year=day.year - years, day=28)


def empirical_quantiles(ordered: Sequence[float], shift: float = 0.0) -> List[float]:
    """`shift` plus the linearly interpolated quantiles of `ordered` at every level of `GRID`.

    Interpolated as `low + w * (high - low)`, which, unlike `low * (1 - w) + high * w`, is
    exactly `low` between two equal values. Rounding is monotone, so the quantiles never
    cross, and the scorer, which refuses a crossing, accepts them.
    """

    if not ordered:
        raise ProtocolError("an empirical distribution needs at least one value")
    out = []
    for level in GRID:
        position = level * (len(ordered) - 1)
        low = int(position)
        weight = position - low
        value = ordered[low]
        if weight:
            value = value + weight * (ordered[low + 1] - value)
        out.append(shift + value)
    return out


def _require_public(rows: Iterable[int], anchor: int, dates: Sequence[date], where: str) -> None:
    """Every row a benchmark draws on is at or before the anchor, the last public row.

    Mutation record: replacing `if row > anchor:` with `if row > anchor + 1:` makes
    `test_protocol_benchmarks.GuardTests.test_a_row_past_the_anchor_is_refused` fail with
    `AssertionError` ("LookAheadError not raised"); restored, it passes.

    Raises:
        LookAheadError: naming the first row read after the anchor.
    """

    for row in sorted(rows):
        if row > anchor:
            raise LookAheadError(
                f"{where} reads {dates[row]}, after {dates[anchor]}, the last row public "
                f"at the decision instant"
            )


def _anchor(
    panel: Sequence[DailyObservation],
    decision_index: int,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> int:
    """The anchor of the decision on row `decision_index`, the same for every lead.

    Each lead's rule is checked in both directions, and the anchors are required to agree:
    they share one decision instant.
    """

    dates = [row.date for row in panel]
    anchors = set()
    for h in HORIZONS:
        scored = decision_index + h
        if scored >= len(panel):
            raise ProtocolError(
                f"lead {h} from {dates[decision_index]} has no row in the panel; the panel must "
                f"carry the target rows (their calendar columns, at least)"
            )
        rule = InformationRule(registry, (), decision_time=decision_time, horizon=h)
        info = rule.information_set(dates, scored)
        rule.check(dates, info)
        anchors.add(info.anchor)
    if len(anchors) != 1:
        raise ProtocolError(f"the leads of {dates[decision_index]} disagree on the last public row")
    return anchors.pop()


def _window_start(panel: Sequence[DailyObservation], decision_index: int, years: int) -> int:
    """The first row strictly after the decision day less `years` years."""

    start = years_before(panel[decision_index].date, years)
    for index, row in enumerate(panel):
        if row.date > start:
            return index
    raise ProtocolError(f"no row after {start}")


def anchor_lag(
    panel: Sequence[DailyObservation],
    decision_index: int,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> int:
    """The lag of the decision on row `decision_index`, in panel rows: the decision row less the anchor row (#1388).

    The anchor is the last public row, so on an ordinary day it is the row before the decision day (a lag of 1) and the
    elapsed horizon from the anchor to the target row `decision_index + h` is `h + lag`. B1* and B1'* count the change
    over that span; B1 and B1' count `h`.
    """

    return decision_index - _anchor(panel, decision_index, registry, decision_time)


def b1_anchor_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> Dict[int, List[float]]:
    """B1*: B1 with the change window anchor-to-target (#1388; development tier, `metadata/b1_anchor_horizon_1388.json`).

    The last public spread plus the trailing two years' changes over `h + lag` rows, `spread[s] - spread[s - h - lag]` for every
    row `s` in the window up to the anchor, where `lag` is `anchor_lag`. Everything else is B1's: the window, the centre and the
    guard. It is not a benchmark of the protocol; whether it replaces B1 is Eleonora's.

    Mutation record: see `tests/test_b1_anchor_horizon_1388.py`.
    """

    anchor = _anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    dates = [row.date for row in panel]
    first = _window_start(panel, decision_index, B1_YEARS)
    last = panel[anchor].spread_bps
    out = {}
    for h in HORIZONS:
        span = h + lag
        ends = [s for s in range(max(first, span), anchor + 1)]
        if not ends:
            raise ProtocolError(f"B1* has no {span}-day change before {dates[anchor]}")
        _require_public(ends, anchor, dates, f"B1* for {dates[decision_index]}, lead {h}")
        changes = sorted(panel[s].spread_bps - panel[s - span].spread_bps for s in ends)
        out[h] = empirical_quantiles(changes, last)
    return out


def b1_calendar_anchor_forecast(panel: Sequence[DailyObservation], decision_index: int, **settings) -> Dict[int, List[float]]:
    """B1'*: `b1_calendar.b1_calendar_anchor_forecast`, reachable from here beside B1* (#1388)."""

    from . import b1_calendar  # b1_calendar imports this module

    return b1_calendar.b1_calendar_anchor_forecast(panel, decision_index, **settings)


def b1_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> Dict[int, List[float]]:
    """§4 B1: the last public spread plus the trailing two years' h-row changes, per lead.

    The changes are `spread[s] - spread[s - h]` for every row `s` in the window up to the
    anchor (`s - h` may fall before the window, never before the panel).
    """

    anchor = _anchor(panel, decision_index, registry, decision_time)
    dates = [row.date for row in panel]
    first = _window_start(panel, decision_index, B1_YEARS)
    last = panel[anchor].spread_bps
    out = {}
    for h in HORIZONS:
        ends = [s for s in range(max(first, h), anchor + 1)]
        if not ends:
            raise ProtocolError(f"B1 has no {h}-day change before {dates[anchor]}")
        _require_public(ends, anchor, dates, f"B1 for {dates[decision_index]}, lead {h}")
        changes = sorted(panel[s].spread_bps - panel[s - h].spread_bps for s in ends)
        out[h] = empirical_quantiles(changes, last)
    return out


def b2_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> Dict[int, List[float]]:
    """§4 B2: the trailing year's spreads on days of the target's type, per lead, with the thin-pool fallback.

    While the record `docs/decisions/b2-thin-pool.md` is in force (`b2_pool.IN_FORCE`, #1155, put in force by #1198) a
    target whose type has fewer than `b2_pool.POOL_MIN` rows in the trailing year reads the next step of its declared chain
    (`b2_pool.CHAINS`), and a first year-end is forecast instead of refused. Otherwise it is `b2_forecast_no_minimum`.
    """

    from . import b2_pool  # b2_pool imports this module

    if b2_pool.IN_FORCE:
        return b2_pool.b2_fallback_forecast(
            panel, decision_index, registry=registry, decision_time=decision_time, splits=splits,
            pool_min=b2_pool.POOL_MIN,
        )
    return b2_forecast_no_minimum(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits)


def b2_forecast_no_minimum(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> Dict[int, List[float]]:
    """§4 B2 as it stood before #1155 was in force: the trailing year's spreads on days of the target's type, per lead.

    No minimum pool: a type with no row in the window raises `ProtocolError`. The target's type is read from its own
    calendar columns, which are known in advance; every sampled row's from its own.
    """

    anchor = _anchor(panel, decision_index, registry, decision_time)
    dates = [row.date for row in panel]
    first = _window_start(panel, decision_index, B2_YEARS)
    kinds = {
        s: turn_days.reporting_day_type(splits, panel[s].date, panel[s].values) for s in range(first, anchor + 1)
    }
    out = {}
    for h in HORIZONS:
        target = panel[decision_index + h]
        kind = turn_days.reporting_day_type(splits, target.date, target.values)
        rows = [s for s, value in kinds.items() if value == kind]
        if not rows:
            raise ProtocolError(
                f"B2 has no {kind} day in the year before {dates[decision_index]} to forecast "
                f"{target.date} from"
            )
        _require_public(rows, anchor, dates, f"B2 for {dates[decision_index]}, lead {h}")
        sample = sorted(panel[s].spread_bps for s in rows)
        out[h] = empirical_quantiles(sample)
    return out


def b2_star_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    used: Optional[Dict[int, Tuple[str, int]]] = None,
) -> Dict[int, List[float]]:
    """B2* (#1420): the calendar climatology with its pools, lookback and fallback frozen in `metadata/b2_star_1420.json`.

    The pools are the day types of the record in force (`turn_days`); the lookback is `B2STAR_YEARS` (two) calendar years before the decision
    day, clipped at the start of the panel; a type with fewer than `B2STAR_POOL_MIN` (10) rows in it reads the next step of its chain
    (`b2_pool.CHAINS`, hard fallback, no shrinkage), else every day of the window. At the same decision instant and under the same guards as B2
    (`_anchor`, `_require_public`). `used`, when given, is filled with `{lead: (pool, rows)}`. A development-tier benchmark: whether it enters
    the protocol's decision rule is Eleonora's, and B2 (`b2_forecast`) is unchanged.
    """

    from . import b2_pool  # b2_pool imports this module

    return b2_pool.b2_fallback_forecast(
        panel, decision_index, registry=registry, decision_time=decision_time, splits=splits,
        pool_min=B2STAR_POOL_MIN, years=B2STAR_YEARS, used=used,
    )


def b4_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: Optional[SplitDeclaration] = None,
    table=None,
    reserves=None,
) -> Dict[int, List[float]]:
    """B4, the plain quantile regression of #1360, for the decision on row `decision_index`: the 23 quantiles at each lead h = 1..5.

    A linear quantile regression per lead and level on the last observed spread, the as-of reserve balances and the calendar terms read at the target day,
    on direct pairs of the expanding window, refitted at this decision (`repo_model.b4_quantile_regression`; `metadata/b4_quantile_regression_1360.json`). The
    walk of the study refits every 21 decision days instead, as the candidate does. `table` (a `spread_mr_calendar.TermTable`) and `reserves` (a
    `b4_quantile_regression.ReserveTable`) are built here when not given; a caller that scores many days builds them once. `splits` is accepted so that B4 is
    called as B2 is, and is not read.

    Whether B4 is a benchmark of the protocol's decision rule, or is reported beside it, is not decided here (the marked question of the pull request that
    closes #1360): this function only makes the forecast available to the registration and the live record.

    Raises:
        InsufficientHistory: fewer than `b4_quantile_regression.MIN_PAIRS` training pairs at some lead.
        LookAheadError: a row after the anchor, or a reserve value after the decision, is read.
    """

    from . import b4_quantile_regression as b4  # b4 imports this module
    from . import spread_mr_calendar as cal

    table = cal.TermTable(panel, (), decision_time=decision_time) if table is None else table
    reserves = b4.ReserveTable(panel, registry=registry, decision_time=decision_time) if reserves is None else reserves
    estimates = b4.refit(panel, decision_index, table, reserves, registry=registry, decision_time=decision_time)
    return b4.forecast(panel, decision_index, estimates, table, reserves, registry=registry, decision_time=decision_time)


def capped_forecast(
    forecast: Mapping[int, Sequence[float]],
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    register,
    decision_time: time,
) -> Dict[int, List[float]]:
    """`forecast` (a baseline's 23 quantiles per lead) with every quantile clipped at the SRF line, as the candidate (s3c) reads it (#1421).

    The line for lead h is `s3c_candidate.cap_line` on the target `panel[decision_index + h]`, from the register entries announced at or before the decision
    instant (`decision_time` on the decision day, `panel[decision_index]`) and effective by the target: the candidate's cap, margin 0 bp, at full allotment
    only. Where the target has no line the lead is copied unchanged. The clip is monotone, so the levels stay ordered. Fits nothing.

    Raises:
        ProtocolError: a lead has no target row in the panel.
        LookAheadError: a register entry announced after the decision instant is read (`policy_events.require_announced`).
    """

    from . import s3c_candidate  # s3c_candidate imports nothing from here; the import is lazy to keep this module's imports as they were

    as_of = datetime.combine(panel[decision_index].date, decision_time)
    out = {}
    for h, quantiles in forecast.items():
        if decision_index + h >= len(panel):
            raise ProtocolError(f"lead {h} from {panel[decision_index].date} has no row in the panel")
        out[h] = s3c_candidate.capped_quantiles(quantiles, register, as_of, panel[decision_index + h].date)
    return out


def capped_exceedance(
    forecast: Mapping[int, Sequence[float]],
    panel: Sequence[DailyObservation],
    decision_index: int,
    h: int,
    tau: float,
    *,
    register,
    decision_time: time,
) -> float:
    """P(spread > tau) at lead `h` of a baseline's UNCAPPED `forecast` under the candidate's law: the cap and rule (b), `capped_law` `open_tail` (#1421).

    Where the target has no line the law is the status-quo law of the uncapped vector, which is what rule (b) gives with no cap.
    """

    from . import s3c_candidate

    as_of = datetime.combine(panel[decision_index].date, decision_time)
    return s3c_candidate.candidate_exceedance(forecast[h], register, as_of, panel[decision_index + h].date, tau)


def b1_calendar_anchor_capped_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    register,
) -> Dict[int, List[float]]:
    """B1'*-cap (#1421): B1'* (`b1_calendar_anchor_forecast`) clipped at the SRF line of the candidate, `capped_forecast`."""

    raw = b1_calendar_anchor_forecast(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits)
    return capped_forecast(raw, panel, decision_index, register=register, decision_time=decision_time)


def b2_star_capped_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    register,
) -> Dict[int, List[float]]:
    """B2*-cap (#1440): B2* (`b2_star_forecast`, #1420) clipped at the SRF line of the candidate, `capped_forecast`, the rule of B1'*-cap."""

    raw = b2_star_forecast(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits)
    return capped_forecast(raw, panel, decision_index, register=register, decision_time=decision_time)


def forecasts(
    benchmark,
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    **settings,
) -> Dict[date, Dict[int, List[float]]]:
    """`benchmark` (`b1_forecast` or `b2_forecast`) on each of `decision_days`."""

    position = {row.date: index for index, row in enumerate(panel)}
    out = {}
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        out[day] = benchmark(panel, position[day], **settings)
    return out


def incumbent() -> Dict[str, object]:
    """§4 B3: which declaration is the incumbent, and the levels it forecasts at."""

    daily = json.loads((ROOT / INCUMBENT_DAILY).read_text(encoding="utf-8"))
    return {
        "record": INCUMBENT_RECORD,
        "daily": INCUMBENT_DAILY,
        "published_declaration_sha256": daily["published_declaration_sha256"],
        "levels": tuple(float(level) for level in daily["levels"]),
    }


def b3_forecast(levels: Sequence[float], forecast: Mapping[int, Sequence[float]]) -> Dict[int, List[float]]:
    """§4 B3: the incumbent's forecast for one decision day, on the incumbent's own levels.

    Eleonora's ruling of 13 October 2026 (PR #660): the published v1 declaration forecasts five
    levels (0.05, 0.25, 0.5, 0.75, 0.95), and B3 is scored on those five against each candidate
    read at the same five (`scoring_protocol.on_levels`, `scoring_protocol.level_crps`), as a
    secondary comparison. B1 and B2 stay the primary benchmarks on the 23-level grid.

    Raises:
        ProtocolError: a level is not on `GRID`, a lead carries the wrong number of
            quantiles, or a lead is missing.
    """

    grid = tuple(float(level) for level in levels)
    for level in grid:
        if level not in GRID:
            raise ProtocolError(f"the incumbent's level {level} is not on the protocol's grid")
    if set(forecast) != set(HORIZONS):
        raise ProtocolError(f"the incumbent's forecast carries leads {sorted(forecast)}")
    out = {}
    for h in HORIZONS:
        values = [float(value) for value in forecast[h]]
        if len(values) != len(grid):
            raise ProtocolError(f"the incumbent's lead-{h} forecast has {len(values)} quantiles, not {len(grid)}")
        out[h] = values
    return out
