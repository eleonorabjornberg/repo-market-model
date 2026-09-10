"""Point-in-time daily panel loading and validation."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from repo_model.contract import (
    resolve_identity_tolerance,
    validate_identity_tolerance,
)


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

    `unmatched_derived_fields` is a **third** kind of absence, not more entries
    in `absent_fields`, and that is why it is a separate field. `absent_fields`
    says the archive could supply no observation: the table is not there, or the
    report month has no declared vocabulary to read it with. This says the
    opposite about the input and the same thing about the output -- the table was
    present, readable and parsed, the field this one derives from *was* observed
    for this cross-section, and the derivation ran over those very rows and
    matched none of them. Folding the two together would lose the distinction
    that makes the second worth recording: "we could not look" and "we looked and
    found nothing" are different facts, and only the second is evidence about the
    market.

    Each entry is a `(field, disposition)` pair, the same shape as
    `submission_types` above, where `disposition` is one of
    `DERIVED_ABSENCE_DECLARED_ZERO` or `DERIVED_ABSENCE_UNDECLARED` -- whether
    the source registry declares that field a structural zero at all. That is
    the difference between "these funds held no Fed ON RRP" and "we never found
    it", which is the sentence the published limitation says this repository
    cannot currently write. It is recorded and never resolved: no `0.0` row is
    emitted either way, because coercing an absent declared field to zero
    destroys the distinction the structural-zero declaration exists to preserve.

    Like `absent_fields` it does not affect `admitted`, and it is recorded for
    excluded cross-sections as well as admitted ones. The record is a fact about
    what the adapter observed in the archive, not a claim about what the panel
    contains -- and a cross-section the floor dropped is precisely the one a
    reader may want to re-examine.
    """

    source_id: str
    ref_date: date
    entity_unit: str
    entity_count: int
    declared_floor: Optional[int]
    admitted: bool
    row_count: int
    submission_types: tuple = ()
    absent_fields: tuple = ()
    era_id: Optional[str] = None
    unmatched_derived_fields: tuple = ()

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "ref_date": self.ref_date.isoformat(),
            "entity_unit": self.entity_unit,
            "entity_count": self.entity_count,
            "declared_floor": self.declared_floor,
            "era_id": self.era_id,
            "rows": self.row_count,
            "submission_types": {
                str(name): int(count) for name, count in self.submission_types
            },
            "absent_fields": list(self.absent_fields),
            # Its own key, for the same reason it is its own field: a reader who
            # cannot tell "the table was not there" from "the table was there and
            # the derivation matched nothing" will read the second as the first,
            # and the second is the one that carries information.
            "unmatched_derived_fields": [
                {"field": str(field), "disposition": str(disposition)}
                for field, disposition in self.unmatched_derived_fields
            ],
            "reason": self.reason,
        }

    @property
    def reason(self) -> str:
        """Why this cross-section was refused, or why it was admitted.

        Two refusals, and they are not the same finding. A cross-section below
        its era's floor is a straggler cohort: the floor did its job. A
        cross-section whose `ref_date` falls in no declared era is a gap in the
        registry, and reading it as "below the floor" would report a
        measurement where there was none -- the undeclared thing priced at
        zero, one level up from the values.
        """

        if self.era_id is None:
            return (
                "ref_date falls in no declared coverage era, so no floor "
                "applies to it; declare the era rather than admitting it"
            )
        if not self.admitted:
            return (
                "reporting entities below the coverage floor declared in the "
                f"source registry for era {self.era_id}"
            )
        return f"admitted against the declared floor for era {self.era_id}"


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
class ViolatedIdentity:
    """One `(source, identity, ref_date)` the identity was checked on and failed.

    The fourth outcome, recorded the way `UnevaluatedIdentity` records the
    third. Every declared term was observed, so a residual exists -- and unlike
    an unevaluable date this one has a number. The number is only readable next
    to the bound it was measured against, which is why both are carried. A bare
    `violated` would be the defect `absent_fields` was added one class up to
    fix: a verdict a reader cannot act on, because 0.312 against a bound of 0.5
    and 0.312 against a bound of 0.0001 are different findings and only the pair
    says which.

    Recording is not tolerating. `build_daily_panel` raises on a violation in a
    source it actually built a column from; see rule 5 there, and
    `docs/DATA_QUALITY_DECISIONS.md`, "Whether a source may abort a build it
    contributes nothing to". The abort had to move because the hop that
    evaluates identities runs before any wide panel exists and therefore cannot
    know which sources a panel depends on. This record is what lets the hop that
    does know ask.
    """

    source_id: str
    identity: str
    ref_date: date
    residual: float
    bound: float

    def as_dict(self) -> Mapping[str, object]:
        return {
            "source_id": self.source_id,
            "identity": self.identity,
            "ref_date": self.ref_date.isoformat(),
            "verdict": IDENTITY_VIOLATED,
            "residual": self.residual,
            "bound": self.bound,
            "reason": (
                "every declared term of this identity was observed for this "
                "reference date and the residual exceeds the declared tolerance"
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
    `held_where_evaluable`, which no caller can mistake for the former. When any
    reference date was checked and failed it is `violated`, and that answer
    outranks the other two: a panel-level `held_where_evaluable` on an identity
    that failed somewhere would be the same lie by omission, one outcome later.

    `maximum_residual` is the largest residual over every date that produced
    one, **violating dates included**. That is a deliberate choice and it
    reverses nothing: until this class carried violations the function raised on
    the first one, so the field had never seen a violating residual and could
    not have. Keeping it over the passing dates only would have made it a
    summary statistic that cannot report the worst thing it summarises -- a
    number that goes *down* as the data gets worse. It is pinned by
    `IdentityVerdictTests.test_the_maximum_residual_does_not_exclude_the_violating_dates`.
    """

    source_id: str
    name: str
    maximum_residual: Optional[float]
    evaluated_ref_dates: int
    unevaluated: tuple = ()
    violations: tuple = ()

    @property
    def verdict(self) -> str:
        if self.violations:
            return IDENTITY_VIOLATED
        if self.unevaluated:
            return IDENTITY_HELD_WHERE_EVALUABLE
        return IDENTITY_HELD

    @property
    def violated_ref_dates(self) -> tuple:
        """Every reference date this identity was checked on and failed."""

        return tuple(sorted({item.ref_date for item in self.violations}))

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
            # The dates, not a count. A count is exactly what let 5.5 years of
            # an unchecked balance sheet read as one number, and a violation is
            # not less actionable than an absence.
            "violated_ref_dates": [item.as_dict() for item in self.violations],
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
    violated_identities: Sequence[ViolatedIdentity] = ()

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
            # Its own key again, and for the third time the same reason. "Held",
            # "not checked" and "checked and failed" are three different facts,
            # and this one used to reach a reader as a traceback and a build
            # that stopped -- which is a report only for whoever was watching
            # the build. Every violating reference date is named, with its
            # residual and its bound, because a count of violations is not
            # something anyone can act on.
            "violated_identities": [
                item.as_dict()
                for item in sorted(
                    self.violated_identities,
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
    violated_identities: Optional[Iterable[ViolatedIdentity]] = None,
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
        violated_identities=tuple(violated_identities or ()),
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
    violated_identities: Optional[Iterable[ViolatedIdentity]] = None,
) -> PointInTimeAuditReport:
    """Write a deterministic JSON missingness/revision report."""

    report = audit_point_in_time_panel(
        observations,
        expected_ref_dates=expected_ref_dates,
        excluded_cross_sections=excluded_cross_sections,
        unevaluated_identities=unevaluated_identities,
        violated_identities=violated_identities,
    )
    payload = json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)
    return report


#: How a coverage era declares its bounds. Inclusive at both ends, and a
#: calendar month rather than a date, because the cross-section a floor judges
#: is a calendar month -- see `_nmfp_cross_section`. Declaring a bound as a date
#: would invite the reader to believe a floor can change mid-month.
COVERAGE_ERA_MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

COVERAGE_ERA_KEYS = frozenset(
    {
        "era_id",
        "start",
        "end",
        "minimum_reporting_entities",
        "observed_minimum_entities",
        "observed_complete_months",
        "note",
    }
)


@dataclass(frozen=True)
class CoverageEra:
    """One declared era of a source's reporting universe, and its floor.

    `minimum_reporting_entities` is the floor. The other two numbers are what
    it was calibrated from and are carried beside it deliberately: a floor
    whose calibration input is not stated is a number nobody can check, and
    the registry has already been through one round of exactly that.

    Bounds are inclusive `YYYY-MM` strings. They are *declared*, never derived
    from the counts the floor judges -- a floor that infers its own eras from
    the data it is guarding is the anchoring failure this repository keeps
    finding, and `validate_coverage_eras` refuses a declaration that leaves
    any month between the first and last era unclaimed rather than letting one
    be filled in by proximity.
    """

    era_id: str
    start: str
    end: str
    minimum_reporting_entities: int
    observed_minimum_entities: int
    observed_complete_months: int
    note: str = ""

    def contains(self, ref_date: date) -> bool:
        return self.start <= f"{ref_date.year:04d}-{ref_date.month:02d}" <= self.end


@dataclass(frozen=True)
class CoverageFloor:
    """A source's declared coverage floors, one per era of its universe.

    Replaces the `(entity_unit, floor)` pair this function used to return. That
    pair bundled two scalars that always travelled together; the floor is no
    longer a scalar, and returning `(entity_unit, something_with_methods)`
    would keep the shape of an answer that no longer exists.

    There is exactly one way to ask for a floor -- `era_for` -- and it returns
    `None` for a `ref_date` in no declared era rather than a number. A second
    accessor that raised, or one that fell back to the nearest era, would be a
    second reading of the same question, and the fallback is the silent zero
    this repository legislates against: an undeclared date admitted on a floor
    that was calibrated for a different universe.
    """

    entity_unit: str
    eras: tuple

    def era_for(self, ref_date: date) -> Optional[CoverageEra]:
        """The era governing `ref_date`, or `None` if none declares it."""

        for era in self.eras:
            if era.contains(ref_date):
                return era
        return None


def validate_coverage_eras(source_id: str, declared: object) -> tuple:
    """Read and check a source's declared eras, or say exactly what is wrong.

    Every branch here is a way the declaration can stop guarding while still
    looking like a declaration, so each one raises with its own message.
    """

    if not isinstance(declared, Sequence) or isinstance(declared, (str, bytes)):
        raise DataContractError(
            f"{source_id}: cross_section.eras must be a list of declared eras"
        )
    if not declared:
        raise DataContractError(
            f"{source_id}: cross_section.eras is empty; a source that emits "
            "cross-sections and declares no era has no floor anywhere"
        )
    eras = []
    for entry in declared:
        if not isinstance(entry, Mapping):
            raise DataContractError(
                f"{source_id}: each cross_section.eras entry must be an object"
            )
        unknown = sorted(set(entry) - COVERAGE_ERA_KEYS)
        if unknown:
            raise DataContractError(
                f"{source_id}: cross_section.eras entry has unpermitted keys "
                f"{unknown}"
            )
        missing = sorted(COVERAGE_ERA_KEYS - {"note"} - set(entry))
        if missing:
            raise DataContractError(
                f"{source_id}: cross_section.eras entry lacks required keys "
                f"{missing}"
            )
        era_id = entry["era_id"]
        if not isinstance(era_id, str) or not era_id.strip():
            raise DataContractError(
                f"{source_id}: cross_section.eras entry needs a non-empty era_id"
            )
        for key in ("start", "end"):
            bound = entry[key]
            if not isinstance(bound, str) or not COVERAGE_ERA_MONTH.match(bound):
                raise DataContractError(
                    f"{source_id}: era {era_id} has a {key} of {bound!r}; "
                    "bounds are inclusive YYYY-MM months"
                )
        if entry["start"] > entry["end"]:
            raise DataContractError(
                f"{source_id}: era {era_id} starts at {entry['start']} and ends "
                f"at {entry['end']}, which declares no months at all"
            )
        counts = {}
        for key in (
            "minimum_reporting_entities",
            "observed_minimum_entities",
            "observed_complete_months",
        ):
            value = entry[key]
            if isinstance(value, bool) or not isinstance(value, int):
                raise DataContractError(
                    f"{source_id}: era {era_id} {key} must be an integer"
                )
            counts[key] = value
        floor = counts["minimum_reporting_entities"]
        if floor < 1:
            # The prohibited silent zero, written down as data. A floor of 0
            # admits every cross-section and reads, to the next person, as a
            # check that ran.
            raise DataContractError(
                f"{source_id}: era {era_id} minimum_reporting_entities must be "
                f"at least 1; {floor} admits every cross-section and guards nothing"
            )
        if counts["observed_complete_months"] < 1:
            raise DataContractError(
                f"{source_id}: era {era_id} declares a floor calibrated from "
                "no observed month; state the months it was measured over"
            )
        if floor > counts["observed_minimum_entities"]:
            # A floor above the smallest complete month observed in its own era
            # refuses a month that era saw. Whatever it is guarding against, it
            # is not stragglers, and the number is wrong on its own evidence.
            raise DataContractError(
                f"{source_id}: era {era_id} floor {floor} exceeds the smallest "
                f"complete month it was calibrated from "
                f"({counts['observed_minimum_entities']}), so it refuses a "
                "cross-section its own calibration observed"
            )
        note = entry.get("note", "")
        if not isinstance(note, str):
            raise DataContractError(
                f"{source_id}: era {era_id} note must be a string"
            )
        eras.append(
            CoverageEra(
                era_id=era_id.strip(),
                start=entry["start"],
                end=entry["end"],
                minimum_reporting_entities=floor,
                observed_minimum_entities=counts["observed_minimum_entities"],
                observed_complete_months=counts["observed_complete_months"],
                note=note,
            )
        )
    eras.sort(key=lambda era: era.start)
    seen = set()
    for era in eras:
        if era.era_id in seen:
            raise DataContractError(
                f"{source_id}: cross_section.eras declares era_id {era.era_id!r} twice"
            )
        seen.add(era.era_id)
    for earlier, later in zip(eras, eras[1:]):
        if later.start <= earlier.end:
            raise DataContractError(
                f"{source_id}: eras {earlier.era_id} and {later.era_id} overlap "
                f"at {later.start}; one month cannot have two floors"
            )
        if _month_after(earlier.end) != later.start:
            # A gap between declared eras is worse than an undeclared tail: the
            # months in it look covered, because they lie inside the declared
            # range, and are refused anyway.
            raise DataContractError(
                f"{source_id}: eras {earlier.era_id} and {later.era_id} leave "
                f"{_month_after(earlier.end)} undeclared; declare every month "
                "between the first era and the last"
            )
    return tuple(eras)


def _month_after(month: str) -> str:
    year, index = int(month[:4]), int(month[5:])
    return f"{year + 1:04d}-01" if index == 12 else f"{year:04d}-{index + 1:02d}"


def declared_coverage_floor(
    source_id: str,
    source: Mapping[str, object],
) -> CoverageFloor:
    """Read one source's declared cross-section coverage floors.

    Returns a `CoverageFloor` carrying the entity unit and one `CoverageEra`
    per declared era. Raises if the source does not declare one, or declares
    one that cannot guard anything.

    Fails closed on purpose. An adapter reaches this function only because it
    knows how to count that source's reporting entities, and a counted quantity
    with no declared floor is a measurement nothing acts on. The registry is
    where the floors live -- they are claims about the source, not about the
    code, and Track A owns the registry.

    The floor is per era because one absolute cannot hold across a universe
    that changes size. `sec_nmfp` falls from 730 reporting series in 2010 to
    307 in 2024: the single floor of 200 this replaced was 27 percent of the
    early universe and 65 percent of the late one, which is not one floor
    applied twice but two different rules wearing one number.
    """

    declaration = source.get("cross_section")
    if not isinstance(declaration, Mapping):
        raise DataContractError(
            f"{source_id}: emits cross-sections but the registry declares no "
            "cross_section coverage floor"
        )
    permitted = {"entity_unit", "eras", "note"}
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
    if "eras" not in declaration:
        raise DataContractError(
            f"{source_id}: cross_section declares no eras; the floor is per era"
        )
    return CoverageFloor(
        entity_unit=entity_unit.strip(),
        eras=validate_coverage_eras(source_id, declaration["eras"]),
    )


# The two readings of a derived field that ran and matched nothing. They are the
# two halves of the sentence the published limitation says this repository cannot
# write, and the only thing that separates them is whether the registry declares
# the field a structural zero -- which is a reviewer's judgement recorded in
# `metadata/sources.json`, not something a parser can conclude from an empty
# match.
#
# Neither one is a zero. A declared structural zero means a reviewer has said the
# true value is zero for a stateable reason; it still does not license this
# adapter to write a `0.0` row, because a row is an observation and there was
# none. The declaration is what lets a *reader* treat the gap as a zero, at the
# point where they can also see who said so and on what grounds.
DERIVED_ABSENCE_DECLARED_ZERO = "declared_structural_zero"
DERIVED_ABSENCE_UNDECLARED = "no_declaration"


def declared_structural_zeros(
    source_id: str,
    source: Mapping[str, object],
) -> Mapping[str, str]:
    """Read one source's declared structural zeros, each field to the `when` it names.

    This is the registry declaration nothing in this package used to read. It was
    declared, shape-checked by `tests/test_contract.py`, and never consulted --
    and a declaration nothing reads cannot distinguish anything, which is why a
    field nobody observed and a derivation that found nothing had the same
    representation: no row, and no way to tell which had happened.

    Fails open, unlike `declared_coverage_floor` next door, and the asymmetry is
    deliberate. A missing coverage floor means a counted quantity nothing acts
    on, so refusing is the only safe answer. An empty `structural_zeros` is the
    honest state of a source nobody has reviewed yet -- `AGENT_CONTRACT.md` says
    in as many words that an empty `structural_zeros` is not a finding -- so
    raising on one would make every unreviewed source unreadable and would push a
    reviewer towards declaring something to make the build pass, which is the one
    outcome this field must never reward.

    `when` is carried through verbatim and is **not** compared against a
    reference date, because the registry declares no grammar for it: it is
    free-form prose that `tests/test_contract.py` requires only to be a non-empty
    string. So this answers "is this field declared a structural zero at all",
    which is the question that separates "they held none" from "we never found
    it". It does not answer "is it declared for *this* month", and a
    `DERIVED_ABSENCE_DECLARED_ZERO` must not be read as a period assertion.
    Narrowing it would take a declared `when` grammar in the registry, which is a
    change to a shared schema and not this function's to invent.

    `structural_zeros_reviewed` is deliberately not re-checked here.
    `tests/test_contract.py` already requires an unreviewed source's
    `structural_zeros` to be empty, so a non-empty declaration is reviewed by
    construction; restating that rule here would be the second copy of a rule
    that `tests/test_contract.py` names as how one field came to be called
    `calendar` on one side and `unit` on the other.
    """

    declarations = source.get("structural_zeros")
    if not isinstance(declarations, Sequence) or isinstance(declarations, (str, bytes)):
        raise DataContractError(
            f"{source_id}: structural_zeros must be a list of declarations"
        )
    found: Dict[str, str] = {}
    for declaration in declarations:
        if not isinstance(declaration, Mapping):
            raise DataContractError(
                f"{source_id}: each structural_zeros entry must be an object"
            )
        field = declaration.get("field")
        when = declaration.get("when")
        if not isinstance(field, str) or not field.strip():
            raise DataContractError(
                f"{source_id}: a structural_zeros entry names no field"
            )
        if not isinstance(when, str) or not when.strip():
            raise DataContractError(
                f"{source_id}: structural_zeros entry for {field!r} states no "
                "'when'; a structural zero nobody bounded is not reviewable"
            )
        # Two declarations for one field would make the disposition depend on
        # iteration order, and the answer here is one disposition per field.
        # Refusing costs less than picking one.
        if field.strip() in found:
            raise DataContractError(
                f"{source_id}: structural_zeros declares {field.strip()!r} twice"
            )
        found[field.strip()] = when.strip()
    return found


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
    tolerance: Mapping[str, object],
) -> tuple:
    """Answer one declared identity on one reference date.

    Returns `(verdict, residual, absent_fields, bound)`. The verdict is one of
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
        return IDENTITY_NOT_EVALUABLE, None, absent, None
    left_value = sum(float(values[field]) for field in left_fields)
    right_value = sum(float(values[field]) for field in right_fields)
    residual = abs(left_value - right_value)
    # The scale is the magnitude of the quantity the identity is about, and it
    # is taken from the larger side rather than from a named term, so that the
    # rule reads the same for an identity that has no term called "net assets".
    scale = max(abs(left_value), abs(right_value))
    bound = resolve_identity_tolerance(dict(tolerance), scale)
    verdict = IDENTITY_HELD if residual <= bound else IDENTITY_VIOLATED
    return verdict, residual, (), bound


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

    Neither a violated nor an unevaluable reference date raises. Both are
    recorded -- the unevaluable one named term by named term, the violated one
    with its residual and the bound it was measured against. A *malformed
    declaration* still raises, and the distinction is the whole of it: a broken
    registry is a fault in what this repository wrote, and a violated identity
    is a finding about data a source published. The two do not get the same
    channel.

    The abort that used to live here has moved to `build_daily_panel`, which is
    the first hop that knows whether the panel contains a column from the source
    the violation is in. `sec_nmfp` supplies no column to any build -- the
    pricing function refuses `mmf_assets` in all of them -- and a violated
    identity in it was halting builds of the eight columns that have nothing to
    do with it. See `docs/DATA_QUALITY_DECISIONS.md`, "Whether a source may
    abort a build it contributes nothing to". This is a scoping of the guard.
    A violated identity in a source the panel depends on still stops the panel.

    Which reference dates belong in the panel is a policy question and it is not
    this function's to answer -- but it can no longer be answered by accident.
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
            tolerance_problems = validate_identity_tolerance(source_id, name, tolerance)
            if tolerance_problems:
                raise DataContractError("; ".join(tolerance_problems))
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
            violations: List[ViolatedIdentity] = []
            for ref_date in sorted(observed_dates):
                values = {
                    field: (
                        latest[(field, ref_date)].value
                        if (field, ref_date) in latest
                        else None
                    )
                    for field in fields
                }
                verdict, residual, absent, bound = _identity_verdict(
                    left_fields, right_fields, values, tolerance
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
                    # Recorded, not raised, and deliberately symmetric with the
                    # branch above it. This function runs at the first hop,
                    # before any wide panel exists, so it cannot know whether
                    # the panel will contain a column from this source -- and
                    # that is the only fact that makes a violation here a reason
                    # to stop a build. `build_daily_panel` knows it and raises;
                    # see rule 5 there.
                    violations.append(
                        ViolatedIdentity(
                            source_id=source_id,
                            identity=name,
                            ref_date=ref_date,
                            residual=residual,
                            bound=bound,
                        )
                    )
                # Not in an `else`. A violating residual is still a residual,
                # and a maximum computed over the passing dates alone would fall
                # as the data got worse.
                maximum = max(maximum, residual)
            evaluations[f"{source_id}:{name}"] = IdentityEvaluation(
                source_id=source_id,
                name=name,
                maximum_residual=maximum,
                evaluated_ref_dates=len(observed_dates) - len(unevaluated),
                unevaluated=tuple(unevaluated),
                violations=tuple(violations),
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


#: Every declared panel column except the `date` index, in the order the
#: model layer declares them. The join attempts each one and refuses the ones
#: latest vintage cannot carry faithfully; it is not a shorter list of the
#: columns someone expects to succeed, because a column that quietly stopped
#: being attempted would be indistinguishable from one that has no data.
PANEL_COLUMNS = tuple(
    field for field in REQUIRED_FIELDS if field != "date"
) + OPTIONAL_NUMERIC_FIELDS


@dataclass(frozen=True)
class DailyPanelBuild:
    """A wide daily panel and the record of how it was built.

    `refusals` maps a column that was *not* built to the reason the pricing
    function gave for refusing it, verbatim. A refused column is absent from
    every row's `values` -- never present and quietly carrying a revised
    number -- and the reason travels with the panel so a reader of the manifest
    does not have to re-derive it.

    `holes` counts, per built column, the `ref_date`s in the panel that carry
    no observation for it. A hole is not a zero and is not the previous day's
    value; it is recorded and left empty. It is counted over the grid the panel
    actually carries -- see `incomplete_dates`.

    `incomplete_dates` counts the `ref_date`s that the union of the sources
    reported but that this panel does not carry, because a `REQUIRED_FIELDS`
    column had no observation on them. It is never a default: a build that
    dropped nothing records zero, and a reader can tell that apart from a build
    that was never asked.
    """

    observations: Sequence[DailyObservation]
    built_columns: Sequence[str]
    refusals: Mapping[str, str]
    holes: Mapping[str, int]
    build_cutoff: datetime
    decision_time: object
    incomplete_dates: int


def _priceable_columns(
    columns: Iterable[str],
    registry: Mapping[str, Mapping[str, object]],
    decision_time,
) -> tuple[List[str], Dict[str, str]]:
    """Split declared columns into the ones latest vintage may carry, and why not.

    The test is `registry.max_release_lag_days`, called -- not restated. A
    column is built exactly when the pricing function returns a purge for the
    `(source, field)` pairs behind it, and refused exactly when it raises. That
    delegation is the whole point: a field on a `snapshot_retrieved_at` source
    with no `revision_policy` is refused there because its latest value may
    differ from the value that stood on the day, and a second copy of that rule
    here would be free to drift from the registry it is supposed to describe.

    Both refusal channels are named rather than caught as bare `ValueError`.
    `RegistryContractError` is the pricing function declining to price;
    `UndeclaredFeatureError` is `contract` declining to resolve a column to
    sources at all -- an unsourced or calendar-only column. Anything else
    raised from here is a fault, not a refusal, and is left to propagate.
    """

    from .contract import UndeclaredFeatureError, field_sources_for_features
    from .registry import RegistryContractError, max_release_lag_days

    built: List[str] = []
    refusals: Dict[str, str] = {}
    for column in columns:
        try:
            pairs = field_sources_for_features([column])
            max_release_lag_days(registry, pairs, decision_time=decision_time)
        except (RegistryContractError, UndeclaredFeatureError) as exc:
            refusals[column] = str(exc)
            continue
        built.append(column)
    return built, refusals


def build_daily_panel(
    observations: Iterable[PointInTimeObservation],
    registry: Mapping[str, Mapping[str, object]],
    *,
    build_cutoff: datetime,
    decision_time,
    columns: Sequence[str] = PANEL_COLUMNS,
) -> DailyPanelBuild:
    """Join long point-in-time observations into the wide daily panel.

    This is the hop that was missing: `DailyObservation` was constructed in
    exactly one place, inside `load_daily_panel`, parsing a hand-written CSV.

    Four rules, and three of them are about not re-deciding something this
    repository has already decided once.

    **1. Indexed by `ref_date`; a cell carries the latest vintage available at
    `build_cutoff`.** Rows whose `available_at` is after the cutoff do not
    exist for this build. Among the rest, the cell for `(column, ref_date)` is
    the row with the greatest `available_at`. The cutoff is a property of the
    build and is returned so the manifest can record it.

    **2. The join does not subtract the release lag. The purge does.** The
    value at `ref_date` d is the value whose `ref_date` is d -- not the value
    from d minus the source's lag. `splits.rolling_origin` and
    `event_eval.evaluate_event_window` already hold the last training row a
    full release lag clear of the scored day. A join that shifted values by
    that lag as well would apply the gap twice: it would silently destroy
    training rows and move every reported number, while looking careful.
    `decision_time` is passed *through* to the pricing function and is never
    used to move a value.

    **3. A column is built only if the pricing function will price it.** See
    `_priceable_columns`. Refused columns are absent, with the reason recorded.

    **4. No forward fill.** A `ref_date` with no observation for a built column
    gets `None`, counted in `holes`. Absent is not zero and is not yesterday.

    **6. The grid is the dates the panel is readable on.** The union of every
    source's `ref_date`s is not a panel: an administered rate that prints every
    calendar day and a market rate that prints on business days produce rows
    where the target is undefined, and `REQUIRED_FIELDS` then makes the file
    unreadable by `load_daily_panel` -- so `build` wrote something `backtest`
    could not open, and that gap sat on Milestone A's critical path. A
    `ref_date` missing any built `REQUIRED_FIELDS` column is therefore not a
    row. This is not rule 4 in reverse: an *optional* column with no
    observation is still a hole and still recorded. A weekend is not a hole in
    SOFR, it is a day `sofr - iorb` does not exist, and the count of dropped
    dates goes in the manifest so the distinction is auditable rather than
    asserted. `holes` is counted over the retained grid, because a hole count
    over a grid the panel does not carry describes nothing.

    **7. A column declared from more than one field is a splice, and the fields
    must partition the dates.** `iorb` is drawn from IORB and, before
    2021-07-29, from IOER. Where two fields both report the same `ref_date` the
    tie-break in rule 1 would pick one of them by `available_at` -- and two
    fields read out of a single latest-vintage snapshot share an `available_at`
    and a `vintage_id` exactly, so the winner would be whichever the iteration
    reached last. That is a silent choice about what a series means, so it
    raises instead.

    **5. A violated identity in a source this panel built a column from stops
    the build.** This is where that abort belongs and it is why it moved here.
    `validate_accounting_identities` runs one hop earlier, inside
    `build_point_in_time_snapshot`, where no wide panel exists yet -- so it
    could see the violation but not whether anything depended on the source,
    and it halted every build regardless. `sec_nmfp` supplies no column to any
    build, because the pricing function refuses `mmf_assets` in all of them
    under rule 3, so a violated N-MFP identity was stopping builds of the eight
    columns that have nothing to do with it. The verdict is now always recorded
    in the quality report and the abort is scoped to a source that actually
    supplied a column that was built. See `docs/DATA_QUALITY_DECISIONS.md`,
    "Whether a source may abort a build it contributes nothing to".

    This is a scoping and not a loosening, and the second half is what keeps it
    honest: a violated identity in a source the panel *does* contain still stops
    the panel, and never by dropping the offending rows.

    The identities are evaluated over the rows this build can see, for the same
    reason rule 1 gives -- a vintage that arrives after `build_cutoff` does not
    exist for this build, and neither does a violation only that vintage
    reveals.

    Raises `DataContractError` if the cutoff is naive, if no declared column
    survives pricing, if nothing is left to index, or under rule 5.
    """

    from .contract import FEATURE_FIELDS

    if build_cutoff.tzinfo is None or build_cutoff.utcoffset() is None:
        raise DataContractError("build_cutoff must include a UTC offset")

    declared = list(columns)
    built, refusals = _priceable_columns(declared, registry, decision_time)
    if not built:
        raise DataContractError(
            "no declared column survived pricing: "
            + "; ".join(f"{name}: {reason}" for name, reason in sorted(refusals.items()))
        )

    # Source field -> panel column, for the built columns only. `FEATURE_FIELDS`
    # is the one place the rename is written down; deriving it by string
    # matching on `series_id` is the thing that block was written to avoid.
    column_for_series: Dict[str, str] = {}
    for column in built:
        for _source_id, field in FEATURE_FIELDS[column]:
            column_for_series[str(field)] = column

    visible = [row for row in observations if row.available_at <= build_cutoff]

    latest: Dict[tuple, PointInTimeObservation] = {}
    contributors: Dict[tuple, set] = {}
    for row in visible:
        column = column_for_series.get(row.series_id)
        if column is None:
            continue
        key = (column, row.ref_date)
        contributors.setdefault(key, set()).add(str(row.series_id))
        previous = latest.get(key)
        if previous is None or (row.available_at, row.vintage_id) > (
            previous.available_at,
            previous.vintage_id,
        ):
            latest[key] = row

    if not latest:
        raise DataContractError(
            f"no observation for any built column is available at {build_cutoff.isoformat()}"
        )

    # Rule 5. Only the sources behind the columns this build actually made, so
    # the question asked is "did a source this panel depends on violate an
    # identity", not "did any source in the registry". Restricting the registry
    # rather than filtering the answers is deliberate: a source that supplied
    # nothing should not be able to fail this build through any channel,
    # including a malformed declaration of its own.
    built_sources = {
        str(source_id) for column in built for source_id, _field in FEATURE_FIELDS[column]
    }
    depended_on = {
        source_id: source
        for source_id, source in registry.items()
        if source_id in built_sources and source.get("identities")
    }
    if depended_on:
        for evaluation in sorted(
            validate_accounting_identities(visible, depended_on).values(),
            key=lambda item: (item.source_id, item.name),
        ):
            if not evaluation.violations:
                continue
            worst = max(evaluation.violations, key=lambda item: item.residual)
            supplied = sorted(
                column
                for column in built
                if any(
                    str(source_id) == evaluation.source_id
                    for source_id, _field in FEATURE_FIELDS[column]
                )
            )
            raise DataContractError(
                f"{evaluation.source_id}: identity {evaluation.name} is violated on "
                f"{len(evaluation.violated_ref_dates)} reference date(s) "
                f"({', '.join(item.isoformat() for item in evaluation.violated_ref_dates)}); "
                f"worst residual {worst.residual:g} exceeds tolerance {worst.bound:g} on "
                f"{worst.ref_date}. This panel builds {', '.join(supplied)} from that "
                "source, so the build stops here rather than reporting a column whose "
                "source does not reconcile"
            )

    # Rule 7. Checked before any row is assembled, so an overlapping splice is
    # reported as the ambiguity it is rather than resolved by iteration order.
    overlaps = sorted(
        (column, ref_date, sorted(series))
        for (column, ref_date), series in contributors.items()
        if len(series) > 1
    )
    if overlaps:
        column, ref_date, series = overlaps[0]
        raise DataContractError(
            f"column {column!r} is declared from more than one field and they "
            f"overlap: {' and '.join(series)} both report {ref_date.isoformat()}"
            f"{f' (and {len(overlaps) - 1} further date(s))' if len(overlaps) > 1 else ''}. "
            "A spliced column's fields must partition the reference dates; "
            "which field wins on a shared date is a decision about what the "
            "series means and this build will not make it silently"
        )

    ref_dates = sorted({ref_date for _column, ref_date in latest})

    # Rule 6. `date` is in REQUIRED_FIELDS but is the index, not a column.
    required = [column for column in built if column in REQUIRED_FIELDS]
    retained = [
        ref_date
        for ref_date in ref_dates
        if all(latest.get((column, ref_date)) is not None for column in required)
    ]
    incomplete_dates = len(ref_dates) - len(retained)
    if not retained:
        raise DataContractError(
            "no reference date carries every required column ("
            + ", ".join(required)
            + f"); {incomplete_dates} date(s) were reported and none is a row"
        )

    rows: List[DailyObservation] = []
    holes: Dict[str, int] = {column: 0 for column in built}
    for ref_date in retained:
        values: Dict[str, Optional[float]] = {}
        for column in built:
            row = latest.get((column, ref_date))
            if row is None:
                holes[column] += 1
                values[column] = None
            else:
                values[column] = row.value
        rows.append(DailyObservation(ref_date, values))

    return DailyPanelBuild(
        observations=tuple(rows),
        built_columns=tuple(built),
        refusals=dict(sorted(refusals.items())),
        holes=holes,
        build_cutoff=build_cutoff,
        decision_time=decision_time,
        incomplete_dates=incomplete_dates,
    )


def write_daily_panel(
    build: DailyPanelBuild, path: Path, *, source_shas: Sequence[str] = ()
) -> Path:
    """Write a built panel as CSV and its build manifest beside it.

    The CSV carries the built columns and nothing else, and an empty cell for a
    hole -- the encoding `load_daily_panel` already reads as absent. Note that
    a panel missing a `REQUIRED_FIELDS` column will not load back through
    `load_daily_panel`; that is a true report of what the sources support at
    latest vintage, not a defect in the writer, and inventing the column to
    make the round trip succeed is exactly what rule 3 forbids.

    The manifest is the committable half, as with the N-MFP archive set: the
    panel bytes are derived from gitignored raw snapshots and are not tracked.
    Returns the manifest path.

    The manifest carries `sha256`, the lowercase hex SHA-256 of the panel bytes
    as written -- the same convention the run records use. It is read back off
    disk with `path.read_bytes()` rather than taken over the text this function
    just rendered. The two agree here and would agree on most inputs, which is
    exactly why the distinction has to be made deliberately: a digest over a
    second rendering is a claim about a string that was never the file, and it
    stays green while the encoding, the line terminator or the write itself
    drifts away from it. `path` is what a later reader will hash, so `path` is
    what this hashes.

    Without it a manifest was a claim about a *name*: `baseline._bind_build_manifest`
    could bind a run record to it only by extent -- row count and end dates --
    and said so in the artifact as `build_manifest_binding.kind = "extent"`.
    Comparing the digest there is that function's to add, not this one's.
    """

    header = ["date", *build.built_columns]
    lines = [",".join(header)]
    for observation in build.observations:
        cells = [observation.date.isoformat()]
        for column in build.built_columns:
            value = observation.values.get(column)
            cells.append("" if value is None else format(value, ".15g"))
        lines.append(",".join(cells))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # The bytes on disk, not the text above: see the docstring.
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    dates = [observation.date for observation in build.observations]
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    manifest = {
        "path": str(path),
        "build_cutoff": build.build_cutoff.isoformat(),
        "decision_time": str(build.decision_time),
        "row_count": len(build.observations),
        "sha256": digest,
        "start_date": dates[0].isoformat(),
        "end_date": dates[-1].isoformat(),
        "built_columns": list(build.built_columns),
        "refused_columns": dict(build.refusals),
        "holes": dict(build.holes),
        "incomplete_dates": build.incomplete_dates,
        "required_columns": [
            column for column in build.built_columns if column in REQUIRED_FIELDS
        ],
        "source_shas": list(source_shas),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest_path
