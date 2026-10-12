"""Group-conditional recalibration of a pressure probability (#380, track C of #374).

Track C asks whether recalibrating the current model's exceedance probability,
per threshold and horizon, is enough. `probability_calibration` supplies the
pooled curves (isotonic, Platt). This module adds the conditional ones, whose
curve may depend on the day's group, read as of the decision instant:

* the **group** is the reserve-scarcity state band (`scarcity.py`: 0 and 1 are
  `ample`, 2 and 3 are `scarce`, no state is `unknown`) crossed with the
  pressure-day type (`scheduled` for a quarter-end, month-end or tax date,
  otherwise `ordinary`), the scarcity-conditioned calendar of #128 reduced to
  cells that hold enough pairs to fit a curve;
* `group`: a Platt curve (the published recalibration's family) fitted on the
  target group's own earlier pairs, falling back to the pooled Platt curve when
  the group holds fewer than `GROUP_MINIMUM_PAIRS` pairs or `GROUP_MINIMUM_EVENTS`
  events. The group-conditional analogue of the conditional conformal
  calibration of Gibbs, Cherian and Candes (2023), whose function class is the
  group indicators, with the quantile step replaced by a probability curve;
* `weighted`: one Platt curve on every earlier pair, the target group's pairs
  weighted 1 and all others `OTHER_GROUP_WEIGHT`, a regime-weighted calibration
  after Barber et al. (2023, "Conformal prediction beyond exchangeability").

**Walk-forward**, as `probability_calibration.walk_forward`: a refit block's
forecasts use only the pairs whose scored day is at or before the block's last
training label, and nothing is fitted before the pooled gate
(`pc.MINIMUM_PAIRS` pairs and `pc.MINIMUM_EVENTS` events), so every method
starts on the day the published recalibration does. `fit` and `weighted` refuse
a later pair with `LookAheadError`.

Every constant was declared before any scoring and none was searched. Standard
library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from datetime import date
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import probability_calibration as pc
from .baseline import _logistic_fit
from .splits import LookAheadError

__all__ = [
    "GROUP_MINIMUM_EVENTS",
    "GROUP_MINIMUM_PAIRS",
    "MODES",
    "OTHER_GROUP_WEIGHT",
    "SHRINKAGE_PRECISION",
    "declaration",
    "fit",
    "fit_floor",
    "fit_shrunk",
    "group_label",
    "regime_walk_forward",
    "require_observable",
    "scarcity_state_label",
    "require_regimes_asof",
    "walk_forward",
    "walk_forward_floor",
    "walk_forward_shrunk",
]

MODES = ("group", "weighted")

#: A group's own curve needs this many earlier pairs...
GROUP_MINIMUM_PAIRS = 60
#: ...and this many events among them (and one non-event); otherwise the pooled curve.
GROUP_MINIMUM_EVENTS = 3
#: The weight of a pair outside the target group in `weighted` mode.
OTHER_GROUP_WEIGHT = 0.25

#: The ridge precision on a group's intercept offset in `fit_shrunk` (#589): a prior of standard deviation 1 on the
#: log-odds scale, declared before any scoring and not searched.
SHRINKAGE_PRECISION = 1.0

_STATE_BANDS = {0: "ample", 1: "ample", 2: "scarce", 3: "scarce"}


def declaration() -> dict:
    """Every constant the conditional recalibrators run with, as a result names them."""

    return {
        "modes": list(MODES),
        "groups": "reserve-scarcity state band (0-1 ample, 2-3 scarce, none unknown) x day type "
        "(scheduled: quarter_end, month_end, tax_date; else ordinary), read as of the decision instant",
        "group_minimum_pairs": GROUP_MINIMUM_PAIRS,
        "group_minimum_events": GROUP_MINIMUM_EVENTS,
        "other_group_weight": OTHER_GROUP_WEIGHT,
        "gate": f"identity until the pooled pairs number {pc.MINIMUM_PAIRS} and hold {pc.MINIMUM_EVENTS} events",
    }


def group_label(state: Optional[float], day_type: str) -> str:
    """`band|kind` for a scarcity state (0 to 3, or None) and a pressure-day type.

    Raises:
        ValueError: for a state that is not 0, 1, 2, 3 or None.
    """

    if state is None:
        band = "unknown"
    else:
        try:
            band = _STATE_BANDS[int(state)]
        except KeyError:
            raise ValueError(f"reserve-scarcity state {state!r} is not 0 to 3") from None
        if int(state) != state:
            raise ValueError(f"reserve-scarcity state {state!r} is not 0 to 3")
    return f"{band}|{'ordinary' if day_type == 'ordinary' else 'scheduled'}"


def scarcity_state_label(state: Optional[float]) -> str:
    """The group label of an as-of reserve-scarcity state: `0` to `3`, or `unknown` for none (#515).

    Raises:
        ValueError: for a state that is not 0, 1, 2, 3 or None.
    """

    if state is None:
        return "unknown"
    if state not in (0, 1, 2, 3):
        raise ValueError(f"reserve-scarcity state {state!r} is not 0 to 3")
    return str(int(state))


def require_observable(pairs: Sequence[Tuple[date, float, int, str]], fitted_at: date) -> None:
    """Refuse a pair whose scored day is after the curve's fitting date.

    Raises:
        LookAheadError: its outcome was not observable when the curve was fitted.
    """

    late = [when for when, _, _, _ in pairs if when > fitted_at]
    if late:
        raise LookAheadError(
            f"a group-conditional curve fitted at {fitted_at} was handed the outcome of {late[0]}, "
            f"after its fitting date"
        )


def _events_ok(ys: Sequence[int], minimum_pairs: int, minimum_events: int) -> bool:
    events = sum(ys)
    return len(ys) >= minimum_pairs and minimum_events <= events < len(ys)


def fit(
    mode: str,
    pairs: Sequence[Tuple[date, float, int, str]],
    fitted_at: date,
    *,
    target_group: str,
    other_weight: float = OTHER_GROUP_WEIGHT,
    minimum_pairs: int = GROUP_MINIMUM_PAIRS,
    minimum_events: int = GROUP_MINIMUM_EVENTS,
) -> Callable[[float], float]:
    """The `mode` curve for `target_group`, fitted on `(day, forecast, outcome, group)` pairs.

    Raises:
        LookAheadError: if a pair's scored day is after `fitted_at`.
        ValueError: for a mode not in `MODES`.
    """

    if mode not in MODES:
        raise ValueError(f"unknown conditional recalibrator {mode!r}; expected one of {MODES}")
    require_observable(pairs, fitted_at)
    if mode == "group":
        own = [(p, y) for _, p, y, g in pairs if g == target_group]
        if _events_ok([y for _, y in own], minimum_pairs, minimum_events):
            return pc._platt(own)
        return pc._platt([(p, y) for _, p, y, _ in pairs])
    count = len(pairs)
    raw = [1.0 if g == target_group else other_weight for _, _, _, g in pairs]
    scale = count / sum(raw)
    b0, b1 = pc._weighted_logistic(
        [pc._logit(p) for _, p, _, _ in pairs], [y for _, _, y, _ in pairs], [w * scale for w in raw]
    )
    return lambda p: pc._sigmoid(b0 + b1 * pc._logit(p))


def walk_forward(
    mode: str,
    forecasts: Sequence[float],
    outcomes: Sequence[int],
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
    groups: Sequence[str],
) -> Tuple[float, ...]:
    """Every forecast recalibrated by `mode`, each block from its observable past.

    Raises:
        ValueError: for an unknown mode or a `groups` column of another length.
    """

    if mode not in MODES:
        raise ValueError(f"unknown conditional recalibrator {mode!r}; expected one of {MODES}")
    if not len(forecasts) == len(outcomes) == len(scored_dates) == len(train_ends) == len(groups):
        raise ValueError("forecasts, outcomes, dates, train ends and groups must be one per scored day")
    column = [float(p) for p in forecasts]
    for start, stop, end in pc.blocks(scored_dates, train_ends):
        past = pc.past_positions(scored_dates, train_ends, start)
        if not pc._ready(outcomes, past):
            continue
        pairs = [(scored_dates[i], forecasts[i], outcomes[i], groups[i]) for i in past]
        curves: Dict[str, Callable[[float], float]] = {}
        for index in range(start, stop):
            group = groups[index]
            if group not in curves:
                curves[group] = fit(mode, pairs, end, target_group=group)
            column[index] = curves[group](forecasts[index])
    return tuple(column)


def require_regimes_asof(scored_dates: Sequence[date], regimes: Sequence[str], splits) -> None:
    """Refuse a regime label that is not the declared calendar's for its day.

    A regime is as-of when it is read off the date (`metadata/evaluation_splits.json`), known at the
    decision instant. A label assigned from realised outcomes would put the outcome in the curve's key.

    Raises:
        LookAheadError: a day's label differs from the declared calendar's regime for that day.
        ValueError: the labels are not one per scored day.
    """

    if len(scored_dates) != len(regimes):
        raise ValueError("regime labels must be one per scored day")
    wrong = [(day, label) for day, label in zip(scored_dates, regimes) if splits.regime(day) != label]
    if wrong:
        raise LookAheadError(
            f"regime label {wrong[0][1]!r} for {wrong[0][0]} is not the declared calendar's "
            f"{splits.regime(wrong[0][0])!r}; a regime must be read as of the decision instant"
        )


def regime_walk_forward(
    forecasts: Sequence[float],
    outcomes: Sequence[int],
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
    regimes: Sequence[str],
    splits,
) -> Tuple[float, ...]:
    """Platt per declared regime (#471): `walk_forward('group')` with the regime as the group.

    Each refit block fits one curve per regime on that regime's earlier observable pairs, and the
    pooled curve when the regime holds fewer than `GROUP_MINIMUM_PAIRS` pairs or `GROUP_MINIMUM_EVENTS`
    events, so a regime's first days are pooled until it has its own record.

    Raises:
        LookAheadError: a regime label is not the declared calendar's for its day.
        ValueError: as `walk_forward`.
    """

    require_regimes_asof(scored_dates, regimes, splits)
    return walk_forward("group", forecasts, outcomes, scored_dates, train_ends, regimes)


def fit_shrunk(
    pairs: Sequence[Tuple[date, float, int, str]],
    fitted_at: date,
    *,
    precision: float = SHRINKAGE_PRECISION,
) -> Callable[[float, str], float]:
    """A pooled Platt curve with one shrunk intercept offset per group (#589), fitted on `(day, forecast, outcome, group)`.

    The slope and intercept are the pooled Platt fit on every pair. Each group then gets an offset `u` on the log-odds scale,
    the maximiser of its own log likelihood minus `precision * u**2 / 2`, so a group with few pairs or events keeps an offset
    near zero (the pooled curve) and a group with many may depart from it: a hierarchical intercept with a normal prior,
    after Gelman and Hill (2007). A group with no pair gets the pooled curve.

    Raises:
        LookAheadError: if a pair's scored day is after `fitted_at`.
        ValueError: if `precision` is not positive.
    """

    if not precision > 0.0:
        raise ValueError(f"the shrinkage precision must be positive, got {precision!r}")
    require_observable(pairs, fitted_at)
    b0, b1 = _logistic_fit([pc._logit(p) for _, p, _, _ in pairs], [y for _, _, y, _ in pairs])
    scores: Dict[str, List[Tuple[float, int]]] = {}
    for _, p, y, g in pairs:
        scores.setdefault(g, []).append((b0 + b1 * pc._logit(p), y))
    offsets: Dict[str, float] = {}
    for group, items in scores.items():
        u = 0.0
        for _ in range(100):
            probabilities = [pc._sigmoid(z + u) for z, _ in items]
            gradient = sum(y - q for (_, y), q in zip(items, probabilities)) - precision * u
            curvature = sum(q * (1.0 - q) for q in probabilities) + precision
            step = gradient / curvature
            u += step
            if abs(step) < 1e-12:
                break
        offsets[group] = u
    return lambda p, group: pc._sigmoid(b0 + b1 * pc._logit(p) + offsets.get(group, 0.0))


def walk_forward_shrunk(
    forecasts: Sequence[float],
    outcomes: Sequence[int],
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
    groups: Sequence[str],
    *,
    precision: float = SHRINKAGE_PRECISION,
) -> Tuple[float, ...]:
    """Every forecast through `fit_shrunk`, each refit block from its observable past, identity before the pooled gate.

    Raises:
        ValueError: for a `groups` column (or another) of another length.
    """

    if not len(forecasts) == len(outcomes) == len(scored_dates) == len(train_ends) == len(groups):
        raise ValueError("forecasts, outcomes, dates, train ends and groups must be one per scored day")
    column = [float(p) for p in forecasts]
    for start, stop, end in pc.blocks(scored_dates, train_ends):
        past = pc.past_positions(scored_dates, train_ends, start)
        if not pc._ready(outcomes, past):
            continue
        curve = fit_shrunk(
            [(scored_dates[i], forecasts[i], outcomes[i], groups[i]) for i in past], end, precision=precision
        )
        for index in range(start, stop):
            column[index] = curve(forecasts[index], groups[index])
    return tuple(column)


def fit_floor(
    pairs: Sequence[Tuple[date, float, int, str]],
    fitted_at: date,
    *,
    target_group: Optional[str] = None,
    minimum_pairs: int = GROUP_MINIMUM_PAIRS,
    minimum_events: int = GROUP_MINIMUM_EVENTS,
) -> Optional[float]:
    """The floor for a day that is not a risk date, from `(day, forecast, outcome, group)` pairs of such days (#606).

    The pooled rate of pressure days among the pairs; with a `target_group`, that group's own rate once it holds
    `minimum_pairs` pairs and `minimum_events` events, the pooled rate before. None while the pooled pairs number fewer than
    `minimum_pairs`.

    Raises:
        LookAheadError: if a pair's scored day is after `fitted_at`.
    """

    require_observable(pairs, fitted_at)
    if len(pairs) < minimum_pairs:
        return None
    pooled = sum(y for _, _, y, _ in pairs) / len(pairs)
    if target_group is None:
        return pooled
    own = [y for _, _, y, g in pairs if g == target_group]
    return sum(own) / len(own) if len(own) >= minimum_pairs and sum(own) >= minimum_events else pooled


def walk_forward_floor(
    forecasts: Sequence[float],
    outcomes: Sequence[int],
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
    off_risk: Sequence[bool],
    groups: Optional[Sequence[str]] = None,
    *,
    minimum_pairs: int = GROUP_MINIMUM_PAIRS,
    minimum_events: int = GROUP_MINIMUM_EVENTS,
) -> Tuple[float, ...]:
    """A floor under the forecasts of the days that are not risk dates (#606), each refit block from its observable past.

    A risk-date row forecasts exactly 0 on a day that is not a risk date, and a pressure day on such a day is then a pure
    miss. The floor of a block is `fit_floor` on the earlier pairs that were off the risk dates and observable when the
    block was fitted (`pc.past_positions`). A forecast is raised to the floor, never lowered, and a risk date keeps its
    forecast.

    Raises:
        ValueError: for columns of different lengths.
    """

    lengths = [len(forecasts), len(outcomes), len(scored_dates), len(train_ends), len(off_risk)]
    if groups is not None:
        lengths.append(len(groups))
    if len(set(lengths)) != 1:
        raise ValueError("forecasts, outcomes, dates, train ends, risk flags and groups must be one per scored day")
    column = [float(p) for p in forecasts]
    for start, stop, end in pc.blocks(scored_dates, train_ends):
        past = [i for i in pc.past_positions(scored_dates, train_ends, start) if off_risk[i]]
        pairs = [(scored_dates[i], forecasts[i], outcomes[i], groups[i] if groups is not None else "") for i in past]
        floors: Dict[str, Optional[float]] = {}
        for index in range(start, stop):
            if not off_risk[index]:
                continue
            group = groups[index] if groups is not None else ""
            if group not in floors:
                floors[group] = fit_floor(
                    pairs, end, target_group=group if groups is not None else None,
                    minimum_pairs=minimum_pairs, minimum_events=minimum_events,
                )
            if floors[group] is not None:
                column[index] = max(column[index], floors[group])
    return tuple(column)
