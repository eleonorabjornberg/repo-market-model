"""The day-of-month bucket of the target day, a calendar column (#1032, H5 step 2, Lens A of #958).

The spread's mean is lowest on the 19th to 23rd (about -5.4 to -6.6 bp, against -4.8 to -5.6 on the 6th to 14th and +1.3 on
the 31st; `docs/reviews/2026-10-19-five-lens/lens-A-repo-trader.md`). It is a level effect, not an onset effect, which is why
#631's screen of onsets could not see it. `dom_bucket` is the bucket of the calendar day of the month of a row's own date,
numbered 0 to 4 over `BUCKETS`.

**Read at the target day.** A bucket is a function of the date alone and is always known, like the columns of
`contract.CALENDAR_FEATURES`; `asof` rule 2 serves such a column from the target row. A one-step fit would train it a row off
(#914), so the column is declared in `target_day_columns.TARGET_DAY_COLUMNS` and `one_step_guard` refuses it there. Train it
on direct pairs (`training_pairs="direct"`).

**Off.** The column is not in `contract.CALENDAR_FEATURES`, whose bytes the final test freezes, and no published panel,
declaration or record reads it. `switched_on` serves it as a calendar column for one run, the way `scripts/net_settlement.py`
switches its columns on; `add_columns` writes it onto a scratch panel. Whether it joins a published declaration is a
publishing question and is Eleonora's.

Standard library only.
"""

from __future__ import annotations

import contextlib
from datetime import date
from typing import Iterator, List, Sequence
from unittest import mock

from .data import DailyObservation

__all__ = ["BUCKETS", "COLUMN", "add_columns", "bucket", "label", "switched_on"]

COLUMN = "dom_bucket"

#: The inclusive day-of-month range of each bucket, in order: the first week, the 6th to 14th, the 15th to 18th, the trough
#: (19th to 23rd), and the 24th to month end. Declared before any score (`metadata/dom_level_term_1032.json`).
BUCKETS = ((1, 5), (6, 14), (15, 18), (19, 23), (24, 31))


def bucket(day: date) -> float:
    """The bucket number (0 to 4) of `day`'s day of the month."""

    for number, (low, high) in enumerate(BUCKETS):
        if low <= day.day <= high:
            return float(number)
    raise ValueError(f"{day} has no day-of-month bucket")  # unreachable for a real date


def label(day: date) -> str:
    """The bucket of `day` as 'first-last', for a result page."""

    low, high = BUCKETS[int(bucket(day))]
    return f"{low}-{high}"


def add_columns(rows: Sequence[DailyObservation]) -> List[DailyObservation]:
    """`rows` with `COLUMN` added: each row's value is the bucket of its own date, never of another row's.

    Raises:
        ValueError: a row already carries the column (it would be overwritten silently).
    """

    out: List[DailyObservation] = []
    for row in rows:
        if COLUMN in row.values:
            raise ValueError(f"{row.date} already carries {COLUMN!r}")
        values = dict(row.values)
        values[COLUMN] = bucket(row.date)
        out.append(DailyObservation(row.date, values))
    return out


@contextlib.contextmanager
def switched_on() -> Iterator[None]:
    """`COLUMN` served as a calendar column (rule 2 of `asof.py`) for this run only."""

    from . import asof, contract

    extended = contract.CALENDAR_FEATURES | {COLUMN}
    with mock.patch.object(contract, "CALENDAR_FEATURES", extended), mock.patch.object(asof, "CALENDAR_FEATURES", extended):
        yield
