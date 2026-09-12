"""Scoring, calibration diagnostics and intervals for the scoring holdout.

Implements the metrics named in `AGENT_CONTRACT.md`, "Metrics":

    - Brier skill score against climatology, plus Murphy decomposition, so
      reliability is reported separately from resolution. Raw Brier is retained
      only to satisfy the stated commitment; it is not the headline.
    - Log score and threshold-weighted CRPS on the continuous target.
    - Precision-recall, not ROC.
    - CORP/isotonic reliability with consistency bands. Fixed-bin ECE is
      prohibited at these base rates.
    - All intervals from a stationary block bootstrap.
    - Event windows get the exceedance curve and realized path. No aggregate
      Brier or reliability number on a single event window.

Stdlib only, per the contract's working rules.

Which holdout these are for
---------------------------

The scoring holdout. `repo_model.event_eval` produces the knowledge holdout and
deliberately computes none of this -- the last bullet above is a prohibition on
exactly that, and `EventWindowReport` carries no aggregate field for a number
from here to be written into. Nothing in this module should ever be applied to a
single event window; the honest output there is the exceedance curve and the
realized path, read by a human.

That prohibition is not enforced by a row-count threshold here, because there is
no defensible number to pick and a wrong one would be worse than none. What is
enforced is narrower and real: the decomposition below refuses a sample whose
arithmetic is degenerate -- one outcome class, where uncertainty is zero and
there is no discrimination to realise a share of -- and a ten-day all-stressed
stress window is exactly that. See `_require_scoreable_outcomes`.

How much of the achievable discrimination was realised
------------------------------------------------------

`resolution` is an absolute quantity and it is not readable on its own, because
its ceiling moves with the base rate. On the published conditional run
(`docs/runs/exceedance_gbm_mh61.json`) resolution falls by four orders of
magnitude from the 5bp threshold to the 50bp one -- but so does `uncertainty`,
because exceedances get rarer, and from the two numbers side by side a reader
cannot tell a model that stopped discriminating from a sample that stopped
offering anything to discriminate.

`CorpDecomposition.realized_discrimination` is `resolution / uncertainty`: the
share of the discrimination that was there to be realised that the forecasts
actually realised. It is bounded in `[0, 1]` -- resolution is `UNC` minus the
recalibrated score, and the recalibrated score is between 0 and `UNC` because
the isotonic fit can be neither worse than climatology nor better than perfect
-- so the two ends are meaningful without reference to how rare the event is: 1
is a perfectly discriminating forecast, 0 is one that carries no information
about the outcome at all.

`discrimination_note` names the case where that share rounds to nothing at
`REPORTED_PRECISION_PLACES`, which is the precision the terms are published at.
This exists because the alternative is a table cell reading `0.0000`, which the
reader takes for a small number rather than for none -- and that is what the
generated results table currently prints for resolution at 50bp. A share is not
allowed to reproduce the failure it was added to fix one level up, so where the
share is illegible at the reported precision the return value says so in
words rather than leaving a float for the reader to interpret.

Constant forecasts are the case this describes, and `corp_decomposition`
reports rather than refuses them for that reason. `corp_reliability_curve`
still refuses them: a curve has no place to put a sentence, and a band around a
single point is not a diagram.

Why fixed-bin ECE is absent, and why the decomposition is bin-free
------------------------------------------------------------------

Expected calibration error over fixed probability bins is a biased estimator
whose bias depends on the bin count, and at the base rates here -- exceedances
of 20bp and 50bp are rare -- most bins hold a handful of points or none. The
number moves when the bin count moves, which makes it tunable after the fact by
whoever picks the bins. The contract prohibits it, and
`tests/test_metrics.py::FixedBinECEProhibitionTests` fails the build if it
reappears anywhere in the Python sources.

That prohibition has a consequence people miss: the textbook Murphy
decomposition is *also* binned. Murphy (1973) splits the Brier score as

    BS = reliability - resolution + uncertainty

by partitioning forecasts into groups of equal predicted probability, which on
continuous forecasts means binning, which reintroduces exactly the tunable
quantity that was just prohibited. So the decomposition here is the CORP form
(Dimitriadis, Gneiting and Jordan): the partition is chosen by the pool-adjacent
violators algorithm rather than by hand, which is what "CORP/isotonic" in the
contract's bullet refers to. It satisfies the same identity, reports reliability
separately from resolution as the contract requires, and has nothing to tune.

The three components, in the contract's vocabulary and in CORP's:

    reliability  = MCB, miscalibration. How far the forecasts are from their own
                   recalibrated selves. Lower is better; zero is perfectly
                   calibrated.
    resolution   = DSC, discrimination. How much better the recalibrated
                   forecasts are than climatology. Higher is better.
    uncertainty  = UNC. The Brier score of climatology itself. A property of the
                   sample, not of the model.

    score = reliability - resolution + uncertainty

Why climatology is an argument and never computed here
------------------------------------------------------

`brier_skill_score` requires `climatology` and this module never estimates it
from the outcomes it is scoring. Estimating it in-sample is the contract's
transform-isolation failure wearing different clothes: a learned parameter
fitted on the evaluation rows. It also flatters quietly rather than loudly --
the skill score stays finite and plausible, it just measures the model against a
baseline that already knows the answer.

The decomposition's `uncertainty` term *is* the in-sample base rate, which is
not a contradiction: UNC is defined as a property of the sample being scored,
and reporting it is how a reader sees that a window was easy. It is not a
baseline the model is credited against. `brier_skill_score` is that, and it
takes the number from outside.

Intervals
---------

Every interval in this module comes from `stationary_bootstrap_interval`, the
Politis-Romano stationary bootstrap. Daily repo data is serially dependent --
stress arrives in runs -- and an iid bootstrap on it produces intervals that are
too narrow, which is the failure mode that makes a model look significant when
it is not. `block_length` and `seed` are both required: a default block length
of 1 silently gives the iid bootstrap this exists to avoid, and an unseeded run
is not reproducible, which the contract makes load-bearing.
"""

from __future__ import annotations

import bisect
import math
import random
from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple


__all__ = [
    "REPORTED_PRECISION_PLACES",
    "CorpDecomposition",
    "MetricError",
    "PrecisionRecallCurve",
    "ReliabilityCurve",
    "average_precision",
    "brier_score",
    "brier_skill_score",
    "corp_decomposition",
    "corp_reliability_curve",
    "crps_on_grid",
    "log_score",
    "pinball_loss",
    "crps_from_quantiles",
    "precision_recall_curve",
    "stationary_bootstrap_indices",
    "stationary_bootstrap_interval",
    "threshold_weighted_crps",
]


class MetricError(ValueError):
    """Raised when a metric is asked for on data that cannot support it.

    A raise, not an `assert`: `python -O` strips asserts, and these checks are
    the difference between a reported number and a meaningless one. Same
    reasoning as `repo_model.splits.LookAheadError`, and for the same reason it
    is written out here rather than left to a bare `assert`.
    """


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------


def _validate_probabilities(probabilities: Sequence[float], name: str = "probabilities") -> Tuple[float, ...]:
    checked = []
    for position, value in enumerate(probabilities):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise MetricError(f"{name}[{position}] is not numeric: {value!r}")
        value = float(value)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise MetricError(f"{name}[{position}] is not a probability: {value}")
        checked.append(value)
    if not checked:
        raise MetricError(f"{name} is empty")
    return tuple(checked)


def _validate_outcomes(outcomes: Sequence[float]) -> Tuple[int, ...]:
    """Outcomes are binary. A soft label here would silently change the metric."""

    checked = []
    for position, value in enumerate(outcomes):
        if isinstance(value, bool):
            checked.append(int(value))
            continue
        if not isinstance(value, (int, float)) or value not in (0, 1):
            raise MetricError(
                f"outcomes[{position}] must be 0 or 1, got {value!r}; a soft or "
                "probabilistic label changes what every score below means"
            )
        checked.append(int(value))
    if not checked:
        raise MetricError("outcomes is empty")
    return tuple(checked)


def _paired(probabilities: Sequence[float], outcomes: Sequence[float]):
    forecast = _validate_probabilities(probabilities)
    realized = _validate_outcomes(outcomes)
    if len(forecast) != len(realized):
        raise MetricError(
            f"{len(forecast)} probabilities against {len(realized)} outcomes"
        )
    return forecast, realized


def _require_scoreable_outcomes(
    forecast: Sequence[float], realized: Sequence[int]
) -> None:
    """Refuse a sample whose outcomes are all one class.

    Not a sample-size threshold -- there is no defensible one, and the contract
    handles the ten-day event window structurally instead, by giving
    `EventWindowReport` nowhere to put an aggregate. This is the case where the
    arithmetic is degenerate rather than merely noisy: uncertainty is exactly
    zero, so resolution is measured against a baseline that is already perfect,
    and the share of achievable discrimination is `0 / 0`. A ten-day window with
    no non-stressed day lands here.

    This runs **before** `corp_decomposition` divides, and that order is the
    guard. Divide first and the caller gets a `ZeroDivisionError` naming a line
    of arithmetic instead of a `MetricError` naming a single-class sample and
    pointing at the contract's event-window rule.
    """

    if len(set(realized)) < 2:
        raise MetricError(
            f"all {len(realized)} outcomes are {realized[0]}; a decomposition "
            "against climatology is degenerate on a single-class sample. If this "
            "is one event window, the contract asks for the exceedance curve and "
            "realized path instead of an aggregate"
        )


def _require_decomposable(forecast: Sequence[float], realized: Sequence[int]) -> None:
    """The outcome refusal, plus a refusal of a single distinct forecast value.

    Used by `corp_reliability_curve`, and deliberately **not** by
    `corp_decomposition`. A constant forecast set is not degenerate arithmetic:
    uncertainty is positive, resolution is exactly zero, and reliability is
    `(p - base_rate) ** 2`, which is a real and reportable measurement of how
    far the constant sits from the rate it should have been. The decomposition
    reports that case and names it through `discrimination_note`; the
    reliability curve has nowhere to put a sentence and a consistency band
    around one point is not a diagram, so here it stays a refusal.

    The previous wording of this refusal said reliability and resolution were
    "both zero by construction" on a constant forecast. Resolution is; that is
    what a single isotonic block means. Reliability is not, and the correction
    matters, because it is the whole of what such a sample still has to say.
    """

    _require_scoreable_outcomes(forecast, realized)
    if len(set(forecast)) < 2:
        raise MetricError(
            f"all {len(forecast)} forecasts are {forecast[0]}; the isotonic fit "
            "is a single block, so the curve is one point and resolution is zero "
            "by construction. Use corp_decomposition, which reports this case "
            "and names it, instead of a reliability diagram that cannot"
        )


# --------------------------------------------------------------------------
# Brier score and skill
# --------------------------------------------------------------------------


def brier_score(probabilities: Sequence[float], outcomes: Sequence[float]) -> float:
    """Mean squared error of the probability forecasts.

    Retained because the contract commits to retaining it, and reported as such.
    It is not the headline: a Brier score is dominated by the base rate, so at
    the exceedance rates here two models with very different discrimination
    produce similar-looking numbers. `brier_skill_score` and
    `corp_decomposition` are what should be read.
    """

    forecast, realized = _paired(probabilities, outcomes)
    return sum((p - y) ** 2 for p, y in zip(forecast, realized)) / len(forecast)


def _reference_curve(climatology, rows: int) -> Tuple[float, ...]:
    """The reference forecast, one value per scored row.

    Two shapes, because a climatology is fitted and a fitted thing has a
    training set. A **scalar** is one reference standing behind every row: the
    caller estimated a base rate once, off data it is not scoring. A
    **sequence** is one reference per row, which is what a reference refitted
    fold by fold looks like once the folds are pooled -- the same object the
    scored model is, refitted on the same rows, so that the ratio compares two
    things measured the same way.

    The two admit different values, and the difference is not an oversight:

    * A scalar must be strictly inside `(0, 1)`. A scalar is a *declaration*
      that the event has this rate, and a declared 0 or 1 says the event is
      impossible or certain -- for which the reference Brier score is 0
      whenever the declaration is right, and the ratio is undefined.
    * A sequence element may be exactly 0 or 1. It is not a declaration; it is
      an estimate on one fold's training rows, and
      `baseline.climatology_exceedance` returns a hard 0 above everything it
      was fitted on, deliberately and at length. Refusing that element would
      make the honest early folds of a rolling run unscoreable, and the failure
      it is meant to catch -- a reference that agrees with every outcome -- is
      caught where it actually lives, on the pooled reference score below.
    """

    if isinstance(climatology, (str, bytes)):
        raise MetricError(f"climatology must be a number or a sequence, got {climatology!r}")
    if isinstance(climatology, bool):
        raise MetricError(f"climatology must be a number, got {climatology!r}")
    if isinstance(climatology, (int, float)):
        value = float(climatology)
        if not math.isfinite(value) or not 0.0 < value < 1.0:
            raise MetricError(
                f"climatology must be strictly inside (0, 1), got {value}; at 0 "
                "or 1 the reference Brier score can be 0 and the skill score is undefined"
            )
        return (value,) * rows
    try:
        supplied = tuple(climatology)
    except TypeError as exc:
        raise MetricError(
            f"climatology must be a number or a sequence, got {climatology!r}"
        ) from exc
    curve = _validate_probabilities(supplied, "climatology")
    if len(curve) != rows:
        raise MetricError(
            f"{len(curve)} climatology values against {rows} outcomes; a "
            "per-row reference has one value per scored row, in the same order"
        )
    return curve


def brier_skill_score(
    probabilities: Sequence[float],
    outcomes: Sequence[float],
    *,
    climatology,
) -> float:
    """Brier score against a climatological reference. Higher is better; 0 is no skill.

    Args:
        probabilities: forecast `P(event)`, one per scored row.
        outcomes: the realized 0/1 labels.
        climatology: the reference. **Required, and estimated outside this
            module, from data that is not being scored here.** Computing it
            from `outcomes` would be a learned parameter fitted on the
            evaluation window -- the contract's transform-isolation failure --
            and it fails quietly, because the resulting score stays finite and
            plausible while measuring the model against a baseline that already
            knows the answer. There is deliberately no default.

            Either a single base rate, or one value per scored row. The second
            is what a reference refitted on each fold's training rows looks
            like once the folds are pooled, and it is the only shape in which
            such a reference can be expressed: a rolling run's reference is not
            one number, and collapsing it to one would be exactly the
            asymmetric comparison `rolling_exceedance_backtest` exists to
            avoid. See `_reference_curve` for what each shape admits.

    Raises:
        MetricError: on malformed inputs, on a scalar climatology of exactly 0
            or 1, or when the pooled reference Brier score is 0 -- a reference
            that was right about every scored row, against which no model can
            have measurable skill.
    """

    forecast, realized = _paired(probabilities, outcomes)
    curve = _reference_curve(climatology, len(realized))
    reference = sum((c - y) ** 2 for c, y in zip(curve, realized)) / len(realized)
    if reference == 0.0:
        raise MetricError("reference Brier score is 0; skill is undefined")
    return 1.0 - brier_score(forecast, realized) / reference


# --------------------------------------------------------------------------
# Isotonic regression and the CORP decomposition
# --------------------------------------------------------------------------


def _pool_adjacent_violators(
    values: Sequence[float], weights: Sequence[float]
) -> Tuple[float, ...]:
    """Weighted isotonic regression: the non-decreasing least-squares fit.

    One fitted value per input, inputs assumed already ordered by the covariate.
    The classic PAV stack: append, then merge back while the previous block
    exceeds the new one.
    """

    blocks = []  # [weighted mean, total weight, member count]
    for value, weight in zip(values, weights):
        blocks.append([float(value), float(weight), 1])
        while len(blocks) > 1 and blocks[-2][0] > blocks[-1][0]:
            mean_high, weight_high, count_high = blocks.pop()
            mean_low, weight_low, count_low = blocks.pop()
            total = weight_low + weight_high
            blocks.append(
                [
                    (mean_low * weight_low + mean_high * weight_high) / total,
                    total,
                    count_low + count_high,
                ]
            )
    fitted = []
    for mean, _weight, count in blocks:
        fitted.extend([mean] * count)
    return tuple(fitted)


def _recalibrate(forecast: Sequence[float], realized: Sequence[int]) -> Tuple[float, ...]:
    """CORP recalibration: the isotonic fit of outcomes on forecasts.

    Returned in the caller's original order. Ties in the forecast are pooled
    before the fit, so that two rows carrying the same predicted probability
    always receive the same recalibrated one -- without that, the fit could
    order tied forecasts arbitrarily and the decomposition would depend on the
    input order rather than on the forecasts.
    """

    order = sorted(range(len(forecast)), key=lambda index: forecast[index])

    grouped_values = []
    grouped_weights = []
    members = []
    for index in order:
        if members and forecast[index] == forecast[members[-1][-1]]:
            bucket = members[-1]
            bucket.append(index)
            grouped_values[-1] = sum(realized[i] for i in bucket) / len(bucket)
            grouped_weights[-1] = float(len(bucket))
        else:
            members.append([index])
            grouped_values.append(float(realized[index]))
            grouped_weights.append(1.0)

    fitted_groups = _pool_adjacent_violators(grouped_values, grouped_weights)

    recalibrated = [0.0] * len(forecast)
    for value, bucket in zip(fitted_groups, members):
        for index in bucket:
            recalibrated[index] = value
    return tuple(recalibrated)


REPORTED_PRECISION_PLACES = 4
"""Decimal places the decomposition's terms are published at.

`scripts/emit_results.py` prints resolution to four places in the generated
results table, and that string is the number a reader actually sees. Declared
here rather than read from there, because a metric that learned its own
precision by importing a page generator would change when the page changed.
If the published precision ever moves, this constant is the one edit.
"""


def _discrimination_note(
    resolution: float, uncertainty: float, share: float
) -> Optional[str]:
    """Name a share that rounds to nothing, or return `None`.

    `None` means the share is legible as printed and needs no sentence. It is
    not "no problem found" standing in for "not checked": the share is always
    computed, and this only decides whether the printed float can be read
    without help.
    """

    printed = "%.*f" % (REPORTED_PRECISION_PLACES, share)
    if float(printed) != 0.0:
        return None
    return (
        "no discrimination at the reported precision: the forecasts realised "
        f"{share!r} of the discrimination this sample had available "
        f"({resolution!r} of {uncertainty!r}), which prints as {printed} at the "
        f"{REPORTED_PRECISION_PLACES} decimal places these terms are reported "
        "at. Read that as none rather than as a small amount of it -- the "
        "recalibrated forecasts are climatology to within the reported "
        "precision, so the resolution beside it is a rounding artefact and not "
        "a measurement of weak skill"
    )


@dataclass(frozen=True)
class CorpDecomposition:
    """`score = reliability - resolution + uncertainty`, computed bin-free.

    `reliability` is CORP's MCB and `resolution` is its DSC; the contract's
    requirement is that the two are reported separately, which they are. See the
    module docstring for why the textbook binned form is not used.

    `realized_discrimination` is `resolution / uncertainty`, in `[0, 1]`, and
    `discrimination_note` names it when it rounds to nothing at
    `REPORTED_PRECISION_PLACES`. Both are ordinary fields rather than computed
    properties on purpose: the division has to happen inside
    `corp_decomposition`, after the refusal that makes it safe, so that moving
    it in front of that refusal is a change a test can see.
    """

    score: float
    reliability: float
    resolution: float
    uncertainty: float
    base_rate: float
    n: int
    realized_discrimination: float
    discrimination_note: Optional[str]

    def identity_residual(self) -> float:
        """`score - (reliability - resolution + uncertainty)`. Should be ~0.

        Exposed rather than merely asserted internally so that a caller, and the
        test suite, can check the decomposition adds up on real data instead of
        trusting that it does.
        """

        return self.score - (self.reliability - self.resolution + self.uncertainty)


def corp_decomposition(
    probabilities: Sequence[float], outcomes: Sequence[float]
) -> CorpDecomposition:
    """Split the Brier score into reliability, resolution and uncertainty.

    Also reports what share of the achievable discrimination was realised --
    `resolution / uncertainty` -- and names that share when it rounds to nothing
    at the precision the terms are published at. See the module docstring: an
    absolute resolution is unreadable across thresholds whose base rates differ,
    which is the whole of what the published exceedance record shows.

    A constant forecast set is reported, not refused. It is the case the share
    exists to describe, it still carries a real reliability, and the published
    50bp row is close enough to it that refusing would put a record beyond
    scoring.

    Raises:
        MetricError: on malformed inputs, or on a single-class sample, where
            uncertainty is zero and the share would be `0 / 0`. See
            `_require_scoreable_outcomes` -- and note that a single event window
            is expected to fail it, which is the contract's rule surfacing
            rather than a defect.
    """

    forecast, realized = _paired(probabilities, outcomes)
    # Before the division below, not after. Uncertainty is zero on a
    # single-class sample, and a ZeroDivisionError does not name its cause.
    _require_scoreable_outcomes(forecast, realized)

    recalibrated = _recalibrate(forecast, realized)
    base_rate = sum(realized) / len(realized)

    score = sum((p - y) ** 2 for p, y in zip(forecast, realized)) / len(forecast)
    calibrated_score = sum(
        (p - y) ** 2 for p, y in zip(recalibrated, realized)
    ) / len(realized)
    uncertainty = sum((base_rate - y) ** 2 for y in realized) / len(realized)
    resolution = uncertainty - calibrated_score

    # Unguarded on purpose. A `uncertainty == 0` branch here would return a
    # named "undefined" and leave the refusal above with nothing to catch it,
    # so reordering the two would stop being visible to any test.
    share = resolution / uncertainty

    return CorpDecomposition(
        score=score,
        reliability=score - calibrated_score,
        resolution=resolution,
        uncertainty=uncertainty,
        base_rate=base_rate,
        n=len(forecast),
        realized_discrimination=share,
        discrimination_note=_discrimination_note(resolution, uncertainty, share),
    )


@dataclass(frozen=True)
class ReliabilityCurve:
    """The CORP reliability diagram, with a bootstrap band.

    `lower` and `upper` are empty when no band was requested. When present they
    come from the stationary block bootstrap, per the contract's interval rule,
    and are a confidence band around the fitted curve: they answer "how much of
    this departure from the diagonal survives the serial dependence in the
    data", which is the question worth asking before reporting miscalibration.
    """

    forecast: Tuple[float, ...]
    recalibrated: Tuple[float, ...]
    lower: Tuple[float, ...]
    upper: Tuple[float, ...]
    n: int


def corp_reliability_curve(
    probabilities: Sequence[float],
    outcomes: Sequence[float],
    *,
    block_length: float = None,
    replications: int = 1000,
    level: float = 0.90,
    seed: int = None,
) -> ReliabilityCurve:
    """The isotonic reliability curve, optionally with a consistency band.

    Args:
        probabilities, outcomes: the scored rows.
        block_length: mean block length for the bootstrap band. Omit it (with
            `seed`) for the bare curve; supply both for a band. Required for a
            band and never defaulted, for the reason in the module docstring.
        replications: bootstrap replications.
        level: band coverage, e.g. 0.90.
        seed: required for a band. Reproducibility is load-bearing here.

    Returns:
        A `ReliabilityCurve` sorted by forecast probability.
    """

    forecast, realized = _paired(probabilities, outcomes)
    recalibrated = _recalibrate(forecast, realized)
    order = sorted(range(len(forecast)), key=lambda index: forecast[index])
    sorted_forecast = tuple(forecast[index] for index in order)
    sorted_fit = tuple(recalibrated[index] for index in order)

    if block_length is None and seed is None:
        return ReliabilityCurve(sorted_forecast, sorted_fit, (), (), len(forecast))
    if block_length is None or seed is None:
        raise MetricError(
            "a consistency band needs both block_length and seed; supplying one "
            "without the other is a request for an interval that is either not "
            "block-bootstrapped or not reproducible"
        )

    _require_decomposable(forecast, realized)
    rng = random.Random(seed)
    n = len(forecast)
    replicate_curves = []
    for _ in range(replications):
        indices = stationary_bootstrap_indices(n, block_length, rng)
        resampled_forecast = [forecast[i] for i in indices]
        resampled_outcomes = [realized[i] for i in indices]
        fit = _recalibrate(resampled_forecast, resampled_outcomes)
        # Step-interpolate the replicate's fit back onto the observed grid.
        # The keys are split out here, once per replicate, rather than inside
        # `_step_lookup`: the lookup runs n times per replicate, and building a
        # key list inside it would trade a linear scan for a linear copy.
        pairs = sorted(zip(resampled_forecast, fit))
        keys = [key for key, _ in pairs]
        values = [value for _, value in pairs]
        replicate_curves.append(
            tuple(_step_lookup(keys, values, x) for x in sorted_forecast)
        )

    lower_probability = (1.0 - level) / 2.0
    lower = []
    upper = []
    for position in range(n):
        column = sorted(curve[position] for curve in replicate_curves)
        lower.append(_quantile(column, lower_probability))
        upper.append(_quantile(column, 1.0 - lower_probability))
    return ReliabilityCurve(
        sorted_forecast, sorted_fit, tuple(lower), tuple(upper), n
    )


def _step_lookup(
    keys: Sequence[float], values: Sequence[float], x: float
) -> float:
    """Value of a right-continuous step function at `x`.

    `keys` is ascending and `values[i]` belongs to `keys[i]`. The value at `x`
    is the one belonging to the greatest key `<= x`, so a key exactly equal to
    `x` counts -- that is `bisect_right`, not `bisect_left`. With duplicate
    keys the last of the run wins, which is what the linear scan this replaced
    did and what keeps the step function right-continuous. Below the first key
    the first value is returned, as the scan's initialisation did.

    `bisect_right` rather than a scan because this is called
    `replications * n` times inside `corp_reliability_curve` on a sequence
    already sorted; the scan made that `O(replications * n^2)` and was 78% of
    the exceedance backtest. `StepLookupCostTests` asserts the cost, because a
    scan reinstated here would be correct and the numbers would not move.
    """

    position = bisect.bisect_right(keys, x) - 1
    if position < 0:
        return values[0]
    return values[position]


def _quantile(ordered: Sequence[float], probability: float) -> float:
    """Linear-interpolated quantile of an already-sorted sequence."""

    if not ordered:
        raise MetricError("quantile requires at least one value")
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


# --------------------------------------------------------------------------
# Log score
# --------------------------------------------------------------------------


def log_score(probabilities: Sequence[float], outcomes: Sequence[float]) -> float:
    """Mean negative log likelihood. Lower is better.

    Returns `inf` when the forecast assigned probability 0 to something that
    happened. That is deliberate and is not clipped: clipping replaces an
    infinite loss with an arbitrary finite one chosen by whoever picked the
    clip, which is the tunable-after-the-fact problem again, and it hides
    exactly the failure worth seeing. A model that emits categorical 0 or 1 on
    a stress forecast is making a claim it cannot support, and the score should
    say so rather than round it off.
    """

    forecast, realized = _paired(probabilities, outcomes)
    total = 0.0
    for probability, outcome in zip(forecast, realized):
        likelihood = probability if outcome == 1 else 1.0 - probability
        if likelihood <= 0.0:
            return math.inf
        total -= math.log(likelihood)
    return total / len(forecast)


# --------------------------------------------------------------------------
# Continuous target: pinball, CRPS, threshold-weighted CRPS
# --------------------------------------------------------------------------


def pinball_loss(level: float, predicted: float, observed: float) -> float:
    """Quantile loss at `level`. The contract fixes the levels across models."""

    if not 0.0 < level < 1.0:
        raise MetricError(f"quantile level must be in (0, 1), got {level}")
    difference = observed - predicted
    return level * difference if difference >= 0 else (level - 1.0) * difference


def crps_from_quantiles(
    levels: Sequence[float],
    predicted: Sequence[float],
    observed: float,
) -> float:
    """CRPS approximated from a quantile vector, via the pinball identity.

    `CRPS = 2 * integral of the quantile loss over levels`, so the mean pinball
    loss across the declared levels times two is the Riemann approximation of it
    on the grid the contract fixes. It is an approximation, and the error is a
    function of how coarse that grid is -- but the grid is fixed across all
    models by the forecast interface, so the approximation is the same one for
    every model and the comparison it supports is sound.
    """

    grid = _validate_levels(levels)
    values = [float(value) for value in predicted]
    if len(values) != len(grid):
        raise MetricError(f"{len(grid)} levels against {len(values)} quantiles")
    for position in range(1, len(values)):
        if values[position] < values[position - 1]:
            raise MetricError(
                f"quantiles cross: level {grid[position - 1]} predicts "
                f"{values[position - 1]} but level {grid[position]} predicts "
                f"{values[position]}"
            )
    return 2.0 * sum(
        pinball_loss(level, value, observed) for level, value in zip(grid, values)
    ) / len(grid)


def _validate_levels(levels: Sequence[float]) -> Tuple[float, ...]:
    grid = tuple(float(level) for level in levels)
    if not grid:
        raise MetricError("no quantile levels declared")
    for position, level in enumerate(grid):
        if not 0.0 < level < 1.0:
            raise MetricError(f"level {position} is {level}, must be in (0, 1)")
        if position and level <= grid[position - 1]:
            raise MetricError("quantile levels must be strictly ascending")
    return grid


def _validate_grid(thresholds: Sequence[float], exceedance: Sequence[float]):
    grid = tuple(float(threshold) for threshold in thresholds)
    if len(grid) < 2:
        raise MetricError("a threshold grid needs at least two thresholds to integrate over")
    for position in range(1, len(grid)):
        if grid[position] <= grid[position - 1]:
            raise MetricError("thresholds must be strictly ascending")
    if not all(math.isfinite(threshold) for threshold in grid):
        raise MetricError("thresholds must be finite")
    curve = _validate_probabilities(exceedance, "exceedance")
    if len(curve) != len(grid):
        raise MetricError(f"{len(grid)} thresholds against {len(curve)} probabilities")
    for position in range(1, len(curve)):
        if curve[position] > curve[position - 1]:
            raise MetricError(
                f"exceedance rises from threshold {grid[position - 1]} to "
                f"{grid[position]}; P(Y > tau) cannot increase with tau"
            )
    return grid, curve


def crps_on_grid(
    thresholds: Sequence[float],
    exceedance: Sequence[float],
    observed: float,
) -> float:
    """Unweighted CRPS on a threshold grid, from an exceedance curve.

    `CRPS = integral (F(z) - 1{observed <= z})^2 dz`, with `F(z) = 1 - P(Y > z)`
    read off the declared tau family, integrated by the trapezoid rule. This is
    the same predictive object `repo_model.event_eval` reports as a curve, so
    the pooled evaluation and the event report are reading one thing.

    The integral is truncated to the grid, so it is a lower bound on the true
    CRPS and comparable only across models sharing the grid -- which the
    contract guarantees, since the tau family is declared once.
    """

    return _integrate_squared_error(thresholds, exceedance, observed, None)


def threshold_weighted_crps(
    thresholds: Sequence[float],
    exceedance: Sequence[float],
    observed: float,
    weights: Sequence[float],
) -> float:
    """twCRPS: `integral w(z) (F(z) - 1{observed <= z})^2 dz`.

    The contract's headline continuous-target score. `weights` is required and
    has no default: an unweighted CRPS is a different metric with a different
    name (`crps_on_grid`), and silently defaulting the weights to 1 would report
    it under this one. Weighting toward the upper tau puts the score where the
    question is -- the interesting failure is a model that is comfortable
    everywhere and wrong at 50bp.
    """

    if weights is None:
        raise MetricError(
            "weights are required; for the unweighted score call crps_on_grid, "
            "which says in its name what it is"
        )
    return _integrate_squared_error(thresholds, exceedance, observed, weights)


def _integrate_squared_error(thresholds, exceedance, observed, weights) -> float:
    grid, curve = _validate_grid(thresholds, exceedance)

    if weights is None:
        applied = [1.0] * len(grid)
    else:
        applied = [float(weight) for weight in weights]
        if len(applied) != len(grid):
            raise MetricError(f"{len(grid)} thresholds against {len(applied)} weights")
        for position, weight in enumerate(applied):
            if not math.isfinite(weight) or weight < 0.0:
                raise MetricError(f"weight {position} is {weight}; must be finite and >= 0")
        if not any(applied):
            raise MetricError("all weights are 0; the score would be 0 for every model")

    if isinstance(observed, bool) or not isinstance(observed, (int, float)):
        raise MetricError(f"observed is not numeric: {observed!r}")
    observed = float(observed)
    if not math.isfinite(observed):
        raise MetricError("observed is not finite")

    def integrand(position: int) -> float:
        cdf = 1.0 - curve[position]
        indicator = 1.0 if observed <= grid[position] else 0.0
        return applied[position] * (cdf - indicator) ** 2

    total = 0.0
    for position in range(1, len(grid)):
        width = grid[position] - grid[position - 1]
        total += 0.5 * width * (integrand(position - 1) + integrand(position))
    return total


# --------------------------------------------------------------------------
# Precision-recall
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PrecisionRecallCurve:
    """Thresholds with the precision and recall each achieves.

    ROC is deliberately absent, per the contract. At these base rates the false
    positive rate has a very large denominator, so a model can move from useless
    to useful with almost no visible change in ROC, and the area under it stays
    high because true negatives are abundant and free. Precision against recall
    asks the question that matters: of the days flagged as stressed, how many
    were, and of the stressed days, how many were flagged.
    """

    thresholds: Tuple[float, ...]
    precision: Tuple[float, ...]
    recall: Tuple[float, ...]
    base_rate: float
    n: int


def precision_recall_curve(
    probabilities: Sequence[float], outcomes: Sequence[float]
) -> PrecisionRecallCurve:
    """Precision and recall at every threshold the forecasts actually take.

    Thresholds are the distinct forecast values, descending, so the curve has a
    point wherever the classification could change and none where it could not.
    Precision at a threshold that flags nothing is reported as 1.0 by the usual
    convention, with recall 0.
    """

    forecast, realized = _paired(probabilities, outcomes)
    positives = sum(realized)
    if positives == 0:
        raise MetricError(
            "no positive outcomes; precision-recall is undefined without them, "
            "and a window with no stressed day cannot evidence stress forecasting"
        )

    ordered = sorted(range(len(forecast)), key=lambda index: -forecast[index])
    thresholds = []
    precision = []
    recall = []
    true_positives = 0
    flagged = 0
    for position, index in enumerate(ordered):
        flagged += 1
        true_positives += realized[index]
        is_last = position + 1 == len(ordered)
        if not is_last and forecast[ordered[position + 1]] == forecast[index]:
            continue  # only emit a point where the threshold can actually cut
        thresholds.append(forecast[index])
        precision.append(true_positives / flagged)
        recall.append(true_positives / positives)

    return PrecisionRecallCurve(
        thresholds=tuple(thresholds),
        precision=tuple(precision),
        recall=tuple(recall),
        base_rate=positives / len(realized),
        n=len(forecast),
    )


def average_precision(
    probabilities: Sequence[float], outcomes: Sequence[float]
) -> float:
    """Area under the precision-recall curve, by the step-sum convention.

    `sum (R_k - R_{k-1}) * P_k`, which does not interpolate between points --
    interpolating a PR curve is optimistic, because the segment between two
    achievable operating points is not itself achievable.

    The no-skill reference is the base rate, not 0.5. An average precision of
    0.1 against a base rate of 0.02 is a real result; the same number against a
    base rate of 0.1 is nothing at all, so report `base_rate` beside it.
    """

    curve = precision_recall_curve(probabilities, outcomes)
    total = 0.0
    previous_recall = 0.0
    for precision, recall in zip(curve.precision, curve.recall):
        total += (recall - previous_recall) * precision
        previous_recall = recall
    return total


# --------------------------------------------------------------------------
# Stationary block bootstrap
# --------------------------------------------------------------------------


def stationary_bootstrap_indices(
    n: int, block_length: float, rng: random.Random
) -> Tuple[int, ...]:
    """One Politis-Romano stationary bootstrap resample of `range(n)`.

    Blocks have geometric length with mean `block_length` and wrap at the end of
    the series, which is what makes the resampled series stationary -- a
    fixed-block bootstrap is not, because positions near a block boundary are
    treated differently from positions in the middle.

    Args:
        n: series length.
        block_length: mean block length, `>= 1`. Size it to the serial
            dependence in the scored series; 1 is the iid bootstrap and should
            be chosen explicitly if it is what is wanted.
        rng: a seeded `random.Random`. Passed in rather than created here so a
            caller can drive many resamples from one reproducible stream.
    """

    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise MetricError(f"n must be a positive int, got {n!r}")
    if isinstance(block_length, bool) or not isinstance(block_length, (int, float)):
        raise MetricError(f"block_length must be a number, got {block_length!r}")
    block_length = float(block_length)
    if not math.isfinite(block_length) or block_length < 1.0:
        raise MetricError(
            f"block_length must be at least 1, got {block_length}; below 1 the "
            "restart probability exceeds 1 and the geometric length is undefined"
        )

    restart_probability = 1.0 / block_length
    indices = []
    current = rng.randrange(n)
    for _ in range(n):
        indices.append(current)
        if rng.random() < restart_probability:
            current = rng.randrange(n)
        else:
            current = (current + 1) % n
    return tuple(indices)


def stationary_bootstrap_interval(
    statistic: Callable[[Sequence[int]], float],
    n: int,
    *,
    block_length: float,
    seed: int,
    replications: int = 2000,
    level: float = 0.90,
) -> Tuple[float, float]:
    """Percentile interval for `statistic`, from the stationary block bootstrap.

    Every interval this project reports comes through here, per the contract.

    Args:
        statistic: called with a resampled index sequence and returns the
            statistic on those rows. Taking indices rather than data lets one
            call cover a statistic over several aligned series -- forecasts and
            outcomes, say -- resampled together, which is required: resampling
            them independently would destroy the pairing the score is computed
            from.
        n: length of the series being resampled.
        block_length: mean block length. Required; see the module docstring.
        seed: required. An interval that cannot be reproduced cannot be checked.
        replications: bootstrap replications.
        level: coverage, e.g. 0.90 for a 5th-95th percentile interval.

    Returns:
        `(lower, upper)`.

    Raises:
        MetricError: on bad arguments, or if `statistic` returns a non-finite
            value on a resample -- which usually means the statistic is
            undefined on a sample that happened to contain no positive outcome,
            and silently dropping those replicates would narrow the interval.
    """

    if not callable(statistic):
        raise MetricError("statistic must be callable")
    if isinstance(replications, bool) or not isinstance(replications, int) or replications < 2:
        raise MetricError(f"replications must be an int >= 2, got {replications!r}")
    if not 0.0 < level < 1.0:
        raise MetricError(f"level must be in (0, 1), got {level}")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise MetricError(
            f"seed must be an int, got {seed!r}; an unseeded interval is not "
            "reproducible, and reproducibility is load-bearing here"
        )

    rng = random.Random(seed)
    draws = []
    for replication in range(replications):
        indices = stationary_bootstrap_indices(n, block_length, rng)
        value = statistic(indices)
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise MetricError(
                f"statistic returned {value!r} on bootstrap replication "
                f"{replication}; discarding such replicates would narrow the "
                "interval, so this raises instead"
            )
        draws.append(float(value))

    draws.sort()
    tail = (1.0 - level) / 2.0
    return _quantile(draws, tail), _quantile(draws, 1.0 - tail)
