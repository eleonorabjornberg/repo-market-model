"""Ranking the next 20 business days by tail probability combined with the day type (#765; H8 step 2, development tier).

`metadata/ranking_765.json` is the declaration; `repo_model.ranking_daytype` is its arithmetic. Three rankers, each
built on the model of #686 on 20 leads (`repo_model.ranking`, unchanged): the calendar first with the tail probability
inside it, the tail probability from a residual pool of the target's day type, and a blend of the two ranks with a
weight chosen on trailing scored windows.

What these tests pin: the mid-ranks and the blend, the calendar-first score, the day-type pool (its membership, its
fallback when thin, the band of leads), the weight chosen on trailing windows (the grid, the default, the tie rule), the
as-of guards (no pool pair and no trailing window reads a row after the anchor; a change to every spread after the
anchor moves no ranker and no weight), and the declaration against the module.

Recorded mutations (the new leakage guards; each run on the tests named, then restored):

* `residual_pools`: `pb._require_public(targets, anchor, dates, ...)` replaced with
  `pb._require_public(targets, anchor + 400, dates, ...)`, so a pool pair whose target is after the anchor is admitted.
  `PoolTests.test_a_pool_pair_after_the_anchor_is_refused` failed with `AssertionError` ("LookAheadError not raised");
  restored, it passes.
* `trailing_windows`: `if window.index + max(LEADS) <= anchor:` replaced with
  `if window.index + max(LEADS) <= anchor + 5:`, so a window whose last targets are after the anchor is weighed.
  `WeightTests.test_a_change_to_every_spread_after_the_anchor_moves_no_weight` failed with `LookAheadError` ("... reads
  ..., after ..., the last row public at the decision instant", raised by `protocol_benchmarks._require_public`);
  restored, it passes.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from repo_model import protocol_benchmarks as pb
from repo_model import ranking
from repo_model import ranking_daytype as rd
from repo_model import spread_mean_reversion as smr
from repo_model.splits import LookAheadError

import test_ranking as tr

ROOT = Path(__file__).resolve().parent.parent


class RankTests(unittest.TestCase):

    def test_mid_ranks_share_the_places_of_a_tie(self):
        self.assertEqual(rd.rank_scores([0.1, 0.5, 0.5, 0.9]), [0.125, 0.5, 0.5, 0.875])

    def test_all_tied_is_all_in_the_middle(self):
        self.assertEqual(rd.rank_scores([0.3] * 4), [0.5] * 4)

    def test_the_blend_is_the_weighted_mean_of_the_two_ranks(self):
        cal = [0.0, 0.0, 1.0, 1.0]
        tail = [0.9, 0.1, 0.2, 0.3]
        blend = rd.blend_scores(cal, tail, 0.25)
        for b, c, t in zip(blend, rd.rank_scores(cal), rd.rank_scores(tail)):
            self.assertAlmostEqual(b, 0.25 * c + 0.75 * t)

    def test_a_weight_outside_the_grid_is_refused(self):
        with self.assertRaises(ValueError):
            rd.blend_scores([0.0, 1.0], [0.5, 0.5], 0.3)

    def test_the_calendar_comes_first_and_the_tail_breaks_its_ties(self):
        scores = rd.calendar_then_tail([0.0, 1.0, 0.0, 1.0], [0.9, 0.1, 0.8, 0.2])
        order = sorted(range(4), key=lambda i: -scores[i])
        self.assertEqual(order, [3, 1, 0, 2])


class WeightTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = tr.panel_and_settings()
        cls.t = tr.decision_index(cls.panel, "2022-03-07")
        cls.anchor = pb._anchor(cls.panel, cls.t, cls.settings["registry"], cls.settings["decision_time"])

    def window(self, perfect_calendar, n=1):
        flags = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cal = [float(f) for f in flags] if perfect_calendar else [0.0] * 20
        tail = [1.0 - 0.01 * i if not perfect_calendar else 0.01 * i for i in range(20)]
        return cal, tail, flags

    def test_before_the_minimum_the_weight_is_the_default(self):
        windows = [self.window(True) for _ in range(rd.MIN_TRAILING - 1)]
        self.assertEqual(rd.choose_weight(windows), (rd.DEFAULT_WEIGHT, rd.MIN_TRAILING - 1))

    def test_a_calendar_that_is_right_and_a_tail_that_is_reversed_takes_the_smallest_weight_that_lets_the_calendar_lead(self):
        windows = [self.window(True) for _ in range(rd.MIN_TRAILING)]
        weight, used = rd.choose_weight(windows)
        self.assertEqual((weight, used), (0.75, rd.MIN_TRAILING))

    def test_a_tail_that_is_right_and_a_blind_calendar_takes_the_tail(self):
        windows = [self.window(False) for _ in range(rd.MIN_TRAILING)]
        self.assertEqual(rd.choose_weight(windows)[0], 0.0)

    def quiet_window(self):
        flags = [0] * 20
        return [0.0] * 20, [1.0 - 0.01 * i for i in range(20)], flags

    def test_windows_that_hold_no_pressure_day_take_the_default_not_the_tie_break(self):
        """#930, ruling on #925: every grid weight ties at zero precision, which the tie-break sent to w = 0.0.

        Failed on main with `AssertionError: (0.0, 60) != (0.5, 60)`; the tie-break line is the one under test.
        """
        windows = [self.quiet_window() for _ in range(rd.MIN_TRAILING)]
        self.assertEqual(rd.choose_weight(windows), (rd.DEFAULT_WEIGHT, rd.MIN_TRAILING))

    def test_one_pressure_day_among_the_trailing_windows_restores_the_choice(self):
        windows = [self.quiet_window() for _ in range(rd.MIN_TRAILING - 1)] + [self.window(False)]
        self.assertEqual(rd.choose_weight(windows)[0], 0.0)

    def test_a_pressure_day_older_than_the_trailing_windows_does_not_count(self):
        windows = [self.window(False)] + [self.quiet_window() for _ in range(rd.TRAILING)]
        self.assertEqual(rd.choose_weight(windows), (rd.DEFAULT_WEIGHT, rd.TRAILING))

    def test_a_tie_among_windows_that_hold_a_pressure_day_still_goes_to_the_smaller_weight(self):
        flags = [1] + [0] * 19
        flat = ([0.5] * 20, [0.5] * 20, flags)
        windows = [flat for _ in range(rd.MIN_TRAILING)]
        self.assertEqual(rd.choose_weight(windows)[0], 0.0)

    def test_only_the_latest_trailing_windows_are_weighed(self):
        old = [self.window(True) for _ in range(40)]
        recent = [self.window(False) for _ in range(rd.TRAILING)]
        self.assertEqual(rd.choose_weight(old + recent), (0.0, rd.TRAILING))

    def test_only_windows_complete_by_the_anchor_are_eligible(self):
        history = [rd.Window(i, [0.0] * 20, [0.0] * 20) for i in range(self.t - 60, self.t - 1)]
        eligible = rd.trailing_windows(history, self.panel, self.anchor)
        self.assertTrue(eligible)
        self.assertEqual(len(eligible), sum(1 for w in history if w.index + 20 <= self.anchor))
        for cal, tail, flags in eligible:
            self.assertEqual(len(flags), 20)

    def test_a_change_to_every_spread_after_the_anchor_moves_no_weight(self):
        history = [rd.Window(i, [0.0] * 20, [0.01 * j for j in range(20)]) for i in range(self.t - 120, self.t - 1)]
        base = rd.trailing_windows(history, self.panel, self.anchor)
        shocked = list(self.panel)
        for i in range(self.anchor + 1, len(shocked)):
            shocked[i] = tr.with_spread(shocked[i], 250.0 + i)
        self.assertEqual(base, rd.trailing_windows(history, shocked, self.anchor))


class PoolTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = tr.panel_and_settings()
        cls.t = tr.decision_index(cls.panel, "2022-03-07")
        cls.fit = ranking.fit(cls.panel, cls.t, **cls.settings)
        cls.anchor = pb._anchor(cls.panel, cls.t, cls.settings["registry"], cls.settings["decision_time"])
        cls.pools = rd.residual_pools(cls.panel, cls.t, cls.fit, **cls.settings)

    def test_every_pool_is_a_sorted_list_of_residuals_of_its_type(self):
        for (kind, lead), values in self.pools.items():
            self.assertIn(kind, ("quarter_end", "month_end", "tax_date", "ordinary"))
            self.assertIn(lead, ranking.LEADS)
            self.assertEqual(values, sorted(values))

    def test_a_pool_takes_the_leads_within_the_band(self):
        counts = {(kind, lead): len(values) for (kind, lead), values in self.pools.items()}
        rows = ranking.training_rows(
            self.panel, self.t, self.anchor, lag=self.t - self.anchor,
            levels=smr.ordinary_levels(self.panel, self.settings["splits"]), leads=ranking.LEADS,
        )
        kinds = lambda s: self.settings["splits"].reporting_day_type(self.panel[s].date, self.panel[s].values)  # noqa: E731
        for lead in (1, 10, 20):
            for kind in ("ordinary", "quarter_end"):
                band = range(max(1, lead - rd.POOL_BAND), min(20, lead + rd.POOL_BAND) + 1)
                expect = sum(1 for h in band for _, s in rows[h] if kinds(s) == kind)
                self.assertEqual(counts.get((kind, lead), 0), expect)

    def test_a_thin_pool_falls_back_to_the_step_one_residuals(self):
        thin = {key: values for key, values in self.pools.items() if key[0] != "quarter_end"}
        quantiles, fallback = rd.typed_quantiles(self.panel, self.t, self.fit, thin, **self.settings)
        base = ranking.forecast(self.panel, self.t, self.fit, **self.settings)
        for lead in ranking.LEADS:
            kind = self.settings["splits"].reporting_day_type(self.panel[self.t + lead].date, self.panel[self.t + lead].values)
            if kind == "quarter_end":
                self.assertTrue(fallback[lead])
                self.assertEqual(quantiles[lead], base[lead])

    def test_a_pool_at_the_minimum_is_used(self):
        self.assertTrue(any(len(v) >= rd.MIN_POOL for v in self.pools.values()))
        quantiles, fallback = rd.typed_quantiles(self.panel, self.t, self.fit, self.pools, **self.settings)
        base = ranking.forecast(self.panel, self.t, self.fit, **self.settings)
        used = [h for h in ranking.LEADS if not fallback[h]]
        self.assertTrue(used)
        self.assertTrue(any(quantiles[h] != base[h] for h in used))
        for h in used:
            self.assertEqual(quantiles[h], sorted(quantiles[h]))

    def test_a_pool_pair_after_the_anchor_is_refused(self):
        rows = ranking.training_rows(
            self.panel, self.t, self.anchor, lag=self.t - self.anchor,
            levels=smr.ordinary_levels(self.panel, self.settings["splits"]), leads=ranking.LEADS,
        )
        bad = {h: list(pairs) for h, pairs in rows.items()}
        bad[3].append((self.anchor - 2, self.anchor + 2))
        with self.assertRaises(LookAheadError):
            rd.residual_pools(self.panel, self.t, self.fit, rows=bad, **self.settings)


class ScoreTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = tr.panel_and_settings()
        cls.t = tr.decision_index(cls.panel, "2022-03-07")
        cls.anchor = pb._anchor(cls.panel, cls.t, cls.settings["registry"], cls.settings["decision_time"])

    def scores(self, panel):
        fit = ranking.fit(panel, self.t, **self.settings)
        pools = rd.residual_pools(panel, self.t, fit, **self.settings)
        return rd.window_scores(panel, self.t, fit, pools, **self.settings)

    def test_the_new_rankers_score_twenty_days_beside_the_old(self):
        scores = self.scores(self.panel)
        for name in ("calendar_then_tail", "tail_by_type", "model_prob", "calendar", "climatology", "persistence"):
            self.assertEqual(len(scores[name]), 20, name)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in scores["tail_by_type"]))

    def test_a_future_spread_moves_no_score(self):
        shocked = list(self.panel)
        for i in range(self.anchor + 1, len(shocked)):
            shocked[i] = tr.with_spread(shocked[i], 250.0 + i)
        self.assertEqual(self.scores(self.panel), self.scores(shocked))

    def test_the_calendar_then_tail_never_puts_a_quiet_day_above_a_risk_date(self):
        scores = self.scores(self.panel)
        cal, mixed = scores["calendar"], scores["calendar_then_tail"]
        risk = [m for c, m in zip(cal, mixed) if c == 1.0]
        quiet = [m for c, m in zip(cal, mixed) if c == 0.0]
        self.assertTrue(risk and quiet)
        self.assertGreater(min(risk), max(quiet))


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = tr.panel_and_settings()
        first = tr.decision_index(cls.panel, "2022-03-07")
        cls.days = [row.date for row in cls.panel[first: first + 70]]
        cls.walk = rd.walk(cls.panel, cls.days, **cls.settings)

    def test_every_scored_window_carries_every_ranker(self):
        self.assertTrue(self.walk.scores)
        for scores in self.walk.scores.values():
            self.assertEqual(
                set(scores),
                {"calendar_then_tail", "tail_by_type", "blend", "model_prob", "model_median", "calendar", "climatology", "persistence"},
            )
            self.assertTrue(all(len(v) == 20 for v in scores.values()))

    def test_the_weight_is_chosen_at_each_refit_from_the_grid(self):
        self.assertEqual(set(self.walk.weights), set(self.walk.fits))
        for weight, used in self.walk.weights.values():
            self.assertIn(weight, rd.WEIGHT_GRID)
            self.assertLessEqual(used, rd.TRAILING)

    def test_the_first_refit_has_no_trailing_window_and_takes_the_default(self):
        first = min(self.walk.weights)
        self.assertEqual(self.walk.weights[first], (rd.DEFAULT_WEIGHT, 0))

    def test_the_fallback_share_is_a_share(self):
        self.assertTrue(0.0 <= self.walk.fallback_share() <= 1.0)


class DeclarationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.declaration = json.loads((ROOT / "metadata" / "ranking_765.json").read_text(encoding="utf-8"))

    def test_the_declaration_names_the_constants_of_the_module(self):
        r = self.declaration["candidates"]
        self.assertEqual(r["tail_by_type"]["pool_band"], rd.POOL_BAND)
        self.assertEqual(r["tail_by_type"]["min_pool"], rd.MIN_POOL)
        self.assertEqual(tuple(r["blend"]["weight_grid"]), rd.WEIGHT_GRID)
        self.assertEqual(r["blend"]["default_weight"], rd.DEFAULT_WEIGHT)
        self.assertEqual(r["blend"]["trailing_windows"], rd.TRAILING)
        self.assertEqual(r["blend"]["min_trailing_windows"], rd.MIN_TRAILING)

    def test_at_most_three_rankers_and_they_are_the_modules(self):
        self.assertEqual(set(self.declaration["candidates"]), set(rd.CANDIDATES))
        self.assertLessEqual(len(rd.CANDIDATES), self.declaration["limits"]["max_rankers"])
        self.assertEqual(self.declaration["limits"]["max_rankers"], 3)

    def test_the_declared_last_day_is_the_modules(self):
        self.assertEqual(self.declaration["limits"]["last_day"], ranking.LAST_DAY.isoformat())


if __name__ == "__main__":
    unittest.main()
