"""B2's thin-pool fallback of #1155 (H5 step 2, benchmarks), in force since #1198 on her `GO #1155`: minimum pool 4.

`repo_model.b2_pool.b2_fallback_forecast` is B2 (`protocol_benchmarks.b2_forecast_no_minimum`) with a minimum pool and a declared
chain; `protocol_benchmarks.b2_forecast`, the B2 the protocol scores, is this function while `b2_pool.IN_FORCE` is True: a target whose own type has fewer than `pool_min` rows in the trailing year takes the first later step of its chain
that has `pool_min`, else every day of the window. `Hand` restates it in the test's own words. What these tests pin: the
pure choice (`choose_pool`), including the boundary at `pool_min`; that a pool with enough rows is exactly B2's; that a
year-end target with no earlier year-end in the window is forecast instead of refused; the chain's order; and that a
change to every spread after the anchor moves nothing.

#1198 rewrote the draft-state tests (the switch is off, the record is a draft, `b2_forecast` is plain B2) into in-force ones,
and watched them fail first: `POOL_MIN` was 10, `IN_FORCE` False, the record in `drafts/`, `b2_forecast` refused a first
year-end. The explicit `pool_min` of 10 below is the drafted alternative, kept as a parameter of the function.

Written before the code: the module did not exist (`ModuleNotFoundError: No module named 'repo_model.b2_pool'`).

Recorded mutation (the as-of guard; run on `AsOfTests` and `ForecastTests`, then restored):

* `b2_fallback_forecast`: `range(first, anchor + 1)` replaced with `range(first, anchor + 2)`, so the row after the anchor,
  not public at the decision instant, is counted and sampled. `AsOfTests.test_a_spread_after_the_anchor_moves_nothing` errored
  with `LookAheadError` (raised by `protocol_benchmarks._require_public`: "B2 pool for ... reads ..., after ..., the last row
  public at the decision instant"); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import json
import unittest
from datetime import date
from unittest import mock

from repo_model import b2_pool
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model import turn_days as td

import test_protocol_benchmarks as tpb


def setup():
    panel = tpb.published_panel()["rows"]
    labels = td.TurnLabels(tpb.SPLITS)
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=labels)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class Hand:
    """The fallback from its definition, in the test's own words."""

    def __init__(self, panel, settings, pool_min):
        self.panel, self.settings, self.pool_min = panel, settings, pool_min

    def kind(self, s):
        return self.settings["splits"].reporting_day_type(self.panel[s].date, self.panel[s].values)

    def anchor(self, t):
        return pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])

    def window(self, t):
        return range(pb._window_start(self.panel, t, 1), self.anchor(t) + 1)

    def counts(self, t):
        out = {}
        for s in self.window(t):
            out[self.kind(s)] = out.get(self.kind(s), 0) + 1
        return out

    def rows(self, t, h):
        kind = self.kind(t + h)
        counts = self.counts(t)
        chain = {"year_end": ["year_end", "quarter_end_turn", "turn"], "quarter_end_turn": ["quarter_end_turn", "turn"]}
        for step in chain.get(kind, [kind]):
            if counts.get(step, 0) >= self.pool_min:
                return [s for s in self.window(t) if self.kind(s) == step], step
        return list(self.window(t)), b2_pool.ALL_DAYS

    def forecast(self, t):
        return {h: pb.empirical_quantiles(sorted(self.panel[s].spread_bps for s in self.rows(t, h)[0]))
                for h in sp.HORIZONS}


def find(panel, settings, pool_min, wanted, start=300):
    hand = Hand(panel, settings, pool_min)
    for t in range(start, len(panel) - 6):
        if wanted(hand, t):
            return hand, t
    raise AssertionError("no such decision day on the published panel")


class ChoosePoolTests(unittest.TestCase):
    def test_a_type_with_enough_rows_keeps_its_own_pool(self):
        self.assertEqual(b2_pool.choose_pool("turn", {"turn": 15}, 10), "turn")

    def test_the_boundary_is_inclusive(self):
        self.assertEqual(b2_pool.choose_pool("turn", {"turn": 10}, 10), "turn")
        self.assertEqual(b2_pool.choose_pool("turn", {"turn": 9}, 10), b2_pool.ALL_DAYS)

    def test_year_end_walks_its_chain_in_order(self):
        counts = {"year_end": 2, "quarter_end_turn": 5, "turn": 15}
        self.assertEqual(b2_pool.choose_pool("year_end", counts, 10), "turn")
        self.assertEqual(b2_pool.choose_pool("year_end", {**counts, "quarter_end_turn": 10}, 10), "quarter_end_turn")
        self.assertEqual(b2_pool.choose_pool("year_end", {**counts, "year_end": 10}, 10), "year_end")
        self.assertEqual(b2_pool.choose_pool("year_end", {**counts, "turn": 9}, 10), b2_pool.ALL_DAYS)

    def test_a_minimum_of_four_sends_only_year_end_to_the_quarter_end_turn(self):
        thin = {"year_end": 2, "quarter_end_turn": 4, "turn": 12, "tax_date": 10}
        self.assertEqual(b2_pool.choose_pool("year_end", thin, 4), "quarter_end_turn")
        self.assertEqual(b2_pool.choose_pool("quarter_end_turn", thin, 4), "quarter_end_turn")
        self.assertEqual(b2_pool.choose_pool("turn", thin, 4), "turn")
        self.assertEqual(b2_pool.choose_pool("tax_date", thin, 4), "tax_date")
        self.assertEqual(b2_pool.choose_pool("quarter_end_turn", thin, 10), "turn")

    def test_a_missing_type_counts_as_empty(self):
        self.assertEqual(b2_pool.choose_pool("year_end", {}, 1), b2_pool.ALL_DAYS)

    def test_a_quarter_end_turn_never_falls_to_a_year_end_pool(self):
        self.assertEqual(b2_pool.choose_pool("quarter_end_turn", {"quarter_end_turn": 4, "year_end": 50}, 10), b2_pool.ALL_DAYS)

    def test_ordinary_and_tax_date_go_straight_to_every_day(self):
        self.assertEqual(b2_pool.choose_pool("tax_date", {"tax_date": 3, "turn": 50}, 10), b2_pool.ALL_DAYS)
        self.assertEqual(b2_pool.choose_pool("ordinary", {"ordinary": 200}, 10), "ordinary")

    def test_a_minimum_below_one_is_refused(self):
        with self.assertRaises(ValueError):
            b2_pool.choose_pool("turn", {"turn": 1}, 0)

    def test_the_declared_chains_use_the_turn_labels(self):
        for kind, chain in b2_pool.CHAINS.items():
            self.assertIn(kind, td.LABELS)
            self.assertEqual(chain[0], kind)
            self.assertTrue(set(chain) <= set(td.LABELS))
        self.assertEqual(b2_pool.CHAINS["year_end"], ("year_end", "quarter_end_turn", "turn"))
        self.assertEqual(b2_pool.POOL_MIN, 4)


class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_it_matches_the_definition_on_sampled_days(self):
        hand = Hand(self.panel, self.settings, b2_pool.POOL_MIN)
        self.assertEqual(b2_pool.POOL_MIN, 4)
        for t in (300, 520, 905, 1200, 1500, 1800, len(self.panel) - 12):
            got = b2_pool.b2_fallback_forecast(self.panel, t, **self.settings)
            self.assertEqual(sorted(got), list(sp.HORIZONS))
            want = hand.forecast(t)
            for h in sp.HORIZONS:
                self.assertEqual(len(got[h]), len(sp.GRID))
                for x, y in zip(got[h], want[h]):
                    self.assertAlmostEqual(x, y)

    def test_a_pool_with_enough_rows_is_exactly_b2(self):
        hand, t = find(self.panel, self.settings, 10, lambda h, t: all(h.rows(t, k)[1] == h.kind(t + k) for k in sp.HORIZONS))
        plain = pb.b2_forecast_no_minimum(self.panel, t, **self.settings)
        self.assertEqual(b2_pool.b2_fallback_forecast(self.panel, t, pool_min=10, **self.settings), plain)

    def test_a_year_end_target_with_a_thin_pool_reads_the_turn_pool(self):
        hand, t = find(self.panel, self.settings, 10,
                       lambda h, t: h.kind(t + 1) == "year_end" and h.counts(t).get("year_end", 0) < 10
                       and h.counts(t).get("quarter_end_turn", 0) < 10 and h.counts(t).get("turn", 0) >= 10)
        used = {}
        got = b2_pool.b2_fallback_forecast(self.panel, t, pool_min=10, used=used, **self.settings)
        self.assertEqual(used[1][0], "turn")
        want = pb.empirical_quantiles(sorted(self.panel[s].spread_bps for s in hand.rows(t, 1)[0]))
        for x, y in zip(got[1], want):
            self.assertAlmostEqual(x, y)
        self.assertGreaterEqual(used[1][1], 10)

    def test_the_first_year_end_of_a_panel_is_forecast_instead_of_refused(self):
        hand, t = find(self.panel, self.settings, 10,
                       lambda h, t: h.kind(t + 1) == "year_end" and h.counts(t).get("year_end", 0) == 0, start=5)
        with self.assertRaises(sp.ProtocolError):
            pb.b2_forecast_no_minimum(self.panel, t, **self.settings)
        got = b2_pool.b2_fallback_forecast(self.panel, t, **self.settings)
        self.assertEqual(got[1], sorted(got[1]))
        self.assertEqual(pb.b2_forecast(self.panel, t, **self.settings), got)

    def test_a_larger_minimum_widens_the_pool(self):
        hand, t = find(self.panel, self.settings, 30,
                       lambda h, t: h.kind(t + 1) == "turn" and 10 <= h.counts(t).get("turn", 0) < 30)
        used10, used30 = {}, {}
        b2_pool.b2_fallback_forecast(self.panel, t, pool_min=10, used=used10, **self.settings)
        b2_pool.b2_fallback_forecast(self.panel, t, pool_min=30, used=used30, **self.settings)
        self.assertEqual(used10[1][0], "turn")
        self.assertEqual(used30[1][0], b2_pool.ALL_DAYS)
        self.assertGreater(used30[1][1], used10[1][1])

    def test_it_is_a_valid_forecast_for_the_scorer(self):
        got = b2_pool.b2_fallback_forecast(self.panel, 1500, **self.settings)
        for h in sp.HORIZONS:
            self.assertEqual(got[h], sorted(got[h]))

    def test_the_record_is_in_force_with_her_go(self):
        record = b2_pool.ROOT / "docs" / "decisions" / "b2-thin-pool.md"
        self.assertTrue(b2_pool.IN_FORCE)
        self.assertTrue(record.exists())
        self.assertFalse((b2_pool.ROOT / "docs" / "decisions" / "drafts" / "b2-thin-pool.md").exists())
        text = record.read_text(encoding="utf-8")
        self.assertIn("**Status: in force.**", text)
        self.assertIn("GO #1155", text)
        self.assertNotIn("not in force", text)
        self.assertEqual(b2_pool.POOL_MIN, 4)

    def test_the_switch_and_the_record_move_together(self):
        self.assertEqual(b2_pool.IN_FORCE, (b2_pool.ROOT / "docs" / "decisions" / "b2-thin-pool.md").exists())

    def test_the_attestation_names_this_change(self):
        entries = json.loads((b2_pool.ROOT / "metadata" / "owner_attestations.json").read_text())["attestations"]
        mine = [e for e in entries if e["issue"] == 1155 and e["comment_id"] == 6387463494 and "IN_FORCE True" in e["what"]]
        self.assertEqual(len(mine), 1)
        self.assertEqual(mine[0]["kind"], "decisions")
        self.assertEqual(mine[0]["phrase"], "GO #1155")


class WiringTests(unittest.TestCase):
    """`protocol_benchmarks.b2_forecast` is the fallback while the record is in force, and plain B2 when the switch is off."""

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_b2_forecast_is_the_fallback_with_the_declared_minimum(self):
        for t in (300, 905, 1500, len(self.panel) - 12):
            self.assertEqual(pb.b2_forecast(self.panel, t, **self.settings),
                             b2_pool.b2_fallback_forecast(self.panel, t, pool_min=4, **self.settings))

    def test_only_year_end_changes_pool_at_a_minimum_of_four(self):
        for t in range(300, len(self.panel) - 6, 7):
            a = pb.b2_forecast(self.panel, t, **self.settings)
            b = pb.b2_forecast_no_minimum(self.panel, t, **self.settings)
            for h in sp.HORIZONS:
                kind = td.reporting_day_type(self.settings["splits"], self.panel[t + h].date, self.panel[t + h].values)
                if kind != "year_end":
                    self.assertEqual(a[h], b[h], (t, h, kind))

    def test_with_the_switch_off_b2_is_plain(self):
        t = 1500
        with mock.patch.object(b2_pool, "IN_FORCE", False):
            self.assertEqual(pb.b2_forecast(self.panel, t, **self.settings),
                             pb.b2_forecast_no_minimum(self.panel, t, **self.settings))

    def test_every_decision_day_of_the_published_panel_is_forecast(self):
        # the first year-end of the panel is refused by plain B2 and is forecast now
        refused = 0
        for t in range(5, len(self.panel) - 6, 3):
            try:
                pb.b2_forecast_no_minimum(self.panel, t, **self.settings)
            except sp.ProtocolError:
                refused += 1
            pb.b2_forecast(self.panel, t, **self.settings)
        self.assertGreater(refused, 0)


class AsOfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = setup()

    def test_a_spread_after_the_anchor_moves_nothing(self):
        t = 1200
        a = Hand(self.panel, self.settings, 10).anchor(t)
        shocked = list(self.panel)
        for i in range(a + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 500.0)
        self.assertEqual(b2_pool.b2_fallback_forecast(self.panel, t, **self.settings),
                         b2_pool.b2_fallback_forecast(shocked, t, **self.settings))

    def test_a_panel_without_a_target_row_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            b2_pool.b2_fallback_forecast(self.panel[:1500], 1498, **self.settings)


if __name__ == "__main__":
    unittest.main()
