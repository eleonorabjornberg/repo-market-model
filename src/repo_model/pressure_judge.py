"""The pressure-day judge (#375, track J of #374): one bar for every candidate.

Eleonora's ruling of 7 October 2026 on #375 ("the success bar is replaced") sets
the bar a pressure probability must clear, on days up to 2025-12-31:

* A *pressure day* is SOFR - IORB > +5 bp. An *onset* is a pressure day with no
  pressure day on the five panel days before it (`pressure.onsets`, the same
  quiet-days rule as `onset.leap_onset_group`, read on the spread itself rather
  than on the leap target). A *flag* is a probability at or above the candidate's
  declared cut-off. An onset has *lead* h when it was flagged at horizon h, from
  a decision instant h business days before it.
* **Tier 1, onset warning.** At lead >= 1 (flagged at some horizon h >= 1) at
  least 50% of onsets, with the lower end of the bootstrap 90% interval on that
  recall above climatology's recall at the same false-alarm rate; at most 2 false
  alarms per onset. At lead >= 3, at least 30% of onsets (reported only).
* **Tier 2, risky dates.** On scheduled risk dates in scarcity state >= 2, at
  lead 5: AUROC >= 0.75 and above calendar-type climatology, paired, with an
  interval (reported only).
* **Tier 3, no crying wolf.** In abundant-reserve stretches (scarcity state 0,
  and the 2021-23 regime) at most 21 flags per 252 business days, at each lead 1
  to 5; and calibration by regime (CORP reliability; predicted frequency within
  the interval of the realised one), tested only in regimes with at least one
  pressure day (+5 bp) in the scored window and reported in the others.
* **Tier 4, continuation.** Brier at +5 bp against the persistence-logistic,
  paired, at each lead 1 to 5 (reported only). +10 bp is reported only.
* **Tier 5, week-ahead window.** P(at least one pressure day in the next 5
  business days), forecast each day: calibrated and better than climatology on
  Brier, paired, with a 90% interval excluding zero.
* **Pass rule.** Tier 1 at lead >= 1, tier 3 at every lead, and tier 5, all on
  2018-06-29 to 2025-12-31. Beside it, for every row, the same three tiers on the
  scarce regime's days alone (scarcity state >= the tier 2 state): reported, not
  part of the rule. **Confirmation:** one look at 2026-01-01 to
  2026-09-03 for a candidate named in the declaration's `confirmation.candidates`
  before the look; the judge refuses that window otherwise (`require_scored_days`).

This module applies that bar to walk-forward probabilities. It fits nothing: a
candidate is a `Forecast` (its probability for each scored day, at each
threshold and horizon) produced elsewhere, and `benchmark_forecasts` produces
the two benchmarks the same way every candidate is produced.

**The declaration is files the judge reads** (`metadata/pressure_judge.json` and
`metadata/pressure_judge/candidates/<name>.json`): the thresholds, the horizons, the
rule that chooses the flag cut-off, the tier limits and the pass rule in the first;
each candidate, its role, features and calibration step, in a file of its own, so
that two pull requests that each add a candidate touch different files. All are
committed before any score is computed. Every result carries the digest of them all.

**The flag cut-off** (ruling of 8 October 2026, #407, replacing the fixed 0.2
placeholder). It is not declared per candidate: the declared `cutoff_rule` chooses it,
for every candidate and benchmark alike, at each refit and horizon, from that refit's
training window alone. `select_cutoff` takes the cut-off with the highest onset recall
whose false alarms per onset on the window are at most the limit (2); `choose_cutoffs`
applies it block by block, the window of a block being the forecast's own earlier
walk-forward probabilities on the days whose outcome was known at the block's first
decision instant. A window with no onset, or with no cut-off within the limit that
flags an onset, flags nothing. No scored day is read: `select_cutoff` raises
`LookAheadError` for a window that reaches past the refit's training end, and the
judge refuses cut-offs that did not come from `choose_cutoffs` under this declaration.

**The scored days.** `require_scored_days` refuses a day in a lockbox tier that
has not been opened (`docs/decisions/lockbox.md`), and a day outside the window
being scored: development scores days up to the declared last scored day, and a
confirmation look scores the declared confirmation window and nothing else. All
are `LookAheadError`, raised before any score is computed.

**"At the same false-alarm rate."** The reference's recall is read where its own
ranking has raised as many false alarms (flags on days that are not pressure
days) as the candidate: it flags its highest probabilities until the count is
reached, and a group of tied probabilities is flagged in part
(`matched_false_alarm_weights`), the expected recall of breaking the tie at
random. The weights are fixed from the scored days and held across bootstrap
resamples.

**The week-ahead probability.** At decision day t, the horizon-k forecasts of
t+1 ... t+5 (`Declaration.week_combine`: independent, `1 - prod(1 - p_k)`, or
their maximum) are combined into P(at least one pressure day in t+1 ... t+5); the
outcome is whether any of those days is one. It is derived from the same
horizons for the candidate and for climatology.

**The intervals** are stationary bootstrap, at the declared level, block length,
replications and seed; the day is resampled whole, so the pairing holds. A
statistic undefined on any resample (no alarm drawn, say) has no interval, and
the criterion that needs it is not met: the replicates are never dropped
(`metrics.stationary_bootstrap_interval`'s rule).

Reported beside the tiers: Brier with its CORP decomposition and reliability
steps, AUROC, average precision, usefulness (Alessi & Detken, 2011; Sarlin) at
the declared cut-off, and the Brier, calibration and flags by every declared
grouping (regime, reserve-scarcity state of #115, pressure-day type, and any
grouping a later track declares) and on the knowledge-holdout windows.

Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import random
from dataclasses import dataclass
from datetime import date
from operator import itemgetter
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

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
    "WeightedMiss",
    "auroc",
    "benchmark_forecasts",
    "build_grid",
    "choose_cutoffs",
    "cooldown_flags",
    "false_alarm_weights",
    "forecasts_from_horizon_document",
    "judge",
    "load_declaration",
    "load_weighted_miss",
    "matched_false_alarm_weights",
    "miss_weight",
    "report_forecast",
    "restrict_forecast",
    "require_scored_days",
    "select_cutoff",
    "usefulness",
]

DEFAULT_DECLARATION = Path(__file__).parents[2] / "metadata" / "pressure_judge.json"
DEFAULT_WEIGHTED_MISS = Path(__file__).parents[2] / "metadata" / "weighted_miss.json"


def candidates_directory(path: Path = DEFAULT_DECLARATION) -> Path:
    """Where the declaration at `path` keeps its candidates: one `<name>.json` file each, in `<stem>/candidates/`."""

    path = Path(path)
    return path.with_suffix("") / "candidates"


def declaration_files(path: Path = DEFAULT_DECLARATION) -> List[Path]:
    """Every file the declaration is read from: the declaration itself, then each candidate's file by name."""

    directory = candidates_directory(path)
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    return [Path(path), *files]

_ROLES = ("benchmark", "baseline", "candidate")
_COMBINERS = ("independence", "max")
#: The groupings the tiers read, whatever else is declared for reporting.
_TIER_GROUPS = ("regime", "scarcity_state", "risk_date")


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
    confirmation_first: date
    confirmation_last: date
    confirmation_candidates: Tuple[str, ...]
    thresholds: Tuple[float, ...]
    primary: float
    horizons: Tuple[int, ...]
    level: float
    replications: int
    block_length: int
    seed: int
    cutoff_false_alarms_at_most: float
    cutoff_refit_every: int
    onset_lead: int
    onset_recall_at_least: float
    onset_false_alarms_at_most: float
    far_lead: int
    far_recall_at_least: float
    risky_state_at_least: int
    risky_lead: int
    risky_auroc_at_least: float
    abundant_state: str
    abundant_regime: str
    flags_per_year_at_most: float
    business_days_per_year: int
    week_days: int
    week_combine: str
    usefulness_preference: float
    groupings: Tuple[str, ...]
    climatology: str
    persistence: str
    candidates: Mapping[str, Mapping[str, Any]]
    weighted_miss: Optional["WeightedMiss"] = None

    @property
    def weighting_applied(self) -> bool:
        """Whether false alarms are weighted by their distance to a pressure day (#454); by default they are not."""

        return self.weighted_miss is not None and self.weighted_miss.applied

    def document(self) -> dict:
        """What a result carries about the declaration it was judged under."""

        document = self._document()
        if self.weighted_miss is not None:
            document["weighted_miss"] = self.weighted_miss.document()
        return document

    def _document(self) -> dict:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "status": self.status,
            "last_scored_day": self.last_day.isoformat(),
            "confirmation": {
                "first": self.confirmation_first.isoformat(),
                "last": self.confirmation_last.isoformat(),
                "candidates": list(self.confirmation_candidates),
            },
            "cutoff_rule": {
                "false_alarms_per_onset_at_most": self.cutoff_false_alarms_at_most,
                "refit_every": self.cutoff_refit_every,
                "no_onsets": "never_flag",
                "none_meets_limit": "never_flag",
            },
            "thresholds_bp": list(self.thresholds),
            "primary_threshold_bp": self.primary,
            "horizons": list(self.horizons),
            "bootstrap": {
                "level": self.level,
                "replications": self.replications,
                "block_length": self.block_length,
                "seed": self.seed,
            },
            "tiers": {
                "onset_warning": {
                    "lead_at_least": self.onset_lead,
                    "recall_at_least": self.onset_recall_at_least,
                    "false_alarms_per_onset_at_most": self.onset_false_alarms_at_most,
                    "far_lead_at_least": self.far_lead,
                    "far_recall_at_least": self.far_recall_at_least,
                },
                "risky_dates": {
                    "scarcity_state_at_least": self.risky_state_at_least,
                    "lead": self.risky_lead,
                    "auroc_at_least": self.risky_auroc_at_least,
                },
                "no_crying_wolf": {
                    "abundant_scarcity_state": self.abundant_state,
                    "abundant_regime": self.abundant_regime,
                    "flags_per_year_at_most": self.flags_per_year_at_most,
                    "business_days_per_year": self.business_days_per_year,
                },
                "week_ahead": {"days": self.week_days, "combine": self.week_combine},
            },
            "usefulness_preference": self.usefulness_preference,
            "groupings": list(self.groupings),
            "climatology": self.climatology,
            "persistence": self.persistence,
            "candidates": {
                name: {key: entry[key] for key in ("role", "features", "calibration", "alarm_rule") if key in entry}
                for name, entry in self.candidates.items()
            },
        }


@dataclass(frozen=True)
class WeightedMiss:
    """`metadata/weighted_miss.json`: how much a false alarm counts, by its distance to a pressure day (#454).

    A flag on a day that is not a pressure day is a false alarm of weight `w(d)`, `d` the trading days to the
    nearest pressure day. `bands` is `(distance_at_most, weight)` in ascending distance; a distance past the last
    band, or no pressure day in reach, weighs `beyond`. `in_force` is the declared switch: false until Eleonora
    merges `docs/decisions/weighted-miss.md` and attests the adoption (#256). `applied` is what a run does: the
    judge counts the weighted false alarms only when it is true, and defaults to `in_force`.
    """

    path: str
    sha256: str
    in_force: bool
    applied: bool
    bands: Tuple[Tuple[int, float], ...]
    beyond: float

    def document(self) -> dict:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "in_force": self.in_force,
            "applied": self.applied,
            "weights": [{"distance_at_most": d, "weight": w} for d, w in self.bands],
            "beyond": self.beyond,
        }


def _weight(value: object, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 < value <= 1.0:
        raise ValueError(f"{where} must be a number above 0 and at most 1, got {value!r}")
    return float(value)


def load_weighted_miss(path: Path = DEFAULT_WEIGHTED_MISS, *, applied: Optional[bool] = None) -> WeightedMiss:
    """Read and check the weighted miss rule. `applied` overrides the declared switch for one run.

    Raises:
        ValueError: on a missing or malformed file, a switch that is not a boolean, bands that are not in
            ascending distance, or a weight outside (0, 1].
    """

    raw = Path(path).read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} is not JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{path} must hold an object")
    in_force = document.get("in_force")
    if not isinstance(in_force, bool):
        raise ValueError(f"{path}: in_force must be true or false")
    entries = document.get("weights")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path}: weights must be a non-empty list")
    bands: List[Tuple[int, float]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: each weight must be an object")
        distance = _integer(entry.get("distance_at_most"), "weights.distance_at_most")
        weight = _weight(entry.get("weight"), "weights.weight")
        if bands and distance <= bands[-1][0]:
            raise ValueError(f"{path}: weights must be in ascending distance_at_most")
        bands.append((distance, weight))
    beyond = _weight(document.get("beyond"), "beyond")
    return WeightedMiss(
        path=_display(Path(path)),
        sha256=hashlib.sha256(raw).hexdigest(),
        in_force=in_force,
        applied=in_force if applied is None else bool(applied),
        bands=tuple(bands),
        beyond=beyond,
    )


def miss_weight(rule: WeightedMiss, distance: Optional[int]) -> float:
    """The weight of a false alarm `distance` trading days from the nearest pressure day (None: none in reach).

    Raises:
        ValueError: if `distance` is below 1 (a pressure day is not a false alarm).
    """

    if distance is None:
        return rule.beyond
    if distance < 1:
        raise ValueError(f"a false alarm is at least 1 trading day from a pressure day, got {distance}")
    for limit, weight in rule.bands:
        if distance <= limit:
            return weight
    return rule.beyond


def false_alarm_weights(
    rule: WeightedMiss,
    *,
    positions: Sequence[int],
    pressure: Sequence[int],
    known_through: int,
) -> Tuple[float, ...]:
    """The weight of a false alarm on each day: 0 on a pressure day, else `miss_weight` of its distance.

    `positions[k]` is the panel position of day k, ascending. The distance is read on the days given alone, so a
    pressure day that was not yet known cannot lower a weight: `known_through` is the last panel position whose
    outcome was known (inside the cut-off rule's training window, the refit's training end).

    Raises:
        LookAheadError: if a day is after `known_through`.
        ValueError: if the series differ in length or positions are not ascending.
    """

    if len(positions) != len(pressure):
        raise ValueError("the weights need one pressure flag per day")
    if any(b <= a for a, b in zip(positions, positions[1:])):
        raise ValueError("positions must be ascending")
    late = [p for p in positions if p > known_through]
    if late:
        raise LookAheadError(
            f"{len(late)} day(s) from position {min(late)} on are after position {known_through}, the last whose "
            f"outcome was known; a false alarm's weight reads the pressure days known by then only"
        )
    pressure_positions = [p for p, y in zip(positions, pressure) if y]
    out = []
    for position, y in zip(positions, pressure):
        if y:
            out.append(0.0)
            continue
        near = None
        if pressure_positions:
            k = bisect.bisect_left(pressure_positions, position)
            gaps = []
            if k > 0:
                gaps.append(position - pressure_positions[k - 1])
            if k < len(pressure_positions):
                gaps.append(pressure_positions[k] - position)
            near = min(gaps)
        out.append(miss_weight(rule, near))
    return tuple(out)


def _display(path: Path) -> str:
    """The declaration's path as a result names it: relative to the repository when inside it."""

    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(Path(__file__).parents[2]))
    except ValueError:
        return str(path)


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


def _day(value: object, where: str) -> date:
    try:
        return date.fromisoformat(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{where} must be an ISO date, got {value!r}") from exc


def _section(document: Mapping[str, Any], *path: str) -> Mapping[str, Any]:
    node: Any = document
    for step in path:
        node = node.get(step) if isinstance(node, Mapping) else None
        if not isinstance(node, Mapping):
            raise ValueError(f"the declaration lacks {'.'.join(path)!r}")
    return node


def load_declaration(path: Path = DEFAULT_DECLARATION) -> Declaration:
    """Read and check the judge's declaration.

    Raises:
        ValueError: on a missing or malformed file, a cut-off that is not a
            probability strictly between 0 and 1, a candidate without a
            cut-off at every threshold and horizon, a benchmark that is not a
            declared candidate, a confirmation window that overlaps the scored
            days or names an undeclared candidate, or horizons that do not
            cover the week-ahead window.
    """

    raw = Path(path).read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} is not JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{path} must hold an object")
    for key in (
        "status", "scoring", "confirmation", "thresholds_bp", "primary_threshold_bp",
        "horizons", "bootstrap", "cutoff_rule", "tiers", "early_warning", "groupings", "benchmarks",
    ):
        if key not in document:
            raise ValueError(f"{path} declares no {key!r}")
    if "candidates" in document:
        raise ValueError(
            f"{path} declares 'candidates'; each candidate is a file of its own in "
            f"{candidates_directory(path)}, never an entry in this file"
        )
    last_day = _day(document["scoring"].get("last_day"), "scoring.last_day")
    confirmation = document["confirmation"]
    confirmation_first = _day(confirmation.get("first"), "confirmation.first")
    confirmation_last = _day(confirmation.get("last"), "confirmation.last")
    if not last_day < confirmation_first <= confirmation_last:
        raise ValueError(
            f"{path}: the confirmation window must follow the last scored day "
            f"({last_day}) and not be empty"
        )
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
    bootstrap = document["bootstrap"]
    rule = _section(document, "cutoff_rule")
    for key in ("no_onsets", "none_meets_limit"):
        if rule.get(key) != "never_flag":
            raise ValueError(
                f"{path}: cutoff_rule.{key} must be 'never_flag' (the only rule the judge applies), "
                f"got {rule.get(key)!r}"
            )
    onset = _section(document, "tiers", "onset_warning")
    risky = _section(document, "tiers", "risky_dates")
    wolf = _section(document, "tiers", "no_crying_wolf")
    week = _section(document, "tiers", "week_ahead")
    onset_lead = _integer(onset.get("lead_at_least"), "onset_warning.lead_at_least")
    far_lead = _integer(onset.get("far_lead_at_least"), "onset_warning.far_lead_at_least")
    risky_lead = _integer(risky.get("lead"), "risky_dates.lead")
    week_days = _integer(week.get("days"), "week_ahead.days")
    combine = week.get("combine")
    if combine not in _COMBINERS:
        raise ValueError(f"{path}: week_ahead.combine must be one of {list(_COMBINERS)}, got {combine!r}")
    for lead, where in ((onset_lead, "onset_warning.lead_at_least"), (far_lead, "onset_warning.far_lead_at_least"), (risky_lead, "risky_dates.lead")):
        if lead not in horizons:
            raise ValueError(f"{path}: {where} = {lead} is not one of the horizons {list(horizons)}")
    if not set(range(1, week_days + 1)) <= set(horizons):
        raise ValueError(
            f"{path}: the week-ahead window of {week_days} days needs horizons 1 to {week_days}, "
            f"got {list(horizons)}"
        )
    groupings = tuple(document["groupings"])
    if not groupings or any(not isinstance(g, str) or not g for g in groupings):
        raise ValueError(f"{path}: groupings must be non-empty names")

    files = declaration_files(path)[1:]
    if not files:
        raise ValueError(f"{path}: no candidate files in {candidates_directory(path)}")
    digest = hashlib.sha256(raw)
    candidates: Dict[str, Dict[str, Any]] = {}
    for file in files:
        name = file.stem
        candidate_raw = file.read_bytes()
        digest.update(name.encode("utf-8") + b"\0" + candidate_raw)
        try:
            entry = json.loads(candidate_raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{file} is not JSON: {exc}") from exc
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: candidate {name!r} must be an object")
        if entry.get("role") not in _ROLES:
            raise ValueError(f"{path}: candidate {name!r} needs a role in {list(_ROLES)}")
        for key in ("features", "calibration"):
            if key not in entry:
                raise ValueError(f"{path}: candidate {name!r} declares no {key!r}")
        if "alarm_rule" in entry:
            _check_alarm_rule(path, name, entry["alarm_rule"])
        if "cutoffs" in entry:
            raise ValueError(
                f"{path}: candidate {name!r} declares a fixed 'cutoffs'; a flag cut-off is chosen from "
                f"each refit's training window by the declared 'cutoff_rule', never declared per candidate"
            )
        candidates[name] = entry

    look = tuple(confirmation.get("candidates", ()))
    for name in look:
        if name not in candidates or candidates[name]["role"] != "candidate":
            raise ValueError(f"{path}: confirmation.candidates names {name!r}, which is not a declared candidate")

    pair = document["benchmarks"]
    climatology, persistence = pair.get("climatology"), pair.get("persistence")
    for label, name in (("climatology", climatology), ("persistence", persistence)):
        if name not in candidates:
            raise ValueError(f"{path}: benchmarks.{label} {name!r} is not a declared candidate")

    return Declaration(
        path=_display(path),
        sha256=digest.hexdigest(),
        status=str(document["status"]),
        last_day=last_day,
        confirmation_first=confirmation_first,
        confirmation_last=confirmation_last,
        confirmation_candidates=look,
        thresholds=thresholds,
        primary=primary,
        horizons=horizons,
        level=_number(bootstrap.get("level"), "bootstrap.level", 0.0, 1.0, open_ends=True),
        replications=_integer(bootstrap.get("replications"), "bootstrap.replications", 2),
        block_length=_integer(bootstrap.get("block_length"), "bootstrap.block_length"),
        seed=_integer(bootstrap.get("seed"), "bootstrap.seed", 0),
        cutoff_false_alarms_at_most=_number(
            rule.get("false_alarms_per_onset_at_most"), "cutoff_rule.false_alarms_per_onset_at_most", 0.0, 1000.0
        ),
        cutoff_refit_every=_integer(rule.get("refit_every"), "cutoff_rule.refit_every"),
        onset_lead=onset_lead,
        onset_recall_at_least=_number(onset.get("recall_at_least"), "onset_warning.recall_at_least", 0.0, 1.0),
        onset_false_alarms_at_most=_number(
            onset.get("false_alarms_per_onset_at_most"), "onset_warning.false_alarms_per_onset_at_most", 0.0, 1000.0
        ),
        far_lead=far_lead,
        far_recall_at_least=_number(onset.get("far_recall_at_least"), "onset_warning.far_recall_at_least", 0.0, 1.0),
        risky_state_at_least=_integer(risky.get("scarcity_state_at_least"), "risky_dates.scarcity_state_at_least", 0),
        risky_lead=risky_lead,
        risky_auroc_at_least=_number(risky.get("auroc_at_least"), "risky_dates.auroc_at_least", 0.0, 1.0),
        abundant_state=str(_integer(wolf.get("abundant_scarcity_state"), "no_crying_wolf.abundant_scarcity_state", 0)),
        abundant_regime=str(wolf.get("abundant_regime")),
        flags_per_year_at_most=_number(wolf.get("flags_per_year_at_most"), "no_crying_wolf.flags_per_year_at_most", 0.0, 1000.0),
        business_days_per_year=_integer(wolf.get("business_days_per_year"), "no_crying_wolf.business_days_per_year"),
        week_days=week_days,
        week_combine=combine,
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
    decision instant. `onset[k]` is 1 when day k is a +5 bp onset
    (`pressure.onsets`).
    """

    horizon: int
    dates: Tuple[date, ...]
    outcomes: Mapping[float, Tuple[int, ...]]
    groups: Mapping[str, Tuple[str, ...]]
    onset: Tuple[int, ...]
    onsets: Optional[Mapping[float, Tuple[int, ...]]] = None

    def onset_at(self, tau: float, primary: float) -> Tuple[int, ...]:
        """The 0/1 onset flag per day at `tau`: `onset` at the primary threshold, else `onsets[tau]`."""

        if tau == primary:
            return self.onset
        if self.onsets is None or tau not in self.onsets:
            raise ValueError(f"grid h = {self.horizon}: no onset flags at {_key(tau)} bp")
        return tuple(self.onsets[tau])


@dataclass(frozen=True)
class Forecast:
    """One candidate's walk-forward probabilities at one horizon.

    `cutoffs[tau][k]` is the flag cut-off in force on scored day k (`math.inf`:
    the refit's rule flags nothing). It is set by `choose_cutoffs` and by nothing
    else: `cutoff_rule` is the digest of the declaration it was chosen under, and `cutoff_weighting` the digest of
    the weighted miss rule it counted false alarms by (#454), None when it counted every false alarm as 1.
    """

    name: str
    horizon: int
    dates: Tuple[date, ...]
    probabilities: Mapping[float, Tuple[float, ...]]
    cutoffs: Optional[Mapping[float, Tuple[float, ...]]] = None
    cutoff_rule: Optional[str] = None
    cutoff_weighting: Optional[str] = None


def require_scored_days(
    declaration: Declaration,
    days: Sequence[date],
    *,
    where: str,
    confirmation: bool = False,
) -> None:
    """Refuse a day the comparison may not score.

    Development (`confirmation=False`) scores days up to the declared last
    scored day. The single confirmation look scores the declared confirmation
    window and nothing else, so a look that also re-scores a development day, or
    runs past the window, is refused.

    Raises:
        LookAheadError: for a day in a lockbox tier that has not been opened,
            after the last scored day in development, or outside the
            confirmation window in a look. All are checked before any score is
            computed.
    """

    lockbox.require_unlocked(days, where=where)
    for day in sorted(days):
        if confirmation:
            if not declaration.confirmation_first <= day <= declaration.confirmation_last:
                raise LookAheadError(
                    f"{where}: scored day {day} is outside the declared confirmation window "
                    f"{declaration.confirmation_first} to {declaration.confirmation_last} "
                    f"({declaration.path}); the single look scores that window only"
                )
        elif day > declaration.last_day:
            raise LookAheadError(
                f"{where}: scored day {day} is after the declared last scored day "
                f"{declaration.last_day} ({declaration.path}); development scores days before "
                f"2026-01-01 only, and the confirmation look is a separate, declared run"
            )


def _check_grid(
    declaration: Declaration, grids: Mapping[int, Grid], *, confirmation: bool
) -> None:
    if sorted(grids) != list(declaration.horizons):
        raise ValueError(
            f"the grids cover horizons {sorted(grids)}; the declaration judges "
            f"{list(declaration.horizons)}"
        )
    for horizon, grid in grids.items():
        if grid.horizon != horizon:
            raise ValueError(f"grid keyed {horizon} says horizon {grid.horizon}")
        require_scored_days(
            declaration, grid.dates, where=f"pressure_judge.judge (h = {horizon})", confirmation=confirmation
        )
        count = len(grid.dates)
        if count == 0 or list(grid.dates) != sorted(set(grid.dates)):
            raise ValueError(f"grid h = {horizon}: the scored days must be non-empty, ascending and distinct")
        if len(grid.onset) != count or any(o not in (0, 1) for o in grid.onset):
            raise ValueError(f"grid h = {horizon}: needs a 0/1 onset flag per day")
        for tau in declaration.thresholds:
            outcomes = grid.outcomes.get(tau)
            if outcomes is None or len(outcomes) != count or any(y not in (0, 1) for y in outcomes):
                raise ValueError(f"grid h = {horizon}: needs a 0/1 outcome per day at {_key(tau)} bp")
        absent = sorted((set(declaration.groupings) | set(_TIER_GROUPS)) - set(grid.groups))
        if absent:
            raise ValueError(f"grid h = {horizon} lacks the declared groupings {absent}")
        for dimension in grid.groups:
            if len(grid.groups[dimension]) != count:
                raise ValueError(f"grid h = {horizon}: grouping {dimension!r} is not one label per day")


def _check_forecasts(
    declaration: Declaration,
    grids: Mapping[int, Grid],
    forecasts: Sequence[Forecast],
    *,
    confirmation: bool,
) -> Dict[str, Dict[int, Forecast]]:
    by_name: Dict[str, Dict[int, Forecast]] = {}
    for forecast in forecasts:
        if forecast.name not in declaration.candidates:
            raise ValueError(
                f"{forecast.name!r} is not declared in {declaration.path}; "
                f"every candidate is declared before it is scored"
            )
        if confirmation and (
            declaration.candidates[forecast.name]["role"] == "candidate"
            and forecast.name not in declaration.confirmation_candidates
        ):
            raise ValueError(
                f"{forecast.name!r} is not in confirmation.candidates of {declaration.path}; "
                f"the single look is for the winner or a list fixed before the look"
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
        if forecast.cutoffs is not None:
            if forecast.cutoff_rule != declaration.sha256:
                raise ValueError(
                    f"{forecast.name!r} h = {forecast.horizon}: its cut-offs were not chosen under "
                    f"{declaration.path} (digest {declaration.sha256[:12]}); the judge scores cut-offs "
                    f"chosen by `choose_cutoffs` from training data under the declared rule only"
                )
            expected = declaration.weighted_miss.sha256 if declaration.weighting_applied else None
            if forecast.cutoff_weighting != expected:
                raise ValueError(
                    f"{forecast.name!r} h = {forecast.horizon}: its cut-offs counted false alarms "
                    f"{'by the weights of ' + forecast.cutoff_weighting[:12] if forecast.cutoff_weighting else 'flat'}"
                    f", but this run counts them "
                    f"{'by the weights of ' + expected[:12] if expected else 'flat'}; choose them again"
                )
            for tau in declaration.thresholds:
                column = forecast.cutoffs.get(tau)
                if column is None or len(column) != len(grid.dates):
                    raise ValueError(f"{forecast.name!r} h = {forecast.horizon}: no cut-off column at {_key(tau)} bp")
        by_name[forecast.name][forecast.horizon] = forecast
    for name, per_horizon in by_name.items():
        missing = [h for h in declaration.horizons if h not in per_horizon]
        # The published baseline is a scored run of its own (hours at each
        # horizon); it may cover fewer horizons, and the result says which.
        if missing and declaration.candidates[name]["role"] != "baseline":
            raise ValueError(f"{name!r} has no forecasts at horizons {missing}")
    for label, name in (("climatology", declaration.climatology), ("persistence", declaration.persistence)):
        if name not in by_name:
            raise ValueError(
                f"the declared {label} benchmark {name!r} was not scored; the judge pairs every "
                f"candidate against it"
            )
    return by_name


# --------------------------------------------------------------------------
# The flag cut-off, chosen from training data only
# --------------------------------------------------------------------------


def _check_alarm_rule(path: Path, name: str, rule: object) -> None:
    """A candidate's `alarm_rule` (#459): a cool-down on its flags, declared in its file."""

    if (
        not isinstance(rule, dict)
        or rule.get("kind") != "cooldown"
        or not isinstance(rule.get("base"), str)
        or not rule["base"]
        or not isinstance(rule.get("keep_when_pressure_starts"), bool)
        or set(rule) != {"kind", "base", "trading_days", "keep_when_pressure_starts"}
    ):
        raise ValueError(
            f"{path}: candidate {name!r} alarm_rule must be exactly "
            f"{{kind: 'cooldown', base, trading_days, keep_when_pressure_starts}}"
        )
    _integer(rule.get("trading_days"), f"candidate {name!r} alarm_rule.trading_days")


def cooldown_flags(
    flags: Sequence[int],
    onset: Sequence[int],
    trading_days: int,
    *,
    keep_when_pressure_starts: bool = True,
) -> List[int]:
    """The flags with repeats inside a cool-down counted as the alarm they repeat (#459).

    A flag outside every earlier alarm's window raises an alarm. The window is the `trading_days` days after
    it. A flag inside the window is a repeat and is dropped, so the burst counts once, unless
    `keep_when_pressure_starts` and a pressure day starts (`onset`) inside the window: then the repeats stay,
    each its own flag. A repeat never opens a window of its own. The series is one candidate's flags at one
    horizon in day order; `onset[k]` is 1 when a pressure day starts on day k.

    The exception reads the days after the flag, so it is a rule for counting alarms on a scored record, not
    for a live forecaster; `keep_when_pressure_starts=False` is the rule a forecaster could apply as it goes.

    Raises:
        ValueError: if the series differ in length or `trading_days` is below 1.
    """

    if len(flags) != len(onset):
        raise ValueError("the cool-down needs one onset flag per day")
    if trading_days < 1:
        raise ValueError("the cool-down is at least one trading day")
    out = [0] * len(flags)
    anchor = None
    for k, flag in enumerate(flags):
        if not flag:
            continue
        if anchor is None or k > anchor + trading_days:
            anchor = k
            out[k] = 1
        elif keep_when_pressure_starts and any(onset[anchor + 1 : anchor + trading_days + 1]):
            out[k] = 1
    return out


def _alarm_flags(declaration: "Declaration", name: str, flags: Sequence[int], onset: Sequence[int]) -> List[int]:
    """`flags`, cooled down when the candidate declares an `alarm_rule`, else unchanged."""

    rule = declaration.candidates[name].get("alarm_rule")
    if rule is None:
        return list(flags)
    return cooldown_flags(
        flags, onset, rule["trading_days"], keep_when_pressure_starts=rule["keep_when_pressure_starts"]
    )


def select_cutoff(
    declaration: Declaration,
    *,
    days: Sequence[date],
    probabilities: Sequence[float],
    pressure: Sequence[int],
    onset: Sequence[int],
    training_end: Optional[date],
    false_alarm_weights: Optional[Sequence[float]] = None,
) -> float:
    """The flag cut-off for one refit, chosen on its training window alone.

    The cut-off with the highest onset recall whose false alarms per onset on
    the window are at most the declared limit (`cutoff_rule`). A false alarm is
    a flag on a day that is not a pressure day, counted per onset of the window,
    as tier 1 counts it. Candidate cut-offs are the window's own probabilities;
    of cut-offs with the same recall the highest wins. A window with no onset, or
    in which no cut-off within the limit flags an onset, flags nothing: the
    cut-off is `math.inf`, as the declared rule says.

    With `false_alarm_weights` (one per day, from the weighted miss rule, #454) a false alarm counts its weight
    instead of 1; the limit stays the declared one.

    Raises:
        LookAheadError: if a day of the window is after `training_end`, the last
            day whose outcome the refit could read, or the window has a day and
            no training end.
        ValueError: if the series differ in length.
    """

    if not len(days) == len(probabilities) == len(pressure) == len(onset):
        raise ValueError("the cut-off window needs one probability, outcome and onset flag per day")
    if false_alarm_weights is not None and len(false_alarm_weights) != len(days):
        raise ValueError("the cut-off window needs one false-alarm weight per day")
    if days:
        late = [day for day in days if training_end is None or day > training_end]
        if late:
            raise LookAheadError(
                f"cut-off chosen from {len(late)} day(s) from {min(late)} on, after the refit's "
                f"training end ({training_end}); a flag cut-off is chosen on training data only"
            )
    onsets = sum(onset)
    if not onsets:
        return math.inf
    by_value: Dict[float, List[int]] = {}
    for index, p in enumerate(probabilities):
        by_value.setdefault(p, []).append(index)
    caught, false_alarms = 0, 0
    best_recall, best = 0, math.inf
    for value in sorted(by_value, reverse=True):
        for index in by_value[value]:
            if onset[index]:
                caught += 1
            elif not pressure[index]:
                false_alarms += 1 if false_alarm_weights is None else false_alarm_weights[index]
        if false_alarms / onsets > declaration.cutoff_false_alarms_at_most + 1e-12:
            break
        if caught > best_recall:
            best_recall, best = caught, value
    return best


def _state_at_least(label: str, at_least: int) -> bool:
    """Whether a scarcity-state label ("0", "1", "2", "unknown") is a state of at least `at_least`."""

    try:
        return int(label) >= at_least
    except ValueError:
        return False


def choose_cutoffs(
    declaration: Declaration,
    grids: Mapping[int, Grid],
    forecasts: Sequence[Forecast],
    calendar: Sequence[date],
    scarce_at_least: Optional[int] = None,
) -> List[Forecast]:
    """Each forecast with the flag cut-off in force on every day, chosen refit by refit.

    The model is refitted every `cutoff_rule.refit_every` scored days from the
    first (the shared fold grid's blocks). The cut-off of a block is
    `select_cutoff` on the forecast's own earlier walk-forward probabilities and
    the outcomes known at the block's first decision instant: the scored days up
    to the business day before that instant (SOFR for a day is published the
    morning after). A block with no such day flags nothing. No day of the block
    or after it is read. Every forecast and threshold is treated alike, the
    benchmarks included.

    `grids` must cover the forecasts' days, which may reach past the days a
    comparison scores (the single look reads the development days as training).

    With `scarce_at_least` (#461) a day whose as-of scarcity state (the grid's
    `scarcity_state` label, read at the day's decision instant) is at least that
    value takes a separate cut-off: `select_cutoff`, the same rule and limit, on
    the training days of that block that are in such a state, and on those alone.
    Other days, and days with an unknown state, keep the cut-off chosen on all
    training days.

    Raises:
        LookAheadError: if a window reaches past its training end.
        ValueError: if a forecast's days are not its grid's, or are not panel days,
            or `scarce_at_least` is set and the grid has no scarcity state.
    """

    position = {day: k for k, day in enumerate(calendar)}
    step = declaration.cutoff_refit_every
    out = []
    for forecast in forecasts:
        grid = grids[forecast.horizon]
        if tuple(forecast.dates) != tuple(grid.dates):
            raise ValueError(
                f"{forecast.name!r} h = {forecast.horizon}: forecasts are not on the grid's days; "
                f"cut-offs are chosen on the grid the forecast was scored on"
            )
        missing = [day for day in forecast.dates if day not in position]
        if missing:
            raise ValueError(f"{forecast.name!r}: scored day {missing[0]} is not a panel day")
        states = grid.groups.get("scarcity_state") if scarce_at_least is not None else None
        if scarce_at_least is not None and states is None:
            raise ValueError(f"{forecast.name!r} h = {forecast.horizon}: the grid has no scarcity state")
        cutoffs: Dict[float, List[float]] = {tau: [] for tau in declaration.thresholds}
        for start in range(0, len(forecast.dates), step):
            block = forecast.dates[start : start + step]
            last_known = position[block[0]] - forecast.horizon - 1
            training_end = calendar[last_known] if last_known >= 0 else None
            window = [k for k in range(start) if training_end is not None and forecast.dates[k] <= training_end]
            scarce_window = (
                [k for k in window if _state_at_least(states[k], scarce_at_least)] if states is not None else []
            )
            for tau in declaration.thresholds:

                def chosen(rows):
                    weights = None
                    if declaration.weighting_applied and rows:
                        # The distance to a pressure day is read on the training rows alone: a pressure day
                        # after the training end was not yet known at the refit's first decision instant.
                        weights = false_alarm_weights(
                            declaration.weighted_miss,
                            positions=[position[forecast.dates[k]] for k in rows],
                            pressure=[grid.outcomes[tau][k] for k in rows],
                            known_through=position[training_end],
                        )
                    return select_cutoff(
                        declaration,
                        days=[forecast.dates[k] for k in rows],
                        probabilities=[forecast.probabilities[tau][k] for k in rows],
                        pressure=[grid.outcomes[tau][k] for k in rows],
                        onset=[grid.onset_at(tau, declaration.primary)[k] for k in rows],
                        training_end=training_end,
                        false_alarm_weights=weights,
                    )

                value = chosen(window)
                scarce_value = chosen(scarce_window) if states is not None else value
                for k in range(start, start + len(block)):
                    scarce = states is not None and _state_at_least(states[k], scarce_at_least)
                    cutoffs[tau].append(scarce_value if scarce else value)
        out.append(
            Forecast(
                name=forecast.name,
                horizon=forecast.horizon,
                dates=forecast.dates,
                probabilities=forecast.probabilities,
                cutoffs={tau: tuple(column) for tau, column in cutoffs.items()},
                cutoff_rule=declaration.sha256,
                cutoff_weighting=declaration.weighted_miss.sha256 if declaration.weighting_applied else None,
            )
        )
    return out


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




def matched_false_alarm_weights(
    probabilities: Sequence[float], pressure: Sequence[int], target_false_alarms: float
) -> Tuple[float, ...]:
    """Per-day flag weights of a reference that raises `target_false_alarms` false alarms.

    A false alarm is a flag on a day that is not a pressure day. The reference
    flags its highest probabilities first. Groups of tied probabilities are
    flagged whole until the next group would overshoot the count; that group is
    flagged in part, the same fraction of each of its days, which is the
    expected recall of breaking the tie at random.
    """

    weights = [0.0] * len(pressure)
    used = 0.0
    by_value: Dict[float, List[int]] = {}
    for index, p in enumerate(probabilities):
        by_value.setdefault(p, []).append(index)
    for value in sorted(by_value, reverse=True):
        members = by_value[value]
        group = sum(1 for i in members if not pressure[i])
        if used + group <= target_false_alarms + 1e-12:
            for i in members:
                weights[i] = 1.0
            used += group
        else:
            fraction = (target_false_alarms - used) / group
            for i in members:
                weights[i] = fraction
            break
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


def _quantile(ordered: Sequence[float], probability: float) -> float:
    position = probability * (len(ordered) - 1)
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)



# --------------------------------------------------------------------------
# The paired bootstrap
# --------------------------------------------------------------------------

Statistic = Callable[[Sequence[float]], Optional[float]]


def _seed(base: int, *parts: object) -> int:
    material = "\x00".join([str(base)] + [str(part) for part in parts])
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:4], "big") & 0x7FFFFFFF


def _ratio(numerator: int, denominator: int) -> Statistic:
    return lambda t: t[numerator] / t[denominator] if t[denominator] else None


#: Cell vectors of `_paired_vectors`, in order: the days inside, the Brier score
#: the reference loses to the candidate against climatology and against the
#: persistence-logistic (positive: the candidate is better), and realised minus
#: predicted.
_PAIRED_STATS: Mapping[str, Statistic] = {
    "brier_difference_vs_climatology": _ratio(1, 0),
    "brier_difference_vs_persistence": _ratio(2, 0),
    "realised_minus_predicted": _ratio(3, 0),
}

#: Cell vectors of the onset tier: onsets, onsets caught, onsets the reference catches.
_ONSET_STATS: Mapping[str, Statistic] = {
    "recall": _ratio(1, 0),
    "climatology_recall": _ratio(2, 0),
    "recall_difference": lambda t: (t[1] - t[2]) / t[0] if t[0] else None,
}


def _paired_vectors(
    probabilities: Sequence[float],
    climatology: Sequence[float],
    persistence: Sequence[float],
    outcomes: Sequence[int],
    members: Optional[Sequence[int]] = None,
) -> List[List[float]]:
    count = len(outcomes)
    inside = [1.0] * count if members is None else [0.0] * count
    if members is not None:
        for position in members:
            inside[position] = 1.0

    def loss(reference: Sequence[float], i: int) -> float:
        return (reference[i] - outcomes[i]) ** 2 - (probabilities[i] - outcomes[i]) ** 2

    return [
        inside,
        [inside[i] * loss(climatology, i) for i in range(count)],
        [inside[i] * loss(persistence, i) for i in range(count)],
        [inside[i] * (outcomes[i] - probabilities[i]) for i in range(count)],
    ]


def _quantile_interval(
    declaration: Declaration, draws: Sequence[float], undefined: int, point: Optional[float], seed: int, what: str
) -> Dict[str, Any]:
    cell: Dict[str, Any] = {"mean": point}
    if undefined or point is None:
        cell["interval_unavailable"] = (
            f"{what} is undefined on {undefined} of {declaration.replications} resamples "
            f"(no alarm or no event drawn); replicates are not dropped"
            if point is not None
            else f"{what} is undefined on the scored days (no alarm or no event)"
        )
        return cell
    ordered = sorted(draws)
    tail = (1.0 - declaration.level) / 2.0
    cell["interval"] = {
        "lower": _quantile(ordered, tail),
        "upper": _quantile(ordered, 1.0 - tail),
        "level": declaration.level,
        "method": "stationary_bootstrap",
        "block_length": declaration.block_length,
        "replications": declaration.replications,
        "seed": seed,
    }
    return cell


def _bootstrap(
    declaration: Declaration,
    cells: Mapping[str, Sequence[Sequence[float]]],
    statistics: Mapping[str, Statistic],
    count: int,
    *,
    seed: int,
) -> Dict[str, Dict[str, Any]]:
    """Point estimates and bootstrap intervals for every cell, on shared resamples.

    `cells[label]` holds one per-day vector for each total a statistic reads
    (zero where the day is outside the cell). Every cell is read off the same
    resampled days, so a comparison between two models on one cell is paired.
    """

    rng = random.Random(seed)
    draws: Dict[Tuple[str, str], List[float]] = {(l, s): [] for l in cells for s in statistics}
    undefined: Dict[Tuple[str, str], int] = {key: 0 for key in draws}
    for _ in range(declaration.replications):
        indices = stationary_bootstrap_indices(count, declaration.block_length, rng)
        pick = itemgetter(*indices) if count > 1 else (lambda v, i=indices[0]: (v[i],))
        for label, vectors in cells.items():
            totals = [sum(pick(vector)) for vector in vectors]
            for name, statistic in statistics.items():
                value = statistic(totals)
                if value is None:
                    undefined[(label, name)] += 1
                else:
                    draws[(label, name)].append(value)
    out: Dict[str, Dict[str, Any]] = {}
    for label, vectors in cells.items():
        totals = [sum(vector) for vector in vectors]
        entry: Dict[str, Any] = {"days": _clean(totals[0])}
        for name, statistic in statistics.items():
            entry[name] = _quantile_interval(
                declaration, draws[(label, name)], undefined[(label, name)], statistic(totals), seed, name
            )
        out[label] = entry
    return out


def _lower(cell: Mapping[str, Any]) -> Optional[float]:
    interval = cell.get("interval")
    return interval["lower"] if interval else None


def _excludes_zero_above(cell: Mapping[str, Any]) -> bool:
    lower = _lower(cell)
    return lower is not None and lower > 0.0


def _covers_zero(cell: Mapping[str, Any]) -> bool:
    interval = cell.get("interval")
    return bool(interval) and interval["lower"] <= 0.0 <= interval["upper"]




# --------------------------------------------------------------------------
# The judge
# --------------------------------------------------------------------------


def _group_cells(grid: Grid, dimension: str) -> Dict[str, List[int]]:
    cells: Dict[str, List[int]] = {}
    for position, label in enumerate(grid.groups[dimension]):
        cells.setdefault(str(label), []).append(position)
    return dict(sorted(cells.items()))


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
    calendar: Sequence[date],
    holdouts: Optional[Mapping[str, Tuple[date, date]]] = None,
    confirmation: bool = False,
) -> dict:
    """Apply the declared bar to every forecast and return the evidence.

    `calendar` is the panel's business days in order; the week-ahead window
    reads the five days after each decision day from it. With
    `confirmation=True` the run is the single look: it scores the declared
    confirmation window only, and only candidates the declaration names.

    Raises:
        LookAheadError: if a scored day is in a locked lockbox tier, after the
            declared last scored day (development), or outside the declared
            confirmation window (the look).
        ValueError: if a forecast's candidate, cut-off or grid is not as
            declared, a probability is outside [0, 1], the declared
            climatology or persistence benchmark was not scored, or a candidate
            is scored in the look without being named for it.
    """

    _check_grid(declaration, grids, confirmation=confirmation)
    by_name = _check_forecasts(declaration, grids, forecasts, confirmation=confirmation)
    if list(calendar) != sorted(set(calendar)):
        raise ValueError("the calendar must be ascending and distinct")
    holdouts = dict(holdouts or {})
    # A forecast without cut-offs gets them chosen here, from the days of its own grid. The single
    # look passes forecasts cut to its window with the cut-offs `choose_cutoffs` chose on the
    # development days before it.
    unchosen = [f for f in forecasts if f.cutoffs is None]
    if confirmation and unchosen:
        raise ValueError(
            f"{unchosen[0].name!r} h = {unchosen[0].horizon}: the single look needs cut-offs chosen on "
            f"the development days before its window (`choose_cutoffs`), not on the window itself"
        )
    chosen = {(f.name, f.horizon): f for f in choose_cutoffs(declaration, grids, unchosen, calendar)}
    by_name = {
        name: {h: chosen.get((name, h), forecast) for h, forecast in per_horizon.items()}
        for name, per_horizon in by_name.items()
    }

    scarce = _scarce_inputs(declaration, grids, by_name)
    result_candidates: Dict[str, dict] = {}
    for name in sorted(by_name, key=lambda n: (declaration.candidates[n]["role"] != "benchmark", n)):
        result_candidates[name] = _candidate(declaration, name, grids, by_name, calendar, holdouts)
        result_candidates[name]["verdict"]["scarce_regime"] = _scarce_verdict(
            declaration, name, scarce, calendar
        )

    first = grids[declaration.horizons[0]]
    return {
        "declaration": declaration.document(),
        "mode": "confirmation" if confirmation else "development",
        "scored_window": {
            "first": first.dates[0].isoformat(),
            "last": first.dates[-1].isoformat(),
            "days_by_horizon": {str(h): len(grids[h].dates) for h in declaration.horizons},
        },
        "holdouts": {k: [v[0].isoformat(), v[1].isoformat()] for k, v in holdouts.items()},
        "candidates": result_candidates,
    }


def _scarce_inputs(
    declaration: Declaration, grids: Mapping[int, Grid], by_name: Mapping[str, Mapping[int, Forecast]]
) -> Optional[Tuple[Dict[int, Grid], Dict[str, Dict[int, Forecast]]]]:
    """The grids and forecasts cut to the days in the scarce regime (scarcity state at least the
    declared one, read as of each horizon's decision instant), or `None` if a horizon has none."""

    keep: Dict[int, List[int]] = {}
    for horizon, grid in grids.items():
        keep[horizon] = [
            k
            for k, state in enumerate(grid.groups["scarcity_state"])
            if str(state).lstrip("-").isdigit() and int(state) >= declaration.risky_state_at_least
        ]
        if not keep[horizon]:
            return None

    def pick(values: Sequence[Any], positions: Sequence[int]) -> Tuple[Any, ...]:
        return tuple(values[k] for k in positions)

    scarce_grids = {
        horizon: Grid(
            horizon=horizon,
            dates=pick(grid.dates, keep[horizon]),
            outcomes={tau: pick(column, keep[horizon]) for tau, column in grid.outcomes.items()},
            groups={dimension: pick(labels, keep[horizon]) for dimension, labels in grid.groups.items()},
            onset=pick(grid.onset, keep[horizon]),
            onsets=None
            if grid.onsets is None
            else {tau: pick(column, keep[horizon]) for tau, column in grid.onsets.items()},
        )
        for horizon, grid in grids.items()
    }
    scarce_forecasts = {
        name: {
            horizon: Forecast(
                name=name,
                horizon=horizon,
                dates=pick(forecast.dates, keep[horizon]),
                probabilities={tau: pick(c, keep[horizon]) for tau, c in forecast.probabilities.items()},
                cutoffs={tau: pick(c, keep[horizon]) for tau, c in forecast.cutoffs.items()},
                cutoff_rule=forecast.cutoff_rule,
                cutoff_weighting=forecast.cutoff_weighting,
            )
            for horizon, forecast in per_horizon.items()
        }
        for name, per_horizon in by_name.items()
    }
    return scarce_grids, scarce_forecasts


def _scarce_verdict(
    declaration: Declaration,
    name: str,
    scarce: Optional[Tuple[Dict[int, Grid], Dict[str, Dict[int, Forecast]]]],
    calendar: Sequence[date],
) -> dict:
    """The pass rule on the scarce regime's days alone: reported, never part of the pass rule.

    Tiers 1, 3 and 5 are judged exactly as on all days, with the cut-offs the forecast already
    carries, on the days whose scarcity state is at least `risky_dates.scarcity_state_at_least`.
    The week-ahead tier then reads the decision days whose five target days are all scarce.
    """

    out: Dict[str, Any] = {
        "reported_only": True,
        "scarcity_state_at_least": declaration.risky_state_at_least,
    }
    if scarce is None:
        out.update(passes=False, unavailable="a judged horizon has no day in the scarce regime")
        return out
    grids, by_name = scarce
    result = _candidate(declaration, name, grids, by_name, calendar, {}, lean=True)
    verdict = result["verdict"]
    near = result["tiers"]["onset_warning"][f"lead_at_least_{declaration.onset_lead}"]
    out.update(
        days_by_horizon={str(h): len(grid.dates) for h, grid in grids.items()},
        onsets=near.get("onsets"),
        events_by_horizon={str(h): sum(grid.outcomes[declaration.primary]) for h, grid in grids.items()},
        tier_1_onset_warning=verdict["tier_1_onset_warning"],
        tier_3_no_crying_wolf=verdict["tier_3_no_crying_wolf"],
        tier_5_week_ahead=verdict["tier_5_week_ahead"],
        recall=near.get("recall"),
        worst_false_alarms_per_onset=near.get("worst_false_alarms_per_onset"),
        week_ahead_days=result["tiers"]["week_ahead"].get("days"),
        passes=verdict["passes"],
    )
    return out


def _candidate(
    declaration: Declaration,
    name: str,
    grids: Mapping[int, Grid],
    by_name: Mapping[str, Mapping[int, Forecast]],
    calendar: Sequence[date],
    holdouts: Mapping[str, Tuple[date, date]],
    *,
    lean: bool = False,
) -> dict:
    """One candidate's evidence. `lean` is the scarce-regime pass: the primary threshold, the regime
    split and the three tiers of the pass rule only."""

    entry = declaration.candidates[name]
    primary = _key(declaration.primary)
    scored = [h for h in declaration.horizons if h in by_name[name]]
    per_horizon: Dict[str, dict] = {}
    for horizon in scored:
        grid = grids[horizon]
        per_tau: Dict[str, dict] = {}
        for tau in ((declaration.primary,) if lean else declaration.thresholds):
            forecast = by_name[name][horizon].probabilities[tau]
            outcomes = grid.outcomes[tau]
            cutoffs = by_name[name][horizon].cutoffs[tau]
            flags = _alarm_flags(
                declaration, name, [1 if p >= c else 0 for p, c in zip(forecast, cutoffs)],
                grid.onset_at(tau, declaration.primary),
            )
            per_tau[_key(tau)] = _row(
                declaration, name, horizon, tau, grid, forecast, outcomes, cutoffs, flags, by_name, holdouts,
                lean=lean,
            )
        per_horizon[str(horizon)] = per_tau

    onset_tiers = {
        f"lead_at_least_{declaration.onset_lead}": _onset_tier(
            declaration, name, declaration.onset_lead, scored, grids, by_name, calendar
        ),
    }
    if not lean:
        onset_tiers[f"lead_at_least_{declaration.far_lead}"] = _onset_tier(
            declaration, name, declaration.far_lead, scored, grids, by_name, calendar
        )
    tiers = {
        "onset_warning": onset_tiers,
        "no_crying_wolf": {h: per_horizon[h][primary]["no_crying_wolf"] for h in per_horizon},
        "week_ahead": _week_ahead(declaration, name, scored, grids, by_name, calendar),
    }
    if not lean:
        tiers["risky_dates"] = _risky_dates(declaration, name, scored, grids, by_name)
    near = tiers["onset_warning"][f"lead_at_least_{declaration.onset_lead}"]
    wolf_by_horizon = {
        str(h): bool(tiers["no_crying_wolf"][str(h)]["ok"]) if str(h) in tiers["no_crying_wolf"] else False
        for h in declaration.horizons
    }
    verdict = {
        "threshold_bp": declaration.primary,
        "tier_1_onset_warning": bool(near.get("passes")),
        "tier_3_no_crying_wolf_by_horizon": wolf_by_horizon,
        "tier_3_no_crying_wolf": all(wolf_by_horizon.values()),
        "tier_5_week_ahead": bool(tiers["week_ahead"].get("passes")),
        "not_scored": [h for h in declaration.horizons if h not in scored],
    }
    verdict["passes"] = (
        verdict["tier_1_onset_warning"] and verdict["tier_3_no_crying_wolf"] and verdict["tier_5_week_ahead"]
    )
    return {
        "role": entry["role"],
        "features": entry["features"],
        "calibration": entry["calibration"],
        **({"alarm_rule": entry["alarm_rule"]} if "alarm_rule" in entry else {}),
        "horizons": per_horizon,
        "scored_horizons": scored,
        "tiers": tiers,
        "verdict": verdict,
    }


def _row(
    declaration: Declaration,
    name: str,
    horizon: int,
    tau: float,
    grid: Grid,
    probabilities: Sequence[float],
    outcomes: Sequence[int],
    cutoffs: Sequence[float],
    flags: Sequence[int],
    by_name: Mapping[str, Mapping[int, Forecast]],
    holdouts: Mapping[str, Tuple[date, date]],
    *,
    lean: bool = False,
) -> dict:
    count = len(outcomes)
    summary = _flags_summary(flags, outcomes)
    row: Dict[str, Any] = {
        "days": count,
        "events": sum(outcomes),
        "base_rate": sum(outcomes) / count,
        "cutoff": _cutoff_summary(cutoffs),
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

    climatology = by_name[declaration.climatology][horizon].probabilities[tau]
    persistence = by_name[declaration.persistence][horizon].probabilities[tau]
    cells: Dict[str, Sequence[Sequence[float]]] = {
        "pooled": _paired_vectors(probabilities, climatology, persistence, outcomes)
    }
    index: Dict[str, Tuple[str, str]] = {}
    primary = tau == declaration.primary
    if primary:
        for dimension in ("regime",) if lean else dict.fromkeys(declaration.groupings + ("regime",)):
            for label, members in _group_cells(grid, dimension).items():
                key = f"{dimension}\x00{label}"
                cells[key] = _paired_vectors(probabilities, climatology, persistence, outcomes, members)
                index[key] = (dimension, label)
    evidence = _bootstrap(
        declaration, cells, _PAIRED_STATS, count, seed=_seed(declaration.seed, name, horizon, _key(tau))
    )
    pooled = evidence["pooled"]
    row["paired"] = {
        "vs_calendar_climatology": {"brier_difference": pooled["brier_difference_vs_climatology"]},
        "vs_persistence_logistic": {
            "brier_difference": pooled["brier_difference_vs_persistence"],
            "note": "tier 4: reported, not part of the pass rule",
        },
    }
    row["calibration"] = {
        "mean_predicted": sum(probabilities) / count,
        "realised_frequency": sum(outcomes) / count,
        "realised_minus_predicted": pooled["realised_minus_predicted"],
    }
    if not primary:
        row["note"] = "reported at this threshold, not the pass condition"
    else:
        splits: Dict[str, Dict[str, dict]] = {}
        for key, (dimension, label) in index.items():
            members = _group_cells(grid, dimension)[label]
            member_p = [probabilities[i] for i in members]
            member_y = [outcomes[i] for i in members]
            cell = evidence[key]
            splits.setdefault(dimension, {})[label] = {
                "days": cell["days"],
                "events": sum(member_y),
                "flags": _flags_summary([flags[i] for i in members], member_y),
                "mean_predicted": sum(member_p) / len(members),
                "realised_frequency": sum(member_y) / len(members),
                "brier_difference_vs_climatology": cell["brier_difference_vs_climatology"],
                "brier_difference_vs_persistence": cell["brier_difference_vs_persistence"],
                "realised_minus_predicted": cell["realised_minus_predicted"],
            }
        row["splits"] = splits
        row["no_crying_wolf"] = _no_crying_wolf(declaration, grid, flags, splits, restricted=lean)
    held: Dict[str, dict] = {}
    for window, (first, last) in ({} if lean else holdouts).items():
        positions = [k for k, day in enumerate(grid.dates) if first <= day <= last]
        held[window] = _holdout_cell(positions, probabilities, climatology, outcomes, flags)
    if holdouts and not lean:
        row["holdouts"] = held
    return row


def _cutoff_summary(cutoffs: Sequence[float]) -> dict:
    """The cut-offs chosen over the scored days: how many days flag nothing, and the spread of the rest."""

    finite = sorted(c for c in cutoffs if not math.isinf(c))
    out: Dict[str, Any] = {"days_never_flag": len(cutoffs) - len(finite), "days": len(cutoffs)}
    if finite:
        out.update(minimum=finite[0], median=_quantile(finite, 0.5), maximum=finite[-1])
    return out


def _no_crying_wolf(
    declaration: Declaration,
    grid: Grid,
    flags: Sequence[int],
    splits: Mapping[str, Mapping[str, dict]],
    *,
    restricted: bool = False,
) -> dict:
    """Tier 3 at one lead: the alarm rate in abundant stretches and calibration by regime.

    `restricted` is the scarce-regime reading, where an abundant stretch may have no day left in
    the days scored; an empty stretch then has no alarm rate to exceed.
    """

    stretches = {
        f"scarcity_state_{declaration.abundant_state}": [
            k for k, label in enumerate(grid.groups["scarcity_state"]) if str(label) == declaration.abundant_state
        ],
        f"regime_{declaration.abundant_regime}": [
            k for k, label in enumerate(grid.groups["regime"]) if str(label) == declaration.abundant_regime
        ],
    }
    abundant: Dict[str, dict] = {}
    for label, members in stretches.items():
        flagged = sum(flags[k] for k in members)
        rate = flagged / len(members) * declaration.business_days_per_year if members else None
        abundant[label] = {
            "days": len(members),
            "flags": flagged,
            "flags_per_year": rate,
            "at_most": declaration.flags_per_year_at_most,
            "ok": (rate is None and restricted) or (rate is not None and rate <= declaration.flags_per_year_at_most),
        }
    # Calibration is tested in the regimes that had a pressure day (+5 bp) in the scored window; the
    # others are reported (does the interval cover zero?) and do not count (ruling of 8 October 2026).
    tested: Dict[str, bool] = {}
    reported: Dict[str, dict] = {}
    for label, cell in splits["regime"].items():
        covers = _covers_zero(cell["realised_minus_predicted"])
        if cell["events"] > 0:
            tested[label] = covers
        else:
            reported[label] = {"days": cell["days"], "events": 0, "covers_zero": covers}
    return {
        "abundant_stretches": abundant,
        "calibrated_by_regime": tested,
        "calibration_reported_regimes": reported,
        "ok": all(c["ok"] for c in abundant.values()) and all(tested.values()),
    }


def _onset_tier(
    declaration: Declaration,
    name: str,
    lead: int,
    scored: Sequence[int],
    grids: Mapping[int, Grid],
    by_name: Mapping[str, Mapping[int, Forecast]],
    calendar: Sequence[date] = (),
) -> dict:
    """Tier 1 at lead >= `lead`: the share of +5 bp onsets flagged at some horizon h >= lead.

    False alarms are flags on days that are not pressure days, counted at each
    horizon h >= lead; the worst horizon's count per onset is the tier's.

    With the weighted miss rule loaded (#454) each false alarm is also counted at its weight, by its distance
    in `calendar` days to the nearest pressure day of the scored days (a test-only reading: the full outcome
    record of the scored days). The tier's limit is read on that count when the rule is applied, on the flat
    count otherwise; both are reported.
    """

    tau = declaration.primary
    wanted = [h for h in declaration.horizons if h >= lead]
    horizons = [h for h in wanted if h in scored]
    if not horizons:
        return {"lead_at_least": lead, "unavailable": f"not scored at any horizon from {lead}"}
    common = sorted(set.intersection(*(set(grids[h].dates) for h in horizons)))
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in horizons}
    first = horizons[0]
    onset = [float(grids[first].onset[position[first][day]]) for day in common]
    onsets = int(sum(onset))
    caught = [0.0] * len(common)
    reference_missed = [1.0] * len(common)
    false_alarms: Dict[str, dict] = {}
    rule = declaration.weighted_miss
    weighted_alarms: Dict[str, dict] = {}
    by_regime: Dict[str, Dict[str, dict]] = {}
    if rule is not None:
        place = {day: k for k, day in enumerate(calendar)}
        regime_column = grids[first].groups.get("regime")
        regimes = (
            [regime_column[position[first][day]] for day in common] if regime_column is not None else ["all"] * len(common)
        )
        missing = [day for day in common if day not in place]
        if missing:
            raise ValueError(f"scored day {missing[0]} is not a panel day; the weighted count needs the calendar")
    for h in horizons:
        at = [position[h][day] for day in common]
        pressure = [grids[h].outcomes[tau][k] for k in at]
        chosen = by_name[name][h]
        flags = _alarm_flags(
            declaration, name, [1 if chosen.probabilities[tau][k] >= chosen.cutoffs[tau][k] else 0 for k in at], onset
        )
        raised = sum(1 for f, y in zip(flags, pressure) if f and not y)
        weights = matched_false_alarm_weights(
            [by_name[declaration.climatology][h].probabilities[tau][k] for k in at], pressure, raised
        )
        caught = [max(c, float(f)) for c, f in zip(caught, flags)]
        reference_missed = [m * (1.0 - w) for m, w in zip(reference_missed, weights)]
        false_alarms[str(h)] = {
            "false_alarms": raised,
            "per_onset": raised / onsets if onsets else None,
        }
        if rule is not None:
            places = [place[day] for day in common]
            miss = false_alarm_weights(rule, positions=places, pressure=pressure, known_through=places[-1])
            weighted = sum(w for f, w in zip(flags, miss) if f)
            weighted_alarms[str(h)] = {
                "false_alarms": weighted,
                "per_onset": weighted / onsets if onsets else None,
            }
            for index, label in enumerate(regimes):
                if flags[index] and not pressure[index]:
                    cell = by_regime.setdefault(label, {}).setdefault(str(h), {"flat": 0, "weighted": 0.0})
                    cell["flat"] += 1
                    cell["weighted"] += miss[index]
    reference_caught = [1.0 - m for m in reference_missed]
    out: Dict[str, Any] = {
        "lead_at_least": lead,
        "horizons": horizons,
        "complete": horizons == wanted,
        "days": len(common),
        "onsets": onsets,
        "onsets_flagged": _clean(sum(o * c for o, c in zip(onset, caught))),
        "false_alarms_by_horizon": false_alarms,
    }
    if rule is not None:
        out["weighted_miss_applied"] = rule.applied
        out["weighted_false_alarms_by_horizon"] = weighted_alarms
        out["by_regime"] = {
            label: {
                "onsets": int(sum(o for o, r in zip(onset, regimes) if r == label)),
                "onsets_flagged": _clean(sum(o * c for o, c, r in zip(onset, caught, regimes) if r == label)),
                "false_alarms_by_horizon": {
                    str(h): by_regime.get(label, {}).get(str(h), {"flat": 0, "weighted": 0.0}) for h in horizons
                },
            }
            for label in sorted(set(regimes))
        }
    if not onsets:
        out["unavailable"] = "no onset on the scored days"
        return out
    evidence = _bootstrap(
        declaration,
        {"onsets": [onset, [o * c for o, c in zip(onset, caught)], [o * c for o, c in zip(onset, reference_caught)]]},
        _ONSET_STATS,
        len(common),
        seed=_seed(declaration.seed, name, "onsets", lead),
    )["onsets"]
    worst = max(f["per_onset"] for f in false_alarms.values())
    limited = worst
    if rule is not None:
        worst_weighted = max(f["per_onset"] for f in weighted_alarms.values())
        out["worst_weighted_false_alarms_per_onset"] = worst_weighted
        if rule.applied:
            limited = worst_weighted
    out.update(
        recall=evidence["recall"],
        climatology_recall=evidence["climatology_recall"]["mean"],
        recall_difference=evidence["recall_difference"],
        worst_false_alarms_per_onset=worst,
    )
    if lead == declaration.onset_lead:
        lower = _lower(evidence["recall"])
        out["criteria"] = {
            "recall": evidence["recall"]["mean"] is not None
            and evidence["recall"]["mean"] >= declaration.onset_recall_at_least,
            "recall_above_climatology": lower is not None
            and lower > evidence["climatology_recall"]["mean"],
            "false_alarms": limited <= declaration.onset_false_alarms_at_most,
        }
        out["passes"] = out["complete"] and all(out["criteria"].values())
    else:
        out["reported_only"] = True
        out["meets_far_recall"] = (
            evidence["recall"]["mean"] is not None
            and evidence["recall"]["mean"] >= declaration.far_recall_at_least
        )
    return out


def _risky_dates(
    declaration: Declaration,
    name: str,
    scored: Sequence[int],
    grids: Mapping[int, Grid],
    by_name: Mapping[str, Mapping[int, Forecast]],
) -> dict:
    """Tier 2 (reported only): AUROC on scheduled risk dates in scarcity state >= the declared one."""

    lead, tau = declaration.risky_lead, declaration.primary
    if lead not in scored:
        return {"lead": lead, "unavailable": f"not scored at h = {lead}", "reported_only": True}
    grid = grids[lead]
    members = []
    for k, (risk, state) in enumerate(zip(grid.groups["risk_date"], grid.groups["scarcity_state"])):
        if str(risk) == "1" and str(state).lstrip("-").isdigit() and int(state) >= declaration.risky_state_at_least:
            members.append(k)
    outcomes = [grid.outcomes[tau][k] for k in members]
    p = [by_name[name][lead].probabilities[tau][k] for k in members]
    reference = [by_name[declaration.climatology][lead].probabilities[tau][k] for k in members]
    out: Dict[str, Any] = {"lead": lead, "days": len(members), "events": sum(outcomes), "reported_only": True}
    value, base = auroc(p, outcomes), auroc(reference, outcomes)
    if value is None or base is None:
        out["unavailable"] = "no pressure day, or only pressure days, among the risky dates"
        return out
    rng = random.Random(_seed(declaration.seed, name, "risky", lead))
    draws, undefined = [], 0
    for _ in range(declaration.replications):
        indices = stationary_bootstrap_indices(len(members), declaration.block_length, rng)
        y = [outcomes[i] for i in indices]
        a, b = auroc([p[i] for i in indices], y), auroc([reference[i] for i in indices], y)
        if a is None or b is None:
            undefined += 1
        else:
            draws.append(a - b)
    difference = _quantile_interval(declaration, draws, undefined, value - base, 0, "the AUROC difference")
    out.update(
        auroc=value,
        climatology_auroc=base,
        auroc_difference=difference,
        meets_auroc=value >= declaration.risky_auroc_at_least,
        beats_climatology=_excludes_zero_above(difference),
    )
    return out


def _combine(declaration: Declaration, probabilities: Sequence[float]) -> float:
    if declaration.week_combine == "max":
        return max(probabilities)
    miss = 1.0
    for p in probabilities:
        miss *= 1.0 - p
    return 1.0 - miss


def _week_ahead(
    declaration: Declaration,
    name: str,
    scored: Sequence[int],
    grids: Mapping[int, Grid],
    by_name: Mapping[str, Mapping[int, Forecast]],
    calendar: Sequence[date],
) -> dict:
    """Tier 5: P(at least one pressure day in the next W business days), forecast each day."""

    tau, width = declaration.primary, declaration.week_days
    needed = list(range(1, width + 1))
    missing = [h for h in needed if h not in scored]
    if missing:
        return {"unavailable": f"not scored at horizons {missing}", "passes": False}
    position = {h: {day: k for k, day in enumerate(grids[h].dates)} for h in needed}
    names = (name, declaration.climatology, declaration.persistence)
    series = {n: [] for n in names}
    outcomes: List[int] = []
    decision_days: List[date] = []
    for i in range(len(calendar) - width):
        targets = [calendar[i + h] for h in needed]
        if any(day not in position[h] for h, day in zip(needed, targets)):
            continue
        at = [position[h][day] for h, day in zip(needed, targets)]
        outcomes.append(max(grids[h].outcomes[tau][k] for h, k in zip(needed, at)))
        decision_days.append(calendar[i])
        for n in names:
            series[n].append(_combine(declaration, [by_name[n][h].probabilities[tau][k] for h, k in zip(needed, at)]))
    if not outcomes:
        return {"unavailable": "no decision day has all five targets scored", "passes": False}
    p, climatology, persistence = (series[n] for n in names)
    count = len(outcomes)
    evidence = _bootstrap(
        declaration,
        {"pooled": _paired_vectors(p, climatology, persistence, outcomes)},
        _PAIRED_STATS,
        count,
        seed=_seed(declaration.seed, name, "week"),
    )["pooled"]
    criteria = {
        "calibrated": _covers_zero(evidence["realised_minus_predicted"]),
        "beats_climatology_brier": _excludes_zero_above(evidence["brier_difference_vs_climatology"]),
    }
    return {
        "days": count,
        "first_decision_day": decision_days[0].isoformat(),
        "last_decision_day": decision_days[-1].isoformat(),
        "combine": declaration.week_combine,
        "events": sum(outcomes),
        "base_rate": sum(outcomes) / count,
        **_decomposition(p, outcomes),
        "reliability_steps": _reliability_steps(p, outcomes),
        "mean_predicted": sum(p) / count,
        "realised_minus_predicted": evidence["realised_minus_predicted"],
        "brier_difference_vs_climatology": evidence["brier_difference_vs_climatology"],
        "brier_difference_vs_persistence": evidence["brier_difference_vs_persistence"],
        "criteria": criteria,
        "passes": all(criteria.values()),
    }


# --------------------------------------------------------------------------
# Producing the inputs
# --------------------------------------------------------------------------


def restrict_forecast(forecast: Forecast, first: date, last: date) -> Forecast:
    """The days of a walk-forward forecast inside `[first, last]`, values unchanged.

    The confirmation look scores its window only; the forecasts for it are
    walk-forward through the window's last day and are cut to its days here.
    """

    keep = [k for k, day in enumerate(forecast.dates) if first <= day <= last]
    return Forecast(
        name=forecast.name,
        horizon=forecast.horizon,
        dates=tuple(forecast.dates[k] for k in keep),
        probabilities={tau: tuple(column[k] for k in keep) for tau, column in forecast.probabilities.items()},
        cutoffs=None
        if forecast.cutoffs is None
        else {tau: tuple(column[k] for k in keep) for tau, column in forecast.cutoffs.items()},
        cutoff_rule=forecast.cutoff_rule,
        cutoff_weighting=forecast.cutoff_weighting,
    )


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
    end: Optional[date] = None,
) -> List[Forecast]:
    """The two benchmarks, scored by the judge itself on the shared fold grid.

    Calendar-type climatology and the persistence-logistic, each by
    `baseline.rolling_exceedance_backtest` through `end` (the declared last
    scored day unless the confirmation look passes its window's last day),
    under the declaration's thresholds.
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
            end=declaration.last_day if end is None else end,
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
    """The shared grid at one horizon: outcomes, onsets and the declared groupings.

    The groupings are read from the day alone or as of its decision instant:
    the regime, the pressure-day type (`splits.reporting_day_type`, #278) and
    the scheduled risk date (`_scheduled_risk_date`) from the calendar, and the
    reserve-scarcity state from `scarcity_state`, which
    `scarcity.pressure_days_by_state` reads at the forecast's decision.
    `extra_groups` supplies any grouping a later track declares (a policy
    period, say).
    """

    from .data import exceeds_bp
    from . import pressure

    by_date = {row.date: row for row in rows}
    onset_days = {tau: set(pressure.onsets(rows, tau, scored_dates)) for tau in declaration.thresholds}
    onsets = onset_days[declaration.primary]
    missing = [day for day in scored_dates if day not in by_date]
    if missing:
        raise ValueError(f"scored day {missing[0]} is not a row of the panel")
    groups: Dict[str, List[str]] = {"regime": [], "day_type": [], "scarcity_state": [], "risk_date": []}
    for day in scored_dates:
        values = by_date[day].values
        groups["regime"].append(splits.regime(day))
        groups["day_type"].append(splits.reporting_day_type(day, values))
        groups["risk_date"].append("1" if _scheduled_risk_date(values) else "0")
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
        onset=tuple(1 if day in onsets else 0 for day in scored_dates),
        onsets={
            tau: tuple(1 if day in days else 0 for day in scored_dates) for tau, days in onset_days.items()
        },
    )


def _scheduled_risk_date(values: Mapping[str, Optional[float]]) -> bool:
    """A quarter-end, a tax date or a day with a coupon settlement (the "large Treasury settlement").

    Calendar facts, known ahead of the day, as the day-type grouping already reads them.
    """

    coupons = values.get("treasury_settlement_coupons")
    return (
        float(values["quarter_end"] or 0.0) == 1.0
        or float(values["tax_date"] or 0.0) == 1.0
        or (coupons is not None and float(coupons) > 0.0)
    )
