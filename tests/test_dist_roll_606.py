"""The best tier-1 passer's tier 3 and tier 5 failures (#606): the diagnosis of step 1, a pure reading of the judge's output.

`risk_date_shortfall` splits the shortfall of a risk-date row's forecast (realised minus predicted, summed over days) between
the risk dates and the days that are not risk dates, where the row forecasts exactly 0. `tier_cells` reads the judge's own
regime cells and tier 5 cell and states the test statistic, its threshold and the margin.

Recorded mutation, 12 October 2026, in a disposable copy: in `scripts/dist_roll_606.py`, `require_scored_window`, the line
`pj.require_scored_days(pj.load_declaration(), [day], where="dist_roll_606")` replaced by `pass`.
`GuardTests.test_diagnose_refuses_a_locked_day` then failed with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("dist_roll_606_script", ROOT / "scripts" / "dist_roll_606.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["dist_roll_606_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class ShortfallTests(unittest.TestCase):
    def test_non_risk_days_carry_their_pressure_days_as_shortfall(self):
        p = [0.5, 0.2, 0.0, 0.0, 0.0]
        y = [1, 0, 1, 1, 0]
        risk = [True, True, False, False, False]
        out = SCRIPT.risk_date_shortfall(p, y, risk)
        self.assertEqual(out["days"], 5)
        self.assertEqual(out["pressure_days"], 3)
        self.assertEqual(out["pressure_days_not_risk"], 2)
        self.assertAlmostEqual(out["shortfall_total"], (3 - 0.7) / 5)
        self.assertAlmostEqual(out["shortfall_not_risk"], 2 / 5)
        self.assertAlmostEqual(out["shortfall_risk"], (1 - 0.7) / 5)
        self.assertAlmostEqual(out["share_not_risk"], (2 / 5) / ((3 - 0.7) / 5))

    def test_a_nonzero_forecast_off_a_risk_date_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.risk_date_shortfall([0.1], [1], [False])

    def test_length_mismatch_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.risk_date_shortfall([0.1, 0.2], [1], [True, True])

    def test_no_shortfall_gives_no_share(self):
        out = SCRIPT.risk_date_shortfall([0.5, 0.0], [1, 0], [True, False])
        self.assertAlmostEqual(out["shortfall_total"], 0.25)
        out = SCRIPT.risk_date_shortfall([0.5, 0.5], [1, 0], [True, True])
        self.assertAlmostEqual(out["shortfall_total"], 0.0)
        self.assertIsNone(out["share_not_risk"])


class CellTests(unittest.TestCase):
    def _cell(self, mean, lower, upper, events=30):
        return {"events": events, "days": 100, "mean_predicted": 0.1, "realised_frequency": 0.1 + mean,
                "realised_minus_predicted": {"mean": mean, "interval": {"lower": lower, "upper": upper}}}

    def test_a_regime_fails_when_its_interval_excludes_zero(self):
        out = SCRIPT.regime_cell(self._cell(0.18, 0.10, 0.25), minimum_events=20)
        self.assertTrue(out["tested"])
        self.assertFalse(out["covers_zero"])
        self.assertAlmostEqual(out["margin"], -0.10)  # distance from the interval to zero, negative when it fails

    def test_a_regime_passes_when_it_covers_zero(self):
        out = SCRIPT.regime_cell(self._cell(0.01, -0.02, 0.04), minimum_events=20)
        self.assertTrue(out["covers_zero"])
        self.assertAlmostEqual(out["margin"], 0.02)

    def test_a_thin_regime_is_reported_not_tested(self):
        out = SCRIPT.regime_cell(self._cell(0.18, 0.10, 0.25, events=4), minimum_events=20)
        self.assertFalse(out["tested"])

    def test_margin_is_negative_below_zero_too(self):
        out = SCRIPT.regime_cell(self._cell(-0.1, -0.2, -0.05), minimum_events=20)
        self.assertFalse(out["covers_zero"])
        self.assertAlmostEqual(out["margin"], -0.05)


class GuardTests(unittest.TestCase):
    def test_diagnose_refuses_a_locked_day(self):
        with self.assertRaises(LookAheadError):
            SCRIPT.require_scored_window("2026-01-02")

    def test_a_window_inside_the_open_period_is_allowed(self):
        SCRIPT.require_scored_window("2025-12-31")


if __name__ == "__main__":
    unittest.main()
