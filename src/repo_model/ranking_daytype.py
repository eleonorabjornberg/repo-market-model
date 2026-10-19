"""Ranking the next 20 business days by tail probability combined with the day type (#765; H8 step 2, development tier).

`metadata/ranking_765.json` is the declaration; this module is its arithmetic, on top of `repo_model.ranking` (#694), which it
does not edit. The tail probability is the step-1 one: P(spread > +5 bp) from the model of #686 on 20 leads. Three rankers:

- `calendar_then_tail` (a): the calendar's ordering first (a scheduled risk date above any other day), the tail probability
  inside each of the two groups;
- `tail_by_type` (b): the tail probability with the residuals of the fit pooled by the target's day type (the leads within
  `POOL_BAND` of the target's lead), the lead's own all-type residuals when the pool holds fewer than `MIN_POOL`;
- `blend` (c): a weighted mean of the window mid-ranks of the calendar and of the tail probability, the weight chosen from
  `WEIGHT_GRID` at each refit on the trailing scored windows whose 20 targets are all public by then.

Everything is as-of. The day type is read from the target row's calendar columns, known in advance; every spread a pool
residual or a trailing outcome reads is at or before the anchor (`protocol_benchmarks._require_public` raises
`LookAheadError`). Ties are broken by their expected value over a random order (`ranking.top_k_hits`). Stdlib only.
"""

from __future__ import annotations

from datetime import date, time
from typing import Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import ranking
from . import spread_mean_reversion as smr
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .splits import SplitError

#: The pool of a (type, lead) takes the residuals of the leads within this many of it.
POOL_BAND = 2
#: A pool with fewer residuals falls back to the lead's own all-type residuals.
MIN_POOL = 30
#: The weight on the calendar rank in the blend.
WEIGHT_GRID: Tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
#: The weight before `MIN_TRAILING` trailing windows exist.
DEFAULT_WEIGHT = 0.5
#: The most trailing scored windows the weight is chosen on, and the fewest.
TRAILING = 252
MIN_TRAILING = 60
#: The top-k the weight is chosen on.
CHOOSE_K = 5

CANDIDATES: Tuple[str, ...] = ("calendar_then_tail", "tail_by_type", "blend")
BENCHMARKS: Tuple[str, ...] = ranking.BENCHMARKS
#: Shown beside the benchmarks for context; not one of the declared rankers.
REFERENCE = "model_prob"
RANKERS: Tuple[str, ...] = CANDIDATES + BENCHMARKS + (REFERENCE,)
TIES: Mapping[str, str] = {**ranking.TIES, **{name: "expected" for name in CANDIDATES}}


class Window(NamedTuple):
    """A scored window kept for the weight: its decision row, and its calendar and tail scores per lead."""

    index: int
    calendar: Sequence[float]
    tail: Sequence[float]


# -- the arithmetic of the blend ---------------------------------------------------------------------------------------


def rank_scores(values: Sequence[float]) -> List[float]:
    """The mid-rank of each value in (0, 1): (values below + half of the values tied with it, itself included) / n."""

    n = len(values)
    out = []
    for value in values:
        below = sum(1 for other in values if other < value)
        tied = sum(1 for other in values if other == value)
        out.append((below + tied / 2.0) / n)
    return out


def blend_scores(calendar: Sequence[float], tail: Sequence[float], weight: float) -> List[float]:
    """`weight` x the calendar mid-rank + (1 - weight) x the tail mid-rank.

    Raises:
        ValueError: a weight outside `WEIGHT_GRID`.
    """

    if weight not in WEIGHT_GRID:
        raise ValueError(f"weight {weight} is not in the declared grid {WEIGHT_GRID}")
    return [weight * c + (1.0 - weight) * t for c, t in zip(rank_scores(calendar), rank_scores(tail))]


def calendar_then_tail(calendar: Sequence[float], tail: Sequence[float]) -> List[float]:
    """2 x the calendar flag + the tail probability: a risk date always above a quiet day, the tail inside each group."""

    return [2.0 * c + t for c, t in zip(calendar, tail)]


def _mean_precision(windows: Sequence[Tuple[Sequence[float], Sequence[float], Sequence[int]]], weight: float) -> float:
    total = 0.0
    for calendar, tail, flags in windows:
        total += ranking.top_k_hits(blend_scores(calendar, tail, weight), flags, CHOOSE_K, "expected") / CHOOSE_K
    return total / len(windows)


def choose_weight(windows: Sequence[Tuple[Sequence[float], Sequence[float], Sequence[int]]]) -> Tuple[float, int]:
    """The weight of `WEIGHT_GRID` with the highest mean top-5 precision over the latest `TRAILING` of `windows`.

    `windows` are (calendar scores, tail scores, realised flags) in time order. A tie goes to the smaller weight. With
    fewer than `MIN_TRAILING` windows the weight is `DEFAULT_WEIGHT`. Returns the weight and the windows it was chosen on.
    """

    used = list(windows)[-TRAILING:]
    if len(used) < MIN_TRAILING:
        return DEFAULT_WEIGHT, len(used)
    best = max(WEIGHT_GRID, key=lambda w: (_mean_precision(used, w), -w))
    return best, len(used)


def trailing_windows(
    history: Sequence[Window], panel: Sequence[DailyObservation], anchor: int
) -> List[Tuple[Sequence[float], Sequence[float], Sequence[int]]]:
    """The windows of `history` whose 20 targets are all at or before the anchor, with their realised flags.

    Mutation record: replacing `if window.index + max(ranking.LEADS) <= anchor:` with `... <= anchor + 5:` makes
    `tests/test_ranking_daytype.WeightTests.test_a_change_to_every_spread_after_the_anchor_moves_no_weight` fail with
    `LookAheadError`; restored, it passes.

    Raises:
        LookAheadError: an outcome row after the anchor is read.
    """

    dates = [row.date for row in panel]
    out = []
    for window in history:
        if window.index + max(ranking.LEADS) <= anchor:
            pb._require_public(
                [window.index + h for h in ranking.LEADS], anchor, dates, f"the weight of the blend, window {dates[window.index]}"
            )
            out.append((window.calendar, window.tail, ranking.realised(panel, window.index)))
    return out


# -- the day-type pools ------------------------------------------------------------------------------------------------


def residual_pools(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: smr.Fit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    leads: Sequence[int] = ranking.LEADS,
    rows: Optional[Mapping[int, Sequence[Tuple[int, int]]]] = None,
) -> Dict[Tuple[str, int], List[float]]:
    """Per (day type, lead), the sorted residuals of the training pairs of the leads within `POOL_BAND` whose target has the type.

    A residual is the one `ranking.fit` defines: the target deviation from the origin's level less phi^k times the origin
    deviation, k the pair's own row distance. `rows` are the (origin, target) pairs per lead (default: the fit's own).

    Mutation record: replacing `pb._require_public(targets, anchor, ...)` with `pb._require_public(targets, anchor + 400, ...)`
    makes `tests/test_ranking_daytype.PoolTests.test_a_pool_pair_after_the_anchor_is_refused` fail with `AssertionError`
    ("LookAheadError not raised"); restored, it passes.

    Raises:
        LookAheadError: a pair reads a row after the anchor.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    if rows is None:
        rows = ranking.training_rows(panel, decision_index, anchor, lag=lag, levels=levels, leads=leads)
    dates = [row.date for row in panel]
    targets = {s for pairs in rows.values() for _, s in pairs} | {o for pairs in rows.values() for o, _ in pairs}
    pb._require_public(targets, anchor, dates, f"the day-type pools for {dates[decision_index]}")
    kinds: Dict[int, str] = {}
    by_lead: Dict[Tuple[str, int], List[float]] = {}
    for h in leads:
        k = h + lag
        for origin, target in rows[h]:
            if target not in kinds:
                kinds[target] = splits.reporting_day_type(panel[target].date, panel[target].values)
            residual = (panel[target].spread_bps - levels[origin]) - fit_.phi**k * (panel[origin].spread_bps - levels[origin])
            by_lead.setdefault((kinds[target], h), []).append(residual)
    pools: Dict[Tuple[str, int], List[float]] = {}
    for kind in {key[0] for key in by_lead}:
        for lead in leads:
            pooled = [
                value
                for h in leads
                if abs(h - lead) <= POOL_BAND
                for value in by_lead.get((kind, h), ())
            ]
            if pooled:
                pools[(kind, lead)] = sorted(pooled)
    return pools


def typed_quantiles(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: smr.Fit,
    pools: Mapping[Tuple[str, int], Sequence[float]],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    leads: Sequence[int] = ranking.LEADS,
) -> Tuple[Dict[int, List[float]], Dict[int, bool]]:
    """Per lead, the 23 quantiles with the target's day-type residual pool, and whether the lead fell back to the all-type residuals.

    Raises:
        InsufficientHistory: the anchor has no level.
    """

    ranking._need_rows(panel, decision_index, leads)
    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level = levels[anchor]
    if level is None:
        raise smr.InsufficientHistory(f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor")
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    quantiles: Dict[int, List[float]] = {}
    fallback: Dict[int, bool] = {}
    for h in leads:
        target = panel[decision_index + h]
        pool = pools.get((splits.reporting_day_type(target.date, target.values), h), ())
        centre = level + fit_.phi ** (h + lag) * (last - level)
        if len(pool) >= MIN_POOL:
            quantiles[h] = pb.empirical_quantiles(list(pool), centre)
            fallback[h] = False
        else:
            quantiles[h] = [centre + value for value in fit_.residuals[h]]
            fallback[h] = True
    return quantiles, fallback


def _window_scores(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: smr.Fit,
    pools: Mapping[Tuple[str, int], Sequence[float]],
    **settings,
) -> Tuple[Dict[str, List[float]], Dict[int, bool]]:
    scores = ranking.window_scores(panel, decision_index, fit_, **settings)
    quantiles, fallback = typed_quantiles(panel, decision_index, fit_, pools, **settings)
    leads = settings.get("leads", ranking.LEADS)
    scores["tail_by_type"] = [smr.exceedance(quantiles[h]) for h in leads]
    scores["calendar_then_tail"] = calendar_then_tail(scores["calendar"], scores["model_prob"])
    return scores, fallback


def window_scores(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: smr.Fit,
    pools: Mapping[Tuple[str, int], Sequence[float]],
    **settings,
) -> Dict[str, List[float]]:
    """The scores of `calendar_then_tail` and `tail_by_type` beside the five of step 1, from information public at the decision instant."""

    return _window_scores(panel, decision_index, fit_, pools, **settings)[0]


class Walk:
    """The scored windows of a run of decision days."""

    def __init__(self) -> None:
        self.scores: Dict[date, Dict[str, List[float]]] = {}
        self.fits: Dict[date, smr.Fit] = {}
        self.fit_used: Dict[date, date] = {}
        #: Refit day -> (the blend's weight, the trailing windows it was chosen on).
        self.weights: Dict[date, Tuple[float, int]] = {}
        #: Decision day -> the weight in force.
        self.weight_used: Dict[date, float] = {}
        self.skipped: List[date] = []
        self.fallback_leads = 0
        self.leads_seen = 0

    def fallback_share(self) -> float:
        return self.fallback_leads / self.leads_seen if self.leads_seen else 0.0


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    leads: Sequence[int] = ranking.LEADS,
) -> Walk:
    """The windows of `decision_days`, refitting (the model, the pools and the blend's weight) on the first day with a forecast and every `refit_every`-th after it."""

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels, leads=leads)
    out = Walk()
    history: List[Window] = []
    current: Optional[smr.Fit] = None
    pools: Mapping[Tuple[str, int], Sequence[float]] = {}
    weight = DEFAULT_WEIGHT
    since = 0
    for day in decision_days:
        if day not in position:
            raise ranking.ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                fitted = ranking.fit(panel, index, **settings)
                pools = residual_pools(panel, index, fitted, **settings)
                anchor = pb._anchor(panel, index, registry, decision_time)
                chosen = choose_weight(trailing_windows(history, panel, anchor))
                current = fitted
                weight = chosen[0]
                out.fits[day] = current
                out.weights[day] = chosen
                since = 0
            scores, fallback = _window_scores(panel, index, current, pools, **settings)
        except smr.InsufficientHistory:
            out.skipped.append(day)
            continue
        except SplitError:
            if current is not None:
                raise
            out.skipped.append(day)
            continue
        except ranking.NoDayOfType:
            out.skipped.append(day)
            continue
        scores["blend"] = blend_scores(scores["calendar"], scores["model_prob"], weight)
        out.scores[day] = scores
        out.fit_used[day] = current.fitted_on
        out.weight_used[day] = weight
        out.leads_seen += len(fallback)
        out.fallback_leads += sum(1 for v in fallback.values() if v)
        history.append(Window(index, scores["calendar"], scores["model_prob"]))
        since += 1
    return out
