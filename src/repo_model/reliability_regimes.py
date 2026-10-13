"""The reliability slope and intercept of a probability forecast, pooled and within regimes (#683, finding #670).

The reliability line is `logit P(y = 1) = intercept + slope * logit(p)` (Cox 1958; #616): a calibrated forecast has intercept 0 and
slope 1, a slope below 1 means the forecast is spread further than the outcomes, a slope of 0 that it ranks nothing.

**A pooled slope misleads here.** A regime with no pressure days (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the
bottom of the curve, which raises the pooled slope; inside 2018-19 the same forecasts are badly over-spread. So every reading of
calibration is made inside a regime (`REGIMES`) and, where a page splits by it, inside a scarcity state, with the pooled cell beside
them and never alone. A cell with no event, or with a constant forecast, has no slope and says "undefined".

Intervals are 90% stationary-block-bootstrap percentile intervals (`repo_model.metrics.stationary_bootstrap_indices`), each cell
resampled on its own days. A resample on which the slope is undefined (it drew no event) is counted, not dropped silently: a cell
that is undefined on more than `MAX_UNDEFINED_SHARE` of its resamples reports no interval.

Standard library only. Development data is never a verdict (scoring protocol v1).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .metrics import MetricError, stationary_bootstrap_indices

#: The regimes of the directive (#683): `(label, first day, last day)`; every scored day falls in exactly one.
REGIMES: Tuple[Tuple[str, date, date], ...] = (
    ("2018-19", date(2018, 1, 1), date(2019, 12, 31)),
    ("2020-24", date(2020, 1, 1), date(2024, 12, 31)),
    ("2025-26", date(2025, 1, 1), date(2026, 12, 31)),
)

#: A probability is clipped to `[CLIP, 1 - CLIP]` before its logit.
CLIP = 1e-6
#: A cell that is undefined on more than this share of its resamples reports no interval.
MAX_UNDEFINED_SHARE = 0.05
#: A cell with fewer events than this reports a slope but no interval (an interval from a handful of events is not information).
DEFAULT_MINIMUM_EVENTS = 5

_Interval = Optional[Tuple[float, float]]


@dataclass(frozen=True)
class Reliability:
    slope: float
    intercept: float


@dataclass(frozen=True)
class Cell:
    """One cell's days, events and reliability line; every figure is `None` where it is undefined."""

    days: int
    events: int
    slope: Optional[float]
    intercept: Optional[float]
    slope_interval: _Interval
    intercept_interval: _Interval


def regime_of(day: date) -> str:
    """The regime a day falls in; a day outside every regime is refused, never given a default."""

    for label, first, last in REGIMES:
        if first <= day <= last:
            return label
    raise ValueError(f"{day} falls in no regime ({REGIMES[0][1]} to {REGIMES[-1][2]})")


def _logit(p: float) -> float:
    p = min(1.0 - CLIP, max(CLIP, p))
    return math.log(p / (1.0 - p))


def fit(probabilities: Sequence[float], outcomes: Sequence[int]) -> Optional[Reliability]:
    """The logistic fit of the outcome on the logit of the forecast, by Newton's method; `None` where it is not identified.

    Not identified: no day, one outcome class, a constant forecast, or a fit that does not converge to finite values.
    """

    if len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes differ in length")
    for p in probabilities:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"a probability must lie in [0, 1], got {p!r}")
    if not probabilities:
        return None
    events = sum(outcomes)
    xs = [_logit(p) for p in probabilities]
    if events == 0 or events == len(outcomes) or max(xs) - min(xs) < 1e-9:
        return None
    a, b = 0.0, 1.0
    for _ in range(100):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in zip(xs, outcomes):
            z = max(-40.0, min(40.0, a + b * x))
            mu = 1.0 / (1.0 + math.exp(-z))
            w = mu * (1.0 - mu)
            g0 += y - mu
            g1 += (y - mu) * x
            h00 += w
            h01 += w * x
            h11 += w * x * x
        h00 += 1e-8
        h11 += 1e-8
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-18:
            return None
        da = (h11 * g0 - h01 * g1) / det
        db = (h00 * g1 - h01 * g0) / det
        size = max(abs(da), abs(db))
        if size > 5.0:  # damp a runaway step on near-separated data
            da, db = da * 5.0 / size, db * 5.0 / size
        a, b = a + da, b + db
        if abs(da) + abs(db) < 1e-9:
            break
    else:
        return None
    if not (math.isfinite(a) and math.isfinite(b)) or abs(a) > 50.0 or abs(b) > 50.0:
        return None
    return Reliability(slope=b, intercept=a)


def _percentile(ordered: Sequence[float], probability: float) -> float:
    position = probability * (len(ordered) - 1)
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _cell(
    probabilities: Sequence[float],
    outcomes: Sequence[int],
    *,
    block_length: float,
    seed: int,
    replications: int,
    level: float,
    minimum_events: int,
) -> Cell:
    days, events = len(outcomes), int(sum(outcomes))
    point = fit(probabilities, outcomes)
    if point is None:
        return Cell(days, events, None, None, None, None)
    if events < minimum_events or days - events < minimum_events:
        return Cell(days, events, point.slope, point.intercept, None, None)
    rng = random.Random(seed)
    slopes: List[float] = []
    intercepts: List[float] = []
    undefined = 0
    for _ in range(replications):
        indices = stationary_bootstrap_indices(days, block_length, rng)
        r = fit([probabilities[i] for i in indices], [outcomes[i] for i in indices])
        if r is None:
            undefined += 1
        else:
            slopes.append(r.slope)
            intercepts.append(r.intercept)
    if undefined > MAX_UNDEFINED_SHARE * replications:
        return Cell(days, events, point.slope, point.intercept, None, None)
    slopes.sort()
    intercepts.sort()
    tail = (1.0 - level) / 2.0
    return Cell(
        days,
        events,
        point.slope,
        point.intercept,
        (_percentile(slopes, tail), _percentile(slopes, 1.0 - tail)),
        (_percentile(intercepts, tail), _percentile(intercepts, 1.0 - tail)),
    )


def by_cell(
    probabilities: Sequence[float],
    outcomes: Sequence[int],
    labels: Sequence[str],
    *,
    block_length: float,
    seed: int,
    replications: int = 2000,
    level: float = 0.90,
    minimum_events: int = DEFAULT_MINIMUM_EVENTS,
) -> Dict[str, Cell]:
    """The reliability line of the pooled days and of each label's days, `"pooled"` first and the labels in order of first appearance.

    `labels` gives each day's cell (a regime from `regime_of`, a scarcity state): one per day. The bootstrap arguments are required, as
    everywhere in this project: an interval that cannot be reproduced cannot be checked.
    """

    if not len(probabilities) == len(outcomes) == len(labels):
        raise ValueError("probabilities, outcomes and labels differ in length")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise MetricError(f"seed must be an int, got {seed!r}")
    if isinstance(block_length, bool) or not isinstance(block_length, (int, float)) or block_length < 1.0:
        raise MetricError(f"block_length must be a number of at least 1, got {block_length!r}")
    if isinstance(replications, bool) or not isinstance(replications, int) or replications < 2:
        raise MetricError(f"replications must be an int >= 2, got {replications!r}")
    if not 0.0 < level < 1.0:
        raise MetricError(f"level must be in (0, 1), got {level}")
    settings = dict(
        block_length=block_length, seed=seed, replications=replications, level=level, minimum_events=minimum_events
    )
    cells: Dict[str, Cell] = {"pooled": _cell(probabilities, outcomes, **settings)}
    members: Dict[str, List[int]] = {}
    for i, label in enumerate(labels):
        if label == "pooled":
            raise ValueError('"pooled" is the name of the pooled cell and cannot label a day')
        members.setdefault(label, []).append(i)
    for label, rows in members.items():
        cells[label] = _cell([probabilities[i] for i in rows], [outcomes[i] for i in rows], **settings)
    return cells


def _figure(value: Optional[float], interval: _Interval, signed: bool = False) -> str:
    if value is None:
        return "undefined"
    text = f"{value:+.2f}" if signed else f"{value:.2f}"
    if interval is None:
        return text
    return f"{text} [{interval[0]:.2f}, {interval[1]:.2f}]"


def markdown_table(cells: Mapping[str, Cell], *, level: float = 0.90) -> str:
    """The cells as a Markdown table, the pooled one first; "undefined" where a cell has no slope."""

    head = [
        f"| cell | days | pressure days | slope [{round(level * 100)}%] | intercept [{round(level * 100)}%] |",
        "|---|---|---|---|---|",
    ]
    rows = [
        f"| {name} | {c.days} | {c.events} | {_figure(c.slope, c.slope_interval)} | {_figure(c.intercept, c.intercept_interval, True)} |"
        for name, c in cells.items()
    ]
    return "\n".join(head + rows) + "\n"
