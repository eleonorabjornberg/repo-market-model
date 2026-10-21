"""H1 (#1014, finding #1001): the B3 five-level critical value is calibrated in the orientation `report` reads.

`scoring_protocol.report` reads B3 as the benchmark: its `against_b3` test has d = S(B3) - S(candidate), so a value for it
is the quantile of the studentized mean of S(B3) - S(B1). The drafts of #873 and #886 calibrated it on S(B1) - S(B3)
(`protocol_coverage.calibration_series`), the reverse, and the daily difference is skewed, so the two quantiles differ.
These tests read the orientation from `sp.paired_test` itself and require `scripts/b3_orientation_1014.py` to calibrate on
what that orientation gives. They pin the series, the window settings and the null share; they read no result.

Recorded mutation (2026-10-20): in `scripts/b3_orientation_1014.py`, `report_orientation_series` returned
`[a - b for a, b in zip(s1, s3)]` (S(B1) - S(B3), the drafts' orientation) instead of `[b - a ...]`;
`test_the_series_is_the_one_report_reads` raised AssertionError (the mean was minus the test's) and so did
`test_it_is_not_the_drafts_series`. Not a leakage guard.
"""

import importlib.util
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b3_orientation_1014_script", ROOT / "scripts" / "b3_orientation_1014.py")
b3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b3)

DAYS = 400


def scores(seed, shift=0.0):
    rng = random.Random(seed)
    return [1.0 + shift + rng.random() * rng.random() for _ in range(DAYS)]


def calendar(first=date(2020, 1, 1)):
    return [first + timedelta(days=i) for i in range(DAYS)]


class TestOrientation(unittest.TestCase):
    def setUp(self):
        self.s1 = scores(1, shift=0.4)
        self.s3 = scores(3)
        self.days = calendar()

    def paired(self, bench, candidate):
        return sp.paired_test(dict(zip(self.days, bench)), dict(zip(self.days, candidate)), seed=1, draws=50, with_skill=True)

    def test_the_series_is_the_one_report_reads(self):
        """`report`'s `against_b3` has B3 as the benchmark and the candidate (here B1) on the other side."""

        _, series = b3.report_orientation_series(self.days, self.s1, self.s3, first=self.days[0])
        test = self.paired(self.s3, self.s1)
        self.assertAlmostEqual(sum(series) / len(series), test.mean_difference, places=12)
        self.assertLess(test.mean_difference, 0.0)

    def test_it_is_not_the_drafts_series(self):
        pc_spec = importlib.util.spec_from_file_location("pc_for_1014", ROOT / "scripts" / "protocol_coverage.py")
        pc = importlib.util.module_from_spec(pc_spec)
        pc_spec.loader.exec_module(pc)
        drafts = pc.calibration_series((self.s1, self.s3), (self.s1, self.s3))[sp.FIVE_LEVEL_COMPARISON]
        _, series = b3.report_orientation_series(self.days, self.s1, self.s3, first=self.days[0])
        self.assertEqual(series, [-v for v in drafts])

    def test_only_the_days_from_the_first_are_kept(self):
        days, series = b3.report_orientation_series(self.days, self.s1, self.s3, first=self.days[100])
        self.assertEqual(days[0], self.days[100])
        self.assertEqual(len(days), len(series))
        self.assertEqual(len(series), DAYS - 100)

    def test_unequal_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            b3.report_orientation_series(self.days, self.s1[:-1], self.s3, first=self.days[0])


class TestTheCalibration(unittest.TestCase):
    def setUp(self):
        _, self.series = b3.report_orientation_series(calendar(), scores(1, shift=0.4), scores(3), first=calendar()[0])

    def test_the_value_is_the_protocols_calibration_with_the_settings_of_the_record(self):
        value = b3.calibrate_value(self.series, days=125, level=0.05, windows=300)
        self.assertEqual(value, sp.calibrate_critical_value(self.series, days=125, level=0.05, windows=300, seed=1))
        self.assertEqual(b3.SEED, 1)
        self.assertEqual(b3.WINDOWS, 20_000)
        self.assertEqual(sp.WINDOW_BLOCK, 10)

    def test_the_orientation_matters_for_a_skewed_series(self):
        forward = b3.calibrate_value(self.series, days=125, level=0.05, windows=300)
        reverse = b3.calibrate_value([-v for v in self.series], days=125, level=0.05, windows=300)
        self.assertNotAlmostEqual(forward, reverse, places=3)


class TestTheNullShare(unittest.TestCase):
    def setUp(self):
        self.s1, self.s3 = scores(1, shift=0.4), scores(3)

    def test_a_huge_value_detects_nothing_and_a_negative_one_everything(self):
        huge = b3.null_share(self.s1, self.s3, {125: 1e9, 250: 1e9}, paths=40)
        self.assertEqual(huge, {"125": 0.0, "250": 0.0})
        low = b3.null_share(self.s1, self.s3, {125: -1e9, 250: -1e9}, paths=40)
        self.assertEqual(low, {"125": 1.0, "250": 1.0})

    def test_a_smaller_value_detects_at_least_as_often(self):
        loose = b3.null_share(self.s1, self.s3, {125: 1.0, 250: 0.5}, paths=60)
        tight = b3.null_share(self.s1, self.s3, {125: 3.0, 250: 2.0}, paths=60)
        for look in ("125", "250"):
            self.assertGreaterEqual(loose[look], tight[look])


class TestThePage(unittest.TestCase):
    def test_the_page_is_what_the_record_gives(self):
        record = {
            "orientation": b3.ORIENTATION, "first_day": "2020-04-03", "last_day": "2025-12-23", "series_days": 3,
            "windows": 20000, "seed": 1, "block": 10, "paths": 2000, "nominal_levels": {"125": 0.01, "250": 0.05},
            "calibrated": {"125": 1.5, "250": 1.2},
            "values": [{"name": "in force", "source": "x", "critical": {"125": 9.5, "250": 5.4},
                        "null_share": {"125": 0.0, "250": 0.0}},
                       {"name": "calibrated here", "source": "y", "critical": {"125": 1.5, "250": 1.2},
                        "null_share": {"125": 0.01, "250": 0.05}}],
        }
        page = b3.render(record)
        self.assertIn("Eleonora", page)
        self.assertIn("section 13", page)
        self.assertIn("1.500", page)
        self.assertEqual(page, b3.render(record))


if __name__ == "__main__":
    unittest.main()
