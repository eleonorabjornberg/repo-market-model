"""A time-to-pressure hazard model (#387, track Z of #374).

The pressure-day probability is built from a **discrete-time hazard** rather
than fitted directly to the label of the scored day. At a decision instant `t`
the model asks, for each lead `k` = 1 to `K`, how likely the *first* pressure day
(SOFR - IORB above the threshold) after `t` is business day `t + k`, given
that none of `t + 1 .. t + k - 1` was:

    lambda_k(x) = P(Y[t+k] = 1 | Y[t+1 .. t+k-1] = 0, x)

where `x` is what was public at `t` (the latest spread, the reserves scarcity
state, the TGA's change) and the lead's own scheduled terms are the pressure-day
type of `t + k` (quarter end, month end, tax date), alone and times scarcity.
Calendar types are a function of the date alone (`data.CALENDAR_COLUMN_RULES`),
so day `t + k`'s type is public at `t`. The hazards are one pooled logistic
regression over (decision, lead) pairs, with a dummy per lead and the spread
decaying with the lead, fitted to the threshold's own label (+5 bp, +10 bp)
exactly as the direct models are.

Two quantities follow in closed form:

* **The window probability**, "at least one pressure day among the next `N`
  business days": `1 - prod_{k<=N} (1 - lambda_k)`. It is the desk-facing
  summary, and the week-ahead measure of the success bar when `N` = 5.
* **The per-day probability at horizon `h`**, the quantity the judge scores,
  `P(Y[t+h] = 1) = sum_{j<=h} F_j * q_{h-j}`, where `F_j = lambda_j * prod_{l<j}
  (1 - lambda_l)` is the probability that the first pressure day is `t + j` and
  `q_m` is the probability that the pressure persists `m` business days beyond
  the first pressure day (`q_0` = 1), a second pooled logistic regression on the
  training episodes. The decomposition is exact: the first pressure day is one
  of `t + 1 .. t + h`, or `t + h` is not a pressure day.

Standard library only. The two fits go through `ml._fit_classifier`, which is
imported inside the functions that need it (`tests/test_dependency_boundary.py`).

**The information set.** A decision's covariates are read by the as-of rule at
its own decision instant (`asof.InformationRule`); a lead's calendar type from
the date. A label enters a fit only if its row is inside the training frame, and
a pair is refused (`LookAheadError`) otherwise. The served lead calendar is the
date of `t + k`, worked out from the served row's anchor and the rule's own gap
between a scored day and its anchor, and refused (`ValueError`) unless the
target's calendar columns, which the rule read, agree with it.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, time
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .data import (
    CALENDAR_COLUMN_RULES,
    DailyObservation,
    exceeds_bp,
    next_business_day,
)
from .splits import LookAheadError, SplitError

__all__ = [
    "DEFAULT_DECLARATION",
    "Declaration",
    "HAZARD_SETTINGS",
    "day_probability",
    "first_passage_probabilities",
    "load_declaration",
    "pressure_hazard_exceedance",
    "survival",
    "window_benchmark_exceedance",
    "window_probability",
]

#: Settings chosen before scoring, not tuned: the direct logistic's own
#: (`ml.PRESSURE_LOGISTIC_SETTINGS`, an L2 logistic regression on standardised
#: columns), so the comparison with it isolates the hazard structure.
HAZARD_SETTINGS = MappingProxyType(
    {
        "estimator": "LogisticRegression",
        "C": 1.0,
        "penalty": "l2",
        "standardized": True,
        "structure": "discrete-time first-passage hazard, pooled over leads",
        "persistence": "logistic on the pressure persisting m days past the first pressure day",
    }
)

_TYPES = ("quarter_end", "month_end", "tax_date")
_CALENDAR = ("days_to_month_end", "quarter_end", "tax_date")


# --------------------------------------------------------------------------
# The closed forms
# --------------------------------------------------------------------------


def _unit(value: float, name: str) -> float:
    if not (isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0):
        raise ValueError(f"{name} must be a probability in [0, 1], got {value!r}")
    return float(value)


def survival(hazards: Sequence[float]) -> List[float]:
    """`S_k = prod_{l<=k} (1 - lambda_l)`, the chance of no pressure day through lead `k`."""

    out: List[float] = []
    running = 1.0
    for index, value in enumerate(hazards, start=1):
        running *= 1.0 - _unit(value, f"hazard {index}")
        out.append(running)
    return out


def first_passage_probabilities(hazards: Sequence[float]) -> List[float]:
    """`F_j = lambda_j * S_{j-1}`: the first pressure day after the decision is lead `j`."""

    out: List[float] = []
    running = 1.0
    for index, value in enumerate(hazards, start=1):
        value = _unit(value, f"hazard {index}")
        out.append(value * running)
        running *= 1.0 - value
    return out


def window_probability(hazards: Sequence[float], window: int) -> float:
    """P(at least one pressure day in the next `window` business days) from the hazards."""

    if window < 1 or window > len(hazards):
        raise ValueError(f"a window of {window} days needs {window} hazards, got {len(hazards)}")
    return 1.0 - survival(hazards[:window])[-1]


def day_probability(hazards: Sequence[float], persistence: Sequence[float], horizon: int) -> float:
    """P(lead `horizon` is a pressure day) = `sum_j F_j * q_{horizon-j}`.

    `persistence[m - 1]` is `q_m`, the chance the pressure still holds `m`
    business days past the first pressure day, for `m` = 1 to `horizon - 1`;
    `q_0` = 1.
    """

    if horizon < 1 or horizon > len(hazards):
        raise ValueError(f"horizon {horizon} needs {horizon} hazards, got {len(hazards)}")
    if len(persistence) < horizon - 1:
        raise ValueError(f"horizon {horizon} needs {horizon - 1} persistence terms, got {len(persistence)}")
    first = first_passage_probabilities(hazards[:horizon])
    total = first[horizon - 1]
    for lead in range(1, horizon):
        total += first[lead - 1] * _unit(persistence[horizon - lead - 1], "persistence")
    return min(1.0, max(0.0, total))


# --------------------------------------------------------------------------
# Calendar
# --------------------------------------------------------------------------


def calendar_values(day: date) -> Dict[str, float]:
    """The three calendar columns of `day`, from the date alone."""

    return {name: float(CALENDAR_COLUMN_RULES[name](day)) for name in _CALENDAR}


def _type_vector(kind: str) -> List[float]:
    return [1.0 if kind == name else 0.0 for name in _TYPES]


def gap_to_anchor(rule: Any) -> int:
    """How many panel days the rule puts between a scored day and its anchor.

    The anchor is the latest row whose target is public at the decision
    instant. It is measured on a synthetic run of consecutive business days
    (the rule counts business days on the market holiday table), so it is a
    property of the declaration alone.
    """

    days = [date(2023, 5, 1)]
    while len(days) < 40:
        days.append(next_business_day(days[-1], 1))
    index = len(days) - 1
    info = rule.information_set(days, index)
    return index - info.anchor


def lead_days(anchor: date, gap: int, horizon: int, leads: Optional[int] = None) -> List[date]:
    """The dates of leads 1 to `leads` (default `horizon`) after a decision.

    The decision day is `gap - horizon` business days after the anchor, so lead
    `k` is `gap - horizon + k` after it and the scored day (lead `horizon`) is
    `gap` after it.
    """

    start = gap - horizon
    if start < 0:
        raise ValueError(f"a gap of {gap} days is shorter than the horizon {horizon}")
    count = horizon if leads is None else leads
    return [next_business_day(anchor, start + k) for k in range(1, count + 1)]


# --------------------------------------------------------------------------
# The design
# --------------------------------------------------------------------------


class _Design:
    """The hazard's columns, from the declared features."""

    def __init__(self, features: Sequence[str], declaration: Any, leads: int) -> None:
        declared = tuple(dict.fromkeys(str(name) for name in features))
        if "spread_bps" not in declared:
            raise ValueError("a hazard model reads the latest public spread; declare spread_bps")
        calendar = [name for name in _CALENDAR if name in declared]
        if len(calendar) != len(_CALENDAR):
            raise ValueError(
                f"the lead's pressure-day type is read from {list(_CALENDAR)} together; "
                f"{calendar} were declared"
            )
        if not hasattr(declaration, "day_type"):
            raise ValueError("the pressure-day type needs the split declaration that defines it")
        if "tga" in declared and "reserve_balances" not in declared:
            raise ValueError("tga enters only as its change times reserves; declare reserve_balances with it")
        if leads < 1:
            raise ValueError(f"leads must be at least 1, got {leads}")
        self.features = declared
        self.declaration = declaration
        self.leads = leads
        self.scarcity = "reserve_balances" in declared
        self.tga = "tga" in declared
        state = ["spread_bps"]
        if self.scarcity:
            state.append(SCARCITY)
        if self.tga:
            state += ["tga_change", "tga_change_x_scarcity"]
        self.state_names = tuple(state)

    # -- the decision's own covariates -------------------------------------

    def state(self, observation: DailyObservation, tga_change: Optional[float]) -> List[float]:
        values = [self._value(observation, "spread_bps", observation.spread_bps)]
        reserves = 0.0
        if self.scarcity:
            reserves = self._value(observation, "reserve_balances") / 1000.0
            values.append(reserves)
        if self.tga:
            if tga_change is None:
                raise ValueError("the TGA change is required when tga is declared")
            values += [tga_change, tga_change * reserves]
        return values

    @staticmethod
    def _value(observation: DailyObservation, column: str, value: Any = None) -> float:
        value = observation.values.get(column) if value is None else value
        if value is None or not math.isfinite(float(value)):
            raise ValueError(
                f"{observation.date}: the as-of read of {column!r} is missing; a hazard "
                f"model is not fitted on an unobserved input"
            )
        return float(value)

    # -- the lead's terms ---------------------------------------------------

    def kind(self, values: Mapping[str, Optional[float]]) -> str:
        return self.declaration.day_type(values)

    def lead_row(self, state: Sequence[float], lead: int, kind: str) -> List[float]:
        """One (decision, lead) row of the hazard regression."""

        reserves = state[1] if self.scarcity else 0.0
        types = _type_vector(kind)
        row = list(state) + [state[0] / lead]
        row += types
        if self.scarcity:
            row += [term * reserves for term in types]
        row += [1.0 if lead == step else 0.0 for step in range(2, self.leads + 1)]
        return row

    def persistence_row(self, state: Sequence[float], steps: int, kind: str) -> List[float]:
        """One (decision, steps-past-first-pressure) row of the persistence regression."""

        reserves = state[1] if self.scarcity else 0.0
        types = _type_vector(kind)
        row = [state[0]] + ([reserves] if self.scarcity else [])
        row += types
        row += [1.0 if steps == step else 0.0 for step in range(2, self.leads)]
        return row

    def names(self) -> Dict[str, List[str]]:
        types = [f"type_{name}" for name in _TYPES]
        hazard = list(self.state_names) + ["spread_bps_over_lead"] + types
        if self.scarcity:
            hazard += [f"{name}_x_scarcity" for name in types]
        hazard += [f"lead_{step}" for step in range(2, self.leads + 1)]
        persistence = ["spread_bps"] + ([SCARCITY] if self.scarcity else []) + types
        persistence += [f"steps_{step}" for step in range(2, self.leads)]
        return {"hazard": hazard, "persistence": persistence}


SCARCITY = "reserve_balances_usd_tn"


# --------------------------------------------------------------------------
# The predictor
# --------------------------------------------------------------------------


def _decisions(
    design: _Design,
    information: Any,
    train_rows: Sequence[DailyObservation],
    cache: dict,
) -> Dict[int, List[float]]:
    """Each training decision's covariates, keyed by its row, under the as-of rule.

    Decision `i` is the instant `information.horizon` panel days before row
    `i + horizon`: the row whose information set is read, checked by both
    guards. A decision with no read or a missing input trains no pair. Cached by
    date: a decision reads only rows public by its own instant.
    """

    from . import ml

    dates = [row.date for row in train_rows]
    base = (information.horizon, information.features, design.features)
    out: Dict[int, List[float]] = {}
    for target in range(information.horizon, len(train_rows)):
        key = (base, dates[target])
        if key not in cache:
            cache[key] = None
            try:
                info = information.information_set(dates, target)
            except SplitError:
                continue
            information.check(dates, info)
            tga_change: Optional[float] = None
            if design.tga:
                (read,) = [r for r in info.reads if r.feature == "tga"]
                tga_change = ml._tga_change_at(train_rows, read.row)
                if tga_change is None:
                    continue
            try:
                cache[key] = design.state(information.observation(train_rows, info), tga_change)
            except ValueError:
                continue
        if cache[key] is not None:
            out[target - information.horizon] = cache[key]
    return out


def require_labels_inside(last_label: int, rows: int, *, what: str) -> None:
    """Refuse a training label at or past the end of the training frame.

    Raises:
        LookAheadError: if `last_label` is not a row of the frame.
    """

    if last_label >= rows:
        raise LookAheadError(
            f"{what}: a training pair reads the label of row {last_label}, but the "
            f"training frame has {rows} rows"
        )


def hazard_pairs(
    design: _Design,
    train_rows: Sequence[DailyObservation],
    decisions: Mapping[int, Sequence[float]],
    tau: float,
    persistence_leads: int,
) -> Tuple[List[List[float]], List[int], List[List[float]], List[int], int]:
    """Hazard and persistence training pairs for one threshold.

    For each decision `i` and lead `k` while no pressure day has occurred among
    `i + 1 .. i + k - 1`: the row for (i, k) labelled with whether `i + k` is a
    pressure day. The first pressure day `i + j` (if within the leads) then opens
    the persistence pairs (i, m) for `m` = 1 to `persistence_leads - 1`, labelled
    by `i + j + m`. Returns both designs, their labels, and the highest label
    row index read.
    """

    rows = len(train_rows)
    kinds = [design.kind(row.values) for row in train_rows]
    pressure = [1 if exceeds_bp(row.spread_bps, tau) else 0 for row in train_rows]
    hx: List[List[float]] = []
    hy: List[int] = []
    px: List[List[float]] = []
    py: List[int] = []
    highest = -1
    for i, state in sorted(decisions.items()):
        first: Optional[int] = None
        for lead in range(1, design.leads + 1):
            label_row = i + lead
            if label_row >= rows:
                break
            require_labels_inside(label_row, rows, what="hazard pair")
            highest = max(highest, label_row)
            hx.append(design.lead_row(state, lead, kinds[label_row]))
            hy.append(pressure[label_row])
            if pressure[label_row]:
                first = lead
                break
        if first is None:
            continue
        for steps in range(1, persistence_leads):
            label_row = i + first + steps
            if label_row >= rows:
                break
            require_labels_inside(label_row, rows, what="persistence pair")
            highest = max(highest, label_row)
            px.append(design.persistence_row(state, steps, kinds[label_row]))
            py.append(pressure[label_row])
    return hx, hy, px, py, highest


def _fit(
    xs: Sequence[Sequence[float]],
    labels: Sequence[int],
    served: Sequence[Sequence[float]],
    *,
    empty: Optional[float] = None,
) -> List[float]:
    """P(label = 1) at `served` from the declared logistic; a constant when one class only.

    `empty`: the value when there is no training pair at all, `None` to refuse.
    The persistence fit passes 0.0: with no pressure episode followed by a later
    label there is no evidence the pressure persists, and the hazards are then
    zero or the episode is the last row of the frame.
    """

    from . import ml

    if not served:
        return []
    if not xs:
        if empty is None:
            raise ValueError("a hazard fit has no training pair")
        return [empty] * len(served)
    if len(set(labels)) < 2:
        return [float(labels[0])] * len(served)
    return ml._fit_classifier("logistic", xs, labels, served)


def pressure_hazard_exceedance(
    features: Sequence[str],
    declaration: Any,
    *,
    minimum_history: int,
    window: Optional[int] = None,
    max_horizon: int = 5,
) -> Any:
    """The hazard predictor, in the `ExceedancePredictor` shape.

    By default the curves are the per-day probability P(spread > tau) at the
    run's horizon. With `window=N` they are P(at least one pressure day among
    the next N business days) from the decision instant; that run must be at
    horizon 1, so the window starts at the scored day.
    """

    from .baseline import ExceedanceCurves

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")
    if window is not None and not (1 <= window <= max_horizon):
        raise ValueError(f"window must be 1 to {max_horizon}, got {window}")
    cache: dict = {}

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[Any] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> Any:
        from . import ml

        if information is None:
            raise ValueError(
                "a hazard model reads each decision's covariates under the as-of rule, "
                "which only the rule can say; it was called without one"
            )
        horizon = information.horizon
        if window is not None and horizon != 1:
            raise ValueError(f"a window forecast is made at horizon 1, not {horizon}")
        if horizon > max_horizon:
            raise ValueError(f"horizon {horizon} is beyond the declared {max_horizon}")
        leads = window if window is not None else horizon
        design = _Design(features, declaration, leads)
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a hazard model needs at least {minimum_history} training rows, got {len(train_rows)}"
            )
        if design.tga and (histories is None or len(histories) != len(feature_rows)):
            raise ValueError(
                "the TGA change is read off each forecast's own as-of history; "
                "one history per feature row is required"
            )
        decisions = _decisions(design, information, train_rows, cache)
        if not decisions:
            raise ValueError("no training decision has a complete as-of read")
        gap = gap_to_anchor(information)
        served_state: List[List[float]] = []
        served_kinds: List[List[str]] = []
        for day, row in enumerate(feature_rows):
            tga_change = ml._served_tga_change(histories[day], row) if design.tga else None
            served_state.append(design.state(row, tga_change))
            served_kinds.append(_served_kinds(design, row, gap, horizon, leads, window is not None))
        persistence_leads = leads if window is None else 1
        curves_by_tau: List[List[float]] = []
        for tau in taus:
            hx, hy, px, py, highest = hazard_pairs(
                design, train_rows, decisions, float(tau), persistence_leads
            )
            require_labels_inside(highest, len(train_rows), what=f"fit at {tau:g} bp")
            haz_served = [
                design.lead_row(state, lead, kinds[lead - 1])
                for state, kinds in zip(served_state, served_kinds)
                for lead in range(1, leads + 1)
            ]
            hazards = _fit(hx, hy, haz_served)
            persistence: List[float] = []
            if window is None and horizon > 1:
                per_served = [
                    design.persistence_row(state, steps, kinds[horizon - 1])
                    for state, kinds in zip(served_state, served_kinds)
                    for steps in range(1, horizon)
                ]
                persistence = _fit(px, py, per_served, empty=0.0)
            column: List[float] = []
            for day in range(len(feature_rows)):
                lam = hazards[day * leads : (day + 1) * leads]
                if window is not None:
                    column.append(window_probability(lam, window))
                else:
                    q = persistence[day * (horizon - 1) : (day + 1) * (horizon - 1)]
                    column.append(day_probability(lam, q, horizon))
            curves_by_tau.append(column)
        curves = []
        for day in range(len(feature_rows)):
            curve: List[float] = []
            for column in curves_by_tau:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        names = design.names()
        settings = dict(HAZARD_SETTINGS)
        settings.update(
            {
                "design": names,
                "leads": leads,
                "target": "window" if window is not None else "day",
                "window": window,
                "scarcity_state": SCARCITY if design.scarcity else None,
            }
        )
        return ExceedanceCurves(
            tuple(curves),
            design.features,
            ml_libraries=ml._library_versions(),
            model_settings=MappingProxyType(settings),
        )

    return fit_predict


def _served_kinds(
    design: _Design,
    observation: DailyObservation,
    gap: int,
    horizon: int,
    leads: int,
    window: bool,
) -> List[str]:
    """The pressure-day type of each lead after the served row's decision.

    Day `t + k` is `gap - horizon + k` business days after the anchor. For a
    per-day forecast the scored day is lead `horizon`, and for a window
    forecast lead 1; the rule read that day's calendar columns, so the date
    worked out here must reproduce them.

    Raises:
        ValueError: if the scored day's calendar columns are not those of the
            date worked out, which would put every lead on the wrong day.
    """

    days = lead_days(observation.date, gap, horizon, max(horizon, leads))
    scored = days[horizon - 1]
    expected = calendar_values(scored)
    for name in _CALENDAR:
        read = observation.values.get(name)
        if read is None or abs(float(read) - expected[name]) > 1e-9:
            raise ValueError(
                f"{observation.date}: the served row read {name} = {read!r} for its scored "
                f"day, but the day {gap} panel days after its anchor ({scored}) has {expected[name]!r}"
            )
    return [design.kind(calendar_values(day)) for day in days[:leads]]


# --------------------------------------------------------------------------
# The declaration, and the window's benchmarks
# --------------------------------------------------------------------------

DEFAULT_DECLARATION = Path(__file__).parents[2] / "metadata" / "pressure_hazard.json"


@dataclass(frozen=True)
class Declaration:
    """`metadata/pressure_hazard.json`, parsed and checked."""

    path: str
    sha256: str
    candidate: str
    last_day: date
    minimum_history: int
    refit_every: int
    decision_time: time
    thresholds: Tuple[float, ...]
    horizons: Tuple[int, ...]
    features: Tuple[str, ...]
    window_days: int
    window_cutoffs: Mapping[float, float]
    cutoffs: Mapping[float, float]


def load_declaration(path: Path = DEFAULT_DECLARATION) -> Declaration:
    """Read and check the hazard declaration.

    Raises:
        ValueError: on a missing or malformed file, a cut-off that is not a
            probability strictly between 0 and 1, or a window longer than the
            horizons the model is declared for.
    """

    raw = Path(path).read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} is not JSON: {exc}") from exc
    for key in ("candidate", "scoring", "thresholds_bp", "horizons", "features", "model", "window", "cutoffs"):
        if key not in document:
            raise ValueError(f"{path} declares no {key!r}")
    thresholds = tuple(float(tau) for tau in document["thresholds_bp"])
    horizons = tuple(int(h) for h in document["horizons"])

    def cutoffs(block: Mapping[str, Any], where: str) -> Dict[float, float]:
        out = {}
        for tau in thresholds:
            value = block.get(f"{tau:g}")
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0.0 < float(value) < 1.0:
                raise ValueError(f"{path}: {where} cut-off at {tau:g} bp must be strictly between 0 and 1")
            out[tau] = float(value)
        return out

    window_days = int(document["window"]["days"])
    if not 1 <= window_days <= max(horizons):
        raise ValueError(f"{path}: the window of {window_days} days is outside 1 to {max(horizons)}")
    scoring = document["scoring"]
    hour, minute = (int(part) for part in str(scoring["decision_time"]).split(":"))
    return Declaration(
        path=str(path),
        sha256=hashlib.sha256(raw).hexdigest(),
        candidate=str(document["candidate"]),
        last_day=date.fromisoformat(scoring["last_day"]),
        minimum_history=int(scoring["minimum_history"]),
        refit_every=int(scoring["refit_every"]),
        decision_time=time(hour, minute),
        thresholds=thresholds,
        horizons=horizons,
        features=tuple(document["features"]),
        window_days=window_days,
        window_cutoffs=cutoffs(document["window"]["cutoffs"], "window"),
        cutoffs=cutoffs(document["cutoffs"], "day"),
    )


def window_benchmark_exceedance(
    kind: str,
    features: Sequence[str],
    declaration: Any,
    *,
    minimum_history: int,
    window: int = 5,
) -> Any:
    """The window event's two benchmarks, in the `ExceedancePredictor` shape.

    * `"climatology"`: the frequency of the window event among training
      decisions whose window holds the same set of pressure-day types (any of
      quarter end, month end, tax date), the global frequency where fewer than
      `MINIMUM_GROUP` training decisions share the set.
    * `"persistence"`: a logistic regression of the window event on the latest
      public spread.

    Both are fitted on the training decisions at horizon 1, whose windows lie
    wholly inside the training frame (`hazard_pairs`' rule), and both are
    forecasts of the same window the hazard's window run forecasts.
    """

    from .baseline import ExceedanceCurves

    if kind not in ("climatology", "persistence"):
        raise ValueError(f"unknown window benchmark {kind!r}")
    cache: dict = {}

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
        information: Optional[Any] = None,
        histories: Optional[Sequence[Sequence[DailyObservation]]] = None,
    ) -> Any:
        from . import ml

        if information is None or information.horizon != 1:
            raise ValueError("a window benchmark is fitted under the as-of rule at horizon 1")
        if len(train_rows) < minimum_history:
            raise ValueError(
                f"a window benchmark needs at least {minimum_history} training rows, got {len(train_rows)}"
            )
        design = _Design(features, declaration, window)
        decisions = _decisions(design, information, train_rows, cache)
        if not decisions:
            raise ValueError("no training decision has a complete as-of read")
        gap = gap_to_anchor(information)
        kinds = [design.kind(row.values) for row in train_rows]
        served = [
            _served_kinds(design, row, gap, 1, window, True) for row in feature_rows
        ]
        columns = []
        for tau in taus:
            events = [1 if exceeds_bp(row.spread_bps, float(tau)) else 0 for row in train_rows]
            labels: Dict[int, int] = {}
            groups: Dict[Tuple[str, ...], List[int]] = {}
            for i in decisions:
                if i + window >= len(train_rows):
                    continue
                require_labels_inside(i + window, len(train_rows), what="window benchmark")
                label = 1 if any(events[i + k] for k in range(1, window + 1)) else 0
                labels[i] = label
                key = tuple(sorted({kinds[i + k] for k in range(1, window + 1)} - {"ordinary"}))
                groups.setdefault(key, []).append(label)
            if not labels:
                raise ValueError("no training decision has a full window inside the training frame")
            overall = sum(labels.values()) / len(labels)
            if kind == "climatology":
                column = []
                for lead_kinds in served:
                    key = tuple(sorted(set(lead_kinds) - {"ordinary"}))
                    group = groups.get(key, [])
                    column.append(sum(group) / len(group) if len(group) >= MINIMUM_GROUP else overall)
            else:
                xs = [[decisions[i][0]] for i in labels]
                ys = [labels[i] for i in labels]
                state = [[design.state(row, None)[0]] for row in feature_rows]
                column = _fit(xs, ys, state)
            columns.append(column)
        curves = []
        for day in range(len(feature_rows)):
            curve: List[float] = []
            for column in columns:
                value = min(1.0, max(0.0, column[day]))
                curve.append(value if not curve else min(curve[-1], value))
            curves.append(tuple(curve))
        return ExceedanceCurves(
            tuple(curves),
            tuple(features),
            ml_libraries=ml._library_versions(),
            model_settings=MappingProxyType({"window_benchmark": kind, "window": window}),
        )

    return fit_predict


#: Fewer training decisions than this share a window's type set: use the global frequency.
MINIMUM_GROUP = 10
