"""`scripts/s3c_bill_iorb_1346.py` (#1346; H5 step 3, development tier): (s3c-ann-net-bill), one arm on the candidate (s3c-ann-net) reading the
4-week bill rate less IORB of the previous business day, scored against (s3c-ann-net) and (s3c) at the 18:00 decision instant, on both windows
of #1255.

Written first, against the declaration. The new read path (`repo_model.s3c_bill_iorb.BillLessIorbTable`) and its leakage test are in
`test_s3c_bill_iorb`. What these tests pin: that the declaration names what the module has (seed, models, arm, references, the last day, no
amendment) and that the cleared register row exists; the test plan; the effect and range arithmetic on hand cases (an effect in bp per 10 bp of
the gap, a term out of the fit counted as zero); the refusal to write a walk that lacks a scored day; the page (the same-day availability that #1334
leaves open is named, the marked questions carry numbered options and a default); a small run of `score` and `page` end to end on the fixture panel;
and that the tracked page is what the script renders from the tracked record, and that the record's references are #1321's.

Recorded mutation (the check of this study, #1346): in `s3c_bill_iorb_1346.walk_of`, the comparison `if d not in walk.forecasts[name]:` was changed
to `if False:`. `WalkTests.test_a_scored_day_without_a_forecast_is_refused` then failed with `AssertionError` (`ValueError not raised`); restored,
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

from repo_model import s3c_announced, s3c_bill_iorb
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_bill_iorb_1346", ROOT / "scripts" / "s3c_bill_iorb_1346.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_bill_iorb_1346"] = script  # the script's worker pool pickles its functions by module name
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
    def __init__(self, n=26):
        self.dates = business_days(date(2025, 12, 1), n)
        self.days = [d for d in self.dates if date(2025, 12, 8) <= d <= date(2025, 12, 17)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]

    def regime(self, d):
        return "2025-26"


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1346)
        self.assertEqual(script.SEED, 1346)
        self.assertIn("seed 1346", declaration["scoring"]["test"])
        self.assertEqual([c["name"] for c in declaration["candidates"]], list(script.ARMS))
        self.assertEqual([c["name"] for c in declaration["references"]], list(script.REFERENCES))
        self.assertEqual(declaration["models"], [script.S3C, script.ANNNET, script.BILL])
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3C, script.ANNNET, script.BILL])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual(declaration["arms"][-1]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertIn("previous business day", declaration["candidates"][0]["definition"])
        self.assertIn("units of 10 bp", declaration["candidates"][0]["definition"])

    def test_the_arm_is_the_module(self):
        self.assertEqual(s3c_bill_iorb.BILL_ARM.name, "sc_s3_ann_net_bill")
        self.assertEqual(s3c_bill_iorb.UNIT_BPS, 10.0)
        self.assertIn("repo_model.s3c_bill_iorb", script.committed_declaration()["candidates"][0]["module"])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_bill_iorb_1346.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_bill_iorb_1346.json", "scripts/s3c_bill_iorb_1346.py", "direct"))

    def test_the_plan(self):
        self.assertEqual(script.plan(script.BILL), [script.ANNNET, script.S3C])
        self.assertEqual(script.plan(script.S3C), [])
        self.assertEqual(script.plan(script.ANNNET), [])


class EffectTests(unittest.TestCase):

    def walk(self, frame, estimate):
        used = frame.dates[0]
        return SimpleNamespace(fit_used={d: used for d in frame.days}, estimates={used: {s3c_bill_iorb.BILL_ARM.name: {3: estimate}}},
                               detail={d: {"scale": 5.0} for d in frame.days})

    def table(self, value):
        return SimpleNamespace(read=lambda lead, index: {sc.BILL_LESS_IORB: value})

    def test_the_effect_is_in_bp_per_10_bp_of_the_gap(self):
        frame = Frame()
        frame.days = frame.days[:3]
        est = sc.StateEstimate((sc.BILL_LESS_IORB,), {sc.BILL_LESS_IORB: 0.02}, {}, {}, [0.0], 1, 0, 1)
        out = script.effects(frame, self.walk(frame, est), 3, self.table(-2.0), reps=20)["all"]
        self.assertAlmostEqual(out["mean"], 0.1)  # 0.02 per 10 bp x 5 bp scale
        self.assertEqual(out["share_in_fit"], 1.0)
        self.assertAlmostEqual(out["mean_abs_shift_bp"], 0.1 * 2.0)

    def test_a_term_out_of_the_fit_counts_zero(self):
        frame = Frame()
        frame.days = frame.days[:3]
        est = sc.StateEstimate((), {}, {}, {}, [0.0], 1, 0, 1)
        out = script.effects(frame, self.walk(frame, est), 3, self.table(-2.0), reps=20)["all"]
        self.assertEqual((out["mean"], out["share_in_fit"], out["mean_abs_shift_bp"]), (0.0, 0.0, 0.0))

    def test_the_range_of_the_term(self):
        frame = Frame()
        values = {d: v for d, v in zip(frame.days, [-3.0, -1.0, 0.0, 1.0, 1.0, 2.0, 2.0, 2.0])}
        table = SimpleNamespace(read=lambda lead, index: {sc.BILL_LESS_IORB: values[frame.dates[index]]})
        out = script.term_range(frame, table)
        self.assertEqual((out["days"], out["min"], out["max"]), (8, -3.0, 2.0))
        self.assertAlmostEqual(out["mean"], 0.5)
        self.assertAlmostEqual(out["sd"], (sum((v - 0.5) ** 2 for v in values.values()) / 8) ** 0.5)
        self.assertAlmostEqual(out["share_positive"], 5 / 8)
        self.assertEqual(out["unit_bp"], 10.0)


class WalkTests(unittest.TestCase):

    def run_walk(self, drop=None):
        frame = Frame()
        frame.forecasts = {}
        names = (s3c_announced.ANN_NET_ARM.name, s3c_bill_iorb.BILL_ARM.name)

        def fake_walk(panel, days, table, states, arms, **kw):
            self.assertEqual([a.name for a in arms], list(names))
            self.assertIsInstance(kw["iorb"], s3c_bill_iorb.BillLessIorbTable)
            self.assertIsNotNone(kw["sizes"])
            forecasts = {n: {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days} for n in names}
            if drop is not None:
                forecasts[drop].pop(frame.days[0])
            return SimpleNamespace(forecasts=forecasts, fits={})

        original = script.sc.walk, script.m1288.candidate_days
        script.sc.walk, script.m1288.candidate_days = fake_walk, lambda *a, **kw: list(frame.days)
        try:
            panel = [DailyObservation(d, {"tbill_4w": 1.0, "iorb": 1.0}) for d in frame.dates]
            return script.walk_of("development", frame, panel, None, {}, [], [], None)
        finally:
            script.sc.walk, script.m1288.candidate_days = original

    def test_a_complete_walk_is_accepted_with_the_bill_table(self):
        walk, table = self.run_walk()
        self.assertIsInstance(table, s3c_bill_iorb.BillLessIorbTable)
        self.assertEqual(sorted(walk.forecasts), sorted([s3c_announced.ANN_NET_ARM.name, s3c_bill_iorb.BILL_ARM.name]))

    def test_a_scored_day_without_a_forecast_is_refused(self):
        # Recorded mutation: see the module docstring (`walk_of`, the scored-day comparison).
        for name in (s3c_announced.ANN_NET_ARM.name, s3c_bill_iorb.BILL_ARM.name):
            with self.assertRaises(ValueError):
                self.run_walk(drop=name)


class DecisionInstantTests(unittest.TestCase):
    """The study modules of #1115 to #1288 type 16:00; this study runs them at the declared instant and puts them back.

    Recorded mutation (#1346): in `decision_instant_pinned`, `module.DECISION_TIME = DECISION_TIME` was changed to
    `module.DECISION_TIME = LEGACY_DECISION_TIME` (the pin that pins nothing). All three tests then failed with `ValueError` (the guard on entry
    to the block: the instant of the chain is 16:00, not the declared 18:00); restored, they pass.
    """

    def test_the_chain_reads_18_00_inside_the_block(self):
        with script.decision_instant_pinned() as instant:
            self.assertEqual(instant, time(18, 0))
            for module in (script.k, script.c, script.s686, script.m1255.d1222):
                self.assertEqual(module.DECISION_TIME, time(18, 0), module.__name__)

    def test_the_legacy_instant_is_back_after_the_block(self):
        with script.decision_instant_pinned():
            pass
        for module in (script.k, script.c, script.s686, script.m1255.d1222):
            self.assertEqual(module.DECISION_TIME, time(16, 0), module.__name__)

    def test_a_block_that_fails_still_puts_it_back(self):
        with self.assertRaises(RuntimeError), script.decision_instant_pinned():
            raise RuntimeError("inside")
        self.assertEqual(script.s686.DECISION_TIME, time(16, 0))


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertEqual(text.count("(default)"), 1)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertIn("3. ", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-09-02"

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

    def test_the_arm_is_scored_against_what_the_plan_says_on_the_declared_splits(self):
        for w in self.result["windows"].values():
            self.assertTrue({"pooled", "lead", "pressure_day_type"} <= set(w["groups"]) <= set(script.SPLITS))
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["vs"][script.BILL]), sorted(script.plan(script.BILL)))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
            for metric in script.TESTED:
                self.assertIn(metric, w["groups"]["lead"]["h=1"])

    def test_the_arm_differs_from_the_candidate_and_the_term_is_reported(self):
        for w in self.result["windows"].values():
            self.assertTrue(all(n > 0 for n in w["lead_difference"]["bill_against_ann_net"]["differing_cells"].values()))
            self.assertEqual(sorted(w["effects"]), ["1", "2", "3", "4", "5"])
            for eff in w["effects"].values():
                self.assertIn("mean", eff["all"])
            self.assertLessEqual(w["term_range"]["min"], w["term_range"]["max"])

    def test_the_page_names_the_availability_the_arm_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## Summary: grid CRPS by lead", text)
        self.assertIn("#1334", text)
        self.assertIn("(s3c-ann-net-bill)", text)
        self.assertIn("previous business day", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-bill-iorb-1346" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-bill-iorb-1346-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"], record["reps"]), (script.SEED, sp.DRAWS, script.REPS))
        self.assertEqual(record["declaration"], "metadata/s3c_bill_iorb_1346.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["decision_time"], "18:00")
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())

    def test_the_references_are_the_ones_1321_re_ran_at_18_00(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for window, metrics_ in record["against_1321"].items():
            for metric, rows in metrics_.items():
                for model, v in rows.items():
                    self.assertLess(abs(v["difference"]), 1e-9, (window, metric, model))


if __name__ == "__main__":
    unittest.main()
