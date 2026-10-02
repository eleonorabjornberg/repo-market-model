"""Per-quarter peak pressure in the quarter-end window (#140).

Drafted in `docs/decisions/quarter-end-window.md` for Eleonora's ruling. The
New York Fed reads month-end pressure as the maximum of a spread over the 5
business days centred on the month's last business day; this module reads the
quarter-end version on SOFR - IORB, one value per quarter, over
`data.quarter_end_window_days`.

Beside each realised peak it reports, for each model, the highest
P(spread > tau) the model gave on any day of the window, each probability the
one forecast for that day at its own as-of decision instant (as the walk-forward
backtest made it). It reports; it ranks nothing and scores nothing.

**The lockbox binds the table.** A window day after `end` is not read, and the
days it does read are checked by `lockbox.require_unlocked`, so a table read into
a locked tier raises `LookAheadError` rather than print a locked day's spread or
forecast (`docs/decisions/lockbox.md`). 2025 Q4's window ends on 2026-01-05,
so read to 2025-12-31 it stops two days short, and its row says so.

**Above a threshold is read on whole basis points**: a peak is above tau when
its spread rounded to whole bp is strictly above tau, so a peak exactly on
+5 bp is not above it (Eleonora's ruling of 2 October 2026 on #155).

Standard library only.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .data import QUARTER_END_WINDOW_BUSINESS_DAYS, quarter_end_window_days
from .lockbox import require_unlocked

__all__ = ["quarter_peak_table"]


def _quarters(first: Tuple[int, int], last: Tuple[int, int]) -> List[Tuple[int, int]]:
    if not (1 <= first[1] <= 4 and 1 <= last[1] <= 4):
        raise ValueError(f"a quarter is numbered 1 to 4, got {first} and {last}")
    if last < first:
        raise ValueError(f"the last quarter {last} is before the first {first}")
    out = []
    year, quarter = first
    while (year, quarter) <= last:
        out.append((year, quarter))
        year, quarter = (year, quarter + 1) if quarter < 4 else (year + 1, 1)
    return out


def _tau_key(tau: float) -> str:
    return f"{tau:g}"


def quarter_peak_table(
    spreads: Mapping[date, float],
    forecasts: Mapping[str, Mapping[float, Mapping[date, float]]],
    *,
    first: Tuple[int, int],
    last: Tuple[int, int],
    end: date,
    taus: Sequence[float],
) -> List[Dict[str, Any]]:
    """One row per quarter from `first` to `last`: the window's realised peak and each model's.

    Args:
        spreads: SOFR - IORB in bp, by day, from the panel.
        forecasts: model name -> tau -> day -> P(spread > tau), the forecast
            for that day.
        first, last: (year, quarter), inclusive.
        end: the last day read. Window days after it are counted in
            `window_days_after_end` and not read.
        taus: the thresholds, each present in every model's forecasts.

    Raises:
        LookAheadError: if a day read is in a locked tier of
            `metadata/lockbox.json`.
        ValueError: on a malformed quarter range, a missing threshold, or a
            window the market holiday table does not cover.
    """

    for name, by_tau in forecasts.items():
        for tau in taus:
            if tau not in by_tau:
                raise ValueError(f"{name} carries no forecast at {tau:g} bp")
    rows = []
    for year, quarter in _quarters(first, last):
        window = quarter_end_window_days(year, quarter)
        read = [day for day in window if day <= end]
        require_unlocked(read, where="quarter_peaks.quarter_peak_table")
        observed = [day for day in read if day in spreads]
        peak_day: Optional[date] = None
        if observed:
            peak_day = max(observed, key=lambda day: (float(spreads[day]), day))
        peak = None if peak_day is None else float(spreads[peak_day])
        model_peaks: Dict[str, Dict[str, Any]] = {}
        for name, by_tau in forecasts.items():
            model_peaks[name] = {}
            for tau in taus:
                days = [day for day in read if day in by_tau[tau]]
                best = max(days, key=lambda day: (by_tau[tau][day], day)) if days else None
                model_peaks[name][_tau_key(tau)] = {
                    "max": None if best is None else by_tau[tau][best],
                    "day": None if best is None else best.isoformat(),
                    "days_forecast": len(days),
                }
        rows.append(
            {
                "quarter": f"{year} Q{quarter}",
                "window": [day.isoformat() for day in window],
                "window_days_after_end": len(window) - len(read),
                "window_days_without_spread": len(read) - len(observed),
                "peak_bps": peak,
                "peak_day": None if peak_day is None else peak_day.isoformat(),
                # The window's centre is the day `quarter_end` marks.
                "peak_on_quarter_end": peak_day is not None
                and peak_day == window[QUARTER_END_WINDOW_BUSINESS_DAYS],
                "above": {
                    _tau_key(tau): (peak is not None and round(peak) > tau) for tau in taus
                },
                "forecast_peaks": model_peaks,
            }
        )
    return rows
