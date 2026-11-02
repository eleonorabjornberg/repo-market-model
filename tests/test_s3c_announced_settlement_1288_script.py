"""`scripts/s3c_announced_settlement_1288.py` (#1288; H5 step 3, development tier): (s3c-ann) and (s3c-ann-net), (s3c) with its settlement terms read at
leads 2 to 5 from the auction announcement, scored against (s3c), (s3), (s3c-net), B1, B1' and B2 on both windows of #1255.

Written first, against the declaration. The new read paths (`repo_model.s3c_announced`) and their leakage tests are in `test_s3c_announced`; the cap, the
line and the full-allotment flag are (s3c)'s (`test_s3c_candidate`); the (s3c-net) reader is #1273's (`test_s3c_net`). What these tests pin: that the
declaration names what the module has (seed, models, arms, legs, the last day, no amendment) and that the cleared register row exists; the test plan
(narrower on the announced-term splits); the settlement-day types of a target (coupon, bill, with and without a cash management
bill, neither); the announced-term day split; the announcement check (the announced gross against the panel's at lead 1, and the share of settlement
days announced by lead); the per-lead effect arithmetic on a hand case; the refusal to walk a day whose (s3) differs from #1255's frame, and the
refusal of an arm that is not (s3) (or (s3c-net)) at lead 1; the page (the bill-leg caveat is named, the marked questions carry numbered options and
a default); a small run of `score` and `page` end to end on the fixture panel; and, once the full run is committed, that the tracked page is what the
script renders from the tracked record and that #1255's and #1273's pooled means are reproduced.

Recorded mutation (the check of this study, #1288): in `s3c_announced_settlement_1288.extra_walks`, the comparison
`if walks[name].forecasts[arms[name]][d][1] != at_one:` was changed to `if False:`. `ExtraWalkTests.test_an_arm_that_is_not_s3_at_lead_1_is_refused` then
failed with `AssertionError` (`ValueError not raised`); restored, it passes. Second mutation (the settlement-day type): in `settlement_facts`,
`float(row.values.get("treasury_settlement_bills") or 0.0) > 0.0` was replaced by `... >= 0.0` (every day a bill day);
`SettlementTypeTests.test_the_types_of_a_target_day` then failed with `AssertionError`.
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
from repo_model import s3c_announced, s3c_net
from repo_model import scoring_protocol as sp
from repo_model import settlement_dating as sd
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_announced_settlement_1288", ROOT / "scripts" / "s3c_announced_settlement_1288.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_announced_settlement_1288"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

Q = [float(x) for x in range(-2, 21)]  # 23 ordered values, from -2 to 20 bp
NOON = time(12, 0)


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class Frame:
    """The few members of the scoring frame the checks read."""

    def __init__(self, n=26):
        self.dates = business_days(date(2025, 12, 1), n)
        self.days = [d for d in self.dates if date(2025, 12, 8) <= d <= date(2025, 12, 17)]
        self.outcome = {d: 5.0 for d in self.dates}
        self.position = {d: i for i, d in enumerate(self.dates)}

    def target(self, d, h):
        return self.dates[self.position[d] + h]

    def regime(self, d):
        return "2025-26"


def panel_of(frame, coupon_on=(), bill_on=()):
    return [
        DailyObservation(d, {
            "treasury_settlement_coupons": 40.0 if d in coupon_on else 0.0,
            "treasury_settlement_bills": 60.0 if d in bill_on else 0.0,
        })
        for d in frame.dates
    ]


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1288)
        self.assertEqual(script.SEED, 1288)
        self.assertIn("seed 1288", declaration["scoring"]["test"])
        self.assertEqual([c["name"] for c in declaration["candidates"]], list(script.ARMS))
        self.assertEqual([c["name"] for c in declaration["references"]], [script.S3CN, script.ANNC, script.ANNB])
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3, script.S3C, script.S3CN, *script.ARMS, *script.LEGS])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(len(declaration["amendments"]), 1)
        self.assertIn("before the declared run", declaration["amendments"][0])
        self.assertEqual(declaration["arms"][1]["margin_bp"], script.s3c_candidate.MARGIN_BP)

    def test_the_arms_are_the_modules(self):
        self.assertEqual(s3c_announced.ANN_ARM.name, "sc_s3_ann")
        self.assertEqual(s3c_announced.ANN_NET_ARM.name, "sc_s3_ann_net")
        for candidate in script.committed_declaration()["candidates"]:
            self.assertIn("repo_model.s3c_announced", candidate["module"])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_announced_settlement_1288.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_announced_settlement_1288.json", "scripts/s3c_announced_settlement_1288.py", "direct"))

    def test_the_dating_is_the_declaration_in_the_tree_and_is_not_changed_here(self):
        declaration = script.committed_declaration()
        self.assertIn("metadata/settlement_announcement_dating.json", declaration["dating"]["declaration"])
        self.assertEqual(json.loads(script.DATING.read_text(encoding="utf-8"))["available_time"], "12:00")
        self.assertIn("unverified", declaration["dating"]["bill_caveat"])

    def test_the_plan(self):
        full = [script.S3C, script.S3, script.S3CN, "B1", script.B1P, "B2"]
        self.assertEqual(script.plan(script.ANN), full)
        self.assertEqual(script.plan(script.ANNNET), [script.S3C, script.S3, script.S3CN, script.ANN, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.ANN, script.DAY_TYPE), full)
        self.assertEqual(script.plan(script.ANN, script.ANNOUNCED), [script.S3C, script.S3CN])
        self.assertEqual(script.plan(script.ANNNET, script.ANNOUNCED_NET), [script.S3C, script.S3CN, script.ANN])
        for leg in script.LEGS:
            self.assertEqual(script.plan(leg), [script.S3C])
        self.assertEqual(script.plan(script.S3), [])


class SettlementTypeTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()
        d = self.frame.dates
        # d[10]: coupon only; d[11]: bill only; d[12]: bill with a cash management bill, and a coupon; d[13]: nothing.
        self.panel = panel_of(self.frame, coupon_on={d[10], d[12]}, bill_on={d[11], d[12]})
        self.auctions = [ns.Auction(d[12], "CMB", True, 30.0, 0.0, 0.0, datetime.combine(d[11], NOON), None, True)]
        self.facts = script.settlement_facts(self.panel, self.auctions)

    def test_the_types_of_a_target_day(self):
        d = self.frame.dates
        self.assertEqual(self.facts[d[10]], {"coupon": True, "bill": False, "cmb": False})
        self.assertEqual(self.facts[d[11]], {"coupon": False, "bill": True, "cmb": False})
        self.assertEqual(self.facts[d[12]], {"coupon": True, "bill": True, "cmb": True})
        self.assertEqual(self.facts[d[13]], {"coupon": False, "bill": False, "cmb": False})

    def test_the_decision_days_by_type_at_a_lead(self):
        d = self.frame.dates
        members = script.day_type_members(self.frame, self.facts, 2)
        # the decision day is two rows before the target
        self.assertEqual(members[script.TYPE_LABELS[0]], [d[8], d[10]])
        self.assertEqual(members[script.TYPE_LABELS[1]], [d[9], d[10]])
        self.assertEqual(members[script.TYPE_LABELS[2]], [d[10]])
        self.assertEqual(members[script.TYPE_LABELS[3]], [d[9]])
        self.assertIn(d[11], members[script.TYPE_LABELS[4]])
        self.assertNotIn(d[8], members[script.TYPE_LABELS[4]])


class AnnouncementCheckTests(unittest.TestCase):

    def setUp(self):
        self.frame = Frame()
        d = self.frame.dates
        self.target = d[12]
        self.panel = panel_of(self.frame, coupon_on={self.target})
        self.records = [{
            "announcemt_date": d[9].isoformat(), "auction_date": d[9].isoformat(), "issue_date": self.target.isoformat(),
            "security_type": "Note", "offering_amt": "40000000000", "total_accepted": "null", "closing_time_comp": "01:00 PM",
        }]
        self.results = sd.auction_results(self.records, sd.load_result_dating(script.DATING))
        self.term_table = s3c_announced.AnnouncedTermTable(self.panel, [], self.results, [], decision_time=time(16, 0))
        self.net_table = s3c_announced.AnnouncedNetSizeTable(self.panel, [], decision_time=time(16, 0))
        self.facts = script.settlement_facts(self.panel, [])

    def test_the_announced_gross_agrees_with_the_panel_at_lead_1(self):
        check = script.announcement_check(self.frame, self.panel, self.results, self.facts, self.term_table, self.net_table)
        self.assertEqual(check["lead_1_differences"], 0)
        self.panel[self.frame.position[self.target]].values["treasury_settlement_coupons"] = 10.0
        check = script.announcement_check(self.frame, self.panel, self.results, self.facts, self.term_table, self.net_table)
        self.assertEqual(check["lead_1_differences"], 1)

    def test_the_coverage_counts_the_settlement_days_announced_by_lead(self):
        check = script.announcement_check(self.frame, self.panel, self.results, self.facts, self.term_table, self.net_table)
        # announced on d[9] at 12:00: public from the 16:00 decision of d[9]; the target d[12] is lead 3 from d[9]
        cov = check["coverage"]
        self.assertEqual({h: cov[str(h)]["coupon_days"] for h in sp.HORIZONS}, {1: 1, 2: 1, 3: 1, 4: 1, 5: 1})
        self.assertEqual({h: cov[str(h)]["coupon_announced"] for h in sp.HORIZONS}, {1: 1, 2: 1, 3: 1, 4: 0, 5: 0})

    def test_the_announced_term_days_split_by_lead(self):
        (flagged, plain), (net_on, net_off) = script.announced_members(self.frame, self.term_table, self.net_table, 3)
        self.assertEqual(flagged, [self.frame.dates[9]])
        self.assertEqual(sorted(flagged + plain), sorted(self.frame.days))
        self.assertEqual(net_on, [])  # no net auction on file
        self.assertEqual(sorted(net_off), sorted(self.frame.days))


class EffectTests(unittest.TestCase):

    def test_the_effect_is_in_bp_at_the_lead_and_a_day_without_the_term_counts_zero(self):
        frame = Frame()
        frame.days = frame.days[:3]
        used = frame.dates[0]
        with_term = sc.StateEstimate(("settlement_bill",), {"settlement_bill": 0.02}, {}, {}, [0.0], 1, 0, 1, True)
        without = sc.StateEstimate((), {}, {}, {}, [0.0], 1, 0, 1, True)
        walk = SimpleNamespace(
            fit_used={d: used for d in frame.days},
            estimates={used: {"arm": {3: with_term}, "arm2": {3: without}}},
            detail={d: {"scale": 5.0} for d in frame.days},
        )
        target = frame.target(frame.days[0], 3)

        def read(lead, index):
            return {"settlement_bill": 1.0 if frame.dates[index + lead] == target else 0.0, "settlement_coupon": 0.0}

        out = script.effects(frame, walk, SimpleNamespace(name="arm"), 3, read)
        self.assertAlmostEqual(out["all"]["settlement_bill"]["mean"], 0.1)  # 0.02 per unit x 5 bp scale
        self.assertEqual(out["all"]["settlement_bill"]["share_in_fit"], 1.0)
        self.assertEqual(out["all"]["active_days"], 1)
        self.assertAlmostEqual(out["all"]["mean_abs_shift_bp_on_active_days"], 0.1)
        none = script.effects(frame, walk, SimpleNamespace(name="arm2"), 3, read)
        self.assertEqual(none["all"]["settlement_bill"]["mean"], 0.0)
        self.assertEqual(none["all"]["settlement_bill"]["share_in_fit"], 0.0)

    def test_a_net_is_read_per_100_bn(self):
        frame = Frame()
        frame.days = frame.days[:2]
        used = frame.dates[0]
        est = sc.StateEstimate(("settlement_coupon",), {"settlement_coupon": 0.02}, {}, {}, [0.0], 1, 0, 1, True)
        walk = SimpleNamespace(fit_used={d: used for d in frame.days}, estimates={used: {"arm": {2: est}}},
                               detail={d: {"scale": 5.0} for d in frame.days})
        out = script.effects(frame, walk, SimpleNamespace(name="arm"), 2, lambda lead, i: {"settlement_coupon": 200.0}, unit=100.0)
        self.assertAlmostEqual(out["all"]["mean_abs_shift_bp_on_active_days"], 0.2)  # 2.0 x 100 bn x 0.1 bp per 100 bn


class ExtraWalkTests(unittest.TestCase):

    def run_extra(self, ann_at_one, net_at_one=None, s3_shift=0.0):
        frame = Frame()
        frame.forecasts = {script.S3: {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}}

        def make(per_lead_one):
            return {d: {h: (list(per_lead_one) if h == 1 else [q + 1.0 for q in Q]) for h in sp.HORIZONS} for d in frame.days}

        def fake_walk(panel, days, table, states, arms, **kw):
            names = [a.name for a in arms]
            forecasts = {}
            for name in names:
                if name == s3c_net.NET_ARM.name:
                    forecasts[name] = make(Q)
                elif name == s3c_announced.ANN_NET_ARM.name:
                    forecasts[name] = make(Q if net_at_one is None else net_at_one)
                else:
                    forecasts[name] = make(ann_at_one)
            forecasts[script.S3] = {d: {h: [q + s3_shift for q in Q] for h in sp.HORIZONS} for d in frame.days}
            return SimpleNamespace(forecasts=forecasts, fits={})

        original = script.sc.walk, script.candidate_days
        script.sc.walk, script.candidate_days = fake_walk, lambda *a, **kw: list(frame.days)
        try:
            panel = [DailyObservation(d, {}) for d in frame.dates]
            return script.extra_walks("development", frame, panel, None, {}, None, [], [], None)
        finally:
            script.sc.walk, script.candidate_days = original

    def test_walks_that_agree_with_the_frame_at_lead_1_are_accepted(self):
        walks, _term, _net = self.run_extra(list(Q))
        self.assertEqual(sorted(walks), ["ann", "bill", "coupon", "net"])

    def test_a_walk_that_is_not_1255s_is_refused(self):
        with self.assertRaises(ValueError):
            self.run_extra(list(Q), s3_shift=1.0)

    def test_an_arm_that_is_not_s3_at_lead_1_is_refused(self):
        # Recorded mutation: see the module docstring (`extra_walks`, the lead-1 comparison).
        with self.assertRaises(ValueError):
            self.run_extra([q + 0.5 for q in Q])

    def test_the_net_arm_that_is_not_s3c_net_at_lead_1_is_refused(self):
        with self.assertRaises(ValueError):
            self.run_extra(list(Q), net_at_one=[q + 0.5 for q in Q])


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        for number in (1, 2, 3):
            self.assertIn(f"**Question {number}.", text)
        self.assertEqual(text.count("(default)"), 3)
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

    def test_the_arms_are_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            for candidate in script.ARMS + script.LEGS:
                self.assertEqual(sorted(cell["vs"][candidate]), sorted(script.plan(candidate)))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_arms_differ_from_s3c_at_leads_2_to_5_and_equal_it_at_lead_1(self):
        for w in self.result["windows"].values():
            diff = w["lead_difference"]["ann_against_s3c"]["differing_cells"]
            self.assertEqual(diff["1"], 0)
            for h in ("2", "3", "4", "5"):
                self.assertGreater(diff[h], 0, h)
            net = w["lead_difference"]["ann_net_against_s3c_net"]["differing_cells"]
            self.assertEqual(net["1"], 0)

    def test_the_announced_gross_is_the_panels_at_lead_1(self):
        for w in self.result["windows"].values():
            self.assertEqual(w["announcement_check"]["lead_1_differences"], 0, w["announcement_check"])

    def test_every_settlement_day_is_announced_at_lead_1_and_fewer_later(self):
        for w in self.result["windows"].values():
            cov = w["announcement_check"]["coverage"]
            self.assertEqual(cov["1"]["coupon_announced"], cov["1"]["coupon_days"])
            self.assertEqual(cov["1"]["bill_announced"], cov["1"]["bill_days"])
            self.assertLessEqual(cov["5"]["bill_announced"], cov["1"]["bill_announced"] + cov["5"]["bill_days"])

    def test_the_effect_is_reported_by_lead_and_regime_for_both_terms(self):
        for w in self.result["windows"].values():
            for arm in ("ann", "ann_net"):
                self.assertEqual(sorted(w["effects"][arm]), ["1", "2", "3", "4", "5"])
                for lead, eff in w["effects"][arm].items():
                    self.assertIn("all", eff)
                    for term in script.TERMS:
                        self.assertIn("mean", eff["all"][term])
            for leg in ("coupon_leg", "bill_leg"):
                self.assertEqual(sorted(w["effects"][leg]), ["2", "3", "4", "5"])

    def test_the_settlement_day_types_and_announced_terms_are_split_by_lead(self):
        for w in self.result["windows"].values():
            labels = w["groups"][script.DAY_TYPE]
            for lead in (2, 3, 4, 5):
                self.assertIn(f"h={lead}: {script.TYPE_LABELS[0]}", labels)
                self.assertIn(f"h={lead}: {script.TYPE_LABELS[4]}", labels)
            self.assertEqual(sorted(w["announced_days"]), ["2", "3", "4", "5"])

    def test_the_page_names_the_bill_caveat_the_legs_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## Summary: grid CRPS against (s3c), by lead", text)
        self.assertIn("Lens E", text)
        self.assertIn("cash management bill", text)
        self.assertIn("(s3c-ann-coupon)", text)
        self.assertIn("(s3c-ann-bill)", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-announced-settlement-1288" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-announced-settlement-1288-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_announced_settlement_1288.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertEqual(w["announcement_check"]["lead_1_differences"], 0)

    def test_s3_s3c_and_s3c_net_are_reproduced_from_1255_and_1273(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(sorted(record["against_records"]), ["1255", "1273"])
        for windows in record["against_records"].values():
            for rec in windows.values():
                for rows in rec["metrics"].values():
                    for v in rows.values():
                        self.assertLess(abs(v["difference"]), 1e-9)


if __name__ == "__main__":
    unittest.main()
