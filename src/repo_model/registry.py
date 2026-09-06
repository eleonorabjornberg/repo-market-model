"""Source-registry release-lag conversion.

The model/evaluation layer consumes a scalar purge measured in calendar days.
This module owns the provenance-sensitive conversion from the structured source
metadata to that scalar.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import time
from typing import Any


class RegistryContractError(ValueError):
    """Raised when registry metadata cannot support a safe purge bound."""


def _selected_sources(sources: object) -> list[tuple[str, object | None]]:
    if isinstance(sources, Mapping):
        return [(str(source_id), rows) for source_id, rows in sources.items()]
    if isinstance(sources, (str, bytes)) or not isinstance(sources, Iterable):
        raise TypeError("sources must be an iterable of source IDs or a source-to-rows mapping")
    return [(str(source_id), None) for source_id in sources]


def _parse_decision_time(decision_time: object) -> time:
    if not isinstance(decision_time, time):
        raise TypeError("decision_time must be a datetime.time")
    if decision_time.tzinfo is not None:
        raise RegistryContractError(
            "decision_time must be a local wall-clock time matching registry availability times"
        )
    return decision_time


def _available_time(source_id: str, release_lag: Mapping[str, Any]) -> time:
    raw = release_lag.get("available_time")
    try:
        parsed = time.fromisoformat(raw)
    except (TypeError, ValueError) as exc:
        raise RegistryContractError(
            f"{source_id}: release_lag.available_time must be an ISO time"
        ) from exc
    if parsed.tzinfo is not None:
        raise RegistryContractError(
            f"{source_id}: release_lag.available_time must be a local wall-clock time"
        )
    return parsed


def _nonnegative_int(source_id: str, field: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RegistryContractError(f"{source_id}: release_lag.{field} must be a nonnegative integer")
    return value


def _rows_have_available_at(rows: object | None) -> bool:
    if rows is None or isinstance(rows, (str, bytes)):
        return False
    if isinstance(rows, Mapping):
        candidates = (rows,)
    else:
        try:
            candidates = iter(rows)  # type: ignore[arg-type]
        except TypeError:
            candidates = iter((rows,))

    for row in candidates:
        if isinstance(row, Mapping):
            available_at = row.get("available_at")
        else:
            available_at = getattr(row, "available_at", None)
        if available_at is None or available_at == "":
            return False
    return True


def max_release_lag_days(
    registry: Mapping[str, Mapping[str, object]],
    sources: object,
    *,
    decision_time: time,
) -> int:
    """Return the conservative calendar-day purge for selected feature sources.

    ``sources`` may be an iterable of source IDs for lag-based sources. A
    mapping of source ID to rows is required for ``snapshot_retrieved_at`` so
    every row can be checked for an explicit ``available_at`` value.
    """

    cutoff_time = _parse_decision_time(decision_time)
    maximum = 0
    for source_id, rows in _selected_sources(sources):
        try:
            source = registry[source_id]
        except KeyError as exc:
            raise RegistryContractError(f"unknown source: {source_id}") from exc

        release_lag = source.get("release_lag")
        if not isinstance(release_lag, Mapping):
            raise RegistryContractError(f"{source_id}: release_lag must be an object")

        basis = release_lag.get("basis")
        calendar = release_lag.get("calendar")
        days = _nonnegative_int(source_id, "days", release_lag.get("days"))

        if basis == "ref_date" and calendar == "business_days":
            bound = _nonnegative_int(
                source_id,
                "worst_case_calendar_days",
                release_lag.get("worst_case_calendar_days"),
            )
            if bound < days + 5:
                raise RegistryContractError(
                    f"{source_id}: worst_case_calendar_days must be at least days + 5"
                )
            contribution = bound
        elif basis == "record_date" and calendar == "calendar_days":
            contribution = days + int(_available_time(source_id, release_lag) > cutoff_time)
        elif basis == "snapshot_retrieved_at":
            if calendar != "none":
                raise RegistryContractError(
                    f"{source_id}: snapshot_retrieved_at requires calendar 'none'"
                )
            if not _rows_have_available_at(rows):
                raise RegistryContractError(
                    f"{source_id}: every snapshot row must carry available_at"
                )
            contribution = 0
        else:
            raise RegistryContractError(
                f"{source_id}: unsupported release-lag basis/calendar pair {basis!r}/{calendar!r}"
            )

        maximum = max(maximum, contribution)
    return maximum
