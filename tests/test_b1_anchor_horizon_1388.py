"""B1* and B1'*, the persistence benchmarks with the horizon counted from the last public anchor (#1388; H5, registration design).

`protocol_benchmarks.b1_anchor_forecast` (B1*) and `b1_calendar.b1_calendar_anchor_forecast` (B1'*, also
`protocol_benchmarks.b1_calendar_anchor_forecast`) are checked against `Hand`, an independent restatement written in the test from
`metadata/b1_anchor_horizon_1388.json`: the lag is `L = decision row - anchor row` (rows of the panel), the change spans
`H = h + L` rows, and everything else is B1's (B1''s) own: the window, the centre, the pool by the target's type and its floor of 30.
Stdlib only. What these tests pin: that H is h plus the lag and not h; that a lag of one makes B1* B1 at horizon h + 1; that a lag
longer than one (a decision after a gap in the public rows) is counted; the pool and its fallback for B1'*; the window; that a change
to any spread after the anchor moves nothing; and that B1 and B1' themselves did not move.

Written before the code: the functions did not exist (`AttributeError: module 'repo_model.protocol_benchmarks' has no attribute
'b1_anchor_forecast'`).

Recorded mutations (run on the tests named, then restored):

* `b1_anchor_forecast` (as-of guard): `range(max(first, span), anchor + 1)` replaced with `range(max(first, span), anchor + 2)`, so the
  row after the anchor, not public at the decision instant, is read. `AsOfTests.test_a_spread_after_the_anchor_moves_nothing` and
  `ForecastTests.test_b1_star_matches_the_definition_on_sampled_days` errored with `LookAheadError` (raised by
  `protocol_benchmarks._require_public`); restored, they pass.
* `b1_calendar_anchor_forecast` (as-of guard): the same replacement in its `range(max(first, span), anchor + 1)`. `AsOfTests.
  test_a_spread_after_the_anchor_moves_nothing` errored with `LookAheadError`; restored, it passes.
* `anchor_lag` and `b1_anchor_forecast` (the horizon): `return decision_index - _anchor(...)` replaced with `return 1`, and
  `lag = decision_index - anchor` with `lag = 1`, so that every change spans h + 1 rows whatever the anchor. `ForecastTests.
  test_a_lag_longer_than_one_is_counted` failed with `AssertionError` (`1 != 2`, the lag read for an anchor two rows back); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import unittest
from unittest import mock

from repo_model import b1_calendar as b1c
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp

import test_protocol_benchmarks as tpb

import legacy_day_types

# the legacy day types of the published reproductions (see tests/legacy_day_types.py); B1'* shares B1''s labels whichever are in force
setUpModule, tearDownModule = legacy_day_types.setUpModule, legacy_day_types.tearDownModule


def setup():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class Hand:
    """B1* and B1'* from the definition, in the test's own words."""

    def __init__(self, panel, settings, splits):
        self.panel, self.settings, self.splits = panel, settings, splits

    def anchor(self, t):
        return pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])

    def kind(self, s):
        return self.splits.reporting_day_type(self.panel[s].date, self.panel[s].values)

    def last_ordinary(self, s):
        while s >= 0 and self.kind(s) != "ordinary":
            s -= 1
        return s if s >= 0 else None

    def b1_star(self, t, h):
        a = self.anchor(t)
        span = h + (t - a)
        first = pb._window_start(self.panel, t, 2)
        changes = sorted(self.panel[s].spread_bps - self.panel[s - span].spread_bps for s in range(max(first, span), a + 1))
        return pb.empirical_quantiles(changes, self.panel[a].spread_bps)

    def prime_changes(self, t, h):
        a = self.anchor(t)
        span = h + (t - a)
        first = pb._window_start(self.panel, t, 2)
        ends = [e for e in range(max(first, span), a + 1) if self.last_ordinary(e - span) is not None]
        same = [e for e in ends if self.kind(e) == self.kind(t + h)]
        pool = same if len(same) >= 30 else ends
        return sorted(self.panel[e].spread_bps - self.panel[self.last_ordinary(e - span)].spread_bps for e in pool), len(same)

    def b1_prime_star(self, t, h):
        centre = self.panel[self.last_ordinary(self.anchor(t))].spread_bps
        return pb.empirical_quantiles(self.prime_changes(t, h)[0], centre)


class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()
        cls.splits = tpb.SPLITS
        cls.hand = Hand(cls.panel, cls.settings, cls.splits)

    def test_the_lag_of_an_ordinary_decision_is_one_row(self):
        for t in (520, 900, 1500):
            self.assertEqual(pb.anchor_lag(self.panel, t, **self.settings), 1)

    def test_b1_star_matches_the_definition_on_sampled_days(self):
        for t in (520, 700, 905, 1200, 1500, 1800, len(self.panel) - 12):
            got = pb.b1_anchor_forecast(self.panel, t, **self.settings)
            self.assertEqual(sorted(got), list(sp.HORIZONS))
            for h in sp.HORIZONS:
                self.assertEqual(len(got[h]), len(sp.GRID))
                for x, y in zip(got[h], self.hand.b1_star(t, h)):
                    self.assertAlmostEqual(x, y)

    def test_b1_prime_star_matches_the_definition_on_sampled_days(self):
        for t in (520, 700, 905, 1200, 1500, 1800, len(self.panel) - 12):
            got = b1c.b1_calendar_anchor_forecast(self.panel, t, splits=self.splits, **self.settings)
            self.assertEqual(sorted(got), list(sp.HORIZONS))
            for h in sp.HORIZONS:
                for x, y in zip(got[h], self.hand.b1_prime_star(t, h)):
                    self.assertAlmostEqual(x, y)

    def test_protocol_benchmarks_exposes_b1_prime_star(self):
        t = 1500
        self.assertEqual(pb.b1_calendar_anchor_forecast(self.panel, t, splits=self.splits, **self.settings),
                         b1c.b1_calendar_anchor_forecast(self.panel, t, splits=self.splits, **self.settings))

    def test_with_a_lag_of_one_b1_star_at_h_is_b1_at_h_plus_one(self):
        # B1 at horizon h + 1 is the changes over h + 1 rows from the same anchor: B1* at lead h is that distribution
        t = 1500
        star = pb.b1_anchor_forecast(self.panel, t, **self.settings)
        b1 = pb.b1_forecast(self.panel, t, **self.settings)
        for h in (1, 2, 3, 4):
            self.assertNotEqual(star[h], b1[h])
        a = self.hand.anchor(t)
        first = pb._window_start(self.panel, t, 2)
        for h in (1, 4):
            changes = sorted(self.panel[s].spread_bps - self.panel[s - h - 1].spread_bps for s in range(max(first, h + 1), a + 1))
            for x, y in zip(star[h], pb.empirical_quantiles(changes, self.panel[a].spread_bps)):
                self.assertAlmostEqual(x, y)

    def test_a_lag_longer_than_one_is_counted(self):
        # on the published panel the lag is always one row; a longer one (the last public row two rows back) is made by stating
        # the anchor, and the change must then span h + 2 rows from that anchor
        t = 1500
        with mock.patch.object(pb, "_anchor", lambda panel, index, registry, decision_time: index - 2):
            self.assertEqual(pb.anchor_lag(self.panel, t, **self.settings), 2)
            got = pb.b1_anchor_forecast(self.panel, t, **self.settings)
            prime = b1c.b1_calendar_anchor_forecast(self.panel, t, splits=self.splits, **self.settings)
            first = pb._window_start(self.panel, t, 2)
            a = t - 2
            for h in sp.HORIZONS:
                span = h + 2
                changes = sorted(self.panel[s].spread_bps - self.panel[s - span].spread_bps for s in range(max(first, span), a + 1))
                for x, y in zip(got[h], pb.empirical_quantiles(changes, self.panel[a].spread_bps)):
                    self.assertAlmostEqual(x, y)
                for x, y in zip(prime[h], self.hand.b1_prime_star(t, h)):
                    self.assertAlmostEqual(x, y)
        self.assertNotEqual(got, pb.b1_anchor_forecast(self.panel, t, **self.settings))

    def test_it_is_not_b1(self):
        t = 1500
        self.assertNotEqual(pb.b1_anchor_forecast(self.panel, t, **self.settings), pb.b1_forecast(self.panel, t, **self.settings))

    def test_b1_prime_star_is_not_b1_prime(self):
        t = 1500
        self.assertNotEqual(
            b1c.b1_calendar_anchor_forecast(self.panel, t, splits=self.splits, **self.settings),
            b1c.b1_calendar_forecast(self.panel, t, splits=self.splits, **self.settings),
        )

    def test_a_target_type_with_few_changes_falls_back_to_every_type(self):
        for t in range(520, len(self.panel) - 6):
            if self.hand.prime_changes(t, 1)[1] < 30 and self.hand.kind(t + 1) != "ordinary":
                break
        else:
            self.fail("no such decision day")
        got = b1c.b1_calendar_anchor_forecast(self.panel, t, splits=self.splits, **self.settings)[1]
        a = self.hand.anchor(t)
        first = pb._window_start(self.panel, t, 2)
        every = sorted(self.panel[e].spread_bps - self.panel[self.hand.last_ordinary(e - 2)].spread_bps
                       for e in range(max(first, 2), a + 1) if self.hand.last_ordinary(e - 2) is not None)
        want = pb.empirical_quantiles(every, self.panel[self.hand.last_ordinary(a)].spread_bps)
        for x, y in zip(got, want):
            self.assertAlmostEqual(x, y)

    def test_the_quantiles_are_a_valid_forecast_for_the_scorer(self):
        for forecast in (pb.b1_anchor_forecast(self.panel, 1500, **self.settings),
                         b1c.b1_calendar_anchor_forecast(self.panel, 1500, splits=self.splits, **self.settings)):
            for h in sp.HORIZONS:
                self.assertEqual(forecast[h], sorted(forecast[h]))
                sp.grid_crps(forecast[h], 0.0)


class OriginalsUnmovedTests(unittest.TestCase):
    """B1 and B1' are as they were: the recorded hand reproduction of B1 (test_protocol_benchmarks) and B1''s own tests still run, and these pins
    show that the shared code did not change what the originals return."""

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_b1_is_its_own_definition(self):
        t = 1500
        got = pb.b1_forecast(self.panel, t, **self.settings)
        a = pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])
        first = pb._window_start(self.panel, t, 2)
        for h in sp.HORIZONS:
            changes = sorted(self.panel[s].spread_bps - self.panel[s - h].spread_bps for s in range(max(first, h), a + 1))
            for x, y in zip(got[h], pb.empirical_quantiles(changes, self.panel[a].spread_bps)):
                self.assertAlmostEqual(x, y)


class AsOfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_a_spread_after_the_anchor_moves_nothing(self):
        t = 1200
        a = pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])
        shocked = list(self.panel)
        for i in range(a + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 500.0)
        self.assertEqual(pb.b1_anchor_forecast(self.panel, t, **self.settings), pb.b1_anchor_forecast(shocked, t, **self.settings))
        self.assertEqual(
            b1c.b1_calendar_anchor_forecast(self.panel, t, splits=tpb.SPLITS, **self.settings),
            b1c.b1_calendar_anchor_forecast(shocked, t, splits=tpb.SPLITS, **self.settings),
        )

    def test_a_panel_without_a_target_row_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            pb.b1_anchor_forecast(self.panel[:1500], 1498, **self.settings)
        with self.assertRaises(sp.ProtocolError):
            b1c.b1_calendar_anchor_forecast(self.panel[:1500], 1498, splits=tpb.SPLITS, **self.settings)


if __name__ == "__main__":
    unittest.main()
