"""The H.4.1 read per release, measured and off (#541).

Eleonora's ruling of 10 October 2026 (relayed on #541): the H.4.1 is read per release, at the
release's own publication instant, not five calendar days after the Wednesday.
`metadata/h41_release_dating.json` declares it; `asof.release_instant` dates a Wednesday level by it.

`metadata/sources.json` is frozen by the final-test pre-registration (bytes), so it is not edited.
`release_dated_registry` returns a copy of the registry with a `release_calendar` block on the
`fred_macro_latest_vintage` source, which `asof.declared_availability` reads for the listed fields. The
fields' `field_release_lags` are kept as they are (the purge still reads their `days`); only the
instant a read is dated by changes. No published record reads either file.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import copy
import json
from datetime import date, time, timedelta
from pathlib import Path
from typing import Mapping

from . import asof
from .asof import RELEASE_CALENDAR_KEY

__all__ = ["load_release_dating", "release_dated_registry"]

_REQUIRED = {
    "source", "fields", "observation_weekday", "offset_days", "available_time", "timezone",
    "covers", "rule", "evidence", "exceptions",
}


def load_release_dating(path: Path) -> dict:
    """The declaration, checked for the keys this module reads.

    Raises:
        ValueError: a key is missing, the instant is not an HH:MM time, or an exception is not a
            Wednesday released on a later weekday than the default.
    """

    declaration = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = sorted(_REQUIRED - set(declaration))
    if missing:
        raise ValueError(f"{path}: the H.4.1 release dating declaration lacks {missing}")
    if declaration["observation_weekday"] != "Wednesday":
        raise ValueError(f"{path}: the H.4.1 is observed on Wednesdays, got {declaration['observation_weekday']!r}")
    time.fromisoformat(declaration["available_time"])
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
        "exceptions": dict(declaration["exceptions"]),
        "note": "A measurement variant, read by no published record (#541).",
    }
    return out
