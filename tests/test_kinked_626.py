"""A kinked elasticity in the structural model (#626, ruling on #597): `metadata/kinked_626.json` and `scripts/kinked_626.py`.

The elasticity's own arithmetic and the fitted-level guard are in `tests/test_satiation.py` (`DesignTests`, `PredictorTests`). What is
covered here:

* `DeclarationTests` -- the declaration is written before any score, is at most two variants plus the current form as control, agrees with
  the module (the forms, the length, the fixed level), and has a judge candidate file for every row; the inputs are off in the published
  feature map; the sign of the exponent is the declared one and the literal reading is recorded, not scored.
* `ReliabilityTests` -- the reliability line (#616) recovers a planted intercept and slope and is not identified for a constant forecast.
* `RunGuardTests` -- `run`, `panel` and `extras` refuse a scored day in a locked tier (`docs/decisions/lockbox.md`).

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, each
confirmed applied by `grep` and restored before the next):

1. `run_command`: replace `require_unlocked([last], where="kinked_626")` by `pass`; `RunGuardTests.test_run_refuses_a_locked_last_day`
   fails with `FileNotFoundError` (the guard is skipped and the run goes on to read the panel).
2. `panel_command`: replace `require_unlocked([end], where="kinked_626")` by `pass`; `RunGuardTests.test_panel_refuses_a_locked_last_day`
   fails with `FileNotFoundError` (the guard is skipped and the build goes on to read the panel).
3. `structural_liquidity.elasticity`: replace `max(0.0, float(satiation) - float(ratio))` by `float(satiation) - float(ratio)` (the kink
   removed); `tests/test_satiation.py` `DesignTests.test_the_kinked_elasticity_is_flat_above_the_level_and_exponential_below_it` fails with
   `AssertionError: 0.049787068367863944 != 1.0`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
import unittest
from pathlib import Path
from unittest import mock

from repo_model import contract, satiation as sat, scarcity, structural_liquidity as sl
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
DECLARATION = REPO / "metadata" / "kinked_626.json"
CANDIDATES = REPO / "metadata" / "pressure_judge" / "candidates"


def _script():
    sys.path.insert(0, str(REPO / "src"))
    spec = importlib.util.spec_from_file_location("kinked_626_script", REPO / "scripts" / "kinked_626.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["kinked_626_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


def _declared():
    """The declaration file as read, without the script's committed-and-unchanged check (a working tree may be dirty)."""

    return json.loads(DECLARATION.read_text())


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = _declared()

    def test_at_most_two_variants_plus_the_current_form_as_control(self):
        self.assertEqual(sorted(self.document["variants"]), ["structural_kinked_fitted", "structural_kinked_rolling"])
        self.assertEqual(self.document["rows"]["new"], ["structural_kinked_fitted", "structural_kinked_rolling"])
        self.assertIn("structural_liquidity", self.document["rows"]["controls"])

    def test_every_variant_names_a_form_the_module_computes(self):
        for name, spec in self.document["variants"].items():
            self.assertIn(spec["form"], sl.KINKED_FORMS, name)
        self.assertEqual(sl.KINKED_FORMS["kinked_fitted"], "fitted")
        self.assertEqual(sl.KINKED_FORMS["kinked_rolling"], "rolling")

    def test_the_constants_are_the_modules(self):
        self.assertEqual(self.document["fixed_level"], sat.FIXED)
        self.assertEqual(self.document["elasticity"]["length"], sl.LENGTH)
        self.assertEqual(sl.SATIATION, 0.12)
        self.assertEqual(scarcity.SATIATION_BAND, (0.12, 0.13))

    def test_the_declared_sign_is_the_growing_one_and_the_literal_reading_is_recorded(self):
        self.assertAlmostEqual(sl.elasticity(0.10, 0.12, kinked=True), math.exp(2.0))
        note = self.document["elasticity"]["sign_note"]
        self.assertIn("exp(-max(0, level - ratio) / 0.01)", note)
        self.assertIn("not scored", note)

    def test_a_candidate_file_exists_for_every_row(self):
        names = list(self.document["rows"]["controls"]) + list(self.document["rows"]["new"]) + [self.document["rows"]["comparator"]]
        for name in names:
            entry = json.loads((CANDIDATES / f"{name}.json").read_text())
            self.assertEqual(entry["role"], "candidate", name)
        rolling = json.loads((CANDIDATES / "structural_kinked_rolling.json").read_text())
        self.assertIn(sat.ROLLING_COLUMN, rolling["features"])

    def test_every_row_is_paired_with_a_declared_row(self):
        rows = set(self.document["rows"]["controls"]) | set(self.document["rows"]["new"])
        for name, partner in self.document["rows"]["pairs"].items():
            self.assertIn(name, rows)
            self.assertIn(partner, rows)

    def test_the_scored_window_ends_before_the_locked_tiers(self):
        self.assertEqual(self.document["scoring"]["last_day"], "2025-12-31")

    def test_the_satiation_columns_are_off_in_the_published_feature_map(self):
        for column in (sat.ROLLING_COLUMN, sat.DISTANCE_COLUMN, sat.HINGE_COLUMN):
            self.assertNotIn(column, contract.FEATURE_FIELDS)

    def test_the_references_hold_no_row_twice(self):
        refs = self.document["references"]
        listed = refs["pair_against"] + refs["controls"] + refs["risk_date_passers"]
        self.assertEqual(len(listed), len(set(listed)) + len(set(refs["pair_against"]) & set(refs["risk_date_passers"])))


class ReliabilityTests(unittest.TestCase):
    def sample(self, intercept, slope, n=6000, seed=3):
        rng = random.Random(seed)
        p, y = [], []
        for _ in range(n):
            q = rng.uniform(0.02, 0.6)
            z = intercept + slope * math.log(q / (1.0 - q))
            p.append(q)
            y.append(1 if rng.random() < 1.0 / (1.0 + math.exp(-z)) else 0)
        return p, y

    def test_a_calibrated_forecast_has_intercept_zero_and_slope_one(self):
        a, b = SCRIPT.reliability(*self.sample(0.0, 1.0))
        self.assertAlmostEqual(a, 0.0, delta=0.15)
        self.assertAlmostEqual(b, 1.0, delta=0.12)

    def test_a_planted_intercept_and_slope_are_recovered(self):
        a, b = SCRIPT.reliability(*self.sample(-0.6, 0.5))
        self.assertAlmostEqual(a, -0.6, delta=0.15)
        self.assertAlmostEqual(b, 0.5, delta=0.12)

    def test_a_constant_forecast_or_one_class_has_no_line(self):
        self.assertIsNone(SCRIPT.reliability([0.1] * 50, [0, 1] * 25))
        self.assertIsNone(SCRIPT.reliability([0.1, 0.2, 0.3], [0, 0, 0]))
        self.assertIsNone(SCRIPT.reliability([0.1, 0.2, 0.3], [1, 1, 1]))

    def test_the_interval_is_the_declared_quantiles_and_none_when_most_draws_are_undefined(self):
        self.assertEqual(SCRIPT._interval([1.0, 2.0, 3.0, 4.0, 5.0], 0.5), [2.0, 4.0])
        self.assertIsNone(SCRIPT._interval([None, None, 1.0], 0.9))


class RunGuardTests(unittest.TestCase):
    def args(self, **changes):
        base = dict(horizon=1, panel=REPO / "no-such-panel.csv", published=REPO / "no-such-panel.csv",
                    output=REPO / "no-such-output.json", scratch=REPO / "no-such-panel.csv", bench="x", parents="x", rows="x", markdown=None)
        base.update(changes)
        return argparse.Namespace(**base)

    def locked(self):
        declared = _declared()
        declared["scoring"]["last_day"] = "2026-09-10"
        return declared

    def test_run_refuses_a_locked_last_day(self):
        with mock.patch.object(SCRIPT, "declared_document", return_value=self.locked()):
            with self.assertRaises(LookAheadError):
                SCRIPT.run_command(self.args())

    def test_the_declared_last_day_is_not_refused(self):
        with mock.patch.object(SCRIPT, "declared_document", return_value=_declared()), mock.patch.object(
            SCRIPT, "load_daily_panel", side_effect=FileNotFoundError
        ):
            with self.assertRaises(FileNotFoundError):  # past the guard, into the panel
                SCRIPT.run_command(self.args())

    def test_panel_refuses_a_locked_last_day(self):
        with mock.patch.object(SCRIPT, "declared_document", return_value=self.locked()):
            with self.assertRaises(LookAheadError):
                SCRIPT.panel_command(argparse.Namespace(panel=REPO / "x.csv", output=REPO / "y.csv", check_every=40))

    def test_extras_refuses_a_locked_last_day(self):
        with mock.patch.object(SCRIPT, "declared_document", return_value=self.locked()):
            with self.assertRaises(LookAheadError):
                SCRIPT.extras_command(self.args())


if __name__ == "__main__":
    unittest.main()
