"""The reported-only knowledge-holdout and H.4.1 lag study (#280).

These tests hold the two facts the study's text rests on, not its scores (the
scores are in the pull request that ran it): the measured first-print lags
come from the tracked vintages, and the shorter-lag registry is a copy that
moves only the H.4.1 fields and leaves the declared registry as it was.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "knowledge_holdout_lag_study.py"


def _load():
    spec = importlib.util.spec_from_file_location("knowledge_holdout_lag_study", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MeasuredLagTests(unittest.TestCase):
    def test_three_tracked_cases_give_one_two_and_five_days(self):
        cases = {
            (case["series"], case["observation"]): case["lag_calendar_days_at_most"]
            for case in _load().measured_lags()
        }
        # The week ending 2020-12-23 (Christmas), the one case the declared five
        # days rests on; Thanksgiving 2025; and an ordinary Thursday.
        self.assertEqual(cases[("WRESBAL", "2020-12-23")], 5)
        self.assertEqual(cases[("WLRRAOL", "2020-12-23")], 5)
        self.assertEqual(cases[("WRESBAL", "2025-11-26")], 2)
        self.assertEqual(cases[("WRESBAL", "2026-09-09")], 1)

    def test_no_case_is_measured_across_a_gap_between_tracked_vintage_clusters(self):
        for case in _load().measured_lags():
            self.assertLess(case["lag_calendar_days_at_most"], 14, case)

    def test_the_vintage_that_lacks_a_week_bounds_the_lag_from_below(self):
        for case in _load().measured_lags():
            self.assertGreaterEqual(
                case["lag_calendar_days_at_most"], case["lag_calendar_days_at_least"]
            )


class ShorterLagRegistryTests(unittest.TestCase):
    def test_only_the_h41_fields_move_and_the_registry_is_not_edited(self):
        module = _load()
        registry = json.loads((ROOT / "metadata" / "sources.json").read_text())
        before = json.dumps(registry, sort_keys=True)
        shorter = module.with_h41_lag(registry, 1)
        self.assertEqual(json.dumps(registry, sort_keys=True), before)
        fields = shorter[module.H41_SOURCE]["field_release_lags"]
        declared = registry[module.H41_SOURCE]["field_release_lags"]
        for name, entry in fields.items():
            if name in module.H41_FIELDS:
                self.assertEqual(entry["days"], 1)
            else:
                self.assertEqual(entry, declared[name])
        for source, entry in shorter.items():
            if source != module.H41_SOURCE:
                self.assertEqual(entry, registry[source])


if __name__ == "__main__":
    unittest.main()
