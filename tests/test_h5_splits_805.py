"""The splits of H5's headline claims (#805): the parts of `scripts/h5_splits_805.py` that decide which days enter which figure.

The script re-reads #634's and #707's walks and reports each skill headline against B1 and B2 by the type of the
decision day's anchor and without decision day 2019-09-18, and the upper-tail Brier claims by regime and pressure-day
type. These tests pin the helpers that cut the days: the excluded day leaves every group and nothing else does, a group
is the days that carry its label, and an event tally counts what the group holds.

No new leakage or staleness guard: the script reads no day the lockbox locks (`sd.refuse_locked`, tested with #634's
script) and every anchor is `anchor_day_types`' own (tested in `test_anchor_day_type`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "h5_splits_805.py"


def _module():
    spec = importlib.util.spec_from_file_location("h5_splits_805_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DAYS = [date(2019, 9, 16), date(2019, 9, 17), date(2019, 9, 18), date(2019, 9, 19)]


class DropDayTests(unittest.TestCase):
    def test_the_excluded_day_leaves_and_no_other_does(self):
        module = _module()
        self.assertEqual(module.drop_day(DAYS, date(2019, 9, 18)), [DAYS[0], DAYS[1], DAYS[3]])

    def test_a_day_that_is_not_in_the_group_is_a_data_error(self):
        module = _module()
        with self.assertRaises(ValueError):
            module.drop_day(DAYS[:2], date(2019, 9, 18))

    def test_the_excluded_day_is_the_one_of_the_finding(self):
        self.assertEqual(_module().EXCLUDED_DAY, date(2019, 9, 18))


class GroupTests(unittest.TestCase):
    def test_a_group_is_the_days_that_carry_its_label_in_order(self):
        module = _module()
        labels = {DAYS[0]: "ordinary", DAYS[1]: "spike", DAYS[2]: "ordinary", DAYS[3]: "spike"}
        self.assertEqual(
            module.group_by_label(reversed(DAYS), labels),
            {"ordinary": [DAYS[0], DAYS[2]], "spike": [DAYS[1], DAYS[3]]},
        )

    def test_a_day_without_a_label_is_a_data_error(self):
        module = _module()
        with self.assertRaises(KeyError):
            module.group_by_label(DAYS, {DAYS[0]: "ordinary"})


class OrientationTests(unittest.TestCase):
    def test_the_two_orientations_are_each_others_negative(self):
        module = _module()
        out = module.orientations([1.0, -2.0, 0.5])
        self.assertEqual(out["S(B2) - S(B1)"], [1.0, -2.0, 0.5])
        self.assertEqual(out["S(B1) - S(B2)"], [-1.0, 2.0, -0.5])


class EventTallyTests(unittest.TestCase):
    def test_it_counts_event_cells_and_the_days_that_hold_them(self):
        module = _module()
        happened = {(DAYS[0], 1): True, (DAYS[0], 2): True, (DAYS[1], 1): False, (DAYS[2], 3): True}
        self.assertEqual(module.event_tally(happened, [DAYS[0], DAYS[1]]), {"cells": 3, "event_cells": 2, "event_days": 1})

    def test_a_group_with_no_cells_tallies_zero(self):
        self.assertEqual(_module().event_tally({}, DAYS), {"cells": 0, "event_cells": 0, "event_days": 0})


if __name__ == "__main__":
    unittest.main()
