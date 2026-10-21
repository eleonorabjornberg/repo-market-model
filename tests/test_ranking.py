"""Ranking the next 20 business days by risk (#694; H8, development tier).

`metadata/ranking_694.json` is the declaration; `repo_model.ranking` is its arithmetic. The candidate is the model of
#686 on leads 1..20; the benchmarks are B1 persistence, climatology by day type and the calendar of known risk dates.

What these tests pin: the top-k arithmetic and its tie rules on hand cases, the 20-lead fit against the model of
#686 on the leads they share, the as-of guard (a training row after the anchor is refused, and a change to every
spread after the anchor moves no ranker's scores), the climatology's share, the calendar's reading, and the
scored-day guard.

Recorded mutations (the new leakage guards; each run on the tests named, then restored):

* `training_rows`: `range(max(first, k), anchor + 1)` over the target rows replaced with `range(max(first, k), anchor + 2)`,
  so a pair whose target is the row after the anchor is trained on. `test_a_future_spread_moves_no_score` and
  `test_the_training_window_stops_at_the_anchor` failed with `LookAheadError` ("... reads ..., after ..., the last row
  public at the decision instant", raised by `protocol_benchmarks._require_public`); restored, both pass.
* `require_scored_days`: `if day > last:` replaced with `if day > last + timedelta(days=400):`, so a day after the
  declared end is admitted. `ScopeTests.test_a_day_after_the_declared_end_is_refused` failed with `AssertionError`
  ("LookAheadError not raised"); restored, it passes.
* `walk`'s `except LookAheadError: raise` removed (code review), so a guard trip before the first fit is skipped as
  "no public row". `WalkGuardTests.test_a_guard_trip_before_the_first_fit_is_raised_not_skipped` failed with
  `AssertionError: LookAheadError not raised`; restored, it passes.
"""

from __future__ import annotations

import dataclasses
import json
import unittest
import unittest.mock
from datetime import date
from pathlib import Path

from repo_model import protocol_benchmarks as pb
from repo_model import ranking
from repo_model import scoring_protocol as sp
from repo_model import spread_mean_reversion as smr
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent


def panel_and_settings():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def decision_index(panel, day):
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class TopKTests(unittest.TestCase):

    def test_the_best_scores_are_taken(self):
        scores = [0.1, 0.9, 0.5, 0.7]
        flags = [0, 1, 0, 1]
        self.assertEqual(ranking.top_k_hits(scores, flags, 2), 2.0)
        self.assertEqual(ranking.top_k_hits(scores, flags, 1), 1.0)

    def test_a_ranker_that_puts_the_pressure_days_last_scores_nothing(self):
        self.assertEqual(ranking.top_k_hits([0.9, 0.8, 0.1, 0.0], [0, 0, 1, 1], 2), 0.0)

    def test_a_tie_that_straddles_the_cutoff_contributes_its_share(self):
        # one place left among three tied days, one of which is a pressure day: 1/3 of a hit in expectation
        scores = [1.0, 0.5, 0.5, 0.5, 0.0]
        flags = [0, 0, 1, 0, 0]
        self.assertAlmostEqual(ranking.top_k_hits(scores, flags, 2), 1.0 / 3.0)

    def test_a_tie_that_fits_inside_the_cutoff_is_counted_whole(self):
        self.assertEqual(ranking.top_k_hits([0.5, 0.5, 0.0], [1, 0, 1], 2), 1.0)

    def test_first_mode_takes_the_earliest_of_a_tie(self):
        scores = [0.5, 0.5, 0.5, 0.0]
        self.assertEqual(ranking.top_k_hits(scores, [1, 0, 0, 0], 1, ties="first"), 1.0)
        self.assertEqual(ranking.top_k_hits(scores, [0, 0, 1, 0], 1, ties="first"), 0.0)

    def test_every_day_tied_scores_the_base_rate(self):
        flags = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        self.assertAlmostEqual(ranking.top_k_hits([0.2] * 10, flags, 5) / 5, sum(flags) / len(flags))

    def test_k_beyond_the_window_is_refused(self):
        with self.assertRaises(ValueError):
            ranking.top_k_hits([0.1, 0.2], [0, 1], 3)

    def test_unequal_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            ranking.top_k_hits([0.1, 0.2], [0], 1)

    def test_an_unknown_tie_rule_is_refused(self):
        with self.assertRaises(ValueError):
            ranking.top_k_hits([0.1], [0], 1, ties="random")

    def test_precision_and_recall(self):
        scores = [0.9, 0.8, 0.7, 0.1, 0.0]
        flags = [1, 0, 1, 1, 0]
        metrics = ranking.window_metrics(scores, flags, (3,))
        self.assertAlmostEqual(metrics[3]["precision"], 2.0 / 3.0)
        self.assertAlmostEqual(metrics[3]["recall"], 2.0 / 3.0)

    def test_recall_is_undefined_on_a_window_with_no_pressure_day(self):
        metrics = ranking.window_metrics([0.9, 0.8, 0.7], [0, 0, 0], (3,))
        self.assertEqual(metrics[3]["precision"], 0.0)
        self.assertIsNone(metrics[3]["recall"])


class WalkGuardTests(unittest.TestCase):

    def test_a_guard_trip_before_the_first_fit_is_raised_not_skipped(self):
        panel, settings = panel_and_settings()
        days = [row.date for row in panel if row.date.isoformat() >= "2022-03-07"][:3]

        def tripped(*args, **kwargs):
            raise LookAheadError("a read after the decision instant")

        with unittest.mock.patch.object(ranking, "fit", tripped):
            with self.assertRaises(LookAheadError):
                ranking.walk(panel, days, **settings)


class FitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.t = decision_index(cls.panel, "2022-03-07")

    def test_the_fit_has_twenty_leads_of_the_grid(self):
        fit = ranking.fit(self.panel, self.t, **self.settings)
        self.assertEqual(set(fit.residuals), set(range(1, 21)))
        for lead in fit.residuals.values():
            self.assertEqual(len(lead), len(sp.GRID))
            self.assertEqual(lead, sorted(lead))

    def test_on_the_five_leads_of_686_it_is_the_model_of_686(self):
        mine = ranking.fit(self.panel, self.t, leads=sp.HORIZONS, **self.settings)
        theirs = smr.fit(self.panel, self.t, **self.settings)
        self.assertEqual(mine.phi, theirs.phi)
        self.assertEqual(dict(mine.residuals), dict(theirs.residuals))
        self.assertEqual(
            ranking.forecast(self.panel, self.t, mine, leads=sp.HORIZONS, **self.settings),
            smr.forecast(self.panel, self.t, theirs, **self.settings),
        )

    def test_a_forecast_of_twenty_leads_needs_twenty_target_rows(self):
        with self.assertRaises(sp.ProtocolError):
            ranking.fit(self.panel[: self.t + 10], self.t, **self.settings)

    def test_a_decision_with_too_little_history_is_refused(self):
        with self.assertRaises(smr.InsufficientHistory):
            ranking.fit(self.panel, 20, **self.settings)


class AsOfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.t = decision_index(cls.panel, "2022-03-07")
        cls.anchor = pb._anchor(cls.panel, cls.t, cls.settings["registry"], cls.settings["decision_time"])

    def scores(self, panel):
        fit = ranking.fit(panel, self.t, **self.settings)
        return ranking.window_scores(panel, self.t, fit, **self.settings)

    def test_a_future_spread_moves_no_score(self):
        shocked = list(self.panel)
        for i in range(self.anchor + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 250.0 + i)
        self.assertEqual(self.scores(self.panel), self.scores(shocked))

    def test_the_anchor_spread_does_move_the_scores(self):
        shocked = list(self.panel)
        shocked[self.anchor] = with_spread(shocked[self.anchor], self.panel[self.anchor].spread_bps + 30.0)
        base, moved = self.scores(self.panel), self.scores(shocked)
        self.assertNotEqual(base["model_median"], moved["model_median"])
        self.assertNotEqual(base["persistence"], moved["persistence"])

    def test_the_training_window_stops_at_the_anchor(self):
        rows = ranking.training_rows(
            self.panel, self.t, self.anchor, lag=self.t - self.anchor,
            levels=smr.ordinary_levels(self.panel, tpb.SPLITS), leads=ranking.LEADS,
        )
        self.assertEqual(set(rows), set(ranking.LEADS))
        self.assertLessEqual(max(target for lead in rows.values() for _, target in lead), self.anchor)


class WindowScoreTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.t = decision_index(cls.panel, "2022-03-07")
        cls.fit = ranking.fit(cls.panel, cls.t, **cls.settings)
        cls.scores = ranking.window_scores(cls.panel, cls.t, cls.fit, **cls.settings)

    def test_every_ranker_scores_twenty_days(self):
        self.assertEqual(set(self.scores), {"model_prob", "model_median", "persistence", "climatology", "calendar"})
        for series in self.scores.values():
            self.assertEqual(len(series), 20)

    def test_probabilities_are_probabilities(self):
        for name in ("model_prob", "persistence", "climatology"):
            self.assertTrue(all(0.0 <= value <= 1.0 for value in self.scores[name]))

    def test_the_calendar_is_one_on_a_scheduled_risk_date_and_zero_elsewhere(self):
        for lead, value in enumerate(self.scores["calendar"], start=1):
            values = self.panel[self.t + lead].values
            fixed = float(values["quarter_end"] or 0.0) == 1.0 or float(values["tax_date"] or 0.0) == 1.0
            settles = float(values["treasury_settlement_coupons"] or 0.0) > 0.0 and lead == 1
            self.assertEqual(value, 1.0 if fixed or settles else 0.0)
        self.assertIn(1.0, self.scores["calendar"])
        self.assertIn(0.0, self.scores["calendar"])

    def test_a_coupon_settlement_counts_only_where_it_was_public_at_the_decision(self):
        """A settlement is public one panel day ahead (`metadata/sources.json`), so at lead 1 only (#770).

        Mutation record: in `ranking.calendar`, `risk = available <= rule.decision_instant(dates, scored)` replaced with
        `risk = True`; this test failed with `AssertionError` (1.0 != 0.0 at lead 5, a settlement not yet announced read
        as a risk date); restored, it passes.
        """

        rows = list(self.panel)
        for lead in (1, 5, 9):
            row = rows[self.t + lead]
            values = dict(row.values)
            values.update(quarter_end=0.0, tax_date=0.0, treasury_settlement_coupons=10.0)
            rows[self.t + lead] = dataclasses.replace(row, values=values)
        # lead 9 is a quarter-end, whatever settles: a calendar fact, known ahead
        values = dict(rows[self.t + 9].values)
        values["quarter_end"] = 1.0
        rows[self.t + 9] = dataclasses.replace(rows[self.t + 9], values=values)
        for lead in (2, 3, 4, 6, 7, 8):
            row = rows[self.t + lead]
            values = dict(row.values)
            values.update(quarter_end=0.0, tax_date=0.0, treasury_settlement_coupons=0.0)
            rows[self.t + lead] = dataclasses.replace(row, values=values)
        got = ranking.calendar(rows, self.t, registry=self.settings["registry"], decision_time=self.settings["decision_time"])
        self.assertEqual(got[0], 1.0, "lead 1: the settlement is public")
        self.assertEqual(got[4], 0.0, "lead 5: the settlement was not yet announced, so not a risk date")
        self.assertEqual(got[8], 1.0, "lead 9: a quarter-end is a calendar fact")
        self.assertEqual(got[1], 0.0)


    def test_climatology_is_the_share_of_pressure_days_of_the_targets_type_in_the_trailing_year(self):
        anchor = pb._anchor(self.panel, self.t, self.settings["registry"], self.settings["decision_time"])
        first = pb._window_start(self.panel, self.t, pb.B2_YEARS)
        kinds = {s: tpb.SPLITS.reporting_day_type(self.panel[s].date, self.panel[s].values) for s in range(first, anchor + 1)}
        for lead, value in enumerate(self.scores["climatology"], start=1):
            target = self.panel[self.t + lead]
            kind = tpb.SPLITS.reporting_day_type(target.date, target.values)
            same = [s for s, k in kinds.items() if k == kind]
            hand = sum(1 for s in same if round(self.panel[s].spread_bps) > 5.0) / len(same)
            self.assertAlmostEqual(value, hand, places=12)

    def test_a_type_share_with_no_day_of_the_type_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            ranking.type_share(["ordinary", "ordinary"], [True, False], "quarter_end")

    def test_a_type_share_is_the_share_of_pressure_days_of_that_type(self):
        kinds = ["ordinary", "quarter_end", "ordinary", "quarter_end", "ordinary"]
        pressure = [True, True, False, False, False]
        self.assertAlmostEqual(ranking.type_share(kinds, pressure, "ordinary"), 1.0 / 3.0)
        self.assertEqual(ranking.type_share(kinds, pressure, "quarter_end"), 0.5)

    def test_the_median_is_the_grid_median(self):
        centre = sp.GRID.index(0.5)
        forecast = ranking.forecast(self.panel, self.t, self.fit, **self.settings)
        for lead, value in enumerate(self.scores["model_median"], start=1):
            self.assertEqual(value, forecast[lead][centre])


class ScopeTests(unittest.TestCase):

    def test_a_day_after_the_declared_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            ranking.require_scored_days([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_declared_last_day_is_scored(self):
        ranking.require_scored_days([date(2025, 12, 31)])

    def test_a_locked_day_is_refused_even_when_the_end_is_moved(self):
        with self.assertRaises(LookAheadError):
            ranking.require_scored_days([date(2026, 9, 4)], last=date(2027, 1, 1))

    def test_the_declaration_ends_where_the_module_does(self):
        declaration = json.loads((ROOT / "metadata" / "ranking_694.json").read_text(encoding="utf-8"))
        self.assertEqual(declaration["limits"]["last_day"], ranking.LAST_DAY.isoformat())
        self.assertEqual(declaration["limits"]["max_rankers"], len(ranking.CANDIDATES))


if __name__ == "__main__":
    unittest.main()
