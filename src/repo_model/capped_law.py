"""The law the capped candidate emits: one distribution for its quantiles, its probabilities and its PIT (#1389; H5, registration design).

The candidate (s3c-ann-net) forecasts 23 quantiles, and `s3c_candidate` clips each at the Standing Repo Facility line on a target day at
full allotment. Its probabilities (`spread_mean_reversion.exceedance`, `ml.exceedance_from_quantiles`) read the clipped vector with the
linear law between the quantiles, run on at the outer segments' slopes to 0 and 1, ties nudged by 1e-6 bp per level. Where the cap binds
that is not one distribution: with q97.5 = 9 and q99 = 10 the probability above 10 bp is about 0.0025, and when several upper levels
tie at the line it is about zero, so what the forecast says about the tail beyond the line depends on how many levels the cap happened to
reach. This module states the law, and two coherent rules for it, each behind the `rule` flag (default `"status_quo"`, which is the
published reading, bit for bit; nothing published changes).

* `"status_quo"`: `spread_mean_reversion.exceedance` on the capped vector.
* `"atom_at_line"` (a): a bounded law. The uncapped law (the status-quo completion of the uncapped vector) clipped at the line,
  `Y = min(Y_uncapped, line + margin)`: the mass the uncapped law had above the line sits as an atom at the line, nothing lies above it.
  The order is calibrate (the uncapped vector is the calibrated one), then cap (a transformation of the variable), then read every
  probability and PIT from the clipped law. The quantiles of the law are the capped vector.
* `"open_tail"` (b): the capped percentiles with an explicit unbounded completion. The vector is capped, and the law is read from the
  capped vector only: linear between the levels below the line, an atom at the line of the mass between the first capped level and q99,
  and the 1% above q99 running on above the line, linearly, at the slope of the last segment that still opens (the segment ending at the
  first capped level). No claim that the tail beyond the line is impossible, and the number of levels the cap reached no longer decides
  the tail. If every level is capped there is no open segment and the law is bounded at the line (`OPEN_TAIL_NO_SLOPE`).

The grid CRPS and the upper-tail twCRPS read the quantile vector, which is the capped vector under every rule, so the three rules score
alike on them; the rules differ in P(> tau), in the line exceedance and in the PIT.

Probabilities are for the whole-basis-point event of `data.exceeds_bp`: P(Y > tau) is `1 - F(floor(tau) + 0.5)`. Stdlib only.
"""

from __future__ import annotations

import math
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from . import spread_mean_reversion as _smr
from .scoring_protocol import GRID
from .srf_line import cap_quantiles

__all__ = [
    "DEFAULT_RULE", "OPEN_TAIL_NO_SLOPE", "PiecewiseLaw", "Point", "RULES", "cap", "emitted_law", "exceedance", "pit_interval",
    "randomized_pit",
]

#: The rules, the flag's values. The default is the published reading.
RULES: Tuple[str, ...] = ("status_quo", "atom_at_line", "open_tail")
DEFAULT_RULE = "status_quo"
#: What (b) does when every level is capped, so that no segment opens: the law is bounded at the line.
OPEN_TAIL_NO_SLOPE = "bounded"
_NUDGE = 1e-6


@dataclass(frozen=True)
class Point:
    """A vertex of the cumulative distribution: `f` is the probability at `x`. Two vertices at one `x` are an atom."""

    x: float
    f: float


class PiecewiseLaw:
    """A cumulative distribution, linear between its vertices (sorted by `x`, then `f`; the first at 0, the last at 1)."""

    def __init__(self, points: Sequence[Point]):
        pts: List[Point] = []
        for point in points:
            if pts and pts[-1] == point:
                continue
            pts.append(point)
        if len(pts) < 2 or pts[0].f != 0.0 or pts[-1].f != 1.0:
            raise ValueError("a law runs from probability 0 to probability 1")
        for a, b in zip(pts, pts[1:]):
            if b.x < a.x or b.f < a.f:
                raise ValueError("a law's vertices do not decrease")
        self.points = tuple(pts)
        self._xs = [p.x for p in pts]

    def cdf(self, x: float) -> float:
        """P(Y <= x)."""

        xs, pts = self._xs, self.points
        if x < xs[0]:
            return 0.0
        if x >= xs[-1]:
            return 1.0
        i = bisect_right(xs, x) - 1
        if xs[i] == x:
            return pts[i].f
        a, b = pts[i], pts[i + 1]
        return a.f + (x - a.x) / (b.x - a.x) * (b.f - a.f)

    def cdf_left(self, x: float) -> float:
        """P(Y < x)."""

        xs, pts = self._xs, self.points
        if x <= xs[0]:
            return 0.0
        if x > xs[-1]:
            return 1.0
        j = bisect_left(xs, x)
        if xs[j] == x:
            return pts[j].f
        a, b = pts[j - 1], pts[j]
        return a.f + (x - a.x) / (b.x - a.x) * (b.f - a.f)

    def survival(self, x: float) -> float:
        """P(Y > x)."""

        return min(1.0, max(0.0, 1.0 - self.cdf(x)))

    def atom_at(self, x: float) -> float:
        """P(Y = x)."""

        return self.cdf(x) - self.cdf_left(x)

    def quantile(self, p: float) -> float:
        """The smallest x with F(x) >= p."""

        pts = self.points
        j = next((i for i, point in enumerate(pts) if point.f >= p), len(pts) - 1)
        if j == 0:
            return pts[0].x
        a, b = pts[j - 1], pts[j]
        if b.x == a.x or b.f == a.f:
            return b.x
        return a.x + (p - a.f) / (b.f - a.f) * (b.x - a.x)


def _check(quantiles: Sequence[float]) -> List[float]:
    values = [float(v) for v in quantiles]
    if len(values) != len(GRID):
        raise ValueError(f"{len(values)} quantiles; the grid has {len(GRID)}")
    if any(not math.isfinite(v) for v in values) or any(b < a for a, b in zip(values, values[1:])):
        raise ValueError("the quantiles are finite and do not decrease")
    return values


def cap(quantiles: Sequence[float], line: Optional[float], margin: float = 0.0) -> List[float]:
    """The quantiles clipped at `line + margin` (`srf_line.cap_quantiles`), a copy where there is no line."""

    return cap_quantiles(_check(quantiles), line, margin)


def _status_quo_points(quantiles: Sequence[float]) -> List[Point]:
    """The vertices of `spread_mean_reversion.exceedance`'s law of `quantiles`: nudged knots, outer slopes run on to 0 and 1."""

    knots = [float(v) + _NUDGE * i for i, v in enumerate(quantiles)]
    low = (knots[1] - knots[0]) / (GRID[1] - GRID[0])
    high = (knots[-1] - knots[-2]) / (GRID[-1] - GRID[-2])
    return ([Point(knots[0] - GRID[0] * low, 0.0)] + [Point(x, p) for x, p in zip(knots, GRID)]
            + [Point(knots[-1] + (1.0 - GRID[-1]) * high, 1.0)])


def _bounded_points(uncapped: Sequence[float], ceiling: float) -> List[Point]:
    """(a): the uncapped law clipped at `ceiling`; the mass above it is an atom at it."""

    base = PiecewiseLaw(_status_quo_points(uncapped))
    if ceiling >= base.points[-1].x:
        return list(base.points)
    below = base.cdf(ceiling)
    points = [p for p in base.points if p.x < ceiling] or [Point(ceiling, 0.0)]
    points.append(Point(ceiling, below))
    if below < 1.0:
        points.append(Point(ceiling, 1.0))
    return points


def _open_tail_points(uncapped: Sequence[float], ceiling: float) -> List[Point]:
    """(b): the law of the capped vector alone, with an atom at the ceiling and the last 1% running on above it."""

    capped = [min(float(v), ceiling) for v in uncapped]
    first = next((i for i, v in enumerate(capped) if v >= ceiling), None)
    if first is None:
        return _status_quo_points(capped)
    low = (capped[1] - capped[0]) / (GRID[1] - GRID[0])
    points = [Point(capped[0] - GRID[0] * low, 0.0)] + [Point(capped[i], GRID[i]) for i in range(first)]
    points.append(Point(ceiling, GRID[first]))
    points.append(Point(ceiling, GRID[-1]))
    if first == 0:
        points.append(Point(ceiling, 1.0))  # OPEN_TAIL_NO_SLOPE: nothing opens, bounded at the line
    else:
        slope = (ceiling - capped[first - 1]) / (GRID[first] - GRID[first - 1])
        points.append(Point(ceiling + (1.0 - GRID[-1]) * slope, 1.0))
    return points


def emitted_law(quantiles: Sequence[float], line: Optional[float], rule: str = DEFAULT_RULE, margin: float = 0.0) -> PiecewiseLaw:
    """The law a forecast emits, from its UNCAPPED 23 quantiles, the line (`None`: no cap) and the rule.

    Raises:
        ValueError: an unknown rule, a negative margin, or a vector that is not 23 finite, non-decreasing values.
    """

    if rule not in RULES:
        raise ValueError(f"a rule is one of {RULES}, got {rule!r}")
    values = _check(quantiles)
    capped = cap(values, line, margin)
    if rule == "status_quo":
        return PiecewiseLaw(_status_quo_points(capped))
    if line is None:
        return PiecewiseLaw(_status_quo_points(values))
    ceiling = line + margin
    if rule == "atom_at_line":
        return PiecewiseLaw(_bounded_points(values, ceiling))
    return PiecewiseLaw(_open_tail_points(values, ceiling))


def exceedance(quantiles: Sequence[float], line: Optional[float], tau: float, rule: str = DEFAULT_RULE, margin: float = 0.0) -> float:
    """P(spread > tau), whole basis points, from the UNCAPPED quantiles under `rule`.

    The default rule is `spread_mean_reversion.exceedance` on the capped vector, the published reading.
    """

    if rule not in RULES:
        raise ValueError(f"a rule is one of {RULES}, got {rule!r}")
    if rule == "status_quo":
        return _smr.exceedance(cap(quantiles, line, margin), tau)
    return emitted_law(quantiles, line, rule, margin).survival(math.floor(float(tau)) + 0.5)


def pit_interval(law: PiecewiseLaw, outcome_bp: float) -> Tuple[float, float]:
    """The interval of the PIT of an outcome on whole basis points: `(F(k - 0.5), F(k + 0.5))` for `k = round(outcome)`."""

    k = round(float(outcome_bp))
    return law.cdf(k - 0.5), law.cdf(k + 0.5)


def randomized_pit(law: PiecewiseLaw, outcome_bp: float, v: float) -> float:
    """The randomized PIT: a point of `pit_interval` chosen by `v` in [0, 1]. Uniform when the outcome is drawn from the law."""

    if not 0.0 <= v <= 1.0:
        raise ValueError(f"v is in [0, 1], got {v}")
    lo, hi = pit_interval(law, outcome_bp)
    return lo + v * (hi - lo)
