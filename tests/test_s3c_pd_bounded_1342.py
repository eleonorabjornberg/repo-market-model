"""`scripts/s3c_pd_bounded_1342.py` (#1342; H5 step 3, development tier): (s3c-pd) with the weekly-carry bound, at the 18:00 decision, against
(s3c-ann-net) and (s3c).

Written first, against the declaration (`metadata/s3c_pd_bounded_1342.json`). What these tests pin: that the declaration names what the module has
(the issue, the seed, the models, the references, the 18:00 instant, the scored variant `carry_bounded_v2` of `metadata/s3c_pd_1329.json`); that the
states the study reads are the bounded ones at the 18:00 instant (the bound is the panel's constant and the decision-day check of #1341 holds: a
level two missed prints old, or older than the bound from the decision day, is no state); the four classes a decision day falls in (fresh, carried
within the bound, removed by the bound, no state otherwise) on a hand case; the test plan; the refusal of a state walk whose (s3) is not the frame's;
the refusal of a decision instant other than 18:00; a small run of `score` and `page` end to end on the fixture panel; and, once the full run is
committed, that the tracked page is what the script renders from the tracked record.

Recorded mutation (the staleness guard of this study, #1342): in `s3c_pd_bounded_1342.bounded_states`, `max_carry_days=MAX_CARRY_DAYS` was changed to
`max_carry_days=None` (the unbounded read of #1296's record). Three tests failed with `AssertionError`:
`BoundedStateTests.test_a_level_two_missed_prints_old_is_no_state` (`1.3779... is not None`: the unbounded read carried the stale level),
`BoundedStateTests.test_a_snapshot_that_stops_short_of_the_decision_day_is_no_state` (`1.0602... is not None`) and
`BoundedStateTests.test_the_classes_of_a_hand_case` (`'carried' != 'removed_by_bound'`); restored, they pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from types import SimpleNamespace

from repo_model import data as data_module
from repo_model import s3c_pd as pd
from repo_model import scoring_protocol as sp

from test_s3c_pd import wednesdays, weekly

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_pd_bounded_1342", ROOT / "scripts" / "s3c_pd_bounded_1342.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_pd_bounded_1342"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1342)
        self.assertEqual(script.SEED, 1342)
        self.assertIn("seed 1342", declaration["scoring"]["test"])
        self.assertEqual(declaration["variant"], "carry_bounded_v2")
        self.assertEqual(declaration["models"], ["B1", "B1_prime", "B2", script.S3C, script.ANNNET, script.PDB])
        self.assertEqual(list(script.MODELS), declaration["models"])
        self.assertEqual([r["name"] for r in declaration["references"]], [script.ANNNET, script.S3C, "B1", "B1_prime", "B2"])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertEqual(script.DECISION_TIME, time(18, 0))
        self.assertEqual(sorted(declaration["state_classes"]), sorted(script.CLASSES))
        self.assertIn("never a verdict", declaration["status"])

    def test_the_variant_is_the_one_declared_by_1329_and_that_file_is_not_edited_here(self):
        older = json.loads((ROOT / "metadata" / "s3c_pd_1329.json").read_text(encoding="utf-8"))
        self.assertIn(script.declaration_variant(), older["variants"])
        self.assertIs(older["variants"][script.declaration_variant()]["scored"], False)

    def test_the_candidate_is_tested_against_the_two_named_references(self):
        self.assertEqual(script.plan(script.PDB), [script.ANNNET, script.S3C])
        self.assertEqual(script.plan(script.S3C), [])


class BoundedStateTests(unittest.TestCase):
    """The states are the bounded ones, read at 18:00.

    Recorded mutation: see the module docstring (`bounded_states`).
    """

    FIRST = date(2024, 1, 3)

    def levels(self, withhold=()):
        values = [100.0 + (i % 7) * 3.0 + i * 0.5 for i in range(80)]
        for i in withhold:
            values[i] = None
        return weekly(values, first=self.FIRST)

    def day_after_release(self, week):
        return pd.release_instant(week).date() + timedelta(days=1)

    def test_the_bound_is_the_panels_constant(self):
        self.assertEqual(script.MAX_CARRY_DAYS, data_module.WEEKLY_CARRY_MAX_STALENESS_DAYS)
        self.assertEqual(script.MAX_CARRY_DAYS, 13)

    def test_a_level_two_missed_prints_old_is_no_state(self):
        levels = self.levels(withhold=(60, 61, 62))
        weeks = wednesdays(self.FIRST, 80)
        day = self.day_after_release(weeks[62])
        states = script.bounded_states(levels, [day])
        self.assertIsNone(states[day])
        self.assertIsNotNone(pd.state_at(levels, day, max_carry_days=None))

    def test_one_missed_print_is_carried_and_a_fresh_week_reads_its_own_level(self):
        levels = self.levels(withhold=(61,))
        weeks = wednesdays(self.FIRST, 80)
        carried = self.day_after_release(weeks[61])
        fresh = self.day_after_release(weeks[62])
        states = script.bounded_states(levels, [carried, fresh])
        self.assertAlmostEqual(states[carried], pd.state_at(levels, carried), places=12)
        self.assertIsNotNone(states[carried])
        self.assertIsNotNone(states[fresh])

    def test_the_instant_is_18_00_so_the_release_day_reads_the_new_week(self):
        levels = self.levels()
        weeks = wednesdays(self.FIRST, 80)
        release_day = pd.release_instant(weeks[60]).date()
        self.assertEqual(pd.latest_public_week(levels, release_day, decision_time=script.DECISION_TIME), weeks[60])
        states = script.bounded_states(levels, [release_day])
        self.assertAlmostEqual(states[release_day], pd.state_at(levels, release_day, decision_time=time(18, 0)), places=12)

    def test_a_snapshot_that_stops_short_of_the_decision_day_is_no_state(self):
        levels = self.levels()
        weeks = wednesdays(self.FIRST, 80)
        last = pd.release_instant(weeks[-1]).date()
        late = last + timedelta(days=script.MAX_CARRY_DAYS + 1)
        self.assertIsNone(script.bounded_states(levels, [late])[late])
        self.assertIsNotNone(script.bounded_states(levels, [last + timedelta(days=script.MAX_CARRY_DAYS)])[last + timedelta(days=script.MAX_CARRY_DAYS)])

    def test_the_classes_of_a_hand_case(self):
        levels = self.levels(withhold=(60, 61, 62))
        weeks = wednesdays(self.FIRST, 80)
        cases = {
            "fresh": self.day_after_release(weeks[59]),  # the latest public week has a level
            "carried": self.day_after_release(weeks[60]),  # one week skipped, 7 days: within the bound
            "removed_by_bound": self.day_after_release(weeks[61]),  # two weeks skipped, 14 days: the bound removes the level
            "no_state": self.FIRST + timedelta(days=7 * 9 + 14),  # fewer than 13 weeks of history
        }
        for label, day in cases.items():
            self.assertEqual(script.state_class(levels, day), label, f"{label}: {day}")
        self.assertEqual(script.state_class(levels, self.day_after_release(weeks[63])), "fresh")

    def test_the_four_classes_are_declared(self):
        self.assertEqual(script.CLASSES, ("fresh", "carried", "removed_by_bound", "no_state"))
        self.assertEqual(sorted(script.CLASS_TITLES), sorted(script.CLASSES))


class InstantTests(unittest.TestCase):

    def test_another_decision_instant_is_refused(self):
        script.require_instant(time(18, 0))
        with self.assertRaises(ValueError):
            script.require_instant(time(16, 0))


class WalkTests(unittest.TestCase):

    def frame(self):
        days = [date(2026, 7, 6) + timedelta(days=i) for i in range(3)]
        return SimpleNamespace(days=days, forecasts={script.S3: {d: {h: list(Q) for h in sp.HORIZONS} for d in days}})

    def walk(self, frame, differ=False, drop=False):
        days = list(frame.days)
        s3 = {d: {h: ([x + 1.0 for x in Q] if differ and d == days[1] else list(Q)) for h in sp.HORIZONS} for d in days}
        forecasts = {d: s3[d] for d in days[1:]} if drop else dict(s3)
        return SimpleNamespace(forecasts=forecasts, s3=s3)

    def test_a_walk_with_the_frames_s3_is_accepted(self):
        frame = self.frame()
        script.require_same_s3(frame, self.walk(frame))

    def test_a_walk_whose_s3_differs_from_the_frames_is_refused(self):
        frame = self.frame()
        with self.assertRaises(ValueError):
            script.require_same_s3(frame, self.walk(frame, differ=True))

    def test_a_frame_day_missing_from_the_walk_is_refused(self):
        frame = self.frame()
        with self.assertRaises(ValueError):
            script.require_same_s3(frame, self.walk(frame, drop=True))


class PageTests(unittest.TestCase):

    def test_the_question_has_numbered_options_and_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("**Options**", text)
        self.assertIn("(default)", text)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-11-03"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--draws", "20", "--reps", "5",
                     "--workers", "2", "--first", cls.FIRST])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_both_windows_are_scored_inside_the_limit_at_18_00(self):
        self.assertEqual(sorted(self.result["windows"]), sorted(script.WINDOWS))
        self.assertEqual(self.result["decision_time"], "18:00")
        for window, w in self.result["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertLessEqual(w["notes"]["last_target"], script.LAST_DAY.isoformat())

    def test_the_candidate_is_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["vs"][script.PDB]), sorted(script.plan(script.PDB)))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_state_classes_partition_the_decision_days(self):
        for w in self.result["windows"].values():
            groups = w["groups"][script.CLASS_SPLIT]
            self.assertEqual(sum(g["days"] for g in groups.values()), w["groups"]["pooled"]["all decision days"]["days"])
            self.assertEqual(sum(w["term_use"]["class_counts"].values()), w["term_use"]["decision_days"])

    def test_every_state_the_study_read_is_within_the_bound(self):
        self.assertEqual(self.result["bound_days"], data_module.WEEKLY_CARRY_MAX_STALENESS_DAYS)
        for w in self.result["windows"].values():
            self.assertLessEqual(w["term_use"]["largest_level_age_days"], self.result["bound_days"])

    def test_the_page_says_it_is_development_data_and_ends_with_the_marked_question(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("Development data, not a verdict", text)
        self.assertIn("Lens C", text)
        self.assertIn("#1296", text)
        self.assertIn("## Question for Eleonora", text)
        self.assertNotIn("GO #", text)
        self.assertTrue(text.rstrip().splitlines()[-1].startswith("3."))


class TrackedPageTests(unittest.TestCase):
    """Once the full run is committed, the tracked page is what the script renders from the tracked record."""

    RECORD = ROOT / "docs" / "research" / "s3c-pd-bounded-1342" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-pd-bounded-1342-result.md"

    def test_the_tracked_page_is_rendered_from_the_tracked_record(self):
        if not self.RECORD.exists() or not self.PAGE.exists():
            self.skipTest("the full run is not committed yet")
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(script.render(record), self.PAGE.read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual(record["decision_time"], "18:00")
        self.assertEqual(record["draws"], sp.DRAWS)


if __name__ == "__main__":
    unittest.main()
