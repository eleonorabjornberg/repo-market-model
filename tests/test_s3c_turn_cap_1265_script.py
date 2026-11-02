"""`scripts/s3c_turn_cap_1265.py` (#1265; H5 step 3, development tier): (s3c-t), (s3c) with the cap off on turn days, scored against (s3),
(s3c), B1, B1' and B2 from the day the limit was removed, the decision days of 24 to 30 December 2025 included.

Written first, against the declaration. The candidate is `repo_model.s3c_turn_cap` (tested in `test_s3c_turn_cap`); the cap, the line and
the full-allotment flag are (s3c)'s (`test_s3c_candidate`). What these tests pin: that the declaration names what the module has (seed, models,
arms, the last day, the first decision day, no amendment); the arms' forecasts and the cell-by-cell check (on a turn-day target (s3c-t) is
(s3), elsewhere it is (s3c)) on hand cases, with the failure when one cell is moved; the Brier cell arithmetic (strict event on whole basis
points; a probability of 0 for an event that happens scores 1); the bound figures (P(> +10 bp) of (s3c) is 0 when the upper quantiles sit
on the line); the event list (a day above +5 and above +10, the leads with an unscored decision day left out); the test plan (the arms before
it, then the benchmarks); the groups (the 24 to 30 December decision days are their own group); the page (the plain statement about the
bound, the marked questions with numbered options and defaults); a small run of `score` and `page` end to end on the fixture panel; and, once
the full run is committed, that the tracked page is what the script renders from the tracked record and that #1255's 2026 window is
reproduced.

Recorded mutation (the check of this study, #1265): in `s3c_turn_cap_1265.turn_check`, the comparison
`elif list(s3ct[d][h]) != list(s3c[d][h]):` was commented out. `TurnCheckTests.test_a_changed_cell_that_is_not_a_turn_day_is_refused` then
failed with `AssertionError` (`ValueError` not raised for a cell moved on 2025-12-08); restored, it passes. Second mutation (the event
definition): in `cell_table`, `data.exceeds_bp(y, tau)` was replaced by `y >= tau`; `CellTableTests.test_the_event_is_strict_on_whole_basis_points`
then failed with `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model import policy_events as pe
from repo_model import scoring_protocol as sp
from repo_model import turn_days

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_turn_cap_1265", ROOT / "scripts" / "s3c_turn_cap_1265.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_turn_cap_1265"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp
ON_LINE = [min(q, 10.0) for q in Q]  # the upper quantiles sit on the 10 bp line


class Frame:
    """The few members of the scoring frame the checks read: business days from 1 December 2025, a decision on each of the first few."""

    def __init__(self, spreads=None):
        day, self.dates = date(2025, 12, 1), []
        while len(self.dates) < 26:
            if day.weekday() < 5:
                self.dates.append(day)
            day += timedelta(days=1)
        self.days = [d for d in self.dates if date(2025, 12, 8) <= d <= date(2025, 12, 24)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.outcome.update(spreads or {})
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]

    def day_type(self, d):
        return turn_days.turn_day_type(d, tax_date=False)


def register():
    def entry(ident, kind, announced, effective, rate, limit="absent"):
        details = {"rate_percent": rate}
        if limit != "absent":
            details["aggregate_operation_limit_bn"] = limit
        return pe.PolicyEntry(ident, kind, "change", ident, datetime.combine(announced, time(14, 0)), "stated", effective, "https://example.org", True, details)

    return pe.known_entries([
        entry("iorb-0", "iorb_rate", date(2021, 6, 16), date(2021, 6, 17), 3.65),
        entry("srf-0", "standing_repo", date(2021, 7, 28), date(2021, 7, 29), 4.0, limit=500),
        entry("srf-full", "standing_repo", date(2025, 12, 10), date(2025, 12, 11), 3.75, limit=None),
    ], datetime(2030, 1, 1))


def forecasts(frame, q=Q):
    return {d: {h: list(q) for h in sp.HORIZONS} for d in frame.days}


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1265)
        self.assertEqual(script.SEED, 1265)
        self.assertIn("seed 1265", declaration["scoring"]["test"])
        self.assertEqual(declaration["candidate"]["name"], script.S3CT)
        self.assertEqual(declaration["candidate"]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], list(script.ARMS))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertIn("2025-12-10", declaration["frame"]["decision_days"])
        self.assertEqual(script.FIRST_DECISION, date(2025, 12, 10))

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_turn_cap_1265.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_turn_cap_1265.json", "scripts/s3c_turn_cap_1265.py", "direct"))

    def test_the_plan_is_the_arms_before_it_then_the_benchmarks(self):
        self.assertEqual(script.plan(script.S3CT), [script.S3C, script.S3, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.S3C), [script.S3, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.S3), ["B1", script.B1P, "B2"])
        self.assertEqual(script.plan("B2"), [])


class ForecastTests(unittest.TestCase):

    def setUp(self):
        self.frame, self.reg = Frame(), register()
        self.s3 = forecasts(self.frame)

    def test_s3ct_is_s3_on_a_turn_day_and_s3c_elsewhere(self):
        s3c = script.m1255.s3c_forecasts(self.frame, self.reg, self.s3)
        s3ct = script.s3ct_forecasts(self.frame, self.reg, self.s3)
        turn_cells = other_cells = 0
        for d in self.frame.days:
            for h in sp.HORIZONS:
                t = self.frame.target(d, h)
                if script.s3c_turn_cap.is_turn(self.frame.day_type(t)):
                    turn_cells += 1
                    self.assertEqual(s3ct[d][h], Q)
                else:
                    other_cells += 1
                    self.assertEqual(s3ct[d][h], s3c[d][h])
        self.assertGreater(turn_cells, 0)  # the targets of the last decision days reach 31 December, `year_end`
        self.assertGreater(other_cells, 0)

    def test_the_input_is_not_changed(self):
        script.s3ct_forecasts(self.frame, self.reg, self.s3)
        self.assertEqual(self.s3[date(2025, 12, 10)][1], Q)


class TurnCheckTests(unittest.TestCase):

    def setUp(self):
        self.frame, self.reg = Frame(), register()
        self.s3 = forecasts(self.frame)
        self.s3c = script.m1255.s3c_forecasts(self.frame, self.reg, self.s3)
        self.s3ct = script.s3ct_forecasts(self.frame, self.reg, self.s3)

    def test_the_arms_pass_the_check_and_the_cells_are_counted(self):
        out = script.turn_check(self.frame, self.reg, self.s3, self.s3c, self.s3ct)
        self.assertEqual(out["cells"], 5 * len(self.frame.days))
        self.assertGreaterEqual(out["turn_day_cells"], out["turn_day_cells_at_full_allotment"])
        self.assertEqual(out["turn_day_cells_at_full_allotment"], out["turn_day_cells_where_the_cap_moves_s3c"])  # Q reaches above the line

    def test_a_changed_cell_that_is_not_a_turn_day_is_refused(self):
        moved = {d: {h: list(q) for h, q in per_h.items()} for d, per_h in self.s3ct.items()}
        moved[date(2025, 12, 8)][1] = [q - 1.0 for q in moved[date(2025, 12, 8)][1]]  # the target is 2025-12-09, not a turn day
        with self.assertRaises(ValueError):
            script.turn_check(self.frame, self.reg, self.s3, self.s3c, moved)

    def test_a_changed_cell_on_a_turn_day_is_refused(self):
        moved = {d: {h: list(q) for h, q in per_h.items()} for d, per_h in self.s3ct.items()}
        d = next(d for d in self.frame.days for h in sp.HORIZONS if script.s3c_turn_cap.is_turn(self.frame.day_type(self.frame.target(d, h))))
        h = next(h for h in sp.HORIZONS if script.s3c_turn_cap.is_turn(self.frame.day_type(self.frame.target(d, h))))
        moved[d][h] = ON_LINE
        with self.assertRaises(ValueError):
            script.turn_check(self.frame, self.reg, self.s3, self.s3c, moved)


class CellTableTests(unittest.TestCase):

    def test_the_event_is_strict_on_whole_basis_points(self):
        frame = Frame({date(2025, 12, 9): 10.0, date(2025, 12, 10): 10.4999999})  # on the threshold: not above it
        cells = script.cell_table(frame, {date(2025, 12, 8): {h: list(ON_LINE) for h in sp.HORIZONS}})
        # P(> +10 bp) is 0 for these quantiles, and the spread at 10.0 is not above 10: the Brier cell is 0 for h=1 (2025-12-09)
        self.assertEqual(cells["brier_gt10"][(date(2025, 12, 8), 1)], 0.0)
        self.assertEqual(cells["brier_gt10"][(date(2025, 12, 8), 2)], 0.0)

    def test_a_probability_of_zero_for_an_event_that_happens_scores_one(self):
        frame = Frame({date(2025, 12, 9): 22.0})
        cells = script.cell_table(frame, {date(2025, 12, 8): {h: list(ON_LINE) for h in sp.HORIZONS}})
        self.assertEqual(cells["brier_gt10"][(date(2025, 12, 8), 1)], 1.0)
        self.assertEqual(cells["brier_gt5"][(date(2025, 12, 8), 1)], (script.probability(ON_LINE, 5.0) - 1.0) ** 2)

    def test_the_four_metrics_are_there_for_every_cell(self):
        frame = Frame()
        cells = script.cell_table(frame, forecasts(frame))
        self.assertEqual(sorted(cells), sorted(script.METRIC_NAMES))
        for m in script.METRIC_NAMES:
            self.assertEqual(len(cells[m]), 5 * len(frame.days))


class BoundsAndEventsTests(unittest.TestCase):

    def setUp(self):
        self.frame, self.reg = Frame({date(2025, 12, 12): 7.0, date(2025, 12, 15): 12.0}), register()
        s3 = forecasts(self.frame)
        s3c = script.m1255.s3c_forecasts(self.frame, self.reg, s3)
        s3ct = script.s3ct_forecasts(self.frame, self.reg, s3)
        self.frame.forecasts = {m: s3 for m in script.MODELS}
        self.frame.forecasts.update({script.S3C: s3c, script.S3CT: s3ct})

    def test_s3c_gives_zero_for_more_than_ten_where_its_upper_quantiles_sit_on_the_line(self):
        b = script.bounds(self.frame, self.reg, self.frame.forecasts)
        self.assertEqual(b[script.S3C]["all"]["max_p10"], 0.0)
        self.assertEqual(b[script.S3C]["all"]["p10_zero"], b[script.S3C]["all"]["cells"])
        self.assertGreater(b[script.S3]["all"]["max_p10"], 0.0)
        self.assertEqual(b[script.S3]["all"]["cells"], b[script.S3C]["all"]["cells"])

    def test_the_event_list_has_every_day_above_five_with_its_probabilities(self):
        ev = script.events(self.frame)
        dates = [r["date"] for r in ev["days"]]
        self.assertEqual(dates, ["2025-12-12", "2025-12-15"])
        self.assertEqual([(r["above_5"], r["above_10"]) for r in ev["days"]], [(True, False), (True, True)])
        self.assertEqual((ev["positive_days_5"], ev["positive_days_10"]), (2, 1))
        row = ev["days"][1]
        self.assertEqual(row["probabilities"][script.S3C]["1"]["p10"], 0.0)
        self.assertGreater(row["probabilities"][script.S3]["1"]["p10"], 0.0)
        # the lead whose decision day (2025-12-12 - h rows, i.e. before 2025-12-08) is not scored is left out, not guessed
        self.assertIsNone(ev["days"][0]["probabilities"][script.S3]["5"])

    def test_the_target_days_and_cells_are_counted(self):
        ev = script.events(self.frame)
        self.assertEqual(ev["cells"], 5 * len(self.frame.days))
        self.assertEqual(ev["positive_cells_10"], sum(1 for d in self.frame.days for h in sp.HORIZONS if self.frame.target(d, h) == date(2025, 12, 15)))


class GroupTests(unittest.TestCase):

    def test_the_gap_decision_days_are_their_own_group(self):
        frame = Frame()
        frame.days = [d for d in frame.dates if date(2025, 12, 8) <= d <= date(2025, 12, 24)]
        groups = {(s, l): m for s, l, _g, m in script.groups_of(frame)}
        self.assertEqual(groups[("pooled", "all decision days")], frame.days)
        self.assertEqual(groups[("decision_window", "decision days 10 Dec 2025 to 23 Dec 2025")], [d for d in frame.days if d < script.GAP_FIRST])
        self.assertEqual(groups[("decision_window", "decision days 24 to 30 Dec 2025 (in neither window of #1255)")], [date(2025, 12, 24)])
        turn, other = groups[("turn_day", "turn days (cap off in (s3c-t))")], groups[("turn_day", "other days")]
        self.assertFalse(set(turn) & set(other))
        self.assertEqual(sorted(turn + other), sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS}))


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertEqual(text.count("(default)"), 1)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3c_turn_cap_1265"] = script
        sys.modules["s3c_candidate_1255_in_1265"] = script.m1255
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

    def test_the_frame_starts_at_the_removal_of_the_limit_and_ends_inside_the_limit(self):
        n = self.result["notes"]
        self.assertEqual(n["first"], "2025-12-10")
        self.assertLessEqual(n["last_target"], script.LAST_DAY.isoformat())

    def test_the_gap_decision_days_are_scored(self):
        group = self.result["groups"]["decision_window"]["decision days 24 to 30 Dec 2025 (in neither window of #1255)"]
        self.assertGreater(group["days"], 0)
        self.assertEqual(sorted(group["grid_crps"]["means"]), sorted(script.MODELS))

    def test_the_arms_are_scored_against_what_the_plan_says(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"][script.S3CT]), sorted(script.plan(script.S3CT)))
        self.assertEqual(sorted(cell["vs"][script.S3C]), sorted(script.plan(script.S3C)))
        self.assertEqual(sorted(cell["vs"][script.S3]), sorted(script.plan(script.S3)))

    def test_the_events_include_the_late_december_closes_above_the_line(self):
        days = {r["date"]: r for r in self.result["events"]["days"]}
        self.assertTrue(days["2025-12-31"]["above_10"])
        self.assertTrue(days["2025-12-31"]["turn"])

    def test_the_page_states_the_bound_plainly_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("at most about 1% by construction, and exactly 0 when", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-turn-cap-1265" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-turn-cap-1265-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_turn_cap_1265.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        self.assertEqual(record["notes"]["first"], "2025-12-10")
        self.assertLessEqual(record["notes"]["last_target"], script.LAST_DAY.isoformat())

    def test_s3_and_s3c_are_reproduced_on_the_2026_window(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for metric, rows in record["against_1255"]["metrics"].items():
            for model, v in rows.items():
                self.assertAlmostEqual(v["difference"], 0.0, places=9, msg=f"{metric} {model}")


if __name__ == "__main__":
    unittest.main()
