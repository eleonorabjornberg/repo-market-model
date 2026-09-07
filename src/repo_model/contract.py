"""Shared contract fixtures, owned by neither track.

This module exists because the ownership gate is path-level and cannot see a
*semantic* collision. Four have been found on this project: the `release_lag`
dict-versus-scalar incompatibility, the duplicate spec filename, the
`calendar`-versus-`unit` naming collision on the same field, and the
event-window digest. The first three reached a merge; the fourth was caught
before one, by applying the rule below to a shape that had not yet collided.
Each time, both tracks stayed perfectly in lane and still shipped halves that do
not compose, because AGENT_CONTRACT.md named a field in prose without giving it
a key name, and each track picked its own.

What lives here, therefore, is every shape both tracks must agree on:
the release-lag schema (`validate_release_lag`, `validate_registry_release_lags`
and the vocabulary they check against), the event-window schema
(`EVENT_WINDOW_KEYS`, `event_window_digest`, `validate_event_windows_document`),
and the forecast quantile grid (`QUANTILE_LEVELS`). None was invented here --
each was lifted from the track that had reasoned it through, unchanged except
in name.

The fix is to make the shared shape executable and put it where neither track
owns it. Both tracks import this module; neither edits it. Changing it is a
human edit, and the ownership gate enforces that.

Stdlib only, by contract.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "BASES",
    "UNIT_FOR_BASIS",
    "END_OF_DAY",
    "AVAILABLE_TIME_RE",
    "QUANTILE_LEVELS",
    "validate_release_lag",
    "validate_registry_release_lags",
    "EVENT_WINDOW_KEYS",
    "event_window_digest",
    "validate_event_windows_document",
]

#: Fixed across every model so pinball loss, interval coverage, and predictive
#: distributions are comparable. The outer pair is the repository's existing
#: 90% interval; the median and quartiles give CRPS more than a three-point grid.
QUANTILE_LEVELS = (0.05, 0.25, 0.50, 0.75, 0.95)

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


#: Keys every declared window must carry. Extra keys are permitted — Track A
#: may want a rationale, a source citation, a revision note — and model-eval
#: ignores them.
EVENT_WINDOW_KEYS = ("name", "start", "end", "checksum")


def event_window_digest(name: str, start: str, end: str) -> str:
    """The normative per-window checksum for `metadata/events.json`.

    An opaque per-window `checksum` pins nothing: an edit that moves `start`
    and leaves `checksum` alone yields a document that still validates. For the
    checksum to detect the edit the contract is worried about, it has to be a
    digest *of the boundaries*.

    Args:
        name: the window's stable slug.
        start, end: ISO date strings, `YYYY-MM-DD`. Strings rather than `date`
            objects on purpose — the digest must be computable from the file's
            own bytes without a parse step that could normalise something, so
            what is hashed is what is written.

    Returns:
        Lowercase hex SHA-256, 64 characters.
    """

    canonical = json.dumps(
        {"name": name, "start": start, "end": end},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_event_windows_document(payload: object) -> list[str]:
    """Every way `payload` fails the event-window schema, as readable problems.

    Returns a list rather than raising so a malformed file reports all of its
    faults in one run. Track A should not have to fix one key, re-run, and
    discover the next. An empty list means conforming.

    The bare-list form that `load_event_windows` also accepts is for fixtures,
    not for the declared file: a list has nowhere to carry a version.
    """

    problems: list[str] = []

    if not isinstance(payload, dict):
        return [
            "document must be a JSON object with 'version' and 'windows', got "
            f"{type(payload).__name__}; the bare-list form load_event_windows "
            "also accepts is for fixtures, not for the declared file, because a "
            "list has nowhere to carry a version"
        ]

    if "version" not in payload:
        problems.append(
            "document has no 'version'; the contract requires the file be versioned"
        )
    elif not isinstance(payload["version"], (int, str)) or not str(
        payload["version"]
    ).strip():
        problems.append(
            f"'version' must be a non-empty int or string, got {payload['version']!r}"
        )

    entries = payload.get("windows")
    if entries is None:
        problems.append("document has no 'windows'")
        return problems
    if not isinstance(entries, list) or not entries:
        problems.append("'windows' must be a non-empty list")
        return problems

    seen_names = set()
    parsed = []
    for position, entry in enumerate(entries):
        label = f"window {position}"
        if not isinstance(entry, dict):
            problems.append(f"{label} is not an object")
            continue

        missing = [key for key in EVENT_WINDOW_KEYS if key not in entry]
        if missing:
            problems.append(f"{label} is missing {', '.join(missing)}")
            continue

        name = entry["name"]
        label = f"window {name!r}"
        if not isinstance(name, str) or not name.strip():
            problems.append(f"{label} has a non-string or empty name")
            continue
        if name in seen_names:
            problems.append(
                f"{label} is declared twice; names identify windows in the journal"
            )
        seen_names.add(name)

        boundaries = {}
        for key in ("start", "end"):
            raw = entry[key]
            if not isinstance(raw, str):
                problems.append(f"{label} has a non-string {key}: {raw!r}")
                continue
            try:
                boundaries[key] = date.fromisoformat(raw)
            except ValueError:
                problems.append(
                    f"{label} has a non-ISO {key}: {raw!r}, expected YYYY-MM-DD"
                )
        if len(boundaries) != 2:
            continue
        if boundaries["end"] < boundaries["start"]:
            problems.append(
                f"{label} ends {boundaries['end']} before it starts {boundaries['start']}"
            )
            continue

        checksum = entry["checksum"]
        if not isinstance(checksum, str) or not checksum.strip():
            problems.append(f"{label} has a non-string or empty checksum")
        else:
            expected = event_window_digest(name, entry["start"], entry["end"])
            if checksum != expected:
                problems.append(
                    f"{label} checksum {checksum!r} does not match its boundaries; "
                    f"expected {expected!r}. Either an edge moved without the digest "
                    "being recomputed, or the digest is not "
                    "event_window_digest(name, start, end)"
                )

        parsed.append((name, boundaries["start"], boundaries["end"]))

    ordered = sorted(parsed, key=lambda item: item[1])
    if parsed != ordered:
        problems.append(
            "windows are not in ascending order of start date; the file is read "
            "by humans checking that a boundary has not moved, and an unsorted "
            "list makes that diff harder than it needs to be"
        )
    for earlier, later in zip(ordered, ordered[1:]):
        if later[1] <= earlier[2]:
            problems.append(
                f"windows {earlier[0]!r} ({earlier[1]}..{earlier[2]}) and "
                f"{later[0]!r} ({later[1]}..{later[2]}) overlap; a day in two "
                "knowledge holdouts is scored twice and spends two budgets"
            )

    return problems
