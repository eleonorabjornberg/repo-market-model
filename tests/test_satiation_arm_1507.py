"""`scripts/satiation_arm_1507.py` (#1507; H5 step 2 follow-up, milestone H5.M3, development tier): the satiation-distance arm of the family ablation.

Written first, against the declaration `metadata/satiation_arm_1507.json` (a dated amendment of `metadata/family_ablation_1483.json`, which is not edited).
What these tests pin: that the declaration names what the module has (seed, models, arms, rows, the last day, the 18:00 instant, no later amendment) and
that it amends #1483's declaration without editing it; that each new arm is the candidate with exactly one change, its `extra` term (the Huber fit, the ridge,
the settlement terms and the direct pairs are the candidate's, so a row is the term and nothing else); the plan of paired tests; the refusal to walk at another
instant and the refusal of rows that are not the panel's days; the refusal of a scratch panel whose dates or published columns differ; a small run of
`prechecks`, `score`, `assemble` and `page` end to end on the fixture panel; that #1483's page, given #1507's record, measures the satiation row and carries
the dated correction and the corrected question 2, and is what the script renders from the tracked records; and that `docs/research/milestones.json` is not
touched (she is asked, not told).

The columns' own no-look-ahead guard (`satiation.check_distance_no_future`) is #598's, with its recorded mutations in `tests/test_satiation_distance.py`; the
table that serves them is `repo_model.s3c_satiation`, with its mutation in `tests/test_s3c_satiation.py`.

Recorded mutations (7 November 2026). In `satiation_arm_1507.walks_of`, the guard `if k.DECISION_TIME != DECISION_TIME:` was changed to `if False:`.
`WalkTests.test_a_walk_not_at_the_declared_instant_is_refused` then errored with `AttributeError: 'NoneType' object has no attribute 'dates'` (the guard
gone, the call went on and met the `None` frame; `ValueError` was not raised); restored, it passes. Second, in the same function, the guard `if [r.date for r in built] != [r.date for r in panel]:` was changed to `if False:`;
`WalkTests.test_rows_that_are_not_the_panels_days_are_refused` then errored with the same `AttributeError`; restored, it passes. Third, in
`aug_rows`, `if a.values[name] != value` replaced by `if False`: `ScratchPanelTests.test_a_published_column_that_differs_is_refused` failed with
`AssertionError: ValueError not raised`; restored, it passes.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, time, timedelta
from unittest import mock
from pathlib import Path

from repo_model import s3c_announced
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("satiation_arm_1507", ROOT / "scripts" / "satiation_arm_1507.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["satiation_arm_1507"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)
fa = script.fa

BASE = s3c_announced.ANN_NET_ARM


def declaration() -> dict:
    return json.loads((ROOT / "metadata" / "satiation_arm_1507.json").read_text(encoding="utf-8"))


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        d = declaration()
        self.assertEqual(d["issue"], 1507)
        self.assertEqual(script.SEED, 1483)
        self.assertIn("seed 1483", d["scoring"]["test"])
        self.assertEqual(d["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in d["arms"]], [script.ANNNET] + [script.model_of(a) for a in script.WALK_ARMS[1:]])
        self.assertEqual([(r["key"], r["with"], r["without"]) for r in d["rows"]], [(k, w, o) for k, _f, w, o in script.ROWS])
        self.assertEqual(d["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(d["amendments"], [])
        self.assertIn("18:00", d["decision_instant"])

    def test_it_amends_the_ablations_declaration_without_editing_it(self):
        d = declaration()
        self.assertEqual(d["amends"], "metadata/family_ablation_1483.json")
        old = json.loads((ROOT / "metadata" / "family_ablation_1483.json").read_text(encoding="utf-8"))
        self.assertEqual(len(old["amendments"]), 1)  # #1483's own, a corrected sentence; none was added for this arm
        self.assertEqual([r["key"] for r in old["rows"]], [k for k in fa.ROW_KEYS])
        self.assertEqual([f["family"] for f in old["families"] if f["family"] == "satiation distance"], ["satiation distance"])
        self.assertEqual(d["family"]["family"], "satiation distance")
        self.assertIn("7 November 2026", d["amendment_date"])

    def test_the_register_row_is_cleared_and_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "satiation_arm_1507.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/satiation_arm_1507.json")
        self.assertEqual(row["script"], "scripts/satiation_arm_1507.py")
        self.assertEqual(row["pairing"], "direct")

    def test_the_milestone_is_not_re_marked_by_this_change(self):
        marks = json.loads((ROOT / "docs" / "research" / "milestones.json").read_text(encoding="utf-8"))["milestones"]
        caveat = marks["H5.M3"]["caveat"]
        # #1518 rewrote the caveat on her ruling; #1507 left it alone. The old "has no row" sentence is false after #1507.
        self.assertNotIn("Satiation distance has no row", caveat)
        self.assertIn("Satiation distance is measured (#1507", caveat)
        self.assertIn("2025-26", caveat)
        self.assertIn("2021-23", caveat)


class ArmTests(unittest.TestCase):

    def only_differs_in(self, arm, *fields):
        for f in dataclasses.fields(BASE):
            if f.name in ("name", "role") + fields:
                continue
            self.assertEqual(getattr(arm, f.name), getattr(BASE, f.name), f.name)

    def test_the_distance_arm_adds_the_distance_term_and_nothing_else(self):
        self.assertEqual(script.DIST_ARM.extra, (sc.SATIATION_DIST,))
        self.only_differs_in(script.DIST_ARM, "extra")

    def test_the_hinge_arm_adds_the_hinge_term_and_nothing_else(self):
        self.assertEqual(script.HINGE_ARM.extra, (sc.SATIATION_HINGE,))
        self.only_differs_in(script.HINGE_ARM, "extra")

    def test_the_candidate_is_the_ablations_candidate_and_reads_no_extra_term(self):
        self.assertIs(script.WALK_ARMS[0], s3c_announced.ANN_NET_ARM)
        self.assertEqual(script.WALK_ARMS[0].extra, ())

    def test_the_arms_are_distinct_models_with_the_cap_letter(self):
        self.assertEqual(script.DIST, "sc_s3c_ann_net_satdist")
        self.assertEqual(script.HINGE, "sc_s3c_ann_net_sathinge")
        self.assertEqual(len(set(script.MODELS)), len(script.MODELS))

    def test_a_row_is_the_candidate_with_the_term_against_the_candidate(self):
        for _key, _family, with_, without in script.ROWS:
            self.assertEqual(without, script.ANNNET)
            self.assertIn(with_, script.ARMS)
        self.assertEqual(script.plan(script.DIST), [script.ANNNET])
        self.assertEqual(script.plan(script.HINGE), [script.ANNNET])
        self.assertEqual(script.plan(script.ANNNET), [])
        self.assertEqual(set(script.CANDIDATES), set(script.ARMS))


def panel_rows(n=5):
    day, out = date(2026, 3, 2), []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(DailyObservation(day, {"sofr": 3.0 + len(out)}))
        day += timedelta(days=1)
    return out


class WalkTests(unittest.TestCase):

    def test_a_walk_not_at_the_declared_instant_is_refused(self):
        held = script.k.DECISION_TIME
        script.k.DECISION_TIME = time(16, 0)
        try:
            with self.assertRaises(ValueError):
                script.walks_of("development", None, [], [], None, None, None, None, None)
        finally:
            script.k.DECISION_TIME = held

    def test_rows_that_are_not_the_panels_days_are_refused(self):
        panel = panel_rows()
        shifted = panel_rows()[1:]
        self.assertEqual(script.k.DECISION_TIME, script.DECISION_TIME)
        with self.assertRaises(ValueError):
            script.walks_of("development", None, panel, shifted, None, None, None, None, None)


class ScratchPanelTests(unittest.TestCase):

    def read(self, scratch, panel):
        with mock.patch.object(script, "load_daily_panel", lambda _path: scratch):
            return script.aug_rows(Path("aug.csv"), panel)

    def test_a_scratch_panel_with_the_published_days_and_values_is_read(self):
        panel = panel_rows()
        self.assertEqual([r.date for r in self.read(panel_rows(), panel)], [r.date for r in panel])

    def test_a_scratch_panel_may_carry_columns_the_published_one_does_not(self):
        panel = panel_rows()
        wider = [DailyObservation(r.date, dict(r.values, bank_total_assets=1.0)) for r in panel]
        self.assertEqual(len(self.read(wider, panel)), len(panel))

    def test_a_scratch_panel_with_other_days_is_refused(self):
        panel = panel_rows()
        with self.assertRaises(ValueError):
            self.read(panel_rows()[:-1], panel)

    def test_a_published_column_that_differs_is_refused(self):
        panel = panel_rows()
        other = [DailyObservation(r.date, {"sofr": r.values["sofr"] + (1.0 if i == 2 else 0.0)}) for i, r in enumerate(panel)]
        with self.assertRaises(ValueError):
            self.read(other, panel)


class EndToEndTests(unittest.TestCase):
    """`prechecks`, `score`, `assemble` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-09-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        pv = importlib.util.spec_from_file_location("pressure_v1_1_in_1507", ROOT / "scripts" / "pressure_v1_1.py")
        module = importlib.util.module_from_spec(pv)
        sys.modules["pressure_v1_1_in_1507"] = module
        pv.loader.exec_module(module)
        cls.aug = base / "AUG.csv"
        module.main(["panel", "--output", str(cls.aug), "--end", "2026-09-03"])
        script.main(["prechecks", "--aug-panel", str(cls.aug), "--output", str(base / "prechecks.json"), "--check-every", "400"])
        for window in script.WINDOWS:
            script.main(["score", "--panel", str(cls.panel_path), "--aug-panel", str(cls.aug), "--window", window,
                         "--output", str(base / f"result-{window}.json"), "--draws", "20", "--reps", "5", "--workers", "2",
                         "--first", cls.FIRST, "--check-every", "400"])
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["assemble", "--input-dir", str(base), "--output", str(cls.output)])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))
        old = json.loads((ROOT / "docs" / "research" / "family-ablation-1483" / "result.json").read_text(encoding="utf-8"))
        cls.ablation = base / "ablation.md"
        fa.page(type("A", (), {"score": str(ROOT / "docs/research/family-ablation-1483/result.json"), "satiation": str(cls.output), "output": str(cls.ablation)})())
        cls.old = old

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_both_windows_are_scored_inside_the_limit(self):
        self.assertEqual(sorted(self.result["windows"]), sorted(script.WINDOWS))
        for window, w in self.result["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertLessEqual(w["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["decision_time"], "18:00")

    def test_every_candidate_is_scored_against_the_ablations_candidate(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
            for candidate in script.CANDIDATES:
                self.assertEqual(sorted(cell["vs"][candidate]), [script.ANNNET])

    def test_the_splits_of_the_directive_are_reported(self):
        for w in self.result["windows"].values():
            self.assertTrue({"pooled", "lead", "pressure_day_type"} <= set(w["groups"]))
            self.assertTrue(set(w["groups"]) <= set(script.SPLITS))

    def test_a_term_differs_from_the_candidate_only_where_it_enters(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["differing_cells"]), sorted(script.ARMS))
            self.assertEqual(sorted(w["fits"]), sorted(script.ARMS))
            for ld in w["differing_cells"].values():
                self.assertEqual(sorted(ld["differing_cells"]), ["1", "2", "3", "4", "5"])

    def test_the_prechecks_report_both_findings_at_18_00(self):
        p = self.result["prechecks"]
        self.assertEqual(p["decision_time"], "18:00")
        self.assertIn("per_release_18:00", p["hinge_share_by_year"])
        self.assertIn("weekly_lag_18:00", p["hinge_share_by_year"])
        self.assertIn("rows_where_the_distance_differs", p["weekly_against_per_release"])
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("#621", text)
        self.assertIn("#622", text)

    def test_the_page_has_the_two_rows_and_no_verdict(self):
        text = self.page.read_text(encoding="utf-8")
        for key in ("satiation distance (satiation_dist_roll)", "satiation hinge (satiation_hinge_roll)"):
            self.assertIn(key, text)
        self.assertIn("Development data, not a verdict", text)
        self.assertNotIn("GO #", text)

    def test_the_ablation_page_measures_the_satiation_row_and_carries_the_correction(self):
        text = self.ablation.read_text(encoding="utf-8")
        self.assertIn("**Correction, 7 November 2026 (#1507", text)
        self.assertIn("scored in #1507 (corrected)", text)
        self.assertNotIn("| not measured |", text)
        self.assertIn("**Question 2 (as corrected on 7 November 2026, #1507).", text)
        self.assertEqual("\n".join(fa.question(self.result)).count("(default"), 3)
        self.assertNotIn("GO #", text)

    def test_without_the_record_the_ablation_page_is_what_it_was(self):
        self.assertEqual(fa.render(self.old), fa.render(fa.with_satiation(self.old, Path("/nonexistent/result.json"))))
        self.assertNotIn("Correction, 7 November 2026", fa.render(self.old))


class CommittedRecordTests(unittest.TestCase):
    """The tracked records of the declared run, and the pages generated from them."""

    RECORD = ROOT / "docs" / "research" / "satiation-arm-1507" / "result.json"
    PAGE = ROOT / "docs" / "research" / "satiation-arm-1507-result.md"
    ABLATION_PAGE = ROOT / "docs" / "research" / "family-ablation-1483-result.md"

    @unittest.skipUnless(RECORD.exists(), "the declared run has not been scored yet")
    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    @unittest.skipUnless(RECORD.exists(), "the declared run has not been scored yet")
    def test_the_tracked_ablation_page_is_what_the_script_renders_with_the_new_row(self):
        old = json.loads((ROOT / "docs" / "research" / "family-ablation-1483" / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(self.ABLATION_PAGE.read_text(encoding="utf-8"), fa.render(fa.with_satiation(old, self.RECORD)))

    @unittest.skipUnless(RECORD.exists(), "the declared run has not been scored yet")
    def test_the_control_is_the_ablations_candidate(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for window, against in record["against_1483"].items():
            for metric, models in against.items():
                for model, v in models.items():
                    self.assertLess(abs(v["difference"]), 1e-9, (window, metric, model))

    @unittest.skipUnless(RECORD.exists(), "the declared run has not been scored yet")
    def test_the_walks_stay_inside_the_limit(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
        self.assertEqual(record["decision_time"], "18:00")


if __name__ == "__main__":
    unittest.main()
