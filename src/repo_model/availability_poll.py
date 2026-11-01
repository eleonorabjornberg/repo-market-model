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

Stdlib only.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Callable, Mapping, Optional, Tuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from . import ingest
from .data import market_holidays

EASTERN = ZoneInfo("America/New_York")
WINDOW_START = time(16, 0)
WINDOW_END = time(18, 30)
POLL_MINUTES = 10
THURSDAY = 3

TREASURY = "treasury_bill_rates"
FR2004 = "nyfed_fr2004_release"
#: The page the New York Fed announces each FR 2004 release on.
FR2004_RELEASE_URL = "https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics"
SOURCES = (TREASURY, FR2004)
RECORD_KEYS = (
    "source", "url", "fetched_at", "et_date", "status", "latest_date", "sha256", "bytes", "error",
)

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


def poll_record(source: str, now: datetime, fetcher: Callable = fetch, clock: Optional[Callable] = None) -> dict:
    """One poll of `source`. `now` names the ET day; `clock` (default: the real clock) stamps when the response arrived."""

    url = url_for(source, now.astimezone(EASTERN).date())
    status, body, error = fetcher(url)
    arrived = (clock or (lambda: datetime.now(timezone.utc)))()
    latest = latest_date(source, body) if body and status is not None and status < 400 else None
    return {
        "source": source,
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


def read_all(root: Path) -> list:
    """Every record under `root`, each checked, in path order."""

    out = []
    for path in sorted((Path(root) / "polls").glob("*/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        check_record(record)
        if path != record_path(root, record):
            raise ValueError(f"{path} is not where its record belongs")
        out.append(record)
    return out
