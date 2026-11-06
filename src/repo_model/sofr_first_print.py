"""SOFR first prints for the live log (#940; `docs/decisions/scoring-protocol.md` §6 and §11).

The protocol's H5 target is "SOFR − IORB as first published", and "the outcome is the first published value". The
New York Fed publishes SOFR for a day at about 08:00 ET on the next business day and may revise it at about 14:30 ET
that day, only if the change exceeds one basis point and only on the same day (its page on reference-rate
publication and revisions). The revised value then replaces the first in the API, which carries no publication time
and whose `revisionIndicator` was blank on every one of the 2104 rows fetched on 19 October 2026. A first print that
is not kept at about 08:00 ET is therefore lost: no later fetch can tell it from the revision.

One record per effective date holds what was fetched, as fetched:

* `payload`, the API response text, and its `sha256`;
* `retrieved_at`, an aware instant (UTC);
* `publication_instant` and `revision_instant`, the declared instants (America/New_York wall clock with its offset);
* `sofr_percent` and `revision_indicator`, read off the day's row;
* `iorb`, IORB's first-public source: the FOMC implementation note that set the rate in force on the day
  (`iorb_source`, from the tracked announcement table).

**The guard** (`check_first_print`, run when a record is built, written and read back):

* `LookAheadError` if the record was fetched at or after the revision instant, or if the day's row already carries a
  revision indicator: either way the payload may be the revision, not the first print. Reading "the declared outcome
  instant" of the directive as the end of the window in which the first print is still the only print is a
  judgement the pull request marks for Eleonora.
* `ValueError` for a malformed record: a missing key, a payload that fails its hash or has no row for the day, a
  non-numeric rate, a naive timestamp, a fetch before the publication instant, or an IORB source without its note.

A day's file is written once and never overwritten (`write_first_print`).

**A missed day** (#1404). A day whose print was not kept by its revision instant is lost and never back-filled. The
days that were lost are listed in `metadata/sofr_missed_first_prints.json` (date and reason), so the confirmation's
rule for missing outcomes can count them. `unflagged_misses` names the business days that are due (their revision
instant has passed), have no file and are not on the list; `read_missed` refuses a list that contradicts the branch.

**The count** (#1491). By Eleonora's ruling a lost first print drops that lead alone, for every model
(`docs/decisions/scoring-protocol.md`); the lost days are counted and reported at the 60, 125 and 250-day checks
(`lost_day_report`). The report changes nothing that is scored and sets no ceiling.

Stdlib only.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Mapping, Optional
from zoneinfo import ZoneInfo

from .data import market_holidays, next_business_day
from .splits import LookAheadError

__all__ = [
    "FIRST_EFFECTIVE",
    "FIRST_PRINT_KEYS",
    "MISSED_LIST",
    "IORB_TABLE",
    "PUBLICATION_TIME",
    "REVISION_TIME",
    "captured_days",
    "check_first_print",
    "due_days",
    "first_print_record",
    "iorb_source",
    "latest_published",
    "lost_day_report",
    "publication_instant",
    "read_all",
    "read_missed",
    "revision_instant",
    "unflagged_misses",
    "write_first_print",
]

EASTERN = ZoneInfo("America/New_York")
#: About 08:00 ET on the next business day (the New York Fed's page on reference-rate publication).
PUBLICATION_TIME = time(8, 0)
#: About 14:30 ET the same day, the only time a revision is made.
REVISION_TIME = time(14, 30)
RECORD_VERSION = 1
FIRST_PRINT_KEYS = (
    "version",
    "effective_date",
    "publication_instant",
    "revision_instant",
    "retrieved_at",
    "url",
    "sha256",
    "payload",
    "sofr_percent",
    "revision_indicator",
    "iorb",
)
IORB_KEYS = ("source", "rate_percent", "effective_date", "announced_at", "implementation_note_url", "table_sha256")
IORB_TABLE = (
    Path(__file__).parents[2] / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
)


#: The first effective date the capture kept (published 20 October 2026, the morning after the workflow's merge).
FIRST_EFFECTIVE = date(2026, 10, 19)
MISSED_LIST = Path(__file__).parents[2] / "metadata" / "sofr_missed_first_prints.json"


def _local(day: date, at: time) -> datetime:
    return datetime.combine(day, at)


def publication_instant(effective: date) -> datetime:
    """When the first print for `effective` is published: 08:00 ET on the next business day (naive, ET wall clock)."""

    return _local(next_business_day(effective, 1), PUBLICATION_TIME)


def revision_instant(effective: date) -> datetime:
    """When a revision of `effective`'s print may be made: 14:30 ET on the publication day (naive, ET wall clock)."""

    return _local(next_business_day(effective, 1), REVISION_TIME)


def _aware(naive: datetime) -> datetime:
    return naive.replace(tzinfo=EASTERN)


def _is_business_day(day: date) -> bool:
    return day.weekday() < 5 and day not in market_holidays().closed


def latest_published(now: datetime) -> Optional[date]:
    """The effective date whose first print is published at `now`, or None if `now` is before 08:00 ET, a weekend or a holiday.

    The latest business day before today, on a business day at or after 08:00 ET. It names the day only: whether the
    print may still be taken as a first print is the guard's question (`check_first_print`).
    """

    if now.tzinfo is None:
        raise ValueError("the capture instant needs a time zone")
    local = now.astimezone(EASTERN)
    today = local.date()
    if not _is_business_day(today) or local.time() < PUBLICATION_TIME:
        return None
    day = today - timedelta(days=1)
    while not _is_business_day(day):
        day -= timedelta(days=1)
    return day


def iorb_source(effective: date, table: Path = IORB_TABLE) -> dict:
    """IORB's first-public source for `effective`: the implementation note that set the rate then in force.

    Read from the tracked announcement table (`scripts/build_iorb_table.py`), refused if its bytes are not its
    manifest's. The rate is IOER before 2021-07-29 and IORB after, as the table's `field` column says.

    Raises:
        ValueError: a checksum mismatch, or a day before the table's first (anchor) row.
    """

    table = Path(table)
    manifest = json.loads(table.with_name(table.name + ".manifest.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(table.read_bytes()).hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError(f"{table}: sha256 {digest} is not the manifest's {manifest['sha256']}")
    in_force = None
    with table.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if date.fromisoformat(row["effective_date"]) <= effective:
                in_force = row
    if in_force is None:
        raise ValueError(f"the IORB announcement table has no rate in force on {effective.isoformat()}")
    return {
        "source": "fed-iorb-announcements",
        "rate_percent": float(in_force["rate_percent"]),
        "effective_date": in_force["effective_date"],
        "announced_at": f"{in_force['announcement_date']}T{in_force['announcement_time']}",
        "implementation_note_url": in_force["implementation_note_url"],
        "table_sha256": digest,
    }


def _row(payload: str, effective: date) -> dict:
    try:
        rows = json.loads(payload)["refRates"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError(f"the payload is not a New York Fed refRates response: {exc}") from exc
    if not isinstance(rows, list):
        raise ValueError("the payload's refRates is not a list")
    matches = [r for r in rows if isinstance(r, dict) and r.get("effectiveDate") == effective.isoformat()]
    if len(matches) != 1:
        raise ValueError(f"the payload has {len(matches)} rows for {effective.isoformat()}, not one")
    return matches[0]


def first_print_record(payload: bytes, *, url: str, retrieved_at: datetime, effective: date, iorb: Mapping) -> dict:
    """The record for `effective` from the response `payload` fetched at `retrieved_at`, checked by `check_first_print`.

    Raises:
        ValueError: a malformed record (see `check_first_print`).
        LookAheadError: fetched at or after the revision instant, or the day's row is marked revised.
    """

    if retrieved_at.tzinfo is None:
        raise ValueError("the retrieval time needs a time zone")
    text = payload.decode("utf-8")
    row = _row(text, effective)
    try:
        rate = float(row["percentRate"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"the row for {effective.isoformat()} has no numeric percentRate") from exc
    record = {
        "version": RECORD_VERSION,
        "effective_date": effective.isoformat(),
        "publication_instant": _aware(publication_instant(effective)).isoformat(),
        "revision_instant": _aware(revision_instant(effective)).isoformat(),
        "retrieved_at": retrieved_at.astimezone(timezone.utc).isoformat(),
        "url": url,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "payload": text,
        "sofr_percent": rate,
        "revision_indicator": str(row.get("revisionIndicator", "")).strip(),
        "iorb": dict(iorb),
    }
    check_first_print(record)
    return record


def check_first_print(record: object) -> None:
    """Raise unless `record` is a first print of its day.

    Raises:
        ValueError: a missing or extra key, a payload that fails its hash or has no one row for the day, a rate that
            differs from the payload's, a naive or unparseable timestamp, a fetch before the publication instant,
            or an IORB source without its keys.
        LookAheadError: fetched at or after the revision instant, or the day's row carries a revision indicator.
    """

    if not isinstance(record, dict) or set(record) != set(FIRST_PRINT_KEYS):
        raise ValueError(f"a first-print record has exactly the keys {FIRST_PRINT_KEYS}")
    if record["version"] != RECORD_VERSION:
        raise ValueError(f"unknown first-print record version {record['version']!r}")
    try:
        effective = date.fromisoformat(record["effective_date"])
        retrieved = datetime.fromisoformat(record["retrieved_at"])
        publication = datetime.fromisoformat(record["publication_instant"])
        revision = datetime.fromisoformat(record["revision_instant"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"a first-print record has an unreadable date or instant: {exc}") from exc
    if retrieved.tzinfo is None or publication.tzinfo is None or revision.tzinfo is None:
        raise ValueError("every instant of a first-print record needs a time zone")
    if publication != _aware(publication_instant(effective)) or revision != _aware(revision_instant(effective)):
        raise ValueError("the declared publication or revision instant is not the day's")
    if not isinstance(record["payload"], str):
        raise ValueError("the payload is stored as the response text")
    if hashlib.sha256(record["payload"].encode("utf-8")).hexdigest() != record["sha256"]:
        raise ValueError("the payload does not match its sha256")
    row = _row(record["payload"], effective)
    try:
        rate = float(row["percentRate"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"the row for {effective.isoformat()} has no numeric percentRate") from exc
    if rate != record["sofr_percent"]:
        raise ValueError("sofr_percent is not the payload's percentRate")
    iorb = record["iorb"]
    if not isinstance(iorb, dict) or set(iorb) != set(IORB_KEYS) or not str(iorb["implementation_note_url"]).startswith("http"):
        raise ValueError(f"the IORB source needs exactly the keys {IORB_KEYS}, with the implementation note's URL")
    if retrieved < publication:
        raise ValueError(
            f"fetched at {retrieved.isoformat()}, before the print is published at {publication.isoformat()}"
        )
    indicator = str(row.get("revisionIndicator", "")).strip()
    if indicator:
        raise LookAheadError(
            f"the row for {effective.isoformat()} carries revision indicator {indicator!r}: it is a revision, not the first print"
        )
    if retrieved >= revision:
        raise LookAheadError(
            f"the first print of {effective.isoformat()} is lost: fetched at {retrieved.isoformat()}, at or after the "
            f"revision instant {revision.isoformat()}, so the payload may be a revision, not the first print"
        )


def _path(root: Path, effective: str) -> Path:
    return Path(root) / "sofr" / f"{effective}.json"


def write_first_print(root: Path, record: Mapping) -> Path:
    """Write the day's record once. Returns its path.

    Raises:
        ValueError: a malformed record, or a day whose file already exists (a first print is never overwritten).
        LookAheadError: see `check_first_print`.
    """

    check_first_print(dict(record))
    path = _path(root, record["effective_date"])
    if path.exists():
        raise ValueError(f"{path} exists: a first print is written once and never overwritten")
    payload = (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    return path


def read_all(root: Path) -> list:
    """Every record under `root`, each checked, in date order."""

    out = []
    for path in sorted((Path(root) / "sofr").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        check_first_print(record)
        if path.name != f"{record['effective_date']}.json":
            raise ValueError(f"{path} holds the record of {record['effective_date']}")
        out.append(record)
    return out


def due_days(now: datetime, first: date = FIRST_EFFECTIVE) -> list:
    """The business days from `first` on whose revision instant has passed at `now`: by then the first print is kept or lost."""

    if now.tzinfo is None:
        raise ValueError("the instant needs a time zone")
    out = []
    day = first
    while day <= now.astimezone(EASTERN).date():
        if _is_business_day(day) and _aware(revision_instant(day)) <= now:
            out.append(day)
        day += timedelta(days=1)
    return out


def captured_days(root: Path) -> set:
    """The effective dates that have a file `sofr/<date>.json` under `root` (names only; `read_all` checks the content).

    Raises:
        ValueError: no `sofr/` directory, or a file not named for a date.
    """

    if not (Path(root) / "sofr").is_dir():
        raise ValueError(f"{root} has no sofr/ directory: a checkout that failed is not a branch with no prints")
    out = set()
    for path in (Path(root) / "sofr").glob("*.json"):
        try:
            out.add(date.fromisoformat(path.stem))
        except ValueError as exc:
            raise ValueError(f"{path} is not named for an effective date") from exc
    return out


def read_missed(path: Path = MISSED_LIST) -> dict:
    """`{effective date: reason}` from the tracked list of days whose first print was lost.

    Raises:
        ValueError: a malformed list, a duplicate, a day that is not a business day or is before `FIRST_EFFECTIVE`, or
            an empty reason.
    """

    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"the missed-days list {path} is unreadable: {exc}") from exc
    if not isinstance(document, dict) or set(document) != {"description", "days"} or not isinstance(document["days"], list):
        raise ValueError("the missed-days list has exactly the keys 'description' and 'days' (a list)")
    out = {}
    for entry in document["days"]:
        if not isinstance(entry, dict) or set(entry) != {"effective_date", "reason"}:
            raise ValueError("a missed day has exactly the keys 'effective_date' and 'reason'")
        try:
            day = date.fromisoformat(entry["effective_date"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"unreadable date in the missed-days list: {entry['effective_date']!r}") from exc
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            raise ValueError(f"{day.isoformat()}: a missed day needs a reason")
        if day in out:
            raise ValueError(f"{day.isoformat()} is listed twice")
        if day < FIRST_EFFECTIVE or not _is_business_day(day):
            raise ValueError(f"{day.isoformat()} is not a business day on or after {FIRST_EFFECTIVE.isoformat()}")
        out[day] = entry["reason"].strip()
    return out


def unflagged_misses(captured, now: datetime, missed: Mapping, first: date = FIRST_EFFECTIVE) -> list:
    """The due business days with no file that are not on the missed-days list, oldest first.

    Raises:
        ValueError: a listed day that has a file (it was not missed) or whose revision instant has not passed (it is
            not yet lost): the list never says more than the branch shows.
    """

    captured = set(captured)
    due = due_days(now, first)
    for day in sorted(missed):
        if day in captured:
            raise ValueError(f"{day.isoformat()} is listed as missed but has a first print on the branch")
        if day not in due:
            raise ValueError(f"{day.isoformat()} is listed as missed but its revision instant has not passed")
    return [day for day in due if day not in captured and day not in missed]


LOST_DAY_RULE = "a lost first print drops that lead alone, for every model"


def lost_day_report(missed: Mapping, start: date, now: datetime, checkpoints=None) -> list:
    """The lost first prints in the first N business days from `start`, for each operational checkpoint N (#1491).

    One row per checkpoint: `reached` (the N-th day's revision instant has passed at `now`), `window_days` (N, or the
    days due so far if the checkpoint is not reached), `lost` and `lost_days` (the listed days in that window) and
    `share`. The rule that applies to a lost day is `LOST_DAY_RULE` (`scoring-protocol.md`); this only counts.

    Raises:
        ValueError: `start` is not a business day, or `now` has no time zone.
    """

    if checkpoints is None:
        from .scoring_protocol import CHECKPOINTS as checkpoints
    if not _is_business_day(start):
        raise ValueError(f"{start.isoformat()} is not a business day")
    due = due_days(now, start)
    rows = []
    for checkpoint in checkpoints:
        window = due[: int(checkpoint)]
        lost = sorted(day for day in window if day in missed)
        rows.append(
            {
                "checkpoint": int(checkpoint),
                "reached": len(due) >= int(checkpoint),
                "window_days": len(window),
                "lost": len(lost),
                "share": len(lost) / len(window) if window else 0.0,
                "lost_days": lost,
                "rule": LOST_DAY_RULE,
            }
        )
    return rows
