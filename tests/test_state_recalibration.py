"""State-conditioned recalibration of the best row (#589): the shrinkage curve, the declaration and the run's guards.

`group_calibration.fit_shrunk` is a Platt curve on the pooled earlier pairs with one intercept offset per group,
shrunk toward zero by a ridge penalty (a hierarchical intercept). It sees only pairs whose scored day is at or before
its fitting date.

Recorded mutations, 12 October 2026, in a disposable copy:

* `src/repo_model/group_calibration.py`, `fit_shrunk`: the line `require_observable(pairs, fitted_at)` replaced by `pass`.
  `ShrunkLeakageTests.test_a_pair_after_the_fitting_date_is_refused` then failed with
  `AssertionError: LookAheadError not raised`.
* `scripts/state_recalibration_589.py`, `run_command`: the line `require_unlocked([last], where="state_recalibration_589")`
  replaced by `pass`. `RunGuardTests.test_run_refuses_a_locked_last_day` then errored with
  `TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'` (the guard is skipped and the run goes on to read the
  parent's forecasts from a path that is not there).
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

from repo_model import group_calibration as gc, probability_calibration as pc
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "state_recalibration_589.json").read_text())
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("state_recalibration_589_script", ROOT / "scripts" / "state_recalibration_589.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["state_recalibration_589_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


def _pairs(count=600, seed=3, scarce_lift=4.0):
    """`(day, forecast, outcome, group)` where the scarce group's outcomes run above the forecast."""

    rng = random.Random(seed)
    start = date(2018, 1, 1)
    out = []
    for k in range(count):
        group = "2" if k % 7 == 0 else "0"
        p = min(0.9, max(0.01, rng.betavariate(0.7, 6.0)))
        q = min(0.95, p * scarce_lift) if group == "2" else p
        out.append((start + timedelta(days=k), p, 1 if rng.random() < q else 0, group))
    return out


def _series(count=900, seed=11, block=21, horizon=1):
    pairs = _pairs(count, seed)
    dates = [d for d, _, _, _ in pairs]
    train_ends = [dates[(k // block) * block] - timedelta(days=horizon) for k in range(count)]
    return dates, train_ends, [p for _, p, _, _ in pairs], [y for _, _, y, _ in pairs], [g for _, _, _, g in pairs]


class ShrunkCurveTests(unittest.TestCase):
    def test_a_huge_precision_is_the_pooled_platt_curve(self):
        pairs = _pairs()
        fitted_at = pairs[-1][0]
        shrunk = gc.fit_shrunk(pairs, fitted_at, precision=1e12)
        pooled = pc._platt([(p, y) for _, p, y, _ in pairs])
        for p in (0.02, 0.1, 0.4):
            for group in ("0", "2"):
                self.assertAlmostEqual(shrunk(p, group), pooled(p), places=6)

    def test_a_group_whose_outcomes_run_high_gets_a_higher_curve_than_one_that_does_not(self):
        pairs = _pairs()
        shrunk = gc.fit_shrunk(pairs, pairs[-1][0])
        self.assertGreater(shrunk(0.1, "2"), shrunk(0.1, "0"))

    def test_the_offset_is_pulled_toward_zero_more_when_the_group_is_thin(self):
        pairs = _pairs(count=900)
        rich = [p for p in pairs]
        thin = [p for p in pairs if p[3] == "0"] + [p for p in pairs if p[3] == "2"][:20]
        gap = lambda data: (
            lambda curve: curve(0.1, "2") - curve(0.1, "0")
        )(gc.fit_shrunk(data, pairs[-1][0]))
        self.assertGreater(gap(rich), gap(thin))

    def test_a_larger_precision_shrinks_the_offset_more(self):
        pairs = _pairs()
        gaps = []
        for precision in (0.1, 1.0, 100.0):
            curve = gc.fit_shrunk(pairs, pairs[-1][0], precision=precision)
            gaps.append(curve(0.1, "2") - curve(0.1, "0"))
        self.assertGreater(gaps[0], gaps[1])
        self.assertGreater(gaps[1], gaps[2])

    def test_a_group_with_no_earlier_pair_gets_the_pooled_curve(self):
        pairs = _pairs()
        curve = gc.fit_shrunk(pairs, pairs[-1][0])
        pooled = pc._platt([(p, y) for _, p, y, _ in pairs])
        self.assertAlmostEqual(curve(0.1, "never seen"), pooled(0.1), places=6)

    def test_a_precision_that_is_not_positive_is_refused(self):
        pairs = _pairs()
        for bad in (0.0, -1.0):
            with self.assertRaises(ValueError):
                gc.fit_shrunk(pairs, pairs[-1][0], precision=bad)


class ShrunkLeakageTests(unittest.TestCase):
    def test_a_pair_after_the_fitting_date_is_refused(self):
        pairs = _pairs()
        with self.assertRaises(LookAheadError):
            gc.fit_shrunk(pairs, pairs[-2][0])


class ShrunkWalkForwardTests(unittest.TestCase):
    def test_nothing_is_fitted_before_the_pooled_gate(self):
        dates, ends, forecasts, outcomes, groups = _series()
        column = gc.walk_forward_shrunk(forecasts, outcomes, dates, ends, groups)
        early = [k for k in range(len(dates)) if len(pc.past_positions(dates, ends, k)) < pc.MINIMUM_PAIRS]
        self.assertTrue(early)
        for k in early:
            self.assertEqual(column[k], forecasts[k])

    def test_a_later_outcome_does_not_move_an_earlier_forecast(self):
        dates, ends, forecasts, outcomes, groups = _series()
        base = gc.walk_forward_shrunk(forecasts, outcomes, dates, ends, groups)
        cut = 600
        flipped = list(outcomes)
        for k in range(cut, len(flipped)):
            flipped[k] = 1 - flipped[k]
        again = gc.walk_forward_shrunk(forecasts, flipped, dates, ends, groups)
        self.assertEqual(base[:cut], again[:cut])
        self.assertNotEqual(base[cut:], again[cut:])

    def test_the_columns_must_be_one_per_scored_day(self):
        dates, ends, forecasts, outcomes, groups = _series()
        with self.assertRaises(ValueError):
            gc.walk_forward_shrunk(forecasts, outcomes, dates, ends, groups[:-1])

    def test_it_improves_the_brier_score_of_a_forecast_that_misses_one_group(self):
        dates, ends, forecasts, outcomes, groups = _series(count=1800, seed=5)
        column = gc.walk_forward_shrunk(forecasts, outcomes, dates, ends, groups)
        late = range(900, len(dates))
        brier = lambda col: sum((col[k] - outcomes[k]) ** 2 for k in late)
        self.assertLess(brier(column), brier(forecasts))


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())), DECLARED)

    def test_at_most_three_variants_and_the_parent_is_the_best_row(self):
        self.assertLessEqual(len(DECLARED["variants"]), 3)
        self.assertEqual(DECLARED["parent"]["row"], "risk_gbm+every_day+gate+settle+h41+iorb")
        self.assertEqual(DECLARED["parent"]["row"], SCRIPT.PARENT)

    def test_variant_b_is_not_run_while_587_is_unmerged(self):
        b = next(v for v in DECLARED["variants"] if v["id"] == "b")
        self.assertFalse(b["run"])
        self.assertEqual(SCRIPT.RUN_VARIANTS, ("a", "c"))

    def test_the_constants_are_the_declared_ones_and_none_was_searched(self):
        self.assertEqual(DECLARED["constants"]["shrinkage_precision"], gc.SHRINKAGE_PRECISION)
        self.assertEqual(DECLARED["constants"]["group_minimum_pairs"], gc.GROUP_MINIMUM_PAIRS)
        self.assertEqual(DECLARED["constants"]["group_minimum_events"], gc.GROUP_MINIMUM_EVENTS)
        self.assertIn("none", DECLARED["constants"]["searched"])

    def test_no_hindsight_regime_label_is_used(self):
        self.assertIn("as of the decision instant", DECLARED["conditioning_variable"])
        self.assertIn("515", DECLARED["conditioning_variable"])

    def test_the_scoring_ends_before_the_lockbox(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_the_rows_are_candidates_of_the_judge_and_not_in_the_published_declaration(self):
        published = (ROOT / "metadata" / "pressure_judge.json").read_text()
        for name in SCRIPT.VARIANT_NAMES.values():
            self.assertTrue((CANDIDATES / f"{name}.json").is_file(), name)
            self.assertNotIn(name, published)

    def test_the_candidate_files_are_what_the_script_declares(self):
        for variant, name in SCRIPT.VARIANT_NAMES.items():
            self.assertEqual(SCRIPT.candidate_document(variant), json.loads((CANDIDATES / f"{name}.json").read_text()))


class GroupLabelTests(unittest.TestCase):
    def test_the_label_is_the_as_of_state_and_no_other_key(self):
        scored = [date(2025, 9, 15), date(2025, 9, 16), date(2025, 9, 17)]
        labels = SCRIPT.state_labels(scored, {scored[0]: 2.0, scored[1]: 1.0})
        self.assertEqual(labels, ["2", "1", "unknown"])

    def test_a_state_outside_zero_to_three_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.state_labels([date(2025, 9, 15)], {date(2025, 9, 15): 4.0})


class RunGuardTests(unittest.TestCase):
    def test_run_refuses_a_locked_last_day(self):
        declared = dict(DECLARED, scoring=dict(DECLARED["scoring"], last_day="2026-10-01"))
        args = mock.Mock(horizon=1, panel=Path("/nonexistent"), published=Path("/nonexistent"), parent=Path("/nonexistent"))
        with mock.patch.object(SCRIPT.rds, "committed_declaration", return_value=declared):
            with self.assertRaises(LookAheadError):
                SCRIPT.run_command(args)


if __name__ == "__main__":
    unittest.main()
