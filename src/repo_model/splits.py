"""The error types every leakage guard raises, and the one ordering check.

The purged rolling-origin splitter that used to live here (`rolling_origin`,
`clears_purge`, `require_purge_days`) scored the records now archived in
`docs/runs/archive/pre-asof/`. Directive 03 (#27) re-scored every published
figure under the as-of rule, whose fold grid is `repo_model.asof.fold_grid`, and
directive 05 (#50) removed the splitter. What remains is shared by the as-of
rule, the backtests and the event evaluator:

- `SplitError`, raised when a requested split is malformed or impossible;
- `LookAheadError`, the leakage guard's exception, a `SplitError`;
- `ensure_strictly_ascending`, which refuses a panel whose dates repeat or go
  backwards.
"""

from __future__ import annotations

from datetime import date
from typing import Sequence


__all__ = [
    "LookAheadError",
    "SplitError",
    "ensure_strictly_ascending",
]


class SplitError(ValueError):
    """Raised when a requested split is malformed or impossible."""


class LookAheadError(SplitError):
    """Raised when a fold would let the training window see the test period.

    This is a raise rather than an `assert` on purpose. The checks it guards
    are the only thing separating an honest backtest from a flattering one, and
    `python -O` strips `assert`; a leakage guard that disappears under an
    optimisation flag is not a guard.
    """


def ensure_strictly_ascending(dates: Sequence[date], label: str = "dates") -> None:
    """Reject a panel whose dates repeat or go backwards."""

    for index in range(1, len(dates)):
        if dates[index] <= dates[index - 1]:
            raise SplitError(
                f"{label} must be strictly ascending and unique; "
                f"{dates[index]} at position {index} follows {dates[index - 1]}"
            )
