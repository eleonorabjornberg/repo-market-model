#!/usr/bin/env python3
"""Keep each business day's first SOFR print, separately from any same-day revision (#940).

    PYTHONPATH=src python3 scripts/sofr_first_print.py capture --out-dir DIR
    PYTHONPATH=src python3 scripts/sofr_first_print.py verify --dir DIR
    PYTHONPATH=src python3 scripts/sofr_first_print.py missing --dir DIR --list FILE [--days-out FILE]

The New York Fed publishes SOFR at about 08:00 ET on the next business day and may revise it at about 14:30 ET
(`repo_model.sofr_first_print`). `.github/workflows/sofr-first-print.yml` runs `capture` in the morning, after
08:00 ET and long before 14:30, and appends the day's file, `sofr/<effective date>.json`, to the add-only
`sofr-first-prints` branch. `capture` names the latest effective date published at the moment it runs, takes the
day's row with the repository's fetcher (`ingest.fetch_nyfed_reference_rate`), and writes one record: the payload as
fetched, the retrieval time, its SHA-256, the publication and revision instants and IORB's first-public source.

* A run before 08:00 ET, on a weekend or on a holiday writes nothing and exits 0.
* A day already captured is never fetched again or overwritten: exit 0.
* A fetch that ends at or after the revision instant, or a row already marked revised, is a `LookAheadError`:
  nothing is written and the exit code is 1. The day is lost as a first print and is not back-filled.

* `missing` (#1404) names every business day whose revision instant has passed, that has no file under DIR and that is not
  on the tracked list of lost days (`metadata/sofr_missed_first_prints.json`): exit 3, one line per day on stderr and,
  with `--days-out`, one date per line in that file. The workflow runs it after every slot and comments on #225. A
  list that contradicts the branch is exit 2. Nothing is back-filled.

The live record (`scripts/live_record.py`) runs after the 16:00 ET decision, hours after a revision could have
replaced the print, so it cannot keep first prints itself; its pinned code is untouched.

Stdlib only.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import ingest, sofr_first_print as fp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def capture(out_dir: Path, now: datetime, downloader=ingest._download, clock=None):
    """Capture the latest published first print into `out_dir`. Returns the path written, or None.

    `now` names the day; `clock` (default: the real clock) stamps when each response arrived.

    Raises:
        LookAheadError: the fetch ended at or after the revision instant, or the row is marked revised.
        ValueError: the response is malformed or has no row for the day.
    """

    effective = fp.latest_published(now)
    if effective is None:
        print("nothing is published yet at this time (before 08:00 ET, a weekend or a holiday)")
        return None
    if (Path(out_dir) / "sofr" / f"{effective.isoformat()}.json").exists():
        print(f"{effective.isoformat()} is already captured; a first print is never overwritten")
        return None
    fetched = []

    def timed(url):
        payload = downloader(url)
        fetched.append((clock or (lambda: datetime.now(timezone.utc)))())
        return payload

    with tempfile.TemporaryDirectory() as scratch:
        artifacts = ingest.fetch_nyfed_reference_rate(
            Path(scratch), "sofr", effective.isoformat(), effective.isoformat(), downloader=timed
        )
        rate = next(a for a in artifacts if "type=rate" in a.url)
        payload = rate.path.read_bytes()
        url = rate.url
    # The retrieval time is when the response arrived, never earlier: the guard must not under-read lateness.
    retrieved_at = max(fetched)
    record = fp.first_print_record(
        payload, url=url, retrieved_at=retrieved_at, effective=effective, iorb=fp.iorb_source(effective)
    )
    path = fp.write_first_print(out_dir, record)
    print(f"wrote {path} (SOFR {record['sofr_percent']}, retrieved {record['retrieved_at']})")
    return path


def verify(directory: Path) -> int:
    records = fp.read_all(directory)
    print(f"{len(records)} first prints verified")
    return 0


def missing(directory: Path, listed: Path, now: datetime, days_out=None) -> int:
    """Exit 3 and name each due business day that has no first print and is not on the tracked list."""

    lost = fp.unflagged_misses(fp.captured_days(directory), now, fp.read_missed(listed))
    if days_out is not None:
        Path(days_out).write_text("".join(f"{day.isoformat()}\n" for day in lost), encoding="utf-8")
    if not lost:
        print("no unlisted business day without a first print")
        return 0
    for day in lost:
        print(
            f"MISSED first print: {day.isoformat()} has no file under sofr/ and its revision instant "
            f"{fp.revision_instant(day).isoformat()} ET has passed; it is never back-filled. "
            f"List it with its reason in {fp.MISSED_LIST.relative_to(REPO)}.",
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
    mis.add_argument("--list", type=Path, default=fp.MISSED_LIST, help="the tracked list of lost days")
    mis.add_argument("--now", help="an aware ISO instant, for a test; defaults to the clock")
    mis.add_argument("--days-out", type=Path, help="write the unlisted dates here, one per line")
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            return verify(args.dir)
        if args.command == "missing":
            now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
            return missing(args.dir, args.list, now, args.days_out)
        now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
        capture(args.out_dir, now)
        return 0
    except LookAheadError as exc:
        print(f"look-ahead: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
