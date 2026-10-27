"""DTCC GCF Repo Index, forward capture (#962; H5 groundwork G3, prospective logging).

The DTCC GCF Repo Index is the par-weighted overnight rate (and the par volume) of the GCF Repo contracts that clear
at FICC, for U.S. Treasury and for agency MBS collateral. DTCC's fact sheet says the day's value is posted "at
approximately 3:30 p.m. EST" (quoted in #962; the fact sheet's host, files.dtcc.com, is refused from the capture
environment, so this repository has not re-read it). If that holds it is the only public repo rate for day T that
exists at T's 16:00 ET decision instant: SOFR for T prints at 08:00 ET on the next business day.

The page `https://www.dtcc.com/market-index-data/charts/dtcc-gcf-repo-index` is client-rendered and names its data
file, `/data/gcfindex.csv` on `cms-prod.dtcc.com`, the last year of daily rows:

    Date,MBS Total PAR Value,MBS Weighted Average,Treasury Total PAR Value,Treasury Weighted Average
    10/26/2026,136692000000,  3.967,65840000000,  3.946
    ...
    TRAILER,249,,,,,

Par volumes are USD; rates are percent. The trailer counts the rows. The file is served behind a CDN with
`cache-control: public, max-age=604800`: the page itself requests it with a cache-busting `?v=<epoch ms>` query, and so
does the capture. Without it, a request on 27 October 2026 was answered with a copy 2.2 days old.

One file per business day, `gcf/<effective date>.json`, as fetched:

* a **captured** record holds the response text as `payload`, its `sha256`, the fetch instant in UTC and in ET, the
  window (15:30 to 16:00 ET) and the decision instant, the URL, and the day's Treasury rate and par volume read off the
  payload;
* a **missed** record holds no value. A day whose first successful fetch came after 16:00 ET
  (`fetched_after_decision`), a day on which the file had no row for it after 16:00 ET (`no_posting`), a response that
  could not be read (`unreadable_response`) and a day on which no run happened at all (`no_run`) are each recorded as
  such, with the hash of what was fetched, if anything was.

A day's file is written once and never overwritten, and no day is back-filled: a missed day stays missed.

**The guard** (`check_record`, run when a record is built, written and read back; `read_value` for a reader):

* `LookAheadError` if a captured record was fetched after the day's 16:00 ET decision instant, or, for a reader at
  `as_of`, if it was fetched after `as_of`;
* `ValueError` for a malformed record: a missing or extra key, a payload that fails its hash or has no Treasury row for
  the day, a value that is not the payload's, a naive or disagreeing timestamp, a fetch before the window opens.

No history is read: the file's year of earlier rows is kept inside each day's payload as the bytes were, and is not a
source of any value (#962 criterion 3; the question of whether the "about 3:30 p.m." establishes a publication
instant for the history is Eleonora's).

Stdlib only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import List, Mapping, Optional, Set
from zoneinfo import ZoneInfo

from .data import market_holidays
from .splits import LookAheadError

__all__ = [
    "CAPTURED_KEYS",
    "CSV_URL",
    "DECISION_TIME",
    "MISSED_KEYS",
    "MISSED_REASONS",
    "Plan",
    "WINDOW_START_TIME",
    "captured_record",
    "check_record",
    "decision_instant",
    "missed_record",
    "parse_csv",
    "plan",
    "read_all",
    "read_value",
    "window_start",
    "write_record",
]

EASTERN = ZoneInfo("America/New_York")
#: The data file the page names, on the host the page's own `Charts.Expanded.Url` points to.
CSV_URL = "https://cms-prod.dtcc.com/data/gcfindex.csv"
#: DTCC's stated posting time ("approximately 3:30 p.m."): no fetch before it.
WINDOW_START_TIME = time(15, 30)
#: The decision instant (`docs/decisions/information-set.md`): a fetch after it is a missed day.
DECISION_TIME = time(16, 0)
RECORD_VERSION = 1
HEADER = (
    "Date",
    "MBS Total PAR Value",
    "MBS Weighted Average",
    "Treasury Total PAR Value",
    "Treasury Weighted Average",
)
_COMMON = ("version", "status", "effective_date", "decision_instant", "fetched_at_utc", "fetched_at_et", "url", "sha256")
CAPTURED_KEYS = _COMMON + ("window_start", "payload", "treasury_rate_percent", "treasury_par_usd")
MISSED_REASONS = ("no_run", "no_posting", "fetched_after_decision", "unreadable_response")
MISSED_KEYS = _COMMON + ("reason", "latest_row_date")


def _et(instant: datetime) -> datetime:
    return instant.astimezone(EASTERN)


def _local(day: date, at: time) -> datetime:
    return datetime.combine(day, at, tzinfo=EASTERN)


def window_start(day: date) -> datetime:
    """15:30 ET on `day` (aware)."""

    return _local(day, WINDOW_START_TIME)


def decision_instant(day: date) -> datetime:
    """16:00 ET on `day` (aware): the instant after which a fetch of `day`'s value is too late."""

    return _local(day, DECISION_TIME)


def _is_business_day(day: date) -> bool:
    return day.weekday() < 5 and day not in market_holidays().closed


def _number(cell: str, what: str, line: int) -> Optional[float]:
    text = cell.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"line {line}: {what} {text!r} is not a number") from exc


def parse_csv(text: str) -> dict:
    """The rows of a `gcfindex.csv` response, by date: Treasury and MBS rate (percent) and par (USD).

    A blank cell is `None`, never zero.

    Raises:
        ValueError: an unknown header, an unreadable row or date, a duplicate date, a missing trailer, or a trailer
            whose count is not the number of rows (a truncated file).
    """

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or tuple(cell.strip() for cell in lines[0].split(",")) != HEADER:
        raise ValueError(f"the file does not start with the header {','.join(HEADER)}")
    rows: dict = {}
    trailer = None
    for number, line in enumerate(lines[1:], start=2):
        cells = line.split(",")
        if cells[0].strip() == "TRAILER":
            trailer = cells[1].strip() if len(cells) > 1 else ""
            continue
        if trailer is not None:
            raise ValueError(f"line {number}: a row after the trailer")
        if len(cells) != len(HEADER):
            raise ValueError(f"line {number}: {len(cells)} cells, not {len(HEADER)}")
        try:
            month, day_, year = (int(part) for part in cells[0].strip().split("/"))
            day = date(year, month, day_)
        except ValueError as exc:
            raise ValueError(f"line {number}: {cells[0]!r} is not an MM/DD/YYYY date") from exc
        if day in rows:
            raise ValueError(f"line {number}: {day.isoformat()} appears twice")
        rows[day] = {
            "mbs_par_usd": _number(cells[1], "the MBS par value", number),
            "mbs_rate_percent": _number(cells[2], "the MBS rate", number),
            "treasury_par_usd": _number(cells[3], "the Treasury par value", number),
            "treasury_rate_percent": _number(cells[4], "the Treasury rate", number),
        }
    if trailer is None:
        raise ValueError("the file has no TRAILER line: it may be truncated")
    if trailer != str(len(rows)):
        raise ValueError(f"the trailer counts {trailer!r} rows and the file has {len(rows)}")
    return rows


def _instants(fetched_at: datetime) -> dict:
    if fetched_at.tzinfo is None:
        raise ValueError("the fetch time needs a time zone")
    return {
        "fetched_at_utc": fetched_at.astimezone(timezone.utc).isoformat(),
        "fetched_at_et": _et(fetched_at).isoformat(),
    }


def captured_record(payload: bytes, *, url: str, fetched_at: datetime, effective: date) -> dict:
    """The captured record for `effective` from the response `payload`, fetched at `fetched_at`, checked.

    Raises:
        ValueError: a malformed response, no Treasury row (rate and par) for the day, a naive time, or a fetch before
            the window opens.
        LookAheadError: fetched after the day's decision instant (the caller records a missed day instead).
    """

    text = payload.decode("utf-8")
    row = parse_csv(text).get(effective)
    if row is None or row["treasury_rate_percent"] is None or row["treasury_par_usd"] is None:
        raise ValueError(f"the response has no Treasury rate and par volume for {effective.isoformat()}")
    record = {
        "version": RECORD_VERSION,
        "status": "captured",
        "effective_date": effective.isoformat(),
        "window_start": window_start(effective).isoformat(),
        "decision_instant": decision_instant(effective).isoformat(),
        **_instants(fetched_at),
        "url": url,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "payload": text,
        "treasury_rate_percent": row["treasury_rate_percent"],
        "treasury_par_usd": row["treasury_par_usd"],
    }
    check_record(record)
    return record


def missed_record(
    effective: date,
    reason: str,
    *,
    fetched_at: Optional[datetime] = None,
    url: Optional[str] = None,
    payload: Optional[bytes] = None,
) -> dict:
    """The missed record for `effective`: no value, the reason, and the hash of whatever was fetched.

    Raises:
        ValueError: an unknown reason, a fetch where the reason has none (`no_run`) or none where it needs one, a
            `fetched_after_decision` that was not after the decision instant, or a response that does not parse for a
            reason that says it did.
    """

    if reason not in MISSED_REASONS:
        raise ValueError(f"the reason {reason!r} is not one of {MISSED_REASONS}")
    if reason == "no_run":
        if fetched_at is not None or url is not None or payload is not None:
            raise ValueError("a day with no run has no fetch")
        instants = {"fetched_at_utc": None, "fetched_at_et": None}
        digest = None
        latest = None
    else:
        if fetched_at is None or url is None or payload is None:
            raise ValueError(f"the reason {reason!r} needs the fetch time, the URL and the response")
        instants = _instants(fetched_at)
        digest = hashlib.sha256(payload).hexdigest()
        latest = None
        if reason != "unreadable_response":
            rows = parse_csv(payload.decode("utf-8"))
            latest = max(rows).isoformat() if rows else None
    record = {
        "version": RECORD_VERSION,
        "status": "missed",
        "effective_date": effective.isoformat(),
        "decision_instant": decision_instant(effective).isoformat(),
        **instants,
        "url": url,
        "sha256": digest,
        "reason": reason,
        "latest_row_date": latest,
    }
    check_record(record)
    return record


def _times(record: Mapping, effective: date) -> Optional[datetime]:
    """The fetch instant of a record, checked against its ET twin and the day's decision instant; None for no fetch."""

    utc_text, et_text = record["fetched_at_utc"], record["fetched_at_et"]
    if utc_text is None and et_text is None:
        return None
    try:
        fetched = datetime.fromisoformat(utc_text)
        fetched_et = datetime.fromisoformat(et_text)
        declared = datetime.fromisoformat(record["decision_instant"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"a record has an unreadable instant: {exc}") from exc
    if fetched.tzinfo is None or fetched_et.tzinfo is None or declared.tzinfo is None:
        raise ValueError("every instant of a record needs a time zone")
    if fetched != fetched_et or _et(fetched).isoformat() != et_text:
        raise ValueError("fetched_at_utc and fetched_at_et are not one instant, or the ET one is not in New York time")
    if declared != decision_instant(effective):
        raise ValueError("the declared decision instant is not the day's")
    return fetched


def check_record(record: object) -> None:
    """Raise unless `record` is a well-formed day record, and a captured one was fetched in time.

    Raises:
        ValueError: see the module docstring.
        LookAheadError: a captured record fetched after the day's decision instant.
    """

    if not isinstance(record, dict) or record.get("status") not in ("captured", "missed"):
        raise ValueError("a record has a status of captured or missed")
    keys = CAPTURED_KEYS if record["status"] == "captured" else MISSED_KEYS
    if set(record) != set(keys):
        raise ValueError(f"a {record['status']} record has exactly the keys {keys}")
    if record["version"] != RECORD_VERSION:
        raise ValueError(f"unknown record version {record['version']!r}")
    try:
        effective = date.fromisoformat(record["effective_date"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"a record has an unreadable effective date: {exc}") from exc
    fetched = _times(record, effective)
    decision = decision_instant(effective)
    if record["status"] == "missed":
        _check_missed(record, fetched, decision)
        return
    if fetched is None:
        raise ValueError("a captured record has a fetch time")
    if not isinstance(record["payload"], str):
        raise ValueError("the payload is stored as the response text")
    if hashlib.sha256(record["payload"].encode("utf-8")).hexdigest() != record["sha256"]:
        raise ValueError("the payload does not match its sha256")
    row = parse_csv(record["payload"]).get(effective)
    if row is None or row["treasury_rate_percent"] is None or row["treasury_par_usd"] is None:
        raise ValueError(f"the payload has no Treasury rate and par volume for {effective.isoformat()}")
    if record["treasury_rate_percent"] != row["treasury_rate_percent"] or record["treasury_par_usd"] != row["treasury_par_usd"]:
        raise ValueError("the stored Treasury rate or par volume is not the payload's")
    if datetime.fromisoformat(record["window_start"]) != window_start(effective):
        raise ValueError("the declared window start is not the day's")
    if not isinstance(record["url"], str) or not record["url"].startswith("https://"):
        raise ValueError("a captured record names the URL it was fetched from")
    if fetched < window_start(effective):
        raise ValueError(f"fetched at {record['fetched_at_et']}, before the window opens at {window_start(effective).isoformat()}")
    if fetched > decision:
        raise LookAheadError(
            f"fetched at {record['fetched_at_et']}, after the decision instant {decision.isoformat()}: "
            "the value was not public to a forecast made then"
        )


def _check_missed(record: Mapping, fetched: Optional[datetime], decision: datetime) -> None:
    reason = record["reason"]
    if reason not in MISSED_REASONS:
        raise ValueError(f"the reason {reason!r} is not one of {MISSED_REASONS}")
    if reason == "no_run":
        if fetched is not None or record["sha256"] is not None or record["url"] is not None or record["latest_row_date"] is not None:
            raise ValueError("a day with no run has no fetch")
        return
    if fetched is None or not isinstance(record["sha256"], str) or len(record["sha256"]) != 64 or not record["url"]:
        raise ValueError(f"the reason {reason!r} needs the fetch time, the URL and the response's hash")
    if reason == "fetched_after_decision" and not fetched > decision:
        raise ValueError("a fetch that was not after the decision instant is not a late fetch")


def _path(root, effective: str) -> Path:
    return Path(root) / "gcf" / f"{effective}.json"


def write_record(root, record: Mapping) -> Path:
    """Write the day's record once. Returns its path.

    Raises:
        ValueError: a malformed record, or a day whose file exists (a day is never overwritten).
        LookAheadError: see `check_record`.
    """

    check_record(dict(record))
    path = _path(root, record["effective_date"])
    if path.exists():
        raise ValueError(f"{path} exists: a day is written once and never overwritten")
    body = (json.dumps(record, indent=1, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(body)
    return path


def read_all(root) -> list:
    """Every record under `root`, each checked, in date order."""

    out = []
    for path in sorted((Path(root) / "gcf").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        check_record(record)
        if path.name != f"{record['effective_date']}.json":
            raise ValueError(f"{path} holds the record of {record['effective_date']}")
        out.append(record)
    return out


def read_value(root, day: date, *, as_of: datetime) -> Optional[dict]:
    """The captured value for `day` as a reader at `as_of` may see it; None for a missed or absent day.

    Raises:
        ValueError: a naive `as_of`, or a malformed record.
        LookAheadError: the record was fetched after `as_of` (or after the day's decision instant): the reader
            could not have had it.
    """

    if as_of.tzinfo is None:
        raise ValueError("the reader's instant needs a time zone")
    path = _path(root, day.isoformat())
    if not path.exists():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    check_record(record)
    if record["status"] != "captured":
        return None
    fetched = datetime.fromisoformat(record["fetched_at_utc"])
    if fetched > as_of:
        raise LookAheadError(
            f"the value for {day.isoformat()} was fetched at {record['fetched_at_et']}, after the reader's instant "
            f"{_et(as_of).isoformat()}"
        )
    return {
        "effective_date": record["effective_date"],
        "treasury_rate_percent": record["treasury_rate_percent"],
        "treasury_par_usd": record["treasury_par_usd"],
        "fetched_at_utc": record["fetched_at_utc"],
        "sha256": record["sha256"],
    }


@dataclass
class Plan:
    """What a run does: `action` is none (not a business day), done, wait, fetch or late; `gaps` are no-run days."""

    action: str
    day: Optional[date] = None
    gaps: List[date] = field(default_factory=list)


def plan(now: datetime, already: Set[date]) -> Plan:
    """What a run at `now` does for today (ET), given the days that already have a file.

    * `none`: today is a weekend or a holiday;
    * `done`: today already has its file, which is never fetched again or overwritten;
    * `wait`: before 15:30 ET, nothing is fetched;
    * `fetch`: 15:30 to 16:00 ET inclusive, fetch and keep the day if the file has its row (otherwise a later slot
      tries again);
    * `late`: after 16:00 ET, fetch once and record the day missed (`fetched_after_decision` or `no_posting`).

    `gaps` lists the business days after the branch's earliest day and before today with no file at all, which the run
    records as `no_run`: a day nobody fetched is never filled in later.
    """

    if now.tzinfo is None:
        raise ValueError("the run's instant needs a time zone")
    local = _et(now)
    today = local.date()
    if not _is_business_day(today):
        return Plan("none")
    gaps: List[date] = []
    if already:
        day = min(already) + timedelta(days=1)
        while day < today:
            if _is_business_day(day) and day not in already:
                gaps.append(day)
            day += timedelta(days=1)
    if today in already:
        return Plan("done", today, gaps)
    if local < window_start(today):
        return Plan("wait", today, gaps)
    if local <= decision_instant(today):
        return Plan("fetch", today, gaps)
    return Plan("late", today, gaps)
