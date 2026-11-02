"""B4, a plain linear quantile regression of the spread on reserves and calendar days (#1360; H5, registration design, step 4 to 5).

`metadata/b4_quantile_regression_1360.json` is the declaration; this module is its arithmetic. B4 is a benchmark of the registered test beside B1, B1' and
B2 (Eleonora, 2 November 2026): the question a referee asks is whether the candidate beats a parsimonious model that reads the same public reserve and
calendar information. Whether B4 joins the protocol's decision rule or is reported beside it is hers (a marked question in the pull request that closes
#1360); this module decides nothing on it.

For each lead h = 1..5 and each level tau of the protocol's grid (`scoring_protocol.GRID`), one linear quantile regression of the spread on the scored day
(bp) on an intercept, the last observed spread (the spread of the as-of anchor), the as-of reserve balances (USD trillion) and the calendar terms of the
candidate's base (`spread_mr_calendar.NO_FOMC_IORB`) read at the TARGET day. The check loss is penalised by `RIDGE` times the squared non-intercept
coefficients, nothing else is tuned, and the 23 fitted quantiles of a lead are sorted so that they never cross.

**Direct pairs.** A training pair for the decision on row D (anchor A, lag L = D - A) at lead h is the pair of `spread_mean_reversion.training_rows`:
target T in [h + L, A], origin T - (h + L), the pair's own decision row T - h. Its calendar flags are the flags of T at lead h, never of the origin, and a
scheduled field (the settlement terms) is read only where `asof` rule 2 admits it, lead 1 (`spread_mr_calendar.TermTable`). `fit_quantile_regression`
carries `one_step_guard.guard_one_step_fit`, trains on direct pairs only and needs no allow-list entry. The window is expanding (the declaration).

**The reserve measure** is `reserve_balances` as `asof.InformationRule` serves it at the decision instant of each decision row (`ReserveTable`): a pair is
trained on the value read at its own decision row, a forecast reads the value of its own decision row, and `read_reserves` refuses a later row with
`LookAheadError`.

Stdlib only, so the benchmark reproduces with no install.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from .asof import InformationRule
from .data import DailyObservation
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import GRID, HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: The L2 penalty on every non-intercept coefficient (bp per bp, bp per USD trillion, bp per flagged day), the one fixed small ridge of the directive. The
#: check loss is linear in the residual, so the penalty is a numerical stabiliser here: it equals the loss of a flagged pair only for an effect of
#: (flagged pairs) / (4 * RIDGE) bp, 75 bp for a term that has just entered with three flagged pairs.
RIDGE = 0.01
#: The floor of a residual's absolute value in the reweighting, in bp.
EPSILON = 1e-3
#: The cap on the reweighting iterations of one level, and the largest coefficient move that stops them.
MAX_ITERATIONS = 100
TOLERANCE = 1e-3
#: A term enters a lead's fit only if this many training pairs carry its flag (the candidate's rule).
MIN_FLAGGED = cal.MIN_FLAGGED
#: A lead needs this many training pairs after the pairs with an unknown reserve value are dropped.
MIN_PAIRS = smr.MIN_PAIRS
#: The candidate's refit cadence, in decision days.
REFIT_EVERY = smr.REFIT_EVERY
#: The calendar terms: the candidate's base (s3), without the FOMC and IORB terms.
TERMS: Tuple[str, ...] = cal.NO_FOMC_IORB
RESERVE_COLUMN = "reserve_balances"
#: The panel carries reserve balances in USD billion; the regressor is in USD trillion.
RESERVE_UNIT = 1000.0

InsufficientHistory = smr.InsufficientHistory

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "refit": (
        "not_entry",
        "fits B4 on the pairs whose targets are public at the decision instant (protocol_benchmarks._require_public); makes a forecast, "
        "scores nothing: the forecast is scored only through scoring_protocol.day_scores, which calls require_unlocked on every scored day",
    ),
}


class Pair(NamedTuple):
    """One training pair: its response (the spread at the target, bp), the last spread of its origin, the reserve value of its decision row (USD trillion, or
    `None`) and the flags of the target."""

    response: float
    last: float
    reserves: Optional[float]
    flags: Mapping[str, int]


@dataclass(frozen=True)
class Estimate:
    """The fitted coefficients of one lead: for each level the intercept, the last-spread and reserves slopes, and one slope per entering term."""

    terms: Tuple[str, ...]
    coefficients: Dict[float, Tuple[float, ...]]
    pairs: int
    unknown_reserves: int
    flagged: Dict[str, int]
    iterations: Dict[float, int]
    levels: Tuple[float, ...]


# -- the reserve measure, as a decision could read it ---------------------------------------------------------------------


class ReserveTable:
    """The reserve balances (USD trillion) that the decision on each panel row could read, per row, as `asof.InformationRule` serves them.

    `values[row]` is the value of the latest row on which `reserve_balances` was public at the decision instant of the decision on `row` (the rule at horizon
    1 for the scored row `row + 1`), checked by both of the rule's guards; the last row has none (no row follows it) and is `None`, as is a hole.
    """

    def __init__(self, panel: Sequence[DailyObservation], *, registry: Mapping[str, Mapping[str, object]], decision_time: time):
        dates = [row.date for row in panel]
        rule = InformationRule(registry, (RESERVE_COLUMN,), decision_time=decision_time, horizon=1)
        values: List[Optional[float]] = []
        rows: List[Optional[int]] = []
        for row in range(len(panel)):
            if row + 1 >= len(panel):
                values.append(None)
                rows.append(None)
                continue
            try:
                info = rule.information_set(dates, row + 1)
            except SplitError:  # the first rows: no target is observable yet, so nothing is public to read
                values.append(None)
                rows.append(None)
                continue
            rule.check(dates, info)
            read = next(r for r in info.reads if r.feature == RESERVE_COLUMN)
            level = panel[read.row].values.get(RESERVE_COLUMN)
            values.append(None if level is None else float(level) / RESERVE_UNIT)
            rows.append(read.row)
        self.dates = dates
        self.values = values
        #: The panel row each value was read from.
        self.read_rows = rows

    def read(self, row: int, decision_index: int) -> Optional[float]:
        """The reserve value of the decision on `row`, read by the decision on `decision_index`; `None` if it is not known."""

        return read_reserves(self, row, decision_index)


def read_reserves(table: ReserveTable, row: int, decision_index: int) -> Optional[float]:
    """The value the decision on `row` could read, served to the decision on `decision_index`.

    Raises:
        LookAheadError: `row` is after the decision (its reserve value is not public at the decision instant).
    """

    if row > decision_index:
        raise LookAheadError(
            f"the reserve balances of the decision on {table.dates[row]} are read by the decision on {table.dates[decision_index]}, before they can be known"
        )
    return table.values[row]


# -- the estimation ----------------------------------------------------------------------------------------------------------


def design_row(pair: Pair, terms: Sequence[str]) -> Tuple[float, ...]:
    """The regressors of a pair: 1, the last spread, the reserves (0 where unknown) and the flag of each term."""

    return (1.0, pair.last, 0.0 if pair.reserves is None else pair.reserves) + tuple(float(pair.flags[name]) for name in terms)


def _solve(matrix: List[List[float]], rhs: List[float]) -> List[float]:
    """Gaussian elimination with partial pivoting; the penalised normal matrix is positive definite, so a zero pivot is a bug."""

    n = len(rhs)
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("the normal equations of the quantile regression are singular")
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(col + 1, n):
            factor = a[r][col] / a[col][col]
            if factor:
                a[r] = [x - factor * y for x, y in zip(a[r], a[col])]
    out = [0.0] * n
    for i in range(n - 1, -1, -1):
        out[i] = (a[i][n] - sum(a[i][j] * out[j] for j in range(i + 1, n))) / a[i][i]
    return out


def _weighted_normal(columns: Sequence[Sequence[float]], weights: Sequence[float], ridge: float) -> List[List[float]]:
    p = len(columns)
    weighted = [list(map(operator.mul, weights, column)) for column in columns]
    matrix = [[0.0] * p for _ in range(p)]
    for j in range(p):
        for k in range(j, p):
            value = sum(map(operator.mul, weighted[j], columns[k]))
            matrix[j][k] = matrix[k][j] = value
    for j in range(1, p):
        matrix[j][j] += 2.0 * ridge
    return matrix


def _entering(terms: Sequence[str], pairs: Sequence[Pair], min_flagged: int) -> Tuple[Tuple[str, ...], Dict[str, int]]:
    counts = {name: sum(1 for p in pairs if p.flags.get(name)) for name in terms if all(name in p.flags for p in pairs)}
    return tuple(name for name in terms if counts.get(name, 0) >= min_flagged), counts


@guard_one_step_fit
def fit_quantile_regression(
    pairs: Sequence[Pair],
    *,
    regressors: Sequence[str],
    terms: Sequence[str],
    training_pairs: str,
    ridge: float = RIDGE,
    levels: Sequence[float] = GRID,
    min_flagged: int = MIN_FLAGGED,
    min_pairs: int = MIN_PAIRS,
) -> Estimate:
    """B4's coefficients at one lead: a ridge-penalised linear quantile regression at each of `levels`.

    The objective at level tau is the summed check loss of tau over the pairs plus `ridge` times the squared non-intercept coefficients. It is minimised by
    iteratively reweighted least squares (a quadratic majorizer of |r| at the previous residual, weight 1 / (2 max(|r|, EPSILON))), started from the ridge
    least-squares fit at the first level and from the previous level's coefficients after that; at most `MAX_ITERATIONS` iterations, stopping when no
    coefficient moves by more than `TOLERANCE`. A pair whose reserve value is unknown is dropped (and counted). A term enters when `min_flagged` pairs
    carry its flag.

    `regressors` are the panel columns the terms read (for `one_step_guard`). `training_pairs` is required, and `'direct'` is the only value this fit
    trains on.

    Raises:
        ValueError: `training_pairs` is not `'direct'` (after the one-step guard has looked at the regressors).
        InsufficientHistory: fewer than `min_pairs` pairs with a known reserve value.

    Mutation record: see `tests/test_b4_quantile_regression_1360.py` (the guard decorator).
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_quantile_regression trains on direct pairs only, got training_pairs={training_pairs!r}")
    known = [p for p in pairs if p.reserves is not None]
    if len(known) < min_pairs:
        raise InsufficientHistory(f"{len(known)} training pairs with a known reserve value, fewer than {min_pairs}")
    active, counts = _entering(terms, known, min_flagged)
    rows = [design_row(p, active) for p in known]
    columns = [list(column) for column in zip(*rows)]
    response = [p.response for p in known]
    sums = [sum(column) for column in columns]
    width = len(columns)
    ordered = sorted(levels)
    start = _solve(_weighted_normal(columns, [1.0] * len(known), ridge),
                   [sum(map(operator.mul, column, response)) for column in columns])
    coefficients: Dict[float, Tuple[float, ...]] = {}
    iterations: Dict[float, int] = {}
    beta = start
    for tau in ordered:
        shift = (2.0 * tau - 1.0) / 2.0
        steps = 0
        for steps in range(1, MAX_ITERATIONS + 1):
            residual = [y - sum(map(operator.mul, beta, row)) for y, row in zip(response, rows)]
            weights = [1.0 / (2.0 * max(abs(r), EPSILON)) for r in residual]
            matrix = _weighted_normal(columns, weights, ridge)
            rhs = [sum(map(operator.mul, map(operator.mul, weights, column), response)) + shift * total
                   for column, total in zip(columns, sums)]
            new = _solve(matrix, rhs)
            moved = max(abs(a - b) for a, b in zip(new, beta))
            beta = new
            if moved <= TOLERANCE:
                break
        coefficients[tau] = tuple(beta)
        iterations[tau] = steps
    return Estimate(active, coefficients, len(known), len(pairs) - len(known), counts, iterations, tuple(ordered))


def _raw(estimate: Estimate, last: float, reserves: Optional[float], flags: Mapping[str, int]) -> List[float]:
    row = (1.0, last, 0.0 if reserves is None else reserves) + tuple(float(flags[name]) for name in estimate.terms)
    return [sum(map(operator.mul, estimate.coefficients[tau], row)) for tau in estimate.levels]


def predict(estimate: Estimate, last: float, reserves: Optional[float], flags: Mapping[str, int]) -> List[float]:
    """The quantiles at `estimate.levels`, sorted so that they never cross (the rearrangement of the fitted values)."""

    return sorted(_raw(estimate, last, reserves, flags))


def crossed(estimate: Estimate, last: float, reserves: Optional[float], flags: Mapping[str, int]) -> bool:
    """Whether the fitted quantiles at these regressors cross, so that the sort changed them."""

    raw = _raw(estimate, last, reserves, flags)
    return raw != sorted(raw)


# -- the walk -------------------------------------------------------------------------------------------------------------------


def training_pairs(panel: Sequence[DailyObservation], decision_index: int, anchor: int, *, lag: int) -> Dict[int, List[Tuple[int, int]]]:
    """Per lead h, the (origin, target) rows of the expanding window's direct pairs, `k = h + lag` rows apart.

    The target is at or before the anchor; the origin is on the panel. Every row read is required public.

    Raises:
        LookAheadError: a row after the anchor is among the pairs.
    """

    dates = [row.date for row in panel]
    out: Dict[int, List[Tuple[int, int]]] = {}
    for h in HORIZONS:
        k = h + lag
        found = [(target - k, target) for target in range(k, anchor + 1)]
        pb._require_public({row for pair in found for row in pair}, anchor, dates, f"the B4 fit for {dates[decision_index]}, lead {h}")
        out[h] = found
    return out


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: cal.TermTable,
    reserves: ReserveTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[float] = GRID,
    ridge: float = RIDGE,
) -> Dict[int, Estimate]:
    """B4's estimate at each lead as of the decision on row `decision_index`, on the direct pairs of the expanding window.

    Raises:
        InsufficientHistory: a lead with fewer than `MIN_PAIRS` pairs with a known reserve value.
        LookAheadError: a row after the anchor is read, or a reserve value after the decision.
        ValueError: the one-step guard (`fit_quantile_regression`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = training_pairs(panel, decision_index, anchor, lag=lag)
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    regressors = tuple(dict.fromkeys(column for name in TERMS for column in cal.TERM[name].reads)) + (RESERVE_COLUMN,)
    out: Dict[int, Estimate] = {}
    for h in HORIZONS:
        pairs = [
            Pair(spreads[target], spreads[origin], reserves.read(target - h, decision_index), table.flags_at(h, target))
            for origin, target in rows[h]
        ]
        out[h] = fit_quantile_regression(
            pairs, regressors=regressors, terms=TERMS, training_pairs="direct", ridge=ridge, levels=levels
        )
    return out


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    estimates: Mapping[int, Estimate],
    table: cal.TermTable,
    reserves: ReserveTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> Dict[int, List[float]]:
    """The forecast of the decision on `decision_index` from `estimates` (possibly an older fit): the last spread, the reserve value and the flags of each
    target are read afresh.

    Raises:
        InsufficientHistory: the decision's reserve value is unknown.
        LookAheadError: a scheduled field of a target row, or a reserve value, is not public at the decision.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    last = panel[anchor].spread_bps
    level = reserves.read(decision_index, decision_index)
    if level is None:
        raise InsufficientHistory(f"{panel[decision_index].date}: the reserve balances are not known at the decision")
    out: Dict[int, List[float]] = {}
    for h in HORIZONS:
        out[h] = predict(estimates[h], last, level, table.read(h, decision_index))
    return out


@dataclass(frozen=True)
class Walk:
    #: Decision day -> lead -> the quantiles.
    forecasts: Dict[date, Dict[int, List[float]]]
    #: Decision day -> the day of the refit its forecast used.
    fit_used: Dict[date, date]
    #: Refit day -> lead -> the estimate.
    estimates: Dict[date, Dict[int, Estimate]]
    #: Decision day -> lead -> whether the fitted quantiles crossed and the sort changed them.
    crossed: Dict[date, Dict[int, bool]]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: cal.TermTable,
    reserves: ReserveTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    refit_every: int = REFIT_EVERY,
    levels: Sequence[float] = GRID,
) -> Walk:
    """B4 on `decision_days`, refitting at the first and then every `refit_every` decision days, as the candidate's walk does.

    Raises:
        ProtocolError: a decision day is not a panel day.
        InsufficientHistory: a decision day has no forecast (B4 never skips a day: the days are compared with every other model's).
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    fit_used: Dict[date, date] = {}
    estimates: Dict[date, Dict[int, Estimate]] = {}
    crossings: Dict[date, Dict[int, bool]] = {}
    current: Optional[Dict[int, Estimate]] = None
    fitted_on: Optional[date] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        if current is None or since >= refit_every:
            current = refit(panel, index, table, reserves, registry=registry, decision_time=decision_time, levels=levels)
            fitted_on = day
            estimates[day] = current
            since = 0
        forecasts[day] = forecast(panel, index, current, table, reserves, registry=registry, decision_time=decision_time)
        anchor = pb._anchor(panel, index, registry, decision_time)
        level = reserves.read(index, index)
        crossings[day] = {
            h: crossed(current[h], panel[anchor].spread_bps, level, table.read(h, index)) for h in HORIZONS
        }
        fit_used[day] = fitted_on
        since += 1
    return Walk(forecasts, fit_used, estimates, crossings)
