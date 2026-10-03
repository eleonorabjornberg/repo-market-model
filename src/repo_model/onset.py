"""Onset scoring (#139): day groups, small-leap targets, and their baselines.

The pressure probability's value is at onset and in the tail, and a mean over
some 1,900 scored days hides both. This module adds, to every pressure and
distribution comparison, a view of the days that matter:

- **Three day groups.** All scored days; scheduled-pressure days (a quarter
  end, a month end or a tax date, as `metadata/evaluation_splits.json`
  declares the types, or a Treasury coupon settlement); and the onset group:
  every day after at least five business days at or below +5 bp, whatever
  happened that day (`ONSET_THRESHOLD_BP`, `ONSET_CALM_DAYS`). Its events are
  the onsets, the days in it above +5 bp (Eleonora's ruling of 3 October
  2026, #209: a group of onsets alone has every outcome 1). For each onset,
  each model's probabilities on the scored days before it are listed too.
  Beside it, descriptive only, #160's one-day variant: every day whose
  previous panel day was at or below +5 bp.
- **Small-leap targets, defined as-of.** The jump of a forecast of day `t` is
  `s_t - s_a(t)`, where `a(t)` is that forecast's as-of anchor
  (`asof.InformationRule.anchor`) -- never the day before `t`, which is not
  yet public when the forecast is made. A leap is a jump strictly above
  `LEAP_JUMP_BP[h]`. A leap onset is a leap with no leap on the five panel
  days before it; the leap-onset group is every day with no leap on the five
  panel days before it, and the leap onsets are its events. A pressure leap is a leap that also ends above IORB.
- **The leap baselines**: a calendar climatology of the leap and a
  persistence-logistic of the leap on the latest as-of jump and spread, both
  refitted walk-forward on the scored model's own refit blocks.
- **Paired evidence**: the stationary bootstrap, as everywhere, and a
  Diebold-Mariano test with a Newey-West variance on the all-days group only.

Every spread compared with a threshold here goes through `data.exceeds_bp`:
whole basis points, strictly greater, so a day that sits on +5 bp is not above
it (#155). A jump is the difference of two whole-bp spreads (`whole_bp`).

Nothing here reads a day the forecast could not have seen: a jump's anchor is
checked against the forecast's decision instant (`as_of_jump`, which raises
`LookAheadError`), and each baseline is fitted only on labels observable at
its block's decision.
"""

from __future__ import annotations

import math
from datetime import date
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .asof import InformationRule
from .data import DailyObservation, exceeds_bp
from .metrics import stationary_bootstrap_interval
from .splits import LookAheadError, SplitError

#: Onset days: the first scored day with SOFR - IORB above this, in whole bp.
ONSET_THRESHOLD_BP = 5
#: ...after at least this many consecutive panel (business) days at or below it.
ONSET_CALM_DAYS = 5
#: How many scored days before an onset its lead-time path lists.
ONSET_LEAD_DAYS = 5

#: The leap threshold `J_h` per horizon `h` (panel days ahead), in bp. The
#: 90th percentile (`LEAP_PERCENTILE`, linear interpolation, numpy's default)
#: of the signed as-of jumps on every scored day of the published fold grid in
#: `LEAP_WINDOW`, days with no admissible anchor excluded, to 2 decimals.
#: Fixed: never recomputed from later data.
#: `tests/test_onset.py::LeapThresholdTests` recomputes it from the tracked panel.
LEAP_JUMP_BP: Mapping[int, float] = MappingProxyType(
    {1: 3.00, 2: 4.00, 3: 4.00, 4: 4.00, 5: 4.00}
)
LEAP_PERCENTILE = 0.90
LEAP_WINDOW = (date(2018, 6, 29), date(2025, 12, 31))
#: A leap onset has no leap on this many panel days before it.
LEAP_ONSET_CALM_DAYS = 5

#: The threshold weight 1{y > +5 bp} (Gneiting & Ranjan 2011) of the
#: threshold-weighted CRPS reported beside the plain CRPS.
TWCRPS_FLOOR_BP = 5.0

#: Below this many events in the all-days group, a leap verdict is
#: "inconclusive": neither a pass nor a fail. **Proposed in the #139 draft for
#: Eleonora's decision**; not a rule until she decides it.
MINIMUM_EVENTS = 20

GROUP_ALL = "all_days"
GROUP_SCHEDULED = "scheduled_pressure_days"
#: Every scored day after `ONSET_CALM_DAYS` calm panel days; the onsets are its events (#209).
GROUP_ONSET = "onset_days"
#: Descriptive only: every scored day whose previous panel day was calm (#160).
GROUP_ONSET_ONE_DAY = "onset_days_one_day"
#: Every scored day with no leap on `LEAP_ONSET_CALM_DAYS` panel days before it.
GROUP_LEAP_ONSET = "leap_onset_days"

ONSET_GROUP_NOTE = (
    "descriptive, not a test: every day after a calm stretch, whatever its outcome, "
    "with the onsets as its events (counted in 'events', the days in 'days'); the "
    "group is mostly calm days, so its score mostly measures false alarms"
)
ONSET_ONE_DAY_NOTE = (
    "descriptive only, decides nothing: #160's definition, every day whose previous "
    "panel day was at or below +5 bp"
)

#: The two named leap baselines, as a record names them. Not the pressure
#: benchmarks' names: these are fitted to the leap, not to a threshold.
LEAP_CALENDAR_CLIMATOLOGY = "leap_calendar_climatology"
LEAP_PERSISTENCE_LOGISTIC = "leap_persistence_logistic"

#: The coupon-settlement column that makes a day a scheduled-pressure day.
COUPON_SETTLEMENT_COLUMN = "treasury_settlement_coupons"

LEVEL = 0.90
REPLICATIONS = 2000


def whole_bp(value: float) -> int:
    """A spread in whole basis points: both rates are quoted to the basis point."""

    return int(round(float(value)))


# --------------------------------------------------------------------------
# Day groups
# --------------------------------------------------------------------------


def _calm_before(flags: Sequence[bool], days: int) -> List[bool]:
    """Per row: are there `days` rows before it, none of them flagged?"""

    return [
        index >= days and not any(flags[index - back] for back in range(1, days + 1))
        for index in range(len(flags))
    ]


def _above(rows: Sequence[DailyObservation]) -> List[bool]:
    return [exceeds_bp(row.spread_bps, ONSET_THRESHOLD_BP) for row in rows]


def at_risk_flags(rows: Sequence[DailyObservation]) -> List[bool]:
    """Per panel row: is it in the onset group, whatever its own outcome (#209)?

    `ONSET_CALM_DAYS` panel days before it, all at or below
    `ONSET_THRESHOLD_BP`. A row with fewer panel days before it is not.
    """

    return _calm_before(_above(rows), ONSET_CALM_DAYS)


def one_day_at_risk_flags(rows: Sequence[DailyObservation]) -> List[bool]:
    """Per panel row: was the previous panel day at or below `ONSET_THRESHOLD_BP` (#160)?"""

    return _calm_before(_above(rows), 1)


def onset_flags(rows: Sequence[DailyObservation]) -> List[bool]:
    """Per panel row: is it an onset day, an event of the onset group?

    Above `ONSET_THRESHOLD_BP`, after `ONSET_CALM_DAYS` panel days at or below
    it. A row with fewer panel days before it than that is never an onset.
    """

    return [risk and today for risk, today in zip(at_risk_flags(rows), _above(rows))]


def _scored_indices(
    rows: Sequence[DailyObservation], scored_dates: Sequence[date]
) -> List[int]:
    position_of = {row.date: index for index, row in enumerate(rows)}
    indices: List[int] = []
    for when in scored_dates:
        if when not in position_of:
            raise ValueError(f"scored day {when} is not a row of the panel")
        indices.append(position_of[when])
    return indices


def onset_positions(
    rows: Sequence[DailyObservation], scored_dates: Sequence[date]
) -> List[int]:
    """Positions into `scored_dates` of the onsets: the lead-time listing's days."""

    onsets = onset_flags(rows)
    return [k for k, index in enumerate(_scored_indices(rows, scored_dates)) if onsets[index]]


def scheduled_pressure(row: DailyObservation, declaration: Any) -> bool:
    """A quarter end, month end or tax date as declared, or a coupon settlement."""

    if declaration.day_type(row.values) != "ordinary":
        return True
    coupons = row.values.get(COUPON_SETTLEMENT_COLUMN)
    return coupons is not None and float(coupons) > 0.0


def day_groups(
    rows: Sequence[DailyObservation],
    scored_dates: Sequence[date],
    declaration: Optional[Any],
) -> Dict[str, Any]:
    """Positions into `scored_dates` for each group, or the reason one is absent."""

    indices = _scored_indices(rows, scored_dates)
    at_risk = at_risk_flags(rows)
    one_day = one_day_at_risk_flags(rows)
    groups: Dict[str, Any] = {
        GROUP_ALL: list(range(len(indices))),
        GROUP_ONSET: [k for k, index in enumerate(indices) if at_risk[index]],
        GROUP_ONSET_ONE_DAY: [k for k, index in enumerate(indices) if one_day[index]],
    }
    if declaration is None:
        groups[GROUP_SCHEDULED] = (
            "no split declaration (--splits) was given, and the scheduled-pressure "
            "day types are the declaration's"
        )
    else:
        groups[GROUP_SCHEDULED] = [
            k for k, index in enumerate(indices) if scheduled_pressure(rows[index], declaration)
        ]
    return groups


# --------------------------------------------------------------------------
# The as-of jump, and the leap targets
# --------------------------------------------------------------------------


def as_of_jump(
    rows: Sequence[DailyObservation],
    rule: InformationRule,
    index: int,
    dates: Optional[Sequence[date]] = None,
) -> Optional[Tuple[int, int]]:
    """The jump of a forecast of `rows[index]`, against that forecast's anchor.

    `(jump, anchor)`, with `jump = s_t - s_a(t)` in whole bp and `a(t)` the
    latest row whose spread is public at the forecast's decision instant
    (`rule.anchor`). `None` when there is no decision instant or no admissible
    anchor: such a day has no jump and is excluded.

    Raises:
        LookAheadError: if the anchor is not before the scored row, or its
            spread is not public by the forecast's decision instant. The jump
            would then read a row the forecast could not have seen.
    """

    dates = [row.date for row in rows] if dates is None else dates
    if index < rule.horizon:
        return None
    anchor = rule.anchor(dates, index)
    if anchor < 0:
        return None
    _require_public(rule, dates, index, anchor)
    return whole_bp(rows[index].spread_bps) - whole_bp(rows[anchor].spread_bps), anchor


def _require_public(
    rule: InformationRule, dates: Sequence[date], index: int, anchor: int
) -> None:
    """The jump's anchor is before the scored row and public at its decision."""

    deadline = rule.decision_instant(dates, index)
    if anchor >= index:
        raise LookAheadError(
            f"the jump for {dates[index]} is anchored at row {anchor}, which is not "
            f"before the scored row"
        )
    available = rule.availability(dates, rule._target_fields(), anchor)
    if available > deadline:
        raise LookAheadError(
            f"the jump for {dates[index]} reads the spread of {dates[anchor]}, first "
            f"public at {available}, after the {deadline} decision"
        )


def percentile(values: Sequence[float], q: float) -> float:
    """The `q` quantile with linear interpolation (Hyndman-Fan type 7, numpy's default)."""

    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("a percentile of no values")
    if not 0.0 <= q <= 1.0:
        raise ValueError(f"q must be in [0, 1], got {q}")
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def leap_threshold(
    rows: Sequence[DailyObservation],
    rule: InformationRule,
    scored_indices: Sequence[int],
    *,
    window: Tuple[date, date] = LEAP_WINDOW,
) -> float:
    """`J_h` by the rule of #139: recomputed by the test, never by a run.

    The `LEAP_PERCENTILE` quantile of the signed jumps at `rule.horizon` over
    the scored rows in `window`, inclusive, excluding rows with no anchor;
    rounded to 2 decimals.
    """

    dates = [row.date for row in rows]
    jumps = []
    for index in scored_indices:
        if not window[0] <= dates[index] <= window[1]:
            continue
        read = as_of_jump(rows, rule, index, dates)
        if read is not None:
            jumps.append(read[0])
    return round(percentile(jumps, LEAP_PERCENTILE), 2)


class LeapTargets:
    """The leap targets over a whole panel at one horizon, read once.

    `jump[i]`, `anchor[i]`, `leap[i]`, `leap_onset[i]`, `leap_at_risk[i]` and
    `pressure_leap[i]` per panel row; `jump[i]` is `None` for a row with no
    admissible anchor, and such a row is never a leap. `leap_at_risk[i]`: no
    leap on the `LEAP_ONSET_CALM_DAYS` panel days before row `i`, whatever row
    `i` was; the leap onsets are the leaps among those rows (#209).
    """

    def __init__(
        self,
        rows: Sequence[DailyObservation],
        rule: InformationRule,
        threshold_bp: float,
    ) -> None:
        self.rows = rows
        self.rule = rule
        self.threshold_bp = float(threshold_bp)
        dates = [row.date for row in rows]
        self.dates = dates
        self.jump: List[Optional[int]] = []
        self.anchor: List[int] = []
        for index in range(len(rows)):
            read = as_of_jump(rows, rule, index, dates)
            self.jump.append(None if read is None else read[0])
            self.anchor.append(-1 if read is None else read[1])
        self.leap = [jump is not None and jump > self.threshold_bp for jump in self.jump]
        self.leap_at_risk = _calm_before(self.leap, LEAP_ONSET_CALM_DAYS)
        self.leap_onset = [
            leap and risk for leap, risk in zip(self.leap, self.leap_at_risk)
        ]
        self.pressure_leap = [
            self.leap[index] and exceeds_bp(rows[index].spread_bps, 0.0)
            for index in range(len(rows))
        ]

    def event_threshold(self, index: int, *, pressure: bool) -> float:
        """The spread above which `rows[index]` is the event, for a curve to be read at.

        The leap is `round(s_t) > s_a + J`; with `round(s_t)` whole, that is
        `round(s_t) >= floor(s_a + J) + 1`, so `s_t > floor(s_a + J) + 0.5`.
        The pressure leap also needs `round(s_t) > 0`.
        """

        anchor = self.anchor[index]
        if anchor < 0:
            raise SplitError(f"{self.dates[index]} has no as-of anchor, so no leap")
        level = whole_bp(self.rows[anchor].spread_bps) + self.threshold_bp
        if pressure:
            level = max(level, 0.0)
        return math.floor(level) + 0.5

    def labels(self, target: str) -> List[bool]:
        return {"leap": self.leap, "pressure_leap": self.pressure_leap}[target]


def leap_onset_group(targets: LeapTargets, scored_dates: Sequence[date]) -> List[int]:
    """Positions into `scored_dates` of the leap-onset group (`LeapTargets.leap_at_risk`)."""

    position_of = {when: index for index, when in enumerate(targets.dates)}
    return [k for k, when in enumerate(scored_dates) if targets.leap_at_risk[position_of[when]]]


# --------------------------------------------------------------------------
# The two named leap baselines, walk-forward
# --------------------------------------------------------------------------


def _blocks(
    position_of: Mapping[date, int],
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
) -> List[Tuple[int, List[int]]]:
    """`(last training row, [scored positions])` per refit block, in order."""

    blocks: List[Tuple[int, List[int]]] = []
    for k, (when, end) in enumerate(zip(scored_dates, train_ends)):
        last = position_of[end]
        if position_of[when] <= last:
            raise LookAheadError(
                f"the fold scoring {when} trains through {end}, which is not before it"
            )
        if blocks and blocks[-1][0] == last:
            blocks[-1][1].append(k)
        else:
            blocks.append((last, [k]))
    return blocks


def leap_calendar_climatology(
    targets: LeapTargets,
    target: str,
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
    declaration: Any,
) -> List[float]:
    """The pre-`t` leap frequency among training days of `t`'s day type.

    Refitted on each refit block, on the rows whose leap label is observable
    at its decision (through the block's last training row). A day type with
    no training day yet takes the pooled frequency.
    """

    labels = targets.labels(target)
    rows = targets.rows
    position_of = {when: index for index, when in enumerate(targets.dates)}
    kinds = [declaration.day_type(row.values) for row in rows]
    out: List[float] = [0.0] * len(scored_dates)
    for last, members in _blocks(position_of, scored_dates, train_ends):
        counts: Dict[str, List[int]] = {}
        pooled = [0, 0]
        for index in range(last + 1):
            if targets.jump[index] is None:
                continue
            hit = 1 if labels[index] else 0
            entry = counts.setdefault(kinds[index], [0, 0])
            entry[0] += hit
            entry[1] += 1
            pooled[0] += hit
            pooled[1] += 1
        if not pooled[1]:
            raise SplitError("no training day has a leap label")
        for k in members:
            entry = counts.get(kinds[position_of[scored_dates[k]]]) or pooled
            out[k] = entry[0] / entry[1]
    return out


def _logistic2(
    xs: Sequence[Tuple[float, float]], ys: Sequence[int]
) -> Tuple[float, float, float]:
    """A two-variable logistic with `baseline._logistic_fit`'s objective.

    Log loss plus half the squared slopes (scikit-learn's default, `C=1`, the
    intercept unpenalised), by Newton's method with step halving.
    """

    def objective(beta) -> float:
        total = 0.5 * (beta[1] ** 2 + beta[2] ** 2)
        for (x1, x2), y in zip(xs, ys):
            z = beta[0] + beta[1] * x1 + beta[2] * x2
            total += (z if z > 0 else 0.0) + math.log1p(math.exp(-abs(z))) - y * z
        return total

    beta = [0.0, 0.0, 0.0]
    current = objective(beta)
    for _ in range(200):
        g = [0.0, 0.0, 0.0]
        h = [[0.0] * 3 for _ in range(3)]
        for (x1, x2), y in zip(xs, ys):
            p = _sigmoid(beta[0] + beta[1] * x1 + beta[2] * x2)
            w = p * (1.0 - p)
            v = (1.0, x1, x2)
            for i in range(3):
                g[i] += (p - y) * v[i]
                for j in range(3):
                    h[i][j] += w * v[i] * v[j]
        g[1] += beta[1]
        g[2] += beta[2]
        h[1][1] += 1.0
        h[2][2] += 1.0
        try:
            step_direction = _solve3(h, g)
        except ZeroDivisionError:
            break
        step = 1.0
        while step > 1e-10:
            trial_beta = [b - step * d for b, d in zip(beta, step_direction)]
            trial = objective(trial_beta)
            if trial <= current:
                break
            step /= 2.0
        else:
            break
        beta, current = trial_beta, trial
        if max(abs(step * d) for d in step_direction) < 1e-12:
            break
    return beta[0], beta[1], beta[2]


def _solve3(a: List[List[float]], b: List[float]) -> List[float]:
    """`a x = b` for a 3x3 system, by Gaussian elimination with pivoting."""

    m = [row[:] + [value] for row, value in zip(a, b)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-300:
            raise ZeroDivisionError("singular Hessian")
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(col + 1, 3):
            factor = m[r][col] / m[col][col]
            for c in range(col, 4):
                m[r][c] -= factor * m[col][c]
    x = [0.0, 0.0, 0.0]
    for r in (2, 1, 0):
        x[r] = (m[r][3] - sum(m[r][c] * x[c] for c in range(r + 1, 3))) / m[r][r]
    return x


def _sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    return math.exp(z) / (1.0 + math.exp(z))


def _as_of_regressors(targets: LeapTargets, index: int) -> Optional[Tuple[float, float]]:
    """The latest as-of jump and spread at `rows[index]`'s decision: its anchor's."""

    anchor = targets.anchor[index]
    if anchor < 0 or targets.jump[anchor] is None:
        return None
    return float(targets.jump[anchor]), float(whole_bp(targets.rows[anchor].spread_bps))


def leap_persistence_logistic(
    targets: LeapTargets,
    target: str,
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
) -> List[float]:
    """A logistic of the leap on the latest as-of jump and the latest as-of spread.

    Refitted on each refit block. A training day `i` pairs its leap label with
    the regressors public at its own decision (its anchor's jump and spread),
    for every `i` through the block's last training row; the scored day is
    read at its own anchor. Labels all one value give that value.
    """

    labels = targets.labels(target)
    position_of = {when: index for index, when in enumerate(targets.dates)}
    out: List[float] = [0.0] * len(scored_dates)
    for last, members in _blocks(position_of, scored_dates, train_ends):
        xs: List[Tuple[float, float]] = []
        ys: List[int] = []
        for index in range(last + 1):
            if targets.jump[index] is None:
                continue
            regressors = _as_of_regressors(targets, index)
            if regressors is None:
                continue
            xs.append(regressors)
            ys.append(1 if labels[index] else 0)
        if not ys:
            raise SplitError("no training day has a leap label and its regressors")
        constant = None if len(set(ys)) > 1 else float(ys[0])
        beta = None if constant is not None else _logistic2(xs, ys)
        for k in members:
            index = position_of[scored_dates[k]]
            regressors = _as_of_regressors(targets, index)
            if constant is not None:
                out[k] = constant
            elif regressors is None:
                out[k] = sum(ys) / len(ys)
            else:
                out[k] = _sigmoid(beta[0] + beta[1] * regressors[0] + beta[2] * regressors[1])
    return out


# --------------------------------------------------------------------------
# Paired evidence
# --------------------------------------------------------------------------


def diebold_mariano(differences: Sequence[float]) -> dict:
    """The Diebold-Mariano test of a zero mean loss difference, HAC variance.

    Newey-West (Bartlett) long-run variance with the automatic lag
    `floor(4 (n / 100) ** (2 / 9))`; the statistic is compared with the
    standard normal, two-sided.
    """

    n = len(differences)
    if n < 2:
        return {"unavailable": f"{n} paired days; the test needs at least 2"}
    mean = sum(differences) / n
    centred = [value - mean for value in differences]
    lag = int(math.floor(4.0 * (n / 100.0) ** (2.0 / 9.0)))
    lag = min(lag, n - 1)
    variance = sum(value * value for value in centred) / n
    for k in range(1, lag + 1):
        weight = 1.0 - k / (lag + 1.0)
        variance += 2.0 * weight * sum(
            centred[t] * centred[t - k] for t in range(k, n)
        ) / n
    if variance <= 1e-20 * max(1.0, mean * mean):
        return {"unavailable": "the loss differences have no variance", "lag": lag}
    statistic = mean / math.sqrt(variance / n)
    return {
        "statistic": statistic,
        "p_value": math.erfc(abs(statistic) / math.sqrt(2.0)),
        "variance": "newey_west",
        "lag": lag,
        "alternative": "two-sided",
    }


def paired_difference(
    benchmark_losses: Sequence[float],
    model_losses: Sequence[float],
    positions: Sequence[int],
    *,
    block_length: int,
    seed: int,
) -> dict:
    """Mean of benchmark minus model over `positions`, with its 90% interval."""

    differences = [benchmark_losses[k] - model_losses[k] for k in positions]
    if not differences:
        return {"days": 0}

    def mean_of(indices: Sequence[int]) -> float:
        return sum(differences[i] for i in indices) / len(indices)

    lower, upper = stationary_bootstrap_interval(
        mean_of,
        len(differences),
        block_length=block_length,
        seed=seed,
        replications=REPLICATIONS,
        level=LEVEL,
    )
    return {
        "days": len(differences),
        "mean": sum(differences) / len(differences),
        "interval": {
            "lower": lower,
            "upper": upper,
            "level": LEVEL,
            "method": "stationary_bootstrap",
            "block_length": block_length,
            "replications": REPLICATIONS,
            "seed": seed,
        },
    }


def _seed(*parts: Any) -> int:
    from .baseline import _seed_from

    return _seed_from(tuple(str(part) for part in parts))


def _brier_losses(probabilities: Sequence[float], outcomes: Sequence[int]) -> List[float]:
    return [(p - o) ** 2 for p, o in zip(probabilities, outcomes)]


def _mean(values: Sequence[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def _group_block(
    model: str,
    columns: Mapping[str, Sequence[float]],
    outcomes: Sequence[int],
    groups: Mapping[str, Any],
    *,
    block_length: int,
    seed_parts: Tuple[Any, ...],
    test_all_days: bool = True,
) -> dict:
    """Brier per model per group, and each other model paired against `model`."""

    losses = {name: _brier_losses(column, outcomes) for name, column in columns.items()}
    out: dict = {}
    for group, positions in groups.items():
        if isinstance(positions, str):
            out[group] = {"unavailable": positions}
            continue
        entry: dict = {
            "days": len(positions),
            "events": sum(outcomes[k] for k in positions),
            "brier": {
                name: _mean([values[k] for k in positions]) for name, values in losses.items()
            },
            "paired": {},
        }
        for name in columns:
            if name == model:
                continue
            paired = paired_difference(
                losses[name],
                losses[model],
                positions,
                block_length=block_length,
                seed=_seed(*seed_parts, group, name),
            )
            if group == GROUP_ALL and test_all_days and positions:
                paired["diebold_mariano"] = diebold_mariano(
                    [losses[name][k] - losses[model][k] for k in positions]
                )
            entry["paired"][name] = paired
        if group in (GROUP_ONSET, GROUP_LEAP_ONSET):
            entry["note"] = ONSET_GROUP_NOTE
        elif group == GROUP_ONSET_ONE_DAY:
            entry["note"] = ONSET_ONE_DAY_NOTE
        out[group] = entry
    return out


def _sign_convention(model: str) -> str:
    return (
        f"paired = brier(benchmark) - brier({model}) on each day; a positive mean "
        f"means {model} had the lower Brier score"
    )


# --------------------------------------------------------------------------
# The exceedance record's onset section
# --------------------------------------------------------------------------


def _lead_paths(
    columns: Mapping[str, Sequence[float]],
    scored_dates: Sequence[date],
    realized_bps: Sequence[float],
    onset_positions: Sequence[int],
) -> List[dict]:
    paths = []
    for k in onset_positions:
        start = max(0, k - ONSET_LEAD_DAYS)
        paths.append(
            {
                "date": scored_dates[k].isoformat(),
                "realized_bps": realized_bps[k],
                "forecasts": [
                    {
                        "scored_date": scored_dates[step].isoformat(),
                        "days_before": k - step,
                        "probability": {
                            name: column[step] for name, column in sorted(columns.items())
                        },
                    }
                    for step in range(start, k + 1)
                ],
            }
        )
    return paths


def exceedance_onset_document(
    report: Any,
    benchmarks: Sequence[Any],
    rows: Sequence[DailyObservation],
    declaration: Optional[Any],
    *,
    panel_sha256: str,
    leap_rule: Optional[InformationRule] = None,
) -> dict:
    """The `onset` section of an exceedance record (#139).

    Per headline threshold, Brier by day group for the scored model, the
    climatology reference and every benchmark, each benchmark paired against
    the model (benchmark minus model, 90% stationary-bootstrap interval;
    Diebold-Mariano on all days), with each onset's lead-time path. The leap
    targets with their two baselines, when the report carries the model's leap
    forecasts. The threshold-weighted CRPS with weight 1{y > +5 bp} beside the
    plain CRPS on the declared grid.
    """

    from .baseline import _maximum_horizon_overlap, _exceedance_seed
    from .metrics import crps_on_grid, threshold_weighted_crps

    for bench in benchmarks:
        if tuple(bench.scored_dates) != tuple(report.scored_dates):
            raise SplitError(
                f"the benchmark {bench.model_name!r} was not scored on the model's grid"
            )
    groups = day_groups(rows, report.scored_dates, declaration)
    onsets = onset_positions(rows, report.scored_dates)
    block = _maximum_horizon_overlap(report.folds)
    base_seed = _exceedance_seed(report, panel_sha256)
    document: dict = {
        "definitions": {
            "labels": "the report's own: whole basis points, strictly greater (#155)",
            "onset_day": (
                f"the first day with SOFR - IORB > +{ONSET_THRESHOLD_BP} bp after at "
                f"least {ONSET_CALM_DAYS} consecutive panel days at or below it"
            ),
            "onset_group": (
                f"every scored day after at least {ONSET_CALM_DAYS} consecutive panel days "
                f"at or below +{ONSET_THRESHOLD_BP} bp, whatever its outcome; its events "
                f"are the onset days (#209)"
            ),
            "onset_group_one_day": (
                f"descriptive only: every scored day whose previous panel day was at or "
                f"below +{ONSET_THRESHOLD_BP} bp (#160)"
            ),
            "scheduled_pressure_day": (
                "a quarter end, month end or tax date as the split declaration types "
                f"them, or a day with a Treasury coupon settlement ({COUPON_SETTLEMENT_COLUMN} > 0)"
            ),
            "lead_days": ONSET_LEAD_DAYS,
        },
        "sign_convention": _sign_convention(report.model_name),
        "by_tau": {},
    }
    headline = [tau for tau in report.taus if tau in (5.0, 10.0)]
    for tau in headline:
        position = report.taus.index(tau)
        # The report's own outcomes, on whole basis points (`exceeds_bp`, #155).
        predicted, reference, outcomes = report.at_tau(position)
        columns: Dict[str, Sequence[float]] = {
            report.model_name: predicted,
            "reference_climatology": reference,
        }
        for bench in benchmarks:
            if bench.model_name in columns:
                raise SplitError(f"two models named {bench.model_name!r}")
            columns[bench.model_name] = bench.at_tau(position)[0]
        entry = _group_block(
            report.model_name,
            columns,
            outcomes,
            groups,
            block_length=block,
            seed_parts=(base_seed, "onset", f"{tau:g}"),
        )
        entry["lead_time"] = _lead_paths(
            columns, report.scored_dates, report.realized_bps, onsets
        )
        document["by_tau"][f"{tau:g}"] = entry

    # twCRPS with weight 1{y > +5 bp}, beside the plain CRPS, on the declared grid.
    weights = [1.0 if tau >= TWCRPS_FLOOR_BP else 0.0 for tau in report.taus]
    try:
        plain = [
            crps_on_grid(report.taus, curve, value)
            for curve, value in zip(report.forecast, report.realized_bps)
        ]
        weighted = [
            threshold_weighted_crps(report.taus, curve, value, weights)
            for curve, value in zip(report.forecast, report.realized_bps)
        ]
        document["crps"] = {
            "crps_on_grid": sum(plain) / len(plain),
            "twcrps_above_5bp": sum(weighted) / len(weighted),
            "weight": "1{z > +5 bp} over the declared grid",
            "note": (
                "the declared grid starts at +5 bp, so on this path the weighted "
                "and plain integrals cover the same range and agree"
            ),
        }
    except Exception as exc:  # MetricError: a one-tau family has no integral
        document["crps"] = {"unavailable": str(exc)}

    if getattr(report, "leap_forecast", None) is not None and leap_rule is not None:
        document["leap"] = leap_document(
            report, rows, declaration, leap_rule, block=block, base_seed=base_seed
        )
    else:
        document["leap"] = {
            "unavailable": "the run did not score the model's leap probability"
        }
    return document


def leap_document(
    report: Any,
    rows: Sequence[DailyObservation],
    declaration: Optional[Any],
    rule: InformationRule,
    *,
    block: int,
    base_seed: int,
) -> dict:
    """The leap and pressure-leap targets, against their two named baselines."""

    if declaration is None:
        return {
            "unavailable": (
                "the calendar-climatology baseline needs the split declaration "
                "(--splits) that types the days"
            )
        }
    threshold = report.leap_threshold_bp
    targets = LeapTargets(rows, rule, threshold)
    position_of = {when: index for index, when in enumerate(targets.dates)}
    scored = [position_of[when] for when in report.scored_dates]
    train_ends = [fold.train_end for fold in report.folds]
    groups = day_groups(rows, report.scored_dates, declaration)
    at_risk = leap_onset_group(targets, report.scored_dates)
    document: dict = {
        "definitions": {
            "jump": (
                "s_t - s_a(t) in whole bp, where a(t) is the forecast's as-of anchor: "
                "the latest spread public at its decision instant"
            ),
            "leap": f"jump > J_h = {threshold:.2f} bp (horizon {rule.horizon}), strictly",
            "leap_onset": (
                f"a leap with no leap on any of the {LEAP_ONSET_CALM_DAYS} panel days "
                f"before it"
            ),
            "leap_onset_group": (
                f"every scored day with no leap on any of the {LEAP_ONSET_CALM_DAYS} panel "
                f"days before it, whatever its outcome; its events are the leap onsets (#209)"
            ),
            "pressure_leap": "a leap that also ends above IORB (s_t > 0 bp)",
            "claim_wording": (
                "the model forecasts as-of jumps in SOFR - IORB better than the named "
                "baselines; a leap is not a stress warning"
            ),
            "minimum_events": MINIMUM_EVENTS,
        },
        "threshold_bp": threshold,
        "horizon": rule.horizon,
        "sign_convention": _sign_convention(report.model_name),
        "targets": {},
    }
    for target, forecast in (
        ("leap", report.leap_forecast),
        ("pressure_leap", report.pressure_leap_forecast),
    ):
        labels = targets.labels(target)
        outcomes = [1 if labels[index] else 0 for index in scored]
        if any(targets.jump[index] is None for index in scored):
            raise SplitError("a scored day has no as-of anchor, so no leap label")
        columns = {
            report.model_name: list(forecast),
            LEAP_CALENDAR_CLIMATOLOGY: leap_calendar_climatology(
                targets, target, report.scored_dates, train_ends, declaration
            ),
            LEAP_PERSISTENCE_LOGISTIC: leap_persistence_logistic(
                targets, target, report.scored_dates, train_ends
            ),
        }
        if len(columns) != 3:
            raise SplitError("the scored model may not be named like a leap baseline")
        target_groups = {
            GROUP_ALL: groups[GROUP_ALL],
            GROUP_SCHEDULED: groups[GROUP_SCHEDULED],
            GROUP_LEAP_ONSET: at_risk,
        }
        entry = _group_block(
            report.model_name,
            columns,
            outcomes,
            target_groups,
            block_length=block,
            seed_parts=(base_seed, target),
        )
        entry["verdict"] = leap_verdict(entry[GROUP_ALL])
        document["targets"][target] = entry
    return document


def leap_verdict(all_days: Mapping[str, Any]) -> dict:
    """Beats both baselines, one of them, or neither; inconclusive below the minimum.

    A baseline is beaten when its paired 90% interval (baseline minus model)
    lies wholly above zero.
    """

    events = int(all_days["events"])
    if events < MINIMUM_EVENTS:
        return {
            "result": "inconclusive",
            "reason": f"{events} events, below the minimum of {MINIMUM_EVENTS}",
        }
    beaten = sorted(
        name
        for name, paired in all_days["paired"].items()
        if paired.get("interval", {}).get("lower", 0.0) > 0.0
    )
    if len(beaten) == len(all_days["paired"]):
        result = "beats both baselines"
    elif beaten:
        result = "beats only " + ", ".join(beaten)
    else:
        result = "beats neither baseline"
    return {"result": result, "beaten": beaten}


# --------------------------------------------------------------------------
# The distribution comparison's onset section
# --------------------------------------------------------------------------


def twcrps_above_from_quantiles(
    levels: Sequence[float], predicted: Sequence[float], observed: float
) -> float:
    """twCRPS with weight 1{z > +5 bp}, from a quantile vector.

    The chaining identity of the threshold-weighted CRPS (Gneiting & Ranjan
    2011; Allen et al. 2023): with weight 1{z > r}, twCRPS(F, y) is the CRPS
    of `max(X, r)` at `max(y, r)`, and the quantiles of `max(X, r)` are
    `max(q, r)`. So it is `metrics.crps_from_quantiles`, the plain CRPS's own
    approximation, on the floored vector.
    """

    from .metrics import crps_from_quantiles

    floor = TWCRPS_FLOOR_BP
    return crps_from_quantiles(
        levels, [max(float(q), floor) for q in predicted], max(float(observed), floor)
    )


def comparison_onset_document(
    comparison: Any,
    rows: Sequence[DailyObservation],
    declaration: Optional[Any],
) -> dict:
    """The `onset` section of a distribution comparison record (#139).

    The paired loss (model a minus model b, as the record's own sign
    convention) by day group, with 90% intervals; the twCRPS with weight
    1{y > +5 bp} beside it when the loss is the CRPS; Diebold-Mariano on all
    days.
    """

    scored = [fold.scored_date for fold in comparison.folds]
    groups = day_groups(rows, scored, declaration)
    series = {"loss": (comparison.losses_a, comparison.losses_b)}
    if getattr(comparison, "twcrps_a", None) is not None:
        series["twcrps_above_5bp"] = (comparison.twcrps_a, comparison.twcrps_b)
    document: dict = {
        "sign_convention": (
            f"difference = loss({comparison.model_a}) - loss({comparison.model_b}) on "
            f"each origin, as the record's own convention"
        ),
        "loss": comparison.loss_name,
        "twcrps_weight": "1{z > +5 bp}",
        "by_series": {},
    }
    for name, (losses_a, losses_b) in series.items():
        entry: dict = {}
        for group, positions in groups.items():
            if isinstance(positions, str):
                entry[group] = {"unavailable": positions}
                continue
            # `paired_difference` takes benchmark minus model; here a minus b.
            paired = paired_difference(
                losses_a,
                losses_b,
                positions,
                block_length=comparison.block_length,
                seed=_seed(comparison.seed, "onset", name, group),
            )
            paired[f"mean_{comparison.model_a}"] = _mean([losses_a[k] for k in positions])
            paired[f"mean_{comparison.model_b}"] = _mean([losses_b[k] for k in positions])
            if group == GROUP_ALL and positions:
                paired["diebold_mariano"] = diebold_mariano(
                    [losses_a[k] - losses_b[k] for k in positions]
                )
            if group == GROUP_ONSET:
                paired["note"] = ONSET_GROUP_NOTE
            elif group == GROUP_ONSET_ONE_DAY:
                paired["note"] = ONSET_ONE_DAY_NOTE
            entry[group] = paired
        document["by_series"][name] = entry
    return document
