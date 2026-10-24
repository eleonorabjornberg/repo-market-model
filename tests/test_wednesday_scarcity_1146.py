"""`scripts/wednesday_scarcity_1146.py` (#1146; H5 step 3, development tier): the Wednesday reserve level as a candidate scarcity input.

Written before the script. The study runs the H5 candidate (#941's scaled mean reversion) with the scarcity state formed from the
week average (as now) and from the Wednesday level (`WRBWFRBL`, same release, same instant), and splits its scores by the state
and on the days where the two states differ. What these tests pin: the declaration; the Wednesday panel (only `reserve_balances`
moves, the dates and the other columns are the published panel's); the release-date guard; the comparison of two walks; the
partition of days by state; and `score` and `page` end to end on the last months of the fixture panel.

Recorded mutation (the guard this script adds, `require_same_release`; the mutated line and the exception the failing test raised):

* In `require_same_release`, replacing `if day not in average_changes:` with `if False:` makes
  `ReleaseGuardTests.test_a_level_that_appears_before_its_week_average_is_refused` fail with `AssertionError: LookAheadError not
  raised` (the Wednesday value stepped three rows before the week average did, and nothing refused it); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("wednesday_scarcity_1146", ROOT / "scripts" / "wednesday_scarcity_1146.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["wednesday_scarcity_1146"] = script
_spec.loader.exec_module(script)


def rows(reserves, start=date(2024, 1, 1)):
    """One row per day with a reserve balance, a TGA and a SOFR/IORB pair."""

    return [
        DailyObservation(start + timedelta(days=i), {"sofr": 5.3, "iorb": 5.4, "reserve_balances": r, "tga": 700.0 + i})
        for i, r in enumerate(reserves)
    ]


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_is_committed_and_names_the_issue_the_one_arm_and_the_limits(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1146)
        self.assertEqual([a["name"] for a in declaration["arms"]["listed_in_full"]], ["spread_mr_fhs_mad20_f0.5"])
        self.assertFalse(declaration["arms"]["listed_in_full"][0]["reads_scarcity_state"])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scoring"]["bootstrap"]["seed"], script.SEED)
        self.assertEqual(declaration["scoring"]["group_minimum_days"], script.MIN_GROUP_DAYS)
        self.assertFalse(declaration["limits"]["published_declaration_changed"])
        self.assertFalse(declaration["limits"]["sources_registry_changed"])

    def test_the_candidate_is_the_one_the_queue_names(self):
        self.assertEqual(script.CANDIDATE, "spread_mr_fhs_mad20_f0.5")
        self.assertIn(script.CANDIDATE, [v.name for v in script.fhs.VARIANTS])


class WednesdayPanelTests(unittest.TestCase):

    def test_only_the_reserve_balance_moves(self):
        published = rows([100.0, 100.0, 110.0, 110.0])
        level = rows([95.0, 95.0, 120.0, 120.0])
        out = script.wednesday_panel(published, level)
        self.assertEqual([r.values["reserve_balances"] for r in out], [95.0, 95.0, 120.0, 120.0])
        for before, after in zip(published, out):
            self.assertEqual(before.date, after.date)
            self.assertEqual({k: v for k, v in before.values.items() if k != "reserve_balances"},
                             {k: v for k, v in after.values.items() if k != "reserve_balances"})
        self.assertEqual([r.values["reserve_balances"] for r in published], [100.0, 100.0, 110.0, 110.0])  # not edited

    def test_other_dates_are_a_data_error(self):
        with self.assertRaisesRegex(ValueError, "dates"):
            script.wednesday_panel(rows([1.0, 2.0]), rows([1.0, 2.0, 3.0]))

    def test_a_hole_in_the_level_stays_a_hole_and_is_never_filled_with_the_average(self):
        out = script.wednesday_panel(rows([100.0, 100.0]), rows([None, 90.0]))
        self.assertIsNone(out[0].values["reserve_balances"])


class ReleaseGuardTests(unittest.TestCase):
    """A Wednesday level is a line of the same release as the week average: its value may step only on a row where the average's
    does, never earlier (`h41_wednesday_levels_970`, 'same release, same instant')."""

    def test_a_level_that_steps_with_its_week_average_passes(self):
        script.require_same_release(rows([100, 100, 100, 110, 110]), rows([95, 95, 95, 120, 120]))

    def test_a_level_that_appears_before_its_week_average_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_same_release(rows([100, 100, 100, 110, 110]), rows([95, 95, 120, 120, 120]))

    def test_a_level_that_holds_while_the_average_steps_is_not_a_look_ahead(self):
        script.require_same_release(rows([100, 100, 110]), rows([95, 95, 95]))


class SameForecastsTests(unittest.TestCase):

    def test_equal_walks_have_every_cell_identical(self):
        q = {date(2024, 1, 2): {1: [0.0, 1.0], 2: [0.5, 1.5]}}
        report = script.compare_forecasts(q, {d: {h: list(v) for h, v in leads.items()} for d, leads in q.items()})
        self.assertEqual(report, {"cells": 2, "identical": 2, "max_abs_difference": 0.0})

    def test_a_moved_quantile_is_counted_and_its_size_reported(self):
        a = {date(2024, 1, 2): {1: [0.0, 1.0], 2: [0.5, 1.5]}}
        b = {date(2024, 1, 2): {1: [0.0, 1.0], 2: [0.5, 1.75]}}
        report = script.compare_forecasts(a, b)
        self.assertEqual((report["cells"], report["identical"]), (2, 1))
        self.assertAlmostEqual(report["max_abs_difference"], 0.25)

    def test_walks_on_other_days_are_a_data_error(self):
        with self.assertRaisesRegex(ValueError, "days"):
            script.compare_forecasts({date(2024, 1, 2): {1: [0.0]}}, {date(2024, 1, 3): {1: [0.0]}})


class PartitionTests(unittest.TestCase):
    D = [date(2024, 1, 1) + timedelta(days=i) for i in range(6)]

    def test_days_split_into_differ_and_agree_with_direction(self):
        avg = dict(zip(self.D, [0.0, 1.0, 2.0, 3.0, None, 2.0]))
        wed = dict(zip(self.D, [0.0, 2.0, 1.0, 3.0, None, None]))
        p = script.partition(avg, wed, self.D)
        self.assertEqual(p["differ"], [self.D[1], self.D[2], self.D[5]])
        self.assertEqual(p["up"], [self.D[1]])
        self.assertEqual(p["down"], [self.D[2], self.D[5]])  # a state that becomes a hole counts as a change, down
        self.assertEqual(p["agree"], [self.D[0], self.D[3], self.D[4]])
        self.assertEqual(sorted(p["differ"] + p["agree"]), self.D)

    def test_a_group_of_days_by_state_leaves_holes_out_and_names_each_state(self):
        states = dict(zip(self.D, [0.0, 1.0, 1.0, 3.0, None, 3.0]))
        by = script.by_state(states, self.D)
        self.assertEqual(by, {"0": [self.D[0]], "1": [self.D[1], self.D[2]], "3": [self.D[3], self.D[5]], "hole": [self.D[4]]})


class ReadingTests(unittest.TestCase):

    def test_a_skill_needs_the_interval_to_clear_zero_and_a_small_group_has_none(self):
        self.assertEqual(script.verdict({"skill_interval": [0.01, 0.05]}), "gain")
        self.assertEqual(script.verdict({"skill_interval": [-0.05, -0.01]}), "loss")
        self.assertEqual(script.verdict({"skill_interval": [-0.01, 0.05]}), "undecided")
        self.assertEqual(script.verdict(None), "undecided")


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-03-03"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["score", "--panel", str(cls.panel_path), "--first", cls.FIRST, "--draws", "20", "--output", str(cls.output)])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))
        cls.text = cls.page.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_candidate_forecasts_are_the_same_under_both_readings(self):
        same = self.result["candidate_under_both_readings"]
        self.assertGreater(same["cells"], 0)
        self.assertEqual(same["identical"], same["cells"])
        self.assertEqual(same["max_abs_difference"], 0.0)

    def test_the_state_is_formed_from_both_readings_at_every_lead(self):
        for h in ("1", "2", "3", "4", "5"):
            self.assertIn(h, self.result["state_movement"])
            self.assertIn("changed", self.result["state_movement"][h])

    def test_the_splits_the_ruling_names_are_all_there(self):
        groups = self.result["groups"]
        self.assertIn("pooled", groups)
        self.assertIn("state_week_average", groups)
        self.assertIn("state_wednesday_level", groups)
        self.assertIn("readings", groups)
        for label in ("agree", "differ"):
            self.assertIn(label, groups["readings"])
        self.assertIn("differ_by_regime", self.result)
        self.assertIn("differ_by_day_type", self.result)

    def test_b1_prime_sits_beside_b1_and_no_day_after_the_last_scored_day_is_read(self):
        entry = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertIn("B1_prime", entry["means"])
        self.assertIn("B1", entry["means"])
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_the_page_says_the_candidate_does_not_read_the_state_and_ends_with_the_marked_question(self):
        text = self.text
        self.assertIn("development data, not a verdict", text.lower())
        self.assertIn("does not read the scarcity state", text)
        tail = text[text.index("## Question for Eleonora"):]
        self.assertEqual(text.count("## Question for Eleonora"), 1)
        for option in ("1. **", "2. **", "3. **"):
            self.assertIn(option, tail)
        self.assertIn("(default)", tail)
        self.assertIn("Nothing is adopted here, nothing is registered", tail)
        self.assertTrue(tail.rstrip().splitlines()[-1].startswith("3."))


if __name__ == "__main__":
    unittest.main()
