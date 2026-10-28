"""(s3c-mbs): (s3c) with indicators for the settlement days of the agency MBS classes A to D (#1276; H5 step 3).

Eleonora, 27 October 2026 (chat, relayed; ledger item 68 on #1116): queue four arms on (s3c), one directive each, independent of each other. This is the
fourth: agency MBS settlement days may move GC through the month, and (s3c) has no MBS term. The source is SIFMA's published settlement dates of the
agency MBS classes (`repo_model.sifma_mbs`); this module adds the arm. (s3c) is (s3) of #1145 (`repo_model.spread_mr_state_calendar`, arm `sc_s3_robust`: calendar
terms in standardised units, Huber fit, ridge 5) with its quantiles clipped at the SRF line from full allotment (`repo_model.s3c_candidate`). The arm adds
indicator terms to (s3)'s fit and leaves every other term, the fit and the cap as they are.

**The terms.** One 0/1 indicator per class, `mbs_a` to `mbs_d`, 1 on the target day when it is a settlement day of that class; or, when a class has
fewer than `MIN_CLASS_DAYS` = 20 settlement days in the window (`class_counts`, `must_pool`), one indicator `mbs_any` that is 1 on a settlement day of any
class. An indicator is a function of the target row's own date and of the source's availability: it is read as 1 only if the day's year was public at the
decision instant (`sifma_mbs.public_at`), and otherwise as 0, never as an earlier date in its place. The decision of a row `r` read at lead `lead` is the
decision at row `r - lead` (16:00 on its day), so a training pair reads what its own decision could read, as `repo_model.s3c_net.NetSizeTable` does.

**The fit.** `fit_mbs_terms` is (s3)'s Huber fit of one lead with the indicator columns added, in standardised units: the target is `raw / scale(origin)`,
the columns are (s3)'s entering flag terms and the indicators that at least `MIN_FLAGGED` = 3 training pairs carry, with ridge 5 on every coefficient and no
penalty on the intercept, which is then dropped from the pool as for the flag terms. A forecast adds `scale(anchor) * sum(coefficient_k * indicator_k)` to
every quantile, beside the shift and the pool of the fit. Where no indicator enters, the estimate is `fit_state_terms`' on the same pairs, element for element.

**Direct pairs.** A training pair reads its indicator from its own target row (`training_pairs="direct"`); `fit_mbs_terms` is decorated with
`one_step_guard.guard_one_step_fit`, with no allow-list entry, and trains on direct pairs only.

Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import sifma_mbs
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from . import spread_mr_state_calendar as sc
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

__all__ = [
    "ARM", "CLASS_TERMS", "MIN_CLASS_DAYS", "POOLED_TERM", "MbsEstimate", "MbsTable", "MbsWalk", "class_counts", "effect_bp", "fit_mbs_terms",
    "forecast_leads", "must_pool", "refit", "walk",
]

#: One indicator per class (`sifma_mbs.CLASSES`), and the single indicator the classes pool into.
CLASS_TERMS: Tuple[str, ...] = tuple("mbs_" + k.lower() for k in sifma_mbs.CLASSES)
POOLED_TERM = "mbs_any"
#: A class with fewer settlement days than this in the window pools the classes (the directive's rule).
MIN_CLASS_DAYS = 20
#: (s3)'s arm, whose terms, fit and ridge the indicators join.
ARM = sc.ARMS[2]


class MbsTable:
    """The MBS settlement indicators at every panel row, as the decision `lead` rows before could read them.

    The value for target row `r` read at lead `lead` is the indicator of `dates[r]` under the availability rule at the decision instant of row
    `r - lead` (`decision_time` on that day). All leads are readable: a calendar public before the decision is as public at lead 5 as at lead 1.
    """

    def __init__(
        self,
        panel: Sequence[DailyObservation],
        sifma: Mapping[str, FrozenSet[date]],
        public_from: Mapping[int, Optional[datetime]],
        *,
        pooled: bool = False,
        decision_time: time = time(16, 0),
    ):
        self.dates = [row.date for row in panel]
        self.pooled = pooled
        self.terms: Tuple[str, ...] = (POOLED_TERM,) if pooled else CLASS_TERMS
        self._sifma, self._public, self._time = sifma, public_from, decision_time
        self._cache: Dict[Tuple[int, int], Dict[str, int]] = {}

    def _value(self, decision_row: int, target_row: int) -> Dict[str, int]:
        """The indicators of the target row as the decision on `decision_row` reads them.

        Raises:
            ValueError: a row outside the panel.

        Mutation record: see `tests/test_s3c_mbs.py` (`MbsTable._value`).
        """

        if decision_row < 0 or target_row >= len(self.dates) or decision_row >= target_row:
            raise ValueError(f"row {target_row} read at the decision of row {decision_row} is outside the panel")
        key = (decision_row, target_row)
        if key not in self._cache:
            instant = datetime.combine(self.dates[decision_row], self._time)
            flags = sifma_mbs.flags(self._sifma, self._public, self.dates[target_row], instant)
            if self.pooled:
                self._cache[key] = {POOLED_TERM: 1 if any(flags.values()) else 0}
            else:
                self._cache[key] = {"mbs_" + k.lower(): v for k, v in flags.items()}
        return self._cache[key]

    def flags_at(self, lead: int, row: int) -> Dict[str, int]:
        """The indicators of target row `row`, as the decision `lead` rows earlier read them (a training pair's, or a forecast's)."""

        return dict(self._value(row - lead, row))

    def read(self, lead: int, decision_index: int) -> Dict[str, int]:
        """The indicators a forecast of the decision on row `decision_index` at `lead` reads, from its target row."""

        return self.flags_at(lead, cal.target_row(decision_index, lead))


def class_counts(
    panel: Sequence[DailyObservation],
    sifma: Mapping[str, FrozenSet[date]],
    public_from: Mapping[int, Optional[datetime]],
    *,
    last: date,
    decision_time: time = time(16, 0),
) -> Dict[str, int]:
    """The settlement days of each class in the window: panel rows up to `last` whose indicator, as the decision the row before reads it, is 1."""

    table = MbsTable(panel, sifma, public_from, decision_time=decision_time)
    counts = {k: 0 for k in sifma_mbs.CLASSES}
    for row, day in enumerate(table.dates):
        if row == 0 or day > last:
            continue
        for k in sifma_mbs.CLASSES:
            counts[k] += table.flags_at(1, row)["mbs_" + k.lower()]
    return counts


def must_pool(counts: Mapping[str, int]) -> bool:
    """Whether a class has fewer than `MIN_CLASS_DAYS` settlement days in the window, so that the classes pool into one indicator."""

    return any(n < MIN_CLASS_DAYS for n in counts.values())


# -- the fit -----------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class MbsEstimate:
    """One lead's estimate: (s3)'s kind of estimate (`state`, whose pool is the pool after the indicators too) and the indicators' coefficients.

    `coefficient` has every indicator of the table, 0 where it did not enter; `active` lists those that did; `counts` are the training pairs that
    carry each indicator.
    """

    state: sc.StateEstimate
    coefficient: Mapping[str, float]
    active: Tuple[str, ...]
    counts: Mapping[str, int]


@guard_one_step_fit
def fit_mbs_terms(
    pairs: Sequence[sc.StatePair],
    mbs: Sequence[Mapping[str, int]],
    *,
    regressors: Sequence[str],
    terms: Sequence[str],
    mbs_terms: Sequence[str],
    training_pairs: str,
    min_flagged: int = sc.MIN_FLAGGED,
    ridge: float = sc.ROBUST_RIDGE,
    baseline: Optional[sc.StateEstimate] = None,
) -> MbsEstimate:
    """(s3)'s Huber fit of one lead with the MBS indicator columns added, in standardised units.

    `mbs[i]` holds the indicators of pair `i`, read at its target row as of its own decision. An indicator enters when at least `min_flagged` pairs carry
    it. Where none enters the estimate is `fit_state_terms`' (or `baseline`, the same call made by the caller on these pairs).

    Raises:
        ValueError: `training_pairs` is not `'direct'`, or one row of indicators per pair is not given.
        InsufficientHistory: there is no pair.

    Mutation record: see `tests/test_s3c_mbs.py` (`fit_mbs_terms`).
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_mbs_terms trains on direct pairs only, got training_pairs={training_pairs!r}")
    if len(mbs) != len(pairs):
        raise ValueError("fit_mbs_terms needs one row of indicators per pair")
    counts = {name: sum(int(m[name]) for m in mbs) for name in mbs_terms}
    entering = tuple(name for name in mbs_terms if counts[name] >= min_flagged)
    zero = {name: 0.0 for name in mbs_terms}
    if not entering:
        base = baseline or sc.fit_state_terms(
            pairs, regressors=regressors, terms=terms, interact=False, robust=True, training_pairs="direct", ridge=ridge)
        return MbsEstimate(base, zero, (), counts)
    active, flag_counts = sc._entering(terms, pairs, min_flagged)
    target = [p.raw / p.scale for p in pairs]
    design = [[1.0] + [float(p.flags[name]) for name in active] + [float(m[name]) for name in entering] for p, m in zip(pairs, mbs)]
    coefficients, iterations = sc.huber(design, target, ridge)
    effect = dict(zip(active, coefficients[1 : 1 + len(active)]))
    mine = dict(zip(entering, coefficients[1 + len(active) :]))
    pool = [
        y - sum(effect[name] * float(p.flags[name]) for name in effect) - sum(mine[name] * float(m[name]) for name in mine)
        for p, y, m in zip(pairs, target, mbs)
    ]
    flag_counts.update(counts)
    state = sc.StateEstimate(
        active, effect, {}, flag_counts, tuple(pb.empirical_quantiles(sorted(pool))), len(pairs), sum(1 for p in pairs if p.state is None),
        iterations, False, tuple(p.origin for p in pairs), tuple(p.target for p in pairs), tuple(pool), 0,
    )
    return MbsEstimate(state, {**zero, **mine}, entering, counts)


def effect_bp(estimate: MbsEstimate, flags: Mapping[str, int], scale: float) -> float:
    """The shift the indicators add to every quantile, in bp: the scale at the anchor times the sum of coefficient times indicator."""

    return scale * sum(estimate.coefficient[name] * flags[name] for name in estimate.coefficient)


def forecast_leads(
    estimates: Mapping[int, MbsEstimate],
    quantiles: Mapping[int, Sequence[float]],
    flags: Mapping[int, Mapping[str, int]],
    scales: Mapping[int, float],
) -> Dict[int, List[float]]:
    """Each lead's quantiles with the indicator effect added: `quantiles` are `sc.forecast`'s from the estimates' `state`, `flags` the leads' indicators,
    `scales` the scale at the anchor (the same at every lead; given by lead for the caller's convenience)."""

    return {h: [q + effect_bp(estimates[h], flags[h], scales[h]) for q in quantiles[h]] for h in quantiles}


# -- the walk ---------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class MbsWalk:
    #: Decision day -> lead -> 23 quantiles of (s3-mbs) (before the SRF cap), and (s3)'s own, from the same walk.
    forecasts: Dict[date, Dict[int, List[float]]]
    s3: Dict[date, Dict[int, List[float]]]
    #: Decision day -> lead -> the indicators read.
    values: Dict[date, Dict[int, Dict[str, int]]]
    #: Decision day -> the scale at the anchor.
    scale: Dict[date, float]
    #: Refit day -> lead -> the estimate.
    estimates: Dict[date, Dict[int, MbsEstimate]]
    #: Decision day -> the refit day whose estimates it used.
    fit_used: Dict[date, date]
    skipped: Tuple[date, ...]


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: cal.TermTable,
    mbs: MbsTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    training_pairs: str = "direct",
) -> Tuple[Dict[int, MbsEstimate], Dict[int, sc.StateEstimate]]:
    """The arm's estimate at each lead, and (s3)'s, as of the decision on row `decision_index`, on the base model's training pairs.

    Mirrors `spread_mr_state_calendar.refit` for (s3) (the same pairs, the same scale, the same terms) and reads the indicators at each pair's target row
    as the decision `lead` rows before it could.

    Raises:
        InsufficientHistory: the base fit's, or a lead with no pair that has a scale.
        LookAheadError: a row the scale reads is after the anchor.
        ValueError: the one-step guard (`fit_mbs_terms`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in HORIZONS for origin, _ in rows[h]} | {anchor})
    variant = sc.BASE_VARIANT
    read = {j for origin in origins if origin - variant.window >= 0 for j in fhs.scale_rows(origin, variant.window)}
    pb._require_public(read, anchor, dates, f"the scale of {variant.name} for {dates[decision_index]}")
    reader = fhs.ScaleReader(spreads, variant)
    mine: Dict[int, MbsEstimate] = {}
    s3: Dict[int, sc.StateEstimate] = {}
    for h in HORIZONS:
        k = h + lag
        pairs: List[sc.StatePair] = []
        indicators: List[Dict[str, int]] = []
        for origin, target in rows[h]:
            scale = reader.at(origin)
            if scale is None:
                continue
            raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
            flags_row = target if training_pairs == "direct" else origin
            pairs.append(sc.StatePair(raw, scale, table.flags_at(h, flags_row), None, {}, origin, target, {}, False))
            indicators.append(mbs.flags_at(h, flags_row))
        if not pairs:
            raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
        regressors = cal.regressors_of(ARM, h)
        s3[h] = sc.fit_state_terms(
            pairs, regressors=regressors, terms=ARM.location, interact=False, robust=True, training_pairs=training_pairs, ridge=ARM.ridge)
        mine[h] = fit_mbs_terms(
            pairs, indicators, regressors=regressors, terms=ARM.location, mbs_terms=mbs.terms, training_pairs=training_pairs, baseline=s3[h])
    return mine, s3


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: cal.TermTable,
    mbs: MbsTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    training_pairs: str = "direct",
) -> MbsWalk:
    """(s3) and (s3-mbs) on `decision_days`, refitting as `spread_mr_state_calendar.walk` does (a day with no forecast is skipped and does not count
    toward the next refit), so that (s3) here is that walk's (s3) forecast for forecast.

    The indicators of a forecast are read at the target row as of the decision.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    s3_out: Dict[date, Dict[int, List[float]]] = {}
    values: Dict[date, Dict[int, Dict[str, int]]] = {}
    scales: Dict[date, float] = {}
    estimates: Dict[date, Dict[int, MbsEstimate]] = {}
    fit_used: Dict[date, date] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    mine_now: Dict[int, MbsEstimate] = {}
    s3_now: Dict[int, sc.StateEstimate] = {}
    refit_day: Optional[date] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                fhs.fit(panel, index, [sc.BASE_VARIANT], base=base, **settings)  # the walk's own refit can skip the day: so does this
                mine_now, s3_now = refit(
                    panel, index, table, mbs, registry=registry, decision_time=decision_time, levels=levels, base=base, training_pairs=training_pairs)
                current, refit_day = base, day
                estimates[day] = mine_now
                since = 0
            read = {h: mbs.read(h, index) for h in HORIZONS}
            fcfg = dict(registry=registry, decision_time=decision_time, levels=levels, base=current)
            theirs, _ = sc.forecast(panel, index, {ARM.name: s3_now}, table, {}, (ARM,), **fcfg)
            ours, detail = sc.forecast(panel, index, {ARM.name: {h: e.state for h, e in mine_now.items()}}, table, {}, (ARM,), **fcfg)
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
        fit_used[day] = refit_day
        since += 1
        s3_out[day] = theirs[ARM.name]
        forecasts[day] = forecast_leads(mine_now, ours[ARM.name], read, {h: detail["scale"] for h in HORIZONS})
        values[day] = read
        scales[day] = detail["scale"]
    return MbsWalk(forecasts, s3_out, values, scales, estimates, fit_used, tuple(skipped))
