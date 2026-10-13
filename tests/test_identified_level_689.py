"""Identified estimators for the satiation level (#689, finding #671): `structural_liquidity` forms `kinked_profile` and
`kinked_slow`, and `metadata/identified_level_689.json`.

`satiation.fit_level` picks the kink by least squares of the spread level on a hinge, an objective that is not the
logistic it feeds; its fitted level jumped between refits. Two declared alternatives pick it from the logistic itself:

* `kinked_profile` (a): at each refit the level on `satiation.KINK_GRID` that minimises the ridge logistic's own objective
  (the profile), on the training pairs' +5 bp labels alone;
* `kinked_slow` (b): the same profile, with a quadratic penalty on the change from the previous refit's level.

What is covered:

* `ProfileTests` -- the profile recovers a planted kink from the logistic's own objective, flags a flat profile, counts
  local minima, and reads nothing but the pairs it is given.
* `ChoiceTests` -- the penalty is zero for (a), pulls (b) toward the previous level, and starts from the fixed 0.12.
* `PredictorTests` -- both forms forecast every day under the fold loop's guards, record the level, its interval and its
  minima at every refit, and a refit's level is unmoved by rows after its training end.
* `DeclarationTests` -- `metadata/identified_level_689.json` says what the module computes.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run
alone, each confirmed applied by `grep` and restored before the next):

1. `structural_exceedance.fit_predict` (profile forms): replace `_profile_level(design, xs, spreads, taus, state, penalty)`
   by `_profile_level(design, xs + served, list(spreads) + [0.0] * len(served), taus, state, penalty)`. The refit's level
   then reads the rows it forecasts, which are after its training end;
   `PredictorTests.test_a_profile_level_is_unmoved_by_rows_after_the_training_end` fails with an `AssertionError` (the refit's
   profile interval, `[0.115, 0.2]` for `kinked_profile`, differs from the unmutated refit's).
"""

from __future__ import annotations

import json
import random
import unittest
from datetime import date, time
from pathlib import Path

from repo_model import satiation as sat, scarcity, structural_liquidity as sl
from repo_model.baseline import rolling_exceedance_backtest
from repo_model.data import DailyObservation
from test_satiation import SPLITS, _Measured, _panel, _require_extra

REPO = Path(__file__).resolve().parents[1]
DECLARATION = REPO / "metadata" / "identified_level_689.json"


def planted(kink=0.11, n=600, seed=3, slope=1.2):
    """Raw design rows (`RAW_NAMES`) and +5 bp labels generated from the kinked model at `kink`."""

    rng = random.Random(seed)
    raws, labels = [], []
    for _ in range(n):
        ratio = 0.09 + 0.07 * rng.random()
        short = 40.0 * rng.random()
        e = sl.elasticity(ratio, kink, True)
        p = 1.0 / (1.0 + pow(2.718281828, -(-3.0 + slope * (e * short / 10.0))))
        raws.append([0.5, ratio, short, 0.0, 0.0, 0.0])
        labels.append(1 if rng.random() < p else 0)
    return raws, labels


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.design = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "kinked_profile")

    def test_a_planted_kink_is_recovered_from_the_logistic_itself(self):
        for kink in (0.11, 0.13):
            raws, labels = planted(kink)
            curve = sl.profile_curve(self.design, raws, labels)
            level, info = sl.choose_profile_level(sat.KINK_GRID, curve, len(raws))
            self.assertLess(abs(level - kink), 0.015, (kink, level))
            self.assertTrue(info["interval"][0] <= level <= info["interval"][1])

    def test_the_curve_has_one_entry_per_grid_point_and_a_minimum_of_zero_excess(self):
        raws, labels = planted()
        curve = sl.profile_curve(self.design, raws, labels)
        self.assertEqual(len(curve), len(sat.KINK_GRID))
        level, info = sl.choose_profile_level(sat.KINK_GRID, curve, len(raws))
        self.assertEqual(min(info["excess"]), 0.0)
        self.assertEqual(info["excess"][list(sat.KINK_GRID).index(level)], 0.0)

    def test_a_label_free_of_the_ratio_has_a_wide_interval(self):
        raws, _ = planted()
        rng = random.Random(5)
        labels = [1 if rng.random() < 0.2 else 0 for _ in raws]
        level, info = sl.choose_profile_level(sat.KINK_GRID, sl.profile_curve(self.design, raws, labels), len(raws))
        width = info["interval"][1] - info["interval"][0]
        raws2, labels2 = planted()
        _l2, info2 = sl.choose_profile_level(sat.KINK_GRID, sl.profile_curve(self.design, raws2, labels2), len(raws2))
        self.assertGreater(width, info2["interval"][1] - info2["interval"][0])

    def test_local_minima_are_counted(self):
        grid = (0.10, 0.11, 0.12, 0.13, 0.14)
        info = sl.choose_profile_level(grid, [5.0, 3.0, 4.0, 1.0, 2.0], 100)[1]
        self.assertEqual(info["local_minima"], 2)
        self.assertEqual(sl.choose_profile_level(grid, [5.0, 4.0, 3.0, 2.0, 1.0], 100)[1]["local_minima"], 1)

    def test_a_change_in_a_training_row_changes_the_curve(self):
        raws, labels = planted(n=400)
        first = sl.profile_curve(self.design, raws, labels)
        changed = [list(r) for r in raws]
        changed[7][1] = 0.0912
        self.assertNotEqual(first, sl.profile_curve(self.design, changed, labels))
        self.assertEqual(first, sl.profile_curve(self.design, raws, labels))


class ChoiceTests(unittest.TestCase):
    grid = (0.10, 0.11, 0.12, 0.13, 0.14)
    curve = [6.0, 2.0, 5.0, 0.0, 1.0]

    def test_no_penalty_is_the_profile_minimum(self):
        self.assertEqual(sl.choose_profile_level(self.grid, self.curve, 100, previous=0.10, penalty=0.0)[0], 0.13)

    def test_a_penalty_pulls_the_level_toward_the_previous_one(self):
        # excess per pair: 0.06, 0.02, 0.05, 0.0, 0.01; moving 3 points from 0.10 to 0.13 costs 9 * penalty per pair
        near = sl.choose_profile_level(self.grid, self.curve, 100, previous=0.10, penalty=0.01)[0]
        far = sl.choose_profile_level(self.grid, self.curve, 100, previous=0.10, penalty=0.0)[0]
        self.assertLess(near, far)
        self.assertEqual(sl.choose_profile_level(self.grid, self.curve, 100, previous=0.10, penalty=100.0)[0], 0.10)

    def test_the_penalty_is_per_pair_so_a_scaled_sample_makes_the_same_choice(self):
        # the same excess per pair on twice the pairs (twice the nats) is the same choice
        for penalty in (0.0, 0.003, 0.01):
            one = sl.choose_profile_level(self.grid, self.curve, 100, previous=0.10, penalty=penalty)[0]
            two = sl.choose_profile_level(self.grid, [2.0 * v for v in self.curve], 200, previous=0.10, penalty=penalty)[0]
            self.assertEqual(one, two)

    def test_a_missing_fit_is_never_chosen(self):
        self.assertEqual(sl.choose_profile_level(self.grid, [None, None, 5.0, None, 9.0], 100)[0], 0.12)
        with self.assertRaises(ValueError):
            sl.choose_profile_level(self.grid, [None] * 5, 100)

    def test_the_declared_penalty_and_forms(self):
        self.assertEqual(sl.PROFILE_PENALTY, 0.001)
        self.assertEqual(sl.KINKED_FORMS["kinked_profile"], "profile")
        self.assertEqual(sl.KINKED_FORMS["kinked_slow"], "profile")
        self.assertIn("kinked_profile", sl.STRUCTURAL_FORMS)
        self.assertIn("kinked_slow", sl.STRUCTURAL_FORMS)
        # the profile forms read the same columns as the fixed form; the level comes from the refit
        self.assertEqual(sl.features_at_horizon(1, "kinked_profile"), sl.features_at_horizon(1))
        design = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "kinked_slow")
        self.assertTrue(design.kinked)


class PredictorTests(_Measured):
    """Both forms under the fold loop's guards, on a panel whose pressure follows a planted kink."""

    def setUp(self):
        _require_extra(self)
        super().setUp()
        self.rows = _panel(700)
        blocks = (0.095, 0.15, 0.105, 0.14, 0.11, 0.16, 0.10, 0.145, 0.115, 0.155, 0.1, 0.15)
        for index, row in enumerate(self.rows):
            ratio = blocks[(index // 55) % len(blocks)]
            row.values["reserve_balances"] = 26000.0 * ratio
            row.values["net_settlement_ahead_1d"] = 300.0 if index % 4 == 0 else 0.0
            row.values["on_rrp"] = 5.0
            row.values["sofr"] = 4.0 + (8.0 if (index % 4 == 1 and ratio < 0.12) else -1.0) / 100.0

    def structural(self, form, rows=None):
        features = sl.features_at_horizon(1, form)
        predictor = sl.structural_exceedance(features, SPLITS, minimum_history=61, satiation=form)
        data = sat.build_columns(
            self.rows if rows is None else rows, self.rule(), last_day=date(2025, 12, 31), q=0.1, window=100, minimum=20
        )
        with scarcity.measurement_declaration():
            report = rolling_exceedance_backtest(
                data, predictor=predictor, model_name="structural_" + form, features=features, registry=self.registry,
                decision_time=time(16, 0),
                taus=(5.0, 10.0), minimum_history=61, refit_every=21, horizon=1,
            )
        return report, predictor

    def test_both_forms_forecast_every_day_and_record_the_level_its_interval_and_minima(self):
        for form in ("kinked_profile", "kinked_slow"):
            report, predictor = self.structural(form)
            self.assertTrue(report.scored_dates, form)
            self.assertTrue(all(0.0 < p[0] < 1.0 for p in report.forecast), form)
            fitted = [f for f in predictor.fits if f["fitted"]]
            self.assertTrue(fitted, form)
            for record in fitted:
                self.assertIn(record["satiation_level"], sat.KINK_GRID)
                self.assertEqual(len(record["interval"]), 2)
                self.assertGreaterEqual(record["local_minima"], 1)
            # the first refits have too few pairs: the fixed level
            self.assertEqual(predictor.fits[0]["satiation_level"], sat.FIXED)
            self.assertFalse(predictor.fits[0]["fitted"])

    def test_the_slow_level_moves_no_more_than_the_profile_level(self):
        _r1, profile = self.structural("kinked_profile")
        _r2, slow = self.structural("kinked_slow")
        path = lambda p: [f["satiation_level"] for f in p.fits]  # noqa: E731
        travel = lambda levels: sum(abs(b - a) for a, b in zip(levels, levels[1:]))  # noqa: E731
        self.assertLessEqual(travel(path(slow)), travel(path(profile)) + 1e-12)
        for f in slow.fits:
            if f["fitted"]:
                self.assertIn("profile_level", f)
                self.assertIn("previous_level", f)

    def test_a_profile_level_is_unmoved_by_rows_after_the_training_end(self):
        for form in ("kinked_profile", "kinked_slow"):
            _report, predictor = self.structural(form)
            first = next(f for f in predictor.fits if f["fitted"])
            end = [r.date.isoformat() for r in self.rows].index(first["last_training_row"])
            changed = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
            for later in changed[end + 1:]:
                later.values["sofr"] = 4.0 + 0.30
                later.values["reserve_balances"] = 26000.0 * 0.20
            _report2, predictor2 = self.structural(form, changed)
            again = next(f for f in predictor2.fits if f["last_training_row"] == first["last_training_row"])
            self.assertTrue(again["fitted"], form)
            self.assertEqual(first["satiation_level"], again["satiation_level"], form)
            self.assertEqual(first["interval"], again["interval"], form)

    def test_a_refit_with_one_class_keeps_the_fixed_level_and_says_why(self):
        for row in self.rows:
            row.values["sofr"] = 4.0 - 0.01
        _report, predictor = self.structural("kinked_profile")
        self.assertTrue(all(f["satiation_level"] == sat.FIXED and not f["fitted"] for f in predictor.fits))
        self.assertIn("no", predictor.fits[-1]["reason"])


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(DECLARATION.read_text())

    def test_the_declaration_says_what_the_module_computes(self):
        self.assertEqual(self.document["issue"], 689)
        self.assertEqual(self.document["penalty_per_pair"], sl.PROFILE_PENALTY)
        self.assertEqual(self.document["grid"], [min(sat.KINK_GRID), max(sat.KINK_GRID), 0.0025])
        self.assertEqual(self.document["minimum_pairs"], sat.KINK_MINIMUM_PAIRS)
        self.assertEqual(self.document["fixed_level"], sat.FIXED)
        self.assertEqual(sorted(self.document["variants"]), ["structural_kinked_profile", "structural_kinked_slow"])
        for name, spec in self.document["variants"].items():
            self.assertIn(spec["form"], sl.KINKED_FORMS)
        self.assertEqual(self.document["scoring"]["last_day"], "2025-12-31")
        self.assertEqual(self.document["horizons"], [1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
