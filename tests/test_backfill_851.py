"""The back-fill build runs, serves only admitted series, and its guard reads the model's own columns (#851).

H4 steps 2-3; implements Eleonora's ruling on #742 as finding #832 reports it. Three defects, one test
class each. Red first, against main at 4832d8a2:

* `ThePanelBuilds`: `AttributeError: 'Namespace' object has no attribute 'end'` (`backfill_history.py`
  called `pressure_v1_1.panel_command` without `end`).
* `BackFilledRowsServeOnlyAdmittedSeries`: the back-filled rows carried `tbill_4w`, `reserve_balances`, `tga`,
  `on_rrp`, `reserve_scarcity_state` and the rest (`AssertionError`), once the build ran.
* `TheGuardReadsTheModelsColumns`: `AttributeError: module 'repo_model.backfill' has no attribute
  'series_read'`, and `run` still took the series from `--reads`.

Mutation record (the guard that reads the model's columns). In a copy of the working tree under the
session's scratchpad, CPython 3.11 (`/opt/rmm-venv`), `PYTHONDONTWRITEBYTECODE=1`, `python -B`, this file run
alone, unmutated control green before and after, the mutated line confirmed applied by grep. In
`scripts/backfill_history.py`, `run_command.with_history`, the line
`reads = backfill.series_read(features)` was mutated to `reads = ("tgcr", "bgcr", "sofr")` (the caller's
list, as `--reads tgcr,bgcr,sofr` was). Killed: `test_a_model_that_reads_an_unadmitted_series_is_refused`
failed with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from repo_model import backfill, baseline
from repo_model.baseline import ScoredFold
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
ADMITTED = backfill.load_admitted_series(ROOT / "metadata" / "backfill_posting.json")


def _history():
    spec = importlib.util.spec_from_file_location("backfill_history_851", ROOT / "scripts" / "backfill_history.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Built(unittest.TestCase):
    """The extended panel, built once from the tracked snapshots."""

    @classmethod
    def setUpClass(cls):
        cls._folder = tempfile.TemporaryDirectory()
        folder = Path(cls._folder.name)
        cls.output, scratch = folder / "ext.csv", folder / "scratch.csv"
        with mock.patch("builtins.print"):
            cls.status = _history().panel_command(argparse.Namespace(output=cls.output, scratch=scratch))
        with cls.output.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            cls.header = reader.fieldnames
            cls.rows = list(reader)

    @classmethod
    def tearDownClass(cls):
        cls._folder.cleanup()


class ThePanelBuilds(_Built):
    def test_the_build_runs_and_writes_back_filled_and_published_rows(self):
        self.assertEqual(self.status, 0)
        days = [date.fromisoformat(row["date"]) for row in self.rows]
        self.assertLess(days[0], backfill.FIRST_PUBLISHED)
        self.assertGreaterEqual(days[-1], backfill.FIRST_PUBLISHED)


class BackFilledRowsServeOnlyAdmittedSeries(_Built):
    def _back_filled(self):
        return [row for row in self.rows if date.fromisoformat(row["date"]) < backfill.FIRST_PUBLISHED]

    def test_every_series_that_is_not_admitted_is_blank(self):
        back = self._back_filled()
        self.assertTrue(back)
        for name in ("tbill_4w", "tbill_13w", "reserve_balances", "tga", "on_rrp", "treasury_settlement",
                     "treasury_settlement_bills", "treasury_settlement_coupons", "treasury_settlement_soma",
                     "dealer_treasury_position", "bank_total_assets", "effr", "reserve_scarcity_state"):
            self.assertIn(name, self.header)
            self.assertTrue(all(not row[name] for row in back), name)

    def test_the_admitted_series_the_calendar_and_iorb_are_kept(self):
        back = self._back_filled()
        for name in ("sofr", "tgcr", "bgcr", "iorb", "quarter_end", "tax_date", "days_to_month_end"):
            self.assertTrue(any(row[name] for row in back), name)

    def test_published_rows_are_untouched(self):
        published = [row for row in self.rows if date.fromisoformat(row["date"]) >= backfill.FIRST_PUBLISHED]
        for name in ("tbill_4w", "reserve_balances", "tga", "reserve_scarcity_state"):
            self.assertTrue(any(row[name] for row in published), name)


class TheGuardReadsTheModelsColumns(unittest.TestCase):
    def test_series_read_follows_derived_features_to_their_series(self):
        self.assertEqual(backfill.series_read(("spread_bps",)), ("sofr",))
        self.assertEqual(backfill.series_read(("sofr_p25", "sofr", "tgcr")), ("sofr", "tgcr"))
        self.assertEqual(backfill.series_read(("quarter_end", "tax_date", "iorb")), ())
        self.assertEqual(backfill.series_read(("tbill_4w", "reserve_balances")), ("reserve_balances", "tbill_4w"))
        self.assertEqual(backfill.series_read(("reserves_when_depleted",)), ("on_rrp", "reserve_balances"))
        self.assertEqual(backfill.series_read(("reserve_scarcity_state",)), ("reserve_scarcity_state",))

    def _run(self, features):
        """`run_command` over a script whose model reads `features`, one back-filled fit."""

        history = _history()
        fold = ScoredFold(
            train_start=date(2014, 8, 22), train_end=date(2018, 6, 27), train_rows=70,
            feature_date=date(2018, 6, 27), scored_date=date(2018, 6, 29),
        )

        def fake(observations, *, minimum_history=20, **kwargs):
            return SimpleNamespace(folds=[fold])

        def main(argv):
            baseline.rolling_exceedance_backtest([], features=features)
            return 0

        with tempfile.TemporaryDirectory() as folder:
            panel = Path(folder) / "ext.csv"
            days = [date(2018, 3, 28) + timedelta(days=i) for i in range(10)]
            with panel.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(["date", "sofr", "iorb"])
                for day in days:
                    writer.writerow([day.isoformat(), "1.5", "1.4"])
            args = argparse.Namespace(
                extended=panel, script=ROOT / "scripts" / "pressure_v1_1.py", control=False,
                rest=[], folds_output=None, pairs_output=None,
            )
            with mock.patch.object(baseline, "rolling_exceedance_backtest", fake), \
                    mock.patch.object(history, "_script", return_value=SimpleNamespace(main=main)), \
                    mock.patch("builtins.print"):
                return history.run_command(args)

    def test_a_model_that_reads_only_admitted_series_passes(self):
        self.assertEqual(self._run(("spread_bps", "tgcr", "quarter_end")), 0)

    def test_a_model_that_reads_an_unadmitted_series_is_refused(self):
        with self.assertRaises(LookAheadError) as caught:
            self._run(("spread_bps", "tbill_4w"))
        self.assertIn("tbill_4w", str(caught.exception))

    def test_the_run_command_takes_no_reads_list(self):
        self.assertNotIn("--reads", (ROOT / "scripts" / "backfill_history.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
