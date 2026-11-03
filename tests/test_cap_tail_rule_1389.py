"""The cap and tail-rule study (#1389): `scripts/cap_tail_rule_1389.py`.

The tests fix the arithmetic on hand cases: how many levels the cap reaches, the per-cell probabilities and Brier cells of the three rules
(`repo_model.capped_law`), the decile counts of the randomized PIT, the decision-day series of a group, the check that every rule's law has
the capped vector as its quantiles, and the refusal of a record whose rules score alike on the grid but whose capped vector is not the
candidate's. The study adds no leakage, availability or staleness guard of its own: the window guard is #1366's `refuse_beyond`, loaded
unchanged and tested in `tests/test_calibration_masking_candidate_1366.py`.

Recorded mutations (the checks this script adds; the tests were written before the script and failed with `FileNotFoundError` until it existed;
each mutation was applied and restored):

* `binding_count`, `v > ceiling` replaced by `v >= ceiling`: `BindingTests.test_a_level_exactly_at_the_line_is_not_reached` fails with
  `AssertionError` (`1 != 0`);
* `check_quantiles`, `if abs(got - want) > tolerance:` replaced by `if False:`: `CheckTests.test_a_law_that_does_not_have_the_capped_quantiles_is_refused`
  fails with `AssertionError` (`ValueError not raised`).
"""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cap_tail_rule_1389_script", REPO / "scripts" / "cap_tail_rule_1389.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import capped_law as cl  # noqa: E402
from repo_model.scoring_protocol import GRID  # noqa: E402


def ramp(start, step):
    return [start + step * i for i in range(len(GRID))]


def many_knots():
    u = ramp(-4.0, 0.5)
    u[-4:] = [11.0, 20.0, 25.0, 40.0]
    return u


class BindingTests(unittest.TestCase):
    def test_the_levels_the_cap_reaches_are_counted(self):
        self.assertEqual(script.binding_count(many_knots(), 10.0), 4)
        self.assertEqual(script.binding_count(ramp(-4.0, 0.1), 10.0), 0)

    def test_a_level_exactly_at_the_line_is_not_reached(self):
        u = ramp(-20.0, 1.0)
        u[-1] = 10.0
        self.assertEqual(script.binding_count(u, 10.0), 0)

    def test_no_line_reaches_nothing(self):
        self.assertEqual(script.binding_count(many_knots(), None), 0)

    def test_the_classes(self):
        self.assertEqual([script.binding_class(n) for n in (0, 1, 2, 3, 4, 9)], ["0", "1", "2-3", "2-3", "4+", "4+"])


class CellTests(unittest.TestCase):
    def test_the_status_quo_and_the_open_tail_disagree_where_four_levels_tie(self):
        row = script.cell_scores(many_knots(), 10.0, 12.0)
        self.assertLess(row["status_quo"]["p10"], 1e-6)
        self.assertAlmostEqual(row["open_tail"]["p10"], 0.005, places=9)
        self.assertEqual(row["atom_at_line"]["p10"], 0.0)
        # the outcome is above the line: the Brier cell is the square of what was missed
        self.assertAlmostEqual(row["open_tail"]["brier10"], (1 - 0.005) ** 2, places=9)
        self.assertAlmostEqual(row["atom_at_line"]["brier10"], 1.0)
        self.assertEqual(row["atom_at_line"]["line_event"], 1)

    def test_a_cell_without_a_line_has_no_line_cell(self):
        row = script.cell_scores(many_knots(), None, 3.0)
        for rule in cl.RULES:
            self.assertIsNone(row[rule]["brier_line"])
        self.assertEqual(row["status_quo"]["p5"], row["open_tail"]["p5"])

    def test_the_event_is_the_whole_basis_point(self):
        # 10.4 bp rounds to 10: not above the line at 10
        row = script.cell_scores(many_knots(), 10.0, 10.4)
        self.assertEqual(row["status_quo"]["line_event"], 0)
        self.assertEqual(row["status_quo"]["event10"], 0)
        self.assertEqual(row["status_quo"]["event5"], 1)

    def test_the_pit_interval_is_that_of_the_law(self):
        row = script.cell_scores(many_knots(), 10.0, 10.0)
        law = cl.emitted_law(many_knots(), 10.0, "open_tail")
        self.assertEqual(row["open_tail"]["pit"], cl.pit_interval(law, 10.0))


class CheckTests(unittest.TestCase):
    def test_every_rule_has_the_capped_quantiles(self):
        script.check_quantiles(many_knots(), 10.0)

    def test_a_law_that_does_not_have_the_capped_quantiles_is_refused(self):
        with self.assertRaises(ValueError):
            script.check_quantiles(many_knots(), 10.0, laws={"status_quo": cl.emitted_law(ramp(-4.0, 0.5), None)})


class SeriesTests(unittest.TestCase):
    def test_a_day_is_the_mean_of_its_cells_in_the_group(self):
        cells = [
            {"day": "2026-01-02", "lead": 1, "regime": "a"}, {"day": "2026-01-02", "lead": 2, "regime": "b"},
            {"day": "2026-01-05", "lead": 1, "regime": "a"},
        ]
        values = [1.0, 3.0, 5.0]
        self.assertEqual(script.day_series(cells, values, lambda c: True), {date(2026, 1, 2): 2.0, date(2026, 1, 5): 5.0})
        self.assertEqual(script.day_series(cells, values, lambda c: c["regime"] == "b"), {date(2026, 1, 2): 3.0})

    def test_deciles(self):
        counts = script.decile_counts([0.0, 0.05, 0.1, 0.55, 0.999, 1.0])
        self.assertEqual(counts, [2, 1, 0, 0, 0, 1, 0, 0, 0, 2])
        self.assertEqual(sum(counts), 6)


class TailExtentTests(unittest.TestCase):
    def test_the_open_tail_runs_one_bp_above_the_line_where_four_levels_bind(self):
        # the last open segment is 5 bp over 0.05 of probability (100 bp per unit); the last 1% runs 1 bp
        self.assertAlmostEqual(script.tail_extent(many_knots(), 10.0, "open_tail"), 1.0, places=9)

    def test_a_bounded_law_has_none(self):
        self.assertEqual(script.tail_extent(many_knots(), 10.0, "atom_at_line"), 0.0)
        self.assertLess(script.tail_extent(many_knots(), 10.0, "status_quo"), 1e-4)
        self.assertEqual(script.tail_extent(many_knots(), None, "open_tail"), 0.0)


class RecordTests(unittest.TestCase):
    """The committed record and page: the page is the record rendered, and the record keeps what the study promises."""

    record = REPO / "docs" / "research" / "cap-tail-rule-1389" / "result.json"
    page = REPO / "docs" / "research" / "cap-tail-rule-1389-result.md"

    def test_the_page_is_the_record_rendered(self):
        import json

        self.assertEqual(self.page.read_text(encoding="utf-8"), script.render(json.loads(self.record.read_text(encoding="utf-8"))))

    def test_the_record_is_a_development_study_with_no_locked_day(self):
        import json

        r = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(r["label"], "development, not a verdict")
        self.assertEqual(sorted(r["windows"]), ["2026", "development"])
        for w in r["windows"].values():
            self.assertTrue(w["grid_scores"]["identical_under_every_rule"])
            self.assertLess(abs(w["reproduction"]["mean_grid_crps"] - w["reproduction"]["record_1314"]), 1e-9)

    def test_the_page_asks_one_marked_question_with_options_and_a_default(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## Question for Eleonora", text)
        self.assertIn("Default if she has not answered", text)
        for n in ("1.", "2.", "3.", "4."):
            self.assertIn(f"\n{n} ", text)


class RuleAgreementTests(unittest.TestCase):
    def test_where_the_cap_does_not_bind_the_open_tail_and_the_status_quo_agree(self):
        rng = random.Random(1389)
        for _ in range(50):
            u = sorted(rng.uniform(-6, 9) for _ in GRID)
            row = script.cell_scores(u, 10.0, rng.uniform(-3, 12))
            self.assertAlmostEqual(row["open_tail"]["p5"], row["status_quo"]["p5"], places=5)


if __name__ == "__main__":
    unittest.main()
