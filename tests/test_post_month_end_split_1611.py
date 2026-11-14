"""The post-month-end split of (s3c-ann-net)'s misses by business day (#1611): `scripts/post_month_end_split_1611.py`.

The tests fix the arithmetic on hand cases: which business day and which kind of month-end a target day follows, the per-day miss series of a
group of cells, the studentized stationary-bootstrap interval of scoring protocol v1 (and the case it cannot studentize), the split by business day
and lead, and the guards the script adds: a locked day is refused (`LookAheadError`), and the study's business-day count must agree with the
`post_month_end_window` flag of the walk file (`ValueError`).

Recorded mutations (the guards this script adds):

* `check_unlocked`, the call `lockbox.require_unlocked(days, where=WHERE)` replaced by `pass`: `test_a_locked_target_day_is_refused` fails with
  `AssertionError` (`LookAheadError not raised`); restored, it passes.
* `check_reproduction`, the test `if len(mine) != theirs["cells"] or ...:` replaced by `if False:`: `test_cells_that_differ_from_1547_are_refused`
  fails with `AssertionError` (`ValueError not raised`); restored, it passes.
* `check_flag_agreement`, the test `if flagged != counted:` replaced by `if False:`: `test_a_flag_that_disagrees_with_the_business_day_is_refused`
  fails with `AssertionError` (`ValueError not raised`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("post_month_end_split_1611_script", REPO / "scripts" / "post_month_end_split_1611.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402

G05, G50, G95 = script.G05, script.G50, script.G95


def cell(t: str, h: int, y: float, *, low: float = -1.0, mid: float = 0.0, high: float = 1.0, regime: str = "2021-23") -> dict:
    """A cell whose forecast quantiles are low/mid/high at the 5/50/95 grid positions (the rest are filled in order)."""

    q = [0.0] * len(script.q.GRID)
    q[G05], q[G50], q[G95] = low, mid, high
    return {"d": "2021-01-01", "h": h, "t": t, "y": y, "q": q, "regime": regime}


class CalendarTests(unittest.TestCase):
    def test_business_day_counts_market_days_of_the_month(self):
        self.assertEqual(script.business_day(date(2024, 4, 1)), 1)  # a Monday
        self.assertEqual(script.business_day(date(2024, 4, 3)), 3)
        self.assertEqual(script.business_day(date(2024, 3, 1)), 1)  # a Friday
        self.assertEqual(script.business_day(date(2024, 3, 5)), 3)  # the weekend is skipped

    def test_a_target_after_a_quarter_end_month_end_is_in_the_quarter_end_scope(self):
        for month in (1, 4, 7, 10):
            self.assertEqual(script.month_end_kind(date(2024, month, 2)), "quarter_end")
        for month in (2, 3, 5, 6, 8, 9, 11, 12):
            self.assertEqual(script.month_end_kind(date(2024, month, 2)), "other")


class SeriesTests(unittest.TestCase):
    def test_miss_series_is_strict_and_one_value_per_target_day(self):
        cells = [cell("2021-02-02", 1, -1.0), cell("2021-02-02", 2, -2.0), cell("2021-03-02", 1, 1.0), cell("2021-04-05", 1, 5.0)]
        s = script.day_series(cells)
        self.assertEqual(s["days"], ["2021-02-02", "2021-03-02", "2021-04-05"])
        self.assertEqual(s["low"], [0.5, 0.0, 0.0])  # y == q05 is not below it
        self.assertEqual(s["up"], [0.0, 0.0, 1.0])  # y == q95 is not above it
        self.assertEqual(s["error"], [-1.5, 1.0, 5.0])

    def test_the_error_is_the_outcome_less_the_forecast_median(self):
        s = script.day_series([cell("2021-02-02", 1, 3.0, mid=1.0, low=-5.0, high=5.0)])
        self.assertEqual(s["error"], [2.0])


class IntervalTests(unittest.TestCase):
    def test_a_series_with_no_variation_cannot_be_studentized(self):
        self.assertIsNone(script.studentized_interval([0.0] * 40, reps=200, seed=1))

    def test_the_interval_holds_the_point_and_is_reproducible(self):
        values = [1.0 if i % 9 == 0 else 0.0 for i in range(90)]
        a = script.studentized_interval(values, reps=500, seed=7)
        b = script.studentized_interval(values, reps=500, seed=7)
        self.assertEqual(a, b)
        point, lo, hi = a
        self.assertAlmostEqual(point, 10 / 90)
        self.assertLessEqual(lo, point)
        self.assertGreaterEqual(hi, point)
        self.assertGreaterEqual(lo, 0.0)
        self.assertLessEqual(hi, 1.0)

    def test_a_short_series_is_refused_an_interval(self):
        self.assertIsNone(script.studentized_interval([0.0, 1.0] * 5, reps=100, seed=1))

    def test_the_median_interval_is_a_percentile_interval_of_resampled_medians(self):
        point, lo, hi = script.median_interval([float(i) for i in range(60)], reps=300, seed=3)
        self.assertEqual(point, 29.5)
        self.assertLessEqual(lo, point)
        self.assertGreaterEqual(hi, point)


class SplitTests(unittest.TestCase):
    def cells(self):
        out = []
        for year in (2019, 2021):
            for month in range(1, 13):
                for day in (1, 2, 3):
                    t = f"{year}-{month:02d}-{day:02d}"
                    d = date.fromisoformat(t)
                    if d.weekday() >= 5:
                        continue
                    for h in (1, 2):
                        out.append(cell(t, h, 2.0 if h == 1 else 0.0, regime="2018-19" if year == 2019 else "2021-23"))
        return out

    def test_the_split_has_one_entry_per_business_day_and_lead_with_counts(self):
        res = script.split(self.cells(), reps=50, seed=1)
        self.assertEqual(sorted(res), ["1", "2", "3"])
        for bday, leads in res.items():
            self.assertEqual(sorted(leads), ["1", "2", "all"])
            self.assertEqual(leads["1"]["cells"], leads["1"]["days"])
            self.assertEqual(leads["all"]["cells"], 2 * leads["all"]["days"])

    def test_lead_one_misses_above_and_lead_two_does_not(self):
        res = script.split(self.cells(), reps=50, seed=1)
        self.assertEqual(res["1"]["1"]["up"]["misses"], res["1"]["1"]["days"])
        self.assertEqual(res["1"]["2"]["up"]["misses"], 0)
        self.assertEqual(res["1"]["1"]["low"]["misses"], 0)

    def test_a_day_past_business_day_three_is_not_in_the_split(self):
        res = script.split([cell("2021-02-04", 1, 9.0)], reps=10, seed=1)
        self.assertEqual(res, {})

    def test_a_group_without_an_interval_still_carries_its_point_errors(self):
        res = script.split(self.cells(), reps=0, seed=1)
        e = res["1"]["1"]
        self.assertEqual(e["median_error"], [2.0, None, None])
        self.assertEqual(e["mean_error"], [2.0, None, None])
        self.assertIsNone(e["up"]["interval"])

    def test_regimes_are_split_and_a_thin_one_has_no_interval(self):
        res = script.by_regime(self.cells(), reps=50, seed=1)
        self.assertEqual(sorted(res["1"]), ["2018-19", "2021-23"])
        self.assertIsNone(res["1"]["2018-19"]["up"]["interval"])  # about 12 target days: under the minimum for an interval


class GuardTests(unittest.TestCase):
    def test_a_locked_target_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.check_unlocked([cell("2026-09-04", 1, 0.0)])

    def test_an_unlocked_day_passes(self):
        script.check_unlocked([cell("2025-12-02", 1, 0.0)])

    def test_the_origin_day_is_read_too(self):
        c = cell("2025-12-02", 1, 0.0)
        c["d"] = "2026-09-04"
        with self.assertRaises(LookAheadError):
            script.check_unlocked([c])

    def test_a_flag_that_disagrees_with_the_business_day_is_refused(self):
        targets = {"2021-02-02": {"types": ["ordinary"]}, "2021-02-03": {"types": ["post_month_end_window"]}}
        with self.assertRaises(ValueError):
            script.check_flag_agreement(targets)

    def test_a_flag_that_agrees_passes(self):
        targets = {"2021-02-02": {"types": ["post_month_end_window"]}, "2021-02-10": {"types": ["ordinary"]}}
        script.check_flag_agreement(targets)


class ReproductionTests(unittest.TestCase):
    def reference(self, cells, low, up):
        return {"cells": cells, "paired": {"miss_q05_low": [low], "miss_q95_up": [up]}}

    def test_cells_that_equal_1547_pass(self):
        cells = [cell("2021-03-01", 1, 5.0), cell("2021-03-02", 1, -5.0), cell("2021-03-03", 1, 0.0), cell("2021-03-19", 1, 5.0)]
        got = script.check_reproduction(cells, self.reference(3, 1 / 3, 1 / 3))
        self.assertEqual(got["cells"], 3)

    def test_cells_that_differ_from_1547_are_refused(self):
        cells = [cell("2021-02-02", 1, 5.0), cell("2021-02-03", 1, 0.0)]
        with self.assertRaises(ValueError):
            script.check_reproduction(cells, self.reference(2, 0.0, 0.0))


class PageTests(unittest.TestCase):
    def test_the_page_is_written_from_a_score_and_quotes_its_figures(self):
        cells = SplitTests().cells()
        score = script.score_cells({"development": cells, "2026": []}, reps=40, seed=1)
        text = script.page(score)
        self.assertIn("#1611", text)
        self.assertIn("business day 1", text)
        json.dumps(score)  # serialisable


if __name__ == "__main__":
    unittest.main()
