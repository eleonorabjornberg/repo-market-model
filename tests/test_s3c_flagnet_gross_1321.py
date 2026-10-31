"""`scripts/s3c_flagnet_gross_1321.py` (#1321; H5 step 3, development tier): (s3c-ann-flagnet) and (s3c-ann-gross), two arms on avenue #1318 scored
against (s3c-ann-net), (s3c) and (s3c-ann) at the 18:00 decision instant, on both windows of #1255.

Written first, against the declaration. The new read path (`repo_model.s3c_announced.AnnouncedSizeTerms`) and its leakage test are in
`test_s3c_announced_sizes_1321`; #1288's flag and net readers are `test_s3c_announced`'s. What these tests pin: that the declaration names what the
module has (seed, models, arms, references, the last day, no amendment) and that the cleared register row exists; the test plan; the effect
arithmetic on hand cases (a flag effect in bp, a size effect per USD 100 bn, a term out of the fit counted as zero); the settlement shift, premium and
bias arithmetic on a hand case; the refusal to write a walk whose (s3c-ann) is not (s3) at lead 1 or that lacks a scored day; the page (the bill-leg
caveat is named, the marked questions carry numbered options and a default); a small run of `score` and `page` end to end on the fixture panel; and,
once the full run is committed, that the tracked page is what the script renders from the tracked record.

Recorded mutation (the check of this study, #1321): in `s3c_flagnet_gross_1321.walks_of`, the comparison
`if walks["refs"].forecasts[s3c_announced.ANN_ARM.name][d][1] != frame.forecasts[S3][d][1]:` was changed to `if False:`.
`WalkTests.test_an_ann_arm_that_is_not_s3_at_lead_1_is_refused` then failed with `AssertionError` (`ValueError not raised`); restored, it passes.
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

from repo_model import s3c_announced
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_flagnet_gross_1321", ROOT / "scripts" / "s3c_flagnet_gross_1321.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_flagnet_gross_1321"] = script  # the script's worker pool pickles its functions by module name
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
        self.assertEqual(declaration["issue"], 1321)
        self.assertEqual(script.SEED, 1321)
        self.assertIn("seed 1321", declaration["scoring"]["test"])
        self.assertEqual([c["name"] for c in declaration["candidates"]], list(script.ARMS))
        self.assertEqual([c["name"] for c in declaration["references"]], [script.S3C, script.ANN, script.ANNNET])
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3C, script.ANN, script.ANNNET, *script.ARMS])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual(declaration["arms"][-1]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertIn("net x scarcity", declaration["limits"]["not_in_this_directive"].replace("×", "x"))

    def test_the_arms_are_the_modules(self):
        self.assertEqual(s3c_announced.FLAGNET_ARM.name, "sc_s3_ann_flagnet")
        self.assertEqual(s3c_announced.GROSS_ARM.name, "sc_s3_ann_gross")
        for candidate in script.committed_declaration()["candidates"]:
            self.assertIn("repo_model.s3c_announced", candidate["module"])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_flagnet_gross_1321.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]),
                         ("metadata/s3c_flagnet_gross_1321.json", "scripts/s3c_flagnet_gross_1321.py", "direct"))

    def test_the_effect_terms_are_the_terms_the_arms_fit(self):
        self.assertEqual(script.EFFECT_TERMS[script.FLAGNET], ("settlement_coupon", "settlement_bill", sc.NET_COUPON, sc.NET_BILL))
        self.assertEqual(script.EFFECT_TERMS[script.GROSS], (sc.GROSS_COUPON, "settlement_bill"))
        self.assertEqual(set(script.EFFECT_TERMS[script.GROSS]) - set(s3c_announced.GROSS_ARM.location), {sc.GROSS_COUPON})

    def test_the_plan(self):
        for arm in script.ARMS:
            self.assertEqual(script.plan(arm), [script.ANNNET, script.S3C, script.ANN])
        self.assertEqual(script.plan(script.S3C), [])


class EffectTests(unittest.TestCase):

    def walk_of(self, frame, estimate, name="arm"):
        used = frame.dates[0]
        return SimpleNamespace(fit_used={d: used for d in frame.days}, estimates={used: {name: {3: estimate}}},
                               detail={d: {"scale": 5.0} for d in frame.days})

    def test_a_flag_and_a_size_effect_are_in_bp_and_a_term_out_of_the_fit_counts_zero(self):
        frame = Frame()
        frame.days = frame.days[:3]
        est = sc.StateEstimate(("settlement_coupon", sc.NET_COUPON), {"settlement_coupon": 0.02, sc.NET_COUPON: 0.1}, {}, {}, [0.0], 1, 0, 1)
        terms = ("settlement_coupon", "settlement_bill", sc.NET_COUPON)

        def read(lead, index):
            return {"settlement_coupon": 1.0, "settlement_bill": 1.0, sc.NET_COUPON: 0.5}

        out = script.effects(frame, self.walk_of(frame, est), "arm", terms, 3, read, reps=20)["all"]
        self.assertAlmostEqual(out["settlement_coupon"]["mean"], 0.1)  # 0.02 per day x 5 bp scale
        self.assertAlmostEqual(out[sc.NET_COUPON]["mean"], 0.5)  # 0.1 per USD 100 bn x 5 bp
        self.assertEqual(out["settlement_bill"]["mean"], 0.0)
        self.assertEqual(out["settlement_bill"]["share_in_fit"], 0.0)
        self.assertEqual(out["settlement_coupon"]["share_in_fit"], 1.0)
        self.assertEqual(out["active_days"], 3)
        self.assertAlmostEqual(out["mean_abs_shift_bp_on_active_days"], 0.1 + 0.5 * 0.5)

    def test_the_values_of_a_gross_arm_are_a_flag_for_the_bill_and_a_size_for_the_coupon(self):
        flags = {"settlement_bill": 1, "settlement_coupon": 1}
        term_table = SimpleNamespace(read=lambda lead, index: flags)
        size_terms = SimpleNamespace(read=lambda lead, index: {sc.GROSS_COUPON: 0.4, sc.NET_COUPON: 0.1, sc.NET_BILL: -0.2})
        net_table = SimpleNamespace(read=lambda lead, index: {"settlement_coupon": 10.0, "settlement_bill": -20.0})
        self.assertEqual(script.effect_values(script.GROSS, 3, 0, term_table, net_table, size_terms), {sc.GROSS_COUPON: 0.4, "settlement_bill": 1.0})
        self.assertEqual(script.effect_values(script.FLAGNET, 3, 0, term_table, net_table, size_terms),
                         {"settlement_coupon": 1.0, "settlement_bill": 1.0, sc.NET_COUPON: 0.1, sc.NET_BILL: -0.2})
        self.assertEqual(script.effect_values(script.ANNNET, 3, 0, term_table, net_table, size_terms),
                         {"settlement_coupon": 0.1, "settlement_bill": -0.2})
        self.assertEqual(script.effect_values(script.ANN, 3, 0, term_table, net_table, size_terms), {"settlement_coupon": 1.0, "settlement_bill": 1.0})


class ShiftTests(unittest.TestCase):

    def cells(self):
        # Two decision days, one lead each; day 1 settles (spread 8, medians 5), day 2 does not (spread 2, medians 3).
        base = {"regime": "2025-26", "h": 3}
        mk = lambda d, y, settle, med, shift: dict(base, d=d, y=y, settle=settle, med={m: med for m in script.MODELS}, shift={a: shift for a in script.SHIFT_ARMS})
        return [mk(date(2025, 12, 1), 8.0, True, 5.0, 1.5), mk(date(2025, 12, 2), 2.0, False, 3.0, 0.0)]

    def test_the_premium_the_shift_and_the_bias(self):
        units = script.bias_units(self.cells(), [3])
        totals = script._sum_units(units, range(len(units)))
        names = [("all", script.S3C, "premium"), ("all", script.ANN, "shift"), ("all", script.ANN, "bias"), ("2025-26", script.ANNNET, "shift")]
        premium, shift, bias, shift2 = script.bias_statistics(totals, names)
        self.assertAlmostEqual(premium, 8.0 - 2.0)
        self.assertAlmostEqual(shift, 1.5)
        self.assertAlmostEqual(bias, (8.0 - 5.0) - (2.0 - 3.0))
        self.assertAlmostEqual(shift2, 1.5)

    def test_a_resample_without_a_settlement_day_reads_zero_not_an_error(self):
        units = script.bias_units(self.cells(), [3])
        totals = script._sum_units(units, [1])
        self.assertEqual(script.bias_statistics(totals, [("all", script.ANN, "shift")]), [0.0])

    def test_only_the_asked_leads_count(self):
        self.assertEqual(script.bias_units(self.cells(), [1]), [])


class WalkTests(unittest.TestCase):

    def run_walks(self, ann_at_one, drop=None):
        frame = Frame()
        frame.forecasts = {script.S3: {d: {h: list(Q) for h in sp.HORIZONS} for d in frame.days}}

        def make(at_one):
            return {d: {h: (list(at_one) if h == 1 else [q + 1.0 for q in Q]) for h in sp.HORIZONS} for d in frame.days}

        def fake_walk(panel, days, table, states, arms, **kw):
            forecasts = {a.name: make(ann_at_one if a.name == s3c_announced.ANN_ARM.name else Q) for a in arms}
            if drop is not None and drop in forecasts:
                forecasts[drop].pop(frame.days[0])
            return SimpleNamespace(forecasts=forecasts, fits={})

        original = script.sc.walk, script.m1288.candidate_days
        script.sc.walk, script.m1288.candidate_days = fake_walk, lambda *a, **kw: list(frame.days)
        try:
            panel = [DailyObservation(d, {}) for d in frame.dates]
            return script.walks_of("development", frame, panel, None, {}, None, [], [], None)
        finally:
            script.sc.walk, script.m1288.candidate_days = original

    def test_walks_that_agree_with_the_frame_at_lead_1_are_accepted(self):
        walks, term_table, net_table, size_terms = self.run_walks(list(Q))
        self.assertEqual(sorted(walks), ["new", "refs"])
        self.assertIs(size_terms.terms, term_table)
        self.assertIs(size_terms.net, net_table)

    def test_an_ann_arm_that_is_not_s3_at_lead_1_is_refused(self):
        # Recorded mutation: see the module docstring (`walks_of`, the lead-1 comparison).
        with self.assertRaises(ValueError):
            self.run_walks([q + 0.5 for q in Q])

    def test_a_scored_day_without_a_forecast_is_refused(self):
        with self.assertRaises(ValueError):
            self.run_walks(list(Q), drop=s3c_announced.FLAGNET_ARM.name)


class DecisionInstantTests(unittest.TestCase):
    """The study modules of #1115 to #1288 type 16:00; this study runs them at the declared instant and puts them back.

    Recorded mutation (#1321): in `decision_instant_pinned`, `module.DECISION_TIME = DECISION_TIME` was changed to
    `module.DECISION_TIME = LEGACY_DECISION_TIME` (the pin that pins nothing). All three tests then failed with `ValueError` (`k.DECISION_TIME is
    16:00:00, not the declared instant 18:00:00`, the guard on entry to the block); restored, they pass. The first full run of this study was made
    without the pin, so at 16:00 (it reproduced #1288's pooled means exactly, which is how the miss was seen); it was discarded and re-run.
    """

    def test_the_chain_reads_18_00_inside_the_block(self):
        from datetime import time

        with script.decision_instant_pinned() as instant:
            self.assertEqual(instant, time(18, 0))
            for module in (script.k, script.c, script.s686, script.m1255.d1222):
                self.assertEqual(module.DECISION_TIME, time(18, 0), module.__name__)

    def test_the_legacy_instant_is_back_after_the_block(self):
        from datetime import time

        with script.decision_instant_pinned():
            pass
        for module in (script.k, script.c, script.s686, script.m1255.d1222):
            self.assertEqual(module.DECISION_TIME, time(16, 0), module.__name__)

    def test_a_block_that_fails_still_puts_it_back(self):
        from datetime import time

        with self.assertRaises(RuntimeError), script.decision_instant_pinned():
            raise RuntimeError("inside")
        self.assertEqual(script.s686.DECISION_TIME, time(16, 0))


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        for number in (1, 2):
            self.assertIn(f"**Question {number}.", text)
        self.assertEqual(text.count("(default)"), 2)
        self.assertIn("1. ", text)
        self.assertIn("2. ", text)
        self.assertNotIn("GO #", text)


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

    def test_the_arms_are_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            for candidate in script.ARMS:
                self.assertEqual(sorted(cell["vs"][candidate]), sorted(script.plan(candidate)))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_references_equal_s3c_at_lead_1_for_the_flag_arm(self):
        for w in self.result["windows"].values():
            self.assertEqual(w["lead_difference"]["ann_against_s3c"]["differing_cells"]["1"], 0)
            self.assertEqual(w["announcement_check"]["lead_1_differences"], 0, w["announcement_check"])

    def test_the_shift_against_premium_is_reported_by_regime_for_both_lead_sets(self):
        for w in self.result["windows"].values():
            for key, leads in (("later", [2, 3, 4, 5]), ("lead1", [1])):
                block = w["shift_against_premium"][key]
                self.assertEqual(block["leads"], leads)
                self.assertEqual(block["regimes"][0], "all")
                for regime in block["regimes"]:
                    entry = block["by_regime"][regime]
                    self.assertIn("value", entry["premium"])
                    for arm in script.SHIFT_ARMS:
                        self.assertIn("value", entry[arm]["shift"])
                        self.assertIn("value", entry[arm]["bias"])
                    self.assertIn("value", entry[script.S3C]["bias"])

    def test_the_effect_is_reported_by_lead_for_every_arm_and_term(self):
        for w in self.result["windows"].values():
            for arm in script.SHIFT_ARMS:
                self.assertEqual(sorted(w["effects"][arm]), ["1", "2", "3", "4", "5"])
                for eff in w["effects"][arm].values():
                    for term in script.EFFECT_TERMS[arm]:
                        self.assertIn("mean", eff["all"][term])

    def test_the_settlement_day_types_are_split_by_lead(self):
        for w in self.result["windows"].values():
            labels = w["groups"][script.DAY_TYPE]
            for lead in (1, 2, 3, 4, 5):
                self.assertIn(f"h={lead}: {script.TYPE_LABELS[0]}", labels)

    def test_the_page_names_the_bill_caveat_the_arms_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## Summary: grid CRPS against (s3c-ann-net), by lead", text)
        self.assertIn("Lens E", text)
        self.assertIn("(s3c-ann-flagnet)", text)
        self.assertIn("(s3c-ann-gross)", text)
        self.assertIn("realised settlement-day premium", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-flagnet-gross-1321" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-flagnet-gross-1321-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"], record["reps"]), (script.SEED, sp.DRAWS, script.REPS))
        self.assertEqual(record["declaration"], "metadata/s3c_flagnet_gross_1321.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["decision_time"], "18:00")
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertEqual(w["announcement_check"]["lead_1_differences"], 0)
            self.assertEqual(w["lead_difference"]["ann_against_s3c"]["differing_cells"]["1"], 0)


if __name__ == "__main__":
    unittest.main()
