"""H5 (#965): the 15 October measurement reads the scored days, the intervals and the windows as declared.

The script is `scripts/tax_date_october_965.py`; the declaration is `metadata/tax_date_october_965.json`. The labels
themselves are tested in `test_tax_date_october.py`. These tests cover the script's own arithmetic, the scope guard and the
page.

Recorded mutation (2026-10-19), for the scope guard `require_scored_days`: deleting its `if day > LAST_DAY: raise
LookAheadError(...)` loop made `test_a_day_after_the_declared_end_is_refused_by_this_script` fail with AssertionError
("LookAheadError not raised"). Restored, it passes.
"""

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tax_date_october_965", ROOT / "scripts" / "tax_date_october_965.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class ScopeTests(unittest.TestCase):
    def test_a_day_after_the_declared_end_is_refused_by_this_script(self):
        with self.assertRaisesRegex(LookAheadError, "the last day #965 scores"):
            script.require_scored_days([date(2026, 1, 2)])

    def test_the_declared_last_day_is_scored(self):
        script.require_scored_days([date(2025, 12, 31)])


class IntervalTests(unittest.TestCase):
    def test_the_interval_is_the_point_less_the_95th_and_5th_percentile_of_the_t_draws(self):
        draws = [float(x) for x in range(-50, 51)]  # sorted, 101 values: the 5th percentile is -45, the 95th is +45
        low, high = script.two_sided(1.0, draws, 0.1, len(draws))
        self.assertAlmostEqual(low, 1.0 - 4.5)
        self.assertAlmostEqual(high, 1.0 + 4.5)

    def test_the_reading_follows_the_skill_interval(self):
        self.assertEqual(script.verdict_words({"skill_interval": [0.01, 0.2]}), "candidate better")
        self.assertEqual(script.verdict_words({"skill_interval": [-0.2, -0.01]}), "candidate worse")
        self.assertEqual(script.verdict_words({"skill_interval": [-0.1, 0.1]}), "no difference")
        self.assertEqual(script.verdict_words({"undefined": "x", "difference": 0.0}), "scores identical")

    def test_the_unstudentized_interval_brackets_a_constant_difference(self):
        low, high = script.percentile_interval([0.5] * 30, 200)
        self.assertAlmostEqual(low, 0.5)
        self.assertAlmostEqual(high, 0.5)


class GroupTests(unittest.TestCase):
    class Splits:
        def reporting_day_type(self, when, values):
            return values["kind"]

    class Panel:
        def __init__(self):
            self.splits = GroupTests.Splits()
            self.values = {date(2019, 10, 15): {"kind": "ordinary"}, date(2019, 11, 15): {"kind": "ordinary"},
                           date(2019, 4, 15): {"kind": "tax_date"}, date(2019, 5, 22): {"kind": "ordinary"}}

    def test_the_target_groups_partition_the_days(self):
        groups = script.target_groups(self.Panel())
        for day in self.Panel().values:
            self.assertEqual(sum(1 for inside in groups.values() if inside(day)), 1, day)
        self.assertTrue(groups["october window"](date(2019, 10, 15)))
        self.assertTrue(groups["control window"](date(2019, 11, 15)))
        self.assertTrue(groups["tax_date as is"](date(2019, 4, 15)))
        self.assertTrue(groups["other days"](date(2019, 5, 22)))


class NothingDecidedMovesTests(unittest.TestCase):
    def test_the_critical_values_are_untouched(self):
        self.assertIn(sp.GRID_COMPARISON, sp.CRITICAL_VALUES)
        self.assertEqual(script.LAST_DAY, date(2025, 12, 31))


class PageTests(unittest.TestCase):
    def test_the_committed_page_is_what_the_committed_record_gives(self):
        record = json.loads(script.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(script.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_page_says_it_is_development_data_and_no_verdict(self):
        text = script.PAGE.read_text(encoding="utf-8")
        self.assertIn("Development data, not a verdict", text)
        self.assertIn("Questions for Eleonora", text)
        self.assertEqual(json.loads(script.RECORD.read_text(encoding="utf-8"))["last_day"], "2025-12-31")


if __name__ == "__main__":
    unittest.main()
