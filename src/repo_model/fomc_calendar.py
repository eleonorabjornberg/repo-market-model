"""The FOMC meeting calendar as columns read at the target day, only when it was public (#1038).

`metadata/fomc_calendar.json` (built from the Board's own pages by `scripts/build_fomc_calendar.py`) lists every
scheduled meeting of the Federal Open Market Committee from January 2018, the release that first published its
schedule, the unscheduled meetings and the one cancellation. The rule is `docs/decisions/fomc-point-in-time.md`: a
meeting is a fact about a forecast only from the moment it was public, and a cancelled meeting stops being one from the
moment its cancellation was.

**Read at the target day** (rule 2 of `asof.py`): a forecast for the day `T` is made at `dates[T - h]`'s decision time,
and reads whether `T` is a meeting day from the calendar as it stood at that instant. A scheduled meeting is public from
the earliest schedule release that lists it; an unscheduled meeting from its own release (the Committee met first and
said so after: 4 October 2019 was public on 11 October); a cancelled meeting is visible until its cancellation is.

**The columns** (`COLUMNS`), one value per panel row, never missing:

* `fomc_meeting_day`: 1 on each day of a visible meeting (both days of a two-day meeting), else 0;
* `fomc_days_to_next_meeting`: calendar days from the target day to the first day of the nearest visible meeting that
  starts on or after it (0 on a meeting's first day, the next meeting's distance on its second), capped at `DAYS_CAP`.

**The guard** is `require_public`: using a meeting at an instant before it was public raises `LookAheadError`.
`visible_at` is the filter and `require_public` the explicit second check on every meeting a value uses, so a filter
that stops filtering is refused rather than read.

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`: no published panel, declaration or record reads these
columns. The source, `fomc_calendar`, is declared in `metadata/sources_measurement.json`, not in `metadata/sources.json`,
which the final-test pre-registration freezes by its bytes.

Instants are America/New_York wall-clock datetimes, like `policy_events`. Standard library only.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .data import DailyObservation
from .splits import LookAheadError

__all__ = [
    "CALENDAR_PATH",
    "COLUMNS",
    "COLUMN_FIELDS",
    "DAYS_CAP",
    "Meeting",
    "SOURCE_ID",
    "add_columns",
    "fomc_feature_values",
    "load_calendar",
    "parse_calendar",
    "require_public",
    "visible_at",
]

CALENDAR_PATH = Path(__file__).resolve().parents[2] / "metadata" / "fomc_calendar.json"
SOURCE_ID = "fomc_calendar"
#: The cap on the wait to the next meeting, in calendar days. The longest gap between two scheduled meetings is under
#: two months, so the cap binds only for a target past the last published schedule.
DAYS_CAP = 90

COLUMNS = ("fomc_meeting_day", "fomc_days_to_next_meeting")

#: Every column's source field, for the as-of rule. **Off**: see the module docstring.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {name: ((SOURCE_ID, name),) for name in COLUMNS}


class Meeting(NamedTuple):
    """One Committee meeting, its days, and when it became (and, if cancelled, stopped being) public."""

    id: str
    kind: str  # "scheduled" or "unscheduled"
    start: date
    end: date
    public_at: datetime  # America/New_York wall clock, naive
    cancelled_at: Optional[datetime]
    source_url: str


def _instant(raw: Mapping[str, object], where: str) -> datetime:
    try:
        return datetime.combine(
            date.fromisoformat(str(raw["announced_date"])), time.fromisoformat(str(raw["announced_time"]))
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{where}: unreadable announcement instant: {exc}") from exc


def _check_url(raw: Mapping[str, object], where: str) -> str:
    url = str(raw.get("source_url", ""))
    if not url.startswith("https://"):
        raise ValueError(f"{where}: source_url must be an https URL")
    return url


def parse_calendar(document: Mapping[str, object], label: str = "calendar") -> Tuple[Meeting, ...]:
    """The meetings of a calendar document, in start order.

    Raises:
        ValueError: a meeting that ends before it starts, or two dates for one meeting; a meeting dated before its
            own announcement; a source that is not an https URL; a cancellation of a meeting that is not scheduled,
            or announced before the meeting was public.
    """

    first_public: Dict[date, datetime] = {}
    ends: Dict[date, date] = {}
    urls: Dict[date, str] = {}
    for number, entry in enumerate(document["schedule_announcements"]):
        where = f"{label} schedule {number}"
        announced = _instant(entry, where)
        url = _check_url(entry, where)
        for raw in entry["meetings"]:
            start, end = date.fromisoformat(raw["start"]), date.fromisoformat(raw["end"])
            if end < start:
                raise ValueError(f"{where}: meeting {start} ends {end}, before it starts")
            if start in ends and ends[start] != end:
                raise ValueError(f"{where}: meeting {start} has two end dates, {ends[start]} and {end}")
            if announced.date() > start:
                raise ValueError(f"{where}: meeting {start} is dated before its announcement {announced}")
            if start not in first_public or announced < first_public[start]:
                first_public[start], urls[start] = announced, url
            ends[start] = end
    cancelled: Dict[date, datetime] = {}
    for number, raw in enumerate(document["cancellations"]):
        where = f"{label} cancellation {number}"
        start = date.fromisoformat(raw["meeting_start"])
        if start not in first_public:
            raise ValueError(f"{where}: {start} is not a scheduled meeting")
        when = _instant(raw, where)
        if when <= first_public[start]:
            raise ValueError(f"{where}: cancelled {when}, before the meeting was public at {first_public[start]}")
        _check_url(raw, where)
        cancelled[start] = when
    meetings: List[Meeting] = [
        Meeting(f"scheduled-{start.isoformat()}", "scheduled", start, ends[start], first_public[start],
                cancelled.get(start), urls[start])
        for start in first_public
    ]
    for number, raw in enumerate(document["unscheduled_meetings"]):
        where = f"{label} unscheduled meeting {number}"
        start = date.fromisoformat(raw["date"])
        meetings.append(
            Meeting(f"unscheduled-{start.isoformat()}", "unscheduled", start, start, _instant(raw, where), None,
                    _check_url(raw, where))
        )
    ids = [m.id for m in meetings]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label}: duplicate meeting id")
    return tuple(sorted(meetings, key=lambda m: (m.start, m.id)))


def load_calendar(path: Path = CALENDAR_PATH) -> Tuple[Meeting, ...]:
    """Read and check `metadata/fomc_calendar.json` (see `parse_calendar` for what is refused)."""

    return parse_calendar(json.loads(Path(path).read_text(encoding="utf-8")), str(path))


def _check_instant(as_of: datetime) -> None:
    if not isinstance(as_of, datetime):
        raise ValueError(f"as_of must be a datetime, not {type(as_of).__name__}")
    if as_of.tzinfo is not None:
        raise ValueError("as_of is a naive America/New_York wall-clock datetime")


def require_public(meeting: Meeting, as_of: datetime) -> Meeting:
    """Return `meeting`, or raise `LookAheadError` if it was not public at `as_of`."""

    _check_instant(as_of)
    if meeting.public_at > as_of:
        raise LookAheadError(
            f"FOMC meeting {meeting.id} is public from {meeting.public_at}, after the decision instant {as_of}"
        )
    return meeting


def visible_at(meeting: Meeting, as_of: datetime) -> bool:
    """Whether `meeting` is public at `as_of` and its cancellation, if any, is not."""

    return meeting.public_at <= as_of and (meeting.cancelled_at is None or meeting.cancelled_at > as_of)


def fomc_feature_values(
    calendar: Sequence[Meeting], target: date, as_of: datetime
) -> Dict[str, float]:
    """The columns for the target day `target`, from the calendar as it stood at the decision instant `as_of`.

    Raises:
        LookAheadError: a meeting that was not public at `as_of` reached a value (cannot happen through
            `visible_at`; the guard is explicit).
        ValueError: `as_of` is not a naive wall-clock datetime, is on a day after `target`, or is before the first
            published schedule (the calendar would read as empty, not as unknown).
    """

    _check_instant(as_of)
    if as_of.date() > target:
        raise ValueError(f"decision instant {as_of} is after the target day {target}")
    if calendar and as_of < min(m.public_at for m in calendar):
        raise ValueError(f"decision instant {as_of} is before the first published schedule")
    seen = [m for m in calendar if visible_at(m, as_of)]
    for meeting in seen:
        require_public(meeting, as_of)
    today = any(m.start <= target <= m.end for m in seen)
    ahead = [(m.start - target).days for m in seen if m.start >= target]
    wait = min(DAYS_CAP, min(ahead)) if ahead else DAYS_CAP
    return {"fomc_meeting_day": float(today), "fomc_days_to_next_meeting": float(wait)}


def add_columns(
    rows: Sequence[DailyObservation],
    calendar: Optional[Sequence[Meeting]] = None,
    *,
    horizon: int = 1,
    decision_time: time = time(16, 0),
) -> List[DailyObservation]:
    """`rows` with the columns added: each row's day, read at the decision instant `horizon` panel days before it.

    A row before the first one that far back is read at the same time on the day `horizon` calendar days before
    it. A row's values depend on its own date, the dates before it and the calendar, never on the rows after it.
    """

    if horizon < 1:
        raise ValueError("horizon is at least one panel day")
    meetings = load_calendar() if calendar is None else calendar
    out: List[DailyObservation] = []
    for index, row in enumerate(rows):
        decided = rows[index - horizon].date if index >= horizon else row.date - timedelta(days=horizon)
        values = dict(row.values)
        values.update(fomc_feature_values(meetings, row.date, datetime.combine(decided, decision_time)))
        out.append(DailyObservation(row.date, values))
    return out
