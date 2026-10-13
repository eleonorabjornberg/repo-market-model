"""The steps of the every-day part, taken apart one at a time (#687, avenue #674).

Recorded mutations, 13 October 2026, in a disposable copy of `scripts/every_day_steps_687.py`:
1. in `gate_cut`, the window of earlier days widened to include the day itself (`range(max(0, k - window), k + 1)`).
   `GateCutTests.test_a_cut_off_reads_earlier_forecasts_only` then fails with `AssertionError: 0.9 != 0.1`.
2. in `within_block_auroc`, the pairs counted over all days instead of the days of one block (every day put in block 0, `by_block.setdefault(0, [])`).
   `WithinBlockTests.test_a_level_shift_between_blocks_costs_the_pooled_figure_only` then fails with `AssertionError: 0.75 != 1.0`.
3. in `apply_steps`, the order of the steps reversed (`for step in reversed(STEPS)`). `StepTests.test_the_steps_are_applied_in_the_declared_order`
   then fails with `AssertionError: Lists differ: [[0.0, 0.0, 0.0, 0.3, 0.7, 0.2], ...`.
4. in `block_costs`, the difference taken the other way (pooled less within). `BlockCostTests.test_the_difference_is_within_less_pooled` then fails
   with `AssertionError: -0.25 not greater than 0`.
5. in `lost_pressure_days`, the cut-off compared with `>=` where it is `>` (a forecast at the cut counted as above it).
   `LostDaysTests.test_a_forecast_at_the_cut_is_not_above_it` then fails with `AssertionError: 1 != 0`.

The component's forecasts, the as-of reads of the tail spread and of the day-level inputs, and the fold grid are the existing readers
(`iorb_every_day_579`, `every_day_conditioning_601.read_levels`, `off_risk_day_624.read_features`), each with its own as-of guards and tests;
this script makes no new availability declaration.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "every_day_steps_687.json").read_text())


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("every_day_steps_687_script_t", ROOT / "scripts" / "every_day_steps_687.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["every_day_steps_687_script_t"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()
BOOT = dict(seed=687, replications=60, block_length=10, level=0.9)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(), DECLARED)

    def test_the_scoring_and_the_bootstrap_are_the_earlier_steps(self):
        step_one = json.loads((ROOT / "metadata" / "off_risk_day_624_step1.json").read_text())
        persistence = json.loads((ROOT / "metadata" / "off_risk_day_681.json").read_text())
        self.assertEqual(DECLARED["scoring"], step_one["scoring"])
        self.assertEqual(DECLARED["bootstrap"], persistence["bootstrap"])
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_the_step_values_are_the_published_ones(self):
        self.assertEqual({k: v for k, v in DECLARED["steps"]["gate"].items() if k != "rule"}, SCRIPT.fa.CONTROLS["gate"])
        self.assertEqual({k: v for k, v in DECLARED["steps"]["persist"].items() if k != "rule"}, SCRIPT.fa.CONTROLS["persist"])
        self.assertEqual(
            {k: DECLARED["steps"]["cap"][k] for k in ("quantile", "window", "minimum_earlier")}, SCRIPT.cond.CAPS["cap75"]
        )

    def test_nothing_is_published(self):
        self.assertEqual(DECLARED["published"], "nothing")


class RowNameTests(unittest.TestCase):
    def test_every_subset_of_the_steps_has_a_name_in_the_declared_order(self):
        names = [SCRIPT.row_name(s) for s in SCRIPT.subsets()]
        self.assertEqual(len(names), 8)
        self.assertEqual(len(set(names)), 8)
        self.assertEqual(SCRIPT.row_name(("cap", "persist")), "comp+persist+cap")
        self.assertEqual(SCRIPT.row_name(()), "comp")

    def test_an_undeclared_step_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.row_name(("floor",))

    def test_leave_one_out_removes_one_step_each(self):
        got = SCRIPT.leave_one_out()
        self.assertEqual(got["gate"], ("persist", "cap"))
        self.assertEqual(set(got), set(SCRIPT.STEPS))


class GateCutTests(unittest.TestCase):
    PARAMS = dict(quantile=0.5, window=4, minimum_earlier=2)

    def test_a_cut_off_reads_earlier_forecasts_only(self):
        raw = [0.1, 0.1, 0.1, 0.1, 0.9]
        off = [True] * 5
        # day 4's earlier forecasts are days 0 to 3, all 0.1; its own 0.9 must not enter the largest of them
        self.assertEqual(SCRIPT.gate_cut(raw, off, quantile=1.0, window=4, minimum_earlier=2)[4], 0.1)

    def test_a_later_forecast_never_moves_an_earlier_cut_off(self):
        raw = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        off = [True] * 6
        base = SCRIPT.gate_cut(raw, off, **self.PARAMS)
        moved = SCRIPT.gate_cut(raw[:4] + [9.0, 9.0], off, **self.PARAMS)
        self.assertEqual(base[:5], moved[:5])

    def test_a_risk_date_has_no_cut_off_and_is_not_counted_among_the_earlier_days(self):
        raw = [0.1, 0.2, 0.3, 0.4]
        off = [True, False, True, True]
        cuts = SCRIPT.gate_cut(raw, off, **self.PARAMS)
        self.assertIsNone(cuts[1])
        self.assertIsNone(cuts[2])  # one earlier ordinary day, fewer than the minimum
        self.assertEqual(cuts[3], 0.1)  # days 0 and 2: the nearest-rank median of 0.1 and 0.3


class StepTests(unittest.TestCase):
    CONTROLS = {"persist": {"days": 2}, "gate": {"quantile": 0.5, "window": 4, "minimum_earlier": 2}}

    def setUp(self):
        self.raw = [[0.5, 0.9, 0.3, 0.8, 0.7, 0.2], [0.25, 0.45, 0.15, 0.4, 0.35, 0.1]]
        self.off = [True] * 6

    def test_no_step_leaves_the_forecasts_alone(self):
        self.assertEqual(SCRIPT.apply_steps(self.raw, self.off, (), self.CONTROLS), self.raw)

    def test_persist_takes_the_smaller_of_today_and_yesterday(self):
        got = SCRIPT.apply_steps(self.raw, self.off, ("persist",), self.CONTROLS)
        self.assertEqual(got[0], [0.0, 0.5, 0.3, 0.3, 0.7, 0.2])

    def test_the_cap_zeroes_the_days_that_are_not_kept_and_needs_its_mask(self):
        keep = [True, False, True, True, False, True]
        got = SCRIPT.apply_steps(self.raw, self.off, ("cap",), self.CONTROLS, keep)
        self.assertEqual(got[0], [0.5, 0.0, 0.3, 0.8, 0.0, 0.2])
        with self.assertRaises(ValueError):
            SCRIPT.apply_steps(self.raw, self.off, ("cap",), self.CONTROLS)
        with self.assertRaises(ValueError):
            SCRIPT.apply_steps(self.raw, self.off, ("cap",), self.CONTROLS, keep[:-1])

    def test_the_steps_are_applied_in_the_declared_order(self):
        keep = [True, False, True, True, True, True]
        both = SCRIPT.apply_steps(self.raw, self.off, ("persist", "cap"), self.CONTROLS, keep)
        by_hand = SCRIPT.apply_steps(
            SCRIPT.apply_steps(self.raw, self.off, ("persist",), self.CONTROLS), self.off, ("cap",), self.CONTROLS, keep
        )
        self.assertEqual(both, by_hand)
        reversed_order = SCRIPT.apply_steps(
            SCRIPT.apply_steps(self.raw, self.off, ("cap",), self.CONTROLS, keep), self.off, ("persist",), self.CONTROLS
        )
        self.assertNotEqual(both[0], reversed_order[0])

    def test_the_curve_across_thresholds_stays_non_increasing(self):
        keep = [True] * 6
        got = SCRIPT.apply_steps([[0.1] * 6, [0.9] * 6], self.off, ("cap",), self.CONTROLS, keep)
        self.assertTrue(all(a >= b for a, b in zip(got[0], got[1])))

    def test_a_risk_date_keeps_the_parent_s_forecast_through_the_gate(self):
        off = [True, True, True, False, True, True]
        got = SCRIPT.apply_steps(self.raw, off, ("gate",), self.CONTROLS)
        self.assertEqual(got[0][3], 0.8)


class WithinBlockTests(unittest.TestCase):
    def test_a_level_shift_between_blocks_costs_the_pooled_figure_only(self):
        # inside each block the pressure day is above the others; block 1 sits 10 higher than block 0
        scores = [1.0, 0.0, 0.0, 10.0, 11.0, 10.0]
        outcomes = [1, 0, 0, 0, 1, 0]
        blocks = [0, 0, 0, 1, 1, 1]
        self.assertEqual(SCRIPT.within_block_auroc(scores, outcomes, blocks), 1.0)
        self.assertLess(SCRIPT.pj.auroc(scores, outcomes), 1.0)

    def test_ties_count_half_and_no_pair_gives_none(self):
        self.assertEqual(SCRIPT.within_block_auroc([1.0, 1.0], [1, 0], [0, 0]), 0.5)
        self.assertIsNone(SCRIPT.within_block_auroc([1.0, 2.0], [1, 0], [0, 1]))

    def test_columns_of_different_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.within_block_auroc([1.0], [1, 0], [0, 0])


class BlockCostTests(unittest.TestCase):
    def setUp(self):
        n = 120
        self.blocks = [k // 20 for k in range(n)]
        self.y = [1 if k % 5 == 0 else 0 for k in range(n)]
        # each block ranks perfectly inside it and block 1, 3, 5 sit 5 higher than the others
        self.shifted = [(5.0 if b % 2 else 0.0) + (1.0 if v else 0.0) for b, v in zip(self.blocks, self.y)]
        self.level = [1.0 if v else 0.0 for v in self.y]

    def test_the_difference_is_within_less_pooled(self):
        got = SCRIPT.block_costs(self.shifted, self.y, self.blocks, **BOOT)
        self.assertEqual(got["within_block_auroc"], 1.0)
        self.assertGreater(got["difference"], 0)
        self.assertAlmostEqual(got["difference"], got["within_block_auroc"] - got["pooled_auroc"])

    def test_a_forecast_with_no_shift_costs_nothing(self):
        got = SCRIPT.block_costs(self.level, self.y, self.blocks, **BOOT)
        self.assertEqual(got["difference"], 0.0)

    def test_draws_and_left_out_add_to_the_replications(self):
        got = SCRIPT.block_costs(self.shifted, self.y, self.blocks, **BOOT)
        self.assertEqual(got["draws"] + got["left_out"], BOOT["replications"])

    def test_the_same_seed_gives_the_same_interval(self):
        self.assertEqual(
            SCRIPT.block_costs(self.shifted, self.y, self.blocks, **BOOT), SCRIPT.block_costs(self.shifted, self.y, self.blocks, **BOOT)
        )


class LostDaysTests(unittest.TestCase):
    def test_zeroed_counts_pressure_days_a_step_takes_to_zero(self):
        y = [1, 1, 0, 1]
        before = [0.3, 0.3, 0.3, 0.0]
        after = [0.0, 0.2, 0.0, 0.0]
        got = SCRIPT.lost_pressure_days(y, before, after, [0.1, 0.1, 0.1, 0.1])
        self.assertEqual(got["zeroed"], 1)
        self.assertEqual(got["pressure_days"], 3)

    def test_a_forecast_at_the_cut_is_not_above_it(self):
        got = SCRIPT.lost_pressure_days([1], [0.2], [0.1], [0.2])
        self.assertEqual(got["below_cut"], 0)
        self.assertEqual(SCRIPT.lost_pressure_days([1], [0.3], [0.1], [0.2])["below_cut"], 1)

    def test_a_day_with_no_cut_is_left_out_of_the_cut_count(self):
        got = SCRIPT.lost_pressure_days([1, 1], [0.3, 0.3], [0.0, 0.0], [None, 0.2])
        self.assertEqual((got["below_cut"], got["days_with_cut"]), (1, 1))

    def test_columns_of_different_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.lost_pressure_days([1], [0.1, 0.2], [0.1], [0.1])


class ReportTests(unittest.TestCase):
    CELL = {"pressure_days": 5, "auroc": 0.8, "brier_skill": 0.1, "slope": 1.0, "pressure_days_on_zero": 2,
            "intervals": {"auroc": {"lower": 0.7, "upper": 0.9}, "brier_skill": {"lower": 0.0, "upper": 0.2}}}

    def test_the_ladder_prints_a_row_with_its_interval_and_a_missing_cell_is_left_out(self):
        document = {"rows": {"r": {"1": {"cells": {"all": self.CELL}}, "2": {"cells": {}}}}}
        text = SCRIPT.ladder_markdown(document)
        self.assertIn("| `r` | 1 | 5 | 0.800 [0.700, 0.900] | 0.100 [0.000, 0.200] | 1.000 | 2 |", text)
        self.assertNotIn("| `r` | 2 |", text)

    def test_the_paired_table_signs_the_difference(self):
        pair = {"auroc": {"difference": -0.1, "lower": -0.2, "upper": 0.0}, "brier_skill": None}
        document = {"rows": {"r": {"1": {"cells": {"all": self.CELL}, "paired_with_ref": {"all": pair}}}, "ref": {"1": {"cells": {"all": self.CELL}}}}}
        text = SCRIPT.paired_ladder_markdown(document)
        self.assertIn("-0.100 [-0.200, +0.000]", text)
        self.assertIn("Reference: `ref`", text)

    def test_the_block_table_shows_an_undefined_difference_as_a_dash(self):
        entry = dict(blocks=3, pooled_auroc=None, within_block_auroc=None, difference=None, lower=None, upper=None)
        self.assertIn("| – | – | – |", SCRIPT.blocks_markdown({"rows": {"r": {"1": entry}}}))


if __name__ == "__main__":
    unittest.main()
