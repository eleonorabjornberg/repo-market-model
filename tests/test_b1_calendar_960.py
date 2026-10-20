"""B1', the calendar-aware persistence of #960 (H5 step 5, H1 step 3; development tier).

`repo_model.b1_calendar.b1_calendar_forecast` is checked against `Hand`, an independent restatement written in the
test from the definition in `metadata/b1_calendar_960.json`: the anchor is the spread of the last ordinary day at or
before the as-of anchor; the changes are `spread[e] - last_ordinary[e - h]` over the trailing two years, pooled by the
target's reporting day type with a floor of 30 changes (else every type). Stdlib only. What these tests pin: the
anchor, including an anchor days after the last ordinary row (a weekend or holiday between rows); the pool and its
fallback; the window; that the benchmarks' own anchor rule is the one used; and that a change to every spread after the
anchor moves nothing.

Written before the code: the module did not exist (`ModuleNotFoundError: No module named 'repo_model.b1_calendar'`).

Recorded mutation (the as-of guard; run on the tests named, then restored):

* `b1_calendar_forecast`: `range(max(first, h), anchor + 1)` replaced with `range(max(first, h), anchor + 2)`, so the
  row after the anchor, not public at the decision instant, is read. `AsOfTests.test_a_spread_after_the_anchor_moves_nothing`
  (and four `ForecastTests`) errored with `LookAheadError` (raised by `protocol_benchmarks._require_public`:
  "B1' for 2023-01-23, lead 1 reads 2023-01-23, after 2023-01-20, the last row public at the decision instant");
  restored, they pass.
"""

from __future__ import annotations

import dataclasses
import unittest

from repo_model import b1_calendar as b1c
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp

import test_protocol_benchmarks as tpb


def setup():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class Hand:
    """B1' from the definition, in the test's own words."""

    def __init__(self, panel, settings):
        self.panel, self.splits = panel, settings["splits"]
        self.settings = settings

    def kind(self, s):
        return self.splits.reporting_day_type(self.panel[s].date, self.panel[s].values)

    def anchor(self, t):
        return pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])

    def last_ordinary(self, s):
        while s >= 0 and self.kind(s) != "ordinary":
            s -= 1
        return s if s >= 0 else None

    def changes(self, t, h):
        a = self.anchor(t)
        first = pb._window_start(self.panel, t, 2)
        ends = [e for e in range(max(first, h), a + 1) if self.last_ordinary(e - h) is not None]
        same = [e for e in ends if self.kind(e) == self.kind(t + h)]
        pool = same if len(same) >= 30 else ends
        return sorted(self.panel[e].spread_bps - self.panel[self.last_ordinary(e - h)].spread_bps for e in pool), len(same)

    def forecast(self, t):
        centre = self.panel[self.last_ordinary(self.anchor(t))].spread_bps
        return {h: pb.empirical_quantiles(self.changes(t, h)[0], centre) for h in sp.HORIZONS}


def find(panel, settings, wanted):
    """The first decision row after the first two years for which `wanted(hand, t)` holds."""
    hand = Hand(panel, settings)
    for t in range(520, len(panel) - 6):
        if wanted(hand, t):
            return hand, t
    raise AssertionError("no such decision day on the published panel")


class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_it_matches_the_definition_on_sampled_days(self):
        hand = Hand(self.panel, self.settings)
        for t in (520, 700, 905, 1200, 1500, 1800, len(self.panel) - 12):
            got = b1c.b1_calendar_forecast(self.panel, t, **self.settings)
            self.assertEqual(sorted(got), list(sp.HORIZONS))
            want = hand.forecast(t)
            for h in sp.HORIZONS:
                self.assertEqual(len(got[h]), len(sp.GRID))
                for x, y in zip(got[h], want[h]):
                    self.assertAlmostEqual(x, y)

    def test_an_ordinary_anchor_is_its_own_centre(self):
        hand, t = find(self.panel, self.settings, lambda h, t: h.kind(h.anchor(t)) == "ordinary")
        a = hand.anchor(t)
        self.assertEqual(hand.last_ordinary(a), a)
        got = b1c.b1_calendar_forecast(self.panel, t, **self.settings)
        want = pb.empirical_quantiles(hand.changes(t, 1)[0], self.panel[a].spread_bps)
        for x, y in zip(got[1], want):
            self.assertAlmostEqual(x, y)

    def test_a_risk_anchor_is_centred_on_the_last_ordinary_spread(self):
        hand, t = find(self.panel, self.settings, lambda h, t: h.kind(h.anchor(t)) != "ordinary")
        a = hand.anchor(t)
        o = hand.last_ordinary(a)
        self.assertLess(o, a)
        self.assertNotEqual(self.panel[o].spread_bps, self.panel[a].spread_bps)
        got = b1c.b1_calendar_forecast(self.panel, t, **self.settings)
        changes = hand.changes(t, 3)[0]
        want = pb.empirical_quantiles(changes, self.panel[o].spread_bps)
        for x, y in zip(got[3], want):
            self.assertAlmostEqual(x, y)

    def test_a_weekend_or_holiday_between_rows_does_not_shorten_the_walk_back(self):
        # the walk back is over panel rows (business days), so a weekend or holiday between two rows costs nothing
        hand, t = find(self.panel, self.settings,
                       lambda h, t: (h.panel[h.anchor(t)].date - h.panel[h.last_ordinary(h.anchor(t))].date).days >= 3
                       and h.kind(h.anchor(t)) != "ordinary")
        o = hand.last_ordinary(hand.anchor(t))
        got = b1c.b1_calendar_forecast(self.panel, t, **self.settings)
        want = pb.empirical_quantiles(hand.changes(t, 1)[0], self.panel[o].spread_bps)
        for x, y in zip(got[1], want):
            self.assertAlmostEqual(x, y)

    def test_a_target_type_with_few_changes_falls_back_to_every_type(self):
        hand, t = find(self.panel, self.settings, lambda h, t: h.changes(t, 1)[1] < 30 and h.kind(t + 1) != "ordinary")
        pooled = b1c.b1_calendar_forecast(self.panel, t, **self.settings)[1]
        a = hand.anchor(t)
        first = pb._window_start(self.panel, t, 2)
        every = sorted(self.panel[e].spread_bps - self.panel[hand.last_ordinary(e - 1)].spread_bps
                       for e in range(max(first, 1), a + 1) if hand.last_ordinary(e - 1) is not None)
        want = pb.empirical_quantiles(every, self.panel[hand.last_ordinary(a)].spread_bps)
        for x, y in zip(pooled, want):
            self.assertAlmostEqual(x, y)

    def test_a_target_type_with_enough_changes_is_pooled_by_type(self):
        hand, t = find(self.panel, self.settings, lambda h, t: h.changes(t, 1)[1] >= 30 and h.kind(t + 1) == "ordinary")
        pooled = b1c.b1_calendar_forecast(self.panel, t, **self.settings)[1]
        a = hand.anchor(t)
        first = pb._window_start(self.panel, t, 2)
        allends = sorted(self.panel[e].spread_bps - self.panel[hand.last_ordinary(e - 1)].spread_bps
                         for e in range(max(first, 1), a + 1) if hand.last_ordinary(e - 1) is not None)
        centre = self.panel[hand.last_ordinary(a)].spread_bps
        self.assertNotEqual([round(x, 9) for x in pooled], [round(x, 9) for x in pb.empirical_quantiles(allends, centre)])

    def test_it_is_not_b1(self):
        t = 1500
        b1 = pb.b1_forecast(self.panel, t, registry=self.settings["registry"], decision_time=self.settings["decision_time"])
        self.assertNotEqual(b1c.b1_calendar_forecast(self.panel, t, **self.settings), b1)

    def test_it_is_a_valid_forecast_for_the_scorer(self):
        got = b1c.b1_calendar_forecast(self.panel, 1500, **self.settings)
        for h in sp.HORIZONS:
            self.assertEqual(got[h], sorted(got[h]))


class AsOfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_a_spread_after_the_anchor_moves_nothing(self):
        t = 1200
        a = Hand(self.panel, self.settings).anchor(t)
        shocked = list(self.panel)
        for i in range(a + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 500.0)
        self.assertEqual(b1c.b1_calendar_forecast(self.panel, t, **self.settings),
                         b1c.b1_calendar_forecast(shocked, t, **self.settings))

    def test_a_panel_without_a_target_row_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            b1c.b1_calendar_forecast(self.panel[:1500], 1498, **self.settings)


if __name__ == "__main__":
    unittest.main()
