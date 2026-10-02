"""Build the dated IORB/IOER change table from fetched Federal Reserve pages.

    python3 scripts/build_iorb_table.py tests/fixtures/snapshots/fed-iorb-announcements
    python3 scripts/build_iorb_table.py tests/fixtures/snapshots/fed-iorb-announcements --check

The snapshot directory holds `pages/`, the Board's press releases as fetched,
one plain GET each, from

    https://www.federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm   (FOMC statement)
    https://www.federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa1.htm  (implementation note)

For every implementation note the script reads one sentence, "The Board of
Governors ... voted ... to <action> the interest rate paid on <reserve
balances> <to|at> <rate> percent, effective <date>", and from the statement of
the same day the "For release at <h:mm> <a.m.|p.m.> <EDT|EST>" line. A page
without exactly one of each is refused: the table is read from the pages, never
typed in.

It writes `iorb_changes.csv`, one row per note in announcement order, and
`iorb_changes.csv.manifest.json`: the table's SHA-256, and each page's URL,
SHA-256 and retrieval instant. `--check` rebuilds the table in memory and exits
1 if the tracked CSV differs, so the table is a command over tracked bytes.

`kind` is `anchor` for the first row (the rate in force when the published
panel opens on 2018-04-03, kept so the first change has a previous rate),
`change` when the rate moved, and `unchanged` when a note restated the rate
(2021-07-28: IORB replaced IOER at the same 0.15 percent). Standard library
only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

BASE_URL = "https://www.federalreserve.gov/newsevents/pressreleases/"
TABLE_NAME = "iorb_changes.csv"
MANIFEST_NAME = TABLE_NAME + ".manifest.json"
COLUMNS = (
    "announcement_date",
    "announcement_time",
    "timezone",
    "effective_date",
    "field",
    "action",
    "rate_percent",
    "change_bps",
    "kind",
    "implementation_note_url",
    "statement_url",
)

_NOTE = re.compile(
    r"voted (?:unanimously )?to (\w+) the interest rate paid on "
    r"((?:required and excess )?reserve balances) (?:to|at) (\d+(?:\.\d+)?) percent,? "
    r"effective (\w+ \d{1,2}, \d{4})"
)
_RELEASE = re.compile(r"For release at (\d{1,2}):(\d{2}) ([ap])\.m\. (EDT|EST)")
_PAGE = re.compile(r"monetary(\d{8})a1\.htm")


def page_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def _one(pattern: re.Pattern, text: str, path: Path) -> tuple:
    found = pattern.findall(text)
    if len(found) != 1:
        raise SystemExit(f"{path}: expected one match of {pattern.pattern!r}, found {len(found)}")
    return found[0]


def read_rows(pages: Path) -> list[dict]:
    notes = sorted(pages.glob("monetary*a1.htm"))
    if not notes:
        raise SystemExit(f"{pages}: no implementation notes")
    rows = []
    previous_bps = None
    for note in notes:
        stamp = _PAGE.fullmatch(note.name).group(1)
        announced = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
        statement = note.with_name(f"monetary{stamp}a.htm")
        if not statement.exists():
            raise SystemExit(f"{statement}: the statement for {note.name} was not fetched")
        action, balances, rate, effective = _one(_NOTE, page_text(note), note)
        hour, minute, half, zone = _one(_RELEASE, page_text(statement), statement)
        hour = int(hour) % 12 + (12 if half == "p" else 0)
        effective_date = datetime.strptime(effective, "%B %d, %Y").date()
        rate_bps = round(float(rate) * 100)
        if previous_bps is None:
            kind, change = "anchor", ""
        else:
            delta = rate_bps - previous_bps
            kind, change = ("change" if delta else "unchanged"), str(delta)
        previous_bps = rate_bps
        rows.append(
            {
                "announcement_date": announced.isoformat(),
                "announcement_time": f"{hour:02d}:{minute}",
                "timezone": "America/New_York",
                "effective_date": effective_date.isoformat(),
                "field": "IORB" if balances == "reserve balances" else "IOER",
                "action": action,
                "rate_percent": f"{rate_bps / 100:.2f}",
                "change_bps": change,
                "kind": kind,
                "implementation_note_url": BASE_URL + note.name,
                "statement_url": BASE_URL + statement.name,
                "_zone": zone,
            }
        )
    return rows


def render(rows: list[dict]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--check", action="store_true", help="exit 1 if the tracked table differs")
    args = parser.parse_args(argv)
    pages = args.snapshot / "pages"
    rows = read_rows(pages)
    table = render(rows)
    target = args.snapshot / TABLE_NAME
    if args.check:
        if not target.exists() or target.read_bytes() != table:
            print(f"{target} does not match the pages it is built from", file=sys.stderr)
            return 1
        manifest = json.loads((args.snapshot / MANIFEST_NAME).read_text(encoding="utf-8"))
        if manifest["sha256"] != sha256(table):
            print(f"{MANIFEST_NAME}: sha256 does not match {TABLE_NAME}", file=sys.stderr)
            return 1
        for entry in manifest["pages"]:
            data = (args.snapshot / entry["path"]).read_bytes()
            if sha256(data) != entry["sha256"]:
                print(f"{entry['path']}: sha256 does not match the manifest", file=sys.stderr)
                return 1
        return 0
    target.write_bytes(table)
    entries = []
    for path in sorted(pages.glob("monetary*.htm")):
        data = path.read_bytes()
        retrieved = datetime.utcfromtimestamp(path.stat().st_mtime).replace(microsecond=0)
        entries.append(
            {
                "path": f"pages/{path.name}",
                "url": BASE_URL + path.name,
                "sha256": sha256(data),
                "byte_count": len(data),
                "retrieved_at": retrieved.isoformat() + "Z",
            }
        )
    manifest = {
        "source_id": "fed_iorb_announcements",
        "path": f"{args.snapshot.as_posix()}/{TABLE_NAME}",
        "sha256": sha256(table),
        "byte_count": len(table),
        "built_by": "scripts/build_iorb_table.py",
        "note": (
            "Every row is read from the tracked pages by scripts/build_iorb_table.py; "
            "`--check` rebuilds it. announcement_time is the FOMC statement's "
            "'For release at' time, Eastern (EDT or EST as the page states). "
            "retrieved_at is each page's download time, one plain GET per page."
        ),
        "pages": entries,
    }
    (args.snapshot / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(
            row["announcement_date"], row["announcement_time"], row["_zone"],
            row["effective_date"], row["field"], row["rate_percent"], row["change_bps"], row["kind"],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
