"""The helpers of `scripts/fhs_scale_941.py` (#941; H5 step 3, development tier).

Written after the script, which is measurement code. It adds no reader of its own: the scored days pass
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`), and the
scale guard is recorded in `test_spread_mr_fhs`. What these tests pin: the hit sequences on hand cases (both hit rules, the
restriction to the days a `gbm_funding` law exists for, the groups each test is read on), the reader of `gbm_funding`'s walks,
the reading rule, and a small run of `score` and `page` end to end on a late subset of the fixture panel.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import coverage_tests as ct
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("fhs_scale_941", ROOT / "scripts" / "fhs_scale_941.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["fhs_scale_941"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

START = date(2024, 1, 2)


class FakeFrame:
    """Forty consecutive days; the outcome at day i is i % 10 bp, the regime is by half, the day type alternates."""

    def __init__(self, quantile=4.5, split=21):
        self.split = split
        self.dates = [START + timedelta(days=i) for i in range(50)]
        self.days = self.dates[:40]
        self.outcome = {day: float(i % 10) for i, day in enumerate(self.dates)}
        self.position = {day: i for i, day in enumerate(self.dates)}
        # every quantile of every lead sits at `quantile` bp (4.5: a hit is an outcome of 5..9 under either rule)
        flat = {h: [quantile] * len(sp.GRID) for h in sp.HORIZONS}
        self.forecasts = {name: {day: flat for day in self.days} for name in script.MODELS}

    def target(self, decision, lead):
        return self.dates[self.position[decision] + lead]

    def regime(self, day):
        return "first" if self.position[day] < self.split else "second"

    def day_type(self, day):
        return "ordinary" if self.position[day] % 2 else "quarter_end"


class HitTableTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.frame = FakeFrame()

    def lead_one(self, tables, model="spread_mr_level10", rule="above", level="q90"):
        return tables["rows"][model][rule][level]["h=1"]

    def test_the_hit_is_the_outcome_beyond_the_quantile_and_the_rule_is_reported_both_ways(self):
        tables = script.hit_tables(self.frame, {})
        above = self.lead_one(tables, rule="above")["pooled"]
        at_or_above = self.lead_one(tables, rule="at_or_above")["pooled"]
        # targets of lead 1 are days 1..40 with outcomes i % 10: outcomes 5..9 are above 4.5 in both rules
        self.assertEqual((above["n"], above["hits"]), (40, 20))
        self.assertEqual(at_or_above["hits"], above["hits"])
        # a quantile of 5.0 ties with the outcomes of 5 bp (four of the forty targets): "above" does not count them
        tables = script.hit_tables(FakeFrame(5.0), {})
        self.assertEqual(self.lead_one(tables, rule="above")["pooled"]["hits"], 20 - 4)
        self.assertEqual(self.lead_one(tables, rule="at_or_above")["pooled"]["hits"], 20)

    def test_the_three_tests_are_those_of_coverage_tests(self):
        tables = script.hit_tables(self.frame, {})
        cell = self.lead_one(tables)["pooled"]
        targets = [self.frame.target(d, 1) for d in self.frame.days]
        sequence = ct.hit_sequence([self.frame.outcome[t] for t in targets], [4.5] * 40, rule="above")
        self.assertAlmostEqual(cell["kupiec"]["p_value"], ct.kupiec(sequence, 0.10).p_value, delta=1e-12)
        self.assertAlmostEqual(cell["independence"]["p_value"], ct.christoffersen_independence(sequence).p_value, delta=1e-12)
        self.assertAlmostEqual(
            cell["conditional"]["p_value"], ct.christoffersen_conditional_coverage(sequence, 0.10).p_value, delta=1e-12)

    def test_a_regime_gets_all_three_tests_and_a_day_type_only_kupiec(self):
        tables = script.hit_tables(self.frame, {})
        cell = self.lead_one(tables)
        self.assertIsNotNone(cell["regime/second"]["independence"])
        self.assertIsNone(cell["pressure_day_type/ordinary"]["independence"])
        self.assertIsNone(cell["pressure_day_type/ordinary"]["conditional"])
        self.assertIsNotNone(cell["pressure_day_type/ordinary"]["kupiec"])

    def test_a_group_of_fewer_than_twenty_days_is_not_tested(self):
        cell = self.lead_one(script.hit_tables(FakeFrame(split=10), {}))
        self.assertNotIn("regime/first", cell)
        self.assertIn("regime/second", cell)
        self.assertTrue(all(row["n"] >= script.MIN_GROUP_DAYS for row in cell.values()))

    def test_gbm_funding_restricts_every_model_to_the_days_it_has_a_law_for(self):
        law = [4.5] * len(sp.GRID)
        walks = {1: {self.frame.target(d, 1): law for d in self.frame.days[10:]}}
        tables = script.hit_tables(self.frame, walks)
        self.assertEqual(tables["gbm_leads"], [1])
        self.assertEqual(tables["rows"][script.GBM]["above"]["q90"]["h=1"]["pooled"]["n"], 30)
        self.assertEqual(self.lead_one(tables)["pooled"]["n"], 30)
        # a lead without a walk is read on every scored day, and has no gbm_funding row
        self.assertEqual(tables["rows"]["spread_mr_level10"]["above"]["q90"]["h=2"]["pooled"]["n"], 40)
        self.assertNotIn("h=2", tables["rows"][script.GBM]["above"]["q90"])

    def test_the_levels_read_the_grid_columns_of_q90_q95_q99(self):
        self.assertEqual([sp.GRID.index(level) for level in script.HIT_LEVELS], [19, 20, 22])


class ReadGbmTests(unittest.TestCase):

    def write(self, directory, h, *, variant="gbm_funding", levels=None, laws=None):
        laws = laws if laws is not None else {"2024-03-01": [1.0] * len(sp.GRID), "2026-03-02": [2.0] * len(sp.GRID), "2024-03-04": None}
        document = {"variant": variant, "horizon": h, "levels": list(sp.GRID) if levels is None else levels, "laws": laws}
        (directory / f"gbm_funding_h{h}.json").write_text(json.dumps(document), encoding="utf-8")

    def test_only_the_leads_that_exist_are_read_and_no_day_after_the_last_is_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write(directory, 1)
            self.write(directory, 3)
            laws = script.read_gbm(directory)
        self.assertEqual(sorted(laws), [1, 3])
        self.assertEqual(list(laws[1]), [date(2024, 3, 1)])

    def test_no_directory_is_no_walks(self):
        self.assertEqual(script.read_gbm(None), {})

    def test_a_walk_of_another_lead_or_variant_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write(directory, 1, variant="published")
            with self.assertRaises(ValueError):
                script.read_gbm(directory)
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write(directory, 1)
            (directory / "gbm_funding_h2.json").write_text((directory / "gbm_funding_h1.json").read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaises(ValueError):
                script.read_gbm(directory)

    def test_a_walk_on_five_levels_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write(directory, 1, levels=[0.05, 0.25, 0.5, 0.75, 0.95])
            with self.assertRaises(ValueError):
                script.read_gbm(directory)


class IntervalTests(unittest.TestCase):

    def test_two_equal_series_have_a_zero_difference_interval(self):
        values = [float(i % 3) for i in range(60)]
        self.assertEqual(script.difference_interval(values, values, seed=1, reps=50), [0.0, 0.0])

    def test_the_mean_interval_brackets_a_constant_series(self):
        self.assertEqual(script.mean_interval([2.0] * 40, seed=1, reps=50), [2.0, 2.0])


class ReadingTests(unittest.TestCase):

    def test_a_gain_needs_the_interval_above_zero_and_a_loss_below(self):
        self.assertEqual(script.verdict({"skill_interval": [0.01, 0.05]}), "gain")
        self.assertEqual(script.verdict({"skill_interval": [-0.05, -0.01]}), "loss")
        self.assertEqual(script.verdict({"skill_interval": [-0.01, 0.05]}), "undecided")
        self.assertEqual(script.verdict({"undefined": "no variance"}), "undecided")


class DeclarationTests(unittest.TestCase):

    def test_the_script_reads_the_committed_declaration_and_its_taus_and_levels(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(declaration["hit_sequences"]["levels"], list(script.HIT_LEVELS))
        text = " ".join(declaration["scoring"]["measures"])
        for tau in script.TAUS:
            self.assertIn(f"{tau:g}", text.replace("+", ""))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(script.committed_declaration()["issue"], 941)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last year and a half of the fixture panel, with few resamples: the shape, not the figures."""

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.tmp.name) / "result.json"
        cls.page = Path(cls.tmp.name) / "page.md"
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--draws", "20", "--reps", "5",
                     "--slope-reps", "5", "--workers", "2", "--first", "2024-06-03"])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_declared_variant_is_scored_against_the_reference_and_both_benchmarks(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"]), sorted(script.CANDIDATES))
        for name in script.VARIANT_NAMES:
            self.assertEqual(sorted(cell["vs"][name]), ["B1", "B2", script.REFERENCE])
        self.assertEqual(sorted(cell["vs"][script.REFERENCE]), ["B1", "B2"])

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], "2024-06-03")

    def test_the_measures_the_directive_names_are_all_there(self):
        self.assertEqual(sorted(self.result["calibration"]), ["0", "10", "5"])
        pooled = self.result["groups"]["pooled"]["all decision days"]
        for metric in script.SCORE_METRICS + script.COVERAGE_METRICS:
            self.assertIn(metric, pooled)
        for h in sp.HORIZONS:
            self.assertIn("grid_crps", self.result["groups"]["lead"][f"h={h}"])
        self.assertIn("regime", self.result["groups"])
        self.assertIn("pressure_day_type", self.result["groups"])

    def test_the_hit_sequences_cover_both_rules_three_levels_and_five_leads_without_gbm_walks(self):
        rows = self.result["hits"]["rows"]
        self.assertNotIn(script.GBM, rows)
        for model in script.MODELS:
            self.assertEqual(sorted(rows[model]), sorted(ct.HIT_RULES))
            for rule in ct.HIT_RULES:
                self.assertEqual(sorted(rows[model][rule]), ["q90", "q95", "q99"])
                self.assertEqual(sorted(rows[model][rule]["q95"]), [f"h={h}" for h in sp.HORIZONS])

    def test_the_page_says_it_is_development_data_and_names_the_open_question(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("development, not a verdict", text.lower())
        self.assertIn("Any change to the candidate is Eleonora's decision", text)
        self.assertIn("open question and Eleonora's", text)
        self.assertIn("q99, hit when y >= q", text)


if __name__ == "__main__":
    unittest.main()
