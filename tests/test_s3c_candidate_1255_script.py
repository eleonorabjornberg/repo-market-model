"""`scripts/s3c_candidate_1255.py` (#1255; H5 step 3, development tier): the candidate (s3c) scored against (s3), (a), B1, B1' and B2 on the
development window and on the 2026 development days.

Written first, against the declaration. The candidate is `repo_model.s3c_candidate` and is tested in `test_s3c_candidate`; the line and the
clip are #1241's (`test_srf_line`); the frames, the paired tests and the walk are #1241's and #1229's, loaded as they are. What these tests
pin: that the declaration names what the module has (seed, margin, models, the windows, no amendment); the check the directive asks for, that
every cell with a target before full allotment is (s3)'s and so is the score of a decision day all of whose targets are before it, on hand
cases on a small frame, with the failure when one cell is moved; the candidate's forecasts and the binding counts on hand cases; the page
(the opening question, the marked questions with numbered options and defaults); a small run of `score` and `page` end to end on the
fixture panel; and, once the full run is committed, that the tracked page is what the script renders from the tracked record.

Recorded mutation (the check of the directive, #1255): in `s3c_candidate_1255.before_full_allotment`, the comparison
`if list(s3[d][h]) != list(s3c[d][h]):` was commented out. `BeforeFullAllotmentTests.test_a_changed_cell_before_full_allotment_is_refused`
then failed with `AssertionError` (`ValueError` not raised for a cell moved on 2025-12-04); restored, it passes.
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

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_candidate_1255", ROOT / "scripts" / "s3c_candidate_1255.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_candidate_1255"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp


class Frame:
    """The few members of the scoring frame the checks read: business days in December 2025, a decision on each of the first few."""

    def __init__(self):
        day, self.dates = date(2025, 12, 1), []
        while len(self.dates) < 22:
            if day.weekday() < 5:
                self.dates.append(day)
            day += timedelta(days=1)
        self.days = [d for d in self.dates if d <= date(2025, 12, 19)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]


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


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1255)
        self.assertEqual(script.SEED, 1255)
        self.assertIn("seed 1255", declaration["scoring"]["test"])
        self.assertEqual(declaration["candidate"]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertEqual(declaration["candidate"]["name"], script.S3C)
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([w["name"] for w in declaration["windows"]], list(script.WINDOWS))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["limits"]["arms"], 0)
        self.assertEqual(declaration["amendments"], [])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_candidate_1255.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_candidate_1255.json", "scripts/s3c_candidate_1255.py", "direct"))

    def test_the_machinery_is_the_predecessors_unchanged(self):
        self.assertEqual(script.k.S3, "sc_s3_robust")
        self.assertEqual(script.k.SEED, 1255)  # the shared paired-test and interval tasks read the seed of their own module
        self.assertEqual(script.pair_plan(script.S3C), [script.S3, script.A, "B1", script.B1P, "B2"])
        self.assertEqual(script.pair_plan(script.S3), [])
        self.assertEqual(script.block_plan(script.S3C), [script.S3])

    def test_the_first_target_at_full_allotment_is_the_registers(self):
        reg = pe.load_register()
        self.assertFalse(script.s3c_candidate.full_allotment(reg, datetime(2025, 12, 10, 16), script.FULL_ALLOTMENT_FIRST - timedelta(days=1)))
        self.assertTrue(script.s3c_candidate.full_allotment(reg, datetime(2025, 12, 10, 16), script.FULL_ALLOTMENT_FIRST))


class CandidateForecastTests(unittest.TestCase):

    def setUp(self):
        self.frame, self.reg = Frame(), register()
        self.s3 = {d: {h: list(Q) for h in sp.HORIZONS} for d in self.frame.days}
        self.s3c = script.s3c_forecasts(self.frame, self.reg, self.s3)

    def test_a_cell_before_full_allotment_is_s3s_and_a_cell_at_it_is_clipped_at_the_line(self):
        d = date(2025, 12, 10)  # the day the removal of the limit is announced, at 14:00: known to the decision at 16:00
        self.assertEqual(self.frame.target(d, 1), date(2025, 12, 11))
        for h in sp.HORIZONS:
            self.assertEqual(self.s3c[d][h], [min(q, 10.0) for q in Q])  # 3.75 - 3.65 = 10 bp
        d = date(2025, 12, 3)
        self.assertEqual(self.frame.target(d, 5), date(2025, 12, 10))
        for h in sp.HORIZONS:
            self.assertEqual(self.s3c[d][h], Q)

    def test_a_target_at_full_allotment_whose_decision_is_before_the_announcement_is_not_capped(self):
        d = date(2025, 12, 4)  # the fifth target is 2025-12-11, but the removal is announced on 2025-12-10: the decision cannot know it
        self.assertEqual(self.frame.target(d, 5), date(2025, 12, 11))
        self.assertEqual(self.s3c[d][5], Q)

    def test_the_input_is_not_changed(self):
        self.assertEqual(self.s3[date(2025, 12, 10)][1], Q)

    def test_the_binding_counts(self):
        bind = script.binding(self.frame, self.reg, self.s3, self.s3c)
        n = len(self.frame.days)
        self.assertEqual(bind["all"]["cells"], 5 * n)
        at = sum(1 for d in self.frame.days for h in sp.HORIZONS if d >= date(2025, 12, 10))
        self.assertEqual(bind["all"]["at_full_allotment"], at)
        self.assertEqual(bind["all"]["moved"], at)  # Q reaches 20 bp, above the 10 bp line, in every cell
        self.assertEqual(bind["all"]["moves_q95"], at)
        self.assertEqual(sum(bind[str(h)]["moved"] for h in sp.HORIZONS), bind["all"]["moved"])


class BeforeFullAllotmentTests(unittest.TestCase):

    def setUp(self):
        self.frame, self.reg = Frame(), register()
        self.s3 = {d: {h: list(Q) for h in sp.HORIZONS} for d in self.frame.days}
        self.s3c = script.s3c_forecasts(self.frame, self.reg, self.s3)

    def test_the_cells_and_the_days_before_full_allotment_are_counted_and_identical(self):
        check = script.before_full_allotment(self.frame, self.s3, self.s3c)
        self.assertEqual(check["cells_before"], check["cells_before_identical"])
        self.assertGreater(check["cells_before"], 0)
        self.assertEqual(check["decision_days_before"], check["decision_days_before_identical"])
        self.assertGreater(check["decision_days_before"], 0)
        self.assertEqual(check["first_full_allotment_target"], "2025-12-11")

    def test_a_changed_cell_before_full_allotment_is_refused(self):
        moved = {d: {h: list(q) for h, q in per_h.items()} for d, per_h in self.s3c.items()}
        moved[date(2025, 12, 4)][1] = [q - 1.0 for q in Q]  # the target is 2025-12-05
        with self.assertRaises(ValueError):
            script.before_full_allotment(self.frame, self.s3, moved)

    def test_a_cell_at_full_allotment_may_differ(self):
        script.before_full_allotment(self.frame, self.s3, self.s3c)  # does not raise although cells at the line are clipped
        self.assertNotEqual(self.s3[date(2025, 12, 10)][1], self.s3c[date(2025, 12, 10)][1])


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question({}))
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertIn("**Question 2.", text)
        self.assertEqual(text.count("(default)"), 2)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3c_candidate_1255"] = script
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

    def test_both_windows_are_scored_inside_their_limits(self):
        dev, y26 = self.result["windows"]["development"]["notes"], self.result["windows"]["2026"]["notes"]
        self.assertLessEqual(dev["last_target"], "2025-12-31")
        self.assertGreaterEqual(y26["first_target"], "2026-01-02")
        self.assertLessEqual(y26["last_target"], script.LAST_DAY.isoformat())

    def test_the_candidate_is_scored_against_the_four_references_and_s3(self):
        for window in script.WINDOWS:
            cell = self.result["windows"][window]["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
            self.assertEqual(sorted(cell["vs"][script.S3C]), sorted(script.REFERENCES))

    def test_days_before_full_allotment_are_identical_in_the_development_window(self):
        check = self.result["windows"]["development"]["before_full_allotment"]
        self.assertEqual(check["cells_before"], check["cells_before_identical"])
        self.assertEqual(check["decision_days_before"], check["decision_days_before_identical"])
        self.assertGreater(check["cells_before"], 0)

    def test_every_2026_cell_is_at_full_allotment(self):
        bind = self.result["windows"]["2026"]["binding"]["all"]
        self.assertEqual(bind["cells"], bind["at_full_allotment"])

    def test_the_page_opens_with_the_question_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertTrue(text.split("\n", 2)[2].lstrip().startswith("**Does the cap, carried from full allotment onwards"))
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-candidate-1255" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-candidate-1255-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_candidate_1255.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["margin_bp"], 0.0)
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        self.assertLessEqual(record["windows"]["2026"]["notes"]["last_target"], script.LAST_DAY.isoformat())

    def test_the_two_scores_move_by_the_same_amount_where_the_cap_acts_only_above_zero(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for window in script.WINDOWS:
            pooled = record["windows"][window]["groups"]["pooled"]["all decision days"]
            a, b = pooled["grid_crps"]["means"], pooled["upper_tail_twcrps"]["means"]
            self.assertAlmostEqual(a[script.S3] - a[script.S3C], b[script.S3] - b[script.S3C], places=9)

    def test_the_predecessors_s3_is_reproduced(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for window, there in record["against_records"].items():
            for metric, v in there["metrics"].items():
                self.assertAlmostEqual(v["difference"], 0.0, places=9, msg=f"{window} {metric}")


if __name__ == "__main__":
    unittest.main()
