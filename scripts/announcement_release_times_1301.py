"""The stated release time of every Treasury offering announcement in the tracked auctions snapshot (#1301; read for #1310).

`metadata/settlement_announcement_dating.json` dates a settlement from its auction's announcement, 12:00 New York time on
`announcemt_date`, and says Treasury publishes no clock time for an announcement. Every announcement PDF does state its release time
("Embargoed Until 11:00 A.M.", or "For Immediate Release"). This script reads the PDF named in `pdf_filenm_announcemt` for each record of the
tracked snapshot, from treasurydirect.gov, and counts the stated times by class.

    python3 scripts/announcement_release_times_1301.py fetch --output metadata/announcement_release_times_1301.json
    python3 scripts/announcement_release_times_1301.py check

`fetch` needs the network and `pdftotext` (poppler). `parse_release` and `summarise` need neither, and `tests/test_announcement_release_times_1301.py`
runs them on fixture text. The record it writes carries the stated text per file, so a reader can re-derive every count without the network.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "tests/fixtures/snapshots/funding_inputs/treasury_auctions/20260914T051023Z_722359ea9bc7.json"
URL = "https://www.treasurydirect.gov/instit/annceresult/press/preanre/{year}/{name}"
#: The release time the dating declaration stamps, and the published records' decision time (New York).
DECLARED = "12:00"
DECISION = "16:00"
IMMEDIATE = "immediate"
UNREADABLE = "unreadable"

EMBARGO = re.compile(r"Embargoed\s+Until:?\s*(\d{1,2})[:.](\d{2})\s*([AaPp])\.?\s*[Mm]\.?")
IMMEDIATE_RELEASE = re.compile(r"For\s+Immediate\s+Release", re.IGNORECASE)

BILL, CASH_MANAGEMENT, COUPON = "bills", "cash_management_bills", "notes_and_bonds"


def parse_release(text: str) -> str:
    """The stated release time as "HH:MM" (24-hour), `IMMEDIATE`, or `UNREADABLE`.

    A time wins over "for immediate release" when a PDF carries both words, which none of the tracked ones does.
    """

    found = EMBARGO.search(text)
    if found:
        hour, minute, half = int(found.group(1)), int(found.group(2)), found.group(3).lower()
        if hour == 12:
            hour = 0
        if half == "p":
            hour += 12
        return f"{hour:02d}:{minute:02d}"
    if IMMEDIATE_RELEASE.search(text):
        return IMMEDIATE
    return UNREADABLE


def record_class(record: Mapping[str, object]) -> str:
    """Bills, cash management bills, or notes and bonds, by `security_type` and `cash_management_bill_cmb`."""

    if record["security_type"] == "Bill":
        return CASH_MANAGEMENT if record.get("cash_management_bill_cmb") == "Yes" else BILL
    return COUPON


def announcement_url(name: str) -> str:
    return URL.format(year=name[2:6], name=name)


def _business_days_between(start: date, end: date) -> int:
    """Weekdays after `start` up to and including `end` (no holiday table: a count for the evidence, not a rule)."""

    count, day = 0, start
    while day < end:
        day += timedelta(days=1)
        if day.weekday() < 5:
            count += 1
    return count


def summarise(records: Sequence[Mapping[str, object]], stated: Mapping[str, str]) -> dict:
    """Counts by stated time and class, the announcements after the decision, and those with no stated time.

    `stated` maps each `pdf_filenm_announcemt` to `parse_release`'s result. Every record's file must be in it.
    """

    missing = sorted({str(r["pdf_filenm_announcemt"]) for r in records} - set(stated))
    if missing:
        raise ValueError(f"no stated release time for {len(missing)} announcement file(s), first {missing[0]}")
    by_time: Dict[str, Counter] = {}
    after_decision: List[dict] = []
    between: List[dict] = []
    immediate = Counter()
    for record in records:
        name, when = str(record["pdf_filenm_announcemt"]), stated[str(record["pdf_filenm_announcemt"])]
        klass = record_class(record)
        by_time.setdefault(when, Counter())[klass] += 1
        if when == IMMEDIATE:
            immediate[klass] += 1
        if when in (IMMEDIATE, UNREADABLE):
            continue
        row = {
            "file": name,
            "class": klass,
            "stated": when,
            "announcemt_date": record["announcemt_date"],
            "issue_date": record["issue_date"],
            "weekdays_to_settlement": _business_days_between(
                date.fromisoformat(str(record["announcemt_date"])), date.fromisoformat(str(record["issue_date"]))
            ),
        }
        if when > DECISION:
            after_decision.append(row)
        elif when > DECLARED:
            between.append(row)
    rows = {when: dict(sorted(counts.items())) for when, counts in sorted(by_time.items())}
    return {
        "records": len(records),
        "files": len({str(r["pdf_filenm_announcemt"]) for r in records}),
        "by_stated_time_and_class": rows,
        "after_decision_16_00": sorted(after_decision, key=lambda r: r["file"]),
        "after_declared_12_00_to_decision_16_00": sorted(between, key=lambda r: (r["announcemt_date"], r["file"])),
        "unreadable": sum(by_time.get(UNREADABLE, Counter()).values()),
        "for_immediate_release": {
            "total": sum(immediate.values()),
            "by_class": dict(sorted(immediate.items())),
        },
    }


METHOD = (
    "Each pdf_filenm_announcemt of the tracked auctions snapshot (3828 records, 3828 files) was fetched from "
    "https://www.treasurydirect.gov/instit/annceresult/press/preanre/<year>/<file> and read with pdftotext -layout for the line "
    "'Embargoed Until <time>' (parse_release), or 'For Immediate Release' when no time is stated. Classes: bills and cash management "
    "bills by security_type = Bill and cash_management_bill_cmb, notes and bonds otherwise. weekdays_to_settlement counts Monday to Friday "
    "days after announcemt_date up to issue_date, with no holiday table. Where the PDF on file is an amended announcement dated after "
    "announcemt_date (A_20220517_*, A_20230316_*, A_20250415_*), the time read is the amendment's, not the original's."
)


def build_record(records: Sequence[Mapping[str, object]], stated: Mapping[str, str], *, retrieved: str, failed: Mapping[str, str]) -> dict:
    """The committed evidence file: method, the counts and the stated time of every file."""

    return {
        "directive": "#1310",
        "finding": "#1301",
        "status": "evidence. Read from Treasury's own announcement files; no declaration, record or figure reads this file, and "
        "metadata/settlement_announcement_dating.json, metadata/net_settlement.json and metadata/sources_measurement.json are not edited by it.",
        "snapshot": "tests/fixtures/snapshots/funding_inputs/treasury_auctions/20260914T051023Z_722359ea9bc7.json",
        "retrieved": retrieved,
        "method": METHOD,
        "script": "scripts/announcement_release_times_1301.py (fetch needs the network and pdftotext; check and summarise need neither)",
        "declared_instant": f"{DECLARED} America/New_York on announcemt_date (metadata/settlement_announcement_dating.json)",
        "decision_instant": f"{DECISION} America/New_York on the decision day",
        "failed": dict(failed),
        "summary": summarise(records, stated),
        "stated": dict(sorted(stated.items())),
    }


def load_records(path: Path = SNAPSHOT) -> List[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["data"]


def _fetch_text(name: str) -> str:
    request = urllib.request.Request(announcement_url(name), headers={"User-Agent": "repo-market-model release-time check (#1301)"})
    with urllib.request.urlopen(request, timeout=60) as response:
        pdf = response.read()
    done = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, capture_output=True, check=True)
    return done.stdout.decode("utf-8", errors="replace")


def fetch_command(args: argparse.Namespace) -> int:
    records = load_records(Path(args.snapshot))
    names = sorted({str(r["pdf_filenm_announcemt"]) for r in records})

    def one(name: str):
        for attempt in range(3):
            try:
                text = _fetch_text(name)
                return name, parse_release(text), None
            except Exception as error:  # noqa: BLE001 - a failed file is reported, never guessed
                last = f"{type(error).__name__}: {error}"
        return name, UNREADABLE, last

    stated: Dict[str, str] = {}
    failed: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for name, when, error in pool.map(one, names):
            stated[name] = when
            if error:
                failed[name] = error
    result = build_record(records, stated, retrieved=datetime.now().astimezone().date().isoformat() if args.date is None else args.date, failed=failed)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(stated)} files, {len(failed)} failed", file=sys.stderr)
    return 1 if failed else 0


def summarise_command(args: argparse.Namespace) -> int:
    stated = json.loads(Path(args.stated).read_text(encoding="utf-8"))["stated"]
    print(json.dumps(summarise(load_records(Path(args.snapshot)), stated), indent=1))
    return 0


def check_command(args: argparse.Namespace) -> int:
    """Recompute the committed record's summary from its own stated times (no network)."""

    record = json.loads(Path(args.record).read_text(encoding="utf-8"))
    again = summarise(load_records(Path(args.snapshot)), record["stated"])
    if again != record["summary"]:
        print("the record's summary is not the one its stated times give", file=sys.stderr)
        return 1
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch", help="read every announcement PDF (network, pdftotext)")
    fetch.add_argument("--snapshot", default=str(SNAPSHOT))
    fetch.add_argument("--output", required=True)
    fetch.add_argument("--workers", type=int, default=12)
    fetch.add_argument("--date", default=None, help="the retrieval date to record (default: today)")
    fetch.set_defaults(func=fetch_command)
    summary = sub.add_parser("summarise", help="count a fetched record (no network)")
    summary.add_argument("--snapshot", default=str(SNAPSHOT))
    summary.add_argument("--stated", required=True)
    summary.set_defaults(func=summarise_command)
    check = sub.add_parser("check", help="recompute a committed record's summary from its stated times (no network)")
    check.add_argument("--snapshot", default=str(SNAPSHOT))
    check.add_argument("--record", default=str(REPO / "metadata/announcement_release_times_1301.json"))
    check.set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
