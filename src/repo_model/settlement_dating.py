"""A Treasury settlement dated from its auction result (#175) or its announcement (#541), measured and off.

`metadata/sources.json` declares a settlement public one panel business day
before it settles (`treasury_auctions`, `scheduled_availability`), so at a
decision two or more panel days ahead it is not yet public, and every
declaration drops it there (#114, #170 option A). That declaration is the one
every published record is scored under, and nothing here changes it.

`metadata/settlement_result_dating.json` declares an alternative, read by a
scoring script and by no published record: an auction's settlement date and
offering amount are public from its result, at the declared instant on its
auction date. For the forecast made `h` panel days before a settlement day `d`,
a settlement column for `d` is then the sum of the offering amounts of the
auctions settling on `d` whose results were public by that instant on the
decision day, `dates[d - h]`. That sum is public at that instant by
construction, which is what `result_dated_registry` declares to the as-of
rule: the same scheduled block, `h` panel days ahead instead of one.

The guard is `check_known_columns`. A column that counts an auction whose
result was not yet public raises `LookAheadError`; one that leaves out an
auction whose result was public raises `StaleReadError`. The published panel's
own columns pass it at `h = 1` and are refused at `h = 2`.

`metadata/settlement_announcement_dating.json` (#541, Eleonora's ruling of 10 October 2026) declares
the second basis, `auction_announcement`: an auction's settlement date and offering amount are public from
its announcement, at the declared instant on its `announcemt_date`. Everything above applies unchanged
with "announced" for "result": a column that counts an auction not yet announced raises
`LookAheadError`, one that leaves out an announced auction raises `StaleReadError`. The announcement
carries no closing-time guard (it precedes the auction); a record announced after its auction or its
settlement is refused instead. Neither declaration is read by a published record.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import copy
import json
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .asof import SCHEDULED_AVAILABILITY_KEY, StaleReadError
from .contract import TREASURY_BILL_SECURITY_TYPES, TREASURY_COUPON_SECURITY_TYPES
from .data import DailyObservation
from .splits import LookAheadError

__all__ = [
    "AGGREGATE",
    "ANNOUNCEMENT",
    "AuctionResult",
    "RESULT",
    "COLUMNS",
    "auction_results",
    "check_known_columns",
    "coverage",
    "known_amount",
    "known_columns",
    "load_result_dating",
    "load_snapshot_results",
    "result_dated_registry",
]

#: The aggregate column; every auction settling on a day is in it.
AGGREGATE = "treasury_settlement"
#: The panel columns this declaration dates, the aggregate first.
COLUMNS = (AGGREGATE, "treasury_settlement_bills", "treasury_settlement_coupons")
#: An auction result outside the aggregate, which this declaration does not date.
SOMA = "treasury_settlement_soma"
#: Fiscal Data's token for a field it does not have yet.
WITHHELD = "null"
#: How far two sums of the same amounts may differ by summation order alone.
TOLERANCE = 1e-9

#: The two bases a declaration may carry, and the keys each reads besides the common ones.
RESULT = "auction_result"
ANNOUNCEMENT = "auction_announcement"
_COMMON = {"source", "basis", "columns", "available_time", "timezone", "rule", "missing", "evidence"}
_REQUIRED = {
    RESULT: _COMMON | {"result_date_field", "result_held_field"},
    ANNOUNCEMENT: _COMMON | {"announcement_date_field"},
}


class AuctionResult(NamedTuple):
    """One auction: the day it settles, its leg, its offering, and when its result was public.

    `public_at` is `None` when the snapshot carries no result for it (a result-dated declaration;
    an announcement-dated one always has an instant).
    """

    settles: date
    column: str
    amount: float
    public_at: Optional[datetime]


def load_result_dating(path: Path) -> dict:
    """The declaration, checked for the keys this module reads.

    Raises:
        ValueError: a key is missing, the basis or columns are not this
            module's, or the instant is not an HH:MM time.
    """

    declaration = json.loads(Path(path).read_text(encoding="utf-8"))
    basis = declaration.get("basis")
    if basis not in _REQUIRED:
        raise ValueError(f"{path}: basis must be one of {sorted(_REQUIRED)}, got {basis!r}")
    missing = sorted(_REQUIRED[basis] - set(declaration))
    if missing:
        raise ValueError(f"{path}: the settlement dating declaration lacks {missing}")
    if tuple(declaration["columns"]) != COLUMNS:
        raise ValueError(f"{path}: columns must be {list(COLUMNS)}, got {list(declaration['columns'])}")
    time.fromisoformat(declaration["available_time"])
    return declaration


def _instant(declaration: Mapping[str, object]) -> time:
    return time.fromisoformat(str(declaration["available_time"]))


def _closing(text: str) -> time:
    return datetime.strptime(text.strip(), "%I:%M %p").time()


def auction_results(
    records: Sequence[Mapping[str, object]], declaration: Mapping[str, object]
) -> Tuple[AuctionResult, ...]:
    """Each Fiscal Data auction record as an `AuctionResult`, in record order.

    Under a result-dated declaration `public_at` is the declared instant on the
    auction date, and `None` for an auction with no result on file. Under an
    announcement-dated one it is the declared instant on the announcement date,
    for every record.

    Raises:
        ValueError: a record lacks a field read here, has a security type in
            neither declared set, closed for competitive bids after the
            declared result instant (which would date its result before the
            auction ended), or was announced after its auction or its
            settlement (which would date it from after it happened).
    """

    moment = _instant(declaration)
    announced_basis = declaration["basis"] == ANNOUNCEMENT
    date_field = str(declaration["announcement_date_field" if announced_basis else "result_date_field"])
    held_field = None if announced_basis else str(declaration["result_held_field"])
    out = []
    for number, record in enumerate(records, start=1):
        try:
            settles = date.fromisoformat(str(record["issue_date"]))
            dated = date.fromisoformat(str(record[date_field]))
            kind = str(record["security_type"])
            amount = float(str(record["offering_amt"]).replace(",", "")) / 1_000_000_000
            if announced_basis:
                held, closing = True, WITHHELD
                held_on = date.fromisoformat(str(record["auction_date"]))
            else:
                held, closing = str(record[held_field]) != WITHHELD, str(record["closing_time_comp"])
                held_on = dated
        except (KeyError, ValueError) as exc:
            needs = (
                f"issue_date, auction_date, {date_field}, security_type or offering_amt"
                if announced_basis
                else f"issue_date, {date_field}, security_type, offering_amt, {held_field} or closing_time_comp"
            )
            raise ValueError(f"auction record {number} lacks {needs}") from exc
        if kind in TREASURY_BILL_SECURITY_TYPES:
            column = "treasury_settlement_bills"
        elif kind in TREASURY_COUPON_SECURITY_TYPES:
            column = "treasury_settlement_coupons"
        else:
            raise ValueError(f"auction record {number} has security_type {kind!r}, in neither declared set")
        if announced_basis and (dated > held_on or dated > settles):
            raise ValueError(
                f"auction record {number} was announced on {dated}, after its auction ({held_on}) or "
                f"its settlement ({settles}); the declaration would date it from after it happened"
            )
        if not announced_basis and held and closing != WITHHELD and _closing(closing) > moment:
            raise ValueError(
                f"auction record {number} ({dated}) closed at {closing}, after the declared "
                f"result instant {moment.strftime('%H:%M')}; the declaration would date its result "
                f"before the auction ended"
            )
        public_at = datetime.combine(dated, moment) if held else None
        out.append(AuctionResult(settles, column, amount, public_at))
    return tuple(out)


def load_snapshot_results(path: Path, declaration: Mapping[str, object]) -> Tuple[AuctionResult, ...]:
    """`auction_results` over a tracked Fiscal Data auctions snapshot."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = payload.get("data") if isinstance(payload, Mapping) else None
    if not isinstance(records, list):
        raise ValueError(f"{path} does not contain a Fiscal Data data list")
    return auction_results(records, declaration)


def _by_day(results: Sequence[AuctionResult]) -> Dict[date, List[AuctionResult]]:
    out: Dict[date, List[AuctionResult]] = {}
    for result in results:
        out.setdefault(result.settles, []).append(result)
    return out


def known_amount(
    results: Sequence[AuctionResult], column: str, instant: datetime
) -> float:
    """The amount in `column` of `results` (one settlement day's) whose result was public at `instant`."""

    return sum(
        (
            result.amount
            for result in results
            if (column == AGGREGATE or result.column == column)
            and result.public_at is not None
            and result.public_at <= instant
        ),
        0.0,
    )


def _decision(dates: Sequence[date], position: int, horizon: int, declaration) -> Optional[datetime]:
    if position < horizon:
        return None
    return datetime.combine(dates[position - horizon], _instant(declaration))


def known_columns(
    rows: Sequence[DailyObservation],
    results: Sequence[AuctionResult],
    horizon: int,
    declaration: Mapping[str, object],
) -> List[DailyObservation]:
    """`rows` with each settlement column as known `horizon` panel days ahead.

    A row keeps a hole where the panel has one (outside the snapshot's
    coverage) and gets one where no panel day lies `horizon` days before it.
    Otherwise each column is `known_amount` at the declared instant on the
    decision day: 0.0 when nothing settling that day had a public result.
    `treasury_settlement_soma` is a hole: this declaration does not date it.
    """

    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError(f"horizon must be an int of at least 1, got {horizon!r}")
    dates = [row.date for row in rows]
    by_day = _by_day(results)
    out = []
    for position, row in enumerate(rows):
        values = dict(row.values)
        instant = _decision(dates, position, horizon, declaration)
        settling = by_day.get(row.date, ())
        for column in COLUMNS:
            if instant is None or values.get(column) is None:
                values[column] = None
            else:
                values[column] = known_amount(settling, column, instant)
        values[SOMA] = None
        out.append(DailyObservation(row.date, values))
    return out


def check_known_columns(
    rows: Sequence[DailyObservation],
    results: Sequence[AuctionResult],
    horizon: int,
    declaration: Mapping[str, object],
) -> None:
    """Refuse a settlement column that is not what was public `horizon` panel days ahead.

    Rows with no panel day `horizon` days before them, and holes, are not
    read. Amounts are never negative, so a value above the public sum counts
    something not yet public, and one below it leaves something public out.

    Raises:
        LookAheadError: a value counts an auction whose result was not public
            at the declared instant on the decision day.
        StaleReadError: a value leaves out an auction whose result was.
    """

    dates = [row.date for row in rows]
    by_day = _by_day(results)
    for position, row in enumerate(rows):
        instant = _decision(dates, position, horizon, declaration)
        if instant is None:
            continue
        settling = by_day.get(row.date, ())
        for column in COLUMNS:
            value = row.values.get(column)
            if value is None:
                continue
            public = known_amount(settling, column, instant)
            if float(value) > public + TOLERANCE:
                raise LookAheadError(
                    f"{column} for {row.date.isoformat()} is {value}, but only {public} of it "
                    f"had a public auction result by {instant}, the decision {horizon} panel "
                    f"day(s) ahead"
                )
            if float(value) < public - TOLERANCE:
                raise StaleReadError(
                    f"{column} for {row.date.isoformat()} is {value}, but {public} of it had a "
                    f"public auction result by {instant}; the read left out a public result"
                )


def result_dated_registry(
    registry: Mapping[str, Mapping[str, object]],
    declaration: Mapping[str, object],
    horizon: int,
) -> dict:
    """A copy of `registry` declaring the dated columns public `horizon` days ahead.

    The `treasury_auctions` scheduled block keeps its fields, instant and
    timezone; its `days` becomes `horizon`, and its evidence names this
    declaration. It describes columns made by `known_columns` at the same
    horizon and checked by `check_known_columns`, and no others. `registry`
    itself is not changed.
    """

    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError(f"horizon must be an int of at least 1, got {horizon!r}")
    out = copy.deepcopy(dict(registry))
    source = str(declaration["source"])
    block = dict(out[source][SCHEDULED_AVAILABILITY_KEY])
    announced = declaration["basis"] == ANNOUNCEMENT
    if block["timezone"] != declaration["timezone"] or (
        not announced and block["available_time"] != declaration["available_time"]
    ):
        raise ValueError(
            f"the settlement dating instant {declaration['available_time']} {declaration['timezone']} is not "
            f"the published block's {block['available_time']} {block['timezone']}"
        )
    block["days"] = horizon
    block["available_time"] = str(declaration["available_time"])
    what = "announced" if announced else "whose results were public"
    where = "metadata/settlement_announcement_dating.json (#541)" if announced else "metadata/settlement_result_dating.json (#175)"
    block["evidence"] = (
        f"{where}, at horizon {horizon}: each column is the "
        f"sum of the auctions {what} by {declaration['available_time']} on the "
        f"decision day, made by settlement_dating.known_columns and checked by "
        f"settlement_dating.check_known_columns. " + str(declaration["evidence"])
    )
    block["note"] = f"A measurement variant, read by no published record ({where.split('(')[1]}"
    out[source] = dict(out[source])
    out[source][SCHEDULED_AVAILABILITY_KEY] = block
    return out


def coverage(
    rows: Sequence[DailyObservation],
    results: Sequence[AuctionResult],
    horizons: Sequence[int],
    declaration: Mapping[str, object],
    *,
    end: date,
) -> Dict[int, Dict[str, int]]:
    """Per horizon, how many settlement days up to `end` were fully or partly known.

    A settlement day is a panel day on or before `end` with an auction
    settling on it. `complete` counts those whose every result was public at
    the decision, `partial` those with some but not all, `none` the rest.
    """

    dates = [row.date for row in rows]
    by_day = _by_day(results)
    out = {}
    for horizon in horizons:
        counts = {"settlement_days": 0, "complete": 0, "partial": 0, "none": 0}
        for position, day in enumerate(dates):
            if day > end or day not in by_day:
                continue
            instant = _decision(dates, position, horizon, declaration)
            if instant is None:
                continue
            settling = by_day[day]
            public = sum(1 for r in settling if r.public_at is not None and r.public_at <= instant)
            counts["settlement_days"] += 1
            if public == len(settling):
                counts["complete"] += 1
            elif public:
                counts["partial"] += 1
            else:
                counts["none"] += 1
        out[horizon] = counts
    return out

