#!/usr/bin/env python3
"""Keep each business day's DTCC GCF Repo Index value, fetched between 15:30 and 16:00 ET (#962).

    PYTHONPATH=src python3 scripts/gcf_index_capture.py capture --out-dir DIR
    PYTHONPATH=src python3 scripts/gcf_index_capture.py verify --dir DIR

DTCC posts the day's index at about 15:30 ET on the day itself (`repo_model.gcf_index`).
`.github/workflows/gcf-index-capture.yml` runs `capture` in slots around that time and appends the day's file,
`gcf/<effective date>.json`, to the add-only `gcf-index-captures` branch. One request per run, to
`https://cms-prod.dtcc.com/data/gcfindex.csv?v=<epoch ms>` (the cache-busting query the page itself sends).

* Before 15:30 ET, on a weekend or a holiday, or when the day is already on the branch: nothing is fetched.
* From 15:30 to 16:00 ET inclusive: fetch. If the file has the day's Treasury row, keep it (`captured`); if not, write
  nothing and exit 0, and a later slot tries again.
* After 16:00 ET (or a fetch that returns after it): fetch once and record the day `missed`, with no value:
  `fetched_after_decision` if the row is there, `no_posting` if it is not, `unreadable_response` if the file does not
  parse. A day is never back-filled.
* Business days after the branch's first day that have no file at all are recorded `no_run`, with no fetch.
* A response that does not parse inside the window writes nothing: exit 2, the run goes red, a later slot retries.

Exit codes: 0 done or nothing to do, 1 `LookAheadError`, 2 a refused (malformed) response. Stdlib only.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import gcf_index as gi, ingest  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def _existing(out_dir: Path) -> set:
    return {date.fromisoformat(path.stem) for path in (Path(out_dir) / "gcf").glob("*.json")}


def capture(out_dir: Path, now: datetime, downloader=ingest._download, clock=None) -> str:
    """One run at `now`. Returns what happened: none, wait, done, not_posted, captured or missed.

    `clock` (default: the real clock) stamps when the response arrived.

    Raises:
        ValueError: the response did not parse inside the window.
        LookAheadError: a record that the guard refuses (never written).
    """

    now_clock = clock or (lambda: datetime.now(timezone.utc))
    already = _existing(out_dir)
    decision = gi.plan(now, already)
    for day in decision.gaps:
        path = gi.write_record(out_dir, gi.missed_record(day, "no_run"))
        print(f"wrote {path} (no run on {day.isoformat()}; not back-filled)")
    if decision.action in ("none", "wait", "done"):
        print(f"{decision.action}: nothing to fetch at {now.isoformat()}")
        return decision.action
    day = decision.day
    url = f"{gi.CSV_URL}?v={int(now.timestamp() * 1000)}"
    payload = downloader(url)
    fetched_at = max(now_clock(), now)
    late = fetched_at > gi.decision_instant(day)
    try:
        rows = gi.parse_csv(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        if decision.action == "fetch" and not late:
            raise ValueError(f"the response did not parse: {exc}") from exc
        record = gi.missed_record(day, "unreadable_response", fetched_at=fetched_at, url=url, payload=payload)
        path = gi.write_record(out_dir, record)
        print(f"wrote {path} (missed: unreadable response)")
        return "missed"
    row = rows.get(day)
    posted = row is not None and row["treasury_rate_percent"] is not None and row["treasury_par_usd"] is not None
    if decision.action == "fetch" and not late:
        if not posted:
            print(f"{day.isoformat()} is not posted yet at {fetched_at.isoformat()}; a later slot tries again")
            return "not_posted"
        path = gi.write_record(out_dir, gi.captured_record(payload, url=url, fetched_at=fetched_at, effective=day))
        print(f"wrote {path} (Treasury {rows[day]['treasury_rate_percent']}, fetched {fetched_at.isoformat()})")
        return "captured"
    reason = "fetched_after_decision" if posted else "no_posting"
    path = gi.write_record(out_dir, gi.missed_record(day, reason, fetched_at=fetched_at, url=url, payload=payload))
    print(f"wrote {path} (missed: {reason}; no value kept)")
    return "missed"


def verify(directory: Path) -> int:
    records = gi.read_all(directory)
    captured = sum(1 for r in records if r["status"] == "captured")
    print(f"{len(records)} day records verified ({captured} captured, {len(records) - captured} missed)")
    return 0


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
            return verify(args.dir)
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
