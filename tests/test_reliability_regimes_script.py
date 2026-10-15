"""The tables of `scripts/reliability_regimes_683.py` (#683): what a reader sees when a regime has no slope.

Nothing here is a leakage guard, so no mutation record is required; the figures the script tabulates are read from tracked evidence.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("reliability_regimes_683_script", ROOT / "scripts" / "reliability_regimes_683.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


S = _script()


def _cell(slope, pressure_days, days=100):
    return {"days": days, "pressure_days": pressure_days, "slope": slope}


class SlopeTextTests(unittest.TestCase):
    def test_a_regime_with_no_pressure_day_is_undefined_not_a_number(self):
        self.assertEqual(S._slope_text(_cell(None, 0)), "undefined")
        self.assertEqual(S._slope_text(_cell(0.7, 0)), "undefined")

    def test_a_missing_slope_with_pressure_days_is_a_dash(self):
        self.assertEqual(S._slope_text(_cell(None, 12)), "–")
        self.assertEqual(S._slope_text(None), "–")

    def test_a_near_separated_fit_is_called_unstable(self):
        self.assertEqual(S._slope_text(_cell(-99.35, 3)), "unstable")

    def test_a_cell_of_few_pressure_days_is_marked(self):
        self.assertEqual(S._slope_text(_cell(6.2, 3)), "6.20†")
        self.assertEqual(S._slope_text(_cell(0.48, 62)), "0.48")


class TrackedTextTests(unittest.TestCase):
    def test_the_pooled_column_comes_first_and_the_reading_is_restated(self):
        result = {
            "source": "x.json",
            "reading": S.READING,
            "rows": {"row": {"1": {
                "all": _cell(0.83, 82, 1469),
                "regime 2018-19": _cell(0.48, 62, 294),
                "regime 2021-23": _cell(None, 0, 586),
            }}},
        }
        text = S.tracked_text(result)
        self.assertIn("Pooled slopes mislead here", text)
        self.assertIn("| lead | all days (pooled) | regime 2018-19 | regime 2020 |", text)
        self.assertIn("| 1 | 0.83 | 0.48 | – | undefined |", text)
        self.assertIn("development, not a verdict".lower(), text.lower())


if __name__ == "__main__":
    unittest.main()
