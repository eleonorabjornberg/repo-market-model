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

`require_posting_established` is the second (#572): the ruling is drafted, not in force, until the date the
Bank first posted the workbook is established, and a back-filled value is stamped public in real time from
2014 by the ordinary parser. A fit that trains on it is refused unless the posting instant is declared
(`metadata/backfill_posting.json`) and is no later than the start of the fit's training-end day.

`require_series_admitted` is the third (#742): the posting instant above is the workbook's, but the extended
panel also carries series from other sources (bill rates, reserves, the TGA, ON RRP results, auctions) whose
posting is not established. A fit that trains on back-filled rows must name the series it reads, and each must be
listed under `admitted` in `metadata/backfill_posting.json` with its own instant; any other series raises
`LookAheadError` (Eleonora's ruling on #742, 14 October 2026).

Standard library only: the workbook is read with `zipfile` and `xml.etree`.
"""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from xml.etree import ElementTree

from . import contract
from .splits import LookAheadError

__all__ = [
    "BACKFILL_SOURCE_ID",
    "augment_rows",
    "BackfilledDay",
    "load_admitted_series",
    "load_posting_instant",
    "FIRST_PUBLISHED",
    "RATE_NAMES",
    "nyfed_documents",
    "parse_workbook",
    "prefix_length",
    "require_posting_established",
    "require_series_admitted",
    "series_read",
    "unadmitted_columns",
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


def load_posting_instant(path: Path) -> Optional[datetime]:
    """The declared instant the Bank first posted the workbook, or `None` while it is unknown.

    Raises:
        ValueError: the file has no `posting_instant` key, or it is neither null nor an ISO date-time.
    """

    declaration = json.loads(Path(path).read_text(encoding="utf-8"))
    if "posting_instant" not in declaration:
        raise ValueError(f"{path}: the back-fill posting declaration lacks 'posting_instant'")
    value = declaration["posting_instant"]
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{path}: posting_instant must be null or an ISO date-time, got {value!r}") from exc


def require_posting_established(
    folds: Iterable, posting_instant: Optional[datetime], *, where: str
) -> None:
    """Refuse a fit that trains on back-filled values before the workbook's posting instant (#572).

    A fold whose training window begins before `FIRST_PUBLISHED` uses back-filled values. Such a fit is
    refused while `posting_instant` is unknown (`None`), and when it is declared but later than the start of
    the day the fit's training ends (the instant may fall after that day's decision, so the day itself is
    not enough). A fold trained on published days only is not affected.

    Raises:
        LookAheadError: naming `where`, the fold and the dates.
    """

    for fold in folds:
        if fold.train_start >= FIRST_PUBLISHED:
            continue
        start = datetime.combine(fold.train_end, time.min)
        if posting_instant is None or posting_instant > start:
            declared = "is not declared" if posting_instant is None else f"is {posting_instant.isoformat()}"
            raise LookAheadError(
                f"{where}: the fit scored on {fold.scored_date} trains on back-filled values (from "
                f"{fold.train_start}) and ends {fold.train_end}, but the workbook's posting instant {declared}; "
                f"no back-filled value is training history before it is established "
                f"(docs/decisions/information-set.md, metadata/backfill_posting.json)"
            )


def load_admitted_series(path: Path) -> Dict[str, datetime]:
    """The series the back-fill guard admits, each with its own posting instant (#742).

    Raises:
        ValueError: the file has no non-empty `admitted` mapping, or an instant is not an ISO date-time.
    """

    declaration = json.loads(Path(path).read_text(encoding="utf-8"))
    listed = declaration.get("admitted")
    if not isinstance(listed, dict) or not listed:
        raise ValueError(f"{path}: the back-fill posting declaration lacks a non-empty 'admitted' mapping")
    out: Dict[str, datetime] = {}
    for name, value in listed.items():
        try:
            out[name] = datetime.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{path}: admitted[{name!r}] must be an ISO date-time, got {value!r}") from exc
    return out


#: Panel columns the New York Fed's workbook feeds, by the back-fill series each is drawn from. SOFR's volume and
#: percentiles are the same series as its rate (the workbook publishes none of them, so they are blank).
WORKBOOK_SERIES = {"sofr": "sofr", "sofr_volume": "sofr", "sofr_p25": "sofr", "sofr_p75": "sofr",
                   "tgcr": "tgcr", "bgcr": "bgcr"}

#: Features that are not a back-fill series: the calendar, and IORB, an administered rate that defines the
#: spread (whether it needs its own `admitted` entry is a marked question on #742's pull request, not settled here).
NOT_A_SERIES = contract.CALENDAR_FEATURES | {"iorb"}


def series_read(features: Iterable[str]) -> Tuple[str, ...]:
    """The back-fill series that a model reading `features` draws on, from the feature declarations (#832).

    Derived and composed features (`spread_bps`, `reserves_when_depleted`) are followed to the panel columns
    they are computed from. A workbook column maps to its series; the calendar and IORB are no series; any other
    column stands for itself, so a column this module does not know is never admitted.
    """

    pending, seen, out = list(features), set(), []
    while pending:
        name = str(pending.pop(0))
        if name in seen:
            continue
        seen.add(name)
        if name in contract.DERIVED_FEATURES:
            pending.extend(contract.DERIVED_FEATURES[name])
        elif name in contract.COMPOSED_FEATURES:
            pending.extend(contract.COMPOSED_FEATURES[name])
        elif name not in NOT_A_SERIES:
            out.append(WORKBOOK_SERIES.get(name, name))
    return tuple(sorted(dict.fromkeys(out)))


def unadmitted_columns(columns: Iterable[str], admitted: Mapping[str, datetime]) -> List[str]:
    """The panel columns that carry a series `admitted` does not list: blank on a back-filled row (#742, #832)."""

    return [name for name in columns if any(series not in admitted for series in series_read([name]))]


def require_series_admitted(
    folds: Iterable, reads: Sequence[str], admitted: Mapping[str, datetime], *, where: str
) -> None:
    """Refuse a fit that trains on back-filled values of a series that is not admitted (#742).

    `reads` names every series the fit reads from the back-filled rows. A fold whose training window begins
    before `FIRST_PUBLISHED` uses them. Each must be in `admitted`, and its own instant must be no later than
    the start of the day the fit's training ends. A fold trained on published days only is not affected.

    Raises:
        ValueError: a back-filled fit names no series (what it reads is not declared).
        LookAheadError: a series is not admitted, or is read before its own instant; naming `where`, the
            series and the fold.
    """

    for fold in folds:
        if fold.train_start >= FIRST_PUBLISHED:
            continue
        if not reads:
            raise ValueError(f"{where}: a fit on back-filled values must name the series it reads")
        start = datetime.combine(fold.train_end, time.min)
        for name in reads:
            instant = admitted.get(name)
            if instant is None:
                raise LookAheadError(
                    f"{where}: the fit scored on {fold.scored_date} trains on back-filled values of {name!r} "
                    f"(from {fold.train_start}), which is not admitted; only {sorted(admitted)} are "
                    f"(metadata/backfill_posting.json, #742)"
                )
            if instant > start:
                raise LookAheadError(
                    f"{where}: the fit scored on {fold.scored_date} trains on back-filled values of {name!r} "
                    f"and ends {fold.train_end}, but its posting instant is {instant.isoformat()} "
                    f"(metadata/backfill_posting.json, #742)"
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
