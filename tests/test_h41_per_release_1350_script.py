"""`scripts/h41_per_release_1350.py` (#1350; H5 step 3, development tier): the H.4.1 weeklies read per release at the 18:00 decision, against the carried
reading in force, on (s3c-ann-net), (s3c+state) and (s3c-ann-net x state).

Written first, against the declaration. The guard on the per-release read and its recorded mutation are in `test_h41_per_release_read_1350`. What these
tests pin: that the declaration names what the module has (seed, models, arms, references, the last day, the 18:00 instant, the one amendment that
changes no figure); the test plan (each per-release arm against its carried counterpart, (s3c-ann-net) and (s3c)); the Wednesday of a panel row; the
state check on a hand case (a level read of a different week on a Thursday, the state moving, the largest age against the weekly-carry bound); the cells
that differ, by weekday and lead; the scope helpers that give the Thursday, Friday and Monday-to-Wednesday decisions their own cells; the refusal to write
a record whose references are not #1321's; the page (the marked question carries numbered options and a default, the registry is said to be unchanged); a
small run of `score` and `page` end to end on the fixture panel; and, once the full run is committed, that the tracked page is what the script renders from
the tracked record.

Recorded mutation (the check of this study, #1350): in `h41_per_release_1350.walks_of`, the comparison `if d not in walks[key].forecasts[arm.name]:` was
changed to `if False:`. `WalkTests.test_a_scored_day_without_a_forecast_is_refused` then failed with `AssertionError` (`ValueError not raised`); restored,
it passes.
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

from repo_model import scoring_protocol as sp
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("h41_per_release_1350", ROOT / "scripts" / "h41_per_release_1350.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["h41_per_release_1350"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class Frame:
    def __init__(self, n=30):
        self.dates = business_days(date(2026, 6, 29), n)
        self.days = [d for d in self.dates if date(2026, 7, 6) <= d <= date(2026, 7, 24)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]

    def regime(self, d):
        return "2026"


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1350)
        self.assertEqual(script.SEED, 1350)
        self.assertIn("seed 1350", declaration["scoring"]["test"])
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.ANNNET, *script.ARMS])
        self.assertEqual([r["name"] for r in declaration["references"]], [script.ANNNET, script.S3C, "B1", "B1_prime", "B2"])
        self.assertEqual(declaration["models"], ["B1", "B1_prime", "B2", script.S3C, script.ANNNET, *script.ARMS])
        self.assertEqual(list(script.MODELS), declaration["models"])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual([a["changes_a_figure"] for a in declaration["amendments"]], [False])
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertEqual(script.DECISION_TIME, time(18, 0))
        self.assertIn("not changed", declaration["status"])

    def test_every_arm_is_tested_against_its_counterpart_and_the_two_candidates(self):
        for arm in script.ARMS:
            plan = script.PLAN[arm]
            self.assertIn(script.S3C, plan)
            self.assertIn(script.ANNNET, plan)
            if arm in script.COUNTERPART:
                self.assertIn(script.COUNTERPART[arm], plan)
        self.assertEqual(sorted(script.COUNTERPART), sorted([script.PRN, script.S3SP, script.ANSP]))

    def test_the_scopes_are_thursday_friday_and_the_rest(self):
        scopes = {name: days for name, _title, days in script.SCOPES}
        self.assertEqual(scopes["thursday"], (3,))
        self.assertEqual(scopes["friday"], (4,))
        self.assertEqual(sorted(scopes["all"]), sorted(scopes["mon_wed"] + scopes["thursday"] + scopes["friday"]))


class StateCheckTests(unittest.TestCase):

    def test_the_wednesday_of_a_row(self):
        self.assertEqual(script.wednesday_of(date(2026, 7, 8)), date(2026, 7, 8))
        self.assertEqual(script.wednesday_of(date(2026, 7, 9)), date(2026, 7, 8))
        self.assertEqual(script.wednesday_of(date(2026, 7, 13)), date(2026, 7, 8))
        self.assertEqual(script.wednesday_of(date(2026, 7, 14)), date(2026, 7, 8))
        self.assertEqual(script.wednesday_of(date(2026, 7, 15)), date(2026, 7, 15))

    def test_the_check_counts_the_decisions_where_the_level_and_the_state_differ(self):
        def row(day, read, state, age):
            return {"decision_day": day, "scored_day": day, "state": state, "read": read, "age_days": age}

        carried = [row(date(2026, 7, 8), date(2026, 7, 1), 2.0, 7), row(date(2026, 7, 9), date(2026, 7, 2), 2.0, 8),
                   row(date(2026, 7, 10), date(2026, 7, 3), 2.0, 9), row(date(2026, 7, 13), date(2026, 7, 8), 2.0, 5)]
        per = [row(date(2026, 7, 8), date(2026, 7, 1), 2.0, 7), row(date(2026, 7, 9), date(2026, 7, 9), 3.0, 1),
               row(date(2026, 7, 10), date(2026, 7, 10), 3.0, 2), row(date(2026, 7, 13), date(2026, 7, 13), 2.0, 5)]
        check = script.state_check(carried, per)
        self.assertEqual(check["by_weekday"]["Wednesday"], {"decisions": 1, "level_differs": 0, "state_differs": 0})
        self.assertEqual(check["by_weekday"]["Thursday"], {"decisions": 1, "level_differs": 1, "state_differs": 1})
        self.assertEqual(check["by_weekday"]["Friday"], {"decisions": 1, "level_differs": 1, "state_differs": 1})
        self.assertEqual(check["by_weekday"]["Monday"], {"decisions": 1, "level_differs": 0, "state_differs": 0})
        self.assertEqual([x["decision_day"] for x in check["state_changes"]], ["2026-07-09", "2026-07-10"])
        self.assertEqual(check["max_age_days"], {"carried": 9, "per_release": 7})
        self.assertEqual(check["reads_checked_by_guard"], 4)
        self.assertEqual(check["weekly_carry_bound_days"], 13)

    def test_a_subset_start_leaves_out_the_earlier_decisions(self):
        def row(day, read, state):
            return {"decision_day": day, "scored_day": day, "state": state, "read": read, "age_days": 1}

        carried = [row(date(2026, 7, 9), date(2026, 7, 2), 2.0), row(date(2026, 7, 16), date(2026, 7, 9), 2.0)]
        per = [row(date(2026, 7, 9), date(2026, 7, 9), 3.0), row(date(2026, 7, 16), date(2026, 7, 16), 3.0)]
        check = script.state_check(carried, per, first=date(2026, 7, 10))
        self.assertEqual(check["by_weekday"]["Thursday"]["decisions"], 1)
        self.assertEqual([x["decision_day"] for x in check["state_changes"]], ["2026-07-16"])


class CellsTests(unittest.TestCase):

    def test_the_cells_that_differ_are_counted_by_weekday_and_lead(self):
        frame = Frame()
        frame.forecasts = {"a": {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days},
                           "b": {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}}
        thursday = next(d for d in frame.days if d.weekday() == 3)
        frame.forecasts["b"][thursday][2] = [x + 0.5 for x in Q]
        frame.forecasts["b"][thursday][4] = [x + 0.5 for x in Q]
        out = script.cells_differ(frame, "a", "b")
        self.assertEqual(out["differing_cells"]["Thursday"], {"1": 0, "2": 1, "3": 0, "4": 1, "5": 0})
        self.assertEqual(sum(sum(v.values()) for k, v in out["differing_cells"].items() if k != "Thursday"), 0)
        self.assertEqual(out["decision_days"]["Thursday"], 3)

    def test_a_scope_holds_only_its_weekdays(self):
        frame = Frame()
        friday = scoped = script.scoped_frame(frame, (4,))
        self.assertTrue(friday.days and all(d.weekday() == 4 for d in friday.days))
        self.assertEqual(len(frame.days), 15)
        cells = {"grid_crps": {(d, h): 1.0 for d in frame.days for h in sp.HORIZONS}}
        part = script.scoped_cells(cells, (3, 4))
        self.assertEqual({k[0].weekday() for k in part["grid_crps"]}, {3, 4})
        self.assertIs(scoped.dates, frame.dates)


class WalkTests(unittest.TestCase):

    def run_walks(self, drop=None):
        frame = Frame()
        calls = []

        def fake_walk(panel, days, table, states, arms, **kw):
            calls.append((arms[0].name, states))
            forecasts = {a.name: {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days} for a in arms}
            if drop is not None and calls[-1][0] == drop[0] and len(calls) == drop[1]:
                forecasts[drop[0]].pop(frame.days[0])
            return SimpleNamespace(forecasts=forecasts, fits={})

        original = script.sc.walk, script.m1288.candidate_days
        script.sc.walk, script.m1288.candidate_days = fake_walk, lambda *a, **kw: list(frame.days)
        try:
            panel = [DailyObservation(d, {}) for d in frame.dates]
            states = {"constant": {"c": 1.0}, "carried": {"k": 1.0}, "per_release": {"p": 1.0}}
            out = script.walks_of("development", frame, panel, None, {}, {}, None, [], [], None, states)
            return out, calls
        finally:
            script.sc.walk, script.m1288.candidate_days = original

    def test_walks_with_every_scored_day_are_accepted_and_read_the_state_they_name(self):
        (walks, names), calls = self.run_walks()
        self.assertEqual(sorted(walks), ["ans", "ans_p", "ref", "ref_p", "s3s", "s3s_p"])
        self.assertEqual(names["s3s"], script.sc.S3_STATE.name)
        self.assertEqual(names["ans_p"], script.s3c_announced.ANN_NET_ARM.name)
        read = {key: list(states) for (_name, states), key in zip(calls, ["ref", "ref_p", "s3s", "s3s_p", "ans", "ans_p"])}
        self.assertEqual(read, {"ref": ["c"], "ref_p": ["c"], "s3s": ["k"], "s3s_p": ["p"], "ans": ["k"], "ans_p": ["p"]})

    def test_a_scored_day_without_a_forecast_is_refused(self):
        # Recorded mutation: see the module docstring (`walks_of`).
        with self.assertRaises(ValueError):
            self.run_walks(drop=(script.sc.S3_STATE.name, 4))


class AgainstRecordTests(unittest.TestCase):

    def test_references_that_differ_from_1321s_record_are_refused(self):
        if not script.RECORD_1321.exists():
            self.skipTest("#1321's record is not in this tree")
        there = json.loads(script.RECORD_1321.read_text(encoding="utf-8"))["windows"]
        window = next(iter(there))
        group = json.loads(json.dumps(there[window]["groups"]["pooled"]["all decision days"]))
        results = {window: {"groups": {"all": {"pooled": {"all decision days": group}}}}}
        self.assertEqual(script.against_1321(results)[window]["grid_crps"][script.S3C]["difference"], 0.0)
        group["grid_crps"]["means"][script.ANNNET] += 1e-6
        with self.assertRaises(ValueError):
            script.against_1321(results)


class PageTests(unittest.TestCase):

    def test_the_question_has_numbered_options_and_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Question for Eleonora", text)
        self.assertIn("1. **Keep the declared lags; nothing changes** (default).", text)
        self.assertIn("2.", text)
        self.assertIn("default", text)


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

    def test_both_windows_are_scored_inside_the_limit(self):
        self.assertEqual(sorted(self.result["windows"]), sorted(script.WINDOWS))
        for window, w in self.result["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertLessEqual(w["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["decision_time"], "18:00")

    def test_the_arms_are_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["all"]["pooled"]["all decision days"]["grid_crps"]
            for arm in script.ARMS:
                self.assertEqual(sorted(cell["vs"][arm]), sorted(script.PLAN[arm]))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_per_release_run_of_the_candidate_equals_the_candidate(self):
        # (s3c-ann-net) holds the state constant and reads no H.4.1 series: the per-release run of it is the same forecasts, cell for cell.
        for w in self.result["windows"].values():
            entry = w["cells_differ"][f"{script.PRN}|{script.ANNNET}"]
            self.assertEqual(sum(sum(v.values()) for v in entry["differing_cells"].values()), 0)
            vs = w["groups"]["all"]["pooled"]["all decision days"]["grid_crps"]["vs"][script.PRN][script.ANNNET]
            self.assertTrue(vs.get("identical"))

    def test_thursday_and_friday_are_scopes_of_their_own(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["groups"]), ["all", "friday", "mon_wed", "thursday"])
            for scope, weekday in (("thursday", 3), ("friday", 4)):
                days = w["groups"][scope]["pooled"]["all decision days"]["days"]
                self.assertGreater(days, 0)
                self.assertLess(days, w["groups"]["all"]["pooled"]["all decision days"]["days"])

    def test_the_state_read_agrees_from_the_monday_on(self):
        by = self.result["state_check"]["by_weekday"]
        for day in ("Tuesday", "Wednesday"):
            self.assertEqual(by[day]["level_differs"], 0)
            self.assertEqual(by[day]["state_differs"], 0)
        self.assertGreater(by["Thursday"]["level_differs"], 0)
        self.assertLessEqual(self.result["state_check"]["max_age_days"]["per_release"], self.result["state_check"]["weekly_carry_bound_days"])

    def test_the_page_says_the_registry_is_unchanged_and_ends_with_the_marked_question(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("**The registry's reading is not changed here**", text)
        self.assertIn("Development data, not a verdict", text)
        self.assertIn("Lens C", text)
        self.assertTrue(text.rstrip().splitlines()[-1].startswith("4."))
        self.assertIn("## Question for Eleonora", text)


class TrackedPageTests(unittest.TestCase):
    """Once the full run is committed, the tracked page is what the script renders from the tracked record."""

    RECORD = ROOT / "docs" / "research" / "h41-per-release-1350" / "result.json"
    PAGE = ROOT / "docs" / "research" / "h41-per-release-1350-result.md"

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
