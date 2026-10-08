"""The pressure-day judge (#375, track J of #374): one bar for every candidate.

Eleonora's ruling of 7 October 2026 on #374 sets the bar a pressure probability
must clear. On days before 2026-01-01, under the shared fold grid and
`docs/decisions/information-set.md`, a candidate succeeds only if, for
P(SOFR - IORB > +5 bp) at a lead of at least one business day:

1. it flags at least **70%** of the days above +5 bp (recall);
2. it raises **at most one false alarm per true pressure day** at the flagging
   cut-off used for that recall (precision of at least 50%); and
3. it beats **calendar-type climatology at the same recall**, paired, with a
   stationary-bootstrap 90% interval that excludes zero on both the Brier score
   and precision.

This module applies that bar to walk-forward probabilities. It fits nothing: a
candidate is a `Forecast` (its probability for each scored day, at each
threshold and horizon) produced elsewhere, and `benchmark_forecasts` produces
the two benchmarks the same way every candidate is produced.

**The declaration is a file the judge reads** (`metadata/pressure_judge.json`):
every candidate, its features, its calibration step, its flagging cut-off, the
thresholds, the horizons and the pass rule, committed before any score is
computed. `Declaration.cutoff` is the only way a cut-off enters a score, and it
refuses a candidate or threshold the file does not carry and a requested cut-off
that differs from the declared one: a cut-off is never tuned on scored days.
Every result carries the declaration's digest.

**The scored days.** `require_scored_days` refuses a day in a lockbox tier that
has not been opened (`docs/decisions/lockbox.md`) and a day after the
declaration's last scored day (2025-12-31, #374), both with `LookAheadError`,
before any score is computed.

**What it reports**, per candidate, horizon and threshold, beside the pooled
bar: Brier with its CORP decomposition and the CORP reliability steps, AUROC,
average precision, usefulness (Alessi & Detken, 2011; Sarlin) at the declared
cut-off, lead time at +5 bp, and the bar by every declared grouping (the
regimes, the reserve-scarcity state of #115, the pressure-day type, and any
grouping a later track declares) and on the knowledge-holdout windows.

**"At the same recall."** The reference's precision is read where its own
ranking reaches the candidate's recall: the reference flags its highest
probabilities until the share of pressure days flagged equals the candidate's,
and a group of tied probabilities is flagged in part (`matched_recall_weights`),
which is the expected precision of breaking the tie at random. The weights are
fixed from the scored days and held across bootstrap resamples, so the paired
precision difference measures the candidate against a fixed reference rule.

**The intervals** are stationary bootstrap, at the declared level, block length,
replications and seed; the day is resampled whole, so the pairing holds. A
statistic undefined on any resample (no alarm drawn, say) has no interval, and
the criterion that needs it is not met: the replicates are never dropped
(`metrics.stationary_bootstrap_interval`'s rule).

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from datetime import date
from operator import itemgetter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from . import lockbox
from .metrics import (
    MetricError,
    average_precision,
    corp_decomposition,
    corp_reliability_curve,
    stationary_bootstrap_indices,
)
from .splits import LookAheadError

__all__ = [
    "DEFAULT_DECLARATION",
    "Declaration",
    "Forecast",
    "Grid",
    "auroc",
    "benchmark_forecasts",
    "build_grid",
    "forecasts_from_horizon_document",
    "judge",
    "load_declaration",
    "matched_recall_weights",
    "report_forecast",
    "require_scored_days",
    "usefulness",
]

DEFAULT_DECLARATION = Path(__file__).parents[2] / "metadata" / "pressure_judge.json"

_ROLES = ("benchmark", "baseline", "candidate")


# --------------------------------------------------------------------------
# The declaration
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Declaration:
    """`metadata/pressure_judge.json`, parsed and checked."""

    path: str
    sha256: str
    status: str
    last_day: date
    thresholds: Tuple[float, ...]
    primary: float
    horizons: Tuple[int, ...]
    pass_horizons: Tuple[int, ...]
    recall_at_least: float
    false_alarms_per_true_at_most: float
    level: float
    replications: int
    block_length: int
    seed: int
    usefulness_preference: float
    groupings: Tuple[str, ...]
    climatology: str
    persistence: str
    candidates: Mapping[str, Mapping[str, Any]]

    def cutoff(
        self,
        name: str,
        tau: float,
        horizon: int,
        requested: Optional[float] = None,
    ) -> float:
        """The flagging cut-off the declaration carries for one candidate cell.

        Raises:
            ValueError: if the candidate or its cut-off at `tau` is not
                declared, or `requested` differs from the declared cut-off. A
                cut-off that is not in the file was not declared before
                scoring.
        """

        entry = self.candidates.get(name)
        if entry is None:
            raise ValueError(f"{name!r} is not a declared candidate in {self.path}")
        cutoffs = entry["cutoffs"].get(_key(tau))
        if cutoffs is None:
            raise ValueError(
                f"{name!r} declares no cut-off at {_key(tau)} bp in {self.path}; "
                f"a cut-off is declared before scoring, never chosen on scored days"
            )
        declared = cutoffs if not isinstance(cutoffs, Mapping) else cutoffs.get(str(horizon))
        if declared is None:
            raise ValueError(f"{name!r} declares no cut-off at {_key(tau)} bp, h = {horizon}")
        if requested is not None and float(requested) != float(declared):
            raise ValueError(
                f"cut-off {requested} for {name!r} at {_key(tau)} bp is not the declared "
                f"{declared}; the judge scores the declared cut-off only"
            )
        return float(declared)

    def document(self) -> dict:
        """What a result carries about the declaration it was judged under."""

        return {
            "path": self.path,
            "sha256": self.sha256,
            "status": self.status,
            "last_scored_day": self.last_day.isoformat(),
            "thresholds_bp": list(self.thresholds),
            "primary_threshold_bp": self.primary,
            "horizons": list(self.horizons),
            "pass_horizons": list(self.pass_horizons),
            "bar": {
                "recall_at_least": self.recall_at_least,
                "false_alarms_per_true_at_most": self.false_alarms_per_true_at_most,
                "level": self.level,
                "replications": self.replications,
                "block_length": self.block_length,
                "seed": self.seed,
            },
            "usefulness_preference": self.usefulness_preference,
            "groupings": list(self.groupings),
            "climatology": self.climatology,
            "persistence": self.persistence,
            "candidates": {
                name: {key: entry[key] for key in ("role", "features", "calibration", "cutoffs")}
                for name, entry in self.candidates.items()
            },
        }


def _key(tau: float) -> str:
    return f"{float(tau):g}"


def _number(value: object, where: str, low: float, high: float, *, open_ends: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{where} must be a number, got {value!r}")
    inside = low < value < high if open_ends else low <= value <= high
    if not inside:
        raise ValueError(f"{where} must be in {'(' if open_ends else '['}{low}, {high}{')' if open_ends else ']'}, got {value!r}")
    return float(value)


def _integer(value: object, where: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{where} must be an int >= {minimum}, got {value!r}")
    return value


def load_declaration(path: Path = DEFAULT_DECLARATION) -> Declaration:
    """Read and check the judge's declaration.

    Raises:
        ValueError: on a missing or malformed file, a cut-off that is not a
            probability strictly between 0 and 1, a candidate without a
            cut-off at every threshold and horizon, or a benchmark that is
            not a declared candidate.
    """

    raw = Path(path).read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} is not JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{path} must hold an object")
    for key in (
        "status", "scoring", "thresholds_bp", "primary_threshold_bp", "horizons",
        "pass_horizons", "bar", "early_warning", "groupings", "benchmarks", "candidates",
    ):
        if key not in document:
            raise ValueError(f"{path} declares no {key!r}")
    try:
        last_day = date.fromisoformat(document["scoring"]["last_day"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{path}: scoring.last_day must be an ISO date") from exc
    thresholds = tuple(
        _number(tau, "thresholds_bp", 0.0, 1000.0) for tau in document["thresholds_bp"]
    )
    if not thresholds or list(thresholds) != sorted(set(thresholds)):
        raise ValueError(f"{path}: thresholds_bp must be ascending and distinct")
    primary = _number(document["primary_threshold_bp"], "primary_threshold_bp", 0.0, 1000.0)
    if primary not in thresholds:
        raise ValueError(f"{path}: primary_threshold_bp must be one of thresholds_bp")
    horizons = tuple(_integer(h, "horizons") for h in document["horizons"])
    if not horizons or list(horizons) != sorted(set(horizons)):
        raise ValueError(f"{path}: horizons must be ascending and distinct")
    pass_horizons = tuple(_integer(h, "pass_horizons") for h in document["pass_horizons"])
    if not pass_horizons or not set(pass_horizons) <= set(horizons):
        raise ValueError(f"{path}: pass_horizons must be a non-empty subset of horizons")
    bar = document["bar"]
    groupings = tuple(document["groupings"])
    if not groupings or any(not isinstance(g, str) or not g for g in groupings):
        raise ValueError(f"{path}: groupings must be non-empty names")

    candidates: Dict[str, Dict[str, Any]] = {}
    for name, entry in document["candidates"].items():
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: candidate {name!r} must be an object")
        if entry.get("role") not in _ROLES:
            raise ValueError(f"{path}: candidate {name!r} needs a role in {list(_ROLES)}")
        for key in ("features", "calibration", "cutoffs"):
            if key not in entry:
                raise ValueError(f"{path}: candidate {name!r} declares no {key!r}")
        cutoffs = entry["cutoffs"]
        if not isinstance(cutoffs, dict):
            raise ValueError(f"{path}: candidate {name!r} cutoffs must be an object")
        for tau in thresholds:
            declared = cutoffs.get(_key(tau))
            where = f"{path}: {name!r} cut-off at {_key(tau)} bp"
            if declared is None:
                raise ValueError(f"{where} is not declared; declare it before scoring")
            if isinstance(declared, dict):
                if sorted(declared) != [str(h) for h in horizons]:
                    raise ValueError(f"{where} must name every horizon {list(horizons)}")
                for h, value in declared.items():
                    _number(value, f"{where}, h = {h}", 0.0, 1.0, open_ends=True)
            else:
                _number(declared, where, 0.0, 1.0, open_ends=True)
        candidates[name] = entry

    pair = document["benchmarks"]
    climatology, persistence = pair.get("climatology"), pair.get("persistence")
    for label, name in (("climatology", climatology), ("persistence", persistence)):
        if name not in candidates:
            raise ValueError(f"{path}: benchmarks.{label} {name!r} is not a declared candidate")

    return Declaration(
        path=str(path),
        sha256=hashlib.sha256(raw).hexdigest(),
        status=str(document["status"]),
        last_day=last_day,
        thresholds=thresholds,
        primary=primary,
        horizons=horizons,
        pass_horizons=pass_horizons,
        recall_at_least=_number(bar.get("recall_at_least"), "bar.recall_at_least", 0.0, 1.0),
        false_alarms_per_true_at_most=_number(
            bar.get("false_alarms_per_true_at_most"), "bar.false_alarms_per_true_at_most", 0.0, 1000.0
        ),
        level=_number(bar.get("level"), "bar.level", 0.0, 1.0, open_ends=True),
        replications=_integer(bar.get("replications"), "bar.replications", 2),
        block_length=_integer(bar.get("block_length"), "bar.block_length"),
        seed=_integer(bar.get("seed"), "bar.seed", 0),
        usefulness_preference=_number(
            document["early_warning"].get("usefulness_preference"),
            "early_warning.usefulness_preference", 0.0, 1.0, open_ends=True,
        ),
        groupings=groupings,
        climatology=climatology,
        persistence=persistence,
        candidates=candidates,
    )


# --------------------------------------------------------------------------
# Inputs and guards
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Grid:
    """The shared scored days at one horizon, their outcomes and their groups.

    `outcomes[tau]` is 1 on a day with SOFR - IORB strictly above `tau` bp.
    `groups[dimension]` is the day's label in that grouping, read as of its
    decision instant. `onsets` are the +5 bp onset days (`pressure.onsets`),
    for lead time.
    """

    horizon: int
    dates: Tuple[date, ...]
    outcomes: Mapping[float, Tuple[int, ...]]
    groups: Mapping[str, Tuple[str, ...]]
    onsets: Tuple[date, ...]


@dataclass(frozen=True)
class Forecast:
    """One candidate's walk-forward probabilities at one horizon."""

    name: str
    horizon: int
    dates: Tuple[date, ...]
    probabilities: Mapping[float, Tuple[float, ...]]


def require_scored_days(declaration: Declaration, days: Sequence[date], *, where: str) -> None:
    """Refuse a day the comparison may not score.

    Raises:
        LookAheadError: for a day in a lockbox tier that has not been opened,
            or after the declaration's last scored day. Both are checked before
            any score is computed.
    """

    lockbox.require_unlocked(days, where=where)
    for day in sorted(days):
        if day > declaration.last_day:
            raise LookAheadError(
                f"{where}: scored day {day} is after the declared last scored day "
                f"{declaration.last_day} ({declaration.path}); #374 scores days before "
                f"2026-01-01 only"
            )


def _check_grid(declaration: Declaration, grids: Mapping[int, Grid]) -> None:
    if sorted(grids) != list(declaration.horizons):
        raise ValueError(
            f"the grids cover horizons {sorted(grids)}; the declaration judges "
            f"{list(declaration.horizons)}"
        )
    for horizon, grid in grids.items():
        if grid.horizon != horizon:
            raise ValueError(f"grid keyed {horizon} says horizon {grid.horizon}")
        require_scored_days(declaration, grid.dates, where=f"pressure_judge.judge (h = {horizon})")
        count = len(grid.dates)
        if count == 0 or list(grid.dates) != sorted(set(grid.dates)):
            raise ValueError(f"grid h = {horizon}: the scored days must be non-empty, ascending and distinct")
        for tau in declaration.thresholds:
            outcomes = grid.outcomes.get(tau)
            if outcomes is None or len(outcomes) != count or any(y not in (0, 1) for y in outcomes):
                raise ValueError(f"grid h = {horizon}: needs a 0/1 outcome per day at {_key(tau)} bp")
        absent = sorted(set(declaration.groupings) - set(grid.groups))
        if absent:
            raise ValueError(f"grid h = {horizon} lacks the declared groupings {absent}")
        for dimension in declaration.groupings:
            if len(grid.groups[dimension]) != count:
                raise ValueError(f"grid h = {horizon}: grouping {dimension!r} is not one label per day")


def _check_forecasts(
    declaration: Declaration, grids: Mapping[int, Grid], forecasts: Sequence[Forecast]
) -> Dict[str, Dict[int, Forecast]]:
    by_name: Dict[str, Dict[int, Forecast]] = {}
    for forecast in forecasts:
        if forecast.name not in declaration.candidates:
            raise ValueError(
                f"{forecast.name!r} is not declared in {declaration.path}; "
                f"every candidate is declared before it is scored"
            )
        if forecast.horizon not in grids:
            raise ValueError(f"{forecast.name!r}: horizon {forecast.horizon} is not judged")
        if forecast.horizon in by_name.setdefault(forecast.name, {}):
            raise ValueError(f"{forecast.name!r} appears twice at h = {forecast.horizon}")
        grid = grids[forecast.horizon]
        if tuple(forecast.dates) != tuple(grid.dates):
            raise ValueError(
                f"{forecast.name!r} h = {forecast.horizon}: forecasts are not on the grid's days; "
                f"a paired comparison needs one grid"
            )
        for tau in declaration.thresholds:
            column = forecast.probabilities.get(tau)
            if column is None or len(column) != len(grid.dates):
                raise ValueError(f"{forecast.name!r} h = {forecast.horizon}: no probability column at {_key(tau)} bp")
            for p in column:
                if not isinstance(p, (int, float)) or isinstance(p, bool) or not 0.0 <= p <= 1.0:
                    raise ValueError(
                        f"{forecast.name!r} h = {forecast.horizon}: probability {p!r} is not in [0, 1]"
                    )
        by_name[forecast.name][forecast.horizon] = forecast
    for name, per_horizon in by_name.items():
        missing = [h for h in declaration.horizons if h not in per_horizon]
        if missing:
            raise ValueError(f"{name!r} has no forecasts at horizons {missing}")
    for label, name in (("climatology", declaration.climatology), ("persistence", declaration.persistence)):
        if name not in by_name:
            raise ValueError(
                f"the declared {label} benchmark {name!r} was not scored; the judge pairs every "
                f"candidate against it"
            )
    return by_name


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------


def auroc(probabilities: Sequence[float], outcomes: Sequence[int]) -> Optional[float]:
    """The area under the ROC curve: P(event day ranks above non-event day), ties half.

    `None` when there is no event or no non-event.
    """

    events = sum(outcomes)
    others = len(outcomes) - events
    if events == 0 or others == 0:
        return None
    order = sorted(range(len(outcomes)), key=lambda i: probabilities[i])
    rank_sum, position = 0.0, 0
    while position < len(order):
        tie_end = position
        while tie_end + 1 < len(order) and probabilities[order[tie_end + 1]] == probabilities[order[position]]:
            tie_end += 1
        average_rank = (position + tie_end) / 2.0 + 1.0
        rank_sum += average_rank * sum(outcomes[order[k]] for k in range(position, tie_end + 1))
        position = tie_end + 1
    return (rank_sum - events * (events + 1) / 2.0) / (events * others)


def usefulness(flags: Sequence[int], outcomes: Sequence[int], preference: float) -> dict:
    """Alessi & Detken's usefulness of a flagging rule at preference `theta`.

    Loss L = theta FNR + (1 - theta) FPR; the best default (never flag, or
    always flag) loses min(theta, 1 - theta). Absolute usefulness is that
    minus L; relative is absolute over the default's loss.
    """

    events = sum(outcomes)
    others = len(outcomes) - events
    if events == 0 or others == 0:
        return {"preference": preference, "absolute": None, "relative": None, "unavailable": "no events or no non-events"}
    false_negatives = sum(1 for f, y in zip(flags, outcomes) if y and not f)
    false_positives = sum(1 for f, y in zip(flags, outcomes) if f and not y)
    loss = preference * false_negatives / events + (1.0 - preference) * false_positives / others
    default = min(preference, 1.0 - preference)
    return {
        "preference": preference,
        "false_negative_rate": false_negatives / events,
        "false_positive_rate": false_positives / others,
        "loss": loss,
        "absolute": default - loss,
        "relative": (default - loss) / default,
    }


def matched_recall_weights(
    probabilities: Sequence[float], outcomes: Sequence[int], target_recall: float
) -> Tuple[float, ...]:
    """Per-day flag weights of a reference that reaches `target_recall` exactly.

    The reference flags its highest probabilities first. Groups of tied
    probabilities are flagged whole until the next group would overshoot the
    recall; that group is flagged in part, the same fraction of each of its
    days, which is the expected precision of breaking the tie at random.
    """

    events = sum(outcomes)
    if events == 0:
        raise ValueError("no event day: a recall is undefined")
    needed = target_recall * events
    weights = [0.0] * len(outcomes)
    flagged_events = 0.0
    by_value: Dict[float, List[int]] = {}
    for index, p in enumerate(probabilities):
        by_value.setdefault(p, []).append(index)
    for value in sorted(by_value, reverse=True):
        if flagged_events >= needed - 1e-12:
            break
        members = by_value[value]
        group_events = sum(outcomes[i] for i in members)
        if group_events == 0 or flagged_events + group_events <= needed + 1e-12:
            for i in members:
                weights[i] = 1.0
            flagged_events += group_events
        else:
            fraction = (needed - flagged_events) / group_events
            for i in members:
                weights[i] = fraction
            flagged_events = needed
    return tuple(weights)


def _flags_summary(flags: Sequence[float], outcomes: Sequence[int]) -> dict:
    alarms = sum(flags)
    hits = sum(f for f, y in zip(flags, outcomes) if y)
    events = sum(outcomes)
    false_alarms = alarms - hits
    return {
        "alarms": _clean(alarms),
        "hits": _clean(hits),
        "false_alarms": _clean(false_alarms),
        "recall": None if events == 0 else hits / events,
        "precision": None if alarms == 0 else hits / alarms,
        "false_alarms_per_true": None if hits == 0 else false_alarms / hits,
    }


def _clean(value: float) -> Any:
    return int(value) if float(value).is_integer() else value


def _decomposition(probabilities: Sequence[float], outcomes: Sequence[int]) -> dict:
    count = len(outcomes)
    entry: dict = {
        "brier": sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / count,
    }
    try:
        decomposition = corp_decomposition(probabilities, outcomes)
    except MetricError as exc:
        entry["decomposition_unavailable"] = str(exc)
    else:
        entry["reliability"] = decomposition.reliability
        entry["resolution"] = decomposition.resolution
        entry["uncertainty"] = decomposition.uncertainty
    return entry


def _reliability_steps(probabilities: Sequence[float], outcomes: Sequence[int]) -> Any:
    try:
        curve = corp_reliability_curve(probabilities, outcomes)
    except MetricError as exc:
        return {"unavailable": str(exc)}
    steps: List[dict] = []
    for forecast, fitted in zip(curve.forecast, curve.recalibrated):
        if steps and steps[-1]["observed"] == fitted:
            steps[-1]["forecast_high"] = forecast
            steps[-1]["days"] += 1
        else:
            steps.append({"forecast_low": forecast, "forecast_high": forecast, "observed": fitted, "days": 1})
    return steps


# --------------------------------------------------------------------------
# The paired bootstrap
# --------------------------------------------------------------------------

#: The per-day vectors a paired cell sums, in the order `_cell_statistics` reads.
_SUMS = ("days", "brier_difference", "flags", "hits", "reference_flags", "reference_hits", "events")


def _seed(base: int, *parts: object) -> int:
    material = "\x00".join([str(base)] + [str(part) for part in parts])
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:4], "big") & 0x7FFFFFFF


def _cell_statistics(sums: Sequence[float]) -> Dict[str, Optional[float]]:
    days, brier_difference, flags, hits, reference_flags, reference_hits, events = sums
    out: Dict[str, Optional[float]] = {
        "brier_difference": brier_difference / days if days else None,
        "recall": hits / events if events else None,
        "precision": hits / flags if flags else None,
        "reference_precision": reference_hits / reference_flags if reference_flags else None,
    }
    out["precision_difference"] = (
        None if out["precision"] is None or out["reference_precision"] is None
        else out["precision"] - out["reference_precision"]
    )
    return out


_INTERVALLED = ("brier_difference", "precision_difference")


def _paired_cells(
    declaration: Declaration,
    cells: Mapping[str, Sequence[Sequence[float]]],
    count: int,
    *,
    seed: int,
) -> Dict[str, dict]:
    """Point estimates and bootstrap intervals for every cell, on shared resamples.

    `cells[label]` holds one per-day vector for each of `_SUMS` (zero where the
    day is outside the cell). Every cell is read off the same resampled days.
    """

    labels = list(cells)
    rng = random.Random(seed)
    draws: Dict[Tuple[str, str], List[float]] = {(l, s): [] for l in labels for s in _INTERVALLED}
    undefined: Dict[Tuple[str, str], int] = {key: 0 for key in draws}
    for _ in range(declaration.replications):
        indices = stationary_bootstrap_indices(count, declaration.block_length, rng)
        pick = itemgetter(*indices) if count > 1 else (lambda v, i=indices[0]: (v[i],))
        for label in labels:
            totals = [sum(pick(vector)) for vector in cells[label]]
            statistics = _cell_statistics(totals)
            for name in _INTERVALLED:
                value = statistics[name]
                if value is None:
                    undefined[(label, name)] += 1
                else:
                    draws[(label, name)].append(value)
    tail = (1.0 - declaration.level) / 2.0
    out: Dict[str, dict] = {}
    for label in labels:
        point = _cell_statistics([sum(vector) for vector in cells[label]])
        entry: Dict[str, Any] = {
            "days": _clean(sum(cells[label][0])),
            "events": _clean(sum(cells[label][-1])),
            **{key: point[key] for key in ("recall", "precision", "reference_precision")},
        }
        for name in _INTERVALLED:
            cell = {"mean": point[name]}
            if undefined[(label, name)] or point[name] is None:
                cell["interval_unavailable"] = (
                    f"{name} is undefined on {undefined[(label, name)]} of "
                    f"{declaration.replications} resamples (no alarm or no event drawn); "
                    f"replicates are not dropped"
                    if point[name] is not None
                    else f"{name} is undefined on the scored days (no alarm or no event)"
                )
            else:
                ordered = sorted(draws[(label, name)])
                cell["interval"] = {
                    "lower": _quantile(ordered, tail),
                    "upper": _quantile(ordered, 1.0 - tail),
                    "level": declaration.level,
                    "method": "stationary_bootstrap",
                    "block_length": declaration.block_length,
                    "replications": declaration.replications,
                    "seed": seed,
                }
            entry[name] = cell
        out[label] = entry
    return out


def _quantile(ordered: Sequence[float], probability: float) -> float:
    position = probability * (len(ordered) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def _excludes_zero_above(cell: Mapping[str, Any]) -> bool:
    interval = cell.get("interval")
    return bool(interval) and interval["lower"] > 0.0


# --------------------------------------------------------------------------
# The judge
# --------------------------------------------------------------------------


def _group_cells(grid: Grid, dimension: str) -> Dict[str, List[int]]:
    cells: Dict[str, List[int]] = {}
    for position, label in enumerate(grid.groups[dimension]):
        cells.setdefault(str(label), []).append(position)
    return dict(sorted(cells.items()))


def _vectors(
    probabilities: Sequence[float],
    reference: Sequence[float],
    outcomes: Sequence[int],
    cutoff: float,
    flags: Sequence[int],
    weights: Sequence[float],
    members: Optional[Sequence[int]],
) -> List[List[float]]:
    count = len(outcomes)
    inside = [1.0] * count if members is None else [0.0] * count
    if members is not None:
        for position in members:
            inside[position] = 1.0
    return [
        inside,
        [inside[i] * ((reference[i] - outcomes[i]) ** 2 - (probabilities[i] - outcomes[i]) ** 2) for i in range(count)],
        [inside[i] * flags[i] for i in range(count)],
        [inside[i] * flags[i] * outcomes[i] for i in range(count)],
        [inside[i] * weights[i] for i in range(count)],
        [inside[i] * weights[i] * outcomes[i] for i in range(count)],
        [inside[i] * outcomes[i] for i in range(count)],
    ]


def _criteria(
    declaration: Declaration, flags_summary: Mapping[str, Any], clim: Optional[Mapping[str, Any]]
) -> dict:
    recall = flags_summary["recall"]
    ratio = flags_summary["false_alarms_per_true"]
    criteria = {
        "recall": recall is not None and recall >= declaration.recall_at_least,
        "false_alarms": (
            flags_summary["alarms"] > 0
            and ratio is not None
            and ratio <= declaration.false_alarms_per_true_at_most
        ),
        "beats_climatology_brier": clim is not None and _excludes_zero_above(clim["brier_difference"]),
        "beats_climatology_precision": clim is not None and _excludes_zero_above(clim["precision_difference"]),
    }
    criteria["passes"] = all(criteria.values())
    return criteria


def _holdout_cell(
    positions: Sequence[int],
    probabilities: Sequence[float],
    reference: Sequence[float],
    outcomes: Sequence[int],
    flags: Sequence[int],
) -> dict:
    if not positions:
        return {"days": 0}
    p = [probabilities[i] for i in positions]
    r = [reference[i] for i in positions]
    y = [outcomes[i] for i in positions]
    f = [flags[i] for i in positions]
    return {
        "days": len(positions),
        "events": sum(y),
        "flags": _flags_summary(f, y),
        "brier": sum((a - b) ** 2 for a, b in zip(p, y)) / len(y),
        "climatology_brier": sum((a - b) ** 2 for a, b in zip(r, y)) / len(y),
        "note": "descriptive: a window holds too few days for an interval",
    }


def judge(
    declaration: Declaration,
    grids: Mapping[int, Grid],
    forecasts: Sequence[Forecast],
    *,
    holdouts: Optional[Mapping[str, Tuple[date, date]]] = None,
) -> dict:
    """Apply the declared bar to every forecast and return the evidence.

    Raises:
        LookAheadError: if a scored day is in a locked lockbox tier or after
            the declared last scored day.
        ValueError: if a forecast's candidate, cut-off or grid is not as
            declared, a probability is outside [0, 1], or the declared
            climatology or persistence benchmark was not scored.
    """

    _check_grid(declaration, grids)
    by_name = _check_forecasts(declaration, grids, forecasts)
    holdouts = dict(holdouts or {})
    for name in sorted(by_name):
        for horizon in declaration.horizons:
            for tau in declaration.thresholds:
                declaration.cutoff(name, tau, horizon)

    result_candidates: Dict[str, dict] = {}
    for name in sorted(by_name, key=lambda n: (declaration.candidates[n]["role"] != "benchmark", n)):
        entry = declaration.candidates[name]
        per_horizon: Dict[str, dict] = {}
        flags_by: Dict[Tuple[int, float], List[int]] = {}
        for horizon in declaration.horizons:
            grid = grids[horizon]
            per_tau: Dict[str, dict] = {}
            for tau in declaration.thresholds:
                forecast = by_name[name][horizon].probabilities[tau]
                outcomes = grid.outcomes[tau]
                cutoff = declaration.cutoff(name, tau, horizon)
                flags = [1 if p >= cutoff else 0 for p in forecast]
                flags_by[(horizon, tau)] = flags
                per_tau[_key(tau)] = _row(
                    declaration, name, horizon, tau, grid, forecast, outcomes, cutoff, flags,
                    by_name, holdouts,
                )
            per_horizon[str(horizon)] = per_tau
        primary = _key(declaration.primary)
        by_horizon_pass = {
            str(h): bool(per_horizon[str(h)][primary]["bar"]["passes"]) for h in declaration.pass_horizons
        }
        result_candidates[name] = {
            "role": entry["role"],
            "features": entry["features"],
            "calibration": entry["calibration"],
            "horizons": per_horizon,
            "lead_time": _lead_time(declaration, grids, by_name[name], name),
            "verdict": {
                "threshold_bp": declaration.primary,
                "pass_horizons": list(declaration.pass_horizons),
                "by_horizon": by_horizon_pass,
                "passes": all(by_horizon_pass.values()),
                "passes_at_horizon_1": per_horizon["1"][primary]["bar"]["passes"] if "1" in per_horizon else None,
            },
        }

    first = grids[declaration.horizons[0]]
    return {
        "declaration": declaration.document(),
        "scored_window": {
            "first": first.dates[0].isoformat(),
            "last": first.dates[-1].isoformat(),
            "days_by_horizon": {str(h): len(grids[h].dates) for h in declaration.horizons},
        },
        "holdouts": {k: [v[0].isoformat(), v[1].isoformat()] for k, v in holdouts.items()},
        "candidates": result_candidates,
    }


def _row(
    declaration: Declaration,
    name: str,
    horizon: int,
    tau: float,
    grid: Grid,
    probabilities: Sequence[float],
    outcomes: Sequence[int],
    cutoff: float,
    flags: Sequence[int],
    by_name: Mapping[str, Mapping[int, Forecast]],
    holdouts: Mapping[str, Tuple[date, date]],
) -> dict:
    count = len(outcomes)
    summary = _flags_summary(flags, outcomes)
    row: Dict[str, Any] = {
        "days": count,
        "events": sum(outcomes),
        "base_rate": sum(outcomes) / count,
        "cutoff": cutoff,
        "flags": summary,
        **_decomposition(probabilities, outcomes),
        "reliability_steps": _reliability_steps(probabilities, outcomes),
        "auroc": auroc(probabilities, outcomes),
    }
    try:
        row["average_precision"] = average_precision(probabilities, outcomes)
    except MetricError as exc:
        row["average_precision_unavailable"] = str(exc)
    row["usefulness"] = usefulness(flags, outcomes, declaration.usefulness_preference)

    climatology_name = declaration.climatology
    clim_probabilities = by_name[climatology_name][horizon].probabilities[tau]
    paired: Dict[str, Any] = {}
    pooled_clim: Optional[dict] = None
    splits: Dict[str, Dict[str, dict]] = {}
    if name != climatology_name:
        weights = (
            matched_recall_weights(clim_probabilities, outcomes, summary["recall"])
            if summary["recall"] is not None and sum(outcomes) and summary["recall"] > 0.0
            else tuple([0.0] * count)
        )
        row["climatology_matched_recall"] = {
            "recall": summary["recall"],
            "reference": climatology_name,
            "method": (
                "the reference flags its highest probabilities until its recall equals the "
                "candidate's; tied probabilities are flagged in part"
            ),
        }
        cells: Dict[str, Sequence[Sequence[float]]] = {
            "pooled": _vectors(probabilities, clim_probabilities, outcomes, cutoff, flags, weights, None)
        }
        index: Dict[str, Tuple[str, str]] = {}
        if tau == declaration.primary:
            for dimension in declaration.groupings:
                for label, members in _group_cells(grid, dimension).items():
                    key = f"{dimension}\x00{label}"
                    cells[key] = _vectors(
                        probabilities, clim_probabilities, outcomes, cutoff, flags, weights, members
                    )
                    index[key] = (dimension, label)
        evidence = _paired_cells(
            declaration, cells, count, seed=_seed(declaration.seed, name, horizon, _key(tau), "climatology")
        )
        pooled_clim = evidence["pooled"]
        paired["vs_calendar_climatology"] = pooled_clim
        for key, (dimension, label) in index.items():
            splits.setdefault(dimension, {})[label] = _split_cell(declaration, evidence[key], outcomes, grid, dimension, label, flags)
    else:
        for dimension in declaration.groupings if tau == declaration.primary else ():
            for label, members in _group_cells(grid, dimension).items():
                member_outcomes = [outcomes[i] for i in members]
                member_flags = [flags[i] for i in members]
                splits.setdefault(dimension, {})[label] = {
                    "days": len(members),
                    "events": sum(member_outcomes),
                    "flags": _flags_summary(member_flags, member_outcomes),
                    "brier": sum((probabilities[i] - outcomes[i]) ** 2 for i in members) / len(members),
                }
    persistence = by_name[declaration.persistence][horizon].probabilities[tau]
    if name not in (declaration.persistence, climatology_name):
        weights = (
            matched_recall_weights(persistence, outcomes, summary["recall"])
            if summary["recall"] is not None and sum(outcomes) and summary["recall"] > 0.0
            else tuple([0.0] * count)
        )
        evidence = _paired_cells(
            declaration,
            {"pooled": _vectors(probabilities, persistence, outcomes, cutoff, flags, weights, None)},
            count,
            seed=_seed(declaration.seed, name, horizon, _key(tau), "persistence"),
        )
        paired["vs_persistence_logistic"] = evidence["pooled"]
        paired["vs_persistence_logistic"]["note"] = "reported beside the bar; the bar names calendar climatology"
    row["paired"] = paired
    if tau == declaration.primary:
        row["splits"] = splits
    row["bar"] = _criteria(declaration, summary, pooled_clim)
    if tau != declaration.primary:
        row["bar"]["note"] = "reported at this threshold, not the pass condition"
    held: Dict[str, dict] = {}
    for window, (first, last) in holdouts.items():
        positions = [k for k, day in enumerate(grid.dates) if first <= day <= last]
        held[window] = _holdout_cell(positions, probabilities, clim_probabilities, outcomes, flags)
    if holdouts:
        row["holdouts"] = held
    return row


def _split_cell(
    declaration: Declaration,
    evidence: Mapping[str, Any],
    outcomes: Sequence[int],
    grid: Grid,
    dimension: str,
    label: str,
    flags: Sequence[int],
) -> dict:
    cell = {
        "days": evidence["days"],
        "events": evidence["events"],
        "flags": {
            "recall": evidence["recall"],
            "precision": evidence["precision"],
        },
        "reference_precision": evidence["reference_precision"],
        "brier_difference": evidence["brier_difference"],
        "precision_difference": evidence["precision_difference"],
    }
    recall, precision = evidence["recall"], evidence["precision"]
    cell["bar"] = {
        "recall": recall is not None and recall >= declaration.recall_at_least,
        "false_alarms": precision is not None and precision >= 1.0 / (1.0 + declaration.false_alarms_per_true_at_most),
        "beats_climatology_brier": _excludes_zero_above(evidence["brier_difference"]),
        "beats_climatology_precision": _excludes_zero_above(evidence["precision_difference"]),
    }
    cell["bar"]["passes"] = all(cell["bar"].values())
    return cell


def _lead_time(
    declaration: Declaration, grids: Mapping[int, Grid], forecasts: Mapping[int, Forecast], name: str
) -> dict:
    """How many business days ahead each +5 bp onset was flagged at the declared cut-off.

    An onset's lead is the longest horizon whose forecast of that day reached
    that horizon's declared cut-off, and 0 when none did.
    """

    tau = declaration.primary
    onsets = grids[declaration.horizons[0]].onsets
    leads = []
    for day in onsets:
        flagged = []
        for horizon in declaration.horizons:
            grid = grids[horizon]
            if day not in grid.dates:
                flagged = None
                break
            position = grid.dates.index(day)
            if forecasts[horizon].probabilities[tau][position] >= declaration.cutoff(name, tau, horizon):
                flagged.append(horizon)
        if flagged is None:
            continue
        leads.append(max(flagged) if flagged else 0)
    return {
        "threshold_bp": tau,
        "onsets": len(leads),
        "flagged": sum(1 for lead in leads if lead > 0),
        "mean_lead_days": None if not leads else sum(leads) / len(leads),
    }


# --------------------------------------------------------------------------
# Producing the inputs
# --------------------------------------------------------------------------


def report_forecast(name: str, report: Any) -> Forecast:
    """A `baseline.ExceedanceBacktestReport` as a `Forecast`, at the report's own thresholds."""

    return Forecast(
        name=name,
        horizon=int(report.horizon),
        dates=tuple(report.scored_dates),
        probabilities={
            float(tau): tuple(curve[position] for curve in report.forecast)
            for position, tau in enumerate(report.taus)
        },
    )


def forecasts_from_horizon_document(document: Mapping[str, Any]) -> List[Forecast]:
    """The forecasts of a `scripts/pressure_model_v1.py horizon` file, one per model.

    Reads its `forecasts` block (`{model: {tau: {date: probability}}}`) at the
    file's `horizon`.
    """

    horizon = int(document["horizon"])
    out = []
    for name, columns in document["forecasts"].items():
        taus = sorted(columns, key=float)
        dates = tuple(date.fromisoformat(d) for d in sorted(columns[taus[0]]))
        out.append(
            Forecast(
                name=name,
                horizon=horizon,
                dates=dates,
                probabilities={
                    float(tau): tuple(columns[tau][d.isoformat()] for d in dates) for tau in taus
                },
            )
        )
    return out


def benchmark_forecasts(
    declaration: Declaration,
    rows: Sequence[Any],
    splits: Any,
    registry: Mapping[str, Any],
    *,
    horizon: int,
    decision_time: Any,
    minimum_history: int,
    refit_every: int,
) -> List[Forecast]:
    """The two benchmarks, scored by the judge itself on the shared fold grid.

    Calendar-type climatology and the persistence-logistic, each by
    `baseline.rolling_exceedance_backtest` through the declared last scored
    day, under the declaration's thresholds.
    """

    from .baseline import (
        calendar_climatology_exceedance,
        persistence_logistic_exceedance,
        rolling_exceedance_backtest,
    )

    runs = (
        (
            declaration.climatology,
            calendar_climatology_exceedance(splits, minimum_history=minimum_history),
            ("spread_bps", "days_to_month_end", "quarter_end", "tax_date"),
        ),
        (
            declaration.persistence,
            persistence_logistic_exceedance(minimum_history=minimum_history),
            ("spread_bps",),
        ),
    )
    out = []
    for name, predictor, features in runs:
        report = rolling_exceedance_backtest(
            rows,
            predictor=predictor,
            model_name=name,
            features=features,
            registry=registry,
            decision_time=decision_time,
            taus=declaration.thresholds,
            minimum_history=minimum_history,
            refit_every=refit_every,
            end=declaration.last_day,
            horizon=horizon,
        )
        out.append(report_forecast(name, report))
    return out


def build_grid(
    declaration: Declaration,
    horizon: int,
    rows: Sequence[Any],
    scored_dates: Sequence[date],
    splits: Any,
    *,
    scarcity_state: Mapping[date, Optional[float]],
    extra_groups: Optional[Mapping[str, Mapping[date, str]]] = None,
) -> Grid:
    """The shared grid at one horizon: outcomes and the declared groupings.

    The groupings are read from the day alone or as of its decision instant:
    the regime and the pressure-day type (`splits.reporting_day_type`, #278)
    from the calendar, and the reserve-scarcity state from `scarcity_state`,
    which `scarcity.pressure_days_by_state` reads at the forecast's decision.
    `extra_groups` supplies any grouping a later track declares (a policy
    period, say).
    """

    from .data import exceeds_bp
    from . import pressure

    by_date = {row.date: row for row in rows}
    missing = [day for day in scored_dates if day not in by_date]
    if missing:
        raise ValueError(f"scored day {missing[0]} is not a row of the panel")
    groups: Dict[str, List[str]] = {"regime": [], "day_type": [], "scarcity_state": []}
    for day in scored_dates:
        groups["regime"].append(splits.regime(day))
        groups["day_type"].append(splits.reporting_day_type(day, by_date[day].values))
        state = scarcity_state.get(day)
        groups["scarcity_state"].append("unknown" if state is None else str(int(state)))
    for dimension, labels in (extra_groups or {}).items():
        groups[dimension] = [str(labels[day]) for day in scored_dates]
    return Grid(
        horizon=horizon,
        dates=tuple(scored_dates),
        outcomes={
            tau: tuple(int(exceeds_bp(by_date[day].spread_bps, tau)) for day in scored_dates)
            for tau in declaration.thresholds
        },
        groups={dimension: tuple(labels) for dimension, labels in groups.items()},
        onsets=pressure.onsets(rows, declaration.primary, scored_dates),
    )
