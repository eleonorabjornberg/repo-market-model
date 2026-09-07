"""Shared contract fixtures, owned by neither track.

This module exists because the ownership gate is path-level and cannot see a
*semantic* collision. Three have now reached a merge on this project: the
`release_lag` dict-versus-scalar incompatibility, the duplicate spec filename,
and the `calendar`-versus-`unit` naming collision on the same field. Each time,
both tracks stayed perfectly in lane and still shipped halves that do not
compose, because AGENT_CONTRACT.md named a field in prose without giving it a
key name, and each track picked its own.

The fix is to make the shared shape executable and put it where neither track
owns it. Both tracks import this module; neither edits it. Changing it is a
human edit, and the ownership gate enforces that.

Stdlib only, by contract.
"""

from __future__ import annotations

import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "BASES",
    "UNIT_FOR_BASIS",
    "END_OF_DAY",
    "AVAILABLE_TIME_RE",
    "validate_release_lag",
    "validate_registry_release_lags",
]

#: The three publication bases the contract recognises, and the day-count unit
#: each one is measured in. The pairing is fixed: see "One rule per basis" in
#: AGENT_CONTRACT.md. `unit` is still declared explicitly rather than derived,
#: so that a source whose author meant the other calendar is a validation
#: error rather than a silent reinterpretation.
UNIT_FOR_BASIS = {
    "ref_date": "business_days",
    "record_date": "calendar_days",
    "snapshot_retrieved_at": None,  # contributes no purge; declares no day count
}

BASES = tuple(UNIT_FOR_BASIS)

#: `available_time` is an HH:MM wall-clock string in the declared `timezone`.
#: Seconds are not carried: nothing in the as-of rule resolves below a minute,
#: and a spurious `:59` invites the reader to believe it does.
AVAILABLE_TIME_RE = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")

#: The conservative end-of-day convention, for a source whose publication time
#: within the day is unknown.
END_OF_DAY = "23:59"

_ALLOWED_KEYS = {
    "basis",
    "unit",
    "days",
    "worst_case_calendar_days",
    "available_time",
    "timezone",
    "note",
}


def _is_int(value: object) -> bool:
    # bool is a subclass of int and must not pass as a day count.
    return isinstance(value, int) and not isinstance(value, bool)


def validate_release_lag(source_id: str, release_lag: object) -> list[str]:
    """Return a list of human-readable problems with one `release_lag` object.

    An empty list means the object conforms. This function never raises on
    malformed input and never returns a partial answer: callers that want to
    fail closed raise on a non-empty result.
    """

    problems: list[str] = []

    if not isinstance(release_lag, dict):
        return [f"{source_id}: release_lag must be an object, got {type(release_lag).__name__}"]

    unknown = sorted(set(release_lag) - _ALLOWED_KEYS)
    if unknown:
        problems.append(f"{source_id}: unknown release_lag keys {unknown}")

    basis = release_lag.get("basis")
    if basis not in UNIT_FOR_BASIS:
        problems.append(
            f"{source_id}: basis must be one of {list(BASES)}, got {basis!r}"
        )
        return problems

    note = release_lag.get("note")
    if note is not None and not isinstance(note, str):
        problems.append(f"{source_id}: note must be a string")

    expected_unit = UNIT_FOR_BASIS[basis]

    if expected_unit is None:
        # A snapshot source contributes no purge and MUST NOT be mapped to
        # zero. It therefore carries no day count and no unit at all: a `days:
        # 0` here is the silent zero this contract keeps legislating against,
        # written down as data.
        for key in ("unit", "days", "worst_case_calendar_days", "available_time"):
            if key in release_lag:
                problems.append(
                    f"{source_id}: a {basis} source must not declare {key!r}; it "
                    f"contributes no purge, and a day count here is the "
                    f"mapping-to-zero the contract prohibits"
                )
        if "timezone" in release_lag:
            problems.append(
                f"{source_id}: timezone is declared with no available_time to "
                f"interpret; a declared-and-never-read timezone is how naive "
                f"times got compared across zones once already"
            )
        return problems

    unit = release_lag.get("unit")
    if unit != expected_unit:
        problems.append(
            f"{source_id}: a {basis} source must declare unit "
            f"{expected_unit!r}, got {unit!r}"
        )

    days = release_lag.get("days")
    if not _is_int(days) or days < 0:
        problems.append(
            f"{source_id}: days must be a non-negative integer, got {days!r}"
        )

    if basis == "ref_date":
        bound = release_lag.get("worst_case_calendar_days")
        if not _is_int(bound):
            problems.append(
                f"{source_id}: a ref_date source must declare an integer "
                f"worst_case_calendar_days, got {bound!r}"
            )
        elif _is_int(days) and bound < days + 5:
            problems.append(
                f"{source_id}: worst_case_calendar_days {bound} is below "
                f"days + 5 ({days + 5}); a weekend plus three consecutive "
                f"holidays is the floor, and a bound that is too small makes "
                f"every purge sized from it too small"
            )

    available_time = release_lag.get("available_time")
    if basis == "record_date" and available_time is None:
        problems.append(
            f"{source_id}: a record_date source must declare available_time; "
            f"the rule adds a day when it falls after decision_time, which "
            f"cannot be evaluated without it (use {END_OF_DAY!r} for a source "
            f"whose intraday publication time is unknown)"
        )

    if available_time is not None:
        if not isinstance(available_time, str) or not AVAILABLE_TIME_RE.match(available_time):
            problems.append(
                f"{source_id}: available_time must be an HH:MM string, got "
                f"{available_time!r}"
            )
        timezone = release_lag.get("timezone")
        if not isinstance(timezone, str) or not timezone:
            problems.append(
                f"{source_id}: available_time requires a timezone; comparing "
                f"naive times across declared zones is a leakage bug, not a "
                f"formatting one"
            )
        else:
            try:
                ZoneInfo(timezone)
            except (ZoneInfoNotFoundError, ValueError):
                problems.append(
                    f"{source_id}: timezone {timezone!r} is not an IANA zone"
                )
    elif "timezone" in release_lag:
        problems.append(
            f"{source_id}: timezone is declared with no available_time to "
            f"interpret; drop one or add the other"
        )

    return problems


def validate_registry_release_lags(registry: dict) -> dict[str, list[str]]:
    """Validate every source's `release_lag`. Returns {source_id: problems}.

    Sources declaring no `release_lag` at all are reported, because a missing
    lag reads as a zero lag to anything that skips it.
    """

    offenders: dict[str, list[str]] = {}
    for source_id, source in registry.items():
        if not isinstance(source, dict) or "release_lag" not in source:
            offenders[source_id] = [f"{source_id}: no release_lag declared"]
            continue
        problems = validate_release_lag(source_id, source["release_lag"])
        if problems:
            offenders[source_id] = problems
    return offenders
