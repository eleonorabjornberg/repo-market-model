"""Tests for `repo_model.splits`.

The splitter has one job -- keep the training window strictly behind the test
block by at least the longest release lag -- and exactly one way to fail at it
quietly. So these tests are weighted towards the gap: that it is measured in
calendar days rather than rows, that it drops the rows it is supposed to drop
and no others, that a gap too small to cover the lag is visibly different from
one that covers it, and that the module's own look-ahead guard fires when fed a
fold that violates it.

The contract-level version of the purge test lives in `tests/test_contract.py`;
it runs against the sample panel and states the property the contract cares
about. What is here is the implementation's own coverage.
"""

import inspect
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.data import load_daily_panel
from repo_model.splits import (
    LookAheadError,
    SplitError,
    _assert_no_look_ahead,
    _folds_unchecked,
    rolling_origin,
)


SAMPLE_PANEL = Path(__file__).parents[1] / "data" / "sample" / "daily_market.csv"


# The lag a purge gap has to cover in these tests. Two days is enough to be
# violated by an ordinary Tuesday-to-Wednesday adjacency and satisfied by a
# Friday-to-Monday one, which is what makes the day/row distinction visible.
RELEASE_LAG_DAYS = 2


def reference_folds(dates, min_train, step, purge):
    """Brute-force rolling-origin folds, written to share nothing with `splits`.

    An oracle computed the same way as the implementation cannot catch an error
    the two have in common, so this deliberately avoids every mechanism the
    module uses. No `bisect`; a plain scan over every earlier row. No
    `timedelta` on either side of the comparison; a day count taken from the
    date difference, which is a third arithmetic form -- the module subtracts
    the lag from the block's date, the module's docstring states it as adding
    the lag to the row's date, and this asks how many days apart they are. All
    three agree only if the boundary is right.

    Returns `[]` where the module raises, so callers can assert both.
    """

    def survivors(test_start):
        keep = []
        for index in range(test_start):
            if (dates[test_start] - dates[index]).days > purge:
                keep.append(index)
        return keep

    count = len(dates)
    first_start = None
    for candidate in range(count):
        if len(survivors(candidate)) >= min_train:
            first_start = candidate
            break
    if first_start is None:
        return []

    folds = []
    start = first_start
    while start < count:
        stop = min(start + step, count)
        folds.append((tuple(survivors(start)), tuple(range(start, stop))))
        start += step
    return folds


def business_days(start: date, count: int):
    """`count` weekdays from `start` inclusive. Weekends are simply absent."""

    days = []
    cursor = start
    while len(days) < count:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


class FoldShapeTests(unittest.TestCase):
    """Structure: prefix training windows, tiled test blocks, time order."""

    def setUp(self):
        self.dates = business_days(date(2026, 1, 5), 40)
        # Unchecked on purpose: a construction bug must surface as a wrong fold
        # these tests can diff, not as a `LookAheadError` from the guard.
        self.folds = list(_folds_unchecked(self.dates, min_train=10, step=3, purge=0))

    def test_at_least_one_fold_is_produced(self):
        self.assertTrue(self.folds, msg="no folds; every other test here is vacuous")

    def test_training_window_is_a_prefix_and_expands(self):
        previous = 0
        for train, _ in self.folds:
            self.assertEqual(train, tuple(range(len(train))))
            self.assertGreaterEqual(len(train), previous)
            previous = len(train)

    def test_first_fold_honours_min_train(self):
        train, _ = self.folds[0]
        self.assertGreaterEqual(len(train), 10)

    def test_test_blocks_tile_the_tail_without_overlap_or_gaps(self):
        blocks = [test for _, test in self.folds]
        for test in blocks:
            self.assertEqual(test, tuple(range(test[0], test[-1] + 1)))
        flattened = [index for test in blocks for index in test]
        self.assertEqual(flattened, sorted(flattened))
        self.assertEqual(len(flattened), len(set(flattened)), msg="test blocks overlap")
        self.assertEqual(
            flattened,
            list(range(blocks[0][0], len(self.dates))),
            msg="test blocks skip or duplicate observations",
        )

    def test_folds_arrive_in_time_order(self):
        opens = [self.dates[test[0]] for _, test in self.folds]
        self.assertEqual(opens, sorted(opens))
        self.assertEqual(len(opens), len(set(opens)))

    def test_blocks_are_step_sized_except_a_short_final_block(self):
        sizes = [len(test) for _, test in self.folds]
        self.assertTrue(all(size == 3 for size in sizes[:-1]))
        self.assertIn(sizes[-1], (1, 2, 3))

    def test_a_final_partial_block_is_still_yielded(self):
        # 21 rows, min_train 10, step 4: whatever the tail length, the last
        # observation must be scored rather than dropped for not filling a block.
        dates = business_days(date(2026, 1, 5), 21)
        folds = list(_folds_unchecked(dates, min_train=10, step=4, purge=0))
        self.assertEqual(folds[-1][1][-1], len(dates) - 1)


class PurgeGapTests(unittest.TestCase):
    """The gap itself: size, units, and what it removes."""

    def setUp(self):
        self.dates = business_days(date(2026, 1, 5), 40)

    def test_every_fold_clears_the_gap(self):
        for purge in (0, 1, 2, 5, 10):
            for train, test in _folds_unchecked(self.dates, 10, 3, purge):
                last_train = self.dates[train[-1]]
                first_test = self.dates[test[0]]
                self.assertLess(
                    last_train + timedelta(days=purge),
                    first_test,
                    msg=f"purge={purge}: {last_train} -> {first_test} is inside the gap",
                )

    def test_purge_drops_the_rows_inside_the_gap_and_no_others(self):
        purge = RELEASE_LAG_DAYS
        for train, test in _folds_unchecked(self.dates, 10, 3, purge):
            first_test = self.dates[test[0]]
            # Everything between the training window and the block is dropped
            # precisely because it sits inside the gap.
            for dropped in range(len(train), test[0]):
                self.assertGreaterEqual(
                    self.dates[dropped] + timedelta(days=purge),
                    first_test,
                    msg=f"row {dropped} was dropped but clears the gap",
                )
            # And the last kept row clears it, so nothing eligible was thrown away.
            self.assertLess(self.dates[train[-1]] + timedelta(days=purge), first_test)

    def test_a_zero_gap_leaks_where_the_correct_gap_does_not(self):
        """The test that gives the rest of this class its power.

        With no gap, training ends the business day before the block opens --
        one calendar day, inside a two-day release lag, so a value stamped with
        the last training date is not yet observable when the block opens. With
        the gap set to the lag, no fold is in that position.
        """

        leaky = [
            (self.dates[train[-1]], self.dates[test[0]])
            for train, test in _folds_unchecked(self.dates, 10, 3, purge=0)
        ]
        self.assertTrue(
            any(
                (first_test - last_train).days <= RELEASE_LAG_DAYS
                for last_train, first_test in leaky
            ),
            msg="a zero gap leaked nothing on this panel; the comparison has no power",
        )

        purged = [
            (self.dates[train[-1]], self.dates[test[0]])
            for train, test in _folds_unchecked(self.dates, 10, 3, purge=RELEASE_LAG_DAYS)
        ]
        for last_train, first_test in purged:
            self.assertGreater(
                (first_test - last_train).days,
                RELEASE_LAG_DAYS,
                msg=f"{last_train} -> {first_test} does not clear a {RELEASE_LAG_DAYS}-day lag",
            )

    def test_the_gap_is_calendar_days_not_rows(self):
        """A weekend is three calendar days across one row boundary.

        Under a row-counted purge the Friday before a Monday block would be
        dropped exactly like a Tuesday before a Wednesday block. Under a
        day-counted one it survives, because three days already exceed the lag.
        Assert the survival, which a row-counted implementation cannot produce.
        """

        dates = business_days(date(2026, 1, 5), 20)
        folds = list(_folds_unchecked(dates, min_train=5, step=1, purge=RELEASE_LAG_DAYS))
        weekend_blocks = [
            (train, test)
            for train, test in folds
            if test[0] > 0
            and dates[test[0]].weekday() == 0
            and (dates[test[0]] - dates[test[0] - 1]).days == 3
        ]
        self.assertTrue(weekend_blocks, msg="panel has no weekend boundary to test")
        for train, test in weekend_blocks:
            self.assertEqual(
                train[-1],
                test[0] - 1,
                msg="the Friday before a Monday block was purged unnecessarily",
            )

    def test_a_larger_gap_never_keeps_more_training_rows(self):
        sizes = {}
        for purge in (0, 1, 2, 3, 5):
            folds = list(_folds_unchecked(self.dates, 10, 1, purge))
            sizes[purge] = {test[0]: len(train) for train, test in folds}
        for smaller, larger in ((0, 1), (1, 2), (2, 3), (3, 5)):
            shared = set(sizes[smaller]) & set(sizes[larger])
            self.assertTrue(shared, msg="no shared test block to compare across gaps")
            for start in shared:
                self.assertLessEqual(sizes[larger][start], sizes[smaller][start])


class ReferenceOracleTests(unittest.TestCase):
    """The splitter against a brute-force reference, on the real sample panel.

    Every other test here states a property. A property test can only catch
    what it thought to ask about; this one compares the whole fold sequence --
    survivor sets, block boundaries, fold count and order -- against an
    independent construction, so a survivor set that is wrong in a way nobody
    anticipated still shows up, as a diff.
    """

    # Chosen to exercise short and long gaps, unit and multi-day blocks, a gap
    # of zero, and a gap wide enough that the module refuses to split at all.
    CASES = [
        (5, 1, 0),
        (10, 3, 0),
        (10, 1, 2),
        (10, 3, 2),
        (8, 4, 4),
        (12, 2, 1),
        (5, 7, 3),
        (10, 3, 10),
        (10, 2, 400),
    ]

    def setUp(self):
        self.dates = [row.date for row in load_daily_panel(SAMPLE_PANEL)]

    def test_folds_match_the_reference_on_the_sample_panel(self):
        exercised = 0
        for min_train, step, purge in self.CASES:
            expected = reference_folds(self.dates, min_train, step, purge)
            with self.subTest(min_train=min_train, step=step, purge=purge):
                if not expected:
                    # The reference found no fold; the module must say so.
                    with self.assertRaisesRegex(SplitError, "yield no fold"):
                        list(_folds_unchecked(self.dates, min_train, step, purge))
                    continue
                actual = list(_folds_unchecked(self.dates, min_train, step, purge))
                self.assertEqual(actual, expected)
                exercised += 1
        self.assertEqual(
            exercised,
            len(self.CASES) - 1,
            msg="a case silently produced no folds; the comparison is thinner than it looks",
        )

    def test_the_reference_disagrees_with_a_deliberately_wrong_gap(self):
        """Guards the oracle: it must be able to tell gaps apart at all.

        If `reference_folds` ignored `purge`, the comparison above would pass
        against an implementation that ignored it too.
        """

        two = reference_folds(self.dates, 10, 3, 2)
        zero = reference_folds(self.dates, 10, 3, 0)
        self.assertNotEqual(two, zero)
        off_by_one = reference_folds(self.dates, 10, 3, 1)
        self.assertNotEqual(two, off_by_one, msg="oracle cannot see a one-day error")

    def test_the_public_entry_point_yields_the_constructed_folds(self):
        """The guard passes clean folds through rather than reshaping them.

        Content is tested against `_folds_unchecked`; this is what ties that
        coverage to what callers actually receive.
        """

        for min_train, step, purge in [(10, 3, 0), (10, 3, 2), (5, 1, 4)]:
            with self.subTest(min_train=min_train, step=step, purge=purge):
                self.assertEqual(
                    list(rolling_origin(self.dates, min_train, step, purge)),
                    list(_folds_unchecked(self.dates, min_train, step, purge)),
                )


class PurgeIsRequiredTests(unittest.TestCase):
    """`purge` must be supplied deliberately; a silent default is the bug."""

    def test_signature_declares_no_default_for_purge(self):
        parameter = inspect.signature(rolling_origin).parameters["purge"]
        self.assertIs(
            parameter.default,
            inspect.Parameter.empty,
            msg="purge acquired a default; a silent gap is the failure this prevents",
        )

    def test_omitting_purge_is_a_type_error(self):
        with self.assertRaises(TypeError):
            rolling_origin(business_days(date(2026, 1, 5), 20), 10, 3)

    def test_none_is_rejected_rather_than_treated_as_no_gap(self):
        with self.assertRaisesRegex(SplitError, "purge must be an int"):
            rolling_origin(business_days(date(2026, 1, 5), 20), 10, 3, None)

    def test_a_float_gap_is_rejected(self):
        with self.assertRaisesRegex(SplitError, "purge must be an int"):
            rolling_origin(business_days(date(2026, 1, 5), 20), 10, 3, 2.0)

    def test_a_boolean_gap_is_rejected(self):
        # `True` is an int and would silently mean a one-day gap.
        with self.assertRaisesRegex(SplitError, "purge must be an int"):
            rolling_origin(business_days(date(2026, 1, 5), 20), 10, 3, True)

    def test_a_negative_gap_is_rejected(self):
        with self.assertRaisesRegex(SplitError, "non-negative"):
            rolling_origin(business_days(date(2026, 1, 5), 20), 10, 3, -1)

    def test_zero_is_accepted_when_chosen_explicitly(self):
        folds = list(rolling_origin(business_days(date(2026, 1, 5), 20), 10, 3, 0))
        self.assertTrue(folds)


class InvalidInputTests(unittest.TestCase):
    """Arguments are validated eagerly, not on first iteration."""

    def test_unsorted_dates_are_rejected(self):
        dates = business_days(date(2026, 1, 5), 20)
        dates[4], dates[5] = dates[5], dates[4]
        with self.assertRaisesRegex(SplitError, "strictly ascending"):
            rolling_origin(dates, 10, 3, 0)

    def test_duplicate_dates_are_rejected(self):
        dates = business_days(date(2026, 1, 5), 20)
        dates[5] = dates[4]
        with self.assertRaisesRegex(SplitError, "strictly ascending"):
            rolling_origin(dates, 10, 3, 0)

    def test_empty_panel_is_rejected(self):
        with self.assertRaisesRegex(SplitError, "empty panel"):
            rolling_origin([], 10, 3, 0)

    def test_non_positive_min_train_and_step_are_rejected(self):
        dates = business_days(date(2026, 1, 5), 20)
        with self.assertRaisesRegex(SplitError, "min_train must be at least 1"):
            rolling_origin(dates, 0, 3, 0)
        with self.assertRaisesRegex(SplitError, "step must be at least 1"):
            rolling_origin(dates, 10, 0, 0)

    def test_validation_happens_before_iteration(self):
        with self.assertRaises(SplitError):
            rolling_origin([], 10, 3, 0)

    def test_too_short_a_panel_raises_rather_than_yielding_nothing(self):
        dates = business_days(date(2026, 1, 5), 8)
        with self.assertRaisesRegex(SplitError, "yield no fold"):
            list(rolling_origin(dates, min_train=10, step=1, purge=0))

    def test_a_gap_wider_than_the_panel_raises(self):
        dates = business_days(date(2026, 1, 5), 20)
        with self.assertRaisesRegex(SplitError, "yield no fold"):
            list(rolling_origin(dates, min_train=10, step=1, purge=365))


class LookAheadGuardTests(unittest.TestCase):
    """The module's own guard, fed folds the generator would never build.

    `rolling_origin` cannot produce these, which is the point: the guard exists
    to catch a future edit that can. Driving it directly is the only way to show
    it still fires.
    """

    def setUp(self):
        self.dates = business_days(date(2026, 1, 5), 20)

    def test_a_fold_inside_the_gap_is_rejected(self):
        # Training ends Thursday, the block opens Friday: one calendar day
        # against a two-day gap.
        with self.assertRaisesRegex(LookAheadError, "inside the 2-day purge gap"):
            _assert_no_look_ahead(self.dates, tuple(range(9)), (9, 10), 2, 0)

    def test_a_training_row_at_or_after_the_block_is_rejected(self):
        with self.assertRaisesRegex(LookAheadError, "not strictly before"):
            _assert_no_look_ahead(self.dates, tuple(range(12)), (10, 11), 0, 0)

    def test_a_training_window_that_is_not_a_prefix_is_rejected(self):
        with self.assertRaisesRegex(LookAheadError, "not the prefix"):
            _assert_no_look_ahead(self.dates, (2, 3, 4), (10, 11), 0, 0)

    def test_overlapping_test_blocks_are_rejected(self):
        with self.assertRaisesRegex(LookAheadError, "overlapping the previous block"):
            _assert_no_look_ahead(self.dates, tuple(range(10)), (10, 11), 0, 12)

    def test_empty_windows_are_rejected(self):
        with self.assertRaisesRegex(SplitError, "empty training window"):
            _assert_no_look_ahead(self.dates, (), (10, 11), 0, 0)
        with self.assertRaisesRegex(SplitError, "empty test block"):
            _assert_no_look_ahead(self.dates, tuple(range(10)), (), 0, 0)

    def test_a_clean_fold_passes(self):
        _assert_no_look_ahead(self.dates, tuple(range(10)), (13, 14), 2, 0)


if __name__ == "__main__":
    unittest.main()
