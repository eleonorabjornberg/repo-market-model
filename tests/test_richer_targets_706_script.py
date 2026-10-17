"""The measurement script of #706 (`scripts/richer_targets_706.py`): the parts that decide what is scored and what is read.

Recorded mutation (the one guard this script adds; the scorer's own lockbox guard is tested with the scorer):

* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`; the blind tier is every day after 2026-09-03, `metadata/lockbox.json`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("richer_targets_706_script", REPO / "scripts" / "richer_targets_706.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402


class LockedDayTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 4)])

    def test_a_development_day_passes(self):
        script.refuse_locked([date(2025, 12, 31)])


class DeclarationTests(unittest.TestCase):
    def test_the_committed_declaration_names_the_rules_choice(self):
        declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(declared["issue"], 706)
        self.assertEqual(len(declared["choice"]["chosen"]), 3)
        self.assertLessEqual(set(declared["choice"]["chosen"]), {row["target"] for row in declared["choice"]["ranking"]})
        # the choice is what the rule gives on step 1's tables, so a changed table cannot leave the declaration standing
        screen = json.loads(script.SCREEN.read_text(encoding="utf-8"))
        self.assertEqual(script.richer_targets.choose_targets(screen)["chosen"], declared["choice"]["chosen"])

    def test_an_uncommitted_declaration_is_refused(self):
        class Done:
            stdout = " M metadata/richer_targets_706.json\n"

        with mock.patch.object(script.subprocess, "run", return_value=Done()):
            with self.assertRaises(SystemExit):
                script.committed_declaration()


class PanelRowsTests(unittest.TestCase):
    def write(self, directory: Path, values):
        path = directory / "panel.csv"
        lines = ["date,sofr,iorb,sofr_p25,sofr_p75,tgt"]
        for i, value in enumerate(values):
            lines.append(f"2024-03-{4 + i:02d},5.3,5.4,5.3,5.3,{'' if value is None else value}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def rows(self, values):
        from repo_model.data import DailyObservation

        return [
            DailyObservation(date(2024, 3, 4 + i), {"sofr": 5.3, "iorb": 5.4, "tgt": value}) for i, value in enumerate(values)
        ]

    def test_a_leading_hole_is_dropped_and_a_later_one_is_an_error(self):
        with mock.patch.object(script, "load_daily_panel", return_value=self.rows([None, 1.0, 2.0])), mock.patch.object(
            script, "audit_panel"
        ):
            kept = script.panel_rows(Path("unused"), "tgt")
        self.assertEqual([row.values["tgt"] for row in kept], [1.0, 2.0])
        with mock.patch.object(script, "load_daily_panel", return_value=self.rows([1.0, None, 2.0])), mock.patch.object(
            script, "audit_panel"
        ):
            with self.assertRaises(ValueError):
                script.panel_rows(Path("unused"), "tgt")

    def test_days_after_the_last_target_day_are_not_read(self):
        from repo_model.data import DailyObservation

        rows = [DailyObservation(date(2025, 12, 31), {"tgt": 1.0}), DailyObservation(date(2026, 1, 2), {"tgt": 2.0})]
        with mock.patch.object(script, "load_daily_panel", return_value=rows), mock.patch.object(script, "audit_panel"):
            kept = script.panel_rows(Path("unused"), "tgt")
        self.assertEqual([row.date for row in kept], [date(2025, 12, 31)])


class FinishedWalkTests(unittest.TestCase):
    def test_a_walk_is_finished_only_for_its_own_target_lead_panel_and_declaration(self):
        digest = script.hashlib.sha256(script.DECLARATION.read_bytes()).hexdigest()
        document = {"target": "t", "horizon": 2, "panel_sha256": "p", "declaration_sha256": digest, "laws": {}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "walk.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            self.assertTrue(script.finished(path, "t", 2, "p"))
            self.assertFalse(script.finished(path, "t", 3, "p"))
            self.assertFalse(script.finished(path, "u", 2, "p"))
            self.assertFalse(script.finished(path, "t", 2, "q"))
            self.assertFalse(script.finished(Path(directory) / "missing.json", "t", 2, "p"))


class ReadingTests(unittest.TestCase):
    def result(self, lower_bound, ample, scarce):
        return {
            "pooled": {"B1 -> model": {"mean_difference_lower_95_one_sided": lower_bound}},
            "lead_on_onsets": {"cells": {"model_median": {"ample": ample, "scarce": scarce}}},
        }

    def test_skill_needs_the_lower_bound_above_zero(self):
        low = {"onsets": 4, "auc_low": 0.6}
        self.assertEqual(script.readings(self.result(0.01, low, low)), (True, True))
        self.assertEqual(script.readings(self.result(0.0, low, low))[0], False)
        self.assertEqual(script.readings(self.result(-0.2, low, low))[0], False)

    def test_a_lead_needs_every_state_with_three_onsets_above_one_half(self):
        up = {"onsets": 4, "auc_low": 0.6}
        down = {"onsets": 23, "auc_low": 0.45}
        few = {"onsets": 2}
        self.assertTrue(script.readings(self.result(1.0, up, up))[1])
        self.assertFalse(script.readings(self.result(1.0, up, down))[1])
        self.assertTrue(script.readings(self.result(1.0, few, up))[1])  # a state with fewer than 3 onsets is not read
        self.assertFalse(script.readings(self.result(1.0, few, few))[1])  # no state is readable: no lead is shown


if __name__ == "__main__":
    unittest.main()


def _cell(lower):
    return {"skill": 0.1, "skill_lower_95_one_sided": lower}


def _result(lower_b1, lower_b2=0.1, auc=0.55):
    tests = {"B1 -> model": _cell(lower_b1), "B2 -> model": _cell(lower_b2)}
    band = {"onsets": 5, "auc": auc, "auc_low": auc - 0.1, "auc_high": auc + 0.1}
    return {
        "decision_days": {"n": 100},
        "pooled": tests,
        "by_lead": {str(h): {"tests": tests} for h in script.HORIZONS},
        "by_state": {"ample": {"n": 60, "tests": tests}},
        "by_day_type": {"month_end": {"decision_days": 30, "tests": tests}},
        "lead_on_onsets": {"cells": {"model_median": {"ample": band, "scarce": band}}},
    }


class SensitivityTests(unittest.TestCase):
    """#902: the same score with and without decision day 2019-09-18."""

    def document(self, lower_with, lower_without):
        return {"dropped_day": "2019-09-18", "targets": {"t": {"with": _result(lower_with), "without": _result(lower_without)}}}

    def test_a_with_column_that_differs_from_the_tracked_score_is_named(self):
        tracked = {"a": {"x": 1}, "b": {"x": 2}}
        self.assertEqual(script.reproduces({"a": {"x": 1}, "b": {"x": 3}}, tracked), ["b"])
        self.assertEqual(script.reproduces(tracked, tracked), [])

    def test_a_missing_target_does_not_reproduce(self):
        self.assertEqual(script.reproduces({}, {"a": {"x": 1}}), ["a"])

    def test_a_bound_that_changes_sign_is_listed_in_every_cut_it_changes(self):
        changes = script.sign_changes(self.document(0.05, -0.02))
        self.assertTrue(changes)
        self.assertTrue(any("pooled" in c and "over B1" in c for c in changes))
        self.assertFalse(any("over B2" in c for c in changes))

    def test_bounds_on_the_same_side_are_not_listed(self):
        self.assertEqual(script.sign_changes(self.document(0.05, 0.01)), [])

    def test_the_page_is_labelled_and_states_the_sign_changes(self):
        page = script.sensitivity_markdown(self.document(0.05, -0.02))
        self.assertIn("not a verdict", page)
        self.assertIn("## Interval bounds that change sign", page)
        self.assertIn("lower bound +0.050 with the day, -0.020 without", page)
        self.assertIn("None: no lower bound", script.sensitivity_markdown(self.document(0.05, 0.01)))
