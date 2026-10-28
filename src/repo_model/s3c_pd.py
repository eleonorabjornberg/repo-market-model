"""(s3c-pd): (s3c) with primary dealers' reverse repo plus securities borrowed as a balance-sheet state input (#1296; H5 step 3, ledger item 72 on #1116).

Eleonora, 28 October 2026 (chat, relayed on #1296): the supplementary leverage ratio change lets dealer balance sheets grow, and (s3c) has no
input for dealer balance-sheet capacity. This module adds one state term to (s3)'s fit and leaves every other term, the Huber fit, the ridge
of 5 and the SRF cap (`repo_model.s3c_candidate`) as they are, the way `repo_model.s3c_carry` adds its term.

**The level.** For each weekly as-of date (a Wednesday) the level is, in USD billions, the sum of four New York Fed Primary Dealer Statistics
(FR 2004) totals: reverse repurchase agreements (`PDSIRRA-`) and securities borrowed (`PDSIOSB-`) on U.S. Treasury securities excluding TIPS
(`UTSETTOT`) and on TIPS (`UTSTTOT`). These are the Treasury rows of the lines the Office of Financial Research's Short-term Funding Monitor
shows in "Primary dealer reverse repo and securities borrowing by tenor". A figure the New York Fed withheld for confidentiality (`*`) is no
observation, never 0: a week with any of the four withheld has no level.

**The state.** The state read by the decision on day `D` is the z-score of the latest public week's level against the weeks of the year
before it: `(level - mean) / stdev` over the defined levels of the `TRAILING_WEEKS` as-of weeks before the latest public week, when at least
`MIN_TRAILING` of them are defined and their standard deviation is positive; `None` otherwise, and `None` when the latest public week has no
level. No older week is carried in its place (a staleness rule would be a threshold nobody has set): the term is 0 on such a day, as the
scarcity state reads 0 when unknown (`spread_mr_state_calendar.standardised_shift`). The transform is declared in
`metadata/s3c_pd_1296.json` before any score and is not tuned.

**Information set.** A week's figures are public once released: `release_instant(week)` is the declared lag after the as-of date, 6 business
days on `metadata/market_holidays.json` (the Thursday of the following week) at 16:30 America/New_York, which is what the New York Fed's page
states ("updated on Thursdays at approximately 4:15 p.m. with the previous week's statistics") rounded up. A decision at 16:00 on the release
day itself therefore cannot read the week; the next business day's can. `read_level` raises `LookAheadError` for a week released after the
decision instant. The state is a slow variable of the *decision*, not of the target: like the scarcity state it is keyed by the decision day
(`spread_mr_state_calendar.read_state` raises `LookAheadError` for a later day), a training pair is trained on the state of its own decision day
(`spread_mr_state_calendar.pair_state`), and a forecast reads the state of its own decision day. The snapshot holds the latest revised vintage
of each series, not first prints; the figures are rarely revised and this is stated on the page.

**Direct pairs.** `fit_pd_terms` is decorated with `one_step_guard.guard_one_step_fit` with no allow-list entry; the calendar terms it keeps are
read at the target row. The state is no panel column and no calendar or scheduled field.

Stdlib only.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import data as data_module
from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from . import spread_mr_state_calendar as sc
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

__all__ = [
    "ARM", "PD", "PdEstimate", "PdWalk", "SERIES", "decision_states", "fit_pd_terms", "forecast_leads", "load_levels", "read_level",
    "release_instant", "state_at", "walk",
]

#: The four New York Fed totals whose sum is the level (USD millions in the file, USD billions here).
SERIES: Tuple[str, ...] = ("PDSIRRA-UTSETTOT", "PDSIRRA-UTSTTOT", "PDSIOSB-UTSETTOT", "PDSIOSB-UTSTTOT")
#: The name of the term in `StateEstimate.flagged`.
PD = "pd_state"
#: Business days from the as-of Wednesday to its release (the Thursday of the following week), as `metadata/sources.json` declares for the
#: same release (`nyfed_fr2004`).
RELEASE_LAG_BUSINESS_DAYS = 6
#: The release time declared for the source: the page says "approximately 4:15 p.m."; 16:30 is the conservative instant within that day.
RELEASE_TIME = time(16, 30)
#: The weeks before the latest public week that the standardisation looks back over, and the least number of them with a level.
TRAILING_WEEKS = 52
MIN_TRAILING = 26
#: The term enters a lead's fit when at least this many training pairs have a state: the base model's minimum of training pairs.
MIN_STATE_PAIRS = smr.MIN_PAIRS
#: USD millions in the file to USD billions.
MILLIONS_PER_BILLION = 1000.0
#: (s3)'s arm, whose terms, fit and ridge the new term joins.
ARM = sc.ARMS[2]


def _series_rows(path: Path) -> Dict[date, Optional[float]]:
    body = json.loads(path.read_text(encoding="utf-8"))
    out: Dict[date, Optional[float]] = {}
    for row in body["pd"]["timeseries"]:
        day = date.fromisoformat(row["asofdate"])
        if day in out:
            raise ValueError(f"{path.name}: the as-of date {day} appears twice")
        text = str(row["value"]).strip()
        if text == "*":
            out[day] = None  # withheld for confidentiality: no observation, never 0
            continue
        try:
            out[day] = float(text)
        except ValueError as exc:
            raise ValueError(f"{path.name}: the value {text!r} on {day} is neither a number nor '*'") from exc
    return out


def load_levels(directory: Path) -> Dict[date, Optional[float]]:
    """The weekly level in USD billions by as-of date from the tracked snapshot; `None` where any of the four totals is withheld.

    Raises:
        ValueError: a file is missing, a value is neither a number nor `*`, or the four files do not cover the same as-of dates.
    """

    series = {}
    for key in SERIES:
        path = Path(directory) / f"{key}.json"
        if not path.exists():
            raise ValueError(f"{path} is missing")
        series[key] = _series_rows(path)
    days = set(series[SERIES[0]])
    for key in SERIES[1:]:
        if set(series[key]) != days:
            raise ValueError(f"{key} does not cover the as-of dates of {SERIES[0]}")
    out: Dict[date, Optional[float]] = {}
    for day in sorted(days):
        parts = [series[key][day] for key in SERIES]
        out[day] = None if any(p is None for p in parts) else sum(parts) / MILLIONS_PER_BILLION
    return out


def release_instant(asof: date) -> datetime:
    """When the figures of the as-of date become public: `RELEASE_LAG_BUSINESS_DAYS` market business days after it, at `RELEASE_TIME`
    (America/New_York, naive like the decision instants of the walks).

    Mutation record: see `tests/test_s3c_pd.py` (`release_instant`).
    """

    return datetime.combine(data_module.next_business_day(asof, RELEASE_LAG_BUSINESS_DAYS), RELEASE_TIME)


def read_level(levels: Mapping[date, Optional[float]], asof: date, decision_day: date, *, decision_time: time = time(16, 0)) -> Optional[float]:
    """The level of the as-of week, read by the decision at `decision_time` on `decision_day`.

    Raises:
        LookAheadError: the week is released after the decision instant.
        ValueError: the week is not in the snapshot.

    Mutation record: see `tests/test_s3c_pd.py` (`read_level`).
    """

    if asof not in levels:
        raise ValueError(f"the as-of week {asof} is not in the snapshot")
    instant = datetime.combine(decision_day, decision_time)
    if release_instant(asof) > instant:
        raise LookAheadError(
            f"the primary dealer figures of the week {asof} are released at {release_instant(asof)}, after the decision at {instant}"
        )
    return levels[asof]


def latest_public_week(levels: Mapping[date, Optional[float]], decision_day: date, *, decision_time: time = time(16, 0)) -> Optional[date]:
    """The latest as-of week in the snapshot released at or before the decision instant, or `None`."""

    instant = datetime.combine(decision_day, decision_time)
    public = [week for week in levels if release_instant(week) <= instant]
    return max(public) if public else None


def state_at(levels: Mapping[date, Optional[float]], decision_day: date, *, decision_time: time = time(16, 0)) -> Optional[float]:
    """The state a decision on `decision_day` reads: the z-score of the latest public week's level against the year before it.

    `None` where the latest public week has no level, where fewer than `MIN_TRAILING` of the `TRAILING_WEEKS` weeks before it have one, or
    where their standard deviation is not positive. Every week it reads is read through `read_level`, so none is released after the decision.
    """

    week = latest_public_week(levels, decision_day, decision_time=decision_time)
    if week is None:
        return None
    latest = read_level(levels, week, decision_day, decision_time=decision_time)
    if latest is None:
        return None
    earlier = [
        read_level(levels, w, decision_day, decision_time=decision_time)
        for w in levels if 0 < (week - w).days <= 7 * TRAILING_WEEKS
    ]
    trailing = [x for x in earlier if x is not None]
    if len(trailing) < MIN_TRAILING:
        return None
    spread = statistics.stdev(trailing)
    if spread <= 0.0:
        return None
    return (latest - statistics.fmean(trailing)) / spread


def decision_states(
    levels: Mapping[date, Optional[float]], dates: Sequence[date], *, decision_time: time = time(16, 0)
) -> Dict[date, Optional[float]]:
    """`states[d]`: the state a decision on panel day `d` could read (what `spread_mr_state_calendar.read_state` and `pair_state` look up)."""

    return {d: state_at(levels, d, decision_time=decision_time) for d in dates}


@dataclass(frozen=True)
class PdEstimate:
    """One lead's estimate: (s3)'s kind of estimate (`state`, whose pool is the pool after the state term too) and the coefficient.

    `coefficient` is in standardised units per standard unit of the state (0 and `active` False where the term did not enter); `state` is
    then what `fit_state_terms` returns on the same pairs.
    """

    state: sc.StateEstimate
    coefficient: float
    active: bool
    #: Training pairs with a state.
    pd_pairs: int


@guard_one_step_fit
def fit_pd_terms(
    pairs: Sequence[sc.StatePair],
    values: Sequence[Optional[float]],
    *,
    regressors: Sequence[str],
    terms: Sequence[str],
    training_pairs: str,
    min_pairs: int = MIN_STATE_PAIRS,
    ridge: float = sc.ROBUST_RIDGE,
    baseline: Optional[sc.StateEstimate] = None,
) -> PdEstimate:
    """(s3)'s Huber fit of one lead with the state column added, in standardised units.

    `values[i]` is the state of pair `i`'s own decision day (`None` reads as 0); the term enters when at least `min_pairs` pairs have a state,
    otherwise the estimate is `fit_state_terms`' (or `baseline`, the same call made by the caller on these pairs).

    Raises:
        ValueError: `training_pairs` is not `'direct'`, or one value per pair is not given.
        InsufficientHistory: there is no pair.
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_pd_terms trains on direct pairs only, got training_pairs={training_pairs!r}")
    if len(values) != len(pairs):
        raise ValueError("fit_pd_terms needs one state per pair")
    count = sum(1 for x in values if x is not None)
    if count < min_pairs:
        base = baseline or sc.fit_state_terms(
            pairs, regressors=regressors, terms=terms, interact=False, robust=True, training_pairs="direct", ridge=ridge)
        return PdEstimate(base, 0.0, False, count)
    active, counts = sc._entering(terms, pairs, sc.MIN_FLAGGED)
    target = [p.raw / p.scale for p in pairs]
    column = [0.0 if x is None else x for x in values]
    design = [[1.0] + [float(p.flags[name]) for name in active] + [x] for p, x in zip(pairs, column)]
    coefficients, iterations = sc.huber(design, target, ridge)
    effect = dict(zip(active, coefficients[1 : 1 + len(active)]))
    coefficient = coefficients[-1]
    pool = [
        y - sum(effect[name] * float(p.flags[name]) for name in effect) - coefficient * x
        for p, y, x in zip(pairs, target, column)
    ]
    counts[PD] = count
    state = sc.StateEstimate(
        active, effect, {}, counts, tuple(pb.empirical_quantiles(sorted(pool))), len(pairs),
        sum(1 for p in pairs if p.state is None), iterations, False, tuple(p.origin for p in pairs), tuple(p.target for p in pairs),
        tuple(pool), 0,
    )
    return PdEstimate(state, coefficient, True, count)


def forecast_leads(
    estimates: Mapping[int, PdEstimate], quantiles: Mapping[int, Sequence[float]], value: Optional[float], scale: float
) -> Dict[int, List[float]]:
    """Each lead's quantiles with the state effect added: `quantiles` are `sc.forecast`'s from the estimates' `state`, `value` the decision
    day's state and `scale` the anchor's. The effect is `coefficient * value * scale` in bp, added to every quantile (0 where the term is not
    active or the state is unknown)."""

    x = 0.0 if value is None else value
    return {h: [q + estimates[h].coefficient * x * scale for q in quantiles[h]] for h in quantiles}


# -- the walk ---------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PdWalk:
    #: Decision day -> lead -> 23 quantiles of (s3-pd) (before the SRF cap), and (s3)'s own, from the same walk.
    forecasts: Dict[date, Dict[int, List[float]]]
    s3: Dict[date, Dict[int, List[float]]]
    #: Decision day -> the state it read and the scale at its anchor.
    values: Dict[date, Optional[float]]
    scales: Dict[date, float]
    #: Refit day -> lead -> the estimate.
    estimates: Dict[date, Dict[int, PdEstimate]]
    #: Decision day -> the refit day whose estimates it used.
    fit_used: Dict[date, date]
    skipped: Tuple[date, ...]


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: cal.TermTable,
    states: Mapping[date, Optional[float]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    training_pairs: str = "direct",
) -> Tuple[Dict[int, PdEstimate], Dict[int, sc.StateEstimate]]:
    """The state arm's estimate at each lead, and (s3)'s, as of the decision on row `decision_index`, on the base model's training pairs.

    Mirrors `spread_mr_state_calendar.refit` for (s3) (the same pairs, the same scale, the same terms) and reads each pair's state at the
    decision day of that pair, `origin + lag`.

    Raises:
        InsufficientHistory: the base fit's, or a lead with no pair that has a scale.
        LookAheadError: a row the scale reads is after the anchor, or a state is read after the decision.
        ValueError: the one-step guard (`fit_pd_terms`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in HORIZONS for origin, _ in rows[h]} | {anchor})
    variant = sc.BASE_VARIANT
    read = {j for origin in origins if origin - variant.window >= 0 for j in fhs.scale_rows(origin, variant.window)}
    pb._require_public(read, anchor, dates, f"the scale of {variant.name} for {dates[decision_index]}")
    reader = fhs.ScaleReader(spreads, variant)
    mine: Dict[int, PdEstimate] = {}
    s3: Dict[int, sc.StateEstimate] = {}
    for h in HORIZONS:
        k = h + lag
        pairs: List[sc.StatePair] = []
        values: List[Optional[float]] = []
        for origin, target in rows[h]:
            scale = reader.at(origin)
            if scale is None:
                continue
            raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
            flags_row = target if training_pairs == "direct" else origin
            pairs.append(sc.StatePair(raw, scale, table.flags_at(h, flags_row), None, {}, origin, target, {}, False))
            values.append(sc.pair_state(states, dates, origin, lag, decision_index))
        if not pairs:
            raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
        regressors = cal.regressors_of(ARM, h)
        s3[h] = sc.fit_state_terms(
            pairs, regressors=regressors, terms=ARM.location, interact=False, robust=True, training_pairs=training_pairs,
            ridge=ARM.ridge)
        mine[h] = fit_pd_terms(
            pairs, values, regressors=regressors, terms=ARM.location, training_pairs=training_pairs, baseline=s3[h])
    return mine, s3


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: cal.TermTable,
    states: Mapping[date, Optional[float]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    training_pairs: str = "direct",
) -> PdWalk:
    """(s3) and (s3-pd) on `decision_days`, refitting as `spread_mr_state_calendar.walk` does (a day with no forecast is skipped and does not
    count toward the next refit), so that (s3) here is that walk's (s3) forecast for forecast.

    `states[d]` is the state a decision on panel day `d` could read (`decision_states`); a forecast reads that of its own decision day.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    dates = [row.date for row in panel]
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    s3_out: Dict[date, Dict[int, List[float]]] = {}
    values: Dict[date, Optional[float]] = {}
    scales: Dict[date, float] = {}
    estimates: Dict[date, Dict[int, PdEstimate]] = {}
    fit_used: Dict[date, date] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    mine_now: Dict[int, PdEstimate] = {}
    s3_now: Dict[int, sc.StateEstimate] = {}
    refit_day: Optional[date] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                fhs.fit(panel, index, [sc.BASE_VARIANT], base=base, **settings)  # the walk's own refit can skip the day: so does this
                mine_now, s3_now = refit(
                    panel, index, table, states, registry=registry, decision_time=decision_time, levels=levels, base=base,
                    training_pairs=training_pairs)
                current, refit_day = base, day
                estimates[day] = mine_now
                since = 0
            fcfg = dict(registry=registry, decision_time=decision_time, levels=levels, base=current)
            theirs, detail = sc.forecast(panel, index, {ARM.name: s3_now}, table, {}, (ARM,), **fcfg)
            ours, _ = sc.forecast(panel, index, {ARM.name: {h: e.state for h, e in mine_now.items()}}, table, {}, (ARM,), **fcfg)
            state = sc.read_state(states, dates, index, index)
        except smr.InsufficientHistory:
            skipped.append(day)
            continue
        except LookAheadError:
            raise  # a guard trip is never "no public row yet"
        except SplitError:
            if current is not None:
                raise
            skipped.append(day)
            continue
        fit_used[day] = refit_day
        since += 1
        s3_out[day] = theirs[ARM.name]
        scale = float(detail["scale"])
        forecasts[day] = forecast_leads(mine_now, ours[ARM.name], state, scale)
        values[day] = state
        scales[day] = scale
    return PdWalk(forecasts, s3_out, values, scales, estimates, fit_used, tuple(skipped))
