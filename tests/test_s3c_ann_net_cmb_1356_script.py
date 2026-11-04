"""`scripts/s3c_ann_net_cmb_1356.py` (#1356; H5 step 3, development tier): (s3c-ann-net-cmb), a separate cash management bill term on the candidate
(s3c-ann-net), in a flag and a size form, scored against (s3c-ann-net), (s3c) and B1, B1' and B2 at the 18:00 decision instant, on both windows of #1255.

Written first, against the declaration. The new read path (`repo_model.s3c_announced.AnnouncedCmbTerms`, `AnnouncedNetExCmbSizeTable`) and its leakage
test are in `test_s3c_announced_cmb_1356`. What these tests pin: that the declaration names what the module has (seed, models, arms, references, the
last day, no amendment) and that the cleared register row exists; the test plan (the benchmarks on the full splits only); the effect arithmetic on
hand cases; the CMB check on a hand case; the added groups (2020 by month and without the immediate-release days; the immediate-release days by
lead); the refusal to write a walk that lacks a scored day and a record whose references are not #1321's; the page (Lens E's caveat is named, the
marked question carries numbered options and a default); a small run of `score` and `page` end to end on the fixture panel; and, once the full run is
committed, that the tracked page is what the script renders from the tracked record.

Recorded mutation (the check of this study, #1356): in `s3c_ann_net_cmb_1356.walks_of`, the comparison
`if d not in walk.forecasts[names[key]]:` was changed to `if False:`. `WalkTests.test_a_scored_day_without_a_forecast_is_refused` then failed with
`AssertionError` (`ValueError not raised`); restored, it passes.
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

from repo_model import net_settlement as ns
from repo_model import s3c_announced
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_ann_net_cmb_1356", ROOT / "scripts" / "s3c_ann_net_cmb_1356.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_ann_net_cmb_1356"] = script  # the script's worker pool pickles its functions by module name
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
        self.dates = business_days(date(2020, 3, 2), n)
        self.days = [d for d in self.dates if date(2020, 3, 9) <= d <= date(2020, 3, 18)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]

    def regime(self, d):
        return "2020"


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1356)
        self.assertEqual(script.SEED, 1356)
        self.assertIn("seed 1356", declaration["scoring"]["test"])
        self.assertEqual([c["name"] for c in declaration["candidates"]], list(script.ARMS))
        self.assertEqual([c["name"] for c in declaration["references"]], [script.ANNNET, script.S3C, "B1", "B1_prime", "B2"])
        self.assertEqual(declaration["models"], ["B1", "B1_prime", "B2", script.S3C, script.ANNNET, *script.ARMS])
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.ANNNET, script.S3C, *script.ARMS])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual([a["changes_a_figure"] for a in declaration["amendments"]], [False])  # the one naming correction
        self.assertEqual(declaration["arms"][-1]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertIn("18:00", declaration["decision_instant"])

    def test_the_models_are_the_declared_ones_with_the_benchmarks_named_as_the_frame_names_them(self):
        self.assertEqual(script.MODELS, ("B1", script.B1P, "B2", script.S3C, script.ANNNET, *script.ARMS))
        self.assertEqual(script.B1P, "B1_prime")

    def test_the_arms_are_the_modules(self):
        self.assertEqual(s3c_announced.CMB_FLAG_ARM.name.replace("sc_s3_", "sc_s3c_"), script.CMBF)
        self.assertEqual(s3c_announced.CMB_SIZE_ARM.name.replace("sc_s3_", "sc_s3c_"), script.CMBS)
        for candidate in script.committed_declaration()["candidates"]:
            self.assertIn("repo_model.s3c_announced", candidate["module"])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_ann_net_cmb_1356.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_ann_net_cmb_1356.json", "scripts/s3c_ann_net_cmb_1356.py", "direct"))

    def test_the_effect_terms_are_the_terms_the_arms_fit(self):
        self.assertEqual(script.EFFECT_TERMS[script.CMBF], ("settlement_coupon", "settlement_bill", sc.CMB_FLAG))
        self.assertEqual(script.EFFECT_TERMS[script.CMBS], ("settlement_coupon", "settlement_bill", sc.CMB_SIZE))
        self.assertEqual(s3c_announced.CMB_SIZE_ARM.extra, (sc.CMB_SIZE,))

    def test_the_plan(self):
        for arm in script.ARMS:
            self.assertEqual(script.plan(arm, "pooled"), [script.ANNNET, script.S3C, "B1", script.B1P, "B2"])
            self.assertEqual(script.plan(arm, "lead"), [script.ANNNET, script.S3C, "B1", script.B1P, "B2"])
            self.assertEqual(script.plan(arm, script.DAY_TYPE), [script.ANNNET, script.S3C])
            self.assertEqual(script.plan(arm, script.IMMEDIATE), [script.ANNNET, script.S3C])
        self.assertEqual(script.plan(script.ANNNET, "regime"), [script.S3C])
        self.assertEqual(script.plan(script.S3C), [])


class EffectTests(unittest.TestCase):

    def test_a_flag_and_a_size_effect_are_in_bp_and_a_term_out_of_the_fit_counts_zero(self):
        frame = Frame()
        frame.days = frame.days[:3]
        used = frame.dates[0]
        est = sc.StateEstimate(("settlement_coupon", sc.CMB_SIZE), {"settlement_coupon": 0.1, sc.CMB_SIZE: 0.2}, {}, {}, [0.0], 1, 0, 1)
        walk = SimpleNamespace(fit_used={d: used for d in frame.days}, estimates={used: {"arm": {3: est}}}, detail={d: {"scale": 5.0} for d in frame.days})
        terms = ("settlement_coupon", "settlement_bill", sc.CMB_SIZE)

        def read(lead, index):
            return {"settlement_coupon": 0.3, "settlement_bill": 1.0, sc.CMB_SIZE: 0.5}

        out = script.effects(frame, walk, "arm", terms, 3, read, reps=20)["all"]
        self.assertAlmostEqual(out["settlement_coupon"]["mean"], 0.5)  # 0.1 per USD 100 bn x 5 bp
        self.assertAlmostEqual(out[sc.CMB_SIZE]["mean"], 1.0)
        self.assertEqual(out["settlement_bill"]["mean"], 0.0)
        self.assertEqual(out["settlement_bill"]["share_in_fit"], 0.0)
        self.assertEqual(out["active_days"], 3)
        self.assertAlmostEqual(out["mean_abs_shift_bp_on_active_days"], 0.5 * 0.3 + 1.0 * 0.5)

    def test_the_values_are_the_net_over_the_unit_and_the_cmb_term(self):
        net_table = SimpleNamespace(read=lambda lead, index: {"settlement_coupon": 10.0, "settlement_bill": -20.0})
        ex_table = SimpleNamespace(read=lambda lead, index: {"settlement_coupon": 10.0, "settlement_bill": -30.0})
        cmb = {sc.CMB_FLAG: SimpleNamespace(read=lambda lead, index: {sc.CMB_FLAG: 1.0}),
               sc.CMB_SIZE: SimpleNamespace(read=lambda lead, index: {sc.CMB_SIZE: 0.1})}
        tables = (None, net_table, ex_table, cmb)
        self.assertEqual(script.effect_values(script.ANNNET, 3, 0, tables), {"settlement_coupon": 0.1, "settlement_bill": -0.2})
        self.assertEqual(script.effect_values(script.CMBF, 3, 0, tables), {"settlement_coupon": 0.1, "settlement_bill": -0.3, sc.CMB_FLAG: 1.0})
        self.assertEqual(script.effect_values(script.CMBS, 3, 0, tables), {"settlement_coupon": 0.1, "settlement_bill": -0.3, sc.CMB_SIZE: 0.1})


class CheckTests(unittest.TestCase):

    def test_the_cmb_check_counts_announced_immediate_and_gate_cells(self):
        frame = Frame()
        frame.days = frame.days[:2]
        panel = [DailyObservation(d, {}) for d in frame.dates]
        target = frame.target(frame.days[0], 2)
        noon = lambda d: datetime.combine(d, time(12, 0))  # noqa: E731
        # A 60 bn CMB announced before the first decision day, with the regular bills of the day announced after it (the class gate).
        auctions = [ns.Auction(target, "Bill", True, 60.0, 20.0, 0.0, noon(frame.dates[0]), None, True),
                    ns.Auction(target, "Bill", True, 30.0, 20.0, 0.0, noon(frame.dates[8]), None, False)]
        t = s3c_announced
        tables = (None, t.AnnouncedNetSizeTable(panel, auctions), t.AnnouncedNetExCmbSizeTable(panel, auctions),
                  {sc.CMB_FLAG: t.AnnouncedCmbTerms(panel, auctions, (sc.CMB_FLAG,)), sc.CMB_SIZE: t.AnnouncedCmbTerms(panel, auctions, (sc.CMB_SIZE,))})
        facts = {d: {"cmb": d == target} for d in frame.dates}
        out = script.cmb_check(frame, facts, tables, [target.isoformat()])
        self.assertEqual(out["2"]["cmb_days"], 1)
        self.assertEqual(out["2"]["cmb_announced"], 1)
        self.assertEqual(out["2"]["immediate_days"], 1)
        self.assertEqual(out["2"]["gate_differs"], 1)  # the regular bill is announced later: (s3c-ann-net) reads 0, the CMB term 0.6
        self.assertEqual(out["1"]["cmb_days"], 1)  # the second decision day's lead-1 target is the same day
        self.assertEqual(out["3"]["cmb_days"], 0)


class GroupTests(unittest.TestCase):

    def test_the_added_groups(self):
        frame = Frame()
        labels = {d: ["x"] for d in frame.dates}
        facts = {d: {"coupon": False, "bill": True, "cmb": d.day % 2 == 0} for d in frame.dates}
        imm = [d.isoformat() for d in frame.dates if d.day % 4 == 0]
        groups, counts = script.extra_groups(frame, labels, facts, imm)
        by = {(g[0], g[1]): g[3] for g in groups}
        spring = by[("regime", script.Y2020_SPRING)]
        self.assertTrue(spring and all(3 <= t.month <= 6 for t in spring))
        self.assertTrue(all(t.isoformat() not in imm for t in by[("regime", script.Y2020_NO_IMMEDIATE)]))
        self.assertEqual(len(by[("regime", script.Y2020_SPRING)]) + len(by.get(("regime", script.Y2020_REST), [])), len(labels))
        self.assertIn((script.DAY_TYPE, f"h=3: {script.CMB_DAYS}"), by)
        on = by[(script.IMMEDIATE, "h=2: an immediate-release CMB settles on the target")]
        self.assertTrue(all(frame.target(d, 2).isoformat() in imm for d in on))
        self.assertEqual(counts["2"], len(on))


class WalkTests(unittest.TestCase):

    def run_walks(self, drop=None):
        frame = Frame()

        def fake_walk(panel, days, table, states, arms, **kw):
            forecasts = {a.name: {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days} for a in arms}
            if drop is not None and drop in forecasts:
                forecasts[drop].pop(frame.days[0])
            return SimpleNamespace(forecasts=forecasts, fits={})

        original = script.sc.walk, script.m1288.candidate_days
        script.sc.walk, script.m1288.candidate_days = fake_walk, lambda *a, **kw: list(frame.days)
        try:
            panel = [DailyObservation(d, {}) for d in frame.dates]
            return script.walks_of("development", frame, panel, None, {}, [], [], None)
        finally:
            script.sc.walk, script.m1288.candidate_days = original

    def test_walks_with_every_scored_day_are_accepted(self):
        walks, names, tables = self.run_walks()
        self.assertEqual(sorted(walks), ["flag", "ref", "size"])
        self.assertEqual(names["flag"], s3c_announced.CMB_FLAG_ARM.name)
        self.assertEqual(tables[2].__class__, s3c_announced.AnnouncedNetExCmbSizeTable)
        self.assertEqual(sorted(tables[3]), [sc.CMB_FLAG, sc.CMB_SIZE])

    def test_a_scored_day_without_a_forecast_is_refused(self):
        # Recorded mutation: see the module docstring (`walks_of`).
        with self.assertRaises(ValueError):
            self.run_walks(drop=s3c_announced.CMB_SIZE_ARM.name)


class ReferenceTests(unittest.TestCase):

    def test_references_that_are_not_1321s_are_refused(self):
        there = json.loads(script.RECORD_1321.read_text(encoding="utf-8"))["windows"]
        window = next(iter(there))
        here = json.loads(json.dumps({window: there[window]}))
        script.against_1321(here)  # the same record agrees
        here[window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"][script.ANNNET] += 1e-6
        with self.assertRaises(ValueError):
            script.against_1321(here)


class DecisionInstantTests(unittest.TestCase):
    """The chain held 16:00 until the family's default moved to 18:00 (#1397); the test puts it back at 16:00 for its length, as a run that sets
    `RMM_DECISION_TIME=16:00` would have it."""

    def setUp(self):
        self._held = [(m, m.DECISION_TIME) for m in script.m1321.chain_modules() if hasattr(m, "DECISION_TIME")]
        for module, _ in self._held:
            module.DECISION_TIME = time(16, 0)
        self.addCleanup(lambda: [setattr(m, "DECISION_TIME", t) for m, t in self._held])

    def test_the_chain_reads_18_00_inside_the_block_and_16_00_after_it(self):
        with script.decision_instant_pinned() as instant:
            self.assertEqual(instant, time(18, 0))
            for module in (script.k, script.c, script.s686):
                self.assertEqual(module.DECISION_TIME, time(18, 0), module.__name__)
        self.assertEqual(script.s686.DECISION_TIME, time(16, 0))


class PageTests(unittest.TestCase):

    def test_the_question_is_marked_numbered_and_carries_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Question for Eleonora", text)
        self.assertEqual(text.count("(default)"), 1)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertNotIn("GO #", text)

    def test_a_release_day_list_is_dates_of_cash_management_bills(self):
        days = script.release_days()
        self.assertTrue(days)
        self.assertTrue(all(len(d) == 10 for d in days))


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

    def test_the_forms_are_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            for split, label in (("pooled", "all decision days"), (script.DAY_TYPE, f"h=2: {script.TYPE_LABELS[1]}")):
                cell = w["groups"][split][label]["grid_crps"]
                for candidate in script.ARMS:
                    self.assertEqual(sorted(cell["vs"][candidate]), sorted(script.plan(candidate, split)))
                self.assertEqual(sorted(cell["vs"][script.ANNNET]), [script.S3C])
                self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_split_adds_up_except_where_the_class_gate_differs(self):
        for w in self.result["windows"].values():
            for lead, n in w["cmb_check"].items():
                self.assertEqual(n["split_not_exact"], n["gate_differs"], lead)

    def test_the_effect_is_reported_by_lead_for_every_model_and_term(self):
        for w in self.result["windows"].values():
            for model in script.EFFECT_TERMS:
                self.assertEqual(sorted(w["effects"][model]), ["1", "2", "3", "4", "5"])
                for eff in w["effects"][model].values():
                    for term in script.EFFECT_TERMS[model]:
                        self.assertIn("mean", eff["all"][term])

    def test_the_cmb_days_are_split_against_the_other_bill_days_at_each_lead(self):
        for w in self.result["windows"].values():
            labels = w["groups"][script.DAY_TYPE]
            for lead in (1, 2, 3, 4, 5):
                self.assertIn(f"h={lead}: {script.CMB_DAYS}", labels)
                self.assertIn(f"h={lead}: {script.OTHER_BILL_DAYS}", labels)

    def test_the_page_names_the_caveat_the_forms_and_ends_with_the_marked_question(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## Does the arm remove the 2020 loss, and at what cost elsewhere?", text)
        self.assertIn("Lens E", text)
        self.assertIn("flag form", text)
        self.assertIn("size form", text)
        self.assertIn("## Question for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-ann-net-cmb-1356" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-ann-net-cmb-1356-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"], record["reps"]), (script.SEED, sp.DRAWS, script.REPS))
        self.assertEqual(record["declaration"], "metadata/s3c_ann_net_cmb_1356.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["decision_time"], "18:00")
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertEqual(w["cmb_check"]["1"]["split_not_exact"], w["cmb_check"]["1"]["gate_differs"])
        self.assertTrue(record["against_1321"])


if __name__ == "__main__":
    unittest.main()
