"""The as-of information set: what a forecast may read, and from which row.

`docs/decisions/information-set.md` decides the rule; this module is its one
implementation. A forecast for the scored row `T` is made at the declared
decision time on the panel day before it, `dates[T - 1]` -- the *decision
instant*. At that instant:

1. **Each declared input is read per field**, at the latest panel row whose
   declared first-observable instant is at or before the decision instant.
   The declarations are the registry's own: a field's `field_release_lags`
   block where it has one, else its source's `release_lag`, read by
   `declared_availability`. Nothing here assumes a lag.
2. **Scheduled inputs are read at `T` itself.** The calendar columns
   (`contract.CALENDAR_FEATURES`) are a function of the date and always known.
   A source field is scheduled only when its source declares it in a
   `scheduled_availability` block: the value for a date is announced `days`
   panel business days before it, at `available_time`. The block carries its
   evidence, and the value still passes the same availability check as every
   other read.
3. **The target is read at one row, the anchor.** The target is `spread_bps`,
   `sofr - iorb`; a derived feature is read at the latest row where every one
   of its constituents is observable, never assembled from two rows. The
   anchor is also the label-observability boundary: a training label is
   admissible exactly when its row is at or before the anchor, so the training
   frame is the prefix ending there. This replaces the purge as the rule for
   training labels.
4. **One fold grid.** The anchor depends on the target's declarations alone,
   so the first scored row -- the first with `minimum_history` admissible
   labels -- does not move with the declared features, and any two
   declarations scored on one panel are paired by construction.
5. **Both directions are guarded** by `InformationRule.check`: a read newer
   than the decision instant raises `LookAheadError` (leakage), and a read
   older than the latest admissible row raises `StaleReadError` (staleness).

Business days are counted on the panel's own dates, as
`baseline._check_decision_relative_availability` always has: the panel is the
only calendar this project keeps, and `data.py` refuses to invent another.
Wall clocks are compared, not zoned instants, for the same reason that guard
gives.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import (
    Dict,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
)

from .contract import (
    AVAILABLE_TIME_RE,
    CALENDAR_FEATURES,
    DERIVED_FEATURES,
    END_OF_DAY,
    PER_FIELD_DERIVED_FEATURES,
    field_sources_for_features,
)
from .data import DailyObservation
from .registry import RegistryContractError
from .splits import LookAheadError, SplitError, ensure_strictly_ascending

__all__ = [
    "FieldRead",
    "InformationRule",
    "InformationSet",
    "SCHEDULED_AVAILABILITY_KEY",
    "StaleReadError",
    "TARGET",
    "declared_availability",
    "fold_grid",
    "information_summary",
    "refit_blocks",
    "require_refit_every",
    "validate_scheduled_availability",
]

#: The target every model here forecasts, and the feature the anchor reads.
TARGET = "spread_bps"

#: The panel columns the target is computed from. They are read at the anchor
#: and only there: `DailyObservation.spread_bps` reads them off one mapping,
#: so carrying either from another row would assemble a spread no day had.
TARGET_COLUMNS = tuple(DERIVED_FEATURES[TARGET])

#: The source-level key declaring scheduled fields. Beside `release_lag`
#: rather than inside it: `release_lag` also dates the point-in-time rows the
#: panel is built from, and the panel's bytes must not move because a
#: forecast-time declaration was added.
SCHEDULED_AVAILABILITY_KEY = "scheduled_availability"

_SCHEDULED_KEYS = {
    "basis",
    "unit",
    "days",
    "available_time",
    "timezone",
    "fields",
    "evidence",
    "note",
}

#: Later than any deadline a panel can express. A business-day count whose
#: publication day runs off the end of the panel is late, not unknown -- see
#: `baseline._NEVER_ON_THIS_PANEL`, which is this value.
NEVER_ON_THIS_PANEL = datetime.max

KIND_OBSERVED = "observed"
KIND_SCHEDULED = "scheduled"
KIND_CALENDAR = "calendar"


class StaleReadError(ValueError):
    """A read is older than the latest value admissible at its decision instant.

    Not a `LookAheadError`: a stale read leaks nothing, and a handler written
    for leakage must not swallow it. It is the guard the purge design lacked --
    every leakage guard passed while every input was read a week late.
    """


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_scheduled_availability(source_id: str, block: object) -> List[str]:
    """Problems with one `scheduled_availability` block; empty means it conforms.

    The claim is "the value for date d is public `days` panel business days
    before d, at `available_time`". It is the earliest claim a declaration can
    make -- earlier than the value's own date -- so it must carry `evidence`
    naming what establishes it, exactly as `registry.check_availability_provenance`
    requires of an early `available_time`.
    """

    label = f"{source_id}.{SCHEDULED_AVAILABILITY_KEY}"
    if not isinstance(block, Mapping):
        return [f"{label} must be an object, got {type(block).__name__}"]
    problems = []
    unknown = sorted(set(block) - _SCHEDULED_KEYS)
    if unknown:
        problems.append(f"{label}: unknown keys {unknown}")
    if block.get("basis") != "announced_before_ref_date":
        problems.append(
            f"{label}: basis must be 'announced_before_ref_date', got "
            f"{block.get('basis')!r}"
        )
    if block.get("unit") != "business_days":
        problems.append(f"{label}: unit must be 'business_days', got {block.get('unit')!r}")
    days = block.get("days")
    if not _is_int(days) or days < 1:
        problems.append(
            f"{label}: days must be an integer of at least 1, got {days!r}; a "
            f"value announced on its own date is not known the day before it"
        )
    moment = block.get("available_time")
    if not isinstance(moment, str) or not AVAILABLE_TIME_RE.match(moment):
        problems.append(f"{label}: available_time must be an HH:MM string, got {moment!r}")
    zone = block.get("timezone")
    if not isinstance(zone, str) or not zone:
        problems.append(f"{label}: available_time requires a timezone")
    fields = block.get("fields")
    if (
        not isinstance(fields, list)
        or not fields
        or not all(isinstance(name, str) and name for name in fields)
    ):
        problems.append(f"{label}: fields must be a non-empty list of field names")
    evidence = block.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        problems.append(
            f"{label}: evidence must name what establishes the claim; a value "
            f"declared public before its own date is the earliest claim a "
            f"declaration can make"
        )
    return problems


def _scheduled_blocks(
    registry: Mapping[str, Mapping[str, object]],
) -> Dict[Tuple[str, str], Mapping[str, object]]:
    """Every declared scheduled field, validated, keyed by `(source, field)`."""

    found: Dict[Tuple[str, str], Mapping[str, object]] = {}
    problems: List[str] = []
    for source_id, source in registry.items():
        if not isinstance(source, Mapping) or SCHEDULED_AVAILABILITY_KEY not in source:
            continue
        block = source[SCHEDULED_AVAILABILITY_KEY]
        issues = validate_scheduled_availability(str(source_id), block)
        if not issues:
            declared = set(source.get("fields") or ())
            for name in block["fields"]:
                if name not in declared:
                    issues.append(
                        f"{source_id}.{SCHEDULED_AVAILABILITY_KEY}: {name!r} is not "
                        f"one of the source's declared fields"
                    )
                found[(str(source_id), name)] = block
        problems.extend(issues)
    if problems:
        raise RegistryContractError("; ".join(problems))
    return found


def declared_availability(
    registry: Mapping[str, Mapping[str, object]],
    source_id: str,
    field: str,
    dates: Sequence[date],
    position: int,
) -> Optional[datetime]:
    """The first instant a field's value for `dates[position]` is observable.

    The per-field lag -- `field_release_lags[field]`, else the source's
    `release_lag` -- counted on the panel's dates for a business-day unit and
    on the calendar otherwise. `None` where the declaration makes no
    row-relative claim: a `snapshot_retrieved_at` basis, or no `days`.

    A field the source lists in `scheduled_availability` is dated by that block
    instead: `days` panel rows before `position`, at `available_time`. A value
    whose announcement day precedes the panel is dated to the panel's first
    midnight, which is later than the truth and so the safe side.

    `baseline._declared_availability` is this function; the name there is kept
    for the callers and the audit script that mirror it.
    """

    source = registry[source_id]
    scheduled = source.get(SCHEDULED_AVAILABILITY_KEY)
    if isinstance(scheduled, Mapping) and field in (scheduled.get("fields") or ()):
        moment = time.fromisoformat(str(scheduled["available_time"]))
        announced = position - int(scheduled["days"])
        if announced < 0:
            return datetime.combine(dates[0], time.min)
        return datetime.combine(dates[announced], moment)
    field_lags = source.get("field_release_lags") or {}
    lag = field_lags.get(field) or source.get("release_lag") or {}
    if lag.get("basis") == "snapshot_retrieved_at":
        return None
    days = lag.get("days")
    if days is None:
        return None
    moment = time.fromisoformat(str(lag.get("available_time", END_OF_DAY)))
    if lag.get("unit") == "business_days":
        published = position + int(days)
        if published >= len(dates):
            return NEVER_ON_THIS_PANEL
        return datetime.combine(dates[published], moment)
    return datetime.combine(dates[position] + timedelta(days=int(days)), moment)


class FieldRead(NamedTuple):
    """One declared feature's read at one decision instant.

    `row` is the panel row the value comes from. `rows` is how many panel rows
    it sits before the scored row (0 for a scheduled or calendar read, 2 for a
    daily NY Fed rate on an ordinary day). `hours` is how long the value had
    been observable at the decision instant, `None` for a calendar column,
    which has no publication.
    """

    feature: str
    kind: str
    fields: Tuple[Tuple[str, str], ...]
    row: int
    available_at: Optional[datetime]
    rows: int
    hours: Optional[float]


class InformationSet(NamedTuple):
    """Everything one forecast reads: the scored row, its instant, its reads."""

    scored_index: int
    decision_instant: datetime
    anchor: int
    reads: Tuple[FieldRead, ...]


class _Group(NamedTuple):
    feature: str
    kind: str
    fields: Tuple[Tuple[str, str], ...]
    columns: Tuple[str, ...]


def _columns_of(feature: str) -> Tuple[str, ...]:
    """The panel columns a declared feature is carried in."""

    if feature in DERIVED_FEATURES:
        out: List[str] = []
        for part in DERIVED_FEATURES[feature]:
            out.extend(_columns_of(part))
        return tuple(dict.fromkeys(out))
    return (feature,)


class InformationRule:
    """The as-of rule for one declared feature set, one registry, one time.

    Construct once per run; every method is a pure function of the panel
    dates (and rows) it is handed, so the same rule serves the fold loop and a
    fitter's internal calibration rows alike.
    """

    def __init__(
        self,
        registry: Mapping[str, Mapping[str, object]],
        features: Sequence[str],
        *,
        decision_time: time,
    ) -> None:
        if not isinstance(decision_time, time):
            raise TypeError("decision_time must be a datetime.time")
        self.registry = registry
        self.features = tuple(features)
        self.decision_time = decision_time
        self._scheduled = _scheduled_blocks(registry)
        groups = [self._group(TARGET)]
        composed: List[str] = []
        for feature in dict.fromkeys(self.features):
            if feature in PER_FIELD_DERIVED_FEATURES:
                composed.append(feature)
            elif feature != TARGET:
                groups.append(self._group(feature))
        # A per-field derived feature is no read of its own: each input is read
        # as any declared input is, and the feature is computed from those
        # reads (`contract.PER_FIELD_DERIVED_FEATURES`, #88).
        named = {group.feature for group in groups}
        for feature in composed:
            for part in DERIVED_FEATURES[feature]:
                if part not in named:
                    groups.append(self._group(part))
                    named.add(part)
        self.groups: Tuple[_Group, ...] = tuple(groups)
        self.composed: Tuple[str, ...] = tuple(composed)
        # Every column the declaration reads, less the target's own.
        self.columns = tuple(
            dict.fromkeys(
                column
                for group in self.groups[1:]
                for column in group.columns
                if column not in TARGET_COLUMNS
            )
        )

    def _group(self, feature: str) -> _Group:
        if feature in CALENDAR_FEATURES:
            return _Group(feature, KIND_CALENDAR, (), (feature,))
        fields = field_sources_for_features((feature,))
        for pair in fields:
            if pair[0] not in self.registry:
                raise RegistryContractError(
                    f"{feature!r} reads {pair[0]}.{pair[1]}, and the registry "
                    f"declares no source {pair[0]!r}"
                )
        scheduled = [pair in self._scheduled for pair in fields]
        if any(scheduled) and not all(scheduled):
            raise RegistryContractError(
                f"{feature!r} reads {list(fields)}, of which only some are "
                f"scheduled; a feature is read at one row, so its fields must be "
                f"one kind"
            )
        columns = _columns_of(feature)
        if feature in TARGET_COLUMNS:
            # `sofr` or `iorb` declared on its own is still read with the target.
            return _Group(feature, KIND_OBSERVED, self._target_fields(), columns)
        return _Group(
            feature, KIND_SCHEDULED if all(scheduled) else KIND_OBSERVED, fields, columns
        )

    @staticmethod
    def _target_fields() -> Tuple[Tuple[str, str], ...]:
        return field_sources_for_features((TARGET,))

    # -- instants ---------------------------------------------------------

    def decision_instant(self, dates: Sequence[date], scored_index: int) -> datetime:
        """The declared decision time on the panel day before `scored_index`."""

        if scored_index < 1:
            raise SplitError(
                f"row {scored_index} has no panel day before it, so no decision instant"
            )
        return datetime.combine(
            dates[scored_index - 1], self.decision_time.replace(tzinfo=None)
        )

    def availability(
        self,
        dates: Sequence[date],
        fields: Tuple[Tuple[str, str], ...],
        position: int,
    ) -> datetime:
        """When every one of `fields` is observable for `dates[position]`.

        A field with no row-relative declaration cannot be read under the
        rule, and is refused rather than read at whatever row it sits on.
        """

        latest = datetime.min
        for source_id, field in fields:
            moment = declared_availability(self.registry, source_id, field, dates, position)
            if moment is None:
                raise RegistryContractError(
                    f"{source_id}.{field} declares no availability relative to its "
                    f"row (a snapshot_retrieved_at basis, or no days), so the as-of "
                    f"rule cannot say which of its rows was public at a decision "
                    f"instant; declare its lag before reading it"
                )
            latest = max(latest, moment)
        return latest

    def _latest(
        self,
        dates: Sequence[date],
        fields: Tuple[Tuple[str, str], ...],
        scored_index: int,
        deadline: datetime,
    ) -> int:
        """The latest row before `scored_index` whose `fields` are all observable.

        -1 when no such row exists. Scans back from the day before the scored
        row: every declared lag here is monotone in the row, so the first row
        that qualifies is the latest.
        """

        position = scored_index - 1
        while position >= 0:
            if self.availability(dates, fields, position) <= deadline:
                return position
            position -= 1
        return position

    def anchor(self, dates: Sequence[date], scored_index: int) -> int:
        """The latest row whose target is observable at `scored_index`'s decision.

        The label-observability boundary: labels at or before it are admissible
        for a fit made at that instant, and the target feature is read there.
        -1 when there is none.
        """

        deadline = self.decision_instant(dates, scored_index)
        return self._latest(dates, self._target_fields(), scored_index, deadline)

    # -- reads ------------------------------------------------------------

    def information_set(self, dates: Sequence[date], scored_index: int) -> InformationSet:
        """Every declared read for the forecast of `dates[scored_index]`."""

        deadline = self.decision_instant(dates, scored_index)
        anchor = self._latest(dates, self._target_fields(), scored_index, deadline)
        if anchor < 0:
            raise SplitError(
                f"no row's target is observable at the {deadline} decision that "
                f"scores {dates[scored_index]}"
            )
        reads = []
        for group in self.groups:
            if group.kind == KIND_CALENDAR:
                row, available = scored_index, None
            elif group.kind == KIND_SCHEDULED:
                row = scored_index
                available = self.availability(dates, group.fields, row)
            else:
                row = (
                    anchor
                    if group.fields == self._target_fields()
                    else self._latest(dates, group.fields, scored_index, deadline)
                )
                if row < 0:
                    raise SplitError(
                        f"{group.feature!r} has no row observable at the {deadline} "
                        f"decision that scores {dates[scored_index]}"
                    )
                available = self.availability(dates, group.fields, row)
            reads.append(
                FieldRead(
                    feature=group.feature,
                    kind=group.kind,
                    fields=group.fields,
                    row=row,
                    available_at=available,
                    rows=scored_index - row,
                    hours=(
                        None
                        if available is None
                        else (deadline - available).total_seconds() / 3600.0
                    ),
                )
            )
        return InformationSet(scored_index, deadline, anchor, tuple(reads))

    def check(self, dates: Sequence[date], info: InformationSet) -> None:
        """Both guards, over every read of one information set.

        Leakage: nothing read is observable only after the decision instant,
        and no observed read is at or after the scored row. Staleness: no
        observed read has an admissible row after it, and a scheduled or
        calendar read is at the scored row itself.

        Raises:
            LookAheadError: a read is newer than the decision instant.
            StaleReadError: a read is older than the latest admissible value.
        """

        deadline = self.decision_instant(dates, info.scored_index)
        if deadline != info.decision_instant:
            raise LookAheadError(
                f"the information set for {dates[info.scored_index]} names the "
                f"decision instant {info.decision_instant}, not {deadline}"
            )
        scored = info.scored_index
        for read in info.reads:
            where = f"{read.feature!r} for the forecast of {dates[scored]}"
            if read.row > scored or (read.kind == KIND_OBSERVED and read.row >= scored):
                raise LookAheadError(
                    f"{where} reads row {read.row} ({dates[read.row] if read.row < len(dates) else 'past the panel'}), "
                    f"which is not before the scored row; only a declared scheduled "
                    f"input may refer to the scored day"
                )
            if read.kind == KIND_CALENDAR:
                if read.row != scored:
                    raise StaleReadError(
                        f"{where} reads row {read.row}; a calendar column is known "
                        f"in advance and is read at the scored day"
                    )
                continue
            available = self.availability(dates, read.fields, read.row)
            if available > deadline:
                raise LookAheadError(
                    f"{where} reads {dates[read.row]}, first observable at "
                    f"{available}, after the {deadline} decision"
                )
            if read.kind == KIND_SCHEDULED:
                if read.row != scored:
                    raise StaleReadError(
                        f"{where} reads {dates[read.row]}; a scheduled input is "
                        f"read at the scored day, whose value was announced by "
                        f"{self.availability(dates, read.fields, scored)}"
                    )
                continue
            following = read.row + 1
            if following < scored and self.availability(dates, read.fields, following) <= deadline:
                raise StaleReadError(
                    f"{where} reads {dates[read.row]}, but {dates[following]} was "
                    f"observable at {self.availability(dates, read.fields, following)}, "
                    f"by the {deadline} decision; the forecast used an older value "
                    f"than the one public when it was made"
                )

    # -- what a model is handed --------------------------------------------

    def observation(
        self, rows: Sequence[DailyObservation], info: InformationSet
    ) -> DailyObservation:
        """The feature row a model reads: the anchor row, re-read per field.

        Dated at the anchor, so a model reading history by position (lags, a
        GARCH recursion, a trailing scale) finds it in its frame. The target's
        columns are the anchor's; each declared column is its own read's. An
        undeclared column is left as the anchor row carries it and is read by
        no model that passes the fold loops: `baseline._check_fitter_stayed_inside`
        refuses, with `LookAheadError`, any model whose `features_read` leaves
        the declaration -- which is the refusal a model reading one should get,
        rather than a data error about a hole put there to stop it.
        """

        anchor = rows[info.anchor]
        values: Dict[str, Optional[float]] = dict(anchor.values)
        taken: Dict[str, int] = {}
        for read, group in zip(info.reads, self.groups):
            if read.feature != group.feature:  # pragma: no cover - construction bug
                raise LookAheadError("reads and declared groups are out of step")
            for column in group.columns:
                if column in TARGET_COLUMNS:
                    continue
                if column in taken and taken[column] != read.row:
                    raise ValueError(
                        f"column {column!r} is read at row {taken[column]} for one "
                        f"declared feature and {read.row} for another"
                    )
                taken[column] = read.row
                values[column] = rows[read.row].values.get(column)
        return self._compose(DailyObservation(anchor.date, values))

    def _compose(self, row: DailyObservation) -> DailyObservation:
        """`row` with each per-field derived feature computed from its columns.

        In `observation` the columns are the inputs' own as-of reads, so the
        feature combines exactly what was public at the decision instant; in
        `frame` they are the training row's, masked where not yet observable,
        and a masked input makes the feature a hole.
        """

        if not self.composed:
            return row
        values = dict(row.values)
        values.update((name, getattr(row, name)) for name in self.composed)
        return DailyObservation(row.date, values)

    def frame(
        self, rows: Sequence[DailyObservation], info: InformationSet
    ) -> List[DailyObservation]:
        """The training frame at `info`'s decision instant.

        The prefix ending at the anchor -- every admissible label, and no
        other -- with each declared column's value a hole (`None`) on a row
        where it was not yet observable. Only the tail can be masked: a lag is
        monotone in the row, so the scan stops at the first row whose every
        declared column was observable.
        """

        frame = list(rows[: info.anchor + 1])
        observed = [
            group for group in self.groups[1:]
            if group.kind == KIND_OBSERVED and group.fields != self._target_fields()
        ]
        if not observed:
            return [self._compose(row) for row in frame]
        dates = [row.date for row in rows]
        deadline = info.decision_instant
        for position in range(len(frame) - 1, -1, -1):
            late = [
                column
                for group in observed
                if self.availability(dates, group.fields, position) > deadline
                for column in group.columns
                if column not in TARGET_COLUMNS
            ]
            if not late:
                break
            values = dict(frame[position].values)
            for column in late:
                values[column] = None
            frame[position] = DailyObservation(frame[position].date, values)
        return [self._compose(row) for row in frame]


def require_refit_every(refit_every: object) -> int:
    """Refuse anything but a deliberate positive number of scored days."""

    if not _is_int(refit_every) or refit_every < 1:
        raise ValueError(
            f"refit_every must be an int of at least 1, got {refit_every!r}"
        )
    return int(refit_every)


def refit_blocks(grid: Sequence[int], refit_every: int) -> Tuple[Tuple[int, ...], ...]:
    """The grid cut into consecutive blocks of `refit_every` scored rows.

    One fit per block, made at the decision instant of the block's first row;
    every row of the block is then forecast from its own decision instant's
    reads with that fit.
    """

    step = require_refit_every(refit_every)
    ordered = tuple(grid)
    return tuple(ordered[start : start + step] for start in range(0, len(ordered), step))


def fold_grid(
    dates: Sequence[date],
    registry: Mapping[str, Mapping[str, object]],
    *,
    decision_time: time,
    minimum_history: int,
) -> Tuple[int, ...]:
    """The scored rows: every row from the first with `minimum_history` labels.

    Built from the target's declarations alone, so it is one grid for every
    feature declaration on the same panel.
    """

    ensure_strictly_ascending(dates)
    if not _is_int(minimum_history) or minimum_history < 1:
        raise SplitError(f"minimum_history must be an int of at least 1, got {minimum_history!r}")
    target = InformationRule(registry, (TARGET,), decision_time=decision_time)
    for index in range(1, len(dates)):
        if target.anchor(dates, index) + 1 >= minimum_history:
            return tuple(range(index, len(dates)))
    raise SplitError(
        f"{len(dates)} observations from {dates[0]} to {dates[-1]} yield no "
        f"scored row with {minimum_history} observable labels before its decision"
    )


def information_summary(
    rule: InformationRule, infos: Sequence[InformationSet]
) -> Dict[str, object]:
    """Per-feature staleness over a run, for a record.

    For each declared feature: its kind, its fields, how many scored rows read
    it at each distance (`rows` before the scored row), and the least and most
    hours its value had been observable at the decision instant.
    """

    features: Dict[str, object] = {}
    for position, group in enumerate(rule.groups):
        counts: Dict[str, int] = {}
        hours = []
        for info in infos:
            read = info.reads[position]
            counts[str(read.rows)] = counts.get(str(read.rows), 0) + 1
            if read.hours is not None:
                hours.append(read.hours)
        features[group.feature] = {
            "kind": group.kind,
            "fields": [f"{source}.{field}" for source, field in group.fields],
            "rows_before_scored": dict(sorted(counts.items(), key=lambda kv: int(kv[0]))),
            "hours_observable": (
                None if not hours else {"min": min(hours), "max": max(hours)}
            ),
        }
    return {
        "rule": "as_of",
        "decision_instant": "decision_time on the panel day before the scored day",
        "features": features,
    }
