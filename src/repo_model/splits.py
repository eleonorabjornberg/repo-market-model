"""Purged rolling-origin splitting for the daily panel.

The contract (`AGENT_CONTRACT.md`, "The splitter interface") specifies::

    rolling_origin(dates, min_train, step, purge) -> yields (train_idx, test_idx)

Random splits are prohibited and there is no configuration flag that enables
them. This module implements the one permitted scheme.

Which holdout this is
---------------------

`AGENT_CONTRACT.md`, "Two holdout roles", names two and this module produces
exactly one of them: the **scoring holdout**, where crisis dates are excluded
from the headline metric but are available for training once they are in the
past. That is the deployable model -- it is trained the way the deployed one
would be, on everything known at the cutoff.

The other role, the **knowledge holdout** -- crises stripped from training
entirely, scored once per window as an extrapolation check -- is produced by
`repo_model.event_eval`, and the contract says so in as many words: "Produced
by event_eval, not by a splitter flag." No argument here yields it and none
should be added. The reason is structural rather than stylistic: training is an
expanding prefix, so a fold that scores a late crisis has already trained on
every earlier one, and no setting of `min_train`, `step` or `purge` changes
that. A flag purporting to give the knowledge holdout from here would produce
a fold contaminated by earlier events while being labelled as though it were
not, which is worse than not offering it. The two numbers are never averaged
together, so they are never produced by one call.

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

`purge` is the release lag of the slowest field in the feature set. A release
lag is a duration, so the gap that covers it is a duration too. A training row
survives only if

    dates[i] + purge < dates[test_start]

strictly. A field observed at `ref_date` i and published `purge` days later is
first observable on ``dates[i] + purge``; if that date falls on or after the
test block opens, the training row carries information the forecaster could not
have had, and the row is dropped.

Counting dropped *rows* instead would not be unsafe on the panel as it stands,
and it is worth being exact about why. `repo_model.data` loads one row per
business date, so consecutive rows are at least one calendar day apart and
dropping k rows always leaves a gap of at least k + 1 days. Here a row count
can only ever purge too much, never too little. What it costs is training data:
a row-counted gap of two drops the Thursday *and* the Friday before a Monday
block, even though that Friday already sits three calendar days ahead of the
block -- four, when a holiday Monday pushes it out. A day-counted gap of two
keeps that Friday, and drops the Thursday before a Friday block, which is one
calendar day away and genuinely inside the lag.

Row counting stops being merely wasteful and becomes wrong the moment two rows
can share a date -- which is precisely the schema the contract is aiming at.
The long point-in-time panel (`series_id`, `ref_date`, `available_at`,
`vintage_id`) puts many series on one `ref_date`, and a revision appends
another row at a `ref_date` already present. There, k dropped rows can span
zero calendar days, and a row-counted gap degenerates to no gap at all without
changing shape or raising anything. Counting days now means this module does
not have to be revisited, or re-audited, when that panel lands.

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


__all__ = [
    "Fold",
    "LookAheadError",
    "SplitError",
    "clears_purge",
    "ensure_strictly_ascending",
    "require_purge_days",
    "rolling_origin",
]


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


def clears_purge(row_date: date, opens: date, purge: int) -> bool:
    """Is a row dated `row_date` eligible to train for a window opening `opens`?

    The one definition of the purge boundary in this project, but the two
    callers reach it differently and it is worth being exact about that.
    `repo_model.event_eval` selects its training rows with this function, so a
    change here changes what it trains on. `rolling_origin` finds its prefix
    with `bisect` on the equivalent boundary date and then states the boundary
    through this function in `_assert_no_look_ahead`. So tightening this
    comparison makes the splitter's guard fire on folds `_train_end` still
    builds -- the disagreement surfaces. Loosening it does not change the
    splitter's folds at all; it only makes the guard stop objecting, and what
    defends that direction is the reference oracle in `tests/test_splits.py`.

    A row observed at `row_date` and published `purge` days later is first
    observable on ``row_date + purge``. It is eligible only if that falls
    strictly before the window opens -- on the day itself the value is not yet
    in hand when the window starts, so the comparison is `<`, not `<=`.
    """

    return row_date + timedelta(days=purge) < opens


def ensure_strictly_ascending(dates: Sequence[date], label: str = "dates") -> None:
    """Reject a panel whose dates repeat or go backwards."""

    for index in range(1, len(dates)):
        if dates[index] <= dates[index - 1]:
            raise SplitError(
                f"{label} must be strictly ascending and unique; "
                f"{dates[index]} at position {index} follows {dates[index - 1]}"
            )


def require_purge_days(purge: int) -> None:
    """Reject anything that is not a deliberate non-negative day count.

    `bool` is an `int`, and a `True` that means "one day" is a typo. `None` is
    rejected rather than read as "no gap": a silent default is the failure the
    purge exists to prevent, and that reasoning is the same for the event
    evaluator as for the splitter.
    """

    if isinstance(purge, bool) or not isinstance(purge, int):
        raise SplitError(f"purge must be an int, got {purge!r}")
    if purge < 0:
        raise SplitError(f"purge must be a non-negative number of days, got {purge}")


def rolling_origin(
    dates: Sequence[date],
    min_train: int,
    step: int,
    purge: int,
) -> Iterator[Fold]:
    """Yield purged rolling-origin folds over `dates`, earliest fold first.

    These are scoring-holdout folds. See "Which holdout this is" in the module
    docstring for what that does and does not certify.

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
    return _checked(ordered, min_train, step, purge)


def _validate_arguments(
    dates: Sequence[date],
    min_train: int,
    step: int,
    purge: int,
) -> None:
    if not dates:
        raise SplitError("cannot split an empty panel")
    ensure_strictly_ascending(dates)
    require_purge_days(purge)
    for name, value in (("min_train", min_train), ("step", step)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise SplitError(f"{name} must be an int, got {value!r}")
    if min_train < 1:
        raise SplitError(f"min_train must be at least 1, got {min_train}")
    if step < 1:
        raise SplitError(f"step must be at least 1, got {step}")


def _train_end(dates: Sequence[date], test_start: int, purge: int) -> int:
    """Rows before `test_start` that clear the purge gap, as a prefix length.

    A row survives iff ``dates[i] + purge < dates[test_start]``. Since `dates`
    ascends, the survivors are exactly the prefix `0..end - 1`.
    """

    boundary = dates[test_start] - timedelta(days=purge)
    return bisect_left(dates, boundary, 0, test_start)


def _folds_unchecked(
    dates: Sequence[date],
    min_train: int,
    step: int,
    purge: int,
) -> Iterator[Fold]:
    """Construct folds. No look-ahead checking -- that is `_checked`'s job.

    Kept separate so the two can be tested apart: a construction bug shows up
    here as a wrong fold that a test can inspect and diff, rather than as a
    `LookAheadError` from the guard intercepting it first. Nothing outside this
    module should call this; `rolling_origin` is the checked entry point.
    """

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

    for start in range(first_start, count, step):
        stop = min(start + step, count)
        yield tuple(range(_train_end(dates, start, purge))), tuple(range(start, stop))


def _checked(
    dates: Sequence[date],
    min_train: int,
    step: int,
    purge: int,
) -> Iterator[Fold]:
    """Every constructed fold, past the look-ahead guard."""

    previous_stop = 0
    for train, test in _folds_unchecked(dates, min_train, step, purge):
        _assert_no_look_ahead(dates, train, test, purge, previous_stop)
        previous_stop = test[-1] + 1
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
    # The gap itself: max(train) + purge < min(test), in calendar days. Stated
    # through `clears_purge` so `_train_end`'s bisect is checked against the
    # authoritative comparison on every fold rather than trusted to agree.
    if not clears_purge(dates[last_train], dates[first_test], purge):
        raise LookAheadError(
            f"training ends {dates[last_train]} and testing opens {dates[first_test]}, "
            f"which is inside the {purge}-day purge gap"
        )
    if first_test < previous_stop:
        raise LookAheadError(
            f"test block opens at {first_test}, overlapping the previous block "
            f"which ended at {previous_stop}"
        )
