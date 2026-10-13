"""The near-threshold bill input and the post-month-end window (#688): the readings, the screen's statistics and the declaration.

Pure functions, the committed declaration and the as-of reading of the two inputs; nothing here fits a model.

Recorded mutations, 13 October 2026, each in a disposable copy and each killed by the test named:

- `scripts/near_threshold_688.py`, `post_month_end_window`: the condition `bday_of_month(day) <= WINDOW_DAYS` replaced by
  `bday_of_month(day) < WINDOW_DAYS` (the window is two days, not three). `PostMonthEndWindowTests.test_the_first_three_market_days`
  failed with `AssertionError`.
- `scripts/near_threshold_688.py`, `switched`: `calendar = contract.CALENDAR_FEATURES | {FLAG}` replaced by
  `calendar = contract.CALENDAR_FEATURES` (the flag is then a column no declaration classifies).
  `AsOfReadTests.test_the_window_flag_is_read_for_the_scored_day_at_every_lead` errored with `contract.UndeclaredFeatureError`.
- `scripts/near_threshold_688.py`, `refuse_locked`: the call to `require_unlocked` removed. `LockboxTests.test_a_locked_day_is_refused`
  failed with `AssertionError` (no `LookAheadError` was raised).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("near_threshold_688_script", ROOT / "scripts" / "near_threshold_688.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["near_threshold_688_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()
DECLARATION = json.loads((ROOT / "metadata" / "near_threshold_688.json").read_text())


class PostMonthEndWindowTests(unittest.TestCase):
    def test_the_first_three_market_days(self):
        # 2024-02: Thursday the 1st is market day 1; Monday the 5th is day 3; the 6th is day 4.
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 2, 1)), 1.0)
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 2, 5)), 1.0)
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 2, 6)), 0.0)

    def test_a_month_that_starts_at_the_weekend_counts_from_the_first_market_day(self):
        # 2024-06-01 is a Saturday: Monday the 3rd is day 1 and Wednesday the 5th is day 3.
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 6, 3)), 1.0)
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 6, 5)), 1.0)
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 6, 6)), 0.0)

    def test_a_holiday_is_not_a_market_day(self):
        # 2024-01-01 is a holiday: Tuesday the 2nd is day 1 and Thursday the 4th is day 3.
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 1, 4)), 1.0)
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 1, 5)), 0.0)

    def test_the_last_days_of_a_month_are_not_in_the_window(self):
        self.assertEqual(SCRIPT.post_month_end_window(date(2024, 1, 31)), 0.0)


class BandTests(unittest.TestCase):
    def test_the_near_band_is_two_to_five_on_whole_basis_points(self):
        self.assertEqual(SCRIPT.spread_band(1.0), "low")
        self.assertEqual(SCRIPT.spread_band(1.99), "low")
        self.assertEqual(SCRIPT.spread_band(2.0), "near")
        self.assertEqual(SCRIPT.spread_band(5.0), "near")
        self.assertEqual(SCRIPT.spread_band(5.4), "near")
        self.assertEqual(SCRIPT.spread_band(5.6), "high")
        self.assertEqual(SCRIPT.spread_band(-3.0), "low")

    def test_a_missing_spread_has_no_band(self):
        self.assertIsNone(SCRIPT.spread_band(None))


class StratifiedDifferenceTests(unittest.TestCase):
    def test_a_known_value(self):
        # stratum a: 2 of 4 with the input are pressure days, 1 of 4 without (n = 8, weight 4*4/8 = 2, difference 0.25)
        # stratum b: 1 of 2 with, 0 of 6 without (n = 8, weight 2*6/8 = 1.5, difference 0.5)
        rows = (
            [(1, 1, "a")] * 2 + [(1, 0, "a")] * 2 + [(0, 1, "a")] + [(0, 0, "a")] * 3
            + [(1, 1, "b")] + [(1, 0, "b")] + [(0, 0, "b")] * 6
        )
        value = SCRIPT.stratified_difference(rows)
        self.assertAlmostEqual(value, (2 * 0.25 + 1.5 * 0.5) / 3.5)

    def test_a_stratum_with_only_one_side_carries_no_weight(self):
        rows = [(1, 1, "a"), (1, 0, "a"), (1, 1, "b"), (0, 0, "b"), (0, 1, "b")]
        self.assertAlmostEqual(SCRIPT.stratified_difference(rows), (1.0 - 0.5))

    def test_no_stratum_with_both_sides_is_none(self):
        self.assertIsNone(SCRIPT.stratified_difference([(1, 1, "a"), (0, 0, "b")]))

    def test_the_difference_is_zero_when_the_input_adds_nothing_inside_strata(self):
        rows = [(1, 1, "a"), (1, 0, "a"), (0, 1, "a"), (0, 0, "a")] + [(1, 0, "b"), (0, 0, "b")]
        self.assertAlmostEqual(SCRIPT.stratified_difference(rows), 0.0)


class RateTests(unittest.TestCase):
    def test_rates_with_and_without(self):
        rows = [(1, 1), (1, 0), (1, 0), (0, 1), (0, 0), (0, 0), (0, 0), (0, 0)]
        cell = SCRIPT.rate_cell(rows)
        self.assertEqual((cell["with_n"], cell["with_events"], cell["without_n"], cell["without_events"]), (3, 1, 5, 1))
        self.assertAlmostEqual(cell["with_rate"], 1 / 3)
        self.assertAlmostEqual(cell["without_rate"], 0.2)
        self.assertAlmostEqual(cell["difference"], 1 / 3 - 0.2)

    def test_a_cell_with_too_few_days_has_no_rate(self):
        cell = SCRIPT.rate_cell([(1, 1), (0, 0)], minimum_days=30, minimum_events=3)
        self.assertIsNone(cell["difference"])


class DeclarationTests(unittest.TestCase):
    def test_the_grid_is_the_protocols(self):
        from repo_model import scoring_protocol as sp

        self.assertEqual(tuple(SCRIPT.GRID), sp.GRID)

    def test_at_most_three_rows_are_run(self):
        self.assertEqual(set(DECLARATION["model"]["variants"]), {"control", "bill_x_band", "post_month_end_window"})
        self.assertLessEqual(len(DECLARATION["model"]["variants"]), 3)

    def test_the_last_scored_day_is_before_the_locked_tiers(self):
        self.assertLess(date.fromisoformat(DECLARATION["scoring"]["last_day"]), date(2026, 1, 1))

    def test_an_uncommitted_declaration_is_refused(self):
        import subprocess

        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", "metadata/near_threshold_688.json"], cwd=ROOT, capture_output=True, text=True
        ).stdout.strip()
        if dirty:
            with self.assertRaises(SystemExit):
                SCRIPT.committed_declaration()
        else:
            self.assertEqual(SCRIPT.committed_declaration()["issue"], 688)


class LockboxTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        from repo_model.splits import LookAheadError

        with self.assertRaises(LookAheadError):
            SCRIPT.refuse_locked([date(2026, 9, 4)])

    def test_the_last_scored_day_is_allowed(self):
        SCRIPT.refuse_locked([date(2025, 12, 31)])


class AsOfReadTests(unittest.TestCase):
    """The two inputs through the as-of rule on the panel built from the tracked fixtures (no model is fitted)."""

    @classmethod
    def setUpClass(cls):
        import contextlib
        import io
        import tempfile

        from repo_model import cli, measurement_fields
        from repo_model.data import load_daily_panel

        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            panel = Path(directory) / "panel.csv"
            with contextlib.redirect_stdout(io.StringIO()):
                code = cli.main([
                    "build", "--raw-root", str(ROOT / "tests/fixtures/snapshots/funding_inputs"),
                    "--output", str(panel), "--build-cutoff", manifest["build_cutoff"],
                    "--decision-time", manifest["decision_time"],
                ])
            assert code == 0, code
            cls.rows = load_daily_panel(panel)
        cls.registry = measurement_fields.load_registry()
        cls.raw_bills = {row.date: row.values.get("treasury_settlement_bills") for row in cls.rows}

    def test_the_window_flag_is_read_for_the_scored_day_at_every_lead(self):
        for lead in (1, 3, 5):
            values = SCRIPT.read_inputs(self.rows, self.registry, lead, ("post_month_end_window",), limit=40)
            self.assertTrue(values, "no scored day was read")
            for day, read in values.items():
                self.assertEqual(read["post_month_end_window"], SCRIPT.post_month_end_window(day))

    def test_the_bill_column_is_never_more_than_what_settles_and_is_announced_before_the_decision(self):
        seen = 0
        for lead in (1, 2, 5):
            values = SCRIPT.read_inputs(self.rows, self.registry, lead, ("treasury_settlement_bills",), limit=400)
            for day, read in values.items():
                known = read["treasury_settlement_bills"]
                if known is None:
                    continue
                seen += 1
                self.assertLessEqual(known, self.raw_bills[day] + 1e-9, f"{day} lead {lead}: more bills than settle")
        self.assertGreater(seen, 0)


if __name__ == "__main__":
    unittest.main()
