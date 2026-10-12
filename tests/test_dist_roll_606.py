"""The best tier-1 passer's tier 3 and tier 5 failures (#606): the diagnosis of step 1, a pure reading of the judge's output.

`risk_date_shortfall` splits the shortfall of a risk-date row's forecast (realised minus predicted, summed over days) between
the risk dates and the days that are not risk dates, where the row forecasts exactly 0. `tier_cells` reads the judge's own
regime cells and tier 5 cell and states the test statistic, its threshold and the margin.

Recorded mutation, 12 October 2026, in a disposable copy: in `scripts/dist_roll_606.py`, `require_scored_window`, the line
`pj.require_scored_days(pj.load_declaration(), [day], where="dist_roll_606")` replaced by `pass`.
`GuardTests.test_diagnose_refuses_a_locked_day` then failed with `AssertionError: LookAheadError not raised`.

Recorded mutations of the floor (step 2), 12 October 2026, in a disposable copy:

* `src/repo_model/group_calibration.py`, `fit_floor`: the line `require_observable(pairs, fitted_at)` replaced by `pass`.
  `FloorTests.test_a_pair_after_the_fitting_date_is_refused` then failed with `AssertionError: LookAheadError not raised`.
* `src/repo_model/group_calibration.py`, `walk_forward_floor`: `pc.past_positions(scored_dates, train_ends, start)` replaced by
  `range(start)` (every earlier pair, observable or not). `FloorTests.test_a_pair_not_yet_observable_at_the_fit_is_left_out`
  then errored with `repo_model.splits.LookAheadError` (the guard in `fit_floor` refused the unobservable pairs).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from datetime import date, timedelta

from repo_model import group_calibration as gc
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


def _days(n, start=date(2018, 1, 1)):
    return [start + timedelta(days=k) for k in range(n)]


SMALL = {"minimum_pairs": 10, "minimum_events": 1}


class FloorTests(unittest.TestCase):
    """`group_calibration.walk_forward_floor`: a floor on the days that are not risk dates, from earlier observable pairs."""

    def _setup(self, n=200, block=50, lag=1):
        days = _days(n)
        off = [k % 2 == 0 for k in range(n)]  # half the days are off the risk dates
        outcomes = [1 if (o and k % 4 == 0) else 0 for k, o in enumerate(off)]  # a quarter of the off days are pressure days
        forecasts = [0.0 if o else 0.3 for o in off]
        train_ends = [days[max(0, (k // block) * block - lag)] for k in range(n)]
        return days, off, outcomes, forecasts, train_ends

    def test_floor_is_the_earlier_off_risk_rate(self):
        days, off, y, p, ends = self._setup()
        column = gc.walk_forward_floor(p, y, days, ends, off, **SMALL)
        # the second block (days 50 to 99) is floored by the off-risk pairs observable at its fit
        self.assertGreater(column[50], 0.0)
        self.assertAlmostEqual(column[50], 13 / 25)  # 13 of the 25 earlier off-risk days (every fourth day from the first) were pressure days
        # a risk date keeps its forecast
        self.assertEqual(column[51], 0.3)

    def test_nothing_is_floored_before_the_gate(self):
        days, off, y, p, ends = self._setup()
        column = gc.walk_forward_floor(p, y, days, ends, off, **SMALL)
        self.assertEqual(column[0], 0.0)
        self.assertEqual(column[48], 0.0)  # the first block has no earlier pairs

    def test_a_floor_never_lowers_a_forecast(self):
        days, off, y, p, ends = self._setup()
        p = [0.9 if o else q for o, q in zip(off, p)]
        column = gc.walk_forward_floor(p, y, days, ends, off, **SMALL)
        self.assertTrue(all(c >= q for c, q in zip(column, p)))

    def test_a_pair_after_the_fitting_date_is_refused(self):
        days = _days(100)
        pairs = [(d, 0.0, 0, "") for d in days]
        with self.assertRaises(LookAheadError):
            gc.fit_floor(pairs, days[50])
        self.assertIsNone(gc.fit_floor(pairs[:59], days[58]))
        self.assertEqual(gc.fit_floor(pairs[:60], days[59]), 0.0)

    def test_the_floor_uses_no_outcome_of_its_own_block(self):
        days, off, y, p, ends = self._setup()
        flipped = list(y)
        for k in range(50, 100):
            flipped[k] = 1 - flipped[k]
        a = gc.walk_forward_floor(p, y, days, ends, off, **SMALL)
        b = gc.walk_forward_floor(p, flipped, days, ends, off, **SMALL)
        self.assertEqual(a[50:100], b[50:100])

    def test_a_pair_not_yet_observable_at_the_fit_is_left_out(self):
        days = _days(120)
        off = [True] * 120
        # the block starting at day 60 trains on labels up to day 49; days 50 to 59 are scored but their outcomes are not yet known
        ends = [days[49] if k >= 60 else days[0] for k in range(120)]
        y = [0] * 50 + [1] * 10 + [0] * 60
        column = gc.walk_forward_floor([0.0] * 120, y, days, ends, off, **SMALL)
        self.assertEqual(column[60], 0.0)

    def test_a_group_with_enough_pairs_gets_its_own_rate(self):
        days = _days(300)
        groups = ["a" if k % 4 < 2 else "b" for k in range(300)]
        off = [True] * 300
        y = [1 if (g == "b" or k % 5 == 0) else 0 for k, g in enumerate(groups)]  # group b always has one, group a one day in five
        ends = [days[max(0, (k // 100) * 100 - 1)] for k in range(300)]
        p = [0.0] * 300
        grouped = gc.walk_forward_floor(p, y, days, ends, off, groups, **SMALL)
        pooled = gc.walk_forward_floor(p, y, days, ends, off, **SMALL)
        k = 100
        self.assertEqual(groups[k], "a")
        self.assertEqual(groups[k + 2], "b")
        self.assertLess(grouped[k], pooled[k])
        self.assertLess(pooled[k], grouped[k + 2])
        self.assertEqual(grouped[k + 2], 1.0)

    def test_a_thin_group_falls_back_to_the_pooled_rate(self):
        days, off, y, p, ends = self._setup(n=400, block=100)
        groups = ["rare" if k == 1 else "common" for k in range(400)]
        pooled = gc.walk_forward_floor(p, y, days, ends, off, **SMALL)
        grouped = gc.walk_forward_floor(p, y, days, ends, off, groups, **SMALL)
        self.assertEqual(pooled, grouped)

    def test_lengths_must_match(self):
        days, off, y, p, ends = self._setup()
        with self.assertRaises(ValueError):
            gc.walk_forward_floor(p, y[:-1], days, ends, off)


class DeclarationTests(unittest.TestCase):
    def test_every_variant_has_a_candidate_file_and_a_pair(self):
        import json

        declared = json.loads((ROOT / "metadata" / "dist_roll_606.json").read_text())
        names = list(SCRIPT.VARIANT_NAMES.values())
        self.assertEqual(sorted(declared["variants"]), sorted(names))
        self.assertLessEqual(len(names), 3)  # the directive allows at most three variants
        for name in names:
            candidate = json.loads((ROOT / "metadata" / "pressure_judge" / "candidates" / f"{name}.json").read_text())
            self.assertEqual(candidate["parent"], SCRIPT.BEST)
            self.assertIn("metadata/dist_roll_606.json", candidate["calibration"])
            self.assertEqual(declared["rows"]["pairs"][name], SCRIPT.BEST)

    def test_the_declaration_is_what_declare_writes(self):
        import json

        declared = json.loads((ROOT / "metadata" / "dist_roll_606.json").read_text())
        self.assertEqual(declared, json.loads(json.dumps(SCRIPT.declaration_document())))

    def test_no_variant_reads_a_hindsight_regime_label(self):
        import json

        text = (ROOT / "metadata" / "dist_roll_606.json").read_text()
        self.assertIn("No hindsight regime label", text)
        self.assertNotIn("splits.regime", text)

    def test_the_declared_last_day_is_before_the_locked_tiers(self):
        import json

        declared = json.loads((ROOT / "metadata" / "dist_roll_606.json").read_text())
        self.assertLess(date.fromisoformat(declared["scoring"]["last_day"]), date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
