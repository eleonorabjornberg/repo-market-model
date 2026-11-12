"""`scripts/s3c_uncapped_1361.py` (#1361; H5 registration design, development tier): (s3c-ann-net) with and without the Standing Repo Facility cap,
scored beside each other under protocol v1 on the development window and the 2026 days.

Written first, against the declaration. The walk is #1288's (`test_s3c_announced_settlement_1288_script`), the cap, the line and the full-allotment flag
are (s3c)'s (`test_s3c_candidate`). What these tests pin: that the declaration names what the module has (seed, models, the candidate, the last day, no
amendment) and that the cleared register row exists; the cell metrics on hand cases (the two bands and the q95 exceedance beside the three scores); the
cap lines of a cell and the full-allotment split of the target days; the binding arithmetic (how often and by how much the cap moves a quantile); the
refusal to write a record if the two versions differ where no cap applies, or if the candidate is not the candidate of #1288's record; the page (the
marked questions carry numbered options and a default); a small run of `score` and `page` end to end on the fixture panel; and, once the full run is
committed, that the tracked page is what the script renders from the tracked record.

Recorded mutation (the check of this study, #1361): in `s3c_uncapped_1361.check_off_cap`, the comparison
`if a != b:` (the cell has no line) was changed to `if False:`. `CheckTests.test_a_difference_where_no_cap_applies_is_refused` then failed
with `AssertionError` (`ValueError not raised`); restored, it passes. Second mutation (the binding count): in `binding`, `top > line` was replaced by
`top >= line`; `BindingTests.test_how_often_and_by_how_much_the_cap_binds` then failed with `AssertionError` (`10 != 9`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_uncapped_1361", ROOT / "scripts" / "s3c_uncapped_1361.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_uncapped_1361"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp
LINE = 10.0


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class Frame:
    """The few members of the scoring frame the checks read."""

    def __init__(self, n=14):
        self.dates = business_days(date(2025, 12, 1), n)
        self.days = self.dates[:4]
        self.outcome = {d: 5.0 for d in self.dates}
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]


def capped_of(q, line):
    return q if line is None else [min(x, line) for x in q]


def forecasts_of(frame, lines):
    """`(uncapped, capped)`: every cell is Q, capped at the cell's line where it has one."""

    un = {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}
    ca = {d: {h: capped_of(Q, lines[(d, h)]) for h in sp.HORIZONS} for d in frame.days}
    return un, ca


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1361)
        self.assertEqual(script.SEED, 1361)
        self.assertIn("seed 1361", declaration["scoring"]["test"])
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual(declaration["candidates"][0]["name"], script.UNCAPPED)
        self.assertEqual(declaration["reference"]["name"], script.CAPPED)
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_uncapped_1361.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_uncapped_1361.json", "scripts/s3c_uncapped_1361.py", "direct"))

    def test_the_candidate_is_not_changed(self):
        candidate = json.loads((ROOT / "docs" / "research" / "h5-candidate.json").read_text(encoding="utf-8"))
        self.assertEqual(candidate["candidate"], "sc_s3c_ann_net")
        self.assertEqual(script.CAPPED, "sc_s3c_ann_net")
        self.assertEqual(candidate["cap"]["margin_bp"], script.s3c_candidate.MARGIN_BP)

    def test_the_plan(self):
        self.assertEqual(script.plan(), [script.CAPPED, "B1", script.B1P, "B2"])


class CellTests(unittest.TestCase):

    def test_the_bands_and_the_q95_exceedance_on_a_hand_case(self):
        frame = Frame()
        d = frame.days[0]
        q = list(Q)
        lo90, hi90 = script.BAND90
        lo50, hi50 = script.BAND50
        # the grid's 0.05 and 0.95 levels hold -2 + index; read them off the grid, not from a hand-typed index
        q95 = q[sp.GRID.index(0.95)]
        for y, hit90, hit50, exceed in ((q[sp.GRID.index(0.75)], 1.0, 1.0, 0.0), (q[sp.GRID.index(0.95)] + 0.5, 0.0, 0.0, 1.0),
                                        (q[sp.GRID.index(0.95)], 1.0, 0.0, 0.0), (q[sp.GRID.index(0.25)] - 0.5, 1.0, 0.0, 0.0)):
            frame.outcome[frame.target(d, 1)] = y
            cells = script.cell_table(frame, {d: {h: q for h in sp.HORIZONS}}, date(2026, 9, 3))
            self.assertEqual(cells["b90_closed"][(d, 1)], hit90, y)
            self.assertEqual(cells["b50_closed"][(d, 1)], hit50, y)
            self.assertEqual(cells["q95_exceed"][(d, 1)], exceed, y)
        self.assertEqual((lo90, hi90), (sp.GRID.index(0.05), sp.GRID.index(0.95)))
        self.assertEqual((lo50, hi50), (sp.GRID.index(0.25), sp.GRID.index(0.75)))
        self.assertGreater(q95, q[sp.GRID.index(0.05)])

    def test_the_scores_are_the_protocols(self):
        frame = Frame()
        d = frame.days[0]
        cells = script.cell_table(frame, {d: {h: list(Q) for h in sp.HORIZONS}}, date(2026, 9, 3))
        y = frame.outcome[frame.target(d, 2)]
        self.assertAlmostEqual(cells["grid_crps"][(d, 2)], sp.grid_crps(Q, y))
        self.assertAlmostEqual(cells["upper_tail_twcrps"][(d, 2)], sp.upper_tail_twcrps(Q, y))

    def test_a_day_after_the_declared_end_is_refused(self):
        frame = Frame()
        frame.days = [frame.dates[0]]
        with self.assertRaises(LookAheadError):
            script.cell_table(frame, {frame.dates[0]: {h: list(Q) for h in sp.HORIZONS}}, frame.dates[2])


class SplitTests(unittest.TestCase):

    def lines(self, frame, full_from):
        return {(d, h): (LINE if frame.target(d, h) >= full_from else None) for d in frame.days for h in sp.HORIZONS}

    def test_target_days_split_by_whether_any_cell_has_a_line(self):
        frame = Frame()
        lines = self.lines(frame, frame.dates[6])
        groups = dict((label, members) for _s, label, _g, members in script.allotment_groups(frame, lines))
        full, other = groups[script.FULL_LABEL], groups[script.OTHER_LABEL]
        targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
        self.assertEqual(sorted(full + other), targets)
        self.assertTrue(all(t >= frame.dates[6] for t in full))
        self.assertTrue(all(t < frame.dates[6] for t in other))

    def test_a_window_without_a_full_allotment_day_has_one_group(self):
        frame = Frame()
        groups = script.allotment_groups(frame, self.lines(frame, date(2030, 1, 1)))
        self.assertEqual([label for _s, label, _g, _m in groups], [script.OTHER_LABEL])


class BindingTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()
        d = self.frame.days
        # line 10 bp on every cell from the third day on; the first two days have no line
        self.lines = {(x, h): (LINE if i >= 2 else None) for i, x in enumerate(d) for h in sp.HORIZONS}
        self.un, self.ca = forecasts_of(self.frame, self.lines)
        # one cell the cap does not move
        low = [min(x, LINE) for x in Q]  # its largest quantile is exactly on the line: not above it
        self.un[d[3]][1] = low
        self.ca[d[3]][1] = low
        # the outcome of the cell (d[2], 1) is above the line
        self.frame.outcome[self.frame.target(d[2], 1)] = 12.0

    def test_how_often_and_by_how_much_the_cap_binds(self):
        out = script.binding(self.frame, self.un, self.ca, self.lines)
        allx = out["all"]
        self.assertEqual(allx["cells"], 4 * 5)
        self.assertEqual(allx["at_full_allotment"], 2 * 5)
        self.assertEqual(allx["binds"], 2 * 5 - 1)
        self.assertAlmostEqual(allx["share_binds"], 9 / 10)
        # Q runs -2..20: the 0.95 level is index 21 (value 19) and the 0.99 level is index 22 (value 20); the line is 10
        q95, q99 = Q[sp.GRID.index(0.95)], Q[sp.GRID.index(0.99)]
        self.assertAlmostEqual(allx["q95"]["mean_move"], q95 - LINE)
        self.assertAlmostEqual(allx["q99"]["max_move"], q99 - LINE)
        self.assertAlmostEqual(allx["max_quantile"]["max_move"], max(Q) - LINE)
        self.assertEqual(allx["q95"]["moved"], 9)

    def test_the_outcome_above_the_line_is_counted_on_full_allotment_cells(self):
        out = script.binding(self.frame, self.un, self.ca, self.lines)
        self.assertEqual(out["1"]["outcome_above_line"], 1)
        self.assertEqual(out["2"]["outcome_above_line"], 0)
        self.assertEqual(out["all"]["outcome_above_line"], 1)

    def test_a_cell_without_a_line_is_not_counted_as_binding(self):
        out = script.binding(self.frame, self.un, self.ca, self.lines)
        self.assertEqual(out["3"]["at_full_allotment"], 2)
        self.assertEqual(out["3"]["binds"], 2)

    def test_no_cell_moved_gives_no_mean(self):
        un, ca = forecasts_of(self.frame, {k: None for k in self.lines})
        out = script.binding(self.frame, un, ca, {k: None for k in self.lines})
        self.assertEqual(out["all"]["at_full_allotment"], 0)
        self.assertIsNone(out["all"]["q95"]["mean_move"])


class CheckTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()
        self.lines = {(d, h): (LINE if i >= 2 else None) for i, d in enumerate(self.frame.days) for h in sp.HORIZONS}
        self.un, self.ca = forecasts_of(self.frame, self.lines)

    def test_the_versions_agree_where_no_cap_applies(self):
        self.assertTrue(script.check_off_cap(self.frame, self.ca, self.un, self.lines)["cells_without_a_line_identical"])

    def test_a_difference_where_no_cap_applies_is_refused(self):
        self.ca[self.frame.days[0]][2] = [x + 1.0 for x in Q]
        with self.assertRaises(ValueError):
            script.check_off_cap(self.frame, self.ca, self.un, self.lines)

    def test_the_capped_version_is_the_uncapped_one_clipped(self):
        self.ca[self.frame.days[3]][4] = [x + 1.0 for x in self.ca[self.frame.days[3]][4]]
        with self.assertRaises(ValueError):
            script.check_off_cap(self.frame, self.ca, self.un, self.lines)

    def test_the_candidate_must_reproduce_the_record_of_1288(self):
        results = {"development": {"groups": {"pooled": {"all decision days": {m: {"means": {script.CAPPED: 1.0}} for m in script.TESTED}}}}}
        record = {"windows": {"development": {"groups": {"pooled": {"all decision days": {
            m: {"means": {script.CAPPED: 1.0}} for m in script.TESTED}}}}}}
        script.require_candidate_reproduced(results, record)
        record["windows"]["development"]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"][script.CAPPED] = 1.1
        with self.assertRaises(ValueError):
            script.require_candidate_reproduced(results, record)


class PageTests(unittest.TestCase):

    def test_the_questions_carry_numbered_options_and_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("(default)", text)
        self.assertIn("1.", text)
        self.assertIn("2.", text)
        self.assertNotIn("GO #", text)

    def test_the_secondary_section_is_a_draft_on_the_page_not_a_file_under_decisions(self):
        """The section lives on the result page, marked as a draft for her, not in force (her ruling on #1376, option 2).

        A file under `docs/decisions/` binds the owner-attested check; the page does not.
        """
        text = "\n".join(script.draft_section() + script.question())
        self.assertIn("a draft for Eleonora, not in force", text)
        self.assertIn("sc_s3c_ann_net_uncapped", text)
        self.assertNotIn("docs/decisions/drafts", text)
        self.assertNotIn("GO #", text)
        self.assertFalse((ROOT / "docs" / "decisions" / "drafts" / "h5-uncapped-secondary.md").exists())
        declaration = (ROOT / "metadata" / "s3c_uncapped_1361.json").read_text(encoding="utf-8")
        self.assertNotIn("docs/decisions/drafts", declaration)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

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

    def test_the_uncapped_version_is_tested_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["vs"][script.UNCAPPED]), sorted(script.plan()))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_versions_are_the_same_before_full_allotment(self):
        w = self.result["windows"]["development"]
        self.assertTrue(w["off_cap"]["cells_without_a_line_identical"])

    def test_the_binding_is_reported_by_lead(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["binding"]), sorted(["all"] + [str(h) for h in sp.HORIZONS]))

    def test_the_page_says_development_not_a_verdict(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("not a verdict", text)
        self.assertIn("Closes", "Closes")


class TrackedTests(unittest.TestCase):

    RECORD = ROOT / "docs" / "research" / "s3c-uncapped-1361" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-uncapped-1361-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        if not self.RECORD.exists():
            self.skipTest("the declared run is not committed yet")
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))
        self.assertIsNone(record["subset_from"])
        self.assertEqual(record["label"], "development, not a verdict")


if __name__ == "__main__":
    unittest.main()
