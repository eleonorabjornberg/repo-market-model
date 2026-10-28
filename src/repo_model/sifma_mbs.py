"""SIFMA's agency MBS class settlement dates, and when each year's calendar was public (#1276; H5 step 3).

Eleonora, 27 October 2026 (chat, relayed; ledger item 68 on #1116): agency MBS settlement days may move GC through the month, and SIFMA publishes the
settlement dates of the agency MBS classes (A to D) well ahead. Adding the source is her decision, taken in that ruling.

**The table.** `data/sifma-mbs-settlement/settlement_dates.csv` holds one row per (class, settlement date) for 2018 to 2027, built by
`scripts/build_sifma_table_1276.py` from the Internet Archive's captures of SIFMA's page and workbook (`data/sifma-wayback-1276/`, checksummed in its
`manifest.json`) and from nothing else.

**When a date is public.** The declaration `metadata/sifma_mbs_1276.json` lists, for each year, the earliest archived capture that shows the year's
calendar (a label '(updated for <year>)' or the table of its dates) with the capture's timestamp, or `null` where no capture shows it. A date of class `k`
on day `d` is public at a decision instant `I` only if `public_from[year(d)]` is not `null` and is at or before `I` (`public_at`). A date that is not public
reads as 0, never as an earlier date in its place; asked for outright it raises `LookAheadError` (`require_public`). A year with no capture is never
public: the archive does not show when it was, and it is not guessed. A date that falls before its own year's capture is not public in that year either: every decision that can target it was made before the capture.

The decision instant is a naive America/New_York wall-clock datetime (16:00 on the decision day for the published records); the archive stamps captures in
UTC, and the stamp is converted once, here. Stdlib only.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, FrozenSet, Mapping, Optional
from zoneinfo import ZoneInfo

from .splits import LookAheadError

__all__ = [
    "CLASSES", "DECLARATION", "FIELDS", "TABLE", "UTC", "flags", "indicator", "load_public_from", "load_table", "parse_public_from", "public_at",
    "require_public",
]

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "data" / "sifma-mbs-settlement" / "settlement_dates.csv"
DECLARATION = ROOT / "metadata" / "sifma_mbs_1276.json"
CLASSES = ("A", "B", "C", "D")
#: The scheduled fields of the source, by class (`metadata/sifma_mbs_1276.json`).
FIELDS = {"A": "mbs_settlement_class_a", "B": "mbs_settlement_class_b", "C": "mbs_settlement_class_c", "D": "mbs_settlement_class_d"}
UTC = timezone.utc
_EASTERN = ZoneInfo("America/New_York")
_STAMP = re.compile(r"^\d{14}$")


def load_table(path: Path = TABLE) -> Dict[str, FrozenSet[date]]:
    """The settlement dates by class.

    Raises:
        ValueError: a row without a known class or a date, or a class with no date.
    """

    found: Dict[str, set] = {k: set() for k in CLASSES}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("class") not in found:
                raise ValueError(f"{path}: unknown class {row.get('class')!r}")
            found[row["class"]].add(date.fromisoformat(row["settlement_date"]))
    if not all(found.values()):
        raise ValueError(f"{path}: a class has no settlement date")
    return {k: frozenset(v) for k, v in found.items()}


def parse_public_from(entries: Mapping[str, Mapping[str, object]]) -> Dict[int, Optional[datetime]]:
    """The year -> instant from which the year's calendar is public, an aware UTC datetime, or `None` where no capture shows it.

    Raises:
        ValueError: a timestamp that is not the archive's fourteen digits `YYYYMMDDhhmmss`.
    """

    out: Dict[int, Optional[datetime]] = {}
    for year, entry in entries.items():
        stamp = entry.get("capture_timestamp")
        if stamp is None:
            out[int(year)] = None
            continue
        if not isinstance(stamp, str) or not _STAMP.match(stamp):
            raise ValueError(f"public_from[{year}]: {stamp!r} is not an archive timestamp (YYYYMMDDhhmmss)")
        out[int(year)] = datetime.strptime(stamp, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    return out


def load_public_from(path: Path = DECLARATION) -> Dict[int, Optional[datetime]]:
    """The declaration's `public_from`, parsed."""

    return parse_public_from(json.loads(path.read_text(encoding="utf-8"))["public_from"])


def public_at(moment: Optional[datetime], instant: datetime) -> bool:
    """Whether a calendar public from `moment` (aware UTC; `None` for a year no capture shows) is public at `instant`, a naive America/New_York time.

    Raises:
        ValueError: `instant` is aware (the rule compares wall-clock instants of one zone).

    Mutation record: see `tests/test_sifma_mbs.py` (`public_at`).
    """

    if instant.tzinfo is not None:
        raise ValueError("the decision instant is a naive America/New_York wall-clock datetime")
    if moment is None:
        return False
    return moment <= instant.replace(tzinfo=_EASTERN).astimezone(UTC)


def require_public(day: date, instant: datetime, public_from: Mapping[int, Optional[datetime]]) -> None:
    """The settlement dates of `day`'s year are public at `instant`.

    Raises:
        LookAheadError: no archived capture shows the year's calendar at or before `instant`.
    """

    if not public_at(public_from.get(day.year), instant):
        raise LookAheadError(f"the SIFMA MBS settlement calendar of {day.year} is not shown by any archived capture at or before {instant}")


def indicator(table: Mapping[str, FrozenSet[date]], public_from: Mapping[int, Optional[datetime]], klass: str, day: date, instant: datetime) -> int:
    """1 when `day` is a class-`klass` settlement date and its year's calendar is public at `instant`, 0 otherwise."""

    if day not in table[klass]:
        return 0
    return 1 if public_at(public_from.get(day.year), instant) else 0


def flags(table: Mapping[str, FrozenSet[date]], public_from: Mapping[int, Optional[datetime]], day: date, instant: datetime) -> Dict[str, int]:
    """`indicator` for each class on `day`."""

    return {k: indicator(table, public_from, k, day, instant) for k in CLASSES}
