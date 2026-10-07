"""The live scorer scores the final test's leap-onset and at-risk groups and its false-alarm level (#363).

Eleonora's ruling of 7 October 2026 on PR #357's first question: the live scorer also scores
the groups `scripts/final_test_opening.py` scores, defined as it defines them. The leap cell
gets `leap_onset_days` (`onset.leap_onset_group`); the +5 bp and +10 bp cells get `onset_days`,
the at-risk group (`onset.day_groups`). Each group carries the same regime and day-type splits
and the h + 1 event block rule as the cell it sits in, and a false-alarm level: each column's
mean probability on the group's days whose outcome is 0, computed by
`final_test_opening.false_alarm_level` itself, not by a copy.

What is held here (fixtures only; no live or blind outcome is read):

* the groups' days and false-alarm figures agree with the final test's own functions on the
  same panel (`AgreementTests`);
* the group cells carry the cell's splits, block length and event minimum
  (`GroupCellTests`);
* the existing cells are unchanged (`ExistingCellsTests`);
* leap flags are built from panel rows before the scoring date only, and a locked day is
  still refused (`GuardTests`).

Recorded mutation (the panel-prefix guard): in `scripts/live_score.py`, `_event_groups` builds
the leap targets from `before = [row for row in rows if row.date < day]`; replaced by `rows`
-> `test_the_groups_read_only_rows_before_the_scoring_date` fails with `AssertionError`.
"""

from __future__ import annotations

import importlib.util
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock
import unittest

from repo_model import onset
from repo_model.asof import InformationRule
from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"


def _script(name):
    spec = importlib.util.spec_from_file_location(f"live_groups_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


live = _script("live_record")
score = _script("live_score")
opening = _script("final_test_opening")
score.now_utc = lambda: datetime(2030, 1, 1, 12, tzinfo=timezone.utc)

DAY = date(2028, 1, 3)
PERIOD = 8


def _record(day, targets, i):
    from test_live_record import _record as base

    record = base(day.isoformat())
    for h in live.HORIZONS:
        record["targets"][h - 1]["target_date"] = targets[h - 1].isoformat()
        record["targets"][h - 1]["anchor_spread_bp"] = 1
        # Varying, bounded probabilities: model, persistence and climatology differ.
        for name in live.TARGET_NAMES:
            record["models"]["pressure_model_v1"]["forecasts"][str(h)][name] = 0.05 + 0.01 * ((i + h) % 7)
        for baseline in ("persistence_logistic", "calendar_climatology"):
            for name in live.PRESSURE_TARGETS:
                record["baselines"][baseline]["forecasts"][str(h)][name] = 0.10 + 0.02 * ((i * 3 + h) % 5)
        for baseline in (onset.LEAP_PERSISTENCE_LOGISTIC, onset.LEAP_CALENDAR_CLIMATOLOGY):
            for name in live.LEAP_TARGETS:
                record["baselines"][baseline]["forecasts"][str(h)][name] = 0.08 + 0.02 * ((i * 2 + h) % 4)
    return record


def fixture(days=330):
    """Records and the outcome panel: 1 bp, with a 12 bp spike every `PERIOD` business days.

    A spike is a leap and a +5 bp and +10 bp exceedance; the days just before it, once five
    calm days have passed, are the at-risk group.
    """

    records, decision = [], date(2026, 10, 5)
    while len(records) < days:
        if live.is_decision_day(decision):
            targets = live.next_decision_days(decision, max(live.HORIZONS))
            records.append(_record(decision, targets, len(records)))
        decision = date.fromordinal(decision.toordinal() + 1)
    last = date.fromisoformat(records[-1]["targets"][-1]["target_date"])
    rows, current, n = [], date(2026, 10, 5), 0
    while current <= last:
        if live.is_decision_day(current):
            spread = 12 if n % PERIOD == PERIOD - 1 else 1
            values = {"sofr": 4.00 + spread / 100, "iorb": 4.00}
            values.update({column: rule(current) for column, rule in CALENDAR_COLUMN_RULES.items()})
            rows.append(DailyObservation(date=current, values=values))
            n += 1
        current = date.fromordinal(current.toordinal() + 1)
    return records, rows


class _Fast(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.splits = load_split_declaration(SPLITS)
        patch = mock.patch.object(onset, "REPLICATIONS", 40)
        patch.start()
        cls.addClassCleanup(patch.stop)
        cls.records, cls.rows = fixture()
        cls.result = score.score(cls.records, cls.rows, cls.splits, DAY)


class AgreementTests(_Fast):
    def _expected(self, cell_name, h):
        """The final test's groups and false-alarm level on the cell's own days."""

        cell = self.result["cells"][f"{cell_name}/h{h}"]
        by_date = {row.date: row for row in self.rows}
        days = [date.fromisoformat(r["targets"][h - 1]["target_date"]) for r in self.records]
        days = [d for d in days if d < DAY and d in by_date]
        self.assertEqual(len(days), cell["days"])
        if cell_name == "leap":
            rule = InformationRule(__import__("json").loads(opening.fp.REGISTRY.read_text()),
                                   ("spread_bps",), decision_time=opening.fp.DECISION, horizon=h)
            targets = onset.LeapTargets([r for r in self.rows if r.date < DAY], rule,
                                        opening.fp.leap_jump_bp(h))
            return days, onset.GROUP_LEAP_ONSET, onset.leap_onset_group(targets, days)
        groups = onset.day_groups([r for r in self.rows if r.date < DAY], days, self.splits)
        return days, onset.GROUP_ONSET, groups[onset.GROUP_ONSET]

    def test_each_group_is_the_final_tests_group(self):
        for cell_name in ("leap", "+5bp", "+10bp"):
            for h in (1, 3):
                with self.subTest(cell=cell_name, h=h):
                    cell = self.result["cells"][f"{cell_name}/h{h}"]
                    days, name, positions = self._expected(cell_name, h)
                    group = cell["groups"][name]
                    self.assertEqual(group["days"], len(positions))
                    self.assertGreater(len(positions), 0)

    def test_the_false_alarm_level_is_the_final_tests(self):
        for cell_name in ("leap", "+5bp", "+10bp"):
            with self.subTest(cell=cell_name):
                h = 1
                cell = self.result["cells"][f"{cell_name}/h{h}"]
                days, name, positions = self._expected(cell_name, h)
                outcomes = [cell_outcome(self, cell_name, h, d) for d in days]
                columns = self._columns(cell_name, h, days)
                expected = opening.false_alarm_level(name, positions, outcomes, columns)
                self.assertEqual(cell["groups"][name]["false_alarm_level"], expected)
                self.assertGreater(expected["days"], 0)

    def _columns(self, cell_name, h, days):
        by_target = {r["targets"][h - 1]["target_date"]: r for r in self.records}
        columns = {"pressure_model_v1": []}
        baselines = score.BASELINES[cell_name]
        for b in baselines:
            columns[b] = []
        for d in days:
            record = by_target[d.isoformat()]
            columns["pressure_model_v1"].append(record["models"]["pressure_model_v1"]["forecasts"][str(h)][cell_name])
            for b in baselines:
                columns[b].append(record["baselines"][b]["forecasts"][str(h)][cell_name])
        return columns

    def test_the_false_alarm_helper_is_shared_with_the_final_test(self):
        with mock.patch.object(score._opening(), "false_alarm_level", wraps=opening.false_alarm_level) as spy:
            score.score(self.records, self.rows, self.splits, DAY)
        self.assertTrue(spy.called)


def cell_outcome(test, cell_name, h, when):
    row = {r.date: r for r in test.rows}[when]
    spread = round(row.spread_bps)
    if cell_name == "leap":
        return 1 if spread - 1 > onset.LEAP_JUMP_BP[h] else 0
    return 1 if spread > float(cell_name[1:-2]) else 0


class GroupCellTests(_Fast):
    def test_a_group_cell_has_the_cells_splits_and_block_rule(self):
        cell = self.result["cells"]["leap/h2"]
        group = cell["groups"][onset.GROUP_LEAP_ONSET]
        self.assertGreaterEqual(group["events"], onset.MINIMUM_EVENTS)
        entry = group["models"]["pressure_model_v1"]
        for baseline in score.BASELINES["leap"]:
            paired = entry["paired"][baseline]
            self.assertEqual(paired["all_days"]["interval"]["block_length"], 3)
            self.assertIn("by_regime", paired)
            self.assertIn("by_day_type", paired)
            self.assertIn(paired["all_days"]["label"], ("shown better", "shown worse", "not shown"))

    def test_a_group_below_the_event_minimum_is_inconclusive(self):
        records, rows = fixture(days=60)
        result = score.score(records, rows, self.splits, DAY)
        group = result["cells"]["leap/h1"]["groups"][onset.GROUP_LEAP_ONSET]
        self.assertEqual(group["result"], "inconclusive")
        self.assertNotIn("models", group)

    def test_the_groups_are_reported_only(self):
        for cell in self.result["cells"].values():
            for group in cell.get("groups", {}).values():
                self.assertEqual(group["role"], "reported only")

    def test_the_leap_cell_gets_the_leap_group_and_the_others_the_at_risk_group(self):
        self.assertEqual(set(self.result["cells"]["leap/h1"]["groups"]), {onset.GROUP_LEAP_ONSET})
        for name in ("+5bp/h1", "+10bp/h1"):
            self.assertEqual(set(self.result["cells"][name]["groups"]), {onset.GROUP_ONSET})


class ExistingCellsTests(_Fast):
    def test_the_all_days_cells_are_unchanged_by_the_groups(self):
        with mock.patch.object(score, "_event_groups", lambda *a, **k: {}):
            bare = score.score(self.records, self.rows, self.splits, DAY)
        for name, cell in self.result["cells"].items():
            stripped = {k: v for k, v in cell.items() if k != "groups"}
            self.assertEqual(stripped, {k: v for k, v in bare["cells"][name].items() if k != "groups"})


class GuardTests(_Fast):
    def test_the_groups_read_only_rows_before_the_scoring_date(self):
        seen = []
        real = onset.LeapTargets

        def spy(rows, rule, threshold):
            seen.append(max(row.date for row in rows))
            return real(rows, rule, threshold)

        extra = DailyObservation(date=date(2027, 6, 1), values=dict(self.rows[-1].values))
        with mock.patch.object(onset, "LeapTargets", spy):
            score.score(self.records, self.rows + [extra], self.splits, DAY)
        self.assertTrue(seen)
        self.assertTrue(all(when < DAY for when in seen))

    def test_a_locked_day_is_still_refused(self):
        with mock.patch.object(score, "_require_scored_days_unlocked",
                               side_effect=LookAheadError("locked")):
            with self.assertRaises(LookAheadError):
                score.score(self.records, self.rows, self.splits, DAY)


if __name__ == "__main__":
    unittest.main()
