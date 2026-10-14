"""The confirmation-design study (H1 step 2, #733): `scripts/confirmation_design.py`.

The rule is `docs/research/confirmation-design-733.md`. These tests cover the script's parts on small inputs and its
agreement with the rule's text; the study's own result is `docs/research/confirmation-design-733/result.json`, made by
`run` and checked by `check`.

**Recorded mutation** (CLAUDE.md), 14 October 2026, in a disposable copy of the tree, CPython 3.11,
`PYTHONDONTWRITEBYTECODE=1`, applied by `sed` and confirmed by `grep`: `confirmation_design.decision_positions`, the
guard `if rows[t + max(sp.HORIZONS)].date > STUDY_END:` changed to `if False:`.
`PoolTests.test_no_day_after_the_study_end_is_read` failed with `AssertionError: datetime.date(2026, 9, 3) not less
than or equal to datetime.date(2025, 12, 31)` (the pool's last target ran to the panel's end); with that guard gone,
`build_pool` would still stop at `require_study_window`, which raises `LookAheadError`.
A second mutation, in `require_study_window`, `if late:` changed to `if False:`:
`StudyWindowTests.test_a_day_after_the_study_end_is_refused` failed with `AssertionError: LookAheadError not raised`.
"""

import importlib.util
import json
import random
import re
import sys
import unittest
from datetime import date
from pathlib import Path

from test_protocol_benchmarks import published_panel

from repo_model import scoring_protocol as sp
from repo_model.data import DailyObservation, next_business_day
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("confirmation_design_script", ROOT / "scripts" / "confirmation_design.py")
cd = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cd
spec.loader.exec_module(cd)

RULE = ROOT / "docs" / "research" / "confirmation-design-733.md"
RESULT = ROOT / "docs" / "research" / "confirmation-design-733" / "result.json"


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            cd.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_study_end_itself_is_allowed(self):
        cd.require_study_window([date(2025, 12, 31), date(2018, 6, 29)])


class PoolTests(unittest.TestCase):
    def test_no_day_after_the_study_end_is_read(self):
        rows = list(published_panel()["rows"])
        positions = cd.decision_positions(rows)
        last = rows[positions[-1] + max(sp.HORIZONS)]
        self.assertLessEqual(last.date, cd.STUDY_END)
        # rows appended after the panel's end change nothing, and the panel's own later rows are never targets
        self.assertGreater(rows[-1].date, cd.STUDY_END)
        extra = list(rows)
        day = extra[-1].date
        for _ in range(8):
            day = next_business_day(day, 1)
            extra.append(DailyObservation(date=day, values=dict(extra[-1].values)))
        self.assertEqual(cd.decision_positions(extra), positions)


class CheckpointTests(unittest.TestCase):
    def test_the_looks_are_the_protocols_shares_of_the_days(self):
        self.assertEqual(cd.checkpoints(250), (60, 125, 250))
        self.assertEqual(cd.checkpoints(375), (90, 188, 375))
        self.assertEqual(cd.checkpoints(500), (120, 250, 500))

    def test_the_protocols_own_looks_have_the_protocols_levels(self):
        self.assertEqual(sp.nominal_levels(cd.checkpoints(250)), sp.nominal_levels())


class CandidateTests(unittest.TestCase):
    def series(self):
        rng = random.Random(1)
        b = [1.0 + rng.random() for _ in range(300)]
        e = [rng.gauss(0.0, 0.5) for _ in range(300)]
        return b, e

    def test_the_candidates_skill_is_exactly_delta(self):
        b, e = self.series()
        for noise in (1.0, 0.5):
            x = cd.candidate(b, e, 0.03, noise)
            self.assertAlmostEqual(sum(x) / sum(b), 0.03, places=12)

    def test_under_no_difference_the_mean_is_zero(self):
        b, e = self.series()
        self.assertAlmostEqual(sum(cd.candidate(b, e, 0.0, 1.0)), 0.0, places=9)


class ScaleTests(unittest.TestCase):
    def test_the_first_days_have_no_scale_and_the_next_has(self):
        values = [1.0 + 0.01 * i for i in range(120)]
        scale = cd.trailing_scale(values)
        self.assertTrue(all(m is None for m in scale[: cd.WARMUP]))
        self.assertIsNotNone(scale[cd.WARMUP])
        self.assertEqual(cd.WARMUP, 65)

    def test_the_scale_reads_only_days_whose_leads_are_published(self):
        rng = random.Random(2)
        values = [1.0 + rng.random() for _ in range(150)]
        base = cd.trailing_scale(values)
        i = 100
        for j in range(i - cd.SCALE_LAG + 1, len(values)):  # day i - 5 and everything later
            moved = list(values)
            moved[j] = 1.0e6
            self.assertEqual(cd.trailing_scale(moved)[i], base[i], j)
        moved = list(values)
        moved[i - cd.SCALE_LAG] = 1.0e6  # the last day the scale may read
        self.assertNotEqual(cd.trailing_scale(moved)[i], base[i])

    def test_the_scale_is_the_mean_of_sixty_days(self):
        values = [float(i) for i in range(100)]
        scale = cd.trailing_scale(values)
        i = 90
        self.assertAlmostEqual(scale[i], sum(values[i - 65: i - 5]) / 60)


class WindowTests(unittest.TestCase):
    def test_a_windows_statistic_is_the_scorers_for_the_same_seed(self):
        rng = random.Random(4)
        values = [rng.gauss(0.0, 1.0) for _ in range(400)]
        mine = cd.window_statistics(values, days=80, lengths=[80], windows=200, seed=7)[80]
        theirs = sp.window_t_statistics(values, days=80, windows=200, seed=7)
        self.assertEqual(mine, theirs)

    def test_a_shorter_look_reads_the_windows_first_days(self):
        rng = random.Random(5)
        values = [rng.gauss(0.0, 1.0) for _ in range(400)]
        both = cd.window_statistics(values, days=80, lengths=[40, 80], windows=100, seed=3)
        self.assertEqual(len(both[40]), 100)
        self.assertNotEqual(both[40], both[80])


class DesignTests(unittest.TestCase):
    def table(self):
        text = RULE.read_text(encoding="utf-8")
        rows = re.findall(r"^\| (D\d) \| (\d+) \| [^|]+ \| ([^|]+) \| [^|]+ \| ([\w ]+) \|$", text, re.M)
        return [(i, int(days), leads.strip(), scale) for i, days, leads, scale in rows]

    def test_the_closed_list_is_the_rules_table(self):
        table = self.table()
        self.assertEqual([row[0] for row in table], [d.id for d in cd.DESIGNS])
        for design, (_, days, leads, scale) in zip(cd.DESIGNS, table):
            self.assertEqual(design.days, days)
            self.assertEqual(design.leads == (1,), leads == "lead 1 alone")
            self.assertEqual(design.standardized, scale.strip() == "standardized")

    def test_the_rules_counts_are_the_scripts(self):
        text = RULE.read_text(encoding="utf-8")
        self.assertIn(f"{cd.PATHS:,} paths", text)
        self.assertIn(f"{cd.WINDOWS:,} per pair", text)
        self.assertEqual(cd.STUDY_END.isoformat(), "2025-12-31")
        self.assertIn(cd.STUDY_END.isoformat(), text)

    def test_the_scenarios_cover_the_rules_grid(self):
        deltas = {delta for _, delta, noise, history in cd.SCENARIOS if history == "full" and noise == 1.0}
        self.assertEqual(deltas, {0.0, *cd.MDE_GRID, 0.10})


class PathTests(unittest.TestCase):
    def setUp(self):
        rng = random.Random(3)
        self.b = [2.0 + rng.random() for _ in range(600)]
        self.e = [rng.gauss(0.0, 0.05) for _ in range(600)]
        self.design = cd.Design("T", 250, sp.HORIZONS, False)

    def share(self, delta, critical):
        cd.init_worker({("T", "full"): (self.b, self.e)}, {"T": {"125": critical, "250": critical}})
        results = [cd.run_path((self.design, "full", delta, 1.0, 100 + i)) for i in range(40)]
        return sum(1 for r in results if r[1] is not None) / len(results)

    def test_a_strong_candidate_is_detected_and_a_null_one_is_not(self):
        self.assertGreater(self.share(0.3, 1.7), 0.9)
        self.assertLess(self.share(0.0, 1.7), 0.2)

    def test_a_larger_critical_value_never_detects_more(self):
        self.assertLessEqual(self.share(0.05, 6.0), self.share(0.05, 1.7))

    def test_the_gate_withholds_a_detection_below_the_mme(self):
        cd.init_worker({("T", "full"): (self.b, self.e)}, {"T": {"125": 0.5, "250": 0.5}})
        ungated = [cd.run_path((self.design, "full", 0.02, 0.05, 9 + i)) for i in range(40)]
        self.assertTrue(any(r[0] is not None for r in ungated))
        self.assertTrue(all(r[1] is None for r in ungated))


class ReadingTests(unittest.TestCase):
    def scenarios(self, size, power3):
        out = {}
        for design in cd.DESIGNS:
            last = str(design.days)
            out[design.id] = {}
            for name, *_ in cd.SCENARIOS:
                s = size[design.id] if name.startswith("size") else power3[design.id]
                out[design.id][name] = {
                    "without_the_mme_gate": {last: s}, "without_the_mme_gate_se": 0.005,
                    "with_the_mme_gate": {last: s}, "with_the_mme_gate_se": 0.01,
                    "mean_days_to_detection": None,
                }
        return out

    def test_the_best_admissible_design_wins_and_a_tie_goes_to_fewer_days(self):
        size = {d.id: 0.03 for d in cd.DESIGNS}
        size["D2"] = 0.2  # not admissible
        power = {"D0": 0.2, "D1": 0.5, "D2": 0.9, "D3": 0.1, "D4": 0.495, "D5": 0.5}
        reading = cd.reading(self.scenarios(size, power))
        self.assertNotIn("D2", reading["admissible"])
        self.assertEqual(reading["recommended"], "D4")  # D4 is within one standard error of D1 and D5 and has fewest days
        self.assertEqual(reading["reach_target_power_at_3"], [])

    def test_no_admissible_design_means_no_recommendation(self):
        size = {d.id: 0.2 for d in cd.DESIGNS}
        reading = cd.reading(self.scenarios(size, {d.id: 0.5 for d in cd.DESIGNS}))
        self.assertIsNone(reading["recommended"])


class ResultTests(unittest.TestCase):
    @unittest.skipUnless(RESULT.exists(), "the study has not been run")
    def test_the_result_was_made_under_this_rule_and_ends_in_time(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(result["rule_sha256"], cd.sha256(cd.RULE))
        self.assertLessEqual(result["pool"]["last"], cd.STUDY_END.isoformat())
        add = RESULT.with_name("addendum.json")
        add = json.loads(add.read_text(encoding="utf-8")) if add.exists() else None
        self.assertEqual(cd.PAGE.read_text(encoding="utf-8"), cd.render_page(result, add))
        self.assertEqual(set(result["designs"]), {d.id for d in cd.DESIGNS})
        self.assertEqual(set(result["scenarios"]["D0"]), {name for name, *_ in cd.SCENARIOS})


if __name__ == "__main__":
    unittest.main()
