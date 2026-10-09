"""Net Treasury cash settlement, read as announced (#426, track N of #374).

The panel carries gross settlement sizes (`treasury_settlement` and its bill and
coupon legs). What drains cash on a settlement day is new money: the securities
settling less the securities maturing. `metadata/net_settlement.json` declares how
it is built from Fiscal Data auction records, each figure read at its announcement:

* the **offering** (`offering_amt`), the announced public offering;
* the **maturing amount** (`est_pub_held_mat_by_type_amt`), the announced estimate of
  the publicly held securities of that type maturing on the settlement date, one
  figure for every auction of a security type settling that day;
* the **SOMA add-on** (`soma_accepted`), an auction result. The Federal Reserve rolls
  its maturing holdings into add-ons the publicly held estimate excludes, so the
  SOMA leg cancels and is not in the net. It is carried and reconciled, not read.

Three columns, in USD billions, on the row of day `t`, each public at the declared
announcement instant on `t` (12:00 New York) and so read by the 16:00 decision of
`t`:

* `net_settlement`: the net of the settlements dated `t`;
* `net_settlement_bills`: the same for the bill types;
* `net_settlement_due_5d`: the net of the settlements dated on the five business
  days after `t`, whatever was announced for them by that instant.

An auction enters a column only when its `announcemt_date` is on or before `t`. A
day partly announced reads low, which is what was known. `check_known_columns` is the
guard: a column that counts an auction announced after the instant raises
`LookAheadError`, and one that leaves out an announced auction raises
`StaleReadError`.

Off in every published declaration: no published panel, declaration or record reads
these columns (`COLUMN_FIELDS` is not part of `contract.FEATURE_FIELDS`).

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .asof import StaleReadError
from .contract import TREASURY_BILL_SECURITY_TYPES, TREASURY_COUPON_SECURITY_TYPES
from .data import DailyObservation, next_business_day
from .splits import LookAheadError

__all__ = [
    "Auction",
    "COLUMNS",
    "COLUMN_FIELDS",
    "WINDOW_DAYS",
    "auction_records",
    "check_known_columns",
    "gross_by_day",
    "known_auctions",
    "load_declaration",
    "load_snapshot",
    "net_for_day",
    "with_net_settlement",
]

#: The panel columns, in the declaration's order.
COLUMNS = ("net_settlement", "net_settlement_bills", "net_settlement_due_5d")
#: The source the as-of rule reads them through (`metadata/sources_measurement.json`).
SOURCE_ID = "treasury_auction_net_settlement"
#: Every column's source field, for the as-of rule. **Off**: a track switches them on.
COLUMN_FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {name: ((SOURCE_ID, name),) for name in COLUMNS}
#: The business days after a row's day that `net_settlement_due_5d` covers.
WINDOW_DAYS = 5
#: Fiscal Data's token for a field it does not have yet.
WITHHELD = "null"
#: How far two sums of the same amounts may differ by summation order alone.
TOLERANCE = 1e-9

_REQUIRED = {
    "source", "snapshot", "inputs", "columns", "announcement_time", "result_time", "timezone",
    "announcement_date_field", "result_date_field", "rule", "evidence", "thresholds_bp", "scoring",
}


class Auction(NamedTuple):
    """One auction: what settles, how much, what matures with it, and when each became public.

    `maturing` is `None` when the record carries no figure. `soma` and `result_at`
    are `None` for an auction not held at retrieval.
    """

    settles: date
    kind: str
    is_bill: bool
    offering: float
    maturing: Optional[float]
    soma: Optional[float]
    announced_at: datetime
    result_at: Optional[datetime]


def load_declaration(path: Path) -> dict:
    """The declaration, checked for the keys this module reads.

    Raises:
        ValueError: a key is missing, the columns are not this module's, or an
            instant is not an HH:MM time.
    """

    declaration = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = sorted(_REQUIRED - set(declaration))
    if missing:
        raise ValueError(f"{path}: the net settlement declaration lacks {missing}")
    if tuple(declaration["columns"]) != COLUMNS:
        raise ValueError(f"{path}: columns must be {list(COLUMNS)}, got {list(declaration['columns'])}")
    time.fromisoformat(str(declaration["announcement_time"]))
    time.fromisoformat(str(declaration["result_time"]))
    return declaration


def _billions(text: object) -> Optional[float]:
    value = str(text)
    return None if value == WITHHELD else float(value.replace(",", "")) / 1_000_000_000


def auction_records(
    records: Sequence[Mapping[str, object]], declaration: Mapping[str, object]
) -> Tuple[Auction, ...]:
    """Each Fiscal Data auction record as an `Auction`, in record order.

    Raises:
        ValueError: a record lacks a field read here, has a security type in
            neither declared set, or was announced after its auction was held or
            after it settles, which the declaration cannot date.
    """

    announced_time = time.fromisoformat(str(declaration["announcement_time"]))
    result_time = time.fromisoformat(str(declaration["result_time"]))
    announce_field = str(declaration["announcement_date_field"])
    result_field = str(declaration["result_date_field"])
    out: List[Auction] = []
    for number, record in enumerate(records, start=1):
        try:
            settles = date.fromisoformat(str(record["issue_date"]))
            announced = date.fromisoformat(str(record[announce_field]))
            auctioned = date.fromisoformat(str(record[result_field]))
            kind = str(record["security_type"])
            offering = _billions(record["offering_amt"])
            maturing = _billions(record["est_pub_held_mat_by_type_amt"])
            soma = _billions(record["soma_accepted"])
            held = str(record["total_accepted"]) != WITHHELD
        except (KeyError, ValueError) as exc:
            raise ValueError(
                f"auction record {number} lacks issue_date, {announce_field}, {result_field}, "
                f"security_type, offering_amt, est_pub_held_mat_by_type_amt, soma_accepted or total_accepted"
            ) from exc
        if offering is None:
            raise ValueError(f"auction record {number} has no offering_amt")
        if kind in TREASURY_BILL_SECURITY_TYPES:
            is_bill = True
        elif kind in TREASURY_COUPON_SECURITY_TYPES:
            is_bill = False
        else:
            raise ValueError(f"auction record {number} has security_type {kind!r}, in neither declared set")
        if announced > auctioned or announced > settles:
            raise ValueError(
                f"auction record {number} was announced on {announced}, after its auction on "
                f"{auctioned} or its settlement on {settles}"
            )
        out.append(
            Auction(
                settles,
                kind,
                is_bill,
                offering,
                maturing,
                soma,
                datetime.combine(announced, announced_time),
                datetime.combine(auctioned, result_time) if held else None,
            )
        )
    return tuple(out)


def load_snapshot(path: Path, declaration: Mapping[str, object]) -> Tuple[Auction, ...]:
    """`auction_records` over a tracked Fiscal Data auctions snapshot."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = payload.get("data") if isinstance(payload, Mapping) else None
    if not isinstance(records, list):
        raise ValueError(f"{path} does not contain a Fiscal Data data list")
    return auction_records(records, declaration)


def _by_day(auctions: Sequence[Auction]) -> Dict[date, List[Auction]]:
    out: Dict[date, List[Auction]] = {}
    for auction in auctions:
        out.setdefault(auction.settles, []).append(auction)
    return out


def known_auctions(auctions: Sequence[Auction], instant: datetime) -> List[Auction]:
    """The auctions announced at or before `instant`."""

    return [auction for auction in auctions if auction.announced_at <= instant]


def net_for_day(auctions: Sequence[Auction], instant: datetime) -> Tuple[float, float, int]:
    """`(net, net of the bill types, groups with no maturing figure)` of one settlement day's auctions.

    The auctions announced by `instant` are grouped by security type. A group's net is
    its summed offerings less its maturing amount, which is the largest figure any of
    its announced auctions carries, and 0.0 when none carries one (counted).
    """

    groups: Dict[str, List[Auction]] = {}
    for auction in known_auctions(auctions, instant):
        groups.setdefault(auction.kind, []).append(auction)
    net = bills = 0.0
    unknown = 0
    for members in groups.values():
        figures = [a.maturing for a in members if a.maturing is not None]
        maturing = max(figures) if figures else 0.0
        unknown += not figures
        value = sum(a.offering for a in members) - maturing
        net += value
        if members[0].is_bill:
            bills += value
    return net, bills, unknown


def _instant(day: date, declaration: Mapping[str, object]) -> datetime:
    return datetime.combine(day, time.fromisoformat(str(declaration["announcement_time"])))


def _columns_for(
    day: date, by_day: Mapping[date, Sequence[Auction]], instant: datetime
) -> Dict[str, float]:
    net, bills, _unknown = net_for_day(by_day.get(day, ()), instant)
    ahead = 0.0
    current = day
    for _ in range(WINDOW_DAYS):
        current = next_business_day(current, 1)
        ahead += net_for_day(by_day.get(current, ()), instant)[0]
    return {"net_settlement": net, "net_settlement_bills": bills, "net_settlement_due_5d": ahead}


def with_net_settlement(
    rows: Sequence[DailyObservation], auctions: Sequence[Auction], declaration: Mapping[str, object]
) -> List[DailyObservation]:
    """`rows` with the three columns, each as announced by the declared instant on the row's own day."""

    by_day = _by_day(auctions)
    out = []
    for row in rows:
        values = dict(row.values)
        values.update(_columns_for(row.date, by_day, _instant(row.date, declaration)))
        out.append(DailyObservation(row.date, values))
    return out


def gross_by_day(auctions: Sequence[Auction]) -> Dict[date, Dict[str, float]]:
    """Summed offerings per settlement day, in the panel's gross columns (USD billions, no dating)."""

    out: Dict[date, Dict[str, float]] = {}
    for auction in auctions:
        entry = out.setdefault(
            auction.settles,
            {"treasury_settlement": 0.0, "treasury_settlement_bills": 0.0, "treasury_settlement_coupons": 0.0},
        )
        entry["treasury_settlement"] += auction.offering
        entry["treasury_settlement_bills" if auction.is_bill else "treasury_settlement_coupons"] += auction.offering
    return out


def check_known_columns(
    rows: Sequence[DailyObservation], auctions: Sequence[Auction], declaration: Mapping[str, object]
) -> None:
    """Refuse a column that is not what was announced by the declared instant on its row's day.

    A hole (`None`) is not read.

    Raises:
        LookAheadError: a value is not what was announced by the instant but is what
            a later announcement instant would make it.
        StaleReadError: a value differs from what was announced and from every later
            reading, so it leaves out something that was public.
    """

    by_day = _by_day(auctions)
    announcements = sorted({auction.announced_at for auction in auctions})
    for row in rows:
        instant = _instant(row.date, declaration)
        known = _columns_for(row.date, by_day, instant)
        for column in COLUMNS:
            value = row.values.get(column)
            if value is None or abs(float(value) - known[column]) <= TOLERANCE:
                continue
            later = [
                _columns_for(row.date, by_day, moment)[column] for moment in announcements if moment > instant
            ]
            if any(abs(float(value) - other) <= TOLERANCE for other in later):
                raise LookAheadError(
                    f"{column} for {row.date.isoformat()} is {value}, which counts an auction announced "
                    f"after {instant}; only {known[column]} had been announced"
                )
            raise StaleReadError(
                f"{column} for {row.date.isoformat()} is {value}, but {known[column]} had been announced "
                f"by {instant}; the read left out an announcement"
            )
