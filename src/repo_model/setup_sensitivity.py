"""Sensitivity of the pressure-day judge's results to four features of its setup (#482).

Reported-only measurements on top of the judge of #375 as amended by #407. They change no rule and no published figure,
and read scored days before 2026-01-01 only (`docs/decisions/lockbox.md`). The declaration is
`metadata/setup_sensitivity.json`. This module holds the arithmetic; `scripts/setup_sensitivity.py` reads the forecasts.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Callable, Dict, List, Mapping, Optional, Sequence

from . import pressure_judge as pj
from .splits import LookAheadError


def downweights(in_period: Sequence[bool], share: float) -> List[float]:
    """Weights that give the days in the period `share` of the window's total weight.

    Days outside the period weigh 1; days in it weigh the same as each other, so that their weight is `share` of
    the whole. A window with no day on one side cannot be rebalanced and weighs every day 1.

    Raises:
        ValueError: if `share` is not strictly between 0 and 1.
    """

    if not 0.0 < share < 1.0:
        raise ValueError(f"the period's share of all days must be strictly between 0 and 1, not {share}")
    inside = sum(1 for flag in in_period if flag)
    outside = len(in_period) - inside
    if not inside or not outside:
        return [1.0] * len(in_period)
    weight = share / (1.0 - share) * outside / inside
    return [weight if flag else 1.0 for flag in in_period]


def period_weights(first: date, last: date, share: float) -> Callable[[Sequence[date]], List[float]]:
    """`downweights` for the days in `first`..`last`, as a function of a fit's training days (#518).

    The refit of a model takes the label days of its training pairs and returns one weight per pair, so that the
    period carries `share` of the fit's total weight. A fit whose pairs are all inside the period, or all outside it,
    weighs every pair 1: the rule rebalances the period against the rest, and with nothing to rebalance against it is
    the identity (the window of every refit that ends before 2020).
    """

    def weigh(days: Sequence[date]) -> List[float]:
        return downweights([first <= day <= last for day in days], share)

    return weigh


def select_cutoff_weighted(
    limit: float,
    *,
    days: Sequence[date],
    probabilities: Sequence[float],
    pressure: Sequence[int],
    onset: Sequence[int],
    weights: Sequence[float],
    training_end: Optional[date],
) -> float:
    """`pressure_judge.select_cutoff` with every onset and every false alarm counted at its day's weight.

    The cut-off with the highest weighted onset recall whose weighted false alarms per weighted onset are at most
    `limit`; of equal recall the highest. With every weight 1 it is `pressure_judge.select_cutoff`.

    Raises:
        LookAheadError: if a day of the window is after `training_end`, or there is a day and no training end.
        ValueError: if the series differ in length, or a weight is not positive.
    """

    if not len(days) == len(probabilities) == len(pressure) == len(onset) == len(weights):
        raise ValueError("the cut-off window needs one probability, outcome, onset flag and weight per day")
    if any(not w > 0 for w in weights):
        raise ValueError("every weight must be positive")
    if days:
        late = [day for day in days if training_end is None or day > training_end]
        if late:
            raise LookAheadError(
                f"cut-off chosen from {len(late)} day(s) from {min(late)} on, after the refit's "
                f"training end ({training_end}); a flag cut-off is chosen on training data only"
            )
    onsets = sum(w for w, o in zip(weights, onset) if o)
    if not onsets:
        return math.inf
    by_value: Dict[float, List[int]] = {}
    for index, p in enumerate(probabilities):
        by_value.setdefault(p, []).append(index)
    caught, false_alarms = 0.0, 0.0
    best_recall, best = 0.0, math.inf
    for value in sorted(by_value, reverse=True):
        for index in by_value[value]:
            if onset[index]:
                caught += weights[index]
            elif not pressure[index]:
                false_alarms += weights[index]
        if false_alarms / onsets > limit + 1e-12:
            break
        if caught > best_recall + 1e-12:
            best_recall, best = caught, value
    return best


def choose_cutoffs_with(
    declaration: pj.Declaration,
    grids: Mapping[int, pj.Grid],
    forecasts: Sequence[pj.Forecast],
    calendar: Sequence[date],
    selector: Callable[..., float],
) -> List[pj.Forecast]:
    """`pressure_judge.choose_cutoffs` with the cut-off of each block chosen by `selector`.

    `selector(days=, probabilities=, pressure=, onset=, training_end=)` sees the block's training window exactly as
    `pressure_judge.select_cutoff` does: the forecast's own earlier probabilities on the scored days whose outcome was
    known at the block's first decision instant. The refit cadence is the declaration's `cutoff_refit_every`.
    """

    position = {day: k for k, day in enumerate(calendar)}
    step = declaration.cutoff_refit_every
    out = []
    for forecast in forecasts:
        grid = grids[forecast.horizon]
        if tuple(forecast.dates) != tuple(grid.dates):
            raise ValueError(f"{forecast.name!r} h = {forecast.horizon}: forecasts are not on the grid's days")
        cutoffs: Dict[float, List[float]] = {tau: [] for tau in declaration.thresholds}
        for start in range(0, len(forecast.dates), step):
            block = forecast.dates[start : start + step]
            last_known = position[block[0]] - forecast.horizon - 1
            training_end = calendar[last_known] if last_known >= 0 else None
            window = [k for k in range(start) if training_end is not None and forecast.dates[k] <= training_end]
            for tau in declaration.thresholds:
                value = selector(
                    days=[forecast.dates[k] for k in window],
                    probabilities=[forecast.probabilities[tau][k] for k in window],
                    pressure=[grid.outcomes[tau][k] for k in window],
                    onset=[grid.onset_at(tau, declaration.primary)[k] for k in window],
                    training_end=training_end,
                )
                cutoffs[tau].extend([value] * len(block))
        out.append(
            pj.Forecast(
                name=forecast.name,
                horizon=forecast.horizon,
                dates=forecast.dates,
                probabilities=forecast.probabilities,
                cutoffs={tau: tuple(column) for tau, column in cutoffs.items()},
                cutoff_rule=declaration.sha256,
                cutoff_weighting=None,
            )
        )
    return out


def tier_one_by_group(
    groups: Sequence[str],
    onset: Sequence[int],
    caught: Sequence[int],
    alarms_by_horizon: Mapping[int, Sequence[int]],
) -> Dict[str, dict]:
    """Tier 1's counts in each group of days: onsets, onsets flagged at some horizon, false alarms per onset.

    `alarms_by_horizon[h][k]` is 1 when day k is a false alarm at horizon h. The worst horizon's count per onset is
    reported, as the tier does; a group with no onset has no rate.
    """

    out: Dict[str, dict] = {}
    for label in sorted(set(groups)):
        members = [k for k, g in enumerate(groups) if g == label]
        onsets = sum(onset[k] for k in members)
        counts = {h: sum(column[k] for k in members) for h, column in alarms_by_horizon.items()}
        worst = max(counts.values()) if counts else 0
        out[label] = {
            "days": len(members),
            "onsets": onsets,
            "onsets_flagged": sum(onset[k] * caught[k] for k in members),
            "recall": (sum(onset[k] * caught[k] for k in members) / onsets) if onsets else None,
            "false_alarms_by_horizon": counts,
            "worst_false_alarms": worst,
            "worst_false_alarms_per_onset": (worst / onsets) if onsets else None,
        }
    return out


def flag_rate_by_group(
    groups: Sequence[str], flags: Sequence[int], business_days_per_year: int
) -> Dict[str, dict]:
    """Flags per `business_days_per_year` days in each group of days (tier 3's alarm rate)."""

    out: Dict[str, dict] = {}
    for label in sorted(set(groups)):
        members = [k for k, g in enumerate(groups) if g == label]
        flagged = sum(flags[k] for k in members)
        out[label] = {
            "days": len(members),
            "flags": flagged,
            "flags_per_year": flagged / len(members) * business_days_per_year,
        }
    return out


def changed_onsets(
    days: Sequence[date], onset: Sequence[int], declared: Sequence[int], other: Sequence[int]
) -> List[dict]:
    """The onsets whose warning differs between two readings: day, and whether each reading flagged it."""

    return [
        {"day": day.isoformat(), "declared_flagged": bool(a), "other_flagged": bool(b)}
        for day, o, a, b in zip(days, onset, declared, other)
        if o and bool(a) != bool(b)
    ]
