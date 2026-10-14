"""The H4 back-fill spread measurement's fixed parts (#633): its days, its guards and its interval.

`scripts/backfill_spread_633.py` is exploration on development data. These tests pin what does not depend on a
fit: no decision day before 2018-06-29 and no target after 2025-12-31, both back-fill guards applied to every
block, and the bootstrap interval of a mean.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "backfill_spread_633.py"


def _module():
    spec = importlib.util.spec_from_file_location("backfill_spread_633_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _business_days(first: date, last: date):
    day, out = first, []
    while day <= last:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class TheDecisionDays(unittest.TestCase):
    def test_they_start_on_29_june_2018_and_no_target_passes_2025(self):
        module = _module()
        dates = _business_days(date(2018, 4, 3), date(2026, 1, 30))
        chosen = [dates[k] for k in module.decision_indices(dates)]
        self.assertEqual(chosen[0], date(2018, 6, 29))
        last = module.decision_indices(dates)[-1]
        self.assertLessEqual(dates[last + 5], date(2025, 12, 31))
        self.assertGreater(dates[last + 6], date(2025, 12, 31))


class TheGuards(unittest.TestCase):
    def test_every_block_passes_both_back_fill_guards_with_the_declared_instant(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("backfill.require_training_only(folds", text)
        self.assertIn("backfill.require_posting_established(folds, posting", text)
        self.assertIn("backfill.load_posting_instant(POSTING)", text)

    def test_the_declaration_states_the_kill_rule_and_the_arms(self):
        declared = json.loads((ROOT / "metadata" / "backfill_spread_633.json").read_text(encoding="utf-8"))
        self.assertIn("covers zero", declared["kill_rule_reading"])
        self.assertEqual(set(declared["arms"]), {"with", "without"})


class TheInterval(unittest.TestCase):
    def test_a_constant_difference_has_a_point_interval(self):
        low, high = _module()._interval([0.25] * 40, draws=200)
        self.assertAlmostEqual(low, 0.25)
        self.assertAlmostEqual(high, 0.25)

    def test_it_brackets_the_mean(self):
        values = [(-1.0) ** k * (k % 7) / 7.0 for k in range(120)]
        low, high = _module()._interval(values, draws=500)
        mean = sum(values) / len(values)
        self.assertLess(low, mean)
        self.assertGreater(high, mean)


if __name__ == "__main__":
    unittest.main()
