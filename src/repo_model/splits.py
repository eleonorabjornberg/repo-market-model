"""The evaluation's shared errors, and the one ordering check every path makes.

This module used to hold `rolling_origin`, the purged rolling-origin splitter,
and `clears_purge`, its gap rule. The as-of rule (`docs/decisions/information-set.md`)
replaced the purge: what a forecast reads at its decision instant is decided
per field by `repo_model.asof`, and the backtests in `repo_model.baseline` walk
their own expanding refit blocks under that rule. The splitter was kept until the
re-score of directive 03 had compared old against new, and was removed after it
(directive 05, #50). Its reasoning, and the records scored with it, are in
`docs/runs/archive/pre-asof/` and in git history.

What is left is what the rest of the package imports:

* `SplitError`, a `ValueError` for a split or evaluation that is malformed;
* `LookAheadError`, its subclass for a leak. Leakage guards raise it, never
  `assert`: `python -O` strips an `assert`, and a leakage guard that
  disappears under an optimisation flag is not a guard;
* `ensure_strictly_ascending`, which rejects a panel whose dates repeat or go
  backwards.

Random splits are prohibited, and no flag enables them.
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
