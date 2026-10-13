"""The persistence-logistic and raw-spread reference rows of the off-risk-day measurement (#681, finding #667).

Recorded mutations, 13 October 2026, in a disposable copy of `scripts/off_risk_day_624.py`:
1. in `paired_cells`, the pairing's resample restricted to the days of the cell replaced by the days of the first row only is not a
   leakage guard, so it has none; the guard of this file is the equal-days refusal. In `paired_cells`, the `len(...) != 1` check on the
   column lengths deleted: `test_columns_of_different_lengths_are_refused` then fails with `AssertionError: ValueError not raised`.
2. in `paired_cells`, the difference taken the other way (`q` less `p`): `test_a_better_ranker_has_a_positive_difference` then fails with
   `AssertionError: -0.5 not greater than 0`.
3. in `asof_spread_document`, the refusal of a hole in the read deleted: `test_a_hole_in_the_read_is_refused` then fails with
   `AssertionError: ValueError not raised`.
4. in `cell_statistics`, the `probability` switch ignored (the Brier skill and the reliability fit taken of the raw spread):
   `test_a_raw_spread_has_a_ranking_and_no_probability_statistics` then fails with `AssertionError: 0.3 is not None`.
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
        spread = [0.3, 0.3, 2.0, 2.0, 6.0, 7.0]
        y = [0, 0, 0, 1, 1, 1]
        cell = SCRIPT.cell_statistics(spread, y, [None] * 6, probability=False)
        self.assertIsNotNone(cell["auroc"])
        for key in ("brier_skill", "slope", "intercept"):
            self.assertIsNone(cell[key])
        self.assertEqual(cell["pressure_days"], 3)

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


if __name__ == "__main__":
    unittest.main()
