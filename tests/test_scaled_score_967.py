"""H1 step 2 and the H5 primary score (#967): a scale-free score, its as-of read, and the study's readings.

The scale of a decision day is the median of B2's grid CRPS over the trailing year of cells whose target has the same
pressure-day type, with the last 6 pool positions left out so that every cell in the window has a target strictly before the
decision day. The tests check it on series with known answers: the median is the hand-computed one; it is the same
whatever happens after the cut-off (the as-of invariance); a series multiplied by a constant has the same scaled score (the
point of a scale); a type with too few cells falls back to the whole window; and the first positions have no full year.

**The guard** `require_public` raises `LookAheadError` for a scale cell whose target day is not before the decision day.
Recorded mutations, both in `scripts/scaled_score_967.py`, both run and both killed:
(1) the guard's line `if target >= decision:` changed to `if False:` fails
`test_the_guard_refuses_a_target_on_or_after_the_decision` and `test_a_window_that_reaches_an_unpublished_target_is_refused`,
each with `AssertionError: LookAheadError not raised`;
(2) `SCALE_LAG = 6` changed to `SCALE_LAG = 1` makes the guard raise `LookAheadError` ("reads the outcome of ... not public at
the instant") in `test_the_default_lag_leaves_every_target_before_the_decision` and in every test that builds scales.

The study's readings are checked on records built by hand: the two kill rules of the declaration fire exactly when it says,
and the misranking is a change in the order of the two candidates in a regime with enough days.
"""

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


script = load("scaled_score_967")

KINDS = ("ordinary", "month_end", "tax_date", "quarter_end")
START = date(2019, 1, 1)


def pool(n, *, scores=None, kinds=None):
    """`n` consecutive decision days; lead h of day i targets day i + h. Scores default to a deterministic pattern."""

    days = [START + timedelta(days=i) for i in range(n + 5)]
    decisions = days[:n]
    targets = [[days[i + h] for h in sp.HORIZONS] for i in range(n)]
    if kinds is None:
        kinds = [[("month_end" if (i + h) % 21 == 0 else "ordinary") for h in sp.HORIZONS] for i in range(n)]
    if scores is None:
        scores = [[1.0 + ((i * 7 + h * 3) % 11) / 10.0 for h in sp.HORIZONS] for i in range(n)]
    return decisions, targets, kinds, scores


def median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2.0


class TestTheScaleIsAsOf(unittest.TestCase):
    def test_the_scale_is_the_median_of_the_trailing_year_of_the_same_type(self):
        decisions, targets, kinds, scores = pool(320)
        scales = script.trailing_scales(decisions, targets, kinds, scores)
        i = 300
        window = range(i - script.SCALE_LAG - script.TRAILING + 1, i - script.SCALE_LAG + 1)
        for kind in ("ordinary", "month_end"):
            cells = [scores[u][h] for u in window for h in range(5) if kinds[u][h] == kind]
            self.assertGreaterEqual(len(cells), script.MIN_CELLS)
            self.assertAlmostEqual(scales[i][kind], median(cells), places=12)

    def test_the_first_positions_have_no_full_year(self):
        decisions, targets, kinds, scores = pool(320)
        scales = script.trailing_scales(decisions, targets, kinds, scores)
        first = script.TRAILING + script.SCALE_LAG - 1
        self.assertTrue(all(s is None for s in scales[:first]))
        self.assertIsNotNone(scales[first])

    def test_the_scale_does_not_move_when_scores_after_the_cut_off_change(self):
        decisions, targets, kinds, scores = pool(320)
        i = 300
        before = script.trailing_scales(decisions, targets, kinds, scores)[i]
        changed = [list(row) for row in scores]
        for u in range(i - script.SCALE_LAG + 1, 320):
            changed[u] = [1e6] * 5
        after = script.trailing_scales(decisions, targets, kinds, changed)[i]
        self.assertEqual(before, after)

    def test_a_score_inside_the_window_moves_it(self):
        decisions, targets, kinds, scores = pool(320)
        i = 300
        before = script.trailing_scales(decisions, targets, kinds, scores)[i]
        changed = [list(row) for row in scores]
        for u in range(i - script.SCALE_LAG - script.TRAILING + 1, i - script.SCALE_LAG + 1):
            changed[u] = [50.0] * 5
        after = script.trailing_scales(decisions, targets, kinds, changed)[i]
        self.assertNotEqual(before, after)

    def test_a_type_with_too_few_cells_falls_back_to_the_whole_window(self):
        decisions, targets, kinds, scores = pool(320)
        kinds = [["ordinary"] * 5 for _ in range(320)]
        kinds[250][2] = "quarter_end"
        scales = script.trailing_scales(decisions, targets, kinds, scores)
        i = 300
        window = range(i - script.SCALE_LAG - script.TRAILING + 1, i - script.SCALE_LAG + 1)
        everything = median([scores[u][h] for u in window for h in range(5)])
        self.assertAlmostEqual(scales[i]["quarter_end"], everything, places=12)

    def test_a_series_times_a_constant_has_the_same_scaled_score(self):
        decisions, targets, kinds, scores = pool(320)
        scales = script.trailing_scales(decisions, targets, kinds, scores)
        big = [[7.0 * v for v in row] for row in scores]
        big_scales = script.trailing_scales(decisions, targets, kinds, big)
        i = 300
        self.assertAlmostEqual(script.scaled_day(scores[i], kinds[i], scales[i]),
                               script.scaled_day(big[i], kinds[i], big_scales[i]), places=12)

    def test_a_spike_day_is_bounded_by_its_scale(self):
        decisions, targets, kinds, scores = pool(320)
        scales = script.trailing_scales(decisions, targets, kinds, scores)
        i = 300
        spike = [300.0] * 5
        self.assertGreater(script.scaled_day(spike, kinds[i], scales[i]), 100.0)
        self.assertLess(script.scaled_day(scores[i], kinds[i], scales[i]), 3.0)


class TestTheGuard(unittest.TestCase):
    def test_the_guard_refuses_a_target_on_or_after_the_decision(self):
        decision = date(2024, 5, 10)
        with self.assertRaises(LookAheadError):
            script.require_public(decision, decision)
        with self.assertRaises(LookAheadError):
            script.require_public(decision, decision + timedelta(days=1))
        script.require_public(decision, decision - timedelta(days=1))

    def test_a_window_that_reaches_an_unpublished_target_is_refused(self):
        decisions, targets, kinds, scores = pool(320)
        with self.assertRaises(LookAheadError):
            script.trailing_scales(decisions, targets, kinds, scores, lag=1)

    def test_the_default_lag_leaves_every_target_before_the_decision(self):
        decisions, targets, kinds, scores = pool(320)
        script.trailing_scales(decisions, targets, kinds, scores)
        self.assertEqual(script.SCALE_LAG, 6)

    def test_the_study_reads_no_day_after_its_end(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 31)])


class TestTheReadings(unittest.TestCase):
    def test_scale_buys_nothing_when_power_is_below_twenty_percent_or_size_above_five(self):
        def record(power, size):
            return {"designs": {"D4": {"post_2020": {"power_10": power, "size": size}}}}

        self.assertTrue(script.kill_scale_buys_nothing(record(0.19, 0.03))["fires"])
        self.assertTrue(script.kill_scale_buys_nothing(record(0.40, 0.06))["fires"])
        self.assertFalse(script.kill_scale_buys_nothing(record(0.20, 0.05))["fires"])

    def test_the_misranking_is_a_change_of_order_in_a_regime_with_enough_days(self):
        def regime(n, raw, scaled):
            return {"n": n, "raw": dict(zip(("gbm_funding", "spread_mr_ctx"), raw)),
                    "scaled": dict(zip(("gbm_funding", "spread_mr_ctx"), scaled))}

        changed = {"a": regime(100, (0.2, 0.1), (0.1, 0.2)), "b": regime(100, (0.2, 0.1), (0.3, 0.1))}
        self.assertTrue(script.misranking(changed)["holds"])
        thin = {"a": regime(20, (0.2, 0.1), (0.1, 0.2)), "b": regime(100, (0.2, 0.1), (0.3, 0.1))}
        self.assertFalse(script.misranking(thin)["holds"])
        same = {"a": regime(100, (0.2, 0.1), (0.4, 0.3))}
        self.assertFalse(script.misranking(same)["holds"])


class TestTheCalibrationSeries(unittest.TestCase):
    """#1014: the critical value is calibrated on the series the paths are drawn from, `e = S(B1) - S(B2)`, not on `-e`.

    The windows are studentized about the series mean, so a skewed series has a different upper quantile from its negation.
    Recorded mutation: `series = list(e)` in `calibrate` changed back to `series = [-v for v in e]` fails
    `test_the_critical_value_is_the_upper_quantile_of_the_path_series` with `AssertionError` (the contiguous critical value
    equals the one of `-e`, not the one of `e`).
    """

    DESIGN = script.Design("T", 40, (1,), "raw")

    @staticmethod
    def skewed(n=300):
        # rare large negative differences: S(B1) - S(B2) is left-skewed, so its two tails differ
        return [(-6.0 if i % 23 == 0 else 0.4) + ((i * 7) % 5) / 10.0 for i in range(n)]

    def upper(self, series):
        cc = script._load("contiguous_calibration_963")
        levels = sp.nominal_levels(self.DESIGN.checkpoints)
        out = {}
        for k, n in enumerate(self.DESIGN.checkpoints[1:], start=1):
            ordered = cc.contiguous_window_statistics(series, days=n)
            out[str(n)] = sp._bound(ordered, 1.0 - levels[k], len(ordered))
        return out

    def test_the_critical_value_is_the_upper_quantile_of_the_path_series(self):
        e = self.skewed()
        _, record = script.calibrate((self.DESIGN, e, 2000))
        self.assertEqual(record["critical"], self.upper(e))
        self.assertNotEqual(record["critical"], self.upper([-v for v in e]))


class TestTheRowCheck(unittest.TestCase):
    """#1014 criterion 3: the old orientation, run again, gives the values #999 published."""

    def test_the_row_check_reproduces_a_record_made_on_the_negated_series_and_refuses_one_made_on_the_series(self):
        import tempfile

        e = TestTheCalibrationSeries.skewed(1500)
        series = {d: (None, None, e) for d in script.ROW_CHECK_DESIGNS}

        def record(sign):
            designs = {}
            for d in script.ROW_CHECK_DESIGNS:
                _, info = script.calibrate_series(script.DESIGN_BY_ID[d], [sign * v for v in e], 2000)
                designs[d] = {"critical": info["critical"], "critical_stationary": info["critical_stationary"]}
            return {"designs": designs}

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            path.write_text(json.dumps(record(-1.0)), encoding="utf-8")
            self.assertTrue(all(v["matches"] for v in script.row_check(series, 2000, path).values()))
            path.write_text(json.dumps(record(1.0)), encoding="utf-8")
            self.assertFalse(any(v["matches"] for v in script.row_check(series, 2000, path).values()))


class TestTheDeclaration(unittest.TestCase):
    def test_the_declaration_is_the_one_the_script_runs(self):
        declaration = json.loads((ROOT / "metadata" / "scaled_score_967.json").read_text(encoding="utf-8"))
        self.assertEqual(script.TRAILING, 252)
        self.assertEqual(script.MIN_CELLS, 20)
        self.assertIn("20 cells", declaration["scale"]["minimum_cells"])
        self.assertIn("t - 257 <= u <= t - 6", declaration["scale"]["trailing_year"])
        self.assertEqual(script.TRAILING + script.SCALE_LAG - 1, 257)

    def test_nothing_decided_moves(self):
        self.assertEqual(sp.CRITICAL_VALUES[sp.GRID_COMPARISON][250], 2.425730476113518)
        self.assertEqual(sp.MME, 0.03)


if __name__ == "__main__":
    unittest.main()
