"""The benchmarks of scoring protocol v1, section 4 (#655).

`docs/decisions/scoring-protocol.md` §4 fixes three benchmarks, each forecasting the 23
quantiles of `scoring_protocol.GRID` at leads h = 1..5, made at the decision instant of
`docs/decisions/information-set.md`:

- **B1, as-of persistence.** The last public spread, plus the empirical distribution of
  that horizon's own h-day changes over the trailing two years.
- **B2, calendar climatology.** The empirical distribution of the spread over the trailing
  year, on days of the same type as the target (quarter-end, month-end, tax date, ordinary).
- **B3, the incumbent.** The best registered model; initially the published v1 funding
  declaration. Scored on its own five levels against the candidate's same five, as a
  secondary comparison (`b3_forecast`; ruling of 13 October 2026, PR #660).

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
from datetime import date, time
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

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
