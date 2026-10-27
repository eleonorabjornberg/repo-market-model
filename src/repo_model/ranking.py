"""Ranking the next 20 business days by risk (#694; H8, development tier).

`metadata/ranking_694.json` is the declaration; this module is its arithmetic. At a decision day the 20 panel rows after
it are ranked by a risk score, and the top k are scored against the days that were realised pressure days (the
whole-basis-point event of `data.exceeds_bp`, strictly above +5 bp).

Five rankers, each a risk score per lead h = 1..20:

- `model_prob`, `model_median`: the model of #686 (`spread_mean_reversion`) extended to 20 leads, read as P(spread > +5 bp)
  and as the predicted median;
- `persistence`: P(spread > +5 bp) from B1 (the anchor plus the trailing two years' h-row changes), on 20 leads;
- `climatology`: the share of pressure days among the trailing year's days of the target's type (B2's window and type);
- `calendar`: 1 on a scheduled risk date (a quarter-end, a tax date, or a coupon settlement where it was public at the
  decision instant, #770), else 0, the earliest date first on a tie.

Everything a ranker reads is as-of: the anchor is the last row public at the decision instant
(`protocol_benchmarks._anchor`), no spread after it is read (`protocol_benchmarks._require_public` raises
`LookAheadError`), and the calendar columns of the target days are known ahead, as the day-type groupings already read
them. Ties are broken by their expected value over a random order, so that no ranker gains from an arbitrary order,
except the calendar's, which is declared to break them by date. Stdlib only.
"""

from __future__ import annotations

from datetime import date, time
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import turn_days
from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import lockbox
from .asof import InformationRule
from .contract import field_sources_for_features
from .data import DailyObservation, exceeds_bp
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import GRID, ProtocolError
from .splits import LookAheadError, SplitError

#: The leads ranked: the 20 business days after the decision day.
LEADS: Tuple[int, ...] = tuple(range(1, 21))
#: Top-k cutoffs.
TOP_K: Tuple[int, ...] = (3, 5)
#: The coupon-settlement column the calendar ranker reads, where it was public (`risk_dates.COUPONS`).
SETTLEMENT_COLUMN = "treasury_settlement_coupons"
#: The pressure threshold, in bp.
TAU = smr.TAIL_TAU
#: The declared last scored day (`metadata/ranking_694.json`).
LAST_DAY = date(2025, 12, 31)
#: The rankers that are candidates, and the benchmarks.
CANDIDATES: Tuple[str, ...] = ("model_prob", "model_median")
BENCHMARKS: Tuple[str, ...] = ("persistence", "climatology", "calendar")
RANKERS: Tuple[str, ...] = CANDIDATES + BENCHMARKS
#: How each ranker breaks a tie.
TIES: Mapping[str, str] = {
    "model_prob": "expected", "model_median": "expected", "persistence": "expected",
    "climatology": "expected", "calendar": "first",
}


class NoDayOfType(ProtocolError):
    """The climatology window holds no day of some target's type."""


# -- the top-k arithmetic -------------------------------------------------------------------------------------------


def top_k_hits(scores: Sequence[float], flags: Sequence[int], k: int, ties: str = "expected") -> float:
    """The pressure days among the top `k` days by `scores`, a tie across the cutoff resolved by `ties`.

    `ties="expected"`: a tie group that straddles the cutoff contributes its pressure days in proportion to the places
    left (the expectation over a random order). `ties="first"`: the earliest days of the group (by position) are taken.

    Raises:
        ValueError: unequal lengths, `k` outside 1..len(scores), or an unknown tie rule.
    """

    if ties not in ("expected", "first"):
        raise ValueError(f"unknown tie rule {ties!r}")
    if len(scores) != len(flags):
        raise ValueError(f"{len(scores)} scores and {len(flags)} flags")
    if not 1 <= k <= len(scores):
        raise ValueError(f"k = {k} is outside 1..{len(scores)}")
    groups: Dict[float, List[int]] = {}
    for position, value in enumerate(scores):
        groups.setdefault(value, []).append(position)
    left = k
    hits = 0.0
    for value in sorted(groups, reverse=True):
        members = groups[value]
        if len(members) <= left:
            hits += sum(flags[p] for p in members)
            left -= len(members)
        else:
            if ties == "expected":
                hits += left * sum(flags[p] for p in members) / len(members)
            else:
                hits += sum(flags[p] for p in members[:left])
            left = 0
        if left == 0:
            break
    return hits


def window_metrics(
    scores: Sequence[float], flags: Sequence[int], ks: Iterable[int] = TOP_K, ties: str = "expected"
) -> Dict[int, Dict[str, Optional[float]]]:
    """Per k: the hits, precision (hits / k) and recall (hits / pressure days in the window; `None` if there is none)."""

    total = sum(flags)
    out: Dict[int, Dict[str, Optional[float]]] = {}
    for k in ks:
        hits = top_k_hits(scores, flags, k, ties)
        out[k] = {"hits": hits, "precision": hits / k, "recall": hits / total if total else None}
    return out


def realised(panel: Sequence[DailyObservation], decision_index: int, leads: Sequence[int] = LEADS) -> List[int]:
    """1 for each lead whose target day is a pressure day (strictly above +5 bp on whole basis points)."""

    return [int(exceeds_bp(panel[decision_index + h].spread_bps, TAU)) for h in leads]


def require_scored_days(days: Iterable[date], last: date = LAST_DAY) -> None:
    """Refuse a day after `last`, the declared end of the scored days, and a locked day.

    Mutation record: replacing `if day > last:` with `if day > last + timedelta(days=400):` makes
    `test_ranking.ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with `AssertionError`
    ("LookAheadError not raised"); restored, it passes.

    Raises:
        LookAheadError: a day after `last`, or in a locked tier.
    """

    days = list(days)
    for day in sorted(days):
        if day > last:
            raise LookAheadError(f"{day} is after {last}, the last day #694 scores; the declaration admits no later day")
    lockbox.require_unlocked(days, where="repo_model.ranking")


# -- the candidate on 20 leads ---------------------------------------------------------------------------------------


def _need_rows(panel: Sequence[DailyObservation], decision_index: int, leads: Sequence[int]) -> None:
    if decision_index + max(leads) >= len(panel):
        raise ProtocolError(
            f"lead {max(leads)} from {panel[decision_index].date} has no row in the panel; the panel must carry the target rows"
        )


def training_rows(
    panel: Sequence[DailyObservation],
    decision_index: int,
    anchor: int,
    *,
    lag: int,
    levels: Sequence[Optional[float]],
    leads: Sequence[int] = LEADS,
) -> Dict[int, List[Tuple[int, int]]]:
    """Per lead h, the (origin, target) rows of the training pairs, `k = h + lag` rows apart: `smr.training_rows` on `leads`.

    The target is in the trailing window and at or before the anchor; the origin has a level. Every row read is
    required public (`protocol_benchmarks._require_public`).

    Raises:
        LookAheadError: a row after the anchor is among the pairs.
    """

    dates = [row.date for row in panel]
    first = pb._window_start(panel, decision_index, smr.TRAIN_YEARS)
    out: Dict[int, List[Tuple[int, int]]] = {}
    for h in leads:
        k = h + lag
        pairs = []
        for target in range(max(first, k), anchor + 1):
            origin = target - k
            if levels[origin] is not None:
                pairs.append((origin, target))
        rows = {row for pair in pairs for row in pair}
        pb._require_public(rows, anchor, dates, f"the ranking fit for {dates[decision_index]}, lead {h}")
        out[h] = pairs
    return out


def fit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    leads: Sequence[int] = LEADS,
) -> smr.Fit:
    """phi and the residual quantiles per lead of `leads`, as of the decision: `smr.fit` on more leads.

    Raises:
        ProtocolError: a target row of some lead is not in the panel.
        InsufficientHistory: fewer than `smr.MIN_PAIRS` training pairs at some lead.
        LookAheadError, StaleReadError: the information-set guards of the decision.
    """

    _need_rows(panel, decision_index, leads)
    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = training_rows(panel, decision_index, anchor, lag=lag, levels=levels, leads=leads)
    short = [h for h in leads if len(rows[h]) < smr.MIN_PAIRS]
    if short:
        raise smr.InsufficientHistory(
            f"{panel[decision_index].date}: lead {short[0]} has {len(rows[short[0]])} training pairs, "
            f"fewer than the {smr.MIN_PAIRS} the declaration requires"
        )
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    pairs = []
    deviations: Dict[int, List[Tuple[float, float]]] = {}
    for h in leads:
        k = h + lag
        deviations[h] = [(spreads[o] - levels[o], spreads[s] - levels[o]) for o, s in rows[h]]
        pairs.extend((k, x, y) for x, y in deviations[h])
    phi = smr.fit_phi(pairs)
    residuals = {}
    for h in leads:
        k = h + lag
        residuals[h] = pb.empirical_quantiles(sorted(y - phi**k * x for x, y in deviations[h]))
    return smr.Fit(phi, residuals, {h: len(rows[h]) for h in leads}, panel[decision_index].date)


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: smr.Fit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    leads: Sequence[int] = LEADS,
) -> Dict[int, List[float]]:
    """The decision day's 23 quantiles per lead from `fit_`: `last`, `level` and the row lag read afresh.

    Raises:
        InsufficientHistory: the anchor has no level.
    """

    _need_rows(panel, decision_index, leads)
    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level = levels[anchor]
    if level is None:
        raise smr.InsufficientHistory(f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor")
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    return {
        h: [level + fit_.phi ** (h + lag) * (last - level) + value for value in fit_.residuals[h]] for h in leads
    }


# -- the benchmarks ---------------------------------------------------------------------------------------------------


def b1_forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    leads: Sequence[int] = LEADS,
) -> Dict[int, List[float]]:
    """B1 (`protocol_benchmarks.b1_forecast`) on `leads`: the last public spread plus the trailing two years' h-row changes."""

    _need_rows(panel, decision_index, leads)
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    dates = [row.date for row in panel]
    first = pb._window_start(panel, decision_index, pb.B1_YEARS)
    last = panel[anchor].spread_bps
    out = {}
    for h in leads:
        ends = list(range(max(first, h), anchor + 1))
        if not ends:
            raise ProtocolError(f"B1 has no {h}-day change before {dates[anchor]}")
        pb._require_public(ends, anchor, dates, f"B1 for {dates[decision_index]}, lead {h}")
        out[h] = pb.empirical_quantiles(sorted(panel[s].spread_bps - panel[s - h].spread_bps for s in ends), last)
    return out


def type_share(kinds: Sequence[str], pressure: Sequence[bool], kind: str) -> float:
    """The share of the days of type `kind` that were pressure days.

    Raises:
        ProtocolError: no day of that type.
    """

    same = [flag for k, flag in zip(kinds, pressure) if k == kind]
    if not same:
        raise NoDayOfType(f"no {kind} day in the window to take a share from")
    return sum(1 for flag in same if flag) / len(same)


def climatology(
    panel: Sequence[DailyObservation],
    decision_index: int,
    anchor: int,
    *,
    splits: SplitDeclaration,
    leads: Sequence[int] = LEADS,
) -> List[float]:
    """Per lead, the share of pressure days among the trailing year's days (up to the anchor) of the target's type."""

    dates = [row.date for row in panel]
    first = pb._window_start(panel, decision_index, pb.B2_YEARS)
    rows = list(range(first, anchor + 1))
    pb._require_public(rows, anchor, dates, f"climatology for {dates[decision_index]}")
    kinds = [turn_days.reporting_day_type(splits, panel[s].date, panel[s].values) for s in rows]
    pressure = [exceeds_bp(panel[s].spread_bps, TAU) for s in rows]
    out = []
    for h in leads:
        target = panel[decision_index + h]
        out.append(type_share(kinds, pressure, turn_days.reporting_day_type(splits, target.date, target.values)))
    return out


def calendar(
    panel: Sequence[DailyObservation],
    decision_index: int,
    leads: Sequence[int] = LEADS,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> List[float]:
    """1.0 on a scheduled risk date, else 0.0, per lead, as far as the decision instant knew it (#770).

    A quarter-end and a tax date are calendar facts, known ahead. A coupon settlement counts at a lead only where its
    column is declared observable at or before the decision instant (the information-set rule; Eleonora's ruling on
    #720, 13 October 2026, point 2): where the settlement was not yet announced, the target day is not a settlement
    risk date and the flag is not read. Under the published declaration a settlement is public one panel day ahead, so
    the coupon clause counts at lead 1 only.
    """

    dates = [row.date for row in panel]
    scores: List[float] = []
    for h in leads:
        scored = decision_index + h
        values = panel[scored].values
        risk = float(values["quarter_end"] or 0.0) == 1.0 or float(values["tax_date"] or 0.0) == 1.0
        coupons = values.get(SETTLEMENT_COLUMN)
        if not risk and coupons is not None and float(coupons) > 0.0:
            rule = InformationRule(registry, (), decision_time=decision_time, horizon=h)
            available = rule.availability(dates, field_sources_for_features((SETTLEMENT_COLUMN,)), scored)
            risk = available <= rule.decision_instant(dates, scored)
        scores.append(1.0 if risk else 0.0)
    return scores


def window_scores(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: smr.Fit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    leads: Sequence[int] = LEADS,
) -> Dict[str, List[float]]:
    """The risk score of each ranker for each lead of `leads`, from information public at the decision instant."""

    settings = dict(registry=registry, decision_time=decision_time)
    quantiles = forecast(panel, decision_index, fit_, splits=splits, levels=levels, leads=leads, **settings)
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    one = b1_forecast(panel, decision_index, leads=leads, **settings)
    middle = GRID.index(0.5)
    return {
        "model_prob": [smr.exceedance(quantiles[h]) for h in leads],
        "model_median": [quantiles[h][middle] for h in leads],
        "persistence": [smr.exceedance(one[h]) for h in leads],
        "climatology": climatology(panel, decision_index, anchor, splits=splits, leads=leads),
        "calendar": calendar(panel, decision_index, leads, **settings),
    }


class Walk:
    """The scored windows of a run of decision days."""

    def __init__(self) -> None:
        self.scores: Dict[date, Dict[str, List[float]]] = {}
        self.fits: Dict[date, smr.Fit] = {}
        self.fit_used: Dict[date, date] = {}
        #: Decision days with no ranking, for want of history or of a day of some target's type.
        self.skipped: List[date] = []


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    leads: Sequence[int] = LEADS,
) -> Walk:
    """The windows of `decision_days`, refitting on the first day with a forecast and every `refit_every`-th after it."""

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels, leads=leads)
    out = Walk()
    current: Optional[smr.Fit] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                current = fit(panel, index, **settings)
                out.fits[day] = current
                since = 0
            out.scores[day] = window_scores(panel, index, current, **settings)
        except smr.InsufficientHistory:
            out.skipped.append(day)
            continue
        except LookAheadError:
            raise  # a guard trip is never "no public row yet"
        except SplitError:
            if current is not None:
                raise
            out.skipped.append(day)
            continue
        except NoDayOfType:
            out.skipped.append(day)
            continue
        out.fit_used[day] = current.fitted_on
        since += 1
    return out
