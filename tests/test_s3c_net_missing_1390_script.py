"""`scripts/s3c_net_missing_1390.py` (#1390; H5 registration design, data meaning; development tier): the count of the settlement days that rest on a missing
figure, and (s3c-ann-net) with those days read as now and with the missing class dropped and a missingness flag, scored against (s3c), B1, B1' and B2 at the
18:00 decision instant on both windows of #1255.

Written first, against the declaration. The reader's state and the two new tables and their leakage tests are in `test_net_missing_1390`. What these tests
pin: that the declaration names what the module has (seed, models, the two readings keyed as `arms`, the last day, the one recorded amendment) and that the cleared register row exists; the test
plan; the count on hand cases (the day-level categories exclude one another, a genuine zero is not missing, a CMB announced later is counted in hindsight and
is not a state); the per-forecast log and the missing-state groups on hand cases; the refusal to write a walk that lacks a scored day and a record whose
references are not #1356's; the page (the marked question carries numbered options and a default); a small run of `score` and `page` end to end on the
fixture panel; and, once the full run is committed, that the tracked page is what the script renders from the tracked record.

Recorded mutation (the check of this study, #1390): in `s3c_net_missing_1390.walks_of`, the comparison `if d not in walk.forecasts[names[key]]:` was changed to
`if False:`. `WalkTests.test_a_scored_day_without_a_forecast_is_refused` then failed with `AssertionError: ValueError not raised`; restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from unittest import mock
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace

from repo_model import net_settlement as ns
from repo_model import s3c_announced, s3c_net_missing
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_net_missing_1390", ROOT / "scripts" / "s3c_net_missing_1390.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_net_missing_1390"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]
CLOSE = time(18, 0)


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


def noon(d):
    return datetime.combine(d, time(12, 0))


def auction(settles, announced, *, bill, offering=40.0, maturing=25.0, cmb=False):
    return ns.Auction(settles, "Bill" if bill else "Note", bill, offering, maturing, 0.0, noon(announced), None, cmb)


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1390)
        self.assertEqual(script.SEED, 1390)
        self.assertIn("seed 1390", declaration["scoring"]["test"])
        self.assertEqual([r["model"] for r in declaration["arms"]], [script.ANNNET, script.DROP])
        self.assertEqual([r["name"] for r in declaration["references"]], [script.ANNNET, script.S3C, "B1", "B1_prime", "B2"])
        self.assertEqual(declaration["models"], ["B1", "B1_prime", "B2", script.S3C, script.ANNNET, script.DROP])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(len(declaration["amendments"]), 1)
        self.assertIn("keyed `arms`", declaration["amendments"][0])
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertEqual(sorted(declaration["states"]), sorted(
            ["source", "absent", "complete", "missing_maturing", "incomplete", "unannounced", "cmb_pending", "day_level"]))

    def test_the_models_are_the_declared_ones(self):
        self.assertEqual(script.MODELS, ("B1", script.B1P, "B2", script.S3C, script.ANNNET, script.DROP))
        self.assertEqual(s3c_net_missing.DROP_ARM.name.replace("sc_s3_", "sc_s3c_"), script.DROP)

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_net_missing_1390.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_net_missing_1390.json", "scripts/s3c_net_missing_1390.py", "direct"))

    def test_the_effect_terms_are_the_terms_the_arms_fit(self):
        self.assertEqual(script.EFFECT_TERMS[script.DROP], ("settlement_coupon", "settlement_bill", sc.MISSING_FLAG))
        self.assertEqual(s3c_net_missing.DROP_ARM.extra, (sc.MISSING_FLAG,))

    def test_the_plan(self):
        self.assertEqual(script.plan(script.DROP, "pooled"), [script.ANNNET, script.S3C, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.DROP, script.MISSING_SPLIT), [script.ANNNET, script.S3C])
        self.assertEqual(script.plan(script.ANNNET), [])


class CountTests(unittest.TestCase):
    """`count_states` on hand cases. Panel days D0..D9 (business days from 2020-03-02); every call reads the 18:00 instant."""

    def setUp(self):
        self.dates = business_days(date(2020, 3, 2), 12)

    def count(self, auctions):
        return script.count_states(self.dates, auctions, date(2020, 12, 31), CLOSE)

    def test_a_missing_maturing_estimate_is_counted_and_a_complete_day_is_not(self):
        d = self.dates
        auctions = [auction(d[6], d[2], bill=True, maturing=None, cmb=True),  # a CMB alone: no maturing figure
                    auction(d[7], d[3], bill=False)]                          # a coupon with its estimate
        out = self.count(auctions)["2020"]["1"]["day"]
        self.assertEqual(out["settlement_days"], 2)
        self.assertEqual(out["net_rests_on_missing"], 1)
        self.assertEqual(out["of_which_missing_maturing"], 1)
        self.assertEqual(out["complete_nonzero"], 1)

    def test_a_genuine_zero_is_not_missing(self):
        d = self.dates
        out = self.count([auction(d[6], d[2], bill=False, offering=25.0, maturing=25.0)])["2020"]["1"]
        self.assertEqual(out["day"]["genuine_zero"], 1)
        self.assertEqual(out["day"]["net_rests_on_missing"], 0)
        self.assertEqual(out["coupon"]["complete_zero"], 1)

    def test_a_class_announced_in_part_at_a_long_lead_is_not_fully_announced_and_is_complete_at_lead_1(self):
        d = self.dates
        auctions = [auction(d[8], d[2], bill=False), auction(d[8], d[6], bill=False)]  # the second is announced two days before the settlement
        out = self.count(auctions)["2020"]
        self.assertEqual(out["4"]["day"]["of_which_class_not_fully_announced"], 1)
        self.assertEqual(out["4"]["coupon"][ns.INCOMPLETE], 1)
        self.assertEqual(out["1"]["day"]["net_rests_on_missing"], 0)
        self.assertEqual(out["1"]["day"]["complete_nonzero"], 1)

    def test_a_cmb_announced_later_is_counted_in_hindsight_and_is_not_a_state(self):
        d = self.dates
        auctions = [auction(d[8], d[2], bill=True), auction(d[8], d[7], bill=True, maturing=None, cmb=True)]
        out = self.count(auctions)["2020"]
        self.assertEqual(out["3"]["day"]["cmb_pending_days"], 1)
        self.assertEqual(out["3"]["day"]["cmb_pending_and_not_otherwise_missing"], 1)
        self.assertEqual(out["3"]["day"]["net_rests_on_missing"], 0)  # nothing at the instant says it is coming
        self.assertEqual(out["3"]["bill"][ns.COMPLETE], 1)
        self.assertEqual(out["1"]["day"]["cmb_pending_days"], 0)

    def test_the_day_level_categories_exclude_one_another(self):
        d = self.dates
        auctions = [auction(d[6], d[2], bill=True, maturing=None, cmb=True), auction(d[7], d[3], bill=False),
                    auction(d[8], d[2], bill=False, offering=25.0, maturing=25.0), auction(d[9], d[7], bill=True, maturing=None, cmb=True)]
        for lead, per in self.count(auctions)["2020"].items():
            day = per["day"]
            self.assertEqual(day["settlement_days"], day["net_rests_on_missing"] + day["nothing_public"] + day["genuine_zero"] + day["complete_nonzero"], lead)

    def test_a_day_after_the_last_day_and_a_day_without_settlement_are_not_counted(self):
        d = self.dates
        out = script.count_states(d, [auction(d[6], d[2], bill=False)], d[5], CLOSE)
        self.assertEqual(out, {})


class GroupTests(unittest.TestCase):

    def test_the_missing_state_groups_and_the_log_follow_the_decision_instant(self):
        frame = Frame()
        d = frame.dates
        panel = [DailyObservation(x, {}) for x in d]
        target = frame.target(frame.days[0], 2)
        auctions = [auction(target, d[0], bill=True, maturing=None, cmb=True), auction(target, d[1], bill=False)]
        tables = (None, None, None, s3c_net_missing.NetMissingTerms(panel, auctions))
        facts = {x: {"coupon": x == target, "bill": x == target, "cmb": False} for x in d}
        members = script.missing_members(frame, facts, tables, 2)
        self.assertEqual(members[script.STATE_LABELS[0]], [frame.days[0]])
        self.assertIn(frame.days[1], members[script.STATE_LABELS[2]])
        rows = script.forecast_log(frame, tables)
        self.assertEqual(len(rows), len(frame.days) * len(script.LEADS))
        row = next(r for r in rows if r["decision_day"] == frame.days[0].isoformat() and r["lead"] == 2)
        self.assertEqual((row["bill"], row["coupon"], row["missing"]), (ns.MISSING_MATURING, ns.COMPLETE, 1))

    def test_the_added_groups(self):
        frame = Frame()
        panel = [DailyObservation(x, {}) for x in frame.dates]
        tables = (None, None, None, s3c_net_missing.NetMissingTerms(panel, []))
        facts = {x: {"coupon": False, "bill": x.day % 2 == 0, "cmb": False} for x in frame.dates}
        groups = script.extra_groups(frame, facts, tables)
        by = {(g[0], g[1]): g[3] for g in groups}
        self.assertIn((script.DAY_TYPE, f"h=3: {script.m1288.TYPE_LABELS[1]}"), by)
        self.assertIn((script.MISSING_SPLIT, f"h=2: {script.STATE_LABELS[1]}"), by)
        self.assertNotIn((script.MISSING_SPLIT, f"h=2: {script.STATE_LABELS[0]}"), by)  # no auction: nothing rests on a missing figure


class EffectTests(unittest.TestCase):

    def test_the_values_are_the_dropped_net_over_the_unit_and_the_flag(self):
        net_table = SimpleNamespace(read=lambda lead, index: {"settlement_coupon": 10.0, "settlement_bill": 40.0})
        drop_table = SimpleNamespace(read=lambda lead, index: {"settlement_coupon": 10.0, "settlement_bill": 0.0})
        missing = SimpleNamespace(read=lambda lead, index: {sc.MISSING_FLAG: 1.0})
        tables = (None, net_table, drop_table, missing)
        self.assertEqual(script.effect_values(script.ANNNET, 3, 0, tables), {"settlement_coupon": 0.1, "settlement_bill": 0.4})
        self.assertEqual(script.effect_values(script.DROP, 3, 0, tables), {"settlement_coupon": 0.1, "settlement_bill": 0.0, sc.MISSING_FLAG: 1.0})


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
        self.assertEqual(sorted(walks), ["drop", "ref"])
        self.assertEqual(names["drop"], s3c_net_missing.DROP_ARM.name)
        self.assertEqual(tables[2].__class__, s3c_net_missing.DroppedNetSizeTable)
        self.assertEqual(tables[3].__class__, s3c_net_missing.NetMissingTerms)

    def test_a_scored_day_without_a_forecast_is_refused(self):
        # Recorded mutation: see the module docstring (`walks_of`).
        with self.assertRaises(ValueError):
            self.run_walks(drop=s3c_net_missing.DROP_ARM.name)


class ReferenceTests(unittest.TestCase):

    def test_references_that_are_not_1356s_are_refused(self):
        there = json.loads(script.RECORD_1356.read_text(encoding="utf-8"))["windows"]
        window = next(iter(there))
        here = json.loads(json.dumps({window: there[window]}))
        script.against_1356(here)  # the same record agrees
        here[window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"][script.ANNNET] += 1e-6
        with self.assertRaises(ValueError):
            script.against_1356(here)


class DecisionInstantTests(unittest.TestCase):

    def test_the_chain_reads_18_00_inside_the_block_and_16_00_after_it(self):
        # The family's default is 18:00 since #1397; a re-run of an old record sets 16:00, which the block pins to 18:00 and then restores.
        with mock.patch.object(script.s686, "DECISION_TIME", time(16, 0)):
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
        for n in ("1. ", "2. ", "3. "):
            self.assertIn(n, text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`count`, `score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-09-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.counts, cls.output, cls.page, cls.log = base / "counts.json", base / "result.json", base / "page.md", base / "log.csv"
        script.main(["count", "--panel", str(cls.panel_path), "--output", str(cls.counts)])
        script.main(["score", "--panel", str(cls.panel_path), "--counts", str(cls.counts), "--output", str(cls.output), "--log", str(cls.log),
                     "--draws", "20", "--reps", "5", "--workers", "2", "--first", cls.FIRST])
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

    def test_the_reading_is_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["vs"][script.DROP]), sorted(script.plan(script.DROP, "pooled")))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_effect_is_reported_by_lead_for_every_model_and_term(self):
        for w in self.result["windows"].values():
            for model in script.EFFECT_TERMS:
                self.assertEqual(sorted(w["effects"][model]), ["1", "2", "3", "4", "5"])
                for eff in w["effects"][model].values():
                    for term in script.EFFECT_TERMS[model]:
                        self.assertIn("mean", eff["all"][term])

    def test_the_log_has_one_row_per_scored_decision_day_and_lead(self):
        lines = self.log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "window,decision_day,lead,target_day,bill,coupon,missing")
        scored = sum(w["notes"]["scored_decision_days"] for w in self.result["windows"].values())
        self.assertEqual(len(lines) - 1, scored * len(script.LEADS))
        self.assertEqual(self.result["log_rows"], len(lines) - 1)

    def test_the_count_is_in_the_score_file_and_the_page_names_the_states(self):
        self.assertTrue(self.result["counts"]["counts"])
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## Step 1: how many settlement days rest on a missing figure", text)
        self.assertIn("## Question for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-net-missing-1390" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-net-missing-1390-result.md"
    LOG = ROOT / "docs" / "research" / "s3c-net-missing-1390" / "missing_log.csv"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"], record["reps"]), (script.SEED, sp.DRAWS, script.REPS))
        self.assertEqual(record["declaration"], "metadata/s3c_net_missing_1390.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["decision_time"], "18:00")
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
        self.assertTrue(record["against_1356"])
        self.assertEqual(record["counts"]["panel_sha256"], record["panel_sha256"])
        self.assertEqual(len(self.LOG.read_text(encoding="utf-8").splitlines()) - 1, record["log_rows"])

    def test_the_candidate_walk_equals_1356s_record(self):
        # `against_1356` refuses to write a record whose references differ; the tracked record carries its comparison.
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        worst = max(abs(v["difference"]) for ms in record["against_1356"].values() for rows in ms.values() for v in rows.values())
        self.assertLessEqual(worst, 1e-9)


if __name__ == "__main__":
    unittest.main()
