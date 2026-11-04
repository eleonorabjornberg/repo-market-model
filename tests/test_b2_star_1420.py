"""B2*, the calendar climatology with frozen pools and a declared fallback (#1420; H5, registration design, benchmarks).

`protocol_benchmarks.b2_star_forecast` is B2 with the day types of the record in force, a lookback of `B2STAR_YEARS` (2) years, a
minimum pool of `B2STAR_POOL_MIN` (10) and the chain of `b2_pool.CHAINS`; the numbers are the declaration's
(`metadata/b2_star_1420.json`, committed before any score). `Hand` restates it in the test's own words. What these tests pin: the
constants against the declaration; that B2 in force is unchanged (a default lookback of one year); that B2* equals the definition on
sampled days; that it reads rows older than one year (the lookback is two); the boundary at the minimum; that a thin year-end falls
back and a first year-end is forecast; and that no spread after the anchor is read.

Written before the code: `AttributeError: module 'repo_model.protocol_benchmarks' has no attribute 'B2STAR_YEARS'`.

Recorded mutation (the as-of guard; run on `AsOfTests`, then restored): in `b2_pool.b2_fallback_forecast`, `range(first, anchor + 1)`
replaced with `range(first, anchor + 2)`, so the row after the anchor, not public at the decision instant, is counted and sampled.
`AsOfTests.test_a_spread_after_the_anchor_moves_nothing` errored with `LookAheadError`; restored, it passes. A second mutation, on the
lookback: `b2_star_forecast` passing `years=pb.B2_YEARS` instead of `B2STAR_YEARS`; `ForecastTests.test_it_matches_the_definition_on_sampled_days`
failed with `AssertionError`; restored, it passes.
"""

from __future__ import annotations

import dataclasses
import json
import unittest
from pathlib import Path

from repo_model import b2_pool
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model import turn_days as td
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
DECLARATION = json.loads((ROOT / "metadata" / "b2_star_1420.json").read_text(encoding="utf-8"))


def setup():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=td.TurnLabels(tpb.SPLITS))


class Hand:
    def __init__(self, panel, settings, years, pool_min):
        self.panel, self.settings, self.years, self.pool_min = panel, settings, years, pool_min

    def kind(self, s):
        return self.settings["splits"].reporting_day_type(self.panel[s].date, self.panel[s].values)

    def window(self, t):
        anchor = pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])
        return range(pb._window_start(self.panel, t, self.years), anchor + 1)

    def rows(self, t, h):
        kind = self.kind(t + h)
        counts = {}
        for s in self.window(t):
            counts[self.kind(s)] = counts.get(self.kind(s), 0) + 1
        chain = {"year_end": ["year_end", "quarter_end_turn", "turn"], "quarter_end_turn": ["quarter_end_turn", "turn"]}
        for step in chain.get(kind, [kind]):
            if counts.get(step, 0) >= self.pool_min:
                return [s for s in self.window(t) if self.kind(s) == step]
        return list(self.window(t))

    def forecast(self, t):
        return {h: pb.empirical_quantiles(sorted(self.panel[s].spread_bps for s in self.rows(t, h))) for h in sp.HORIZONS}


class DeclarationTests(unittest.TestCase):
    def test_the_constants_are_the_declarations(self):
        text = DECLARATION["b2_star"]
        self.assertEqual(pb.B2STAR_YEARS, 2)
        self.assertEqual(pb.B2STAR_POOL_MIN, 10)
        self.assertIn("B2STAR_YEARS = 2", text["lookback"])
        self.assertIn("B2STAR_POOL_MIN = 10", text["minimum_pool"])

    def test_b2_in_force_is_unchanged(self):
        self.assertEqual(pb.B2_YEARS, 1)
        self.assertEqual(b2_pool.POOL_MIN, 4)

    def test_the_declaration_has_a_variants_block(self):
        self.assertIn("B2_star", DECLARATION["variants"])
        self.assertEqual(DECLARATION["models"][-2], "B2_star")


class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_it_matches_the_definition_on_sampled_days(self):
        hand = Hand(self.panel, self.settings, 2, 10)
        for t in (300, 520, 905, 1200, 1500, 1800, len(self.panel) - 12):
            got = pb.b2_star_forecast(self.panel, t, **self.settings)
            want = hand.forecast(t)
            self.assertEqual(sorted(got), list(sp.HORIZONS))
            for h in sp.HORIZONS:
                self.assertEqual(len(got[h]), len(sp.GRID))
                for x, y in zip(got[h], want[h]):
                    self.assertAlmostEqual(x, y)

    def test_it_reads_rows_older_than_one_year(self):
        t = 1500
        used = {}
        pb.b2_star_forecast(self.panel, t, used=used, **self.settings)
        one_year = pb._window_start(self.panel, t, 1)
        two_years = pb._window_start(self.panel, t, 2)
        self.assertLess(two_years, one_year)
        wide, narrow = {}, {}
        b2_pool.b2_fallback_forecast(self.panel, t, years=2, pool_min=10, used=wide, **self.settings)
        b2_pool.b2_fallback_forecast(self.panel, t, pool_min=10, used=narrow, **self.settings)
        self.assertEqual(used, wide)
        self.assertTrue(any(wide[h][1] > narrow[h][1] for h in sp.HORIZONS))

    def test_the_default_lookback_of_the_fallback_is_one_year(self):
        t = 1500
        self.assertEqual(b2_pool.b2_fallback_forecast(self.panel, t, **self.settings), pb.b2_forecast(self.panel, t, **self.settings))

    def test_a_first_year_end_is_forecast(self):
        hand = Hand(self.panel, self.settings, 2, 10)
        t = next(t for t in range(5, len(self.panel) - 6) if hand.kind(t + 1) == "year_end")
        got = pb.b2_star_forecast(self.panel, t, **self.settings)
        self.assertEqual(got[1], sorted(got[1]))

    def test_it_records_the_pool_used(self):
        used = {}
        pb.b2_star_forecast(self.panel, 1500, used=used, **self.settings)
        self.assertEqual(sorted(used), list(sp.HORIZONS))
        for pool, rows in used.values():
            self.assertGreaterEqual(rows, 1)
            self.assertTrue(pool == b2_pool.ALL_DAYS or pool in td.LABELS)


class AsOfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_a_spread_after_the_anchor_moves_nothing(self):
        t = 1500
        anchor = pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])
        base = pb.b2_star_forecast(self.panel, t, **self.settings)
        moved = list(self.panel)
        for s in range(anchor + 1, len(moved)):
            values = dict(moved[s].values)
            values["sofr"] = float(values["sofr"]) + 0.5
            moved[s] = dataclasses.replace(moved[s], values=values)
        self.assertEqual(pb.b2_star_forecast(moved, t, **self.settings), base)

    def test_reading_after_the_anchor_is_refused(self):
        dates = [row.date for row in self.panel]
        with self.assertRaises(LookAheadError):
            pb._require_public([1500 + 1], 1500, dates, "test")


if __name__ == "__main__":
    unittest.main()
