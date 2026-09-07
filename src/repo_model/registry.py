"""Source-registry release-lag conversion.

The model/evaluation layer consumes a scalar purge measured in calendar days.
This module owns the provenance-sensitive conversion from the structured source
metadata to that scalar.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import time

from repo_model.contract import validate_release_lag


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
    return decision_time


def _decision_timezone(decision_time: time) -> str | None:
    if decision_time.tzinfo is None:
        return None
    key = getattr(decision_time.tzinfo, "key", None)
    name = key or decision_time.tzname()
    if not name:
        raise RegistryContractError("decision_time has an unnamed timezone")
    return name


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

    found_row = False
    for row in candidates:
        found_row = True
        if isinstance(row, Mapping):
            available_at = row.get("available_at")
        else:
            available_at = getattr(row, "available_at", None)
        if available_at is None or available_at == "":
            return False
    return found_row


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
    cutoff_timezone = _decision_timezone(cutoff_time)
    cutoff_wall_clock = cutoff_time.replace(tzinfo=None)
    selected = _selected_sources(sources)
    if not selected:
        raise RegistryContractError("sources must select at least one feature source")

    maximum = 0
    inferred_wall_clock_timezone = None
    for source_id, rows in selected:
        try:
            source = registry[source_id]
        except KeyError as exc:
            raise RegistryContractError(f"unknown source: {source_id}") from exc

        release_lag = source.get("release_lag")
        problems = validate_release_lag(source_id, release_lag)
        if problems:
            raise RegistryContractError("; ".join(problems))

        basis = release_lag["basis"]

        if basis == "ref_date":
            contribution = release_lag["worst_case_calendar_days"]
        elif basis == "record_date":
            declared_timezone = release_lag["timezone"]
            if cutoff_timezone is not None:
                if declared_timezone != cutoff_timezone:
                    raise RegistryContractError(
                        f"{source_id}: release timezone {declared_timezone!r} does not "
                        f"match decision_time timezone {cutoff_timezone!r}"
                    )
            elif inferred_wall_clock_timezone is None:
                inferred_wall_clock_timezone = declared_timezone
            elif inferred_wall_clock_timezone != declared_timezone:
                raise RegistryContractError(
                    "naive decision_time cannot be compared across release timezones "
                    f"{inferred_wall_clock_timezone!r} and {declared_timezone!r}"
                )
            contribution = release_lag["days"] + int(
                time.fromisoformat(release_lag["available_time"]) > cutoff_wall_clock
            )
        else:
            if not _rows_have_available_at(rows):
                raise RegistryContractError(
                    f"{source_id}: every snapshot row must carry available_at"
                )
            contribution = 0

        maximum = max(maximum, contribution)
    if maximum == 0:
        raise RegistryContractError("selected sources must produce a nonzero purge")
    return maximum
