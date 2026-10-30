"""The measurement script of #706 (`scripts/richer_targets_706.py`): the parts that decide what is scored and what is read.

Recorded mutation (the one guard this script adds; the scorer's own lockbox guard is tested with the scorer):

* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`; the blind tier is every day after 2026-09-03, `metadata/lockbox.json`).

Direct pairs (#932, review of 8ddde376; Eleonora's ruling of 19 October 2026 on #915): the walks fit on `training_pairs="direct"`,
because `new_features(h)` holds columns the as-of rule serves from the scored row (`tax_date`, `treasury_settlement`, and at lead 1
the announced-IORB pair), which a one-step fit would learn one row off (`one_step_guard`, #914). Recorded mutation, CPython 3.11,
`/opt/rmm-venv`, the killing test run alone, mutation confirmed applied by `grep` and reverted:

* `target_fitter`, the keyword `training_pairs="direct"` removed (the one-step fit of #706 as first written):
  `PairingTests.test_the_walks_fit_passes_the_one_step_guard_at_every_lead` fails with `AssertionError: None != 'direct'`
  (and, with that assertion off, the fitter itself raises the guard's `ValueError` naming `tax_date` and `treasury_settlement`,
  and at lead 1 the announced-IORB pair).
* `check_pairing`, `if named != "direct":` replaced by `if False:`: `PairingTests.test_a_walk_fitted_on_one_step_pairs_is_refused`
  fails with `AssertionError: ValueError not raised`.
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


class PairingTests(unittest.TestCase):
    def test_the_walks_fit_passes_the_one_step_guard_at_every_lead(self):
        """The guard sits on the fitter's def line: a direct fit is not checked, a one-step fit over these inputs raises ValueError."""

        from repo_model import ml, one_step_guard

        for h in script.HORIZONS:
            with self.subTest(lead=h):
                features = script.m634.new_features(h)
                regressors = tuple(f for f in features if f != "spread_bps")
                with self.assertRaises(ValueError):  # premise: these inputs are refused on one-step pairs
                    one_step_guard.check_one_step_regressors("fit_gradient_boosted_quantiles", regressors)
                fit = script.target_fitter(features)
                self.assertEqual(fit.keywords.get("training_pairs"), "direct")
                self.assertIs(fit.func, ml.fit_gradient_boosted_quantiles)
                try:
                    fit([], information=None)
                except ValueError as error:  # an empty frame is refused by the fitter itself, but only after the guard has passed
                    self.assertNotIn("one-step pairs", str(error))

    def test_a_walk_fitted_on_one_step_pairs_is_refused(self):
        with self.assertRaises(ValueError):
            script.check_pairing({})
        with self.assertRaises(ValueError):
            script.check_pairing({"training_pairs": "one_step"})
        script.check_pairing({"training_pairs": "direct"})

    def test_the_declaration_names_the_pairing_and_the_amendment(self):
        declared = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(declared["model"]["training_pairs"], "direct")
        self.assertIn("932", json.dumps(declared["amendments"]))
        self.assertIn("19 October 2026", json.dumps(declared["amendments"]))


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
