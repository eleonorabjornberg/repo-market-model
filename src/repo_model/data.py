"""Point-in-time daily panel loading and validation."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import date
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

