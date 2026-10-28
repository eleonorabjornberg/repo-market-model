"""Build the SIFMA agency MBS class settlement-date table from the Wayback captures (#1276; H5 step 3).

    python3 scripts/build_sifma_table_1276.py
    python3 scripts/build_sifma_table_1276.py --check

The inputs are the tracked captures in `data/sifma-wayback-1276/` (fetched on the Mac by `scripts/sifma_wayback_fetch_1276.py`, listed with their
capture timestamps and SHA-256 in that directory's `manifest.json`). Three of them hold settlement dates, and the table is read from them and from
nothing else; no date is typed in:

* the workbook `TBA_Market_Governance-MBS_Notification_Settlement_Dates_.xlsx` captured on 2025-07-24 (sheets `2017-2021`, with each date as a weekday name
  and a day of the month under a month header; `2022-2023` and `2024 onward readable format`, with dates as spreadsheet serials);
* the page capture of 2025-01-19 (the table of the 2025 dates);
* the page capture of 2026-03-06 (the table of the 2026 and 2027 dates).

It writes `data/sifma-mbs-settlement/settlement_dates.csv`, one row per (class, settlement date) from 2018-01-01 on, and its
`settlement_dates.csv.manifest.json` (the table's SHA-256 and each input's path and SHA-256). Every date read from a weekday-and-day cell is checked
against its weekday, and each month must carry exactly one date per class: a source that fails either is refused, not repaired. `--check` rebuilds the
table in memory and exits 1 if the tracked CSV differs. Whether a date was public at a given instant is not decided here: that is the declaration
`metadata/sifma_mbs_1276.json`, read by `repo_model.sifma_mbs`. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import html
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
CAPTURES = REPO / "data" / "sifma-wayback-1276"
OUT = REPO / "data" / "sifma-mbs-settlement"
TABLE = OUT / "settlement_dates.csv"
MANIFEST = OUT / "settlement_dates.csv.manifest.json"
CLASSES = ("A", "B", "C", "D")
FIRST_YEAR = 2018
COLUMNS = ("settlement_date", "class", "source", "reference")

WORKBOOK = "20250724121315-9d247468-TBA_Market_Governance-MBS_Notification_Settlement_Dates_.xlsx"
PAGE_2025 = "20250119110844-5c9f2523-mbs-notification-and-settlement-dates"
PAGE_2026 = "20260306152332-5c9f2523-mbs-notification-and-settlement-dates"
SHEETS = {"2017-2021": "weekday", "2022-2023": "serial", "2024 onward readable format": "long"}

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_RELNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_WEEKDAY = re.compile(r"^\s*([A-Za-z]+)\s+(\d{1,2})\s*$")
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def serial_date(value: float) -> date:
    """A spreadsheet serial (the 1900 date system) as a date."""

    return date(1899, 12, 30) + timedelta(days=int(float(value)))


def read_capture(name: str) -> bytes:
    raw = (CAPTURES / name).read_bytes()
    return gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw


# -- the workbook -------------------------------------------------------------------------------------------------------------


def sheets(book: bytes) -> Dict[str, List[Dict[str, object]]]:
    """Every sheet of the workbook as a list of rows, each a dict from column letter to a string or a float."""

    z = zipfile.ZipFile(io.BytesIO(book))
    strings = [
        "".join(t.text or "" for t in si.iter(_NS + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml"))
    ]
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    out: Dict[str, List[Dict[str, object]]] = {}
    for sheet in ET.fromstring(z.read("xl/workbook.xml")).find(_NS + "sheets"):
        target = rels[sheet.get(_RELNS + "id")]
        rows: List[Dict[str, object]] = []
        for row in ET.fromstring(z.read("xl/" + target)).iter(_NS + "row"):
            cells: Dict[str, object] = {}
            for cell in row:
                v = cell.find(_NS + "v")
                if v is None:
                    continue
                letter = re.match(r"[A-Z]+", cell.get("r")).group(0)
                cells[letter] = strings[int(v.text)] if cell.get("t") == "s" else float(v.text)
            if cells:
                rows.append(cells)
        out[sheet.get("name")] = rows
    return out


def _weekday_cell(text: str, month_year: Tuple[int, int], where: str) -> date:
    m = _WEEKDAY.match(text)
    if not m:
        raise SystemExit(f"{where}: {text!r} is not a weekday and a day of the month")
    day = date(month_year[0], month_year[1], int(m.group(2)))
    # the first three letters: the workbook has one misspelt name ('Thurday 11', 2021-03-11), whose day and abbreviation agree
    if day.strftime("%a").lower() != m.group(1)[:3].lower():
        raise SystemExit(f"{where}: {text!r} is not a {day.strftime('%A')} ({day})")
    return day


def blocks_sheet(rows: Sequence[Dict[str, object]], style: str, name: str) -> List[Tuple[date, str, date]]:
    """`(settlement date, class, month header)` of a `weekday` or `serial` sheet: a header row with a serial in column A, a `Notification Date` label and
    its values, a `Settlement Date` label and its values."""

    found: List[Tuple[date, str, date]] = []
    header = None
    label = None
    for i, row in enumerate(rows):
        a = row.get("A")
        if isinstance(a, float) and set(row) == {"A"}:
            header, label = serial_date(a), None
            continue
        if isinstance(a, str) and a.strip() in ("Notification Date", "Settlement Date"):
            label = a.strip()
            continue
        if header is None or label is None:
            continue
        if label == "Settlement Date":
            where = f"{name} row {i + 1}"
            for letter, klass in zip("ABCD", CLASSES):
                cell = row.get(letter)
                if cell is None:
                    raise SystemExit(f"{where}: no class {klass} settlement date")
                day = serial_date(cell) if isinstance(cell, float) else _weekday_cell(cell, (header.year, header.month), where)
                found.append((day, klass, header))
        label = None
    return found


def long_sheet(rows: Sequence[Dict[str, object]], name: str) -> List[Tuple[date, str, date]]:
    """`(settlement date, class, month)` of the `2024 onward readable format` sheet: `Jan2024`, `Settlement`, then four serials."""

    found = []
    for i, row in enumerate(rows):
        month, kind = row.get("A"), row.get("B")
        if kind != "Settlement":
            continue
        m = re.match(r"^([A-Z][a-z]{2})(\d{4})$", str(month))
        if not m:
            raise SystemExit(f"{name} row {i + 1}: {month!r} is not a month like Jan2024")
        first = date(int(m.group(2)), _MONTHS.index(m.group(1)) + 1, 1)
        for letter, klass in zip("CDEF", CLASSES):
            found.append((serial_date(row[letter]), klass, first))
    return found


# -- the page tables ----------------------------------------------------------------------------------------------------------


def page_table(page: bytes, name: str) -> List[Tuple[date, str, date]]:
    """`(settlement date, class, month)` from the `Settlement` rows of the first table of a page capture."""

    text = page.decode("utf-8")
    start = text.find("<table")
    end = text.find("</table>", start)
    if start < 0 or end < 0:
        raise SystemExit(f"{name}: no table")
    found = []
    for row in re.findall(r"(?s)<tr.*?</tr>", text[start:end]):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"(?s)<t[dh].*?</t[dh]>", row)]
        if len(cells) != 6 or cells[1] != "Settlement":
            continue
        month = re.match(r"^([A-Z][a-z]{2})-(\d{2}|\d{4})$", cells[0])
        if not month:
            raise SystemExit(f"{name}: {cells[0]!r} is not a month like Jan-25")
        year = int(month.group(2)) + (2000 if len(month.group(2)) == 2 else 0)
        for text_date, klass in zip(cells[2:], CLASSES):
            m, d, y = (int(x) for x in text_date.split("/"))
            found.append((date(y, m, d), klass, date(year, _MONTHS.index(month.group(1)) + 1, 1)))
    return found


# -- the table ----------------------------------------------------------------------------------------------------------------


def rows() -> List[Tuple[str, str, str, str]]:
    """The rows of the table: `(settlement_date, class, source, reference)`, sorted, from 2018-01-01. Each calendar month from 2018-01 to the last
    month of the 2026-2027 table must carry exactly one settlement date for each class, from exactly one source."""

    book = sheets(read_capture(WORKBOOK))
    if sorted(book) != sorted(["KEY", *SHEETS]):
        raise SystemExit(f"unexpected sheets {sorted(book)}")
    found: List[Tuple[date, str, str, str]] = []
    for name, style in SHEETS.items():
        got = long_sheet(book[name], name) if style == "long" else blocks_sheet(book[name], style, name)
        found += [(d, k, WORKBOOK, f"sheet {name}") for d, k, _ in got]
    found += [(d, k, PAGE_2025, "table, Settlement rows") for d, k, _ in page_table(read_capture(PAGE_2025), PAGE_2025)]
    found += [(d, k, PAGE_2026, "table, Settlement rows") for d, k, _ in page_table(read_capture(PAGE_2026), PAGE_2026)]
    kept = sorted((d, k, s, r) for d, k, s, r in found if d.year >= FIRST_YEAR)
    seen: Dict[Tuple[date, str], str] = {}
    for d, k, s, _r in kept:
        if (d, k) in seen:
            raise SystemExit(f"{d} class {k} is in two places: {seen[(d, k)]} and {s}")
        seen[(d, k)] = s
    months: Dict[Tuple[int, int, str], int] = {}
    for d, k, _s, _r in kept:
        months[(d.year, d.month, k)] = months.get((d.year, d.month, k), 0) + 1
    first, last = min(months)[:2], max(months)[:2]
    year, month = first
    while (year, month) <= last:
        for k in CLASSES:
            n = months.get((year, month, k), 0)
            # a class settles once in each calendar month
            if n != 1:
                raise SystemExit(f"{year}-{month:02d} class {k}: {n} settlement dates, expected one")
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return [(d.isoformat(), k, s, r) for d, k, s, r in kept]


def render(table: Sequence[Tuple[str, str, str, str]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(COLUMNS)
    writer.writerows(table)
    return buffer.getvalue().encode("utf-8")


def manifest(data: bytes) -> bytes:
    captured = {e["file"]: e for e in json.loads((CAPTURES / "manifest.json").read_text(encoding="utf-8"))}
    inputs = []
    for name in (WORKBOOK, PAGE_2025, PAGE_2026):
        entry = captured[name]
        if sha256((CAPTURES / name).read_bytes()) != entry["sha256"]:
            raise SystemExit(f"{name}: the bytes differ from data/sifma-wayback-1276/manifest.json")
        inputs.append({"path": f"data/sifma-wayback-1276/{name}", "url": entry["url"], "capture_timestamp": entry["capture_timestamp"],
                       "sha256": entry["sha256"], "byte_count": entry["bytes"]})
    body = {
        "source": "SIFMA, agency MBS class settlement dates (classes A to D), from the Internet Archive's captures",
        "path": "data/sifma-mbs-settlement/settlement_dates.csv",
        "sha256": sha256(data),
        "byte_count": len(data),
        "built_by": "scripts/build_sifma_table_1276.py",
        "note": "Every row is read from the three captures below by the script; `--check` rebuilds it. Whether a date was public at an instant is not in "
                "this table: it is the declaration metadata/sifma_mbs_1276.json. The workbook is the 2025 capture of the file as SIFMA then served it, "
                "which carries SIFMA's later corrections (its own notes of 3/11/2021, 7/15/21, 3/24/2022 and 10/12/2022): the dates of the earlier years "
                "are those of the corrected file, not necessarily as first posted.",
        "inputs": inputs,
    }
    return (json.dumps(body, indent=2) + "\n").encode("utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="rebuild in memory and exit 1 if the tracked table or manifest differs")
    args = parser.parse_args(argv)
    data = render(rows())
    meta = manifest(data)
    if args.check:
        if not TABLE.exists() or TABLE.read_bytes() != data or not MANIFEST.exists() or MANIFEST.read_bytes() != meta:
            print("the tracked SIFMA settlement table or its manifest differs from a rebuild", file=sys.stderr)
            return 1
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    TABLE.write_bytes(data)
    MANIFEST.write_bytes(meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
