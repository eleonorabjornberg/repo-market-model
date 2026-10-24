"""Calm and stress spells on the H5 candidate (#1182; H5 step 3, fix: clustered misses; development tier).

`metadata/regime_spells_1182.json` is the declaration; this module is its arithmetic. The base is (s3) of #1145
(`repo_model.spread_mr_state_calendar`): `centre + scale(anchor) * (shift + z)`, with `z` the pool of the standardised residuals
after the calendar terms. The clustering of the misses of its bands (#1153, #1175) is not about how fast the scale reacts, so
this asks whether the market moves between calm and stress spells that one law cannot represent. Three arm kinds, each changing
only the pool (and, for the Markov arms, the scale) that (s3) applies; the terms, the centre, the refit cadence and the
filtered-historical-simulation form are (s3)'s.

**The one-step residual.** `z1(j)` is the standardised residual of the spread at row `j` against the forecast made one row before
it, after the lead-1 calendar terms of (s3), the calendar read at the target row `j` itself (direct, never one row off). It reads
rows at or before `j` and the scale and level of row `j - 1`. Its 5th and 95th percentiles over the refit's training window are
(s3)'s own 90% band in these units; a row is a *miss* when `z1` lies outside it.

**(m1) the observable episode state.** A row is *in an episode* when a miss fell on any of the last `k` rows ending at it
(`episode_rows`; `k` = 3 and 5, two arms). A training pair is in an episode when its origin is. In an episode the forecast takes
its residual pool, and with it the scale of the law, from the past in-episode origins only; outside from the calm ones; with
fewer than `MIN_STATE_POOL` such origins, from the full pool, which is (s3)'s.

**(m2) a two-state Markov-switching scale.** The one-step residual is `N(0, sigma_s^2)` in a calm (0) or a stress (1) state, the
state a Markov chain with entry probability `p01` and stay probability `p11`. `fit_regimes` fits it by EM (forward-backward) on
the training window only. The state probability at a row is the Hamilton filter (`filter_step`) over the residuals up to that row
and never past it. The pool of (s3)'s residuals is divided by the scale of the state at its own target row (the filtered probability
after that row), and the forecast is the mixture of the pool scaled by `sigma_0` and by `sigma_1`, weighted by the `k`-step state probability from the
anchor (`mixture_quantiles`).

**(m3)** (m2) with the entry probability a logistic function of the calendar type of the day entered (`ENTRY_TERMS`: the month-end
turn, the quarter-end turn, the tax date, the coupon settlement), each flag read at the day itself and never one row off. A
scheduled flag (the coupon settlement) is read only where `asof` rule 2 admits it: a day's flag is public at the decision of the
business day before it, so for a step beyond the day after the decision it is 0 (`entry_flags`). `fit_regimes` is
`one_step_guard`-guarded: a one-step fit of the calendar columns raises `ValueError`.

**As-of.** Every rolling quantity reads rows at or before the anchor, the last row whose spread is public at the decision
(`protocol_benchmarks._require_public` raises `LookAheadError`); a filtered probability, an episode flag or a miss of a row not yet
read raises `LookAheadError`.

Stdlib only.
"""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from . import spread_mr_state_calendar as sc
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import GRID, HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: The two episode memories declared, in rows.
K_EPISODE: Tuple[int, ...] = (3, 5)
#: The fewest in-state origins a state's own pool needs; with fewer the full pool is used.
MIN_STATE_POOL = 60
#: (s3)'s own 90% band, in one-step standardised units.
BAND: Tuple[float, float] = (0.05, 0.95)
#: The calendar types the entry probability reads (all of `spread_mr_calendar`'s terms), and the panel columns they come from.
ENTRY_TERMS: Tuple[str, ...] = ("month_end", "quarter_end", "tax_date", "settlement_coupon")
ENTRY_REGRESSORS: Tuple[str, ...] = ("days_to_month_end", "quarter_end", "tax_date", "treasury_settlement_coupons")
#: EM settings, declared once.
EM_ITERATIONS = 60
EM_TOLERANCE = 1e-6
MIN_OBSERVATIONS = 120
#: The starting scales of the two states, as multiples of the root mean square of the residuals.
SIGMA_START = (0.6, 1.8)
SIGMA_FLOOR = 1e-3
#: The starting entry and stay probabilities.
ENTRY_START = 0.05
STAY_START = 0.90
P_MIN, P_MAX = 1e-3, 1.0 - 1e-3
#: The L2 penalty on the entry slopes, in pseudo-days (none on the intercept).
SLOPE_RIDGE = 1.0
NEWTON_STEPS = 8
COEFFICIENT_LIMIT = 8.0
#: A fitted stress scale less than this multiple of the calm scale is a degenerate (single-state) fit.
MIN_SCALE_RATIO = 1.05
ARM_A = sc.ARM_A
#: (s3) of #1145, the base.
BASE_ARM = sc.ARMS[2]


@dataclass(frozen=True)
class RegimeArm:
    """One declared arm. `kind` is `episode` (m1), `markov` (m2) or `markov_calendar` (m3); `k` is m1's memory in rows."""

    name: str
    role: str
    kind: str
    k: int = 0


ARMS: Tuple[RegimeArm, ...] = (
    RegimeArm("m1_episode_k3", "(m1) observable episode state, last 3 rows", "episode", 3),
    RegimeArm("m1_episode_k5", "(m1) observable episode state, last 5 rows", "episode", 5),
    RegimeArm("m2_markov", "(m2) two-state Markov-switching scale", "markov"),
    RegimeArm("m3_markov_calendar", "(m3) (m2) with a calendar-driven entry to stress", "markov_calendar"),
)
MODEL_NAMES: Tuple[str, ...] = (ARM_A, BASE_ARM.name) + tuple(a.name for a in ARMS)

# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS: Dict[str, Tuple[str, str]] = {}

# -- the episode state --------------------------------------------------------------------------------------------------------


def episode_rows(row: int, k: int) -> range:
    """The rows the episode flag at `row` reads: the `k` rows ending at it. None is after `row`.

    Mutation record: see `tests/test_spread_mr_regime.py` (`episode_rows`).
    """

    if k < 1:
        raise ValueError(f"the episode memory is at least one row, got {k}")
    return range(max(0, row - k + 1), row + 1)


def episode_flag(misses: Mapping[int, int], row: int, k: int) -> int:
    """1 when any of the last `k` rows ending at `row` was a miss, else 0 (a row with no miss recorded counts as no miss)."""

    return int(any(misses.get(j, 0) for j in episode_rows(row, k)))


def band_of(zs: Sequence[float]) -> Tuple[float, float]:
    """(s3)'s own 90% band in one-step units: the `BAND` percentiles of the residuals of the training window."""

    if not zs:
        raise smr.InsufficientHistory("no one-step residual to take the 90% band from")
    quantiles = pb.empirical_quantiles(sorted(zs))
    return quantiles[GRID.index(BAND[0])], quantiles[GRID.index(BAND[1])]


def is_miss(z: Optional[float], band: Tuple[float, float]) -> int:
    """1 when the residual lies strictly outside the band, else 0 (no residual is no miss)."""

    return 0 if z is None else int(z < band[0] or z > band[1])


def state_pool(residuals: Sequence[float], flags: Sequence[int], state: int) -> Optional[List[float]]:
    """The sorted residuals of the pairs whose episode flag equals `state`, or `None` with fewer than `MIN_STATE_POOL`."""

    if len(residuals) != len(flags):
        raise ValueError("state_pool needs one flag per residual")
    chosen = sorted(r for r, f in zip(residuals, flags) if f == state)
    return chosen if len(chosen) >= MIN_STATE_POOL else None


# -- the hidden Markov chain --------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Params:
    """The fitted chain: the two scales (calm, stress), the entry logit (intercept and one slope per entry term), the stay
    probability, the log-likelihood, the EM iterations, and whether the fit is degenerate (no distinct stress scale)."""

    sigma: Tuple[float, float]
    intercept: float
    slopes: Tuple[float, ...]
    stay: float
    loglik: float
    iterations: int
    degenerate: bool


def _logistic(v: float) -> float:
    v = max(-30.0, min(30.0, v))
    return 1.0 / (1.0 + math.exp(-v))


def _logit(p: float) -> float:
    return math.log(p / (1.0 - p))


def entry_prob(params: Params, x: Optional[Sequence[float]]) -> float:
    """The probability of entering stress from calm on a day with entry flags `x` (`None` reads as no flag)."""

    value = params.intercept
    if x is not None:
        value += sum(b * v for b, v in zip(params.slopes, x))
    return min(P_MAX, max(P_MIN, _logistic(value)))


def stationary_stress(params: Params) -> float:
    """The stress share of the chain's stationary distribution on a day with no flag."""

    p01 = entry_prob(params, None)
    return p01 / (p01 + 1.0 - params.stay)


def filter_step(previous: float, z: Optional[float], x: Optional[Sequence[float]], params: Params) -> float:
    """The Hamilton filter's step: the stress probability after the row whose residual is `z` and entry flags `x`, from `previous`,
    the stress probability after the row before. A missing residual only moves the chain on."""

    prior = (1.0 - previous) * entry_prob(params, x) + previous * params.stay
    if z is None:
        return prior
    s0, s1 = params.sigma
    l0 = -0.5 * (z / s0) ** 2 - math.log(s0)
    l1 = -0.5 * (z / s1) ** 2 - math.log(s1)
    m = max(l0, l1)
    w0, w1 = (1.0 - prior) * math.exp(l0 - m), prior * math.exp(l1 - m)
    return w1 / (w0 + w1)


def filter_series(z: Sequence[Optional[float]], xs: Optional[Sequence[Sequence[float]]], params: Params) -> List[float]:
    """The filtered stress probability after each row of `z`; the first row starts from the stationary share."""

    out: List[float] = []
    previous = stationary_stress(params)
    for t, value in enumerate(z):
        previous = filter_step(previous, value, None if xs is None else xs[t], params)
        out.append(previous)
    return out


def stress_after(start: float, xs: Sequence[Optional[Sequence[float]]], params: Params) -> float:
    """The stress probability after the steps whose entry flags are `xs`, from the probability `start` before them."""

    f = start
    for x in xs:
        f = (1.0 - f) * entry_prob(params, x) + f * params.stay
    return f


def _solve(matrix: List[List[float]], rhs: List[float]) -> List[float]:
    n = len(rhs)
    a = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("singular system in the entry fit")
        a[col], a[pivot] = a[pivot], a[col]
        for r in range(col + 1, n):
            factor = a[r][col] / a[col][col]
            for c in range(col, n + 1):
                a[r][c] -= factor * a[col][c]
    out = [0.0] * n
    for i in range(n - 1, -1, -1):
        out[i] = (a[i][n] - sum(a[i][j] * out[j] for j in range(i + 1, n))) / a[i][i]
    return out


def _fit_entry(
    groups: Mapping[Tuple[float, ...], Tuple[float, float]], theta: List[float], width: int
) -> List[float]:
    """Newton steps on the soft-count logistic likelihood of the entry probability: `groups` maps an entry-flag pattern to the sum
    of its soft entries into stress and the sum of its soft days in calm; the slopes carry an L2 penalty of `SLOPE_RIDGE`."""

    theta = theta[:]
    for _ in range(NEWTON_STEPS):
        grad = [0.0] * (1 + width)
        hess = [[0.0] * (1 + width) for _ in range(1 + width)]
        for pattern, (entered, days) in groups.items():
            design = (1.0,) + tuple(pattern)
            p = _logistic(sum(c * v for c, v in zip(theta, design)))
            for i in range(1 + width):
                grad[i] += (entered - days * p) * design[i]
                for j in range(1 + width):
                    hess[i][j] += days * p * (1.0 - p) * design[i] * design[j]
        for i in range(1, 1 + width):
            grad[i] -= SLOPE_RIDGE * theta[i]
            hess[i][i] += SLOPE_RIDGE
        for i in range(1 + width):
            hess[i][i] += 1e-9
        step = _solve(hess, grad)
        theta = [max(-COEFFICIENT_LIMIT, min(COEFFICIENT_LIMIT, c + d)) for c, d in zip(theta, step)]
        if max(abs(d) for d in step) < 1e-9:
            break
    return theta


def _degenerate(z: Sequence[Optional[float]]) -> Params:
    seen = [v for v in z if v is not None]
    rms = math.sqrt(sum(v * v for v in seen) / len(seen)) if seen else 1.0
    s = max(SIGMA_FLOOR, rms)
    return Params((s, s), _logit(ENTRY_START), (0.0,) * len(ENTRY_TERMS), STAY_START, float("nan"), 0, True)


@guard_one_step_fit
def fit_regimes(
    z: Sequence[Optional[float]],
    xs: Optional[Sequence[Sequence[float]]],
    *,
    regressors: Sequence[str],
    training_pairs: str,
    trace: Optional[List[float]] = None,
) -> Params:
    """The two-state chain by EM on the residual sequence `z` (consecutive rows; `None` is a row with no residual).

    `xs` are the entry flags of each row (the day entered), one vector of `len(ENTRY_TERMS)` per row, for (m3); `None` is (m2),
    whose entry probability is constant. `regressors` are the panel columns the flags read (for `one_step_guard`; none for (m2)),
    and `training_pairs` is required and `'direct'` is the only value this fit trains on: a flag is paired with the residual of
    the same row. `trace`, if given, receives the log-likelihood after each iteration.

    State 1 starts as the high-scale state. A series of fewer than `MIN_OBSERVATIONS` residuals, or a fit whose stress scale is not
    `MIN_SCALE_RATIO` times the calm one, is returned degenerate (one scale), which makes the arm (s3).

    Raises:
        ValueError: `training_pairs` is not `'direct'`, or `xs` does not match `z`.
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_regimes trains on direct pairs only, got training_pairs={training_pairs!r}")
    if xs is not None and len(xs) != len(z):
        raise ValueError("fit_regimes needs one entry-flag vector per row")
    seen = [v for v in z if v is not None]
    if len(seen) < MIN_OBSERVATIONS:
        return _degenerate(z)
    width = len(ENTRY_TERMS)
    rms = math.sqrt(sum(v * v for v in seen) / len(seen))
    sigma = [max(SIGMA_FLOOR, SIGMA_START[0] * rms), max(SIGMA_FLOOR, SIGMA_START[1] * rms)]
    theta = [_logit(ENTRY_START)] + [0.0] * width
    stay = STAY_START
    previous = -math.inf
    loglik = previous
    iterations = 0
    T = len(z)
    flags = [tuple(x) for x in xs] if xs is not None else [(0.0,) * width] * T
    for iteration in range(1, EM_ITERATIONS + 1):
        iterations = iteration
        p01 = [min(P_MAX, max(P_MIN, _logistic(theta[0] + sum(b * v for b, v in zip(theta[1:], x))))) for x in flags]
        emis, shift = [], 0.0
        for v in z:
            if v is None:
                emis.append((1.0, 1.0))
                continue
            l0 = -0.5 * (v / sigma[0]) ** 2 - math.log(sigma[0])
            l1 = -0.5 * (v / sigma[1]) ** 2 - math.log(sigma[1])
            m = max(l0, l1)
            shift += m
            emis.append((math.exp(l0 - m), math.exp(l1 - m)))
        start1 = p01[0] / (p01[0] + 1.0 - stay)
        alpha: List[Tuple[float, float]] = []
        scale: List[float] = []
        a0, a1 = (1.0 - start1) * emis[0][0], start1 * emis[0][1]
        c = a0 + a1
        alpha.append((a0 / c, a1 / c))
        scale.append(c)
        for t in range(1, T):
            pa0, pa1 = alpha[-1]
            pred1 = pa0 * p01[t] + pa1 * stay
            b0, b1 = (1.0 - pred1) * emis[t][0], pred1 * emis[t][1]
            c = b0 + b1
            alpha.append((b0 / c, b1 / c))
            scale.append(c)
        loglik = sum(math.log(c) for c in scale) + shift
        if trace is not None:
            trace.append(loglik)
        beta = [(1.0, 1.0)] * T
        for t in range(T - 2, -1, -1):
            w0, w1 = emis[t + 1][0] * beta[t + 1][0], emis[t + 1][1] * beta[t + 1][1]
            beta[t] = (
                ((1.0 - p01[t + 1]) * w0 + p01[t + 1] * w1) / scale[t + 1],
                ((1.0 - stay) * w0 + stay * w1) / scale[t + 1],
            )
        mass = [0.0, 0.0]
        square = [0.0, 0.0]
        n11 = n10 = 0.0
        groups: Dict[Tuple[float, ...], List[float]] = {}
        for t in range(T):
            g0, g1 = alpha[t][0] * beta[t][0], alpha[t][1] * beta[t][1]
            norm = g0 + g1
            g0, g1 = g0 / norm, g1 / norm
            if z[t] is not None:
                mass[0] += g0
                mass[1] += g1
                square[0] += g0 * z[t] ** 2
                square[1] += g1 * z[t] ** 2
            if t == 0:
                continue
            pa0, pa1 = alpha[t - 1]
            e0, e1 = emis[t][0] * beta[t][0], emis[t][1] * beta[t][1]
            n01 = pa0 * p01[t] * e1 / scale[t]
            n00 = pa0 * (1.0 - p01[t]) * e0 / scale[t]
            n11 += pa1 * stay * e1 / scale[t]
            n10 += pa1 * (1.0 - stay) * e0 / scale[t]
            entry = groups.setdefault(flags[t], [0.0, 0.0])
            entry[0] += n01
            entry[1] += n00 + n01
        sigma = [max(SIGMA_FLOOR, math.sqrt(square[s] / mass[s])) if mass[s] > 1e-12 else sigma[s] for s in (0, 1)]
        stay = min(P_MAX, max(P_MIN, n11 / (n11 + n10))) if n11 + n10 > 1e-12 else stay
        if xs is None:
            entered = sum(v[0] for v in groups.values())
            days = sum(v[1] for v in groups.values())
            theta = [_logit(min(P_MAX, max(P_MIN, entered / days)))] + [0.0] * width if days > 1e-12 else theta
        else:
            theta = _fit_entry({k: (v[0], v[1]) for k, v in groups.items()}, theta, width)
        if iteration > 1 and abs(loglik - previous) < EM_TOLERANCE:
            break
        previous = loglik
    degenerate = sigma[1] < MIN_SCALE_RATIO * sigma[0]
    if degenerate:
        rms_fit = math.sqrt(sum(v * v for v in seen) / len(seen))
        return Params((rms_fit, rms_fit), theta[0], tuple(theta[1:]), stay, loglik, iterations, True)
    return Params((sigma[0], sigma[1]), theta[0], tuple(theta[1:]), stay, loglik, iterations, False)


# -- the calendar flags of the day entered ------------------------------------------------------------------------------------


def entry_flags(table: cal.TermTable, row: int, decision_row: int) -> List[float]:
    """The entry flags of the day at `row`, as a decision on row `decision_row` reads them: the day's own flags (direct, never one
    row off). A scheduled flag is public at the decision of the day before it (`asof` rule 2), so it reads 0 when `row - 1` is after
    `decision_row`.

    Mutation record: see `tests/test_spread_mr_regime.py` (`entry_flags`).
    """

    flags = table.flags_at(1, row)
    out = []
    for name in ENTRY_TERMS:
        value = flags[name] or 0
        if cal.TERM[name].scheduled and row - 1 > decision_row:
            value = 0
        out.append(float(value))
    return out


# -- the mixture --------------------------------------------------------------------------------------------------------------


def _cdf(u: Sequence[float], y: float) -> float:
    """The distribution function of the continuous law whose quantile function is `empirical_quantiles`' interpolation of the
    sorted pool `u`: its exact inverse (a jump at a repeated value)."""

    n = len(u)
    if y <= u[0]:
        return 0.0
    if y >= u[-1]:
        return 1.0
    i = bisect.bisect_right(u, y) - 1
    gap = u[i + 1] - u[i]
    return (i + (y - u[i]) / gap) / (n - 1) if gap > 0.0 else i / (n - 1)


def mixture_quantiles(u: Sequence[float], sigma: Tuple[float, float], stress: float) -> List[float]:
    """The 23 quantiles of the pool `u` (sorted) scaled by `sigma[0]` with probability `1 - stress` and by `sigma[1]` with
    probability `stress`.

    The pool is read as the continuous law whose quantiles `protocol_benchmarks.empirical_quantiles` interpolates; the mixture's
    distribution function is the weighted sum of the two scaled laws' (`_cdf`), inverted by bisection. A single state, or two equal
    scales, returns `empirical_quantiles` scaled exactly.

    Raises:
        ValueError: `stress` outside [0, 1], or an empty pool.
    """

    if not 0.0 <= stress <= 1.0:
        raise ValueError(f"the stress probability lies in [0, 1], got {stress}")
    if not u:
        raise ValueError("a mixture needs a non-empty pool")
    if len(u) == 1 or stress == 0.0 or stress == 1.0 or sigma[0] == sigma[1]:
        scale = sigma[1] if stress == 1.0 else sigma[0]
        return [scale * q for q in pb.empirical_quantiles(u)]
    lo0 = min(sigma[0] * u[0], sigma[1] * u[0])
    hi0 = max(sigma[0] * u[-1], sigma[1] * u[-1])
    out: List[float] = []
    for level in GRID:
        lo, hi = lo0, hi0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if (1.0 - stress) * _cdf(u, mid / sigma[0]) + stress * _cdf(u, mid / sigma[1]) < level:
                lo = mid
            else:
                hi = mid
            if hi - lo <= 1e-13 * (1.0 + abs(mid)):
                break
        out.append(max(hi, out[-1]) if out else hi)
    return out


# -- the one-step residuals, the miss track and the filters -------------------------------------------------------------------


class Source:
    """The inputs of the one-step residual and the entry flags at rows up to the anchor: the spreads (rows `0..anchor`), the
    levels, the base model's `phi`, the calendar table and (s3)'s lead-1 estimate."""

    def __init__(
        self, spreads: Sequence[float], levels: Sequence[Optional[float]], phi: float, table: cal.TermTable,
        estimate1: Optional[sc.StateEstimate], variant: fhs.Variant = sc.BASE_VARIANT,
    ):
        self.spreads, self.levels, self.phi, self.table, self.estimate1 = spreads, levels, phi, table, estimate1
        self.reader = fhs.ScaleReader(spreads, variant)

    def z(self, j: int) -> Optional[float]:
        """The one-step standardised residual of row `j`: reads rows `j` and `j - 1`, the scale and level of row `j - 1`, and the
        day's own flags. `None` where there is no level or scale yet."""

        if j < 1:
            return None
        if j >= len(self.spreads):
            raise LookAheadError(f"the one-step residual of row {j} is asked for beyond the last public row {len(self.spreads) - 1}")
        level = self.levels[j - 1]
        scale = self.reader.at(j - 1)
        if level is None or scale is None:
            return None
        raw = (self.spreads[j] - level) - self.phi * (self.spreads[j - 1] - level)
        return raw / scale - sc.standardised_shift(self.estimate1, self.table.flags_at(1, j), None)

    def x(self, j: int) -> List[float]:
        """The entry flags of row `j`, read at the decision of the day before it: the day's own."""

        return entry_flags(self.table, j, j - 1)


class Filter:
    """The filtered stress probability at the rows a track has read, for one set of parameters."""

    def __init__(self, params: Params):
        self.params = params
        self.f: Dict[int, float] = {}

    def step(self, j: int, z: Optional[float], x: Optional[Sequence[float]]) -> None:
        previous = self.f.get(j - 1)
        if previous is None:
            previous = stationary_stress(self.params)
        self.f[j] = filter_step(previous, z, x, self.params)


class Track:
    """The one-step residuals, the misses and the filters from row `start` to the last row read (`next - 1`).

    A row is read in order and once; anything asked of a row not yet read raises `LookAheadError`.
    """

    def __init__(self, start: int):
        self.start = start
        self.next = start
        self.z: Dict[int, Optional[float]] = {}
        self.miss: Dict[int, int] = {}
        self.band: Optional[Tuple[float, float]] = None
        self.filters: Dict[str, Filter] = {}
        self.uses_calendar: Dict[str, bool] = {}

    def collect(self, source: Source, upto: int) -> None:
        """Read the residuals of the rows up to `upto` (and update the misses and filters once they are calibrated)."""

        while self.next <= upto:
            j = self.next
            self.z[j] = source.z(j)
            self._after(j, source)
            self.next += 1

    advance = collect

    def _after(self, j: int, source: Source) -> None:
        if self.band is not None:
            self.miss[j] = is_miss(self.z[j], self.band)
        for name, f in self.filters.items():
            f.step(j, self.z[j], source.x(j) if self.uses_calendar[name] else None)

    def calibrate(self, band: Tuple[float, float], params: Mapping[str, Tuple[Params, bool]], source: Source) -> None:
        """Set the 90% band and the filters' parameters, and replay the rows read so far."""

        self.band = band
        self.miss = {}
        self.filters = {name: Filter(p) for name, (p, _) in params.items()}
        self.uses_calendar = {name: uses for name, (_, uses) in params.items()}
        for j in range(self.start, self.next):
            self._after(j, source)

    def _require_read(self, row: int, what: str) -> None:
        if row >= self.next:
            raise LookAheadError(f"{what} of row {row} is asked for before that row is read (the last row read is {self.next - 1})")

    def episode(self, row: int, k: int) -> int:
        """The episode flag at `row` with memory `k`."""

        self._require_read(row, "the episode flag")
        return episode_flag(self.miss, row, k)

    def stress(self, name: str, row: int) -> float:
        """The filtered stress probability after `row`; the stationary share for a row before the track starts."""

        self._require_read(row, "the filtered stress probability")
        if row < self.start:
            return stationary_stress(self.filters[name].params)
        return self.filters[name].f[row]


# -- the fit -----------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class EpisodeLead:
    """(m1) at one lead: (s3)'s estimate, the calm and the episode pools (`None` where there are too few origins), their sizes."""

    estimate: sc.StateEstimate
    calm: Optional[Tuple[float, ...]]
    episode: Optional[Tuple[float, ...]]
    n_calm: int
    n_episode: int


@dataclass(frozen=True)
class MarkovLead:
    """(m2) or (m3) at one lead: (s3)'s estimate and the pool of the residuals divided by their origin's predicted scale."""

    estimate: sc.StateEstimate
    pool: Tuple[float, ...]
    lag: int


@dataclass
class Fitted:
    """What one refit keeps: (s3)'s estimates, the track, the chains' parameters and each arm's per-lead pools."""

    s3: Dict[int, sc.StateEstimate]
    track: Track
    band: Tuple[float, float]
    params: Dict[str, Params]
    episode: Dict[str, Dict[int, EpisodeLead]]
    markov: Dict[str, Dict[int, MarkovLead]]
    lag: int


def _predicted_scale(params: Params, stress: float) -> float:
    return math.sqrt((1.0 - stress) * params.sigma[0] ** 2 + stress * params.sigma[1] ** 2)


def _markov_lead(estimate: sc.StateEstimate, name: str, track: Track, params: Params, lag: int) -> MarkovLead:
    """The pool of (s3)'s residuals, each divided by the scale of the state at its own target row: the filtered stress probability
    after the target row (a row at or before the anchor), so that the pool is free of the state and the forecast re-applies each state's
    scale. (The first version divided by the scale predicted from the origin and was too narrow: amendment 1 of the declaration.)"""

    pool = [e / _predicted_scale(params, track.stress(name, target)) for e, target in zip(estimate.residuals, estimate.targets)]
    return MarkovLead(estimate, tuple(sorted(pool)), lag)


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: cal.TermTable,
    s3: Mapping[int, sc.StateEstimate],
    arms: Sequence[RegimeArm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    training_pairs: str = "direct",
) -> Fitted:
    """The arms' fits as of the decision on row `decision_index`, on (s3)'s training pairs (`s3` are its estimates, per lead).

    Raises:
        InsufficientHistory: no one-step residual to take the band from.
        LookAheadError: a row the residuals read is after the anchor.
        ValueError: the one-step guard (`fit_regimes`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    dates = [row.date for row in panel]
    first = pb._window_start(panel, decision_index, smr.TRAIN_YEARS)
    start = max(1, first - max(HORIZONS) - lag)
    variant = sc.BASE_VARIANT
    read = set(range(max(0, start - variant.window - 1), anchor + 1))
    pb._require_public(read, anchor, dates, f"the one-step residuals for {dates[decision_index]}")
    source = Source([row.spread_bps for row in panel[: anchor + 1]], levels, base.phi, table, s3[1], variant)
    track = Track(start)
    track.collect(source, anchor)
    zs = [track.z[j] for j in range(start, anchor + 1)]
    band = band_of([v for v in zs if v is not None])
    wanted = {a.kind for a in arms}
    params: Dict[str, Params] = {}
    chains: Dict[str, Tuple[Params, bool]] = {}
    if "markov" in wanted:
        params["m2_markov"] = fit_regimes(zs, None, regressors=(), training_pairs=training_pairs)
        chains["m2_markov"] = (params["m2_markov"], False)
    if "markov_calendar" in wanted:
        xs = [source.x(j) for j in range(start, anchor + 1)]
        params["m3_markov_calendar"] = fit_regimes(zs, xs, regressors=ENTRY_REGRESSORS, training_pairs=training_pairs)
        chains["m3_markov_calendar"] = (params["m3_markov_calendar"], True)
    track.calibrate(band, chains, source)
    episode: Dict[str, Dict[int, EpisodeLead]] = {}
    markov: Dict[str, Dict[int, MarkovLead]] = {}
    for arm in arms:
        if arm.kind == "episode":
            per_lead = {}
            for h in HORIZONS:
                est = s3[h]
                flags = [track.episode(o, arm.k) for o in est.origins]
                calm = state_pool(est.residuals, flags, 0)
                stressed = state_pool(est.residuals, flags, 1)
                per_lead[h] = EpisodeLead(
                    est, None if calm is None else tuple(calm), None if stressed is None else tuple(stressed),
                    flags.count(0), flags.count(1),
                )
            episode[arm.name] = per_lead
        else:
            markov[arm.name] = {
                h: _markov_lead(s3[h], arm.name, track, params[arm.name], lag) for h in HORIZONS
            }
    return Fitted(dict(s3), track, band, params, episode, markov, lag)


def episode_quantiles(
    lead: EpisodeLead, *, centre: float, scale: float, flags: Mapping[str, int], in_episode: int
) -> List[float]:
    """(m1): `centre + scale * (shift + pool)` with the pool of the current state, or (s3)'s full pool where the state has
    fewer than `MIN_STATE_POOL` origins."""

    chosen = lead.episode if in_episode else lead.calm
    pool = lead.estimate.pool if chosen is None else pb.empirical_quantiles(list(chosen))
    shift = sc.standardised_shift(lead.estimate, flags, None)
    return [centre + scale * (shift + v) for v in pool]


def markov_quantiles(
    lead: MarkovLead, params: Params, *, centre: float, scale: float, flags: Mapping[str, int], stress: float
) -> List[float]:
    """(m2), (m3): `centre + scale * (shift + q)` with `q` the mixture of the pool scaled by each state's scale, weighted by the
    `k`-step stress probability from the anchor."""

    shift = sc.standardised_shift(lead.estimate, flags, None)
    return [centre + scale * (shift + v) for v in mixture_quantiles(lead.pool, params.sigma, stress)]


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fitted: Fitted,
    table: cal.TermTable,
    arms: Sequence[RegimeArm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
) -> Tuple[Dict[str, Dict[int, List[float]]], Dict[str, object]]:
    """The arms' forecasts of the decision day from `fitted` (possibly an older fit), and the day's detail (the scale at the anchor,
    each arm's episode flag and each chain's stress probability at the anchor). The track reads the rows up to the anchor, no
    further.

    Raises:
        InsufficientHistory: the anchor has no level or no scale.
        LookAheadError: a row the scale or the residuals read is after the anchor, or a scheduled flag is not public.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level_at = levels[anchor]
    if level_at is None:
        raise smr.InsufficientHistory(f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor")
    dates = [row.date for row in panel]
    variant = sc.BASE_VARIANT
    if anchor - variant.window >= 0:
        pb._require_public(
            fhs.scale_rows(anchor, variant.window), anchor, dates, f"the scale of {variant.name} at the anchor of {dates[decision_index]}"
        )
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    scale = fhs.ScaleReader(spreads, variant).at(anchor)
    if scale is None:
        raise smr.InsufficientHistory(f"{dates[decision_index]}: fewer than {variant.window + 1} rows before the anchor")
    track = fitted.track
    pb._require_public(range(track.next, anchor + 1), anchor, dates, f"the one-step residuals at the anchor of {dates[decision_index]}")
    track.collect(Source(spreads, levels, base.phi, table, fitted.s3[1], variant), anchor)
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    out: Dict[str, Dict[int, List[float]]] = {arm.name: {} for arm in arms}
    detail: Dict[str, object] = {"scale": scale}
    for arm in arms:
        if arm.kind == "episode":
            detail[arm.name] = track.episode(anchor, arm.k)
        else:
            detail[arm.name] = track.stress(arm.name, anchor)
    for h in HORIZONS:
        flags = table.read(h, decision_index)
        centre = level_at + base.phi ** (h + lag) * (last - level_at)
        for arm in arms:
            if arm.kind == "episode":
                out[arm.name][h] = episode_quantiles(
                    fitted.episode[arm.name][h], centre=centre, scale=scale, flags=flags, in_episode=int(detail[arm.name])
                )
                continue
            calendar = arm.kind == "markov_calendar"
            steps = [entry_flags(table, r, decision_index) if calendar else None for r in range(anchor + 1, decision_index + h + 1)]
            stress = stress_after(float(detail[arm.name]), steps, fitted.params[arm.name])
            out[arm.name][h] = markov_quantiles(
                fitted.markov[arm.name][h], fitted.params[arm.name], centre=centre, scale=scale, flags=flags, stress=stress
            )
    return out, detail


# -- the walk -----------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Walk:
    #: Model name -> decision day -> lead -> 23 quantiles; `ARM_A` is #941's variant, (s3) the base, then the arms.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    fit_used: Dict[date, date]
    #: Refit day -> the base fit.
    fits: Dict[date, smr.Fit]
    #: Refit day -> the arms' fit (its chains' parameters and band).
    regimes: Dict[date, Fitted]
    #: Decision day -> the scale at the anchor, each episode flag and each chain's stress probability at the anchor.
    detail: Dict[date, Dict[str, object]]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: cal.TermTable,
    arms: Sequence[RegimeArm] = ARMS,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    training_pairs: str = "direct",
) -> Walk:
    """Arm (a), (s3) and `arms` on `decision_days`, refitting as `spread_mr_dispersion.walk` does (the base fit, #941's pool, the
    terms, then the arms). A day on which any model has no forecast is skipped for all, so they are compared on the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {ARM_A: {}, BASE_ARM.name: {}, **{arm.name: {} for arm in arms}}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, smr.Fit] = {}
    regimes: Dict[date, Fitted] = {}
    detail: Dict[date, Dict[str, object]] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    current_scaled: Optional[fhs.ScaledFit] = None
    current_s3: Dict[str, Dict[int, sc.StateEstimate]] = {}
    current_fit: Optional[Fitted] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                scaled = fhs.fit(panel, index, [sc.BASE_VARIANT], base=base, **settings)[sc.BASE_VARIANT.name]
                found_s3 = sc.refit(
                    panel, index, table, {}, [BASE_ARM], registry=registry, decision_time=decision_time, levels=levels, base=base,
                    training_pairs=training_pairs,
                )
                found = refit(
                    panel, index, table, found_s3[BASE_ARM.name], arms, registry=registry, decision_time=decision_time,
                    levels=levels, base=base, training_pairs=training_pairs,
                )
                current, current_scaled, current_s3, current_fit = base, scaled, found_s3, found
                fits[day], regimes[day] = base, found
                since = 0
            today = {ARM_A: fhs.forecast(panel, index, current_scaled, current, sc.BASE_VARIANT, **settings)}
            mine_s3, extra = sc.forecast(
                panel, index, current_s3, table, {}, [BASE_ARM], registry=registry, decision_time=decision_time, levels=levels,
                base=current,
            )
            today.update(mine_s3)
            mine, extra_r = forecast(
                panel, index, current_fit, table, arms, registry=registry, decision_time=decision_time, levels=levels, base=current,
            )
            today.update(mine)
        except smr.InsufficientHistory:
            skipped.append(day)
            continue
        except LookAheadError:
            raise  # a guard trip is never "no public row yet"
        except SplitError:
            if current is not None:
                raise
            skipped.append(day)
            continue
        fit_used[day] = current.fitted_on
        detail[day] = extra_r
        since += 1
        for name, quantiles in today.items():
            forecasts[name][day] = quantiles
    return Walk(forecasts, fit_used, fits, regimes, detail, tuple(skipped))
