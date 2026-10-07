"""The walk-forward recalibrators of the bake-off (#138).

`probability_calibration` maps a pressure probability through a curve fitted
on the forecast's own earlier (forecast, outcome) pairs. The guard is that a
curve never sees an outcome after its fitting date: `fit` refuses such a pair
with `LookAheadError`, and `walk_forward` and `venn_abers` hand it only pairs
whose scored day is at or before the block's last training label.
"""

from __future__ import annotations

import math
import random
import unittest
from datetime import date, timedelta

from repo_model import pressure, probability_calibration as pc
from repo_model.metrics import _recalibrate
from repo_model.splits import LookAheadError


def _series(count=900, seed=7, horizon=1, block=21):
    """A synthetic scored run: dates, a block's train end, forecasts and outcomes.

    The forecast is miscalibrated on purpose (outcomes drawn at p**0.7), so
    every recalibrator has something to correct.
    """

    rng = random.Random(seed)
    start = date(2018, 1, 1)
    dates = [start + timedelta(days=k) for k in range(count)]
    train_ends = []
    for k in range(count):
        first = (k // block) * block
        train_ends.append(dates[first] - timedelta(days=horizon))
    forecasts = [min(0.95, max(0.01, rng.betavariate(0.6, 4.0))) for _ in range(count)]
    outcomes = [1 if rng.random() < p ** 0.7 else 0 for p in forecasts]
    return dates, train_ends, forecasts, outcomes


class LeakageGuardTests(unittest.TestCase):
    """A recalibrator never sees an outcome after its fitting date.

    Recorded mutation (#138): in `probability_calibration.fit`, the guard line
    `if late:` mutated to `if False:`. `test_fit_refuses_a_pair_after_its_fitting_date`
    then failed with `AssertionError: LookAheadError not raised`, for every method.
    """

    def test_fit_refuses_a_pair_after_its_fitting_date(self):
        dates, _, forecasts, outcomes = _series(400)
        fitted_at = dates[299]
        pairs = list(zip(dates[:301], forecasts[:301], outcomes[:301]))
        for method in pc.CALIBRATORS:
            with self.subTest(method=method):
                with self.assertRaises(LookAheadError):
                    pc.fit(method, pairs, fitted_at)

    def test_fit_accepts_pairs_up_to_its_fitting_date(self):
        dates, _, forecasts, outcomes = _series(400)
        pairs = list(zip(dates[:300], forecasts[:300], outcomes[:300]))
        for method in pc.CALIBRATORS:
            with self.subTest(method=method):
                curve = pc.fit(method, pairs, dates[299])
                self.assertTrue(0.0 <= curve(0.2) <= 1.0)

    def test_walk_forward_never_reads_a_later_outcome(self):
        """Flip every outcome after one block's train end: that block and the earlier ones do not move."""

        dates, train_ends, forecasts, outcomes = _series()
        for method in pc.CALIBRATORS:
            with self.subTest(method=method):
                before = pc.walk_forward(method, forecasts, outcomes, dates, train_ends)
                cut = 20 * 21  # the first day of block 20
                horizon_end = train_ends[cut]
                flipped = [
                    1 - y if when > horizon_end else y for when, y in zip(dates, outcomes)
                ]
                after = pc.walk_forward(method, forecasts, flipped, dates, train_ends)
                stop = cut + 21
                self.assertEqual(before[:stop], after[:stop])
                self.assertNotEqual(before[stop:], after[stop:])

    def test_venn_abers_never_reads_a_later_outcome(self):
        dates, train_ends, forecasts, outcomes = _series()
        before = pc.venn_abers(forecasts, outcomes, dates, train_ends)
        cut = 20 * 21
        flipped = [1 - y if when > train_ends[cut] else y for when, y in zip(dates, outcomes)]
        after = pc.venn_abers(forecasts, flipped, dates, train_ends)
        self.assertEqual(before[: cut + 21], after[: cut + 21])

    def test_venn_abers_refuses_a_pair_scored_after_its_block_fit(self):
        """The refusal itself, not only the invariance of the output.

        `past_positions` already drops every pair scored after the block's train
        end, so the guard in `venn_abers` is a second, independent check on what
        it was handed. Here `past_positions` is made to hand it a later pair, as
        a regression in it would.

        Recorded mutation (CLAUDE.md): in `probability_calibration.venn_abers`,
        `if any(scored_dates[i] > end for i in past):` mutated to `if False:`.
        This test then fails, raising `AssertionError` ("LookAheadError not
        raised").
        """

        from unittest import mock

        dates, train_ends, forecasts, outcomes = _series()
        first = pc.blocks(dates, train_ends)[20][0]
        leaked = [i for i in range(len(dates)) if dates[i] > train_ends[first]][:1]
        real = pc.past_positions

        def handing_over_a_later_pair(scored_dates, ends, start):
            return real(scored_dates, ends, start) + (leaked if start == first else [])

        with mock.patch.object(pc, "past_positions", handing_over_a_later_pair):
            with self.assertRaisesRegex(LookAheadError, "read a later outcome"):
                pc.venn_abers(forecasts, outcomes, dates, train_ends)

    def test_a_block_is_fitted_on_its_earlier_observable_pairs_only(self):
        """At horizon 5 the four scored days before a block's train end are not yet observable."""

        dates, train_ends, forecasts, outcomes = _series(horizon=5)
        for start, stop, end in pc.blocks(dates, train_ends):
            past = pc.past_positions(dates, train_ends, start)
            self.assertTrue(all(dates[i] <= end for i in past))
            self.assertTrue(all(i < start for i in past))
            self.assertEqual(
                past, [i for i in range(start) if dates[i] <= end]
            )


class CalibratorTests(unittest.TestCase):
    def setUp(self):
        dates, _, forecasts, outcomes = _series(600)
        self.pairs = list(zip(dates, forecasts, outcomes))
        self.fitted_at = dates[-1]

    def test_the_half_life_is_a_declared_constant(self):
        self.assertEqual(pc.RECENCY_HALF_LIFE_DAYS, 504)
        self.assertEqual(pc.declaration()["recency_half_life_scored_days"], 504)

    def test_isotonic_is_the_corp_fit_read_as_a_step_function(self):
        curve = pc.fit("isotonic", self.pairs, self.fitted_at)
        xs = [p for _, p, _ in self.pairs]
        ys = [y for _, _, y in self.pairs]
        fitted = _recalibrate(xs, ys)
        for x, value in list(zip(xs, fitted))[:50]:
            self.assertAlmostEqual(curve(x), value)

    def test_every_curve_is_non_decreasing(self):
        grid = [k / 200 for k in range(1, 200)]
        for method in pc.CALIBRATORS:
            with self.subTest(method=method):
                curve = pc.fit(method, self.pairs, self.fitted_at)
                values = [curve(x) for x in grid]
                self.assertTrue(all(b >= a - 1e-12 for a, b in zip(values, values[1:])))

    def test_platt_corrects_an_underconfident_forecast_upwards(self):
        curve = pc.fit("platt", self.pairs, self.fitted_at)
        self.assertGreater(curve(0.1), 0.1)

    def test_beta_keeps_its_shape_parameters_non_negative(self):
        a, b, _ = pc.beta_parameters([(p, y) for _, p, y in self.pairs])
        self.assertGreaterEqual(a, 0.0)
        self.assertGreaterEqual(b, 0.0)

    def test_recency_with_a_very_long_half_life_is_platt(self):
        platt = pc.fit("platt", self.pairs, self.fitted_at)
        long = pc._weighted_platt(
            [(p, y) for _, p, y in self.pairs], half_life=1e12
        )
        for x in (0.02, 0.1, 0.4):
            self.assertAlmostEqual(platt(x), long(x), places=6)

    def test_venn_abers_brackets(self):
        dates, train_ends, forecasts, outcomes = _series()
        pairs = pc.venn_abers(forecasts, outcomes, dates, train_ends)
        bracketed = [pair for pair in pairs if pair is not None]
        self.assertTrue(bracketed)
        self.assertTrue(all(p0 <= p1 for p0, p1 in bracketed))
        self.assertTrue(all(pair is None for pair in pairs[: pc.MINIMUM_PAIRS]))

    def test_identity_until_enough_pairs(self):
        dates, train_ends, forecasts, outcomes = _series()
        column = pc.walk_forward("beta", forecasts, outcomes, dates, train_ends)
        self.assertEqual(column[:252], tuple(forecasts[:252]))
        self.assertNotEqual(column[-21:], tuple(forecasts[-21:]))

    def test_unknown_method_is_refused(self):
        with self.assertRaises(ValueError):
            pc.fit("temperature", self.pairs, self.fitted_at)

    def test_monotone_in_tau(self):
        self.assertEqual(pc.monotone_curves([(0.4, 0.5), (0.2, 0.1)]), [(0.4, 0.4), (0.2, 0.1)])


class WhichCalibratorIsPublishedTests(unittest.TestCase):
    """The published recalibration is Platt; the isotonic control is not it (#211).

    #138's directive called `corp_isotonic` the published recalibration. It is
    the CORP reliability-curve method name; pressure model v1 is published with
    Platt scaling out of fold (`pressure.RECALIBRATION`). The module names both,
    so a reader pairs against the right one.
    """

    def test_the_published_calibrator_is_platt_and_is_not_the_control(self):
        self.assertEqual(pressure.RECALIBRATION["method"], "platt_out_of_fold")
        self.assertEqual(pc.PUBLISHED, "platt")
        self.assertIn(pc.PUBLISHED, pc.CALIBRATORS)
        self.assertNotEqual(pc.PUBLISHED, pc.CONTROL)

    def test_the_frozen_declaration_is_unchanged_by_the_naming(self):
        # `final_test_preregistration` hashes `declaration()`; naming the
        # published calibrator must not add a key to it.
        self.assertNotIn("published", pc.declaration())


if __name__ == "__main__":
    unittest.main()
