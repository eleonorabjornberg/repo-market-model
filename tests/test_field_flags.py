"""Per-field staleness and imputation flags for the live record (#1132, from #984 part 4; H5 groundwork G3).

`repo_model.field_flags.field_flags_block` says, for each declared feature at each horizon of one decision, how old
the value read was (hours, counted from its own observation's declared instant), whether it was the latest row public
at the decision instant, whether it is a carried weekly value, and whether the cell read is a hole that a model would
have to fill. It records facts; it sets no threshold, and what age counts as "too stale" is not decided here.

**Recorded mutations** (CLAUDE.md), 22 October 2026, each in a disposable copy of the tree, CPython 3.11:

1. `field_flags.flag_read`: the leak check `if read.available_at is not None and read.available_at > info.decision_instant:`
   changed to `if False:`. `FlagReadTests.test_a_read_public_only_after_the_decision_is_refused` failed with
   `AssertionError: LookAheadError not raised`.
2. `field_flags.flag_read`: the observed-kind assignment `latest_public = not (following < info.scored_index and ...)` replaced by `latest_public = True`.
   `FlagReadTests.test_an_older_row_than_the_latest_public_one_is_flagged_stale` failed with `AssertionError: True is not False`.
"""

import unittest
from datetime import time

from test_live_v3 import REGISTRY, _placeholder, published_panel

from repo_model import field_flags as ff
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

DECISION = time(16, 0)
T = 1500
FEATURES = ("spread_bps", "reserve_balances", "tga", "sofr_volume", "quarter_end", "days_to_month_end")


def _extended(h, hole=None):
    full = published_panel()["rows"]
    real = list(full[:T])
    if hole is not None:
        column, index = hole
        values = dict(real[index].values)
        values[column] = None
        real[index] = DailyObservation(real[index].date, values)
    return real + [_placeholder(row.date, real[-1].values) for row in full[T:T + h + 1]]


def _block(hole=None):
    return ff.field_flags_block(
        {h: _extended(h, hole) for h in (1, 2)}, {h: FEATURES for h in (1, 2)},
        registry=REGISTRY, decision_time=DECISION,
    )


class BlockTests(unittest.TestCase):
    def test_one_entry_per_feature_per_horizon(self):
        block = _block()
        self.assertEqual(block["version"], ff.FIELD_FLAGS_VERSION)
        self.assertEqual(set(block["horizons"]), {"1", "2"})
        self.assertEqual(set(block["horizons"]["1"]), set(FEATURES))
        self.assertEqual(set(block["basis"]), set(ff.FLAG_KEYS))

    def test_a_calendar_column_is_known_in_advance_and_has_no_age(self):
        cell = _block()["horizons"]["1"]["quarter_end"]
        self.assertEqual((cell["kind"], cell["age_hours"], cell["rows_before_scored"]), ("calendar", None, 0))
        self.assertEqual((cell["latest_public"], cell["carried"], cell["imputed"]), (True, False, False))

    def test_a_weekly_field_is_carried_and_aged_from_its_observation(self):
        rows = _extended(1)
        dates = [row.date for row in rows]
        rule = InformationRule(REGISTRY, FEATURES, decision_time=DECISION, horizon=1)
        info = rule.information_set(dates, len(rows) - 1)
        read = next(r for r in info.reads if r.feature == "reserve_balances")
        cell = _block()["horizons"]["1"]["reserve_balances"]
        self.assertEqual(cell["age_hours"], read.observation_hours)
        self.assertEqual(cell["read_date"], dates[read.row].isoformat())
        self.assertNotEqual(read.observation_hours, read.hours)
        self.assertTrue(cell["carried"])
        self.assertFalse(_block()["horizons"]["1"]["spread_bps"]["carried"])

    def test_a_daily_field_is_the_latest_public_row_and_not_imputed(self):
        cell = _block()["horizons"]["1"]["spread_bps"]
        self.assertEqual((cell["kind"], cell["latest_public"], cell["imputed"]), ("observed", True, False))
        self.assertGreater(cell["age_hours"], 0)

    def test_a_hole_at_the_row_read_is_flagged_imputed(self):
        rows = _extended(1)
        dates = [row.date for row in rows]
        rule = InformationRule(REGISTRY, FEATURES, decision_time=DECISION, horizon=1)
        info = rule.information_set(dates, len(rows) - 1)
        row = next(r for r in info.reads if r.feature == "sofr_volume").row
        block = _block(hole=("sofr_volume", row))
        self.assertTrue(block["horizons"]["1"]["sofr_volume"]["imputed"])
        self.assertFalse(block["horizons"]["1"]["spread_bps"]["imputed"])

    def test_a_feature_the_registry_cannot_date_is_refused(self):
        with self.assertRaises(ValueError):
            ff.field_flags_block({1: _extended(1)}, {1: ("no_such_feature",)}, registry=REGISTRY, decision_time=DECISION)

    def test_the_block_validates_and_a_malformed_one_is_refused(self):
        block = _block()
        ff.validate_field_flags_block(block)
        for bad in ({**block, "version": 2}, {k: v for k, v in block.items() if k != "basis"}):
            with self.assertRaises(ValueError):
                ff.validate_field_flags_block(bad)
        broken = {**block, "horizons": {"1": {"spread_bps": {"kind": "observed"}}}}
        with self.assertRaises(ValueError):
            ff.validate_field_flags_block(broken)


class FlagReadTests(unittest.TestCase):
    def setUp(self):
        self.rows = _extended(1)
        self.dates = [row.date for row in self.rows]
        self.rule = InformationRule(REGISTRY, ("spread_bps",), decision_time=DECISION, horizon=1)
        self.info = self.rule.information_set(self.dates, len(self.rows) - 1)
        self.read = next(r for r in self.info.reads if r.feature == "spread_bps")
        self.group = self.rule.groups[0]

    def _moved(self, row):
        available = self.rule.availability(self.dates, self.read.fields, row)
        return self.read._replace(row=row, available_at=available)

    def test_an_older_row_than_the_latest_public_one_is_flagged_stale(self):
        older = self._moved(self.read.row - 1)
        cell = ff.flag_read(self.rule, self.dates, self.rows, self.info, older, self.group)
        self.assertIs(cell["latest_public"], False)
        self.assertIs(ff.flag_read(self.rule, self.dates, self.rows, self.info, self.read, self.group)["latest_public"], True)

    def test_a_read_public_only_after_the_decision_is_refused(self):
        later = self._moved(self.info.scored_index - 1)
        self.assertGreater(later.available_at, self.info.decision_instant)
        with self.assertRaises(LookAheadError):
            ff.flag_read(self.rule, self.dates, self.rows, self.info, later, self.group)


if __name__ == "__main__":
    unittest.main()
