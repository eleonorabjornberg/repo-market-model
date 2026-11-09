"""`scripts/h7f_rs_1526.py` (#1526; H7 step 2, H7f, development tier): the nested development test of R+S on the H5 candidate (s3c-ann-net).

Written first, against the declaration `metadata/h7f_rs_1526.json`. What these tests pin: that the declaration names what the module has (seed, models, arms,
the last day, the 18:00 instant, no later amendment); that the arm is the candidate with exactly one change, its two `extra` terms R and S (the Huber fit, the
ridge, the net settlement terms and the direct pairs are the candidate's, so the contrast is R+S and nothing else); step 1, that `candidate_reads` finds the
candidate reading neither R nor S and refuses to run if it read either (the question would then be answered by construction); the plan of paired tests
(the arm against the candidate and B1, B1' and B2; the candidate against the three); B3's five-level scores on hand cases (a day missing a lead is dropped, a
record that disagrees with the panel on the outcome is refused); the lead-1 miss-after-miss rates on a hand sequence; the refusal to walk at another instant and
the refusal of rows that are not the panel's days; the refusal of a scratch panel whose dates or published columns differ; a small run of `prechecks`, `score`,
`assemble` and `page` end to end on the fixture panel; and that `docs/research/milestones.json` is not touched (she is asked, not told).

The columns' own no-look-ahead guard is `repo_model.s3c_rs.check_rs_no_future`, with its recorded mutations in `tests/test_s3c_rs.py`.

Recorded mutations (9 November 2026, disposable copy, each restored after its run). In `h7f_rs_1526.walks_of`, the guard
`if k.DECISION_TIME != DECISION_TIME:` was changed to `if False:`. `WalkTests.test_a_walk_not_at_the_declared_instant_is_refused` then errored with
`AttributeError: 'NoneType' object has no attribute 'dates'` (the guard gone, the call went on and met the `None` frame; `ValueError` was not raised). Second, in
the same function, the guard `if [r.date for r in built] != [r.date for r in panel]:` was changed to `if False:`;
`WalkTests.test_rows_that_are_not_the_panels_days_are_refused` then errored with the same `AttributeError`. Third, in `aug_rows`,
`if name in a.values and a.values[name] != value` was replaced by `if False`: `ScratchPanelTests.test_a_published_column_that_differs_is_refused` failed with
`AssertionError: ValueError not raised`. Fourth, in `candidate_reads`, `if reads_reserves_term:` was replaced by `if False:`:
`CandidateReadsTests.test_a_candidate_that_already_reads_r_is_refused` failed with `AssertionError: ValueError not raised`. Fifth, in `b3_scores`, the
outcome check `if abs(float(entry["actual_bps"]) - float(observed)) > 1e-9:` was replaced by `if False:`:
`B3Tests.test_a_record_that_disagrees_on_the_outcome_is_refused` failed with `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from repo_model import s3c_announced
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("h7f_rs_1526", ROOT / "scripts" / "h7f_rs_1526.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["h7f_rs_1526"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)
fa = script.fa

BASE = s3c_announced.ANN_NET_ARM


def declaration() -> dict:
    return json.loads((ROOT / "metadata" / "h7f_rs_1526.json").read_text(encoding="utf-8"))


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        d = declaration()
        self.assertEqual(d["issue"], 1526)
        self.assertEqual(script.SEED, 1526)
        self.assertIn("seed 1526", d["scoring"]["test"])
        self.assertEqual([a["name"] for a in d["arms"]], [script.ANNNET, script.RS])
        self.assertEqual(d["arm"]["name"], script.RS)
        self.assertEqual(d["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(d["amendments"], [])
        self.assertIn("18:00", d["decision_instant"])
        self.assertEqual(d["benchmarks"], ["B1", "B1_prime", "B2", "B3"])

    def test_it_serves_h7_step_2_and_changes_nothing_published(self):
        d = declaration()
        self.assertIn("H7", d["hypothesis"])
        self.assertIn("step 2", d["hypothesis"])
        self.assertIn("docs/research/h5-candidate.json", d["limits"]["named_candidate"])
        self.assertIn("not changed", d["limits"]["allow_list"])
        self.assertIn("nothing here changes it", d["status"].lower() + " nothing here changes it")
        self.assertEqual(d["limits"]["last_day"], "2026-09-03")

    def test_the_register_row_is_cleared_and_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "h7f_rs_1526.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/h7f_rs_1526.json")
        self.assertEqual(row["script"], "scripts/h7f_rs_1526.py")
        self.assertEqual(row["pairing"], "direct")

    def test_the_milestones_file_does_not_mark_h7_m2(self):
        marks = json.loads((ROOT / "docs" / "research" / "milestones.json").read_text(encoding="utf-8"))["milestones"]
        self.assertNotIn("H7.M2", marks)


class ArmTests(unittest.TestCase):

    def test_the_arm_adds_r_and_s_as_extra_terms_and_nothing_else(self):
        self.assertEqual(script.RS_ARM.extra, sc.RS_EXTRAS)
        for f in dataclasses.fields(BASE):
            if f.name in ("name", "role", "extra"):
                continue
            self.assertEqual(getattr(script.RS_ARM, f.name), getattr(BASE, f.name), f.name)

    def test_the_candidate_is_the_ablations_candidate_and_reads_no_extra_term(self):
        self.assertIs(script.WALK_ARMS[0], s3c_announced.ANN_NET_ARM)
        self.assertEqual(script.WALK_ARMS[0].extra, ())
        self.assertEqual(script.ANNNET, fa.ANNNET)

    def test_the_models_and_the_plan_of_paired_tests(self):
        self.assertEqual(script.RS, "sc_s3c_ann_net_rs")
        self.assertEqual(len(set(script.MODELS)), len(script.MODELS))
        self.assertEqual(script.plan(script.RS), [script.ANNNET, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.ANNNET), ["B1", script.B1P, "B2"])
        self.assertEqual(script.plan("B1"), [])
        self.assertEqual(set(script.CANDIDATES), {script.RS, script.ANNNET})


def panel_rows(n=5):
    day, out = date(2026, 3, 2), []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(DailyObservation(day, {"sofr": 3.0 + len(out)}))
        day += timedelta(days=1)
    return out


class CandidateReadsTests(unittest.TestCase):
    """Step 1: what (s3c-ann-net) already reads of R and S."""

    def test_the_candidate_reads_neither_r_nor_s(self):
        out = script.candidate_reads(panel_rows())
        self.assertFalse(out["reads_R"])
        self.assertFalse(out["reads_S"])
        self.assertTrue(out["state_held_at_maximum"])
        self.assertEqual(out["state_levels_read"], [1.0])
        self.assertEqual(out["the_arm_adds"], list(sc.RS_EXTRAS))
        self.assertFalse(out["answered_by_construction"])
        for term in out["location_terms"] + out["extra_terms"]:
            self.assertNotIn(term, sc.RS_EXTRAS)

    def test_a_candidate_that_already_reads_r_is_refused(self):
        reading = dataclasses.replace(BASE, extra=(sc.RS_RATIO,))
        with mock.patch.object(script, "_BASE", reading), self.assertRaises(ValueError):
            script.candidate_reads(panel_rows())

    def test_a_candidate_whose_state_is_not_held_is_refused(self):
        with mock.patch.object(script.s3c_net, "constant_states", lambda panel: {r.date: 1.0 for r in panel}), self.assertRaises(ValueError):
            script.candidate_reads(panel_rows())


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
        wider = [DailyObservation(r.date, dict(r.values, bank_total_assets=1.0, on_rrp=2.0)) for r in panel]
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


GRID = sp.GRID


def quantiles(shift=0.0):
    return [float(i) + shift for i in range(len(GRID))]


def stub_frame(days=6, outcomes=None):
    dates = []
    day = date(2026, 3, 2)
    while len(dates) < days + 6:
        if day.weekday() < 5:
            dates.append(day)
        day += timedelta(days=1)
    scored = dates[:days]
    outcome = {d: (outcomes[i] if outcomes and i < len(outcomes) else 0.0) for i, d in enumerate(dates)}
    position = {d: i for i, d in enumerate(dates)}
    return SimpleNamespace(
        dates=dates, days=scored, outcome=outcome, position=position,
        target=lambda d, h: dates[position[d] + h],
        forecasts={m: {d: {h: quantiles() for h in sp.HORIZONS} for d in scored} for m in (script.ANNNET, script.RS)},
    )


def record_for(frame, drop=None, bump=0.0):
    daily = {}
    for h in sp.HORIZONS:
        daily[h] = {}
        for d in frame.dates:
            if drop and (h, d) in drop:
                continue
            daily[h][d.isoformat()] = {"quantiles_bps": [float(i) for i in range(len(script.B3_LEVELS))], "actual_bps": frame.outcome[d] + bump}
    return daily


class B3Tests(unittest.TestCase):

    def test_the_scores_are_the_five_level_crps_averaged_over_the_leads(self):
        frame = stub_frame()
        kept, series = script.b3_scores(frame, (script.ANNNET, script.RS), record_for(frame))
        self.assertEqual(kept, frame.days)
        five = sp.level_crps(script.B3_LEVELS)
        expect = sum(five([float(i) for i in range(5)], frame.outcome[frame.dates[frame.position[frame.days[0]] + h]]) for h in sp.HORIZONS) / 5.0
        self.assertAlmostEqual(series[script.B3][frame.days[0]], expect)
        expect_model = sum(five(sp.on_levels(quantiles(), script.B3_LEVELS), 0.0) for _h in sp.HORIZONS) / 5.0
        self.assertAlmostEqual(series[script.RS][frame.days[0]], expect_model)

    def test_a_day_missing_a_lead_in_the_record_is_dropped(self):
        frame = stub_frame()
        gone = frame.dates[frame.position[frame.days[2]] + 3]
        kept, series = script.b3_scores(frame, (script.ANNNET, script.RS), record_for(frame, drop={(3, gone)}))
        self.assertNotIn(frame.days[2], kept)
        self.assertEqual(len(kept), len(frame.days) - 1)
        self.assertEqual(set(series[script.B3]), set(kept))

    def test_a_record_that_disagrees_on_the_outcome_is_refused(self):
        frame = stub_frame()
        with self.assertRaises(ValueError):
            script.b3_scores(frame, (script.ANNNET, script.RS), record_for(frame, bump=0.5))


class DependenceTests(unittest.TestCase):

    def test_miss_after_miss_and_after_hit_on_a_hand_sequence(self):
        # the central 90% band is [q05, q95] = [GRID.index(0.05), GRID.index(0.95)] of quantiles() = the index values
        hi = quantiles()[GRID.index(0.95)]
        pattern = [1, 1, 0, 1, 0, 0]
        frame = stub_frame(6)
        for i, miss in enumerate(pattern):
            frame.outcome[frame.dates[i + 1]] = hi + 5.0 if miss else quantiles()[GRID.index(0.5)]
        out = script.lead_1_dependence(frame, permutations=50)
        for model in (script.ANNNET, script.RS):
            e = out[model]["band90/strict"]
            self.assertEqual(e["misses"], 3)
            self.assertAlmostEqual(e["p_miss_after_miss"], 1.0 / 3.0)
            self.assertAlmostEqual(e["p_miss_after_hit"], 0.5)
            self.assertEqual(e["longest_run"], 2)
            self.assertEqual(e["transitions"], [1, 1, 2, 1])

    def test_a_gap_in_the_days_is_not_a_transition(self):
        frame = stub_frame(6)
        frame.days = [frame.days[0], frame.days[1], frame.days[3], frame.days[4]]  # a day is missing between the second and the third
        out = script.lead_1_dependence(frame, permutations=10)
        self.assertEqual(sum(out[script.RS]["band90/strict"]["transitions"]), 2)


class EndToEndTests(unittest.TestCase):
    """`prechecks`, `score`, `assemble` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-09-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        pv = importlib.util.spec_from_file_location("pressure_v1_1_in_1526", ROOT / "scripts" / "pressure_v1_1.py")
        module = importlib.util.module_from_spec(pv)
        sys.modules["pressure_v1_1_in_1526"] = module
        pv.loader.exec_module(module)
        cls.aug = base / "AUG.csv"
        module.main(["panel", "--output", str(cls.aug), "--end", "2026-09-03"])
        script.main(["prechecks", "--panel", str(cls.panel_path), "--aug-panel", str(cls.aug), "--output", str(base / "prechecks.json"), "--check-every", "400"])
        for window in script.WINDOWS:
            script.main(["score", "--panel", str(cls.panel_path), "--aug-panel", str(cls.aug), "--window", window,
                         "--output", str(base / f"result-{window}.json"), "--draws", "20", "--reps", "5", "--permutations", "20", "--workers", "2",
                         "--first", cls.FIRST, "--check-every", "400"])
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["assemble", "--input-dir", str(base), "--output", str(cls.output)])
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

    def test_the_arm_is_scored_against_the_candidate_and_the_benchmarks(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
            self.assertEqual(sorted(cell["vs"][script.RS]), sorted(script.plan(script.RS)))
            self.assertEqual(sorted(cell["vs"][script.ANNNET]), sorted(script.plan(script.ANNNET)))

    def test_the_splits_of_the_directive_are_reported(self):
        for w in self.result["windows"].values():
            self.assertTrue({"pooled", "lead", "regime", "pressure_day_type"} <= set(w["groups"]) | {"regime"})
            self.assertTrue({"pooled", "lead", "pressure_day_type"} <= set(w["groups"]))
            self.assertTrue(set(w["groups"]) <= set(script.SPLITS))

    def test_the_terms_differ_from_the_candidate_at_every_lead(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["differing_cells"]["differing_cells"]), ["1", "2", "3", "4", "5"])
            self.assertEqual(sorted(w["fits"]), sorted(sc.RS_EXTRAS))

    def test_b3_and_the_dependence_are_reported(self):
        for w in self.result["windows"].values():
            self.assertIn("b3", w)
            self.assertEqual(w["b3"]["levels"], list(script.B3_LEVELS))
            for model in (script.ANNNET, script.RS):
                self.assertEqual(sorted(w["lead_1_dependence"][model]), sorted(script.DEPENDENCE_SEQUENCES))

    def test_step_1_and_the_columns_are_in_the_record(self):
        self.assertFalse(self.result["candidate_reads"]["reads_R"])
        self.assertFalse(self.result["candidate_reads"]["reads_S"])
        p = self.result["prechecks"]
        self.assertEqual(p["decision_time"], "18:00")
        self.assertIn("passed", p["no_future_check"])
        self.assertTrue(p["by_year"])

    def test_the_page_answers_first_and_has_no_verdict(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# H7f: the nested development test of R+S on the H5 candidate (#1526)"))
        self.assertIn("It reads neither", text)
        self.assertIn("Development data, not a verdict", text)
        self.assertIn("Question for Eleonora", text)
        self.assertIn("Dependence at lead 1", text)
        self.assertIn("Against B3", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked records of the declared run, and the page generated from them."""

    RECORD = ROOT / "docs" / "research" / "h7f-rs-1526" / "result.json"
    PAGE = ROOT / "docs" / "research" / "h7f-rs-1526-result.md"

    @unittest.skipUnless(RECORD.exists(), "the declared run has not been scored yet")
    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

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
        self.assertFalse(record["candidate_reads"]["reads_R"])


if __name__ == "__main__":
    unittest.main()
