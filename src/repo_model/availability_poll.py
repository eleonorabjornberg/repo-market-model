"""When does a day's Treasury bill rate, and a week's FR 2004, first appear? A measurement, not an input (#1343).

The declarations say Treasury's daily bill rates are public at 16:30 ET on their own date
(`metadata/sources.json`, `treasury_bill_rates`, 0 days) and the decision instant is 18:00 ET (#1312). Nothing has
measured that. This module decides, from the ET clock, whether a run polls, and writes one add-only record per poll:
the fetch time, the HTTP status, the latest date present in the response and a SHA-256 of its bytes.

* Poll business days only, from 16:00 ET to 18:30 ET inclusive (EST and EDT alike: the ET clock decides).
* Treasury's daily bill-rate export (the URL `ingest.fetch_treasury_bill_rates` reads) every poll.
* The New York Fed's Primary Dealer Statistics release page (the FR 2004 release) on Thursdays only.

A poll that fails (HTTP error or no connection) is still a record, with `status` null and an `error`: a gap in the
sample is itself a fact the result page needs. The record changes no declaration and no panel input.

GitHub starts scheduled runs late (finding #1435: the first run, on 3 November 2026, started at 21:32 ET). So a run
after 18:30 ET on a business day is a catch-up (#1441): it records, once per source and day, the first `latest_date`
it sees with its true fetch time, marked `kind: "catch_up"`. It bounds the posting time from above and is never an
in-window sample. A business day with no in-window record is a missed day. It is listed, with the slots scheduled and
the runs that happened, in `metadata/availability_missed_days.json` (in the manner of the SOFR list), and the result
counts in-window days, catch-up-only days and days with no record separately (`classify_days`, `count_days`).

Stdlib only.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional, Tuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from . import ingest
from .data import market_holidays

EASTERN = ZoneInfo("America/New_York")
#: The poll window opens at the earliest scheduled release of the polled sources. It is not the decision clock
#: (`decision_instant.DECISION_TIME`), which the poll only records against.
WINDOW_START = time.fromisoformat("16:00")
WINDOW_END = time(18, 30)
POLL_MINUTES = 10
THURSDAY = 3

TREASURY = "treasury_bill_rates"
FR2004 = "nyfed_fr2004_release"
#: The page the New York Fed announces each FR 2004 release on.
FR2004_RELEASE_URL = "https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics"
SOURCES = (TREASURY, FR2004)
IN_WINDOW = "in_window"
CATCH_UP = "catch_up"
KINDS = (IN_WINDOW, CATCH_UP)
RECORD_KEYS = (
    "source", "kind", "url", "fetched_at", "et_date", "status", "latest_date", "sha256", "bytes", "error",
)
#: The first business day the measurement counts (the workflow merged at 17:20 ET on 3 November 2026, #1435).
FIRST_DAY = date(2026, 11, 3)
MISSED_LIST = Path(__file__).parents[2] / "metadata" / "availability_missed_days.json"
MISSED_KEYS = {"et_date", "slots_scheduled", "runs_started", "reason"}
NO_RECORD, CATCH_UP_ONLY = "no_record", "catch_up_only"

_MONTHS = {m: i for i, m in enumerate(
    ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"), 1)}
_US_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_LONG_DATE = re.compile(r"\b(" + "|".join(m.capitalize() for m in _MONTHS) + r")\s+(\d{1,2}),\s+(\d{4})\b")


def _is_business_day(day: date) -> bool:
    return day.weekday() < 5 and day not in market_holidays().closed


def sources_due(now: datetime) -> Tuple[str, ...]:
    """The sources to poll at `now`: none outside a business day's 16:00-18:30 ET window.

    Raises:
        ValueError: `now` has no time zone.
    """

    if now.tzinfo is None:
        raise ValueError("the poll instant needs a time zone")
    local = now.astimezone(EASTERN)
    if not _is_business_day(local.date()) or not (WINDOW_START <= local.time() <= WINDOW_END):
        return ()
    return SOURCES if local.weekday() == THURSDAY else (TREASURY,)


def catch_up_due(now: datetime, recorded: Iterable[Mapping] = ()) -> Tuple[str, ...]:
    """The sources a late run polls at `now`: those due that ET day with no in-window record and no kept catch-up.

    `recorded` is every record already kept for `now`'s ET day. A business day after 18:30 ET only; a catch-up that
    failed (status null or an HTTP error) does not count, so the next late run tries again.

    Raises:
        ValueError: `now` has no time zone.
    """

    if now.tzinfo is None:
        raise ValueError("the poll instant needs a time zone")
    local = now.astimezone(EASTERN)
    if not _is_business_day(local.date()) or local.time() <= WINDOW_END:
        return ()
    recorded = list(recorded)
    done = {r["source"] for r in recorded if r["kind"] == IN_WINDOW}
    done |= {r["source"] for r in recorded if r["kind"] == CATCH_UP and r["status"] is not None and r["status"] < 400}
    wanted = SOURCES if local.weekday() == THURSDAY else (TREASURY,)
    return tuple(source for source in wanted if source not in done)


def treasury_url(day: date) -> str:
    """The daily bill-rate export for `day`'s calendar year, as `ingest.fetch_treasury_bill_rates` requests it."""

    query = ingest.urlencode(
        {"type": "daily_treasury_bill_rates", "field_tdr_date_value": str(day.year), "_format": "csv"}
    )
    return f"{ingest.TREASURY_BILL_RATES_BASE}/{day.year}/all?{query}"


def url_for(source: str, day: date) -> str:
    if source == TREASURY:
        return treasury_url(day)
    if source == FR2004:
        return FR2004_RELEASE_URL
    raise ValueError(f"unknown source {source!r}")


def latest_date(source: str, payload: bytes) -> Optional[date]:
    """The latest date present in the response, or None if it holds none.

    Treasury: the first column ("Date", MM/DD/YYYY) of the export. The release page: the latest date written
    anywhere in the page, in the US, ISO or long form.
    """

    text = payload.decode("utf-8-sig", errors="replace")
    found = []
    if source == TREASURY:
        for row in csv.reader(io.StringIO(text)):
            match = _US_DATE.fullmatch(row[0].strip()) if row else None
            if match:
                found.append(_day(int(match[3]), int(match[1]), int(match[2])))
    elif source == FR2004:
        found += [_day(int(m[3]), int(m[1]), int(m[2])) for m in _US_DATE.finditer(text)]
        found += [_day(int(m[1]), int(m[2]), int(m[3])) for m in _ISO_DATE.finditer(text)]
        found += [_day(int(m[3]), _MONTHS[m[1].lower()], int(m[2])) for m in _LONG_DATE.finditer(text)]
    else:
        raise ValueError(f"unknown source {source!r}")
    found = [d for d in found if d is not None]
    return max(found) if found else None


def _day(year: int, month: int, day: int) -> Optional[date]:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def fetch(url: str, timeout: int = 60) -> Tuple[Optional[int], bytes, Optional[str]]:
    """(HTTP status, body, error). An HTTP error keeps its status and body; no connection gives (None, b"", reason)."""

    request = Request(url, headers={"User-Agent": ingest.USER_AGENT, "Accept": "*/*", "Cache-Control": "no-cache"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = ingest._decode_transport(response.read(), response.headers.get("Content-Encoding", ""))
            return response.status, body, None
    except HTTPError as exc:
        try:
            body = ingest._decode_transport(exc.read(), exc.headers.get("Content-Encoding", ""))
        except Exception:  # noqa: BLE001 - a body we cannot read is still a poll with a status
            body = b""
        return exc.code, body, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 - every failure is a record, not a crash
        return None, b"", f"{type(exc).__name__}: {exc}"


def poll_record(source: str, now: datetime, fetcher: Callable = fetch, clock: Optional[Callable] = None,
                kind: str = IN_WINDOW) -> dict:
    """One poll of `source`. `now` names the ET day; `clock` (default: the real clock) stamps when the response arrived."""

    url = url_for(source, now.astimezone(EASTERN).date())
    status, body, error = fetcher(url)
    arrived = (clock or (lambda: datetime.now(timezone.utc)))()
    latest = latest_date(source, body) if body and status is not None and status < 400 else None
    return {
        "source": source,
        "kind": kind,
        "url": url,
        "fetched_at": max(arrived, now).astimezone(timezone.utc).isoformat(),
        "et_date": now.astimezone(EASTERN).date().isoformat(),
        "status": status,
        "latest_date": latest.isoformat() if latest else None,
        "sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "error": error,
    }


def check_record(record: object) -> None:
    """Raise ValueError unless `record` is a well-formed poll."""

    if not isinstance(record, Mapping) or set(record) != set(RECORD_KEYS):
        raise ValueError(f"a poll record has exactly the keys {RECORD_KEYS}")
    if record["source"] not in SOURCES:
        raise ValueError(f"unknown source {record['source']!r}")
    if record["kind"] not in KINDS:
        raise ValueError(f"kind is one of {KINDS}, not {record['kind']!r}")
    fetched = datetime.fromisoformat(record["fetched_at"])
    if fetched.tzinfo is None:
        raise ValueError("fetched_at needs a time zone")
    date.fromisoformat(record["et_date"])
    if record["latest_date"] is not None:
        date.fromisoformat(record["latest_date"])
    if record["status"] is not None and not isinstance(record["status"], int):
        raise ValueError("status is an HTTP status or null")
    if not re.fullmatch(r"[0-9a-f]{64}", str(record["sha256"])):
        raise ValueError("sha256 is a hex digest")


def record_path(root: Path, record: Mapping) -> Path:
    stamp = datetime.fromisoformat(record["fetched_at"]).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return Path(root) / "polls" / record["et_date"] / f"{stamp}-{record['source']}.json"


def write_record(root: Path, record: Mapping) -> Path:
    """Write the poll once; a file is never overwritten.

    Raises:
        ValueError: a malformed record, or a path that exists.
    """

    check_record(record)
    path = record_path(root, record)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = path.open("xb")
    except FileExistsError:
        raise ValueError(f"{path} exists: a poll is written once and never overwritten") from None
    with handle:
        handle.write((json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8"))
    return path


def read_all(root: Path, require: bool = False) -> list:
    """Every record under `root`, each checked, in path order.

    Raises:
        ValueError: a malformed record, or (with `require`) no `polls/` directory: a checkout that failed is not a
            branch with no polls.
    """

    if require and not (Path(root) / "polls").is_dir():
        raise ValueError(f"{root} has no polls/ directory: a checkout that failed is not a branch with no polls")
    out = []
    for path in sorted((Path(root) / "polls").glob("*/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        check_record(record)
        if path != record_path(root, record):
            raise ValueError(f"{path} is not where its record belongs")
        out.append(record)
    return out


def read_day(root: Path, day: date) -> list:
    """Every record kept for the ET date `day` under `root` (none if the day has no directory)."""

    return [r for r in read_all(root) if r["et_date"] == day.isoformat()]


def classify_days(records: Iterable[Mapping], days: Iterable[date]) -> dict:
    """Each day's class: `in_window` (at least one in-window record), `catch_up_only` or `no_record`."""

    kinds = {}
    for r in records:
        kinds.setdefault(date.fromisoformat(r["et_date"]), set()).add(r["kind"])
    return {
        day: IN_WINDOW if IN_WINDOW in kinds.get(day, ()) else CATCH_UP_ONLY if kinds.get(day) else NO_RECORD
        for day in days
    }


def count_days(records: Iterable[Mapping], days: Iterable[date]) -> dict:
    """How many of `days` are in-window days, catch-up-only days and days with no record: the three never merge."""

    out = {IN_WINDOW: 0, CATCH_UP_ONLY: 0, NO_RECORD: 0}
    for cls in classify_days(records, days).values():
        out[cls] += 1
    return out


def read_missed(path: Path = MISSED_LIST) -> dict:
    """`{ET date: entry}` from the tracked list of business days with no in-window record.

    Raises:
        ValueError: a malformed list, a duplicate, a day before `FIRST_DAY` or that is not a business day, or an
            empty reason.
    """

    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"the missed-days list {path} is unreadable: {exc}") from exc
    if not isinstance(document, dict) or set(document) != {"description", "days"} or not isinstance(document["days"], list):
        raise ValueError("the missed-days list has exactly the keys 'description' and 'days' (a list)")
    out = {}
    for entry in document["days"]:
        if not isinstance(entry, dict) or set(entry) != MISSED_KEYS:
            raise ValueError(f"a missed day has exactly the keys {sorted(MISSED_KEYS)}")
        try:
            day = date.fromisoformat(entry["et_date"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"unreadable date in the missed-days list: {entry['et_date']!r}") from exc
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            raise ValueError(f"{day.isoformat()}: a missed day needs a reason")
        for key in ("slots_scheduled", "runs_started"):
            if not isinstance(entry[key], int) or isinstance(entry[key], bool) or entry[key] < 0:
                raise ValueError(f"{day.isoformat()}: {key} is a count")
        if day in out:
            raise ValueError(f"{day.isoformat()} is listed twice")
        if day < FIRST_DAY or not _is_business_day(day):
            raise ValueError(f"{day.isoformat()} is not a business day on or after {FIRST_DAY.isoformat()}")
        out[day] = entry
    return out


def unlisted_misses(records: Iterable[Mapping], today: date, listed: Mapping, first: date = FIRST_DAY) -> list:
    """The business days from `first` up to the day before `today` with no in-window record that are not listed.

    A catch-up record does not make a day an in-window day. Today is not yet missed: its window may still open.

    Raises:
        ValueError: a listed day that has an in-window record (it was not missed), or one that is not over yet.
    """

    records = list(records)
    seen = {date.fromisoformat(r["et_date"]) for r in records if r["kind"] == IN_WINDOW}
    for day in sorted(listed):
        if day in seen:
            raise ValueError(f"{day.isoformat()} is listed as missed but has an in-window record on the branch")
        if day >= today:
            raise ValueError(f"{day.isoformat()} is listed as missed but is not over yet")
    out = []
    day = first
    while day < today:
        if _is_business_day(day) and day not in seen and day not in listed:
            out.append(day)
        day += timedelta(days=1)
    return out
