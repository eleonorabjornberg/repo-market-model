"""`scripts/s3c_mbs_1276.py` (#1276; H5 step 3, development tier): (s3c-mbs), (s3c) with the settlement days of the agency MBS classes A to D,
scored against (s3c), (s3), B1, B1' and B2 on the development window and the 2026 development days.

Written against the declarations. The arm is `repo_model.s3c_mbs` and the source `repo_model.sifma_mbs` (tested in `test_s3c_mbs` and `test_sifma_mbs`);
the cap, the line and the full-allotment flag are (s3c)'s (`test_s3c_candidate`). What these tests pin: that the declaration names what the module has (seed,
models, the last day, the pooling window and rule, no amendment); the plan (the arm against (s3c), (s3), then the benchmarks; no other model is a candidate);
that the arm's forecasts are the MBS walk's, capped as (s3c) is capped, and that the run stops when (s3) re-forecast in the walk differs from the frame's on one
cell; the cell table's added measure (the 90% band is closed); the settlement-day groups (the target days on which an indicator is non-zero against the others,
and each indicator's days); the use table and the fitted-effect arithmetic on hand cases; the page (the statement of where the indicators can be non-zero, the
marked questions with numbered options and defaults, no source cited for the idea beyond her ruling, no outside figure); a small run of `score` and `page` end
to end on the fixture panel; and, once the full run is committed, that the tracked page is what the script renders from the tracked record and that #1255's
windows are reproduced.

Recorded mutation (the check of this study): in `s3c_mbs_1276.s3cm_forecasts`, the comparison `if walk.s3[d] != s3[d]:` was changed to `if False:`.
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

from repo_model import s3c_mbs as mm
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_mbs_1276", ROOT / "scripts" / "s3c_mbs_1276.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_mbs_1276"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp
TERMS = ("mbs_a", "mbs_b", "mbs_c", "mbs_d")
ZERO = {t: 0 for t in TERMS}


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


def estimate(coefficient=None, active=()):
    return mm.MbsEstimate(None, {**{t: 0.0 for t in TERMS}, **(coefficient or {})}, tuple(active), {})


def walk_of(frame, shift=0.0, values=None, estimates=None):
    """An `MbsWalk` whose (s3) is the frame's and whose arm is shifted by `shift` bp on every cell; `values[(d, h)]` is a dict of indicators at 1."""

    s3 = frame.forecasts[script.S3]
    arm = {d: {h: [q + shift for q in s3[d][h]] for h in sp.HORIZONS} for d in frame.days}
    vals = {d: {h: {**ZERO, **(values or {}).get((d, h), {})} for h in sp.HORIZONS} for d in frame.days}
    return mm.MbsWalk(arm, {d: {h: list(s3[d][h]) for h in sp.HORIZONS} for d in frame.days}, vals, {d: 2.0 for d in frame.days}, estimates or {}, {}, ())


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1276)
        self.assertEqual(script.SEED, 1276)
        self.assertIn("seed 1276", declaration["scoring"]["test"])
        self.assertEqual(declaration["candidate"]["name"], script.S3CM)
        self.assertEqual(declaration["candidate"]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], list(script.ARMS))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual(script.POOLING_WINDOW_LAST, date(2025, 12, 31))
        self.assertIn("2025-12-31", declaration["candidate"]["window_for_pooling"])
        self.assertIn("fewer than 20", declaration["candidate"]["definition"])
        self.assertEqual(mm.MIN_CLASS_DAYS, 20)

    def test_the_availability_declaration_is_committed_and_dates_every_year_and_names_the_four_the_workbook_capture_dates(self):
        availability = script.committed_availability()
        self.assertEqual(availability["issue"], 1276)
        dated = {y: e["capture_timestamp"] for y, e in availability["public_from"].items()}
        self.assertEqual(sorted(dated), [str(y) for y in range(2018, 2028)])
        # the four years only the 2025-07-21 workbook capture dates (after all their dates); the others a page capture
        self.assertEqual(sorted(y for y, t in dated.items() if t == "20250721210954"), ["2018", "2019", "2022", "2023"])
        self.assertEqual(sorted(y for y, t in dated.items() if t is None), [])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_mbs_1276.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]), ("metadata/s3c_mbs_1276.json", "scripts/s3c_mbs_1276.py", "direct"))

    def test_the_plan_is_s3c_then_s3_then_the_benchmarks(self):
        self.assertEqual(script.plan(script.S3CM), [script.S3C, script.S3, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.S3C), [])
        self.assertEqual(script.plan(script.S3), [])


class ForecastTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()

    def test_the_arms_forecasts_are_the_walks_with_no_cap_where_the_facility_is_not_at_full_allotment(self):
        walk = walk_of(self.frame, shift=0.5)
        out = script.s3cm_forecasts(self.frame, [], walk)
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
        out = script.s3cm_forecasts(self.frame, register, walk)
        expected = script.m1255.s3c_forecasts(self.frame, register, walk.forecasts)
        self.assertEqual({d: out[d] for d in self.frame.days}, {d: expected[d] for d in self.frame.days})
        self.assertLess(max(out[self.frame.days[0]][1]), max(Q))

    def test_the_run_stops_when_s3_of_the_walk_differs_from_the_frames(self):
        walk = walk_of(self.frame)
        d = self.frame.days[3]
        walk.s3[d][2][5] += 1e-9
        with self.assertRaises(ValueError):
            script.s3cm_forecasts(self.frame, [], walk)

    def test_a_frame_day_missing_from_the_walk_stops_the_run(self):
        walk = walk_of(self.frame)
        del walk.forecasts[self.frame.days[0]]
        with self.assertRaises(ValueError):
            script.s3cm_forecasts(self.frame, [], walk)


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

    def test_the_settlement_groups_split_the_target_days_by_whether_an_indicator_is_non_zero(self):
        frame = Frame()
        d1, d2 = frame.days[2], frame.days[7]
        walk = walk_of(frame, values={(d1, 1): {"mbs_a": 1}, (d2, 3): {"mbs_c": 1}, (frame.days[4], 2): {"mbs_a": 1}})
        groups = {label: (grain, members) for _split, label, grain, members in script.settlement_groups(frame, walk)}
        t1, t2, t3 = frame.target(d1, 1), frame.target(d2, 3), frame.target(frame.days[4], 2)
        self.assertEqual(groups[script.ANY_DAYS][1], sorted({t1, t2, t3}))
        self.assertEqual(groups["mbs_a: settlement days"][1], sorted({t1, t3}))
        self.assertEqual(groups["mbs_c: settlement days"][1], [t2])
        self.assertNotIn("mbs_b: settlement days", groups)
        every = {frame.target(d, h) for d in frame.days for h in sp.HORIZONS}
        self.assertEqual(sorted(groups[script.ANY_DAYS][1] + groups[script.OTHER_DAYS][1]), sorted(every))
        self.assertFalse(set(groups[script.ANY_DAYS][1]) & set(groups[script.OTHER_DAYS][1]))
        self.assertTrue(all(g[0] == "target" for g in groups.values()))

    def test_the_use_table_counts_cells_where_an_indicator_is_non_zero_and_where_the_arm_differs(self):
        frame = Frame()
        d = frame.days[1]
        refit = date(2025, 12, 1)
        est = estimate({"mbs_a": 0.3}, active=("mbs_a",))
        base = walk_of(frame, values={(d, 1): {"mbs_a": 1}})
        walk = mm.MbsWalk(base.forecasts, base.s3, base.values, base.scale, {refit: {h: est for h in sp.HORIZONS}}, {x: refit for x in frame.days}, ())
        s3c = {x: {h: list(Q) for h in sp.HORIZONS} for x in frame.days}
        arm = {x: {h: list(Q) for h in sp.HORIZONS} for x in frame.days}
        arm[d][1][3] += 0.1
        use = script.term_use(frame, walk, s3c, arm)
        self.assertEqual((use["1"]["term_nonzero"], use["1"]["differs_from_s3c"], use["1"]["cells"]), (1, 1, len(frame.days)))
        self.assertEqual(use["2"]["term_nonzero"], 0)
        self.assertEqual(use["refits_in_use"], 1)
        self.assertEqual(use["refits_active"]["1"], {"mbs_a": 1, "mbs_b": 0, "mbs_c": 0, "mbs_d": 0})

    def test_the_fitted_effect_is_the_coefficient_in_force_times_the_scale_at_the_anchor(self):
        frame = Frame()
        frame.regime = lambda day: "2025-26"
        d = frame.days[1]
        est = estimate({"mbs_a": 0.4, "mbs_c": -0.1}, active=("mbs_a", "mbs_c"))
        refit = date(2025, 12, 1)
        base = walk_of(frame, values={(d, 1): {"mbs_a": 1}, (d, 2): {"mbs_c": 1}})
        walk = mm.MbsWalk(base.forecasts, base.s3, base.values, base.scale, {refit: {h: est for h in sp.HORIZONS}}, {x: refit for x in frame.days}, ())
        fe = script.fitted_effect(frame, walk)
        self.assertAlmostEqual(fe["effect_bp_by_regime"]["mbs_a"]["all"]["mean_bp"], 0.8)  # 0.4 x scale 2.0
        self.assertAlmostEqual(fe["effect_bp_by_regime"]["mbs_c"]["all"]["mean_bp"], -0.2)
        self.assertEqual(fe["effect_bp_by_regime"]["mbs_a"]["2025-26"]["cells"], 1)
        self.assertNotIn("mbs_b", fe["effect_bp_by_regime"])
        self.assertEqual(fe["coefficient_by_refit_regime"]["mbs_a"]["all"], {"refits": 1, "active": 1, "median": 0.4, "min": 0.4, "max": 0.4})

    def test_the_source_summary_counts_the_dates_of_each_year_and_the_pooling_outcome(self):
        import datetime as dt

        from repo_model import sifma_mbs

        table = sifma_mbs.load_table()
        public = {2020: dt.datetime(2019, 8, 20, 19, 32, 52, tzinfo=sifma_mbs.UTC)}
        summary = script.source_summary(table, public, {"A": 30, "B": 31, "C": 29, "D": 28}, False)
        self.assertEqual(summary["years"]["2020"]["dates_by_class"], {"A": 12, "B": 12, "C": 12, "D": 12})
        self.assertIsNone(summary["years"]["2019"]["public_from_utc"])
        self.assertEqual(summary["years"]["2020"]["dates_after_capture_by_class"], {"A": 12, "B": 12, "C": 12, "D": 12})
        self.assertEqual(summary["years"]["2019"]["dates_after_capture_by_class"], {"A": 0, "B": 0, "C": 0, "D": 0})
        # a capture in the middle of January 2025 leaves the dates of that month before it unreadable
        mid = script.source_summary(table, {2025: dt.datetime(2025, 1, 19, 11, 8, 44, tzinfo=sifma_mbs.UTC)}, {"A": 30, "B": 31, "C": 29, "D": 28}, False)
        self.assertEqual(mid["years"]["2025"]["dates_after_capture_by_class"], {"A": 11, "B": 11, "C": 12, "D": 12})
        self.assertEqual(summary["terms"], list(mm.CLASS_TERMS))
        self.assertEqual(script.source_summary(table, public, {"A": 3, "B": 31, "C": 29, "D": 28}, True)["terms"], [mm.POOLED_TERM])


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Rulings applied, and the question that remains", text)
        self.assertIn("**Question 1.", text)
        self.assertNotIn("**Question 2.", text)  # her Q2 and Q3 were ruled on 28 October 2026
        self.assertEqual(text.count("(default)"), 1)
        for option in ("1. ", "2. ", "3. "):
            self.assertIn(option, text)
        self.assertNotIn("GO #", text.replace("own `GO`", ""))


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3c_mbs_1276"] = script
        sys.modules["s3c_turn_cap_1265_in_1276"] = script.m1265
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
        self.assertEqual(sorted(cell["vs"][script.S3CM]), sorted(script.plan(script.S3CM)))
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_pooling_outcome_follows_the_counts(self):
        src = self.result["source"]
        self.assertEqual(src["pooled"], mm.must_pool(src["settlement_days_in_window"]))
        self.assertEqual(src["terms"], [mm.POOLED_TERM] if src["pooled"] else list(mm.CLASS_TERMS))
        self.assertEqual(src["window_last"], "2025-12-31")

    def test_the_settlement_groups_are_there(self):
        groups = self.result["windows"]["development"]["groups"][script.CHANGED]
        self.assertIn(script.ANY_DAYS, groups)
        self.assertIn(script.OTHER_DAYS, groups)

    def test_the_page_states_where_the_indicators_act_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("Where the indicators can be non-zero", text)
        self.assertIn("## Rulings applied, and the question that remains", text)
        self.assertIn("**Options**", text)
        self.assertIn("### 90% band coverage beside (s3c)'s", text)
        self.assertIn("The fitted effect of each indicator in bp, by regime", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-mbs-1276" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-mbs-1276-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_mbs_1276.json")
        self.assertEqual(record["availability"], "metadata/sifma_mbs_1276.json")
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

    def test_the_page_cites_no_outside_source(self):
        text = self.PAGE.read_text(encoding="utf-8")
        for word in ("http://", "https://", "et al", "arXiv", "doi"):
            self.assertNotIn(word, text)


if __name__ == "__main__":
    unittest.main()
