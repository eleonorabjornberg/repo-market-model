"""Purged rolling-origin splitting for the daily panel.

The contract (`AGENT_CONTRACT.md`, "The splitter interface") specifies::

    rolling_origin(dates, min_train, step, purge) -> yields (train_idx, test_idx)

Random splits are prohibited and there is no configuration flag that enables
them. This module implements the one permitted scheme.

Shape of a fold
---------------

Test blocks tile the panel tail in time order: block ``k`` is the ``step``
observations beginning where block ``k - 1`` ended, so no observation is scored
twice and none is skipped. Training is an expanding prefix, which is why
``step`` is both the block size and the stride -- an origin that advanced by
less than the block size would score the same day in two folds, and one that
advanced by more would silently discard evaluation data.

Why the gap is measured in days, not rows
-----------------------------------------

`purge` is the release lag of the slowest field in the feature set, and a
release lag is a duration. The panel is business-daily, so a row gap and a
calendar gap are not the same thing: the last training row before a weekend is
three calendar days from the next test row, and the last row before a holiday
weekend is four. Purging a fixed number of *rows* would therefore over-purge
across weekends and under-purge inside a week -- and under-purging is the
failure this module exists to prevent. So `purge` is an integer number of
calendar days, and a training row survives only if

    dates[i] + purge < dates[test_start]

strictly. A field observed at `ref_date` i and published `purge` days later is
first observable on `dates[i] + purge`; if that date falls on or after the test
block opens, the training row carries information the forecaster could not have
had, and the row is dropped.

Why `purge` has no default
--------------------------

A silent default is the exact failure mode this splitter exists to prevent: a
gap of zero looks like a working backtest and quietly reports the score of a
model that saw its own test period. So `purge` is required, and passing
something that is not an int -- `None` included -- is an error rather than a
fallback.

TODO(track-a): size `purge` from the registry instead of the caller. Once
`metadata/sources.json` declares a per-source ``"release_lag"`` -- the key
asserted by
``tests/test_contract.py::TargetSchemaTests::test_source_registry_declares_identities_and_structural_zeros``
-- add a helper here that resolves each field in the feature set to its source,
reads ``registry[source]["release_lag"]``, and returns the maximum as the purge
for that feature set. Callers then pass a feature set rather than a number and
cannot get the gap wrong by hand. Until that key exists there is nothing to
read, and guessing a lag is worse than requiring one.
"""

from __future__ import annotations

from bisect import bisect_left
from datetime import date, timedelta
from typing import Iterator, Sequence, Tuple


__all__ = ["Fold", "LookAheadError", "SplitError", "rolling_origin"]


#: ``(train_indices, test_indices)``, both index into the `dates` passed in.
Fold = Tuple[Tuple[int, ...], Tuple[int, ...]]


class SplitError(ValueError):
    """Raised when a requested split is malformed or impossible."""


class LookAheadError(SplitError):
    """Raised when a fold would let the training window see the test period.

    This is a raise rather than an `assert` on purpose. The checks it guards
    are the only thing separating an honest backtest from a flattering one, and
    `python -O` strips `assert`; a leakage guard that disappears under an
    optimisation flag is not a guard.
    """


def rolling_origin(
    dates: Sequence[date],
    min_train: int,
    step: int,
    purge: int,
) -> Iterator[Fold]:
    """Yield purged rolling-origin folds over `dates`, earliest fold first.

    Args:
        dates: the panel's `ref_date` column, strictly ascending and unique.
        min_train: training rows the first fold must have *after* purging.
        step: observations per test block, and the stride between blocks.
        purge: calendar days that must separate the last training row from the
            first test row. Required; size it to the longest release lag of any
            field in the feature set. Zero is legal but must be chosen, not
            defaulted.

    Yields:
        `(train_indices, test_indices)` as tuples of positions into `dates`.
        `train_indices` is always the prefix `0..len(train) - 1`.

    Raises:
        SplitError: on a malformed panel or arguments, or when `dates` is too
            short to produce a single fold under `min_train` and `purge`.
        LookAheadError: if a constructed fold violates the purge gap or the
            ordering invariants. Reaching this means a bug in this module, not
            bad input.
    """

    ordered = list(dates)
    _validate_arguments(ordered, min_train, step, purge)
    return _iter_folds(ordered, min_train, step, purge)


def _validate_arguments(
    dates: Sequence[date],
    min_train: int,
    step: int,
    purge: int,
) -> None:
    if not dates:
        raise SplitError("cannot split an empty panel")
    for index in range(1, len(dates)):
        if dates[index] <= dates[index - 1]:
            raise SplitError(
                "dates must be strictly ascending and unique; "
                f"{dates[index]} at position {index} follows {dates[index - 1]}"
            )
    # `bool` is an `int`, and `rolling_origin(dates, 10, 1, True)` meaning a
    # one-day gap is a typo, not an intention.
    for name, value in (("min_train", min_train), ("step", step), ("purge", purge)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise SplitError(f"{name} must be an int, got {value!r}")
    if min_train < 1:
        raise SplitError(f"min_train must be at least 1, got {min_train}")
    if step < 1:
        raise SplitError(f"step must be at least 1, got {step}")
    if purge < 0:
        raise SplitError(f"purge must be a non-negative number of days, got {purge}")


def _train_end(dates: Sequence[date], test_start: int, purge: int) -> int:
    """Rows before `test_start` that clear the purge gap, as a prefix length.

    A row survives iff ``dates[i] + purge < dates[test_start]``. Since `dates`
    ascends, the survivors are exactly the prefix `0..end - 1`.
    """

    boundary = dates[test_start] - timedelta(days=purge)
    return bisect_left(dates, boundary, 0, test_start)


def _iter_folds(
    dates: Sequence[date],
    min_train: int,
    step: int,
    purge: int,
) -> Iterator[Fold]:
    count = len(dates)
    first_start = None
    for candidate in range(count):
        if _train_end(dates, candidate, purge) >= min_train:
            first_start = candidate
            break
    if first_start is None:
        raise SplitError(
            f"{count} observations from {dates[0]} to {dates[-1]} yield no fold "
            f"with {min_train} training rows behind a {purge}-day purge gap"
        )

    previous_stop = 0
    for start in range(first_start, count, step):
        stop = min(start + step, count)
        train = tuple(range(_train_end(dates, start, purge)))
        test = tuple(range(start, stop))
        _assert_no_look_ahead(dates, train, test, purge, previous_stop)
        previous_stop = stop
        yield train, test


def _assert_no_look_ahead(
    dates: Sequence[date],
    train: Tuple[int, ...],
    test: Tuple[int, ...],
    purge: int,
    previous_stop: int,
) -> None:
    """Check a fold before handing it out. Every check is a leak if it fires."""

    if not train:
        raise SplitError("fold has an empty training window")
    if not test:
        raise SplitError("fold has an empty test block")
    if train[0] != 0 or train[-1] != len(train) - 1:
        raise LookAheadError(f"training window is not the prefix 0..{len(train) - 1}")

    last_train, first_test = train[-1], test[0]
    if last_train >= first_test:
        raise LookAheadError(
            f"training row {last_train} is not strictly before test row {first_test}"
        )
    # The gap itself: max(train) + purge < min(test), in calendar days.
    if not dates[last_train] + timedelta(days=purge) < dates[first_test]:
        raise LookAheadError(
            f"training ends {dates[last_train]} and testing opens {dates[first_test]}, "
            f"which is inside the {purge}-day purge gap"
        )
    if first_test < previous_stop:
        raise LookAheadError(
            f"test block opens at {first_test}, overlapping the previous block "
            f"which ended at {previous_stop}"
        )
