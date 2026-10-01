"""Tests for `repo_model.splits`.

What is left of the module after directive 05 (#50) retired the purged
rolling-origin splitter: the two exceptions every leakage guard raises, and the
ordering check the as-of rule, the backtests and the event evaluator share. The
fold grid itself is `repo_model.asof.fold_grid`, tested in `tests/test_asof.py`.
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import splits
from repo_model.splits import LookAheadError, SplitError, ensure_strictly_ascending


class ErrorTypeTests(unittest.TestCase):
    """`CLAUDE.md`: leakage guards raise `LookAheadError`, data guards `ValueError`."""

    def test_a_look_ahead_error_is_a_split_error_and_a_value_error(self):
        self.assertTrue(issubclass(LookAheadError, SplitError))
        self.assertTrue(issubclass(SplitError, ValueError))


class StrictlyAscendingTests(unittest.TestCase):
    def test_ascending_unique_dates_pass(self):
        ensure_strictly_ascending([date(2026, 1, 2), date(2026, 1, 5), date(2026, 1, 6)])

    def test_unsorted_dates_are_rejected_with_the_offending_position(self):
        with self.assertRaisesRegex(SplitError, "strictly ascending.*position 2"):
            ensure_strictly_ascending([date(2026, 1, 2), date(2026, 1, 6), date(2026, 1, 5)])

    def test_duplicate_dates_are_rejected(self):
        with self.assertRaisesRegex(SplitError, "strictly ascending"):
            ensure_strictly_ascending([date(2026, 1, 2), date(2026, 1, 2)])

    def test_the_label_names_what_was_checked(self):
        with self.assertRaisesRegex(SplitError, "^window dates must"):
            ensure_strictly_ascending([date(2026, 1, 2), date(2026, 1, 1)], "window dates")


class PurgeSplitterRetiredTests(unittest.TestCase):
    """The purge-rule splitter is gone, so nothing can score under it again."""

    def test_the_module_exports_no_purge_splitter(self):
        for name in ("rolling_origin", "clears_purge", "require_purge_days"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(splits, name))


if __name__ == "__main__":
    unittest.main()
