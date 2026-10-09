"""A stacked ensemble of track forecasts (#410, track X of #374).

Each member (a track's walk-forward probability that SOFR - IORB exceeds a
threshold) is a probability for the same scored days. The stack combines them
by a **logistic regression on the members' logits**, fitted anew at each of the
judge's refit blocks (`pressure_judge.choose_cutoffs`, 21 scored days):

    logit P(Y = 1) = b + sum_m w_m * logit(clip(p_m))

with a ridge penalty that pulls the weights towards the equal-weight logit pool
(`w_m = 1/M`, `b = 0`), which is also the fallback while the window is short or
holds too few days of either outcome class. The form, members, penalty and
fallback are declared in `metadata/pressure_stack.json` before any score.

**The information set.** A refit at the block starting at scored day `start`
reads the members' probabilities and the outcomes of earlier blocks' days only,
and of those only the days whose outcome was public at the block's first
decision instant: up to the business day `horizon + 1` business days before the
block's first scored day (SOFR for a day is published the morning after), as the
cut-off rule reads it. Each member's probability for such a day was made at that
day's own decision instant, before this refit, out of sample when made. A window
day after that training end raises `LookAheadError`; a malformed input raises
`ValueError`. Standard library only.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .splits import LookAheadError

DEFAULT_DECLARATION = Path(__file__).resolve().parents[2] / "metadata" / "pressure_stack.json"


def clipped_logit(p: float, clip: float) -> float:
    """`log(p / (1 - p))` with `p` held inside `[clip, 1 - clip]`."""

    q = min(max(float(p), clip), 1.0 - clip)
    return math.log(q / (1.0 - q))


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-min(z, 700.0)))
    e = math.exp(max(z, -700.0))
    return e / (1.0 + e)


def _solve(matrix: List[List[float]], vector: List[float]) -> List[float]:
    """Gauss-Jordan elimination with partial pivoting (the systems here are at most 8 by 8)."""

    n = len(vector)
    a = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-14:
            raise ValueError("the stack's normal equations are singular")
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(n):
            if r != col:
                factor = a[r][col] / a[col][col]
                if factor:
                    for c in range(col, n + 1):
                        a[r][c] -= factor * a[col][c]
    return [a[i][n] / a[i][i] for i in range(n)]


def _loss(theta: Sequence[float], rows, y, ridge: float) -> float:
    m = len(theta) - 1
    total = 0.0
    for x, outcome in zip(rows, y):
        z = theta[0] + sum(theta[1 + j] * x[j] for j in range(m))
        # log(1 + e^z) - y z, stable
        total += max(z, 0.0) + math.log1p(math.exp(-abs(z))) - outcome * z
    total += 0.5 * ridge * sum((theta[1 + j] - 1.0 / m) ** 2 for j in range(m))
    return total


def fit_logit_stack(
    rows: Sequence[Sequence[float]],
    outcomes: Sequence[int],
    *,
    ridge: float,
    iterations: int = 50,
    tolerance: float = 1e-8,
) -> Tuple[float, Tuple[float, ...]]:
    """The intercept and weights of the penalised logistic stack.

    Newton's method, started from the equal-weight pool, with step halving when
    a step does not lower the penalised log loss. The penalty is
    `(ridge / 2) * sum_m (w_m - 1/M)^2`; the intercept is not penalised.

    Raises:
        ValueError: on rows of different widths, a row count that is not the
            outcome count, no rows, or an outcome that is not 0 or 1.
    """

    if len(rows) != len(outcomes):
        raise ValueError(f"{len(rows)} rows but {len(outcomes)} outcomes")
    if not rows:
        raise ValueError("a stack needs at least one row")
    m = len(rows[0])
    if m < 1 or any(len(row) != m for row in rows):
        raise ValueError("every row of the stack needs one logit per member")
    if any(o not in (0, 1) for o in outcomes):
        raise ValueError("stack outcomes are 0 or 1")
    theta = [0.0] + [1.0 / m] * m
    current = _loss(theta, rows, outcomes, ridge)
    for _ in range(iterations):
        gradient = [0.0] * (m + 1)
        hessian = [[0.0] * (m + 1) for _ in range(m + 1)]
        for x, outcome in zip(rows, outcomes):
            z = theta[0] + sum(theta[1 + j] * x[j] for j in range(m))
            p = _sigmoid(z)
            r, v = p - outcome, p * (1.0 - p)
            vec = (1.0,) + tuple(x)
            for a in range(m + 1):
                gradient[a] += r * vec[a]
                for b in range(m + 1):
                    hessian[a][b] += v * vec[a] * vec[b]
        for j in range(m):
            gradient[1 + j] += ridge * (theta[1 + j] - 1.0 / m)
            hessian[1 + j][1 + j] += ridge
        for a in range(m + 1):
            hessian[a][a] += 1e-8
        step = _solve(hessian, gradient)
        scale, moved = 1.0, False
        for _ in range(30):
            trial = [theta[a] - scale * step[a] for a in range(m + 1)]
            loss = _loss(trial, rows, outcomes, ridge)
            if loss <= current + 1e-12:
                moved = True
                break
            scale *= 0.5
        if not moved:
            break
        change = max(abs(trial[a] - theta[a]) for a in range(m + 1))
        theta, current = trial, loss
        if change < tolerance:
            break
    return theta[0], tuple(theta[1:])


@dataclass(frozen=True)
class Fallback:
    """When the window is too thin to fit: the equal-weight logit pool."""

    minimum_days: int
    minimum_each_class: int

    def applies(self, *, days: int, positives: int) -> bool:
        return (
            days < self.minimum_days
            or positives < self.minimum_each_class
            or days - positives < self.minimum_each_class
        )


def require_known(days: Sequence[date], window: Sequence[int], *, training_end: Optional[date]) -> None:
    """Refuse a window day after the refit's training end (the last day whose outcome was public)."""

    late = [days[k] for k in window if training_end is None or days[k] > training_end]
    if late:
        raise LookAheadError(
            f"stack trained on {len(late)} day(s) from {min(late)} on, after the refit's training end "
            f"({training_end}); a stack is fitted on outcomes public at the refit"
        )


def training_end_of(days: Sequence[date], calendar: Sequence[date], *, start: int, horizon: int) -> Optional[date]:
    """The last day whose outcome was public at the first decision instant of the block at `start`."""

    position = {day: k for k, day in enumerate(calendar)}
    last_known = position[days[start]] - horizon - 1
    return calendar[last_known] if last_known >= 0 else None


def training_window(
    days: Sequence[date], calendar: Sequence[date], *, start: int, horizon: int
) -> List[int]:
    """Indices of the scored days the refit at `start` may read: earlier blocks' days known by then."""

    training_end = training_end_of(days, calendar, start=start, horizon=horizon)
    window = [
        k for k in range(start)
        if training_end is not None and days[k] <= training_end
    ]
    require_known(days, window, training_end=training_end)
    return window


@dataclass(frozen=True)
class Stacked:
    probabilities: Tuple[float, ...]
    trace: Tuple[Dict[str, Any], ...]


def stack(
    days: Sequence[date],
    calendar: Sequence[date],
    members: Mapping[str, Sequence[float]],
    outcomes: Sequence[int],
    *,
    horizon: int,
    step: int,
    ridge: float,
    clip: float,
    fallback: Fallback,
    iterations: int = 50,
    tolerance: float = 1e-8,
) -> Stacked:
    """The walk-forward stacked probability for every scored day, and what each refit fitted.

    `members` maps a member's name to its probability on each of `days`;
    `outcomes[k]` is 1 when day `k` was a pressure day (read only through
    `training_window`).

    Raises:
        LookAheadError: if a refit's window would reach past its training end.
        ValueError: if the members, days and outcomes differ in length, or a
            day is not a panel day.
    """

    names = list(members)
    if not names:
        raise ValueError("a stack needs members")
    n = len(days)
    if len(outcomes) != n or any(len(members[name]) != n for name in names):
        raise ValueError("every member and the outcomes need one value per scored day")
    position = {day: k for k, day in enumerate(calendar)}
    missing = [day for day in days if day not in position]
    if missing:
        raise ValueError(f"scored day {missing[0]} is not a panel day")
    features = [[clipped_logit(members[name][k], clip) for name in names] for k in range(n)]
    m = len(names)
    out: List[float] = []
    trace: List[Dict[str, Any]] = []
    for start in range(0, n, step):
        block = range(start, min(start + step, n))
        window = training_window(days, calendar, start=start, horizon=horizon)
        positives = sum(outcomes[k] for k in window)
        if fallback.applies(days=len(window), positives=positives):
            intercept, weights, mode = 0.0, (1.0 / m,) * m, "equal"
        else:
            intercept, weights = fit_logit_stack(
                [features[k] for k in window], [outcomes[k] for k in window],
                ridge=ridge, iterations=iterations, tolerance=tolerance,
            )
            mode = "fitted"
        for k in block:
            out.append(_sigmoid(intercept + sum(w * x for w, x in zip(weights, features[k]))))
        trace.append(
            {
                "first_day": days[start].isoformat(),
                "mode": mode,
                "training_days": len(window),
                "training_pressure_days": positives,
                "intercept": intercept,
                "weights": list(weights),
            }
        )
    return Stacked(tuple(out), tuple(trace))


def equal_average(members: Mapping[str, Sequence[float]]) -> Tuple[float, ...]:
    """The arithmetic mean of the members' probabilities, day by day (no fit)."""

    columns = list(members.values())
    if not columns or any(len(c) != len(columns[0]) for c in columns):
        raise ValueError("the members need one probability per scored day")
    return tuple(sum(c[k] for c in columns) / len(columns) for k in range(len(columns[0])))


@dataclass(frozen=True)
class Declaration:
    path: str
    sha256: str
    candidate: str
    comparison: str
    members: Tuple[str, ...]
    thresholds: Tuple[float, ...]
    clip: float
    ridge: float
    iterations: int
    tolerance: float
    step: int
    fallback: Fallback


def parse_declaration(document: Mapping[str, Any], where: str, digest: str = "") -> Declaration:
    members = tuple(document["members"])
    if len(members) < 2 or len(set(members)) != len(members):
        raise ValueError(f"{where}: members must be at least two distinct names")
    clip = float(document["clip"])
    if not 0.0 < clip < 0.5:
        raise ValueError(f"{where}: clip must be in (0, 0.5)")
    fit, refit, fb = document["fit"], document["refit"], document["fallback"]
    ridge = float(fit["ridge"])
    if ridge < 0:
        raise ValueError(f"{where}: ridge must not be negative")
    return Declaration(
        path=where,
        sha256=digest,
        candidate=str(document["candidate"]),
        comparison=str(document["comparison_candidate"]),
        members=members,
        thresholds=tuple(float(t) for t in document["thresholds_bp"]),
        clip=clip,
        ridge=ridge,
        iterations=int(fit["iterations_at_most"]),
        tolerance=float(fit["tolerance"]),
        step=int(refit["every"]),
        fallback=Fallback(int(fb["minimum_days"]), int(fb["minimum_each_class"])),
    )


def load_declaration(path: Path = DEFAULT_DECLARATION) -> Declaration:
    raw = Path(path).read_bytes()
    return parse_declaration(json.loads(raw), str(path), hashlib.sha256(raw).hexdigest())
