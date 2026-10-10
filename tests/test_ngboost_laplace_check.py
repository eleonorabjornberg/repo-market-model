"""The ngboost_laplace check (#533): the helpers of `scripts/ngboost_laplace_check.py`, a scratch measurement.

The script re-runs the judge for one row and reports what the tier 1 pass rests on. These tests pin its helpers on
small series: onsets warned by calendar year, the onsets that only the row warns, and the refit blocks at which a row
is constant or degenerate. They are data guards (`ValueError`), not leakage guards; the script reads no day after
2025-12-31 because the judge's own declaration sets the last scored day.
"""

import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("ngboost_laplace_check_script", ROOT / "scripts" / "ngboost_laplace_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DAYS = [date(2019, 12, 30) + timedelta(days=k) for k in range(6)]  # 2019-12-30 .. 2020-01-04


class WarnedByYearTests(unittest.TestCase):
    def test_onsets_and_warnings_are_counted_in_the_year_of_the_onset_day(self):
        out = _script().warned_by_year(DAYS, [1, 0, 1, 1, 0, 0], [1, 1, 0, 1, 0, 0])
        self.assertEqual(out, {2019: [1, 1], 2020: [2, 1]})

    def test_a_year_with_no_onset_is_absent(self):
        self.assertEqual(_script().warned_by_year(DAYS, [0] * 6, [1] * 6), {})

    def test_a_warning_on_a_day_that_is_not_an_onset_is_not_counted(self):
        self.assertEqual(_script().warned_by_year(DAYS, [0, 1, 0, 0, 0, 0], [1, 0, 1, 1, 1, 1]), {2019: [1, 0]})

    def test_series_of_different_length_are_refused(self):
        with self.assertRaises(ValueError):
            _script().warned_by_year(DAYS, [1, 0], [1] * 6)


class OnlyThisRowWarnsTests(unittest.TestCase):
    def test_only_onsets_the_row_warns_and_no_other_row_warns_are_listed(self):
        onset = [1, 1, 1, 0, 1, 0]
        row = [1, 1, 1, 1, 0, 0]
        others = [[1, 0, 0, 0, 0, 0], [0, 0, 1, 0, 1, 0]]
        self.assertEqual(_script().only_this_row_warns(DAYS, onset, row, others), [DAYS[1]])

    def test_with_no_other_row_every_warned_onset_is_listed(self):
        self.assertEqual(_script().only_this_row_warns(DAYS, [1, 0, 1, 0, 0, 0], [1, 1, 0, 0, 0, 0], []), [DAYS[0]])

    def test_series_of_different_length_are_refused(self):
        with self.assertRaises(ValueError):
            _script().only_this_row_warns(DAYS, [1] * 6, [1] * 6, [[1, 0]])


class RefitBlockTests(unittest.TestCase):
    def setUp(self):
        self.dates = [date(2020, 1, 1) + timedelta(days=k) for k in range(6)]

    def test_a_block_with_one_probability_is_constant(self):
        blocks = _script().refit_blocks([0.2, 0.2, 0.2, 0.1, 0.3, 0.2], [0.5] * 6, self.dates, 3)
        self.assertEqual([b["constant"] for b in blocks], [True, False])
        self.assertEqual([b["distinct"] for b in blocks], [1, 3])

    def test_a_block_of_zeros_is_constant_and_all_zero(self):
        blocks = _script().refit_blocks([0.0] * 3 + [0.1, 0.2, 0.3], [0.5] * 6, self.dates, 3)
        self.assertTrue(blocks[0]["constant"] and blocks[0]["all_zero"])
        self.assertFalse(blocks[1]["all_zero"])

    def test_an_infinite_cutoff_flags_nothing_and_a_cutoff_under_the_minimum_flags_every_day(self):
        inf = float("inf")
        blocks = _script().refit_blocks([0.1, 0.2, 0.3, 0.1, 0.2, 0.3], [inf] * 3 + [0.1] * 3, self.dates, 3)
        self.assertEqual([b["never_flag"] for b in blocks], [True, False])
        self.assertEqual([b["always_flag"] for b in blocks], [False, True])

    def test_the_last_block_may_be_short(self):
        blocks = _script().refit_blocks([0.1] * 6, [0.5] * 6, self.dates, 4)
        self.assertEqual([b["days"] for b in blocks], [4, 2])

    def test_the_summary_counts_each_kind(self):
        script = _script()
        blocks = script.refit_blocks([0.0] * 3 + [0.1, 0.2, 0.3], [float("inf")] * 3 + [0.05] * 3, self.dates, 3)
        summary = script.block_summary(blocks)
        self.assertEqual(
            (summary["refits"], summary["constant"], summary["all_zero"], summary["never_flag"], summary["always_flag"]),
            (2, 1, 1, 1, 1),
        )
        self.assertEqual(summary["first_days_constant"], ["2020-01-01"])

    def test_unequal_series_and_an_empty_block_are_refused(self):
        script = _script()
        with self.assertRaises(ValueError):
            script.refit_blocks([0.1] * 5, [0.5] * 6, self.dates, 3)
        with self.assertRaises(ValueError):
            script.refit_blocks([0.1] * 6, [0.5] * 6, self.dates, 0)


if __name__ == "__main__":
    unittest.main()
