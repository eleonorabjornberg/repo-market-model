"""New data sources for the ordinary-day gap, and the measurement columns read from them (#630).

Eleonora's directive of 12 October 2026: assess candidate sources for the days that are not known
risk dates, take dated snapshots of those that pass the due diligence
(`docs/pivot/new-sources-due-diligence.md`), register them as measurement sources, and read them
as of each decision instant. Nothing here joins the published panel or a published declaration.

**The sources**

* `nyfed_pd_financing` -- the New York Fed's Primary Dealer Statistics, the series the held
  `nyfed_fr2004` does not read: repo and reverse repo financing of Treasuries (excluding TIPS) and of
  agency MBS, and fails to deliver and to receive Treasuries. Weekly, in USD billions. The same
  release as the held positions, so the same declared lag.
* `treasury_auction_results` -- the results fields of the Treasury auctions table
  (`tests/fixtures/snapshots/treasury_auctions/`, already tracked): the accepted amount, the dealers'
  and indirect bidders' shares of it, and the cover. Public at the auction close.
* `nyfed_on_rrp_counterparties` -- the number of counterparties in the Desk's regular overnight
  reverse repo operation. The split of the amount by counterparty type (`propositions`) is **not**
  read: the Desk adds it a month later (`tests/test_registry.py`, A45), so it was not public on the
  operation date. A record the Desk rewrote on a later day is not read either.
* `treasury_dts_debt_cash` -- the Daily Treasury Statement's cash issues and redemptions of public
  debt, from the deposits-and-withdrawals table. The statement is public on the next business day.

**Where they are declared.** In `metadata/sources_measurement.json`, not `metadata/sources.json`,
which the final-test pre-registration freezes by its bytes
(`docs/decisions/final-test-preregistration.md`). `measurement_fields.load_registry()` is the two
files together.

**Guards.** `parse_auction_results` refuses, with `LookAheadError`, an auction whose competitive
closing time is later than `AUCTION_LATEST_CLOSE` (the declared 15:00 instant leaves no room for a
later result). `require_unamended` refuses a Desk record written after its operation day, and the
parser leaves that day empty and lists it. `add_columns` refuses a panel past `END`, and every
parser drops a day past it. Everything is read from a snapshot, never from the network.

**Off.** `COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`. A track switches the columns on
for its own run (`scripts/new_sources.py panel`), as for `measurement_fields`. Standard library only,
like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import csv
import io
import json
from bisect import bisect_right
from datetime import date, datetime, time
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlencode

from .data import DailyObservation
from .ingest import (
    SnapshotArtifact,
    _download,
    _is_small_value_exercise,
    _nyfed_operations,
    _save_snapshot,
)
from .splits import LookAheadError

__all__ = [
    "AUCTION_LATEST_CLOSE",
    "COLUMN_FIELDS",
    "DTS_LINE_NAMES",
    "END",
    "PD_SERIES",
    "SOURCES",
    "add_columns",
    "fetch_dts_debt_cash",
    "parse_auction_results",
    "parse_dts_debt_cash",
    "parse_on_rrp_counterparties",
    "parse_pd_export",
    "require_result_public",
    "require_unamended",
]

#: No day after this is read (`docs/decisions/lockbox.md`).
END = date(2025, 12, 31)

SOURCE_PD = "nyfed_pd_financing"
SOURCE_AUCTIONS = "treasury_auction_results"
SOURCE_RRP = "nyfed_on_rrp_counterparties"
SOURCE_DTS = "treasury_dts_debt_cash"
SOURCES = (SOURCE_PD, SOURCE_AUCTIONS, SOURCE_RRP, SOURCE_DTS)

#: Column -> the export's series name (Primary Dealer Statistics, USD millions).
#: `UTSET` is Treasuries excluding TIPS, `FGM` agency MBS; `SORA` is financing by repo, `SIRRA` by
#: reverse repo; `PDFTD` and `PDFTR` are fails to deliver and to receive.
PD_SERIES: Mapping[str, str] = {
    "pd_repo_ust": "PDSORA-UTSETTOT",
    "pd_reverse_repo_ust": "PDSIRRA-UTSETTOT",
    "pd_repo_mbs": "PDSORA-FGMTOT",
    "pd_fails_deliver_ust": "PDFTD-UST",
    "pd_fails_receive_ust": "PDFTR-UST",
}
PD_EXPORT_URL = "https://markets.newyorkfed.org/api/pd/get/all/timeseries.csv"

AUCTION_COLUMNS = ("auc_accepted_bn", "auc_dealer_share", "auc_indirect_share", "auc_cover")
AUCTION_FIELDS = ("total_accepted", "primary_dealer_accepted", "indirect_bidder_accepted", "total_tendered")
#: The declared availability is 15:00 New York time on the auction day. The competitive bids close
#: at 11:30 or earlier (most bills), 13:00 (notes, bonds and some bills) or, twice in the tracked table, 14:30, and the results follow within minutes; a later close
#: would not be public by the declared instant.
AUCTION_LATEST_CLOSE = time(14, 30)

RRP_COLUMN = "rrp_counterparties"

DTS_COLUMNS = ("dts_debt_issues_bn", "dts_debt_net_bn")
DTS_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/"
    "deposits_withdrawals_operating_cash"
)
#: The line names of the two legs. The table spells the table reference two ways over time.
DTS_ISSUE_NAMES = ("Public Debt Cash Issues (Table III-B)", "Public Debt Cash Issues (Table IIIB)")
DTS_REDEMPTION_NAMES = ("Public Debt Cash Redemp. (Table III-B)", "Public Debt Cash Redemp. (Table IIIB)")
DTS_LINE_NAMES = DTS_ISSUE_NAMES + DTS_REDEMPTION_NAMES
DTS_PAGE_SIZE = 10000

#: Every column's source fields, for the as-of rule. **Off**: never part of `contract.FEATURE_FIELDS`.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    **{column: ((SOURCE_PD, series),) for column, series in PD_SERIES.items()},
    "auc_accepted_bn": ((SOURCE_AUCTIONS, "total_accepted"),),
    "auc_dealer_share": ((SOURCE_AUCTIONS, "primary_dealer_accepted"), (SOURCE_AUCTIONS, "total_accepted")),
    "auc_indirect_share": ((SOURCE_AUCTIONS, "indirect_bidder_accepted"), (SOURCE_AUCTIONS, "total_accepted")),
    "auc_cover": ((SOURCE_AUCTIONS, "total_tendered"), (SOURCE_AUCTIONS, "total_accepted")),
    RRP_COLUMN: ((SOURCE_RRP, "participatingCpty"),),
    "dts_debt_issues_bn": ((SOURCE_DTS, "debt_cash_issues"),),
    "dts_debt_net_bn": ((SOURCE_DTS, "debt_cash_issues"), (SOURCE_DTS, "debt_cash_redemptions")),
}
#: Columns placed on a panel day by their own date, against those placed on the last panel day at
#: or before their weekly as-of date.
WEEKLY_COLUMNS = tuple(PD_SERIES)


# -- Primary Dealer Statistics ---------------------------------------------------------------


def parse_pd_export(payload: bytes, end: date = END) -> Dict[str, Dict[date, float]]:
    """`{column: {as_of_date: USD billions}}` for the series of `PD_SERIES`.

    A value of `*` is a figure the New York Fed withheld for confidentiality and is skipped. A day
    after `end` is not read. Raises `ValueError` if the response is not the export's CSV.
    """

    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    needed = {"As Of Date", "Time Series", "Value (millions)"}
    if not reader.fieldnames or not needed.issubset(reader.fieldnames):
        raise ValueError(f"primary dealer export must carry the columns {sorted(needed)}")
    wanted = {series: column for column, series in PD_SERIES.items()}
    out: Dict[str, Dict[date, float]] = {column: {} for column in PD_SERIES}
    for row in reader:
        column = wanted.get(row["Time Series"])
        if column is None:
            continue
        day = date.fromisoformat(row["As Of Date"])
        raw = row["Value (millions)"].strip()
        if day > end or raw == "*":
            continue
        out[column][day] = float(raw.replace(",", "")) / 1000.0
    return out


# -- Treasury auction results ----------------------------------------------------------------


def _closing_time(raw: object) -> time:
    try:
        return datetime.strptime(str(raw).strip(), "%I:%M %p").time()
    except ValueError as exc:
        raise ValueError(f"auction closing time {raw!r} is not 'HH:MM AM/PM'") from exc


def require_result_public(record: Mapping[str, object]) -> None:
    """Raise `LookAheadError` if the auction's results could not be public by the declared instant."""

    closing = _closing_time(record.get("closing_time_comp"))
    if closing > AUCTION_LATEST_CLOSE:
        raise LookAheadError(
            f"auction of {record.get('auction_date')} closes at {closing}, after {AUCTION_LATEST_CLOSE}: "
            "its results are not public by the declared 15:00 instant"
        )


def _number(record: Mapping[str, object], field: str) -> Optional[float]:
    raw = record.get(field)
    if raw is None or str(raw).strip().lower() in ("", "null"):
        return None
    return float(str(raw))


def parse_auction_results(payload: bytes, end: date = END) -> Dict[str, Dict[date, float]]:
    """`{column: {auction_date: value}}`: the auctions of one day summed.

    `auc_accepted_bn` is the total accepted in USD billions; `auc_dealer_share` and
    `auc_indirect_share` are the primary dealers' and indirect bidders' accepted amounts over it;
    `auc_cover` is the total tendered over the total accepted. An auction with no result yet
    (`total_accepted` null) is skipped. A day after `end` is not read.
    """

    parsed = json.loads(payload)
    records = parsed.get("data") if isinstance(parsed, dict) else None
    if not isinstance(records, list):
        raise ValueError("auctions response does not contain a data list")
    sums: Dict[date, Dict[str, float]] = {}
    for record in records:
        accepted = _number(record, "total_accepted")
        if accepted is None or accepted <= 0:
            continue
        day = date.fromisoformat(str(record["auction_date"]))
        if day > end:
            continue
        require_result_public(record)
        values = {field: _number(record, field) for field in AUCTION_FIELDS}
        if any(v is None for v in values.values()):
            continue
        bucket = sums.setdefault(day, {field: 0.0 for field in AUCTION_FIELDS})
        for field, value in values.items():
            bucket[field] += value  # type: ignore[operator]
    out: Dict[str, Dict[date, float]] = {column: {} for column in AUCTION_COLUMNS}
    for day, s in sums.items():
        total = s["total_accepted"]
        out["auc_accepted_bn"][day] = total / 1e9
        out["auc_dealer_share"][day] = s["primary_dealer_accepted"] / total
        out["auc_indirect_share"][day] = s["indirect_bidder_accepted"] / total
        out["auc_cover"][day] = s["total_tendered"] / total
    return out


# -- The Desk's overnight reverse repo operations ---------------------------------------------


def require_unamended(record: Mapping[str, object]) -> None:
    """Raise `LookAheadError` for a record the Desk wrote after its operation day.

    `lastUpdated` is the time the Desk last wrote the record. A record written on a later day may
    say something it did not say at publication, and nothing shows which fields moved.
    """

    operation_day = date.fromisoformat(str(record["operationDate"]))
    written = datetime.fromisoformat(str(record["lastUpdated"]).replace("Z", "+00:00")).date()
    if written > operation_day:
        raise LookAheadError(
            f"operation {record.get('operationId')!r} of {operation_day} was rewritten on {written}"
        )


def parse_on_rrp_counterparties(payload: bytes, end: date = END) -> Dict[str, object]:
    """`{"rrp_counterparties": {operation_date: count}, "amended_days": [dates]}`.

    The count is `participatingCpty` of the day's largest regular reverse repo operation. Repo
    operations and small-value exercises are left out. A day whose record was rewritten later
    (`require_unamended`) has no value and is listed in `amended_days`. The propositions are never read.
    Raises `ValueError` for a reverse repo record with no numeric count.
    """

    counts: Dict[date, float] = {}
    amended: set = set()
    for number, record in enumerate(_nyfed_operations(json.loads(payload)), start=1):
        if not isinstance(record, dict) or record.get("operationType") != "Reverse Repo":
            continue
        if _is_small_value_exercise(record):
            continue
        day = date.fromisoformat(str(record["operationDate"]))
        if day > end:
            continue
        count = record.get("participatingCpty")
        if isinstance(count, bool) or not isinstance(count, (int, float)):
            raise ValueError(
                f"reverse repo operation {record.get('operationId', number)!r} on {day} has no numeric "
                f"participatingCpty ({count!r})"
            )
        try:
            require_unamended(record)
        except LookAheadError:
            amended.add(day)
            continue
        counts[day] = max(counts.get(day, 0.0), float(count))
    for day in amended:
        counts.pop(day, None)
    return {RRP_COLUMN: counts, "amended_days": sorted(amended)}


# -- Daily Treasury Statement: cash issues and redemptions of debt -------------------------------


def fetch_dts_debt_cash(
    output_root: Path,
    start: str,
    end: str,
    downloader: Callable[[str], bytes] = _download,
) -> List[SnapshotArtifact]:
    """One snapshot per line name and calendar year of the deposits-and-withdrawals table (#630).

    Each is one plain GET of Fiscal Data's table, filtered to one line name and the year's dates, and
    saved unmodified. A name a year never used yields an empty list, which is saved: it is the record
    that the line was asked for and absent. A page that does not hold every row is refused.
    """

    start_date, end_date = date.fromisoformat(start), date.fromisoformat(end)
    if start_date > end_date:
        raise ValueError("Daily Treasury Statement start date must not follow end date")
    artifacts: List[SnapshotArtifact] = []
    for year in range(start_date.year, end_date.year + 1):
        window_start, window_end = max(start_date, date(year, 1, 1)), min(end_date, date(year, 12, 31))
        for name in DTS_LINE_NAMES:
            query = urlencode(
                {
                    "fields": "record_date,transaction_type,transaction_catg,transaction_today_amt",
                    "filter": (
                        f"record_date:gte:{window_start.isoformat()},"
                        f"record_date:lte:{window_end.isoformat()},"
                        f"transaction_catg:eq:{name}"
                    ),
                    "sort": "record_date",
                    "page[size]": str(DTS_PAGE_SIZE),
                }
            )
            url = f"{DTS_URL}?{query}"
            payload = downloader(url)
            parse_dts_debt_cash([payload])
            artifacts.append(
                _save_snapshot(source_id=SOURCE_DTS, url=url, payload=payload, output_root=output_root, suffix="json")
            )
    return artifacts


def parse_dts_debt_cash(payloads: Sequence[bytes], end: date = END) -> Dict[str, Dict[date, float]]:
    """`{column: {record_date: USD billions}}` from saved responses.

    `dts_debt_issues_bn` is the day's cash issues of public debt; `dts_debt_net_bn` is issues less
    redemptions, on a day with both legs. A day after `end` is not read. Raises `ValueError` for a
    page that does not hold every row of its query, a non-numeric amount, or two values for one
    leg and day.
    """

    issues: Dict[date, float] = {}
    redemptions: Dict[date, float] = {}
    for payload in payloads:
        parsed = json.loads(payload)
        data = parsed.get("data") if isinstance(parsed, dict) else None
        meta = parsed.get("meta", {}) if isinstance(parsed, dict) else {}
        if not isinstance(data, list):
            raise ValueError("Daily Treasury Statement response does not contain a data list")
        if int(meta.get("total-count", len(data))) > len(data):
            raise ValueError("Daily Treasury Statement page is truncated: it holds fewer rows than the query matched")
        for record in data:
            name = record.get("transaction_catg")
            if name in DTS_ISSUE_NAMES:
                target = issues
            elif name in DTS_REDEMPTION_NAMES:
                target = redemptions
            else:
                continue
            day = date.fromisoformat(str(record["record_date"]))
            if day > end:
                continue
            try:
                amount = float(str(record["transaction_today_amt"])) / 1000.0
            except ValueError as exc:
                raise ValueError(f"{name!r} on {day}: amount is not numeric") from exc
            if day in target:
                raise ValueError(f"two values for {name!r} on {day}")
            target[day] = amount
    net = {day: issues[day] - redemptions[day] for day in issues if day in redemptions}
    return {"dts_debt_issues_bn": issues, "dts_debt_net_bn": net}


# -- Columns on a panel ---------------------------------------------------------------------


def add_columns(
    rows: Sequence[DailyObservation], series: Mapping[str, Mapping[date, float]]
) -> List[DailyObservation]:
    """`rows` with the columns of `series` added; the input is not changed.

    A weekly column (`WEEKLY_COLUMNS`) places each as-of date's value on the last panel day at or
    before it (older, never newer). Any other column is placed on its own day. A day with no value
    is `None`. Raises `LookAheadError` for a panel day after `END`.
    """

    dates = [row.date for row in rows]
    for day in dates:
        if day > END:
            raise LookAheadError(f"panel day {day} is after {END}: not read")
    present = set(dates)
    placed: Dict[str, Dict[date, float]] = {}
    for column, values in series.items():
        target: Dict[date, float] = {}
        if column in WEEKLY_COLUMNS:
            for as_of in sorted(values):
                position = bisect_right(dates, as_of) - 1
                if position >= 0:
                    target[dates[position]] = values[as_of]
        else:
            target = {day: value for day, value in values.items() if day in present}
        placed[column] = target
    out: List[DailyObservation] = []
    for row in rows:
        merged = dict(row.values)
        for column, target in placed.items():
            merged[column] = target.get(row.date)
        out.append(DailyObservation(row.date, merged))
    return out
