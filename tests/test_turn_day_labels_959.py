"""H5 (#959): the turn-day measurement reads the scored days, the intervals and the risk types as declared.

The script is `scripts/turn_day_labels_959.py`; the declaration is `metadata/turn_day_labels_959.json`. The labels
themselves are tested in `test_turn_days.py`. These tests cover the script's own arithmetic, the scope guard and the page.

Recorded mutation (2026-10-19), for the scope guard `require_scored_days`: deleting its `if day > LAST_DAY: raise
LookAheadError(...)` loop made `test_a_day_after_the_declared_end_is_refused_by_this_script` fail with AssertionError
("LookAheadError not raised"). Restored, it passes.
"""

import importlib.util
import unittest
from datetime import date
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model import turn_days as td
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("turn_day_labels_959", ROOT / "scripts" / "turn_day_labels_959.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class Base:
    def day_type(self, values):
        return "ordinary"


class ScopeTests(unittest.TestCase):
    def test_a_day_after_the_declared_end_is_refused_by_this_script(self):
        with self.assertRaisesRegex(LookAheadError, "the last day #959 scores"):
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


class RiskTypeTests(unittest.TestCase):
    def labels(self):
        return td.TurnLabels(Base())

    def test_a_turn_day_and_a_tax_date_keep_their_labels_and_other_days_are_risk_dates_only_by_a_coupon(self):
        labels = self.labels()
        plain = {"tax_date": 0.0, "treasury_settlement_coupons": 0.0}
        coupon = {"tax_date": 0.0, "treasury_settlement_coupons": 5.0}
        tax = {"tax_date": 1.0, "treasury_settlement_coupons": 5.0}
        kind = script.risk_type_turn
        self.assertEqual(kind(date(2019, 5, 31), plain, labels, coupon_clause=True), "turn")
        self.assertEqual(kind(date(2019, 5, 15), tax, labels, coupon_clause=True), "tax_date")
        self.assertEqual(kind(date(2019, 5, 22), coupon, labels, coupon_clause=True), "settlement")
        self.assertIsNone(kind(date(2019, 5, 22), coupon, labels, coupon_clause=False))
        self.assertIsNone(kind(date(2019, 5, 22), plain, labels, coupon_clause=True))

    def test_the_penultimate_day_is_no_longer_a_risk_date_by_its_label(self):
        plain = {"tax_date": 0.0, "treasury_settlement_coupons": 0.0}
        self.assertIsNone(script.risk_type_turn(date(2019, 5, 30), plain, self.labels(), coupon_clause=True))


class NothingDecidedMovesTests(unittest.TestCase):
    def test_the_critical_values_are_untouched(self):
        self.assertIn(sp.GRID_COMPARISON, sp.CRITICAL_VALUES)
        self.assertEqual(script.LAST_DAY, date(2025, 12, 31))


class PageTests(unittest.TestCase):
    def test_the_committed_page_is_what_the_committed_record_gives(self):
        import json

        record = json.loads(script.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(script.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_page_says_it_is_development_data_and_no_verdict(self):
        import json

        text = script.PAGE.read_text(encoding="utf-8")
        self.assertIn("Development data, not a verdict", text)
        self.assertIn("Questions for Eleonora", text)
        self.assertEqual(json.loads(script.RECORD.read_text(encoding="utf-8"))["last_day"], "2025-12-31")


if __name__ == "__main__":
    unittest.main()
