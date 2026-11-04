#!/usr/bin/env python3
"""Poll Treasury's bill-rate export (and, on Thursdays, the FR 2004 release page) after 16:00 ET and keep each poll (#1343).

    PYTHONPATH=src python3 scripts/availability_poll.py capture --out-dir DIR [--now ISO]
    PYTHONPATH=src python3 scripts/availability_poll.py verify --dir DIR
    PYTHONPATH=src python3 scripts/availability_poll.py missing --dir DIR [--list FILE] [--now ISO] [--days-out FILE]

`.github/workflows/availability-poll.yml` runs `capture` every ten minutes and adds the files to the add-only
`availability-polls` branch. `capture` decides from the ET clock (`repo_model.availability_poll.sources_due`): outside
a business day's 16:00-18:30 ET window it fetches nothing and exits 0, except a catch-up (#1441): a run after 18:30
ET on a business day records, once per source and day, the first `latest_date` it sees, marked `catch_up`, with its true
fetch time, unless that source already has an in-window record that day. A failed poll is a record, never a crash.
`missing` names each business day since 3 November 2026 with no in-window record that is not on the tracked list
`metadata/availability_missed_days.json`: exit 3, one line per day on stderr; a list that contradicts the branch is exit 2.
The records are a measurement of when each source first shows a day; they change no declaration. Stdlib only.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import availability_poll as ap  # noqa: E402


def capture(out_dir: Path, now: datetime, fetcher=ap.fetch, clock=None) -> list:
    """Poll what is due at `now`; returns the paths written."""

    kind = ap.IN_WINDOW
    due = ap.sources_due(now)
    if not due:
        kind = ap.CATCH_UP
        due = ap.catch_up_due(now, ap.read_day(out_dir, now.astimezone(ap.EASTERN).date()))
    if not due:
        print(f"nothing to poll at {now.isoformat()}")
        return []
    paths = []
    for source in due:
        path = ap.write_record(out_dir, ap.poll_record(source, now, fetcher, clock, kind))
        print(f"wrote {path}")
        paths.append(path)
    return paths


def missing(directory: Path, listed: Path, now: datetime, days_out=None) -> int:
    """Exit 3 and name each business day over with no in-window record that is not on the tracked list."""

    today = now.astimezone(ap.EASTERN).date()
    lost = ap.unlisted_misses(ap.read_all(directory, require=True), today, ap.read_missed(listed))
    if days_out is not None:
        Path(days_out).write_text("".join(f"{day.isoformat()}\n" for day in lost), encoding="utf-8")
    if not lost:
        print("no unlisted business day without an in-window poll")
        return 0
    for day in lost:
        print(
            f"MISSED availability poll: {day.isoformat()} has no in-window record under polls/. List it with the "
            f"slots scheduled, the runs that happened and a reason in {ap.MISSED_LIST.relative_to(REPO)}.",
            file=sys.stderr,
        )
    return 3


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    cap = sub.add_parser("capture")
    cap.add_argument("--out-dir", type=Path, required=True)
    cap.add_argument("--now", help="an aware ISO instant, for a test; defaults to the clock")
    ver = sub.add_parser("verify")
    ver.add_argument("--dir", type=Path, required=True)
    mis = sub.add_parser("missing")
    mis.add_argument("--dir", type=Path, required=True)
    mis.add_argument("--list", type=Path, default=ap.MISSED_LIST, help="the tracked list of missed days")
    mis.add_argument("--now", help="an aware ISO instant, for a test; defaults to the clock")
    mis.add_argument("--days-out", type=Path, help="write the unlisted dates here, one per line")
    args = parser.parse_args(argv)
    try:
        if args.command == "missing":
            now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
            return missing(args.dir, args.list, now, args.days_out)
        if args.command == "verify":
            print(f"{len(ap.read_all(args.dir))} poll records verified")
            return 0
        capture(args.out_dir, datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc))
        return 0
    except ValueError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
