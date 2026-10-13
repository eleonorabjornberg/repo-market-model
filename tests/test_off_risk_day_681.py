"""The persistence-logistic and raw-spread reference rows of the off-risk-day measurement (#681, finding #667).

Recorded mutations, 13 October 2026, in a disposable copy of `scripts/off_risk_day_624.py`:
1. in `paired_cells`, the check that the two rows, the outcomes and the reference are one per day deleted (two rows of different days are paired
   by position). `test_columns_of_different_lengths_are_refused` then errors with `IndexError: list index out of range`.
2. in `paired_cells`, the difference taken the other way (the other row less the row). `test_a_better_ranker_has_a_positive_difference` then fails with
   `AssertionError: -0.4896304020391612 not greater than 0`.
3. in `asof_spread_document`, the refusal of a hole in the as-of read deleted (a hole read as 0 bp). `test_a_hole_in_the_read_is_refused` then fails
   with `AssertionError: ValueError not raised`.
4. in `cell_statistics`, the `probability` switch ignored (the Brier skill and the reliability fit taken of the raw spread).
   `test_a_raw_spread_has_a_ranking_and_no_probability_statistics` then fails with `AssertionError: 0.16552444444444436 is not None`.
5. in `read_features`, the spread read taken off the scored day's own row (`timed_rows[fold.index].spread_bps`) in place of the as-of fold's
   `fold.feature_row.spread_bps`. `test_the_lead_one_read_is_the_spread_two_rows_back` then fails with
   `AssertionError: 17.000000000000014 != -5.000000000000004 within 9 places`.

The as-of read of the spread is `off_risk_day_624.read_features`, the reader of step 2 (`asof.InformationRule` with the leakage and staleness guards of
`baseline._as_of_folds`); `spread_bps` is the row's own sofr less iorb, both already declared, so no new availability declaration is made.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "off_risk_day_681.json").read_text())


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("off_risk_day_624_script_681", ROOT / "scripts" / "off_risk_day_624.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["off_risk_day_624_script_681"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()
BOOT = dict(seed=681, replications=60, block_length=10, level=0.9)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.persistence_declaration_document(), DECLARED)

    def test_the_scoring_and_the_bootstrap_are_step_ones(self):
        step_one = json.loads((ROOT / "metadata" / "off_risk_day_624_step1.json").read_text())
        self.assertEqual(DECLARED["scoring"], step_one["scoring"])
        self.assertEqual(DECLARED["bootstrap"], step_one["bootstrap"])
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_nothing_is_published_and_the_reference_rows_are_named(self):
        self.assertEqual(DECLARED["published"], "nothing")
        self.assertEqual(set(DECLARED["reference_rows"]), {SCRIPT.PERSISTENCE, SCRIPT.SPREAD_REFERENCE})


class PairedTests(unittest.TestCase):
    def setUp(self):
        n = 200
        self.y = [1 if (k % 5 == 0 or k % 7 == 3) else 0 for k in range(n)]
        self.good = [0.7 if v else 0.1 for v in self.y]
        self.noise = [0.6 if k % 3 == 0 else 0.1 for k in range(n)]
        self.ref = [0.2] * n
        self.cells = {"all": list(range(n)), "first half": list(range(n // 2)), "none": []}

    def run_it(self, p, q, **kw):
        return SCRIPT.paired_cells(self.cells, p, q, self.y, self.ref, **{**BOOT, **kw})

    def test_a_better_ranker_has_a_positive_difference(self):
        got = self.run_it(self.good, self.noise)["all"]
        self.assertGreater(got["auroc"]["difference"], 0)
        self.assertGreater(got["auroc"]["lower"], 0)
        self.assertGreater(got["brier_skill"]["difference"], 0)

    def test_a_row_paired_with_itself_differs_by_exactly_nothing(self):
        got = self.run_it(self.noise, self.noise)["all"]
        for stat in ("auroc", "brier_skill"):
            self.assertEqual((got[stat]["difference"], got[stat]["lower"], got[stat]["upper"]), (0.0, 0.0, 0.0))

    def test_the_same_seed_gives_the_same_interval_and_an_empty_cell_has_none(self):
        self.assertEqual(self.run_it(self.good, self.noise), self.run_it(self.good, self.noise))
        self.assertNotEqual(self.run_it(self.good, self.noise), self.run_it(self.good, self.noise, seed=7))
        self.assertIsNone(self.run_it(self.good, self.noise)["none"]["auroc"])

    def test_draws_and_left_out_add_to_the_replications(self):
        entry = self.run_it(self.good, self.noise, block_length=1)["first half"]["auroc"]
        self.assertEqual(entry["draws"] + entry["left_out"], BOOT["replications"])

    def test_the_interval_is_the_one_the_row_s_own_resamples_give(self):
        # one resample per replication, shared by every cell and every row: the same seed draws the same days as `intervals`
        own = SCRIPT.intervals(self.cells, self.good, self.y, self.ref, **BOOT)
        paired = self.run_it(self.good, [0.0] * len(self.y))
        self.assertEqual(own["all"]["auroc"]["draws"], paired["all"]["auroc"]["draws"])

    def test_columns_of_different_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.paired_cells(self.cells, self.good, self.noise[:-1], self.y, self.ref, **BOOT)


class RawSpreadTests(unittest.TestCase):
    def test_a_raw_spread_has_a_ranking_and_no_probability_statistics(self):
        n = 120
        y = [1 if k % 4 == 0 else 0 for k in range(n)]
        spread = [0.2 + (k % 4 == 0 and k % 3 != 0 or k % 5 == 1) * 0.3 + (k % 9) * 0.01 for k in range(n)]
        as_probability = SCRIPT.cell_statistics(spread, y, [0.25] * n)
        self.assertIsNotNone(as_probability["brier_skill"])
        self.assertIsNotNone(as_probability["slope"])
        cell = SCRIPT.cell_statistics(spread, y, [0.25] * n, probability=False)
        self.assertEqual(cell["auroc"], as_probability["auroc"])
        for key in ("brier_skill", "slope", "intercept"):
            self.assertIsNone(cell[key])
        self.assertEqual(cell["pressure_days"], 30)

    def test_the_intervals_of_a_raw_spread_are_its_ranking_only(self):
        n = 120
        y = [1 if k % 4 == 0 else 0 for k in range(n)]
        spread = [5.0 + (k % 4 == 0) * 3.0 + (k % 9) * 0.1 for k in range(n)]
        table = {"p": spread, "y": y, "clim": [0.25] * n, "regime": ["a"] * n, "state": ["s"] * n}
        got = SCRIPT.measure_row(table, dict(BOOT), probability=False)["all"]
        self.assertGreater(got["intervals"]["auroc"]["lower"], 0.5)
        self.assertIsNone(got["intervals"]["brier_skill"])
        self.assertIsNone(got["intervals"]["slope"])

    def test_the_document_is_the_as_of_read_by_day_at_the_primary_threshold(self):
        reads = {"2020-01-02": {"spread_bps": 1.5}, "2020-01-03": {"spread_bps": -0.5}}
        document = SCRIPT.asof_spread_document(reads, ["2020-01-02", "2020-01-03"], 2)
        self.assertEqual(document["horizon"], 2)
        self.assertEqual(document["forecasts"][SCRIPT.SPREAD_REFERENCE]["5"], {"2020-01-02": 1.5, "2020-01-03": -0.5})

    def test_a_hole_in_the_read_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.asof_spread_document({"2020-01-02": {"spread_bps": None}}, ["2020-01-02"], 1)
        with self.assertRaises(ValueError):
            SCRIPT.asof_spread_document({}, ["2020-01-02"], 1)


class MarkdownTests(unittest.TestCase):
    def document(self):
        stat = {
            "days": 100, "pressure_days": 9, "auroc": 0.8, "brier_skill": 0.1, "slope": 0.9, "intercept": 0.0, "positive_days": 90, "pressure_days_on_zero": 1,
            "skill_days": 100, "intervals": {"auroc": None, "brier_skill": None, "slope": None, "intercept": None},
        }
        level = dict(stat, brier_skill=None, slope=None, intercept=None, positive_days=0, pressure_days_on_zero=0)
        pair = {"all": {"auroc": {"difference": 0.05, "lower": -0.01, "upper": 0.1, "draws": 60, "left_out": 0}, "brier_skill": None}}
        return {"rows": {
            SCRIPT.PERSISTENCE: {"1": {"cells": {"all": stat}}},
            "variant": {"1": {"cells": {"all": dict(stat, auroc=0.85)}, "paired_with_" + SCRIPT.PERSISTENCE: pair}},
            SCRIPT.SPREAD_REFERENCE: {"1": {"cells": {"all": level}}},
        }}

    def test_the_paired_table_shows_the_difference_the_cell_s_pressure_days_and_both_rows(self):
        text = SCRIPT.paired_markdown(self.document())
        self.assertIn("`variant` against `persistence_logistic`", text)
        self.assertIn("| all | 1 | 9 | 0.850 | 0.800 | +0.050 [-0.010, +0.100] | 0.100 | 0.100 | – |", text)

    def test_a_level_has_no_zero_forecast_count_in_the_row_table(self):
        text = SCRIPT.markdown(self.document())
        self.assertIn("n/a (a level)", text)

    def test_the_page_table_shows_a_row_once_with_its_reference_beside_it(self):
        document = self.document()
        text = SCRIPT.paired_table_markdown([document, document], "all")
        self.assertEqual(text.count("`variant`"), 1)
        self.assertNotIn("`" + SCRIPT.PERSISTENCE + "` |", text.split("\n", 2)[2])
        self.assertIn("| `variant` | 1 | 9 | 0.850 | 0.800 | +0.050 [-0.010, +0.100] |", text)


class AsOfSpreadTests(unittest.TestCase):
    """The spread read for a lead-1 scored day is the spread of the row two rows back (what is public at its decision instant), never the day's own (the leakage guard of the new reference row)."""

    @classmethod
    def setUpClass(cls):
        import subprocess
        import tempfile

        cls.tmp = tempfile.TemporaryDirectory()
        panel = Path(cls.tmp.name) / "panel.csv"
        env = {**__import__("os").environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
        subprocess.run(
            [sys.executable, "-B", "-m", "repo_model.cli", "build", "--raw-root", str(ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"),
             "--output", str(panel), "--build-cutoff", "2026-09-08T21:31:42+00:00", "--decision-time", "16:00:00"],
            check=True, capture_output=True, env=env, cwd=ROOT,
        )
        from repo_model import measurement_fields
        from repo_model.data import load_daily_panel

        cls.rows = load_daily_panel(panel)
        cls.registry = measurement_fields.load_registry()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_lead_one_read_is_the_spread_two_rows_back(self):
        from datetime import date

        reads = SCRIPT.read_features(self.rows, self.registry, date(2019, 12, 31), 1, fields=("spread_bps",))
        by_date = {row.date.isoformat(): row for row in self.rows}
        ordered = [row.date.isoformat() for row in self.rows]
        self.assertGreater(len(reads), 100)
        for day, read in reads.items():
            self.assertAlmostEqual(read["spread_bps"], by_date[ordered[ordered.index(day) - 2]].spread_bps, places=9, msg=day)


if __name__ == "__main__":
    unittest.main()
