"""The scorer of scoring protocol v1: sections 3, 5, 6 and 11 (#655, H1).

`docs/decisions/scoring-protocol.md` is the rule; this module is its arithmetic. It is
tested on forecasts of known quality before any hypothesis is scored under it
(`tests/test_scoring_protocol_synthetic.py`, H1). The benchmarks of section 4 are in
`repo_model.protocol_benchmarks`.

**What a forecast is (§3).** For one decision day, a mapping from each lead h = 1..5
business days to 23 quantiles of the SOFR - IORB spread in bp, at the levels `GRID`. The
target of lead h is the h-th day after the decision day on the scoring calendar.

**What a day scores (§3).** Grid CRPS, twice the mean pinball loss over `GRID`, for each
lead, averaged with equal weight over the leads: one number per decision day. The key
secondary, the upper-tail twCRPS with threshold weight `1{z > 0 bp}`, is the same grid score
of the forecast and the outcome both mapped through `max(., 0)`: that map is the chaining
function of the weight, and its quantiles are the forecast's quantiles mapped through it.

**One sign everywhere (§5).** `d_t = S(benchmark) - S(candidate)`, so a positive `d` always
favours the candidate, and skill is `mean(d) / mean(S(benchmark))`.

**The interval (§5).** The studentized stationary bootstrap (Eleonora's ruling of 13 October
2026 on PR #660, which replaced the plain percentile bootstrap after H1's coverage check failed):
the resamples of `repo_model.metrics`, mean block 10 business days, 10,000 draws (100,000 at the
interim checkpoints), a seed fixed at registration; each resample's mean(d) is studentized by its
own Newey-West standard error at lag 10, and the bound is read one-sided at 95%. The observed t is
the Diebold-Mariano statistic, reported beside it.

**B3 (ruling of 13 October 2026).** The incumbent is scored on its own five levels against each
candidate read at the same five (`on_levels`, `level_crps`), as a secondary comparison.

**Checkpoints (§6).** 60, 125 and 250 confirmation days, the overall one-sided 5% spent across
them by the Lan-DeMets O'Brien-Fleming function. `nominal_levels` gives the one-sided level each
look is read at.

**Missing data (§11).** `fill_missing` scores a missing candidate forecast as B1's and counts
it; more than 5% missing voids the registration. A target day with no published outcome is
dropped for every forecast. Outcomes are the first published value (`first_published`).

**No locked day is scored.** `day_scores` passes every decision and target day it scores to
`lockbox.require_unlocked` before it scores any of them.

Stdlib only.
"""

from __future__ import annotations

import math
import random
from itertools import islice
from operator import mul
from dataclasses import dataclass
from functools import lru_cache
from datetime import date
from statistics import NormalDist
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import lockbox
from .data import PointInTimeObservation
from .metrics import _quantile, crps_from_quantiles, stationary_bootstrap_indices

#: §3: the 23 quantile levels every forecast is made at.
GRID: Tuple[float, ...] = (
    (0.01, 0.025, 0.05)
    + tuple(round(0.10 + 0.05 * step, 2) for step in range(17))
    + (0.95, 0.975, 0.99)
)
#: §3: leads in business days, averaged with equal weight into one score per decision day.
HORIZONS: Tuple[int, ...] = (1, 2, 3, 4, 5)
#: §3: the key secondary's threshold weight is 1{z > this}, in bp.
TWCRPS_THRESHOLD_BP = 0.0
#: §5: the stationary bootstrap's mean block length (business days) and draws.
BLOCK_LENGTH = 10
DRAWS = 10_000
#: The draws at an interim checkpoint (60 and 125 days), whose nominal levels are finer than
#: 10,000 draws resolve: Eleonora's ruling of 13 October 2026 (PR #660).
INTERIM_DRAWS = 100_000
#: §5, §6: the overall one-sided level.
ALPHA = 0.05
#: §5: the Diebold-Mariano statistic's Newey-West lag.
HAC_LAG = 10
#: §6: confirmation days at each checkpoint.
CHECKPOINTS: Tuple[int, ...] = (60, 125, 250)
#: §6: the minimum meaningful effect, CRPS skill against B1. Proposed at 3% and accepted by
#: Eleonora on #640, to be checked by the power study (#656) before the first registration.
MME = 0.03
#: §11: a registration with a larger share of missing forecasts is void.
MISSING_LIMIT = 0.05

SUPPORTED = "supported"
KILLED = "killed"
INCONCLUSIVE = "inconclusive (continuing)"
NOT_SHOWN = "not shown"

_NORMAL = NormalDist()

Forecast = Mapping[int, Sequence[float]]


class ProtocolError(ValueError):
    """Input the protocol cannot score as given."""


class RegistrationVoid(ProtocolError):
    """§11: more than `MISSING_LIMIT` of a candidate's forecasts are missing."""


class UnresolvedLevel(ProtocolError):
    """A bootstrap bound asked for at a level its draws cannot resolve.

    A one-sided bound at level `a` is the `a` quantile of the draws. With fewer than one draw
    below it (`a * draws < 1`) the bound is the smallest draw whatever `a` is, so it would
    not be the bound the level names. Raised rather than clamped.
    """


# --------------------------------------------------------------------------
# §3: the scores
# --------------------------------------------------------------------------


def _finite(value: float, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProtocolError(f"{what} is not a number: {value!r}")
    value = float(value)
    if not math.isfinite(value):
        raise ProtocolError(f"{what} is not finite: {value}")
    return value


def _quantiles(quantiles: Sequence[float]) -> List[float]:
    values = [_finite(value, "a quantile") for value in quantiles]
    if len(values) != len(GRID):
        raise ProtocolError(f"a forecast carries {len(values)} quantiles; the grid has {len(GRID)}")
    return values


def grid_crps(quantiles: Sequence[float], observed: float) -> float:
    """§3: twice the mean pinball loss over `GRID`. Crossing quantiles are refused."""

    return crps_from_quantiles(GRID, _quantiles(quantiles), _finite(observed, "the outcome"))


def upper_tail_twcrps(quantiles: Sequence[float], observed: float) -> float:
    """§3: the threshold-weighted grid CRPS with weight `1{z > 0 bp}`.

    `twCRPS(F, y) = CRPS(F o v^-1, v(y))` with the chaining function `v(z) = max(z, 0)`, whose
    derivative is the weight. `v` is monotone, so the mapped forecast's quantiles are the
    forecast's quantiles mapped, and the grid form is the grid CRPS of the mapped pair.
    """

    floor = TWCRPS_THRESHOLD_BP
    return crps_from_quantiles(
        GRID,
        [max(value, floor) for value in _quantiles(quantiles)],
        max(_finite(observed, "the outcome"), floor),
    )


def on_levels(quantiles: Sequence[float], levels: Sequence[float]) -> List[float]:
    """A 23-level forecast read at `levels`, each of which must be on `GRID`.

    The secondary comparison against B3 scores B3 on its own levels and each candidate on the
    same ones (ruling of 13 October 2026, PR #660).
    """

    values = _quantiles(quantiles)
    out = []
    for level in levels:
        if float(level) not in GRID:
            raise ProtocolError(f"level {level} is not on the protocol's grid")
        out.append(values[GRID.index(float(level))])
    return out


def level_crps(levels: Sequence[float]) -> Callable[[Sequence[float], float], float]:
    """The grid CRPS on `levels` alone: twice the mean pinball loss over them."""

    grid = tuple(float(level) for level in levels)

    def score(quantiles: Sequence[float], observed: float) -> float:
        values = [_finite(value, "a quantile") for value in quantiles]
        if len(values) != len(grid):
            raise ProtocolError(f"a forecast carries {len(values)} quantiles; the levels are {len(grid)}")
        return crps_from_quantiles(grid, values, _finite(observed, "the outcome"))

    return score


def _calendar(calendar: Sequence[date]) -> List[date]:
    days = list(calendar)
    for position in range(1, len(days)):
        if days[position] <= days[position - 1]:
            raise ProtocolError(
                f"the scoring calendar is not strictly ascending at {days[position]}"
            )
    return days


def day_scores(
    forecasts: Mapping[date, Forecast],
    outcomes: Mapping[date, Optional[float]],
    calendar: Sequence[date],
    *,
    score: Callable[[Sequence[float], float], float] = grid_crps,
) -> Dict[date, float]:
    """§3, §11: one score per decision day, the mean over its leads of `score`.

    Args:
        forecasts: decision day -> lead -> 23 quantiles. Every lead in `HORIZONS` must be
            present; a candidate's missing forecasts are filled by `fill_missing` first.
        outcomes: target day -> first-published spread in bp. A target day absent or `None`
            here has no published outcome, and its lead is dropped from every decision day
            that targets it (§11); a decision day left with no lead is dropped.
        calendar: the business days leads are counted on.
        score: `grid_crps` (primary) or `upper_tail_twcrps` (key secondary).

    Raises:
        LookAheadError: a decision or target day is in a locked lockbox tier.
        ProtocolError: a malformed forecast, or a lead past the end of the calendar.
    """

    days = _calendar(calendar)
    position = {day: index for index, day in enumerate(days)}
    cells: Dict[date, List[Tuple[Sequence[float], date]]] = {}
    for decision in sorted(forecasts):
        if decision not in position:
            raise ProtocolError(f"decision day {decision} is not on the scoring calendar")
        leads = forecasts[decision]
        if set(leads) != set(HORIZONS):
            raise ProtocolError(
                f"the forecast for {decision} carries leads {sorted(leads)}, not "
                f"{list(HORIZONS)}; fill missing forecasts with fill_missing first"
            )
        kept = []
        for h in HORIZONS:
            if position[decision] + h >= len(days):
                raise ProtocolError(
                    f"lead {h} from {decision} runs past the end of the scoring calendar"
                )
            target = days[position[decision] + h]
            if outcomes.get(target) is not None:
                kept.append((leads[h], target))
        if kept:
            cells[decision] = kept
    lockbox.require_unlocked(
        set(cells) | {target for kept in cells.values() for _, target in kept},
        where="scoring_protocol.day_scores",
    )
    return {
        decision: sum(score(quantiles, outcomes[target]) for quantiles, target in kept) / len(kept)
        for decision, kept in cells.items()
    }


# --------------------------------------------------------------------------
# §11: missing data and outcomes
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Filled:
    """A candidate's forecasts with its missing ones scored as B1's (§11)."""

    forecasts: Dict[date, Dict[int, Sequence[float]]]
    #: Decision days on which at least one lead was missing and B1's was used.
    missing_days: Tuple[date, ...]
    missing_share: float


def fill_missing(
    candidate: Mapping[date, Mapping[int, Optional[Sequence[float]]]],
    b1: Mapping[date, Forecast],
    decision_days: Sequence[date],
) -> Filled:
    """§11: every logged business day carries a forecast, B1's where the candidate's is missing.

    A decision day counts as missing when any of its leads is absent or `None`; only the
    missing leads take B1's forecast. The share is missing decision days over `decision_days`.

    Raises:
        RegistrationVoid: more than `MISSING_LIMIT` of the decision days are missing.
        ProtocolError: B1 has no forecast for a lead it must stand in for, or the candidate
            forecasts a day that is not a decision day.
    """

    days = list(dict.fromkeys(decision_days))
    if not days:
        raise ProtocolError("no decision days")
    extra = sorted(set(candidate) - set(days))
    if extra:
        raise ProtocolError(f"the candidate forecasts {extra[0]}, which is not a decision day")
    out: Dict[date, Dict[int, Sequence[float]]] = {}
    missing = []
    for day in days:
        own = candidate.get(day) or {}
        filled = {}
        for h in HORIZONS:
            if own.get(h) is not None:
                filled[h] = own[h]
                continue
            stand_in = (b1.get(day) or {}).get(h)
            if stand_in is None:
                raise ProtocolError(f"B1 has no lead-{h} forecast for {day} to stand in")
            filled[h] = stand_in
        if any(own.get(h) is None for h in HORIZONS):
            missing.append(day)
        out[day] = filled
    share = len(missing) / len(days)
    if share > MISSING_LIMIT:
        raise RegistrationVoid(
            f"{len(missing)} of {len(days)} decision days ({share:.1%}) are missing a "
            f"forecast, above the {MISSING_LIMIT:.0%} that voids a registration (§11)"
        )
    return Filled(out, tuple(missing), share)


def first_published(
    observations: Iterable[PointInTimeObservation], series_id: str
) -> Dict[date, float]:
    """§11: each day's outcome is its first-published value.

    Reads point-in-time observations (one per vintage) and keeps, per reference day, the
    value with the earliest `available_at`. Two vintages first published at the same instant
    with different values have no first value, and are refused.
    """

    earliest: Dict[date, PointInTimeObservation] = {}
    for observation in observations:
        if observation.series_id != series_id:
            continue
        held = earliest.get(observation.ref_date)
        if held is None or observation.available_at < held.available_at:
            earliest[observation.ref_date] = observation
        elif observation.available_at == held.available_at and observation.value != held.value:
            raise ProtocolError(
                f"{series_id} on {observation.ref_date} has two values first published at "
                f"{held.available_at}: {held.value} and {observation.value}"
            )
    return {day: float(observation.value) for day, observation in sorted(earliest.items())}


# --------------------------------------------------------------------------
# §5: the paired test
# --------------------------------------------------------------------------


def _long_run_variance(values: Sequence[float], lag: int) -> float:
    """The Newey-West (Bartlett) long-run variance of `values` at `lag`.

    Each lag's sum runs in C (`map` over `operator.mul`), because the studentized bootstrap
    computes it once per resample.
    """

    n = len(values)
    mean = sum(values) / n
    centred = list(map(mean.__rsub__, values))
    variance = sum(map(mul, centred, centred))
    for k in range(1, lag + 1):
        variance += 2.0 * (1.0 - k / (lag + 1.0)) * sum(map(mul, islice(centred, k, None), centred))
    return variance / n


def _bound(ordered: Sequence[float], level: float, draws: int) -> float:
    """The `level` quantile of sorted draws, refused where the draws cannot resolve it."""

    if not 0.0 < level < 1.0:
        raise ProtocolError(f"a one-sided level must be in (0, 1), got {level}")
    if min(level, 1.0 - level) * draws < 1.0:
        raise UnresolvedLevel(
            f"a one-sided bound at level {level:.6g} needs at least one draw beyond it; "
            f"{draws} draws resolve no level below {1.0 / draws:.6g}"
        )
    return _quantile(ordered, level)


@dataclass(frozen=True)
class PairedTest:
    """One candidate against one benchmark on the same days (§5).

    The interval is the studentized stationary bootstrap (Eleonora's ruling of 13 October
    2026 on PR #660): each resample's statistic is studentized by its own HAC standard error,
    and a bound is the point value less a quantile of those t-draws times the original HAC
    standard error.
    """

    days: Tuple[date, ...]
    #: mean of d_t = S(benchmark) - S(candidate); positive favours the candidate.
    mean_difference: float
    benchmark_mean: float
    #: mean(d) / mean(S(benchmark)).
    skill: float
    #: The HAC (Newey-West, `hac_lag`) standard error of mean(d).
    standard_error: float
    #: Sorted studentized draws `(mean* - mean) / se*`.
    t_draws: Tuple[float, ...]
    #: The HAC standard error of skill, from the linearised series `d - skill * b`, over mean(b);
    #: `None` when the test was made without skill.
    skill_standard_error: Optional[float]
    #: Sorted studentized draws of skill, `(skill* - skill) / se*(skill)`; empty without skill.
    skill_t_draws: Tuple[float, ...]
    #: Share of the t-draws at or above the observed statistic: the one-sided bootstrap p-value.
    p_value: float
    #: `mean / standard_error`: the Diebold-Mariano statistic, the observed t.
    dm_statistic: float
    #: One-sided normal p-value of `dm_statistic`, reported beside the bootstrap's.
    dm_p_value: float
    alpha: float
    draws: int
    block_length: float
    seed: int

    @property
    def n(self) -> int:
        return len(self.days)

    def lower_mean_difference(self, level: Optional[float] = None) -> float:
        """The one-sided lower bound of mean(d) at `level` (default: the test's `alpha`)."""

        level = self.alpha if level is None else level
        return self.mean_difference - _bound(self.t_draws, 1.0 - level, self.draws) * self.standard_error

    def upper_skill(self, level: Optional[float] = None) -> float:
        """The one-sided upper bound of skill at `level` (default: the test's `alpha`)."""

        if self.skill_standard_error is None:
            raise ProtocolError("this test was made without skill (with_skill=False)")
        level = self.alpha if level is None else level
        return self.skill - _bound(self.skill_t_draws, level, self.draws) * self.skill_standard_error


def diebold_mariano(differences: Sequence[float], lag: int = HAC_LAG) -> Tuple[float, float]:
    """§5: the Diebold-Mariano statistic of mean(d), Newey-West (Bartlett) variance at `lag`.

    Returns the statistic and its one-sided p-value against "the candidate is no better"
    (large positive statistics favour the candidate), on the normal approximation.
    """

    values = [_finite(value, "a daily difference") for value in differences]
    n = len(values)
    if n <= lag:
        raise ProtocolError(f"{n} days cannot carry a lag-{lag} long-run variance")
    variance = _long_run_variance(values, lag)
    if variance <= 0.0:
        raise ProtocolError("the daily differences have no variance; the two forecasts score alike")
    statistic = (sum(values) / n) / math.sqrt(variance / n)
    return statistic, 1.0 - _NORMAL.cdf(statistic)


def _standard_error(values: Sequence[float], lag: int, what: str) -> float:
    variance = _long_run_variance(values, lag)
    if variance <= 0.0:
        raise ProtocolError(f"{what} has no long-run variance; it cannot be studentized")
    return math.sqrt(variance / len(values))


def paired_tests(
    pairs: Sequence[Tuple[Mapping[date, float], Mapping[date, float]]],
    *,
    seed: int,
    alpha: float = ALPHA,
    draws: int = DRAWS,
    block_length: float = BLOCK_LENGTH,
    hac_lag: int = HAC_LAG,
    with_skill: bool = True,
) -> Tuple[PairedTest, ...]:
    """§5: each (benchmark scores, candidate scores) pair, tested on one resample stream.

    Every pair must cover the same decision days: the resamples are drawn once, with
    `metrics.stationary_bootstrap_indices` from `random.Random(seed)`, and every pair is
    read off the same draws, so a pair's result does not depend on which others share the
    call. Each resample's mean(d) is studentized by the resample's own HAC standard error.
    `with_skill=False` leaves out skill's bound, which doubles the work.

    Raises:
        ProtocolError: on pairs that do not cover the same days, a benchmark scoring zero
            (skill is undefined), or a series or resample with no long-run variance.
    """

    if not pairs:
        raise ProtocolError("no pairs to test")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ProtocolError(f"the seed must be an int fixed at registration, got {seed!r}")
    days = tuple(sorted(pairs[0][0]))
    if not days:
        raise ProtocolError("no scored days")
    n = len(days)
    if n <= hac_lag:
        raise ProtocolError(f"{n} days cannot carry a lag-{hac_lag} long-run variance")
    cells = []
    for benchmark, candidate in pairs:
        if tuple(sorted(benchmark)) != days or tuple(sorted(candidate)) != days:
            raise ProtocolError(
                "every benchmark and candidate in one call must score the same decision days"
            )
        bench = [_finite(benchmark[day], "a benchmark score") for day in days]
        cand = [_finite(candidate[day], "a candidate score") for day in days]
        diff = [b - c for b, c in zip(bench, cand)]
        benchmark_mean = sum(bench) / n
        if benchmark_mean == 0.0:
            raise ProtocolError("the benchmark scores zero on every day; skill is undefined")
        mean = sum(diff) / n
        se = _standard_error(diff, hac_lag, "the daily difference")
        skill = mean / benchmark_mean
        skill_se = None
        if with_skill:
            linear = [d - skill * b for d, b in zip(diff, bench)]
            skill_se = _standard_error(linear, hac_lag, "skill's linearised series") / benchmark_mean
        cells.append((bench, diff, mean, se, benchmark_mean, skill, skill_se, [], []))
    rng = random.Random(seed)
    for _ in range(draws):
        indices = stationary_bootstrap_indices(n, block_length, rng)
        for bench, diff, mean, se, _, skill, skill_se, t_out, skill_out in cells:
            resample = list(map(diff.__getitem__, indices))
            resampled_mean = sum(resample) / n
            t_out.append(
                (resampled_mean - mean) / _standard_error(resample, hac_lag, "a resampled difference")
            )
            if skill_se is not None:
                resampled_bench = list(map(bench.__getitem__, indices))
                bench_mean = sum(resampled_bench) / n
                if bench_mean == 0.0:
                    raise ProtocolError("a resampled benchmark scores zero; skill is undefined")
                resampled_skill = resampled_mean / bench_mean
                linear = list(map(lambda d, b: d - resampled_skill * b, resample, resampled_bench))
                resampled_se = _standard_error(linear, hac_lag, "a resampled skill") / bench_mean
                skill_out.append((resampled_skill - skill) / resampled_se)
    out = []
    for bench, diff, mean, se, benchmark_mean, skill, skill_se, t_out, skill_out in cells:
        ordered = sorted(t_out)
        statistic = mean / se
        out.append(
            PairedTest(
                days=days,
                mean_difference=mean,
                benchmark_mean=benchmark_mean,
                skill=skill,
                standard_error=se,
                t_draws=tuple(ordered),
                skill_standard_error=skill_se,
                skill_t_draws=tuple(sorted(skill_out)),
                p_value=sum(1 for value in ordered if value >= statistic) / draws,
                dm_statistic=statistic,
                dm_p_value=1.0 - _NORMAL.cdf(statistic),
                alpha=alpha,
                draws=draws,
                block_length=block_length,
                seed=seed,
            )
        )
    return tuple(out)


def paired_test(
    benchmark: Mapping[date, float], candidate: Mapping[date, float], *, seed: int, **settings
) -> PairedTest:
    """`paired_tests` for one pair."""

    return paired_tests([(benchmark, candidate)], seed=seed, **settings)[0]


def holm(p_values: Mapping[str, float], alpha: float = ALPHA) -> Dict[str, bool]:
    """Holm's step-down procedure: which hypotheses are rejected at family level `alpha`."""

    ordered = sorted(p_values.items(), key=lambda item: item[1])
    rejected = {name: False for name in p_values}
    for rank, (name, p) in enumerate(ordered):
        if p > alpha / (len(ordered) - rank):
            break
        rejected[name] = True
    return rejected


# --------------------------------------------------------------------------
# §6: alpha spending and the verdict
# --------------------------------------------------------------------------


def spending(fraction: float, alpha: float = ALPHA) -> float:
    """Lan-DeMets O'Brien-Fleming: the one-sided alpha spent by information `fraction`.

    `alpha(t) = 2 - 2 Phi(z_{1 - alpha/2} / sqrt(t))`, which spends exactly `alpha` at `t = 1`.
    """

    if not 0.0 < fraction <= 1.0:
        raise ProtocolError(f"an information fraction must be in (0, 1], got {fraction}")
    return 2.0 - 2.0 * _NORMAL.cdf(_NORMAL.inv_cdf(1.0 - alpha / 2.0) / math.sqrt(fraction))


def _simpson_weights(count: int, step: float) -> List[float]:
    return [
        (1.0 if k in (0, count - 1) else (4.0 if k % 2 else 2.0)) * step / 3.0
        for k in range(count)
    ]


def boundaries(
    checkpoints: Sequence[int] = CHECKPOINTS, alpha: float = ALPHA, *, nodes: int = 801
) -> Tuple[float, ...]:
    """§6: the efficacy boundary on the z scale at each checkpoint.

    The look-k boundary is set so that the probability, under no difference, of first
    crossing at look k is `spending(t_k) - spending(t_{k-1})`, with `t_k` the share of the last
    checkpoint's days. Computed by the Armitage-McPherson-Rowe recursion on the density of the
    partial-sum process over the continuation region, integrated by Simpson's rule.
    """

    if nodes % 2 == 0 or nodes < 101:
        raise ProtocolError("nodes must be odd and at least 101")
    looks = [int(c) for c in checkpoints]
    if not looks or any(b <= a for a, b in zip(looks, looks[1:])) or looks[0] < 1:
        raise ProtocolError(f"checkpoints must be ascending positive day counts, got {checkpoints}")
    fractions = [look / looks[-1] for look in looks]
    floor = -10.0
    out: List[float] = []
    grid: List[float] = []
    density: List[float] = []
    weights: List[float] = []
    spent = 0.0
    previous = 0.0
    for k, fraction in enumerate(fractions):
        target = spending(fraction, alpha) - spent
        root = math.sqrt(fraction)
        if k == 0:
            edge = root * _NORMAL.inv_cdf(1.0 - target)
        else:
            step_sd = math.sqrt(fraction - previous)

            def crossing(edge: float) -> float:
                return sum(
                    w * f * (1.0 - _NORMAL.cdf((edge - u) / step_sd))
                    for u, f, w in zip(grid, density, weights)
                )

            low, high = floor, 12.0
            for _ in range(80):
                middle = (low + high) / 2.0
                if crossing(middle) > target:
                    low = middle
                else:
                    high = middle
            edge = (low + high) / 2.0
        out.append(edge / root)
        step = (edge - floor) / (nodes - 1)
        new_grid = [floor + i * step for i in range(nodes)]
        if k == 0:
            new_density = [_NORMAL.pdf(s / root) / root for s in new_grid]
        else:
            new_density = [
                sum(
                    w * f * _NORMAL.pdf((s - u) / step_sd) / step_sd
                    for u, f, w in zip(grid, density, weights)
                )
                for s in new_grid
            ]
        grid, density, weights = new_grid, new_density, _simpson_weights(nodes, step)
        spent = spending(fraction, alpha)
        previous = fraction
    return tuple(out)


def nominal_levels(checkpoints: Sequence[int] = CHECKPOINTS, alpha: float = ALPHA) -> Tuple[float, ...]:
    """§6: the one-sided level each checkpoint's bootstrap bound is read at."""

    return _nominal_levels(tuple(int(c) for c in checkpoints), float(alpha))


@lru_cache(maxsize=None)
def _nominal_levels(checkpoints: Tuple[int, ...], alpha: float) -> Tuple[float, ...]:
    return tuple(1.0 - _NORMAL.cdf(bound) for bound in boundaries(checkpoints, alpha))


def verdict(
    against_b1: PairedTest,
    against_b2: PairedTest,
    *,
    look: int,
    futility_level: float,
    checkpoints: Sequence[int] = CHECKPOINTS,
    alpha: float = ALPHA,
    mme: float = MME,
) -> str:
    """§6: the verdict at checkpoint `look` (1-based) on the primary score.

    Supported: the lower bound of mean(d), at the look's nominal level, is above zero against
    B1 and against B2, and the point skill against B1 is at least the MME. Killed: the upper
    bound of skill against B1, at `futility_level`, is below the MME. Otherwise inconclusive,
    or "not shown" at the last checkpoint.

    `futility_level` has no default: §6 does not say at which level the futility bound is
    read, and that is Eleonora's call (asked in the pull request that closes #655).

    Raises:
        ProtocolError: the tests are not on the checkpoint's day count, or not on the same days.
        UnresolvedLevel: the look's nominal level is finer than the draws resolve.
    """

    if not 1 <= look <= len(checkpoints):
        raise ProtocolError(f"look must be 1 to {len(checkpoints)}, got {look}")
    days = checkpoints[look - 1]
    for name, test in (("B1", against_b1), ("B2", against_b2)):
        if test.n != days:
            raise ProtocolError(f"the test against {name} covers {test.n} days, not checkpoint {look}'s {days}")
    if against_b1.days != against_b2.days:
        raise ProtocolError("the tests against B1 and B2 must cover the same days")
    if look < len(checkpoints):
        for name, test in (("B1", against_b1), ("B2", against_b2)):
            if test.draws < INTERIM_DRAWS:
                raise ProtocolError(
                    f"the test against {name} has {test.draws} draws; an interim look is read on "
                    f"{INTERIM_DRAWS} (ruling of 13 October 2026, PR #660)"
                )
    level = nominal_levels(checkpoints, alpha)[look - 1]
    if (
        against_b1.lower_mean_difference(level) > 0.0
        and against_b2.lower_mean_difference(level) > 0.0
        and against_b1.skill >= mme
    ):
        return SUPPORTED
    if against_b1.upper_skill(futility_level) < mme:
        return KILLED
    return NOT_SHOWN if look == len(checkpoints) else INCONCLUSIVE
