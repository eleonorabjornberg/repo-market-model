"""`scripts/s3c_net_settlement_1273.py` (#1273; H5 step 3, development tier): (s3c-net), (s3c) with net bill and net coupon settlement in place of the
gross flags, scored against (s3c), (s3), the control (s3c-gross), B1, B1' and B2 on both windows of #1255.

Written first, against the declaration. The new read path (`repo_model.s3c_net.NetSizeTable`) and its leakage test are in `test_s3c_net`; the cap, the
line and the full-allotment flag are (s3c)'s (`test_s3c_candidate`). What these tests pin: that the declaration names what the module has (seed, models, the
arms, the last day, no amendment) and that the cleared register row exists; the test plan; the Brier cell arithmetic (strict event on whole basis points)
and the 90% band hit; the gross-against-panel check; the cell-by-lead difference count; the changed-term day split; the per-regime effect arithmetic on a
hand case (the term enters the mean in bp per USD 100 bn, a day without the term in the fit counts 0); the page (the control and the practitioner's figure are
named, the marked questions carry numbered options and one default); the refusal to walk a day whose (s3) differs from #1255's frame; a small run of
`score` and `page` end to end on the fixture panel; and, once the full run is committed, that the tracked page is what the script renders from the
tracked record and that #1255's pooled means are reproduced.

Recorded mutation (the check of this study, #1273): in `s3c_net_settlement_1273.extra_walks`, the comparison
`if walk.forecasts[S3][d] != frame.forecasts[S3][d]:` was changed to `if False:`. `ExtraWalkTests.test_a_walk_that_is_not_1255s_is_refused` then failed with
`AssertionError` (`ValueError` not raised); restored, it passes. Second mutation (the event definition): in `cell_table`, `data.exceeds_bp(y, TAU)` was
replaced by `y >= TAU`; `CellTableTests.test_the_event_is_strict_on_whole_basis_points` then failed with `AssertionError` (`1.0 != 0.0`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

from repo_model import net_settlement as ns
from repo_model import s3c_net
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_net_settlement_1273", ROOT / "scripts" / "s3c_net_settlement_1273.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_net_settlement_1273"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class Frame:
    """The few members of the scoring frame the checks read."""

    def __init__(self, spreads=None, n=26):
        self.dates = business_days(date(2025, 12, 1), n)
        self.days = [d for d in self.dates if date(2025, 12, 8) <= d <= date(2025, 12, 24)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.outcome.update(spreads or {})
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]

    def regime(self, d):
        return "2025-26"


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1273)
        self.assertEqual(script.SEED, 1273)
        self.assertIn("seed 1273", declaration["scoring"]["test"])
        self.assertEqual(declaration["candidate"]["name"], script.S3CN)
        self.assertEqual(declaration["control"]["name"], script.S3CG)
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3, script.S3C, script.S3CG, script.S3CN])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual(declaration["candidate"]["margin_bp"], script.s3c_candidate.MARGIN_BP)

    def test_the_arm_and_the_control_are_the_modules(self):
        self.assertEqual(s3c_net.NET_ARM.name, "sc_s3_net")
        self.assertEqual(s3c_net.GROSS_ARM.name, "sc_s3_gross_size")
        self.assertIn("repo_model.s3c_net", script.committed_declaration()["candidate"]["module"])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_net_settlement_1273.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_net_settlement_1273.json", "scripts/s3c_net_settlement_1273.py", "direct"))

    def test_the_plan(self):
        self.assertEqual(script.plan(script.S3CN), [script.S3C, script.S3, script.S3CG, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.S3CG), [script.S3C])
        self.assertEqual(script.plan(script.S3), [])


class CellTableTests(unittest.TestCase):

    def test_the_event_is_strict_on_whole_basis_points(self):
        # 5.0 is on the threshold: not above it; 5.5 rounds to 6 bp: above it (data.exceeds_bp)
        frame = Frame({date(2025, 12, 9): 5.0, date(2025, 12, 10): 5.6})
        flat = {h: [0.0] * 23 for h in sp.HORIZONS}
        cells = script.cell_table(frame, {date(2025, 12, 8): flat}, script.LAST_DAY)
        self.assertEqual(cells["brier_gt5"][(date(2025, 12, 8), 1)], 0.0)
        self.assertEqual(cells["brier_gt5"][(date(2025, 12, 8), 2)], 1.0)

    def test_the_band_hit_is_closed_at_the_ends(self):
        frame = Frame({date(2025, 12, 9): Q[script.BAND90[1]], date(2025, 12, 10): Q[script.BAND90[1]] + 0.01})
        cells = script.cell_table(frame, {date(2025, 12, 8): {h: list(Q) for h in sp.HORIZONS}}, script.LAST_DAY)
        self.assertEqual(cells["b90_closed"][(date(2025, 12, 8), 1)], 1.0)
        self.assertEqual(cells["b90_closed"][(date(2025, 12, 8), 2)], 0.0)

    def test_the_metrics_are_there_for_every_cell(self):
        frame = Frame()
        cells = script.cell_table(frame, {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}, script.LAST_DAY)
        self.assertEqual(sorted(cells), sorted(script.METRIC_NAMES))
        for m in script.METRIC_NAMES:
            self.assertEqual(len(cells[m]), 5 * len(frame.days))

    def test_a_locked_day_is_refused(self):
        frame = Frame(n=26)
        late = {date(2026, 9, 7): {h: list(Q) for h in sp.HORIZONS}}
        frame.dates = business_days(date(2026, 9, 1), 12)
        frame.position = {d: i for i, d in enumerate(frame.dates)}
        frame.outcome = {d: 0.0 for d in frame.dates}
        with self.assertRaises(Exception):
            script.cell_table(frame, late, script.LAST_DAY)


class ChecksTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()
        self.panel = [DailyObservation(d, {"treasury_settlement_bills": 0.0, "treasury_settlement_coupons": 0.0}) for d in self.frame.dates]

    def test_the_gross_check_counts_the_days_that_differ(self):
        target = self.frame.target(date(2025, 12, 8), 1)
        auctions = [ns.Auction(target, "Bill", True, 100.0, 60.0, 0.0, ns.datetime.combine(date(2025, 12, 1), ns.time(12, 0)), None)]
        self.assertEqual(script.gross_check(self.frame, self.panel, auctions)["differences"], 1)
        self.panel[self.frame.position[target]].values["treasury_settlement_bills"] = 100.0
        self.assertEqual(script.gross_check(self.frame, self.panel, auctions)["differences"], 0)

    def test_the_lead_difference_counts_cells_by_lead(self):
        base = {d: {h: list(Q) for h in sp.HORIZONS} for d in self.frame.days}
        other = {d: {h: list(Q) for h in sp.HORIZONS} for d in self.frame.days}
        other[self.frame.days[0]][1] = [q + 1.0 for q in Q]
        self.frame.forecasts = {"a": base, "b": other}
        out = script.lead_difference(self.frame, "a", "b")
        self.assertEqual(out["differing_cells"], {"1": 1, "2": 0, "3": 0, "4": 0, "5": 0})
        self.assertEqual(out["cells_per_lead"], len(self.frame.days))

    def test_the_changed_term_days_split_on_a_non_zero_net_at_lead_1(self):
        target = self.frame.target(self.frame.days[1], 1)
        auctions = [ns.Auction(target, "Note", False, 50.0, 80.0, 0.0, ns.datetime.combine(self.frame.dates[0], ns.time(12, 0)), None)]
        table = s3c_net.NetSizeTable(self.panel, auctions)
        nonzero, zero = script.changed_term_days(self.frame, table)
        self.assertEqual(nonzero, [self.frame.days[1]])
        self.assertEqual(sorted(nonzero + zero), sorted(self.frame.days))


class EffectTests(unittest.TestCase):

    def test_the_effect_is_in_bp_per_100_bn_and_a_day_without_the_term_counts_zero(self):
        frame = Frame()
        frame.days = frame.days[:3]
        used = frame.dates[0]
        with_term = sc.StateEstimate(("settlement_bill",), {"settlement_bill": 0.02}, {}, {}, [0.0], 1, 0, 1, True)
        without = sc.StateEstimate((), {}, {}, {}, [0.0], 1, 0, 1, True)
        walk = SimpleNamespace(
            fit_used={d: used for d in frame.days},
            estimates={used: {"arm": {1: with_term}}},
            detail={d: {"scale": 5.0} for d in frame.days},
        )
        walk.estimates[used]["arm2"] = {1: without}
        panel = [DailyObservation(d, {}) for d in frame.dates]
        target = frame.target(frame.days[0], 1)
        auctions = [ns.Auction(target, "Bill", True, 100.0, 0.0, 0.0, ns.datetime.combine(frame.dates[0], ns.time(12, 0)), None)]
        table = s3c_net.NetSizeTable(panel, auctions)
        arm, arm2 = SimpleNamespace(name="arm"), SimpleNamespace(name="arm2")
        out = script.effects(frame, walk, arm, table)
        self.assertAlmostEqual(out["all"]["settlement_bill"]["mean"], 0.1)  # 0.02 per 100 bn x 5 bp scale
        self.assertEqual(out["all"]["settlement_bill"]["share_in_fit"], 1.0)
        self.assertEqual(out["all"]["active_days"], 1)
        self.assertAlmostEqual(out["all"]["mean_abs_shift_bp_on_active_days"], 0.1)  # 1.0 x 100 bn of net bill: 0.1 bp
        self.assertAlmostEqual(out["all"]["implied_bp_per_100bn_on_active_days"], 0.1)
        none = script.effects(frame, walk, arm2, table)
        self.assertEqual(none["all"]["settlement_bill"]["mean"], 0.0)
        self.assertEqual(none["all"]["settlement_bill"]["share_in_fit"], 0.0)
        self.assertEqual(none["all"]["implied_bp_per_100bn_on_active_days"], 0.0)


class ExtraWalkTests(unittest.TestCase):

    def test_a_walk_that_is_not_1255s_is_refused(self):
        frame = Frame()
        frame.forecasts = {script.S3: {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}}
        arm_names = (s3c_net.NET_ARM.name, s3c_net.GROSS_ARM.name)
        calls = []

        def fake_walk(panel, days, table, states, arms, **kw):
            calls.append(arms)
            shifted = {d: {h: [q + 1.0 for q in Q] for h in sp.HORIZONS} for d in frame.days}
            same = {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}
            forecasts = {script.S3: shifted, **{name: same for name in arm_names}}
            return SimpleNamespace(forecasts=forecasts)

        original, original_days = script.sc.walk, script.candidate_days
        script.sc.walk, script.candidate_days = fake_walk, lambda *a, **kw: list(frame.days)
        try:
            panel = [DailyObservation(d, {}) for d in frame.dates]
            with self.assertRaises(ValueError):
                script.extra_walks("development", frame, panel, None, {}, None, [], None)
        finally:
            script.sc.walk, script.candidate_days = original, original_days


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
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

    def test_the_arm_is_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["vs"][script.S3CN]), sorted(script.plan(script.S3CN)))
            self.assertEqual(sorted(cell["vs"][script.S3CG]), sorted(script.plan(script.S3CG)))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_terms_are_read_at_lead_1_only(self):
        for w in self.result["windows"].values():
            diff = w["lead_difference"]["net_against_s3c"]["differing_cells"]
            self.assertGreater(diff["1"], 0)
            for h in ("2", "3", "4", "5"):
                self.assertEqual(diff[h], 0, h)

    def test_the_net_is_built_from_the_panels_own_auctions(self):
        for w in self.result["windows"].values():
            self.assertEqual(w["gross_check"]["differences"], 0, w["gross_check"])

    def test_the_effect_is_reported_by_regime_for_both_terms(self):
        for w in self.result["windows"].values():
            self.assertIn("all", w["effects"]["net"])
            for term in script.TERMS:
                self.assertIn("mean", w["effects"]["net"]["all"][term])

    def test_the_page_names_the_control_the_practitioner_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("(s3c-gross)", text)
        self.assertIn("practitioner", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-net-settlement-1273" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-net-settlement-1273-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_net_settlement_1273.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertEqual(w["gross_check"]["differences"], 0)

    def test_s3_and_s3c_are_reproduced_from_1255(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertTrue(record["against_1255"])
        for rec in record["against_1255"].values():
            for rows in rec["metrics"].values():
                for v in rows.values():
                    self.assertLess(abs(v["difference"]), 1e-9)


if __name__ == "__main__":
    unittest.main()
