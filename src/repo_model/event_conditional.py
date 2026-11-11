"""An event-conditional residual distribution for the candidate's quarter-end target days (#1548; H5 step 3, a development arm).

The candidate (s3c-ann-net) draws every day's spread from one pool: its quantiles are `centre + scale * (shift + pool_j)`, with `pool_j` the 23
empirical quantiles of the standardised residuals `z` of the refit's direct training pairs (`spread_mr_state_calendar.StateEstimate`). An arm of this
module replaces, on a target day of the event set, `pool_j` by `(1 - w) * pool_j + w * event_j`, `event_j` the 23 empirical quantiles of the residuals
whose own target day is in the event set, at the same refit and lead, and `w = n / (n + k)` with `n` the number of those residuals. Each level has its
own correction (so the event's shape and its location shift are carried, not one width multiplier), shrunk toward the pool the candidate already uses.
The centre, the shift, the scale at the anchor and the fit are the candidate's; `w = 0` is the candidate. The declaration is
`metadata/qe_event_model_1548.json`.

An event set with fewer than `MIN_ROWS` training pairs gets `w = 0` and the candidate's pool, exactly. The type of a day is a function of its date alone
(`turn_days.reporting_day_type`), so reading it at a target day is the calendar rule; the pairs are the refit's own, at or before the anchor.

Stdlib only. This module fits nothing.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Sequence

from . import day_type_scale as dts
from . import protocol_benchmarks as pb
from . import scoring_protocol as sp
from .splits import LookAheadError

#: The event set of #1548: the target days of these pressure-day types (the last business day of a calendar quarter and the first after it; #1531's group).
EVENT_TYPES = dts.GROUP_TYPES
#: The fewest training pairs of the event set, at one lead, that fit an event pool; below it the arm is the candidate.
MIN_ROWS = dts.MIN_ROWS


def event_pool(
    estimate, labels: Mapping[int, str], anchor: int, *, k: float, event: Sequence[str] = EVENT_TYPES, minimum: int = MIN_ROWS
) -> Dict[str, object]:
    """The event-conditional pool of one refit and lead: `{"n", "w", "base", "pool", "event_pool"}`.

    `base` is the candidate's pool, `n` is the number of the refit's training pairs whose target is in `event`, `event_pool` the 23 empirical quantiles of their residuals (`None` below
    `minimum`), `w = n / (n + k)` (0 below `minimum`) and `pool` the 23 quantiles `pool_j + w * (event_j - pool_j)`, which is exactly
    `estimate.pool` when `w` is 0. `labels[row]` is the pressure-day type of a panel row; `anchor` the last row public at the decision.

    Raises:
        LookAheadError: a training target is after `anchor`.
        ValueError: a target row has no label, a label is not in `dts.TYPES`, residuals and targets differ in length, or `k` is negative.
    """

    z, targets = estimate.residuals, estimate.targets
    if len(z) != len(targets):
        raise ValueError(f"{len(z)} residuals for {len(targets)} targets")
    inside: List[float] = []
    for value, target in zip(z, targets):
        if target > anchor:
            raise LookAheadError(f"training target row {target} is after the anchor row {anchor}: its residual is not public at the decision")
        if target not in labels:
            raise ValueError(f"training target row {target} has no pressure-day type")
        label = labels[target]
        if label not in dts.TYPES:
            raise ValueError(f"pressure-day type {label!r} is not one of {dts.TYPES}")
        if label in event:
            inside.append(value)
    n = len(inside)
    w = dts.shrink_weight(n, k)
    base = list(estimate.pool)
    if n < minimum:
        return {"n": n, "w": 0.0, "base": base, "pool": list(base), "event_pool": None}
    own = pb.empirical_quantiles(sorted(inside))
    return {"n": n, "w": w, "base": base, "pool": [p + w * (e - p) for p, e in zip(base, own)], "event_pool": own}


def conditioned_quantiles(quantiles: Sequence[float], pool: Sequence[float], new_pool: Sequence[float], scale: float) -> List[float]:
    """`quantiles` (`centre + scale * (shift + pool_j)`) with the pool replaced by `new_pool`: `q_j + scale * (new_j - pool_j)`.

    Returns the candidate's list unchanged when `new_pool` equals `pool`.

    Raises:
        ValueError: the three sequences differ in length.
    """

    if not (len(quantiles) == len(pool) == len(new_pool)):
        raise ValueError(f"{len(quantiles)} quantiles, {len(pool)} pool values and {len(new_pool)} new pool values")
    if list(new_pool) == list(pool):
        return list(quantiles)
    return [q + scale * (n - p) for q, p, n in zip(quantiles, pool, new_pool)]


def pool_record(fitted: Mapping[object, Mapping[int, Mapping[str, object]]], leads: Sequence[int], *, k: float) -> Optional[dict]:
    """Per lead, over the refits: the mean and least and greatest event count `n` and weight `w`, the share of refits at the fallback, and the mean
    shift of the event pool's median and the mean ratio of its 90% span to the pool's, where an event pool exists."""

    if not fitted:
        return None
    out: dict = {"refits": len(fitted), "k": k, "minimum_rows": MIN_ROWS, "by_lead": {}}
    mid, low, high = sp.GRID.index(0.5), sp.GRID.index(0.05), sp.GRID.index(0.95)
    for h in leads:
        rows = [fitted[r][h] for r in fitted]
        block: dict = {}
        for name in ("n", "w"):
            values = [x[name] for x in rows]
            block[name] = {"mean": sum(values) / len(values), "min": min(values), "max": max(values)}
        block["share_fallback"] = sum(1 for x in rows if x["event_pool"] is None) / len(rows)
        have = [x for x in rows if x["event_pool"] is not None]
        shifts = [x["event_pool"][mid] - x["base"][mid] for x in have]
        ratios = [(x["event_pool"][high] - x["event_pool"][low]) / (x["base"][high] - x["base"][low]) for x in have if x["base"][high] > x["base"][low]]
        block["median_shift"] = sum(shifts) / len(shifts) if shifts else None
        block["span_ratio"] = sum(ratios) / len(ratios) if ratios else None
        out["by_lead"][str(h)] = block
    return out
