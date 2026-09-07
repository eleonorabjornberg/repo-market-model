"""Leakage-safe baselines and rolling-origin evaluation.

The forecast interface `AGENT_CONTRACT.md` declares --

    fit(train_frame)            -> fitted model carrying its cutoff
    predict(feature_row)        -> quantile vector at contract.QUANTILE_LEVELS
    predict_stress(feature_row) -> exceedance vector aligned to the declared taus_bp

-- is implemented here by exactly one model, `FittedPersistence`: the
persistence-plus-empirical-residual baseline `rolling_persistence_backtest` used
to compute inline. Nothing new is forecast. What changed is that the numbers now
have one origin: the backtest fits the model and reads its quantiles instead of
deriving a second set beside it, so there is no longer a pair of interval
computations that can drift apart.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass
from datetime import date
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

from .contract import QUANTILE_LEVELS
from .data import DailyObservation, load_stress_thresholds
from .metrics import _validate_levels
from .splits import LookAheadError, ensure_strictly_ascending


#: `event_eval.FitPredict`, restated as a type alias rather than imported, so
#: `baseline` does not depend on the evaluator it feeds. The evaluator validates
#: the shape at the boundary; this is documentation with a name.
ExceedancePredictor = Callable[
    [Sequence[date], Sequence[float], Sequence[date], Sequence[float]],
    Sequence[Sequence[float]],
]


@dataclass(frozen=True)
class Forecast:
    actual_bps: float
    predicted_bps: float
    lower_bps: float
    upper_bps: float


@dataclass(frozen=True)
class BacktestReport:
    forecasts: Sequence[Forecast]
    mae_bps: float
    interval_coverage: float
    #: The model fitted at the last origin the backtest reached. Present so a
    #: reader can ask the reported run what it was fitted at, and so the
    #: interval bounds above have a named source rather than being a second
    #: derivation that happens to agree.
    model: Optional["FittedPersistence"] = None


#: The interval `rolling_persistence_backtest` reports, derived from the
#: declared levels rather than restated beside them. The outermost declared
#: pair spans this much probability mass; a backtest that named its own number
#: would be a second declaration of the same thing, and the two could drift.
INTERVAL_PROBABILITY = QUANTILE_LEVELS[-1] - QUANTILE_LEVELS[0]


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


class FittedPersistence:
    """The persistence baseline, fitted: a point rule plus a residual law.

    The point forecast is the last observed spread. The predictive distribution
    around it is the empirical distribution of one-step residuals over the
    training frame, and every number this object reports -- quantiles and
    exceedances alike -- is read off that one law.

    Fitted state is the sorted residual vector and the cutoff. Both are set in
    `fit` and nowhere else, which is the contract's "any transform with learned
    parameters ... is fitted inside `fit` and nowhere else": there is no lazy
    re-estimation on the first `predict`, and no path that lets a later call see
    a row the cutoff excluded.

    `cutoff` is the last date the training frame was allowed to contain. It is
    carried because a fitted model that cannot say what it was allowed to see
    cannot be audited for leakage, and because `event_eval` and `rolling_origin`
    both hand out training sets whose end date is the entire point. Predicting
    from a `feature_row` dated at or before the cutoff is not automatically
    wrong -- an in-sample diagnostic is a legitimate thing to want -- so it is
    not refused here. What is refused is not being able to tell:
    `trained_beyond` answers the question directly.
    """

    __slots__ = ("_residuals", "cutoff", "levels")

    def __init__(
        self,
        residuals: Sequence[float],
        cutoff: date,
        levels: Sequence[float] = QUANTILE_LEVELS,
    ) -> None:
        #: Sorted once, at fit time. `_quantile` sorts defensively too; keeping
        #: the fitted copy ordered is what makes the exceedance inversion below
        #: read the same order statistics the quantiles come from.
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
        self.cutoff: date = cutoff
        self.levels: Tuple[float, ...] = _validate_levels(levels)

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (
            f"FittedPersistence(cutoff={self.cutoff.isoformat()}, "
            f"residuals={len(self._residuals)})"
        )

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The fitted residual sample, ascending. A copy-free read-only view."""

        return self._residuals

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?

        True means the predictive distribution saw the feature row's own future.
        That is look-ahead relative to this forecast origin, and a caller
        reporting such a forecast as out-of-sample is reporting a leak. The
        model states the fact and leaves the judgement to the caller, because
        the same condition is exactly what an in-sample diagnostic wants.
        """

        return feature_row.date < self.cutoff

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """One predicted spread quantile per declared level, in declared order.

        The persistence point forecast shifted by the fitted residual quantile
        at each level. Ascending, because `levels` is ascending and `_quantile`
        is non-decreasing in its probability.
        """

        anchor = feature_row.spread_bps
        return tuple(anchor + _quantile(self._residuals, level) for level in self.levels)

    def predict_stress(
        self,
        feature_row: DailyObservation,
        taus: Optional[Sequence[float]] = None,
    ) -> Tuple[float, ...]:
        """`P(spread > tau)` per tau, derived from the distribution `predict` reports.

        Not a separately fitted classifier. `AGENT_CONTRACT.md`, Target: stress
        "is an exceedance **derived from the predictive distribution**", and the
        derivation here is literal -- this is the inverse of `predict`'s own
        quantile function over the same fitted residuals. At a declared level
        `q`, `predict_stress` evaluated at `predict`'s `Q(q)` returns `1 - q`,
        which is the property that distinguishes this implementation from a
        classifier fitted on the `stress_gt_*` label columns. A label-fitted
        classifier can be perfectly calibrated in isolation and still fail that
        equality, because nothing ties it to the quantiles.

        `taus` defaults to the `taus_bp` family declared in
        `metadata/stress_thresholds.json`, read from where Track A declared it
        rather than restated here, and the returned vector is aligned to that
        order. It is accepted as an argument so the agreement above is testable
        at the levels `predict` reports, without a second exceedance code path
        existing to test.

        Exceedance is strict `P(Y > tau)`, matching the contract's
        `P(spread > tau)` and the label columns' `stress_gt_*`.

        Raises:
            ValueError: if the tau family is empty, non-finite, or not strictly
                ascending. Non-increasing output is only meaningful against an
                increasing input, and `metrics._validate_grid` rejects the rest.
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        anchor = feature_row.spread_bps
        return tuple(
            _exceedance_from_residuals(self._residuals, tau - anchor) for tau in family
        )


def _validate_taus_bp(taus: Sequence[float]) -> Tuple[float, ...]:
    family = tuple(float(tau) for tau in taus)
    if not family:
        raise ValueError("no stress thresholds declared")
    for position, tau in enumerate(family):
        if not math.isfinite(tau):
            raise ValueError(f"tau {position} is not finite: {tau!r}")
        if position and tau <= family[position - 1]:
            raise ValueError("stress thresholds must be strictly ascending")
    return family


def _exceedance_from_residuals(ordered: Sequence[float], residual: float) -> float:
    """`P(R > residual)` under the same interpolated law `_quantile` inverts.

    `_quantile` reads the sorted sample at position `p * (n - 1)`, interpolating
    linearly between neighbouring order statistics. This walks that map
    backwards: find where `residual` sits between two order statistics, convert
    the position back to a probability, and return the mass above it. The two
    are inverses by construction, which is what makes `predict_stress` a
    statement about `predict`'s distribution rather than a second opinion.

    Outside the fitted support the answer saturates: below the smallest residual
    everything exceeds, at or above the largest nothing does. No smoothing and
    no prior, for the reason `climatology_exceedance` gives at length -- a
    Laplace correction here would be a prior nobody declared, and it would turn
    the most informative result the evaluator can produce, a model that put no
    weight where the event went, into a small number that merely looks poor.

    Ties are the one place the inversion is approximate. A repeated residual
    makes `_quantile` constant over a range of probabilities, so it has no
    single inverse; the lower end of the range is returned, and the round trip
    through a tied value comes back at most one order statistic low. Real
    one-step residuals in basis points do not tie, and the agreement test says
    so explicitly rather than relying on it silently.
    """

    count = len(ordered)
    if count == 0:
        raise ValueError("exceedance requires at least one fitted residual")
    if count == 1:
        return 1.0 if residual < ordered[0] else 0.0
    if residual < ordered[0]:
        return 1.0
    if residual >= ordered[-1]:
        return 0.0

    upper = bisect_right(ordered, residual)
    lower = upper - 1
    span = ordered[upper] - ordered[lower]
    weight = 0.0 if span <= 0.0 else (residual - ordered[lower]) / span
    return 1.0 - (lower + weight) / (count - 1)


def fit(
    train_frame: Sequence[DailyObservation],
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
) -> FittedPersistence:
    """Fit the persistence baseline on `train_frame` and return the fitted model.

    Args:
        train_frame: the training rows, strictly ascending by date. Residuals
            are the one-step differences within this frame and nothing else.
        cutoff: the last date the model was allowed to see. Defaults to the
            frame's own last date. Passed explicitly by callers that were handed
            a cutoff -- `rolling_origin` and `event_eval` both are -- so the
            frame can be checked against it rather than trusted.
        minimum_history: the shortest frame that may produce a fitted law. A
            residual quantile from a handful of rows is not a residual law.
        levels: the quantile grid, defaulting to the declared one. A model that
            wants different levels is a new model, not a config change; the
            argument exists so a caller can be explicit, not so the grid can be
            tuned.

    Returns:
        A `FittedPersistence` carrying its sorted residuals and its cutoff.

    Raises:
        LookAheadError: if any training row is dated after `cutoff`. That is the
            eligibility rule of contract test 1 at the model boundary, and it
            raises rather than asserts because `python -O` strips asserts and a
            leakage guard that vanishes under an optimisation flag is not one.
        SplitError: if the frame is not strictly ascending by date. Out of
            order, a "one-step residual" is a difference against an arbitrary
            other row.
        ValueError: if the frame is shorter than `minimum_history`.
    """

    rows = list(train_frame)
    if len(rows) < minimum_history:
        raise ValueError(
            f"persistence needs at least {minimum_history} training rows, got "
            f"{len(rows)}; a residual quantile from fewer is not a fitted law"
        )

    dates = [row.date for row in rows]
    ensure_strictly_ascending(dates, label="training frame dates")

    declared = dates[-1] if cutoff is None else cutoff
    if dates[-1] > declared:
        raise LookAheadError(
            f"training frame reaches {dates[-1]}, past its cutoff {declared}; "
            f"a fitted model may not contain a row it was not allowed to see"
        )

    residuals = [
        rows[index].spread_bps - rows[index - 1].spread_bps
        for index in range(1, len(rows))
    ]
    return FittedPersistence(residuals, declared, levels)


def predict(
    model: FittedPersistence, feature_row: DailyObservation
) -> Tuple[float, ...]:
    """`model.predict(feature_row)`, as the module-level name the contract lists.

    The contract writes the interface as three calls. The fitted object is where
    the state lives, so these two are thin and deliberately hold no logic of
    their own -- a second implementation behind the same name is precisely what
    this block exists to prevent.
    """

    return model.predict(feature_row)


def predict_stress(
    model: FittedPersistence,
    feature_row: DailyObservation,
    taus: Optional[Sequence[float]] = None,
) -> Tuple[float, ...]:
    """`model.predict_stress(feature_row, taus)`. See `predict` on why this is thin."""

    return model.predict_stress(feature_row, taus)


def rolling_persistence_backtest(
    observations: Iterable[DailyObservation],
    minimum_history: int = 20,
    interval_probability: Optional[float] = None,
) -> BacktestReport:
    """Forecast tomorrow's spread as today's spread, refitting at every origin.

    At each origin the model is fitted on the rows strictly before it and asked
    for its quantiles; the reported interval is the outermost declared pair.
    Prediction intervals therefore use only previously observed one-step
    residuals, ensuring that no future information leaks into a forecast -- and
    they are the fitted model's own numbers, not a parallel derivation that
    happens to agree with it today.

    Args:
        observations: the panel, ascending by date.
        minimum_history: the first origin scored, and the shortest training
            frame any fit is allowed.
        interval_probability: accepted only for callers that want to state the
            interval they expect. It is no longer an independent setting: the
            bounds come from `contract.QUANTILE_LEVELS`, and the only value
            those levels admit is `INTERVAL_PROBABILITY`. Pass `None`, the
            default, to read it from the declaration.

    Raises:
        ValueError: if the panel is too short, or if `interval_probability`
            names an interval the declared levels do not produce. Silently
            honouring a different number would put the reported coverage and the
            reported interval out of step, which is the drift the derivation
            exists to rule out; adjusting the levels to match is a contract
            question and not this function's to answer.
    """

    if interval_probability is not None and not math.isclose(
        interval_probability, INTERVAL_PROBABILITY, rel_tol=0.0, abs_tol=1e-12
    ):
        raise ValueError(
            f"interval_probability={interval_probability} is not the interval the "
            f"declared levels produce ({INTERVAL_PROBABILITY}, the span from "
            f"{QUANTILE_LEVELS[0]} to {QUANTILE_LEVELS[-1]}); the interval is read "
            f"from contract.QUANTILE_LEVELS, not set here"
        )

    rows = list(observations)
    if len(rows) <= minimum_history:
        raise ValueError("not enough observations for requested minimum history")

    forecasts: List[Forecast] = []
    model: Optional[FittedPersistence] = None

    for index in range(minimum_history, len(rows)):
        # Fitted on rows[:index], so the cutoff is the feature row's own date
        # and nothing dated at or after the scored day is in the frame.
        model = fit(rows[:index], minimum_history=minimum_history)
        feature_row = rows[index - 1]
        quantiles = model.predict(feature_row)
        forecasts.append(
            Forecast(
                actual_bps=rows[index].spread_bps,
                predicted_bps=feature_row.spread_bps,
                lower_bps=quantiles[0],
                upper_bps=quantiles[-1],
            )
        )

    mae = sum(abs(item.actual_bps - item.predicted_bps) for item in forecasts) / len(forecasts)
    coverage = sum(
        item.lower_bps <= item.actual_bps <= item.upper_bps for item in forecasts
    ) / len(forecasts)
    return BacktestReport(forecasts, mae, coverage, model)


def climatology_exceedance(minimum_history: int = 20) -> ExceedancePredictor:
    """Unconditional exceedance from the training distribution alone.

    The reference `AGENT_CONTRACT.md`, "Decided: stress target and event
    holdouts", names in "Metrics": "Brier skill score **against climatology**".
    A climatology is what a skill score is measured against, so it is the first
    exceedance predictor this repo needs and the only one it needs before there
    is something to compare. It is also the honest predictor for a knowledge
    holdout, where the whole question is what a model that has seen only calm
    history says about a crisis it was never shown.

    Shape is `event_eval.FitPredict`: called once with the training rows, the
    scored dates and the tau family, returning `P(value > tau)` per scored day
    per tau. `P(Y > tau)` is the fraction of training values strictly above
    `tau` -- strictly, matching the contract's `P(spread > tau)` and the label
    columns' `stress_gt_*`.

    Two properties worth stating, because both are deliberate:

    * **The curve is the same on every scored day.** A climatology is
      unconditional by definition; a predictor whose curve moved with the day
      would be conditioning on something, and then it would not be the baseline
      a skill score is measured against. `event_eval` still scores each day
      separately against its own realized value, so the report shows a flat
      predicted curve beside a path that moves, which is the comparison.

    * **No smoothing, no prior.** With no training row above 50bp the answer is
      `0.0`, and it stays `0.0` rather than being nudged to `1/(n+2)`. A
      Laplace correction here would be a prior nobody declared, and it would
      quietly convert the most informative result this evaluator can produce --
      a model that put *no* weight where the event actually went -- into a small
      number that looks like a poor forecast rather than an absent one. Scoring
      rules that cannot take a zero are the caller's problem to raise, and
      `event_eval` computes none.

    Monotonicity is automatic: `taus` arrives strictly ascending, and the count
    of values above a larger threshold cannot exceed the count above a smaller
    one, so `_validate_predictions`' non-increasing check is satisfied by
    construction rather than by rounding.

    Args:
        minimum_history: the shortest training set that may produce a curve. A
            fraction over five rows is not a climatology, and at an event
            boundary the training set is whatever survived the purge -- which
            can be very short without anything else objecting.

    Returns:
        A `fit_predict` callable suitable for `event_eval.evaluate_event_window`.

    Raises:
        ValueError: at call time, if the training set is shorter than
            `minimum_history`. A `ValueError` rather than a bespoke type so the
            CLI dispatcher's `(OSError, ValueError)` already covers it.
    """

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")

    def fit_predict(
        train_dates: Sequence[date],
        train_values: Sequence[float],
        test_dates: Sequence[date],
        taus: Sequence[float],
    ) -> List[Tuple[float, ...]]:
        history = [float(value) for value in train_values]
        if len(history) < minimum_history:
            raise ValueError(
                f"climatology needs at least {minimum_history} training rows, got "
                f"{len(history)}; at an event boundary the training set is whatever "
                "cleared the purge gap, and a curve from a handful of rows is not a "
                "climatology"
            )
        denominator = float(len(history))
        curve = tuple(
            sum(1 for value in history if value > float(tau)) / denominator
            for tau in taus
        )
        return [curve for _ in test_dates]

    return fit_predict
