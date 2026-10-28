"""`scripts/s3c_pd_1296.py` (#1296; H5 step 3, development tier): (s3c-pd), (s3c) with primary dealers' reverse repo plus securities borrowed as a
balance-sheet state input, scored against (s3c), (s3), B1, B1' and B2 on the development window and the 2026 development days.

Written against the declaration. The arm is `repo_model.s3c_pd` (tested in `test_s3c_pd`); the cap, the line and the full-allotment flag are
(s3c)'s (`test_s3c_candidate`). What these tests pin: that the declaration names what the module has (seed, models, the last day, the trailing
window, the release lag, no amendment); the plan (the arm against (s3c), (s3), then the benchmarks; no other model is a candidate); that the arm's
forecasts are the state walk's, capped as (s3c) is capped, and that the run stops when (s3) re-forecast in the state walk differs from the frame's
on one cell; the cell table's two added measures (the Brier cell is strict on whole basis points, the 90% band is closed); the state-defined groups
(the decision days with a state against those without); the use table and the fitted-effect arithmetic (bp per standard unit is the coefficient in
force times the anchor's scale) on hand cases; the page (the source, its release and vintage, the marked questions with numbered options and
defaults, no outside figure); a small run of `score` and `page` end to end on the fixture panel; and, once the full run is committed, that the
tracked page is what the script renders from the tracked record and that #1255's windows are reproduced.

Recorded mutation (the check of this study): in `s3c_pd_1296.s3pd_forecasts`, the comparison `if walk.s3[d] != s3[d]:` was commented out.
`ForecastTests.test_the_run_stops_when_s3_of_the_walk_differs_from_the_frames` then failed with `AssertionError` (`ValueError` not raised for a cell
moved on one decision day); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import s3c_pd as cc
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_pd_1296", ROOT / "scripts" / "s3c_pd_1296.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_pd_1296"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp


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
        self.forecasts = {script.S3: {d: {h: list(Q) for h in sp.HORIZONS} for d in self.days}}

    def target(self, d, h):
        return self.dates[self.position[d] + h]


def walk_of(frame, shift=0.0, values=None, scale=2.0):
    """A `PdWalk` whose (s3) is the frame's and whose arm is shifted by `shift` bp on every cell; `values` maps a decision day to its state."""

    s3 = frame.forecasts[script.S3]
    arm = {d: {h: [q + shift for q in s3[d][h]] for h in sp.HORIZONS} for d in frame.days}
    vals = {d: (values or {}).get(d) for d in frame.days}
    return cc.PdWalk(arm, {d: {h: list(s3[d][h]) for h in sp.HORIZONS} for d in frame.days}, vals, {d: scale for d in frame.days}, {}, {}, ())


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1296)
        self.assertEqual(script.SEED, 1296)
        self.assertIn("seed 1296", declaration["scoring"]["test"])
        self.assertEqual(declaration["candidate"]["name"], script.S3PD)
        self.assertEqual(declaration["candidate"]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], list(script.ARMS))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertIn("the 52 as-of weeks", declaration["candidate"]["transform"])
        self.assertIn("fewer than 13 of those 52", declaration["candidate"]["transform"])
        self.assertIn("at least 60 training pairs", declaration["candidate"]["entry"])
        self.assertEqual((cc.TRAILING_WEEKS, cc.MIN_TRAILING, cc.MIN_STATE_PAIRS), (52, 13, 60))

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_pd_1296.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_pd_1296.json", "scripts/s3c_pd_1296.py", "direct"))

    def test_the_plan_is_s3c_then_s3_then_the_benchmarks(self):
        self.assertEqual(script.plan(script.S3PD), [script.S3C, script.S3, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.S3C), [])
        self.assertEqual(script.plan(script.S3), [])


class ForecastTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()

    def test_the_arms_forecasts_are_the_walks_with_no_cap_where_the_facility_is_not_at_full_allotment(self):
        walk = walk_of(self.frame, shift=0.5)
        out = script.s3pd_forecasts(self.frame, [], walk)
        self.assertEqual(sorted(out), self.frame.days)
        self.assertEqual(out[self.frame.days[0]][1], [q + 0.5 for q in Q])

    def test_the_cap_of_s3c_clips_the_arms_quantiles_at_full_allotment(self):
        import datetime as dt

        from repo_model import policy_events as pe

        entry = pe.PolicyEntry("srf-full", "standing_repo", "change", "srf-full", dt.datetime(2025, 12, 1, 14, 0), "stated", date(2025, 12, 2),
                               "https://example.org", True, {"rate_percent": 3.75, "aggregate_operation_limit_bn": None})
        iorb = pe.PolicyEntry("iorb-0", "iorb_rate", "change", "iorb-0", dt.datetime(2021, 6, 16, 14, 0), "stated", date(2021, 6, 17),
                              "https://example.org", True, {"rate_percent": 3.65})
        register = pe.known_entries([iorb, entry], dt.datetime(2030, 1, 1))
        walk = walk_of(self.frame, shift=0.0)
        out = script.s3pd_forecasts(self.frame, register, walk)
        expected = script.m1255.s3c_forecasts(self.frame, register, walk.forecasts)
        self.assertEqual({d: out[d] for d in self.frame.days}, {d: expected[d] for d in self.frame.days})
        self.assertLess(max(out[self.frame.days[0]][1]), max(Q))

    def test_the_run_stops_when_s3_of_the_walk_differs_from_the_frames(self):
        walk = walk_of(self.frame)
        d = self.frame.days[3]
        walk.s3[d][2][5] += 1e-9
        with self.assertRaises(ValueError):
            script.s3pd_forecasts(self.frame, [], walk)

    def test_a_frame_day_missing_from_the_walk_stops_the_run(self):
        walk = walk_of(self.frame)
        del walk.forecasts[self.frame.days[0]]
        with self.assertRaises(ValueError):
            script.s3pd_forecasts(self.frame, [], walk)


class CellTests(unittest.TestCase):

    def test_the_coverage_band_is_closed_and_the_brier_cell_is_strict_on_whole_basis_points(self):
        frame = Frame({date(2025, 12, 9): Q[script.HI] + 1.0})  # the target of the decision on 8 December at lead 1: just above q95
        forecasts = {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}
        table = script.cell_table(frame, forecasts)
        self.assertEqual(sorted(table), sorted(script.METRIC_NAMES))
        self.assertEqual(table["coverage_90"][(date(2025, 12, 8), 1)], 0.0)
        self.assertEqual(table["coverage_90"][(date(2025, 12, 9), 1)], 1.0)
        edge = Frame({date(2025, 12, 9): Q[script.HI]})
        self.assertEqual(script.cell_table(edge, {d: {h: list(Q) for h in sp.HORIZONS} for d in edge.days})["coverage_90"][(date(2025, 12, 8), 1)], 1.0)
        self.assertGreater(table["brier_gt5"][(date(2025, 12, 8), 1)], 0.0)


class GroupTests(unittest.TestCase):

    def test_the_state_groups_split_the_decision_days_by_whether_they_have_a_state(self):
        frame = Frame()
        d1, d2 = frame.days[2], frame.days[7]
        walk = walk_of(frame, values={d1: 0.7, d2: -1.2})
        groups = {label: members for _split, label, _grain, members in script.changed_term_groups(frame, walk)}
        self.assertEqual(groups[script.NONZERO], [d1, d2])
        self.assertEqual(sorted(groups[script.OTHER] + groups[script.NONZERO]), frame.days)
        self.assertFalse(set(groups[script.OTHER]) & set(groups[script.NONZERO]))
        self.assertTrue(all(g[2] == "decision" for g in script.changed_term_groups(frame, walk)))

    def test_a_state_of_zero_is_a_state(self):
        frame = Frame()
        walk = walk_of(frame, values={frame.days[0]: 0.0})
        groups = {label: members for _s, label, _g, members in script.changed_term_groups(frame, walk)}
        self.assertEqual(groups[script.NONZERO], [frame.days[0]])

    def test_the_use_table_counts_cells_with_a_state_and_where_the_arm_differs(self):
        frame = Frame()
        d = frame.days[1]
        refit = date(2025, 12, 1)
        est = cc.PdEstimate(None, 0.0, False, 0)
        base = walk_of(frame, values={d: 0.7})
        walk = cc.PdWalk(base.forecasts, base.s3, base.values, base.scales, {refit: {h: est for h in sp.HORIZONS}}, {x: refit for x in frame.days}, ())
        s3c = {x: {h: list(Q) for h in sp.HORIZONS} for x in frame.days}
        arm = {x: {h: list(Q) for h in sp.HORIZONS} for x in frame.days}
        arm[d][1][3] += 0.1
        use = script.term_use(frame, walk, s3c, arm)
        self.assertEqual((use["1"]["state_defined"], use["1"]["differs_from_s3c"], use["1"]["cells"]), (1, 1, len(frame.days)))
        self.assertEqual(use["2"]["state_defined"], 1)
        self.assertEqual(use["2"]["differs_from_s3c"], 0)
        self.assertEqual((use["decision_days"], use["days_with_state"]), (len(frame.days), 1))
        self.assertEqual(use["refits_in_use"], 1)
        self.assertEqual(use["refits_active"], {str(h): 0 for h in sp.HORIZONS})

    def test_the_use_table_reports_the_age_of_the_level_read(self):
        frame = Frame()
        weeks = [date(2025, 1, 1) + timedelta(days=7 * i) for i in range(60)]
        levels = {w: 100.0 + (i % 5) * 4.0 for i, w in enumerate(weeks)}
        for w in weeks[-3:]:
            levels[w] = None
        est = cc.PdEstimate(None, 0.0, False, 0)
        refit = date(2025, 12, 1)
        base = walk_of(frame, values={frame.days[0]: 0.3, frame.days[1]: -0.2})
        walk = cc.PdWalk(base.forecasts, base.s3, base.values, base.scales, {refit: {h: est for h in sp.HORIZONS}}, {x: refit for x in frame.days}, ())
        s3c = {x: {h: list(Q) for h in sp.HORIZONS} for x in frame.days}
        use = script.term_use(frame, walk, s3c, s3c, levels)
        expected = [cc.skipped_weeks(levels, d) for d in frame.days[:2]]
        self.assertEqual(use["skipped_weeks"]["decision_days"], 2)
        self.assertAlmostEqual(use["skipped_weeks"]["mean"], sum(expected) / 2)
        self.assertEqual(use["skipped_weeks"]["max"], max(expected))

    def test_the_fitted_effect_in_bp_per_unit_is_the_coefficient_in_force_times_the_anchors_scale(self):
        frame = Frame()
        frame.regime = lambda day: "2025-26"
        d = frame.days[1]
        est = cc.PdEstimate(None, 0.4, True, 70)
        refit = date(2025, 12, 1)
        base = walk_of(frame, values={d: 1.5}, scale=2.0)
        walk = cc.PdWalk(base.forecasts, base.s3, base.values, base.scales, {refit: {h: est for h in sp.HORIZONS}}, {x: refit for x in frame.days}, ())
        fe = script.fitted_effect(frame, walk, {})
        self.assertAlmostEqual(fe["effect_bp_per_unit_by_lead"]["1"]["all"]["mean_bp_per_unit"], 0.8)
        self.assertEqual(fe["effect_bp_per_unit_by_lead"]["1"]["2025-26"]["decision_days"], len(frame.days))
        self.assertEqual(fe["coefficient_by_lead"]["3"], {"refits": 1, "active": 1, "median": 0.4, "min": 0.4, "max": 0.4})
        self.assertAlmostEqual(fe["mean_abs_shift_bp_lead1_on_state_days"], 0.8 * 1.5)
        self.assertIsNone(fe["standard_unit_usd_bn"]["mean"])

    def test_the_size_of_a_standard_unit_is_the_trailing_year_standard_deviation(self):
        import statistics as st

        frame = Frame()
        frame.regime = lambda day: "x"
        weeks = [date(2025, 1, 1) + timedelta(days=7 * i) for i in range(60)]
        levels = {w: 100.0 + (i % 5) * 4.0 for i, w in enumerate(weeks)}
        est = cc.PdEstimate(None, 0.0, False, 0)
        base = walk_of(frame, values={})
        walk = cc.PdWalk(base.forecasts, base.s3, base.values, base.scales, {date(2025, 12, 1): {h: est for h in sp.HORIZONS}},
                         {x: date(2025, 12, 1) for x in frame.days}, ())
        expected = []
        for d in frame.days:
            week = cc.latest_defined_week(levels, d)
            expected.append(st.stdev([levels[w] for w in levels if 0 < (week - w).days <= 7 * cc.TRAILING_WEEKS and levels[w] is not None]))
        out = script.fitted_effect(frame, walk, levels)["standard_unit_usd_bn"]
        self.assertEqual(out["decision_days"], len(frame.days))
        self.assertAlmostEqual(out["min"], min(expected), places=9)
        self.assertAlmostEqual(out["max"], max(expected), places=9)
        self.assertAlmostEqual(out["mean"], st.fmean(expected), places=9)


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertIn("Register the source", text)
        self.assertEqual(text.count("(default)"), 1)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3c_pd_1296"] = script
        sys.modules["s3c_turn_cap_1265_in_1296"] = script.m1265
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

    def test_both_windows_are_scored_inside_the_limit(self):
        self.assertEqual(sorted(self.result["windows"]), ["2026", "development"])
        for w in self.result["windows"].values():
            self.assertLessEqual(w["notes"]["last_target"], script.LAST_DAY.isoformat())

    def test_the_arm_is_tested_against_what_the_plan_says(self):
        cell = self.result["windows"]["2026"]["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"][script.S3PD]), sorted(script.plan(script.S3PD)))
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_state_acts_at_every_lead_and_the_arm_is_s3cs_on_days_without_one(self):
        for w in self.result["windows"].values():
            use = w["term_use"]
            self.assertGreater(use["days_with_state"], 0)
            for h in ("1", "2", "3", "4", "5"):
                self.assertEqual(use[h]["state_defined"], use["days_with_state"])
                self.assertLessEqual(use[h]["differs_from_s3c"], use[h]["cells"])

    def test_the_state_groups_are_there(self):
        groups = self.result["windows"]["development"]["groups"][script.CHANGED]
        self.assertIn(script.NONZERO, groups)

    def test_the_record_carries_the_snapshot_and_the_release_evidence(self):
        self.assertEqual(sorted(self.result["snapshot"]), sorted(list(cc.SERIES) + ["release-page"]))
        self.assertIn("Thursdays at approximately 4:15 p.m.", self.result["release_evidence"])
        self.assertEqual(self.result["levels"]["release_lag_business_days"], cc.RELEASE_LAG_BUSINESS_DAYS)
        self.assertEqual(sorted(self.result["levels"]["withheld_by_series"]), sorted(cc.SERIES))

    def test_the_page_states_the_source_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## The source and what it can say", text)
        self.assertIn("latest revised vintage", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)
        self.assertIn("### 90% band coverage beside (s3c)'s", text)
        self.assertIn("The fitted effect of the state term in bp per standard unit", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-pd-1296" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-pd-1296-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_pd_1296.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for w in record["windows"].values():
            self.assertLessEqual(w["notes"]["last_target"], script.LAST_DAY.isoformat())

    def test_s3_and_s3c_are_reproduced_on_both_windows_of_1255(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for window, rec in record["against_records"].items():
            for metric, rows in rec["metrics"].items():
                for model, v in rows.items():
                    self.assertAlmostEqual(v["difference"], 0.0, places=9, msg=f"{window} {metric} {model}")

    def test_the_page_cites_no_outside_figure(self):
        text = self.PAGE.read_text(encoding="utf-8")
        for word in ("http://", "https://", "et al", "arXiv"):
            self.assertNotIn(word, text)


if __name__ == "__main__":
    unittest.main()
