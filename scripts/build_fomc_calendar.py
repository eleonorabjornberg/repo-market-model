"""Build the FOMC meeting calendar, dated by what was public when, from the Board's own pages (#1038).

    python3 scripts/build_fomc_calendar.py
    python3 scripts/build_fomc_calendar.py --check

`tests/fixtures/snapshots/fomc_calendar/pages/` holds the Board's pages as fetched, one plain GET each (the manifest
beside it gives each page's URL, SHA-256 and retrieval instant):

* the meeting calendar page (2021-2027) and the three historical pages (2018, 2019, 2020);
* one press release per published schedule ("The Federal Open Market Committee on <weekday> announced its tentative
  meeting schedule for <year>"), each with its "For release at <h:mm> <a.m.|p.m.> <EDT|EST>" line;
* the release of each unscheduled meeting and each notation vote, which is when it first became public.

It writes `metadata/fomc_calendar.json`. Every date and instant in it is read from those pages: a page that does not
yield exactly what the table below says it should is refused, and the meetings of every schedule are cross-checked
against what the calendar pages say happened (held, cancelled). `--check` rebuilds the file in memory and exits 1 if the
tracked copy differs, so the register is a command over tracked bytes.

What is NOT read from a page, and is therefore declared here and in `docs/decisions/fomc-calendar.md` for review:

* which release belongs to which event (`UNSCHEDULED`, `NOTATION_VOTES`), checked against the label the Board's
  calendar page prints for that date;
* the instant the cancellation of the 17-18 March 2020 meeting became public (`CANCELLATIONS`): the Board's page marks
  the meeting "(cancelled)" and dates nothing, so it is declared as the release of the 15 March 2020 statement, the first
  public word of the Committee meeting that day (the later of the two plausible instants, so the meeting stays visible
  rather than vanishing early).

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "tests" / "fixtures" / "snapshots" / "fomc_calendar"
MANIFEST_PATH = SNAPSHOT_DIR / "manifest.json"
OUTPUT_PATH = ROOT / "metadata" / "fomc_calendar.json"
BUILT_BY = "scripts/build_fomc_calendar.py"

CALENDAR_PAGES = ("fomccalendars.htm", "fomchistorical2018.htm", "fomchistorical2019.htm", "fomchistorical2020.htm")

#: Schedule releases, in publication order: the page, and the years its meetings may carry.
SCHEDULE_PAGES = (
    "monetary20170511b.htm",
    "monetary20180525a.htm",
    "monetary20190517a.htm",
    "monetary20200702a.htm",
    "monetary20210604a.htm",
    "monetary20220624a.htm",
    "monetary20230623a.htm",
    "monetary20240809a.htm",
    "monetary20250905a.htm",
)

#: (meeting date, release page, label the Board's calendar page prints for it).
UNSCHEDULED = (
    (date(2019, 10, 4), "monetary20191011a.htm", "October 4 (unscheduled)"),
    (date(2020, 3, 2), "monetary20200303a.htm", "March 2 (unscheduled)"),
    (date(2020, 3, 15), "monetary20200315a.htm", "March 15 (unscheduled)"),
)
#: (vote date, release page, label).
NOTATION_VOTES = (
    (date(2020, 3, 19), "monetary20200319b.htm", "March 19 (notation vote)"),
    (date(2020, 3, 23), "monetary20200323a.htm", "March 23 (notation vote)"),
    (date(2020, 3, 31), "monetary20200331a.htm", "March 31 (notation vote)"),
    (date(2020, 8, 27), "monetary20200827a.htm", "August 27 (notation vote)"),
    (date(2025, 8, 22), "monetary20250822a.htm", "22 (notation vote)"),
)
#: (meeting start, release page whose release instant is taken as the public cancellation, label).
CANCELLATIONS = ((date(2020, 3, 17), "monetary20200315a.htm", "March 17-18 (cancelled)"),)

BASE_URL = "https://www.federalreserve.gov/newsevents/pressreleases/"
MONTHS = {
    name: number
    for number, name in enumerate(
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
         "November", "December"],
        start=1,
    )
}
SHORT_MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dec": 12}


def lines_of(payload: bytes) -> List[str]:
    text = payload.decode("utf-8", errors="replace")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", text))
    return [line.strip().replace("\xa0", " ") for line in text.split("\n") if line.strip()]


def read_page(name: str) -> bytes:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next((p for p in manifest["pages"] if p["path"] == f"pages/{name}"), None)
    if entry is None:
        raise ValueError(f"{name}: not in {MANIFEST_PATH}")
    payload = (SNAPSHOT_DIR / entry["path"]).read_bytes()
    if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
        raise ValueError(f"{name}: bytes do not match the manifest's SHA-256")
    return payload


def release_instant(name: str) -> Tuple[date, str, str]:
    """The page's own release date, wall-clock time (HH:MM, 24h) and the zone word it states."""

    lines = lines_of(read_page(name))
    stamp = re.search(r"monetary(\d{4})(\d{2})(\d{2})[a-z0-9]*\.htm", name)
    day = date(int(stamp.group(1)), int(stamp.group(2)), int(stamp.group(3)))
    hits = [i for i, line in enumerate(lines) if line.startswith("For release at")]
    if len(hits) != 1:
        raise ValueError(f"{name}: expected one 'For release at' line, found {len(hits)}")
    when = re.fullmatch(r"For release at (\d{1,2}):(\d{2}) ([ap])\.m\. (E[DS]T)", lines[hits[0]])
    if when is None:
        raise ValueError(f"{name}: unreadable release line {lines[hits[0]]!r}")
    dated = [lines[k] for k in (hits[0] - 2, hits[0] - 1) if re.fullmatch(r"[A-Z][a-z]+ \d{2}, \d{4}", lines[k])]
    if dated and datetime.strptime(dated[0], "%B %d, %Y").date() != day:
        raise ValueError(f"{name}: page date {dated[0]} differs from its file name {day}")
    hour = int(when.group(1)) % 12 + (12 if when.group(3) == "p" else 0)
    return day, f"{hour:02d}:{when.group(2)}", when.group(4)


def schedule_meetings(name: str) -> Tuple[str, List[Tuple[date, date]]]:
    """The announcement sentence, and every meeting the release lists, as (first day, last day)."""

    lines = lines_of(read_page(name))
    title_year = None
    sentence = None
    out: List[Tuple[date, date]] = []
    year = None
    start = None
    for i, line in enumerate(lines):
        if "announced its tentative meeting schedule" in line and sentence is None:
            sentence = line
            found = re.search(r"schedule for (\d{4})(?: and (\d{4}))?", line)
            title_year = int(found.group(1))
            year = title_year
            start = i + 1
            break
    if sentence is None:
        raise ValueError(f"{name}: no 'announced its tentative meeting schedule' sentence")
    for line in lines[start:]:
        if line.startswith(("For media", "The Chair", "The Committee", "Last Update")):
            break
        for_year = re.fullmatch(r"For (\d{4}):", line)
        if for_year:
            year = int(for_year.group(1))
            continue
        long = re.fullmatch(
            r"(?:Mon|Tues|Wednes|Thurs|Fri)day, ([A-Z][a-z]+) (\d{1,2}), and (?:Mon|Tues|Wednes|Thurs|Fri)day, "
            r"([A-Z][a-z]+) (\d{1,2})(?:, (\d{4}))?",
            line,
        )
        short = re.fullmatch(
            r"([A-Z][a-z]+) (\d{1,2})-(?:([A-Z][a-z]+) )?(\d{1,2})(?:, (\d{4}))? \([A-Za-z]+-[A-Za-z]+\)", line
        )
        if long:
            m1, d1, m2, d2, y = long.group(1), long.group(2), long.group(3), long.group(4), long.group(5)
        elif short:
            m1, d1, m2, d2, y = short.group(1), short.group(2), short.group(3) or short.group(1), short.group(4), short.group(5)
        else:
            raise ValueError(f"{name}: unreadable meeting line {line!r}")
        meeting_year = int(y) if y else year
        out.append((date(meeting_year, MONTHS[m1], int(d1)), date(meeting_year, MONTHS[m2], int(d2))))
    if len(out) < 9:
        raise ValueError(f"{name}: only {len(out)} meetings read; every schedule lists at least nine")
    return sentence, out


def _range(month_text: str, days_text: str, year: int) -> Tuple[date, date]:
    """`April/May` + `30-1`, `January` + `27-28`, `Jul/Aug` + `31-1`, `March` + `17-18*`."""

    months = [MONTHS.get(part) or SHORT_MONTHS[part] for part in month_text.split("/")]
    first, last = re.fullmatch(r"(\d{1,2})(?:-(\d{1,2}))?\**", days_text).groups()
    start = date(year, months[0], int(first))
    if last is None:
        return start, start
    end_month = months[-1]
    if len(months) == 1 and int(last) < int(first):
        end_month = months[0] + 1
    return start, date(year, end_month, int(last))


def calendar_page_events() -> Dict[str, List[Tuple[date, date, str]]]:
    """(first day, last day, status) per meeting on the Board's calendar pages, by page.

    status is `held`, `cancelled`, `unscheduled` or `notation`.
    """

    out: Dict[str, List[Tuple[date, date, str]]] = {}
    for name in CALENDAR_PAGES:
        lines = lines_of(read_page(name))
        rows: List[Tuple[date, date, str]] = []
        if name == "fomccalendars.htm":
            year = None
            month = None
            for line in lines:
                header = re.fullmatch(r"(\d{4}) FOMC Meetings", line)
                if header:
                    year, month = int(header.group(1)), None
                    continue
                if year is None:
                    continue
                if line.startswith("Back to Top"):
                    break
                if re.fullmatch(r"(?:[A-Z][a-z]+)(?:/[A-Z][a-z]+)?", line) and (
                    line.split("/")[0] in MONTHS or line.split("/")[0] in SHORT_MONTHS
                ):
                    month = line
                    continue
                if month is None:
                    continue
                notation = re.fullmatch(r"(\d{1,2}) \(notation vote\)", line)
                if notation:
                    day = date(year, MONTHS[month], int(notation.group(1)))
                    rows.append((day, day, "notation"))
                    month = None
                elif re.fullmatch(r"\d{1,2}(?:-\d{1,2})?\*?", line):
                    start, end = _range(month, line, year)
                    rows.append((start, end, "held" if year <= 2026 and start <= date(2026, 10, 7) else "scheduled"))
                    month = None
        else:
            year = int(re.search(r"(\d{4})", name).group(1))
            for line in lines:
                found = re.fullmatch(
                    r"([A-Z][a-z]+(?:/[A-Z][a-z]+)?) (\d{1,2}(?:-\d{1,2})?)(?: \((cancelled|unscheduled|notation vote)\))?"
                    r" (?:Meeting )?- (\d{4})",
                    line,
                )
                if found and int(found.group(4)) == year:
                    label = found.group(3)
                    status = {None: "held", "cancelled": "cancelled", "unscheduled": "unscheduled",
                              "notation vote": "notation"}[label]
                    start, end = _range(found.group(1), found.group(2), year)
                    rows.append((start, end, status))
        out[name] = rows
    return out


def build() -> Dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pages = {p["path"][len("pages/"):]: p for p in manifest["pages"]}

    def url_of(name: str) -> str:
        return pages[name]["url"]

    announcements = []
    for name in SCHEDULE_PAGES:
        day, clock, zone = release_instant(name)
        sentence, meetings = schedule_meetings(name)
        announcements.append(
            {
                "id": f"schedule-{name[len('monetary'):len('monetary') + 8]}",
                "announced_date": day.isoformat(),
                "announced_time": clock,
                "time_zone_stated": zone,
                "time_basis": "stated",
                "source_url": url_of(name),
                "page": f"pages/{name}",
                "source_sentence": sentence,
                "meetings": [{"start": a.isoformat(), "end": b.isoformat()} for a, b in meetings],
            }
        )
    announcements.sort(key=lambda a: (a["announced_date"], a["announced_time"]))

    # A meeting listed by two releases must carry the same dates in both: the later release only repeats it.
    seen: Dict[str, Tuple[str, str]] = {}
    for entry in announcements:
        for meeting in entry["meetings"]:
            key = meeting["start"]
            if key in seen and seen[key] != (meeting["start"], meeting["end"]):
                raise ValueError(f"meeting {key} is listed with two different dates")
            seen[key] = (meeting["start"], meeting["end"])
    for entry in announcements:
        for meeting in entry["meetings"]:
            if seen[meeting["start"]][1] != meeting["end"]:
                raise ValueError(f"meeting {meeting['start']} ends on two different days")

    page_events = calendar_page_events()
    labels = "\n".join(
        "\n".join(lines_of(read_page(n))) for n in CALENDAR_PAGES
    )

    def need_label(label: str) -> None:
        if label.split(" (")[0].isdigit() or label.startswith("22 ("):
            if "22\n(notation vote)" not in labels and "22 (notation vote)" not in labels:
                raise ValueError(f"the Board's calendar page does not print {label!r}")
        elif label not in labels and label.replace(" (", " (") not in labels:
            raise ValueError(f"the Board's calendar page does not print {label!r}")

    def event(name: str, day: date, label: str, kind: str) -> Dict[str, object]:
        need_label(label)
        released, clock, zone = release_instant(name)
        title_lines = lines_of(read_page(name))
        at = next(i for i, line in enumerate(title_lines) if line.startswith("For release at"))
        return {
            "kind": kind,
            "date": day.isoformat(),
            "announced_date": released.isoformat(),
            "announced_time": clock,
            "time_zone_stated": zone,
            "time_basis": "stated",
            "source_url": url_of(name),
            "page": f"pages/{name}",
            "release_title": title_lines[at - 1],
            "calendar_label": label,
        }

    unscheduled = [event(n, d, label, "unscheduled_meeting") for d, n, label in UNSCHEDULED]
    notation = [event(n, d, label, "notation_vote") for d, n, label in NOTATION_VOTES]
    cancellations = []
    for start, name, label in CANCELLATIONS:
        need_label(label)
        released, clock, zone = release_instant(name)
        cancellations.append(
            {
                "meeting_start": start.isoformat(),
                "announced_date": released.isoformat(),
                "announced_time": clock,
                "time_zone_stated": zone,
                "time_basis": "declared",
                "source_url": url_of(name),
                "page": f"pages/{name}",
                "calendar_label": label,
                "note": "The Board's calendar page marks the meeting cancelled and dates nothing. Declared as the "
                "release of the statement that closed the 15 March 2020 meeting, the first public word of the "
                "Committee's meeting that replaced it (docs/decisions/fomc-calendar.md, marked question).",
            }
        )

    # Cross-check: every scheduled meeting in the first nine-or-so years' releases through the end of the
    # calendar pages' held range is on a calendar page as held or cancelled, and every held meeting is scheduled.
    scheduled = {(date.fromisoformat(m["start"]), date.fromisoformat(m["end"])) for e in announcements for m in e["meetings"]}
    on_pages = {(a, b, s) for rows in page_events.values() for a, b, s in rows}
    held = {(a, b) for a, b, s in on_pages if s in ("held", "cancelled", "scheduled")}
    first_day = min(a for a, _ in scheduled if a >= date(2018, 1, 1))
    missing_on_page = sorted(m for m in scheduled if m not in held and first_day <= m[0] <= date(2027, 12, 31))
    if missing_on_page:
        raise ValueError(f"scheduled meetings the calendar pages do not carry: {missing_on_page}")
    extra_on_page = sorted(m for m in held if m not in scheduled)
    if extra_on_page:
        raise ValueError(f"meetings on the calendar pages that no schedule release listed: {extra_on_page}")
    unscheduled_on_pages = {(a, s) for a, b, s in on_pages if s == "unscheduled"}
    if unscheduled_on_pages != {(d, "unscheduled") for d, _, _ in UNSCHEDULED}:
        raise ValueError("the calendar pages' unscheduled meetings differ from the declared list")
    notation_on_pages = {a for a, b, s in on_pages if s == "notation"}
    if notation_on_pages != {d for d, _, _ in NOTATION_VOTES}:
        raise ValueError("the calendar pages' notation votes differ from the declared list")
    cancelled_on_pages = {a for a, b, s in on_pages if s == "cancelled"}
    if cancelled_on_pages != {s for s, _, _ in CANCELLATIONS}:
        raise ValueError("the calendar pages' cancelled meetings differ from the declared list")

    return {
        "built_by": BUILT_BY,
        "note": "Read from the tracked Board pages in tests/fixtures/snapshots/fomc_calendar/pages by "
        "scripts/build_fomc_calendar.py; `--check` rebuilds it. A scheduled meeting is public from the earliest "
        "schedule release that lists it (its announced_date and announced_time, Eastern wall clock). An unscheduled "
        "meeting is public from its own release. Notation votes are listed apart and are not meetings. Instants are "
        "naive America/New_York wall-clock times, as in metadata/policy_events.json. Each meeting date is tentative "
        "until the Committee confirms it at the meeting before it (the Board's calendar page says so).",
        "schedule_announcements": announcements,
        "unscheduled_meetings": unscheduled,
        "notation_votes": notation,
        "cancellations": cancellations,
    }


def render() -> str:
    return json.dumps(build(), indent=2, sort_keys=False) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the tracked file differs")
    args = parser.parse_args(argv)
    text = render()
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != text:
            print(f"{OUTPUT_PATH} differs from what the tracked pages give; run scripts/build_fomc_calendar.py")
            return 1
        print("ok")
        return 0
    OUTPUT_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
