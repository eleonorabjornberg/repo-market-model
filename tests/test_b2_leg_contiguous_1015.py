"""H1 step 3 (#1015): #963's contiguous-window rules on the leg against B2, d = S(B2) - S(candidate).

The new pieces are small and checked on series with known answers: the leg's series has the orientation of the leg against B2
(positive favours the candidate over B2), the per-leg reading is #963's 3.0 / 4.0 rule, the joint reading is the worse of
the two legs, and the values the script reads are the ones its declaration states. The script changes no decided value.

No guard is added beyond `ValueError` on a series the leg cannot be read from, so there is no recorded mutation.
"""

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load("b2_leg_contiguous_1015")
IN_FORCE_BEFORE = {k: dict(v) for k, v in sp.CRITICAL_VALUES.items()}


class TestLegSeries(unittest.TestCase):
    def data(self):
        days = [date(2021, 1, 4), date(2021, 1, 5), date(2021, 1, 6)]
        scores = {"B1": [3.0, 3.0, 3.0], "B2": [2.0, 2.5, 1.0], "gbm_funding": [1.5, 2.5, 2.0]}
        return {"days": days, "day_score": {k: dict(zip(days, v)) for k, v in scores.items()}}

    def test_the_b2_leg_is_b2_minus_the_candidate(self):
        series = script.b2_leg_series(self.data(), "gbm_funding", first=date(2021, 1, 4))
        self.assertEqual(list(series.values()), [0.5, 0.0, -1.0])

    def test_the_b1_leg_is_the_other_orientation(self):
        series = script.b1_leg_series(self.data(), "gbm_funding", first=date(2021, 1, 4))
        self.assertEqual(list(series.values()), [1.5, 0.5, 1.0])

    def test_days_before_the_first_are_dropped(self):
        series = script.b2_leg_series(self.data(), "gbm_funding", first=date(2021, 1, 5))
        self.assertEqual(sorted(series), [date(2021, 1, 5), date(2021, 1, 6)])


class TestReadings(unittest.TestCase):
    def test_the_per_leg_rule_is_963s(self):
        self.assertEqual(script.reading(2.99), "survives")
        self.assertEqual(script.reading(3.0), "neither")
        self.assertEqual(script.reading(4.0), "neither")
        self.assertEqual(script.reading(4.01), "fails")

    def test_the_joint_reading_is_the_worse_leg(self):
        self.assertEqual(script.joint_reading(2.07, 2.5), "survives")
        self.assertEqual(script.joint_reading(2.07, 3.86), "neither")
        self.assertEqual(script.joint_reading(3.5, 2.0), "neither")
        self.assertEqual(script.joint_reading(2.07, 4.5), "fails")
        self.assertEqual(script.joint_reading(4.5, 3.5), "fails")


class TestDeclared(unittest.TestCase):
    def test_the_values_read_are_the_declared_ones(self):
        declaration = json.loads((ROOT / "metadata" / "b2_leg_contiguous_1015.json").read_text(encoding="utf-8"))
        text = declaration["calibration"]["values_draft_953"]
        for days, value in script.DRAFT_953.items():
            if days != 500:
                self.assertIn(repr(value), text)
        self.assertEqual(script.DRAFT_953[500], script.DRAFT_953[250])
        self.assertEqual(declaration["variants"], {})

    def test_nothing_decided_moves(self):
        self.assertEqual(sp.CRITICAL_VALUES, IN_FORCE_BEFORE)
        self.assertEqual(script.IN_FORCE[125], 3.419438620805254)
        self.assertEqual(script.IN_FORCE[250], 2.425730476113518)


if __name__ == "__main__":
    unittest.main()
