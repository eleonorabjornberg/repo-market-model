"""The live decision row carries the day's own bill rates, and only those (#1403).

Hypothesis and step: H5 groundwork G3 (the live record), the follow-up to #1368 under Eleonora's ruling of 2 November 2026
(chat, relayed on PR #1384, question 1, option 1; #1323's Q3: same model, logged with the instant in each file). At the
18:00 ET decision instant the frozen v1 features read `tbill_4w` and `tbill_13w` from the decision day's own row
(`treasury_bill_rates` is declared available at 16:30 on its own day, `metadata/sources.json`). The live panel's decision
row was a placeholder carrying only the calendar and the schedule, so `require_reads_on_real_rows` refused. `extend_panel`
now fills those two cells from the point-in-time panel, the latest vintage at or before the instant, and the guard admits
an observed read on the decision row for exactly those columns (`DECISION_ROW_COLUMNS`), and only when the row carries it.

Red first: this file was committed before the change and failed on `live.DECISION_ROW_COLUMNS` and
`live.require_decision_row_declared` (`AttributeError`) and on the decision row carrying no bill rate (`KeyError`).

**Recorded mutations** (2 November 2026), each applied to the tree, confirmed by grep, the class named run, then reverted:

1. `scripts/live_record.py`, `decision_row_values`: the filter line `if row.available_at <= instant` replaced by
   `if True`. `LeakageTests.test_a_vintage_published_after_the_instant_is_not_read` then failed with `AssertionError`
   (the 18:01 vintage, 9.99, was read in place of the 16:30 one), and nothing else in this module failed.
2. `scripts/live_record.py`, `require_reads_on_real_rows`: the admission line `read.row == last_real + 1` replaced by
   `read.row > last_real`. `GuardTests.test_the_bill_rate_on_a_target_placeholder_is_refused` then failed with
   `AssertionError` (`LookAheadError not raised`), and nothing else in this module failed.
3. `scripts/live_record.py`, `require_reads_on_real_rows`: the admission line `and read.feature in DECISION_ROW_COLUMNS`
   replaced by `and True`. `GuardTests.test_no_other_observed_read_on_the_decision_row_is_admitted` then failed with
   `AssertionError` (`LookAheadError not raised`), and nothing else in this module failed.
"""

from __future__ import annotations

import contextlib
import copy
import csv
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from repo_model.asof import InformationRule
from repo_model.data import DailyObservation, load_daily_panel
from repo_model.splits import LookAheadError

from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "metadata" / "sources.json"
FIXTURES = ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"
CUTOFF = "2026-09-08T21:31:42+00:00"
EASTERN = ZoneInfo("America/New_York")
DAY = date(2025, 12, 22)


def _script(name):
    spec = importlib.util.spec_from_file_location(f"decision_row_1403_{name}", ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


live = _script("live_record")


def _auctions():
    return live.auction_records(FIXTURES)


class _Panel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from repo_model.cli import main as cli_main

        cls.tmp = tempfile.mkdtemp()
        cls.panel = Path(cls.tmp) / "funding_panel.csv"
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli_main(["build", "--raw-root", str(FIXTURES), "--output", str(cls.panel),
                             "--build-cutoff", CUTOFF, "--decision-time", "18:00:00"])
        if code != 0:
            raise RuntimeError("the fixture panel did not build")
        cls.pit = cls.panel.with_name(cls.panel.stem + "_point_in_time.csv")
        cls.rows = load_daily_panel(cls.panel)
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def real(self):
        return [row for row in self.rows if row.date < DAY]

    def extend(self, h=2, pit=None):
        return live.extend_panel(self.real(), DAY, h, pit or self.pit, _auctions())


class AvailabilityTests(_Panel):
    def test_the_columns_are_exactly_the_two_bill_rates(self):
        self.assertEqual(live.DECISION_ROW_COLUMNS, ("tbill_4w", "tbill_13w"))

    def test_the_declaration_holds_at_the_instant_in_force(self):
        live.require_decision_row_declared(self.registry)

    def test_a_source_published_after_the_instant_is_refused(self):
        late = copy.deepcopy(self.registry)
        late["treasury_bill_rates"]["release_lag"]["available_time"] = "18:30"
        with self.assertRaisesRegex(ValueError, "treasury_bill_rates"):
            live.require_decision_row_declared(late)

    def test_a_next_day_source_is_refused(self):
        late = copy.deepcopy(self.registry)
        late["treasury_bill_rates"]["release_lag"]["days"] = 1
        with self.assertRaisesRegex(ValueError, "treasury_bill_rates"):
            live.require_decision_row_declared(late)

    def test_the_declared_columns_are_the_bill_rates_the_contract_builds_from_that_source(self):
        from repo_model.contract import FEATURE_FIELDS

        for column in live.DECISION_ROW_COLUMNS:
            self.assertEqual(FEATURE_FIELDS[column][0][0], "treasury_bill_rates")


class DecisionRowTests(_Panel):
    def test_the_decision_row_carries_the_days_own_bill_rates(self):
        extended, _ = self.extend()
        row = next(r for r in extended if r.date == DAY)
        built = {r.date: r for r in self.rows}[DAY]
        for column in live.DECISION_ROW_COLUMNS:
            self.assertIsNotNone(row.values[column])
            self.assertEqual(row.values[column], built.values[column])

    def test_a_target_row_carries_no_bill_rate(self):
        extended, targets = self.extend(h=3)
        for row in extended:
            if row.date in targets:
                for column in live.DECISION_ROW_COLUMNS:
                    self.assertNotIn(column, row.values)

    def test_a_decision_day_without_a_published_bill_rate_is_refused(self):
        stripped = Path(self.tmp) / "stripped.csv"
        with self.pit.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            kept = [r for r in reader if not (r["series_id"] == "tbill_4w_coupon_equivalent"
                                              and r["ref_date"] == DAY.isoformat())]
            names = reader.fieldnames
        with stripped.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=names)
            writer.writeheader()
            writer.writerows(kept)
        with self.assertRaisesRegex(ValueError, "tbill_4w"):
            self.extend(pit=stripped)


class LeakageTests(_Panel):
    """A bill rate published after the instant is not read by the decision row.

    Recorded mutation 1 (module docstring): the filter `if row.available_at <= instant` in
    `decision_row_values` replaced by `if True`; `test_a_vintage_published_after_the_instant_is_not_read`
    then fails with `AssertionError`.
    """

    def _with_late_vintage(self):
        path = Path(self.tmp) / "late.csv"
        stamp = datetime.combine(DAY, time(18, 1), tzinfo=EASTERN).isoformat()
        with self.pit.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            names = reader.fieldnames
            rows = list(reader)
        template = next(r for r in rows if r["series_id"] == "tbill_4w_coupon_equivalent"
                        and r["ref_date"] == DAY.isoformat())
        rows.append(dict(template, available_at=stamp, value="9.99", vintage_id="late"))
        rows.sort(key=lambda r: datetime.fromisoformat(r["available_at"]))
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=names)
            writer.writeheader()
            writer.writerows(rows)
        return path, float(template["value"])

    def test_a_vintage_published_after_the_instant_is_not_read(self):
        path, first = self._with_late_vintage()
        extended, _ = self.extend(pit=path)
        row = next(r for r in extended if r.date == DAY)
        self.assertEqual(row.values["tbill_4w"], first)
        self.assertNotEqual(row.values["tbill_4w"], 9.99)


class GuardTests(_Panel):
    """`require_reads_on_real_rows` admits an observed read on the decision row for the bill rates and no others."""

    def _rule(self, features, h):
        return InformationRule(self.registry, features, decision_time=live.DECISION, horizon=h)

    def test_v1_reads_pass_at_eighteen_hundred_on_the_extended_panel(self):
        for h in live.HORIZONS:
            with self.subTest(h=h):
                rows, _ = self.extend(h=h)
                last_real = len(self.real()) - 1
                for features in (live.V1_FEATURES[h], live.CALENDAR_FEATURES, ("spread_bps",), live.published_features(h)):
                    live.require_reads_on_real_rows(rows, self._rule(features, h), len(rows) - 1, last_real)

    def test_the_bill_rate_on_a_target_placeholder_is_refused(self):
        # A stub rule whose only read is the bill rate on the row after the decision row, a cell that row carries
        # here: the admission is the decision row's alone, so it is refused (the as-of rule never serves it there).
        from types import SimpleNamespace

        from repo_model.asof import FieldRead, KIND_OBSERVED

        rows, _ = self.extend(h=2)
        last_real = len(self.real()) - 1
        target = last_real + 2
        carried = [DailyObservation(date=r.date, values={**r.values, "tbill_4w": 3.5}) if i == target else r
                   for i, r in enumerate(rows)]
        read = FieldRead("tbill_4w", KIND_OBSERVED, (), target, None, 0, None)
        rule = SimpleNamespace(information_set=lambda dates, index: SimpleNamespace(reads=(read,)))
        with self.assertRaisesRegex(LookAheadError, "tbill_4w"):
            live.require_reads_on_real_rows(carried, rule, len(carried) - 1, last_real)

    def test_no_other_observed_read_on_the_decision_row_is_admitted(self):
        # A stub rule whose only read is SOFR on the decision row, a cell that row does carry (the day before's,
        # so that a row exists): an observed read of any column but the bill rates is refused all the same.
        from types import SimpleNamespace

        from repo_model.asof import FieldRead, KIND_OBSERVED

        rows, _ = self.extend(h=1)
        last_real = len(self.real()) - 1
        self.assertIsNotNone(rows[last_real + 1].values["sofr"])
        read = FieldRead("sofr", KIND_OBSERVED, (), last_real + 1, None, 0, None)
        rule = SimpleNamespace(information_set=lambda dates, index: SimpleNamespace(reads=(read,)))
        with self.assertRaisesRegex(LookAheadError, "sofr"):
            live.require_reads_on_real_rows(rows, rule, len(rows) - 1, last_real)

    def test_a_decision_row_that_does_not_carry_the_rate_is_refused(self):
        rows, _ = self.extend(h=1)
        bare = [DailyObservation(date=r.date, values={k: v for k, v in r.values.items()
                                                      if k not in live.DECISION_ROW_COLUMNS})
                if r.date == DAY else r for r in rows]
        with self.assertRaisesRegex(LookAheadError, "tbill_"):
            live.require_reads_on_real_rows(bare, self._rule(live.V1_FEATURES[1], 1), len(bare) - 1,
                                            len(self.real()) - 1)


if __name__ == "__main__":
    unittest.main()
