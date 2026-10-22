"""The helpers of `scripts/richer_targets_902.py` (#902; H9 step 2 redone on #941's scaled mean reversion, development tier).

Written before the script. What these tests pin: the walk files in #706's format (a lead-h law keyed by its target day), the
refusal of a dropped day that is not a scored decision day, the refusal of a locked day, the cells whose lower bound changes
sign when the day is dropped, and the labelling of the page.

Recorded mutations (the guards this script adds; the scorer's own lockbox guard is tested with the scorer):

* `require_dropped_day`, the test `if day not in days:` replaced by `if False:`: `test_a_dropped_day_that_is_not_scored_is_refused`
  fails with `AssertionError` (`ValueError not raised`).
* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused` fails with
  `AssertionError` (`LookAheadError not raised`; every day after 2026-09-03 is blind, `metadata/lockbox.json`).
* `check_inputs`, the comparison of the panel digest with the declared one replaced by `False`: `test_another_panel_is_refused`
  fails with `AssertionError` (`SystemExit not raised`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("richer_targets_902_script", REPO / "scripts" / "richer_targets_902.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402

START = date(2024, 1, 2)
CALENDAR = [START + timedelta(days=i) for i in range(12)]


def _cell(lower, skill=0.1):
    return {"skill": skill, "skill_lower_95_one_sided": lower}


def _result(lower_b1, lower_b2=0.1, lower_b1p=0.1, auc=0.55):
    tests = {"B1 -> model": _cell(lower_b1), "B2 -> model": _cell(lower_b2), "B1p -> model": _cell(lower_b1p)}
    band = {"onsets": 5, "auc": auc, "auc_low": auc - 0.1, "auc_high": auc + 0.1}
    return {
        "decision_days": {"n": 100},
        "pooled": tests,
        "by_lead": {str(h): {"tests": tests} for h in script.HORIZONS},
        "by_state": {"ample": {"n": 60, "tests": tests}},
        "by_day_type": {"month_end": {"decision_days": 30, "tests": tests}},
        "lead_on_onsets": {"cells": {"model_median": {"ample": band, "scarce": band}, "as_of_value": {"ample": band, "scarce": band}}},
        "mean": {"B1": 1.0, "B1p": 1.0, "B2": 1.0, "model": 0.8},
    }


def _document(lower_with, lower_without, **kwargs):
    return {
        "label": "development data, not a verdict",
        "declaration": "metadata/richer_targets_902.json",
        "dropped_day": "2019-09-18",
        "model": "spread_mr_fhs_mad20_f0.5",
        "panel_sha256": "ab" * 32,
        "targets": {
            "t": {
                "with": _result(lower_with, **kwargs),
                "without": _result(lower_without, **kwargs),
                "the_day": {"grid_crps": {"model": 3.0, "B1p": 9.0}},
            }
        },
    }


class WalkFileTests(unittest.TestCase):
    def test_a_lead_h_law_is_keyed_by_its_target_day(self):
        forecasts = {CALENDAR[2]: {1: [1.0], 2: [2.0]}, CALENDAR[3]: {1: [3.0], 2: [4.0]}}
        self.assertEqual(
            script.laws_by_target(forecasts, CALENDAR, 2), {CALENDAR[4]: [2.0], CALENDAR[5]: [4.0]}
        )
        self.assertEqual(script.laws_by_target(forecasts, CALENDAR, 1), {CALENDAR[3]: [1.0], CALENDAR[4]: [3.0]})

    def test_a_decision_day_off_the_calendar_is_an_error(self):
        with self.assertRaises(ValueError):
            script.laws_by_target({date(2000, 1, 1): {1: [1.0]}}, CALENDAR, 1)


class GuardTests(unittest.TestCase):
    def test_the_dropped_day_is_a_scored_decision_day(self):
        script.require_dropped_day([CALENDAR[0], CALENDAR[1]], CALENDAR[1])

    def test_a_dropped_day_that_is_not_scored_is_refused(self):
        with self.assertRaises(ValueError):
            script.require_dropped_day([CALENDAR[0]], CALENDAR[1])

    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 4)])

    def test_a_development_day_passes(self):
        script.refuse_locked([date(2025, 12, 31)])

    def test_another_panel_is_refused(self):
        declared = {"panel": {"sha256": "aa"}}
        script.check_inputs(declared, "aa")
        with self.assertRaises(SystemExit):
            script.check_inputs(declared, "bb")


class SignChangeTests(unittest.TestCase):
    def test_a_bound_that_changes_sign_is_listed_in_every_cut_it_changes(self):
        changes = script.sign_changes(_document(0.05, -0.02))
        self.assertTrue(any("pooled" in c and "over B1:" in c for c in changes))
        self.assertTrue(any("state ample" in c for c in changes))
        self.assertTrue(any("day type month_end" in c for c in changes))
        self.assertFalse(any("over B2" in c for c in changes))
        self.assertFalse(any("over B1'" in c for c in changes))

    def test_bounds_on_the_same_side_are_not_listed(self):
        self.assertEqual(script.sign_changes(_document(0.05, 0.01)), [])

    def test_the_prime_benchmark_is_read_too(self):
        document = _document(0.05, 0.05)
        document["targets"]["t"]["without"]["pooled"]["B1p -> model"] = _cell(-0.01)
        self.assertTrue(any("over B1'" in c for c in script.sign_changes(document)))


class PageTests(unittest.TestCase):
    def test_the_page_is_labelled_and_names_what_it_is_not(self):
        page = script.page_markdown(_document(0.05, -0.02))
        self.assertIn("development data, not a verdict", page)
        self.assertIn("provisional", page)
        self.assertIn("lower bound +0.050 with the day, -0.020 without", page)

    def test_a_page_without_sign_changes_says_so(self):
        self.assertIn("None: no lower bound", script.page_markdown(_document(0.05, 0.01)))

    def test_the_page_carries_b1_prime_pooled_by_state_and_by_day_type(self):
        page = script.page_markdown(_document(0.05, 0.01))
        for title in ("Pooled, skill over B1'", "By as-of scarcity state, skill over B1'", "By day type of the target day, skill over B1'"):
            self.assertIn(title, page)

    def test_the_page_is_json_clean(self):
        json.dumps(_document(0.05, 0.01))


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_the_ruling_the_targets_and_the_day(self):
        declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(declared["issue"], 902)
        self.assertIn("6350222095", json.dumps(declared["rulings"]))
        self.assertEqual(declared["model"]["name"], "spread_mr_fhs_mad20_f0.5")
        self.assertEqual(declared["dropped_day"], "2019-09-18")
        older = json.loads((REPO / "metadata" / "richer_targets_706.json").read_text(encoding="utf-8"))
        self.assertEqual(declared["targets"], older["choice"]["chosen"])
        self.assertEqual(declared["panel"]["sha256"], older["panel"]["sha256"])


if __name__ == "__main__":
    unittest.main()
