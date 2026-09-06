"""Point-in-time daily panel loading and validation."""

from __future__ import annotations

import csv
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
