"""The end of the exploratory window: one constant for every exploratory screen (#684).

`docs/decisions/lockbox.md` opened the near-blind tier (2026-01-01 to 2026-09-03) on 2026-10-05, so its days are
ordinary history. An exploratory screen may therefore read them, as development days: nothing computed on them is
a verdict, and none of it may be presented as out-of-sample evidence for a registered candidate (scoring protocol
v1, #640). The blind tier (every day after 2026-09-03) stays locked.

`EXPLORATORY_END` is the last day such a screen reads. `require_exploratory_window` refuses a day after it, and a
day the lockbox itself still locks, with `LookAheadError`.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from .lockbox import require_unlocked
from .splits import LookAheadError

__all__ = ["EXPLORATORY_END", "NEAR_BLIND_START", "panel_end", "require_exploratory_window"]

#: The last day of the opened near-blind tier; the blind tier starts the day after.
EXPLORATORY_END = date(2026, 9, 3)
#: The first day of the 2026 column: the days the screens read since #684, kept apart so that a figure on 2018-2025 can be compared with earlier pages.
NEAR_BLIND_START = date(2026, 1, 1)


def require_exploratory_window(days: Iterable[date], *, where: str) -> None:
    """Refuse a day after `EXPLORATORY_END`, or one in a tier that is still locked.

    Raises:
        LookAheadError: naming the first offending day.
    """

    days = sorted(days)
    for day in days:
        if day > EXPLORATORY_END:
            raise LookAheadError(
                f"{where}: day {day} is after the exploratory end {EXPLORATORY_END}; the blind tier "
                f"stays shut (docs/decisions/lockbox.md)"
            )
    require_unlocked(days, where=where)


def panel_end(value: Optional[str], default: date, *, where: str) -> date:
    """The last day a scratch-panel command keeps: `default` (the command's own end) unless `--end` names a day.

    A day after `EXPLORATORY_END`, or in a tier that is still locked, is refused (`require_exploratory_window`).
    The default is the command's published behaviour, so a run without `--end` is unchanged (#684).
    """

    end = default if value is None else date.fromisoformat(value)
    require_exploratory_window([end], where=where)
    return end
