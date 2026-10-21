"""Input attribution for `gbm_funding` (`scripts/gbm_attribution_964.py`, #964, H5 step 4): the parts that decide what is shuffled, scored and read.

Recorded mutations (the guard this script adds, and the bookkeeping the attribution rests on):

* `require_study_window`, the line `if late:` changed to `if False:`:
  `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with `AssertionError` (`LookAheadError not raised`).
* `block_attribution`, the score line `score(predict(with_value(design, position[name], order[i])), outcomes[i])` changed to score against
  `outcomes[(i + 1) % len(outcomes)]` (a shuffled forecast scored against another day's outcome):
  `AttributionTests.test_a_shuffled_forecast_is_scored_against_its_own_days_outcome` fails with `AssertionError` (`5.575... != 6.575... within 12 places`: the shuffled day's score is
  no longer the one computed by hand), and the ranking test fails too (`1.2339... != 0.0`: an ignored input shows an importance).
"""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gbm_attribution_964_script", REPO / "scripts" / "gbm_attribution_964.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

NAMES = ("spread_bps", "reserve_balances", "tbill_4w", "tga", "sofr_volume")


def known_model(design):
    """A 23-level law centred on the first column (spread_bps) and blind to every other column."""

    return [design[0] + 0.1 * k for k in range(len(script.GRID))]


def synthetic_block(n=40):
    rng = random.Random(7)
    designs = [[float(i % 10), rng.random(), rng.random(), rng.random(), rng.random()] for i in range(n)]
    outcomes = [design[0] + 1.1 for design in designs]  # the model's median is the truth plus a constant
    return designs, outcomes


def attribute(designs, outcomes, **kw):
    grid = {name: [0.0, 1.0, 2.0, 3.0, 4.0] for name in script.DEPENDENCE_INPUTS}
    sigmas = {name: 1.0 for name in script.DEPENDENCE_INPUTS}
    return script.block_attribution(known_model, designs, outcomes, NAMES, seed_key="1/2020-01-02", grid_points=grid, sigmas=sigmas, **kw)


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 30), date(2025, 12, 31)])


class AttributionTests(unittest.TestCase):
    def test_the_important_input_ranks_first_and_an_ignored_one_has_no_importance(self):
        designs, outcomes = synthetic_block()
        entries = attribute(designs, outcomes)
        importance = {name: script.mean([e["perm"][name] - e["base_score"] for e in entries]) for name in NAMES}
        self.assertGreater(importance["spread_bps"], 0.1)
        for name in NAMES[1:]:
            self.assertEqual(importance[name], 0.0)
        self.assertEqual(max(importance, key=importance.get), "spread_bps")

    def test_a_shuffled_forecast_is_scored_against_its_own_days_outcome(self):
        designs, outcomes = synthetic_block()
        entries = attribute(designs, outcomes, repeats=1)
        order = script.shuffled([d[0] for d in designs], random.Random(f"{script.SEED}/1/2020-01-02/spread_bps/0"))
        for i, entry in enumerate(entries):
            law = known_model([order[i]] + designs[i][1:])
            self.assertAlmostEqual(entry["perm"]["spread_bps"], sp.grid_crps(law, outcomes[i]), places=12)

    def test_a_short_block_is_not_shuffled(self):
        designs, outcomes = synthetic_block(script.MINIMUM_BLOCK - 1)
        entries = attribute(designs, outcomes)
        self.assertTrue(all(e["perm"][name] is None or e["perm"][name] == e["base_score"] for e in entries for name in NAMES))

    def test_the_dependence_and_the_shock_move_only_with_the_input_the_model_reads(self):
        designs, outcomes = synthetic_block()
        entry = attribute(designs, outcomes)[0]
        median = script.GRID.index(0.5)
        self.assertEqual([round(q[0] - entry["pd"]["spread_bps"][0][0], 9) for q in entry["pd"]["spread_bps"]], [0.0, 1.0, 2.0, 3.0, 4.0])
        self.assertEqual({q[0] for q in entry["pd"]["tga"]}, {entry["pd"]["tga"][0][0]})
        self.assertAlmostEqual(entry["shock"]["spread_bps"]["plus"][0] - entry["shock"]["spread_bps"]["minus"][0], 2.0)
        self.assertAlmostEqual(entry["shock"]["tga"]["plus"][0], entry["shock"]["tga"]["minus"][0])
        self.assertAlmostEqual(entry["base"][median], known_model(designs[0])[median])

    def test_the_shuffle_keeps_the_values_and_is_reproducible(self):
        column = [float(i) for i in range(20)]
        a = script.shuffled(column, random.Random("x"))
        self.assertEqual(sorted(a), column)
        self.assertEqual(a, script.shuffled(column, random.Random("x")))
        self.assertNotEqual(a, column)

    def test_mismatched_rows_are_refused(self):
        with self.assertRaises(ValueError):
            attribute([[0.0] * 5], [0.0, 1.0])


class ReadingTests(unittest.TestCase):
    def test_regimes_cover_the_study_window_without_overlap(self):
        self.assertEqual(script.regime_of(date(2019, 12, 31)), "2018-19")
        self.assertEqual(script.regime_of(date(2020, 1, 2)), "2020")
        self.assertEqual(script.regime_of(date(2025, 12, 31)), "2025")
        self.assertIsNone(script.regime_of(date(2026, 1, 2)))

    def test_quantile_and_grid(self):
        self.assertEqual(script.quantile_of([1.0, 2.0, 3.0, 4.0, 5.0], 0.5), 3.0)
        self.assertEqual(script.quantile_of([0.0, 10.0], 0.1), 1.0)
        columns = {name: [float(i) for i in range(101)] for name in script.DEPENDENCE_INPUTS}
        self.assertEqual(script.dependence_grid(columns)["tga"], [10.0, 30.0, 50.0, 70.0, 90.0])

    def test_a_sign_flip_between_regimes_that_read_the_input_is_regime_coded(self):
        flipped = script.reads_input({"a": [0.0, 1.0, 2.0], "b": [2.0, 1.0, 0.0], "c": [1.0, 1.1, 1.2]})
        self.assertTrue(flipped["regime_coded"])
        self.assertEqual(flipped["by_regime"], {"a": "up", "b": "down", "c": "flat"})

    def test_the_same_sign_or_a_flat_regime_is_stable(self):
        self.assertFalse(script.reads_input({"a": [0.0, 1.0, 2.0], "b": [0.0, 3.0, 4.0], "c": [1.0, 1.1, 1.0]})["regime_coded"])

    def test_reserves_split_only_below_the_level(self):
        points = [1600.0, 2800.0, 3200.0, 3300.0, 3800.0]
        self.assertTrue(script.reserve_split(points, [3.0, 1.0, 1.1, 1.0, 1.2]))
        self.assertFalse(script.reserve_split(points, [3.0, 1.0, 2.0, 1.0, 1.2]))
        self.assertFalse(script.reserve_split(points, [1.0, 1.1, 1.2, 1.1, 1.0]))
        with self.assertRaises(ValueError):
            script.reserve_split([1.0], [1.0])


if __name__ == "__main__":
    unittest.main()
