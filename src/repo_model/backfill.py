"""Back-filled repo-rate history, as training history only (#430).

The New York Fed's reference-rate API begins on 2018-04-02. For the months before it, the Bank
published a workbook of indicative values for the same three rates, computed after the fact on
the same method: the Treasury repo rates SOFR, TGCR and BGCR (volume-weighted medians, in whole
basis points) and their volumes, from 2014-08-22 to 2018-03-30. It carries no percentiles.

Eleonora ruled on 8 October 2026 (#374, #430) that this back-fill may be used as **training
history**. `docs/decisions/information-set.md` records the ruling as drafted by the pull request that
closes #430. The rule is narrow:

* a back-filled row is dated before `FIRST_PUBLISHED` (2018-04-03), the first day the API serves;
* it may sit in a fold's training frame, and nowhere else;
* it is never the as-of input of a scored decision, and no scored day is a back-filled day.

`require_training_only` is the guard. It reads a scored backtest report's own folds and raises
`LookAheadError` for any fold whose scored day or feature row is not a published day.

Standard library only: the workbook is read with `zipfile` and `xml.etree`.
"""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple
from xml.etree import ElementTree

from .splits import LookAheadError

__all__ = [
    "BACKFILL_SOURCE_ID",
    "augment_rows",
    "BackfilledDay",
    "FIRST_PUBLISHED",
    "RATE_NAMES",
    "nyfed_documents",
    "parse_workbook",
    "prefix_length",
    "require_training_only",
]

BACKFILL_SOURCE_ID = "nyfed_repo_backfill"

#: The first day the New York Fed's reference-rate API serves. Every value before it is back-filled.
FIRST_PUBLISHED = date(2018, 4, 3)

#: The workbook's three series, in the order of its columns.
RATE_NAMES = ("tgcr", "bgcr", "sofr")

_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_EXCEL_EPOCH = date(1899, 12, 30)


@dataclass(frozen=True)
class BackfilledDay:
    """One back-filled day: each rate in percent, each volume in USD billions."""

    day: date
    rates: Mapping[str, float]
    volumes: Mapping[str, float]


def _cells(sheet: ElementTree.Element, strings: Sequence[str]) -> List[Dict[str, str]]:
    rows = []
    for row in sheet.iter(f"{_MAIN}row"):
        cells = {}
        for cell in row.findall(f"{_MAIN}c"):
            value = cell.find(f"{_MAIN}v")
            if value is None or value.text is None:
                continue
            column = "".join(ch for ch in cell.get("r", "") if ch.isalpha())
            cells[column] = strings[int(value.text)] if cell.get("t") == "s" else value.text
        rows.append(cells)
    return rows


def _series(rows: Sequence[Mapping[str, str]], where: str) -> Dict[date, Dict[str, float]]:
    """The dated rows under the header `Date` of one sheet, columns B to D as the three series."""

    header = next((i for i, row in enumerate(rows) if row.get("A") == "Date"), None)
    if header is None:
        raise ValueError(f"{where}: no 'Date' header row")
    out: Dict[date, Dict[str, float]] = {}
    for row in rows[header + 1:]:
        if "A" not in row:
            continue
        try:
            day = _EXCEL_EPOCH + timedelta(days=int(float(row["A"])))
            values = {name: float(row[column]) for name, column in zip(RATE_NAMES, "BCD")}
        except (KeyError, ValueError) as exc:
            raise ValueError(f"{where}: a dated row is missing a series or is not numeric: {row}") from exc
        if day in out:
            raise ValueError(f"{where}: {day} appears twice")
        out[day] = values
    return out


def parse_workbook(payload: bytes) -> List[BackfilledDay]:
    """The back-filled days of the New York Fed's workbook, oldest first.

    Sheet `Volumes` is USD billions; sheet `VWM Rates` is whole basis points, read as percent.

    Raises:
        ValueError: if a sheet is missing, a row lacks a series, the two sheets disagree on the
            dates, or a day falls on or after `FIRST_PUBLISHED`.
    """

    with zipfile.ZipFile(io.BytesIO(payload)) as book:
        workbook = ElementTree.fromstring(book.read("xl/workbook.xml"))
        relations = ElementTree.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        targets = {rel.get("Id"): rel.get("Target") for rel in relations}
        ids = {
            sheet.get("name"): sheet.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            )
            for sheet in workbook.iter(f"{_MAIN}sheet")
        }
        strings = [
            "".join(t.text or "" for t in item.iter(f"{_MAIN}t"))
            for item in ElementTree.fromstring(book.read("xl/sharedStrings.xml")).findall(f"{_MAIN}si")
        ]
        sheets = {}
        for name in ("Volumes", "VWM Rates"):
            if name not in ids:
                raise ValueError(f"the workbook has no sheet {name!r}; it has {sorted(ids)}")
            sheets[name] = _series(
                _cells(ElementTree.fromstring(book.read("xl/" + targets[ids[name]])), strings), name
            )
    volumes, rates = sheets["Volumes"], sheets["VWM Rates"]
    if set(volumes) != set(rates):
        raise ValueError("the Volumes and VWM Rates sheets do not carry the same dates")
    days = []
    for day in sorted(rates):
        if day >= FIRST_PUBLISHED:
            raise ValueError(f"{day} is not back-filled: the API serves from {FIRST_PUBLISHED}")
        days.append(
            BackfilledDay(
                day,
                {name: rates[day][name] / 100.0 for name in RATE_NAMES},
                dict(volumes[day]),
            )
        )
    if not days:
        raise ValueError("the workbook carries no dated rows")
    return days


def nyfed_documents(days: Iterable[BackfilledDay]) -> Dict[Tuple[str, str], bytes]:
    """The back-fill in the shape of the API's `refRates` responses, one document per rate and kind.

    Key `(rate name, "rate" | "volume")`. The standard parser (`ingest`) reads these as it reads
    the API's own response, with no percentile cells, which a record does not carry.
    """

    days = list(days)
    out = {}
    for name in RATE_NAMES:
        for kind, field, source in (
            ("rate", "percentRate", "rates"),
            ("volume", "volumeInBillions", "volumes"),
        ):
            records = [
                {
                    "effectiveDate": day.day.isoformat(),
                    "type": name.upper(),
                    field: getattr(day, source)[name],
                    "revisionIndicator": "",
                }
                for day in days
            ]
            out[(name, kind)] = (json.dumps({"refRates": records}, sort_keys=True) + "\n").encode("utf-8")
    return out


def prefix_length(dates: Sequence[date]) -> int:
    """How many leading rows of an extended panel are back-filled: those before `FIRST_PUBLISHED`.

    Raises:
        ValueError: if the dates are not ascending, or a back-filled date follows a published one.
    """

    if any(later <= earlier for earlier, later in zip(dates, dates[1:])):
        raise ValueError("the panel's dates are not strictly ascending")
    return sum(1 for day in dates if day < FIRST_PUBLISHED)


def require_training_only(folds: Iterable, *, where: str) -> None:
    """Refuse a backtest in which a back-filled day is scored or is a scored decision's input.

    `folds` are a report's `ScoredFold`s. Each fold's scored day and its feature date (the anchor
    of the as-of observation the forecast was conditioned on) must be published days. A fold's
    training window may begin earlier: that is the use the ruling allows.

    Raises:
        LookAheadError: naming `where`, the fold and the date.
    """

    for fold in folds:
        for label, day in (("scored day", fold.scored_date), ("feature date", fold.feature_date)):
            if day < FIRST_PUBLISHED:
                raise LookAheadError(
                    f"{where}: the {label} {day} of the fold scored on {fold.scored_date} is a "
                    f"back-filled day (before {FIRST_PUBLISHED}); back-filled values are training "
                    f"history only (docs/decisions/information-set.md)"
                )


def augment_rows(
    extended: Sequence[Mapping[str, str]], augmented: Sequence[Mapping[str, str]]
) -> List[Dict[str, str]]:
    """The extended panel's rows with the measurement columns of the published days joined on (#484).

    `extended` is the extended scratch panel (`date` and its columns, as CSV cells); `augmented` is the
    published days' panel with the measurement columns added. Back-filled rows (before
    `FIRST_PUBLISHED`) carry a blank cell in every column `extended` lacks: the sources of those
    columns do not reach back, so a model that reads one trains no pair on such a row. Published rows
    are the augmented panel's.

    Raises:
        ValueError: if the published days differ, or a column both carry differs on a published day.
    """

    first = FIRST_PUBLISHED.isoformat()
    published = [row for row in extended if row["date"] >= first]
    if [row["date"] for row in published] != [row["date"] for row in augmented]:
        raise ValueError("the extended panel's published days are not the augmented panel's days")
    extra = [name for name in augmented[0] if name not in extended[0]] if augmented else []
    for mine, theirs in zip(published, augmented):
        for name in mine:
            a, b = mine[name], theirs.get(name, "")
            if a == b:
                continue
            same = bool(a) and bool(b) and abs(float(a) - float(b)) <= 1e-9
            if not same:
                raise ValueError(f"{mine['date']} {name}: extended {a!r} != augmented {b!r}")
    out: List[Dict[str, str]] = []
    for row in extended:
        if row["date"] < first:
            out.append({**row, **{name: "" for name in extra}})
    out.extend(dict(row) for row in augmented)
    return out
