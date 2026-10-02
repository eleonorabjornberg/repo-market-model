"""Announced IORB: what the decision instant already knew about the rate on `T`.

Directive #38. The rate on reserve balances (IOER before 2021-07-29) moves only
when the Board announces it, in an FOMC implementation note that names the new
rate and the date it takes effect (`docs/decisions/iorb-availability.md`). The
dated table of those notes is
`tests/fixtures/snapshots/fed-iorb-announcements/iorb_changes.csv`, read from
the fetched pages by `scripts/build_iorb_table.py`.

Two features, read for the scored row `T` at the decision instant -- the
declared decision time on the panel day before `T`, `D = dates[T - 1]`:

* `iorb_announced_change_bps`: the IORB change, in basis points, that takes
  effect after `D` and on or before `T`, summed over the notes **announced at
  or before the decision instant**. `0.0` when no such note exists.
* `iorb_days_to_announced_change`: panel business days from `T` to the
  earliest effective date after `D` among those notes; `0.0` when it takes
  effect on `T` itself, `None` when none is announced.

**Keyed on the announcement time, not the effective date.** A note enters a
decision only when its announcement instant (the FOMC statement's release
time, America/New_York wall clock, compared as `asof` compares every instant)
is at or before the decision instant. The Sunday cut of 2020-03-15 (17:00 EDT,
effective Monday 2020-03-16) is therefore invisible to the forecast made on
Friday 2020-03-13 for 2020-03-16, and to every later one: by the decision on
2020-03-16 it is already in force. An effective-date key would have handed that
Friday forecast a -100 bp change nobody knew of.

The columns are computed per scored row, so the value carried at row `T` is by
construction public at `D`'s decision instant. `metadata/sources.json` declares
the two fields under `scheduled_availability` (one panel business day before
`T`, at the 16:00 decision), and the as-of rule checks that declaration like
any other read. The published panel does not carry them: `with_announced_iorb`
adds them to a panel in memory, so the published panel's bytes do not move.

Stdlib only.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

from .data import DailyObservation

__all__ = [
    "ANNOUNCED_CHANGE",
    "DAYS_TO_CHANGE",
    "FEATURES",
    "IorbAnnouncement",
    "announced_iorb_features",
    "check_announcements",
    "load_announcements",
    "with_announced_iorb",
]

ANNOUNCED_CHANGE = "iorb_announced_change_bps"
DAYS_TO_CHANGE = "iorb_days_to_announced_change"
FEATURES = (ANNOUNCED_CHANGE, DAYS_TO_CHANGE)

_KINDS = ("anchor", "change", "unchanged")


class IorbAnnouncement(NamedTuple):
    """One implementation note: when it was public, and what it set from when."""

    announced_at: datetime  # America/New_York wall clock, naive
    effective: date
    rate_bps: int
    change_bps: int  # 0 for the anchor and for a note that restated the rate
    kind: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_announcements(path: Path, *, manifest: Optional[Path] = None) -> Tuple[IorbAnnouncement, ...]:
    """Read and check the table; refuse it if its bytes are not the manifest's.

    `manifest` defaults to the table's sidecar, `<table>.manifest.json`.

    Raises:
        ValueError: a checksum mismatch, a malformed row, or a table that
            fails `check_announcements`.
    """

    path = Path(path)
    manifest = Path(manifest) if manifest is not None else path.with_name(path.name + ".manifest.json")
    recorded = json.loads(manifest.read_text(encoding="utf-8"))["sha256"]
    actual = _sha256(path)
    if actual != recorded:
        raise ValueError(f"{path}: sha256 {actual} is not the manifest's {recorded}")
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for number, row in enumerate(csv.DictReader(handle), start=2):
            try:
                announced_at = datetime.combine(
                    date.fromisoformat(row["announcement_date"]),
                    time.fromisoformat(row["announcement_time"]),
                )
                rate_bps = round(float(row["rate_percent"]) * 100)
                change = int(row["change_bps"]) if row["change_bps"] else 0
                rows.append(
                    IorbAnnouncement(
                        announced_at,
                        date.fromisoformat(row["effective_date"]),
                        rate_bps,
                        change,
                        row["kind"],
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{path} row {number}: {exc}") from exc
    check_announcements(rows)
    return tuple(rows)


def check_announcements(rows: Sequence[IorbAnnouncement]) -> None:
    """Raise unless the table is one the features may be read from.

    * every note takes effect on a **later calendar date** than its
      announcement. The features key on the announcement and count from `D`, so
      a note effective on its own announcement day would be a change in force
      before the instant it became public -- the case
      `docs/decisions/iorb-availability.md` states never happens, checked here
      row by row;
    * announcements and effective dates both strictly ascend;
    * the first row is the anchor, and each later row's `change_bps` is its
      rate less the previous row's, with `kind` `change` exactly when it moved.

    Data guards: `ValueError`, per CLAUDE.md.
    """

    if not rows:
        raise ValueError("the IORB announcement table is empty")
    for index, row in enumerate(rows):
        if row.kind not in _KINDS:
            raise ValueError(f"row {index}: kind {row.kind!r} is not one of {_KINDS}")
        if row.effective <= row.announced_at.date():
            raise ValueError(
                f"row {index}: announced {row.announced_at.isoformat(sep=' ')} but effective "
                f"{row.effective}; a note must take effect after the day it is announced"
            )
        if index == 0:
            if row.kind != "anchor" or row.change_bps != 0:
                raise ValueError("row 0 must be the anchor, with no change")
            continue
        before = rows[index - 1]
        if row.announced_at <= before.announced_at or row.effective <= before.effective:
            raise ValueError(f"row {index}: announcements and effective dates must strictly ascend")
        if row.kind == "anchor":
            raise ValueError(f"row {index}: only the first row is the anchor")
        if row.change_bps != row.rate_bps - before.rate_bps:
            raise ValueError(
                f"row {index}: change_bps {row.change_bps} is not "
                f"{row.rate_bps} - {before.rate_bps}"
            )
        if (row.kind == "change") != (row.change_bps != 0):
            raise ValueError(f"row {index}: kind {row.kind!r} disagrees with change_bps {row.change_bps}")


def _business_days_after(dates: Sequence[date], start: int, until: date) -> int:
    """Panel rows in `(dates[start], until]`; weekdays past the panel's end.

    Past the last panel date there is no panel calendar to count on, so
    weekdays are counted. The panel is the only calendar this project keeps
    (`asof`), and inside it nothing else is used.
    """

    count = 0
    position = start + 1
    while position < len(dates) and dates[position] <= until:
        count += 1
        position += 1
    if position < len(dates):
        return count
    day = max(dates[-1], dates[start])
    while day < until:
        day += timedelta(days=1)
        if day.weekday() < 5:
            count += 1
    return count


def announced_iorb_features(
    dates: Sequence[date],
    announcements: Sequence[IorbAnnouncement],
    *,
    decision_time: time,
) -> List[Dict[str, Optional[float]]]:
    """The two features for every row, each read at that row's decision instant.

    Row 0 has no panel day before it and so no decision instant: both are
    `None`. Every other row `T` reads only notes announced at or before
    `decision_time` on `dates[T - 1]`.
    """

    if not isinstance(decision_time, time):
        raise TypeError("decision_time must be a datetime.time")
    moment = decision_time.replace(tzinfo=None)
    changes = [row for row in announcements if row.kind == "change"]
    out: List[Dict[str, Optional[float]]] = [{ANNOUNCED_CHANGE: None, DAYS_TO_CHANGE: None}]
    for scored in range(1, len(dates)):
        decided = dates[scored - 1]
        instant = datetime.combine(decided, moment)
        known = [row for row in changes if row.announced_at <= instant and row.effective > decided]
        moved = sum(row.change_bps for row in known if row.effective <= dates[scored])
        if known:
            effective = min(row.effective for row in known)
            days: Optional[float] = float(
                0 if effective <= dates[scored] else _business_days_after(dates, scored, effective)
            )
        else:
            days = None
        out.append({ANNOUNCED_CHANGE: float(moved), DAYS_TO_CHANGE: days})
    return out


def with_announced_iorb(
    observations: Sequence[DailyObservation],
    announcements: Sequence[IorbAnnouncement],
    *,
    decision_time: time,
) -> List[DailyObservation]:
    """The panel with the two columns added; every other value untouched.

    Raises:
        ValueError: if the panel already carries either column.
    """

    for observation in observations:
        clash = [name for name in FEATURES if name in observation.values]
        if clash:
            raise ValueError(f"{observation.date}: the panel already carries {clash}")
    features = announced_iorb_features(
        [observation.date for observation in observations],
        announcements,
        decision_time=decision_time,
    )
    return [
        DailyObservation(observation.date, {**observation.values, **added})
        for observation, added in zip(observations, features)
    ]
