#!/usr/bin/env python3
"""Desk outputs (#232): what the published model says on a scheduled pressure day.

Eleonora's ruling on #232 ("I want Nicholas's outputs"). Four outputs, read
from the published model and the panel. **Reporting, not a model variant**: the
frozen model, its declaration and the live record's file schema do not change,
and nothing here writes into `docs/runs/`.

1. **The pressure probability**, P(spread > +5 bp) and P(spread > +10 bp), as
   pressure model v1 produces it at h = 1 to 5. In the history it is the
   published records `docs/runs/pressure_model_v1_hH.json`; live, each day's
   file carries it.
2. **The spread's quantile grid on scheduled pressure days** at h = 1 to 5:
   the published distribution's (`live_record.published_distribution_record`)
   on each day tagged by `pressure_day_tags`, its realised 90% coverage
   against as-of persistence's, and the paired CRPS difference, each with a
   stationary-bootstrap interval, split by tag, regime and scarcity state. The
   upper tail is stated plainly (`upper_tail_statement`).
3. **The turn's expected contribution to the period average**
   (`turn_contribution`): the day's forecast mean (`mean_from_quantiles`)
   times the calendar days of its month it carries
   (`calendar_days_carried`), over the calendar days in the month, as SOFR
   averages are computed. Eleonora ruled on both on PR #241 (Q2: the period;
   Q3: the mean rule, kept; shown with `MEAN_LABEL` and the measured
   bias `mean_bias_label`, as ruled on #269 item 11).
4. **The reserve-scarcity state** (#115, `repo_model.scarcity`) beside every
   forecast, read as of the forecast's decision instant (`scarcity_at`), with
   its ON RRP leg as "buffer present" or "buffer gone". It is not an input to
   any model and stays off in every published declaration.

Wherever the published distribution's 25th-75th percentile band is shown, it
carries `BAND_25_75_LABEL` (Eleonora's ruling on PR #241, #243): that band is
not calibrated. The 5-95 band is shown unlabelled except on a quarter-end, year-end
or tax date, where it carries `band_5_95_label`: its realised coverage on that day type
is below nominal and its misses fall above q95, read from the published record (#266).

The history replays the published distribution and as-of persistence exactly
as the live record runs them (`live_record._compare_sides`, the fold loop of
`live_record.distribution_run`), but keeps every fold's quantile vector
instead of the last one. At h = 1 its CRPS reproduces the published
comparison record's per-day losses, which `history` checks before it writes.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/desk_outputs.py history \\
        --panel PUB.csv --horizon H --output OUT/hH.json          # H = 1 .. 5
    PYTHONPATH=src python3 scripts/desk_outputs.py tables --runs OUT \\
        --first 2018-01-01 --last 2025-12-31 --json OUT/tables.json --markdown OUT/tables.md
    PYTHONPATH=src python3 scripts/desk_outputs.py live --live-dir DIR \\
        --measurement-panel MEASUREMENT.csv --output OUT/live.json

`history` scores through the end of the panel, 2026-09-03; the near-blind
tier is opened (#151, `metadata/lockbox.json`), and `require_history_unlocked`
refuses any day in a tier that is not. `tables --last 2025-12-31` gives the
pre-2026 history; `--first 2026-01-01` the opened 2026 window, reported apart.
`live` reads each frozen `live/YYYY-MM-DD.json` and a measurement panel built at
report time with `on_rrp` and `bank_total_assets` switched on
(`scripts/scarcity_validation.py`'s build); it changes no live file.

Stdlib only, except `history`, which fits the gbm (`ml` extra).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import tempfile
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _script(name):
    spec = importlib.util.spec_from_file_location(f"desk_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: The live record's code path: the published distribution and as-of
#: persistence at each horizon, built as `compare` builds them.
live = _script("live_record")

from repo_model import scarcity  # noqa: E402
from repo_model.asof import (  # noqa: E402
    InformationRule,
    StaleReadError,
    fold_grid,
    refit_blocks,
    require_refit_every,
)
from repo_model.baseline import (  # noqa: E402
    _AsOfFold,
    _at_decision,
    _check_decision_relative_availability,
    _check_fitter_stayed_inside,
    _fit_at_origin,
    _model_settings,
    _reads_information,
    _resolve_fields,
    _with_online_settings,
)
from repo_model.contract import QUANTILE_LEVELS  # noqa: E402
from repo_model.data import (  # noqa: E402
    CALENDAR_COLUMN_RULES,
    ON_RRP_MAX_GAP_DAYS,
    DailyObservation,
    market_holidays,
)
from repo_model.evaluation_splits import DAY_TYPES, load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402
from repo_model.metrics import MetricError, crps_from_quantiles, stationary_bootstrap_interval  # noqa: E402
from repo_model.onset import MINIMUM_EVENTS  # noqa: E402

DECISION = live.DECISION
HORIZONS = live.HORIZONS
REGISTRY = REPO / "metadata" / "sources.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
CRPS_RECORD = REPO / live.CRPS_RECORD

#: The scheduled pressure days, as tags a day may carry several of. Each is
#: read from the repository's own calendar columns: `month_end` is the split
#: declaration's window (`days_to_month_end` at most its
#: `month_end_days_to_month_end_at_most`), `quarter_end` the last business day
#: of a quarter, `year_end` the December one, `tax_date` the corporate tax
#: window, and `coupon_settlement` a day with a Treasury coupon settlement.
PRESSURE_DAY_TAGS = ("month_end", "quarter_end", "year_end", "tax_date", "coupon_settlement")

#: The rule `mean_from_quantiles` states (kept by Eleonora's ruling on PR #241, Q3).
MEAN_RULE = (
    "the mean of the piecewise-linear quantile function through the grid's "
    "points, held flat beyond the outer levels"
)
#: The label wherever the expected value or the turn contribution is shown: the
#: mean is computed from the interior quantiles, which are not calibrated
#: (Eleonora's ruling on #269 item 11, replacing the causal sentence of the
#: ruling on PR #241, Q3). The measured bias is `mean_bias_label`.
MEAN_LABEL = "not yet calibrated (#243): computed from the uncalibrated interior quantiles"
#: The period `turn_contribution` states (Eleonora's ruling on PR #241, Q2).
PERIOD_RULE = (
    "the day's calendar month, weighted by calendar day as SOFR averages are "
    "computed: a weekend or holiday (market holiday table) carries the previous "
    "business day's rate; carried days in the next month count in that month's average"
)
#: The label beside the published distribution's 25-75 band (ruling on PR #241, #243).
BAND_25_75_LABEL = "not yet calibrated (#243)"

#: The published record whose coverage by day type the 5-95 band's label reads (#266).
INTERIOR_RECORD = REPO / "docs" / "runs" / "v1_interior_diagnosis.json"
#: The tags whose 5-95 band is labelled, and the exclusive day type whose recorded
#: coverage each reads: a year-end is a December quarter-end.
BAND_5_95_TURN_TAGS = {"quarter_end": "quarter_end", "year_end": "quarter_end", "tax_date": "tax_date"}

#: The fewest days a cell may have and still carry an interval. A cell below it
#: shows its mean and "too few days": whether a 4-8 day cell got an interval
#: used to depend on the bootstrap seed (#266). The count is the minimum the
#: final test's pages use (`onset.MINIMUM_EVENTS`), taken as the project's
#: until Eleonora rules a project-wide minimum for cells of days.
MINIMUM_CELL_DAYS = MINIMUM_EVENTS

#: The oldest a measurement panel's last row may be, in calendar days before the
#: decision day, when `live` reads the scarcity state: the declared maximum gap of
#: the daily carry column (`data.ON_RRP_MAX_GAP_DAYS`, a Friday to the Tuesday
#: after a Monday holiday). A longer gap is a panel that ended early.
STALE_PANEL_DAYS = ON_RRP_MAX_GAP_DAYS

#: The interval's settings: the project's level and replications, the stationary
#: bootstrap, and a mean block of h + 1 days -- overlapping h-step errors share
#: innovations, and at h = 1 that is the published comparison's block of 2.
BOOTSTRAP_LEVEL = 0.90
BOOTSTRAP_REPLICATIONS = 2000
NOMINAL_COVERAGE = QUANTILE_LEVELS[-1] - QUANTILE_LEVELS[0]

BUFFER_LABELS = {0: "buffer present", 1: "buffer gone"}


# -- output 3: the mean and the period ----------------------------------------


def _checked_grid(levels: Sequence[float], quantiles: Sequence[float]) -> Tuple[tuple, tuple]:
    grid = tuple(float(level) for level in levels)
    values = tuple(float(value) for value in quantiles)
    if len(grid) < 2 or len(grid) != len(values):
        raise ValueError(f"{len(grid)} levels against {len(values)} quantiles")
    if not all(0.0 < a < b < 1.0 for a, b in zip(grid, grid[1:])):
        raise ValueError(f"levels must ascend strictly inside (0, 1), got {grid}")
    if any(b < a for a, b in zip(values, values[1:])):
        raise ValueError(f"quantiles cross: {values}")
    return grid, values


def mean_weights(levels: Sequence[float]) -> Tuple[float, ...]:
    """Each quantile's weight in the mean under `MEAN_RULE`.

    The quantile function is linear between adjacent levels and flat beyond the
    outer ones, so its integral over (0, 1) is a weighted sum of the grid's
    values: the lowest level's value carries the mass below it plus half the
    first interval, each inner value half of each interval beside it, and the
    highest the mass above it plus half the last interval. On the contract's
    grid (0.05, 0.25, 0.5, 0.75, 0.95) that is 0.15, 0.225, 0.25, 0.225, 0.15.
    """

    grid, _ = _checked_grid(levels, levels)
    weights = []
    for position, level in enumerate(grid):
        below = level if position == 0 else (level - grid[position - 1]) / 2.0
        above = 1.0 - level if position == len(grid) - 1 else (grid[position + 1] - level) / 2.0
        weights.append(below + above)
    return tuple(weights)


def mean_from_quantiles(levels: Sequence[float], quantiles: Sequence[float]) -> float:
    """The forecast's mean spread, in bp, from its quantile grid (`MEAN_RULE`).

    Raises:
        ValueError: on a grid whose levels and values differ in length, whose
            levels do not ascend inside (0, 1), or whose quantiles cross.
    """

    grid, values = _checked_grid(levels, quantiles)
    return sum(weight * value for weight, value in zip(mean_weights(grid), values))


def _month(day: date) -> Tuple[date, date]:
    """`day`'s calendar month as (first day, first day of the next month)."""

    first = day.replace(day=1)
    return first, (first + timedelta(days=32)).replace(day=1)


def calendar_days_in_month(day: date) -> int:
    first, following = _month(day)
    return (following - first).days


def calendar_days_carried(day: date) -> int:
    """The calendar days of `day`'s month that carry its rate (`PERIOD_RULE`).

    The day itself and every following weekend day or market holiday up to the
    next business day, counted inside the day's month only: a carried day in
    the next month counts in that month's average, as SOFR averages are
    computed. A Friday whose weekend lies inside its month counts three days.

    Raises:
        ValueError: if `metadata/market_holidays.json` does not cover the month,
            or `day` is not a business day (it carries no rate of its own).
    """

    table = market_holidays()
    first, following = _month(day)
    if not (table.first <= first and following - timedelta(days=1) <= table.last):
        raise ValueError(
            f"{first:%Y-%m} is outside metadata/market_holidays.json ({table.first} to {table.last})"
        )

    def business(when: date) -> bool:
        return when.weekday() < 5 and when not in table.closed

    if not business(day):
        raise ValueError(f"{day} is not a business day in metadata/market_holidays.json")
    count, current = 1, day + timedelta(days=1)
    while current < following and not business(current):
        count += 1
        current += timedelta(days=1)
    return count


def turn_contribution(mean_bps: float, day: date) -> float:
    """The day's expected contribution to its month's average spread, in bp.

    The mean times the calendar days it carries, over the calendar days in the
    month (`PERIOD_RULE`).
    """

    return float(mean_bps) * calendar_days_carried(day) / calendar_days_in_month(day)


# -- output 2: the pressure days and the tail --------------------------------


def coupon_settlement_known(values: Mapping[str, Optional[float]]) -> Optional[bool]:
    """Whether the day settles Treasury coupons; `None` when the row does not say."""

    value = values.get("treasury_settlement_coupons")
    if value is None:
        return None
    return float(value) > 0.0


def pressure_day_tags(values: Mapping[str, Optional[float]], day: date, splits) -> Tuple[str, ...]:
    """The scheduled pressure-day tags of a day, in `PRESSURE_DAY_TAGS` order.

    Read from the row's own calendar columns and the split declaration's
    month-end window. A settlement the row does not carry tags nothing.

    Raises:
        ValueError: if a calendar column is absent; a calendar column is
            always known, so a hole is a data error.
    """

    read = {}
    for column in ("days_to_month_end", "quarter_end", "tax_date"):
        value = values.get(column)
        if value is None:
            raise ValueError(f"the row for {day} carries no {column!r}")
        read[column] = float(value)
    tags = []
    if read["days_to_month_end"] <= splits.month_end_window:
        tags.append("month_end")
    if read["quarter_end"] == 1.0:
        tags.append("quarter_end")
        if day.month == 12:
            tags.append("year_end")
    if read["tax_date"] == 1.0:
        tags.append("tax_date")
    if coupon_settlement_known(values):
        tags.append("coupon_settlement")
    return tuple(tags)


def calendar_values(day: date) -> Dict[str, float]:
    """A day's calendar columns, from their rules (`data.CALENDAR_COLUMN_RULES`)."""

    return {
        column: CALENDAR_COLUMN_RULES[column](day)
        for column in ("days_to_month_end", "quarter_end", "tax_date")
    }


def band_5_95_label(tags: Sequence[str], horizon: int) -> Optional[str]:
    """The 5-95 band's label on a quarter-end, year-end or tax date, else `None`.

    The band is shown unlabelled on other days. On a turn day its realised
    coverage is below nominal, and the misses fall above q95. Every figure is
    read from the published record (`INTERIOR_RECORD`, 2018-2025, the
    repository's exclusive day type at `horizon`), never typed here (#266).
    """

    turn = [tag for tag in BAND_5_95_TURN_TAGS if tag in tags]
    if not turn:
        return None
    cells = json.loads(INTERIOR_RECORD.read_text(encoding="utf-8"))["q1_calibration"][
        f"h{horizon}_2018_2025"]["splits"]["by_day_type"]
    parts = []
    for tag in turn:
        day_type = BAND_5_95_TURN_TAGS[tag]
        cell = cells[day_type]
        above = 100.0 - cell["coverage_half_tie"]["0.95"]
        below = cell["coverage_half_tie"]["0.05"]
        read = f"read from {day_type.replace('_', '-')} days" if tag != day_type else ""
        parts.append(
            f"{tag.replace('_', '-')} 5-95 band, h = {horizon}: realised coverage "
            f"{cell['band_90_half_edge']:.1f}% of {cell['days']} days, below the nominal "
            f"{NOMINAL_COVERAGE:.0%}; misses {above:.1f}% of days above q95, {below:.1f}% below q05"
            + (f" ({read})" if read else "")
        )
    return "; ".join(parts) + " (docs/runs/v1_interior_diagnosis.json, 2018-2025)"


@lru_cache(maxsize=None)
def mean_bias_label() -> str:
    """The published mean's measured bias on quarter-ends, read from the record at run time.

    The forecast mean (`mean_from_quantiles`) minus the outcome, on the
    quarter-end days of `INTERIOR_RECORD`'s per-day rows at h = 1, inside the
    record's diagnosis window only (its rows run on into the opened 2026 days,
    which this never reads), with the desk's stationary-bootstrap interval over
    every day of the window. Negative: the mean sits below what happened.
    """

    record = json.loads(INTERIOR_RECORD.read_text(encoding="utf-8"))
    first, last = (date.fromisoformat(day) for day in record["windows"]["diagnosis"])
    splits = load_split_declaration(SPLITS)
    labels, errors = [], []
    for when, outcome, grid in record["v1_h1_per_day"]:
        day = date.fromisoformat(when)
        if first <= day <= last:
            labels.append(splits.day_type(calendar_values(day)))
            errors.append(mean_from_quantiles(QUANTILE_LEVELS, grid) - float(outcome))
    cell = _cell(labels, errors, "quarter_end", horizon=1, name="mean_bias")
    if "interval" not in cell:
        raise ValueError(f"the quarter-end mean bias has no interval: {cell}")
    return (
        f"measured bias of the mean on quarter-ends, h = 1: forecast mean minus outcome "
        f"{cell['mean']:+.1f} bp (90% interval {cell['interval']['lower']:+.1f} to "
        f"{cell['interval']['upper']:+.1f}, {cell['count']} quarter-end days, "
        f"{first} to {last}; docs/runs/v1_interior_diagnosis.json)"
    )


def upper_tail_statement(levels: Sequence[float], quantiles: Sequence[float]) -> str:
    """The grid in a desk's words: the mean, labelled, and the chance above the top quantile."""

    grid, values = _checked_grid(levels, quantiles)
    return (
        f"expected {mean_from_quantiles(grid, values):+.1f} bp ({MEAN_LABEL}), "
        f"{1.0 - grid[-1]:.0%} chance above {values[-1]:+.1f} bp"
    )


# -- output 4: the scarcity state, as of the decision ------------------------


def scarcity_rule(registry: Mapping, *, horizon: int) -> InformationRule:
    """The as-of rule that reads the declared state at `horizon`.

    Call inside `scarcity.measurement_declaration()`: the state and its inputs
    are off in the published map.
    """

    return InformationRule(
        registry, ("spread_bps", scarcity.RESERVE_SCARCITY_STATE),
        decision_time=DECISION, horizon=horizon,
    )


def scarcity_from(rows: Sequence[DailyObservation], rule: InformationRule, dates, info) -> dict:
    """The state an information set reads, after both of the rule's guards.

    Raises:
        LookAheadError: a read is newer than the decision instant.
        StaleReadError: a read is older than the latest admissible row.
    """

    rule.check(dates, info)
    (read,) = [item for item in info.reads if item.feature == scarcity.RESERVE_SCARCITY_STATE]
    values = rows[read.row].values
    state = values.get(scarcity.RESERVE_SCARCITY_STATE)
    on_rrp = values.get("on_rrp")
    return {
        "decision_instant": info.decision_instant.isoformat(),
        "read_date": rows[read.row].date.isoformat(),
        "state": None if state is None else int(state),
        "label": None if state is None else scarcity.STATE_LABELS[int(state)],
        "on_rrp_bn": on_rrp,
        "buffer": None if on_rrp is None else BUFFER_LABELS[scarcity.buffer_level(on_rrp)],
    }


def scarcity_at(rows: Sequence[DailyObservation], rule: InformationRule, index: int) -> dict:
    """The declared state beside the forecast of `rows[index]`, read as of its decision.

    The state and its ON RRP leg come from one row, the latest whose reserves,
    bank assets and ON RRP were all public at the decision instant, so the
    buffer shown is the leg the score counts.
    """

    dates = [row.date for row in rows]
    return scarcity_from(rows, rule, dates, rule.information_set(dates, index))


# -- the history ----------------------------------------------------------------


def require_history_unlocked(days: Sequence[date]) -> None:
    """Refuse a day in a locked tier of `metadata/lockbox.json`, before any fit."""

    require_unlocked(days, where="desk_outputs.history")


def distribution_history(rows, h: int, registry, *, last: date) -> List[dict]:
    """Both distributions' quantile grids on every scored day through `last`, at `h`.

    `live_record.distribution_run`'s fold loop for each side -- the same grid,
    refit blocks, guards, fits, as-of views and online calibration, in the same
    order -- keeping every fold's vector. Each vector is drawn before its label
    is fed to the online calibration. The sides are checked against their
    published declarations (`live_record._require_crps_declaration`).
    """

    sides, args = live._compare_sides(h)
    dates = [row.date for row in rows]
    grid = fold_grid(
        dates, registry, decision_time=DECISION, minimum_history=args.minimum_history, horizon=h
    )
    scored = [index for index in grid if dates[index] <= last]
    require_history_unlocked([dates[index] for index in scored])
    out = {index: {"date": dates[index].isoformat(), "outcome_bps": rows[index].spread_bps}
           for index in scored}
    for side, (name, fit, features, online_calibration) in sides.items():
        declared = tuple(features)
        _field_sources, sources = _resolve_fields(declared)
        rule = InformationRule(registry, declared, decision_time=DECISION, horizon=h)
        refit = require_refit_every(args.refit_every)
        reads_information = _reads_information(fit)
        online = None if online_calibration is None else online_calibration(rows, rule)
        fitted, settings, checked = None, {}, False
        for indices in refit_blocks(grid, refit):
            if dates[indices[0]] > last:
                break
            for index in indices:
                if dates[index] > last:
                    break
                info = rule.information_set(dates, index)
                rule.check(dates, info)
                for read in info.reads:
                    _check_decision_relative_availability(
                        registry, read.fields, dates, read.row, index,
                        decision_time=DECISION, horizon=h,
                    )
                block_frame = rule.frame(rows, info) if index == indices[0] else None
                fold = _AsOfFold(index, info, block_frame, rule.observation(rows, info))
                if block_frame is not None:
                    fitted = _fit_at_origin(
                        fit, block_frame, minimum_history=args.minimum_history,
                        information=rule, reads_information=reads_information,
                    )
                    if not checked:
                        _check_fitter_stayed_inside(fitted.features_read, declared, sources)
                        settings = _with_online_settings(_model_settings(fitted), online)
                        checked = True
                view = _at_decision(fitted, rows, rule, fold)
                if online is not None:
                    view = online.view(view, index, fold.feature_row)
                if tuple(view.levels) != tuple(QUANTILE_LEVELS):
                    raise ValueError(f"the model reports quantile levels {tuple(view.levels)}")
                out[index][side] = [float(value) for value in view.predict(fold.feature_row)]
                if online is not None:
                    online.label(index, rows[index].spread_bps)
        live._require_crps_declaration(side, h, name, features, settings)
    return [out[index] for index in scored]


def check_against_published(days: Sequence[dict]) -> int:
    """At h = 1, each day's CRPS is the published comparison record's, both sides.

    Returns the number of days compared. Raises `ValueError` on any difference
    above 1e-9 bp, or on a published day the history does not carry.
    """

    record = json.loads(CRPS_RECORD.read_text(encoding="utf-8"))
    by_date = {day["date"]: day for day in days}
    compared = 0
    for origin in record["comparison"]["per_origin"]:
        day = by_date.get(origin["scored_date"])
        if day is None:
            raise ValueError(f"{origin['scored_date']} is in {CRPS_RECORD.name} but not the history")
        for side, key in (("persistence", "loss_a_bps"), ("published", "loss_b_bps")):
            got = crps_from_quantiles(QUANTILE_LEVELS, day[side], day["outcome_bps"])
            if abs(got - origin[key]) > 1e-9:
                raise ValueError(
                    f"{origin['scored_date']}: {side} CRPS {got} is not the record's {origin[key]}"
                )
        compared += 1
    return compared


def history_command(args) -> int:
    from repo_model.data import audit_panel, load_daily_panel

    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    days = distribution_history(rows, args.horizon, registry, last=args.last)
    compared = check_against_published(days) if args.horizon == 1 else None
    payload = {
        "horizon": args.horizon,
        "levels": list(QUANTILE_LEVELS),
        "published_record": live.published_distribution_record(args.horizon),
        "panel_sha256": hashlib.sha256(Path(args.panel).read_bytes()).hexdigest(),
        "reproduces_published_crps_days": compared,
        "days": days,
    }
    Path(args.output).write_text(json.dumps(payload) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("horizon", "published_record",
                                                     "reproduces_published_crps_days")}
                     | {"days": len(days)}))
    return 0


# -- the tables -----------------------------------------------------------------


def _seed(*parts) -> int:
    digest = hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big")


def _cell(labels, series, group, *, horizon, name):
    """`split_summary`'s cell for one group: its mean and domain bootstrap interval."""

    member = [label == group for label in labels]
    values = [float(value) for value in series]
    count = sum(member)
    cell = {"count": count}
    if not count:
        return cell
    cell["mean"] = sum(value for value, inside in zip(values, member) if inside) / count
    if count < MINIMUM_CELL_DAYS:
        cell["interval_unavailable"] = (
            f"too few days: {count}, fewer than the minimum of {MINIMUM_CELL_DAYS}"
        )
        return cell

    def statistic(indices):
        drawn = [values[i] for i in indices if member[i]]
        return sum(drawn) / len(drawn) if drawn else math.nan

    try:
        lower, upper = stationary_bootstrap_interval(
            statistic, len(values), block_length=horizon + 1,
            seed=_seed("desk_outputs", horizon, name, group),
            replications=BOOTSTRAP_REPLICATIONS, level=BOOTSTRAP_LEVEL,
        )
    except MetricError as exc:
        cell["interval_unavailable"] = str(exc)
    else:
        cell["interval"] = {"lower": lower, "upper": upper}
    return cell


def _covered(grid, outcome) -> float:
    return float(grid[0] <= outcome <= grid[-1])


def _series(days: Sequence[dict]) -> Dict[str, List[float]]:
    out = {name: [] for name in (
        "published_coverage", "persistence_coverage", "coverage_published_minus_persistence",
        "crps_persistence_minus_published", "turn_error_persistence_minus_published",
    )}
    for day in days:
        when = date.fromisoformat(day["date"])
        outcome = day["outcome_bps"]
        published, persistence = day["published"], day["persistence"]
        out["published_coverage"].append(_covered(published, outcome))
        out["persistence_coverage"].append(_covered(persistence, outcome))
        out["coverage_published_minus_persistence"].append(
            _covered(published, outcome) - _covered(persistence, outcome)
        )
        out["crps_persistence_minus_published"].append(
            crps_from_quantiles(QUANTILE_LEVELS, persistence, outcome)
            - crps_from_quantiles(QUANTILE_LEVELS, published, outcome)
        )
        realised = turn_contribution(outcome, when)
        out["turn_error_persistence_minus_published"].append(
            abs(turn_contribution(mean_from_quantiles(QUANTILE_LEVELS, persistence), when) - realised)
            - abs(turn_contribution(mean_from_quantiles(QUANTILE_LEVELS, published), when) - realised)
        )
    return out


#: The series a regime or state cell carries; a tag cell carries every series.
SPLIT_SERIES = ("published_coverage", "crps_persistence_minus_published")


def _group_cells(days, series, labels, group, *, horizon, name, keys=None):
    members = [day for day, label in zip(days, labels) if label == group]
    cell = {"days": len(members)}
    if not members:
        return cell
    for key, values in series.items():
        if keys is not None and key not in keys:
            continue
        cell[key] = _cell(labels, values, group, horizon=horizon, name=f"{name}|{key}")
    means = [mean_from_quantiles(QUANTILE_LEVELS, day["published"]) for day in members]
    cell["published_mean_bps"] = sum(means) / len(means)
    cell["published_q95_bps"] = sum(day["published"][-1] for day in members) / len(members)
    cell["realised_mean_bps"] = sum(day["outcome_bps"] for day in members) / len(members)
    cell["expected_turn_contribution_bps"] = sum(
        turn_contribution(mean, date.fromisoformat(day["date"])) for mean, day in zip(means, members)
    ) / len(members)
    cell["realised_turn_contribution_bps"] = sum(
        turn_contribution(day["outcome_bps"], date.fromisoformat(day["date"])) for day in members
    ) / len(members)
    return cell


def summarise(days: Sequence[dict], *, horizon: int, splits) -> dict:
    """Outputs 2 and 3 at one horizon: by tag, by tag and regime, by tag and state.

    Every interval is the domain stationary bootstrap over all of the
    horizon's scored days (`split_summary`), so a cell's resample keeps the
    calendar's dependence. Every comparison is paired against as-of
    persistence: coverage published minus persistence, CRPS persistence minus
    published, and the absolute error of the turn contribution persistence
    minus published (positive favours the published distribution). Also the
    repository's exclusive pressure-day types (`DAY_TYPES`) over every day.
    """

    days = list(days)
    series = _series(days)
    table = {"days": len(days), "by_tag": {}, "by_tag_and_regime": {}, "by_tag_and_state": {},
             "by_day_type": {}}
    for tag in PRESSURE_DAY_TAGS:
        labels = ["in" if tag in day["tags"] else "out" for day in days]
        table["by_tag"][tag] = _group_cells(days, series, labels, "in", horizon=horizon, name=tag)
        for key, field in (("by_tag_and_regime", "regime"), ("by_tag_and_state", "state")):
            labels = [str(day[field]) if tag in day["tags"] else "out" for day in days]
            groups = sorted({label for label in labels if label != "out"})
            table[key][tag] = {
                group: _group_cells(days, series, labels, group, horizon=horizon,
                                    name=f"{tag}|{field}", keys=SPLIT_SERIES)
                for group in groups
            }
    labels = [day["day_type"] if "day_type" in day else "ordinary" for day in days]
    for group in DAY_TYPES:
        table["by_day_type"][group] = _group_cells(
            days, series, labels, group, horizon=horizon, name="day_type",
            keys=SPLIT_SERIES + ("persistence_coverage",),
        )
    return table


def _measurement_rows():
    validation = _script("scarcity_validation")
    with tempfile.TemporaryDirectory() as directory:
        build, digest, _registry, _decision = validation.build_measurement_panel(
            REGISTRY, Path(directory)
        )
    return scarcity.with_reserve_scarcity_state(build.observations), digest


def annotate(history: dict, rows, registry, splits) -> List[dict]:
    """Each history day with its tags, day type, regime and as-of scarcity state."""

    h = history["horizon"]
    index_of = {row.date.isoformat(): position for position, row in enumerate(rows)}
    rule = scarcity_rule(registry, horizon=h)
    out = []
    for day in history["days"]:
        index = index_of[day["date"]]
        when = rows[index].date
        values = rows[index].values
        state = scarcity_at(rows, rule, index)
        out.append({
            **day,
            "tags": list(pressure_day_tags(values, when, splits)),
            "day_type": splits.day_type(values),
            "regime": splits.regime(when),
            "state": state["state"],
            "buffer": state["buffer"],
            "state_read_date": state["read_date"],
        })
    return out


def _fmt(cell, places=3):
    if not cell or "mean" not in cell:
        return "--"
    interval = cell.get("interval")
    if interval is None:
        return f"{cell['mean']:.{places}f} [too few days]"
    return f"{cell['mean']:.{places}f} [{interval['lower']:.{places}f}, {interval['upper']:.{places}f}]"


def _markdown(tables: dict, first: str, last: str) -> str:
    lines = [f"Scored days {first} to {last}. Intervals: stationary bootstrap over every scored "
             f"day of the horizon, mean block h + 1, {BOOTSTRAP_LEVEL:.0%}, "
             f"{BOOTSTRAP_REPLICATIONS} replications. Paired against as-of persistence; "
             "positive CRPS and turn-error differences favour the published distribution. "
             f"A cell of fewer than {MINIMUM_CELL_DAYS} days carries no interval (\"too few "
             "days\"): the final test's minimum count, applied to days until a project-wide "
             "minimum is ruled.", ""]
    lines.append("### By pressure-day tag")
    lines.append("")
    lines.append(f"† Mean and expected turn contribution: {MEAN_LABEL}; {mean_bias_label()}. "
                 "Turn contribution: calendar-day weighted, as SOFR averages are computed.")
    lines.append("")
    lines.append("| h | Tag | Days | Mean† / q95 / realised (bp) | Coverage published | "
                 "Coverage persistence | CRPS persistence − published | Turn contribution "
                 "expected† / realised (bp) | Turn |error| persistence − published |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for h, table in tables.items():
        for tag, cell in table["by_tag"].items():
            if not cell["days"]:
                lines.append(f"| {h} | {tag} | 0 | -- | -- | -- | -- | -- | -- |")
                continue
            lines.append(
                f"| {h} | {tag} | {cell['days']} | {cell['published_mean_bps']:+.2f} / "
                f"{cell['published_q95_bps']:+.2f} / {cell['realised_mean_bps']:+.2f} | "
                f"{_fmt(cell['published_coverage'])} | {_fmt(cell['persistence_coverage'])} | "
                f"{_fmt(cell['crps_persistence_minus_published'])} | "
                f"{cell['expected_turn_contribution_bps']:+.3f} / "
                f"{cell['realised_turn_contribution_bps']:+.3f} | "
                f"{_fmt(cell['turn_error_persistence_minus_published'], 4)} |"
            )
    for key, title in (("by_tag_and_regime", "regime"), ("by_tag_and_state", "scarcity state")):
        lines += ["", f"### By tag and {title}: CRPS persistence − published, and published coverage", ""]
        lines.append("| Tag | " + title.capitalize() + " | " + " | ".join(
            f"h={h} days, CRPS diff, coverage" for h in tables) + " |")
        lines.append("|---|---|" + "---|" * len(tables))
        first_table = next(iter(tables.values()))
        for tag in PRESSURE_DAY_TAGS:
            groups = sorted({group for table in tables.values() for group in table[key][tag]})
            for group in groups:
                label = group
                if key == "by_tag_and_state" and group != "None":
                    label = f"{group} {scarcity.STATE_LABELS[int(group)]}"
                parts = []
                for table in tables.values():
                    cell = table[key][tag].get(group, {"days": 0})
                    if not cell["days"]:
                        parts.append("0")
                        continue
                    parts.append(
                        f"{cell['days']}, {_fmt(cell['crps_persistence_minus_published'])}, "
                        f"{_fmt(cell['published_coverage'], 2)}"
                    )
                lines.append(f"| {tag} | {label} | " + " | ".join(parts) + " |")
        del first_table
    lines += ["", "### Every scored day, by the repository's exclusive pressure-day type", ""]
    lines.append("| h | Day type | Days | CRPS persistence − published | Coverage published | "
                 "Coverage persistence |")
    lines.append("|---|---|---|---|---|---|")
    for h, table in tables.items():
        for group, cell in table["by_day_type"].items():
            if not cell["days"]:
                continue
            lines.append(
                f"| {h} | {group} | {cell['days']} | {_fmt(cell['crps_persistence_minus_published'])} | "
                f"{_fmt(cell['published_coverage'])} | {_fmt(cell['persistence_coverage'])} |"
            )
    return "\n".join(lines) + "\n"


def _examples(annotated: Mapping[int, List[dict]], when: str) -> List[dict]:
    out = []
    for h, days in annotated.items():
        for day in days:
            if day["date"] == when:
                out.append({
                    "horizon": h,
                    "date": when,
                    "tags": day["tags"],
                    "published_grid_bps": day["published"],
                    "published_band_25_75": BAND_25_75_LABEL,
                    "published_band_5_95": band_5_95_label(day["tags"], h),
                    "statement": upper_tail_statement(QUANTILE_LEVELS, day["published"]),
                    "mean_label": MEAN_LABEL,
                    "mean_bias": mean_bias_label(),
                    "expected_turn_contribution_bps": turn_contribution(
                        mean_from_quantiles(QUANTILE_LEVELS, day["published"]),
                        date.fromisoformat(when),
                    ),
                    "realised_bps": day["outcome_bps"],
                    "state": day["state"],
                    "buffer": day["buffer"],
                    "state_read_date": day["state_read_date"],
                })
    return out


def tables_command(args) -> int:
    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    histories = {}
    for h in HORIZONS:
        path = Path(args.runs) / f"h{h}.json"
        if path.exists():
            histories[h] = json.loads(path.read_text(encoding="utf-8"))
    if not histories:
        raise ValueError(f"no history in {args.runs}: run `history` first")
    with scarcity.measurement_declaration():
        rows, digest = _measurement_rows()
        annotated = {
            h: [day for day in annotate(history, rows, registry, splits)
                if args.first.isoformat() <= day["date"] <= args.last.isoformat()]
            for h, history in histories.items()
        }
    tables = {h: summarise(days, horizon=h, splits=splits) for h, days in annotated.items()}
    pressure_days = {
        h: [day for day in days if day["tags"]] for h, days in annotated.items()
    }
    report = {
        "first": args.first.isoformat(),
        "last": args.last.isoformat(),
        "published_columns_digest": digest,
        "mean_rule": MEAN_RULE,
        "mean_label": MEAN_LABEL,
        "mean_bias": mean_bias_label(),
        "period_rule": PERIOD_RULE,
        "published_band_25_75": BAND_25_75_LABEL,
        "scarcity": {"band": list(scarcity.SATIATION_BAND), "on_rrp_buffer_bn": scarcity.ON_RRP_BUFFER_BN},
        "tables": {str(h): table for h, table in tables.items()},
        "examples": _examples(annotated, args.example) if args.example else [],
        "pressure_days": {
            str(h): [
                {**day, "published_band_25_75": BAND_25_75_LABEL,
                 "published_band_5_95": band_5_95_label(day["tags"], h),
                 "statement": upper_tail_statement(QUANTILE_LEVELS, day["published"]),
                 "mean_label": MEAN_LABEL,
                 "mean_bias": mean_bias_label(),
                 "expected_turn_contribution_bps": turn_contribution(
                     mean_from_quantiles(QUANTILE_LEVELS, day["published"]),
                     date.fromisoformat(day["date"]))}
                for day in days
            ]
            for h, days in pressure_days.items()
        },
    }
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    markdown = _markdown(tables, report["first"], report["last"])
    if args.markdown:
        Path(args.markdown).write_text(markdown, encoding="utf-8")
    print(markdown)
    if report["examples"]:
        print(json.dumps(report["examples"], indent=1))
    return 0


# -- live -------------------------------------------------------------------------


def live_outputs(record: dict, rows: Sequence[DailyObservation], registry, splits) -> dict:
    """The four outputs for one frozen live file, read at report time.

    The probabilities and grids are the file's own. The scarcity state is read
    from `rows`, a measurement panel built at report time, as of the file's
    decision instant: rows after the decision day are dropped first, and the
    targets are appended as empty placeholders so the rule counts the horizon
    on the calendar. Every target shares the decision instant, so one read
    serves them all. Call inside `scarcity.measurement_declaration()`.
    """

    live.validate_record(record)
    decision_day = date.fromisoformat(record["decision_day"])
    real = [row for row in rows if row.date <= decision_day]
    if not real or (decision_day - real[-1].date).days > STALE_PANEL_DAYS:
        raise StaleReadError(
            f"the measurement panel's last row on or before {decision_day} is "
            f"{real[-1].date if real else 'absent'}, older than the declared limit of "
            f"{STALE_PANEL_DAYS} calendar days: the state would be read from a panel that "
            "ended early"
        )
    if real[-1].date != decision_day:
        real.append(DailyObservation(decision_day, {}))
    targets = record["targets"]
    first = date.fromisoformat(targets[0]["target_date"])
    padded = real + [DailyObservation(first, {})]
    state = scarcity_at(padded, scarcity_rule(registry, horizon=1), len(padded) - 1)
    levels = record["distributions"]["levels"]
    forecasts = record["models"]["pressure_model_v1"]["forecasts"]
    out = []
    for target in targets:
        h = target["horizon"]
        when = date.fromisoformat(target["target_date"])
        grid = record["distributions"]["published"]["quantiles_bps"][str(h)]
        tags = pressure_day_tags(calendar_values(when), when, splits)
        mean = mean_from_quantiles(levels, grid)
        out.append({
            "horizon": h,
            "target_date": when.isoformat(),
            "p_above_5bp": forecasts[str(h)]["+5bp"],
            "p_above_10bp": forecasts[str(h)]["+10bp"],
            "tags": list(tags),
            "coupon_settlement": "not read: the live file does not carry the day's settlement",
            "published_grid_bps": grid,
            "published_band_25_75": BAND_25_75_LABEL,
            "published_band_5_95": band_5_95_label(tags, h),
            "statement": upper_tail_statement(levels, grid),
            "mean_label": MEAN_LABEL,
            "mean_bias": mean_bias_label(),
            "expected_turn_contribution_bps": turn_contribution(mean, when) if tags else None,
            "scarcity": state,
        })
    return {"decision_day": decision_day.isoformat(),
            "decision_instant": record["decision_instant"], "targets": out}


def live_command(args) -> int:
    from repo_model.data import load_daily_panel

    splits = load_split_declaration(SPLITS)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    with scarcity.measurement_declaration():
        rows = scarcity.with_reserve_scarcity_state(load_daily_panel(args.measurement_panel))
        files = sorted((Path(args.live_dir) / "live").glob("*.json"))
        report = [
            live_outputs(json.loads(path.read_text(encoding="utf-8")), rows, registry, splits)
            for path in files
        ]
    Path(args.output).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    history = commands.add_parser("history")
    history.add_argument("--panel", type=Path, required=True)
    history.add_argument("--horizon", type=int, choices=HORIZONS, required=True)
    history.add_argument("--last", type=date.fromisoformat, default=live.PANEL_END)
    history.add_argument("--output", type=Path, required=True)
    history.set_defaults(run=history_command)
    tables = commands.add_parser("tables")
    tables.add_argument("--runs", type=Path, required=True)
    tables.add_argument("--first", type=date.fromisoformat, default=date(2018, 1, 1))
    tables.add_argument("--last", type=date.fromisoformat, default=date(2025, 12, 31))
    tables.add_argument("--example", default="2025-12-31",
                        help="a date whose forecast is printed in full at every horizon")
    tables.add_argument("--json", type=Path)
    tables.add_argument("--markdown", type=Path)
    tables.set_defaults(run=tables_command)
    live_parser = commands.add_parser("live")
    live_parser.add_argument("--live-dir", type=Path, required=True)
    live_parser.add_argument("--measurement-panel", type=Path, required=True)
    live_parser.add_argument("--output", type=Path, required=True)
    live_parser.set_defaults(run=live_command)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
