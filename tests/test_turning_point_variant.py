"""The turning-point variants of the published model (#453): the declaration and the script's pure parts.

The turn model's training window is a leakage guard: a day's label (a turning point) reads the next day's spread, so a refit
may train only on days whose next day is at or before the block's first as-of row. Recorded mutation: in
`turn_probabilities`, `range(FIRST_TURN_DAY, first_anchor)` changed to `range(FIRST_TURN_DAY, first_anchor + 1)`;
`test_a_label_from_after_the_refit_is_refused` then failed with `LookAheadError`.
"""

from __future__ import annotations

import importlib.util
import json
import random
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("turning_point_variant", REPO / "scripts" / "turning_point_variant.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


variant = _load()
HAVE_ML = importlib.util.find_spec("sklearn") is not None and importlib.util.find_spec("numpy") is not None


class DeclarationTest(unittest.TestCase):
    def setUp(self):
        self.declaration = json.loads((REPO / "metadata" / "turning_point_variant.json").read_text(encoding="utf-8"))

    def test_declares_the_three_candidates_and_the_holm_rule(self):
        self.assertEqual(tuple(self.declaration["candidates"]), variant.CANDIDATES)
        self.assertIn("Holm across the three candidates", self.declaration["test"]["multiple_comparison"])
        self.assertEqual(self.declaration["candidates"]["predicted_turn_switch"]["threshold"], variant.THRESHOLD)

    def test_scores_only_unlocked_days_and_decides_nothing(self):
        scoring = self.declaration["scoring"]
        self.assertEqual(date.fromisoformat(scoring["last_day"]), variant.END)
        self.assertLess(variant.END, date(2026, 1, 1))
        self.assertTrue(self.declaration["decides"].startswith("nothing"))

    def test_the_published_record_is_untouched(self):
        record = json.loads((REPO / "docs" / "runs" / "published_distribution_daily_h1.json").read_text("utf-8"))
        self.assertNotIn("turning_point_variant", json.dumps(record))


class PureTest(unittest.TestCase):
    def test_holm_ranks_by_p_and_steps_down(self):
        rng = random.Random(1)
        strong = [0.5 + rng.gauss(0, 0.2) for _ in range(200)]
        none = [rng.gauss(0, 0.2) for _ in range(200)]
        worse = [-0.5 + rng.gauss(0, 0.2) for _ in range(200)]
        out = variant.holm({"a": none, "b": strong, "c": worse}, replications=300)
        self.assertEqual(out["b"]["holm_rank"], 1)
        self.assertEqual(out["b"]["verdict"], "better")
        self.assertEqual(out["a"]["verdict"], "no difference")
        self.assertEqual(out["c"]["verdict"], "worse")
        self.assertAlmostEqual(out["b"]["holm_level"], variant.ALPHA / 3)

    def test_a_weaker_candidate_cannot_pass_after_a_failed_step(self):
        rng = random.Random(2)
        none = [rng.gauss(0, 0.2) for _ in range(200)]
        out = variant.holm({"a": none, "b": [x + 0.001 for x in none]}, replications=300)
        self.assertNotIn("better", [v["verdict"] for v in out.values()])

    def test_turn_features_read_the_as_of_row_and_the_calendar_of_the_scored_day(self):
        series = [float(i % 5) for i in range(30)]
        flags = {12: [1, 0, 0, 1]}
        row = variant.turn_features(series, flags, 10, 12)
        self.assertEqual(row[0], series[10])
        self.assertEqual(row[1], series[10] - series[9])
        self.assertEqual(row[4:], [1.0, 0.0, 0.0, 1.0])

    def test_the_blend_is_the_equal_average(self):
        class Fit:
            def __init__(self, vector):
                self.levels, self.features_read, self.model_settings = (0.05, 0.5, 0.95), ("spread_bps",), {}
                self._vector = vector

            def predict(self, row):
                return self._vector

        blend = variant._BlendFitted(Fit((0.0, 2.0, 4.0)), Fit((2.0, 4.0, 8.0)))
        self.assertEqual(blend.predict(None), (1.0, 3.0, 6.0))
        self.assertNotIn("calibration", blend.model_settings)


@unittest.skipUnless(HAVE_ML, "needs the ml extra")
class TurnModelTest(unittest.TestCase):
    def _series(self, n=400):
        rng = random.Random(7)
        return [round(rng.gauss(0, 3)) * 1.0 for _ in range(n)]

    def _run(self, series):
        n = len(series)
        scored = list(range(100, n))
        anchors = [s - 2 for s in scored]
        flags = {i: [0, 0, 0, 0] for i in range(n)}
        return variant.turn_probabilities(series, flags, scored, anchors)

    def test_probabilities_are_probabilities(self):
        probabilities = self._run(self._series())
        self.assertTrue(all(0.0 <= p <= 1.0 for p in probabilities))

    def test_a_label_from_after_the_refit_is_refused(self):
        # The second block opens at row 121, whose as-of row is 119. Row 120's spread is not public at its refit, so
        # the forecast of row 121 must not move when it is changed (later rows legitimately read it as a feature).
        series = self._series()
        base = self._run(series)
        changed = list(series)
        changed[120] += 50.0
        after = self._run(changed)
        self.assertEqual(base[21], after[21])
        self.assertEqual(base[:21], after[:21])


if __name__ == "__main__":
    unittest.main()
