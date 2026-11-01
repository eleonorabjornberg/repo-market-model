#!/usr/bin/env python3
"""Poll Treasury's bill-rate export (and, on Thursdays, the FR 2004 release page) after 16:00 ET and keep each poll (#1343).

    PYTHONPATH=src python3 scripts/availability_poll.py capture --out-dir DIR [--now ISO]
    PYTHONPATH=src python3 scripts/availability_poll.py verify --dir DIR

`.github/workflows/availability-poll.yml` runs `capture` every ten minutes and adds the files to the add-only
`availability-polls` branch. `capture` decides from the ET clock (`repo_model.availability_poll.sources_due`): outside
a business day's 16:00-18:30 ET window it fetches nothing and exits 0. A failed poll is a record, never a crash.
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

    due = ap.sources_due(now)
    if not due:
        print(f"nothing to poll at {now.isoformat()}")
        return []
    paths = []
    for source in due:
        path = ap.write_record(out_dir, ap.poll_record(source, now, fetcher, clock))
        print(f"wrote {path}")
        paths.append(path)
    return paths


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    cap = sub.add_parser("capture")
    cap.add_argument("--out-dir", type=Path, required=True)
    cap.add_argument("--now", help="an aware ISO instant, for a test; defaults to the clock")
    ver = sub.add_parser("verify")
    ver.add_argument("--dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
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
