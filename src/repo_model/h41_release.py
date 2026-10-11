"""The H.4.1 read per release, measured and off (#541).

Eleonora's ruling of 10 October 2026 (relayed on #541): the H.4.1 is read per release, at the
release's own publication instant, not five calendar days after the Wednesday.
`metadata/h41_release_dating.json` declares it; `release_instant` dates a Wednesday level by it.

`metadata/sources.json` is frozen by the final-test pre-registration (bytes), so it is not edited.
`release_dated_registry` returns a copy of the registry with a `release_calendar` block on the
`fred_macro_latest_vintage` source, which `release_dating()` makes the as-of rule read for the listed fields,
for the length of one measurement run: `asof.py` is frozen by the final-test pre-registration (the whole
file), so it is not edited, and the rule's two lookups are swapped for the run and restored on the way out. The
fields' `field_release_lags` are kept as they are (the purge still reads their `days`); only the
instant a read is dated by changes. No published record reads either file.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import contextlib
import copy
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterator, Mapping, Optional, Sequence

from . import asof, baseline
from .asof import InformationRule

__all__ = ["RELEASE_CALENDAR_KEY", "load_release_dating", "release_dated_registry", "release_instant", "release_dating"]

#: A source-level block dating a weekly field by its release's own instant. Absent from every published registry.
RELEASE_CALENDAR_KEY = "release_calendar"

_REQUIRED = {
    "source", "fields", "observation_weekday", "offset_days", "available_time", "timezone",
    "covers", "rule", "evidence", "exceptions",
}


def _covers(covers: Mapping[str, object], where: object) -> tuple:
    """The declared range of covered Wednesdays, both ends Wednesdays."""

    try:
        first = date.fromisoformat(str(covers["first_wednesday"]))
        last = date.fromisoformat(str(covers["last_wednesday"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{where}: covers needs ISO first_wednesday and last_wednesday: {covers!r}") from exc
    for end in (first, last):
        if end.weekday() != asof.WEEKLY_OBSERVATION_WEEKDAY:
            raise ValueError(f"{where}: covers end {end} is not a Wednesday")
    return first, last


def load_release_dating(path: Path) -> dict:
    """The declaration, checked for the keys this module reads.

    Raises:
        ValueError: a key is missing, the instant is not an HH:MM time, `covers` is not an ordered
            range of Wednesdays, or an exception is not a Wednesday released on a later weekday than
            the default.
    """

    declaration = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = sorted(_REQUIRED - set(declaration))
    if missing:
        raise ValueError(f"{path}: the H.4.1 release dating declaration lacks {missing}")
    if declaration["observation_weekday"] != "Wednesday":
        raise ValueError(f"{path}: the H.4.1 is observed on Wednesdays, got {declaration['observation_weekday']!r}")
    time.fromisoformat(declaration["available_time"])
    first, last = _covers(declaration["covers"], path)
    if first > last:
        raise ValueError(f"{path}: covers.first_wednesday {first} is after last_wednesday {last}")
    offset = declaration["offset_days"]
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError(f"{path}: offset_days must be a non-negative integer, got {offset!r}")
    for wednesday, printed in declaration["exceptions"].items():
        observed, moved = date.fromisoformat(wednesday), date.fromisoformat(printed)
        if observed.weekday() != asof.WEEKLY_OBSERVATION_WEEKDAY:
            raise ValueError(f"{path}: exception {wednesday} is not a Wednesday")
        if moved.weekday() > 4 or moved <= observed + timedelta(days=offset):
            raise ValueError(
                f"{path}: exception {wednesday} -> {printed} is not a weekday after the default "
                f"{observed + timedelta(days=offset)}"
            )
    return declaration


def release_dated_registry(
    registry: Mapping[str, Mapping[str, object]], declaration: Mapping[str, object]
) -> dict:
    """A copy of `registry` declaring the listed H.4.1 fields public at their release's print.

    The source gains a `release_calendar` block; nothing else changes, and `registry` itself is not
    changed.

    Raises:
        ValueError: the source or a listed field is not in the registry.
    """

    source = str(declaration["source"])
    if source not in registry:
        raise ValueError(f"the registry declares no source {source!r}")
    declared = set(registry[source].get("fields") or ())
    absent = [field for field in declaration["fields"] if field not in declared]
    if absent:
        raise ValueError(f"{source} declares no field {absent}")
    out = copy.deepcopy(dict(registry))
    out[source] = dict(out[source])
    out[source][RELEASE_CALENDAR_KEY] = {
        "fields": sorted(declaration["fields"]),
        "offset_days": declaration["offset_days"],
        "available_time": declaration["available_time"],
        "timezone": declaration["timezone"],
        "covers": dict(declaration["covers"]),
        "exceptions": dict(declaration["exceptions"]),
        "note": "A measurement variant, read by no published record (#541).",
    }
    return out


def release_instant(calendar: Mapping[str, object], row_date: date) -> datetime:
    """The print of the release that first carries the weekly level `row_date` holds.

    A panel row carries the latest Wednesday level on or before it (`docs/decisions/weekly-carry.md`), so
    the instant is the same for every row of a week: the Wednesday plus `offset_days` at `available_time`,
    or the date in `exceptions` when the Board moved the release.

    Raises:
        ValueError: the week's Wednesday is outside the declared `covers` range (#576). A week the
            declaration does not cover is not assumed to print on its Thursday.
    """

    behind = (row_date.weekday() - asof.WEEKLY_OBSERVATION_WEEKDAY) % 7
    observed = row_date - timedelta(days=behind)
    first, last = _covers(calendar["covers"], "release calendar")
    if not (first <= observed <= last):
        raise ValueError(
            f"the H.4.1 week of Wednesday {observed.isoformat()} (row {row_date.isoformat()}) is outside the "
            f"declared coverage {first.isoformat()} to {last.isoformat()}: its release date is not declared "
            f"(metadata/h41_release_dating.json)"
        )
    moved = (calendar.get("exceptions") or {}).get(observed.isoformat())
    printed = date.fromisoformat(str(moved)) if moved else observed + timedelta(days=int(calendar["offset_days"]))
    return datetime.combine(printed, time.fromisoformat(str(calendar["available_time"])))


def _calendar(registry: Mapping[str, Mapping[str, object]], source_id: str, field: str) -> Optional[Mapping[str, object]]:
    calendar = registry[source_id].get(RELEASE_CALENDAR_KEY)
    if isinstance(calendar, Mapping) and field in (calendar.get("fields") or ()):
        return calendar
    return None


@contextlib.contextmanager
def release_dating() -> Iterator[None]:
    """The as-of rule reading a `release_calendar` block, for one measurement run.

    Swaps `asof.declared_availability`, its alias `baseline._declared_availability` (the decision-relative guard reads it) and `InformationRule._observation_available` and restores both on the
    way out, raise or return. A field no block lists is dated by the original functions, so a registry with
    no block is read exactly as before.
    """

    original_availability = asof.declared_availability
    original_baseline = baseline._declared_availability
    original_observation = InformationRule._observation_available

    def declared_availability(registry, source_id, field, dates, position):
        calendar = _calendar(registry, source_id, field)
        if calendar is not None:
            return release_instant(calendar, dates[position])
        return original_availability(registry, source_id, field, dates, position)

    def observation_available(self, dates: Sequence[date], fields, row: int, available: datetime) -> datetime:
        for source_id, field in fields:
            if _calendar(self.registry, source_id, field) is not None:
                # Dated by the release of its own Wednesday: the row's instant is the observation's.
                return available
        return original_observation(self, dates, fields, row, available)

    asof.declared_availability = declared_availability
    baseline._declared_availability = declared_availability
    InformationRule._observation_available = observation_available
    try:
        yield
    finally:
        asof.declared_availability = original_availability
        baseline._declared_availability = original_baseline
        InformationRule._observation_available = original_observation
