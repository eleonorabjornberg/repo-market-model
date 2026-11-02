"""`scripts/s3c_gse_1274.py` (#1274; H5 step 3, development tier): (s3c-gse), (s3c) with the GSE cash cycle as a 19th-25th ramp, scored against
(s3c), (s3), B1, B1' and B2 on the development window and on the 2026 development days.

Written first, against the declaration. The arm's term table is `repo_model.s3c_gse` and is tested in `test_s3c_gse`; the frames, the benchmarks, (s3)
and (s3c) are #1255's (`test_s3c_candidate_1255_script`), loaded as they are. What these tests pin: that the declaration names what the module has (seed,
margin, models, windows, no amendment); the reproduction check of the declaration, that the base-table walk of (s3) is the frame's cell for cell, on hand
cases with the failure when one cell is moved; the arm's forecasts (the ramp walk capped as (s3c) caps) on hand cases; the Brier cell, the ramp-day
split, the refit lookup and the fitted-effect arithmetic on hand cases; the page (the opening question, the marked questions with numbered options and
defaults, no outside source); a small run of `score` and `page` end to end on the fixture panel; and, once the full run is committed, that the tracked
page is what the script renders from the tracked record.

Recorded mutation (the reproduction check of the declaration, #1274): in `s3c_gse_1274.same_as_frame`, the comparison
`if {h: list(q) ...} != {h: list(q) ...}:` was changed to `if False:`. `ReproductionTests.test_a_changed_cell_is_refused` then failed with
`AssertionError` (`ValueError` not raised for a cell moved on 2025-12-04); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace

from repo_model import policy_events as pe
from repo_model import s3c_candidate, s3c_gse
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_gse_1274", ROOT / "scripts" / "s3c_gse_1274.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_gse_1274"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp


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


class Frame:
    """The few members of the scoring frame the functions read: business days in December 2025, a decision on each of the first few."""

    def __init__(self):
        day, self.dates = date(2025, 12, 1), []
        while len(self.dates) < 22:
            if day.weekday() < 5:
                self.dates.append(day)
            day += timedelta(days=1)
        self.days = [d for d in self.dates if d <= date(2025, 12, 19)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.position = {d: i for i, d in enumerate(self.dates)}
        self.forecasts = {}

    def target(self, d, h):
        return self.dates[self.position[d] + h]

    def regime(self, t):
        return "2025-26"

    def day_type(self, t):
        return "ordinary"


def walk_with(frame, quantiles, effect=None, scale=2.0):
    """A stand-in for `spread_mr_state_calendar.Walk`: the same forecast on every day, one refit on the first day, a fixed scale."""

    forecasts = {script.S3: {d: {h: list(quantiles) for h in sp.HORIZONS} for d in frame.days}}
    first = frame.days[0]
    estimates = {first: {script.S3_ARM.name: {h: SimpleNamespace(effect={} if effect is None else {script.TERM: effect}, flagged={}) for h in sp.HORIZONS}}}
    return SimpleNamespace(forecasts=forecasts, estimates=estimates, detail={d: {"scale": scale} for d in frame.days})


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1274)
        self.assertEqual(script.SEED, 1274)
        self.assertIn("seed 1274", declaration["scoring"]["test"])
        self.assertEqual(declaration["candidate"]["margin_bp"], s3c_candidate.MARGIN_BP)
        self.assertEqual(declaration["candidate"]["name"], script.S3CG)
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([w["name"] for w in declaration["frame"]["windows"]], list(script.WINDOWS))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3, script.S3C, script.S3CG])

    def test_the_declared_ramp_is_the_modules(self):
        declaration = script.committed_declaration()
        self.assertIn("(d - 18) / 7", declaration["candidate"]["definition"])
        self.assertEqual((s3c_gse.FIRST_DAY, s3c_gse.LAST_DAY, s3c_gse.REPLACED_TERM), (19, 25, "dom_19_23"))

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_gse_1274.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]), ("metadata/s3c_gse_1274.json", "scripts/s3c_gse_1274.py", "direct"))

    def test_only_the_arm_is_tested_and_against_the_declared_references(self):
        self.assertEqual(script.plan(script.S3CG), [script.S3C, script.S3, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.S3C), [])
        self.assertEqual(script.S3_ARM.name, "sc_s3_robust")

    def test_the_declaration_reads_no_outside_source(self):
        text = json.dumps(script.committed_declaration()).lower()
        self.assertIn("no source", text)


class ReproductionTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()
        self.frame.forecasts = {script.S3: {d: {h: list(Q) for h in sp.HORIZONS} for d in self.frame.days}}
        self.walk = walk_with(self.frame, Q)

    def test_equal_forecasts_are_counted(self):
        self.assertEqual(script.same_as_frame(self.frame, self.walk), len(self.frame.days))

    def test_a_changed_cell_is_refused(self):
        self.walk.forecasts[script.S3][date(2025, 12, 4)][1] = [q - 1.0 for q in Q]
        with self.assertRaises(ValueError):
            script.same_as_frame(self.frame, self.walk)

    def test_a_missing_day_is_refused(self):
        del self.walk.forecasts[script.S3][date(2025, 12, 4)]
        with self.assertRaises(ValueError):
            script.same_as_frame(self.frame, self.walk)


class ForecastTests(unittest.TestCase):

    def setUp(self):
        self.frame, self.reg = Frame(), register()
        self.walk = walk_with(self.frame, Q)

    def test_the_arm_is_the_ramp_walk_capped_as_s3c_caps_it(self):
        ramped, capped = script.gse_forecasts(self.frame, self.walk, self.reg)
        d = date(2025, 12, 10)  # the removal of the limit is announced at 14:00 this day: known to the decision at 16:00
        for h in sp.HORIZONS:
            self.assertEqual(ramped[d][h], Q)
            self.assertEqual(capped[d][h], [min(q, 10.0) for q in Q])
            self.assertEqual(capped[d][h], s3c_candidate.capped_quantiles(Q, self.reg, datetime.combine(d, time(16, 0)), self.frame.target(d, h)))
        d = date(2025, 12, 3)  # every target is before full allotment
        for h in sp.HORIZONS:
            self.assertEqual(capped[d][h], Q)

    def test_the_input_is_not_changed(self):
        script.gse_forecasts(self.frame, self.walk, self.reg)
        self.assertEqual(self.walk.forecasts[script.S3][date(2025, 12, 10)][1], Q)

    def test_a_day_without_a_ramp_forecast_is_refused(self):
        del self.walk.forecasts[script.S3][date(2025, 12, 4)]
        with self.assertRaises(ValueError):
            script.gse_forecasts(self.frame, self.walk, self.reg)


class CellTests(unittest.TestCase):

    def test_the_brier_cell_is_the_squared_error_of_the_probability_of_exceeding_5_bp(self):
        frame = Frame()
        d = frame.days[0]
        t = frame.target(d, 1)
        for outcome, event in ((8.0, 1.0), (5.0, 0.0), (2.0, 0.0)):  # strictly above 5 bp, whole basis points
            frame.outcome[t] = outcome
            forecasts = {d: {h: list(Q) for h in sp.HORIZONS}}
            cells = script.cell_table(frame, forecasts)
            self.assertAlmostEqual(cells["brier_gt5"][(d, 1)], (script.probability(Q, 5.0) - event) ** 2)

    def test_the_band_hit_is_the_closed_q05_to_q95_interval(self):
        frame = Frame()
        d = frame.days[0]
        t = frame.target(d, 1)
        forecasts = {d: {h: list(Q) for h in sp.HORIZONS}}
        lo, hi = Q[sp.GRID.index(0.05)], Q[sp.GRID.index(0.95)]
        for outcome, hit in ((lo, 1.0), (hi, 1.0), (lo - 0.5, 0.0), (hi + 0.5, 0.0)):
            frame.outcome[t] = outcome
            self.assertEqual(script.cell_table(frame, forecasts)["b90_closed"][(d, 1)], hit, outcome)


class GroupTests(unittest.TestCase):

    def test_the_ramp_days_are_the_19th_to_the_25th(self):
        self.assertTrue(all(script.in_ramp(date(2025, 12, d)) for d in range(19, 26)))
        self.assertFalse(any(script.in_ramp(date(2025, 12, d)) for d in (1, 18, 26, 31)))

    def test_the_groups_split_the_target_days_into_ramp_days_and_the_others(self):
        frame = Frame()
        for window, split in (("development", "regime"), ("2026", "month")):
            groups = script.groups_of(frame, window)
            by = {(s, label): members for s, label, _g, members in groups}
            ramp, other = by[(script.RAMP_SPLIT, script.RAMP_DAYS)], by[(script.RAMP_SPLIT, script.OTHER_DAYS)]
            self.assertEqual(set(ramp) & set(other), set())
            self.assertEqual(set(ramp) | set(other), {frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
            self.assertTrue(all(script.in_ramp(t) for t in ramp) and not any(script.in_ramp(t) for t in other))
            self.assertIn(split, {s for s, _l, _g, _m in groups})
            self.assertEqual([s for s, _l, _g, _m in groups if s == "lead"], ["lead"] * 5)

    def test_the_coverage_groups_are_pooled_and_by_lead_in_date_order(self):
        frame = Frame()
        keys = [(d, h) for d in frame.days for h in sp.HORIZONS]
        groups = script.coverage_groups(frame, keys)
        self.assertEqual(list(groups), ["pooled"] + [f"h={h}" for h in sp.HORIZONS])
        self.assertEqual(len(groups["pooled"]), len(keys))
        targets = [frame.target(*x) for x in groups["pooled"]]
        self.assertEqual(targets, sorted(targets))
        self.assertEqual(script.block_of("pooled"), script.CELL_BLOCK)
        self.assertEqual(script.block_of("h=2"), float(sp.BLOCK_LENGTH))


class EffectTests(unittest.TestCase):

    def test_the_latest_refit_on_or_before_the_decision_is_the_fit_in_use(self):
        walk = SimpleNamespace(estimates={date(2025, 12, 1): 1, date(2025, 12, 15): 2})
        self.assertEqual(script.fit_day(walk, date(2025, 12, 1)), date(2025, 12, 1))
        self.assertEqual(script.fit_day(walk, date(2025, 12, 12)), date(2025, 12, 1))
        self.assertEqual(script.fit_day(walk, date(2025, 12, 16)), date(2025, 12, 15))

    def test_the_effect_is_the_coefficient_times_the_scale_and_the_shift_is_scaled_by_the_ramp(self):
        frame = Frame()
        walk = walk_with(frame, Q, effect=1.5, scale=2.0)
        out = script.effect_cells(frame, walk, s3c_gse.ramp)
        cell = out["all regimes"]["all"]
        self.assertEqual(cell["cells"], len(frame.days) * 5)
        self.assertEqual(cell["with_term"], cell["cells"])
        self.assertAlmostEqual(cell["mean_bp_per_unit"], 3.0)
        carrying = [(d, h) for d in frame.days for h in sp.HORIZONS if s3c_gse.ramp(frame.target(d, h)) > 0]
        self.assertEqual(cell["carry"], len(carrying))
        self.assertGreater(cell["carry"], 0)
        self.assertAlmostEqual(cell["mean_applied_bp"], sum(3.0 * s3c_gse.ramp(frame.target(d, h)) for d, h in carrying) / len(carrying))
        self.assertEqual(out["2025-26"]["all"], cell)
        self.assertEqual(sum(out["all regimes"][str(h)]["cells"] for h in sp.HORIZONS), cell["cells"])

    def test_a_fit_without_the_term_has_no_effect_and_is_counted(self):
        frame = Frame()
        out = script.effect_cells(frame, walk_with(frame, Q, effect=None), s3c_gse.ramp)
        cell = out["all regimes"]["all"]
        self.assertEqual((cell["with_term"], cell["mean_bp_per_unit"], cell["mean_applied_bp"]), (0, 0.0, 0.0))


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertEqual(text.count("(default)"), 1)
        for n in ("1. ", "2. ", "3. "):
            self.assertIn(n, text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3c_gse_1274"] = script
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

    def test_the_arm_is_scored_against_the_five_references_on_three_metrics(self):
        for window in script.WINDOWS:
            for metric in script.METRIC_NAMES:
                cell = self.result["windows"][window]["groups"]["pooled"]["all decision days"][metric]
                self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
                self.assertEqual(sorted(cell["vs"][script.S3CG]), sorted(script.REFERENCES))

    def test_the_walk_reproduces_the_frames_s3(self):
        for window in script.WINDOWS:
            w = self.result["windows"][window]
            self.assertEqual(w["walk_equals_frame_days"], w["notes"]["scored_decision_days"])
            self.assertTrue(w["before_full_allotment_is_the_ramp_walk"])

    def test_the_arm_differs_from_s3c_and_the_splits_are_there(self):
        for window in script.WINDOWS:
            w = self.result["windows"][window]
            self.assertGreater(w["cells_where_gse_differs_from_s3c"], 0)
            self.assertIn("ramp_day", w["groups"])
            self.assertIn("lead", w["groups"])
            self.assertIn("pressure_day_type", w["groups"])
            self.assertEqual(set(w["coverage"]), {"pooled"} | {f"h={h}" for h in sp.HORIZONS})
            self.assertEqual(set(w["coverage"]["pooled"]), set(script.COVERAGE_MODELS))
            self.assertIn("all regimes", w["effect"]["gse_ramp"])
        self.assertIn("regime", self.result["windows"]["development"]["groups"])
        self.assertIn("month", self.result["windows"]["2026"]["groups"])

    def test_the_page_opens_with_the_question_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertTrue(text.split("\n", 2)[2].lstrip().startswith("**Does a ramp from the 19th to the 25th"))
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertIn("compares with no outside figure", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-gse-1274" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-gse-1274-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_gse_1274.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["margin_bp"], 0.0)
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        self.assertLessEqual(record["windows"]["2026"]["notes"]["last_target"], script.LAST_DAY.isoformat())

    def test_the_predecessors_s3_and_s3c_are_reproduced(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertTrue(record["against_1255"])
        for window, there in record["against_1255"].items():
            for metric, rows in there["metrics"].items():
                for model, v in rows.items():
                    self.assertAlmostEqual(v["difference"], 0.0, places=9, msg=f"{window} {metric} {model}")


if __name__ == "__main__":
    unittest.main()
