"""The final test's expected leap counts, written down before any opening (#222).

Eleonora's amendment of 4 October 2026 (second), with her scope comment of the
same day on #222: the record states the expected plain-leap count on the
near-blind window (its 169 days counted from panel dates only), the pre-2026
rate it assumes, the Poisson chance of reaching the minimum of 20, and each
pre-2026 year's January-August plain-leap count, recounted on the published
fold grid by `scripts/final_test_leap_counts.py`. No 2026 outcome is read.

Red first: this file was committed before the script and the section existed.
`CountTests` and `LockedDayTests` failed with `FileNotFoundError` on the
missing script, and `RecordTests` failed on the missing section.

The script adds no guard of its own: it refuses a locked scored day through
`final_test_preregistration._refuse_locked`, whose mutation record is in
`tests/test_final_test_freeze.py` (`RefuseLockedTests`).
"""

from __future__ import annotations

import importlib.util
import pickle
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "final_test_leap_counts.py"
RECORD = REPO / "docs" / "decisions" / "final-test-preregistration.md"
SECTION = "## Amendment, 4 October 2026 (second), before any opening"


def _script():
    spec = importlib.util.spec_from_file_location("final_test_leap_counts", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CountTests(unittest.TestCase):
    """Per-year January-August counts and the Poisson tail."""

    def setUp(self):
        self.lc = _script()

    def test_only_january_to_august_is_counted_per_year(self):
        days = [date(2020, 1, 2), date(2020, 8, 31), date(2020, 9, 1), date(2021, 3, 1),
                date(2021, 12, 31)]
        labels = [1, 0, 1, 1, 1]
        self.assertEqual(self.lc.january_to_august(days, labels),
                         {2020: {"days": 2, "leaps": 1}, 2021: {"days": 1, "leaps": 1}})

    def test_the_labels_must_match_the_days(self):
        with self.assertRaises(ValueError):
            self.lc.january_to_august([date(2020, 1, 2)], [1, 0])

    def test_the_poisson_tail(self):
        self.assertEqual(self.lc.poisson_at_least(0, 3.0), 1.0)
        self.assertAlmostEqual(self.lc.poisson_at_least(1, 2.0), 1 - 2.718281828459045 ** -2)
        self.assertEqual(round(self.lc.poisson_at_least(20, 169 * 164 / 1873), 2), 0.11)

    def test_the_summary_scales_the_pre_2026_rate_to_the_window(self):
        days = [date(2019, 1, 2), date(2019, 1, 3), date(2019, 9, 2), date(2020, 1, 2)]
        summary = self.lc.summary(days, [1, 0, 1, 0], window_days=169)
        self.assertEqual((summary["scored_days"], summary["plain_leaps"]), (4, 2))
        self.assertAlmostEqual(summary["expected_leaps"], 169 * 2 / 4)
        self.assertEqual(summary["minimum_events"], 20)
        self.assertEqual(summary["january_to_august"]["2019"]["leaps"], 1)
        self.assertAlmostEqual(summary["january_to_august"]["2019"]["expected_leaps"], 169 / 2)


class LockedDayTests(unittest.TestCase):
    """A run whose scored days reach the near-blind tier is refused before any label is read."""

    def test_a_locked_scored_day_is_refused(self):
        lc = _script()
        with tempfile.TemporaryDirectory() as scratch:
            run = Path(scratch) / "run.pickle"
            run.write_bytes(pickle.dumps({
                "scored_dates": [date(2025, 12, 31), date(2026, 1, 2)],
                "leap_threshold_bp": 3.0,
            }))
            with self.assertRaises(LookAheadError):
                lc.main(["--panel", str(Path(scratch) / "absent.csv"), "--run", str(run)])


class RecordTests(unittest.TestCase):
    """The record carries the dated section after the CRPS-primary amendment."""

    def test_the_section_follows_the_crps_primary_amendment(self):
        text = RECORD.read_text(encoding="utf-8")
        self.assertIn(SECTION, text)
        self.assertLess(text.index("## Amendment, 4 October 2026: the full-range test is the primary cell"),
                        text.index(SECTION))

    def test_the_section_states_the_counts_and_the_three_labels(self):
        text = RECORD.read_text(encoding="utf-8")
        section = " ".join(text[text.index(SECTION):].split())
        for phrase in ("169 scored days", "164 of 1873", "14.8", "20 events", "0.11",
                       "scripts/final_test_leap_counts.py",
                       '"shown better"', '"not shown"', '"shown worse"'):
            self.assertIn(phrase, section)


if __name__ == "__main__":
    unittest.main()
