"""The latent-factor scoring script (#543): the helpers of `scripts/latent_factor.py`, a scratch measurement.

The model itself is tested in `tests/test_ml.py` (`LatentFactorFilterTests`, `LatentFactorPredictorTests`). These
tests pin what the script does around it on small series: the rule that puts the model under a risk-date passer on the
days that are not risk dates, the count of refits at which a loading changes sign, the log loss, and the declaration.
They are data guards (`ValueError`), not leakage guards; the script reads no day after 2025-12-31 and refuses an
uncommitted declaration.
"""

import importlib.util
import json
import math
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("latent_factor_script", ROOT / "scripts" / "latent_factor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DECLARED = json.loads((ROOT / "metadata" / "latent_factor.json").read_text())


class CombineTests(unittest.TestCase):
    DAYS = [date(2020, 3, 30) + __import__("datetime").timedelta(days=k) for k in range(4)]

    def test_a_risk_date_takes_the_passer_and_any_other_day_takes_the_model(self):
        parent = {"5": {self.DAYS[0].isoformat(): 0.4, self.DAYS[1].isoformat(): 0.0, self.DAYS[2].isoformat(): 0.0, self.DAYS[3].isoformat(): 0.9}}
        own = {"5": {d.isoformat(): 0.1 * (k + 1) for k, d in enumerate(self.DAYS)}}
        out = _script().combine(parent, own, {self.DAYS[0], self.DAYS[3]})
        self.assertEqual([out["5"][d.isoformat()] for d in self.DAYS], [0.4, 0.2, 0.30000000000000004, 0.9])

    def test_the_passer_must_be_zero_off_the_risk_dates(self):
        """A passer that forecasts a day the rule calls ordinary is not the passer the rule assumes."""

        day = self.DAYS[0].isoformat()
        with self.assertRaises(ValueError):
            _script().combine({"5": {day: 0.3}}, {"5": {day: 0.1}}, set())

    def test_mismatched_dates_or_thresholds_are_refused(self):
        a, b = self.DAYS[0].isoformat(), self.DAYS[1].isoformat()
        with self.assertRaises(ValueError):
            _script().combine({"5": {a: 0.0}}, {"5": {b: 0.1}}, set())
        with self.assertRaises(ValueError):
            _script().combine({"5": {a: 0.0}}, {"10": {a: 0.1}}, set())


class RiskDateTests(unittest.TestCase):
    def test_a_day_type_other_than_ordinary_is_a_risk_date_and_a_coupon_only_at_horizon_one(self):
        s = _script()
        self.assertTrue(s.is_risk_date("quarter_end", 0.0, 3))
        self.assertTrue(s.is_risk_date("month_end", None, 5))
        self.assertFalse(s.is_risk_date("ordinary", 40.0, 2))
        self.assertTrue(s.is_risk_date("ordinary", 40.0, 1))
        self.assertFalse(s.is_risk_date("ordinary", 0.0, 1))
        self.assertFalse(s.is_risk_date("ordinary", None, 1))


class LoadingSignTests(unittest.TestCase):
    def test_a_refit_that_flips_a_loadings_sign_is_counted_once_per_series_and_change(self):
        out = _script().sign_changes([[1.0, -1.0], [1.0, -1.0], [-0.5, -1.0], [-0.5, 2.0], [0.2, 2.0]])
        self.assertEqual(out, [2, 1])

    def test_a_loading_of_zero_is_not_a_sign(self):
        self.assertEqual(_script().sign_changes([[1.0], [0.0], [1.0]]), [0])

    def test_ragged_refits_are_refused(self):
        with self.assertRaises(ValueError):
            _script().sign_changes([[1.0, 2.0], [1.0]])


class LogLossTests(unittest.TestCase):
    def test_log_loss_clips_the_probability_at_the_declared_floor(self):
        s = _script()
        self.assertAlmostEqual(s.log_loss([0.5, 0.5], [1.0, 0.0]), math.log(2.0))
        self.assertAlmostEqual(s.log_loss([0.0], [1.0]), -math.log(1e-6))
        self.assertAlmostEqual(s.log_loss([1.0], [0.0]), -math.log(1e-6))

    def test_series_of_different_length_are_refused(self):
        with self.assertRaises(ValueError):
            _script().log_loss([0.5], [1.0, 0.0])


class DeclarationTests(unittest.TestCase):
    def test_the_rows_the_script_scores_are_the_declared_ones(self):
        s = _script()
        self.assertEqual(list(s.VARIANTS), ["latent_factor", "latent_factor_resid", "latent_factor_logit"])
        self.assertEqual(
            s.COMBINED,
            {
                "risk_gbm+latent_factor": "latent_factor",
                "risk_gbm+latent_factor_resid": "latent_factor_resid",
                "risk_gbm+latent_factor_logit": "latent_factor_logit",
            },
        )
        self.assertEqual(sorted(DECLARED["rows"]["combined"]["names"]), sorted(s.COMBINED))

    def test_every_scored_row_is_a_judge_candidate_with_a_file_of_its_own(self):
        names = [
            "latent_factor", "latent_factor_resid", "latent_factor_logit",
            "risk_gbm+latent_factor", "risk_gbm+latent_factor_resid", "risk_gbm+latent_factor_logit",
        ]
        for name in names:
            entry = json.loads((ROOT / "metadata" / "pressure_judge" / "candidates" / f"{name}.json").read_text())
            self.assertEqual(entry["role"], "candidate")
            self.assertIn("spread_bps", entry["features"])

    def test_the_scoring_window_ends_before_the_lockbox_and_nothing_is_published(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")
        self.assertIn("nothing is published", DECLARED["unchanged"])
        published = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())
        self.assertNotIn("latent_factor", json.dumps(published.get("confirmation", {})))


if __name__ == "__main__":
    unittest.main()
