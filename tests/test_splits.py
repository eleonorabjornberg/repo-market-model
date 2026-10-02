"""What is left of `repo_model.splits`: its errors and the ordering check.

This module tested `rolling_origin`, the purged rolling-origin splitter, until
directive 05 (#50) removed it. The as-of rule had replaced the purge, and after
the re-score of directive 03 nothing in `src/` called the splitter. Its tests
went with it; they are in git history. What the package still imports from
`repo_model.splits` is tested here.
"""

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from repo_model import splits
from repo_model.splits import LookAheadError, SplitError, ensure_strictly_ascending


class ErrorHierarchyTests(unittest.TestCase):
    """Leakage guards raise `LookAheadError`, and callers may catch `ValueError`.

    `cli` reports a `SplitError` as a usage error because it is a `ValueError`,
    and a `LookAheadError` is a `SplitError` so that one `except` clause sees
    both. A `LookAheadError` that stopped being a `ValueError` would escape the
    CLI's handling as a traceback.
    """

    def test_a_look_ahead_error_is_a_split_error_and_a_value_error(self):
        self.assertTrue(issubclass(LookAheadError, SplitError))
        self.assertTrue(issubclass(SplitError, ValueError))

    def test_the_module_exports_only_what_the_package_imports(self):
        self.assertEqual(
            sorted(splits.__all__),
            ["LookAheadError", "SplitError", "ensure_strictly_ascending"],
        )
        for removed in ("rolling_origin", "clears_purge", "require_purge_days"):
            with self.subTest(removed=removed):
                self.assertFalse(hasattr(splits, removed))


class StrictlyAscendingTests(unittest.TestCase):
    def test_ascending_unique_dates_pass(self):
        ensure_strictly_ascending([date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 9)])
        ensure_strictly_ascending([])

    def test_a_repeated_date_is_rejected(self):
        with self.assertRaisesRegex(SplitError, "position 1"):
            ensure_strictly_ascending([date(2026, 1, 5), date(2026, 1, 5)])

    def test_a_date_that_goes_backwards_is_rejected_with_its_label(self):
        with self.assertRaisesRegex(SplitError, "^panel dates must be strictly ascending"):
            ensure_strictly_ascending(
                [date(2026, 1, 5), date(2026, 1, 7), date(2026, 1, 6)],
                label="panel dates",
            )


if __name__ == "__main__":
    unittest.main()
