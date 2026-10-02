"""The locked final test period, enforced: no comparison scores a locked day.

`docs/decisions/lockbox.md` is the rule and `metadata/lockbox.json` its
declaration. Two tiers are held back from every model comparison: the
near-blind tier (2026-01-01 to 2026-09-03) and the blind tier (every day after
2026-09-03). Each tier carries an `opened` field that starts as `null`.

**What is guarded is the scored day, and only the scored day.** A model may be
trained on, and forecast from, whatever its as-of information set allows; what
it may not do is have a locked day count toward a score. `require_unlocked` is
called by every scoring entry point with the days it is about to score, before
any model is fitted, and raises `LookAheadError` naming the tier and the first
offending date. A forgotten end date is therefore a raised error, not a silent
leak.

**Opening is explicit.** A tier is opened only by setting its `opened` field in
the tracked declaration to the date it was opened and a reference to
Eleonora's ruling. Nothing else opens it: the scoring entry points take no
declaration argument, and no CLI flag or environment variable is read here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Optional, Tuple

from .data import DataContractError
from .splits import LookAheadError


__all__ = [
    "DEFAULT_LOCKBOX",
    "LockboxTier",
    "load_lockbox",
    "locked_tier",
    "locked_tiers",
    "require_unlocked",
]


#: The tracked declaration every scoring entry point reads.
DEFAULT_LOCKBOX = Path(__file__).parents[2] / "metadata" / "lockbox.json"


@dataclass(frozen=True)
class LockboxTier:
    """One locked period, inclusive at both ends; `end` is `None` when open-ended.

    `opened` is `None` while the tier is locked, and otherwise the date it was
    opened and the reference to the ruling that opened it.
    """

    name: str
    start: date
    end: Optional[date]
    opened: Optional[Tuple[date, str]]

    def contains(self, day: date) -> bool:
        return self.start <= day and (self.end is None or day <= self.end)


def _iso_date(value: object, where: str) -> date:
    if not isinstance(value, str):
        raise DataContractError(f"lockbox {where} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise DataContractError(f"lockbox {where} is not an ISO date: {value!r}") from exc


def _opened(value: object, where: str) -> Optional[Tuple[date, str]]:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"date", "ruling"}:
        raise DataContractError(
            f"lockbox {where}.opened must be null or an object with exactly "
            f"'date' and 'ruling'"
        )
    ruling = value["ruling"]
    if not isinstance(ruling, str) or not ruling.strip():
        raise DataContractError(
            f"lockbox {where}.opened.ruling must reference Eleonora's ruling"
        )
    return _iso_date(value["date"], f"{where}.opened.date"), ruling


def load_lockbox(path: Path = DEFAULT_LOCKBOX) -> Tuple[LockboxTier, ...]:
    """Load and validate the lockbox declaration, its tiers in date order.

    The tiers must be ascending and contiguous, each starting the day after the
    previous one ends, and only the last may be open-ended: a gap between two
    tiers would be a day the rule locks and the declaration does not.

    Raises:
        DataContractError: on a missing or malformed file.
    """

    try:
        declaration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataContractError(f"cannot load lockbox metadata: {exc}") from exc
    if not isinstance(declaration, dict):
        raise DataContractError("lockbox metadata must be an object")
    if isinstance(declaration.get("version"), bool) or declaration.get("version") != 1:
        raise DataContractError("lockbox metadata needs version 1")
    raw_tiers = declaration.get("tiers")
    if not isinstance(raw_tiers, list) or not raw_tiers:
        raise DataContractError("lockbox metadata needs a non-empty tiers list")

    tiers = []
    names = set()
    for position, raw in enumerate(raw_tiers):
        where = f"tiers[{position}]"
        if not isinstance(raw, dict) or set(raw) != {"name", "start", "end", "opened"}:
            raise DataContractError(
                f"lockbox {where} must be an object with exactly name, start, "
                f"end and opened"
            )
        name = raw["name"]
        if not isinstance(name, str) or not name or name in names:
            raise DataContractError(f"lockbox {where}.name must be a unique non-empty string")
        names.add(name)
        start = _iso_date(raw["start"], f"{where}.start")
        end = None if raw["end"] is None else _iso_date(raw["end"], f"{where}.end")
        if end is not None and end < start:
            raise DataContractError(f"lockbox {where} ends before it starts")
        if end is None and position != len(raw_tiers) - 1:
            raise DataContractError(f"lockbox {where}: only the last tier may be open-ended")
        if tiers and start != date.fromordinal(tiers[-1].end.toordinal() + 1):
            raise DataContractError(
                f"lockbox {where} must start the day after {tiers[-1].name} ends"
            )
        tiers.append(LockboxTier(name, start, end, _opened(raw["opened"], where)))
    return tuple(tiers)


def locked_tiers(path: Path = DEFAULT_LOCKBOX) -> Tuple[LockboxTier, ...]:
    """The tiers of the declaration at `path` that have not been opened, in date order.

    An opened tier is ordinary history and is not returned. For a descriptive
    page that shows locked days greyed and counts none of them (#141, ruling
    3); a scoring entry point calls `require_unlocked` instead.

    Raises:
        DataContractError: if the declaration is missing or malformed.
    """

    return tuple(tier for tier in load_lockbox(path) if tier.opened is None)


def locked_tier(day: date, tiers: Iterable[LockboxTier]) -> Optional[LockboxTier]:
    """The tier among `tiers` that holds `day`, or `None` if `day` is not locked."""

    return next((tier for tier in tiers if tier.contains(day)), None)


def require_unlocked(scored_days: Iterable[date], *, where: str) -> None:
    """Refuse to score a day that falls in a tier that has not been opened.

    Reads the tracked declaration (`DEFAULT_LOCKBOX`) on every call. `where`
    names the entry point, for the message.

    Raises:
        LookAheadError: naming the tier and the first offending date.
        DataContractError: if the declaration is missing or malformed.
    """

    # The module attribute, read at call time rather than bound as a default.
    locked = [tier for tier in load_lockbox(DEFAULT_LOCKBOX) if tier.opened is None]
    if not locked:
        return
    for day in sorted(scored_days):
        for tier in locked:
            if tier.contains(day):
                end = "open-ended" if tier.end is None else f"to {tier.end}"
                raise LookAheadError(
                    f"{where}: scored day {day} is in the locked {tier.name} tier "
                    f"({tier.start} {end}, docs/decisions/lockbox.md); a comparison "
                    f"scores only unlocked days, so end the run before "
                    f"{tier.start} or have the tier opened in metadata/lockbox.json"
                )
