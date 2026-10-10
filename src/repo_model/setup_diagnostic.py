"""The setup diagnostic (#480): does the evaluation setup itself explain the misses?

Reported-only measurements on the pressure-day judge of #375 (as amended under #407). They change no bar, no
declaration, no model and no published figure, and they write nothing into `docs/runs/`. The declaration is
`metadata/setup_diagnostic.json`; the functions here are pure and stdlib-only, and `scripts/setup_diagnostic.py`
drives them over the published panel.

Mutation record
---------------
The one guard here is `require_window`: no day after the declared last scored day is read
(`docs/decisions/lockbox.md`). Applied in a scratch copy, the unmutated suite green before and after:

1. In `require_window`, replace `if late:` with `if False:`. Killed:
   `tests/test_setup_diagnostic.py::WindowGuard.test_a_day_after_the_last_scored_day_is_refused`, with
   `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .data import exceeds_bp
from .splits import LookAheadError


def require_window(days: Sequence[date], last: date) -> None:
    """Refuse any day after `last`, the last day a comparison may score.

    Raises:
        LookAheadError: if a day is after `last` (`docs/decisions/lockbox.md`).
    """

    late = [day for day in days if day > last]
    if late:
        raise LookAheadError(
            f"{len(late)} day(s) from {min(late)} on are after the last scored day ({last}); "
            "no comparison reads a locked day"
        )


def episodes(
    days: Sequence[date], spreads: Sequence[float], scored: Sequence[date], *, tau: float, calm: int
) -> List[date]:
    """The scored days that open a pressure episode: above `tau` with `calm` calm panel days before.

    `days` and `spreads` are the panel's rows in order. A day is above `tau` on whole basis points,
    strictly (`data.exceeds_bp`). With `calm` = `pressure.ONSET_QUIET_DAYS` this is `pressure.onsets`.
    """

    if len(days) != len(spreads):
        raise ValueError("every panel day needs one spread")
    if calm < 1:
        raise ValueError("an episode needs at least one calm day before it")
    wanted = set(scored)
    above = [exceeds_bp(s, tau) for s in spreads]
    return [
        day
        for k, day in enumerate(days)
        if day in wanted and above[k] and k >= calm and not any(above[k - calm : k])
    ]


def compare(base: Sequence[date], other: Sequence[date]) -> Dict[str, List[date]]:
    """Which of `other`'s episodes `base` also has, and which appear or disappear against `base`."""

    b, o = set(base), set(other)
    return {"kept": sorted(b & o), "appear": sorted(o - b), "disappear": sorted(b - o)}


def training_counts(
    days: Sequence[date], spreads: Sequence[float], *, last: date, tau: float, calm: int
) -> Dict[str, Any]:
    """The pressure days and episodes inside the panel from its first day to `last`.

    This is what a refit with training end `last` has seen of the target. An episode needs `calm` panel days
    before it, so the panel's first days are never episodes.
    """

    inside = [k for k, day in enumerate(days) if day <= last]
    if not inside:
        raise ValueError(f"no panel day on or before {last}")
    end = inside[-1] + 1
    seen = episodes(days[:end], spreads[:end], days[:end], tau=tau, calm=calm)
    return {
        "first": days[0],
        "last": days[end - 1],
        "pressure_days": sum(1 for s in spreads[:end] if exceeds_bp(s, tau)),
        "onsets": len(seen),
    }


def refit_block(scored: Sequence[date], day: date, *, step: int) -> Dict[str, Any]:
    """The refit block of `step` scored days that holds `day`: its first and last index and first day."""

    index = list(scored).index(day)
    first = (index // step) * step
    return {"first_index": first, "last_index": min(first + step, len(scored)) - 1, "first": scored[first]}


def is_technical(change_bps: float) -> bool:
    """An IOER/IORB change that is not a multiple of 25 bp reads as a technical adjustment."""

    return round(change_bps) % 25 != 0


def iorb_changes(
    days: Sequence[date], iorb: Sequence[float], sofr: Sequence[float]
) -> List[Dict[str, Any]]:
    """Each day the administered rate moved, with the move and the spread shift it causes by itself.

    `mechanical_spread_shift_bps` is minus the move: SOFR - IORB falls by the move if SOFR does not follow.
    `sofr_move_bps` is what SOFR did the same day.
    """

    out = []
    for k in range(1, len(days)):
        move = round(100.0 * (iorb[k] - iorb[k - 1]))
        if move == 0:
            continue
        out.append(
            {
                "date": days[k],
                "from": iorb[k - 1],
                "to": iorb[k],
                "change_bps": move,
                "sofr_move_bps": round(100.0 * (sofr[k] - sofr[k - 1])),
                "mechanical_spread_shift_bps": -move,
                "technical": is_technical(move),
            }
        )
    return out


def quantiles(values: Sequence[float], probabilities: Sequence[float]) -> List[float]:
    """Linear-interpolation quantiles of a non-empty sample."""

    if not values:
        raise ValueError("no values")
    ordered = sorted(values)
    out = []
    for p in probabilities:
        position = p * (len(ordered) - 1)
        low = int(position)
        high = min(low + 1, len(ordered) - 1)
        out.append(ordered[low] + (ordered[high] - ordered[low]) * (position - low))
    return out


def _weekdays(first: date, last: date) -> List[date]:
    out, day = [], first
    while day <= last:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def window_integrity(
    days: Sequence[date],
    rows: Sequence[Mapping[str, Optional[float]]],
    episode: date,
    window: int,
    holidays: Sequence[date],
    daily_columns: Sequence[str],
    weekly_columns: Sequence[str],
    *,
    stale_calendar_days: int = 7,
    critical: Sequence[str] = ("sofr", "iorb"),
) -> Dict[str, Any]:
    """The panel in the `window` panel days before `episode`: gaps, blanks, repeats, stale weekly values.

    A gap is a weekday between the window's first and last panel day that is neither a panel day nor a
    holiday. A repeat is a daily column equal to the previous panel day's (how a forward fill reads). A weekly
    column is stale when its value has not changed for more than `stale_calendar_days`, counted to the
    decision-day row (the last row before the episode). The window blinds a model when the decision-day row
    has a blank in a `critical` column, a gap lies in the window, or a weekly column is stale.
    """

    before = [k for k, day in enumerate(days) if day < episode]
    if len(before) < 2:
        raise ValueError("a window needs at least two panel days before the episode")
    inside = before[-window:]
    decision = inside[-1]
    held = set(holidays)
    present = {days[k] for k in inside}
    gaps = [
        d.isoformat()
        for d in _weekdays(days[inside[0]], days[decision])
        if d not in present and d not in held
    ]
    blanks: Dict[str, List[str]] = {}
    repeats: Dict[str, List[str]] = {}
    for column in list(daily_columns) + list(weekly_columns):
        for k in inside:
            if rows[k].get(column) is None:
                blanks.setdefault(column, []).append(days[k].isoformat())
    for column in daily_columns:
        for k in inside:
            if k == 0 or rows[k].get(column) is None or rows[k - 1].get(column) is None:
                continue
            if rows[k][column] == rows[k - 1][column]:
                repeats.setdefault(column, []).append(days[k].isoformat())
    stale: Dict[str, int] = {}
    for column in weekly_columns:
        k = decision
        value = rows[k].get(column)
        while k > 0 and rows[k - 1].get(column) == value:
            k -= 1
        age = (days[decision] - days[k]).days
        if value is not None and age > stale_calendar_days:
            stale[column] = age
    critical_blank = any(rows[decision].get(c) is None for c in critical if c in rows[decision])
    return {
        "first": days[inside[0]].isoformat(),
        "decision_day": days[decision].isoformat(),
        "gaps": gaps,
        "blanks": blanks,
        "repeats": repeats,
        "stale_weekly": stale,
        "blinds_a_model": bool(critical_blank or gaps or stale),
    }


def revisions(
    observations: Sequence[date], first: Mapping[date, float], latest: Mapping[date, float]
) -> List[Dict[str, Any]]:
    """The observations whose first tracked vintage differs from the latest."""

    out = []
    for day in observations:
        if day in first and day in latest and first[day] != latest[day]:
            out.append({"date": day.isoformat(), "first": first[day], "latest": latest[day]})
    return out
