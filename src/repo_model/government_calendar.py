"""Sources dated by the days the government is open, for one measurement run (#1016, of finding #1003).

The OFR's data-release page says: "Releases are not published on government holidays and data for affected days are
instead published on the next day the government is open". A source whose registry entry sets `government_open_days_only`
(`ofr_stfm_repo_cleared`, #968) has its business-day lag counted on panel rows the government is open, so a value is
first observable at the declared time on the `days`-th such row after its own. The panel's rows are SOFR publication
days, so a statutory holiday the market opened (`statutory_days_the_market_opened` in `metadata/market_holidays.json`:
2021-06-18, 2021-12-31, 2023-11-10) is a row the government is closed on and the OFR did not release on.

Government-closed days are the table's `basis: statute` rows and `statutory_days_the_market_opened`, and nothing else:
the executive-order closures are not in the table, and whether they count is Eleonora's question (#1016, criterion 3).

`asof.py` is frozen by the final-test pre-registration (the whole file), so it is not edited. As
`h41_release.release_dating()` does, `government_open_dating()` swaps `asof.declared_availability` and its alias
`baseline._declared_availability` for the length of one run and restores both on the way out, raise or return. A source
that does not opt in is dated by the original function, so a registry with no opt-in is read exactly as before, and no
published declaration sets the key.

Stdlib only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import contextlib
import json
from datetime import date, datetime, time
from typing import Dict, FrozenSet, Iterator, Mapping, Optional, Sequence

from . import asof, baseline, data

__all__ = ["OPT_IN_KEY", "government_closed_days", "government_open_dating"]

#: A source-level flag. Absent from every published registry.
OPT_IN_KEY = "government_open_days_only"

_CACHE: Dict[str, FrozenSet[date]] = {}


def government_closed_days() -> FrozenSet[date]:
    """The statutory holidays in `metadata/market_holidays.json`, whether or not the market closed.

    Raises:
        ValueError: the file is not the one `data.MARKET_HOLIDAYS_SHA256` names (read through `data.market_holidays`).
    """

    holidays = data.market_holidays()  # refuses a file that does not match its pinned checksum
    key = str(data.MARKET_HOLIDAYS_PATH)
    if key not in _CACHE:
        table = json.loads(data.MARKET_HOLIDAYS_PATH.read_text(encoding="utf-8"))
        days = {date.fromisoformat(item["date"]) for item in table["closed"] if item["basis"] == "statute"}
        days |= {date.fromisoformat(item["date"]) for item in table["statutory_days_the_market_opened"]}
        _CACHE[key] = frozenset(days)
    return _CACHE[key]


def _government_open_availability(
    registry: Mapping[str, Mapping[str, object]],
    source_id: str,
    field: str,
    dates: Sequence[date],
    position: int,
    lag: Mapping[str, object],
) -> Optional[datetime]:
    days = int(lag["days"])
    moment = time.fromisoformat(str(lag.get("available_time", asof.END_OF_DAY)))
    holidays = data.market_holidays()
    closed = government_closed_days()
    seen = 0
    for row in range(position + 1, len(dates)):
        row_date = dates[row]
        if not (holidays.first <= row_date <= holidays.last):
            raise ValueError(
                f"{source_id}.{field}: panel day {row_date} is outside the holiday table "
                f"({holidays.first} to {holidays.last}), so whether the government was open is not known"
            )
        if row_date in closed:
            continue
        seen += 1
        if seen == days:
            return datetime.combine(row_date, moment)
    return asof.NEVER_ON_THIS_PANEL


def _opted_in(registry: Mapping[str, Mapping[str, object]], source_id: str, field: str) -> Optional[Mapping[str, object]]:
    source = registry[source_id]
    if not source.get(OPT_IN_KEY):
        return None
    lag = (source.get("field_release_lags") or {}).get(field) or source.get("release_lag") or {}
    if lag.get("unit") != "business_days" or lag.get("days") is None or int(lag["days"]) < 1:
        return None
    return lag


@contextlib.contextmanager
def government_open_dating() -> Iterator[None]:
    """The as-of rule counting an opted-in source's business-day lag on government-open panel rows, for one run."""

    original = asof.declared_availability
    original_baseline = baseline._declared_availability

    def declared_availability(registry, source_id, field, dates, position):
        lag = _opted_in(registry, source_id, field)
        if lag is not None:
            return _government_open_availability(registry, source_id, field, dates, position, lag)
        return original(registry, source_id, field, dates, position)

    asof.declared_availability = declared_availability
    baseline._declared_availability = declared_availability
    try:
        yield
    finally:
        asof.declared_availability = original
        baseline._declared_availability = original_baseline
