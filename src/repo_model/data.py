"""Point-in-time daily panel loading and validation."""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence


REQUIRED_FIELDS = ("date", "sofr", "iorb")
OPTIONAL_NUMERIC_FIELDS = (
    "sofr_volume",
    "sofr_p25",
    "sofr_p75",
    "tgcr",
    "bgcr",
    "reserve_balances",
    "tga",
    "on_rrp",
    "treasury_settlement",
    "dealer_treasury_position",
    "mmf_assets",
    "quarter_end",
    "tax_date",
)
POINT_IN_TIME_FIELDS = (
    "series_id",
    "ref_date",
    "available_at",
    "value",
    "vintage_id",
    "source_sha",
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_STRESS_THRESHOLDS = (
    Path(__file__).parents[2] / "metadata" / "stress_thresholds.json"
)


class DataContractError(ValueError):
    """Raised when a modeling panel violates its declared contract."""


@dataclass(frozen=True)
class DailyObservation:
    date: date
    values: Mapping[str, Optional[float]]

    @property
    def spread_bps(self) -> float:
        return 100.0 * (float(self.values["sofr"]) - float(self.values["iorb"]))


@dataclass(frozen=True)
class PointInTimeObservation:
    """One immutable observation from a specific source vintage."""

    series_id: str
    ref_date: date
    available_at: datetime
    value: float
    vintage_id: str
    source_sha: str


@dataclass(frozen=True)
class AuditReport:
    row_count: int
    start_date: date
    end_date: date
    missing_counts: Mapping[str, int]
    warnings: Sequence[str]


@dataclass(frozen=True)
class SeriesQuality:
    series_id: str
    observation_count: int
    reference_date_count: int
    start_date: date
    end_date: date
    missing_reference_dates: int
    missing_rate: float
    revised_reference_dates: int
    revision_rows: int
    largest_absolute_revision: Optional[float]


@dataclass(frozen=True)
class CrossSectionCoverage:
    """Reporting-entity coverage of one cross-section of a cross-sectional source.

    A source that publishes a periodic cross-section can emit a `ref_date` that
    is present, parseable and internally consistent while representing a small
    fraction of its universe. Missingness reporting cannot see it -- every row
    is there -- and an accounting identity holds just as well on a fraction of a
    market as on all of it. The only thing that distinguishes the two is how
    many entities reported, which is what this records.

    `entity_count` is a count of distinct reporting entities, never a value
    total: the values are the thing under suspicion, so a value threshold would
    be circular.

    `submission_types` is a corroborating record and never an input to the
    decision: how many submissions of each declared type the cross-section
    carries, as `(type, count)` pairs. It is free -- the source states it -- and
    it lets a reader see at a glance that an excluded month was a handful of
    amendments rather than a real month the floor got wrong. It must not become
    a filter: a legitimately amended complete month is entirely amendments and
    would be discarded by one.

    `absent_fields` names the panel series the archive could supply no
    observation of for this cross-section -- because it does not carry the table
    that holds them, or because the report month has no declared
    `INVESTMENTCATEGORY` vocabulary. It is not a coverage failure and does not
    affect `admitted`: an archive filed before 2024-06-10 carries no daily
    shareholder-flow table because the data did not exist, and its balance sheet
    is no less complete for it. Recording it is what keeps "we have no
    observation" from being read off the panel as "we observed nothing", which
    is the same absent-is-not-zero distinction one level up from the rows.
    """

    source_id: str
    ref_date: date
    entity_unit: str
    entity_count: int
    declared_floor: int
    admitted: bool
    row_count: int
    submission_types: tuple = ()
    absent_fields: tuple = ()

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "ref_date": self.ref_date.isoformat(),
            "entity_unit": self.entity_unit,
            "entity_count": self.entity_count,
            "declared_floor": self.declared_floor,
            "rows": self.row_count,
            "submission_types": {
                str(name): int(count) for name, count in self.submission_types
            },
            "absent_fields": list(self.absent_fields),
            "reason": (
                "reporting entities below the coverage floor declared in the "
                "source registry"
            ),
        }


# The three answers a declared identity can give about one `ref_date`. There
# used to be two, and the missing one was not "violated" -- it was this:
#
#   held           every declared term was observed and the residual is within
#                  the declared tolerance
#   violated       every declared term was observed and the residual is not
#   not_evaluable  at least one declared term has no observation for that
#                  `ref_date`, so no residual exists to compare
#
# `not_evaluable` is the one that has to be named. A check that never ran and a
# check that passed are indistinguishable from the outside unless the code says
# which happened, and the failure mode this repo keeps meeting is a guard that
# reads as vigilance because nothing recorded that its input was absent. It is
# the degenerate case of an identity anchored to the thing it is checking: not a
# check that cannot fail because both sides moved together, but a check that
# cannot fail because it has no terms.
IDENTITY_HELD = "held"
IDENTITY_VIOLATED = "violated"
IDENTITY_NOT_EVALUABLE = "not_evaluable"

# The verdict an identity earns over a whole panel when some of its reference
# dates could not be checked. Deliberately not spelled `held`, and deliberately
# not `not_evaluable` either: both would be false. It held where it ran, and a
# caller testing for `held` gets a mismatch, which is the point.
IDENTITY_HELD_WHERE_EVALUABLE = "held_where_evaluable"


@dataclass(frozen=True)
class UnevaluatedIdentity:
    """One `(source, identity, ref_date)` the identity could not be checked on.

    `absent_fields` names the declared terms that have no observation for that
    `ref_date`. Recording the verdict without the terms would be a claim a
    reader cannot act on -- "it did not evaluate" says nothing about whether the
    remedy is a field mapping, a missing table, or a source that never collected
    the column. It is the same reason `CrossSectionCoverage.absent_fields`
    exists, one level up: an absence is only legible once it is named.

    The absent term is never read as `0.0` to make the sum evaluate. An identity
    that "holds" because a missing term was substituted with a zero is strictly
    worse than one that visibly did not run, because the first destroys the
    evidence that anything was missing.
    """

    source_id: str
    identity: str
    ref_date: date
    absent_fields: tuple = ()

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "identity": self.identity,
            "ref_date": self.ref_date.isoformat(),
            "verdict": IDENTITY_NOT_EVALUABLE,
            "absent_fields": list(self.absent_fields),
            "reason": (
                "a declared term of this identity has no observation for this "
                "reference date; the identity was not checked"
            ),
        }


@dataclass(frozen=True)
class IdentityEvaluation:
    """What one declared identity actually established over a panel.

    This replaces a bare maximum residual as the thing a caller reads to learn
    "the identities are fine". A float alone cannot answer the question, because
    it is computed only over the reference dates where every term was present
    and carries no trace of the ones where it was not -- so a panel whose first
    5.5 years cannot be checked at all reports exactly the same number as one
    that was checked throughout.

    `verdict` is therefore `held` only when nothing was left unchecked. When
    some reference dates could not be evaluated it is
    `held_where_evaluable`, which no caller can mistake for the former.
    """

    source_id: str
    name: str
    maximum_residual: Optional[float]
    evaluated_ref_dates: int
    unevaluated: tuple = ()

    @property
    def verdict(self) -> str:
        if self.unevaluated:
            return IDENTITY_HELD_WHERE_EVALUABLE
        return IDENTITY_HELD

    @property
    def fully_evaluated(self) -> bool:
        return not self.unevaluated

    @property
    def absent_fields(self) -> tuple:
        """Every declared term absent on at least one unevaluated date."""

        names: set = set()
        for item in self.unevaluated:
            names.update(item.absent_fields)
        return tuple(sorted(names))

    def as_dict(self) -> Mapping[str, object]:
        return {
            "verdict": self.verdict,
            "maximum_residual": self.maximum_residual,
            "evaluated_ref_dates": self.evaluated_ref_dates,
            "unevaluated_ref_dates": [item.as_dict() for item in self.unevaluated],
        }


@dataclass(frozen=True)
class PointInTimeAuditReport:
    row_count: int
    reference_date_count: int
    start_date: date
    end_date: date
    series: Mapping[str, SeriesQuality]
    missing_series: Mapping[str, int]
    warnings: Sequence[str]
    excluded_cross_sections: Sequence[CrossSectionCoverage] = ()
    unevaluated_identities: Sequence[UnevaluatedIdentity] = ()

    def as_dict(self) -> Mapping[str, object]:
        return {
            "rows": self.row_count,
            "reference_dates": self.reference_date_count,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "series": {
                series_id: {
                    "observations": quality.observation_count,
                    "reference_dates": quality.reference_date_count,
                    "start_date": quality.start_date.isoformat(),
                    "end_date": quality.end_date.isoformat(),
                    "missing_reference_dates": quality.missing_reference_dates,
                    "missing_rate": quality.missing_rate,
                    "revised_reference_dates": quality.revised_reference_dates,
                    "revision_rows": quality.revision_rows,
                    "largest_absolute_revision": quality.largest_absolute_revision,
                }
                for series_id, quality in sorted(self.series.items())
            },
            "missing_series": dict(sorted(self.missing_series.items())),
            # Deliberately its own key, never folded into `missing_series` or a
            # series' `missing_reference_dates`. "We declined to admit this
            # cross-section" and "this cross-section had gaps" are different
            # facts about the data, the same way a structural zero and a missing
            # observation are, and a reader has to be able to tell them apart.
            "excluded_cross_sections": [
                coverage.as_dict()
                for coverage in sorted(
                    self.excluded_cross_sections,
                    key=lambda item: (item.source_id, item.ref_date),
                )
            ],
            # Its own key for the same reason excluded_cross_sections is its
            # own key. "This identity was checked and held" and "this identity
            # was not checked" are different facts, and a reader who cannot
            # tell them apart will read the second as the first -- which is
            # the whole defect this records.
            "unevaluated_identities": [
                item.as_dict()
                for item in sorted(
                    self.unevaluated_identities,
                    key=lambda item: (item.source_id, item.identity, item.ref_date),
                )
            ],
            "warnings": list(self.warnings),
        }


def _parse_float(raw: str, field: str, row_number: int) -> Optional[float]:
    value = raw.strip()
    if value == "":
        return None
    try:
        parsed = float(value)
    except ValueError as exc:
        raise DataContractError(
            f"row {row_number}: {field!r} must be numeric, got {raw!r}"
        ) from exc
    if not math.isfinite(parsed):
        raise DataContractError(f"row {row_number}: {field!r} must be finite")
    return parsed


def load_daily_panel(path: Path) -> List[DailyObservation]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DataContractError("CSV has no header")
        missing_headers = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
        if missing_headers:
            raise DataContractError(f"missing required columns: {', '.join(missing_headers)}")

        observations: List[DailyObservation] = []
        numeric_fields = [field for field in reader.fieldnames if field != "date"]
        for row_number, row in enumerate(reader, start=2):
            try:
                observation_date = date.fromisoformat(row["date"].strip())
            except (AttributeError, ValueError) as exc:
                raise DataContractError(
                    f"row {row_number}: date must use YYYY-MM-DD"
                ) from exc
            values = {
                field: _parse_float(row.get(field, ""), field, row_number)
                for field in numeric_fields
            }
            for field in ("sofr", "iorb"):
                if values.get(field) is None:
                    raise DataContractError(f"row {row_number}: {field!r} is required")
            observations.append(DailyObservation(observation_date, values))

    if not observations:
        raise DataContractError("CSV contains no observations")
    return observations


def _required_text(row: Mapping[str, Optional[str]], field: str, row_number: int) -> str:
    raw = row.get(field)
    value = raw.strip() if raw is not None else ""
    if not value:
        raise DataContractError(f"row {row_number}: {field!r} is required")
    return value


def _parse_available_at(raw: str, row_number: int) -> datetime:
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DataContractError(
            f"row {row_number}: 'available_at' must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DataContractError(
            f"row {row_number}: 'available_at' must include a UTC offset"
        )
    return parsed


def load_point_in_time_panel(
    path: Path,
    *,
    cutoff: Optional[datetime] = None,
) -> List[PointInTimeObservation]:
    """Load the canonical long panel, optionally filtered by observable cutoff.

    Revisions remain separate rows. Filtering is based only on ``available_at``;
    the loader never fills or carries values across reference dates.
    """

    if cutoff is not None and (cutoff.tzinfo is None or cutoff.utcoffset() is None):
        raise DataContractError("cutoff must include a UTC offset")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DataContractError("CSV has no header")
        if len(reader.fieldnames) != len(POINT_IN_TIME_FIELDS) or set(
            reader.fieldnames
        ) != set(POINT_IN_TIME_FIELDS):
            raise DataContractError(
                "point-in-time CSV columns must be exactly: "
                + ", ".join(POINT_IN_TIME_FIELDS)
            )

        observations: List[PointInTimeObservation] = []
        for row_number, row in enumerate(reader, start=2):
            series_id = _required_text(row, "series_id", row_number)
            raw_ref_date = _required_text(row, "ref_date", row_number)
            try:
                ref_date = date.fromisoformat(raw_ref_date)
            except ValueError as exc:
                raise DataContractError(
                    f"row {row_number}: 'ref_date' must use YYYY-MM-DD"
                ) from exc
            available_at = _parse_available_at(
                _required_text(row, "available_at", row_number),
                row_number,
            )
            value = _parse_float(
                _required_text(row, "value", row_number),
                "value",
                row_number,
            )
            if value is None:  # pragma: no cover - _required_text rules this out
                raise DataContractError(f"row {row_number}: 'value' is required")
            vintage_id = _required_text(row, "vintage_id", row_number)
            source_sha = _required_text(row, "source_sha", row_number)
            if not SHA256_PATTERN.fullmatch(source_sha):
                raise DataContractError(
                    f"row {row_number}: 'source_sha' must be a lowercase SHA-256 digest"
                )
            observations.append(
                PointInTimeObservation(
                    series_id=series_id,
                    ref_date=ref_date,
                    available_at=available_at,
                    value=value,
                    vintage_id=vintage_id,
                    source_sha=source_sha,
                )
            )

    if not observations:
        raise DataContractError("point-in-time CSV contains no observations")

    availability = [row.available_at for row in observations]
    if availability != sorted(availability):
        raise DataContractError("point-in-time rows must be appended in availability order")

    vintage_keys = [(row.series_id, row.ref_date, row.vintage_id) for row in observations]
    if len(vintage_keys) != len(set(vintage_keys)):
        raise DataContractError("duplicate series/ref_date/vintage_id row")

    publication_keys = [
        (row.series_id, row.ref_date, row.available_at) for row in observations
    ]
    if len(publication_keys) != len(set(publication_keys)):
        raise DataContractError("duplicate series/ref_date/available_at row")

    if cutoff is None:
        return observations
    return [row for row in observations if row.available_at <= cutoff]


def audit_point_in_time_panel(
    observations: Iterable[PointInTimeObservation],
    *,
    expected_ref_dates: Optional[Mapping[str, Iterable[date]]] = None,
    excluded_cross_sections: Optional[Iterable[CrossSectionCoverage]] = None,
    unevaluated_identities: Optional[Iterable[UnevaluatedIdentity]] = None,
) -> PointInTimeAuditReport:
    """Summarize coverage and revisions without treating a revision as coverage.

    By default, missingness is measured against the union of dates represented by
    the supplied panel. Callers with a source calendar may pass a per-series date
    grid in ``expected_ref_dates``; this is preferable for low-frequency series.
    No value is imputed or carried forward by this report.
    """

    rows = list(observations)
    if not rows:
        raise DataContractError("point-in-time panel contains no observations")
    if [row.available_at for row in rows] != sorted(row.available_at for row in rows):
        raise DataContractError("point-in-time rows must be appended in availability order")

    panel_dates = sorted({row.ref_date for row in rows})
    by_series: Dict[str, List[PointInTimeObservation]] = {}
    for row in rows:
        by_series.setdefault(row.series_id, []).append(row)

    series_report: Dict[str, SeriesQuality] = {}
    warnings: List[str] = []
    for series_id, series_rows in sorted(by_series.items()):
        by_reference: Dict[date, List[PointInTimeObservation]] = {}
        for row in series_rows:
            by_reference.setdefault(row.ref_date, []).append(row)
        reference_dates = sorted(by_reference)
        if expected_ref_dates is None:
            expected = set(panel_dates)
        else:
            expected = set(expected_ref_dates.get(series_id, reference_dates))
        observed = set(reference_dates)
        missing = len(expected - observed)
        denominator = len(expected)
        revised = 0
        revision_rows = 0
        largest_revision: Optional[float] = None
        for ref_date, vintages in by_reference.items():
            ordered = sorted(vintages, key=lambda row: row.available_at)
            if len(ordered) <= 1:
                continue
            revised += 1
            revision_rows += len(ordered) - 1
            for previous, current in zip(ordered, ordered[1:]):
                magnitude = abs(current.value - previous.value)
                largest_revision = (
                    magnitude
                    if largest_revision is None
                    else max(largest_revision, magnitude)
                )
            if any(
                current.available_at <= previous.available_at
                for previous, current in zip(ordered, ordered[1:])
            ):
                warnings.append(
                    f"{series_id} {ref_date}: revisions do not have increasing availability"
                )
        series_report[series_id] = SeriesQuality(
            series_id=series_id,
            observation_count=len(series_rows),
            reference_date_count=len(reference_dates),
            start_date=reference_dates[0],
            end_date=reference_dates[-1],
            missing_reference_dates=missing,
            missing_rate=(missing / denominator if denominator else 0.0),
            revised_reference_dates=revised,
            revision_rows=revision_rows,
            largest_absolute_revision=largest_revision,
        )

    return PointInTimeAuditReport(
        row_count=len(rows),
        reference_date_count=len(panel_dates),
        start_date=panel_dates[0],
        end_date=panel_dates[-1],
        series=series_report,
        missing_series={
            series_id: len(set(expected_dates))
            for series_id, expected_dates in (expected_ref_dates or {}).items()
            if series_id not in by_series
        },
        warnings=warnings,
        excluded_cross_sections=tuple(excluded_cross_sections or ()),
        unevaluated_identities=tuple(unevaluated_identities or ()),
    )


def expected_ref_dates_from_registry(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
) -> Mapping[str, Sequence[date]]:
    """Build per-series coverage grids from declared native-frequency peers.

    Within each source and cadence, the most complete series is the reference
    calendar. This avoids comparing a weekly series with a daily series or a
    2018-start series with a 1954-start series. It also respects actual source
    holidays without silently inventing a holiday calendar.
    """

    rows = list(observations)
    dates_by_series: Dict[str, set[date]] = {}
    for row in rows:
        dates_by_series.setdefault(row.series_id, set()).add(row.ref_date)

    expected: Dict[str, Sequence[date]] = {}
    declared_fields: set[str] = set()
    for source_id, source in registry.items():
        raw_frequencies = source.get("field_frequencies")
        if not isinstance(raw_frequencies, Mapping):
            continue
        fields = [str(field) for field in source.get("fields", [])]
        if set(raw_frequencies) != set(fields):
            raise DataContractError(
                f"{source_id}: field_frequencies must declare every source field"
            )
        overlap = declared_fields.intersection(fields)
        if overlap:
            raise DataContractError(
                f"series belong to multiple field-frequency declarations: {sorted(overlap)}"
            )
        declared_fields.update(fields)
        by_frequency: Dict[str, List[str]] = {}
        for field in fields:
            frequency = raw_frequencies[field]
            if frequency not in {
                "calendar_daily", "business_daily", "weekly", "monthly", "event"
            }:
                raise DataContractError(
                    f"{source_id}: unsupported frequency {frequency!r} for {field}"
                )
            by_frequency.setdefault(str(frequency), []).append(field)
        for frequency, peers in by_frequency.items():
            present = [field for field in peers if dates_by_series.get(field)]
            if not present:
                continue
            anchor = max(present, key=lambda field: len(dates_by_series[field]))
            anchor_dates = dates_by_series[anchor]
            absent = [field for field in peers if field not in present]
            for field in absent:
                expected[field] = tuple(sorted(anchor_dates))
            for field in present:
                own_dates = dates_by_series[field]
                if frequency == "event":
                    expected[field] = tuple(sorted(own_dates))
                    continue
                start, end = min(own_dates), max(own_dates)
                expected[field] = tuple(
                    sorted(value for value in anchor_dates if start <= value <= end)
                )

    for series_id, observed in dates_by_series.items():
        expected.setdefault(series_id, tuple(sorted(observed)))
    return expected


def write_point_in_time_audit_report(
    observations: Iterable[PointInTimeObservation],
    path: Path,
    *,
    expected_ref_dates: Optional[Mapping[str, Iterable[date]]] = None,
    excluded_cross_sections: Optional[Iterable[CrossSectionCoverage]] = None,
    unevaluated_identities: Optional[Iterable[UnevaluatedIdentity]] = None,
) -> PointInTimeAuditReport:
    """Write a deterministic JSON missingness/revision report."""

    report = audit_point_in_time_panel(
        observations,
        expected_ref_dates=expected_ref_dates,
        excluded_cross_sections=excluded_cross_sections,
        unevaluated_identities=unevaluated_identities,
    )
    payload = json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)
    return report


def declared_coverage_floor(
    source_id: str,
    source: Mapping[str, object],
) -> tuple[str, int]:
    """Read one source's declared cross-section coverage floor.

    Returns `(entity_unit, minimum_reporting_entities)`. Raises if the source
    does not declare one, or declares one that cannot guard anything.

    Fails closed on purpose. An adapter reaches this function only because it
    knows how to count that source's reporting entities, and a counted quantity
    with no declared floor is a measurement nothing acts on. The registry is
    where the floor lives -- it is a claim about the source, not about the code,
    and Track A owns the registry.
    """

    declaration = source.get("cross_section")
    if not isinstance(declaration, Mapping):
        raise DataContractError(
            f"{source_id}: emits cross-sections but the registry declares no "
            "cross_section coverage floor"
        )
    permitted = {"entity_unit", "minimum_reporting_entities", "note"}
    unknown = sorted(set(declaration) - permitted)
    if unknown:
        raise DataContractError(
            f"{source_id}: cross_section has unpermitted keys {unknown}"
        )
    entity_unit = declaration.get("entity_unit")
    if not isinstance(entity_unit, str) or not entity_unit.strip():
        raise DataContractError(
            f"{source_id}: cross_section.entity_unit must be a non-empty string "
            "naming what is counted"
        )
    floor = declaration.get("minimum_reporting_entities")
    if isinstance(floor, bool) or not isinstance(floor, int):
        raise DataContractError(
            f"{source_id}: cross_section.minimum_reporting_entities must be an integer"
        )
    if floor < 1:
        # The prohibited silent zero, written down as data. A floor of 0 admits
        # every cross-section and reads, to the next person, as a check that ran.
        raise DataContractError(
            f"{source_id}: cross_section.minimum_reporting_entities must be at "
            f"least 1; {floor} admits every cross-section and guards nothing"
        )
    return entity_unit.strip(), floor


def validate_publication_gaps(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
) -> Mapping[str, int]:
    """Fail if observed ref-date publication gaps exceed a declared bound."""

    field_bounds: Dict[str, tuple[str, int]] = {}
    for source_id, source in registry.items():
        lag = source.get("release_lag")
        if not isinstance(lag, Mapping) or lag.get("basis") != "ref_date":
            continue
        bound = lag.get("worst_case_calendar_days")
        if isinstance(bound, bool) or not isinstance(bound, int):
            raise DataContractError(
                f"{source_id}: ref_date source lacks a valid publication-gap bound"
            )
        for field in source.get("fields", []):
            if field in field_bounds:
                raise DataContractError(f"series {field!r} belongs to multiple sources")
            field_bounds[str(field)] = (source_id, bound)

    worst: Dict[str, int] = {}
    for row in observations:
        if row.series_id not in field_bounds:
            continue
        source_id, bound = field_bounds[row.series_id]
        gap = (row.available_at.date() - row.ref_date).days
        if gap < 0:
            raise DataContractError(
                f"{row.series_id} {row.ref_date}: available_at predates ref_date"
            )
        worst[row.series_id] = max(worst.get(row.series_id, 0), gap)
        if gap > bound:
            raise DataContractError(
                f"{row.series_id} was published {gap} calendar days after its "
                f"ref_date, but {source_id} declares {bound}"
            )
    return worst


def _identity_verdict(
    left_fields: Sequence[str],
    right_fields: Sequence[str],
    values: Mapping[str, Optional[float]],
    tolerance: float,
) -> tuple:
    """Answer one declared identity on one reference date.

    Returns `(verdict, residual, absent_fields)`. The verdict is one of
    `IDENTITY_HELD`, `IDENTITY_VIOLATED` or `IDENTITY_NOT_EVALUABLE`; the
    residual is `None` for the last, because on that reference date there is no
    residual -- not a large one, not a zero one, none.

    An absent term is never read as `0.0`. The sums are not formed at all when
    a term is missing, so nothing here can turn "we did not observe it" into
    "we observed nothing". Substituting a zero would make the identity evaluate
    and, on a balance sheet, would usually make it fail loudly -- but on a panel
    where the missing terms sit on the same side it can just as easily make it
    hold, and an identity that holds because a missing term was imputed is worse
    than one that visibly did not run: the first destroys the evidence.
    """

    absent = tuple(
        field
        for field in (*left_fields, *right_fields)
        if values.get(field) is None
    )
    if absent:
        return IDENTITY_NOT_EVALUABLE, None, absent
    left_value = sum(float(values[field]) for field in left_fields)
    right_value = sum(float(values[field]) for field in right_fields)
    residual = abs(left_value - right_value)
    verdict = IDENTITY_HELD if residual <= tolerance else IDENTITY_VIOLATED
    return verdict, residual, ()


def validate_accounting_identities(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
) -> Mapping[str, "IdentityEvaluation"]:
    """Validate declared additive identities on the latest supplied vintages.

    Returns one `IdentityEvaluation` per declared identity, keyed
    `"{source_id}:{name}"`. Deliberately not a bare maximum residual any more.
    That float was computed over the intersection of the declared terms'
    reference dates, so a panel whose first years cannot be checked at all
    produced exactly the same answer as one checked throughout, and a caller
    asking "are the identities fine?" could not tell the two apart. `verdict` is
    `held` only when every reference date any term was observed on was actually
    checked.

    A violated identity still raises, as it always did. An unevaluable reference
    date does not raise: it is recorded, named term by named term. Which
    reference dates belong in the panel is a policy question and it is not this
    function's to answer -- but it can no longer be answered by accident.
    """

    latest = {}
    for row in observations:
        key = (row.series_id, row.ref_date)
        previous = latest.get(key)
        if previous is None or row.available_at > previous.available_at:
            latest[key] = row

    evaluations: Dict[str, IdentityEvaluation] = {}
    for source_id, source in registry.items():
        identities = source.get("identities", [])
        if not isinstance(identities, list):
            raise DataContractError(f"{source_id}: identities must be a list")
        for identity in identities:
            if not isinstance(identity, Mapping):
                raise DataContractError(f"{source_id}: identity must be an object")
            name = str(identity.get("name") or "").strip()
            left = identity.get("left")
            right = identity.get("right")
            tolerance = identity.get("tolerance")
            if (
                not name
                or not isinstance(left, list)
                or not isinstance(right, list)
                or not isinstance(tolerance, Mapping)
            ):
                raise DataContractError(f"{source_id}: malformed accounting identity")
            absolute = tolerance.get("absolute")
            if isinstance(absolute, bool) or not isinstance(absolute, (int, float)):
                raise DataContractError(f"{source_id}: identity {name} has invalid tolerance")
            left_fields = [str(field) for field in left]
            right_fields = [str(field) for field in right]
            fields = [*left_fields, *right_fields]
            dates_by_field = {
                field: {ref_date for series_id, ref_date in latest if series_id == field}
                for field in fields
            }
            complete_dates = set.intersection(*dates_by_field.values()) if fields else set()
            if not complete_dates:
                raise DataContractError(
                    f"{source_id}: identity {name} has no complete reference date"
                )
            # The union, not the intersection. Every reference date on which any
            # declared term was observed is a date this identity has something
            # to say about -- including "I could not be checked here". Iterating
            # the intersection is what made 5.5 years of an unchecked balance
            # sheet invisible: those dates were not failing the identity, they
            # were never reaching it.
            observed_dates = set().union(*dates_by_field.values()) if fields else set()
            maximum = 0.0
            unevaluated: List[UnevaluatedIdentity] = []
            for ref_date in sorted(observed_dates):
                values = {
                    field: (
                        latest[(field, ref_date)].value
                        if (field, ref_date) in latest
                        else None
                    )
                    for field in fields
                }
                verdict, residual, absent = _identity_verdict(
                    left_fields, right_fields, values, float(absolute)
                )
                if verdict == IDENTITY_NOT_EVALUABLE:
                    unevaluated.append(
                        UnevaluatedIdentity(
                            source_id=source_id,
                            identity=name,
                            ref_date=ref_date,
                            absent_fields=absent,
                        )
                    )
                    continue
                if verdict == IDENTITY_VIOLATED:
                    raise DataContractError(
                        f"{source_id}: identity {name} residual {residual:g} exceeds "
                        f"tolerance {float(absolute):g} on {ref_date}"
                    )
                maximum = max(maximum, residual)
            evaluations[f"{source_id}:{name}"] = IdentityEvaluation(
                source_id=source_id,
                name=name,
                maximum_residual=maximum,
                evaluated_ref_dates=len(observed_dates) - len(unevaluated),
                unevaluated=tuple(unevaluated),
            )
    return evaluations


def load_stress_thresholds(
    path: Path = DEFAULT_STRESS_THRESHOLDS,
) -> Mapping[str, object]:
    """Load and validate the versioned stress-target declaration."""

    try:
        declaration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"cannot load stress threshold metadata: {exc}") from exc
    if not isinstance(declaration, dict):
        raise DataContractError("stress threshold metadata must be an object")
    if isinstance(declaration.get("version"), bool) or not isinstance(
        declaration.get("version"), int
    ):
        raise DataContractError("stress threshold metadata needs an integer version")
    if declaration.get("primary_rule") != "fixed_bp":
        raise DataContractError("stress threshold primary_rule must be 'fixed_bp'")
    raw_taus = declaration.get("taus_bp")
    if not isinstance(raw_taus, list):
        raise DataContractError("stress threshold metadata needs a taus_bp list")
    try:
        taus = tuple(float(tau) for tau in raw_taus)
    except (TypeError, ValueError) as exc:
        raise DataContractError("stress thresholds must be numeric") from exc
    if taus != (5.0, 10.0, 20.0, 50.0):
        raise DataContractError("stress thresholds must be exactly 5, 10, 20, and 50 bp")
    expected_columns = [f"stress_gt_{tau:g}bp" for tau in taus]
    if declaration.get("label_columns") != expected_columns:
        raise DataContractError("stress label_columns must match the declared taus_bp")
    secondary = declaration.get("secondary_rule")
    if not isinstance(secondary, dict):
        raise DataContractError("stress threshold metadata needs a secondary_rule")
    if secondary.get("type") != "trailing_percentile":
        raise DataContractError("secondary stress rule must be 'trailing_percentile'")
    if secondary.get("history") != "rows_strictly_before_label_row":
        raise DataContractError("trailing stress rule must use only pre-label rows")
    if secondary.get("full_sample_allowed") is not False:
        raise DataContractError("full-sample stress percentiles are prohibited")
    return declaration


def _finite_values(values: Sequence[float]) -> List[float]:
    checked: List[float] = []
    for position, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise DataContractError(f"stress value {position} is not numeric")
        number = float(value)
        if not math.isfinite(number):
            raise DataContractError(f"stress value {position} is not finite")
        checked.append(number)
    return checked


def stress_label_threshold(
    values: Sequence[float],
    index: int,
    window: int,
    probability: float,
) -> float:
    """Return a trailing percentile based strictly on rows before ``index``."""

    if isinstance(index, bool) or not isinstance(index, int):
        raise DataContractError("stress label index must be an integer")
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        raise DataContractError("stress label window must be a positive integer")
    if index < window or index > len(values):
        raise DataContractError("stress label threshold has insufficient trailing history")
    if isinstance(probability, bool) or not isinstance(probability, (int, float)):
        raise DataContractError("stress label probability must be numeric")
    quantile = float(probability)
    if not 0.0 <= quantile <= 1.0:
        raise DataContractError("stress label probability must be in [0, 1]")

    history = sorted(_finite_values(values[index - window : index]))
    position = (len(history) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return history[lower]
    weight = position - lower
    return history[lower] * (1.0 - weight) + history[upper] * weight


def fixed_bp_stress_label_columns(
    spreads_bp: Sequence[float],
    declaration: Optional[Mapping[str, object]] = None,
) -> List[Mapping[str, int]]:
    """Build the primary state-label columns from declared fixed thresholds."""

    metadata = declaration or load_stress_thresholds()
    if metadata.get("primary_rule") != "fixed_bp":
        raise DataContractError("fixed-bp labels require primary_rule 'fixed_bp'")
    raw_taus = metadata.get("taus_bp")
    if not isinstance(raw_taus, (list, tuple)):
        raise DataContractError("fixed-bp labels require taus_bp")
    taus = _finite_values(raw_taus)  # type: ignore[arg-type]
    values = _finite_values(spreads_bp)
    return [
        {f"stress_gt_{tau:g}bp": int(spread > tau) for tau in taus}
        for spread in values
    ]


def audit_panel(observations: Iterable[DailyObservation]) -> AuditReport:
    rows = list(observations)
    if not rows:
        raise DataContractError("panel contains no observations")

    dates = [row.date for row in rows]
    if dates != sorted(dates):
        raise DataContractError("dates must be sorted in ascending order")
    duplicates = sorted({value for value in dates if dates.count(value) > 1})
    if duplicates:
        raise DataContractError(f"duplicate dates: {', '.join(map(str, duplicates))}")

    all_fields = sorted({field for row in rows for field in row.values})
    missing_counts: Dict[str, int] = {
        field: sum(row.values.get(field) is None for row in rows) for field in all_fields
    }
    warnings: List[str] = []
    for index, row in enumerate(rows, start=1):
        values = row.values
        if values.get("sofr_p25") is not None and values.get("sofr_p75") is not None:
            if values["sofr_p25"] > values["sofr_p75"]:  # type: ignore[operator]
                warnings.append(f"{row.date}: SOFR p25 exceeds p75")
        for field in ("sofr_volume", "reserve_balances", "tga", "on_rrp"):
            if values.get(field) is not None and values[field] < 0:  # type: ignore[operator]
                warnings.append(f"{row.date}: {field} is negative")
        for field in ("quarter_end", "tax_date"):
            if values.get(field) not in (None, 0.0, 1.0):
                warnings.append(f"{row.date}: {field} should be 0 or 1")

    return AuditReport(
        row_count=len(rows),
        start_date=dates[0],
        end_date=dates[-1],
        missing_counts=missing_counts,
        warnings=warnings,
    )
