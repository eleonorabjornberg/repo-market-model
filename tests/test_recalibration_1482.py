"""H1 step 4 (#1482): the critical and futility values are recalibrated on (s3c-ann-net)'s own loss differentials.

`scripts/recalibration_1482.py` calibrates in the orientation the test applies, d = S(benchmark) - S(candidate), on post-2020 stationary-bootstrap windows
(#886's generator), and changes nothing in force. These tests pin the orientation, the generator, the five-level day rule, the tie to #1392's extract, and
that the constants in force are untouched. They read a result only for the check of the page and the records, which are tracked.

Recorded mutation (2026-11-06): in `scripts/recalibration_1482.py`, `differences` returned `[c - b for b, c in zip(benchmark, candidate)]` (the sign
reversed); `test_the_orientation_favours_the_candidate_above_zero` raised AssertionError ([-0.5, 0.5] != [0.5, -0.5]),
`test_a_better_candidate_gives_a_positive_mean_and_a_worse_one_a_negative_mean` raised AssertionError (-30.0 not greater than 0.0) and
`test_only_post_2020_days_enter_the_calibration` raised AssertionError. Not a leakage guard.
"""

import importlib.util
import json
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("recalibration_1482_script", ROOT / "scripts" / "recalibration_1482.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)


def business_days(first, n):
    out, d = [], first
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


class TestTheOrientation(unittest.TestCase):
    def test_the_orientation_favours_the_candidate_above_zero(self):
        self.assertEqual(rc.differences([2.0, 3.0], [1.5, 3.5]), [0.5, -0.5])

    def test_a_length_mismatch_is_refused(self):
        with self.assertRaises(ValueError):
            rc.differences([1.0], [1.0, 2.0])

    def test_a_better_candidate_gives_a_positive_mean_and_a_worse_one_a_negative_mean(self):
        rng = random.Random(3)
        bench = [1.0 + rng.random() for _ in range(300)]
        good = [b - 0.1 for b in bench]
        self.assertGreater(sum(rc.differences(bench, good)), 0.0)
        self.assertLess(sum(rc.differences(bench, [b + 0.1 for b in bench])), 0.0)


class TestTheGenerator(unittest.TestCase):
    def test_the_windows_are_the_stationary_bootstrap_inside_the_block_and_restored_after(self):
        before = sp._window_indices
        with rc.stationary_windows():
            self.assertIsNot(sp._window_indices, before)
            rng = random.Random(5)
            runs = set()
            for _ in range(100):
                index = sp._window_indices(400, 250, rng, sp.WINDOW_BLOCK)
                length = 1
                for a, b in zip(index, index[1:]):
                    if b == (a + 1) % 400:
                        length += 1
                    else:
                        runs.add(length)
                        length = 1
            self.assertGreater(len(runs), 5)
        self.assertIs(sp._window_indices, before)

    def test_the_calibrated_value_depends_on_the_generator(self):
        rng = random.Random(7)
        series, x = [], 0.0
        for _ in range(600):
            x = 0.7 * x + rng.gauss(0, 1)
            series.append(x)
        settings = dict(days=125, level=0.05, windows=400, seed=1)
        circular = sp.calibrate_critical_value(series, **settings)
        with rc.stationary_windows():
            stationary = sp.calibrate_critical_value(series, **settings)
        self.assertNotEqual(circular, stationary)


class TestTheDays(unittest.TestCase):
    def test_a_decision_day_needs_a_published_forecast_at_every_lead(self):
        dates = business_days(date(2021, 1, 4), 12)
        daily = {h: {dates[i + h].isoformat(): [0.0] for i in range(6)} for h in sp.HORIZONS}
        del daily[3][dates[2 + 3].isoformat()]
        kept = rc.five_level_days(dates[:8], dates, daily)
        self.assertEqual(kept, [dates[i] for i in (0, 1, 3, 4, 5)])

    def test_a_target_past_the_calendar_drops_the_day(self):
        dates = business_days(date(2021, 1, 4), 6)
        daily = {h: {d.isoformat(): [0.0] for d in dates} for h in sp.HORIZONS}
        self.assertEqual(rc.five_level_days(dates, dates, daily), [dates[0]])

    def test_only_post_2020_days_enter_the_calibration(self):
        days = [date(2020, 3, 30) + timedelta(days=i) for i in range(10)]
        leg = {"days": days, "benchmark": [2.0] * 10, "candidate": [1.0] * 10}
        bench, d = rc.post_2020_leg(leg)
        self.assertEqual(len(d), 6)
        self.assertEqual(d, [1.0] * 6)
        self.assertEqual(bench, [2.0] * 6)


class TestTheTie(unittest.TestCase):
    def record(self):
        return {"window": "development", "grid": {"origins": ["2020-04-03"], "B1": [1.0], "B2": [2.0], "candidate": [0.5]}}

    def losses(self, shift=0.0):
        return {"windows": {"development": {"origins": ["2020-04-03"], "scores": {"B1": [1.0], "B2": [2.0], "candidate": [0.5 + shift]}}}}

    def test_the_walk_that_matches_the_1392_extract_passes(self):
        rc.tie_to_1392(self.record(), self.losses())

    def test_a_walk_that_differs_is_refused(self):
        with self.assertRaises(ValueError):
            rc.tie_to_1392(self.record(), self.losses(shift=0.01))

    def test_other_origins_are_refused(self):
        other = self.losses()
        other["windows"]["development"]["origins"] = ["2020-04-06"]
        with self.assertRaises(ValueError):
            rc.tie_to_1392(self.record(), other)

    def test_the_tracked_series_is_the_1392_walk(self):
        if not rc.SERIES.exists():
            self.skipTest("series.json is not written yet")
        rc.tie_to_1392(rc.load_series(), json.loads(rc.LOSSES_1392.read_text(encoding="utf-8")))


class TestNothingInForceMoves(unittest.TestCase):
    def test_the_constants_in_force_are_the_ones_the_page_prints_beside_the_new_values(self):
        self.assertEqual(rc.in_force()["efficacy"]["B1"]["250"], sp.CRITICAL_VALUES[sp.GRID_COMPARISON][250])
        self.assertEqual(rc.in_force()["efficacy"]["B3"]["125"], sp.CRITICAL_VALUES[sp.FIVE_LEVEL_COMPARISON][125])
        self.assertEqual(rc.in_force()["futility"]["60"], sp.FUTILITY_CRITICAL_VALUES[sp.GRID_COMPARISON][60])

    def test_the_b2_leg_reads_the_grid_value_while_none_is_declared(self):
        self.assertEqual(sp.B2_LEG_CRITICAL_VALUES, {})
        self.assertEqual(rc.in_force()["efficacy"]["B2"], rc.in_force()["efficacy"]["B1"])

    def test_the_protocol_is_the_one_the_script_reads(self):
        # the values in force at the time of writing: a change here is her decision under section 13, not this study's.
        self.assertEqual(sp.CRITICAL_VALUES[sp.GRID_COMPARISON], {60: None, 125: 3.419438620805254, 250: 2.425730476113518})
        self.assertEqual(sp.BLOCK_LENGTH, 10)

    def test_the_milestone_is_not_marked_by_this_step(self):
        marks = json.loads((ROOT / "docs" / "research" / "milestones.json").read_text(encoding="utf-8"))
        self.assertNotIn("H1.M3", json.dumps(marks.get("done", marks)) if "done" in marks else json.dumps(marks))


class TestTheDraft(unittest.TestCase):
    def cal(self):
        return {
            "in_force": rc.in_force(),
            "efficacy_critical_values": {n: {"60": None, "125": 1.5, "250": 1.25} for n in rc.LEGS},
            "futility_critical_values": {"60": 3.0, "125": 2.5, "250": 2.0},
        }

    def test_the_draft_says_it_is_a_draft_not_in_force_and_for_her_merge(self):
        text = rc.draft_text(self.cal())
        self.assertIn("a draft by the pull request that closes #1482", text)
        self.assertIn("Nothing here is in force until she merges it", text)

    def test_the_draft_prints_the_values_in_force_beside_the_new_ones(self):
        text = rc.draft_text(self.cal())
        self.assertIn("| 125 | 3.419 | 1.500 |", text)
        self.assertIn("| 250 | 5.455 | 1.250 |", text)
        self.assertIn("| 60 | 1.930 | 3.000 |", text)

    def test_the_decision_record_keeps_exactly_one_draft_and_it_is_marked(self):
        text = (ROOT / "docs" / "decisions" / "scoring-protocol.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(rc.DRAFT_HEADING), 1)
        self.assertEqual(text.count(rc.DRAFT_ANCHOR), 1)


class TestTheParkingAndTheGate(unittest.TestCase):
    """#1506 (her ruling of 7 November 2026, card f1504-h5-gate-power): amendment 6 is parked, the gate reads the confirmation's own power.

    Not a leakage guard; no mutation is recorded.
    """

    def test_the_draft_is_marked_parked_and_not_proposed_for_h5(self):
        text = rc.draft_text(TestTheDraft.cal(None))
        self.assertIn("Parked, 7 November 2026 (#1506): not proposed for H5", text)
        self.assertIn("docs/decisions/h5-confirmation-design.md", text)
        self.assertIn("Nothing here is in force until she merges it", text)

    def test_the_page_beside_the_250_day_figure_states_the_confirmations_own_power(self):
        import json
        cal = json.loads(rc.CALIBRATION.read_text(encoding="utf-8"))
        power = json.loads(rc.POWER.read_text(encoding="utf-8"))
        text = rc.render(cal, power)
        self.assertIn("Dated note, 7 November 2026 (#1506)", text)
        self.assertIn("at most 1.4%", text)
        self.assertIn("about 32-35%", text)
        self.assertIn("The MME stays at 3%", text)
        # the figure of 8 stays as it was written
        self.assertIn("is 7.0% \u00b1 1.1, and 0.6% \u00b1 0.3 at the values in force", text)

    def test_the_quoted_figures_are_in_the_confirmation_design_and_its_study(self):
        design = (ROOT / "docs" / "decisions" / "h5-confirmation-design.md").read_text(encoding="utf-8")
        study = (ROOT / "docs" / "research" / "confirmation-size-power-1392-full-result.md").read_text(encoding="utf-8")
        for needle in ("pass rate is at most 1.4%", "34.6%", "31.6%"):
            self.assertIn(needle, design)
        self.assertIn("at most 1.4%", study)

    def test_the_manuals_name_the_confirmation_study_as_the_gate(self):
        for name in ("H1.md", "H5.md"):
            text = (ROOT / "docs" / "research" / "hypotheses" / name).read_text(encoding="utf-8")
            self.assertIn("confirmation-size-power-1392-full-result.md", text, name)
            self.assertIn("#1506", text, name)


class TestThePage(unittest.TestCase):
    def test_the_page_records_the_mme_ruling_with_the_power_figure(self):
        import json
        cal = json.loads(rc.CALIBRATION.read_text(encoding="utf-8"))
        power = json.loads(rc.POWER.read_text(encoding="utf-8"))
        text = rc.render(cal, power)
        self.assertIn("## 8. Ruling recorded, 6 November 2026: the MME stays at 3% (#1498)", text)
        self.assertIn("is 7.0% \u00b1 1.1, and 0.6% \u00b1 0.3 at the values in force", text)
        self.assertIn("out of reach by 250 confirmation days", text)

    def test_the_records_and_the_page_agree(self):
        if not rc.PAGE.exists():
            self.skipTest("the page is not written yet")
        self.assertEqual(rc.check_command(None), 0)


if __name__ == "__main__":
    unittest.main()
