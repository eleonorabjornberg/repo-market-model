"""Pre-SOFR funding-market history: EFFR - IOER from December 2008 (#129).

A separate study, not a panel and not a published input. The pressure models
learn from the SOFR era's few episodes (2018-04-03 onward); this module builds
the older unsecured history so a study can ask whether pooling it, or
pre-training on it, improves SOFR - IORB pressure forecasts.

**A different market and a different target.** EFFR is unsecured overnight
lending between depository institutions, dominated after 2008 by Federal Home
Loan Bank lending to institutions that do not earn IOER at the full rate; it
traded below IOER throughout 2008-12-16 to 2018-04-02. SOFR is secured Treasury
repo. EFFR - IOER above a threshold is therefore not the event SOFR - IORB above
the same threshold is, and the rows here say which market they come from.

The rows: one per business day the H.15 prints EFFR, from `HISTORY_START` (the
day the FOMC set a target range with IOER at its top) to `HISTORY_END` (the day
before the published panel's first row). Reserves and the TGA are the FRED
weekly series the panel reads, carried by reference date as the panel carries
them (`data.WEEKLY_CARRY_MAX_STALENESS_DAYS`). `days_to_month_end` and
`tax_date` are the panel's own functions. `quarter_end` is not: the panel's
reads `metadata/market_holidays.json`, which covers 2018 onward, so here it is
the last day of the quarter the H.15 printed (`quarter_end_on_print_calendar`).

The read: `HistoryRule` is the as-of rule for these rows. A forecast of row `i`
at horizon `h` is made at the declared decision time on row `i - h`, and reads
each input at the latest earlier row whose declared availability
(`metadata/sources.json`: `frb_ddp`, `fred_macro_latest_vintage`) is at or
before that instant. `HistoryRule.check` re-derives every read's availability
and raises `LookAheadError` on any read that was not public.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
)

from .asof import NEVER_ON_THIS_PANEL, declared_availability
from .data import (
    WEEKLY_CARRY_MAX_STALENESS_DAYS,
    days_to_month_end,
    exceeds_bp,
    tax_date,
)
from .splits import LookAheadError, SplitError

#: The FOMC's 16 December 2008 decision set the target range at 0-25 bp with
#: IOER at its top. IOER began on 9 October 2008 set below the target, and EFFR
#: traded above it until December; those weeks are a different regime again and
#: are left out.
HISTORY_START = date(2008, 12, 16)
#: The day before the published panel's first row (2018-04-03).
HISTORY_END = date(2018, 4, 2)

DDP_SOURCE = "frb_ddp"
FRED_SOURCE = "fred_macro_latest_vintage"
#: The DDP release and series name of each field the study reads.
DDP_SERIES = {"EFFR": ("H15", "RIFSPFF_N.B"), "IOER": ("PRATES", "RESBME_N.D")}
#: History column -> the fields its value is computed from.
FIELDS: Mapping[str, Tuple[Tuple[str, str], ...]] = {
    "spread_bps": ((DDP_SOURCE, "EFFR"), (DDP_SOURCE, "IOER")),
    "reserve_balances": ((FRED_SOURCE, "WRESBAL"),),
    "tga": ((FRED_SOURCE, "WTREGEN"),),
}
WEEKLY_SERIES = {"reserve_balances": "WRESBAL", "tga": "WTREGEN"}
#: The panel's weekly TGA change is measured over this many rows (`ml.TGA_CHANGE_ROWS`).
TGA_CHANGE_ROWS = 5


class HistoryRow(NamedTuple):
    """One business day of the pre-SOFR history.

    `values` carries the inputs the v1 design reads under the panel's names:
    `reserve_balances` and `tga` (USD billions, carried weekly), and the three
    calendar columns. `spread_bps` is EFFR - IOER in basis points.
    """

    date: date
    effr: float
    ioer: float
    values: Mapping[str, Optional[float]]

    @property
    def spread_bps(self) -> float:
        return 100.0 * (self.effr - self.ioer)


def _carry(series: Mapping[date, float], day: date) -> Optional[float]:
    """The latest print at or before `day`, within the panel's staleness bound."""

    best: Optional[date] = None
    for when in series:
        if when <= day and (best is None or when > best):
            best = when
    if best is None or (day - best).days > WEEKLY_CARRY_MAX_STALENESS_DAYS:
        return None
    return float(series[best])


def quarter_end_on_print_calendar(day: date, printed: Sequence[date]) -> float:
    """1.0 on the last day of `day`'s quarter that the H.15 printed EFFR.

    The study's stand-in for `data.quarter_end`, whose holiday table begins in
    2018. A print calendar is hindsight about which days were business days;
    between 2008-12-16 and 2018-04-02 no quarter ended on an unscheduled
    closure, so it names the day the holiday schedule would.

    Raises:
        ValueError: if the print calendar ends before `day`'s quarter does.
    """

    month = 3 * ((day.month - 1) // 3) + 3
    after = date(day.year + (month == 12), 1 if month == 12 else month + 1, 1)
    end = after - timedelta(days=1)
    if not printed or max(printed) < end:
        raise ValueError(f"the print calendar does not reach the end of {day}'s quarter, {end}")
    last = max(when for when in printed if when <= end)
    return float(day == last)


def history_rows(
    effr: Mapping[date, Optional[float]],
    ioer: Mapping[date, Optional[float]],
    weekly: Optional[Mapping[str, Mapping[date, float]]],
    *,
    start: date = HISTORY_START,
    end: date = HISTORY_END,
) -> List[HistoryRow]:
    """The history rows: every business day in range with both rates printed."""

    if start > end:
        raise ValueError(f"start {start} follows end {end}")
    weekly = weekly or {}
    printed = sorted(day for day, value in effr.items() if value is not None)
    sorted_weekly = {name: dict(sorted(series.items())) for name, series in weekly.items()}
    rows: List[HistoryRow] = []
    for day in sorted(effr):
        if not start <= day <= end:
            continue
        rate, floor = effr[day], ioer.get(day)
        if rate is None or floor is None:
            continue
        values: Dict[str, Optional[float]] = {
            name: _carry(sorted_weekly.get(name, {}), day) for name in WEEKLY_SERIES
        }
        values["days_to_month_end"] = days_to_month_end(day)
        values["quarter_end"] = quarter_end_on_print_calendar(day, printed)
        values["tax_date"] = tax_date(day)
        rows.append(HistoryRow(day, float(rate), float(floor), values))
    return rows


def load_ddp_series(directory: Path) -> Tuple[Dict[date, Optional[float]], Dict[date, Optional[float]]]:
    """EFFR and IOER from the tracked DDP snapshots under `directory`.

    Each snapshot's bytes are checked against its manifest's SHA-256 before
    they are read. The newest snapshot of each release is used.
    """

    from . import ingest

    latest: Dict[str, Tuple[str, bytes]] = {}
    for manifest in sorted(Path(directory).glob("*.manifest.json")):
        artifact = ingest.load_snapshot_manifest(manifest)
        payload = ingest._artifact_payload(artifact)
        release = dict(part.split("=", 1) for part in artifact.url.split("?", 1)[1].split("&"))["rel"]
        if release not in latest or artifact.retrieved_at > latest[release][0]:
            latest[release] = (artifact.retrieved_at, payload)
    out = []
    for field in ("EFFR", "IOER"):
        release, series = DDP_SERIES[field]
        if release not in latest:
            raise ValueError(f"no {release} snapshot under {directory}")
        out.append(ingest.frb_ddp_series(latest[release][1], release, series))
    return out[0], out[1]


def load_weekly(fred_snapshot_directory: Path) -> Dict[str, Dict[date, float]]:
    """Reserves and the TGA, USD billions, from the panel's FRED snapshot."""

    from . import ingest

    (manifest,) = sorted(Path(fred_snapshot_directory).glob("*.manifest.json"))
    parsed = ingest.parse_snapshots([ingest.load_snapshot_manifest(manifest)])
    out: Dict[str, Dict[date, float]] = {name: {} for name in WEEKLY_SERIES}
    wanted = {series: name for name, series in WEEKLY_SERIES.items()}
    for row in parsed.rows:
        if row.series_id in wanted:
            out[wanted[row.series_id]][row.ref_date] = float(row.value)
    return out


def load_history_rows(
    ddp_directory: Path, fred_snapshot_directory: Optional[Path]
) -> List[HistoryRow]:
    """The tracked history, `HISTORY_START` to `HISTORY_END`."""

    effr, ioer = load_ddp_series(ddp_directory)
    weekly = None if fred_snapshot_directory is None else load_weekly(fred_snapshot_directory)
    return history_rows(effr, ioer, weekly)


class HistoryRead(NamedTuple):
    """Where one forecast of a history row reads each input."""

    scored_index: int
    decision_instant: datetime
    rows: Mapping[str, int]


class HistoryRule:
    """The as-of rule for the history rows, one horizon, one decision time."""

    def __init__(
        self, registry: Mapping[str, Mapping[str, object]], *, decision_time: time, horizon: int = 1
    ) -> None:
        if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
            raise ValueError(f"horizon must be an int of at least 1, got {horizon!r}")
        for source, _ in (pair for fields in FIELDS.values() for pair in fields):
            if source not in registry:
                raise ValueError(f"the registry declares no source {source!r}")
        self.registry = registry
        self.decision_time = decision_time
        self.horizon = horizon

    def decision_instant(self, dates: Sequence[date], scored_index: int) -> datetime:
        if scored_index < self.horizon:
            raise SplitError(f"row {scored_index} has no row {self.horizon} before it")
        return datetime.combine(dates[scored_index - self.horizon], self.decision_time)

    def availability(
        self, dates: Sequence[date], fields: Sequence[Tuple[str, str]], position: int
    ) -> datetime:
        """When every one of `fields` is public for `dates[position]`."""

        latest = datetime.min
        for source, field in fields:
            moment = declared_availability(self.registry, source, field, dates, position)
            if moment is None:
                raise ValueError(f"{source}.{field} declares no row-relative availability")
            latest = max(latest, moment)
        return latest

    def _latest(self, dates: Sequence[date], fields, scored_index: int, deadline: datetime) -> int:
        position = scored_index - 1
        while position >= 0:
            if self.availability(dates, fields, position) <= deadline:
                return position
            position -= 1
        return position

    def read(self, dates: Sequence[date], scored_index: int) -> HistoryRead:
        """Each input's row for the forecast of `dates[scored_index]`."""

        deadline = self.decision_instant(dates, scored_index)
        rows = {}
        for column, fields in FIELDS.items():
            position = self._latest(dates, fields, scored_index, deadline)
            if position < 0:
                raise SplitError(f"no {column} is public at {deadline}")
            rows[column] = position
        return HistoryRead(scored_index, deadline, rows)

    def check(self, dates: Sequence[date], read: HistoryRead) -> None:
        """The independent guard: every read was public at its decision instant.

        Re-derives the deadline from the scored row and the horizon, and each
        read's availability from the registry, without `_latest`.

        Raises:
            LookAheadError: if a read is the scored row or later, or was not yet
                public at the decision instant.
        """

        index = read.scored_index
        deadline = datetime.combine(dates[index - self.horizon], self.decision_time)
        for column, position in read.rows.items():
            if position >= index:
                raise LookAheadError(
                    f"{dates[index]}: {column} is read at row {position}, not before the scored row"
                )
            moment = self.availability(dates, FIELDS[column], position)
            if moment > deadline:
                raise LookAheadError(
                    f"{dates[index]}: {column} for {dates[position]} is public at {moment}, "
                    f"after the {deadline} decision"
                )

    def label_available_at(self, dates: Sequence[date], index: int) -> datetime:
        return self.availability(dates, FIELDS["spread_bps"], index)


class HistoryObservation(NamedTuple):
    """What a forecast of one history row reads, in the v1 design's shape."""

    date: date
    spread_bps: float
    values: Mapping[str, Optional[float]]


class HistoryPool(NamedTuple):
    """Design rows and labels from the history, with when each label was public."""

    xs: Tuple[Tuple[float, ...], ...]
    spreads: Tuple[float, ...]
    dates: Tuple[date, ...]
    available_at: Tuple[datetime, ...]
    horizon: int


def history_pairs(design: Any, rule: HistoryRule, rows: Sequence[HistoryRow]) -> HistoryPool:
    """Direct pairs from the history: each label with what a forecast of it read.

    `design` is the pressure design (`ml._PressureDesign`, duck-typed so this
    module stays stdlib): `design.row(observation, tga_change)` and
    `design.tga`. Every read passes `rule.check`. A label whose read has a hole
    (a weekly input not yet printed, or too short a TGA history) trains no pair,
    and nor does the last row, whose label is printed on a day past the rows.
    """

    dates = [row.date for row in rows]
    xs: List[Tuple[float, ...]] = []
    spreads: List[float] = []
    kept: List[date] = []
    available: List[datetime] = []
    for index in range(len(rows)):
        try:
            read = rule.read(dates, index)
        except SplitError:
            continue
        rule.check(dates, read)
        values: Dict[str, Optional[float]] = {
            name: rows[read.rows[name]].values.get(name) for name in WEEKLY_SERIES
        }
        for name in ("days_to_month_end", "quarter_end", "tax_date"):
            values[name] = rows[index].values[name]
        observation = HistoryObservation(
            dates[index], rows[read.rows["spread_bps"]].spread_bps, values
        )
        tga_change: Optional[float] = None
        if getattr(design, "tga", False):
            position = read.rows["tga"]
            if position < TGA_CHANGE_ROWS:
                continue
            now, before = rows[position].values.get("tga"), rows[position - TGA_CHANGE_ROWS].values.get("tga")
            if now is None or before is None:
                continue
            tga_change = float(now) - float(before)
        label_public = rule.label_available_at(dates, index)
        if label_public == NEVER_ON_THIS_PANEL:
            # The last row: its print is on a day the rows do not carry.
            continue
        try:
            features = design.row(observation, tga_change)
        except ValueError:
            continue
        xs.append(tuple(float(value) for value in features))
        spreads.append(rows[index].spread_bps)
        kept.append(dates[index])
        available.append(label_public)
    return HistoryPool(tuple(xs), tuple(spreads), tuple(kept), tuple(available), rule.horizon)


def require_pool_public(available_at: Sequence[datetime], last_training_day: date) -> None:
    """Refuse a pool with a label not public before the fit's last training day.

    A fit's last training label is public at the fit's decision instant, and
    that instant is after the start of the label's own day, so a pooled label
    public before that midnight is public at the fit.

    Raises:
        LookAheadError: if any pooled label is public only at or after the start
            of `last_training_day`.
    """

    if not available_at:
        return
    latest = max(available_at)
    cutoff = datetime.combine(last_training_day, time.min)
    if latest >= cutoff:
        raise LookAheadError(
            f"a pooled label is public at {latest}, not before the fit's last "
            f"training day {last_training_day}"
        )


def episodes(rows: Sequence[HistoryRow], tau: float) -> List[Dict[str, Any]]:
    """Runs of consecutive rows with EFFR - IOER strictly above `tau` bp."""

    out: List[Dict[str, Any]] = []
    run: List[HistoryRow] = []
    for row in list(rows) + [None]:  # type: ignore[list-item]
        if row is not None and exceeds_bp(row.spread_bps, tau):
            run.append(row)
            continue
        if run:
            peak = max(run, key=lambda item: item.spread_bps)
            out.append(
                {
                    "start": run[0].date.isoformat(),
                    "end": run[-1].date.isoformat(),
                    "days": len(run),
                    "peak_bps": round(peak.spread_bps, 6),
                    "peak_date": peak.date.isoformat(),
                    "reserve_balances_at_start": run[0].values.get("reserve_balances"),
                }
            )
            run = []
    return out
