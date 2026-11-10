"""A multiplier on the candidate's residual spread per pressure-day type of the target day (#1402; H5 step 3, a development arm).

The candidate (s3c-ann-net) draws every day's spread from one pool: its quantiles are `centre + scale * (shift + pool_j)`, with `pool_j` the 23
empirical quantiles of the standardised residuals `z` of the refit's direct training pairs (`spread_mr_state_calendar.StateEstimate`). An arm of
this module replaces `pool_j` by `c + m * (pool_j - c)`, `c` the pool's median and `m` the multiplier of the target day's type, so the shift, the
centre, the scale at the anchor and the fit are the candidate's and `m = 1` is the candidate. The declaration is `metadata/day_type_scale_1402.json`.

`m` for a type is the root-mean-square ratio of that type's training residuals to all training residuals, about `c`, computed per lead from the
refit's own pairs (`StateEstimate.residuals` and `.targets`). A type with fewer than `MIN_ROWS` pairs reads 1; `m` is clamped to `BOUNDS`. In
`pooled` mode the four non-ordinary types share one multiplier and ordinary days keep 1. The type of a day is a function of its date alone
(`turn_days.reporting_day_type`), so reading it at a target day is the calendar rule; the pairs are the refit's own, at or before the anchor.

Stdlib only. This module fits nothing.
"""

from __future__ import annotations

import math
from typing import Dict, List, Mapping, Sequence

from . import scoring_protocol as sp
from .splits import LookAheadError

#: The pressure-day types of the declaration, `turn_days.reporting_day_type` with the turn record in force.
TYPES = ("turn", "quarter_end_turn", "tax_date", "year_end", "ordinary")
NON_ORDINARY = TYPES[:-1]
ORDINARY = "ordinary"
#: The quarter-end group of #1531: the target days of these two types (the last business day of a calendar quarter and the first after it).
GROUP_TYPES = ("quarter_end_turn", "year_end")
#: The fewest training pairs of a type, at one lead, that fit a multiplier; below it the multiplier is 1.
MIN_ROWS = 10
#: The multiplier is clamped to these.
BOUNDS = (0.5, 4.0)
MODES = ("typed", "pooled")
#: The model name of each mode's arm (the declaration's `arms`).
ARM_NAMES = {"typed": "sc_s3c_ann_net_typed", "pooled": "sc_s3c_ann_net_pooledscale"}
_MEDIAN = sp.GRID.index(0.5)


def pool_centre(pool: Sequence[float]) -> float:
    """The pool's median: its grid level 0.5."""

    return pool[_MEDIAN]


def multipliers(
    estimate, labels: Mapping[int, str], anchor: int, *, mode: str, minimum: int = MIN_ROWS, bounds: Sequence[float] = BOUNDS
) -> Dict[str, float]:
    """The multiplier of each type in `TYPES` for one refit and lead, from `estimate` (its `residuals`, `targets` and `pool`).

    `labels[row]` is the pressure-day type of a panel row; `anchor` is the last row public at the decision.

    Raises:
        LookAheadError: a training target is after `anchor`.
        ValueError: `mode` is not in `MODES`, a target row has no label, or a label is not in `TYPES`.
    """

    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    z, targets = estimate.residuals, estimate.targets
    if len(z) != len(targets):
        raise ValueError(f"{len(z)} residuals for {len(targets)} targets")
    centre = pool_centre(estimate.pool)
    squares: Dict[str, List[float]] = {t: [] for t in TYPES}
    everything = 0.0
    for value, target in zip(z, targets):
        if target > anchor:
            raise LookAheadError(f"training target row {target} is after the anchor row {anchor}: its residual is not public at the decision")
        if target not in labels:
            raise ValueError(f"training target row {target} has no pressure-day type")
        label = labels[target]
        if label not in squares:
            raise ValueError(f"pressure-day type {label!r} is not one of {TYPES}")
        square = (value - centre) ** 2
        squares[label].append(square)
        everything += square
    out = {t: 1.0 for t in TYPES}
    if not z or everything <= 0.0:
        return out
    overall = everything / len(z)
    low, high = bounds
    if mode == "typed":
        groups = {(t,): squares[t] for t in TYPES}
    else:
        groups = {NON_ORDINARY: [s for t in NON_ORDINARY for s in squares[t]]}
    for members, values in groups.items():
        if len(values) < minimum:
            continue
        m = min(max(math.sqrt(sum(values) / len(values) / overall), low), high)
        for t in members:
            out[t] = m
    return out


def rescaled(quantiles: Sequence[float], pool: Sequence[float], scale: float, m: float) -> List[float]:
    """`quantiles` with the pool's spread about its median multiplied by `m`: `q_j + scale * (m - 1) * (pool_j - c)`.

    `quantiles` are `centre + scale * (shift + pool_j)`; the result is `centre + scale * (shift + c + m * (pool_j - c))`.
    """

    if m == 1.0:
        return list(quantiles)
    c = pool_centre(pool)
    return [q + scale * (m - 1.0) * (p - c) for q, p in zip(quantiles, pool)]


def rescale_day(
    forecast: Mapping[int, Sequence[float]], estimates: Mapping[int, object], by_lead: Mapping[int, Mapping[str, float]],
    target_types: Mapping[int, str], scale: float,
) -> Dict[int, List[float]]:
    """A decision day's quantiles at each lead, rescaled by the multiplier of that lead's target day's type.

    `estimates[h].pool` is the pool of the refit the forecast used; `by_lead[h][type]` the multipliers of that refit; `target_types[h]` the type of
    the day `h` panel rows after the decision; `scale` the scale at the anchor.
    """

    return {h: rescaled(forecast[h], estimates[h].pool, scale, by_lead[h][target_types[h]]) for h in forecast}


# -- the shrunk quarter-end-only arm of #1531 ------------------------------------------------------------------------------------


def shrink_weight(n: int, k: float) -> float:
    """`n / (n + k)`: the weight of the raw ratio when the group has `n` training pairs and the constant is `k` (0 when both are 0).

    Raises:
        ValueError: `n` or `k` is negative.
    """

    if n < 0 or k < 0:
        raise ValueError(f"the shrinkage needs n >= 0 and k >= 0, got n = {n} and k = {k}")
    return n / (n + k) if n + k > 0 else 0.0


def shrunk(m_raw: float, n: int, k: float) -> float:
    """`1 + w (m_raw - 1)` with `w = n / (n + k)`: the raw multiplier moved part of the way from 1."""

    return 1.0 + shrink_weight(n, k) * (m_raw - 1.0)


def group_multiplier(
    estimate, labels: Mapping[int, str], anchor: int, *, k: float, group: Sequence[str] = GROUP_TYPES, minimum: int = MIN_ROWS,
    bounds: Sequence[float] = BOUNDS,
) -> Dict[str, float]:
    """The shrunk multiplier of a group of types for one refit and lead (#1531): `{"m_raw", "n", "w", "m"}`.

    `m_raw` is #1402's root-mean-square ratio (about the pool's median) of the group's training residuals, taken as one set, to all training
    residuals, 1 when the group has fewer than `minimum` pairs or the refit has no spread, clamped to `bounds`; `n` is the group's pair count and
    `m = 1 + w (m_raw - 1)`, `w = n / (n + k)`. `labels[row]` is the pressure-day type of a panel row; `anchor` the last row public at the decision.

    Raises:
        LookAheadError: a training target is after `anchor`.
        ValueError: a target row has no label, a label is not in `TYPES`, or `k` is negative.
    """

    z, targets = estimate.residuals, estimate.targets
    if len(z) != len(targets):
        raise ValueError(f"{len(z)} residuals for {len(targets)} targets")
    centre = pool_centre(estimate.pool)
    inside, everything = 0.0, 0.0
    n = 0
    for value, target in zip(z, targets):
        if target > anchor:
            raise LookAheadError(f"training target row {target} is after the anchor row {anchor}: its residual is not public at the decision")
        if target not in labels:
            raise ValueError(f"training target row {target} has no pressure-day type")
        label = labels[target]
        if label not in TYPES:
            raise ValueError(f"pressure-day type {label!r} is not one of {TYPES}")
        square = (value - centre) ** 2
        everything += square
        if label in group:
            inside += square
            n += 1
    m_raw = 1.0
    if z and everything > 0.0 and n >= minimum:
        low, high = bounds
        m_raw = min(max(math.sqrt(inside / n / (everything / len(z))), low), high)
    w = shrink_weight(n, k)
    return {"m_raw": m_raw, "n": n, "w": w, "m": 1.0 + w * (m_raw - 1.0)}
